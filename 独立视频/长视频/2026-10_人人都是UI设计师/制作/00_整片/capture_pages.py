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

# 20 条规则对应《Refactoring UI》官网目录里的章节（规则 11 对应两章，所以 21 个）
TOC_NAMES = ["Choose a personality", "Detail comes later", "Size isn’t everything", "De-emphasize to emphasize", "Labels are a last resort",
             "Semantics are secondary", "Start with too much white space", "You don’t have to fill the whole screen", "Avoid ambiguous spacing",
             "Relative sizing doesn’t scale", "Keep your line length in check", "Line-height is proportional", "Baseline, not center",
             "You need more colors than you think", "Accessible doesn’t have to mean ugly", "Don’t rely on color alone",
             "Add color with accent borders", "Text needs consistent contrast", "Everything has an intended size", "Use fewer borders",
             "Don’t overlook empty states"]
OUT = HERE / "media" / "pages"
DSF = 2
VW = 800

BOOK = "https://refactoringui.com/"
MOWEN = "https://note.mowen.cn/detail/4LZPmLxZzVh6ffGRzhlyi"
EMB = "https://platform.twitter.com/embed/Tweet.html?id={}&theme=light&hideThread=true&lang=zh-cn&dnt=true"
T1 = "2106216781174251724"                                         # 龙海的推文（2026-10-03）

# 名字: (页面, 起点文字, 高度 CSS px, 起点上方留白, [要高亮的句子])
#   起点文字以 # 开头 = 只在 h1–h4 里找这个标题；X_ 开头的是推文（起点文字不用，高度写 "after:某句话" = 截到这句话下面，写 0 = 整条推文）
#   高亮句子的写法：普通文字 = 页面里的原文子串（≤ 15 个词）；"@@文字" = 高亮它所在的整个段落块；"#sel:选择器" = 整块（图表）画框；
#   "@row:行里的字|格子里的字" = 表格里这一行的这个格子（好几行都有同一句话时点名取哪一格）
SPECS = {
    "X_t1": (EMB.format(T1), "", 0, 0, ["龙海", "默认 UI 丑陋依旧是硬伤", "2026年10月3日", "20 条设计军规"]),           # 推文（整条）
    # 书官网首屏：桌面宽度 1440 的真实首屏（顶栏三句话、标题、书封面）；@rect:x,y,w,h = 手动框选（CSS 像素，页面坐标）
    "Y_hero": (BOOK, "", 900, 0, ["creators of", "tailwind css", "@rect:1000,170,430,610", "@rect:1055,610,285,90"]),
    "Y_book": (BOOK, "#The Book", 640, 24, ["50 incredibly visual chapters", "200+ painstakingly typeset pages"]),   # 官网“The Book”一节
    "Y_tactics": (BOOK, "#Design with tactics, not talent.", 700, 30, ["Design with tactics, not talent.", "Use fewer borders.", "It doesn’t take any talent"]),
    "Y_toc": (BOOK, "#Full table of contents", 2780, 24, TOC_NAMES),                                                # 展开后的完整目录（50 章）
    "M_skill": (MOWEN, "", 1300, 0, ["把一本书做成随叫随到的 Skill", "做成了一个 Skill"]),                           # 墨问：文末彩蛋里那篇笔记
}
VWS = {"Y_hero": 1440, "M_skill": 900}                                    # 页面视口宽度（CSS 像素），默认 VW = 800
LOCALES = {"X_t1": "zh-CN", "M_skill": "zh-CN"}                           # 默认 en-US
PREP = {"Y_toc": "See all the chapters in the book"}                      # 截图前先点这个按钮（展开完整目录）
SHOW_URL = {"X_t1": "https://x.com/longhaiqwe123/status/" + T1}                                                  # 推文页面名 → 在浏览器顶栏里显示的 x.com 网址（嵌入页的网址不好看）：{"X_t1": f"https://x.com/ClaudeDevs/status/{T1}"}

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
    for k in only:                                   # 同一个页面、同一种视口 / 语言 / 预操作的合并成一次打开
        by_url.setdefault((SPECS[k][0], VWS.get(k, VW), LOCALES.get(k, "en-US"), PREP.get(k, "")), []).append(k)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for (url, vw, loc, prep), keys in by_url.items():
            ctx = b.new_context(viewport={"width": vw, "height": 1000}, device_scale_factor=DSF, locale=loc)
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
            if prep:                                       # 先点按钮（比如展开完整目录）
                btn = pg.get_by_text(prep).first
                btn.scroll_into_view_if_needed()
                btn.click()
                pg.wait_for_timeout(1500)
                pg.evaluate("window.scrollTo(0, 0)")
                pg.wait_for_timeout(300)
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
                    a = {"top": 0} if anchor == "" else (pg.evaluate(FIND_HEAD_JS, anchor[1:]) if anchor.startswith("#") else pg.evaluate(FIND_JS, anchor))
                    if not a:
                        print(k, f"找不到起点文字：{anchor}"); continue
                    y0 = max(0, a["top"] - pad)
                    hh = min(height, H - y0)
                    clip = {"x": 0, "y": y0, "width": vw, "height": hh}
                f = OUT / f"{k}.png"
                pg.screenshot(path=str(f), clip=clip, full_page=True)
                ms = {}
                for m in marks:
                    if m.startswith("@rect:"):                 # 手动框选：@rect:x,y,w,h（CSS 像素，页面坐标）
                        x, yy, w, h = [float(v) for v in m[6:].split(",")]
                        ms[m] = [[round((x - clip['x']) * DSF), round((yy - y0) * DSF), round(w * DSF), round(h * DSF)]]
                        continue
                    r = pg.evaluate(MARK_JS, [m, y0, y0 + hh])
                    if not r:
                        print(f"  {k}: 没找到要高亮的句子「{m}」")
                        continue
                    ms[m] = [[round((x - clip['x']) * DSF), round((yy - y0) * DSF), round(w * DSF), round(h * DSF)] for x, yy, w, h in r["rects"]]
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
