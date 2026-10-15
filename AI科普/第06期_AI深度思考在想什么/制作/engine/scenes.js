/* 《原LAI如此》第 6 期「点了“深度思考”，AI那几十秒到底在想什么？」— 白板手写版 scenes.js（2026-09-30，v4：按用户口述稿重排）
 *
 * 依据：台本/script_data.py 的画面说明；写法照 references/visuals.md「白板版」和引擎模板里的 scenes.board_example.js。
 * 时间：全部按声音写（段号 / 台词短语，c.P），画面整体提前 ENG.LEAD 秒由引擎做。同一章里翻页用 FL(c, 这一页最后一句)（比 c.flip 早 1 秒，见下）：
 *   这一页在 f.out 擦掉，下一页的东西 at 不早于 f.in。录音前按字数估的时长也能跑；录音到了重跑 build_timeline 自动跟上。
 * 坐标：1920×1080 内容舞台，居中版面（ENG.CX = 960）。标题占 y 60–220，内容 y 250–860、x 200–1720
 *   （左下讲解员：舞台 x ≤ 170；底部字幕：y ≥ 906；右上目录：舞台 x ≥ 1748 且 y ≤ 164）。
 * 手写：黑色记号笔写字，黄色波浪线 / 圈重点，橙色编号、打勾、箭头，红色叉；印刷体只留小字（出处、补充，.bNote）和
 *   贴在白板上的示意卡片（聊天窗口、题目卡、论文原句、选择题），卡片贴胶带。
 * 只有一个例子：鸡兔同笼的草稿（S03），标“示意：按官方描述的过程简化，不是某个模型的原始输出”。
 */
(function () {
  'use strict';
  if (!ENG.SCENES.length) return;
  const { E, EP } = ENG;
  const CX = ENG.CX;
  const HC = ENG.HAND || {};
  const ACC = HC.ACCENT || '#FF4F1A', INK = HC.INK || '#1A1A1A', RED = '#D8342A';
  const SOFT = 'rgba(26,26,26,.45)', FAINT = 'rgba(26,26,26,.26)', YEL = 'rgba(245,197,24,.55)';
  const SG = id => ENG.segId(id);
  const T = id => SG(id).start;
  /** 翻页：这一页最后一句是 id -> {out, in}（场景时钟）。照第 5 期（用户 2026-09-30：“让文字比声音的内容提前一秒出现”）：
   *  c.flip 在这一句说完前 0.15 s 擦板，新一页的第一行只比下一句早 0.1 s；这里提前 1 秒翻：画面上在最后一句说完前
   *  1.1 s 擦板、0.8 s 开始写新一页，新一页的第一行比下一句早约 1 s。
   *  early：擦板比这一句说完早几秒（默认 1.1）。这一页最后一句很短、下一页开头不是马上要念的字时用 0.5–0.8，
   *  让这一页最后一行多留一会儿（check_layout 的 hand-short）。 */
  const FL = (c, id, early = 1.1) => { const out = SG(id).end + (ENG.LEAD || 0) - early; return { out, in: out + 0.3 }; };

  // 调试（制作/build/audit_lead.py 用，成片不受影响）：页面有 window.__BOARD_LOG__ 时，记下每一行手写字开始 / 写完的时刻（场景时钟）
  if (Array.isArray(window.__BOARD_LOG__)) {
    const base = ENG.ctx;
    ENG.ctx = S => {
      const c = base(S), h0 = c.hand;
      c.hand = o => { const it = h0(o); window.__BOARD_LOG__.push({ scene: S.id, text: String(o.text), at: +o.at, t0: it.t0, t1: it.t1 }); return it; };
      return c;
    };
  }

  // ================================================================== 小工具
  /** 印刷小字（出处、补充说明）：.bNote，默认 24 px */
  function note(c, html, x, y, at, o = {}) {
    const e = c.div('bNote', x, y, o.w != null ? o.w : null, null, html, o.parent);
    e.style.fontSize = (o.size || 24) + 'px';
    if (o.align) e.style.textAlign = o.align;
    if (o.color) e.style.color = o.color;
    return { el: e, tr: c.show(e, at, o.until, 4) };
  }
  /** 白板上的一页：一个手写组 + 要一起擦掉的东西（组件的 tr、印刷卡片的 Track、handNode 等），out(t) 整页擦掉 */
  function page(c) {
    const g = c.handGroup(), outs = [];
    return {
      g,
      add(x) { const o = x && (typeof x.out === 'function' ? x : x.tr); if (o && typeof o.out === 'function') outs.push(o); return x; },
      note(html, x, y, at, o = {}) { const n = note(c, html, x, y, at, o); outs.push(n.tr); return n.el; },
      out(t, d = 0.3) { g.setAttribute('data-out', t.toFixed(2)); c.T(g, { o: 1 }).to(t, { o: 0 }, d, E.sine); outs.forEach(x => x.out(t, d)); },
    };
  }
  /** 手写一行（html：<span class="or">…</span> 的字划黄线）；at..until = 写的时间窗 */
  const W = (c, g, html, x, y, size, at, until, o = {}) => c.handText(html, x, y, Object.assign({ size, at, until, parent: g }, o));
  /** 手画的「≠」 */
  function neq(c, g, cx, cy, s, at, color = ACC) {
    c.handLine({ x0: cx - s, y0: cy - s * 0.32, x1: cx + s, y1: cy - s * 0.32, at, dur: 0.12, w: 7, color, parent: g, cue: false });
    c.handLine({ x0: cx - s, y0: cy + s * 0.32, x1: cx + s, y1: cy + s * 0.32, at: at + 0.15, dur: 0.12, w: 7, color, parent: g, cue: false });
    return c.handLine({ x0: cx + s * 0.45, y0: cy - s * 0.95, x1: cx - s * 0.45, y1: cy + s * 0.95, at: at + 0.32, dur: 0.14, w: 7, color, parent: g });
  }
  /** 手画的叉（默认红色） */
  function cross(c, g, cx, cy, s, at, color = RED, w = 8) {
    c.handLine({ x0: cx - s, y0: cy - s, x1: cx + s, y1: cy + s, at, dur: 0.12, w, color, parent: g, cue: false });
    return c.handLine({ x0: cx + s, y0: cy - s, x1: cx - s, y1: cy + s, at: at + 0.14, dur: 0.12, w, color, parent: g });
  }
  /** 几条灰色波浪线 = 一大段字（草稿的样子） */
  function scribble(c, g, x0, y0, w, n, gap, at, dt = 0.2, o = {}) {
    const lens = [1, 0.84, 0.95, 0.7, 0.9, 0.62];
    let last = null;
    for (let i = 0; i < n; i++) {
      last = c.handUnderline({ x0, x1: x0 + w * lens[i % lens.length], y: y0 + i * gap, at: at + dt * i, dur: 0.28, w: o.w || 5, color: o.color || FAINT, parent: g });
    }
    return last;
  }
  /** 竖着的记号笔柱子（几笔并排涂满），底 yb、顶 yt、中线 x、宽 w */
  function column(c, g, x, yb, yt, w, at, color, n = 5) {
    const pen = w / n + 3, r = pen / 2;
    let last = null;
    for (let i = 0; i < n; i++) {
      const xx = x - w / 2 + r + (w - 2 * r) * i / (n - 1);
      last = c.handLine({ x0: xx, y0: yb - r, x1: xx, y1: yt + r, at: at + 0.05 * i, dur: 0.22, w: pen, color, parent: g, cue: false });
    }
    return last;
  }
  /** 纸白卡片（印刷体，贴胶带）+ kicker + 右上「示意」 */
  function paper(c, x, y, w, h, o = {}) {
    const cd = c.card(x, y, w, h);
    if (o.kicker) c.div('kicker', 32, 20, w - 150, null, o.kicker, cd);
    if (o.shiyi) c.div('shiyi', w - 78, 16, null, null, '示意', cd);
    c.tape(cd, o.tape || 0);
    return cd;
  }
  function txt(c, parent, x, y, html, font, o = {}) {
    const e = c.div('', x, y, o.w != null ? o.w : null, null, html, parent);
    Object.assign(e.style, { font, whiteSpace: 'nowrap', color: o.color || 'var(--ink)' });
    if (o.lh) e.style.lineHeight = o.lh + 'px';
    if (o.align) e.style.textAlign = o.align;
    return e;
  }

  // ================================================================== S01 开场：手写大字「深度思考」
  ENG.scene('S01', c => {
    const at = c.P(SG('S01-01'), '深度思考', 0.6) - 0.5;
    c.bigWord({ text: '深度思考', kicker: `原LAI如此 · #${ENG.pad2(EP.number)}`, at, sub: 'AI 回答之前的那几十秒' });
  });

  // ================================================================== S02 三个疑问（用户口述稿 v4）
  ENG.scene('S02', c => {
    const P = (id, ph, fr = 0) => c.P(SG(id), ph, fr);
    // ---- A（S02-02..04）深度思考 = 思维链；聊天窗口（示意）：开关打勾、正在思考… N 秒、滚出内心自白；DeepSeek 一边干活一边思考一边唱歌
    const A = page(c);
    const fA = FL(c, 'S02-04');
    const t02 = Math.max(T('S02-02') + 0.4, P('S02-02', '深度思考', 0.4) - 0.5);
    const dq = W(c, A.g, '深度思考 = <span class="or">思维链</span>', CX, 296, 64, t02, Math.max(t02 + 1.6, P('S02-02', '也就是', 0.8) - 0.1), { align: 'center' });
    A.note('Chain of Thought，简称 CoT', CX - 400, dq.y1 + 20, P('S02-02', 'CoT', 0.9) - 0.3, { w: 800, align: 'center', size: 22 });
    const CW = 800, CH = 340, X0 = 330, Y0 = 410;
    const tCard = T('S02-03') + 0.05;
    const card = paper(c, X0, Y0, CW, CH, { kicker: 'CHAT · 聊天窗口', shiyi: true });
    const bub = c.div('', CW - 32 - 320, 56, 320, 50, '帮我解一道难题……', card);
    Object.assign(bub.style, { background: '#FFFFFF', border: '2px solid #CFC9BE', borderRadius: '16px', font: '700 24px var(--cjk)', lineHeight: '50px', textAlign: 'center', color: 'var(--ink)' });
    // 状态行：● 正在思考… N 秒（示意：秒数一格一格往上跳）
    const tTh = P('S02-03', '开始转圈', 0.3) - 0.2, tTh1 = Math.max(tTh + 1.5, P('S02-03', '内心自白', 0.9));
    const st = txt(c, card, 32, 122, '<span style="color:var(--orange)">●</span> 正在思考…', '700 26px var(--cjk)', { color: 'var(--grey)', lh: 36 });
    c.T(st, { o: 0 }).to(tTh, { o: 1 }, 0.2);
    const secs = [3, 8, 14, 21, 27, 33, 38, 42];
    secs.forEach((s, i) => {
      const e = txt(c, card, 206, 122, `${s} 秒`, '800 26px var(--cjk)', { lh: 36 });
      const t0 = tTh + (tTh1 - tTh) * i / secs.length, t1 = tTh + (tTh1 - tTh) * (i + 1) / secs.length;
      const tr = c.T(e, { o: 0 }).to(t0, { o: 1 }, 0.04);
      if (i < secs.length - 1) tr.to(t1, { o: 0 }, 0.04);
    });
    // 滚出来的内心自白：几行灰色小字（看不清）
    const tL0 = P('S02-03', '内心自白', 0.1) - 0.4, tL1 = Math.max(tL0 + 0.8, T('S02-04'));
    [600, 520, 660, 440, 580].forEach((w, i) => {
      const l = c.div('', 32, 172 + i * 20, w, 9, '', card);
      Object.assign(l.style, { background: '#D6D1C7', borderRadius: '5px' });
      c.T(l, { o: 0 }).to(tL0 + (tL1 - tL0) * i / 5, { o: 1 }, 0.15);
    });
    // 输入框 + 「深度思考」开关
    const bar = c.div('', 32, CH - 74, CW - 64, 52, '', card);
    Object.assign(bar.style, { border: '2px solid #CFC9BE', borderRadius: '26px', background: '#FBFAF7' });
    txt(c, card, 60, CH - 74, '给 AI 发消息', '500 22px var(--cjk)', { color: '#A9A398', lh: 52 });
    const TW = 150, TX = CW - 32 - TW - 12, TY = CH - 74 + 8;
    const tg0 = c.div('', TX, TY, TW, 36, '深度思考', card);
    Object.assign(tg0.style, { border: '2px solid #BDB7AB', borderRadius: '18px', font: '700 20px var(--cjk)', lineHeight: '32px', textAlign: 'center', color: '#6E6A63', background: '#FFFFFF' });
    const tg1 = c.div('', TX, TY, TW, 36, '深度思考', card);
    Object.assign(tg1.style, { border: '2px solid var(--orange)', borderRadius: '18px', font: '800 20px var(--cjk)', lineHeight: '32px', textAlign: 'center', color: 'var(--orange)', background: '#FFE9E0' });
    const tOn = P('S02-03', '深度思考模式', 0.3) - 0.1;
    c.T(tg1, { o: 0 }).to(tOn, { o: 1 }, 0.15);
    A.add(c.show(card, tCard, null, 10));
    c.cue(tCard, 'card');
    c.handCheck({ x: X0 + TX + TW / 2, y: Y0 + TY - 34, size: 44, at: tOn + 0.1, parent: A.g });
    c.cue(tTh, 'item');
    // S02-04：最近的 DeepSeek 一边干活、一边思考、一边唱歌（网友反映）
    const RX = 1210;
    let prev = null;                              // 这一页最后一句：“唱歌”在句末，三行从这句开头接着写，翻页前看得够久
    [['一边干活', INK], ['一边思考', INK], ['一边唱歌', ACC]].forEach(([s, col], i) => {
      const at = prev ? prev.t1 + 0.05 : T('S02-04') + 0.1;
      prev = W(c, A.g, s, RX, 480 + i * 90, 52, at, at + 0.75, { color: col });
    });
    A.note('♪', prev.x1 + 14, 480 + 2 * 90 - 26, prev.t1 + 0.05, { size: 40, color: 'var(--orange)' });
    A.note('网友反映 · DeepSeek V4.1 Flash · 2026-09', RX, 700, prev.t1 + 0.1, { w: 500, size: 22 });
    A.out(fA.out);

    // ---- B（S02-05..09）手写「今天聊三个问题」+ 三个问题（文字取 episode.questions）；到 ENG.tocInTime() 飞进右上目录
    c.questionCards({ title: '今天聊三个问题', at: [P('S02-06', '这几十秒'), P('S02-07', '那段'), P('S02-08', '什么时候')], titleAt: Math.max(fA.in, T('S02-05') + 0.05) });
  });

  // ================================================================== S03 一、这几十秒在干什么：它在写草稿
  ENG.scene('S03', c => {
    const P = (id, ph, fr = 0) => c.P(SG(id), ph, fr);
    c.autoTitle(SG('S03-10'), { text: '一、这几十秒在干什么' });

    // ---- A（S03-10..11）问题 → 一大段文字（思维链）→ 答案；下面就叫它草稿
    const A = page(c);
    const fA = FL(c, 'S03-11', 0.8);   // 下一页开头是一行小字：晚一点擦
    const FY = 330, FH = 140, FM = FY + FH / 2;          // 流程这一排：y 330–470
    // 实测配音这一页只有 7.8 秒、翻页又提前：方框的字写快一点（write），「你等的就是这一格」挪到答案之后
    const t10 = Math.max(T('S03-10') + 0.5, P('S03-10', 'AI会写出', 0.2) - 0.9);
    const nQ = A.add(c.handNode({ x: 200, y: FY, w: 230, h: FH, text: '问题', size: 52, at: t10, dur: 0.4, write: t10 + 0.9 }));
    const tBox = Math.max(nQ.t1 + 0.1, P('S03-10', '一大段文字', 0.3) - 0.5);
    const DX0 = 540, DX1 = 1380, DY0 = FY - 24, DY1 = FY + FH + 24;   // 思维链 / 草稿框（橙色）
    c.handArrow({ x0: nQ.x1 + 12, y0: FM, x1: DX0 - 12, y1: FM, at: tBox - 0.25, dur: 0.25, parent: A.g });
    c.handRect({ x0: DX0, y0: DY0, x1: DX1, y1: DY1, at: tBox, dur: 0.45, w: 6, color: ACC, parent: A.g });
    const sc = scribble(c, A.g, DX0 + 34, DY0 + 98, DX1 - DX0 - 80, 3, 28, tBox + 0.4, 0.22);
    const tCoT = Math.max(sc.t1 + 0.05, P('S03-10', '思维链', 0.5) - 0.4);
    const lab = W(c, A.g, '思维链', DX0 + 34, DY0 + 46, 44, tCoT, tCoT + 0.7);
    const tA = Math.max(lab.t1 + 0.05, P('S03-10', 'Chain', 0.4) - 0.3);
    const nA = A.add(c.handNode({ x: 1490, y: FY, w: 230, h: FH, text: '答案', size: 52, at: tA, dur: 0.4, write: tA + 0.9 }));
    c.handArrow({ x0: DX1 + 12, y0: FM, x1: nA.x0 - 12, y1: FM, at: tA - 0.25, dur: 0.25, parent: A.g });
    A.note('英文 Chain of Thought，简称 CoT', CX - 500, DY1 + 26, P('S03-10', 'Chain', 0.8), { w: 1000, align: 'center' });
    const wait = W(c, A.g, '你等的就是这一格', (DX0 + DX1) / 2, DY1 + 110, 38, nA.t1 + 0.05, nA.t1 + 1.2, { align: 'center', color: ACC });
    // S03-11：为了好理解，下面就叫它草稿（「= 草稿」，圈起来）
    const t11 = Math.max(wait.t1 + 0.05, T('S03-11') + 0.05);
    const cg = W(c, A.g, '= 草稿', lab.x1 + 22, DY0 + 46, 44, t11, t11 + 0.6, { color: ACC });
    c.handMark(cg, 2, 4, { kind: 'circle', at: cg.t1 + 0.05 });
    A.out(fA.out);

    // ---- B（S03-12..13）各家叫法：DeepSeek 深度思考 / OpenAI 推理 / Anthropic（Claude）思考
    const B = page(c);
    const fB = FL(c, 'S03-13');
    B.note('同一个功能，各家的叫法', CX - 400, 262, fA.in, { w: 800, align: 'center' });
    const VX = CX - 70, TX = CX + 70, RY = [380, 510, 640];
    [
      ['DeepSeek', '深度思考', '网页 / App 上的开关', Math.max(fA.in + 0.1, P('S03-12', 'DeepSeek', 0.3) - 0.3), P('S03-12', '深度思考', 0.5) - 0.3],
      ['OpenAI', '推理', '文档里的叫法 · Reasoning（调深浅的参数叫推理强度）', P('S03-12', 'OpenAI', 0.65) - 0.3, P('S03-12', '推理', 0.9) - 0.3],
      ['Anthropic', '思考', '文档里的叫法 · Thinking', T('S03-13') + 0.05, P('S03-13', '叫思考', 0.85) - 1.6, 0.8, 0.7],
    ].forEach(([v, term, sub, tv, tt, dv = 0.9, dt = 0.9], i) => {
      const y = RY[i];
      const vi = W(c, B.g, v, VX, y, 58, tv, tv + dv, { align: 'right' });
      c.handLine({ x0: VX + 22, y0: y, x1: TX - 22, y1: y, at: vi.t1 + 0.03, dur: 0.15, w: 4, color: SOFT, parent: B.g, cue: false });
      const t0 = Math.max(tt, vi.t1 + 0.2);
      const ti = W(c, B.g, term, TX, y, 68, t0, t0 + dt);
      c.handUnderline({ x0: ti.x0 - 6, x1: ti.x1 + 8, y: ti.y1 + 12, at: ti.t1 + 0.04, dur: 0.3, parent: B.g });
      B.note(sub, TX, y + 46, ti.t1 + 0.1, { size: 22 });
    });
    B.note('Claude 的公司', VX - 300, RY[2] + 46, P('S03-13', 'Claude', 0.5), { w: 300, align: 'right', size: 22 });
    B.out(fB.out);

    // ---- C（S03-14..16）Anthropic 官方文档：思考时会做什么（四条；「走不通」画一支箭头回到「尝试几种做法」）
    //      手写的列表自己排（pointList 最后一条的写字窗最长 2.2 s，这一页最后一句短，翻页前显示不够）
    const C = page(c);
    // 下一页开头是方框（不是马上要念的字），这一页晚一点擦（0.5），四条也提前写，「走不通」的回路箭头才看得到
    const fC = FL(c, 'S03-16', 0.5);
    const LX0 = CX - 430, LS0 = 56;
    const t14 = Math.max(fB.in, T('S03-14') + 0.1);
    const kk = c.div('bKick', LX0, 256, 860, null, 'SOURCE · Anthropic 官方文档');
    kk.style.textAlign = 'left';
    C.add(c.show(kk, t14, null, 6));
    const tl = W(c, C.g, '思考时会做什么', LX0, 338, 67, t14, t14 + 1.2);
    c.handLine({ x0: LX0, y0: tl.y1 + 18, x1: LX0 + 640, y1: tl.y1 + 15, at: tl.t1 + 0.03, dur: 0.3, w: 3, color: 'rgba(26,26,26,.4)', parent: C.g, cue: false });
    const item = (n, text, y, at, dur) => {
      const nn = c.hand({ text: String(n), x: LX0 + 4, y, size: LS0, color: ACC, at, until: at + 0.22, parent: C.g, cue: false });
      return W(c, C.g, text, LX0 + 59, y, LS0, nn.t1 + 0.03, nn.t1 + 0.03 + dur);
    };
    const r1 = item(1, '重复一遍题目', 450, Math.max(tl.t1 + 0.3, T('S03-15') - 0.4), 0.9);
    const r2 = item(2, '尝试几种做法', 540, Math.max(r1.t1 + 0.05, P('S03-15', '再尝试', 0.5) - 0.6), 0.9);
    const r3 = item(3, '检查中间结果', 630, Math.max(r2.t1 + 0.05, T('S03-16') - 0.3), 0.9);
    const r4 = item(4, '走不通就换路', 720, Math.max(r3.t1 + 0.05, P('S03-16', '走不通', 0.5) - 0.8), 0.9);
    const m2 = (r2.y0 + r2.y1) / 2, m4 = (r4.y0 + r4.y1) / 2, ax = Math.max(r2.x1, r4.x1) + 60, tLoop = r4.t1 + 0.05;
    c.handLine({ x0: r4.x1 + 20, y0: m4, x1: ax, y1: m4, at: tLoop, dur: 0.12, w: 6, color: ACC, parent: C.g, cue: false });
    c.handLine({ x0: ax, y0: m4, x1: ax, y1: m2, at: tLoop + 0.13, dur: 0.18, w: 6, color: ACC, parent: C.g, cue: false });
    c.handArrow({ x0: ax, y0: m2, x1: r2.x1 + 20, y1: m2, at: tLoop + 0.32, dur: 0.18, w: 6, color: ACC, parent: C.g });
    C.out(fC.out);

    // ---- D（S03-17..22）鸡兔同笼的草稿（示意）：题目卡 + 草稿框里一行一行试算 → 结束思考，写出答案
    const D = page(c);
    const t17 = Math.max(fC.in, T('S03-17') + 0.1);
    const QW = 600, QH = 176, QY = 262;
    const qc = paper(c, 200, QY, QW, QH, { kicker: 'QUESTION · 鸡兔同笼', tape: 1 });
    txt(c, qc, 32, 56, '笼子里有 <span style="color:var(--orange)">35</span> 个头、<span style="color:var(--orange)">94</span> 只脚，<br>鸡和兔各几只？', '800 34px var(--cjk)', { lh: 52 });
    const tQ = Math.max(t17, P('S03-17', '笼子里', 0.4) - 0.2);
    D.add(c.show(qc, tQ, null, 10));
    c.cue(tQ, 'card');
    D.note('示意：按官方描述的过程简化，<br>不是某个模型的原始输出', 200, QY + QH + 22, P('S03-17', '各有几只', 0.8), { w: QW, size: 22 });
    const DX0b = 880, DX1b = 1720, DY0b = 262, DY1b = 790;
    c.handRect({ x0: DX0b, y0: DY0b, x1: DX1b, y1: DY1b, at: t17, dur: 0.5, w: 5, parent: D.g });
    W(c, D.g, '草稿', DX0b + 30, DY0b + 44, 40, t17 + 0.45, t17 + 1.0, { color: ACC });
    const LX = DX0b + 44, LS = 46, LY = [DY0b + 120, DY0b + 208, DY0b + 296, DY0b + 384, DY0b + 466];
    const t18 = P('S03-18', '随手试', 0.3) - 0.2;
    W(c, D.g, '试：鸡 20，兔 15', LX, LY[0], LS, t18, T('S03-19') - 0.05);
    const t19 = T('S03-19') + 0.05, t19b = P('S03-19', '比94', 0.4);
    const L2a = W(c, D.g, '脚 = 100', LX, LY[1], LS, t19, Math.max(t19 + 0.6, t19b - 0.1));
    const L2b = W(c, D.g, '，比 94 多 6 只', L2a.x1 + 4, LY[1], LS, Math.max(t19b, L2a.t1 + 0.05), P('S03-19', '兔子多了', 0.8) - 0.1, { color: RED });
    const t19c = Math.max(L2b.t1 + 0.05, P('S03-19', '兔子多了', 0.85) - 0.3);
    W(c, D.g, '→ 兔多了', L2b.x1 + 18, LY[1], LS, t19c, t19c + 0.8, { color: ACC });
    const t20 = T('S03-20') + 0.05, t20b = P('S03-20', '换三只', 0.4);
    const L3a = W(c, D.g, '兔换成鸡：每只少 2 脚', LX, LY[2], LS, t20, Math.max(t20 + 1.2, t20b - 0.1));
    W(c, D.g, '→ 换 3 只', L3a.x1 + 18, LY[2], LS, Math.max(t20b, L3a.t1 + 0.05), Math.max(t20b, L3a.t1 + 0.05) + 0.8, { color: ACC });
    const t21 = P('S03-21', '检查', 0.3) - 0.3;
    const L4 = W(c, D.g, '检查：鸡 23，兔 12', LX, LY[3], LS, t21, Math.max(t21 + 1.2, P('S03-21', '头35', 0.5) - 0.1));
    const tH = Math.max(L4.t1 + 0.05, P('S03-21', '头35', 0.5) - 0.25);
    const h35 = W(c, D.g, '头 35', LX + 150, LY[4], 44, tH, tH + 0.5);
    c.handCheck({ x: h35.x1 + 36, y: LY[4] - 4, size: 40, at: h35.t1 + 0.05, parent: D.g });
    const tF = Math.max(h35.t1 + 0.3, P('S03-21', '脚94', 0.5) - 0.25);
    const f94 = W(c, D.g, '脚 94', h35.x1 + 100, LY[4], 44, tF, tF + 0.5);
    c.handCheck({ x: f94.x1 + 36, y: LY[4] - 4, size: 40, at: f94.t1 + 0.05, parent: D.g });
    // S03-22：结束思考过程，正式返回给用户 → 写出答案
    const tAn = Math.max(f94.t1 + 0.3, P('S03-22', '结束', 0.3) - 0.3);
    c.handArrow({ x0: DX0b - 14, y0: 640, x1: 752, y1: 640, at: tAn - 0.25, dur: 0.25, w: 7, color: ACC, parent: D.g });
    D.add(c.handNode({ x: 220, y: 582, w: 520, h: 116, text: '答案：鸡 23，兔 12', size: 44, at: tAn, write: tAn + 1.6, color: ACC, pen: 6 }));
    D.note('思考结束，才正式回答用户', 220, 710, P('S03-22', '写出答案', 0.6), { w: 520, align: 'center', size: 22 });
  });

  // ================================================================== S04 为什么要写草稿（第一题的第二章）
  ENG.scene('S04', c => {
    const P = (id, ph, fr = 0) => c.P(SG(id), ph, fr);
    const ttl = c.autoTitle(SG('S04-23'));

    // ---- A（S04-24..29）token 一个一个往外写；一口气答 ✗；用深度思考：第 1 步 → 第 3 步 → 答案 ✓
    const A = page(c);
    const fA = FL(c, 'S04-29');
    const tTk = Math.max(ttl.morph + 0.3, P('S04-24', 'token', 0.5) - 0.35);
    const tk = W(c, A.g, 'token', 250, 312, 64, tTk, tTk + 0.8, { color: ACC });
    const q0 = Math.max(tk.t1 + 0.05, P('S04-24', '一个token', 0.5)), q1 = Math.max(q0 + 1.2, P('S04-24', '往外写', 0.9));
    const NQ = 14;
    for (let i = 0; i < NQ; i++) {
      const x = 250 + i * 62;
      c.handRect({ x0: x, y0: 374, x1: x + 44, y1: 418, at: q0 + (q1 - q0) * i / NQ, dur: 0.12, w: 4, r: 6, color: i === NQ - 1 ? ACC : INK, parent: A.g, cue: false });
    }
    c.cue(q0, 'item');
    const t25 = Math.max(tk.t1 + 0.1, T('S04-25') + 0.1);
    W(c, A.g, '：一个字 · 一个词 · 词的一部分', tk.x1 + 12, 312, 44, t25, T('S04-26') - 0.1);
    A.note('大致如此，不同模型切法不同', 250, 438, P('S04-25', '一部分', 0.9), { size: 22 });
    // S04-26：一口气给不出答案 → 容易错
    const R1 = 560, R2 = 700, NX = [560, 790, 1020, 1250];
    const t26 = T('S04-26') + 0.05;
    const l1 = W(c, A.g, '一口气答', 250, R1, 48, t26, t26 + 1.0);
    const tA1 = Math.max(l1.t1 + 0.1, P('S04-26', '一口气', 0.5) - 0.2);
    c.handArrow({ x0: l1.x1 + 16, y0: R1, x1: NX[0] - 12, y1: R1, at: tA1 - 0.2, dur: 0.2, w: 5, parent: A.g });
    const n1 = A.add(c.handNode({ x: NX[0], y: R1 - 45, w: 150, h: 90, text: '答案', size: 40, at: tA1, write: tA1 + 0.8, pen: 4 }));
    cross(c, A.g, NX[0] + 75, R1, 40, Math.max(n1.t1 + 0.1, P('S04-26', '无法给出答案', 0.7) - 0.3));
    // S04-27..29：用深度思考：一步一步写下来 → 答案 ✓
    const t27 = T('S04-27') + 0.05;
    const l2 = W(c, A.g, '深度思考', 250, R2, 48, t27, t27 + 1.0, { color: ACC });
    const s0 = Math.max(l2.t1 + 0.1, P('S04-28', '中间的步骤', 0.4) - 0.2), s1 = Math.max(s0 + 1.5, P('S04-28', '写下来', 0.9) - 0.4);
    let last = null;
    ['第1步', '第2步', '第3步', '答案'].forEach((s, i) => {
      const at = s0 + (s1 - s0) * i / 3, x = NX[i];
      c.handArrow({ x0: i ? x - 80 + 12 : l2.x1 + 16, y0: R2, x1: x - 12, y1: R2, at: at - 0.18, dur: 0.18, w: 5, color: i ? SOFT : INK, parent: A.g });
      last = A.add(c.handNode({ x, y: R2 - 45, w: 150, h: 90, text: s, size: 38, at, write: at + 0.65, pen: 4, color: i === 3 ? ACC : undefined }));
    });
    c.handCheck({ x: NX[3] + 150 + 46, y: R2, size: 48, at: Math.max(last.t1 + 0.05, T('S04-29') + 0.1), parent: A.g });
    A.out(fA.out);

    // ---- B（S04-30..32）能提高哪些任务的表现；那几十秒主要在写思维链，写得越多等得越久
    const B = page(c);
    const fB = FL(c, 'S04-32');
    const t30 = Math.max(fA.in, T('S04-30') + 0.1);
    let lw = null;
    [['数学', CX - 420], ['写代码', CX], ['分析', CX + 420]].forEach(([w, x]) => {
      const at = Math.max(t30, lw ? lw.t1 + 0.05 : 0, P('S04-30', w, 0.2) - 0.6);
      lw = W(c, B.g, w, x, 330, 72, at, at + 0.6, { align: 'center' });
      c.handMark(lw, 0, [...w].length, { kind: 'circle', at: lw.t1 + 0.05 });
    });
    const tUp = Math.max(lw.t1 + 0.2, P('S04-30', '表现', 0.9) - 1.0);
    const up = W(c, B.g, '表现更好', CX, 476, 56, tUp, tUp + 0.9, { align: 'center', color: ACC });
    c.handArrow({ x0: up.x1 + 40, y0: 506, x1: up.x1 + 40, y1: 446, at: up.t1 + 0.05, dur: 0.22, w: 6, color: ACC, parent: B.g });
    B.note('出处：Anthropic 官方文档；Wei 等 2022（思维链论文）', CX - 500, 526, up.t1 + 0.2, { w: 1000, align: 'center', size: 22 });
    const t31 = T('S04-31') + 0.05;
    W(c, B.g, '那几十秒：主要在写思维链', CX, 640, 54, t31, Math.max(t31 + 1.4, T('S04-32') - 0.1), { align: 'center' });
    const t32 = Math.max(t31 + 1.5, T('S04-32') + 0.05);
    const lg = W(c, B.g, '写得越多 → 等得越久', CX, 748, 66, t32, t32 + 1.5, { align: 'center' });
    c.handUnderline({ x0: lg.x0 - 8, x1: lg.x1 + 10, y: lg.y1 + 16, at: lg.t1 + 0.05, parent: B.g });
    B.note('结果往往也更准一些，但有收益递减（第三部分）· 等待还受排队、联网搜索等影响', CX - 560, 814, P('S04-32', '更准一些', 0.5), { w: 1120, align: 'center', size: 22 });
    B.out(fB.out);

    // ---- C（S04-33..38）DeepSeek-R1 论文公开的一种练法：不给人写的过程、只看最终答案给奖励 = 强化学习；草稿越练越长
    const C = page(c);
    const fC = FL(c, 'S04-38');
    const t33 = Math.max(fB.in, T('S04-33') + 0.1);
    const kq = c.div('bKick', 250, 240, 900, null, 'Q · 大模型的思维链是怎么练出来的？');
    kq.style.textAlign = 'left';
    C.add(c.show(kq, t33, null, 6));
    const t34 = Math.max(t33 + 0.3, P('S04-34', 'DeepSeek', 0.35) - 0.35);
    const hd = W(c, C.g, 'DeepSeek-R1 论文：一种练法', 250, 314, 54, t34, Math.max(t34 + 1.6, T('S04-35') - 0.05));
    C.note('《自然》2025 · arXiv 2501.12948', 250, 354, hd.t1 + 0.1, { size: 22 });
    const t35 = Math.max(hd.t1 + 0.1, P('S04-35', '不给它看', 0.4) - 0.3);
    cross(c, C.g, 272, 450, 18, t35);
    const r35 = W(c, C.g, '不给它看人写的解题过程', 310, 450, 48, t35 + 0.3, Math.max(t35 + 1.8, T('S04-36') - 0.1));
    C.note('这一版叫 R1-Zero；正式版 R1 另加了少量冷启动数据和多阶段训练', 310, 488, r35.t1 + 0.1, { size: 22 });
    const t36 = Math.max(r35.t1 + 0.1, T('S04-36') + 0.05);
    c.handCheck({ x: 272, y: 576, size: 40, at: t36, parent: C.g });
    const r36 = W(c, C.g, '只看最终答案：对了给奖励', 310, 576, 48, t36 + 0.2, Math.max(t36 + 2.0, T('S04-37') - 0.05));
    C.note('另有格式奖励 · 中间怎么写不打分', 310, 614, r36.t1 + 0.1, { size: 22 });
    const t37 = Math.max(r36.t1 + 0.1, T('S04-37') + 0.05);
    const rl = W(c, C.g, '= 强化学习', 310, 698, 62, t37, t37 + 1.0, { color: ACC });
    c.handMark(rl, 2, 6, { kind: 'underline', at: rl.t1 + 0.05 });
    const GX = 1130, GY = 700, GW = 540, GH = 320;
    const t38 = T('S04-38') + 0.05;
    c.handLine({ x0: GX, y0: GY, x1: GX + GW, y1: GY, at: t38, dur: 0.25, w: 4, parent: C.g, cue: false });
    c.handLine({ x0: GX, y0: GY, x1: GX, y1: GY - GH, at: t38 + 0.12, dur: 0.25, w: 4, parent: C.g, cue: false });
    C.note('训练时间 →', GX + GW - 200, GY + 12, t38 + 0.3, { w: 200, align: 'right', size: 22 });
    C.note('↑ 草稿长度', GX - 8, GY - GH - 38, t38 + 0.3, { size: 22 });
    const tc = Math.max(t38 + 0.35, P('S04-38', '越长', 0.3) - 0.4);
    const pts = [[GX + 10, GY - 24], [GX + 140, GY - 62], [GX + 260, GY - 118], [GX + 380, GY - 196], [GX + 510, GY - 292]];
    for (let i = 0; i < pts.length - 1; i++) {
      c.handLine({ x0: pts[i][0], y0: pts[i][1], x1: pts[i + 1][0], y1: pts[i + 1][1], at: tc + 0.16 * i, dur: 0.16, w: 7, color: ACC, parent: C.g, cue: false });
    }
    c.cue(tc, 'chart');
    C.out(fC.out);

    // ---- D（S04-39..42）论文记下的片段：写到一半“等一下”→ 回头重算；现在的 DeepSeek 也常见；15.6% → 77.9%
    const D = page(c);
    const t39 = Math.max(fC.in, P('S04-39', '写到一半', 0.4) - 0.4);
    const wt = W(c, D.g, '写到一半：“等一下”', CX, 308, 66, t39, Math.max(t39 + 1.8, P('S04-39', '等一下', 0.8) + 0.2), { align: 'center' });
    c.handMark(wt, 6, 9, { kind: 'underline', at: wt.t1 + 0.05 });
    const tQ = Math.max(wt.t1 + 0.1, P('S04-39', '等一下', 0.9) - 0.2);
    const qw = 1200, qh = 150;
    const qc = paper(c, CX - qw / 2, 392, qw, qh, { kicker: 'DeepSeek-R1 论文 · R1-Zero 中间版本写下的原话（英文）', tape: 2 });
    txt(c, qc, 36, 62, "“Wait, wait. Wait. That's an aha moment I can flag here.”", 'italic 700 34px var(--cjk)', { lh: 56 });
    D.add(c.show(qc, tQ, null, 10));
    c.cue(tQ, 'card');
    const t40 = T('S04-40') + 0.05;
    W(c, D.g, '→ 回头检查，重新算一遍', CX, 612, 54, t40, t40 + 1.8, { align: 'center', color: ACC });
    D.note('现在 DeepSeek 的思维链里，也常见“等一下”', CX - 500, 652, T('S04-41') + 0.3, { w: 1000, align: 'center', size: 24 });
    const t42 = T('S04-42') + 0.05;
    const lb = W(c, D.g, '正确率', CX - 560, 750, 50, t42, t42 + 0.9);
    const tNa = Math.max(lb.t1 + 0.1, P('S04-42', '从15', 0.5) - 0.4);
    const va = W(c, D.g, '15.6%', lb.x1 + 50, 750, 70, tNa, tNa + 0.8);
    c.handArrow({ x0: va.x1 + 26, y0: 750, x1: va.x1 + 180, y1: 750, at: va.t1 + 0.05, dur: 0.3, w: 8, color: ACC, parent: D.g });
    const tNb = Math.max(va.t1 + 0.45, P('S04-42', '升到了', 0.6) - 0.2);
    const vb = W(c, D.g, '77.9%', va.x1 + 210, 750, 80, tNb, tNb + 0.8, { color: ACC });
    c.handUnderline({ x0: vb.x0 - 6, x1: vb.x1 + 8, y: vb.y1 + 14, at: vb.t1 + 0.05, parent: D.g });
    D.note('一套数学竞赛题（AIME 2024）· 平均 pass@1 · R1-Zero 训练过程 · Nature 版数字（arXiv 初版写的是 71.0%）', CX - 720, 814, vb.t1 + 0.2, { w: 1440, align: 'center', size: 22 });
  });

  // ================================================================== S05 二、思考过程是真想法吗
  ENG.scene('S05', c => {
    const P = (id, ph, fr = 0) => c.P(SG(id), ph, fr);
    c.autoTitle(SG('S05-43'), { text: '二、思考过程是真想法吗' });

    // ---- A（S05-43..44）思考过程 = 草稿；先告诉你：可以当线索 ✓ / 不能当证明 ✗
    const A = page(c);
    const fA = FL(c, 'S05-44', 0.6);   // 最后一句只有 3 秒、“不能当证明”在句尾：晚一点擦
    const t43 = Math.max(T('S05-43') + 1.0, P('S05-43', '思考过程', 0.5) - 0.3);
    const eq = W(c, A.g, '思考过程 = 草稿', CX, 372, 84, t43, t43 + 1.4, { align: 'center' });
    c.handMark(eq, 7, 9, { kind: 'underline', at: eq.t1 + 0.05 });
    const tL = Math.max(eq.t1 + 0.2, T('S05-44') - 0.3), tR = Math.max(tL + 1.2, P('S05-44', '不能当证明', 0.5) - 1.3);
    c.handCheck({ x: CX - 520, y: 600, size: 56, at: tL, parent: A.g });
    W(c, A.g, '可以：当线索', CX - 468, 600, 64, tL + 0.25, tR - 0.05);
    cross(c, A.g, CX + 110, 600, 24, tR);
    W(c, A.g, '不能：当证明', CX + 160, 600, 64, tR + 0.3, tR + 1.1);
    A.out(fA.out);

    // ---- B（S05-45..49）各家接口怎么给：DeepSeek 直接返回 / OpenAI 摘要 / Claude 摘要（另一个模型写）
    const B = page(c);
    const fB = FL(c, 'S05-49');
    const t45 = Math.max(fA.in, T('S05-45') + 0.1);
    W(c, B.g, '接口里，思考过程怎么给？', CX, 290, 56, t45, Math.max(t45 + 2.0, T('S05-46') - 0.05), { align: 'center' });
    B.note('产品界面各版本不同，这里按各家接口文档来说', CX - 450, 334, P('S05-45', '怎么描述', 0.5), { w: 900, align: 'center', size: 22 });
    const VX = 700, TX = 780, RY = [440, 570, 700];
    const v1 = W(c, B.g, 'DeepSeek', VX, RY[0], 56, T('S05-46') + 0.05, T('S05-46') + 0.9, { align: 'right' });
    const tv1 = Math.max(v1.t1 + 0.1, P('S05-46', '单独', 0.5) - 0.3);
    const x1 = W(c, B.g, '直接返回', TX, RY[0], 60, tv1, tv1 + 1.1);
    c.handCheck({ x: x1.x1 + 42, y: RY[0], size: 44, at: x1.t1 + 0.05, parent: B.g });
    B.note('单独一个字段 reasoning_content · 文档没说它是摘要', TX, RY[0] + 50, x1.t1 + 0.1, { size: 22 });
    const v2 = W(c, B.g, 'OpenAI', VX, RY[1], 56, T('S05-47') + 0.05, T('S05-47') + 0.8, { align: 'right' });
    const tv2 = Math.max(v2.t1 + 0.1, P('S05-47', '摘要', 0.8) - 0.4);
    const x2 = W(c, B.g, '摘要', TX, RY[1], 60, tv2, tv2 + 0.7, { color: SOFT });
    B.note('不给原文；摘要要主动要，部分模型没有', TX, RY[1] + 50, x2.t1 + 0.1, { size: 22 });
    const v3 = W(c, B.g, 'Claude', VX, RY[2], 56, T('S05-48') + 0.05, T('S05-48') + 0.8, { align: 'right' });
    const tv3 = Math.max(v3.t1 + 0.1, P('S05-48', '摘要', 0.5) - 0.3);
    const x3 = W(c, B.g, '摘要', TX, RY[2], 60, tv3, tv3 + 0.7, { color: SOFT });
    const tM = Math.max(x3.t1 + 0.1, P('S05-48', '另一个模型', 0.6) - 0.3);
    const nm = B.add(c.handNode({ x: 1190, y: RY[2] - 52, w: 300, h: 104, text: '另一个模型', size: 40, at: tM, write: tM + 1.3 }));
    c.handArrow({ x0: nm.x0 - 12, y0: RY[2], x1: x3.x1 + 18, y1: RY[2], at: nm.t1 + 0.05, dur: 0.25, parent: B.g });
    B.note('最新模型在接口里默认连摘要也不返回', TX, RY[2] + 50, nm.t1 + 0.1, { size: 22 });
    const t49a = P('S05-49', '直接返回', 0.3) - 0.3, t49b = Math.max(t49a + 0.5, P('S05-49', '有的只是', 0.8) - 0.3);
    c.handUnderline({ x0: x1.x0 - 6, x1: x1.x1 + 8, y: x1.y1 + 12, at: t49a, parent: B.g });
    c.handUnderline({ x0: x2.x0 - 6, x1: x2.x1 + 8, y: x2.y1 + 12, at: t49b, parent: B.g });
    c.handUnderline({ x0: x3.x0 - 6, x1: x3.x1 + 8, y: x3.y1 + 12, at: t49b + 0.3, parent: B.g });
    B.out(fB.out);

    // ---- C（S05-50..53）直接返回的 ≠ 真正原因；2025 年 Anthropic 的实验：选择题 + 悄悄塞的提示
    const C = page(c);
    const fC = FL(c, 'S05-53', 0.8);
    const t50 = Math.max(fB.in, P('S05-50', '直接返回', 0.2) - 0.2);
    const la = W(c, C.g, '直接返回的', CX - 80, 300, 60, t50, t50 + 1.4, { align: 'right' });
    neq(c, C.g, CX, 300, 30, Math.max(la.t1 + 0.1, P('S05-50', '不一定', 0.5) - 0.3));
    const tRa = Math.max(la.t1 + 0.7, P('S05-50', '真正的原因', 0.8) - 0.45);
    const ra = W(c, C.g, '真正原因', CX + 80, 300, 60, tRa, tRa + 1.1);
    c.handUnderline({ x0: ra.x0 - 6, x1: ra.x1 + 8, y: ra.y1 + 14, at: ra.t1 + 0.05, parent: C.g });
    const t51 = T('S05-51') + 0.05;
    W(c, C.g, '2025 · Anthropic 的实验', 250, 404, 50, t51, Math.max(t51 + 1.8, T('S05-52') - 0.05));
    const t52 = T('S05-52') + 0.05;
    const qz = paper(c, 250, 500, 560, 250, { kicker: 'QUIZ · 选择题', shiyi: true, tape: 0 });
    txt(c, qz, 32, 58, '下面哪一项是对的？', '800 32px var(--cjk)', { lh: 48 });
    ['A　……', 'B　……', 'C　……', 'D　……'].forEach((s, i) => txt(c, qz, 32 + (i % 2) * 250, 124 + Math.floor(i / 2) * 52, s, '700 28px var(--cjk)', { lh: 40 }));
    C.add(c.show(qz, t52, null, 10));
    c.cue(t52, 'card');
    // 悄悄塞进来的提示：一张黄色小纸条从右边滑进来（外层跟轨道动，里层转个角度）
    const tHint = Math.max(t52 + 0.5, P('S05-52', '悄悄塞', 0.5) - 0.2);
    const hw = c.div('', 690, 648, 250, 90, '');
    const hin = c.div('', 0, 0, 250, 90, '提示：答案是 C', hw);
    Object.assign(hin.style, { background: '#FFE98A', font: '800 28px var(--cjk)', lineHeight: '90px', textAlign: 'center', color: 'var(--ink)', transform: 'rotate(-6deg)', boxShadow: '0 6px 14px rgba(0,0,0,.14)' });
    C.add(c.T(hw, { o: 0, x: 140 }).to(tHint, { o: 1, x: 0 }, 0.45, E.out));
    c.cue(tHint, 'item');
    const t53 = T('S05-53') + 0.05;
    const ch = W(c, C.g, '因为提示改了答案', 1010, 540, 50, t53, t53 + 1.2);
    c.handArrow({ x0: 1100, y0: 578, x1: 1100, y1: 618, at: ch.t1 + 0.05, dur: 0.2, w: 5, color: SOFT, parent: C.g });
    const t53b = Math.max(ch.t1 + 0.3, P('S05-53', '有没有提到', 0.3) - 1.0);
    const qq = W(c, C.g, '草稿里提没提？', 1010, 660, 56, t53b, t53b + 1.0);
    c.handMark(qq, 3, 6, { kind: 'underline', at: qq.t1 + 0.05 });
    C.out(fC.out);

    // ---- D（S05-54..57）结果：草稿提到提示的比例 Claude 3.7 Sonnet 25% / DeepSeek R1 39%；没提到的部分涂黄
    const D = page(c);
    const fD = FL(c, 'S05-57', 0.8);
    const BY = 760, BH = 400, BW = 110, TOP = BY - BH;
    const t54 = Math.max(fC.in, T('S05-54') + 0.1);
    c.handLine({ x0: 440, y0: BY, x1: 1060, y1: BY, at: t54, dur: 0.3, w: 4, parent: D.g, cue: false });
    const bars = [
      { x: 580, v: 0.25, lab: 'Claude 3.7 Sonnet', val: '25%', tl: Math.max(t54 + 0.2, P('S05-54', 'Claude', 0.4) - 0.3), tb: P('S05-54', '只有', 0.6) - 0.3 },
      { x: 880, v: 0.39, lab: 'DeepSeek R1', val: '39%', tl: T('S05-55') + 0.05, tb: P('S05-55', '只有39', 0.6) - 0.3 },
    ];
    bars.forEach(b => {
      const lab = W(c, D.g, b.lab, b.x, BY + 40, 30, b.tl, b.tl + 1.0, { align: 'center' });
      const tb = Math.max(lab.t1 + 0.1, b.tb);
      const col = column(c, D.g, b.x, BY - 3, BY - b.v * BH, BW, tb, ACC);
      W(c, D.g, b.val, b.x + BW / 2 + 16, BY - b.v * BH + 18, 50, col.t1 + 0.05, col.t1 + 0.6, { color: ACC });
      c.cue(tb, 'item');
    });
    D.note('改了答案的那些题里，草稿提到提示的比例 · 多种提示取平均 · Anthropic 2025', 440, 828, P('S05-55', '只有39', 0.9), { w: 900, size: 22 });
    const t56 = T('S05-56') + 0.05;
    c.handLine({ x0: 440, y0: TOP, x1: 1060, y1: TOP, at: t56, dur: 0.35, w: 3, color: SOFT, parent: D.g, cue: false });
    W(c, D.g, '100%', 424, TOP, 30, t56 + 0.2, t56 + 0.6, { align: 'right', color: SOFT });
    const tY = Math.max(t56 + 0.5, P('S05-56', '没有那个', 0.5) - 1.0);
    bars.forEach((b, i) => column(c, D.g, b.x, BY - b.v * BH - 8, TOP + 6, BW, tY + 0.25 * i, YEL));
    const np = W(c, D.g, '没提到', 1130, 480, 56, tY + 0.5, tY + 1.3);
    c.handArrow({ x0: np.x0 - 14, y0: 480, x1: 950, y1: 480, at: np.t1 + 0.05, dur: 0.25, w: 6, color: ACC, parent: D.g });
    const t57 = Math.max(np.t1 + 0.35, T('S05-57') - 0.4);
    const sa = W(c, D.g, '像样', 1210, 680, 60, t57, t57 + 0.6, { align: 'center' });
    neq(c, D.g, sa.x1 + 60, 680, 28, sa.t1 + 0.05);
    W(c, D.g, '说全了', sa.x1 + 120, 680, 60, sa.t1 + 0.5, sa.t1 + 1.3);
    D.out(fD.out);

    // ---- E（S05-58..59）研究者自己也说：选择题 · 场景比较刻意 · 只测了两家公司的模型
    const Ep = page(c);
    const fE = FL(c, 'S05-59', 0.6);   // 下一页开头的字在下一句中间才念到：晚一点擦，三条也提前写
    Ep.add(c.pointList({ x: CX - 470, y: 262, w: 940, size: 56, mark: 'dash', title: '研究者自己也说', at: Math.max(fD.in, T('S05-58') + 0.05),
      items: [
        { text: '这是选择题', at: P('S05-58', '选择题', 0.5) - 0.6 },
        { text: '场景比较刻意', at: P('S05-58', '刻意', 0.8) - 0.7 },
        { text: '只测了两家公司的模型', at: P('S05-59', '只测了', 0.3) - 0.5, sub: 'Anthropic 和 DeepSeek' },
      ] }));
    Ep.out(fE.out);

    // ---- F（S05-60..62）可以当线索（看错题？用错条件？→ 补清条件再问）；不能当证明（答案自己核对）
    const F = page(c);
    const t60 = Math.max(fE.in, P('S05-60', '当成线索', 0.2) - 1.0);
    c.handCheck({ x: 250, y: 320, size: 56, at: t60, parent: F.g });
    const lh = W(c, F.g, '可以：当线索', 300, 320, 64, t60 + 0.25, t60 + 1.5);
    const i1 = Math.max(lh.t1 + 0.1, P('S05-60', '看错题', 0.6) - 1.0), i2 = Math.max(i1 + 1.2, P('S05-60', '用错条件', 0.8) - 1.0);
    c.handDash({ x: 310, y: 444, len: 26, at: i1, parent: F.g });
    W(c, F.g, '有没有看错题', 352, 440, 50, i1 + 0.12, i2 - 0.05);
    c.handDash({ x: 310, y: 534, len: 26, at: i2, parent: F.g });
    W(c, F.g, '有没有用错条件', 352, 530, 50, i2 + 0.12, i2 + 1.6);
    const t61 = Math.max(i2 + 1.7, T('S05-61') + 0.05);
    W(c, F.g, '→ 补清条件，再问一遍', 310, 640, 50, t61, t61 + 2.2, { color: ACC });
    const t62 = T('S05-62') + 0.05;
    cross(c, F.g, 1050, 320, 24, t62);
    W(c, F.g, '不能：当证明', 1100, 320, 64, t62 + 0.3, Math.max(t62 + 1.9, P('S05-62', '到底对不对', 0.5)));
    const t62b = Math.max(t62 + 2.0, P('S05-62', '自己去核对', 0.8) - 0.6);
    const ck = W(c, F.g, '答案自己核对', 1100, 460, 56, t62b, t62b + 1.3);
    c.handMark(ck, 0, 6, { kind: 'circle', at: ck.t1 + 0.05 });
  });

  // ================================================================== S06 三、什么时候该点
  ENG.scene('S06', c => {
    const P = (id, ph, fr = 0) => c.P(SG(id), ph, fr);
    c.autoTitle(SG('S06-63'));

    // ---- A（S06-64..71）适合点开 ✓ / 一般不用点 ✗；要算好几步、一口气答容易错（脱口而出）；拿不准先不点
    const A = page(c);
    const fA = FL(c, 'S06-71');
    A.add(c.pointList({ x: 230, y: 262, w: 700, size: 52, mark: 'check', title: '适合点开', at: T('S06-64') + 0.05,
      items: [
        { text: '数学 · 写代码', at: P('S06-64', '数学', 0.3) - 0.25 },
        { text: '多步推理 · 复杂分析', at: P('S06-64', '多步推理', 0.6) - 0.3 },
      ] }));
    // S06-66..68：要算好几步（一串小方块）；想一步完成 → 一支红箭头直接跳到最后，打叉；脱口而出：快，但容易错
    const cy = 628, cx0 = 250, gc = 130;
    const tCh = T('S06-66') + 0.05;
    for (let i = 0; i < 5; i++) {
      const x = cx0 + i * gc, at = tCh + 0.28 * i;
      if (i) c.handArrow({ x0: x - gc + 58, y0: cy, x1: x - 10, y1: cy, at: at - 0.14, dur: 0.14, w: 4, color: SOFT, parent: A.g, cue: false });
      c.handRect({ x0: x, y0: cy - 22, x1: x + 44, y1: cy + 22, at, dur: 0.2, w: 5, r: 8, parent: A.g, cue: false });
    }
    A.note('中间要算好几步，没法一步完成', 230, cy + 42, tCh + 1.4, { size: 22 });
    const tJ = Math.max(tCh + 1.6, P('S06-67', '一步完成', 0.4) - 0.3);
    c.handArrow({ x0: cx0 + 22, y0: cy - 50, x1: cx0 + 4 * gc + 22, y1: cy - 50, at: tJ, dur: 0.35, w: 6, color: RED, parent: A.g });
    cross(c, A.g, cx0 + 2 * gc + 22, cy - 50, 20, Math.max(tJ + 0.4, P('S06-67', '错的', 0.5) - 0.3));
    const tBl = Math.max(tJ + 0.8, P('S06-68', '脱口而出', 0.4) - 0.4);
    W(c, A.g, '脱口而出：快，但容易错', 230, 752, 42, tBl, tBl + 1.8, { color: RED });
    // S06-69：一般不用点
    A.add(c.pointList({ x: 1030, y: 262, w: 690, size: 52, mark: 'x', title: '一般不用点', at: T('S06-69') - 0.6,
      items: [
        { text: '简单事实问答', at: T('S06-69') + 0.3 },
        { text: '要得快的场景', at: P('S06-69', '快点回答', 0.7) - 0.3 },
      ] }));
    A.note('两栏出处：OpenAI、Anthropic 官方文档', 1030, 544, P('S06-69', '不用点', 0.9), { size: 22 });
    // S06-70..71：拿不准先不点，答得不对再点开重问（作者的建议）
    const t70 = T('S06-70') + 0.05;
    const k70 = W(c, A.g, '拿不准：先不点，问一遍', 1030, 666, 48, t70, t70 + 1.5);
    const t71 = Math.max(k70.t1 + 0.1, T('S06-71') - 0.4);
    const k71 = W(c, A.g, '→ 答得不对，点开再问', 1030, 756, 48, t71, t71 + 1.4, { color: ACC });
    A.note('作者的建议', 1030, 796, k71.t1 + 0.05, { size: 22 });
    A.out(fA.out);

    // ---- B（S06-72..76）论文：算 2 + 3 = ? 也想很久，提升很小；难题也有收益递减（手画曲线）
    const B = page(c);
    const fB = FL(c, 'S06-76');
    const t72 = Math.max(fA.in, T('S06-72') + 0.1);
    const hd = W(c, B.g, '2024 年底的论文 · 标题大意', 250, 356, 40, t72, t72 + 1.8);
    B.note('论文：Do NOT Think That Much for 2+3=? On the Overthinking of o1-Like LLMs（arXiv，2024-12）', CX - 750, 262, hd.t1, { w: 1500, align: 'center', size: 22 });
    const t73 = T('S06-73') + 0.05;
    const q23 = W(c, B.g, '算 2 + 3 = ?', 250, 452, 84, t73, t73 + 1.1);
    const tNo = Math.max(q23.t1 + 0.05, P('S06-73', '别想那么多', 0.3) - 0.3);
    W(c, B.g, '别想那么多', 250, 556, 60, tNo, tNo + 1.1, { color: ACC });
    const t74 = T('S06-74') + 0.05;
    const tLk = Math.max(t74, P('S06-74', '想很久', 0.5) - 0.4);
    const lk = W(c, B.g, '想很久', 250, 660, 50, tLk, tLk + 0.8);
    scribble(c, B.g, lk.x1 + 30, 636, 380, 3, 22, lk.t1 + 0.05, 0.15, { w: 5 });
    const tSm = Math.max(lk.t1 + 0.6, P('S06-74', '提升却很小', 0.5) - 0.3);
    W(c, B.g, '提升很小', 250, 750, 50, tSm, tSm + 1.0, { color: RED });
    B.note('论文实测 QwQ-32B-Preview、DeepSeek-R1 等 o1 这类模型', 250, 790, P('S06-74', '提升却很小', 0.9), { size: 22 });
    const GX = 1090, GY = 740, GW = 560, GH = 330;
    const t75 = T('S06-75') + 0.05;
    c.handLine({ x0: GX, y0: GY, x1: GX + GW, y1: GY, at: t75, dur: 0.25, w: 4, parent: B.g, cue: false });
    c.handLine({ x0: GX, y0: GY, x1: GX, y1: GY - GH, at: t75 + 0.12, dur: 0.25, w: 4, parent: B.g, cue: false });
    B.note('想得越多 →', GX + GW - 200, GY + 12, t75 + 0.3, { w: 200, align: 'right', size: 22 });
    B.note('↑ 提升', GX - 8, GY - GH - 38, t75 + 0.3, { size: 22 });
    const tcv = Math.max(t75 + 0.4, P('S06-75', '新增的提升', 0.3) - 0.4);
    const cp = [[GX + 8, GY - 16], [GX + 110, GY - 150], [GX + 230, GY - 222], [GX + 360, GY - 258], [GX + 480, GY - 274], [GX + 550, GY - 280]];
    for (let i = 0; i < cp.length - 1; i++) {
      c.handLine({ x0: cp[i][0], y0: cp[i][1], x1: cp[i + 1][0], y1: cp[i + 1][1], at: tcv + 0.15 * i, dur: 0.15, w: 7, color: ACC, parent: B.g, cue: false });
    }
    c.cue(tcv, 'chart');
    // 这句只有 2 秒、翻页紧跟着：句子一开始就写，免得刚写完就擦
    const t76 = Math.max(tcv + 0.8, T('S06-76') + 0.05);
    const sy = W(c, B.g, '收益递减', GX + 520, GY - GH + 10, 54, t76, t76 + 0.9, { align: 'right' });
    c.handUnderline({ x0: sy.x0 - 6, x1: sy.x1 + 8, y: sy.y1 + 12, at: sy.t1 + 0.05, parent: B.g });
    B.note('Anthropic 文档：思考预算越高，收益递减（随任务而异）', GX, GY + 48, sy.t1 + 0.1, { w: 620, size: 22 });
    B.out(fB.out);

    // ---- C（S06-77..81）多想 → 久等 → 花钱；草稿 = 输出 token；看不到也照样收；占着上下文窗口
    const C = page(c);
    const fC = FL(c, 'S06-81', 0.8);
    const chainW = ENG.handWidth('多想', 64) + ENG.handWidth('→ 久等', 64) + ENG.handWidth('→ 花钱', 64) + 60;
    const mx0 = CX - chainW / 2;
    const tM1 = Math.max(fB.in, P('S06-77', '想得越多', 0.2) - 0.2);
    const m1 = W(c, C.g, '多想', mx0, 304, 64, tM1, tM1 + 0.6);
    const tM2 = Math.max(m1.t1 + 0.1, P('S06-77', '等得就越久', 0.4) - 0.3);
    const m2 = W(c, C.g, '→ 久等', m1.x1 + 30, 304, 64, tM2, tM2 + 0.8);
    const tM3 = Math.max(m2.t1 + 0.1, P('S06-77', '花更多的钱', 0.5) - 0.3);
    const m3 = W(c, C.g, '→ 花钱', m2.x1 + 30, 304, 64, tM3, tM3 + 0.8, { color: RED });
    C.note('用 API 时', m3.x1 - 110, 340, m3.t1 + 0.05, { w: 110, align: 'right', size: 22 });
    const t78 = Math.max(m3.t1 + 0.2, P('S06-78', '草稿按输出', 0.4) - 0.3);
    W(c, C.g, '草稿 = 输出 token', CX, 424, 58, t78, t78 + 1.4, { align: 'center' });
    C.note('OpenAI、Anthropic 文档：思考用的 token 按输出 token 计费', CX - 500, 462, P('S06-78', '收费', 0.8), { w: 1000, align: 'center', size: 22 });
    const t79 = T('S06-79') + 0.05;
    const nv = W(c, C.g, '你看不到，也照样收', CX, 552, 56, t79, t79 + 1.6, { align: 'center' });
    c.handMark(nv, 6, 9, { kind: 'underline', at: nv.t1 + 0.05, color: 'rgba(216,52,42,.75)' });
    // 台词先说“草稿”、后说“上下文窗口”：框一画完先涂草稿，再写框的名字
    const t80 = Math.max(nv.t1 + 0.35, T('S06-80') - 0.5);
    const BX0 = 400, BX1 = 1520, BY0 = 624, BY1 = 820;
    c.handRect({ x0: BX0, y0: BY0, x1: BX1, y1: BY1, at: t80, dur: 0.5, w: 6, parent: C.g });
    const tFill = t80 + 0.45;
    scribble(c, C.g, BX0 + 30, BY0 + 94, 480, 3, 30, tFill, 0.15, { w: 9, color: FAINT });
    const dg = W(c, C.g, '草稿', BX0 + 30 + 490, BY0 + 124, 40, tFill + 0.45, tFill + 0.95, { color: ACC });
    const tCw = Math.max(dg.t1 + 0.1, P('S06-80', '上下文窗口', 0.3) - 1.0);
    const cw = W(c, C.g, '上下文窗口', BX0 + 30, BY0 + 42, 42, tCw, tCw + 0.9);
    const t81 = Math.max(cw.t1 + 0.1, T('S06-81') - 0.5);
    W(c, C.g, '= 一次能装下的内容上限', cw.x1 + 30, BY0 + 42, 40, t81, t81 + 1.5);
    C.note('OpenAI 文档：推理 token 占用上下文窗口', BX1 - 600, BY1 + 8, t81 + 1.0, { w: 600, align: 'right', size: 22 });
    C.out(fC.out);

    // ---- D（S06-82..83）这些厂商都能调思考的深浅；能调的话，简单题低一点，难题高一点
    const D = page(c);
    const t82 = Math.max(fC.in, T('S06-82') + 0.1);
    const SX0 = CX - 420, SX1 = CX + 420, SY = 480;
    W(c, D.g, '思考的深浅，可以调', CX, 320, 60, t82, Math.max(t82 + 1.6, T('S06-83') - 0.1), { align: 'center' });
    c.handLine({ x0: SX0, y0: SY, x1: SX1, y1: SY, at: t82 + 0.6, dur: 0.4, w: 8, parent: D.g });
    W(c, D.g, '不想', SX0, SY + 64, 44, t82 + 1.0, t82 + 1.5);
    W(c, D.g, '想很深', SX1, SY + 64, 44, t82 + 1.5, t82 + 2.2, { align: 'right' });
    D.note('DeepSeek：low / high / max · OpenAI：none … max · Claude：effort（最新的 Claude 还能让模型自己决定：自适应思考）', CX - 700, SY + 130, t82 + 1.8, { w: 1400, align: 'center', size: 22 });
    const t83a = Math.max(t82 + 2.3, P('S06-83', '简单题低', 0.3) - 0.3), t83b = Math.max(t83a + 1.0, P('S06-83', '难题高', 0.6) - 0.3);
    const ea = W(c, D.g, '简单题', SX0 + 170, SY - 92, 44, t83a, t83a + 0.8, { align: 'center' });
    c.handArrow({ x0: SX0 + 170, y0: SY - 62, x1: SX0 + 170, y1: SY - 16, at: ea.t1 + 0.05, dur: 0.2, w: 5, color: ACC, parent: D.g });
    const eb = W(c, D.g, '难题', SX1 - 130, SY - 92, 44, t83b, t83b + 0.6, { align: 'center' });
    c.handArrow({ x0: SX1 - 130, y0: SY - 62, x1: SX1 - 130, y1: SY - 16, at: eb.t1 + 0.05, dur: 0.2, w: 5, color: ACC, parent: D.g });
  });

  // ================================================================== S07 总结（手写，逐条出现；最后一句落款）
  ENG.scene('S07', c => {
    const sm = c.summary({
      items: [
        ['深度思考 = 打草稿', '复述题目 · 试做法 · 检查'],
        ['思考过程 = <span class="or">线索</span>', '直接返回的、摘要，都不等于全部原因'],
        ['难题点开 · 简单题不点', '草稿要花时间，用 API 还要花钱'],
      ],
      at: [T('S07-85') + 0.1, T('S07-88') + 0.1, T('S07-90') + 0.1],
      cardAt: T('S07-84') + 0.1,
      signAt: T('S07-92') + 0.1,
    });
    // S07-87：草稿越长，等得越久（写在第一条右边）
    const r0 = sm.rows[0].item, t87 = T('S07-87') + 0.05;
    c.handText('草稿越长 → 等得越久', r0.x1 + 56, (r0.y0 + r0.y1) / 2, { size: 36, at: t87, until: t87 + 1.6, color: ACC, parent: sm.el });
  });
})();
