# -*- coding: utf-8 -*-
"""录官方页面和官方推文：用 Playwright（viewport 800 宽、2 倍像素 → 图宽 1600；推文是它自己的宽度）把要讲的小节截成高清长图，并算出要高亮的那句话在图里的位置。
输出 media/pages/<名字>.png + pages.js（window.PG = {名字: {src, w, h, url, bg, marks: {句子: [[x,y,w,h], …]}}}，坐标是图片像素）。

  python capture_pages.py            全部重录
  python capture_pages.py T_open …   只录指定的几张

视频里（scenes.js 的 pageShot）按解说时刻把图往上滚、给对应的句子刷上荧光笔，就像在录屏。
页面都是公开页面：claude.dev、code.claude.com 文档；推文用 X 的公开嵌入页（platform.twitter.com/embed/Tweet.html?id=…，不用登录），截的是官方推文本身，浏览器顶栏里显示的是它在 x.com 上的网址。
每张图只截要讲的那一小段（约 450–900 CSS 像素高），不整页放。
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "media" / "pages"
DSF = 2
VW = 800

EMB ="https://platform.twitter.com/embed/Tweet.html?id={}&theme=light&hideThread=true&lang=en&dnt=true"
T_ART = "2106639522586829094"    # @AYi_AInotes 的万字长文（X Article 卡片，10-04 06:56 UTC）
T_AYI = "2106649320179032146"    # @AYi_AInotes 的长推文（引用文章，10-04 07:35 UTC）
T_LW1 = "2106665574067761626"    # @LawrenceW_Zen 买号商账号的经历和结论（10-04 08:39 UTC）
T_LW2 = "2106752929139159401"    # @LawrenceW_Zen 的总结（10-04 14:26 UTC）

# 名字: (页面, 起点文字, 高度 CSS px, 起点上方留白, [要高亮的句子])
#   起点文字以 # 开头 = 只在 h1–h4 里找这个标题；"@top" = 从页面最顶上截起；X_ 开头的是推文（起点文字不用，高度写 "after:某句话" = 截到这句话下面，写 0 = 整条推文）
#   要高亮的写法：普通句子 = 按文字找；"@@文字" = 高亮它所在的整个段落块；"#sel:选择器" = 整块画框；(别名, 查找写法) = scenes.js 里用别名
QDIR = "file:///" + str(HERE / "quotes").replace("\\", "/")
SPECS = {
    # 推文嵌入页（真截图；长推文只露开头几行，关键句在 Show more 后面，所以关键句另做 Q_ 引用卡）
    "X_ayi": (EMB.format(T_AYI), "", 0, 0, [("ayi_hot", "封号潮来得极其凶猛")]),
    # 原帖节选卡（make_quotes.py 生成的本地 HTML，原文一字不改）
    "Q_ayi": (f"{QDIR}/Q_ayi.html", "@top", 560, 0, [("ayi_hot", "封号潮来得极其凶猛"), ("ayi_old", "老号、刚充了 Max 的开发者账号全被一锅端"), ("ayi_tz", "时区撕裂、WebRTC 泄漏以及终端命令行里残留的系统代理")]),
    "Q_lw": (f"{QDIR}/Q_lw.html", "@top", 525, 0, [("lw_caveat", "时效性跟有效性自行判断"), ("lw_tz", "IP、时区无所谓")]),
    "Q_scmp": (f"{QDIR}/Q_scmp.html", "@top", 330, 0, [("head", "Hong Kong users caught off guard as Anthropic tightens VPN access to Claude")]),
    # 官方页面（真页面，Playwright 直接截）
    "R_sept": ("https://www.anthropic.com/threat-intelligence-report-september-2026", "#How we address illicit distillation", 1010, 10,
               [("resale", "unauthorized resale of Claude"), ("cn", "unsupported countries like China, Russia, and Iran"),
                ("verify", "require users to verify their identity to retain access"), ("banned", "Accounts that fail to do so are banned")]),
    "R_refund": ("https://support.claude.com/en/articles/12386328-request-a-refund-for-a-paid-claude-plan", "#Request a refund for a paid Claude plan", 560, 30,
                 [("except", "Except as expressly provided in our Consumer Terms of Service or where required by law"), ("nonrefund", "all payments are non-refundable")]),
}
SHOW_URL = {"X_ayi": f"https://x.com/AYi_AInotes/status/{T_AYI}",
            "Q_ayi": f"原帖节选 · x.com/AYi_AInotes/status/{T_AYI}", "Q_lw": f"原帖节选 · x.com/LawrenceW_Zen/status/{T_LW1}",
            "Q_scmp": "报道标题 · scmp.com/tech/tech-war/article/3369526"}

FIND_JS = """
(needle) => {
  const nl = needle.toLowerCase().replace(/[’']/g, "'");
  const norm = s => s.replace(/\\s+/g, ' ').toLowerCase().replace(/[’']/g, "'");
  // 最小的、文字包含 needle 的元素的上边（页面坐标）
  let best = null;
  for (const el of document.querySelectorAll('h1,h2,h3,h4,p,li,td,th,pre,code,div,span,a,article')) {
    const t = norm(el.textContent || '');
    if (!t.includes(nl)) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) continue;
    if (!best || t.length < best.len) best = {len: t.length, top: r.top + window.scrollY, left: r.left + window.scrollX, w: r.width, h: r.height};
  }
  return best;
}
"""

FIND_HEAD_JS = """
(needle) => {
  const norm = s => s.replace(/[​]/g, '').replace(/\\s+/g, ' ').trim().toLowerCase().replace(/[’']/g, "'");
  const nl = norm(needle);
  for (const el of document.querySelectorAll('h1,h2,h3,h4')) {
    if (norm(el.textContent || '') !== nl) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) continue;
    return {len: 0, top: r.top + window.scrollY, left: r.left + window.scrollX, w: r.width, h: r.height};
  }
  return null;
}
"""

MARK_JS = """
([needle, y0, y1]) => {
  if (needle.startsWith('#sel:')) {                          // #sel:选择器 = 区域里第一个够大的这个元素（例：图表）
    for (const el of document.querySelectorAll(needle.slice(5))) {
      const b = el.getBoundingClientRect(), top = b.top + window.scrollY;
      if (b.width > 60 && b.height > 60 && top >= y0 - 2 && top <= y1) return {kind: 'block', rects: [[b.left + window.scrollX, top, b.width, b.height]]};
    }
    return null;
  }
  if (needle === '@time') {                                  // GitHub 提交行里的相对时间（relative-time 的文字在 shadow DOM 里，按文字找不到）
    for (const el of document.querySelectorAll('relative-time')) {
      const b = el.getBoundingClientRect(), top = b.top + window.scrollY;
      if (b.width > 20 && top >= y0 - 2 && top <= y1) return {kind: 'range', rects: [[b.left + window.scrollX, top, b.width, b.height]]};
    }
    return null;
  }
  if (needle.startsWith('@css:')) {                          // @css:选择器 = 区域里第一个匹配的元素（链接、按钮这类小元素也行）
    for (const el of document.querySelectorAll(needle.slice(5))) {
      const b = el.getBoundingClientRect(), top = b.top + window.scrollY;
      if (b.width > 8 && b.height > 8 && top >= y0 - 2 && top <= y1) return {kind: 'range', rects: [[b.left + window.scrollX, top, b.width, b.height]]};
    }
    return null;
  }
  if (needle.startsWith('@row:')) {                          // @row:行里的文字|格子里的文字 = 表里这一行的这个格子（几行都有同一句话时用）
    const [rowKey, cellKey] = needle.slice(5).split('|');
    const nz = s => (s || '').replace(/\\s+/g, ' ').toLowerCase();
    for (const tr of document.querySelectorAll('tr')) {
      if (!nz(tr.textContent).includes(nz(rowKey))) continue;
      for (const td of tr.querySelectorAll('td,th')) {
        if (nz(td.textContent).includes(nz(cellKey)) && nz(td.textContent).length < nz(cellKey).length + 12) {
          const b = td.getBoundingClientRect();
          return {kind: 'block', rects: [[b.left + window.scrollX, b.top + window.scrollY, b.width, b.height]]};
        }
      }
    }
    return null;
  }
  const blockOnly = needle.startsWith('@@');
  if (blockOnly) needle = needle.slice(2);
  const nl = needle.toLowerCase().replace(/[’']/g, "'");
  const norm = s => s.toLowerCase().replace(/[’']/g, "'");
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while (!blockOnly && (n = w.nextNode())) {
    const t = norm(n.textContent);
    const i = t.indexOf(nl);
    if (i < 0) continue;
    const r = document.createRange(); r.setStart(n, i); r.setEnd(n, Math.min(n.textContent.length, i + needle.length));
    const rects = [...r.getClientRects()].map(q => [q.left + window.scrollX, q.top + window.scrollY, q.width, q.height]).filter(q => q[2] > 2 && q[3] > 2);
    if (rects.length && rects[0][1] >= y0 - 2 && rects[0][1] <= y1) {
      if (blockOnly) {                                           // @@：高亮这句话所在的整个段落块
        const el = n.parentElement.closest('p,li,td,th,pre,blockquote,div');
        if (el) { const b = el.getBoundingClientRect(); return {kind: 'block', rects: [[b.left + window.scrollX, b.top + window.scrollY, b.width, b.height]]}; }
      }
      return {kind: 'range', rects};
    }
  }
  // 回退：区域里最小的、文字包含 needle 的块元素
  const norm2 = s => s.replace(/​/g, '').replace(/\\s+/g, ' ').toLowerCase().replace(/[’']/g, "'");
  let best = null;
  for (const el of document.querySelectorAll('p,li,td,th,pre,code,h1,h2,h3,h4,div,a,span')) {
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


def main():
    from PIL import Image
    only = sys.argv[1:] or list(SPECS)
    OUT.mkdir(parents=True, exist_ok=True)
    meta_file = HERE / "pages.json"
    meta = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
    by_url = {}
    for k in only:
        by_url.setdefault(SPECS[k][0], []).append(k)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for url, keys in by_url.items():
            ctx = b.new_context(viewport={"width": VW, "height": 1000}, device_scale_factor=DSF, locale="en-US")
            pg = ctx.new_page()
            try:
                pg.goto(url, wait_until="networkidle", timeout=60000)
            except Exception as e:
                print(url, "goto:", str(e)[:100])
            pg.wait_for_timeout(2500)
            pg.evaluate("document.fonts.ready.then(() => true)")
            H = pg.evaluate("document.documentElement.scrollHeight")
            y = 0
            while y < H:                                   # 滚一遍触发懒加载
                pg.evaluate(f"window.scrollTo(0, {y})")
                pg.wait_for_timeout(100)
                y += 700
            pg.evaluate("window.scrollTo(0, 0)")
            pg.wait_for_timeout(600)
            H = pg.evaluate("document.documentElement.scrollHeight")
            for k in keys:
                _, anchor, height, pad, marks = SPECS[k]
                if k.startswith("X_"):                     # 推文：按 article 的外框截，宽度是推文自己的
                    el = pg.locator("article").first
                    if el.count() == 0:
                        print(k, "找不到推文，跳过"); continue
                    bb = el.bounding_box()
                    sy = pg.evaluate("window.scrollY")
                    y0, hh = bb["y"] + sy, bb["height"]
                    if isinstance(height, str) and height.startswith("after:"):
                        r = pg.evaluate(MARK_JS, [height[6:], 0, 99999])
                        if r:
                            hh = max(yy + h for _, yy, _, h in r["rects"]) - y0 + 30
                    clip = {"x": bb["x"], "y": y0, "width": bb["width"], "height": hh}
                else:
                    # 视口截图（2026-10-05 Claude 封号潮那条改的）：整页截图遇到很长的页面（9 月报告 15 万像素高）时 Playwright 会把视口撑到整页高、页面跟着重排，
                    # 图里的布局和之后量出来的高亮位置对不上（高亮整体偏了一段）。改成：先把视口设成“要截的高度 + 80”，在这个视口下量起点和高亮，再滚到起点、隐藏悬浮 / 吸顶元素，按视口截图。
                    pg.set_viewport_size({"width": VW, "height": max(1000, int(height) + 80)})
                    pg.wait_for_timeout(1200)
                    H = pg.evaluate("document.documentElement.scrollHeight")
                    a = {"top": 0} if anchor == "@top" else pg.evaluate(FIND_HEAD_JS, anchor[1:]) if anchor.startswith("#") else pg.evaluate(FIND_JS, anchor)
                    if not a:
                        print(k, f"找不到起点文字：{anchor}"); continue
                    y0 = max(0, a["top"] - pad)
                    hh = min(height, H - y0)
                    pg.evaluate("() => { for (const el of document.querySelectorAll('*')) { const p = getComputedStyle(el).position; if (p === 'fixed' || p === 'sticky') el.style.visibility = 'hidden'; } }")
                    pg.evaluate("document.documentElement.style.scrollBehavior = 'auto'; document.body.style.scrollBehavior = 'auto'")      # 有的站 CSS 写了 smooth，scrollTo 会慢慢滚，读到的 scrollY 是半路的
                    pg.evaluate(f"window.scrollTo({{top: {y0}, left: 0, behavior: 'instant'}})")
                    pg.wait_for_timeout(900)
                    sy = pg.evaluate("window.scrollY")
                    print(f"  {k}: y0={y0:.0f} scrollY={sy:.0f} H={H} hh={hh:.0f}")
                    clip = {"x": 0, "y": y0 - sy, "width": VW, "height": hh}
                f = OUT / f"{k}.png"
                if k.startswith("X_"):
                    pg.screenshot(path=str(f), clip=clip, full_page=True)
                else:
                    pg.screenshot(path=str(f), clip=clip)
                ms = {}
                for m in marks:
                    key, needle = m if isinstance(m, (tuple, list)) else (m, m)      # (别名, 查找写法)：scenes.js 里用别名
                    r = pg.evaluate(MARK_JS, [needle, y0, y0 + hh])
                    if not r:
                        print(f"  {k}: 没找到要高亮的句子「{key}」")
                        continue
                    ms[key] = [[round((x - clip['x']) * DSF), round((yy - y0) * DSF), round(w * DSF), round(h * DSF)] for x, yy, w, h in r["rects"]]
                _im = Image.open(f).convert("RGB")
                bg = "#%02X%02X%02X" % _im.getpixel((6, _im.height - 6))
                meta[k] = {"src": f"pages/{k}.png", "w": _im.width, "h": _im.height, "url": SHOW_URL.get(k, url), "bg": bg, "marks": ms}
                print(f"{k}: {_im.width}×{_im.height}，高亮 {len(ms)}/{len(marks)}（起点 y={y0:.0f}）")
            ctx.close()
        b.close()
    meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "pages.js").write_text("window.PG = " + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main()
