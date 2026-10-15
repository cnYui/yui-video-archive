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

TUT = "https://claude.dev/blog/getting-started-with-claude-code-mods/"
DOCS = "https://code.claude.com/docs/en/plugins/mods/overview"
CHANGELOG = "https://code.claude.com/docs/en/changelog"
EMB ="https://platform.twitter.com/embed/Tweet.html?id={}&theme=light&hideThread=true&lang=en&dnt=true"
NAT, WANG1, WANG2, AYI = "2106099383037309211", "2106113742266089526", "2106113745282015730", "2106239579938238880"
SITE = "https://gadgets.muse.ai/"
REPO = "https://github.com/facebookincubator/muse-gadget-sdk"

# 名字: (页面, 起点文字, 高度 CSS px, 起点上方留白, [要高亮的句子])
#   起点文字以 # 开头 = 只在 h1–h4 里找这个标题；"@top" = 从页面最顶上截起（GitHub 仓库页要带上标题栏、星标数）；X_ 开头的是推文（起点文字不用，高度写 "after:某句话" = 截到这句话下面，写 0 = 整条推文）
#   要高亮的写法：普通句子 = 按文字找；"@time" = GitHub 提交行的相对时间（relative-time 在 shadow DOM 里，按文字找不到）；"@css:选择器" = 区域里第一个匹配的元素；
#   (别名, 查找写法) = scenes.js 里用别名（例：("MIT", "@css:a[href='#MIT-1-ov-file']")）。星数这类每天在变的数字按 "k stars" 找，别写具体数字。
#   （@top / @time / @css / 别名是 2026-10-04 image-blaster 那条短视频加的，见 docs/ai/context/20261004-111500-image-blaster-short-video_CN.md）
#   高亮句子的写法：普通文字 = 页面里的原文子串（≤ 15 个词）；"@@文字" = 高亮它所在的整个段落块；"#sel:选择器" = 整块（图表）画框；
#   "@row:行里的字|格子里的字" = 表格里这一行的这个格子（好几行都有同一句话时点名取哪一格）
SPECS = {
    # 推文（X 嵌入页，整条）
    "X_nat": (EMB.format(NAT), "", 0, 0, ["open source ESP32 firmware and Linux sdk", "point your favorite coding agent at the github repo"]),
    "X_wang1": (EMB.format(WANG1), "", 0, 0, ["open-source ESP32 firmware and Linux SDK", "Muse Home Link"]),
    "X_wang2": (EMB.format(WANG2), "", 0, 0, ["batch of 5,000", "free for muse subscribers while supplies last"]),
    # GitHub 仓库首页 / README
    "G_repo": (REPO, "@top", 1500, 0, ["Open source SDK to build Muse gadgets", "k stars", ("Apache", "@css:a[href*='Apache-2.0']"), ("time", "@time")]),
    "G_readme": (REPO, "Muse gadgets are open source devices you build yourself", 980, 40,
                 ["Muse gadgets are open source devices you build yourself", "ESP32 Device SDK", "Linux Device SDK", "SDK token", "Every gadget needs a", "Settings > Devices", "AGENTS.md for coding agents"]),
    # gadgets.muse.ai（640 宽的单栏版式：字更大）
    "S_make": (SITE, "#Make your own", 1330, 70,
               ["Side effects of tinkering may include bricked boards, voided warranties, brownouts, or bankruptcies", "SDK token", "ESP32 Device SDK", "Linux Device SDK"]),
    "S_src": (SITE, "The device SDKs and firmware are open source", 220, 150, ["Apache 2.0 license"]),
    "S_home": (SITE, "Connect Muse to your home Wi-Fi so it can reach", 520, 150,
               ["Community-built skills can let Muse turn on a light", "United States only", "limit one per subscriber", "Ships in October"]),
    # 官网的 Gadget SDK Token Terms（事实核对时发现：代码是 Apache 2.0，但 token 条款限个人非商用 / 最多 50 台 / 不能卖 / Meta 可随时收回）
    "S_terms": (SITE + "sdk-terms", "These terms apply when you use any Muse gadget SDK token", 1500, 170,
                ["personal, non-commercial use", "no more than 50 devices", "You may not embed it in any device that you sell", "Meta may suspend or withdraw your access"]),
}
VW_OF = {"S_make": 640, "S_src": 640, "S_home": 640, "S_terms": 640}          # 页面图的视口宽度（默认 800）：官网用 640 的单栏版式，字比 800 的两栏版大 1.25 倍
COLOR_OF = {}                                                  # 网址 → 配色（light / dark）
SHOW_URL = {"X_nat": f"https://x.com/natfriedman/status/{NAT}", "X_wang1": f"https://x.com/alexandr_wang/status/{WANG1}", "X_wang2": f"https://x.com/alexandr_wang/status/{WANG2}"}   # 推文页面名 → 在浏览器顶栏里显示的 x.com 网址（嵌入页的网址不好看）

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
        by_url.setdefault((SPECS[k][0], VW_OF.get(k, VW)), []).append(k)          # 同一网址、同一视口宽度的页面图一起录（VW_OF：这条加的，官网用 640 宽的单栏版式字更大）
    with sync_playwright() as p:
        b = p.chromium.launch()
        for (url, vw), keys in by_url.items():
            ctx = b.new_context(viewport={"width": vw, "height": 1000}, device_scale_factor=DSF, locale="en-US", color_scheme=COLOR_OF.get(url, "light"),
                                  timezone_id="America/Los_Angeles")          # 推文嵌入页的时间按浏览器时区显示：用美西时间，和旁白里的“10 月 2 日”（美国日期）对得上（东京时间会显示成 10 月 3 日）
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
                    a = {"top": 0} if anchor == "@top" else pg.evaluate(FIND_HEAD_JS, anchor[1:]) if anchor.startswith("#") else pg.evaluate(FIND_JS, anchor)
                    if not a:
                        print(k, f"找不到起点文字：{anchor}"); continue
                    y0 = max(0, a["top"] - pad)
                    hh = min(height, H - y0)
                    clip = {"x": 0, "y": y0, "width": vw, "height": hh}
                f = OUT / f"{k}.png"
                pg.screenshot(path=str(f), clip=clip, full_page=True)
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
