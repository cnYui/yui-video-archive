/* 《原LAI如此》第 2 期「从学会说人话到AGI」— scenes.js（本期画面）
 *
 * 依据：台本/script_data.py 每一行的第 4 个字段（画面说明）。组件见 components.js，写法参考 scenes.example.js（第 1 期）。
 * 时间：一律按段号 / 台词短语取（P('S03-14', '1750亿')、c.seg / c.segs / c.P / c.endTalk / ENG.endTalk），不写死秒数。
 *
 * 全片复用、不随场景淡出的两件东西（挂在 #scenes 层、轨道放 ENG.global；在 S03 的 builder 里一次建好、排好全片时刻）：
 *   · 「四个阶段」小色带图：顶部章节标题右侧（x 780–1500、y 20–162，和右上目录同高），S03-10 起到 S06-47。
 *     S03 开头、S03-20、S06-47 用同款大图（场景内容），大图出现时小图让位；每章亮对应的一条。
 *   · 「训练目标」小清单：右下角（x 1600–1880、y 850–986），S03-16 起到片尾；①②③ 随章节逐条出现，
 *     S04-29 / S05-38 由居中的「训练目标 +1」卡片飞进去。
 * 版面：内容 x 470–1840、y ≥ 186（顶部是标题、小色带图、目录）、y ≤ 900；左下角色 x < 380；字幕 y ≥ 922；
 *   右下角 x ≥ 1600、y ≥ 846 留给训练目标清单。品牌只写文字不画 logo；图表 / 界面 / 流程图都标「示意」。
 */
(function () {
  'use strict';
  const { E, esc } = ENG;
  const ICON = ENG.ICON;
  if (!ENG.SCENES.length) return;

  // ================================================================== 本期样式（模板 style.css 不改，在这里补）
  const CSS = `
  .hudp { position: absolute; background: rgba(20,20,20,.74); border-top: 2px solid var(--orange); box-shadow: 0 8px 22px rgba(0,0,0,.28); }
  .hudp .hk { position: absolute; left: 16px; top: 9px; font: 500 13px var(--mono); letter-spacing: .22em; color: var(--grey2); white-space: nowrap; }
  .hudp .hk b { font: 500 15px var(--cjk); letter-spacing: .12em; color: rgba(237,234,227,.72); margin-right: 10px; }
  .bc-lbl { position: absolute; white-space: nowrap; font-family: var(--cjk); font-weight: 800; color: rgba(237,234,227,.42); }
  .bc-yr { position: absolute; white-space: nowrap; font-family: var(--mono); font-weight: 500; color: rgba(237,234,227,.5); text-align: center; }
  .bc-in { position: absolute; white-space: nowrap; font-family: var(--cjk); font-weight: 800; color: var(--ink); }
  .goalRow { position: absolute; height: 30px; padding-left: 40px; font: 500 19px var(--cjk); line-height: 30px; color: rgba(237,234,227,.92); white-space: nowrap; transform-origin: 0 50%; }
  .goalRow .gbar { position: absolute; left: 0; top: 3px; width: 4px; height: 24px; background: var(--orange); opacity: 0; }
  .goalRow .gnum { position: absolute; left: 10px; top: 4px; width: 22px; height: 22px; border-radius: 50%; text-align: center; font: 700 14px var(--mono); line-height: 22px; }
  .goalRow .gtx, .goalRow .gq { position: absolute; left: 40px; top: 0; }
  .goalRow .gq { color: rgba(237,234,227,.5); font-weight: 700; }
  .dd { position: absolute; font: 700 22px var(--mono); color: var(--orange); letter-spacing: .04em; white-space: nowrap; }
  .tagp { position: absolute; white-space: nowrap; font: 700 17px var(--cjk); line-height: 26px; padding: 0 10px; border-radius: 5px; border: 2px solid var(--orange); color: var(--orange); background: #FFF6F0; }
  .bub { position: absolute; background: var(--paper); color: var(--ink); white-space: nowrap; box-shadow: 0 12px 30px rgba(0,0,0,.34); }
  .bub.me { background: var(--orange); color: var(--paper); }
  .bub .bt { position: absolute; background: inherit; transform: rotate(45deg); }
  .bub .btx { position: relative; }
  .callout { position: absolute; white-space: nowrap; background: rgba(20,20,20,.88); color: var(--paper); border-left: 4px solid var(--orange); border-radius: 4px; padding: 6px 14px; font: 700 21px var(--cjk); line-height: 30px; box-shadow: 0 8px 20px rgba(0,0,0,.35); }
  .callout .s { font-weight: 500; font-size: 18px; color: rgba(237,234,227,.8); }
  .inbox { position: absolute; background: #E4DFD5; border-radius: 10px; }
  `;
  const styleEl = document.createElement('style');
  styleEl.textContent = CSS;
  document.head.appendChild(styleEl);

  // ================================================================== 时间工具（按段号 / 台词短语）
  const SG = id => ENG.segId(id);
  /** 段 id 里说到 phrase 的时刻；找不到时用段内 frac 处，并在控制台 warn */
  function P(id, phrase, frac = 0) {
    const sg = SG(id), t = ENG.phraseTime(sg, phrase);
    if (t == null) console.warn(`scenes.js: phrase "${phrase}" not found in ${id} (fallback ${frac})`);
    return t != null ? t : sg.start + (sg.end - sg.start) * frac;
  }
  /** 「训练目标 +1」卡片飞进右下清单：说到这一条后 1 s 起飞（最早在段尾前 0.9 s），0.7 s 到达 */
  function goalFly(id, phrase) {
    const sg = SG(id), t = Math.max(P(id, phrase, 0.6) + 1.0, sg.end - 0.9);
    return { t, arrive: t + 0.7 };
  }

  // ================================================================== 小工具
  const rgba = (hex, a) => { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; };
  /** 一行文字：tx(c, parent, x, y, html, font, {w, color, align, lh, ls, wrap}) */
  function tx(c, parent, x, y, html, font, o = {}) {
    const e = c.div('', x, y, o.w != null ? o.w : null, null, html, parent || undefined);
    e.style.font = font;
    e.style.whiteSpace = o.wrap ? 'normal' : 'nowrap';
    if (o.lh) e.style.lineHeight = o.lh + 'px';
    if (o.color) e.style.color = o.color;
    if (o.align) e.style.textAlign = o.align;
    if (o.ls) e.style.letterSpacing = o.ls;
    return e;
  }
  /** 橙色圆形编号 */
  function badge(c, parent, x, y, n, d = 40, fs = 22, col = 'var(--orange)') {
    const b = c.div('', x, y, d, d, String(n), parent);
    Object.assign(b.style, { borderRadius: '50%', background: col, color: 'var(--paper)', font: `800 ${fs}px var(--mono)`, textAlign: 'center', lineHeight: d + 'px' });
    return b;
  }
  /** 纸白卡片 + 可选 kicker / 右上「示意」 */
  function paper(c, x, y, w, h, o = {}) {
    const cd = c.card(x, y, w, h, o.parent);
    if (o.kicker) c.div('kicker', o.kx || 36, 22, w - 140, null, o.kicker, cd);
    if (o.shiyi) c.div('shiyi', w - 78, 16, null, null, typeof o.shiyi === 'string' ? o.shiyi : '示意', cd);
    return cd;
  }
  /** 橙框小标签（卡片右上等） */
  function tagp(c, parent, html, x, y, o = {}) {
    const e = c.div('tagp', x, y, null, null, html, parent);
    if (o.right != null) { e.style.left = ''; e.style.right = o.right + 'px'; }
    if (o.size) e.style.fontSize = o.size + 'px';
    return e;
  }
  /** 时间点卡片：橙色日期、粗体标题、可选 1–2 行小字、右上小标签。o: {x, y, w, date, title, sub, tag, size, at, until} */
  function dateCard(c, o) {
    const w = o.w || 440, ts = o.size || 36, lh = Math.round(ts * 1.3), subs = o.sub == null ? [] : [].concat(o.sub);
    const h = 54 + lh + subs.length * 30 + 20;
    const cd = c.card(o.x, o.y, w, h, o.parent);
    c.div('dd', 26, 18, null, null, esc(o.date), cd);
    tx(c, cd, 26, 50, o.title, `900 ${ts}px var(--cjk)`, { lh });
    subs.forEach((sb, i) => tx(c, cd, 26, 52 + lh + i * 30, sb, '500 20px var(--cjk)', { color: '#5A564F', lh: 28 }));
    if (o.tag) tagp(c, cd, o.tag, null, 16, { right: 20 });
    const tr = c.show(cd, o.at, o.until, 12);
    c.cue(o.at, 'card');
    return { el: cd, tr, w, h };
  }
  /** 聊天气泡（示意：虚构对话，无头像、无 logo）。o: {x, y, text, size, me (橙色回复), at, until, parent} */
  function bubble(c, o) {
    const fs = o.size || 40, h = Math.round(fs * 1.8), pad = Math.round(fs * 0.72), ts = Math.round(fs * 0.62);
    const b = c.div('bub' + (o.me ? ' me' : ''), o.x, o.y, null, h, '', o.parent);
    Object.assign(b.style, { font: `800 ${fs}px var(--cjk)`, lineHeight: h + 'px', padding: `0 ${pad}px`, borderRadius: Math.round(h / 2) + 'px' });
    const tl = c.div('bt', o.me ? null : Math.round(h * 0.5), h - Math.round(ts * 0.62), ts, ts, '', b);
    if (o.me) tl.style.right = Math.round(h * 0.5) + 'px';
    ENG.el('span', 'btx', b, o.text);
    const tr = o.at != null ? c.show(b, o.at, o.until, 10) : null;
    if (o.at != null) c.cue(o.at, 'bubble');
    return { el: b, tr, w: b.offsetWidth, h };
  }
  /** 一排「A → B → C」小卡（示意）。o: {x, y, items, at, step, until, fs, h, hot: [橙色的序号]} */
  function chain(c, o) {
    const fs = o.fs || 28, h = o.h || 60, aw = 50, step = o.step != null ? o.step : 0.2;
    let x = o.x;
    const els = [], trs = [];
    o.items.forEach((it, i) => {
      if (i) {
        const a = c.arrow(x + 8, o.y + h / 2, x + aw - 8, o.y + h / 2, 'rgba(237,234,227,.8)', { w: 3.5, head: 11 });
        const ta = c.T(a, { o: 0 }).to(o.at + step * i - 0.1, { o: 1 }, 0.25);
        if (o.until != null) ta.out(o.until);
        trs.push(ta);
        x += aw;
      }
      const e = c.div('chip' + ((o.hot || []).includes(i) ? ' o' : ''), x, o.y, null, h, it);
      Object.assign(e.style, { fontSize: fs + 'px', padding: '0 20px' });
      trs.push(c.show(e, o.at + step * i, o.until, 6));
      els.push(e);
      x += e.offsetWidth;
    });
    c.cue(o.at, 'chain');
    return { els, trs, w: x - o.x };
  }
  /** 斜线填充的虚线框（色带图里「交叠」的时间窗） */
  function hatch(c, x, y, w, h) {
    const e = c.div('', x, y, w, h, '');
    Object.assign(e.style, { background: 'repeating-linear-gradient(135deg, rgba(237,234,227,.62) 0 3px, rgba(237,234,227,0) 3px 11px)', border: '2px dashed rgba(237,234,227,.9)', borderRadius: '8px' });
    return e;
  }

  // ================================================================== 「四个阶段」色带图（小 / 大 / 放大 / 缩小版共用一个画法）
  const Y0 = 2017, Y1 = 2027;   // 横轴：2017 年初 … 2026 年底
  const STAGES = [
    { name: '接龙', col: '#F2A0BD', start: 2018.45 },                 // 预训练：GPT-1 2018-06
    { name: '对话', col: '#F6C945', start: 2022.08 },                 // SFT + RLHF：InstructGPT 2022-01
    { name: '思考', col: '#4A6FD0', start: 2024.70, pre: 2022.08 },   // o1 2024-09；浅色段 = 思维链提示 2022-01 起（只是提问技巧）
    { name: '做事', col: '#E2463F', start: 2023.45 },                 // 函数调用 2023-06
  ];
  // g: {x, y, w, h, lx (label x), lw (label column), pad, top (first band y), pitch, bh (band height), lf (label px),
  //     yf (year px; 0 = no years), yearY, kicker (html), kf (kicker px), ky}
  const DOCK = { x: 780, y: 20, w: 720, h: 142, lx: 16, lw: 78, pad: 16, top: 36, pitch: 22, bh: 15, lf: 15, yf: 12, yearY: 121, kicker: '<b>四个阶段</b>STAGES · 示意' };
  const BIG = { x: 590, y: 262, w: 1120, h: 362, lx: 32, lw: 150, pad: 30, top: 74, pitch: 62, bh: 38, lf: 34, yf: 20, yearY: 324, kicker: '<b>AI 变强的四个阶段</b>STAGES · 示意', kf: 17, ky: 22 };
  const ZOOM = { x: 480, y: 290, w: 1360, h: 424, lx: 32, lw: 170, pad: 30, top: 64, pitch: 74, bh: 40, lf: 34, yf: 20, yearY: 392, kicker: '<b>四个阶段</b>STAGES · 示意', kf: 17, ky: 20 };
  const MINI9 = { x: 1580, y: 426, w: 270, h: 130, lx: 12, lw: 54, pad: 12, top: 36, pitch: 23, bh: 13, lf: 14, yf: 0, kicker: '<b>四个阶段</b>', kf: 12, ky: 10 };

  function bandChart(parent, g) {
    const root = ENG.box('div', 'hudp', parent, g.x, g.y, g.w, g.h);
    root.style.transformOrigin = '0 0';
    const x0 = g.lw, x1 = g.w - g.pad;
    const yx = yr => x0 + (yr - Y0) / (Y1 - Y0) * (x1 - x0);
    const ry = i => g.top + i * g.pitch;
    if (g.kicker) {
      const k = ENG.el('div', 'hk', root, g.kicker);
      if (g.kf) {
        Object.assign(k.style, { fontSize: g.kf + 'px', left: g.lx + 'px', top: (g.ky || 9) + 'px' });
        const b = k.querySelector('b'); if (b) b.style.fontSize = Math.round(g.kf * 1.25) + 'px';
      }
    }
    let grid = '';
    for (let yr = Y0; yr <= Y1; yr++) grid += `<line x1="${yx(yr).toFixed(1)}" y1="${g.top - 6}" x2="${yx(yr).toFixed(1)}" y2="${ry(3) + g.bh + 6}" stroke="rgba(237,234,227,.10)" stroke-width="1"/>`;
    ENG.svg(root, 0, 0, g.w, g.h, grid);
    if (g.yf) for (let yr = Y0; yr < Y1; yr++) {
      const e = ENG.box('div', 'bc-yr', root, yx(yr), g.yearY, yx(yr + 1) - yx(yr), null);
      e.textContent = String(yr);
      Object.assign(e.style, { fontSize: g.yf + 'px', lineHeight: Math.round(g.yf * 1.25) + 'px' });
    }
    const r = g.bh / 2;
    const bands = STAGES.map((s, i) => {
      const y = ry(i), xs = yx(s.pre || s.start), xm = yx(s.start);
      const under = ENG.box('div', '', root, xs, y, x1 - xs, g.bh);
      Object.assign(under.style, { background: 'rgba(237,234,227,.13)', borderRadius: r + 'px' });
      let pre = null;
      if (s.pre) {
        pre = ENG.box('div', '', root, xs, y, xm - xs, g.bh);
        Object.assign(pre.style, { background: s.col, borderRadius: `${r}px 0 0 ${r}px`, opacity: 0 });
      }
      const fill = ENG.box('div', '', root, xm, y, x1 - xm, g.bh);
      Object.assign(fill.style, { background: s.col, borderRadius: s.pre ? `0 ${r}px ${r}px 0` : r + 'px', opacity: 0 });
      const ring = ENG.box('div', '', root, xs - 4, y - 4, x1 - xs + 8, g.bh + 8);
      Object.assign(ring.style, { border: `${g.bh > 20 ? 3 : 2}px solid rgba(237,234,227,.95)`, borderRadius: (r + 4) + 'px', opacity: 0 });
      const lbl = ENG.box('div', 'bc-lbl', root, g.lx, y + g.bh / 2 - Math.round(g.lf * 0.72), null, null);
      lbl.textContent = s.name;
      Object.assign(lbl.style, { fontSize: g.lf + 'px', lineHeight: Math.round(g.lf * 1.44) + 'px' });
      return { i, s, y, xs, xm, under, pre, fill, ring, lbl };
    });
    return { el: root, g, yx, ry, x0, x1, bands, sx: yr => g.x + yx(yr), sy: i => g.y + ry(i) };
  }
  /** 每条色带一条轨道：on（0 灰、0.5 已走过、1 亮）、hi（白框 = 当前阶段）。mk(el, init, fx) 造轨道（场景内 c.T / 全局 ENG.T） */
  function bandTracks(ch, mk) {
    return ch.bands.map(b => mk(null, { on: 0, hi: 0 }, (p, tk) => {
      const on = Math.round(p.on * 100) / 100, hi = Math.round(p.hi * 100) / 100;
      if (tk._on !== on) {
        b.fill.style.opacity = on;
        if (b.pre) b.pre.style.opacity = (on * 0.42).toFixed(3);
        b.lbl.style.color = `rgba(237,234,227,${(0.42 + 0.56 * Math.min(1, on / 0.5)).toFixed(3)})`;
        tk._on = on;
      }
      if (tk._hi !== hi) { b.ring.style.opacity = hi; tk._hi = hi; }
    }));
  }
  const setBands = (trs, t, on, hi, d = 0.35) => trs.forEach((tr, i) => tr.to(t, { on: on[i], hi: hi ? hi[i] : 0 }, d));
  const poseOf = (from, to) => ({ x: to.x - from.x, y: to.y - from.y, s: to.w / from.w });   // transform that puts chart `from` onto `to`

  // ================================================================== 「训练目标」小清单（右下角）
  const GOALS = ['预测下一个词', '人更喜欢哪个回答', '答案对不对'];
  const GL = { x: 1600, y: 850, w: 280, rowY: 34, rowH: 32 };
  const GLH = GL.rowY + GOALS.length * GL.rowH + 6;
  const goalRow = n => ({ x: GL.x + 10, y: GL.y + GL.rowY + (n - 1) * GL.rowH, w: GL.w - 20, h: 30 });

  /** 全片常驻的两件东西（在 S03 的 builder 里调用一次）：小色带图 + 训练目标清单，时刻按全片的段号 / 短语排好 */
  function buildGlobals() {
    const layer = document.getElementById('scenes');
    const G = (e, init, fx) => ENG.T(ENG.global, e, init, fx);
    // ---- 小色带图：S03-10 出现；S03-20 大图回来时让位；S06-47 放大时让位（之后不再出现）
    const dock = bandChart(layer, DOCK);
    const tDock = SG('S03-10').start, tBack = SG('S03-20').start, tBackEnd = ENG.endTalk('S03'), tZoom = SG('S06-47').start;
    G(dock.el, { o: 0 }).to(tDock + 0.2, { o: 1 }, 0.45).to(tBack, { o: 0 }, 0.3).to(tBackEnd + 0.3, { o: 1 }, 0.4).to(tZoom, { o: 0 }, 0.35);
    const dt = bandTracks(dock, G);
    setBands(dt, tDock - 0.3, [1, 0, 0, 0], [1, 0, 0, 0], 0);                                // 第 1 阶段
    setBands(dt, P('S04-21', '第二阶段', 0.4), [0.5, 1, 0, 0], [0, 1, 0, 0]);                 // 第 2 阶段（说到“第二阶段”）
    setBands(dt, ENG.endTalk('S04'), [0.5, 0.5, 1, 0], [0, 0, 1, 0]);                        // S04 末停顿：第 3 条亮起
    setBands(dt, ENG.endTalk('S05'), [0.5, 0.5, 0.5, 1], [0, 0, 0, 1]);                      // S05 末停顿：第 4 条亮起
    ENG.dock = dock;

    // ---- 训练目标清单
    const gl = ENG.box('div', 'hudp', layer, GL.x, GL.y, GL.w, GLH);
    ENG.el('div', 'hk', gl, '<b>训练目标</b>GOALS');
    const rows = GOALS.map((txt, i) => {
      const r = ENG.box('div', 'goalRow', gl, 10, GL.rowY + i * GL.rowH, GL.w - 20, 30);
      const bar = ENG.el('div', 'gbar', r), num = ENG.el('div', 'gnum', r, String(i + 1));
      const tt = ENG.el('span', 'gtx', r, esc(txt)), q = ENG.el('span', 'gq', r, '？');
      const tr = G(null, { v: 0, on: 0, hl: 0 }, (p, tk) => {
        const v = Math.round(p.v * 100) / 100, on = Math.round(p.on * 100) / 100, hl = Math.round(p.hl * 100) / 100;
        const key = `${v}|${on}|${hl}`;
        if (tk._k === key) return;
        tk._k = key;
        r.style.opacity = v;
        r.style.visibility = v <= 0.001 ? 'hidden' : '';
        tt.style.opacity = on; q.style.opacity = (1 - on).toFixed(2);
        num.style.background = on > 0.5 ? 'var(--orange)' : 'rgba(237,234,227,.3)';
        num.style.color = on > 0.5 ? 'var(--paper)' : 'var(--ink)';
        bar.style.opacity = hl;
        r.style.transform = hl ? `scale(${(1 + 0.05 * hl).toFixed(3)})` : '';
        tt.style.color = hl > 0.5 ? '#FFB08F' : '';
      });
      return { r, tr };
    });
    const tG1 = P('S03-16', '预测下一个词', 0.5);
    G(gl, { o: 0, y: 10 }).to(tG1 - 0.3, { o: 1, y: 0 }, 0.4);
    rows[0].tr.to(tG1, { v: 1, on: 1, hl: 1 }, 0.3).to(tG1 + 2.6, { hl: 0 }, 0.4);
    const tQ = P('S03-20', '多了两条', 0.6);                       // 下方出现两个空行「② ？」「③ ？」
    rows[1].tr.to(tQ, { v: 1 }, 0.3);
    rows[2].tr.to(tQ + 0.2, { v: 1 }, 0.3);
    const f2 = goalFly('S04-29', '人更喜欢哪个回答'), f3 = goalFly('S05-38', '答案对不对');
    rows[1].tr.to(f2.arrive - 0.12, { on: 1, hl: 1 }, 0.3).to(f2.arrive + 2.4, { hl: 0 }, 0.4);
    rows[2].tr.to(f3.arrive - 0.12, { on: 1, hl: 1 }, 0.3).to(f3.arrive + 2.4, { hl: 0 }, 0.4);
    // S06-48：“文字接龙”说的只是预训练的目标 → ① 单独亮一下，整张清单框一下
    const tW = P('S06-48', '只是预训练的目标', 0.5);
    rows[0].tr.to(tW, { hl: 1 }, 0.3).to(tW + 2.4, { hl: 0 }, 0.4);
    const ring = ENG.box('div', 'ring', layer, GL.x - 7, GL.y - 7, GL.w + 14, GLH + 14);
    G(ring, { o: 0 }).to(tW, { o: 1 }, 0.25).to(tW + 2.4, { o: 0 }, 0.3);
  }

  /** 「训练目标 +1」：居中卡片出现 → 说到这一条时下面划橙线 → 飞进右下清单第 n 行。o: {n, text, lead, at, hl, fly} */
  function goalCard(c, o) {
    const w = 900, h = 250, x = 1150 - w / 2, y = 320;
    const cd = c.card(x, y, w, h);
    cd.style.transformOrigin = '0 0';
    c.div('kicker', 44, 24, 600, null, 'TRAINING GOAL · 训练目标 +1', cd);
    tx(c, cd, 44, 54, o.lead, '700 30px var(--cjk)', { color: '#4A4741' });
    const main = c.div('', 44, 118, w - 88, 96, '', cd);
    badge(c, main, 0, 14, o.n, 68, 36);
    const mt = tx(c, main, 92, 0, o.text, '900 66px var(--cjk)', { lh: 92 });
    const ul = c.div('', 92, 88, mt.offsetWidth, 7, '', main);
    Object.assign(ul.style, { background: 'var(--orange)', transformOrigin: '0 50%', borderRadius: '3px' });
    c.T(null, { g: 0 }, p => { ul.style.transform = `scaleX(${p.g.toFixed(3)})`; }).to(o.hl, { g: 1 }, 0.45);
    // 飞到清单第 n 行：卡片里的正文（main 内 x 92, y 0, 66px）落在那一行的文字上（19px）
    const row = goalRow(o.n), sc = 19 / 66;
    const dx = row.x + 40 - x - sc * (44 + 92), dy = row.y + (30 - 92 * sc) / 2 - y - sc * 118;
    c.T(cd, { o: 0, y: 14 }).in(o.at, 0.4).to(o.fly, { x: dx, s: sc }, 0.5, E.inOut).to(o.fly, { y: dy }, 0.7, E.inOut).to(o.fly + 0.42, { o: 0 }, 0.3, E.sine);
    c.cue(o.at, 'card');
    return cd;
  }

  // ================================================================== S01 开场白
  ENG.scene('S01', c => {
    const s0 = c.seg(0), g = c.gap(s0);
    const tA = c.P(s0, '今天', 0.3) - 0.1, tSub = c.P(s0, 'AGI', 0.8) - 0.15, tOut = g ? g.start : s0.end;
    const cx = 1150, cy = 470;
    const scrim = c.div('', cx - 660, cy - 260, 1320, 540, '');
    scrim.style.background = 'radial-gradient(closest-side, rgba(14,16,28,.6), rgba(14,16,28,.34) 55%, rgba(14,16,28,0))';
    c.show(scrim, tA - 0.1, tOut, 0, 0.5);
    const box = c.div('', cx - 700, cy - 205, 1400, 410, '');
    const k = tx(c, box, 0, 0, `原LAI如此 · #${ENG.pad2(ENG.EP.number)}`, '600 24px var(--mono)', { w: 1400, align: 'center', color: 'var(--orange)', ls: '.34em' });
    tx(c, box, 0, 46, 'AI：从学会说人话，', '900 96px var(--cjk)', { w: 1400, align: 'center', color: 'var(--paper)', lh: 124, ls: '.02em' });
    const l2 = tx(c, box, 0, 172, '到 AGI<span class="or">？</span>', '900 126px var(--cjk)', { w: 1400, align: 'center', color: 'var(--paper)', lh: 150, ls: '.02em' });
    const rule = c.div('bigRule', 640, 340, 120, 3, '', box);
    const sub = tx(c, box, 0, 358, 'AGI：通用人工智能', '700 34px var(--cjk)', { w: 1400, align: 'center', color: 'rgba(237,234,227,.88)' });
    c.T(box, { o: 0, y: 16 }).in(tA, 0.45).to(tOut, { s: 0.9, o: 0 }, 0.4, E.sine);    // 停顿里：大字缩小、淡出
    c.show(k, tA + 0.1, null, 8);
    c.show(l2, tA + 0.3, null, 10);
    c.show(rule, tA + 0.45, null, 0);
    c.show(sub, tSub, null, 8);
    c.cue(tA, 'word'); c.cue(tSub, 'word');
  });

  // ================================================================== S02 三个疑问
  ENG.scene('S02', c => {
    const s = c.segs();                                   // S02-02 … S02-08
    const tB = c.P(s[0], 'AI不就是', 0.2) - 0.15, tN = c.P(s[1], '新闻', 0.2) - 0.05, tAway = s[2].start;
    // 聊天气泡（示意：虚构对话，无头像、无 logo）
    const lb = c.label('常有人说 <span style="opacity:.7">· 示意（虚构对话）</span>', 700, 214, { size: 22, kind: 's', at: tB - 0.1 });
    const bb = bubble(c, { x: 690, y: 256, text: 'AI 不就是<span class="or">文字接龙</span>吗？', size: 48, at: tB });
    // 新闻标题卡（示意：不写媒体名、不用 logo）
    const nw = paper(c, 1000, 430, 640, 226, { kicker: 'HEADLINE · 新闻标题', shiyi: true });
    tx(c, nw, 36, 58, '<span class="or">AGI</span> 已经来了？', '900 58px var(--cjk)', { lh: 78 });
    [[36, 154, 540], [36, 184, 430]].forEach(([x, y, w]) => { const l = c.div('', x, y, w, 12, '', nw); Object.assign(l.style, { background: '#D6D1C7', borderRadius: '6px' }); });
    const trN = c.show(nw, tN, null, 14);
    c.cue(tN, 'card');
    // 「你可能会有三个疑问」：气泡和标题卡缩小移走 → 疑问卡逐张出现 → 飞进右上目录
    [lb.tr, bb.tr, trN].forEach(tr => tr.to(tAway, { o: 0, x: 220, y: -90, s: 0.7 }, 0.5, E.inOut));
    c.questionCards({ at: [3, 4, 5].map(i => s[i].start + 0.05), titleAt: s[2].start + 0.3 });
  });

  // ================================================================== S03 一、学会接龙
  ENG.scene('S03', c => {
    const s = c.segs();                                   // s[0] S03-09 … s[11] S03-20
    buildGlobals();
    const tMorph = P('S03-09', '是AI变强', 0.45) - 0.1;
    c.autoTitle(s[0], { morph: tMorph });

    // ---- (a) 四个阶段（大）：S03-09 出现、说到“四个阶段”四条一起亮 → 只亮第 1 条；S03-10 收进顶部小图；S03-20 再放大
    const big = bandChart(c.root, BIG);
    const bt = bandTracks(big, (e, i, f) => c.T(e, i, f));
    const toDock = poseOf(BIG, DOCK);
    const tBig = tMorph + 0.35, tFlash = P('S03-09', '四个阶段', 0.5), tFirst = P('S03-09', '里的第一个', 0.7), tPre = P('S03-09', '预训练', 0.9);
    const tBack = s[11].start, tEnd = c.endTalk();
    c.T(big.el, { o: 0, y: 14 }).in(tBig, 0.45)
      .to(s[1].start, Object.assign({ o: 0 }, toDock), 0.6, E.inOut)
      .to(tBack, { o: 1, x: 0, y: 0, s: 1 }, 0.6, E.inOut)
      .to(tEnd, Object.assign({ o: 0 }, toDock), 0.55, E.inOut);
    c.cue(tBig, 'chart'); c.cue(tBack + 0.2, 'chart');
    setBands(bt, tFlash, [1, 1, 1, 1], [0, 0, 0, 0], 0.25);
    setBands(bt, tFirst, [1, 0, 0, 0], [1, 0, 0, 0]);
    const b1 = big.bands[0];
    const pt = ENG.box('div', 'bc-in', big.el, b1.xm + 20, b1.y, null, BIG.bh);
    Object.assign(pt.style, { fontSize: '22px', lineHeight: BIG.bh + 'px' });
    pt.textContent = '预训练';
    c.T(pt, { o: 0 }).to(tPre, { o: 1 }, 0.3);
    const tW = P('S03-20', '往后', 0.55);                 // 后三条依次闪一下
    [1, 2, 3].forEach((k, j) => { const t = tW + 0.32 * j; bt[k].to(t, { on: 1 }, 0.2).to(t + 0.5, { on: 0 }, 0.35); });

    // ---- (b) 预训练：根据前文预测下一个 token（示意）
    const pc = paper(c, 560, 214, 1000, 392, { kicker: 'PRE-TRAINING · 预训练', shiyi: true });
    tx(c, pc, 36, 50, '读海量文本，根据前文预测下一个 <span class="or">token</span>', '800 38px var(--cjk)', { lh: 52 });
    c.div('dash', 36, 116, 928, null, '', pc);
    const tCtx = c.P(s[1], '根据前文', 0.35), tNext = c.P(s[1], '预测下一个', 0.55), tTok = c.P(s[1], '词元', 0.9);
    const sent = tx(c, pc, 46, 170, '今天天气很', '900 72px var(--cjk)', { lh: 100 });
    const blank = c.div('', 450, 172, 96, 96, '？', pc);
    Object.assign(blank.style, { border: '3px dashed var(--orange)', borderRadius: '10px', font: '900 60px var(--cjk)', color: 'var(--orange)', textAlign: 'center', lineHeight: '90px' });
    const trSent = c.show(sent, tCtx, null, 8);
    c.show(blank, tCtx + 0.2, null, 8);
    const ar = c.arrow(566, 220, 622, 220, '#FF4F1A', { w: 4, head: 13, parent: pc });
    c.T(ar, { o: 0 }).to(tNext, { o: 1 }, 0.3);
    const pl = tx(c, pc, 646, 140, '下一个词的概率', '500 20px var(--cjk)', { color: 'var(--grey)' });
    c.show(pl, tNext, null, 6);
    [['好', 0.62], ['热', 0.23], ['冷', 0.15]].forEach(([w, p], i) => {
      const row = c.div('', 646, 172 + i * 62, 320, 56, '', pc);
      tx(c, row, 0, 0, w, '900 42px var(--cjk)', { lh: 56, color: i === 0 ? 'var(--orange)' : 'var(--ink)' });
      const bar = c.div('', 62, 17, Math.round(250 * p), 22, '', row);
      Object.assign(bar.style, { background: i === 0 ? 'var(--orange)' : '#9A958C', borderRadius: '4px' });
      c.show(row, tNext + 0.15 * (i + 1), null, 6);
    });
    c.cue(tNext, 'item');
    // 说到“词元”：这行字切成几段彩色小块
    const tokRow = c.div('', 46, 176, 400, 92, '', pc);
    let tokX = 0;
    [['今天', '#F2A0BD'], ['天气', '#F6C945'], ['很', '#8FA8E8']].forEach(([t, col]) => {
      const e = tx(c, tokRow, tokX, 0, t, '900 58px var(--cjk)', { lh: 84 });
      Object.assign(e.style, { background: rgba(col, 0.42), border: `3px solid ${col}`, borderRadius: '10px', padding: '0 10px' });
      tokX += e.offsetWidth + 10;
    });
    c.T(tokRow, { o: 0 }).to(tTok, { o: 1 }, 0.3);
    trSent.to(tTok, { o: 0 }, 0.25);
    c.bracket(46, 290, tokX - 10, 'token（词元）', { at: tTok + 0.2, parent: pc, size: 26 });
    c.show(pc, s[1].start + 0.55, s[2].start, 14);
    c.cue(s[1].start + 0.55, 'card');

    // ---- (c) Transformer（2017）→ GPT = 生成式 / 预训练 / Transformer
    const tTf = c.P(s[2], '2017', 0.4) - 0.1, tGpt = s[3].start, tOff3 = s[5].start;
    const tf = dateCard(c, { x: 860, y: 284, w: 560, date: '2017', title: 'Transformer', tag: '模型结构',
      sub: ['Google《Attention Is All You Need》', '最初用于机器翻译'], at: tTf, until: tOff3 });
    tf.tr.to(tGpt, { x: 430 }, 0.6, E.inOut);            // 让出左边给 GPT 三个字母
    const cols = [640, 900, 1160];
    const tG = c.P(s[3], 'GPT', 0.5);
    ['G', 'P', 'T'].forEach((L, i) => c.show(tx(c, null, cols[i] - 120, 274, L, '800 150px var(--mono)', { w: 240, align: 'center', color: 'var(--orange)', lh: 170 }), tG + 0.12 * i, tOff3, 12));
    c.cue(tG, 'word');
    const link = c.arrow(1226, 372, 1284, 372, '#FF4F1A', { w: 4, noHead: true, dash: '7 6' });
    c.T(link, { o: 0 }).to(tG + 0.55, { o: 1 }, 0.3).out(tOff3);
    const tZh = [c.P(s[3], '生成式', 0.5), c.P(s[3], '预训练', 0.65), c.P(s[3], 'Transformer', 0.85)];
    ['生成式', '预训练', 'Transformer'].forEach((w, i) => c.show(tx(c, null, cols[i] - 130, 460, w, i === 2 ? '800 34px var(--mono)' : '900 40px var(--cjk)', { w: 260, align: 'center', lh: 56 }), tZh[i], tOff3, 8));
    const tEn = [c.P(s[4], 'Generative', 0.4), c.P(s[4], 'Pre-trained', 0.6), c.P(s[4], 'Transformer', 0.85)];
    ['<span class="or">G</span>enerative', '<span class="or">P</span>re-trained', '<span class="or">T</span>ransformer'].forEach((w, i) =>
      c.show(tx(c, null, cols[i] - 130, 528, w, '700 30px var(--mono)', { w: 260, align: 'center', lh: 44, color: 'rgba(237,234,227,.95)' }), tEn[i], tOff3, 8));
    const note = tx(c, null, 520, 612, 'GPT-1 论文：Improving Language Understanding by Generative Pre-Training（2018）', '500 20px var(--cjk)', { color: 'rgba(237,234,227,.72)' });
    c.show(note, tEn[2] + 0.5, tOff3, 6);

    // ---- (d) GPT-1 → GPT-3 参数量柱状图（对数刻度，示意）
    const tC0 = s[5].start + 0.1, tC1 = s[6].start;
    const bc = paper(c, 560, 196, 1000, 628, { kicker: 'PARAMETERS · 参数量（对数刻度）', shiyi: true });
    tx(c, bc, 36, 48, 'GPT-1 到 GPT-3：只隔了两年', '800 34px var(--cjk)', { lh: 48 });
    const PX0 = 150, PX1 = 640, PB = 470, PT = 136;
    const lv = v => PB - (Math.log10(v) - 7) / 5 * (PB - PT);
    let gs = '';
    [[1e7, '1000 万'], [1e8, '1 亿'], [1e9, '10 亿'], [1e10, '100 亿'], [1e11, '1000 亿'], [1e12, '1 万亿']].forEach(([v, lab]) => {
      const y = lv(v).toFixed(1);
      gs += `<line x1="${PX0}" y1="${y}" x2="${PX1}" y2="${y}" stroke="#C9C3B8" stroke-width="1.5" ${v === 1e7 ? '' : 'stroke-dasharray="6 6"'}/>`;
      tx(c, bc, 18, lv(v) - 13, lab, '500 18px var(--cjk)', { w: PX0 - 34, align: 'right', color: 'var(--grey)', lh: 26 });
    });
    c.svg(0, 0, 1000, 628, gs, bc);
    const bars = [['GPT-1', '2018', 1.17e8, '1.17 亿'], ['GPT-2', '2019', 1.5e9, '15 亿'], ['GPT-3', '2020', 1.75e11, '1750 亿']];
    const bx = [236, 396, 556];
    const tG3 = c.P(s[5], 'GPT-3', 0.3), tV1 = c.P(s[5], '1.17亿', 0.6), tV3 = c.P(s[5], '1750亿', 0.85);
    const tBar = [s[5].start + 0.35, (s[5].start + 0.35 + tG3) / 2, tG3], tVal = [tV1, (tV1 + tV3) / 2, tV3];
    bars.forEach(([name, yr, v, lab], i) => {
      const top = lv(v);
      const b = c.div('', bx[i] - 44, top, 88, PB - top, '', bc);
      Object.assign(b.style, { background: i === 2 ? 'var(--orange)' : '#3A3833', borderRadius: '4px 4px 0 0', transformOrigin: '50% 100%', transform: 'scaleY(0)' });
      c.T(null, { g: 0 }, p => { b.style.transform = `scaleY(${p.g.toFixed(3)})`; }).to(tBar[i], { g: 1 }, 0.6);
      c.show(tx(c, bc, bx[i] - 90, top - 46, lab, '800 28px var(--cjk)', { w: 180, align: 'center', lh: 40, color: i === 2 ? 'var(--orange)' : 'var(--ink)' }), tVal[i], null, 6);
      c.show(tx(c, bc, bx[i] - 90, PB + 10, `<span style="font:700 24px var(--mono)">${name}</span><br><span style="font:500 18px var(--cjk);color:var(--grey)">${yr}</span>`, '700 24px var(--cjk)', { w: 180, align: 'center', lh: 28 }), tBar[i], null, 6);
    });
    c.bracket(bx[0] - 44, PB + 76, bx[2] - bx[0] + 88, '2018 → 2020：只隔两年', { at: c.P(s[5], '只隔了两年', 0.5), parent: bc, size: 22 });
    c.div('', 680, 136, 2, 334, '', bc).style.background = '#D6D1C7';
    const n1 = tx(c, bc, 706, 140, '<b>参数</b>：模型里靠训练调出来的数值', '500 22px var(--cjk)', { w: 260, wrap: true, lh: 34 });
    const n2 = tx(c, bc, 706, 262, 'GPT-4 起，官方不公布参数量', '500 22px var(--cjk)', { w: 260, wrap: true, lh: 34, color: 'var(--grey)' });
    c.show(n1, s[5].start + 1.4, null, 6);
    c.show(n2, tV3 + 0.4, null, 6);
    c.show(bc, tC0, tC1, 14);
    c.cue(tC0, 'chart');

    // ---- (e) 「文字接龙：对了一半」两栏卡（S03-15 … S03-19），下半是按台词替换的示意区
    const tH = s[6].start + 0.08, tHOff = s[11].start;
    const hc = c.card(470, 190, 1360, 640);
    c.div('kicker', 40, 22, 700, null, 'HALF RIGHT · 对了一半', hc);
    tx(c, hc, 40, 44, '文字接龙：<span class="or">对了一半</span>', '900 54px var(--cjk)', { lh: 70 });
    c.div('dash', 40, 124, 1280, null, '', hc);
    const tCols = c.P(s[6], '对了一半', 0.6);
    const hL = tx(c, hc, 40, 142, `<svg width="28" height="26" viewBox="0 0 30 28" style="vertical-align:-3px;margin-right:10px">${ICON.check('#FF4F1A', 4.5)}</svg>对的一半`, '800 28px var(--cjk)', { lh: 40 });
    const hR = tx(c, hc, 700, 142, '<span class="or" style="margin-right:10px">＋</span>另一半', '800 28px var(--cjk)', { lh: 40 });
    const vdiv = c.svg(668, 146, 4, 252, '<line x1="2" y1="0" x2="2" y2="252" stroke="#B9B3A8" stroke-width="2" stroke-dasharray="8 7"/>', hc);
    [hL, hR, vdiv].forEach(e => c.show(e, tCols, null, 6));
    const item = (x, y, n, html, at) => {
      const e = c.div('', x, y, null, 44, '', hc);
      badge(c, e, 0, 2, n, 38, 20);
      tx(c, e, 54, 0, html, '700 30px var(--cjk)', { lh: 42 });
      c.show(e, at, null, 8); c.cue(at, 'item');
      return e;
    };
    item(40, 198, 1, '预训练目标 ＝ 预测下一个 <span class="or">token</span>', c.P(s[7], '训练目标', 0.05));
    item(40, 258, 2, '回答逐个 token 生成', c.P(s[7], '回答也是', 0.5));
    c.show(tx(c, hc, 94, 318, '这里的“词”指 token', '500 22px var(--cjk)', { color: 'var(--grey)' }), c.P(s[7], '一个词一个词', 0.8) + 0.2, null, 6);
    const tR1 = c.P(s[8], 'GPT-2论文推测', 0.05), tR2 = s[9].start + 0.1, tR3 = s[10].start + 0.1;
    item(700, 198, 1, '为了猜准，会学会文本里演示的任务', tR1);
    c.show(tx(c, hc, 754, 240, 'GPT-2 论文的推测（2019）· 比如翻译、问答', '500 19px var(--cjk)', { color: 'var(--grey)' }), tR1 + 0.4, null, 6);
    item(700, 280, 2, '写押韵诗：先想好韵脚，再写这一行', tR2);
    c.show(tx(c, hc, 754, 322, 'Anthropic（Claude 的开发公司）可解释性研究', '500 19px var(--cjk)', { color: 'var(--grey)' }), tR2 + 0.4, null, 6);
    item(700, 360, 3, '逐个输出 ≠ 只想下一个', tR3);
    c.show(c.div('dash', 40, 420, 1280, null, '', hc), c.P(s[8], '演示的任务', 0.75) - 0.3, null, 0);
    // 示意区 ①：给几个例子就会（GPT-3）
    const tFs = c.P(s[8], '演示的任务', 0.75) - 0.2;
    const fs = c.div('', 250, 440, 860, 180, '', hc);
    const pb = c.div('', 0, 4, 340, 166, '', fs);
    Object.assign(pb.style, { background: '#1E1E1D', borderRadius: '10px' });
    tx(c, pb, 26, 14, '苹果 → apple', '700 28px var(--cjk)', { color: 'var(--paper)', lh: 44 });
    tx(c, pb, 26, 60, '香蕉 → banana', '700 28px var(--cjk)', { color: 'var(--paper)', lh: 44 });
    const l3 = tx(c, pb, 26, 106, '葡萄 → <span class="slot" style="position:relative;display:inline-block;width:100px;height:44px;vertical-align:top"><span class="q" style="position:absolute;left:0;top:0;color:#8F897F">？</span><span class="a" style="position:absolute;left:0;top:0;color:#FF7A4D">grape</span></span>', '700 28px var(--cjk)', { color: 'var(--paper)', lh: 44 });
    const qa = l3.querySelector('.q'), an = l3.querySelector('.a');
    c.T(qa, { o: 1 }).to(tFs + 1.0, { o: 0 }, 0.2);
    c.T(an, { o: 0 }).to(tFs + 1.0, { o: 1 }, 0.3);
    tx(c, fs, 380, 20, 'GPT-3（2020）', '800 30px var(--cjk)', { lh: 44 });
    tx(c, fs, 380, 70, '给几个例子就会，参数不变', '600 26px var(--cjk)', { lh: 40, color: '#4A4741' });
    c.div('shiyi', 380, 124, null, null, '示意', fs);
    c.show(fs, tFs, s[9].start, 8);
    c.cue(tFs, 'demo');
    // 示意区 ②：押韵诗先定韵脚（诗句为示意）
    const tPoem = s[9].start + 0.3, tRhyme = c.P(s[9], '先想好韵脚', 0.3), tWrite = c.P(s[9], '再写这一行', 0.6), tPoemOff = c.P(s[10], '理解', 0.5) - 0.3;
    const pm = c.div('', 160, 440, 1080, 180, '', hc);
    tx(c, pm, 0, 6, 'The night was cold, the moon was <span style="text-decoration:underline;text-decoration-color:#FF4F1A;text-underline-offset:6px">bright</span>,', '600 32px var(--mono)', { lh: 46, color: '#6E6A63' });
    const l2 = c.div('', 0, 62, null, 46, '', pm);
    Object.assign(l2.style, { font: '600 32px var(--mono)', lineHeight: '46px', whiteSpace: 'nowrap', color: 'var(--ink)' });
    const words = ['The', 'stars', 'all', 'shone', 'with', 'silver', 'light'];
    const ws = words.map((w, i) => { const sp = ENG.el('span', '', l2, esc(w)); sp.style.display = 'inline-block'; if (i < words.length - 1) sp.style.marginRight = '.6em'; return sp; });
    Object.assign(ws[6].style, { color: 'var(--orange)', outline: '3px solid var(--orange)', outlineOffset: '3px', borderRadius: '3px' });
    c.T(ws[6], { o: 0 }).to(tRhyme, { o: 1 }, 0.3);
    ws.slice(0, 6).forEach((sp, i) => c.T(sp, { o: 0 }).to(tWrite + 0.13 * i, { o: 1 }, 0.2));
    const rl = tx(c, pm, ws[6].offsetLeft + ws[6].offsetWidth + 26, 66, '← 先定韵脚，再写前面', '700 24px var(--cjk)', { color: 'var(--orange)', lh: 38 });
    c.T(rl, { o: 0 }).to(tRhyme + 0.2, { o: 1 }, 0.3);
    tx(c, pm, 0, 130, 'Anthropic 可解释性研究 · 2025-03-27 · 研究对象 Claude 3.5 Haiku · 诗句为示意', '500 19px var(--cjk)', { color: 'var(--grey)' });
    c.show(pm, tPoem, tPoemOff, 8);
    c.cue(tRhyme, 'demo');
    // 示意区 ③：算不算“理解”，学界还在争
    const tSv = tPoemOff + 0.3;
    const sv = c.div('', 160, 440, 1080, 180, '', hc);
    tx(c, sv, 0, 4, '“只靠文本训练的模型，能否理解语言？”', '800 30px var(--cjk)', { lh: 44 });
    const hb = c.div('', 0, 64, 760, 44, '', sv);
    hb.innerHTML = '<div style="position:absolute;left:0;top:0;width:51%;height:44px;background:#3A3833;border-radius:6px 0 0 6px;color:#EDEAE3;font:700 22px var(--cjk);line-height:44px;padding-left:16px">认为能</div>' +
      '<div style="position:absolute;right:0;top:0;width:49%;height:44px;background:#C9C3B8;border-radius:0 6px 6px 0;color:#141414;font:700 22px var(--cjk);line-height:44px;text-align:right;padding-right:16px">认为不能</div>';
    tx(c, sv, 790, 68, '几乎对半分', '800 28px var(--cjk)', { color: 'var(--orange)', lh: 36 });
    tx(c, sv, 0, 128, '2022 年自然语言处理（NLP）研究者调查 · 示意', '500 19px var(--cjk)', { color: 'var(--grey)' });
    c.show(sv, tSv, null, 8);
    c.cue(tSv, 'demo');
    c.show(hc, tH, tHOff, 14);
    c.cue(tH, 'card');
  });

  // ================================================================== S04 二、学会对话
  ENG.scene('S04', c => {
    const s = c.segs();                                   // s[0] S04-21 … s[8] S04-29
    c.autoTitle(s[0]);
    const t2 = P('S04-21', '第二阶段', 0.4);             // 顶部小色带图此刻亮第 2 条（buildGlobals）
    c.label('第二阶段 · 听懂指令，按要求回答', 650, 548, { w: 1000, align: 'center', size: 34, at: t2, until: s[0].end - 0.05 });

    // ---- (a) 两步训练：① SFT 监督微调 → ② RLHF 基于人类反馈的强化学习（英文全称只上屏，首字母高亮）
    const tA0 = s[1].start + 0.1, tA1 = s[5].start;
    const card = paper(c, 470, 196, 1360, 616, { kicker: 'TWO STEPS · 两步训练', shiyi: true });
    tx(c, card, 36, 46, '学会对话：靠两步训练', '800 38px var(--cjk)', { lh: 52 });
    const box = (x, n, stepLbl) => {
      const b = c.div('inbox', x, 116, 620, 440, '', card);
      badge(c, b, 24, 20, n, 36, 20);
      tx(c, b, 72, 22, stepLbl, '700 22px var(--cjk)', { color: 'var(--grey)', lh: 32 });
      return b;
    };
    // ① SFT
    const b1 = box(36, 1, '第一步 · STEP 1');
    const tB1 = c.P(s[1], '第一步', 0.3), tSFT = c.P(s[1], '监督微调', 0.5), tSFTen = c.P(s[1], 'SFT', 0.8);
    const sftHead = c.div('', 24, 62, 580, 80, '', b1);
    tx(c, sftHead, 0, 0, 'SFT', '800 62px var(--mono)', { lh: 80 });
    tx(c, sftHead, 150, 14, '监督微调', '900 44px var(--cjk)', { lh: 60 });
    c.show(sftHead, tSFT, null, 8);
    c.show(tx(c, b1, 24, 146, '<span class="or">S</span>upervised <span class="or">F</span>ine-<span class="or">T</span>uning', '700 30px var(--mono)', { lh: 42 }), tSFTen, null, 6);
    c.div('dash', 24, 206, 572, null, '', b1);
    const tDoc = s[2].start + 0.1, tLearn = c.P(s[2], '模型照着学', 0.6);
    const doc = c.div('', 30, 250, 230, 150, '', b1);
    Object.assign(doc.style, { background: '#FBFAF7', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,.12)' });
    c.svg(24, 26, 36, 40, ICON.doc(), doc);
    tx(c, doc, 74, 22, '人写的', '800 26px var(--cjk)', { lh: 36 });
    tx(c, doc, 74, 58, '标准回答', '800 26px var(--cjk)', { lh: 36 });
    tx(c, doc, 24, 104, '（示范怎么回答）', '500 18px var(--cjk)', { color: 'var(--grey)' });
    c.show(doc, tDoc, null, 8); c.cue(tDoc, 'node');
    const la = c.arrow(272, 325, 352, 325, '#FF4F1A', { w: 4, head: 13, parent: b1 });
    c.T(la, { o: 0 }).to(tLearn - 0.2, { o: 1 }, 0.3);
    c.show(tx(c, b1, 268, 276, '照着学', '800 22px var(--cjk)', { color: 'var(--orange)', w: 90, align: 'center' }), tLearn - 0.1, null, 6);
    const mdl = c.div('', 366, 250, 222, 150, '', b1);
    Object.assign(mdl.style, { background: '#1E1E1D', borderRadius: '8px' });
    c.svg(24, 37, 76, 76, `<g transform="translate(0,0) scale(1)">${ICON.chip('#EDEAE3')}</g>`, mdl);
    tx(c, mdl, 116, 54, '模型', '800 32px var(--cjk)', { color: 'var(--paper)', lh: 44 });
    c.show(mdl, tLearn, null, 8);
    c.T(b1, { o: 0, y: 10 }).to(tA0 + 0.25, { o: 0.5, y: 0 }, 0.35).to(tB1 - 0.1, { o: 1 }, 0.3); c.cue(tB1, 'card');
    // ② RLHF
    const b2 = box(704, 2, '第二步 · STEP 2');
    const tB2 = c.P(s[3], '第二步', 0.1), tRL = c.P(s[3], '强化学习', 0.5), tRLen = c.P(s[3], 'RLHF', 0.8);
    const rlHead = c.div('', 24, 62, 580, 80, '', b2);
    tx(c, rlHead, 0, 0, 'RLHF', '800 62px var(--mono)', { lh: 80 });
    tx(c, rlHead, 176, 20, '基于人类反馈的强化学习', '900 34px var(--cjk)', { lh: 50 });
    c.show(rlHead, tRL - 0.4, null, 8);
    c.show(tx(c, b2, 24, 142, '<span class="or">R</span>einforcement <span class="or">L</span>earning<br>from <span class="or">H</span>uman <span class="or">F</span>eedback', '700 27px var(--mono)', { lh: 34 }), tRLen, null, 6);
    c.div('dash', 24, 222, 572, null, '', b2);
    const tRank0 = s[4].start + 0.1, tSort = c.P(s[4], '排序', 0.3) + 0.3, tRM = c.P(s[4], '打分模型', 0.5), tUp = c.P(s[4], '朝高分', 0.7);
    c.show(tx(c, b2, 30, 236, '人来排序', '700 19px var(--cjk)', { color: 'var(--grey)' }), tRank0, null, 6);
    const ans = ['回答 A', '回答 B', '回答 C'], order = [1, 0, 2];   // 排好以后：B 第一、A 第二、C 第三
    ans.forEach((a, i) => {
      const e = c.div('chip', 30, 268 + i * 52, 150, 44, a, b2);
      e.style.fontSize = '22px'; e.style.textAlign = 'center';
      const tr = c.T(e, { o: 0, y: 8 });
      tr.in(tRank0 + 0.12 * i, 0.3).to(tSort, { y: (order[i] - i) * 52 }, 0.55, E.inOut);
      c.show(badge(c, b2, 190, 272 + i * 52, i + 1, 34, 18), tSort + 0.5, null, 4);
    });
    c.cue(tRank0, 'item');
    const ra1 = c.arrow(232, 346, 292, 346, '#FF4F1A', { w: 4, head: 12, parent: b2 });
    c.T(ra1, { o: 0 }).to(tRM - 0.2, { o: 1 }, 0.3);
    const rm = c.div('', 302, 282, 150, 128, '', b2);
    Object.assign(rm.style, { background: '#1E1E1D', borderRadius: '8px' });
    tx(c, rm, 0, 22, '打分', '800 30px var(--cjk)', { w: 150, align: 'center', color: 'var(--paper)', lh: 40 });
    tx(c, rm, 0, 62, '模型', '800 30px var(--cjk)', { w: 150, align: 'center', color: 'var(--paper)', lh: 40 });
    c.show(rm, tRM, null, 8); c.cue(tRM, 'node');
    const ra2 = c.arrow(462, 346, 512, 346, '#FF4F1A', { w: 4, head: 12, parent: b2 });
    c.T(ra2, { o: 0 }).to(tUp - 0.2, { o: 1 }, 0.3);
    const ai = c.div('', 520, 282, 76, 128, 'AI', b2);
    Object.assign(ai.style, { background: 'var(--orange)', borderRadius: '8px', color: 'var(--paper)', font: '800 30px var(--mono)', textAlign: 'center', lineHeight: '128px' });
    c.show(ai, tUp, null, 8);
    c.show(tx(c, b2, 330, 414, '让 AI 朝高分去学', '800 20px var(--cjk)', { color: 'var(--orange)', w: 266, align: 'right' }), tUp + 0.1, null, 6);
    c.T(b2, { o: 0, y: 10 }).to(tA0 + 0.4, { o: 0.5, y: 0 }, 0.35).to(tB2 - 0.1, { o: 1 }, 0.3); c.cue(tB2, 'card');
    const arr = c.arrow(662, 336, 700, 336, '#FF4F1A', { w: 5, head: 14, parent: card });
    c.T(arr, { o: 0 }).to(tB2, { o: 1 }, 0.3);
    c.show(tx(c, card, 36, 572, '现代 RLHF 常追溯到 2017 年的论文（Christiano 等）', '500 19px var(--cjk)', { color: 'var(--grey)' }), tUp + 0.4, null, 6);
    c.show(card, tA0, tA1, 14);
    c.cue(tA0, 'card');

    // ---- (b) InstructGPT（2022-01）· 人工评估：最小的 13 亿版本胜过 1750 亿的 GPT-3 · ChatGPT（2022-11-30）
    const tB0 = s[5].start + 0.1, tB9 = s[8].start;
    dateCard(c, { x: 480, y: 214, w: 520, date: '2022-01', title: 'InstructGPT', sub: 'OpenAI · 用这两步训练', at: tB0, until: tB9 });
    dateCard(c, { x: 480, y: 430, w: 520, date: '2022-11-30', title: 'ChatGPT 发布', sub: '方法同 InstructGPT，数据改成对话形式', at: s[7].start + 0.12, until: tB9 });
    const tCmp = s[6].start + 0.1, tSmall = c.P(s[6], '13亿', 0.5), tBigSq = c.P(s[6], '1750亿', 0.5), tWin = c.P(s[6], '更受欢迎', 0.8);
    const cmp = paper(c, 1060, 214, 780, 548, { kicker: 'HUMAN EVAL · 人工评估', shiyi: true });
    tx(c, cmp, 36, 48, '谁的回答更受评估者欢迎？', '800 32px var(--cjk)', { lh: 46 });
    const side = Math.round(300 / Math.sqrt(1750 / 13));     // 面积 ∝ 参数量
    const bigSq = c.div('', 420, 120, 300, 300, '', cmp);
    Object.assign(bigSq.style, { background: 'rgba(20,20,20,.1)', border: '3px solid #3A3833', borderRadius: '4px' });
    const smSq = c.div('', 164 - side / 2, 420 - side, side, side, '', cmp);
    Object.assign(smSq.style, { background: '#3A3833', borderRadius: '2px' });
    const smL = c.div('', 30, 434, 270, 80, '', cmp);
    tx(c, smL, 0, 0, 'InstructGPT（最小版）', '700 21px var(--cjk)', { w: 270, align: 'center', lh: 30 });
    tx(c, smL, 0, 32, '13 亿参数', '900 28px var(--cjk)', { w: 270, align: 'center', lh: 40, color: 'var(--orange)' });
    const bgL = c.div('', 420, 434, 300, 80, '', cmp);
    tx(c, bgL, 0, 0, 'GPT-3', '700 22px var(--mono)', { w: 300, align: 'center', lh: 30 });
    tx(c, bgL, 0, 32, '1750 亿参数', '900 28px var(--cjk)', { w: 300, align: 'center', lh: 40 });
    c.show(smSq, tSmall, null, 4); c.show(smL, tSmall, null, 6);
    c.show(bigSq, tBigSq, null, 6); c.show(bgL, tBigSq, null, 6);
    c.T(null, { w: 0 }, p => { smSq.style.background = p.w > 0.5 ? 'var(--orange)' : '#3A3833'; smSq.style.boxShadow = p.w > 0.5 ? '0 0 0 6px rgba(255,79,26,.25)' : ''; }).to(tWin, { w: 1 }, 0.1);
    c.chip(`<svg width="22" height="20" viewBox="0 0 30 28" style="vertical-align:-3px;margin-right:6px">${ICON.check('#EDEAE3', 5)}</svg>评估者更喜欢`, 72, 338, { kind: 'o', size: 22, h: 42, at: tWin, parent: cmp });
    c.cue(tWin, 'item');
    tx(c, cmp, 36, 514, 'InstructGPT 论文，2022 · 方块面积 ∝ 参数量', '500 18px var(--cjk)', { color: 'var(--grey)' });
    c.show(cmp, tCmp, tB9, 14);
    c.cue(tCmp, 'card');

    // ---- (c) 训练目标多了一条：② 人更喜欢哪个回答 → 飞进右下清单
    const f2 = goalFly('S04-29', '人更喜欢哪个回答');
    goalCard(c, { n: 2, text: '人更喜欢哪个回答', lead: '从这个阶段开始，训练目标多了一条：', at: s[8].start + 0.15, hl: P('S04-29', '人更喜欢哪个回答', 0.6), fly: f2.t });
  });

  // ================================================================== S05 三、学会思考
  ENG.scene('S05', c => {
    const s = c.segs();                                   // s[0] S05-30 … s[8] S05-38
    const tM = P('S05-30', '先写出', 0.5) - 0.25;
    c.autoTitle(s[0], { morph: tM });
    // ---- (a) 问题 → 步骤 1 → 步骤 2 → 答案（示意）
    const tSteps = tM + 0.4, tOffA = s[3].start;
    const st4 = chain(c, { x: 480, y: 206, items: ['问题', '步骤 1', '步骤 2', '答案'], at: tSteps, step: 0.22, until: tOffA, hot: [3] });
    c.label('先写推理步骤，再给答案 · 示意', 480 + st4.w + 24, 222, { size: 22, kind: 's', at: tSteps + 0.8, until: tOffA });
    // 思维链提示（2022-01）+ 提示词示意
    const row = c.div('', 0, 0, null, null, '');           // 时间线一排：思维链提示 → o1 → R1（整排跟着上移）
    const rowTr = c.T(row, { o: 1 });
    dateCard(c, { x: 480, y: 318, w: 440, date: '2022-01', title: '思维链提示', sub: 'Chain-of-Thought（CoT）· Google', at: s[1].start + 0.1, parent: row });
    const tPb = s[2].start + 0.1, tTip = c.P(s[2], '提问技巧', 0.5);
    const pb = paper(c, 980, 318, 860, 420, { kicker: 'PROMPT · 提示词', shiyi: true });
    const pLine = (y, tag, html, col) => {
      tagp(c, pb, tag, 36, y + 6, {});
      return tx(c, pb, 120, y, html, '600 25px var(--cjk)', { lh: 40, color: col || 'var(--ink)' });
    };
    pLine(60, '例题', '3 个苹果，又买 2 个，吃掉 1 个，还剩几个？');
    pLine(108, '步骤', '3 + 2 = 5，5 − 1 = 4。<b>答案：4</b>', '#4A4741');
    pLine(168, '新题', '6 支笔，用掉 2 支，又放进 3 支，现在几支？');
    c.div('dash', 36, 230, 788, null, '', pb);
    const outL = c.div('', 36, 250, 788, 44, '', pb);
    tx(c, outL, 0, 0, '模型输出', '700 20px var(--cjk)', { color: 'var(--grey)', lh: 44 });
    tx(c, outL, 96, 0, '步骤：6 − 2 = 4，4 + 3 = 7。<b class="or">答案：7</b>', '700 25px var(--cjk)', { lh: 44 });
    c.show(outL, c.P(s[2], '跟着写', 0.5), null, 6);
    c.chip('提示技巧 · 模型没变', 36, 336, { kind: 'dark', size: 22, h: 44, at: tTip, parent: pb });
    c.cue(tTip, 'item');
    c.show(pb, tPb, tOffA, 14); c.cue(tPb, 'card');
    // ---- (b) 时间线：思维链提示 → o1（2024-09-12 预览版）→ DeepSeek-R1（2025-01-20）；S05-35 起整排上移让出下半
    rowTr.to(s[5].start, { y: -122 }, 0.55, E.inOut).out(s[8].start);
    const o1 = dateCard(c, { x: 950, y: 318, w: 440, date: '2024-09-12', title: 'o1（预览版）', sub: 'OpenAI', at: s[3].start + 0.35, parent: row });
    const tRL = c.P(s[3], '强化学习', 0.5);
    c.chip('训练方法 · 强化学习', 950, 318 + o1.h + 12, { kind: 'o', size: 21, h: 40, at: tRL, parent: row });
    c.cue(tRL, 'item');
    const tR1 = s[4].start + 0.1;
    dateCard(c, { x: 1420, y: 318, w: 420, date: '2025-01-20', title: 'DeepSeek-R1', sub: '开源权重', at: tR1, parent: row });
    [[922, 946], [1392, 1416]].forEach(([a, b], i) => {
      const e = c.arrow(a, 318 + 76, b, 318 + 76, 'rgba(237,234,227,.85)', { w: 3.5, head: 10, parent: row });
      c.T(e, { o: 0 }).to(i ? tR1 : s[3].start + 0.35, { o: 1 }, 0.3);
    });
    c.label('几个月后', 1420, 318 + o1.h + 20, { w: 420, align: 'left', size: 20, kind: 's', at: c.P(s[4], '几个月后', 0.2), parent: row });
    // ---- (c) R1-Zero（试验版）：跳过 SFT，直接强化学习；奖励只看答案、格式
    const tZ = s[5].start + 0.1, tSkip = c.P(s[5], '跳过监督微调', 0.3) + 0.4, tRLon = c.P(s[5], '直接做强化学习', 0.5);
    const zc = paper(c, 480, 420, 690, 400, { kicker: 'R1-ZERO · 试验版', shiyi: true });
    tx(c, zc, 36, 46, 'R1-Zero：跳过 SFT，直接强化学习', '800 30px var(--cjk)', { lh: 44 });
    const nd = (x, w, html, dark) => { const e = c.div('', x, 118, w, 80, html, zc); Object.assign(e.style, { background: dark ? '#1E1E1D' : '#E4DFD5', color: dark ? 'var(--paper)' : 'var(--ink)', borderRadius: '8px', font: '800 26px var(--cjk)', textAlign: 'center', lineHeight: '80px' }); return e; };
    nd(36, 160, '基座模型', true);
    const sft = nd(262, 130, 'SFT');
    Object.assign(sft.style, { background: 'transparent', border: '3px dashed #9A958C', color: '#9A958C', lineHeight: '74px', fontFamily: 'var(--mono)' });
    const strike = c.svg(262, 118, 130, 80, '<line x1="10" y1="70" x2="120" y2="10" stroke="#D8342A" stroke-width="5" stroke-linecap="round"/>', zc);
    c.T(strike, { o: 0 }).to(tSkip, { o: 1 }, 0.25);
    const rl = nd(458, 196, '强化学习', true);
    c.T(null, { w: 0 }, p => { rl.style.background = p.w > 0.5 ? 'var(--orange)' : '#1E1E1D'; }).to(tRLon, { w: 1 }, 0.1);
    [[200, 258], [396, 454]].forEach(([a, b]) => c.arrow(a, 158, b, 158, '#3A3833', { w: 3.5, head: 11, parent: zc }));
    tx(c, zc, 36, 236, '奖励只看：', '800 26px var(--cjk)', { lh: 44 });
    const rwd = (x, html, at) => { const e = c.chip(`<svg width="22" height="20" viewBox="0 0 30 28" style="vertical-align:-3px;margin-right:8px">${ICON.check('#FF4F1A', 5)}</svg>${html}`, x, 236, { size: 24, h: 44, at, parent: zc }); e.el.style.border = '2px solid var(--orange)'; c.cue(at, 'item'); return e; };
    rwd(176, '答案对不对', c.P(s[5], '答案对不对', 0.7) - 0.1);
    rwd(400, '格式对不对', c.P(s[5], '格式对不对', 0.85) - 0.1);
    c.show(tx(c, zc, 36, 318, '正式版 R1：先用少量冷启动数据做 SFT，再强化学习', '500 19px var(--cjk)', { color: 'var(--grey)' }), c.P(s[5], '格式对不对', 0.85) + 0.5, null, 6);
    c.show(zc, tZ, s[8].start, 14); c.cue(tZ, 'card');
    // ---- (d) 正确率曲线 15.6% → 71.0%（示意）+ 回头检查
    const tCh = s[6].start + 0.1, t15 = c.P(s[6], '15.6%', 0.6), t71 = c.P(s[6], '71%', 0.85);
    const ch = paper(c, 1200, 420, 640, 400, { kicker: 'R1-ZERO · 训练过程', shiyi: true });
    tx(c, ch, 36, 46, '一次做对的比例', '800 30px var(--cjk)', { lh: 44 });
    const X0 = 96, X1 = 600, YB = 318, YT = 118, yv = p => YB - p / 80 * (YB - YT);
    let ax = '';
    [0, 20, 40, 60, 80].forEach(p => {
      ax += `<line x1="${X0}" y1="${yv(p)}" x2="${X1}" y2="${yv(p)}" stroke="#D2CCC1" stroke-width="1.5" ${p ? 'stroke-dasharray="5 6"' : ''}/>`;
      tx(c, ch, 20, yv(p) - 12, p + '%', '500 17px var(--mono)', { w: 64, align: 'right', color: 'var(--grey)', lh: 24 });
    });
    c.svg(0, 0, 640, 400, ax, ch);
    tx(c, ch, X1 - 140, YB + 8, '训练步数 →', '500 17px var(--cjk)', { w: 140, align: 'right', color: 'var(--grey)' });
    const pts = [[0, 15.6], [0.08, 17], [0.16, 22], [0.25, 28], [0.33, 33], [0.42, 40], [0.5, 46], [0.58, 52], [0.67, 58], [0.75, 62], [0.83, 66], [0.92, 69], [1, 71.0]];
    const px = f => X0 + 14 + f * (X1 - X0 - 28);
    const d = pts.map(([f, p], i) => `${i ? 'L' : 'M'}${px(f).toFixed(1)} ${yv(p).toFixed(1)}`).join(' ');
    const line = c.svg(0, 0, 640, 400, `<path d="${d}" fill="none" stroke="#FF4F1A" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`, ch);
    const path = line.querySelector('path');
    c.T(null, { p: 0 }, q => { path.style.strokeDashoffset = (1 - q.p).toFixed(4); }).to(t15, { p: 1 }, Math.max(0.6, t71 - t15), E.inOut);
    const dotA = c.div('', px(0) - 8, yv(15.6) - 8, 16, 16, '', ch), dotB = c.div('', px(1) - 9, yv(71) - 9, 18, 18, '', ch);
    [dotA, dotB].forEach(e => Object.assign(e.style, { borderRadius: '50%', background: 'var(--paper)', border: '4px solid var(--orange)' }));
    c.show(dotA, t15 - 0.1, null, 0); c.show(dotB, t71, null, 0);
    c.show(tx(c, ch, px(0) + 14, yv(15.6) - 44, '15.6%', '800 28px var(--mono)', { lh: 34 }), t15 - 0.1, null, 6);
    c.show(tx(c, ch, px(1) - 150, yv(71) + 14, '71.0%', '800 30px var(--mono)', { w: 150, align: 'right', color: 'var(--orange)', lh: 36 }), t71, null, 6);
    tx(c, ch, 36, 354, 'AIME 2024 数学竞赛题 · R1-Zero 论文数据', '500 18px var(--cjk)', { color: 'var(--grey)' });
    c.show(ch, tCh, s[8].start, 14); c.cue(tCh, 'chart'); c.cue(t71, 'item');
    const tWait = s[7].start + 0.08;
    bubble(c, { x: 1560, y: 652, text: 'Wait… 再检查一下', size: 24, at: tWait, until: s[8].start });
    c.label('论文称 “aha moment” · 示意', 1568, 712, { size: 16, at: tWait + 0.3, until: s[8].start }).el.style.color = '#6E6A63';
    // ---- (e) 训练目标又多了一条：③ 答案对不对 → 飞进右下清单
    const f3 = goalFly('S05-38', '答案对不对');
    goalCard(c, { n: 3, text: '答案对不对', lead: '这个阶段，训练目标又多了一条：', at: s[8].start + 0.15, hl: P('S05-38', '答案对不对', 0.6), fly: f3.t });
  });

  // ================================================================== S06 四、学会做事
  ENG.scene('S06', c => {
    const s = c.segs();                                   // s[0] S06-39 … s[9] S06-48
    const tM = P('S06-39', '操作电脑', 0.45) - 0.15;
    c.autoTitle(s[0], { morph: tM });
    const tOffA = s[4].start, tOffB = s[8].start;
    // ---- (a) 智能体：目标 → 调工具 → 看结果 → 再调工具 → 完成（示意）
    const agent = chain(c, { x: 480, y: 206, items: ['目标', '调工具', '看结果', '再调工具', '完成'], at: tM + 0.4, step: 0.2, until: tOffA, hot: [4] });
    c.label('示意', 480 + agent.w + 18, 222, { size: 20, kind: 's', at: tM + 1.3, until: tOffA });
    const tAg = c.P(s[0], '智能体', 0.3);
    c.bracket(480, 276, agent.w, '这样的 AI 叫<span class="or" style="margin-left:10px">智能体 Agent</span>', { at: tAg, until: tOffA, size: 28 });
    // 函数调用（2023-06-13）
    dateCard(c, { x: 480, y: 372, w: 480, date: '2023-06-13', title: '函数调用', sub: 'Function Calling · OpenAI', at: s[1].start + 0.1, until: tOffA });
    const tFn = s[2].start + 0.1, tJs = c.P(s[2], '要调哪个函数', 0.3), tRun = c.P(s[2], '由程序去执行', 0.5), tRes = tRun + 0.55, tFnOff = s[3].start;
    c.node({ x: 1040, y: 360, w: 230, h: 150, icon: 'chip', title: '模型', size: 30, at: tFn, until: tFnOff });
    const js = c.code({ x: 1330, y: 360, w: 510, h: 154, title: '函数名 + 要传的数据', kicker: 'JSON', fs: 21, lh: 36, top: 56,
      lines: ['{ "name": "get_weather",', '  "arguments": { "city": "北京" } }'] });
    js.tr.in(tJs, 0.35).out(tFnOff);
    c.node({ x: 1560, y: 596, w: 280, h: 150, icon: 'server', title: '程序执行', size: 28, at: tRun, until: tFnOff });
    c.node({ x: 1040, y: 618, w: 230, h: 106, title: '结果', sub: '比如：晴，22°C', size: 30, at: tRes, until: tFnOff });
    [[1276, 435, 1324, 435, tJs], [1700, 520, 1700, 590, tRun], [1554, 671, 1276, 671, tRes], [1155, 612, 1155, 516, tRes + 0.3]].forEach(([a, b, x2, y2, t]) => {
      const e = c.arrow(a, b, x2, y2, '#FF4F1A', { w: 4, head: 13 });
      c.T(e, { o: 0 }).to(t, { o: 1 }, 0.3).out(tFnOff);
    });
    // 电脑操作（2024-10-22）：看屏幕、点鼠标、打字（虚构界面）
    dateCard(c, { x: 480, y: 580, w: 480, date: '2024-10-22', title: '电脑操作', sub: 'Computer Use · Anthropic', at: c.P(s[3], '电脑操作', 0.4), until: tOffA });
    const tWin = s[3].start + 0.12, tLook = c.P(s[3], '看屏幕', 0.4), tClick = c.P(s[3], '点鼠标', 0.55), tType = c.P(s[3], '打字', 0.75);
    const win = c.browser({ x: 1040, y: 360, w: 800, h: 440, title: '某个应用 · 虚构界面', at: tWin, until: tOffA });
    const v = win.view(tWin, null);
    c.div('ui-h', 40, 32, null, null, '天气查询', v);
    c.div('ui-t', 40, 94, null, null, '城市', v);
    const fld = c.div('field', 40, 130, 440, 56, '', v);
    ['北', '京'].forEach((ch, i) => { const sp = ENG.el('span', '', fld, ch); sp.style.fontFamily = 'var(--cjk)'; c.T(sp, { o: 0 }).to(tType + 0.28 * i, { o: 1 }, 0.05); });
    c.div('btn', 510, 132, null, 52, '查询', v);
    const steps3 = [['看屏幕', tLook], ['点鼠标', tClick], ['打字', tType]];
    steps3.forEach(([w, t], i) => c.chip(w, 40 + i * 150, 268, { kind: i === 2 ? 'o' : 'dark', size: 22, h: 42, at: t, until: tOffA, parent: v }));
    const cur = c.svg(640, 330, 30, 38, '<path d="M3 3 L3 31 L10 24 L15 35 L20 33 L15 22 L26 22 Z" fill="#141414" stroke="#EDEAE3" stroke-width="2.2" stroke-linejoin="round"/>', win.el);
    c.T(cur, { o: 0, x: 0, y: 0 }).to(tLook, { o: 1 }, 0.3).to(tClick - 0.55, { x: -400, y: -110 }, 0.55, E.inOut);
    const clk = c.div('', 222, 200, 44, 44, '', win.el);
    Object.assign(clk.style, { border: '3px solid var(--orange)', borderRadius: '50%' });
    c.T(clk, { o: 0, s: 0.4 }).to(tClick, { o: 1, s: 1 }, 0.25).to(tClick + 0.3, { o: 0 }, 0.3);
    c.cue(tWin, 'ui');

    // ---- (b) METR：能做多长的任务？ 50% 任务时间跨度（对数纵轴，示意）
    const tH = s[4].start + 0.1, tMetr = c.P(s[4], 'METR', 0.5);
    const hd = paper(c, 480, 196, 560, 198, { kicker: 'METR · 评测机构' });
    tx(c, hd, 36, 46, '能做多长的任务？', '900 44px var(--cjk)', { lh: 60 });
    const hs = c.div('', 36, 116, 500, 60, '', hd);
    tx(c, hs, 0, 0, 'Model Evaluation and Threat Research', '600 18px var(--mono)', { lh: 26 });
    tx(c, hs, 0, 28, '模型评估与威胁研究 · 非营利研究机构', '500 18px var(--cjk)', { color: 'var(--grey)', lh: 26 });
    c.show(hs, tMetr, null, 6);
    c.show(hd, tH, tOffB, 14); c.cue(tH, 'card');
    const tDef = s[5].start + 0.1, tOffDef = s[7].start;
    const df = paper(c, 480, 414, 560, 262, { kicker: 'DEFINITION · 怎么算' });
    tx(c, df, 36, 46, '50% 任务时间跨度', '900 34px var(--cjk)', { lh: 48 });
    const dItem = (y, n, html, at) => { const e = c.div('', 36, y, 490, 44, '', df); badge(c, e, 0, 2, n, 38, 20); tx(c, e, 54, 0, html, '700 26px var(--cjk)', { lh: 42 }); c.show(e, at, null, 6); c.cue(at, 'item'); };
    dItem(112, 1, '找出 AI 成功率 50% 的任务', tDef);
    const dArr = c.arrow(55, 162, 55, 196, '#FF4F1A', { w: 4, head: 11, parent: df });
    c.T(dArr, { o: 0 }).to(c.P(s[5], '人类专家', 0.5) - 0.2, { o: 1 }, 0.3);
    dItem(202, 2, '人类专家完成它要多久', c.P(s[5], '人类专家', 0.5));
    c.show(df, tDef, tOffDef, 14);
    // 注意事项（S06-46）
    const tN = s[7].start + 0.1;
    const nt = paper(c, 480, 414, 560, 262, { kicker: 'NOTE · 注意' });
    const nItem = (y, html, at) => {
      const e = c.div('', 36, y, 500, 44, '', nt);
      const b = c.div('', 0, 3, 36, 36, '!', e);
      Object.assign(b.style, { borderRadius: '50%', background: 'var(--orange)', color: 'var(--paper)', font: '900 24px var(--cjk)', textAlign: 'center', lineHeight: '36px' });
      tx(c, e, 52, 0, html, '700 26px var(--cjk)', { lh: 42 });
      c.show(e, at, null, 6); c.cue(at, 'item');
    };
    nItem(58, '人类耗时 ≠ AI 连续工作时长', c.P(s[7], '人类要花的时间', 0.4));
    nItem(120, '50% 成功率', c.P(s[7], '不代表', 0.5) + 0.9);
    nItem(182, '以软件类任务为主', c.P(s[7], '软件类任务', 0.8) - 0.2);
    c.show(nt, tN, tOffB, 14);
    // METR 图（对数纵轴）
    const tCh = s[6].start + 0.08, tG4 = c.P(s[6], 'GPT-4', 0.2), tG4l = c.P(s[6], '4分钟', 0.35), t26 = c.P(s[6], '2026年', 0.6), tTop = c.P(s[6], '十几个小时', 0.9);
    const mc = paper(c, 1060, 196, 780, 634, { kicker: 'METR · 50% 任务时间跨度', shiyi: true });
    tx(c, mc, 36, 46, 'AI 有一半把握做完的任务，人类要做多久', '800 27px var(--cjk)', { lh: 40 });
    tx(c, mc, 36, 88, '纵轴：人类专家需要的时间（不是 AI 连续工作的时间）', '600 18px var(--cjk)', { color: '#4A4741', lh: 26 });
    tx(c, mc, 36, 114, '主要是软件类任务 · 对数刻度', '600 18px var(--cjk)', { color: '#4A4741', lh: 26 });
    const GX0 = 124, GX1 = 744, GB = 540, GT = 206, LOGMAX = 5.6;
    const yS = sec => GB - Math.log10(sec) / LOGMAX * (GB - GT), xY = yr => GX0 + (yr - 2019) / (2026.7 - 2019) * (GX1 - GX0);
    const seg1 = [[2019.0, 2], [2024.3, 600]], seg2 = [[2024.3, 600], [2026.3, 62640]];   // 示意：2 段斜率（约 7 个月 / 约 3 个月翻倍）
    const lineY = yr => { const [a, b] = yr <= 2024.3 ? seg1 : seg2, f = (yr - a[0]) / (b[0] - a[0]); return yS(Math.pow(10, Math.log10(a[1]) + f * (Math.log10(b[1]) - Math.log10(a[1])))); };
    let ms = '';
    [[1, '1 秒'], [60, '1 分钟'], [600, '10 分钟'], [3600, '1 小时'], [36000, '10 小时']].forEach(([sec, lab]) => {
      ms += `<line x1="${GX0}" y1="${yS(sec).toFixed(1)}" x2="${GX1}" y2="${yS(sec).toFixed(1)}" stroke="#D2CCC1" stroke-width="1.5" ${sec > 1 ? 'stroke-dasharray="5 6"' : ''}/>`;
      tx(c, mc, 20, yS(sec) - 12, lab, '500 17px var(--cjk)', { w: GX0 - 30, align: 'right', color: 'var(--grey)', lh: 24 });
    });
    for (let yr = 2019; yr <= 2026; yr++) tx(c, mc, xY(yr) - 30, GB + 8, String(yr), '500 16px var(--mono)', { w: 60, align: 'center', color: 'var(--grey)' });
    c.svg(0, 0, 780, 634, ms, mc);
    const y16 = yS(16 * 3600);
    const unc = c.div('', GX0, GT - 4, GX1 - GX0, y16 - GT + 4, '', mc);
    Object.assign(unc.style, { border: '2.5px dashed #8A857C', borderRadius: '6px', background: 'rgba(138,133,124,.10)' });
    tx(c, unc, 12, 7, '16 小时以上：测不准', '700 17px var(--cjk)', { color: '#6E6A63', lh: 24 });
    c.show(unc, tTop - 0.3, null, 0);
    const pathOf = sg => sg.map(([yr, sec], i) => `${i ? 'L' : 'M'}${xY(yr).toFixed(1)} ${yS(sec).toFixed(1)}`).join(' ');
    const pg = c.svg(0, 0, 780, 634, `<path class="a" d="${pathOf(seg1)}" fill="none" stroke="#3A3833" stroke-width="5" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>` +
      `<path class="b" d="${pathOf(seg2)}" fill="none" stroke="#FF4F1A" stroke-width="5" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`, mc);
    const pa = pg.querySelector('.a'), pb2 = pg.querySelector('.b');
    c.T(null, { p: 0 }, q => { pa.style.strokeDashoffset = (1 - q.p).toFixed(4); }).to(tCh + 0.3, { p: 1 }, Math.max(0.8, tG4l - tCh - 0.3), E.inOut);
    c.T(null, { p: 0 }, q => { pb2.style.strokeDashoffset = (1 - q.p).toFixed(4); }).to(t26, { p: 1 }, Math.max(0.8, tTop - t26), E.inOut);
    const mdot = (yr, sec, col, at) => { const e = c.div('', xY(yr) - 9, yS(sec) - 9, 18, 18, '', mc); Object.assign(e.style, { borderRadius: '50%', background: 'var(--paper)', border: `4px solid ${col}` }); c.show(e, at, null, 0); return e; };
    mdot(2023.2, 240, '#141414', tG4);
    c.show(tx(c, mc, xY(2023.2) + 30 - 290, yS(240) - 52, 'GPT-4 · 约 4 分钟（2023）', '800 21px var(--cjk)', { w: 290, align: 'right', lh: 30 }), tG4l, null, 6);
    mdot(2026.3, 62640, 'var(--orange)', tTop);
    c.show(tx(c, mc, xY(2026.3) - 22 - 330, GT + 5, '2026 年测到最好：十几小时', '800 21px var(--cjk)', { w: 330, align: 'right', color: 'var(--orange)', lh: 30 }), tTop, null, 6);
    c.cue(tG4, 'item'); c.cue(tTop, 'item');
    const tSlope = tTop + 0.5;
    c.show(tx(c, mc, xY(2020.8), lineY(2020.8) + 14, '约 7 个月翻倍（2019 起）', '700 18px var(--cjk)', { color: '#4A4741', lh: 24 }), tSlope, null, 6);
    c.show(tx(c, mc, xY(2025.0) - 16 - 260, lineY(2025.0) - 32, '约 3 个月翻倍（2024 起）', '700 18px var(--cjk)', { w: 260, align: 'right', color: 'var(--orange)', lh: 24 }), tSlope + 0.2, null, 6);
    tx(c, mc, 36, 590, '数据：METR 2026-05 · 翻倍周期：METR 2025-03 论文 / 2026-01 更新', '500 16px var(--cjk)', { color: 'var(--grey)' });
    c.show(mc, tCh, tOffB, 14); c.cue(tCh, 'chart');

    // ---- (c) 四个阶段（放大）：交叠着往前走；「文字接龙」只罩住第一条
    const tZ = s[8].start + 0.05;
    const Z = bandChart(c.root, ZOOM);
    const zt = bandTracks(Z, (e, i, f) => c.T(e, i, f));
    setBands(zt, tZ - 0.3, [0.5, 0.5, 0.5, 1], [0, 0, 0, 1], 0);
    setBands(zt, tZ + 0.55, [1, 1, 1, 1], [0, 0, 0, 0], 0.45);
    c.T(Z.el, Object.assign({ o: 0 }, poseOf(ZOOM, DOCK))).to(tZ, { o: 1, x: 0, y: 0, s: 1 }, 0.7, E.inOut);
    c.cue(tZ + 0.3, 'chart');
    const zx = yr => ZOOM.x + Z.yx(yr), zy = i => ZOOM.y + Z.ry(i), bh = ZOOM.bh;
    const zdot = (yr, i, at) => { const e = c.div('', zx(yr) - 9, zy(i) + bh / 2 - 9, 18, 18, ''); Object.assign(e.style, { borderRadius: '50%', background: 'var(--paper)', border: '3.5px solid var(--ink)' }); c.show(e, at, null, 0); return e; };
    const zlab = (x, y, html, at, o = {}) => c.label(html, x, y, Object.assign({ size: 18, at }, o));
    const tFnO1 = P('S06-47', '函数调用比o1', 0.2) + 0.3, tOver = P('S06-47', '交叠', 0.7);
    // 交叠 ②：函数调用 2023-06 早于 o1 2024-09（第 3、4 条）
    c.show(hatch(c, zx(2023.45), zy(2) - 7, zx(2024.70) - zx(2023.45), zy(3) + bh + 7 - (zy(2) - 7)), tFnO1, null, 0);
    zdot(2023.45, 3, tFnO1); zdot(2024.70, 2, tFnO1);
    zlab(zx(2023.45) - 6, zy(3) + bh + 6, '函数调用', tFnO1);
    zlab(zx(2024.70) + 14, zy(2) + bh + 6, 'o1', tFnO1);
    const co2 = c.div('callout', 842, zy(3) - 4, null, null, '函数调用 2023-06<br><span class="s">早于 o1 2024-09</span>');
    c.show(co2, tFnO1 + 0.15, null, 6);
    const l2 = c.arrow(842 + co2.offsetWidth + 6, zy(3) + bh / 2, zx(2023.45) - 12, zy(3) + bh / 2, '#FF4F1A', { w: 3.5, head: 11 });
    c.T(l2, { o: 0 }).to(tFnO1 + 0.25, { o: 1 }, 0.3);
    // 交叠 ①：思维链提示 2022-01 早于 ChatGPT 2022-11（第 2、3 条）
    c.show(hatch(c, zx(2022.08), zy(1) - 7, zx(2022.91) - zx(2022.08), zy(2) + bh + 7 - (zy(1) - 7)), tOver, null, 0);
    zdot(2022.91, 1, tOver); zdot(2022.08, 2, tOver);
    zlab(zx(2022.91) + 14, zy(1) + bh + 6, 'ChatGPT', tOver);
    zlab(zx(2022.08) - 6, zy(2) + bh + 6, '思维链提示', tOver);
    const co1 = c.div('callout', 842, zy(1) - 4, null, null, '思维链提示 2022-01<br><span class="s">早于 ChatGPT 2022-11</span>');
    c.show(co1, tOver + 0.15, null, 6);
    const l1 = c.arrow(842 + co1.offsetWidth + 6, zy(1) + bh / 2 + 8, zx(2022.08) - 12, zy(1) + bh / 2 + 8, '#FF4F1A', { w: 3.5, head: 11 });
    c.T(l1, { o: 0 }).to(tOver + 0.25, { o: 1 }, 0.3);
    c.label('交叠着往前走', ZOOM.x + ZOOM.w - 330, ZOOM.y + 12, { w: 300, align: 'right', size: 26, kind: 'o', at: tOver });
    // 「做事」色带上的两个小标记（只上屏）
    const tMk = tOver + 0.7;
    zdot(2024.90, 3, tMk); zdot(2025.20, 3, tMk + 0.2);
    zlab(zx(2024.90) - 8, zy(3) + bh + 6, '2024-11 MCP 工具接入开放标准', tMk, { size: 16 });
    zlab(zx(2025.20) - 8, zy(3) + bh + 28, '2025 编程智能体陆续发布', tMk + 0.2, { size: 16 });
    // S06-48：开场的聊天气泡回来；「文字接龙」四个字只罩住第一条色带
    const tBub = s[9].start + 0.1, tCover = P('S06-48', '文字接龙', 0.5), tCap = P('S06-48', '只是预训练的目标', 0.5);
    bubble(c, { x: 492, y: 188, text: 'AI 不就是<span class="or">文字接龙</span>吗？', size: 34, at: tBub });
    const cover = c.div('', zx(STAGES[0].start) - 8, zy(0) - 7, ZOOM.x + Z.x1 - zx(STAGES[0].start) + 16, bh + 14, '文字接龙');
    Object.assign(cover.style, { border: '3px solid var(--orange)', background: 'rgba(255,79,26,.3)', borderRadius: '27px', font: '900 30px var(--cjk)', color: 'var(--ink)', textAlign: 'center', lineHeight: (bh + 8) + 'px', letterSpacing: '.3em' });
    c.show(cover, tCover, null, 0);
    const cl = c.arrow(930, 236, 1010, zy(0) - 10, '#FF4F1A', { w: 3, dash: '6 6', head: 10 });
    c.T(cl, { o: 0 }).to(tCover, { o: 1 }, 0.3);
    setBands(zt, tCover, [1, 0.35, 0.35, 0.35], [0, 0, 0, 0], 0.4);
    c.show(tx(c, null, 960, 200, '<span class="or">＝</span> 预训练的目标 <span class="or">＋</span> 输出的方式', '800 30px var(--cjk)', { color: 'var(--paper)', lh: 44 }), tCap, null, 8);
    c.cue(tCover, 'item'); c.cue(tCap, 'item');
  });

  // ================================================================== S07 五、AGI 到了吗
  ENG.scene('S07', c => {
    const s = c.segs();                                   // s[0] S07-49 … s[15] S07-64
    const tM = P('S07-49', '全称', 0.5) - 0.12;
    c.autoTitle(s[0], { morph: tM });
    const tP3 = s[6].start;                               // 「那现在实现了吗」：定义卡收到右侧边栏
    // ---- (a) Artificial General Intelligence · 通用人工智能 · 没有统一定义
    const words = [['A', 'rtificial', 'Artificial'], ['G', 'eneral', 'General'], ['I', 'ntelligence', 'Intelligence']];
    const wr = c.div('', 480, 196, 1360, 80, '');
    Object.assign(wr.style, { textAlign: 'center', whiteSpace: 'nowrap', font: '700 56px var(--mono)', lineHeight: '80px', color: 'var(--paper)' });
    words.forEach(([a, b, ph], i) => {
      const sp = ENG.el('span', '', wr, `<span class="or">${a}</span>${b}`);
      sp.style.display = 'inline-block'; if (i < 2) sp.style.marginRight = '.5em';
      c.T(sp, { o: 0, y: 10 }).in(P('S07-49', ph, 0.3 + 0.2 * i), 0.3);
    });
    c.cue(P('S07-49', 'Artificial', 0.3), 'word');
    const zh = tx(c, null, 480, 284, '通用人工智能', '900 44px var(--cjk)', { w: 1360, align: 'center', lh: 60 });
    c.show(zh, c.P(s[1], '通用人工智能', 0.2), tP3, 8);
    const noDef = c.chip('没有统一定义', 1336, 290, { kind: 'line', size: 24, h: 46, at: c.P(s[1], '没有统一定义', 0.5), until: tP3 });
    c.T(wr, { o: 1 }).out(tP3);
    // ---- (b) 三种定义卡
    const DX = [480, 940, 1400], DY = 384, DW = 440, DH = 446;
    const tEmpty = c.P(s[1], '常见的有三种', 0.4);
    const heads = ['看工作', '分等级', '看学习效率'];
    const fillAt = [c.P(s[2], '第一种', 0.05), c.P(s[3], '第二种', 0.05), c.P(s[5], '第三种', 0.05)];
    const phs = DX.map((x, i) => {
      const e = c.div('', x, DY, DW, DH, '');
      Object.assign(e.style, { border: '2.5px dashed rgba(237,234,227,.5)', borderRadius: '8px', background: 'rgba(20,20,20,.35)' });
      tx(c, e, 0, 180, `定义 <span class="mono">${'①②③'[i]}</span>`, '800 36px var(--cjk)', { w: DW, align: 'center', color: 'rgba(237,234,227,.6)' });
      c.T(e, { o: 0, y: 10 }).in(tEmpty + 0.15 * i, 0.35).to(fillAt[i] + 0.3, { o: 0 }, 0.3);
      return e;
    });
    c.cue(tEmpty, 'card');
    const dcards = DX.map((x, i) => {
      const cd = c.card(x, DY, DW, DH);
      cd.style.transformOrigin = '0 0';
      badge(c, cd, 24, 22, i + 1, 46, 24);
      tx(c, cd, 84, 22, heads[i], '900 34px var(--cjk)', { lh: 46 });
      const tr = c.T(cd, { o: 0, y: 14 }).in(fillAt[i], 0.4);
      c.cue(fillAt[i], 'card');
      return { cd, tr };
    });
    // ① 看工作：OpenAI 章程（2018）
    const c1 = dcards[0].cd;
    tx(c, c1, 24, 84, 'OpenAI 章程 · 2018', '700 20px var(--cjk)', { color: 'var(--grey)' });
    const q1 = tx(c, c1, 24, 120, '“在大多数有经济价值的工作上，胜过人类的高度自主系统”', '800 27px var(--cjk)', { w: DW - 48, wrap: true, lh: 40 });
    const q1e = tx(c, c1, 24, 262, 'highly autonomous systems that outperform humans at most economically valuable work', '500 16px var(--mono)', { w: DW - 48, wrap: true, lh: 23, color: 'var(--grey)' });
    c.show(q1, c.P(s[2], '经济价值', 0.6) - 0.8, null, 6);
    c.show(q1e, c.P(s[2], '经济价值', 0.6) - 0.2, null, 6);
    // ② 分等级：Google DeepMind 0–5 级，1 级「初现」
    const c2 = dcards[1].cd;
    tx(c, c2, 24, 84, 'Google DeepMind《Levels of AGI》· 2023-11', '600 16px var(--cjk)', { color: 'var(--grey)' });
    const lad = c.div('', 22, 110, 396, 238, '', c2);
    const lvName = ['无 AI', '初现', '胜任', '专家', '卓越', '超人'];
    const tLad = c.P(s[3], '0到5级', 0.6) - 0.2, tLv1 = c.P(s[4], '只到1级', 0.55), tChat = c.P(s[4], '2023年', 0.2), tEm = c.P(s[4], '没受过训练', 0.6);
    const steps = lvName.map((nm, i) => {
      const w = 60, hgt = 70 + i * 33, x = i * 66, y = 238 - hgt;
      const st = c.div('', x, y, w, hgt, '', lad);
      Object.assign(st.style, { background: '#3A3833', borderRadius: '6px 6px 0 0' });
      tx(c, st, 0, 6, String(i), '800 24px var(--mono)', { w, align: 'center', color: 'var(--paper)', lh: 28 });
      tx(c, st, 0, 36, nm, '700 17px var(--cjk)', { w, align: 'center', color: 'rgba(237,234,227,.9)', lh: 24 });
      c.show(st, tLad + 0.08 * i, null, 6);
      return st;
    });
    c.T(null, { w: 0 }, p => { steps[1].style.background = p.w > 0.5 ? 'var(--orange)' : '#3A3833'; }).to(tLv1, { w: 1 }, 0.1);
    c.cue(tLv1, 'item');
    c.show(tx(c, c2, 66 + 22, 354, '<span class="or">↑</span> 2023 年的聊天模型', '800 19px var(--cjk)', { lh: 26 }), Math.max(tChat, tLad + 0.6), null, 6);
    c.show(tx(c, c2, 24, 392, '初现 Emerging：等于或略好于没受过训练的人', '600 17px var(--cjk)', { w: DW - 48, wrap: true, lh: 24, color: '#4A4741' }), tEm, null, 6);
    // ③ 看学习效率：肖莱 2019
    const c3 = dcards[2].cd;
    tx(c, c3, 24, 88, 'François Chollet', '800 26px var(--cjk)', { lh: 36 });
    tx(c, c3, 24, 126, '肖莱 · AI 研究者', '600 19px var(--cjk)', { color: 'var(--grey)' });
    tx(c, c3, 24, 158, '2019《On the Measure of Intelligence》', '600 17px var(--cjk)', { color: 'var(--grey)' });
    c.div('dash', 24, 200, DW - 48, null, '', c3);
    const iq = c.div('', 24, 222, DW - 48, 150, '', c3);
    tx(c, iq, 0, 0, '智能 ＝', '800 30px var(--cjk)', { lh: 44 });
    tx(c, iq, 0, 48, '技能获取效率', '900 50px var(--cjk)', { lh: 64, color: 'var(--orange)' });
    tx(c, iq, 0, 116, '学会新技能有多快', '600 21px var(--cjk)', { color: 'var(--grey)' });
    c.show(iq, c.P(s[5], '智能', 0.5) - 0.1, null, 8);
    c.cue(c.P(s[5], '智能', 0.5), 'item');
    // ---- (c) 那现在实现了吗？ 三张定义卡收进右侧边栏 · 截至 2026-09
    const SBX = 1622, SBW = 218;
    dcards.forEach(({ tr }, i) => tr.to(tP3, { x: SBX - DX[i], y: 252 + i * 66 - DY, s: SBW / DW, o: 0 }, 0.6, E.inOut));
    c.chip('截至 2026-09', SBX, 196, { kind: 'line', size: 22, h: 42, w: SBW, center: true, at: tP3 + 0.3, until: s[15].start });
    const tabs = heads.map((h, i) => {
      const e = c.div('chip', SBX, 252 + i * 66, SBW, 54, `<span class="mono or" style="margin-right:8px">${'①②③'[i]}</span>${h}`);
      e.style.fontSize = '22px';
      c.show(e, tP3 + 0.4 + 0.1 * i, s[15].start, 6);
      return e;
    });
    const colT = (x, text, at, until) => c.show(tx(c, null, x, 192, `<span style="display:inline-block;width:14px;height:14px;background:var(--orange);margin-right:12px;vertical-align:4px"></span>${text}`, '900 38px var(--cjk)', { lh: 52 }), at, until, 8);
    colT(480, '说到了', c.P(s[6], '有人说到了', 0.3), s[15].start);
    // 引语卡：只用文字，不放照片；写清是个人表态 / 主持人给的标准
    const quote = (y, h, who, when, en, zhq, at, until) => {
      const cd = c.card(480, y, 580, h);
      tx(c, cd, 28, 20, who, '800 21px var(--cjk)', { lh: 30 });
      tx(c, cd, 28, 52, when, '500 17px var(--cjk)', { color: 'var(--grey)', lh: 24 });
      const qe = tx(c, cd, 28, 86, en, '800 32px var(--cjk)', { lh: 44 });
      const qz = tx(c, cd, 28, 132, zhq, '700 23px var(--cjk)', { color: '#4A4741', lh: 32 });
      const tr = c.show(cd, at, until, 14);
      c.cue(at, 'card');
      return { cd, tr, qe, qz };
    };
    const tQ1 = s[7].start + 0.1, tQ1q = c.P(s[7], '欢迎来到', 0.5) - 0.25;
    const Q1 = quote(256, 268, 'Greg Brockman · OpenAI 总裁', '布罗克曼 · 2026-09-03 GPT-6 Astra 发布时的媒体简报', '“Welcome to the AGI era.”', '“欢迎来到 AGI 时代。”', tQ1, s[15].start);
    c.T(Q1.qe, { o: 0 }).to(tQ1q, { o: 1 }, 0.3); c.T(Q1.qz, { o: 0 }).to(tQ1q + 0.2, { o: 1 }, 0.3);
    c.show(tx(c, Q1.cd, 28, 172, '他也说：每个人对 AGI 的定义都不同', '500 18px var(--cjk)', { color: 'var(--grey)' }), tQ1q + 0.9, null, 6);
    const tPer = c.P(s[8], '个人表态', 0.3) - 0.1, tNo = c.P(s[8], '没有正式宣布', 0.6) - 0.2;
    c.show(tagp(c, Q1.cd, '个人表态', null, 18, { right: 22, size: 19 }), tPer, null, 4);
    const off1 = c.div('', 28, 210, 524, 40, '', Q1.cd);
    Object.assign(off1.style, { borderLeft: '4px solid var(--ink)', paddingLeft: '12px', font: '800 22px var(--cjk)', lineHeight: '40px', whiteSpace: 'nowrap' });
    off1.textContent = 'OpenAI 官方：未正式宣布实现 AGI';
    c.show(off1, tNo, null, 6); c.cue(tNo, 'item');
    const tQ2 = s[9].start + 0.1, tStd = c.P(s[9], '主持人', 0.4);
    const Q2 = quote(544, 286, '黄仁勋 · 英伟达 CEO', '2026-03 · 播客访谈', '“I think we\'ve achieved AGI.”', '“我认为我们已经实现了 AGI。”', tQ2, s[15].start);
    c.show(tagp(c, Q2.cd, '个人表态', null, 18, { right: 22, size: 19 }), tQ2 + 0.3, null, 4);
    const std = c.div('', 28, 176, 524, 96, '', Q2.cd);
    tx(c, std, 0, 0, '用的是主持人提的标准：', '600 17px var(--cjk)', { color: 'var(--grey)', lh: 24 });
    tx(c, std, 0, 26, 'AI 能创办并运营一家市值超 10 亿美元的公司', '800 21px var(--cjk)', { lh: 32 });
    tx(c, std, 0, 62, '黄仁勋补充：不必长久', '500 17px var(--cjk)', { color: 'var(--grey)', lh: 24 });
    c.show(std, tStd, null, 6); c.cue(tStd, 'item');
    // ---- (d) 不认同：ARC Prize 按第三种定义出题 → ARC-AGI-3 → 成绩 → “我们没说它就是 AGI”
    const tNo2 = c.P(s[10], '不认同', 0.3), tArc = c.P(s[10], 'ARC Prize', 0.5), tDef3 = c.P(s[10], '第三种定义', 0.6);
    [Q1.tr, Q2.tr].forEach(tr => tr.to(tNo2, { o: 0.62 }, 0.4));
    colT(1090, '不认同', tNo2, s[15].start);
    const an = c.div('', 1090, 250, 510, 74, '', c.root);
    tx(c, an, 0, 0, 'ARC Prize：按定义 <span class="mono or">③</span> 出题', '800 22px var(--cjk)', { lh: 32 });
    tx(c, an, 0, 34, 'ARC = Abstraction and Reasoning Corpus（抽象与推理语料库），肖莱 2019 年提出', '500 15px var(--cjk)', { w: 500, wrap: true, lh: 20, color: 'rgba(237,234,227,.78)' });
    c.show(an, tArc, s[15].start, 6);
    c.ring(SBX, 252 + 2 * 66, SBW, 54, tDef3, tDef3 + 1.6);
    const tGame = s[11].start + 0.1, tRule = c.P(s[11], '摸索规则', 0.6), tScore = s[12].start + 0.1;
    const gm = paper(c, 1090, 334, 500, 250, { kicker: 'ARC-AGI-3 · 2026-03', shiyi: true });
    tx(c, gm, 32, 44, '没有说明的新游戏', '900 30px var(--cjk)', { lh: 42 });
    tx(c, gm, 32, 90, '要自己摸索规则', '700 22px var(--cjk)', { color: '#4A4741', lh: 32 });
    const grid = c.div('', 300, 60, 168, 168, '', gm);
    const GC = ['#E4DFD5', '#4A6FD0', '#F6C945', '#E2463F', '#3A3833'];
    const cells = [0,0,1,1,0,0,0,0, 0,4,1,0,0,2,2,0, 0,4,0,0,0,2,0,0, 0,4,4,0,0,0,0,0, 0,0,0,0,3,3,0,0, 0,1,0,0,3,0,0,4, 0,1,1,0,0,0,0,4, 0,0,0,0,0,0,4,4];
    grid.innerHTML = cells.map((k, i) => `<div style="position:absolute;left:${(i % 8) * 21}px;top:${Math.floor(i / 8) * 21}px;width:19px;height:19px;border-radius:2px;background:${GC[k]}"></div>`).join('');
    const rq = tx(c, gm, 32, 150, '规则？', '900 44px var(--cjk)', { color: 'var(--orange)', lh: 56 });
    c.show(rq, tRule, null, 6);
    c.show(gm, tGame, tScore, 14); c.cue(tGame, 'card');
    // 成绩卡（ARC Prize 官方数据，示意）：前沿 AI <1% · 人类 100% · Astra 62.7%（标准测法）与 99.9%（厂商适配框架）并排
    const sc = paper(c, 1090, 334, 500, 352, { kicker: 'ARC-AGI-3 · 成绩', shiyi: true });
    tx(c, sc, 250, 19, '数据：ARC Prize 官方', '600 15px var(--cjk)', { color: 'var(--grey)' });
    const BB = 214, BH = 120;
    const t1p = c.P(s[12], '不到1%', 0.6), t627 = c.P(s[13], '标准测法', 0.3), t627v = c.P(s[13], '62.7%', 0.8);
    const barsA = [
      { x: 30, pct: 0.8, val: '<1%', n1: '前沿 AI', n2: '2026-03', col: '#3A3833', at: t1p },
      { x: 130, pct: 100, val: '100%', n1: '人类', n2: '', col: '#9A958C', at: tScore + 0.35 },
      { x: 262, pct: 62.7, val: '62.7%', n1: '标准测法', n2: '', col: 'var(--orange)', at: t627, vat: t627v },
      { x: 362, pct: 99.9, val: '99.9%', n1: '厂商适配', n2: '框架', col: 'repeating-linear-gradient(135deg, #FFB08F 0 6px, #FFD2BD 6px 12px)', at: t627v + 0.4 },
    ];
    barsA.forEach(b => {
      const hgt = Math.max(3, BH * b.pct / 100);
      const e = c.div('', b.x, BB - hgt, 84, hgt, '', sc);
      Object.assign(e.style, { background: b.col, borderRadius: '3px 3px 0 0', transformOrigin: '50% 100%', transform: 'scaleY(0)' });
      c.T(null, { g: 0 }, p => { e.style.transform = `scaleY(${p.g.toFixed(3)})`; }).to(b.at, { g: 1 }, 0.55);
      c.show(tx(c, sc, b.x - 20, BB - hgt - 34, b.val, '800 24px var(--mono)', { w: 124, align: 'center', lh: 30, color: b.col === 'var(--orange)' ? 'var(--orange)' : 'var(--ink)' }), b.vat || b.at + 0.2, null, 4);
      c.show(tx(c, sc, b.x - 20, BB + 6, b.n1 + (b.n2 ? '<br>' + b.n2 : ''), '700 16px var(--cjk)', { w: 124, align: 'center', lh: 20 }), b.at, null, 4);
      c.cue(b.at, 'item');
    });
    c.svg(20, BB, 460, 4, '<line x1="0" y1="1" x2="460" y2="1" stroke="#3A3833" stroke-width="2"/>', sc);
    c.bracket(254, BB + 48, 200, 'GPT-6 Astra · 2026-09', { at: t627, parent: sc, size: 16 });
    const arcN = tx(c, sc, 30, BB + 104, 'ARC Prize：适配框架保留推理状态，成绩算“模型 + 工具”', '600 16px var(--cjk)', { color: '#4A4741', lh: 22 });
    c.show(arcN, t627v + 0.9, null, 6);
    c.show(sc, tScore, s[15].start, 14); c.cue(tScore, 'card');
    const tArcQ = s[14].start + 0.1;
    const aq = c.card(1090, 700, 500, 160);
    tx(c, aq, 26, 16, '“we are not claiming that it is AGI”', '700 20px var(--cjk)', { color: '#4A4741', lh: 28 });
    tx(c, aq, 26, 48, '我们没说它就是 AGI', '900 32px var(--cjk)', { lh: 44 });
    tx(c, aq, 26, 96, '— ARC Prize · 2026-09 · 对 GPT-6 Astra 的分析', '500 16px var(--cjk)', { color: 'var(--grey)', lh: 22 });
    tx(c, aq, 26, 122, '理由之一：测试规则固定、目标封闭，不代表真实世界', '500 16px var(--cjk)', { color: 'var(--grey)', lh: 22 });
    c.show(aq, tArcQ, s[15].start, 12); c.cue(tArcQ, 'card');
    // ---- (e) 结论卡：截至 2026-09，正式宣布 ✕ 独立认证 ✕ 共识 ✕
    const tC = s[15].start + 0.15;
    const cc = paper(c, 600, 264, 1100, 430, { kicker: 'CONCLUSION · 截至 2026-09' });
    tx(c, cc, 40, 48, '实现 AGI 这件事', '900 46px var(--cjk)', { lh: 62 });
    [['正式宣布', '没有哪家公司正式宣布', c.P(s[15], '正式宣布', 0.4)], ['独立认证', '没有独立机构认证', c.P(s[15], '独立认证', 0.6)], ['共识', '也没有共识', c.P(s[15], '共识', 0.9)]].forEach(([a, b, at], i) => {
      const cell = c.div('', 40 + i * 346, 140, 326, 170, '', cc);
      Object.assign(cell.style, { background: '#E4DFD5', borderRadius: '10px' });
      c.svg(24, 24, 48, 48, ICON.x('#3A3833'), cell);
      tx(c, cell, 90, 26, a, '900 36px var(--cjk)', { lh: 44 });
      tx(c, cell, 24, 104, b, '600 20px var(--cjk)', { color: '#4A4741', lh: 28 });
      c.show(cell, at, null, 8); c.cue(at, 'item');
    });
    c.show(tx(c, cc, 40, 340, '也有学者认为已具备通用智能（《Nature》评论，2026-02），有争议', '500 19px var(--cjk)', { color: 'var(--grey)' }), c.P(s[15], '独立认证', 0.6) + 0.5, null, 6);
    c.show(cc, tC, null, 14); c.cue(tC, 'card');
  });

  // ================================================================== S08 六、还差什么
  ENG.scene('S08', c => {
    const s = c.segs();                                   // s[0] S08-65 … s[6] S08-71
    const tM = P('S08-65', '四点', 0.8) - 0.35;
    c.autoTitle(s[0], { morph: tM });
    const tSlots = tM + 0.35;
    c.chip('观点 · 均有出处', 1640, 186, { kind: 'line', size: 19, h: 36, w: 200, center: true, at: tSlots });
    const CX = [480, 1180], CY = [232, 548], CW = 660, CH = 290;
    const info = [
      { n: 1, title: '持续学习', at: c.P(s[1], '第一', 0.05), src: 'Demis Hassabis（Google DeepMind CEO）2026-02 · Andrej Karpathy 2025-10' },
      { n: 2, title: '可靠性', at: c.P(s[2], '第二', 0.05), src: 'METR 2026-05 ·《国际 AI 安全报告 2026》' },
      { n: 3, title: '开放的真实任务', at: c.P(s[4], '第三', 0.05), src: 'METR 时间跨度页 FAQ' },
      { n: 4, title: '物理世界', at: c.P(s[5], '第四', 0.05), src: 'Yann LeCun（杨立昆）2026-01 · 原话：缺少世界模型（world model）' },
    ];
    const cells = info.map((it, i) => {
      const x = CX[i % 2], y = CY[Math.floor(i / 2)];
      const ph = c.div('', x, y, CW, CH, '');
      Object.assign(ph.style, { border: '2.5px dashed rgba(237,234,227,.45)', borderRadius: '8px', background: 'rgba(20,20,20,.3)' });
      tx(c, ph, 0, 110, `<span class="mono">${'①②③④'[i]}</span>`, '800 50px var(--cjk)', { w: CW, align: 'center', color: 'rgba(237,234,227,.55)' });
      c.T(ph, { o: 0, y: 10 }).in(tSlots + 0.1 * i, 0.35).to(it.at + 0.3, { o: 0 }, 0.3);
      const cd = c.card(x, y, CW, CH);
      badge(c, cd, 30, 26, it.n, 52, 28);
      tx(c, cd, 100, 24, it.title, '900 40px var(--cjk)', { lh: 56 });
      tx(c, cd, 30, CH - 44, it.src, '500 16px var(--cjk)', { color: 'var(--grey)', lh: 22 });
      c.show(cd, it.at, null, 12); c.cue(it.at, 'card');
      return cd;
    });
    c.cue(tSlots, 'card');
    tx(c, cells[0], 30, 100, '模型训练完，参数就固定了；<br>用的时候学到的东西，留不下来', '700 25px var(--cjk)', { lh: 40 });
    // ② 可靠性：按十次做对八次算 → 人类约 3 小时；另外会编造信息
    const c2 = cells[1];
    tx(c, c2, 30, 90, '按“十次做对八次”算，测过的最好模型<span style="font:500 16px var(--cjk);color:var(--grey);margin-left:12px">人类耗时 · 示意</span>', '700 23px var(--cjk)', { lh: 34 });
    const bars = [['50% 把握', 1.0, '十几小时', '#9A958C'], ['80% 把握', 3.1 / 17.4, '约 3 小时', 'var(--orange)']];
    const tB = c.P(s[2], '十次做对八次', 0.4), tB3 = c.P(s[2], '约3小时', 0.6);
    bars.forEach(([lab, f, val, col], i) => {
      const r = c.div('', 30, 130 + i * 36, 600, 32, '', c2);
      tx(c, r, 0, 0, lab, '700 18px var(--cjk)', { lh: 32, color: '#4A4741' });
      const bw = Math.round(330 * f);
      const b = c.div('', 96, 7, bw, 18, '', r);
      Object.assign(b.style, { background: col, borderRadius: '3px' });
      tx(c, r, 108 + bw, 0, val, '800 20px var(--cjk)', { lh: 32, color: i ? 'var(--orange)' : 'var(--ink)' });
      c.show(r, i ? tB3 : tB, null, 4);
    });
    const lie = tx(c, c2, 30, 204, '<span class="or">＋</span> 还会编造信息', '800 24px var(--cjk)', { lh: 34 });
    c.show(lie, c.P(s[3], '编造信息', 0.3) - 0.1, null, 6); c.cue(c.P(s[3], '编造信息', 0.3), 'item');
    tx(c, cells[2], 30, 100, '实际工作比测试题乱，<br>也没有标准答案，AI 做得更差', '700 25px var(--cjk)', { lh: 40 });
    tx(c, cells[3], 30, 100, '只学文字的模型，<br>不懂真实世界怎么运转', '700 25px var(--cjk)', { lh: 40 });
    // AGI 到没到，看定义；能确定的是：任务越来越长 ↑
    const tUp = c.P(s[6], '越来越长', 0.5);
    const up = c.chip(`<svg width="24" height="24" viewBox="0 0 24 24" style="vertical-align:-4px;margin-right:8px"><path d="M4 18 L12 8 L20 18" fill="none" stroke="#EDEAE3" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg>AI 能完成的任务越来越长`, 980, 180, { kind: 'o', size: 24, h: 44, at: tUp - 0.4 });
    c.cue(tUp - 0.4, 'item');
  });

  // ================================================================== S09 总结
  ENG.scene('S09', c => {
    const s = c.segs();                                   // s[0] S09-72 … s[5] S09-77
    const X = 480, Y = 190, W = 1070, rowH = 110;
    const card = c.card(X, Y, W, 150 + 3 * rowH + 14);
    c.div('kicker', 44, 24, 600, null, `SUMMARY · 原LAI如此 #${ENG.pad2(ENG.EP.number)}`, card);
    tx(c, card, 44, 50, '本期总结', '900 50px var(--cjk)', { lh: 66 });
    const dbl = c.div('', 44, 126, W - 88, 7, '', card);
    dbl.style.background = 'linear-gradient(var(--ink),var(--ink)) 0 0/100% 3px no-repeat, linear-gradient(var(--ink),var(--ink)) 0 100%/100% 1.5px no-repeat';
    c.show(card, s[0].start + 0.1, null, 14); c.cue(s[0].start + 0.1, 'summary');
    const dot = col => `<span style="display:inline-block;width:14px;height:14px;border-radius:3px;background:${col};margin:0 8px 0 2px;vertical-align:3px"></span>`;
    const R = [
      ['预训练 ＝ 预测下一个词，但不只想下一个词', '“文字接龙”只说对了一半'],
      [`${dot('#F6C945')}对话 ← 人的反馈<span class="gy" style="margin:0 12px">｜</span>${dot('#4A6FD0')}思考 ← 答案对错<span class="gy" style="margin:0 12px">｜</span>${dot('#E2463F')}做事 ← 工具`, '接龙之后，又加了三个阶段'],
      ['<span class="or">AGI</span>：没有统一定义', '截至 2026-09：没有公司正式宣布实现，也没有共识'],
    ];
    R.forEach(([a, b], i) => {
      const r = c.div('', 44, 150 + i * rowH, W - 88, rowH - 8, '', card);
      badge(c, r, 0, 10, i + 1, 52, 28);
      tx(c, r, 76, 2, a, '800 32px var(--cjk)', { lh: 46 });
      tx(c, r, 76, 50, esc(b), '500 22px var(--cjk)', { color: '#5A564F', lh: 32 });
      if (i < R.length - 1) c.div('dash', 0, rowH - 14, W - 88, null, '', r);
      const at = s[1 + i].start + 0.1;
      c.show(r, at, null, 10); c.cue(at, 'summary');
    });
    // 旁边：缩小版色带图（「训练目标」清单一直在右下角）
    const mini = bandChart(c.root, MINI9);
    const mt = bandTracks(mini, (e, i, f) => c.T(e, i, f));
    const tMini = s[2].start + 0.4;
    setBands(mt, tMini + 0.2, [1, 1, 1, 1], [0, 0, 0, 0], 0.4);
    c.show(mini.el, tMini, null, 8);
    // 下次再听到“AI 不就是文字接龙”，你可以说：对了一半。
    const tQ = s[4].start + 0.12, tA = c.P(s[4], '对了一半', 0.6) - 0.1;
    bubble(c, { x: 520, y: 704, text: 'AI 不就是<span class="or">文字接龙</span>吗？', size: 32, at: tQ });
    bubble(c, { x: 870, y: 790, text: '对了一半。', size: 32, me: true, at: tA });
    c.label('示意 · 虚构对话', 940, 722, { size: 18, kind: 's', at: tQ + 0.3 });
    const sig = tx(c, null, 1150, 842, `原LAI如此 <span class="mono or">#${ENG.pad2(ENG.EP.number)}</span> · 下期见`, '700 26px var(--cjk)', { w: 400, align: 'right', color: 'rgba(237,234,227,.88)' });
    c.show(sig, s[5].start + 0.2, null, 6);
  });
})();
