# -*- coding: utf-8 -*-
r"""把 Tavus 官网（Griffin 页、9 月基准博客）里要用的区块截成高清图（2 倍像素），并算出要高亮的文字在图里的位置。

  python capture_pages.py [名字 …]        不写名字 = 全部

输出：../素材/官网截图/<名字>.png，../素材/官网截图/boxes.json（每张图里每个要高亮的文字的位置，占整张图的比例 [x0, y0, x1, y1]）。
做法：打开页面 → 隐藏固定 / 吸顶元素（导航、公告条、无障碍按钮）→ 一路滚到底触发懒加载 → 把目标元素滚到视口中间、等动画放完 → 元素截图。
这些是 Tavus 自己的页面（第三方素材），整个 素材/ 目录不进 git。
"""
import asyncio
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "素材" / "官网截图"
OUT.mkdir(parents=True, exist_ok=True)

GRIFFIN = "https://www.tavus.io/griffin"
BLOG = "https://www.tavus.io/blog/september-2026-benchmarks"

# 名字 → (页面, 选择器 / 含文字的元素, 第几个, 要高亮的文字们, 等多久（秒）)
# sel 以 "text:" 开头 = 找“含这段文字、尺寸最小的 .griffin-figure / .griffin-wide”
TARGETS = {
    "g_hero":     (GRIFFIN, ".griffin-hero", 0, ["The First Human Interaction Model", "48%", "#1", "37%", "READ THE RESEARCH BREAKDOWN"], 3),
    "g_hero_art": (GRIFFIN, ".griffin-hero", 0, [], 3),                  # 首屏底图（夕阳 + 鹰头狮），文字和数据条隐藏掉，做封面用
    "g_intro":    (GRIFFIN, ".griffin-intro .griffin-column", 0, ["Today we’re introducing Griffin", "first model to pass the real-time, video Turing test", "48% of participants", "Griffin-Lite, a research preview"], 2),
    "g_duplex":   (GRIFFIN, "text:04.2 / TURN-BASED VS FULL-DUPLEX", 0, ["Turn-based vs full-duplex", "nod, backchannel or begin its reply while you are still talking"], 4),
    "g_what":     (GRIFFIN, "#what", 0, ["Griffin-Lite is a preview of our first Human Interaction Model", "full-duplex video-to-video model", "Perception, deciding when and how to respond"], 2),
    "g_latency":  (GRIFFIN, "text:05.1 / AUDIO-TO-VIDEO LATENCY", 0, ["0.50×", "1.00×", "0.43 seconds"], 5),
    "g_fdb_gen":  (GRIFFIN, "text:05.2 / VIDEOFDB · GENERATION", 0, ["3.92", "3.83", "2.80", "+1.03", "−0.09", "62.8%"], 5),
    "g_fdb_perc": (GRIFFIN, "text:05.2 / VIDEOFDB · PERCEPTION", 0, ["4.20", "3.73", "3.44", "3.17", "2.97", "+0.29", "73.8%"], 5),
    "g_study":    (GRIFFIN, "text:05.3 / FACE-TO-FACE STUDY", 0, ["48", "2.4", "26 of 54", "1 of 41", "79%", "<20 s"], 6),
    "g_safety":   (GRIFFIN, "#responsibility", 0, ["Given Griffin-Lite is the first model to pass the Turing test", "deceive a human", "will not be available for use for customers at this time"], 2),
    "g_build":    (GRIFFIN, ".griffin-build-inner", 0, ["Griffin isn’t on the Tavus platform yet", "Phoenix generates the face, Raven sees and understands you, and Sparrow knows when to talk"], 2),
    "b_pref":     (BLOG, "text:People preferred Tavus in all three matchups", 0, ["60.8%", "85.1%", "75.0%", "vs Anam", "vs LemonSlice", "vs HeyGen"], 5),
    "b_metrics":  (BLOG, "text:Tavus had the best average on all seven metrics", 0, ["0.926", "106.5", "24.6", "8.52", "7.84", "0.469", "0.268"], 3),
    "b_summary":  (BLOG, "text:Key statistics", 0, ["60.8%", "85.1%", "75.0%", "7 of 7"], 4),
}

HIDE_EXTRA = {"g_hero_art": [".griffin-hero-inner", ".griffin-hero-stats", ".griffin-hero-scroll"]}

HIDE_JS = r"""() => {
  const kill = [];
  for (const e of document.querySelectorAll('*')) {
    const cs = getComputedStyle(e);
    if (cs.position === 'fixed' || cs.position === 'sticky') kill.push(e);
  }
  kill.forEach(e => e.style.setProperty('display', 'none', 'important'));
  for (const e of document.querySelectorAll('[class*="banner"], [class*="announce"], [class*="cookie"], [class*="consent"], [id*="cookie"], [class*="accessib"]')) e.style.setProperty('display', 'none', 'important');
  return kill.length;
}"""

FIND_JS = r"""([sel, idx]) => {
  let el = null;
  if (sel.startsWith('text:')) {
    const needle = sel.slice(5).toLowerCase();
    const cands = [...document.querySelectorAll('.griffin-figure, .griffin-wide, section, div, figure')]
      .filter(e => (e.innerText || '').toLowerCase().includes(needle));
    cands.sort((a, b) => a.getBoundingClientRect().width * a.getBoundingClientRect().height - b.getBoundingClientRect().width * b.getBoundingClientRect().height);
    // 取尺寸最小、但又足够大（是一张图而不是一行字）的那个
    el = cands.find(e => e.getBoundingClientRect().height > 260 && e.getBoundingClientRect().width > 500) || cands[0];
  } else {
    el = document.querySelectorAll(sel)[idx];
  }
  if (!el) return null;
  el.setAttribute('data-cap', '1');
  return true;
}"""

BOX_JS = r"""(needles) => {
  const root = document.querySelector('[data-cap="1"]');
  const R = root.getBoundingClientRect();
  const out = {};
  for (const n of needles) {
    const low = n.toLowerCase();
    let best = null, bestA = 1e12;
    for (const e of root.querySelectorAll('*')) {
      const t = (e.innerText || '').replace(/\s+/g, ' ').toLowerCase();
      if (!t.includes(low)) continue;
      const r = e.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) continue;
      const a = r.width * r.height;
      if (a < bestA) { bestA = a; best = r; }
    }
    if (best) out[n] = [(best.left - R.left) / R.width, (best.top - R.top) / R.height, (best.right - R.left) / R.width, (best.bottom - R.top) / R.height];
    else out[n] = null;
  }
  return out;
}"""


async def main():
    want = sys.argv[1:] or list(TARGETS)
    boxes_path = OUT / "boxes.json"
    boxes = json.loads(boxes_path.read_text(encoding="utf-8")) if boxes_path.exists() else {}
    by_page = {}
    for k in want:
        by_page.setdefault(TARGETS[k][0], []).append(k)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for url, names in by_page.items():
            ctx = await b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
            pg = await ctx.new_page()
            await pg.goto(url, wait_until="networkidle", timeout=90000)
            await pg.wait_for_timeout(2000)
            h = await pg.evaluate("document.documentElement.scrollHeight")
            y = 0
            while y < h:                                   # 一路滚到底，触发懒加载 / 入场动画
                await pg.evaluate(f"window.scrollTo(0,{y})")
                await pg.wait_for_timeout(250)
                y += 600
            await pg.evaluate("window.scrollTo(0,0)")
            await pg.wait_for_timeout(500)
            n = await pg.evaluate(HIDE_JS)
            print(url, "隐藏了", n, "个固定 / 吸顶元素")
            for name in names:
                _, sel, idx, needles, wait = TARGETS[name]
                await pg.evaluate("document.querySelectorAll('[data-cap]').forEach(e => e.removeAttribute('data-cap'))")
                ok = await pg.evaluate(FIND_JS, [sel, idx])
                if not ok:
                    print("  没找到", name, sel)
                    continue
                el = pg.locator('[data-cap="1"]')
                await el.scroll_into_view_if_needed()
                await pg.evaluate("() => { const e = document.querySelector('[data-cap=\"1\"]'); const r = e.getBoundingClientRect(); window.scrollBy(0, r.top - Math.max(40, (innerHeight - r.height) / 2)); }")
                await pg.wait_for_timeout(int(wait * 1000))
                for sel_h in HIDE_EXTRA.get(name, []):
                    await pg.evaluate("(q) => document.querySelectorAll(q).forEach(e => e.style.setProperty('visibility', 'hidden', 'important'))", sel_h)
                await el.screenshot(path=str(OUT / f"{name}.png"))
                for sel_h in HIDE_EXTRA.get(name, []):
                    await pg.evaluate("(q) => document.querySelectorAll(q).forEach(e => e.style.removeProperty('visibility'))", sel_h)
                bx = await pg.evaluate(BOX_JS, needles)
                boxes[name] = bx
                bb = await el.bounding_box()
                miss = [k for k, v in bx.items() if v is None]
                print(f"  {name}: {bb['width']:.0f}×{bb['height']:.0f} css px → {OUT / (name + '.png')}" + (f"  没找到的文字：{miss}" if miss else ""))
            await ctx.close()
        await b.close()
    boxes_path.write_text(json.dumps(boxes, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
