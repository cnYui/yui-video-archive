"""Engine layout check: seeks to the end-state and middle of every segment and reports text overflowing its box,
content intruding into the subtitle band / character / TOC / chapter bar, and content leaving the frame.
Also fails on console errors (the same ones that make render.py exit with code 2).

    python engine/check_layout.py                    # in 制作/: uses ../timeline.json next to the engine dir
    python engine/check_layout.py --timeline path/to/timeline.json --only S03,S04
"""
import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ENGINE = Path(__file__).resolve().parent
JS = r"""(t) => {
  window.renderAt(t);
  const out = [];
  const effO = e => { let o = 1; for (let x = e; x && x !== document.body; x = x.parentElement) { const cs = getComputedStyle(x); if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= +cs.opacity; } return o; };
  const root = document.getElementById('scenes');
  const all = root.querySelectorAll('*');
  const toc = document.getElementById('toc');
  const tr = toc && effO(toc) > 0.2 ? toc.getBoundingClientRect() : null;
  const zones = [['subtitle', 340, 922, 1580, 1000], ['char', 40, 690, 380, 1005], ['bar', 0, 1000, 1920, 1080]];
  if (tr) zones.push(['toc', tr.left - 2, tr.top - 2, tr.right + 2, tr.bottom + 2]);
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
    const box = e.parentElement && e.parentElement.closest('.card,.code,.win,.node,.modal,.chip,.field,.btn');
    if (hasText && box) {
      const b = box.getBoundingClientRect();
      const rng = document.createRange(); rng.selectNodeContents(e); const tx = rng.getBoundingClientRect();
      if (tx.width > 0 && (tx.left < b.left - 2 || tx.right > b.right + 2 || tx.top < b.top - 2 || tx.bottom > b.bottom + 2)) out.push(`outside ${box.className}: ${name} text[${tx.left|0},${tx.top|0},${tx.right|0},${tx.bottom|0}] box[${b.left|0},${b.top|0},${b.right|0},${b.bottom|0}]`);
    }
  }
  return out;
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", default=str(ENGINE.parent / "timeline.json"))
    ap.add_argument("--only", help="comma-separated scene ids")
    args = ap.parse_args()
    data = json.loads(Path(args.timeline).read_text(encoding="utf-8"))
    only = set(args.only.split(",")) if args.only else None
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--force-color-profile=srgb"])
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.add_init_script("window.__CAPTURE__=true;window.__DATA__=" + json.dumps(data, ensure_ascii=False) + ";")
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        pg.goto((ENGINE / "index.html").resolve().as_uri())
        pg.wait_for_function("window.__READY__ === true", timeout=30000)
        total = 0
        for s in data["segments"]:
            if only and s["scene"] not in only:
                continue
            for t in (round(max(s["start"] + 0.5, s["end"] - 0.35), 2), round((s["start"] + s["end"]) / 2, 2)):
                for r in pg.evaluate(JS, t):
                    print(f'{s["id"]} t={t}: {r}'); total += 1
        print("issues:", total, "console errors:", errs)
        b.close()
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
