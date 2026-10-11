# -*- coding: utf-8 -*-
"""录官方页面：用 Playwright（viewport 800 宽、2 倍像素 → 图宽 1600）把要讲的小节截成高清长图，并算出要高亮的那句话在图里的位置。
输出 media/pages/<名字>.png + pages.js（window.PG = {名字: {src, w, h, url, marks: {句子: [[x,y,w,h], …]}}}，坐标是图片像素）。

  python capture_pages.py            全部重录
  python capture_pages.py T_how …    只录指定的几张

视频里（scenes.js 的 pageShot）按解说时刻把图往上滚、给对应的句子刷上荧光笔，就像在录屏。
页面都是公开页面：claude.dev、code.claude.com 文档、x.com/ClaudeDevs 的帖子（访客视图）。
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
SON = "https://claude.dev/blog/building-with-claude-sonnet-5-5/"
EV = "https://claude.dev/blog/automating-eval-design-and-hillclimbing/"
HOME = "https://claude.dev/"
X = "https://x.com/ClaudeDevs/status/2105721434807083061"

# 名字: (页面, 起点文字, 高度 CSS px, 起点上方留白, [要高亮的句子])
SPECS = {
    "T_intro": (TUT, "Claude Code already lets you change a lot", 620, 40,
                ["settings", "permission rules", "slash commands", "skills", "a status line", "Mods go further"]),
    "T_how": (TUT, "A mod is a Claude Code plugin whose behavior", 900, 30,
              ["register(on, options)", 'on("tool.call"', "Hooks form a chain"]),
    "T_shortcut": (TUT, "#The shortcut: let Claude build it", 760, 30,
                   ["describe the one you want and let it do the work", "Make me a Claude Code mod called token-weather"]),
    "T_validate": (TUT, "#Step 5: Validate and test", 820, 30,
                   ["claude plugin validate", "hooks:", "calls:", "Validation passed"]),
    "T_share": (TUT, "A mod is a Claude Code plugin, so you share it the same way", 760, 40,
                ["/plugin marketplace add", "/plugin install", "/reload-plugins", "only install from people you trust", "The Claude directory accepts plugins that include mods"]),
    "T_safety": (TUT, "safety net, not a permission system", 640, 300,
                 ["safety net, not a permission system", "get past it", "Use permission rules for a hard block"]),
    "D_install": (DOCS, "#Install or update a mod", 640, 30,
                  ["A mod installs as a plugin, from a marketplace", "/plugin install token-chart@your-org"]),
    "D_where": (DOCS, "Mods work in the Claude Code CLI", 420, 60,
                ["Mods work in the Claude Code CLI and in the Code tab of the Claude Desktop app"]),
    "D_turn": (DOCS, "#Turn mods on or off", 900, 30,
               ["Mods require Claude Code v2.1.287 or later", "on by default", "One mod: disable or uninstall its plugin from the Installed tab in /plugin", "--safe-mode"]),
    "D_builtin": (DOCS, "#Mods built into Claude Code", 1020, 30,
                  ["cc-plugin-agents-md", "cc-plugin-diff"]),
    "D_reach": (DOCS, "#What a mod can reach", 880, 30,
                ["A mod runs with your permissions", "Act on your machine as you: read and write files", "Read your secrets: environment variables", "Mods aren"]),
    "D_trust": (DOCS, "#Decide whether to trust a mod", 300, 30,
                ["@@Install mods only from authors and"]),
    "S_hero": (SON, "Claude Sonnet 5.5 is our second model", 215, 40,
               ["second model in the Claude 5.5 family", "smarter, more efficient and 30% faster", "The per-token price is unchanged", "costs up to 30% less for most work"]),
    "S_choose": (SON, "In the Claude 5.5 family, Opus 5.5", 780, 60,
                 ["Opus 5.5 is built for complex work", "well-scoped everyday tasks like fixing bugs and quickly iterating on features"]),
    "S_cc": (SON, "From Claude Code v2.1.284", 560, 80,
             ["the sonnet alias resolves to Sonnet 5.5", "The default model stays Opus 5.5", "/model sonnet"]),
    "E_intro": (EV, "Evaluations provide a signal", 560, 40,
                ["claude-api skill", "/claude-api build-eval", "/claude-api hillclimb", "held-out set of examples"]),
    "E_fig8": (EV, "We ran /claude-api hillclimb on an internal customer support benchmark", 1500, 20,
               ["customer support benchmark", "#sel:figure.art-fig", "at about one fifth of the cost"]),
    "H_top": (HOME, "claude.dev", 1180, 0,
              ["Getting started with Claude Code mods", "Automating eval design and hillclimbing with Claude", "Building with Claude Sonnet 5.5", "Sharing tips, tricks, and POVs", "ENGINEERING", "PLAYBOOKS", "TUTORIALS"]),
}

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
  const norm = s => s.replace(/[​]/g, '').replace(/\s+/g, ' ').trim().toLowerCase().replace(/[’']/g, "'");
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
  for (const el of document.querySelectorAll('p,li,td,th,pre,code,h1,h2,h3,h4,div,a')) {
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
                if k == "X_play":
                    el = pg.locator("article", has_text="Claude Code Playground").first
                    if el.count() == 0:
                        print(k, "找不到那条帖子，跳过"); continue
                    bb = el.bounding_box()
                    y0 = max(0, bb["y"] + pg.evaluate("window.scrollY") - 10)
                    hh = bb["height"] + 20
                    clip = {"x": 0, "y": y0, "width": VW, "height": hh}
                else:
                    a = pg.evaluate(FIND_HEAD_JS, anchor[1:]) if anchor.startswith("#") else pg.evaluate(FIND_JS, anchor)
                    if not a:
                        print(k, f"找不到起点文字：{anchor}"); continue
                    y0 = max(0, a["top"] - pad)
                    hh = min(height, H - y0)
                    clip = {"x": 0, "y": y0, "width": VW, "height": hh}
                f = OUT / f"{k}.png"
                pg.screenshot(path=str(f), clip=clip, full_page=True)
                ms = {}
                for m in marks:
                    r = pg.evaluate(MARK_JS, [m, y0, y0 + hh])
                    if not r:
                        print(f"  {k}: 没找到要高亮的句子「{m}」")
                        continue
                    ms[m] = [[round((x - clip['x']) * DSF), round((yy - y0) * DSF), round(w * DSF), round(h * DSF)] for x, yy, w, h in r["rects"]]
                from PIL import Image
                _im = Image.open(f).convert("RGB")
                bg = "#%02X%02X%02X" % _im.getpixel((6, _im.height - 6))
                meta[k] = {"src": f"pages/{k}.png", "w": round(VW * DSF), "h": round(hh * DSF), "url": url, "bg": bg, "marks": ms}
                print(f"{k}: {round(VW * DSF)}×{round(hh * DSF)}，高亮 {len(ms)}/{len(marks)}（起点 y={y0:.0f}）")
            ctx.close()
        b.close()
    meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "pages.js").write_text("window.PG = " + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main()
