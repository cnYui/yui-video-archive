/* pack.js — shared helpers for the 2026-10 intro / outro candidates (A 鼓励球 / B 纸飞机 / C 铅笔灯泡).
 *
 * Everything is Canvas 2D and a pure function of t: the renderer (render.py / add_to_video.py) seeks to any time
 * and calls window.renderAt(t). No requestAnimationFrame, no timers, no Date — all randomness comes from seeded
 * generators created at load time.
 *
 * Frame: 1920x1080 stage, optionally on a wider canvas (window.__CANVAS__ from add_to_video.py, or data.canvas
 * [W, H]; 2340 = 19.5:9). The stage is centred (OX = (FW - 1920) / 2); paper, confetti and the end fade span the
 * whole width. Pages draw in stage coordinates after ctx.translate(OX, 0).
 *
 * Handwriting: window.__HAND__ (common/handdata.js, built by build_handdata.py from the whiteboard engine's stroke
 * data). Characters without stroke data are drawn with a brush font and revealed with a wipe, so nothing is ever
 * left blank.
 */
window.PACK = (function () {
  'use strict';
  const W = 1920, H = 1080;

  /* ------------------------------------------------------------------ random */
  function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function fnv1a(s) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193); } return h >>> 0; }
  /** rngFor('key') -> rnd(a, b): uniform in [a, b) (default [0, 1)), fixed sequence per key */
  function rngFor(key) { const r = mulberry32(fnv1a(String(key))); return (a = 0, b = 1) => a + (b - a) * r(); }

  /* ------------------------------------------------------------------ easing */
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, e) => a + (b - a) * e;
  const prog = (t, t0, t1) => clamp((t - t0) / (t1 - t0));
  const E = {
    linear: x => x,
    inQuad: x => x * x, outQuad: x => 1 - (1 - x) * (1 - x),
    inCubic: x => x * x * x, outCubic: x => 1 - Math.pow(1 - x, 3),
    inOutCubic: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
    inQuart: x => x * x * x * x, outQuart: x => 1 - Math.pow(1 - x, 4),
    inOutQuart: x => x < .5 ? 8 * x * x * x * x : 1 - Math.pow(-2 * x + 2, 4) / 2,
    outExpo: x => x >= 1 ? 1 : 1 - Math.pow(2, -10 * x),
    inOutExpo: x => x <= 0 ? 0 : x >= 1 ? 1 : x < .5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2,
    inOutSine: x => -(Math.cos(Math.PI * x) - 1) / 2,
    outSine: x => Math.sin(x * Math.PI / 2),
    outBack: x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
    outBackSoft: x => { const c1 = 0.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
    outElastic: x => x <= 0 ? 0 : x >= 1 ? 1 : Math.pow(2, -10 * x) * Math.sin((x * 10 - 0.75) * (2 * Math.PI) / 3) + 1,
    outBounce: x => { const n1 = 7.5625, d1 = 2.75; if (x < 1 / d1) return n1 * x * x; if (x < 2 / d1) return n1 * (x -= 1.5 / d1) * x + .75; if (x < 2.5 / d1) return n1 * (x -= 2.25 / d1) * x + .9375; return n1 * (x -= 2.625 / d1) * x + .984375; },
    smooth: x => x * x * (3 - 2 * x),
    minJerk: u => u * u * u * (10 - 15 * u + 6 * u * u),
  };
  /** a pulse: 0 -> 1 -> 0 over [t0, t1], peak at `peak` (0..1 of the window) */
  function pulse(t, t0, t1, peak = 0.3) { const u = prog(t, t0, t1); return u < peak ? E.outCubic(u / peak) : 1 - E.inOutCubic((u - peak) / (1 - peak)); }

  /* ------------------------------------------------------------------ colours */
  const C = {
    paper: '#ECE6D9', paper2: '#E4DCCB',          // page, slightly darker (shadows on paper)
    white: '#FBF8F1',
    ink: '#2A2D4A', ink2: '#5F6280', ink3: '#9A9CB0',   // navy ink, body, light
    coral: '#EC5A3B', coral2: '#C8422A', coralLight: '#FF8A6C',
    gold: '#F2C14E', goldLight: '#FBE08E',
    mint: '#7FCBB3', mint2: '#56A892',
    lavender: '#AFA8E2', pink: '#F2A6B6', sky: '#BFD6EC', sky2: '#9FBFE0',
    grass: '#A3CF8C', grass2: '#73B36E', grass3: '#4E8F55',
    graphite: '#474A66', graphite2: '#8B8EA6',
  };
  const CONFETTI = [C.coral, C.ink, C.mint, C.gold, C.lavender, C.pink, C.sky2];

  /* ------------------------------------------------------------------ canvas setup */
  /** frame width: window.__CANVAS__ (the viewport add_to_video.py opened) > data.canvas [W, H] > 1920. Height stays 1080. */
  function frameWidth(RAW) {
    const pick = v => (Array.isArray(v) && isFinite(+v[0]) ? Math.round(+v[0]) : null);
    const w = pick(window.__CANVAS__) || pick(RAW && RAW.canvas) || W;
    return w >= W && w <= 4096 ? w : W;
  }
  /** builds the page: one <canvas> of FW x 1080, body sized to it. Returns {FW, OX, cv, ctx}. */
  function setup(RAW, background) {
    const FW = frameWidth(RAW), OX = Math.round((FW - W) / 2);
    document.documentElement.style.cssText = `margin:0;width:${FW}px;height:${H}px;overflow:hidden;background:${background || C.paper}`;
    document.body.style.cssText = `margin:0;width:${FW}px;height:${H}px;overflow:hidden;background:${background || C.paper}`;
    const cv = document.createElement('canvas');
    cv.width = FW; cv.height = H; cv.style.cssText = `position:absolute;left:0;top:0;width:${FW}px;height:${H}px`;
    document.body.appendChild(cv);
    return { FW, OX, cv, ctx: cv.getContext('2d') };
  }
  const HEX = /^#(?:[0-9a-fA-F]{3}){1,2}$/;
  const hexOr = (v, d) => (HEX.test(String(v || '').trim()) ? String(v).trim() : d);
  function rgba(hex, a) {
    let h = hex.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join('');
    const n = parseInt(h, 16); return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})`;
  }
  function mixHex(a, b, e) {
    const pa = a.replace('#', ''), pb = b.replace('#', '');
    const ca = [0, 2, 4].map(i => parseInt(pa.substr(i, 2), 16)), cb = [0, 2, 4].map(i => parseInt(pb.substr(i, 2), 16));
    return '#' + ca.map((v, i) => Math.round(lerp(v, cb[i], e)).toString(16).padStart(2, '0')).join('');
  }

  /* ------------------------------------------------------------------ paper */
  /** cream paper with soft mottling, fine grain and a faint vignette (static, drawn once) */
  function makePaper(FW, o = {}) {
    const base = o.base || C.paper, seed = o.seed || 7, cv = document.createElement('canvas');
    cv.width = FW; cv.height = H;
    const g = cv.getContext('2d', { willReadFrequently: true });
    g.fillStyle = base; g.fillRect(0, 0, FW, H);
    // mottling: two layers of low-resolution noise, scaled up with bilinear smoothing, multiplied in
    const rnd = mulberry32(seed);
    for (const [nx, ny, alpha] of [[14, 8, o.mottle != null ? o.mottle : 0.10], [46, 26, (o.mottle != null ? o.mottle : 0.10) * 0.7]]) {
      const s = document.createElement('canvas'); s.width = nx; s.height = ny;
      const sg = s.getContext('2d'), img = sg.createImageData(nx, ny), d = img.data;
      for (let i = 0; i < d.length; i += 4) { const v = Math.round(lerp(150, 255, rnd())); d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255; }
      sg.putImageData(img, 0, 0);
      g.save(); g.globalCompositeOperation = 'multiply'; g.globalAlpha = alpha; g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
      g.drawImage(s, -FW / nx, -H / ny, FW + 2 * FW / nx, H + 2 * H / ny); g.restore();
    }
    // grain
    const grain = o.grain != null ? o.grain : 7;
    if (grain > 0) {
      const img = g.getImageData(0, 0, FW, H), d = img.data, r2 = mulberry32(seed * 7 + 1);
      for (let i = 0; i < d.length; i += 4) { const n = (r2() - 0.5) * 2 * grain; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
      g.putImageData(img, 0, 0);
    }
    // vignette
    const v = o.vignette != null ? o.vignette : 0.10;
    if (v > 0) {
      const rg = g.createRadialGradient(FW / 2, H * 0.5, H * 0.35, FW / 2, H * 0.5, FW * 0.72);
      rg.addColorStop(0, 'rgba(70,50,30,0)'); rg.addColorStop(1, `rgba(70,50,30,${v})`);
      g.fillStyle = rg; g.fillRect(0, 0, FW, H);
    }
    return cv;
  }

  /* ------------------------------------------------------------------ geometry */
  const dist = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);
  /** polyline [[x,y],...] -> [{x, y, s}] with cumulative length, resampled every `step` px (corners kept) */
  function resample(pts, step) {
    const out = [{ x: pts[0][0], y: pts[0][1], s: 0 }];
    let acc = 0;
    for (let i = 1; i < pts.length; i++) {
      const a = pts[i - 1], b = pts[i], L = dist(a, b);
      if (L < 1e-6) continue;
      const n = Math.max(1, Math.ceil(L / step));
      for (let k = 1; k <= n; k++) { const u = k / n; out.push({ x: lerp(a[0], b[0], u), y: lerp(a[1], b[1], u), s: acc + L * u }); }
      acc += L;
    }
    return out;
  }
  /** point on a resampled polyline at arc length s */
  function pointAt(rs, s) {
    if (s <= 0) return rs[0];
    const last = rs[rs.length - 1];
    if (s >= last.s) return last;
    let lo = 0, hi = rs.length - 1;
    while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (rs[mid].s <= s) lo = mid; else hi = mid; }
    const a = rs[lo], b = rs[hi], u = (s - a.s) / ((b.s - a.s) || 1);
    return { x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u), s };
  }
  /** cubic bezier point */
  function bez(p0, p1, p2, p3, u) {
    const v = 1 - u;
    return [v * v * v * p0[0] + 3 * v * v * u * p1[0] + 3 * v * u * u * p2[0] + u * u * u * p3[0],
            v * v * v * p0[1] + 3 * v * v * u * p1[1] + 3 * v * u * u * p2[1] + u * u * u * p3[1]];
  }
  function bezPoly(p0, p1, p2, p3, n = 48) { const o = []; for (let i = 0; i <= n; i++) o.push(bez(p0, p1, p2, p3, i / n)); return o; }
  /** catmull-rom through points -> dense polyline */
  function spline(pts, per = 12) {
    if (pts.length < 3) return pts.slice();
    const out = [];
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
      for (let k = 0; k < per; k++) {
        const t = k / per, t2 = t * t, t3 = t2 * t;
        out.push([0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                  0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)]);
      }
    }
    out.push(pts[pts.length - 1].slice());
    return out;
  }
  /** hand-made wobble: perpendicular low-frequency noise along a polyline (static, seeded) */
  function wobble(pts, amp, seed, freq = 0.012) {
    const rnd = rngFor('wobble' + seed), ph1 = rnd(0, 6.28), ph2 = rnd(0, 6.28), f2 = freq * rnd(2.1, 3.3);
    const rs = resample(pts, 6), out = [];
    for (let i = 0; i < rs.length; i++) {
      const a = rs[Math.max(0, i - 1)], b = rs[Math.min(rs.length - 1, i + 1)];
      const dx = b.x - a.x, dy = b.y - a.y, L = Math.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L;
      const s = rs[i].s, w = amp * (Math.sin(s * freq + ph1) * 0.7 + Math.sin(s * f2 + ph2) * 0.3);
      out.push([rs[i].x + nx * w, rs[i].y + ny * w]);
    }
    return out;
  }

  /* ------------------------------------------------------------------ ink strokes */
  /** draws a variable-width stroke along a resampled polyline up to arc length `upTo` (default: all).
   *  wfn(u) = width at u (0..1 of the full length), so partial strokes keep their profile. */
  function brush(ctx, rs, wfn, color, upTo) {
    const total = rs[rs.length - 1].s;
    if (total <= 0) return;
    const end = upTo == null ? total : clamp(upTo, 0, total);
    ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    let prev = rs[0];
    if (end < 1) { ctx.beginPath(); ctx.arc(prev.x, prev.y, wfn(0) / 2, 0, 6.2832); ctx.fill(); return; }
    for (let i = 1; i < rs.length; i++) {
      let p = rs[i];
      if (p.s > end) { p = pointAt(rs, end); }
      const u = (prev.s + p.s) / 2 / total, w = Math.max(0.6, wfn(u));
      ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(prev.x, prev.y); ctx.lineTo(p.x, p.y); ctx.stroke();
      prev = p;
      if (p.s >= end) break;
    }
  }
  /** a hand-drawn ink line: points -> wobbled, drawn with a soft width profile. p = 0..1 progress. */
  function inkLine(ctx, pts, o = {}) {
    const rs = o._rs || resample(wobble(pts, o.wobble != null ? o.wobble : 1.6, o.seed || 1, o.freq), 4);
    const w = o.width || 4, p = o.p == null ? 1 : clamp(o.p);
    const prof = o.profile || (u => w * (0.78 + 0.22 * Math.sin(Math.PI * clamp(u))));
    if (p <= 0) return rs;
    brush(ctx, rs, prof, o.color || C.ink, rs[rs.length - 1].s * p);
    return rs;
  }
  /** precompute a wobbled, resampled path for inkLine (pass as o._rs) */
  const inkPath = (pts, o = {}) => resample(wobble(pts, o.wobble != null ? o.wobble : 1.6, o.seed || 1, o.freq), 4);

  /* ------------------------------------------------------------------ handwriting */
  const LAT_XH = 0.46, LAT_BASE = 0.36, CJK_ADV = 0.96, SPACE_ADV = 0.3;
  const HD = () => window.__HAND__ || null;
  function glyph(ch) {
    const hd = HD();
    if (ch === ' ') return { kind: 'space', adv: SPACE_ADV };
    if (ch === '　') return { kind: 'space', adv: 1 };
    if (hd && hd.punct[ch]) return { kind: 'punct', adv: hd.punct[ch].adv, s: hd.punct[ch].s };
    if (hd && hd.cjk[ch]) return { kind: 'cjk', adv: CJK_ADV, s: hd.cjk[ch] };
    const lg = hd && hd.lat.g[ch];
    if (lg) return { kind: 'lat', adv: lg.a / hd.lat.xh * LAT_XH, g: lg };
    // font fallback: CJK-ish characters take a full cell, others roughly half
    const cjk = ch.charCodeAt(0) > 0x2E7F;
    return { kind: 'font', adv: cjk ? CJK_ADV : 0.55 };
  }
  const pairs = flat => { const o = []; for (let i = 0; i + 1 < flat.length; i += 2) o.push([flat[i], flat[i + 1]]); return o; };
  const rotP = (p, deg, c) => { const r = deg * Math.PI / 180, x = p[0] - c[0], y = p[1] - c[1]; return [c[0] + x * Math.cos(r) - y * Math.sin(r), c[1] + x * Math.sin(r) + y * Math.cos(r)]; };
  function smoothPts(pts) { return pts.length >= 3 ? spline(pts, 8) : pts; }

  /** width in px of `text` written by hand at `size` */
  function handWidth(text, size) { return [...String(text)].reduce((a, ch) => a + glyph(ch).adv, 0) * size; }

  /**
   * Hand-written text (stroke by stroke, with a pen the scene can follow).
   *   new Hand({text, x, y, size, align, color, t0, t1, seed, pen, fast, font, hop})
   *     x: left / centre / right edge (align), y: middle of the line, size: CJK cell (px)
   *     t0..t1: window to finish in (pen speed fitted; t1 optional -> natural tempo)
   *     pen: stroke width as a fraction of size (default 0.085); font: fallback font family for missing glyphs
   *   .draw(ctx, t)   .pen(t) -> {x, y, down, started, done}   .end (time the last stroke ends)   .box [x0,y0,x1,y1]
   */
  class Hand {
    constructor(o) {
      const text = String(o.text == null ? '' : o.text), size = o.size || 80;
      const rnd = rngFor('hand|' + (o.seed || text));
      const chars = [...text];
      const total = handWidth(text, size);
      const x0 = o.align === 'center' ? o.x - total / 2 : o.align === 'right' ? o.x - total : o.x;
      this.text = text; this.size = size; this.color = o.color || C.ink; this.font = o.font || `${size * 0.92}px 'Ma Shan Zheng'`;
      this.penW = size * (o.pen || 0.085); this.hop = o.hop != null ? o.hop : size * 0.35;
      this.x0 = x0; this.y = o.y; this.width = total; this.left = x0; this.right = x0 + total;
      this.items = []; this.strokes = [];      // strokes: flat list [{rs, len, w, item}]
      let x = x0;
      for (const ch of chars) {
        const gi = glyph(ch), adv = gi.adv * size;
        if (gi.kind === 'space') { x += adv; continue; }
        const item = { ch, kind: gi.kind, cx: x + adv / 2, cy: o.y, adv, strokes: [] };
        if (gi.kind === 'cjk' || gi.kind === 'punct') {
          const k = size / 1024 * (1 + rnd(-0.05, 0.05)), r = rnd(-2.5, 2.5);
          const cx = x + adv / 2 + rnd(-0.03, 0.03) * size, cy = o.y + rnd(-0.03, 0.03) * size;
          for (const flat of gi.s) {
            let pts = pairs(flat);
            if (gi.kind === 'cjk' && pts.length > 1) {
              const c = [(pts[0][0] + pts[pts.length - 1][0]) / 2, (pts[0][1] + pts[pts.length - 1][1]) / 2];
              const sr = rnd(-2.2, 2.2), sx = rnd(-14, 14), sy = rnd(-14, 14);
              pts = pts.map((p, j) => { const a = (j === 0 || j === pts.length - 1) ? 4 : 8; const q = rotP(p, sr, c); return [q[0] + sx + rnd(-a, a), q[1] + sy + rnd(-a, a)]; });
            }
            pts = pts.map(p => rotP(p, r, [0, 0])).map(p => [cx + p[0] * k, cy + p[1] * k]);
            this._addStroke(item, smoothPts(pts), rnd);
          }
        } else if (gi.kind === 'lat') {
          const hd = HD(), s = LAT_XH * size / hd.lat.xh, base = o.y + LAT_BASE * size;
          const r = rnd(-3, 3), kk = 1 + rnd(-0.04, 0.04), dy = rnd(-0.02, 0.02) * size, dx = rnd(-0.02, 0.02) * size;
          const c = [x + adv / 2 + dx, base - 0.5 * LAT_XH * size + dy];
          let latStrokes = gi.g.s;
          if (ch === 'I' && latStrokes.length === 1) {              // a bare stem reads as "l": give the capital I its serifs
            const st = latStrokes[0], ys = st.filter((_, i) => i % 2), xs = st.filter((_, i) => !(i % 2));
            const top = Math.min(...ys), bot = Math.max(...ys), xm = (Math.min(...xs) + Math.max(...xs)) / 2, h = bot - top;
            latStrokes = [[xm - h * 0.22, top, xm + h * 0.22, top], st, [xm - h * 0.22, bot, xm + h * 0.22, bot]];
          }
          for (const flat of latStrokes) {
            let pts = pairs(flat).map(([gx, gy]) => [x + gx * s + dx, base + gy * s + dy]).map(p => rotP([c[0] + (p[0] - c[0]) * kk, c[1] + (p[1] - c[1]) * kk], r, c));
            if (pts.length === 2) { const [a, b] = pts, m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], n = dist(a, b) || 1, off = rnd(-0.015, 0.015) * n; pts = [a, [m[0] - (b[1] - a[1]) / n * off, m[1] + (b[0] - a[0]) / n * off], b]; }
            this._addStroke(item, smoothPts(pts), rnd, true);
          }
        } else {  // font fallback: one pseudo stroke (a wipe across the cell)
          const st = { rs: resample([[x, o.y], [x + adv, o.y]], 4), len: size * 1.1, w: this.penW, item, font: true };
          item.strokes.push(st); this.strokes.push(st);
        }
        this.items.push(item);
        x += adv;
      }
      // box
      let bx0 = 1e9, by0 = 1e9, bx1 = -1e9, by1 = -1e9;
      for (const st of this.strokes) for (const p of st.rs) { bx0 = Math.min(bx0, p.x); by0 = Math.min(by0, p.y); bx1 = Math.max(bx1, p.x); by1 = Math.max(by1, p.y); }
      if (bx0 > bx1) { bx0 = x0; bx1 = x0 + total; by0 = o.y - size / 2; by1 = o.y + size / 2; }
      this.box = [bx0 - this.penW, Math.min(by0, o.y - size * 0.5) - this.penW, bx1 + this.penW, Math.max(by1, o.y + size * 0.5) + this.penW];
      this._schedule(o.t0 || 0, o.t1, o.fast);
    }
    _addStroke(item, pts, rnd, latin) {
      const rs = resample(pts, 3), len = rs[rs.length - 1].s;
      if (len < 0.5) return;
      // brush profile: a firm start, fuller middle, tapered end on sweeping strokes
      const a = rs[Math.max(0, rs.length - 6)], b = rs[rs.length - 1];
      const ex = b.x - a.x, ey = b.y - a.y, eL = Math.hypot(ex, ey) || 1;
      const sweep = !latin && (ey / eL > 0.45 || (ex / eL < -0.5 && ey / eL > 0.2)) && len > this.size * 0.22;
      const end = sweep ? 0.42 : 0.92, mid = latin ? 1.0 : 1.08, start = latin ? 0.95 : 1.0, var1 = rnd(0.94, 1.06);
      const st = { rs, len, w: this.penW * var1, item, prof: u => (u < 0.5 ? lerp(start, mid, E.outQuad(u * 2)) : lerp(mid, end, E.inQuad((u - 0.5) * 2))) };
      item.strokes.push(st); this.strokes.push(st);
    }
    _schedule(t0, t1, fast) {
      const S = this.strokes, size = this.size, n = S.length;
      this.t0 = t0;
      if (!n) { this.end = t0; return; }
      let ps = 0.025, pc = 0.075;                               // pen lifts: between strokes / between characters
      const vNat = 15 * size, vMin = 8 * size, vMax = (fast ? 70 : 36) * size, MS = 0.03;
      const gaps = () => { let g = 0; for (let i = 1; i < n; i++) g += S[i].item === S[i - 1].item ? ps : pc; return g; };
      const need = v => S.reduce((a, s) => a + Math.max(MS, s.len / v), 0);
      let v = vNat;
      if (t1 != null && t1 > t0) {
        const avail = t1 - t0;
        if (gaps() > avail * 0.4) { const f = Math.max(0.25, avail * 0.4 / gaps()); ps *= f; pc *= f; }
        const body = avail - gaps();
        if (body > n * MS) { let lo = 1, hi = 1e7; for (let it = 0; it < 60; it++) { const m = Math.sqrt(lo * hi); if (need(m) > body) lo = m; else hi = m; } v = hi; }
        else v = vMax;
        v = Math.min(vMax, Math.max(vMin, v));
      }
      let t = t0;
      S.forEach((s, i) => { if (i) t += S[i].item === S[i - 1].item ? ps : pc; s.a = t; s.b = t + Math.max(MS, s.len / v); t = s.b; });
      this.end = t;
    }
    /** arc length drawn of stroke s at time t */
    _upto(s, t) { if (t >= s.b) return s.len; if (t <= s.a) return 0; const u = (t - s.a) / (s.b - s.a); return s.len * (0.4 * u + 0.6 * E.minJerk(u)); }
    draw(ctx, t, color) {
      const col = color || this.color;
      for (const s of this.strokes) {
        if (t <= s.a) continue;
        const up = this._upto(s, t);
        if (s.font) {
          const it = s.item, p = up / s.len;
          ctx.save(); ctx.beginPath(); ctx.rect(it.cx - it.adv / 2 - 4, this.y - this.size * 0.7, (it.adv + 8) * p, this.size * 1.4); ctx.clip();
          ctx.fillStyle = col; ctx.font = this.font; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          ctx.fillText(it.ch, it.cx, this.y + this.size * 0.02); ctx.restore();
        } else {
          brush(ctx, s.rs, u => s.w * s.prof(u), col, up);
        }
      }
    }
    /** pen tip at time t (the ball / pencil follows it) */
    pen(t) {
      const S = this.strokes;
      if (!S.length) return { x: this.x0, y: this.y, down: false, started: false, done: true };
      const first = S[0], last = S[S.length - 1];
      if (t <= first.a) { const p = first.rs[0]; return { x: p.x, y: p.y, down: false, started: false, done: false }; }
      if (t >= last.b) { const p = last.rs[last.rs.length - 1]; return { x: p.x, y: p.y, down: false, started: true, done: true }; }
      for (let i = 0; i < S.length; i++) {
        const s = S[i];
        if (t >= s.a && t < s.b) {
          if (s.font) { const it = s.item, u = this._upto(s, t) / s.len; return { x: it.cx - it.adv / 2 + it.adv * u, y: this.y + this.size * 0.25, down: true, started: true, done: false }; }
          const p = pointAt(s.rs, this._upto(s, t)); return { x: p.x, y: p.y, down: true, started: true, done: false };
        }
        if (t >= s.b && t < S[i + 1].a) {
          const nx = S[i + 1], a = s.font ? { x: s.item.cx + s.item.adv / 2, y: this.y + this.size * 0.25 } : s.rs[s.rs.length - 1];
          const b = nx.font ? { x: nx.item.cx - nx.item.adv / 2, y: this.y + this.size * 0.25 } : nx.rs[0];
          const u = E.inOutSine((t - s.b) / (nx.a - s.b)), hop = Math.min(this.hop, dist([a.x, a.y], [b.x, b.y]) * 0.5 + 6);
          return { x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u) - Math.sin(Math.PI * u) * hop, down: false, started: true, done: false };
        }
      }
      const p = last.rs[last.rs.length - 1]; return { x: p.x, y: p.y, down: false, started: true, done: true };
    }
  }

  /* ------------------------------------------------------------------ confetti */
  /**
   * new Confetti({seed, t0, n, box:[x0,y0,x1,y1] | origin:[x,y], speed:[min,max], dir:[deg0,deg1], life:[min,max],
   *               shapes:['rect','dot','squig','tri'], colors, size:[min,max], gravity, drag, spread})
   * .draw(ctx, t)
   */
  class Confetti {
    constructor(o) {
      const rnd = rngFor('confetti|' + (o.seed || 1));
      this.t0 = o.t0 || 0; this.g = o.gravity != null ? o.gravity : 900; this.k = o.drag != null ? o.drag : 2.4;
      const shapes = o.shapes || ['rect', 'dot', 'squig', 'tri'], colors = o.colors || CONFETTI;
      this.p = [];
      for (let i = 0; i < (o.n || 60); i++) {
        const x = o.origin ? o.origin[0] : rnd(o.box[0], o.box[2]), y = o.origin ? o.origin[1] : rnd(o.box[1], o.box[3]);
        const sp = rnd(o.speed ? o.speed[0] : 200, o.speed ? o.speed[1] : 900), ang = rnd(o.dir ? o.dir[0] : -160, o.dir ? o.dir[1] : -20) * Math.PI / 180;
        this.p.push({ x, y, vx: Math.cos(ang) * sp, vy: Math.sin(ang) * sp, shape: shapes[Math.floor(rnd(0, shapes.length)) % shapes.length], col: colors[Math.floor(rnd(0, colors.length)) % colors.length],
          size: rnd(o.size ? o.size[0] : 8, o.size ? o.size[1] : 22), rot: rnd(0, 6.28), rv: rnd(-7, 7), life: rnd(o.life ? o.life[0] : 1.6, o.life ? o.life[1] : 2.6),
          fl: rnd(0, 6.28), fa: rnd(8, 26), fw: rnd(5, 9), delay: rnd(0, o.stagger || 0), ar: rnd(0.35, 0.7) });
      }
    }
    draw(ctx, t) {
      for (const q of this.p) {
        const tau = t - this.t0 - q.delay;
        if (tau <= 0 || tau > q.life) continue;
        const k = this.k, d = 1 - Math.exp(-k * tau);
        const x = q.x + q.vx * d / k + Math.sin(q.fw * tau + q.fl) * q.fa * clamp(tau * 2);
        const y = q.y + q.vy * d / k + this.g * (tau - d / k) / k;
        const a = clamp((q.life - tau) / 0.5);
        ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.rotate(q.rot + q.rv * tau); ctx.fillStyle = q.col; ctx.strokeStyle = q.col;
        const s = q.size;
        if (q.shape === 'rect') { ctx.scale(1, Math.abs(Math.cos(tau * 4 + q.fl)) * 0.8 + 0.2); ctx.fillRect(-s / 2, -s * q.ar / 2, s, s * q.ar); }
        else if (q.shape === 'dot') { ctx.beginPath(); ctx.arc(0, 0, s * 0.28, 0, 6.2832); ctx.fill(); }
        else if (q.shape === 'tri') { ctx.beginPath(); ctx.moveTo(-s / 2, s * 0.4); ctx.lineTo(s / 2, s * 0.4); ctx.lineTo(0, -s * 0.45); ctx.closePath(); ctx.fill(); }
        else { ctx.lineWidth = s * 0.16; ctx.lineCap = 'round'; ctx.beginPath(); for (let i = 0; i <= 8; i++) { const u = i / 8; const px = -s * 0.6 + s * 1.2 * u, py = Math.sin(u * 6.28 * 1.5) * s * 0.22; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); } ctx.stroke(); }
        ctx.restore();
      }
    }
  }
  /** ink splatter: dots that burst out and settle quickly (the reference's red / navy specks around the title) */
  function splat(o) { return new Confetti(Object.assign({ shapes: ['dot'], speed: [60, 520], dir: [-170, -10], life: [2.2, 3.2], size: [5, 16], gravity: 520, drag: 5.5, colors: o.colors || [C.coral, C.coral, C.ink] }, o)); }

  /* ------------------------------------------------------------------ text */
  const CLOSE_PUNCT = '，。、：；！？）】」』》〉”’…';
  /** wrap `text` (current ctx.font) into lines no wider than maxW: break after CJK characters or at spaces; a long
   *  Latin word / URL is broken by character; closing punctuation never starts a line */
  function wrapText(ctx, text, maxW, maxLines) {
    const chars = [...String(text)], lines = [];
    let line = '', word = '';
    const flush = () => { if (line) lines.push(line); line = ''; };
    const push = tok => {
      const cand = line + tok;
      if (ctx.measureText(cand).width <= maxW || !line) {
        if (ctx.measureText(cand).width > maxW && tok.length > 1) {      // a single token wider than the line: break by char
          for (const ch of [...tok]) { if (ctx.measureText(line + ch).width > maxW && line) flush(); line += ch; }
        } else line = cand;
      } else { flush(); line = tok.replace(/^ +/, ''); }
    };
    for (let i = 0; i < chars.length; i++) {
      const ch = chars[i], cjk = ch.charCodeAt(0) > 0x2E7F;
      if (cjk || ch === ' ') { if (word) { push(word); word = ''; } if (CLOSE_PUNCT.includes(ch)) line += ch; else push(ch); }
      else word += ch;
    }
    if (word) push(word);
    flush();
    // closing punctuation that landed at a line start goes back to the previous line
    for (let i = 1; i < lines.length; i++) while (lines[i] && CLOSE_PUNCT.includes(lines[i][0])) { lines[i - 1] += lines[i][0]; lines[i] = lines[i].slice(1); }
    const out = lines.filter(l => l.length);
    if (maxLines && out.length > maxLines) { const keep = out.slice(0, maxLines); keep[maxLines - 1] = keep[maxLines - 1].replace(/.{2}$/, '') + '…'; return keep; }
    return out;
  }
  /** letter-spaced text (Chromium canvas letterSpacing); returns the width */
  function spacedText(ctx, text, x, y, spacing, align = 'center') {
    ctx.save(); ctx.letterSpacing = spacing + 'px';
    const w = ctx.measureText(text).width - spacing;   // trailing spacing is not visible
    const sx = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
    ctx.textAlign = 'left'; ctx.fillText(text, sx, y); ctx.restore();
    return w;
  }

  /**
   * Credits layout for the outros: up to two columns (references, thanks), fitted to a box.
   *   layoutCredits(ctx, {references:[str], thanks:[{label, value}]}, {x0, y0, x1, y1, gap}, {fontBody, fontNum, fontLabel, fsMax, fsMin, lh, maxLines})
   *   -> {fs, cols:[{kind:'refs'|'thanks', x, w, entries:[{num, label, labelW, lines:[str], y, h}], height}]}
   *   fonts are templates with %s for the size: "500 %spx 'Noto Sans SC'"
   */
  function layoutCredits(ctx, data, box, o) {
    const refs = (data.references || []).map(s => String(s || '').trim()).filter(Boolean).slice(0, o.maxRefs || 8);
    const thanks = (data.thanks || []).map(t => typeof t === 'string' ? { label: '', value: t } : { label: String(t.label || '').trim(), value: String(t.value || '').trim() }).filter(t => t.label || t.value).slice(0, o.maxThanks || 8);
    const kinds = []; if (refs.length) kinds.push('refs'); if (thanks.length) kinds.push('thanks');
    const gap = o.gap || 80, bw = box.x1 - box.x0, boxH = box.y1 - box.y0;
    const widths = kinds.length === 2 ? [Math.round((bw - gap) * (o.split || 0.58)), 0] : [bw, 0];
    if (kinds.length === 2) widths[1] = bw - gap - widths[0];
    const lhF = o.lh || 1.42, maxLines = o.maxLines || 2;
    const font = (tpl, fs) => tpl.replace('%s', fs);
    let best = null;
    for (let fs = o.fsMax || 32; fs >= (o.fsMin || 20); fs--) {
      const lh = o.lhFixed || Math.round(fs * lhF), egap = o.lhFixed ? Math.round(o.lhFixed * (o.entryGap == null ? 0 : o.entryGap)) : Math.round(fs * (o.entryGap == null ? 0.5 : o.entryGap));
      const cols = kinds.map((kind, ci) => {
        const x = ci === 0 ? box.x0 : box.x0 + widths[0] + gap, w = widths[ci];
        const entries = [];
        if (kind === 'refs') {
          ctx.font = font(o.fontNum, fs); const numW = Math.ceil(ctx.measureText('[8]').width) + Math.round(fs * 0.5);
          ctx.font = font(o.fontBody, fs);
          refs.forEach((r, i) => { const lines = wrapText(ctx, r, w - numW, maxLines); entries.push({ num: `[${i + 1}]`, numW, lines, h: lines.length * lh }); });
        } else {
          ctx.font = font(o.fontLabel, fs);
          const labelW = Math.max(0, ...thanks.map(t => t.label ? ctx.measureText(t.label).width : 0));
          const lw = labelW ? Math.ceil(labelW) + Math.round(fs * 0.9) : 0;
          ctx.font = font(o.fontBody, fs);
          thanks.forEach(t => { const lines = t.value ? wrapText(ctx, t.value, w - lw, maxLines) : ['']; entries.push({ label: t.label, labelW: lw, lines, h: lines.length * lh }); });
        }
        let y = box.y0; entries.forEach(e => { e.y = y; y += e.h + egap; });
        return { kind, x, w, entries, height: y - egap - box.y0 };
      });
      best = { fs, lh, cols, egap };
      if (cols.every(c => c.height <= boxH)) break;
    }
    return best;
  }

  /* ------------------------------------------------------------------ the ball (A) */
  /**
   * drawBall(ctx, {x, y, r, sx, sy, rot, look:[dx,dy] (-1..1), blink (0..1 closed), wink (0..1, right eye), smile (0..1),
   *               shadow:{y, k} ground shadow (k = strength), color})
   */
  function drawBall(ctx, o) {
    const r = o.r || 34, sx = o.sx || 1, sy = o.sy || 1, col = o.color || C.coral;
    if (o.shadow) {
      const sw = r * 1.1 * (o.shadow.k != null ? o.shadow.k : 1) * sx;
      ctx.save(); ctx.globalAlpha = 0.18 * (o.shadow.a != null ? o.shadow.a : 1); ctx.fillStyle = '#3B2F28';
      ctx.beginPath(); ctx.ellipse(o.x, o.shadow.y, sw, Math.max(3, sw * 0.26), 0, 0, 6.2832); ctx.fill(); ctx.restore();
    }
    ctx.save(); ctx.translate(o.x, o.y); ctx.rotate(o.rot || 0); ctx.scale(sx, sy);
    const g = ctx.createRadialGradient(-r * 0.35, -r * 0.4, r * 0.1, 0, 0, r * 1.05);
    g.addColorStop(0, mixHex(col, '#FFFFFF', 0.28)); g.addColorStop(0.55, col); g.addColorStop(1, mixHex(col, '#000000', 0.22));
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, r, 0, 6.2832); ctx.fill();
    // specular
    ctx.save(); ctx.globalAlpha = 0.55; ctx.fillStyle = '#FFFFFF'; ctx.beginPath(); ctx.ellipse(-r * 0.36, -r * 0.5, r * 0.26, r * 0.13, -0.6, 0, 6.2832); ctx.fill(); ctx.restore();
    ctx.rotate(-(o.rot || 0)); ctx.scale(1 / sx, 1 / sy);        // face stays upright and unsquashed
    const look = o.look || [0, 0], ex = r * 0.25, ey = -r * 0.1, er = r * 0.17;
    const blink = clamp(o.blink || 0), wink = clamp(o.wink || 0);
    for (const side of [-1, 1]) {
      const cx = side * ex + look[0] * r * 0.05, cy = ey + look[1] * r * 0.04, closed = side === 1 ? Math.max(blink, wink) : blink;
      if (closed >= 0.98) {   // a happy closed eye: a short arc
        ctx.strokeStyle = C.ink; ctx.lineWidth = Math.max(2, r * 0.07); ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(cx, cy + er * 0.2, er * 0.9, Math.PI * 1.15, Math.PI * 1.85); ctx.stroke(); continue;
      }
      ctx.fillStyle = '#FFFFFF'; ctx.beginPath(); ctx.ellipse(cx, cy, er, er * 1.15 * (1 - closed), 0, 0, 6.2832); ctx.fill();
      ctx.fillStyle = C.ink; ctx.beginPath(); ctx.ellipse(cx + look[0] * er * 0.45, cy + look[1] * er * 0.4, er * 0.5, er * 0.58 * (1 - closed), 0, 0, 6.2832); ctx.fill();
      ctx.fillStyle = '#FFFFFF'; ctx.beginPath(); ctx.arc(cx + look[0] * er * 0.45 - er * 0.15, cy + look[1] * er * 0.4 - er * 0.22, er * 0.14, 0, 6.2832); ctx.fill();
    }
    const smile = o.smile == null ? 0.6 : clamp(o.smile);
    if (smile > 0) { ctx.strokeStyle = C.ink; ctx.lineWidth = Math.max(2, r * 0.07); ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(0, r * 0.08, r * 0.3, Math.PI * (0.5 - 0.28 * smile), Math.PI * (0.5 + 0.28 * smile)); ctx.stroke(); }
    ctx.restore();
  }

  /* ------------------------------------------------------------------ misc drawing */
  /** paper-cut cloud: a cluster of white bumps with a soft offset shadow */
  function drawCloud(ctx, x, y, s, o = {}) {
    const bumps = o.bumps || [[-0.55, 0.05, 0.33], [-0.15, -0.18, 0.42], [0.3, -0.08, 0.38], [0.62, 0.12, 0.28]];
    const path = (dx, dy) => { ctx.beginPath(); ctx.moveTo(x - 0.9 * s + dx, y + 0.22 * s + dy); for (const [bx, by, br] of bumps) ctx.arc(x + bx * s + dx, y + by * s + dy, br * s, Math.PI, 0); ctx.lineTo(x + 0.9 * s + dx, y + 0.22 * s + dy); ctx.closePath(); };
    ctx.save(); ctx.globalAlpha = (o.alpha == null ? 1 : o.alpha);
    ctx.fillStyle = o.shadow || 'rgba(120,100,110,0.22)'; path(s * 0.06, s * 0.08); ctx.fill();
    ctx.fillStyle = o.color || C.white; path(0, 0); ctx.fill();
    if (o.outline) { ctx.strokeStyle = o.outline; ctx.lineWidth = 2; path(0, 0); ctx.stroke(); }
    ctx.restore();
  }
  /** a small sun with hand-drawn rays */
  function drawSun(ctx, x, y, r, o = {}) {
    const rays = o.rays == null ? 1 : clamp(o.rays), n = 12, rnd = rngFor('sun' + (o.seed || 1));
    ctx.save();
    ctx.fillStyle = o.color || C.gold; ctx.beginPath(); ctx.arc(x, y, r, 0, 6.2832); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.beginPath(); ctx.arc(x - r * 0.25, y - r * 0.25, r * 0.45, 0, 6.2832); ctx.fill();
    ctx.strokeStyle = o.ink || C.coral; ctx.lineWidth = 3; ctx.lineCap = 'round';
    for (let i = 0; i < n; i++) {
      const a = i / n * 6.2832 + rnd(-0.08, 0.08), L = r * rnd(0.28, 0.5) * rays, r0 = r * 1.28;
      ctx.beginPath(); ctx.moveTo(x + Math.cos(a) * r0, y + Math.sin(a) * r0); ctx.lineTo(x + Math.cos(a) * (r0 + L), y + Math.sin(a) * (r0 + L)); ctx.stroke();
    }
    ctx.restore();
  }
  /** paper plane (B): nose at +x, ~82 px long at s = 1; optional ground shadow at shadowY */
  function drawPlane(ctx, x, y, a, s, shadowY) {
    if (shadowY != null) { ctx.save(); ctx.globalAlpha = 0.16; ctx.fillStyle = '#3B2F28'; ctx.beginPath(); ctx.ellipse(x, shadowY, 46 * s, 9 * s, 0, 0, 6.2832); ctx.fill(); ctx.restore(); }
    ctx.save(); ctx.translate(x, y); ctx.rotate(a); ctx.scale(s, s);
    ctx.lineJoin = 'round'; ctx.lineWidth = 3 / Math.sqrt(s); ctx.strokeStyle = C.ink;
    ctx.fillStyle = '#D9D3C6'; ctx.beginPath(); ctx.moveTo(44, 0); ctx.lineTo(-30, 20); ctx.lineTo(-22, 2); ctx.closePath(); ctx.fill(); ctx.stroke();   // lower wing
    ctx.fillStyle = C.white; ctx.beginPath(); ctx.moveTo(44, 0); ctx.lineTo(-38, -24); ctx.lineTo(-22, 2); ctx.closePath(); ctx.fill(); ctx.stroke();    // upper wing
    ctx.fillStyle = '#EDE8DD'; ctx.beginPath(); ctx.moveTo(44, 0); ctx.lineTo(-22, 2); ctx.lineTo(-28, 12); ctx.closePath(); ctx.fill(); ctx.stroke();   // keel
    ctx.restore();
  }
  /** pencil (C): tip at (x, y), body leaning along `angle` (rad, from the tip towards the eraser), ~350 px long at s = 1 */
  function drawPencil(ctx, x, y, angle, s = 1, o = {}) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(angle); ctx.scale(s, s);
    const W2 = 15;
    if (o.shadow !== false) { ctx.save(); ctx.globalAlpha = 0.12; ctx.fillStyle = '#3B2F28'; ctx.beginPath(); ctx.moveTo(6, 10); ctx.lineTo(40, W2 + 10); ctx.lineTo(350, W2 + 10); ctx.lineTo(350, -W2 + 10); ctx.lineTo(40, -W2 + 10); ctx.closePath(); ctx.fill(); ctx.restore(); }
    ctx.lineJoin = 'round'; ctx.lineWidth = 3; ctx.strokeStyle = C.ink;
    // wood cone + graphite point
    ctx.fillStyle = '#EBD2AC'; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(42, -W2); ctx.lineTo(42, W2); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.fillStyle = C.graphite; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(12, -4.3); ctx.lineTo(12, 4.3); ctx.closePath(); ctx.fill();
    // body (three faces)
    ctx.fillStyle = C.gold; ctx.fillRect(42, -W2, 262, W2 * 2);
    ctx.fillStyle = '#E2AE3C'; ctx.fillRect(42, W2 * 0.3, 262, W2 * 0.7);
    ctx.fillStyle = '#FBE08E'; ctx.fillRect(42, -W2, 262, W2 * 0.45);
    ctx.strokeRect(42, -W2, 262, W2 * 2);
    // ferrule + eraser
    ctx.fillStyle = '#CDD0D6'; ctx.fillRect(304, -W2, 22, W2 * 2); ctx.strokeRect(304, -W2, 22, W2 * 2);
    ctx.beginPath(); ctx.moveTo(311, -W2); ctx.lineTo(311, W2); ctx.moveTo(319, -W2); ctx.lineTo(319, W2); ctx.stroke();
    ctx.fillStyle = C.pink; ctx.beginPath(); ctx.roundRect(326, -W2, 30, W2 * 2, [0, 9, 9, 0]); ctx.fill(); ctx.stroke();
    ctx.restore();
  }
  /** light bulb (C): glass centred at (cx, cy) radius r; o.lit 0..1, o.rays 0..1, o.face 0..1, o.blink, o.wink, o.glow */
  function drawBulb(ctx, cx, cy, r, o = {}) {
    const lit = clamp(o.lit == null ? 1 : o.lit), rays = clamp(o.rays == null ? lit : o.rays), face = clamp(o.face == null ? lit : o.face);
    const neckY = cy + r * 0.82, baseY = cy + r * 1.62, nw = r * 0.58;
    ctx.save();
    if (lit > 0 && o.glow !== false) {
      const g = ctx.createRadialGradient(cx, cy, r * 0.6, cx, cy, r * 2.6);
      g.addColorStop(0, `rgba(242,193,78,${0.42 * lit})`); g.addColorStop(1, 'rgba(242,193,78,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, r * 2.6, 0, 6.2832); ctx.fill();
    }
    // glass + neck fill
    const gl = ctx.createRadialGradient(cx - r * 0.25, cy - r * 0.3, r * 0.1, cx, cy, r * 1.1);
    gl.addColorStop(0, mixHex('#FBE08E', '#F8F4EC', 1 - lit)); gl.addColorStop(1, mixHex(C.gold, '#EFEAE0', 1 - lit));
    ctx.fillStyle = gl; ctx.beginPath(); ctx.arc(cx, cy, r, 0, 6.2832); ctx.fill();
    ctx.fillStyle = mixHex(C.gold, '#EFEAE0', 1 - lit); ctx.fillRect(cx - nw, neckY - r * 0.2, nw * 2, baseY - neckY + r * 0.2 - r * 0.46);
    // outline (hand-ish)
    ctx.strokeStyle = o.ink || C.graphite; ctx.lineWidth = o.lw || 5; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI * 0.69, Math.PI * 2.31); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx - nw, neckY - r * 0.1); ctx.lineTo(cx - nw, baseY - r * 0.46); ctx.moveTo(cx + nw, neckY - r * 0.1); ctx.lineTo(cx + nw, baseY - r * 0.46); ctx.stroke();
    ctx.fillStyle = '#CDD0D6'; ctx.beginPath(); ctx.roundRect(cx - nw - 2, baseY - r * 0.46, nw * 2 + 4, r * 0.46, 4); ctx.fill(); ctx.stroke();
    for (let i = 1; i <= 2; i++) { const yy = baseY - r * 0.46 + r * 0.46 * i / 3; ctx.beginPath(); ctx.moveTo(cx - nw - 2, yy); ctx.lineTo(cx + nw + 2, yy); ctx.stroke(); }
    ctx.fillStyle = C.graphite; ctx.beginPath(); ctx.roundRect(cx - nw * 0.5, baseY, nw, r * 0.16, 3); ctx.fill();
    // filament
    if (face < 0.5) { ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(cx - nw * 0.6, neckY); ctx.lineTo(cx - r * 0.3, cy - r * 0.1); ctx.lineTo(cx - r * 0.1, cy + r * 0.3); ctx.lineTo(cx + r * 0.1, cy - r * 0.1); ctx.lineTo(cx + r * 0.3, cy + r * 0.3); ctx.lineTo(cx + nw * 0.6, neckY); ctx.stroke(); }
    // rays
    if (rays > 0) { const rnd = rngFor('bulbrays'); ctx.strokeStyle = o.rayColor || C.coral; ctx.lineWidth = 4; for (let i = 0; i < 11; i++) { const a = -Math.PI * 1.08 + i / 10 * Math.PI * 1.16 + rnd(-0.06, 0.06), r0 = r * 1.3, L = r * rnd(0.26, 0.42) * clamp(rays * 1.4 - i * 0.04); if (L <= 0) continue; ctx.beginPath(); ctx.moveTo(cx + Math.cos(a) * r0, cy + Math.sin(a) * r0); ctx.lineTo(cx + Math.cos(a) * (r0 + L), cy + Math.sin(a) * (r0 + L)); ctx.stroke(); } }
    // face
    if (face > 0) {
      ctx.save(); ctx.globalAlpha = face;
      const blink = clamp(o.blink || 0), wink = clamp(o.wink || 0), ex = r * 0.3, ey = cy - r * 0.05, er = r * 0.075;
      for (const side of [-1, 1]) {
        const closed = side === 1 ? Math.max(blink, wink) : blink;
        if (closed >= 0.98) { ctx.strokeStyle = C.ink; ctx.lineWidth = 3.5; ctx.beginPath(); ctx.arc(cx + side * ex, ey + er, er * 1.6, Math.PI * 1.15, Math.PI * 1.85); ctx.stroke(); continue; }
        ctx.fillStyle = C.ink; ctx.beginPath(); ctx.ellipse(cx + side * ex, ey, er, er * 1.25 * (1 - closed), 0, 0, 6.2832); ctx.fill();
        ctx.fillStyle = '#FFFFFF'; ctx.beginPath(); ctx.arc(cx + side * ex - er * 0.3, ey - er * 0.4, er * 0.3, 0, 6.2832); ctx.fill();
      }
      ctx.strokeStyle = C.ink; ctx.lineWidth = 3.5; ctx.beginPath(); ctx.arc(cx, cy + r * 0.12, r * 0.26, Math.PI * 0.2, Math.PI * 0.8); ctx.stroke();
      ctx.restore();
    }
    ctx.restore();
  }
  /** full-frame colour fade (end of an intro) */
  function fade(ctx, FW, color, a) { if (a <= 0 || !color || color === 'none') return; ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = clamp(a); ctx.fillStyle = color; ctx.fillRect(0, 0, FW, H); ctx.restore(); }
  /** little dust puffs at a landing: n grey rings expanding and fading over [t0, t0+dur] */
  function dust(ctx, x, y, t, t0, o = {}) {
    const u = prog(t, t0, t0 + (o.dur || 0.45)); if (u <= 0 || u >= 1) return;
    const rnd = rngFor('dust' + (o.seed || 1) + t0.toFixed(2)), n = o.n || 6;
    ctx.save(); ctx.globalAlpha = (1 - u) * 0.5; ctx.strokeStyle = o.color || C.ink3; ctx.lineWidth = 2.5;
    for (let i = 0; i < n; i++) { const a = rnd(-3.0, -0.2), sp = rnd(40, 110) * (o.scale || 1), r = rnd(3, 7); ctx.beginPath(); ctx.arc(x + Math.cos(a) * sp * E.outCubic(u), y + Math.sin(a) * sp * E.outCubic(u) * 0.5 + 2, r * (1 - u * 0.5), 0, 6.2832); ctx.stroke(); }
    ctx.restore();
  }

  /* ------------------------------------------------------------------ fonts */
  /** resolves when the listed fonts (css font strings) are loaded; the page then sets window.__READY__ = true */
  function fontsReady(specs) {
    return Promise.all(specs.map(s => document.fonts.load(s).catch(() => []))).then(() => document.fonts.ready);
  }

  return { W, H, C, CONFETTI, mulberry32, fnv1a, rngFor, clamp, lerp, prog, E, pulse, frameWidth, setup, hexOr, rgba, mixHex, makePaper,
           dist, resample, pointAt, bez, bezPoly, spline, wobble, brush, inkLine, inkPath, Hand, handWidth, Confetti, splat,
           wrapText, spacedText, layoutCredits, drawBall, drawCloud, drawSun, drawPlane, drawPencil, drawBulb, fade, dust, fontsReady };
})();
