"""Engine layout check: seeks to the end-state and middle of every segment and reports text overflowing its box,
content intruding into the subtitle band / character / TOC / chapter bar, content leaving the frame, and
low-contrast text: text whose colour is nearly the same as the box painted behind it (contrast ratio < 1.6, e.g.
paper-white text on a paper card, or ink text on the dark scene) -- "low-contrast 1.00: lbl:… text #EDEAE3 on #EDEAE3 (card)".
Also fails on console errors (the same ones that make render.py exit with code 2).
At the end it prints the character's actions: explicit ones from the timeline and the auto layer (ENG.autoPlan, v2 only).
Whiteboard episodes (episode.json "style": "board", hand.js): the ink of every handwritten item (<g data-hand>, SVG, which
the text checks cannot see) is checked against the same zones and the canvas ("intrudes subtitle: hand:一、Jev 是什么");
writing still going on when its scene fades (ENG.handLate) and characters without stroke data (ENG.handMissing) count as
issues. The subtitle band follows ENG.SUB (board: 56 px, up to 1500 px wide, from y 906).
Also (2026-09-28, after the episode-3 whiteboard test), for every episode: contents overlapping each other ("overlap:
A × B": handwriting, the board's printed notes, cards / code / windows / nodes / chips / tokens; an element inside
another is not an overlap), c.P phrases not found in their segment ("phrase-miss"); on the board: handwriting erased
less than 0.8 s after it was written ("hand-short": a page flipped too early -- use c.flip), handwriting that overran
its writing window by more than 0.3 s even written fast ("hand-slow": shorten it or give it more time). The board's
questions flying into the TOC are "expected" like the question cards.
Samples are taken at voice times; on the board the scene layer shows what scenes.js puts LEAD s later.

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
  // subtitle band: centred on the canvas, ENG.SUB.maxw wide (1240: x 340..1580 on 1920, 550..1790 on 2340; board 1500),
  // from 12 px above the subtitle box (y 922; board 906); bar: full width
  const SB = ENG.SUB || { maxw: 1240, top: 934 };
  const zones = [['subtitle', CW / 2 - SB.maxw / 2, SB.top - 12, CW / 2 + SB.maxw / 2, 1000], cz, ['bar', 0, 1000, CW, 1080]];
  if (tr) zones.push(['toc', tr.left - 2, tr.top - 2, tr.right + 2, tr.bottom + 2]);
  // the question cards flying into the TOC (c.questionCards / a card with a "QUESTION 0N" kicker, from ENG.tocInTime()
  // for ~1 s) overlap it by design: reported as "expected", not counted
  const tIn = typeof ENG.tocInTime === 'function' ? ENG.tocInTime() : -1e9;
  const flying = e => { const cd = e.closest('.card'); return t >= tIn - 0.05 && t <= tIn + 1.2 && !!cd && /QUESTION \d/.test(cd.textContent); };
  // ---- contrast: text colour vs what is painted behind the text -- the backgrounds of the element itself, its
  //      card, and any card / chip it was placed over, composited (alpha x opacity) over the navy stage
  const rgbaOf = s => { const m = String(s || '').match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(',').map(parseFloat); return { r: v[0], g: v[1], b: v[2], a: v.length > 3 ? v[3] : 1 }; };
  // what is under everything: the navy stage, or the solid background (episode.json bg_color -> ENG.BG_RGB, painted on
  // #bg; it fades in from navy over the first 0.8 s) -- also what 第 3、4 期's own scenes.js painted on #bg
  const bgEl = document.getElementById('bg'), bgC = bgEl ? rgbaOf(getComputedStyle(bgEl).backgroundColor) : null;
  const NAVY = bgEl && effO(bgEl) > 0.5 && ENG.BG_RGB ? ENG.BG_RGB
    : bgC && bgC.a > 0.5 && bgEl && effO(bgEl) > 0.5 ? { r: bgC.r, g: bgC.g, b: bgC.b } : { r: 27, g: 35, b: 64 };
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
  // handwriting (hand.js: one <g data-hand> per written line / mark, inside the scene's SVG ink layer): the ink box of
  // every item that has started to appear, against the same zones and the canvas
  const ts = t + (ENG.LEAD || 0);                          // the scene clock (board: LEAD s ahead of the voice)
  const flyingHand = g => { const f = g.closest('[data-fly]'); if (!f) return false; const tf = +f.getAttribute('data-fly'); return ts >= tf - 0.05 && ts <= tf + 1.2; };
  const handVis = [];
  for (const g of root.querySelectorAll('g[data-hand]')) {
    if (effO(g) < 0.2) continue;
    if (![...g.querySelectorAll('path')].some(q => q.style.visibility === 'visible')) continue;
    const r = g.getBoundingClientRect();
    if (r.width < 2 && r.height < 2) continue;
    const name = 'hand:' + (g.getAttribute('data-text') || g.getAttribute('data-hand'));
    const fly = flyingHand(g);
    if (g.getAttribute('data-hand') === 'text' && !fly) handVis.push([g, r, name]);
    for (const [zn, x0, y0, x1, y1] of zones) {
      if (r.right > x0 + 1 && r.left < x1 - 1 && r.bottom > y0 + 1 && r.top < y1 - 1)
        out.push(`${zn === 'toc' && fly ? 'expected (question flying into the TOC) ' : ''}intrudes ${zn}: ${name} [${r.left|0},${r.top|0},${r.right|0},${r.bottom|0}]`);
    }
    if (r.left < -1 || r.right > CW + 1 || r.top < -1 || r.bottom > CH + 1) out.push(`offscreen: ${name}`);
  }
  // ---- contents overlapping each other: handwriting, printed board notes, and boxes (an element inside another is not
  //      an overlap; handwriting over a box counts); at least 20 % of the smaller one and 150 px²
  const items = handVis.slice();
  for (const e of root.querySelectorAll('.bNote,.bKick,.bSub,.bSign,.card,.code,.win,.node,.chip,.token')) {
    if (effO(e) < 0.2) continue;
    const r = e.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    items.push([e, r, (typeof e.className === 'string' ? e.className.split(/\s+/)[0] : e.tagName) + ':' + (e.textContent || '').trim().slice(0, 16)]);
  }
  const boxy = e => /\b(card|code|win|node|chip|token)\b/.test(typeof e.className === 'string' ? e.className : '');
  for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) {
    const [a, ra, na] = items[i], [b, rb, nb] = items[j];
    if (a.contains(b) || b.contains(a)) continue;
    if (boxy(a) && boxy(b)) continue;                      // box on box (e.g. a chip on a card) is a layout choice
    const w = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left), h = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
    if (w <= 0 || h <= 0) continue;
    const area = w * h, small = Math.min(ra.width * ra.height, rb.width * rb.height);
    if (area >= 150 && area >= 0.2 * small) out.push(`overlap: ${na} × ${nb} [${Math.max(ra.left, rb.left)|0},${Math.max(ra.top, rb.top)|0} ${w|0}×${h|0}]`);
  }
  return out;
}"""

# per episode (once): handwriting erased too soon after it was written (scene clock; data-t1 / data-out, the scene's
# fade, a flying question counts as seen until it lands), writing that overran its window, phrases not found
HAND_JS = r"""() => {
  const out = { short: [], slow: ENG.handSlow || [], miss: ENG.phraseMiss || [] };
  const scenes = {}; for (const S of ENG.scenes || []) scenes[S.id] = S;
  for (const g of document.querySelectorAll('#scenes g[data-hand="text"]')) {
    const t1 = parseFloat(g.getAttribute('data-t1'));
    if (!isFinite(t1) || g.closest('[data-draft]')) continue;     // the storyboard draft is not timing-checked
    let erase = Infinity;
    for (let x = g; x && x.id !== 'scenes'; x = x.parentNode) {
      const o = x.getAttribute && parseFloat(x.getAttribute('data-out'));
      if (isFinite(o)) erase = Math.min(erase, o);
    }
    const sc = g.closest('[id^="scene_"]'), S = sc && scenes[sc.id.slice(6)];
    if (S && !S.last) erase = Math.min(erase, S.end - 0.36);
    const f = g.closest('[data-fly]');
    if (f) erase = Math.max(erase, +f.getAttribute('data-fly') + 0.7);
    if (isFinite(erase) && erase - t1 < 0.8) out.short.push({ scene: S ? S.id : '?', text: g.getAttribute('data-text') || '', t1: +t1.toFixed(2), erase: +erase.toFixed(2) });
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
        hand = pg.evaluate("() => ({ late: ENG.handLate || [], missing: ENG.handMissing || [], board: !!ENG.BOARD })")
        more = pg.evaluate(HAND_JS)
        for x in more["short"]:
            print(f"hand-short: {x['scene']}「{x['text']}」{x['t1']} s 写完，{x['erase']} s 就擦了（只显示 {x['erase'] - x['t1']:.2f} s；"
                  "翻页用 c.flip，或者提前写 / 短一点）")
            total += 1
        for x in more["slow"]:
            print(f"hand-slow: {x['scene']}「{x['text']}」写字窗 {x['at']}–{x['until']} s，写快了也要写到 {x['end']} s（短一点或多给时间）")
            total += 1
        for x in more["miss"]:
            print(f"phrase-miss: {x['scene']} {x['seg']} 里找不到「{x['phrase']}」（c.P 按兜底比例算的时刻）")
            total += 1
        for x in hand["late"]:
            print(f"hand-late: {x['scene']}「{x['text']}」写到 {x['end']} s，场景 {x['sceneEnd']} s 就淡出了（给长一点的时间窗或写短一点）")
            total += 1
        if hand["missing"]:
            print("hand-missing: 没有笔画数据、写出来会留空的字：" + "".join(hand["missing"]))
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
