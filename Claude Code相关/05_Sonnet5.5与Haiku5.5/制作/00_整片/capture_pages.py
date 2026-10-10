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
WIDE = {"H_chart1": 1000, "H_chart2": 1000, "H_chart3": 1000, "H_bench": 1000, "S_perf": 1100, "Y_price": 1180, "Y_models": 1180}   # 表格太宽的页面：放宽视口，不然右边几列被裁掉

HAIKU = "https://www.anthropic.com/claude-haiku-5-5"
SONNET = "https://www.anthropic.com/claude-sonnet-5-5"
PRICING = "https://platform.claude.com/docs/en/about-claude/pricing"
MODELS = "https://platform.claude.com/docs/en/models/overview"
EMB ="https://platform.twitter.com/embed/Tweet.html?id={}&theme=light&hideThread=true&lang=en&dnt=true"
T1, T2 = "2107894039626277339", "2107895955144208813"      # T1 = @claudeai（Haiku 5.5 发布）、T2 = @ClaudeDevs（Haiku 5.5 可用 + 子智能体用法 + 护蛋演示）

# 名字: (页面, 起点文字, 高度 CSS px, 起点上方留白, [要高亮的句子])
#   起点文字以 # 开头 = 只在 h1–h4 里找这个标题；X_ 开头的是推文（起点文字不用，高度写 "after:某句话" = 截到这句话下面，写 0 = 整条推文）
#   高亮句子的写法：普通文字 = 页面里的原文子串（≤ 15 个词）；"@@文字" = 高亮它所在的整个段落块；"#sel:选择器" = 整块（图表）画框；
#   "@row:行里的字|格子里的字" = 表格里这一行的这个格子（好几行都有同一句话时点名取哪一格）
SPECS = {
    # 官方推文（嵌入页，不用登录）：整条截下来（含视频封面）
    "X_t1": (EMB.format(T1), "", 0, 0, ["cheapest, fastest, and most capable small model", "around 75% less to run", "than Claude Haiku 4.5"]),
    "X_t2": (EMB.format(T2), "", 0, 0, ["Claude Platform and Claude Code", "around 75% less to run", "as a subagent", "database queries"]),
    # 发布页的开头（日期 + 标题）
    "S_head": (SONNET, "September 28, 2026", 640, 40, ["September 28, 2026"]),
    "H_head": (HAIKU, "October 7, 2026", 640, 40, ["October 7, 2026"]),
    # Haiku 5.5 发布页（anthropic.com/claude-haiku-5-5）
    "H_intro": (HAIKU, "Introducing Claude Haiku 5.5:", 760, 20, ["high-volume, cost-sensitive tasks", "summaries, compactions, database queries", "as a subagent on coding work", "live customer support and browser use", "around 75% less to run"]),
    "H_bench": (HAIKU, "Here’s how Claude Haiku 5.5 performs", 1500, 20, ["GPT-6 Luna", "@row:GDPval-AA v2.1|1620", "@row:GDPval-AA v2.1|735", "@row:OSWorld 2.1|72.4%Offline subset", "@row:OSWorld 2.1|15.7%Offline subset", "@row:Terminal-Bench 4.0|39.2%", "@row:Terminal-Bench 4.0|0.0%", "@row:Terminal-Bench 4.0|70.6%"]),
    "H_price": (HAIKU, "#Pricing", 900, 20, ["up to 100,000 tokens", "@row:Input tokens|$0.10 / $0.50", "@row:Output tokens|$0.50 / $2.50", "@row:Input tokens|$1.00", "@row:Output tokens|$5.00"]),
    "H_foot": (HAIKU, "priced 90% lower than Claude Haiku 4.5", 640, 500, ["priced 90% lower than Claude Haiku 4.5", "50% lower for requests over 100,000 tokens", "On Haiku 4.5, 90% of requests fell into the former category", "slightly more tokens per task"]),
    "H_cache": (HAIKU, "First, starting today, we’re lowering the price of cache reads", 300, 30, ["Cache reads now cost 50% less", "$0.10 per million tokens rather than $0.20", "around 20%"]),
    "H_remain": (HAIKU, "This chart illustrates an important difference between Haiku 5.5 and our larger models", 300, 40, ["remain better choices for complex agentic coding tasks", "narrowly scoped tasks"]),
    "H_credit": (HAIKU, "Second, this week, we’ll roll out a new monthly API credit", 360, 30, ["this week, we'll roll out", "Max 5x users will get $100", "Max 20x users will get $200", "up to $500, pooled across their users", "They can be used on any of our models"]),
    # 三张按思考力度画的“成绩对成本”图（要点开三个标签，后处理拼成一张 H_charts）
    "H_chart1": (HAIKU, "The charts below show how Haiku 5.5 performs", 860, 0, ["first Haiku-class model to come with an adjustable effort setting", "#sel:figure[class*=frame]"], "Computer use"),
    "H_chart2": (HAIKU, "The charts below show how Haiku 5.5 performs", 860, 0, ["#sel:figure[class*=frame]"], "GDPval"),
    "H_chart3": (HAIKU, "The charts below show how Haiku 5.5 performs", 860, 0, ["#sel:figure[class*=frame]"], "Humanity"),
    # Sonnet 5.5 发布页
    "S_price": (SONNET, "Sonnet 5.5 scores 70.6% on Terminal-Bench 4.0", 520, 20, ["first Sonnet model to beat", "$2 per million input tokens", "far fewer tokens to do the same work", "up to 30% less per task", "30%+ faster than Sonnet 5"]),
    "S_perf": (SONNET, "Sonnet 5.5 improves on Sonnet 5 across domains", 1560, 20, ["Opus 5.5 remains clearly stronger", "@row:Terminal-Bench 4.0|70.6%", "@row:Terminal-Bench 4.0|10.3%", "@row:Terminal-Bench 4.0|66.4%", "@row:GDPval-AA v2.1|1844", "@row:GDPval-AA v2.1|1846", "@row:OSWorld 2.1|80.1%", "@row:OSWorld 2.1|81.8%", "@row:Chartography|61.6%", "@row:Chartography|15.6%", "#sel:table"]),
    # 官方文档：价格页、模型总览
    "Y_models": (MODELS, "which model to use", 1500, 20, ["@@start with Claude Opus 5.5 for most workloads", "@row:Pricing|$10 / input MTok$50 / output MTok", "@row:Pricing|$4 / input MTok$20 / output MTok", "@row:Pricing|$2 / input MTok$10 / output MTok", "@row:Pricing|From $0.10 / input MTokFrom $0.50 / output MTok", "For long-running agentic coding and knowledge work", "The best combination of speed and intelligence", "For high-volume, latency-sensitive tasks", "#sel:table"]),
}
SHOW_URL = {"X_t1": f"https://x.com/claudeai/status/{T1}", "X_t2": f"https://x.com/ClaudeDevs/status/{T2}"}                                                # 推文页面名 → 在浏览器顶栏里显示的 x.com 网址（嵌入页的网址不好看）：{"X_t1": f"https://x.com/ClaudeDevs/status/{T1}"}

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


CLIPX = {"Y_models": (285, 860), "S_perf": (100, 900), "H_bench": (45, 910), "H_chart1": (40, 920), "H_chart2": (40, 920), "H_chart3": (40, 920)}   # 截图的横向范围（CSS px：起点, 宽度）：只留内容，字才大


def stack_charts(meta, Image):
    """H_chart1/2/3（同一页点开三个标签各截一张）上下拼成 H_charts.png，高亮位置跟着平移；框 = #sel:chart1/2/3。"""
    keys = ["H_chart1", "H_chart2", "H_chart3"]
    if not all(k in meta and (OUT / f"{k}.png").exists() for k in keys):
        return
    ims = [Image.open(OUT / f"{k}.png").convert("RGB") for k in keys]
    W, GAP = max(i.width for i in ims), 40
    H = sum(i.height for i in ims) + GAP * (len(ims) - 1)
    bg = meta[keys[0]]["bg"]
    S = Image.new("RGB", (W, H), bg)
    y, marks = 0, {}
    for n, (k, im) in enumerate(zip(keys, ims)):
        S.paste(im, (0, y))
        for needle, rects in meta[k]["marks"].items():
            name = f"#sel:chart{n + 1}" if needle.startswith("#sel:") else needle
            marks[name] = [[x, yy + y, w, h] for x, yy, w, h in rects]
        y += im.height + GAP
    S.save(OUT / "H_charts.png")
    meta["H_charts"] = {"src": "pages/H_charts.png", "w": W, "h": H, "url": HAIKU, "bg": bg, "marks": marks}
    print(f"H_charts: {W}×{H}（三张图拼成一张）")


def main():
    from PIL import Image
    only = sys.argv[1:] or list(SPECS)
    OUT.mkdir(parents=True, exist_ok=True)
    meta_file = HERE / "pages.json"
    meta = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
    by_url = {}
    for k in only:
        by_url.setdefault((SPECS[k][0], WIDE.get(k, VW)), []).append(k)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for (url, vw), keys in by_url.items():
            ctx = b.new_context(viewport={"width": vw, "height": 1000}, device_scale_factor=DSF, locale="en-US")
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
                _, anchor, height, pad, marks = SPECS[k][:5]
                if len(SPECS[k]) > 5:                          # 第 6 项 = 先点开的标签页名字（图表有几个标签的页面）
                    import re as _re
                    pg.get_by_role("tab", name=_re.compile(SPECS[k][5])).first.click()
                    pg.wait_for_timeout(3500)
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
                    a = pg.evaluate(FIND_HEAD_JS, anchor[1:]) if anchor.startswith("#") else pg.evaluate(FIND_JS, anchor)
                    if not a:
                        print(k, f"找不到起点文字：{anchor}"); continue
                    y0 = max(0, a["top"] - pad)
                    hh = min(height, H - y0)
                    x0, cw = CLIPX.get(k, (0, vw))
                    clip = {"x": x0, "y": y0, "width": cw, "height": hh}
                f = OUT / f"{k}.png"
                pg.screenshot(path=str(f), clip=clip, full_page=True)
                ms = {}
                for m in marks:
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
    stack_charts(meta, Image)
    meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "pages.js").write_text("window.PG = " + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main()
