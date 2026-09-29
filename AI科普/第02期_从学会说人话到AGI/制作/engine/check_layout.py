"""Engine layout check: seeks to the end-state and middle of every segment and reports text overflowing its box,
content intruding into the subtitle band / character / TOC / chapter bar, content leaving the frame, and
low-contrast text: text whose colour is nearly the same as the box painted behind it (contrast ratio < 1.6, e.g.
paper-white text on a paper card, or ink text on the dark scene) -- "low-contrast 1.00: lbl:… text #EDEAE3 on #EDEAE3 (card)".
Also fails on console errors (the same ones that make render.py exit with code 2).
At the end it prints the character's actions: explicit ones from the timeline and the auto layer (ENG.autoPlan, v2 only).

Everything is checked on the CANVAS (the page / video frame: timeline.json episode.canvas, default 1920×1080; the
viewport is opened at that size): subtitle band CW/2 ± 620, character canvas, TOC box, chapter bar (full width),
"offscreen" = outside the canvas. Positions in the report are canvas px; scenes.js coordinates are stage px (the
1920×1080 content stage sits at x (CW - 1920) / 2 of the canvas, e.g. +210 on 2340×1080).
The question cards overlap the TOC while they fly into it (ENG.tocInTime() for about 1 s): those lines are marked
"expected (question card flying into the TOC)" and not counted in "issues".

    python engine/check_layout.py                    # in 制作/: uses ../timeline.json next to the engine dir
    python engine/check_layout.py --timeline path/to/timeline.json --only S03,S04
"""
import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ENGINE = Path(__file__).resolve().parent


def canvas_of(data):
    """(w, h) of the page: timeline episode.canvas (or a top-level canvas), else 1920x1080 -- the same rule as core.js
    and render.py (height 1080, width >= 1920; anything else falls back to 1920x1080)"""
    for c in (((data or {}).get("episode") or {}).get("canvas"), (data or {}).get("canvas")):
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            try:
                w, h = int(round(float(c[0]))), int(round(float(c[1])))
            except (TypeError, ValueError):
                continue
            return (w, h) if h == 1080 and w >= 1920 else (1920, 1080)
    return 1920, 1080


JS = r"""(t) => {
  window.renderAt(t);
  const out = [];
  const CW = ENG.CW || 1920, CH = ENG.CH || 1080;          // the canvas (page) size
  const effO = e => { let o = 1; for (let x = e; x && x !== document.body; x = x.parentElement) { const cs = getComputedStyle(x); if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= +cs.opacity; } return o; };
  const root = document.getElementById('scenes');
  const all = root.querySelectorAll('*');
  const toc = document.getElementById('toc');
  const tr = toc && effO(toc) > 0.2 ? toc.getBoundingClientRect() : null;
  // character zone = the character canvas (its place comes from the presenter's geometry) + 10 px each side,
  // i.e. [40, 690, 380, 1005] for the default 50,685 320×320 (canvas px: she stands at the canvas's left edge)
  const ce = document.getElementById('char');
  const cz = ce ? ['char', ce.offsetLeft - 10, ce.offsetTop + 5, ce.offsetLeft + ce.offsetWidth + 10, ce.offsetTop + ce.offsetHeight]
                : ['char', 40, 690, 380, 1005];
  // subtitle band: centred on the canvas, 1240 px wide (x 340..1580 on 1920; 550..1790 on 2340); bar: full width
  const zones = [['subtitle', CW / 2 - 620, 922, CW / 2 + 620, 1000], cz, ['bar', 0, 1000, CW, 1080]];
  if (tr) zones.push(['toc', tr.left - 2, tr.top - 2, tr.right + 2, tr.bottom + 2]);
  // the question cards flying into the TOC (c.questionCards / a card with a "QUESTION 0N" kicker, from ENG.tocInTime()
  // for ~1 s) overlap it by design: reported as "expected", not counted
  const tIn = typeof ENG.tocInTime === 'function' ? ENG.tocInTime() : -1e9;
  const flying = e => { const cd = e.closest('.card'); return t >= tIn - 0.05 && t <= tIn + 1.2 && !!cd && /QUESTION \d/.test(cd.textContent); };
  // ---- contrast: text colour vs what is painted behind the text -- the backgrounds of the element itself, its
  //      card, and any card / chip it was placed over, composited (alpha x opacity) over the navy stage
  const NAVY = { r: 27, g: 35, b: 64 };
  const rgbaOf = s => { const m = String(s || '').match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(',').map(parseFloat); return { r: v[0], g: v[1], b: v[2], a: v.length > 3 ? v[3] : 1 }; };
  const over = (c, bg) => ({ r: c.a * c.r + (1 - c.a) * bg.r, g: c.a * c.g + (1 - c.a) * bg.g, b: c.a * c.b + (1 - c.a) * bg.b });
  const lum = c => { const f = x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const hex = c => '#' + [c.r, c.g, c.b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();
  const surface = (e, px, py) => {
    const hits = document.elementsFromPoint(px, py), k = hits.indexOf(e);
    const stack = (k >= 0 ? hits.slice(k) : hits).filter(u => u !== root && root.contains(u) && !(u !== e && e.contains(u))
      && !(u instanceof SVGElement) && !/^(CANVAS|IMG)$/.test(u.tagName));    // the element itself, then what is below it
    let c = NAVY, who = 'scene';
    for (let i = stack.length - 1; i >= 0; i--) {                  // bottom -> top
      const bg = rgbaOf(getComputedStyle(stack[i]).backgroundColor);
      const a = bg ? bg.a * effO(stack[i]) : 0;
      if (a < 0.02) continue;
      c = over(Object.assign({}, bg, { a }), c);
      if (a >= 0.5 || who === 'scene') who = (typeof stack[i].className === 'string' && stack[i].className.trim().split(/\s+/)[0]) || stack[i].tagName.toLowerCase();
    }
    return { c, who };
  };
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
      if (r.right > x0 + 1 && r.left < x1 - 1 && r.bottom > y0 + 1 && r.top < y1 - 1)
        out.push(`${zn === 'toc' && flying(e) ? 'expected (question card flying into the TOC) ' : ''}intrudes ${zn}: ${name} [${r.left|0},${r.top|0},${r.right|0},${r.bottom|0}]`);
    }
    if (r.left < -1 || r.right > CW + 1 || r.top < -1 || r.bottom > CH + 1) out.push(`offscreen: ${name}`);
    if (hasText && getComputedStyle(e).whiteSpace !== 'normal' && e.scrollWidth > e.clientWidth + 2 && e.clientWidth > 0) out.push(`overflow-x ${e.scrollWidth}>${e.clientWidth}: ${name}`);
    const box = e.parentElement && e.parentElement.closest('.card,.code,.win,.node,.modal,.chip,.field,.btn');
    if (hasText && box) {
      const b = box.getBoundingClientRect();
      const rng = document.createRange(); rng.selectNodeContents(e); const tx = rng.getBoundingClientRect();
      if (tx.width > 0 && (tx.left < b.left - 2 || tx.right > b.right + 2 || tx.top < b.top - 2 || tx.bottom > b.bottom + 2)) out.push(`outside ${box.className}: ${name} text[${tx.left|0},${tx.top|0},${tx.right|0},${tx.bottom|0}] box[${b.left|0},${b.top|0},${b.right|0},${b.bottom|0}]`);
    }
    if (hasText && o >= 0.5) {
      const tn = [...e.childNodes].find(n => n.nodeType === 3 && n.textContent.trim());
      const rg = document.createRange(); rg.selectNodeContents(tn); const tb = rg.getBoundingClientRect();
      const px = tb.left + tb.width / 2, py = tb.top + tb.height / 2;
      const tc = rgbaOf(getComputedStyle(e).color);
      if (tc && tb.width > 0 && px > 0 && px < CW && py > 0 && py < CH) {
        const sf = surface(e, px, py), fg = over(tc, sf.c);
        const l1 = lum(fg), l2 = lum(sf.c), cr = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
        if (cr < 1.6) out.push(`low-contrast ${cr.toFixed(2)}: ${name} text ${hex(fg)} on ${hex(sf.c)} (${sf.who})`);
      }
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
    cw, ch = canvas_of(data)
    print(f"canvas {cw}×{ch}" + ("" if (cw, ch) == (1920, 1080) else f" (content stage 1920×1080 at x {(cw - 1920) // 2})"))
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--force-color-profile=srgb"])
        pg = b.new_page(viewport={"width": cw, "height": ch})
        pg.add_init_script(f"window.__CAPTURE__=true;window.__CANVAS__=[{cw},{ch}];window.__DATA__="
                           + json.dumps(data, ensure_ascii=False) + ";")
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        pg.goto((ENGINE / "index.html").resolve().as_uri())
        pg.wait_for_function("window.__READY__ === true", timeout=30000)
        total = expected = 0
        for s in data["segments"]:
            if only and s["scene"] not in only:
                continue
            for t in (round(max(s["start"] + 0.5, s["end"] - 0.35), 2), round((s["start"] + s["end"]) / 2, 2)):
                for r in pg.evaluate(JS, t):
                    print(f'{s["id"]} t={t}: {r}')
                    if r.startswith("expected"):
                        expected += 1
                    else:
                        total += 1
        print("issues:", total, "console errors:", errs,
              f"(+ {expected} expected: question cards flying into the TOC)" if expected else "")
        st = pg.evaluate("""() => ({ mode: ENG.charMode || 'legacy', acts: ENG.charActs || [], plan: ENG.autoPlan || [],
                                    who: ENG.presenter ? ENG.presenter.name : '',
                                    info: ENG.autoInfo ? { on: ENG.autoInfo.on, notes: ENG.autoInfo.notes, mult: ENG.autoInfo.mult } : null })""")
        mins = max(1e-6, data["main_duration"] / 60)
        cnt = {}
        for a in st["acts"]:
            k = f'{a["type"]}:{a["name"]}'
            cnt[k] = cnt.get(k, 0) + 1
        print(f"character{(' ' + st['who']) if st['who'] else ''} ({st['mode']}): explicit actions {len(st['acts'])}"
              + (" — " + ", ".join(f"{k}×{v}" for k, v in sorted(cnt.items())) if cnt else ""))
        if st["info"] is not None:
            auto = {}
            for a in st["plan"]:
                k = a["type"] + (":" + a["name"] if a["type"] == "body" else "")
                auto[k] = auto.get(k, 0) + 1
            print(f"auto layer: {'on' if st['info']['on'] else 'off'} (gesture ×{st['info'].get('mult')}), {len(st['plan'])} items"
                  + (" — " + ", ".join(f"{k} {v} ({v / mins:.1f}/min)" for k, v in sorted(auto.items())) if auto else ""))
            for n in st["info"]["notes"]:
                print("  note:", n)
        b.close()
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
