# -*- coding: utf-8 -*-
"""系列的页面录屏素材：一次把 Substack 文章各段、作者主页、X 推文卡片截成高清长图，并算出 series_data.py 里所有高亮点在图里的位置。

  python capture_series_pages.py              全部重截
  python capture_series_pages.py A_1 P_bio    只截指定的几张
输出：D:\\大疆\\独立视频\\素材\\2026-10_TimDenning38岁忠告\\页面\\<key>.png + pages.json（和技能引擎的 capture_pages.py 同一个格式：src / w / h / url / bg / marks）。

视口 640 CSS 宽、2.4 倍像素（图宽 1536，比素材框的 1474 略宽，缩进框里是清晰的）；Substack 页面在 640 宽下字更大（正文 17 px、标题约 30 px），竖屏里读得清。
页面都是公开页面（不用登录）：timdenning.substack.com 文章、substack.com/@timdenning 作者主页、platform.twitter.com 的推文嵌入页（X 长文本身在无头浏览器里是登录墙）。
"""
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import series_data as D  # noqa: E402

OUT = D.MAT / "页面"
DSF, VW = 2.4, 640

# 找 / 画高亮：和技能引擎 capture_pages.py 的 MARK_JS 同一套（普通子串，大小写和撇号不敏感；找不到整段文字节点时退回“包含这句话的最小块”）
MARK_JS = r"""
([needle, y0, y1]) => {
  // 把页面里所有文字节点按文档顺序拼成一个长串（1:1 替换撇号 / 引号 / 不换行空格，不改长度），在长串里找 needle，再映射回 Range。
  // 这样 <em> / <strong> / 链接把一句话切成几个节点也找得到。
  const f1 = s => s.replace(/[’‘]/g, "'").replace(/[“”]/g, '"').replace(/ /g, ' ').toLowerCase();
  const nl = f1(needle);
  const nodes = [];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n, full = '';
  while ((n = w.nextNode())) { nodes.push({n, s: full.length}); full += f1(n.textContent); }
  let from = 0;
  while (true) {
    const i = full.indexOf(nl, from);
    if (i < 0) break;
    from = i + 1;
    const e = i + nl.length;
    const a = nodes.findLast(x => x.s <= i), z = nodes.findLast(x => x.s < e);
    if (!a || !z) continue;
    const r = document.createRange();
    r.setStart(a.n, i - a.s); r.setEnd(z.n, e - z.s);
    const rects = [...r.getClientRects()].map(q => [q.left + window.scrollX, q.top + window.scrollY, q.width, q.height]).filter(q => q[2] > 2 && q[3] > 2);
    if (rects.length && rects[0][1] >= y0 - 2 && rects[0][1] <= y1) return {kind: 'range', rects};
  }
  // 回退：区域里最小的、文字包含 needle 的块元素
  const norm2 = s => f1(s.replace(/​/g, '').replace(/\s+/g, ' '));
  let best = null;
  for (const el of document.querySelectorAll('p,li,td,th,pre,code,h1,h2,h3,h4,div,a,span,blockquote,time')) {
    const t = norm2(el.textContent || '');
    if (!t.includes(nl)) continue;
    const r = el.getBoundingClientRect();
    const top = r.top + window.scrollY;
    if (r.width < 4 || r.height < 4 || top < y0 - 2 || top > y1) continue;
    if (!best || t.length < best.len) best = {len: t.length, rect: [r.left + window.scrollX, top, r.width, r.height]};
  }
  return best ? {kind: 'block', rects: [best.rect]} : null;
}
"""

# 找以某段文字开头的 <p>：返回 [段顶, 第 N 行的底]（N = 0 → 整段的底）
PARA_JS = r"""
([starts, nlines]) => {
  const f = s => s.replace(/[’‘]/g, "'").replace(/\u00a0/g, ' ').trim().toLowerCase();
  const p = [...document.querySelectorAll('p')].find(x => f(x.textContent).startsWith(f(starts)));
  if (!p) throw new Error('找不到段落：' + starts);
  const r = document.createRange(); r.selectNodeContents(p);
  const rects = [...r.getClientRects()].filter(q => q.width > 2 && q.height > 2).map(q => [q.top + scrollY, q.bottom + scrollY]);
  const tops = [];
  for (const [t, b] of rects) { const k = tops.find(x => Math.abs(x.t - t) < 3); if (k) k.b = Math.max(k.b, b); else tops.push({t, b}); }
  tops.sort((a, b) => a.t - b.t);
  const pr = p.getBoundingClientRect();
  const use = nlines ? tops.slice(0, nlines) : tops;
  return [pr.top + scrollY, Math.max(...use.map(x => x.b))];
}
"""

H1_JS = """() => [...document.querySelectorAll('h1,h3')].map(h => [h.tagName, Math.round(h.getBoundingClientRect().top + scrollY), h.textContent.trim()])"""


def needles_by_key():
    d = {}
    for ep in D.EPISODES:
        for sc in ep["scenes"]:
            sh = sc["shot"]
            if sh["kind"] == "page":
                for m in sh["marks"]:
                    d.setdefault(sh["key"], [])
                    if m["needle"] not in d[sh["key"]]:
                        d[sh["key"]].append(m["needle"])
    return d


def scroll_through(pg):
    H = pg.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < H:
        pg.evaluate(f"window.scrollTo(0, {y})")
        pg.wait_for_timeout(80)
        y += 700
    pg.evaluate("window.scrollTo(0, 0)")
    pg.wait_for_timeout(500)


def main():
    from PIL import Image
    only = sys.argv[1:] or list(D.PAGES)
    OUT.mkdir(parents=True, exist_ok=True)
    meta_file = OUT / "pages.json"
    meta = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
    nd = needles_by_key()
    with sync_playwright() as p:
        b = p.chromium.launch()

        def ctx_page(url, wait=3000, vw=VW):
            ctx = b.new_context(viewport={"width": vw, "height": 1000}, device_scale_factor=DSF, locale="en-US")
            pg = ctx.new_page()
            try:
                pg.goto(url, wait_until="networkidle", timeout=60000)
            except Exception as e:
                print(url, "goto:", str(e)[:100])
            pg.wait_for_timeout(wait)
            return ctx, pg

        def shoot(key, pg, clip, shown_url):
            f = OUT / f"{key}.png"
            pg.screenshot(path=str(f), clip=clip, full_page=True)
            ms = {}
            for needle in nd.get(key, []):
                r = pg.evaluate(MARK_JS, [needle, clip["y"], clip["y"] + clip["height"]])
                if not r:
                    print(f"  {key}: 没找到「{needle}」")
                    continue
                ms[needle] = [[round((x - clip["x"]) * DSF), round((yy - clip["y"]) * DSF), round(w * DSF), round(h * DSF)] for x, yy, w, h in r["rects"]]
                if r["kind"] == "block":
                    print(f"  {key}: 「{needle[:40]}」退回整块高亮（跨了多个文字节点）")
            im = Image.open(f).convert("RGB")
            bg = "#%02X%02X%02X" % im.getpixel((6, im.height - 6))
            meta[key] = {"src": f"pages/{key}.png", "w": im.width, "h": im.height, "url": shown_url, "bg": bg, "marks": ms}
            print(f"{key}: {im.width}×{im.height}，高亮 {len(ms)}/{len(nd.get(key, []))}（y {clip['y']:.0f}–{clip['y'] + clip['height']:.0f}）")

        # ── Substack 文章：一次打开，按标题位置切段
        art_all = [k for k in only if D.PAGES[k]["kind"] in ("top", "short", "lesson", "li_range", "para_lines")]
        groups = {}
        for k in art_all:                                                   # 按视口宽度分组（单句片段用 420 宽，其余 640）
            groups.setdefault(D.PAGES[k].get("vw", VW), []).append(k)
        for vw_, art_keys in groups.items():
            ctx, pg = ctx_page(D.SUB_URL, 3000, vw_)
            scroll_through(pg)
            heads = pg.evaluate(H1_JS)                                  # [tag, y, text]
            lessons = {}
            for tag, y, t in heads:
                m = re.match(r"^(\d+)\.\s", t)
                if tag == "H1" and m and y > 1000:                         # H3 是顶部的副标题（和第 1 条同文），H1 才是正文里的标题
                    lessons[int(m.group(1))] = y
            short_y = next(y for tag, y, t in heads if tag == "H1" and t.strip() == "Shorter lessons")
            order = sorted(lessons.items())
            nxt = {}
            for (n, y), (n2, y2) in zip(order, order[1:]):
                nxt[n] = y2
            nxt[max(lessons)] = pg.evaluate("document.documentElement.scrollHeight") - 600
            print("标题位置：", {n: y for n, y in order}, "shorter:", short_y)
            for k in art_keys:
                spec = D.PAGES[k]
                if spec["kind"] == "top":
                    y0, y1 = 0, lessons[1] - 8
                elif spec["kind"] == "short":
                    y0, y1 = short_y - 24, lessons[32] - 8
                elif spec["kind"] == "para_lines":                             # 某一段的前 N 行（lines = None 整段）
                    top, bot = pg.evaluate(PARA_JS, [spec["starts"], spec["lines"] or 0])
                    y0, y1 = top - 10, bot + 1
                elif spec["kind"] == "li_range":                              # “Shorter lessons”列表里的单条（或前两条）：按 li 的位置裁
                    a = pg.evaluate("(p) => { const li = [...document.querySelectorAll('li')].find(x => x.textContent.trim().startsWith(p)); const r = li.getBoundingClientRect(); return [r.top + scrollY, r.bottom + scrollY]; }", spec["first"])
                    z = pg.evaluate("(p) => { const li = [...document.querySelectorAll('li')].find(x => x.textContent.trim().startsWith(p)); const r = li.getBoundingClientRect(); return [r.top + scrollY, r.bottom + scrollY]; }", spec["last"])
                    y0 = (short_y - 24) if spec.get("head") else a[0] - 8
                    y1 = z[1] + 6
                else:
                    n = spec["n"]
                    y0 = lessons[n] - 24
                    y1 = min(nxt[n] - 8, y0 + 2600)
                    if spec.get("h"):
                        y1 = y0 + spec["h"]
                    if spec.get("until"):                                     # 截到某一段的底下（避开后面带敏感词的段落）
                        y1 = pg.evaluate(PARA_JS, [spec["until"], 0])[1] + 14
                    if n == 20:                                              # 20 条后面接 “Shorter lessons”
                        y1 = short_y - 8
                    if n == 36:                                              # 最后一条：只要这条本身（后面是订阅页脚 / 评论）
                        y1 = y0 + 540
                shoot(k, pg, {"x": 0, "y": y0, "width": vw_, "height": y1 - y0}, D.SUB_URL)
            ctx.close()

        # ── 作者主页
        if "P_bio" in only:
            ctx, pg = ctx_page(D.PROFILE_URL, 3500)
            shoot("P_bio", pg, {"x": 0, "y": 0, "width": VW, "height": D.PAGES["P_bio"]["h"]}, D.PROFILE_URL)
            ctx.close()

        # ── 推文卡片（X 嵌入页，按 article 外框截）
        if "X_t1" in only:
            ctx, pg = ctx_page(D.EMBED_URL, 3500)
            el = pg.locator("article").first
            bb = el.bounding_box()
            sy = pg.evaluate("window.scrollY")
            shoot("X_t1", pg, {"x": bb["x"], "y": bb["y"] + sy, "width": bb["width"], "height": bb["height"]}, D.TWEET_SHOW_URL)
            ctx.close()
        b.close()
    meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print("->", meta_file)


if __name__ == "__main__":
    main()
