"""《AI每日日报》信息收集器。

    python collect.py collect                      # 抓一遍全部源，新条目入库（只抓取模式，一天 4 次）
    python collect.py export <期目录> [--hours 30] [--no-commit]
                                                   # 取上次导出以来入库的新条目 → <期目录>/items.jsonl、candidates.json、candidates.md
    python collect.py health                       # 来源健康报告（也写进 health/health.md）

“新条目” = 库里没见过的（不看源里写的时间：OpenAI RSS 的时刻是占位值）。一个源第一次被抓时，36 小时以前的条目只入库、不当候选。
只追加、不删除。
"""
import argparse, hashlib, html, json, re, sqlite3, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx
import yaml
from dateutil import parser as dparser
from lxml import etree
from lxml import html as lhtml

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "seen.sqlite"
SNAP_DIR = HERE / "snapshots"
HEALTH_DIR = HERE / "health"
CST = timezone(timedelta(hours=8))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
TIER_RANK = {"official": 0, "community": 1, "media": 2, "cn": 3, "xproxy": 4, "signal": 5, "status": 6, "background": 7}
BACKFILL_HOURS = 36          # first fetch of a source: older items are stored but never become candidates
STALE_RELIST_DAYS = 7        # an unseen item older than this is a re-listing, not news
MAX_SNAPSHOTS_PER_RUN = 25
MAX_HTML_PAGES_PER_SOURCE = 8

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def now_utc():
    return datetime.now(timezone.utc)


def iso(d):
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if d else None


def parse_dt(s):
    if not s:
        return None
    try:
        d = dparser.parse(str(s))
    except (ValueError, OverflowError, TypeError):
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def strip_html(s, limit=600):
    if not s:
        return ""
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</li>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s).strip()
    return s[:limit]


def canon_url(u):
    if not u:
        return ""
    p = urlsplit(u.strip())
    q = "&".join(x for x in p.query.split("&") if x and not x.lower().startswith(("utm_", "ref=", "source=")))
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/") or "/", q, ""))


def uid_for(source_id, key):
    return hashlib.sha1(f"{source_id}|{key}".encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------- storage
def db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS items(
        uid TEXT PRIMARY KEY, source TEXT, org TEXT, tier TEXT, title TEXT, url TEXT, summary TEXT,
        published_raw TEXT, published_utc TEXT, fetched_utc TEXT, backfill INTEGER, snapshot TEXT, extra TEXT)""")
    con.execute("CREATE INDEX IF NOT EXISTS items_fetched ON items(fetched_utc)")
    con.execute("CREATE TABLE IF NOT EXISTS http_cache(url TEXT PRIMARY KEY, etag TEXT, last_modified TEXT)")
    con.execute("""CREATE TABLE IF NOT EXISTS health(source TEXT PRIMARY KEY, last_ok_utc TEXT, last_fail_utc TEXT,
        fails INTEGER DEFAULT 0, last_error TEXT, last_count INTEGER, newest_utc TEXT, via TEXT)""")
    con.execute("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)")
    return con


# ---------------------------------------------------------------- http
class Http:
    def __init__(self, timeout):
        self.c = httpx.Client(follow_redirects=True, timeout=timeout, headers={
            "User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, application/json, text/html;q=0.9, */*;q=0.5",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"})

    def get(self, url, cache=None, **kw):
        """GET with conditional headers. Returns (status, response or None)."""
        headers = dict(kw.pop("headers", None) or {})
        if cache is not None:
            row = cache.get(url)
            if row:
                if row[0]:
                    headers["If-None-Match"] = row[0]
                if row[1]:
                    headers["If-Modified-Since"] = row[1]
        r = self.c.get(url, headers=headers, **kw)
        return r.status_code, r


# ---------------------------------------------------------------- parsers
def _local(tag):
    return tag.split("}", 1)[-1] if isinstance(tag, str) else ""


def parse_feed(content):
    """RSS 2.0 / RSS 1.0 / Atom -> list of dicts(title, link, guid, summary, published, categories)."""
    root = etree.fromstring(content, parser=etree.XMLParser(recover=True, huge_tree=True, resolve_entities=False))
    if root is None:
        return []
    out = []
    for el in root.iter():
        if _local(el.tag) not in ("item", "entry"):
            continue
        rec = {"title": "", "link": "", "guid": "", "summary": "", "published": "", "categories": []}
        for ch in el:
            t = _local(ch.tag)
            text = (ch.text or "").strip()
            if t == "title" and not rec["title"]:
                rec["title"] = strip_html(text, 300)
            elif t == "link":
                href = ch.get("href")
                rel = ch.get("rel", "alternate")
                if href and rel == "alternate" and not rec["link"]:
                    rec["link"] = href
                elif text and not rec["link"]:
                    rec["link"] = text
            elif t in ("guid", "id") and not rec["guid"]:
                rec["guid"] = text
            elif t in ("description", "summary") and not rec["summary"]:
                rec["summary"] = text
            elif t in ("encoded", "content") and not rec["summary"]:
                rec["summary"] = text or etree.tostring(ch, encoding="unicode", method="text")
            elif t in ("pubDate", "published", "date", "issued") and not rec["published"]:
                rec["published"] = text
            elif t in ("updated", "modified") and not rec["published"]:
                rec["updated"] = text
            elif t in ("category", "subject"):
                rec["categories"].append(ch.get("term") or text)
        rec["published"] = rec["published"] or rec.get("updated", "")
        rec["summary"] = strip_html(rec["summary"], 800)
        out.append(rec)
    return out


def page_meta(http, url):
    """Fetch an article page -> (title, description, published, text)."""
    st, r = http.get(url)
    if st != 200:
        raise RuntimeError(f"HTTP {st}")
    doc = lhtml.fromstring(r.content)
    def meta(*names):
        for n in names:
            v = doc.xpath(f'//meta[@property="{n}" or @name="{n}"]/@content')
            if v and v[0].strip():
                return v[0].strip()
        return ""
    title = meta("og:title", "twitter:title") or (doc.findtext(".//title") or "").strip()
    desc = meta("og:description", "description", "twitter:description")
    pub = meta("article:published_time", "og:published_time", "date", "pubdate", "publish-date")
    if not pub:
        t = doc.xpath("//time/@datetime")
        pub = t[0] if t else ""
    return title, desc, pub, extract_text(doc)


def extract_text(doc):
    for bad in doc.xpath("//script|//style|//noscript|//svg|//nav|//footer|//header|//form|//iframe"):
        bad.drop_tree()
    node = None
    for xp in ("//article", "//main", "//body"):
        found = doc.xpath(xp)
        if found:
            node = max(found, key=lambda n: len(n.text_content() or ""))
            break
    if node is None:
        return ""
    parts = []
    for el in node.iter():
        if el.tag in ("p", "li", "h1", "h2", "h3", "h4", "td", "blockquote", "pre"):
            t = re.sub(r"\s+", " ", el.text_content() or "").strip()
            if t:
                parts.append(t)
    text = "\n".join(dict.fromkeys(parts)) or re.sub(r"\s+", " ", node.text_content() or "")
    return text[:60000]


# ---------------------------------------------------------------- source kinds -> raw items
def fetch_rss_like(http, cache, url):
    st, r = http.get(url, cache=cache)
    if st == 304:
        return "304", [], None
    if st != 200:
        raise RuntimeError(f"HTTP {st}")
    items = parse_feed(r.content)
    if not items and b"<rss" not in r.content[:2000] and b"<feed" not in r.content[:2000]:
        raise RuntimeError("返回的不是 RSS/Atom")
    return "ok", items, (r.headers.get("etag"), r.headers.get("last-modified"))


def kind_rss(src, http, cache, cfg):
    status, items, validators = fetch_rss_like(http, cache, src["url"])
    return status, [dict(key=i["guid"] or i["link"], title=i["title"], url=i["link"], summary=i["summary"],
                         published=i["published"], categories=i["categories"]) for i in items], validators, src["url"]


def kind_rsshub(src, http, cache, cfg):
    errors = []
    for base in cfg["defaults"].get("rsshub_instances", []):
        url = base.rstrip("/") + src["route"]
        try:
            status, items, validators = fetch_rss_like(http, None, url)
            if status == "ok" and not items:
                errors.append(f"{urlsplit(base).netloc}: 0 条")
                continue
            return status, [dict(key=i["guid"] or i["link"], title=i["title"], url=i["link"], summary=i["summary"],
                                 published=i["published"], categories=i["categories"]) for i in items], None, url
        except Exception as e:  # noqa: BLE001 - try the next instance
            errors.append(f"{urlsplit(base).netloc}: {str(e)[:40]}")
        time.sleep(1.0)
    raise RuntimeError("RSSHub 实例都不可用（" + "；".join(errors) + "）")


def kind_html_links(src, http, cache, cfg):
    st, r = http.get(src["url"])
    if st != 200:
        raise RuntimeError(f"HTTP {st}")
    doc = lhtml.fromstring(r.content)
    pat = re.compile(src["link_pattern"])
    links = []
    for a in doc.xpath("//a[@href]"):
        href = a.get("href").split("#")[0].split("?")[0]
        path = urlsplit(href).path if href.startswith("http") else href
        if pat.match(path):
            links.append(urljoin(src["base"], path))
    links = list(dict.fromkeys(links))
    if not links:
        raise RuntimeError("列表页没解析出链接（可能改版）")
    return "ok", [dict(key=u, title="", url=u, summary="", published="", needs_page=True) for u in links], None, src["url"]


def kind_deepseek_sitemap(src, http, cache, cfg):
    st, r = http.get(src["url"])
    if st != 200:
        raise RuntimeError(f"HTTP {st}")
    codes = sorted(set(re.findall(r"/news/news(\d{6})", r.text)))
    if not codes:
        raise RuntimeError("sitemap 里没有 /news/ 页面")
    out = []
    for c in codes:
        d = datetime.strptime(c, "%y%m%d").replace(hour=12, tzinfo=CST)
        u = f"https://api-docs.deepseek.com/zh-cn/news/news{c}"
        out.append(dict(key=c, title="", url=u, summary="", published=iso(d), needs_page=True))
    return "ok", out, None, src["url"]


def kind_qwen_api(src, http, cache, cfg):
    st, r = http.get(src["url"])
    if st != 200:
        raise RuntimeError(f"HTTP {st}")
    arts = (r.json().get("data") or {}).get("articles") or []
    if not arts:
        raise RuntimeError("接口返回 0 篇（language 参数要用 zh-CN）")
    out = []
    for a in arts:
        extra = a.get("extra") or {}
        if isinstance(extra, str):
            try:
                extra = json.loads(extra)
            except ValueError:
                extra = {}
        pub = ""
        for k in ("date", "publishDate", "publish_time", "publishTime", "time", "gmtCreate", "createTime"):
            if extra.get(k) or a.get(k):
                pub = str(extra.get(k) or a.get(k))
                break
        path = a.get("path") or a.get("id")
        out.append(dict(key=str(a.get("id") or path), title=a.get("title", ""), url=f"https://qwen.ai/blog?id={path}",
                        summary=strip_html(a.get("content") or extra.get("description") or "", 600), published=pub))
    return "ok", out, None, src["url"]


def kind_hf_models(src, http, cache, cfg):
    out, errs = [], []
    for org, label in src["orgs"].items():
        url = f"https://huggingface.co/api/models?author={org}&sort=createdAt&direction=-1&limit=30"
        try:
            st, r = http.get(url)
            if st != 200:
                raise RuntimeError(f"HTTP {st}")
            for m in r.json():
                mid = m.get("id") or m.get("modelId")
                out.append(dict(key=mid, title=mid, url=f"https://huggingface.co/{mid}", summary=m.get("pipeline_tag") or "",
                                published=m.get("createdAt", ""), org=label))
        except Exception as e:  # noqa: BLE001
            errs.append(f"{org}: {str(e)[:30]}")
    if not out:
        raise RuntimeError("全部失败：" + "；".join(errs))
    return "ok", out, None, "huggingface.co/api/models" + (f"（失败：{'；'.join(errs)}）" if errs else "")


def kind_readhub_daily(src, http, cache, cfg):
    st, r = http.get(src["url"])
    if st != 200:
        raise RuntimeError(f"HTTP {st}")
    data = r.json().get("data") or {}
    day = data.get("date") or data.get("day") or ""
    out = []
    for it in data.get("items") or []:
        uid = it.get("uid")
        out.append(dict(key=uid, title=it.get("title", ""), url=f"https://readhub.cn/topic/{uid}",
                        summary=strip_html(it.get("summary", ""), 600), published=it.get("publishDate") or day))
    if not out:
        raise RuntimeError("早报为空")
    return "ok", out, None, src["url"]


KINDS = {"rss": kind_rss, "rsshub": kind_rsshub, "html_links": kind_html_links, "deepseek_sitemap": kind_deepseek_sitemap,
         "qwen_api": kind_qwen_api, "hf_models": kind_hf_models, "readhub_daily": kind_readhub_daily}


# ---------------------------------------------------------------- filters
def keep(src, it):
    title = it.get("title") or ""
    text = f"{title} {it.get('summary') or ''}"
    cats = set(it.get("categories") or [])
    if cats & set(src.get("exclude_categories") or []):
        return False
    for pat in src.get("exclude_title") or []:
        if re.search(pat, title, re.I):
            return False
    kws = src.get("include_keywords")
    if kws and not any(kw_hit(k, text) for k in kws):
        return False
    return True


def kw_hit(k, text):
    """ASCII keywords match whole words only ("AI" must not hit "said"); CJK keywords match as substrings."""
    if k.isascii():
        return re.search(r"(?<![A-Za-z0-9])" + re.escape(k) + r"(?![A-Za-z0-9])", text, re.I) is not None
    return k in text


ORG_HINTS = [("OpenAI", r"OpenAI|ChatGPT|\bGPT-?\d|Sora|Codex|Altman"), ("Anthropic", r"Anthropic|Claude"),
             ("Google", r"Google|Gemini|DeepMind|Gemma"), ("DeepSeek", r"DeepSeek|深度求索"), ("Qwen", r"Qwen|通义|千问|阿里"),
             ("Kimi", r"Kimi|Moonshot|月之暗面"), ("智谱", r"Zhipu|GLM|智谱|Z\.ai"), ("MiniMax", r"MiniMax|海螺"),
             ("Meta", r"\bMeta\b|Llama"), ("xAI", r"\bxAI\b|Grok|SpaceXAI"), ("Mistral", r"Mistral"), ("NVIDIA", r"NVIDIA|Nvidia|英伟达"),
             ("Microsoft", r"Microsoft|Copilot|微软"), ("Apple", r"\bApple\b|苹果"), ("字节 Seed", r"ByteDance|字节|豆包|Doubao|Seedance"),
             ("腾讯", r"Tencent|腾讯|混元"), ("百度", r"Baidu|百度|文心"), ("小米", r"Xiaomi|小米|MiMo")]


def infer_org(title):
    for org, pat in ORG_HINTS:
        if re.search(pat, title or ""):
            return org
    return ""


# ---------------------------------------------------------------- collect
def collect(args):
    cfg = yaml.safe_load(open(HERE / "sources.yaml", encoding="utf-8"))
    sources = cfg["sources"]
    if args.only:
        wanted = set(args.only.split(","))
        sources = [s for s in sources if s["id"] in wanted]
    con = db()
    cache = {row[0]: (row[1], row[2]) for row in con.execute("SELECT url, etag, last_modified FROM http_cache")}
    http = Http(cfg["defaults"].get("timeout", 25))
    t_run = now_utc()

    def run_one(src):
        t0 = time.time()
        try:
            status, raw, validators, via = KINDS[src["kind"]](src, http, cache, cfg)
            return src, status, raw, validators, via, None, time.time() - t0
        except Exception as e:  # noqa: BLE001 - one broken source must not stop the run
            return src, "fail", [], None, None, f"{type(e).__name__}: {str(e)[:160]}", time.time() - t0

    # RSSHub public instances rate-limit hard: run those one by one after the rest
    normal = [s for s in sources if s["kind"] != "rsshub"]
    hub = [s for s in sources if s["kind"] == "rsshub"]
    with ThreadPoolExecutor(10) as ex:
        results = list(ex.map(run_one, normal))
    for s in hub:
        results.append(run_one(s))

    summary, snap_jobs = [], []
    for src, status, raw, validators, via, err, secs in results:
        sid = src["id"]
        if err:
            con.execute("""INSERT INTO health(source, last_fail_utc, fails, last_error) VALUES(?,?,1,?)
                ON CONFLICT(source) DO UPDATE SET last_fail_utc=excluded.last_fail_utc, fails=health.fails+1, last_error=excluded.last_error""",
                        (sid, iso(t_run), err))
            summary.append((sid, "失败", 0, err))
            continue
        first_time = con.execute("SELECT 1 FROM items WHERE source=? LIMIT 1", (sid,)).fetchone() is None
        new = 0
        newest = None
        for it in raw:
            if not keep(src, it):
                continue
            key = it.get("key") or it.get("url")
            uid = uid_for(sid, key)
            pub = parse_dt(it.get("published"))
            if pub and (newest is None or pub > newest):
                newest = pub
            if con.execute("SELECT 1 FROM items WHERE uid=?", (uid,)).fetchone():
                continue
            age_h = (t_run - pub).total_seconds() / 3600 if pub else None
            if first_time:
                backfill = 1 if (age_h is None and it.get("needs_page")) or (age_h is not None and age_h > BACKFILL_HOURS) else 0
            else:
                backfill = 1 if (age_h is not None and age_h > STALE_RELIST_DAYS * 24) else 0
            extra = {k: v for k, v in it.items() if k in ("categories", "needs_page") and v}
            con.execute("INSERT INTO items VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (uid, sid, it.get("org") or src.get("org") or "", src["tier"], it.get("title") or "", it.get("url") or "",
                         it.get("summary") or "", it.get("published") or "", iso(pub), iso(t_run), backfill, None,
                         json.dumps(extra, ensure_ascii=False) if extra else None))
            if not backfill:
                new += 1
                if it.get("needs_page") or src.get("snapshot"):
                    snap_jobs.append((uid, it.get("url"), bool(it.get("needs_page"))))
        if validators and src["kind"] == "rss" and (validators[0] or validators[1]):
            con.execute("INSERT OR REPLACE INTO http_cache VALUES(?,?,?)", (src["url"], validators[0], validators[1]))
        con.execute("""INSERT INTO health(source, last_ok_utc, fails, last_error, last_count, newest_utc, via) VALUES(?,?,0,NULL,?,?,?)
            ON CONFLICT(source) DO UPDATE SET last_ok_utc=excluded.last_ok_utc, fails=0, last_error=NULL,
            last_count=excluded.last_count, newest_utc=COALESCE(excluded.newest_utc, health.newest_utc), via=excluded.via""",
                    (sid, iso(t_run), len(raw), iso(newest), via))
        summary.append((sid, "304" if status == "304" else ("首次" if first_time else "ok"), new, f"{len(raw)} 条，{secs:.1f}s"))
    con.commit()

    # pages for html_links / sitemap items (title + date) and snapshots for official items
    per_source = {}
    done = 0
    for uid, url, needs_page in snap_jobs:
        if done >= MAX_SNAPSHOTS_PER_RUN:
            break
        src_id = con.execute("SELECT source FROM items WHERE uid=?", (uid,)).fetchone()[0]
        if needs_page:
            per_source[src_id] = per_source.get(src_id, 0) + 1
            if per_source[src_id] > MAX_HTML_PAGES_PER_SOURCE:
                continue
        try:
            title, desc, pub, text = page_meta(http, url)
        except Exception as e:  # noqa: BLE001
            con.execute("UPDATE items SET snapshot=? WHERE uid=?", (f"ERR {str(e)[:60]}", uid))
            continue
        day = t_run.astimezone(CST).strftime("%Y-%m-%d")
        path = SNAP_DIR / day / f"{uid}.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{title}\n{url}\n{pub}\n\n{desc}\n\n{text}", encoding="utf-8")
        sets = ["snapshot=?"]
        vals = [str(path.relative_to(HERE))]
        if needs_page:
            pd = parse_dt(pub)
            sets += ["title=CASE WHEN title='' THEN ? ELSE title END", "summary=CASE WHEN summary='' THEN ? ELSE summary END"]
            vals += [title, strip_html(desc, 600)]
            if pd:
                sets += ["published_raw=?", "published_utc=?"]
                vals += [pub, iso(pd)]
        con.execute(f"UPDATE items SET {', '.join(sets)} WHERE uid=?", (*vals, uid))
        done += 1
    con.commit()

    total_new = sum(n for _, _, n, _ in summary)
    fails = [s for s in summary if s[1] == "失败"]
    print(f"[collect] {t_run.astimezone(CST):%Y-%m-%d %H:%M} 北京时间：{len(summary)} 个源，新条目 {total_new} 条，失败 {len(fails)} 个，快照 {done} 份")
    for sid, st, n, info in summary:
        if n or st in ("失败", "首次") or args.verbose:
            print(f"  {st:<4} {sid:<28} 新 {n:<3} {info}")
    write_health(con)


# ---------------------------------------------------------------- export + cluster
WORD = re.compile(r"[a-z0-9][a-z0-9.\-]{2,}")
CJK = re.compile(r"[一-鿿]")
STOP = {"the", "and", "for", "with", "new", "its", "from", "that", "this", "are", "how", "now", "will", "into", "about", "your", "has", "have", "you", "our", "was",
        "after", "over", "more", "than", "what", "why", "who", "says", "said", "report", "reports", "sources", "amid", "could", "would", "just"}
# company names and words every AI headline shares: they must not be what makes two headlines "the same story"
GENERIC = {"openai", "anthropic", "google", "deepmind", "gemini", "claude", "chatgpt", "deepseek", "qwen", "meta", "nvidia", "microsoft", "apple",
           "xai", "grok", "mistral", "kimi", "model", "models", "ai", "llm", "launch", "launches", "release", "releases", "company", "update", "cnbc",
           "reuters", "bloomberg", "verge", "techcrunch", "人工智能", "模型", "大模型", "发布", "推出"}
BOOST = re.compile(r"launch|release|introduc|announc|unveil|available|open.?source|pricing|price|api|model|agent|发布|推出|上线|开源|降价|涨价|模型|更新|正式", re.I)


def tokens(title):
    t = (title or "").lower()
    toks = {w for w in WORD.findall(t) if w not in STOP}
    chars = CJK.findall(t)
    toks |= {a + b for a, b in zip(chars, chars[1:])}
    return toks


def clean_title(row):
    t = row["title"] or ""
    if row["source"].startswith("gnews"):
        t = re.sub(r"\s+-\s+[^-]{2,60}$", "", t)          # "Title - Publisher"
    return t.strip()


def export(args):
    ep = Path(args.episode_dir)
    ep.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(open(HERE / "sources.yaml", encoding="utf-8"))
    names = {s["id"]: s.get("name", s["id"]) for s in cfg["sources"]}
    con = db()
    con.row_factory = sqlite3.Row
    t_now = now_utc()
    last = con.execute("SELECT value FROM meta WHERE key='last_export_utc'").fetchone()
    since = parse_dt(args.since) if args.since else (parse_dt(last[0]) if last and not args.hours else t_now - timedelta(hours=args.hours or 30))
    rows = [dict(r) for r in con.execute("SELECT * FROM items WHERE backfill=0 AND fetched_utc>? ORDER BY fetched_utc", (iso(since),))]
    srcs = {s["id"]: s for s in cfg["sources"]}
    def still_kept(r):          # re-apply today's filters to rows stored under older rules
        extra = json.loads(r["extra"]) if r.get("extra") else {}
        src = srcs.get(r["source"])
        return src is None or keep(src, {"title": r["title"], "summary": r["summary"], "categories": extra.get("categories")})
    rows = [r for r in rows if still_kept(r)]
    for r in rows:
        r["source_name"] = names.get(r["source"], r["source"])
        r["title"] = clean_title(r)
        if not r["org"]:
            r["org"] = infer_org(r["title"])
    with open(ep / "items.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 1) signal sources: one candidate per source (or HF org) per day
    clusters, used = [], set()
    groups = {}
    for r in rows:
        if r["tier"] == "signal" and r["source"] not in ("ai_research_0xsmw",):
            day = (parse_dt(r["published_utc"]) or parse_dt(r["fetched_utc"])).astimezone(CST).strftime("%m-%d")
            key = (r["source"], r["org"] if r["source"] == "hf_models" else "", day)
            groups.setdefault(key, []).append(r)
            used.add(r["uid"])
    for (sid, org, day), rs in groups.items():
        head = dict(rs[0])
        titles = [x["title"] for x in rs]
        head["title"] = (f"{org} 在 Hugging Face 上传 {len(rs)} 个模型：" if sid == "hf_models" else f"{names.get(sid, sid)} {len(rs)} 次：") + "、".join(titles[:6]) + ("…" if len(titles) > 6 else "")
        clusters.append({"members": rs, "primary": head})
    # 2) everything else: greedy title-similarity clustering within 48 h
    rest = [r for r in rows if r["uid"] not in used]
    rest.sort(key=lambda r: TIER_RANK.get(r["tier"], 9))
    for r in rest:
        tk = tokens(r["title"])
        sig = tk - GENERIC
        pr = parse_dt(r["published_utc"]) or parse_dt(r["fetched_utc"])
        best = None
        for c in clusters:
            if c["primary"]["tier"] == "signal":
                continue
            ctk = c["tokens"]
            shared = sig & (ctk - GENERIC)
            sim = len(tk & ctk) / max(1, min(len(tk), len(ctk)))
            cp = parse_dt(c["primary"]["published_utc"]) or parse_dt(c["primary"]["fetched_utc"])
            close = (not pr or not cp) or abs((pr - cp).total_seconds()) < 48 * 3600
            same_org = r["org"] and r["org"] == c["primary"]["org"]
            if close and len(shared) >= 2 and (sim >= 0.5 or (same_org and len(shared) >= 2)):
                if best is None or sim > best[0]:
                    best = (sim, c)
        if best:
            best[1]["members"].append(r)
            best[1]["tokens"] |= tk
        else:
            clusters.append({"members": [r], "primary": r, "tokens": set(tk)})

    out = []
    for i, c in enumerate(clusters):
        ms = sorted(c["members"], key=lambda r: TIER_RANK.get(r["tier"], 9))
        p = c["primary"] if c["primary"]["tier"] == "signal" else ms[0]
        tiers = sorted({m["tier"] for m in ms}, key=lambda t: TIER_RANK.get(t, 9))
        n_src = len({m["source"] for m in ms})
        score = (8 - TIER_RANK.get(tiers[0], 8)) * 2 + min(n_src, 6) * 1.5 + min(len(ms), 12) * 0.5 + (2 if BOOST.search(p["title"]) else 0)
        if tiers[0] in ("background", "status"):
            score -= 4
        if n_src == 1:          # a lone aggregator / community hit ranks below a story several outlets carry
            score += srcs.get(p["source"], {}).get("weight", 0)
        pub = parse_dt(p["published_utc"])
        out.append({
            "cid": f"C{i + 1:03d}", "score": round(score, 1), "org": p["org"], "tiers": tiers, "n_sources": n_src, "n_items": len(ms),
            "title": p["title"], "url": p["url"], "source": p["source_name"], "tier": p["tier"],
            "published_cst": pub.astimezone(CST).strftime("%m-%d %H:%M") if pub else None,
            "published_note": "OpenAI RSS 的时刻是占位值，只信日期" if p["source"] == "openai_news" else None,
            "summary": (p["summary"] or "")[:400], "snapshot": p["snapshot"] if p["snapshot"] and not str(p["snapshot"]).startswith("ERR") else None,
            "others": [{"source": m["source_name"], "tier": m["tier"], "title": m["title"], "url": m["url"]} for m in ms if m is not p][:12],
        })
    out.sort(key=lambda c: -c["score"])
    meta = {"exported_cst": t_now.astimezone(CST).strftime("%Y-%m-%d %H:%M"), "since_cst": since.astimezone(CST).strftime("%Y-%m-%d %H:%M"),
            "items": len(rows), "candidates": len(out)}
    json.dump({"meta": meta, "candidates": out}, open(ep / "candidates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    write_candidates_md(ep / "candidates.md", meta, out)
    if not args.no_commit:
        con.execute("INSERT OR REPLACE INTO meta VALUES('last_export_utc', ?)", (iso(t_now),))
        con.commit()
    print(f"[export] {meta['since_cst']} → {meta['exported_cst']}（北京时间）：{len(rows)} 条 → {len(out)} 个候选 → {ep / 'candidates.json'}"
          + ("（--no-commit，没有推进导出时间）" if args.no_commit else ""))


def write_candidates_md(path, meta, cands, top=80):
    L = [f"# 候选（{meta['since_cst']} → {meta['exported_cst']} 北京时间）\n",
         f"{meta['items']} 条原始条目，合成 {len(cands)} 个候选，按分数排序；这里列前 {min(top, len(cands))} 个，全部在 candidates.json。\n"]
    for c in cands[:top]:
        L.append(f"## {c['cid']}（{c['score']}，{c['n_items']} 条 / {c['n_sources']} 个源）{c['title']}")
        L.append(f"- {c['source']}（{c['tier']}）· {c['published_cst'] or '无日期'} · {c['url']}")
        if c["others"]:
            L.append("- 旁证：" + "；".join(f"{o['source']}：{o['title'][:40]}" for o in c["others"]))
        if c["summary"]:
            L.append(f"- 摘要：{c['summary'][:200]}")
        L.append("")
    path.write_text("\n".join(L), encoding="utf-8")


# ---------------------------------------------------------------- health
def write_health(con):
    cfg = yaml.safe_load(open(HERE / "sources.yaml", encoding="utf-8"))
    rows = {r[0]: r for r in con.execute("SELECT source, last_ok_utc, last_fail_utc, fails, last_error, last_count, newest_utc, via FROM health")}
    t = now_utc()
    L = ["# 来源健康", "", f"更新：{t.astimezone(CST):%Y-%m-%d %H:%M} 北京时间", "", "| 源 | 状态 | 最新条目 | 备注 |", "|---|---|---|---|"]
    for s in cfg["sources"]:
        r = rows.get(s["id"])
        if not r:
            L.append(f"| {s['name']} | 还没抓过 | | |")
            continue
        newest = parse_dt(r[6])
        age = f"{(t - newest).total_seconds() / 86400:.1f} 天前" if newest else "无日期"
        state = "正常" if not r[3] else f"连续失败 {r[3]} 次"
        stale = newest and (t - newest).days > 30 and s["tier"] in ("official", "community")
        note = (r[4] or "")[:80] + ("；超过 30 天没更新，脚本可能停了" if stale else "")
        L.append(f"| {s['name']} | {state} | {age} | {note} |")
    HEALTH_DIR.mkdir(exist_ok=True)
    (HEALTH_DIR / "health.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def health(args):
    con = db()
    write_health(con)
    print((HEALTH_DIR / "health.md").read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("collect")
    a.add_argument("--only", help="只抓这些源（逗号分隔的 id）")
    a.add_argument("-v", "--verbose", action="store_true")
    b = sub.add_parser("export")
    b.add_argument("episode_dir")
    b.add_argument("--hours", type=float, help="不按上次导出时间，取最近 N 小时入库的条目")
    b.add_argument("--since", help="从这个时间起（ISO 格式）")
    b.add_argument("--no-commit", action="store_true", help="不推进“上次导出时间”（试跑用）")
    sub.add_parser("health")
    args = ap.parse_args()
    {"collect": collect, "export": export, "health": health}[args.cmd](args)


if __name__ == "__main__":
    main()
