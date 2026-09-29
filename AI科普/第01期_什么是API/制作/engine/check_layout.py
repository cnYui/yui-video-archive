"""Engine layout check (python engine/check_layout.py): seeks to the end-state and middle of every segment and reports text overflowing its box and content
intruding into the subtitle band / character area / TOC, and content leaving the content area."""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
JS = r"""(t) => {
  window.renderAt(t);
  const out = [];
  const effO = e => { let o = 1; for (let x = e; x && x !== document.body; x = x.parentElement) { const cs = getComputedStyle(x); if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= +cs.opacity; } return o; };
  const root = document.getElementById('scenes');
  const all = root.querySelectorAll('*');
  const zones = [['subtitle', 440, 922, 1860, 1000], ['char', 40, 690, 380, 1005], ['toc', 1538, 18, 1882, 164], ['bar', 0, 1000, 1920, 1080]];
  for (const e of all) {
    if (e.tagName === 'svg' || e.closest('svg')) continue;
    const r = e.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    const hasText = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    const isBox = /\b(card|code|win|node|modal|chip|token|field|btn|step|lbl|note|item|hdr|bigKick)\b/.test(e.className);
    if (!hasText && !isBox) continue;
    const o = effO(e); if (o < 0.2) continue;
    const name = (e.className || e.tagName) + ':' + (e.textContent || '').trim().slice(0, 24);
    for (const [zn, x0, y0, x1, y1] of zones) {
      if (r.right > x0 + 1 && r.left < x1 - 1 && r.bottom > y0 + 1 && r.top < y1 - 1) out.push(`intrudes ${zn}: ${name} [${r.left|0},${r.top|0},${r.right|0},${r.bottom|0}]`);
    }
    if (r.left < -1 || r.right > 1921 || r.top < -1 || r.bottom > 1081) out.push(`offscreen: ${name}`);
    if (hasText && getComputedStyle(e).whiteSpace !== 'normal' && e.scrollWidth > e.clientWidth + 2 && e.clientWidth > 0) out.push(`overflow-x ${e.scrollWidth}>${e.clientWidth}: ${name}`);
    // text leaves its container
    const box = e.parentElement && e.parentElement.closest('.card,.code,.win,.node,.modal,.chip,.field,.btn');
    if (hasText && box) {
      const b = box.getBoundingClientRect();
      const rng = document.createRange(); rng.selectNodeContents(e); const tr = rng.getBoundingClientRect();
      if (tr.width > 0 && (tr.left < b.left - 2 || tr.right > b.right + 2 || tr.top < b.top - 2 || tr.bottom > b.bottom + 2)) out.push(`outside ${box.className}: ${name} text[${tr.left|0},${tr.top|0},${tr.right|0},${tr.bottom|0}] box[${b.left|0},${b.top|0},${b.right|0},${b.bottom|0}]`);
    }
  }
  return out;
}"""
with sync_playwright() as p:
    b = p.chromium.launch(args=["--force-color-profile=srgb"])
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.add_init_script("window.__CAPTURE__=true;window.__DATA__=" + json.dumps(data, ensure_ascii=False) + ";")
    errs = []
    pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
    pg.goto((ROOT / "engine/index.html").resolve().as_uri())
    pg.wait_for_function("window.__READY__ === true", timeout=30000)
    total = 0
    for s in data["segments"]:
        for t in (round(max(s["start"] + 0.5, s["end"] - 0.35), 2), round((s["start"] + s["end"]) / 2, 2)):
            res = pg.evaluate(JS, t)
            for r in res:
                print(f'{s["id"]} t={t}: {r}'); total += 1
    print("issues:", total, "console errors:", errs)
    b.close()
