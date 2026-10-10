"""Auto-discover RSS/Atom feeds (and sitemaps) for sites that gave no feed at the guessed address.

    python discover.py <sites.py>      # sites.py: SITES = [(group, name, page_url), ...]
"""
import importlib.util, re, sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin, urlsplit

import httpx
from lxml import etree, html as lhtml

sys.path.insert(0, ".")
import probe as P  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
UA = P.C.UA
SUFFIXES = ["/feed", "/feed/", "/rss", "/rss/", "/rss.xml", "/feed.xml", "/atom.xml", "/index.xml", "/blog/rss.xml", "/blog/feed", "/blog/rss",
            "/blog/feed.xml", "/blog/index.xml", "/news/rss", "/news/rss.xml", "/news/feed", "/blog/atom.xml", "/en/feed", "/zh/feed"]


def load(path):
    spec = importlib.util.spec_from_file_location("sites", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.SITES


def get(cli, url):
    try:
        return cli.get(url)
    except Exception as e:  # noqa: BLE001
        return type("R", (), {"status_code": 0, "content": b"", "text": str(e)[:60], "headers": {}, "url": url})()


def sitemap_info(cli, base):
    """Return (n_urls, n_recent7d, sample paths) from /sitemap.xml (follows a sitemapindex one level)."""
    root = f"{urlsplit(base).scheme}://{urlsplit(base).netloc}"
    urls, seen = [], set()
    queue = [root + "/sitemap.xml"]
    n = 0
    while queue and n < 6:
        u = queue.pop(0)
        if u in seen:
            continue
        seen.add(u)
        n += 1
        r = get(cli, u)
        if r.status_code != 200 or b"<" not in r.content[:200]:
            continue
        try:
            doc = etree.fromstring(r.content, parser=etree.XMLParser(recover=True, huge_tree=True))
        except Exception:  # noqa: BLE001
            continue
        if doc is None:
            continue
        for el in doc.iter():
            tag = el.tag.split("}")[-1] if isinstance(el.tag, str) else ""
            if tag == "sitemap":
                loc = next((c.text for c in el if c.tag.endswith("loc")), None)
                if loc and re.search(r"blog|news|post|article|press|update|change", loc, re.I):
                    queue.append(loc.strip())
            elif tag == "url":
                loc = next((c.text for c in el if c.tag.endswith("loc")), None)
                lm = next((c.text for c in el if c.tag.endswith("lastmod")), None)
                if loc:
                    urls.append((loc.strip(), (lm or "").strip()))
    if not urls:
        return None
    now = datetime.now(timezone.utc)
    recent = 0
    for _, lm in urls:
        d = P.C.parse_dt(lm)
        if d and (now - d) < timedelta(days=7):
            recent += 1
    pat = {}
    for loc, _ in urls:
        seg = "/" + "/".join(urlsplit(loc).path.strip("/").split("/")[:2])
        pat[seg] = pat.get(seg, 0) + 1
    top = sorted(pat.items(), key=lambda kv: -kv[1])[:4]
    return len(urls), recent, top


def run(site):
    group, name, page = site
    cli = httpx.Client(follow_redirects=True, timeout=20, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    found = []
    r = get(cli, page)
    html_note = f"HTTP {r.status_code}"
    if r.status_code == 200 and b"<" in r.content[:500]:
        try:
            doc = lhtml.fromstring(r.content)
            for l in doc.xpath('//link[@rel="alternate"]'):
                t = (l.get("type") or "").lower()
                if "xml" in t or "rss" in t or "atom" in t:
                    found.append(urljoin(str(r.url), l.get("href")))
            for a in doc.xpath("//a[@href]"):
                h = a.get("href")
                if re.search(r"(rss|feed|atom)(\.xml|/)?$|/rss/|/feed/|\.rss$", h, re.I):
                    found.append(urljoin(str(r.url), h))
        except Exception as e:  # noqa: BLE001
            html_note += f" parse:{e}"
    base = f"{urlsplit(page).scheme}://{urlsplit(page).netloc}"
    pbase = page.rstrip("/")
    for s in SUFFIXES:
        found.append(base + s)
        found.append(pbase + s)
    found = list(dict.fromkeys(found))[:60]
    good = []
    for u in found:
        res = P.probe((group, name, name, u))
        if not res.get("err") and res.get("n", 0) > 0:
            good.append(res)
            if len(good) >= 3:
                break
    sm = None
    if not good:
        sm = sitemap_info(cli, page)
    return site, html_note, good, sm


def main():
    sites = load(sys.argv[1])
    with ThreadPoolExecutor(10) as ex:
        results = list(ex.map(run, sites))
    last = None
    for (group, name, page), note, good, sm in results:
        if group != last:
            print(f"\n## {group}")
            last = group
        if good:
            for g in good:
                nh = g.get("newest_h")
                age = "无日期" if nh is None else (f"{nh:.0f}h" if nh < 48 else f"{nh/24:.0f}d")
                print(f"  ✓ {name:<22} {g['n']:>3}条 最新 {age:<6} 7d:{g.get('last7d','-'):<3} {g['url']}")
        else:
            extra = ""
            if sm:
                extra = f" | sitemap {sm[0]} 个网址，近 7 天 lastmod {sm[1]} 个，路径 {sm[2]}"
            print(f"  ✗ {name:<22} 没找到 RSS（页面 {note}）{extra}  [{page}]")


if __name__ == "__main__":
    main()
