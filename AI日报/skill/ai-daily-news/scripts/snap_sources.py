"""Screenshot the headline area of every news item's source page and put it into the episode.

    python snap_sources.py <期目录> [--force] [--show]

For each news item the page is 台本.json news[i].snap_url if given, else the first ref that opens with an <h1>.
Headless Chromium (1280x900 CSS px, scale 1.5) loads it, hides pictures / video / iframes, cookie and
subscribe overlays and sticky bars, scrolls the first visible <h1> to the top and clips about 1000x560 CSS px:
headline + byline + the first lines. Pictures are hidden on purpose: we quote the headline with attribution,
we do not reproduce news photos. Pages that block headless browsers, or have no <h1>, are skipped; that scene
then uses the plain one-column layout.

Writes 制作/assets/snaps/news_NN.png + snaps.json, and patches episode.json news[i].snap / snap_src
(paths relative to 制作/engine/, where the page runs). Re-runs keep existing shots of unchanged URLs (--force redoes).
Run after make_episode.py (daily.py build does), before build_timeline.py.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
HIDE_CSS = """
img, picture, video, iframe, canvas, figure, object, embed { visibility: hidden !important; }
[id*="cookie" i], [class*="cookie" i], [id*="consent" i], [class*="consent" i], [class*="gdpr" i], [id*="onetrust" i],
[class*="onetrust" i], [class*="newsletter" i], [class*="paywall" i], [class*="subscribe" i], [class*="modal" i],
[class*="popup" i], [aria-modal="true"], [role="dialog"], [class*="toast" i], [class*="banner-ad" i] { display: none !important; }
header, nav, [class*="sticky" i], [class*="fixed" i], [style*="position: fixed"], [style*="position:fixed"] { position: static !important; }
/* 侧栏（排行榜、热门、推荐）：和本条新闻无关，AI 复核 2026-09-27 发现 IT之家「日榜」、量子位「热门文章」被截进画面 */
aside, [role="complementary"], [class*="sidebar" i], [id*="sidebar" i], [class*="side-bar" i], [class*="rank" i], [id*="rank" i],
[class*="hotlist" i], [class*="hot-list" i], [class*="hot_list" i], [class*="hotnews" i], [class*="hot-news" i],
[class*="recommend" i], [class*="related" i], [class*="trending" i], [class*="popular" i] { display: none !important; }
html, body { overflow: visible !important; }
/* 常见 cookie 同意框的宿主（很多装在 shadow DOM 里，CSS 只能藏宿主）：consentmanager、Usercentrics、Sourcepoint、Quantcast、Didomi、Funding Choices */
#cmpwrapper, #cmpbox, #cmpbox2, .cmpboxBG, #usercentrics-root, #usercentrics-cmp-ui, [id^="sp_message_container"],
#qc-cmp2-container, .qc-cmp2-container, .fc-consent-root, #didomi-host, [class*="didomi" i] { display: none !important; }
"""
HIDE_OVERLAYS_JS = """() => {
    const vw = innerWidth, vh = innerHeight;
    const big = el => { const cs = getComputedStyle(el); if (cs.position !== 'fixed' && cs.position !== 'sticky') return false;
                        const r = el.getBoundingClientRect(); return r.width * r.height > vw * vh * 0.25; };
    for (const el of document.querySelectorAll('body *')) {
        if (big(el)) { el.style.setProperty('display', 'none', 'important'); continue; }
        // 同意框装在 shadow DOM 里时，宿主本身不大：看里面有没有大的固定层，有就藏宿主
        if (el.shadowRoot && [...el.shadowRoot.querySelectorAll('*')].some(big)) el.style.setProperty('display', 'none', 'important');
    }
    document.documentElement.style.setProperty('overflow', 'visible', 'important');
    document.body.style.setProperty('overflow', 'visible', 'important');
}"""
BLOCKED = ("just a moment", "access denied", "attention required", "are you a robot", "verify you are human", "请完成安全验证")
CLIP_W, CLIP_H = 1000, 560


def shoot(page, url, out_png):
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2500)
    title = (page.title() or "").lower()
    if any(b in title for b in BLOCKED):
        raise RuntimeError(f"被拦截（{page.title()[:30]}）")
    page.add_style_tag(content=HIDE_CSS)
    # 遮住大半个画面的固定层（cookie 同意框、灰色遮罩、订阅弹窗）一律藏掉，不点“同意”。
    # 2026-09-28 The Decoder 的同意框类名对不上上面的 CSS，截图被盖住大半（AI 复核发现）。吸顶栏面积小，不受影响。
    page.evaluate(HIDE_OVERLAYS_JS)
    page.wait_for_timeout(400)
    h1 = None
    for el in page.locator("h1").all()[:6]:
        try:
            if el.is_visible() and (el.inner_text() or "").strip():
                h1 = el
                break
        except Exception:  # noqa: BLE001
            continue
    if h1 is None:
        raise RuntimeError("页面里没有可见的 <h1>")
    h1.evaluate("el => window.scrollTo(0, Math.max(0, el.getBoundingClientRect().top + window.scrollY - 70))")
    page.wait_for_timeout(500)
    box = h1.bounding_box()
    vw = page.viewport_size["width"]
    # 只截正文那一栏：从标题往外找最宽、但不超过版面 72% 的祖先（侧栏在它外面）
    col = h1.evaluate("""el => { const vw = window.innerWidth, hw = el.getBoundingClientRect().width; let a = el, best = el;
        while (a && a !== document.body) { const r = a.getBoundingClientRect(); if (r.width >= hw && r.width <= vw * 0.72) best = a; a = a.parentElement; }
        const r = best.getBoundingClientRect(); return {left: r.left, right: r.right}; }""")
    left, right = max(0, col["left"] - 24), min(vw, col["right"] + 24)
    w = min(vw, CLIP_W, max(right - left, box["width"] + 80))
    x = max(0, min(left if right - left >= box["width"] else box["x"] - 40, vw - w))
    y = max(0, box["y"] - 50)
    page.evaluate(HIDE_OVERLAYS_JS)              # 截图前再藏一次：同意框常常过几秒才弹出来
    page.wait_for_timeout(200)
    page.screenshot(path=str(out_png), clip={"x": x, "y": y, "width": w, "height": CLIP_H})
    return (h1.inner_text() or "").strip()[:80]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dir")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--show", action="store_true", help="非无头模式（调试用）")
    args = ap.parse_args()
    ep = Path(args.episode_dir).resolve()
    sc = json.loads((ep / "台本.json").read_text(encoding="utf-8"))
    ep_path = ep / "episode.json"
    episode = json.loads(ep_path.read_text(encoding="utf-8"))
    out_dir = ep / "制作" / "assets" / "snaps"
    out_dir.mkdir(parents=True, exist_ok=True)
    idx_path = out_dir / "snaps.json"
    idx = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else {}
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.show)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1.5, user_agent=UA,
                                  locale="zh-CN", extra_http_headers={"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"})
        for i, n in enumerate(sc["news"], 1):
            png = out_dir / f"news_{i:02d}.png"
            cands = [n["snap_url"]] if n.get("snap_url") else [r["url"] for r in n.get("refs") or [] if r.get("url") and "news.google.com" not in r["url"]]
            prev = idx.get(str(i))
            if prev and prev.get("ok") and prev.get("url") in cands and png.exists() and not args.force:
                results[str(i)] = prev
                print(f"  {i}. 沿用 {prev['url'][:70]}")
                continue
            res = {"ok": False, "tried": []}
            for url in cands:
                page = ctx.new_page()
                t0 = time.time()
                try:
                    h1 = shoot(page, url, png)
                    res = {"ok": True, "url": url, "h1": h1, "file": png.name, "domain": urlsplit(url).netloc.removeprefix("www."),
                           "sha": hashlib.sha1(png.read_bytes()).hexdigest()[:10]}
                    print(f"  {i}. ✓ {res['domain']}（{time.time() - t0:.1f}s）「{h1[:40]}」")
                    break
                except Exception as e:  # noqa: BLE001 - try the next source of this item
                    res["tried"].append({"url": url, "error": str(e)[:120]})
                    print(f"  {i}. ✗ {url[:70]}：{str(e)[:80]}")
                finally:
                    page.close()
            results[str(i)] = res
        browser.close()
    idx_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for i, n in enumerate(episode.get("news") or [], 1):
        r = results.get(str(i)) or {}
        if r.get("ok"):
            n["snap"] = f"../assets/snaps/{r['file']}"
            n["snap_src"] = r["domain"]
        else:
            n.pop("snap", None)
            n.pop("snap_src", None)
    ep_path.write_text(json.dumps(episode, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for r in results.values() if r.get("ok"))
    print(f"截图 {ok}/{len(results)} 条 -> {out_dir}；episode.json 已更新")


if __name__ == "__main__":
    main()
