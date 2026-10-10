"""Probe candidate feeds with the same HTTP settings and parser as collect.py.

    python probe.py <candidates.py> [--out result.json]

candidates.py defines CANDS = [(group, id, name, url), ...]
"""
import importlib.util, json, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from pathlib import Path

COLLECTOR = Path(r"D:\大疆\AI日报\collector")
sys.path.insert(0, str(COLLECTOR))
import httpx  # noqa: E402
import collect as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def load(path):
    spec = importlib.util.spec_from_file_location("cands", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.CANDS


def probe(c):
    group, sid, name, url = c[:4]
    t0 = time.time()
    res = dict(group=group, id=sid, name=name, url=url)
    try:
        cli = httpx.Client(follow_redirects=True, timeout=20, headers={
            "User-Agent": C.UA,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, application/json, text/html;q=0.9, */*;q=0.5",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"})
        r = cli.get(url)
        res["status"] = r.status_code
        res["final"] = str(r.url) if str(r.url) != url else ""
        res["ctype"] = r.headers.get("content-type", "")[:40]
        res["bytes"] = len(r.content)
        head = r.content[:3000].lower()
        if r.status_code != 200:
            res["err"] = f"HTTP {r.status_code}"
        elif b"<rss" not in head and b"<feed" not in head and b"<rdf" not in head and b"<?xml" not in head:
            res["err"] = "not xml: " + r.text[:60].replace("\n", " ")
        else:
            items = C.parse_feed(r.content)
            res["n"] = len(items)
            now = datetime.now(timezone.utc)
            ds = [C.parse_dt(i.get("published")) for i in items]
            ds = [d for d in ds if d]
            res["n_dated"] = len(ds)
            if ds:
                res["newest_h"] = round((now - max(ds)).total_seconds() / 3600, 1)
                res["oldest_d"] = round((now - min(ds)).total_seconds() / 86400, 1)
                res["last7d"] = sum(1 for d in ds if (now - d) < timedelta(days=7))
                res["last30d"] = sum(1 for d in ds if (now - d) < timedelta(days=30))
            res["with_summary"] = sum(1 for i in items if len(i.get("summary") or "") > 40)
            res["sample"] = [i["title"][:80] for i in items[:3]]
    except Exception as e:  # noqa: BLE001
        res["err"] = f"{type(e).__name__}: {str(e)[:80]}"
    res["secs"] = round(time.time() - t0, 1)
    return res


def main():
    cands = load(sys.argv[1])
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    with ThreadPoolExecutor(12) as ex:
        results = list(ex.map(probe, cands))
    last = None
    for r in results:
        if r["group"] != last:
            print(f"\n## {r['group']}")
            last = r["group"]
        if r.get("err"):
            print(f"  ✗ {r['id']:<26} {r['err'][:70]}   [{r['url'][:70]}]")
        else:
            nh = r.get("newest_h")
            age = "无日期" if nh is None else (f"{nh:.0f}h" if nh < 48 else f"{nh/24:.0f}d")
            print(f"  ✓ {r['id']:<26} {r['n']:>3}条 最新 {age:<6} 7d:{r.get('last7d','-'):<3} 30d:{r.get('last30d','-'):<3} 摘要:{r['with_summary']}/{r['n']} | {r['sample'][0] if r.get('sample') else ''}")
    if out:
        Path(out).write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
