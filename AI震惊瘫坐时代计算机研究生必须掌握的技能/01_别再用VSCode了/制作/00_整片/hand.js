/* 手写层 —— 白板“边说边画”（用户 2026-09-30：“这里的视频我也想使用手写版本的。手写版本会有相比于音频提前一些时间出现”）。
 * 从《原LAI如此》引擎模板的 hand.js（AI科普/skill/yuanlai-ruci-episode/assets/engine-template/hand.js，2026-09-28）移植：
 * 笔画、排版、随机抖动、计时、记号笔（波浪线、圈、箭头、框、勾、小横）的算法原样照搬；改的只是接到本页面的时钟上：
 * 那边靠 core.js 的 Track（c.T），这里每个场景建一个 HAND.ctx(root, sid)，在场景的 update(lv) 里调 H.update(lv)。
 * 数据：window.__HAND__（prep_media.py 调原LAI如此的 hand_glyphs.py 生成的 handdata.js；汉字笔画中线来自 hanzi-writer-data，
 *   Arphic Public License；拉丁字母是 EMS Tech 单线字体，SIL OFL；数据在 D:/大疆/AI科普/素材/手写，只读）。
 * 坐标：整个画布（2340 × 1080）的坐标。parent 只能是铺满画布、位置在 (0, 0) 的层（layer(root) 建的），这样坐标不用换算。
 * 时间：场景里的“画面时间” lv（= 声音时间 + LEAD，engine.js 算好传进来）；组件的 at / until / out 都按声音时间写，
 *   画面自然就早 LEAD 秒（和原LAI如此一样，不用自己减）。
 */
const HAND = (() => {
  'use strict';
  const HD = window.__HAND__ || null;
  const NS = 'http://www.w3.org/2000/svg';
  const INK = '#1A1A1A', HILITE = '#F5C518', ACCENT = '#FF4F1A', RED = '#D8342A';
  const EPKEY = 'cs01';
  const warn = { late: [], slow: [], missing: [] };
  window.__HAND_WARN = warn;
  if (window.__HAND__ === undefined) console.warn('hand.js: 没有 handdata.js（先跑 prep_media.py）');

  // ---------------------------------------------------------------- seeded randomness（同原LAI如此）
  function fnv1a(s) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193); } return h >>> 0; }
  function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  const rngFor = key => { const r = mulberry32(fnv1a(`${EPKEY}|${key}`)); return (a, b) => a + (b - a) * r(); };

  // ---------------------------------------------------------------- geometry（同原LAI如此）
  const dist = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);
  const lerpP = (a, b, u) => [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u];
  function rot(p, deg, c) {
    const r = deg * Math.PI / 180, cx = c ? c[0] : 0, cy = c ? c[1] : 0, x = p[0] - cx, y = p[1] - cy;
    return [cx + x * Math.cos(r) - y * Math.sin(r), cy + x * Math.sin(r) + y * Math.cos(r)];
  }
  function turnDeg(a, b, c) {
    const v1 = [b[0] - a[0], b[1] - a[1]], v2 = [c[0] - b[0], c[1] - b[1]];
    const n1 = Math.hypot(v1[0], v1[1]), n2 = Math.hypot(v2[0], v2[1]);
    if (n1 < 1e-9 || n2 < 1e-9) return 0;
    return Math.acos(Math.max(-1, Math.min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))) * 180 / Math.PI;
  }
  function catmullRom(pts, alpha = 0.5) {
    if (pts.length === 2) return [[pts[0], lerpP(pts[0], pts[1], 1 / 3), lerpP(pts[0], pts[1], 2 / 3), pts[1]]];
    const ext = [lerpP(pts[1], pts[0], 2), ...pts, lerpP(pts[pts.length - 2], pts[pts.length - 1], 2)];
    const segs = [];
    for (let i = 1; i < ext.length - 2; i++) {
      const p0 = ext[i - 1], p1 = ext[i], p2 = ext[i + 1], p3 = ext[i + 2];
      const d01 = Math.max(dist(p0, p1), 1e-6) ** alpha, d12 = Math.max(dist(p1, p2), 1e-6) ** alpha, d23 = Math.max(dist(p2, p3), 1e-6) ** alpha;
      const m1 = [0, 1].map(k => (p2[k] - p1[k]) + d12 * ((p1[k] - p0[k]) / d01 - (p2[k] - p0[k]) / (d01 + d12)));
      const m2 = [0, 1].map(k => (p2[k] - p1[k]) + d12 * ((p3[k] - p2[k]) / d23 - (p3[k] - p1[k]) / (d12 + d23)));
      segs.push([p1, [p1[0] + m1[0] / 3, p1[1] + m1[1] / 3], [p2[0] - m2[0] / 3, p2[1] - m2[1] / 3], p2]);
    }
    return segs;
  }
  function smooth(pts, corner = 62) {
    const runs = []; let cur = [pts[0]];
    for (let i = 1; i < pts.length - 1; i++) {
      cur.push(pts[i]);
      if (turnDeg(pts[i - 1], pts[i], pts[i + 1]) > corner) { runs.push(cur); cur = [pts[i]]; }
    }
    cur.push(pts[pts.length - 1]); runs.push(cur);
    return runs.flatMap(r => catmullRom(r));
  }
  const f1 = v => (Math.round(v * 10) / 10).toString();
  const pathD = segs => 'M' + f1(segs[0][0][0]) + ' ' + f1(segs[0][0][1]) + segs.map(s => ` C${f1(s[1][0])} ${f1(s[1][1])} ${f1(s[2][0])} ${f1(s[2][1])} ${f1(s[3][0])} ${f1(s[3][1])}`).join('');
  function bez(s, t) { const u = 1 - t; return [0, 1].map(k => u * u * u * s[0][k] + 3 * u * u * t * s[1][k] + 3 * u * t * t * s[2][k] + t * t * t * s[3][k]); }
  function segsLen(segs) { let L = 0; for (const s of segs) { let prev = s[0]; for (let k = 1; k <= 12; k++) { const p = bez(s, k / 12); L += dist(prev, p); prev = p; } } return L; }
  const pairs = flat => { const out = []; for (let i = 0; i + 1 < flat.length; i += 2) out.push([flat[i], flat[i + 1]]); return out; };
  const ease = (u, e) => (1 - e) * u + e * u * u * u * (10 - 15 * u + 6 * u * u);

  // ---------------------------------------------------------------- layout（同原LAI如此：汉字字距 0.96）
  const LAT_XH = 0.46, LAT_BASE = 0.36, CJK_ADV = 0.96, SPACE_ADV = 0.3, PEN = 0.07;
  function glyph(ch) {
    if (ch === ' ') return { kind: 'space', adv: SPACE_ADV };
    if (ch === '　') return { kind: 'space', adv: 1 };
    if (!HD) return { kind: 'miss', adv: 0.6 };
    if (HD.punct[ch]) return { kind: 'punct', adv: HD.punct[ch].adv, s: HD.punct[ch].s };
    if (HD.cjk[ch]) return { kind: 'cjk', adv: CJK_ADV, s: HD.cjk[ch] };
    const lg = HD.lat.g[ch];
    if (lg) return { kind: 'lat', adv: lg.a / HD.lat.xh * LAT_XH, g: lg };
    return { kind: 'miss', adv: 0.6 };
  }
  const width = (text, size) => [...String(text)].reduce((a, ch) => a + glyph(ch).adv, 0) * size;
  function layoutText(text, x0, midY, size, rnd) {
    const out = [];
    let x = x0;
    [...String(text)].forEach((ch, i) => {
      const gi = glyph(ch), adv = gi.adv * size;
      if (gi.kind === 'miss' && !warn.missing.includes(ch)) { warn.missing.push(ch); console.warn(`hand.js: 没有「${ch}」的笔画数据（留空）`); }
      if (gi.kind === 'cjk' || gi.kind === 'punct') {
        const k = size / 1024 * (1 + rnd(-0.06, 0.06)), r = rnd(-3, 3);
        const cx = x + adv / 2 + rnd(-0.05, 0.05) * size, cy = midY + rnd(-0.04, 0.04) * size;
        const strokes = gi.s.map(flat => {
          let pts = pairs(flat);
          if (gi.kind === 'cjk') {
            const c = lerpP(pts[0], pts[pts.length - 1], 0.5);
            const sr = rnd(-2.5, 2.5), sx = rnd(-18, 18), sy = rnd(-18, 18), st = rnd(-0.06, 0.06);
            const n = dist(pts[0], pts[pts.length - 1]) || 1;
            const ax = [(pts[pts.length - 1][0] - pts[0][0]) / n, (pts[pts.length - 1][1] - pts[0][1]) / n];
            pts = pts.map((p, j) => {
              const a = 9 * ((j === 0 || j === pts.length - 1) ? 0.5 : 1);
              const along = (p[0] - c[0]) * ax[0] + (p[1] - c[1]) * ax[1];
              const q = rot([p[0] + ax[0] * along * st, p[1] + ax[1] * along * st], sr, c);
              return [q[0] + sx + rnd(-a, a), q[1] + sy + rnd(-a, a)];
            });
          }
          return pts.map(p => rot(p, r)).map(p => [cx + p[0] * k, cy + p[1] * k]);
        });
        out.push({ i, ch, strokes });
      } else if (gi.kind === 'lat') {
        const s = LAT_XH * size / HD.lat.xh, base = midY + LAT_BASE * size;
        const r = rnd(-4, 4), kk = 1 + rnd(-0.05, 0.05), dy = rnd(-0.03, 0.03) * size, dx = rnd(-0.03, 0.03) * size;
        const c = [x + adv / 2 + dx, base - 0.5 * LAT_XH * size + dy];
        const strokes = gi.g.s.map(flat => {
          let pts = pairs(flat).map(([gx, gy]) => [x + gx * s + dx, base + gy * s + dy])
            .map(p => rot([c[0] + (p[0] - c[0]) * kk, c[1] + (p[1] - c[1]) * kk], r, c));
          if (pts.length === 2) { const [a, b] = pts, m = lerpP(a, b, 0.5), n = dist(a, b) || 1, off = rnd(-0.02, 0.02) * n; pts = [a, [m[0] - (b[1] - a[1]) / n * off, m[1] + (b[0] - a[0]) / n * off], b]; }
          return pts;
        });
        out.push({ i, ch, strokes });
      }
      x += adv;
    });
    for (const g of out) { const ps = g.strokes.flat(); g.bb = ps.length ? [Math.min(...ps.map(p => p[0])), Math.min(...ps.map(p => p[1])), Math.max(...ps.map(p => p[0])), Math.max(...ps.map(p => p[1]))] : null; }
    return out;
  }

  // ---------------------------------------------------------------- timing（同原LAI如此）
  function schedule(groups, t0, t1, size, vmax = 34, minPause = 0.35, minStroke = 0.03) {
    const vMin = 9 * size, vMax = vmax * size, MS = minStroke;
    let ps = 0.02, pc = 0.07;
    const lens = groups.flat(), nS = lens.length, nC = groups.length;
    const pauses = () => Math.max(0, nS - nC) * ps + Math.max(0, nC - 1) * pc;
    const total = v => lens.reduce((a, L) => a + Math.max(MS, L / v), 0);
    let v = 16 * size;
    if (t1 != null && t1 > t0 && nS) {
      const avail = t1 - t0;
      if (pauses() > avail * 0.4) { const f = Math.max(minPause, avail * 0.4 / pauses()); ps *= f; pc *= f; }
      const need = avail - pauses();
      if (need > nS * MS) { let lo = 1, hi = 1e6; for (let it = 0; it < 60; it++) { const mid = Math.sqrt(lo * hi); if (total(mid) > need) lo = mid; else hi = mid; } v = hi; }
      else v = vMax;
      v = Math.min(vMax, Math.max(vMin, v));
    }
    let t = t0;
    const sched = groups.map((g, gi) => { if (gi) t += pc; return g.map((L, si) => { if (si) t += ps; const d = Math.max(MS, L / v); const w = [t, t + d]; t += d; return w; }); });
    return { sched, end: t };
  }

  // ---------------------------------------------------------------- marks（同原LAI如此）
  function wavy(x0, x1, y, rnd) {
    const wl = rnd(150, 175), amp = 5.5, ph = rnd(0, 2 * Math.PI), ph2 = rnd(0, 2 * Math.PI), tilt = rnd(-10, -4);
    const n = Math.max(8, Math.floor((x1 - x0) / 22)), pts = [];
    for (let i = 0; i <= n; i++) { const u = i / n, x = x0 + (x1 - x0) * u, a = amp * (1 + 0.3 * Math.sin(Math.PI * 1.7 * u + ph2)); const wave = 2 * Math.PI * (x - x0) / wl + ph + 0.7 * Math.sin(2 * Math.PI * 0.8 * u + ph2); pts.push([x, y + a * Math.sin(wave) + tilt * u]); }
    return pts;
  }
  function loop(cx, cy, rx, ry, rnd) {
    const start = 78, over = 24, sweep = 360 + over, ov = over / sweep, n = 90, pts = [];
    const ph1 = rnd(0, 2 * Math.PI), ph2 = rnd(0, 2 * Math.PI);
    for (let i = 0; i <= n; i++) {
      const u = i / n, th = (start + sweep * u) * Math.PI / 180;
      const wob = 1 + 0.025 * Math.sin(2 * th + ph1) + 0.012 * Math.sin(3 * th + ph2);
      let p = [rx * wob * Math.cos(th), ry * wob * Math.sin(th)];
      const land = u < ov ? -3 * (1 - u / ov) : 0, flare = u > 1 - ov ? 11 * ((u - (1 - ov)) / ov) ** 1.5 : 0;
      const r = Math.hypot(p[0], p[1]) || 1;
      p = [p[0] * (1 + (land + flare) / r), p[1] * (1 + (land + flare) / r)];
      p = rot(p, -3);
      pts.push([cx + p[0], cy + p[1]]);
    }
    return pts;
  }
  function arrowPts(x0, y0, x1, y1, rnd) {
    const len = Math.hypot(x1 - x0, y1 - y0) || 1, d = [(x1 - x0) / len, (y1 - y0) / len], nrm = [-d[1], d[0]];
    const bow = rnd(-0.03, 0.03) * len, shaft = [0, 0.3, 0.65, 1].map(u => { const o = bow * Math.sin(Math.PI * u); return [x0 + d[0] * len * u + nrm[0] * o, y0 + d[1] * len * u + nrm[1] * o]; });
    const tip = shaft[3], back = [shaft[2][0] - tip[0], shaft[2][1] - tip[1]], bl = Math.hypot(back[0], back[1]) || 1;
    const head = Math.min(30, len * 0.35), bb = [back[0] / bl * head, back[1] / bl * head];
    let w1 = rot([tip[0] + bb[0], tip[1] + bb[1]], 27 + rnd(-3, 3), tip), w2 = rot([tip[0] + bb[0] * 0.95, tip[1] + bb[1] * 0.95], -27 + rnd(-3, 3), tip);
    if (w1[1] > w2[1]) [w1, w2] = [w2, w1];
    return [shaft, [w1, tip, w2]];
  }
  function rectPts(x0, y0, x1, y1, r, rnd) {
    const w = x1 - x0, h = y1 - y0, rr = Math.max(4, Math.min(r, w / 4, h / 4));
    const jig = () => rnd(-2.2, 2.2);
    const side = (a, b, n) => { const len = dist(a, b) || 1, nrm = [-(b[1] - a[1]) / len, (b[0] - a[0]) / len], bow = rnd(-0.006, 0.006) * len; const pts = []; for (let i = 1; i <= n; i++) { const u = i / (n + 1), o = bow * Math.sin(Math.PI * u); pts.push([a[0] + (b[0] - a[0]) * u + nrm[0] * o, a[1] + (b[1] - a[1]) * u + nrm[1] * o]); } return pts; };
    const arc = (cx, cy, a0) => [0.35, 0.65].map(u => { const th = (a0 + 90 * u) * Math.PI / 180; return [cx + rr * Math.cos(th), cy + rr * Math.sin(th)]; });
    const p = [];
    const s0 = [x0 + rr + 0.15 * w, y0 + jig()];
    p.push(s0, ...side(s0, [x1 - rr, y0], 3), [x1 - rr, y0 + jig() * 0.5], ...arc(x1 - rr, y0 + rr, -90), [x1 + jig() * 0.5, y0 + rr]);
    p.push(...side([x1, y0 + rr], [x1, y1 - rr], 2), [x1 + jig() * 0.5, y1 - rr], ...arc(x1 - rr, y1 - rr, 0), [x1 - rr, y1 + jig() * 0.5]);
    p.push(...side([x1 - rr, y1], [x0 + rr, y1], 3), [x0 + rr, y1 + jig() * 0.5], ...arc(x0 + rr, y1 - rr, 90), [x0 + jig() * 0.5, y1 - rr]);
    p.push(...side([x0, y1 - rr], [x0, y0 + rr], 2), [x0 + jig() * 0.5, y0 + rr], ...arc(x0 + rr, y0 + rr, 180), [x0 + rr, y0 + jig() * 0.5]);
    p.push([s0[0] + 0.06 * w, s0[1] + rnd(1, 4)]);
    return p;
  }

  // ---------------------------------------------------------------- 一个场景的手写层
  /** html -> {text, marks}：<span class="or">…</span> / <b>…</b> 里的字要划黄线（同原LAI如此 board.js parseHTML） */
  function parseHTML(html) {
    let text = '';
    const marks = [], stack = [], re = /<(\/?)([a-z0-9]+)([^>]*)>|([^<]+)/gi;
    let m;
    const len = () => [...text].length;
    while ((m = re.exec(String(html == null ? '' : html)))) {
      if (m[4] != null) { text += m[4].replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&'); continue; }
      const closing = m[1] === '/', tag = m[2].toLowerCase();
      if (tag === 'br') { text += ' '; continue; }
      if (!closing) stack.push(/class\s*=\s*"[^"]*\bor\b/.test(m[3]) || tag === 'b' ? len() : null);
      else { const st = stack.pop(); if (st != null && len() > st) marks.push([st, len()]); }
    }
    return { text: text.replace(/\s+$/, ''), marks };
  }

  /** t0min：场景出现时（lv = LEAD）之前不开始写：开头就要写的东西往后挪到 t0min，写字时间窗一起挪 */
  function ctx(root, sid, sceneEnd, t0min = (typeof LEAD === 'number' ? LEAD : 0)) {
    const items = [], layers = new Map();
    const clampAt = o => { if (o.at != null && o.at < t0min) { const d = t0min - o.at; o = Object.assign({}, o, { at: o.at + d }); if (o.until != null) o.until += d; } return o; };
    function inkLayer(parent) {
      parent = parent || root;
      if (layers.has(parent)) return layers.get(parent);
      const s = document.createElementNS(NS, 'svg');
      s.setAttribute('width', 2340); s.setAttribute('height', 1080); s.setAttribute('viewBox', '0 0 2340 1080');
      Object.assign(s.style, { position: 'absolute', left: '0px', top: '0px', overflow: 'visible', pointerEvents: 'none', zIndex: 6 });
      parent.appendChild(s); layers.set(parent, s);
      return s;
    }
    function addItem(strokes, extra, parent, tag) {
      const g = document.createElementNS(NS, 'g');
      inkLayer(parent).appendChild(g);
      g.setAttribute('data-hand', tag ? tag.kind : 'mark');
      if (tag && tag.text) g.setAttribute('data-text', tag.text.slice(0, 24));
      for (const s of strokes) {
        const p = document.createElementNS(NS, 'path');
        p.setAttribute('d', pathD(s.segs)); p.setAttribute('pathLength', '1'); p.setAttribute('fill', 'none');
        p.setAttribute('stroke', s.col); p.setAttribute('stroke-width', s.w.toFixed(2));
        p.setAttribute('stroke-linecap', 'round'); p.setAttribute('stroke-linejoin', 'round');
        p.style.strokeDasharray = '1 1'; p.style.strokeDashoffset = '1'; p.style.visibility = 'hidden';
        if (s.blend) p.style.mixBlendMode = 'multiply';
        g.appendChild(p);
        s.el = p; s.st = null;
      }
      const item = Object.assign({ g, t0: Math.min(...strokes.map(s => s.t0)), t1: Math.max(...strokes.map(s => s.t1)), strokes, outAt: null }, extra || {});
      item.out = t => { item.outAt = item.outAt == null ? t : Math.min(item.outAt, t); return item; };
      items.push(item);
      return item;
    }
    const fin = (item, o) => { if (item && o && o.out != null) item.out(o.out); return item; };
    const H = {
      /** 写一行字：x 是左边 / 中线 / 右边（align），y 是这一行的中线，size 是汉字方格边长；at..until 是写字的时间窗（写不完自动写快） */
      text(o = {}) {
        o = clampAt(o);
        const text = String(o.text == null ? '' : o.text);
        let size = o.size || 64;
        if (o.maxW) { const w = width(text, size); if (w > o.maxW) size = Math.max(24, size * o.maxW / w); }
        const wd = width(text, size);
        const x0 = o.align === 'center' ? o.x - wd / 2 : o.align === 'right' ? o.x - wd : o.x;
        const rnd = rngFor(`${sid}|${o.seed || text}|${Math.round(o.x)}|${Math.round(o.y)}`);
        const laid = layoutText(text, x0, o.y, size, rnd);
        const pen = o.pen || PEN * size;
        const segsOf = laid.map(g => g.strokes.map(pts => smooth(pts)));
        const lens = segsOf.map(ss => ss.map(segsLen));
        let sch = schedule(lens, o.at, o.until, size, o.vmax, o.minPause, o.minStroke);
        const auto = o.until != null && o.vmax == null && o.minPause == null && o.minStroke == null;
        if (auto && sch.end > o.until + 0.05) sch = schedule(lens, o.at, o.until, size, 70, 0.15, 0.012);
        if (o.until != null && sch.end > o.until + 0.3) warn.slow.push({ scene: sid, text, at: +o.at.toFixed(2), until: +o.until.toFixed(2), end: +sch.end.toFixed(2) });
        if (sceneEnd != null && sch.end > sceneEnd - 0.3) warn.late.push({ scene: sid, text, end: +sch.end.toFixed(2), sceneEnd: +sceneEnd.toFixed(2) });
        const strokes = [];
        segsOf.forEach((ss, gi) => ss.forEach((segs, si) => { const [t0, t1] = sch.sched[gi][si]; strokes.push({ segs, t0, t1, col: o.color || INK, w: pen, e: 0.5 }); }));
        const bbs = laid.map(g => g.bb).filter(Boolean);
        const bbox = bbs.length ? [Math.min(...bbs.map(b => b[0])), Math.min(...bbs.map(b => b[1])), Math.max(...bbs.map(b => b[2])), Math.max(...bbs.map(b => b[3]))] : [x0, o.y - size / 2, x0 + wd, o.y + size / 2];
        if (!strokes.length) return { g: null, x0: bbox[0], y0: bbox[1], x1: bbox[2], y1: bbox[3], t0: o.at, t1: o.at, size, box: () => null, out: () => null };
        const item = fin(addItem(strokes, { x0: bbox[0] - pen / 2, y0: bbox[1] - pen / 2, x1: bbox[2] + pen / 2, y1: bbox[3] + pen / 2, size, parent: o.parent }, o.parent, { kind: 'text', text }), o);
        item.box = (i0, i1) => {
          const bs = laid.filter(g => g.i >= i0 && g.i < i1 && g.bb).map(g => g.bb);
          return bs.length ? [Math.min(...bs.map(b => b[0])) - pen / 2, Math.min(...bs.map(b => b[1])) - pen / 2, Math.max(...bs.map(b => b[2])) + pen / 2, Math.max(...bs.map(b => b[3])) + pen / 2] : null;
        };
        return item;
      },
      /** 同 text，先去掉 HTML；<span class="or"> / <b> 的字划黄线（o.mark = 'circle' 改成圈） */
      html(html, o = {}) {
        const p = parseHTML(html);
        const it = H.text(Object.assign({}, o, { text: p.text }));
        p.marks.forEach(([a, b]) => H.mark(it, a, b, { kind: o.mark === 'circle' ? 'circle' : 'underline', parent: o.parent, out: o.out }));
        return it;
      },
      width,
      stroke(pts, o, corner, def) {
        o = clampAt(o);
        const col = o.color || def.col;
        return fin(addItem([{ segs: smooth(pts, corner), t0: o.at, t1: o.at + (o.dur || def.dur), col, w: o.w || def.w, e: def.e, blend: col === HILITE }], null, o.parent), o);
      },
      underline(o) { return H.stroke(wavy(o.x0, o.x1, o.y, rngFor(`${sid}|ul|${o.x0}|${o.y}`)), o, 179, { col: HILITE, dur: 0.4, w: 10, e: 0.6 }); },
      ellipse(o) {
        const cx = (o.x0 + o.x1) / 2 + 3, cy = (o.y0 + o.y1) / 2 + 2, bh = Math.max(1, o.y1 - o.y0);
        const px = o.padX != null ? o.padX : Math.min(26, 0.32 * bh + 6), py = o.padY != null ? o.padY : Math.min(18, 0.2 * bh + 4);
        return H.stroke(loop(cx, cy, (o.x1 - o.x0) / 2 * 1.12 + px, bh / 2 * 1.15 + py, rngFor(`${sid}|el|${o.x0}|${o.y0}`)), o, 179, { col: HILITE, dur: 0.45, w: 9, e: 0.6 });
      },
      arrow(o) {
        o = clampAt(o);
        const [shaft, head] = arrowPts(o.x0, o.y0, o.x1, o.y1, rngFor(`${sid}|ar|${o.x0}|${o.y0}`));
        const d = o.dur || 0.3, col = o.color || INK, w = o.w || 7;
        return fin(addItem([{ segs: smooth(shaft, 179), t0: o.at, t1: o.at + d * 0.7, col, w, e: 0.6 }, { segs: smooth(head, 40), t0: o.at + d * 0.72, t1: o.at + d, col, w, e: 0.6 }], null, o.parent), o);
      },
      check(o) { const s = o.size || 40, r = rngFor(`${sid}|ck|${o.x}|${o.y}`); return H.stroke([[o.x - 0.45 * s, o.y + r(-0.05, 0.05) * s], [o.x - 0.1 * s, o.y + 0.38 * s], [o.x + 0.5 * s, o.y - 0.5 * s + r(-0.05, 0.05) * s]], Object.assign({ w: 0.14 * s }, o), 40, { col: ACCENT, dur: 0.25, w: 0.14 * s, e: 0.6 }); },
      cross(o) {
        o = clampAt(o);
        const s = o.size || 40, r = rngFor(`${sid}|x|${o.x}|${o.y}`), col = o.color || RED, w = o.w || 0.14 * s, at = o.at, d = o.dur || 0.3;
        const a = [[o.x - s / 2, o.y - s / 2 + r(-2, 2)], [o.x + s / 2, o.y + s / 2]], b = [[o.x + s / 2 + r(-2, 2), o.y - s / 2], [o.x - s / 2, o.y + s / 2]];
        return fin(addItem([{ segs: smooth([a[0], lerpP(a[0], a[1], 0.5), a[1]], 179), t0: at, t1: at + d * 0.45, col, w, e: 0.5 }, { segs: smooth([b[0], lerpP(b[0], b[1], 0.5), b[1]], 179), t0: at + d * 0.55, t1: at + d, col, w, e: 0.5 }], null, o.parent), o);
      },
      dash(o) { const r = rngFor(`${sid}|ds|${o.x}|${o.y}`), len = o.len || 28; return H.stroke([[o.x, o.y + r(-2, 2)], [o.x + len / 2, o.y + r(-3, 1)], [o.x + len, o.y + r(-2, 2)]], o, 179, { col: ACCENT, dur: 0.12, w: 9, e: 0.4 }); },
      rect(o) {
        const d = o.dur || Math.min(0.9, 0.3 + ((o.x1 - o.x0) + (o.y1 - o.y0)) / 4000);
        return Object.assign(H.stroke(rectPts(o.x0, o.y0, o.x1, o.y1, o.r != null ? o.r : 16, rngFor(`${sid}|rc|${o.x0}|${o.y0}`)), Object.assign({ dur: d }, o), 55, { col: INK, dur: d, w: 6, e: 0.35 }), { x0: o.x0, y0: o.y0, x1: o.x1, y1: o.y1 });
      },
      line(o) {
        const r = rngFor(`${sid}|ln|${o.x0}|${o.y0}`), len = Math.hypot(o.x1 - o.x0, o.y1 - o.y0) || 1;
        const nrm = [-(o.y1 - o.y0) / len, (o.x1 - o.x0) / len], bow = r(-0.012, 0.012) * len;
        const pts = [0, 0.33, 0.66, 1].map(u => { const b = bow * Math.sin(Math.PI * u); return [o.x0 + (o.x1 - o.x0) * u + nrm[0] * b, o.y0 + (o.y1 - o.y0) * u + nrm[1] * b]; });
        return H.stroke(pts, Object.assign({ dur: Math.min(0.6, 0.12 + len / 3000) }, o), 179, { col: INK, dur: 0.4, w: 5, e: 0.4 });
      },
      /** 手画折线 / 曲线（示意图的曲线）：pts 是画布坐标 */
      curve(pts, o) { return H.stroke(pts, o, o.corner || 179, { col: INK, dur: 1.2, w: 7, e: 0.2 }); },
      mark(item, i0, i1, o = {}) {
        const b = item && item.box ? item.box(i0, i1) : null;
        if (!b) return null;
        const at = o.at != null ? o.at : item.t1 + 0.1;
        const oo = Object.assign({}, o, { at, parent: o.parent || item.parent });
        return o.kind === 'circle' ? H.ellipse(Object.assign({ x0: b[0], y0: b[1], x1: b[2], y1: b[3], dur: 0.4 }, oo)) : H.underline(Object.assign({ x0: b[0] - 4, x1: b[2] + 6, y: b[3] + 12, dur: 0.3 }, oo));
      },
      /** 手画框 + 框里手写字（流程图的节点）：w / h 是框的大小，pen 是框线粗细 */
      node(o) {
        const x0 = o.x, y0 = o.y, x1 = o.x + (o.w || 300), y1 = o.y + (o.h || 140), size = o.size || 48;
        const rc = H.rect({ x0, y0, x1, y1, at: o.at, w: o.pen || 6, color: o.color, parent: o.parent, out: o.out });
        const ty = o.sub ? (y0 + y1) / 2 - size * 0.3 : (y0 + y1) / 2;
        const tx = H.html(o.text, { x: (x0 + x1) / 2, y: ty, size, align: 'center', maxW: (x1 - x0) - 40, at: rc.t1 + 0.05, until: o.write || rc.t1 + 1.0, color: o.textColor, parent: o.parent, out: o.out });
        return { rect: rc, text: tx, x0, y0, x1, y1, t1: tx.t1 };
      },
      update(lv) {
        for (const it of items) {
          for (const s of it.strokes) {
            const u = (lv - s.t0) / Math.max(1e-6, s.t1 - s.t0);
            const st = u <= 0 ? -1 : u >= 1 ? 2 : Math.round(ease(u, s.e) * 2000) / 2000;
            if (st === s.st) continue;
            s.st = st;
            const ps = s.el.style;
            if (st < 0) { ps.visibility = 'hidden'; continue; }
            ps.visibility = 'visible';
            ps.strokeDashoffset = st >= 2 ? '0' : String(1 - st);
          }
          if (it.outAt != null) it.g.style.opacity = 1 - Math.min(1, Math.max(0, (lv - it.outAt) / 0.3));
        }
      },
      INK, HILITE, ACCENT, RED,
    };
    return H;
  }
  return { ctx, width, warn, INK, HILITE, ACCENT, RED, ready: !!HD };
})();
