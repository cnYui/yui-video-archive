/* brand.js — shared pieces for the Claude-brand intro candidates (2026-10-02).
 *
 * Palette: Anthropic brand colours (anthropics/skills brand-guidelines + claude.dev CSS, see ../README.md):
 *   ivory #FAF9F5 (big background) · dark #141413 (ink) · orange #D97757 (the accent "atom") · yellow #F5DB9A
 *   (highlights) · mid gray #B0AEA5 · light gray #E8E6DC · deep orange #C15F3C.
 *
 * The symbol chain ( ">" -> "{ }" -> "</>" -> AI chip ) is ported from the current intro (../../intro/index.html,
 * SVG) to Canvas 2D: same geometry, same corner-preserving morph, same timing. Pages draw in a centred stage whose
 * origin is the frame centre, scaled by the camera (BASE 1.3 with a slow push-in), exactly like the SVG viewBox did.
 * Everything is a pure function of t (render.py seeks to any time).
 */
window.BRAND = (function () {
  'use strict';
  const P = window.PACK, { clamp, lerp, prog, E } = P;
  const C = { ivory: '#FAF9F5', dark: '#141413', orange: '#D97757', orangeDeep: '#C15F3C', yellow: '#F5DB9A', yellowDeep: '#E9C56F', gray: '#B0AEA5', gray2: '#E8E6DC', white: '#FFFFFF' };
  const morphEase = x => E.inOutQuart(x) * 0.7 + E.inOutExpo(x) * 0.3;

  /* ------------------------------------------------------------ geometry (local units, centre origin, y down) */
  function arc(cx, cy, r, a0, a1, n) { const p = []; for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; p.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); } return p; }
  function join(...parts) { const out = []; for (const part of parts) for (const q of part) { const l = out[out.length - 1]; if (!l || Math.hypot(l[0] - q[0], l[1] - q[1]) > 1e-6) out.push(q); } return out; }
  const mirror = pts => pts.map(p => [-p[0], p[1]]);
  function params(pts) { const L = [0]; for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])); const tot = L[L.length - 1] || 1; return { L, tot, u: L.map(v => v / tot) }; }
  function sampleAt(pts, us) {
    const { L, tot } = params(pts), out = []; let j = 1;
    for (const u of us) { const s = tot * u; while (j < pts.length - 1 && L[j] < s) j++; const seg = L[j] - L[j - 1] || 1, k = clamp((s - L[j - 1]) / seg); out.push([lerp(pts[j - 1][0], pts[j][0], k), lerp(pts[j - 1][1], pts[j][1], k)]); }
    return out;
  }
  /** corner-preserving correspondence: both polylines sampled at the union of their vertex parameters + a grid */
  function pair(Pa, Pb, n = 160) {
    const all = [...params(Pa).u, ...params(Pb).u]; for (let i = 0; i <= n; i++) all.push(i / n);
    all.sort((a, b) => a - b); const us = []; for (const u of all) if (!us.length || u - us[us.length - 1] > 1e-5) us.push(u);
    return [sampleAt(Pa, us), sampleAt(Pb, us)];
  }
  const mix = (Pp, Q, e) => Pp.map((p, i) => [lerp(p[0], Q[i][0], e), lerp(p[1], Q[i][1], e)]);
  const mixXY = (Pp, Q, ex, ey) => Pp.map((p, i) => [lerp(p[0], Q[i][0], ex), lerp(p[1], Q[i][1], ey)]);
  const seg = (a, b, e) => a.map((v, i) => lerp(v, b[i], e));

  // ">" chevron, "{ }" braces, "</>" angle brackets, chip halves "[" "]"
  const chevron = [[-50, -56], [6, 0], [-50, 56]];
  function brace(s, a, H) { const d = a * 1.05; return join(arc(s + a, -H + a, a, -Math.PI / 2, -Math.PI, 18), [[s, -d], [s - a, 0], [s, d]], [[s, H - a]], arc(s + a, H - a, a, Math.PI, Math.PI / 2, 18)); }
  const braceL = brace(-150, 38, 165), braceR = mirror(braceL);
  const ltL = [[-128, -116], [-236, 0], [-128, 116]], ltR = mirror(ltL);
  const CH = 138, OV = 14, CHIP_SW = 24;
  const chipL = [[OV, -CH], [-CH, -CH], [-CH, CH], [OV, CH]], chipR = mirror(chipL);
  const M = { m1L: pair(chevron, braceL), m1R: pair(chevron, braceR), m2L: pair(braceL, ltL), m2R: pair(braceR, ltR), m3L: pair(ltL, chipL), m3R: pair(ltR, chipR) };
  // the orange atom: a stroked segment [x0, y0, x1, y1, width]
  const A = { pre: [-22, -50, -22, 50, 46], typed: [52, -50, 52, 50, 46], brace: [0, -50, 0, 50, 46], slash: [50, -150, -50, 150, 26], die: [0, -62, 0, 62, 124], dieH: [-62, 0, 62, 0, 124], sq: [-CHIP_SW / 2, 0, CHIP_SW / 2, 0, CHIP_SW] };
  // chip pins grow out of the body's outer edge
  const PB = CH + CHIP_SW / 2, PL = 42, pinDefs = [];
  for (const p of [-78, 0, 78]) pinDefs.push([-PB, p, -PB - PL, p], [PB, p, PB + PL, p], [p, -PB, p, -PB - PL], [p, PB, p, PB + PL]);

  /* ------------------------------------------------------------ default timeline of the chain (same as the current intro) */
  const T0 = { pop: [-0.02, 0.10], type: 0.22, m1: [0.36, 0.64], m2: [0.70, 0.96], m3: [1.02, 1.30], ai: [1.19, 1.27], pinsIn: 1.25 };

  /**
   * state of the symbol chain at t (up to and including the finished chip):
   *   {P1, P2 (polylines), w (stroke width), op, pop (scale of the ">" pop), atom [x0,y0,x1,y1,w], aiE (label 0..1), pins:[g…]}
   * T may override T0's times (shifted timelines).
   */
  function chain(t, T = T0) {
    const S = { pop: 1, op: 1, w: 22 };
    if (t < T.type) { S.P1 = S.P2 = chevron; S.op = 0; }
    else if (t < T.m1[0]) { S.P1 = S.P2 = chevron; S.pop = lerp(1.18, 1, E.outCubic(prog(t, T.type, T.type + 0.14))); S.op = prog(t, T.type, T.type + 0.03); }
    else if (t < T.m2[0]) { const e = morphEase(prog(t, T.m1[0], T.m1[1])); S.P1 = e >= 1 ? braceL : mix(M.m1L[0], M.m1L[1], e); S.P2 = e >= 1 ? braceR : mix(M.m1R[0], M.m1R[1], e); S.w = lerp(22, 24, e); }
    else if (t < T.m3[0]) { const e = morphEase(prog(t, T.m2[0], T.m2[1])); S.P1 = e <= 0 ? braceL : e >= 1 ? ltL : mix(M.m2L[0], M.m2L[1], e); S.P2 = e <= 0 ? braceR : e >= 1 ? ltR : mix(M.m2R[0], M.m2R[1], e); S.w = lerp(24, 26, e); }
    else { const p = prog(t, T.m3[0], T.m3[1]), e = morphEase(p), ey = morphEase(clamp(p / 0.72)); S.P1 = e <= 0 ? ltL : e >= 1 ? chipL : mixXY(M.m3L[0], M.m3L[1], e, ey); S.P2 = e <= 0 ? ltR : e >= 1 ? chipR : mixXY(M.m3R[0], M.m3R[1], e, ey); S.w = lerp(26, CHIP_SW, e); S.chip = e >= 1; }
    // atom
    if (t < T.type) { const e = E.outBack(prog(t, T.pop[0], T.pop[1])); S.atom = A.pre.slice(); S.atom[1] = -50 * e; S.atom[3] = 50 * e; S.atom[4] = 46 * clamp(0.4 + 0.6 * e, 0, 1.2); }
    else if (t < T.m1[0]) S.atom = seg(A.pre, A.typed, E.outExpo(prog(t, T.type, T.type + 0.07)));
    else if (t < T.m2[0]) S.atom = seg(A.typed, A.brace, morphEase(prog(t, T.m1[0], T.m1[1])));
    else if (t < T.m3[0]) S.atom = seg(A.brace, A.slash, morphEase(prog(t, T.m2[0], T.m2[1])));
    else S.atom = seg(A.slash, A.die, morphEase(prog(t, T.m3[0], T.m3[1])));
    S.aiE = E.outCubic(prog(t, T.ai[0], T.ai[1]));
    S.pins = pinDefs.map((_, i) => E.outCubic(prog(t, T.pinsIn + (i % 4) * 0.012 + Math.floor(i / 4) * 0.022, T.pinsIn + (i % 4) * 0.012 + Math.floor(i / 4) * 0.022 + 0.13)));
    return S;
  }

  /* ------------------------------------------------------------ drawing (in stage units; caller sets the camera transform) */
  function stroke(ctx, pts, w, color, op = 1, tf) {
    if (!pts || op <= 0.001 || w <= 0.3) return;
    ctx.save(); if (tf) tf(ctx); ctx.globalAlpha *= op; ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineJoin = 'miter'; ctx.miterLimit = 4; ctx.lineCap = 'butt';
    ctx.beginPath(); pts.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.stroke(); ctx.restore();
  }
  function atom(ctx, a, color, op = 1) {
    if (!a || op <= 0.001) return; const [x0, y0, x1, y1, w] = a;
    if (w <= 0.3 || Math.hypot(x1 - x0, y1 - y0) < 0.3) return;
    ctx.save(); ctx.globalAlpha *= op; ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineCap = 'butt'; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke(); ctx.restore();
  }
  function pins(ctx, g, color, scale = 1, op = 1) {
    ctx.save(); ctx.globalAlpha *= op; ctx.strokeStyle = color; ctx.lineWidth = 16; ctx.lineCap = 'butt'; ctx.scale(scale, scale);
    pinDefs.forEach(([x0, y0, x1, y1], i) => { const k = g[i]; if (k * PL < 0.75) return; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(lerp(x0, x1, k), lerp(y0, y1, k)); ctx.stroke(); });
    ctx.restore();
  }
  /** the label on the chip core ("AI" / "LLM"), Poppins 700, ivory on the orange die */
  function label(ctx, text, e, op, size = 54) {
    if (e <= 0 || op <= 0.001) return;
    ctx.save(); ctx.globalAlpha *= op; ctx.scale(lerp(0.8, 1, e), lerp(0.8, 1, e)); ctx.fillStyle = C.ivory; ctx.font = `700 ${size}px 'Poppins'`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.letterSpacing = '1px'; ctx.fillText(text, 0, size * 0.06); ctx.restore();
  }
  /** draw the whole chain state (strokes, pins, atom, label) */
  function drawChain(ctx, S, o = {}) {
    const ink = o.ink || C.dark, acc = o.accent || C.orange;
    const tf = S.pop !== 1 ? (c => { c.translate(-22, 0); c.scale(S.pop, S.pop); c.translate(22, 0); }) : null;
    pins(ctx, S.pins, ink, o.pinScale || 1, o.op == null ? 1 : o.op);
    stroke(ctx, S.P1, S.w, ink, S.op * (o.op == null ? 1 : o.op), tf);
    stroke(ctx, S.P2, S.w, ink, S.op * (o.op == null ? 1 : o.op), tf);
    atom(ctx, S.atom, acc, o.atomOp == null ? 1 : o.atomOp);
    if (o.label) label(ctx, o.label, S.aiE * (o.labelOp == null ? 1 : o.labelOp), 1, o.labelSize);
  }
  /** camera: BASE 1.3 with a slow push-in over [0, tEnd] */
  const zoom = (t, tEnd = 3.44) => 1.3 * lerp(0.975, 1.03, E.inOutSine(prog(t, 0, tEnd)));
  /** "AI鼓励师" with AI in Poppins and the rest in Noto Sans SC; returns the width. x = centre */
  function roleText(ctx, text, x, y, size, color, spacing = 6, align = 'center', op = 1) {
    const m = /^([A-Za-z0-9 ]+)(.*)$/.exec(text); const lat = m ? m[1] : '', cjk = m ? m[2] : text;
    ctx.save(); ctx.globalAlpha *= op; ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.letterSpacing = spacing + 'px';
    ctx.font = `600 ${size}px 'Poppins'`; const wl = lat ? ctx.measureText(lat).width : 0;
    ctx.font = `500 ${size}px 'Noto Sans SC'`; const wc = cjk ? ctx.measureText(cjk).width : 0;
    const w = wl + wc - spacing, sx = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
    ctx.fillStyle = color;
    if (lat) { ctx.font = `600 ${size}px 'Poppins'`; ctx.fillText(lat, sx, y + size * 0.04); }
    if (cjk) { ctx.font = `500 ${size}px 'Noto Sans SC'`; ctx.fillText(cjk, sx + wl, y); }
    ctx.restore(); return w;
  }

  return { C, morphEase, arc, join, mirror, pair, mix, mixXY, seg, chevron, braceL, braceR, ltL, ltR, chipL, chipR, CH, OV, CHIP_SW, PB, PL, A, pinDefs, T0, chain, stroke, atom, pins, label, drawChain, zoom, roleText };
})();
