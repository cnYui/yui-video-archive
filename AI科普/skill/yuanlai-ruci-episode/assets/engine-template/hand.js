/* 手写层 —— 白板风格「边说边画」（用户 2026-09-28：「原LAI如此也用手写白板，字提前一秒出现，字幕也同步放大」）。
 * 从《AI每日日报》的 hand.js（2026-09-28，同一天做的样片和上线版）移植过来，笔画算法、排版、计时、记号笔一模一样；
 * 《原LAI如此》这份多了：强调色用系列橙 #FF4F1A（打勾、小横、编号）；缺字记进 ENG.handMissing（check_layout 报出来）；
 * 写字窗太短时自动写快（笔速上限 70、停顿缩短、每笔最短 0.012 s），还是超出 0.3 s 以上的记进 ENG.handSlow；汉字字距
 * 0.96 倍字号（日报是 1.04，第 3 期测试觉得字太散）；圈的外扩按框的大小算；c.hand / handArrow / handRect 登记内容提示点；
 * 所有组件接受 o.parent（c.handGroup() 建的 <g>，整组一起淡出）；每个 <g> 带 data-hand / data-text（check_layout 查
 * 手写字有没有压字幕、角色、目录、出画布）；新增 c.handRect（手画框）、c.handLine（手画线）、c.handMark（圈 / 划一段字）。
 *
 * 数据：window.__HAND__（sync_assets.py 调 hand_glyphs.py 生成的 handdata.js：汉字笔画中线、手画的标点、单线拉丁字体；
 *   深色 / 卡片版的期写 window.__HAND__ = null）。笔画数据在 SERIES/素材/手写（hanzi-writer-data：Arphic Public License；
 *   EMS Tech 单线字体：SIL OFL），是指向 AI日报/素材/手写 的目录联接。
 * 坐标：内容舞台（1920 × 1080）的坐标，和别的组件一样。时间：场景时间（= 声音时间；白板版画面整体提前 ENG.LEAD 秒是
 *   core.js 在 renderAt 里做的，这里不用减）。
 * 组件（c = 场景上下文）：
 *   c.hand({text, x, y, size, align, color, at, until, maxW, seed, pen, vmax, minPause, minStroke, parent})
 *        逐笔写一行字。x = 左边（align 'left'）/ 中线（'center'）/ 右边（'right'），y = 这一行的中线；size = 汉字方格边长（px）。
 *        at..until 是希望写完的时间窗（按笔速拟合，窗太短就写快一点、仍写不完就顺延）；
 *        笔速上限 vmax 个方格 / 秒（默认 34）；窗太紧时笔画间的停顿最多缩到 minPause 倍（默认 0.35）；
 *        每一笔至少 minStroke 秒（默认 0.03 = 一帧）。给了 until、又没自己给 vmax / minPause / minStroke 时，正常笔速写不完
 *        就自动写快（vmax 70、停顿缩到 0.15、每笔最短 0.012 s）；还超出 0.3 s 以上的记进 ENG.handSlow（check_layout 报
 *        hand-slow）。正常笔速约 0.3 秒一个汉字，最快约 0.12 秒。写到场景淡出还没写完的，记进 ENG.handLate 并 console.warn。
 *        cue: false = 不登记内容提示点（默认登记：角色自动层会看过去）。
 *        -> {g, x0, y0, x1, y1, t0, t1, size, box(i0, i1), out(t)}；box = 第 i0..i1-1 个字的墨迹外框
 *   c.handUnderline({x0, x1, y, at, dur, color, w})     波浪下划线（默认黄色记号笔，multiply 混合：压在黑字上不盖字）
 *   c.handEllipse({x0, y0, x1, y1, at, dur, color, w, padX, padY})  笔画一圈把框圈住（从底部顺时针，收尾出头；外扩默认按框高
 *        算，小字不会盖到上下行）
 *   c.handArrow({x0, y0, x1, y1, at, dur, color, w})    先画杆再画箭头
 *   c.handCheck({x, y, size, at, dur, color, w})        打勾（默认橙）
 *   c.handDash({x, y, len, at, dur, color, w})          一小横（要点前的记号，默认橙）
 *   c.handRect({x0, y0, x1, y1, at, dur, color, w, r})  手画的框（一笔绕一圈，四角略圆，收尾略出头；默认墨黑）
 *   c.handLine({x0, y0, x1, y1, at, dur, color, w})     手画的直线（微微弯）
 *   c.handMark(item, i0, i1, {kind: 'circle' | 'underline', at, dur, color}) 圈出 / 划出 c.hand 写的第 i0..i1-1 个字
 *   c.handGroup(parent?) -> <g>；c.handOut(item, t) item 在 t 淡出
 * 上面每个组件都可以加 o.out：到这个时刻淡出（c.hand 的 until 是“写完的时间窗”，不是淡出）。c.handMark 的圈 / 线默认放进
 * 被圈的那行字所在的组，跟着它一起淡出。
 * 每个 item 一条 Track：k 在 [t0, t1] 上从 0 线性到 1，按 k 算出当前时刻，设置每一笔的 stroke-dashoffset
 * （pathLength = 1）。随机数全部来自固定种子（期号 + 场景 + seed），画面只取决于 t，可以任意顺序 seek。
 */
(function () {
  'use strict';
  const HD = window.__HAND__ || null;
  const NS = 'http://www.w3.org/2000/svg';
  const { W, H, E, EP } = ENG;
  const INK = '#1A1A1A', HILITE = '#F5C518', ACCENT = '#FF4F1A';
  ENG.HAND = { INK, HILITE, ACCENT, BLUE: ACCENT, ready: !!HD };
  ENG.handLate = [];                                     // hand items that would still be writing when their scene fades
  ENG.handSlow = [];                                     // hand text that overran its window by > 0.3 s even written fast
  ENG.handMissing = [];                                  // characters without stroke data (left blank)
  // 不用手写的期 handdata.js 里是 window.__HAND__ = null；undefined 才说明漏了文件
  if (window.__HAND__ === undefined) console.warn('hand.js: 没有 handdata.js，手写组件不可用（先跑 sync_assets.py）');

  // ---------------------------------------------------------------- seeded randomness
  function fnv1a(s) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193); } return h >>> 0; }
  function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  const rngFor = key => { const r = mulberry32(fnv1a(`${EP.date || EP.number || ''}|${key}`)); return (a, b) => a + (b - a) * r(); };

  // ---------------------------------------------------------------- geometry
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
  /** centripetal Catmull-Rom through pts -> cubic Bezier segments [p1, c1, c2, p2] */
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
  /** polyline -> smooth path segments; sharp turns stay corners (the pen changes direction there) */
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
  function bez(s, t) {
    const u = 1 - t;
    return [0, 1].map(k => u * u * u * s[0][k] + 3 * u * u * t * s[1][k] + 3 * u * t * t * s[2][k] + t * t * t * s[3][k]);
  }
  function segsLen(segs) {
    let L = 0;
    for (const s of segs) { let prev = s[0]; for (let k = 1; k <= 12; k++) { const p = bez(s, k / 12); L += dist(prev, p); prev = p; } }
    return L;
  }
  const pairs = flat => { const out = []; for (let i = 0; i + 1 < flat.length; i += 2) out.push([flat[i], flat[i + 1]]); return out; };
  /** pen speed profile inside a stroke: linear blended with minimum-jerk (bell-shaped speed) */
  const ease = (u, e) => (1 - e) * u + e * u * u * u * (10 - 15 * u + 6 * u * u);

  // ---------------------------------------------------------------- layout
  const LAT_XH = 0.46, LAT_BASE = 0.36, CJK_ADV = 0.96, SPACE_ADV = 0.3, PEN = 0.07;   // CJK_ADV: 日报 1.04
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
  /** width in px of `text` written at `size` */
  ENG.handWidth = (text, size) => [...String(text)].reduce((a, ch) => a + glyph(ch).adv, 0) * size;

  /** text -> [{i, strokes: [[pt...]], bb}] in screen px, with seeded hand-made irregularity */
  function layoutText(text, x0, midY, size, rnd) {
    const out = [];
    let x = x0;
    const chars = [...String(text)];
    chars.forEach((ch, i) => {
      const gi = glyph(ch), adv = gi.adv * size;
      if (gi.kind === 'miss' && !ENG.handMissing.includes(ch)) { ENG.handMissing.push(ch); console.warn(`hand.js: 没有「${ch}」的笔画数据（留空）`); }
      if (gi.kind === 'cjk' || gi.kind === 'punct') {
        const k = size / 1024 * (1 + rnd(-0.06, 0.06)), r = rnd(-3, 3);
        const cx = x + adv / 2 + rnd(-0.05, 0.05) * size, cy = midY + rnd(-0.04, 0.04) * size;
        const strokes = gi.s.map(flat => {
          let pts = pairs(flat);
          if (gi.kind === 'cjk') {                       // per stroke: a little shifted / turned / long or short, wobbly
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
          if (pts.length === 2) {                          // a ruler-straight line looks mechanical: slight bow
            const [a, b] = pts, m = lerpP(a, b, 0.5), n = dist(a, b) || 1, off = rnd(-0.02, 0.02) * n;
            pts = [a, [m[0] - (b[1] - a[1]) / n * off, m[1] + (b[0] - a[0]) / n * off], b];
          }
          return pts;
        });
        out.push({ i, ch, strokes });
      }
      x += adv;
    });
    for (const g of out) {
      const ps = g.strokes.flat();
      g.bb = ps.length ? [Math.min(...ps.map(p => p[0])), Math.min(...ps.map(p => p[1])), Math.max(...ps.map(p => p[0])), Math.max(...ps.map(p => p[1]))] : null;
    }
    return out;
  }

  // ---------------------------------------------------------------- timing
  /** groups = per character, stroke lengths (px) -> {sched: [[ [t0, t1] per stroke ] per char], end} at a pen speed
   *  fitted to [t0, t1] (clamped to a natural range for this size); pauses shrink when the window is tight */
  function schedule(groups, t0, t1, size, vmax = 34, minPause = 0.35, minStroke = 0.03) {
    const vMin = 9 * size, vMax = vmax * size, MS = minStroke;   // MS: shortest stroke (default one 30 fps frame)
    let ps = 0.02, pc = 0.07;
    const lens = groups.flat(), nS = lens.length, nC = groups.length;
    const pauses = () => Math.max(0, nS - nC) * ps + Math.max(0, nC - 1) * pc;
    const total = v => lens.reduce((a, L) => a + Math.max(MS, L / v), 0);
    let v = 16 * size;
    if (t1 != null && t1 > t0 && nS) {
      const avail = t1 - t0;
      // pen lifts may take at most 40 % of the window; they shrink down to minPause of their normal length
      if (pauses() > avail * 0.4) { const f = Math.max(minPause, avail * 0.4 / pauses()); ps *= f; pc *= f; }
      const need = avail - pauses();
      if (need > nS * MS) {
        let lo = 1, hi = 1e6;
        for (let it = 0; it < 60; it++) { const mid = Math.sqrt(lo * hi); if (total(mid) > need) lo = mid; else hi = mid; }
        v = hi;
      } else v = vMax;
      v = Math.min(vMax, Math.max(vMin, v));
    }
    let t = t0;
    const sched = groups.map((g, gi) => {
      if (gi) t += pc;
      return g.map((L, si) => { if (si) t += ps; const d = Math.max(MS, L / v); const w = [t, t + d]; t += d; return w; });
    });
    return { sched, end: t };
  }

  // ---------------------------------------------------------------- drawing
  function inkLayer(c) {
    if (c._ink) return c._ink;
    const s = document.createElementNS(NS, 'svg');
    s.setAttribute('width', W); s.setAttribute('height', H); s.setAttribute('viewBox', `0 0 ${W} ${H}`);
    s.setAttribute('class', 'inkLayer');
    Object.assign(s.style, { position: 'absolute', left: '0px', top: '0px', overflow: 'visible', pointerEvents: 'none', zIndex: 5 });
    c.root.appendChild(s);
    c._ink = s;
    return s;
  }
  /** strokes = [{segs, t0, t1, col, w, e, blend}] -> one <g> + one Track -> item */
  function addItem(c, strokes, extra, parent, tag) {
    const g = document.createElementNS(NS, 'g');
    (parent || inkLayer(c)).appendChild(g);
    g.setAttribute('data-hand', tag ? tag.kind : 'mark');
    g.setAttribute('data-t1', String(Math.max(...strokes.map(s => s.t1))));   // written by (scene clock; check_layout)
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
    const T0 = Math.min(...strokes.map(s => s.t0)), T1 = Math.max(...strokes.map(s => s.t1));
    const fx = pp => {
      const t = T0 + pp.k * (T1 - T0);
      for (const s of strokes) {
        const u = (t - s.t0) / Math.max(1e-6, s.t1 - s.t0);
        const st = u <= 0 ? -1 : u >= 1 ? 2 : Math.round(ease(u, s.e) * 2000) / 2000;
        if (st === s.st) continue;
        s.st = st;
        const ps = s.el.style;
        if (st < 0) { ps.visibility = 'hidden'; continue; }
        ps.visibility = 'visible';
        ps.strokeDashoffset = st >= 2 ? '0' : String(1 - st);
      }
    };
    c.T(null, { k: 0 }, fx).to(T0, { k: 1 }, Math.max(0.001, T1 - T0), E.lin);
    const item = Object.assign({ g, t0: T0, t1: T1, strokes }, extra || {});
    item.out = t => {
      c.T(g, { o: 1 }).to(t, { o: 0 }, 0.3, E.sine);
      const prev = parseFloat(g.getAttribute('data-out'));
      if (!(prev <= t)) g.setAttribute('data-out', String(t));             // erased at (check_layout)
      return item;
    };
    return item;
  }

  // ---------------------------------------------------------------- marks (ported from the 2026-09-28 sample)
  function wavy(x0, x1, y, rnd) {
    const wl = rnd(150, 175), amp = 5.5, ph = rnd(0, 2 * Math.PI), ph2 = rnd(0, 2 * Math.PI), tilt = rnd(-10, -4);
    const n = Math.max(8, Math.floor((x1 - x0) / 22)), pts = [];
    for (let i = 0; i <= n; i++) {
      const u = i / n, x = x0 + (x1 - x0) * u, a = amp * (1 + 0.3 * Math.sin(Math.PI * 1.7 * u + ph2));
      const wave = 2 * Math.PI * (x - x0) / wl + ph + 0.7 * Math.sin(2 * Math.PI * 0.8 * u + ph2);
      pts.push([x, y + a * Math.sin(wave) + tilt * u]);
    }
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
  /** a box drawn in one go round: start a little right of the top-left corner, clockwise, rounded corners (radius r),
   *  every side slightly bowed, finishing a touch past the start (the pen overshoots) */
  function rectPts(x0, y0, x1, y1, r, rnd) {
    const w = x1 - x0, h = y1 - y0, rr = Math.max(4, Math.min(r, w / 4, h / 4));
    const jig = () => rnd(-2.2, 2.2);
    const side = (a, b, n) => {                        // bowed side a -> b, n inner points
      const len = dist(a, b) || 1, nrm = [-(b[1] - a[1]) / len, (b[0] - a[0]) / len], bow = rnd(-0.006, 0.006) * len;
      const pts = [];
      for (let i = 1; i <= n; i++) { const u = i / (n + 1), o = bow * Math.sin(Math.PI * u); pts.push([a[0] + (b[0] - a[0]) * u + nrm[0] * o, a[1] + (b[1] - a[1]) * u + nrm[1] * o]); }
      return pts;
    };
    const arc = (cx, cy, a0) => [0.35, 0.65].map(u => { const th = (a0 + 90 * u) * Math.PI / 180; return [cx + rr * Math.cos(th), cy + rr * Math.sin(th)]; });
    const p = [];
    const s0 = [x0 + rr + 0.15 * w, y0 + jig()];
    p.push(s0, ...side(s0, [x1 - rr, y0], 3), [x1 - rr, y0 + jig() * 0.5], ...arc(x1 - rr, y0 + rr, -90), [x1 + jig() * 0.5, y0 + rr]);
    p.push(...side([x1, y0 + rr], [x1, y1 - rr], 2), [x1 + jig() * 0.5, y1 - rr], ...arc(x1 - rr, y1 - rr, 0), [x1 - rr, y1 + jig() * 0.5]);
    p.push(...side([x1 - rr, y1], [x0 + rr, y1], 3), [x0 + rr, y1 + jig() * 0.5], ...arc(x0 + rr, y1 - rr, 90), [x0 + jig() * 0.5, y1 - rr]);
    p.push(...side([x0, y1 - rr], [x0, y0 + rr], 2), [x0 + jig() * 0.5, y0 + rr], ...arc(x0 + rr, y0 + rr, 180), [x0 + rr, y0 + jig() * 0.5]);
    p.push([s0[0] + 0.06 * w, s0[1] + rnd(1, 4)]);     // overshoot past the start
    return p;
  }

  // ---------------------------------------------------------------- context components
  /** o.out: the item fades out at that moment */
  const fin = (item, o) => { if (item && o && o.out != null && item.out) item.out(o.out); return item; };
  const baseCtx = ENG.ctx;
  ENG.ctx = S => {
    const c = baseCtx(S);
    /** an SVG group in the ink layer (or inside `parent`): pass it as o.parent to put several hand items together,
     *  then fade them all with one Track on the group (c.T(g, {o: 1}).to(t, {o: 0}, 0.3)) */
    c.handGroup = parent => { const g = document.createElementNS(NS, 'g'); (parent || inkLayer(c)).appendChild(g); return g; };
    c.hand = (o = {}) => {
      const text = String(o.text == null ? '' : o.text);
      let size = o.size || 64;
      if (o.maxW) { const w = ENG.handWidth(text, size); if (w > o.maxW) size = Math.max(24, size * o.maxW / w); }
      const width = ENG.handWidth(text, size);
      const x0 = o.align === 'center' ? o.x - width / 2 : o.align === 'right' ? o.x - width : o.x;
      const rnd = rngFor(`${c.sid}|${o.seed || text}|${o.x}|${o.y}`);
      const laid = layoutText(text, x0, o.y, size, rnd);
      const pen = o.pen || PEN * size;
      const segsOf = laid.map(g => g.strokes.map(pts => smooth(pts)));
      const lens = segsOf.map(ss => ss.map(segsLen));
      let sch = schedule(lens, o.at, o.until, size, o.vmax, o.minPause, o.minStroke);
      const auto = o.until != null && o.vmax == null && o.minPause == null && o.minStroke == null;
      if (auto && sch.end > o.until + 0.05) sch = schedule(lens, o.at, o.until, size, 70, 0.15, 0.012);   // write faster to fit
      if (o.until != null && sch.end > o.until + 0.3 && !o.draft) {
        ENG.handSlow.push({ scene: c.sid, text, at: +(+o.at).toFixed(2), until: +(+o.until).toFixed(2), end: +sch.end.toFixed(2) });
      }
      if (c.S && sch.end > c.S.end - 0.36) {             // still writing when the scene fades out: say so (tests read ENG.handLate)
        ENG.handLate.push({ scene: c.sid, text, end: +sch.end.toFixed(2), sceneEnd: +c.S.end.toFixed(2) });
        console.warn(`hand.js: 「${text}」写到 ${sch.end.toFixed(2)} s，场景 ${c.sid} 在 ${c.S.end.toFixed(2)} s 就淡出了`);
      }
      const strokes = [];
      segsOf.forEach((ss, gi) => ss.forEach((segs, si) => {
        const [t0, t1] = sch.sched[gi][si];
        strokes.push({ segs, t0, t1, col: o.color || INK, w: pen, e: 0.5 });
      }));
      const bbs = laid.map(g => g.bb).filter(Boolean);
      const bbox = bbs.length ? [Math.min(...bbs.map(b => b[0])), Math.min(...bbs.map(b => b[1])), Math.max(...bbs.map(b => b[2])), Math.max(...bbs.map(b => b[3]))] : [x0, o.y - size / 2, x0 + width, o.y + size / 2];
      if (!strokes.length) return { g: null, x0: bbox[0], y0: bbox[1], x1: bbox[2], y1: bbox[3], t0: o.at, t1: o.at, size, box: () => null, out: () => null };
      const item = fin(addItem(c, strokes, { x0: bbox[0] - pen / 2, y0: bbox[1] - pen / 2, x1: bbox[2] + pen / 2, y1: bbox[3] + pen / 2, size },
        o.parent, { kind: 'text', text }), o);
      if (o.cue !== false) c.cue(o.at, 'hand');
      item.box = (i0, i1) => {
        const bs = laid.filter(g => g.i >= i0 && g.i < i1 && g.bb).map(g => g.bb);
        return bs.length ? [Math.min(...bs.map(b => b[0])) - pen / 2, Math.min(...bs.map(b => b[1])) - pen / 2, Math.max(...bs.map(b => b[2])) + pen / 2, Math.max(...bs.map(b => b[3])) + pen / 2] : null;
      };
      return item;
    };
    const mark = (pts, o, corner) => fin(addItem(c, [{ segs: smooth(pts, corner), t0: o.at, t1: o.at + (o.dur || 0.4), col: o.color || HILITE, w: o.w || 9, e: 0.6, blend: (o.color || HILITE) === HILITE }], null, o.parent), o);
    c.handUnderline = (o = {}) => mark(wavy(o.x0, o.x1, o.y, rngFor(`${c.sid}|ul|${o.x0}|${o.y}`)), Object.assign({ dur: 0.4, w: 10 }, o), 179);
    c.handEllipse = (o = {}) => {
      const cx = (o.x0 + o.x1) / 2 + 3, cy = (o.y0 + o.y1) / 2 + 2, bh = Math.max(1, o.y1 - o.y0);
      // padding in proportion to the box (日报: fixed 26 / 18 px, too big around a small value between two lines)
      const px = o.padX != null ? o.padX : Math.min(26, 0.32 * bh + 6), py = o.padY != null ? o.padY : Math.min(18, 0.2 * bh + 4);
      const rx = (o.x1 - o.x0) / 2 * 1.12 + px, ry = bh / 2 * 1.15 + py;
      return mark(loop(cx, cy, rx, ry, rngFor(`${c.sid}|el|${o.x0}|${o.y0}`)), Object.assign({ dur: 0.45, w: 9 }, o), 179);
    };
    c.handArrow = (o = {}) => {
      const [shaft, head] = arrowPts(o.x0, o.y0, o.x1, o.y1, rngFor(`${c.sid}|ar|${o.x0}|${o.y0}`));
      const d = o.dur || 0.3, col = o.color || INK, w = o.w || 7;
      if (o.cue !== false) c.cue(o.at, 'arrow');
      return fin(addItem(c, [{ segs: smooth(shaft, 179), t0: o.at, t1: o.at + d * 0.7, col, w, e: 0.6 },
        { segs: smooth(head, 40), t0: o.at + d * 0.72, t1: o.at + d, col, w, e: 0.6 }], null, o.parent), o);
    };
    c.handCheck = (o = {}) => {
      const s = o.size || 40, r = rngFor(`${c.sid}|ck|${o.x}|${o.y}`);
      const pts = [[o.x - 0.45 * s, o.y + r(-0.05, 0.05) * s], [o.x - 0.1 * s, o.y + 0.38 * s], [o.x + 0.5 * s, o.y - 0.5 * s + r(-0.05, 0.05) * s]];
      return fin(addItem(c, [{ segs: smooth(pts, 40), t0: o.at, t1: o.at + (o.dur || 0.25), col: o.color || ACCENT, w: o.w || 0.14 * s, e: 0.6 }], null, o.parent), o);
    };
    c.handDash = (o = {}) => {
      const r = rngFor(`${c.sid}|ds|${o.x}|${o.y}`), len = o.len || 28;
      const pts = [[o.x, o.y + r(-2, 2)], [o.x + len / 2, o.y + r(-3, 1)], [o.x + len, o.y + r(-2, 2)]];
      return fin(addItem(c, [{ segs: smooth(pts, 179), t0: o.at, t1: o.at + (o.dur || 0.12), col: o.color || ACCENT, w: o.w || 9, e: 0.4 }], null, o.parent), o);
    };
    c.handRect = (o = {}) => {
      const pts = rectPts(o.x0, o.y0, o.x1, o.y1, o.r != null ? o.r : 16, rngFor(`${c.sid}|rc|${o.x0}|${o.y0}`));
      const d = o.dur || Math.min(0.9, 0.3 + ((o.x1 - o.x0) + (o.y1 - o.y0)) / 4000);
      if (o.cue !== false) c.cue(o.at, 'box');
      return fin(Object.assign(addItem(c, [{ segs: smooth(pts, 55), t0: o.at, t1: o.at + d, col: o.color || INK, w: o.w || 6, e: 0.35 }], null, o.parent),
        { x0: o.x0, y0: o.y0, x1: o.x1, y1: o.y1 }), o);
    };
    c.handLine = (o = {}) => {
      const r = rngFor(`${c.sid}|ln|${o.x0}|${o.y0}`), len = Math.hypot(o.x1 - o.x0, o.y1 - o.y0) || 1;
      const nrm = [-(o.y1 - o.y0) / len, (o.x1 - o.x0) / len], bow = r(-0.012, 0.012) * len;
      const pts = [0, 0.33, 0.66, 1].map(u => { const b = bow * Math.sin(Math.PI * u); return [o.x0 + (o.x1 - o.x0) * u + nrm[0] * b, o.y0 + (o.y1 - o.y0) * u + nrm[1] * b]; });
      return fin(addItem(c, [{ segs: smooth(pts, 179), t0: o.at, t1: o.at + (o.dur || Math.min(0.6, 0.12 + len / 3000)), col: o.color || INK, w: o.w || 5, e: 0.4 }], null, o.parent), o);
    };
    c.handMark = (item, i0, i1, o = {}) => {
      const b = item && item.box ? item.box(i0, i1) : null;
      if (!b) return null;
      const at = o.at != null ? o.at : item.t1 + 0.1;
      // the mark lives in the marked item's group (a board.js block): it fades together with that line
      const pg = item.g && item.g.parentNode;
      if (!o.parent && pg && pg.tagName === 'g') o = Object.assign({}, o, { parent: pg });
      return o.kind === 'underline'
        ? c.handUnderline(Object.assign({ x0: b[0] - 4, x1: b[2] + 6, y: b[3] + 12, at, dur: 0.3 }, o, { at }))
        : c.handEllipse(Object.assign({ x0: b[0], y0: b[1], x1: b[2], y1: b[3], at, dur: 0.4 }, o, { at }));
    };
    c.handOut = (item, t) => (item && item.out ? item.out(t) : null);
    return c;
  };
})();
