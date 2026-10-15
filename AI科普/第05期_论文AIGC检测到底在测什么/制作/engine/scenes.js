/* 《原LAI如此》第 5 期「论文AIGC检测到底在测什么」— 白板手写版 scenes.js（v4，2026-09-30 晚）
 *
 * 依据：台本/script_data.py v4 的画面说明（用户改了开场，S04–S06 按用户口述重写；台词里不出现“鲸鱼娘”，形象和动作照旧）。
 *   说到的要点边说边手写（board.js / hand.js）：开场大字 c.bigWord、章节标题 c.autoTitle、结论 c.statement、总结 c.summary；
 *   开场五个问题用本文件的 questionList（五条问题飞进三行目录：1、2、4 → ①，3 → ②，5 → ③）；
 *   其余用 c.hand / c.handText / c.handNode / c.handArrow / c.handLine / c.handMark / c.handUnderline / c.handRect。
 *   “贴在白板上的东西”（检测报告示意、协议原文节选）是印刷体卡片 + c.tape()；出处、补充说明是印刷小字 .bNote。
 * 时间：全部按声音写（段号 / 台词短语，c.P）；画面整体提前 ENG.LEAD 秒由引擎做，这里不减。
 *   同一章里翻页用 c.flip(这一页最后一句)：这一页 out = f.out，下一页的东西 at 不早于 f.in。
 *   录音还没到时时间轴按字数估时长；录音到了重跑 build_timeline，这里不用改。
 * 坐标：1920×1080 内容舞台，居中版面（ENG.CX = 960）。标题占 y 60–220，内容 y 240–880、x 200–1720
 *   （左下讲解员：舞台 x ≤ 170；底部字幕：y ≥ 906；右上目录：舞台 x ≥ 1748 且 y ≤ 164）。
 * 品牌只写文字、不画 logo；报告、协议都标“示意 / 节选”。v3 留档：本期 _旧稿/scenes_v3_20260930.js。
 */
(function () {
  'use strict';
  if (!ENG.SCENES.length) return;
  const { E, EP } = ENG;
  const CX = ENG.CX;
  const HC = ENG.HAND || {};
  const ACC = HC.ACCENT || '#FF4F1A', INK = HC.INK || '#1A1A1A', RED = '#D8342A';
  const SOFT = 'rgba(26,26,26,.45)', GREY = 'rgba(26,26,26,.16)';

  // 调试（自查脚本用，成片不受影响）：页面有 window.__BOARD_LOG__ 时，记下每一行手写字开始 / 写完的时刻（场景时钟）
  if (Array.isArray(window.__BOARD_LOG__)) {
    const base = ENG.ctx;
    ENG.ctx = S => {
      const c = base(S), h0 = c.hand;
      c.hand = o => { const it = h0(o); window.__BOARD_LOG__.push({ scene: S.id, text: String(o.text), at: +o.at, t0: it.t0, t1: it.t1 }); return it; };
      return c;
    };
  }

  // ================================================================== 时间（声音时钟）
  const SG = id => ENG.segId(id);
  const T = id => SG(id).start;
  /** 段 id 里说到 phrase 的时刻（找不到用段内 frac 处，c.P 会 warn 并记进 ENG.phraseMiss） */
  const P = (c, id, phrase, frac = 0) => c.P(SG(id), phrase, frac);
  /** 翻页：这一页最后一句是 id -> {out, in}（场景时钟）。用户 2026-09-30：“让文字比声音的内容提前一秒出现”——
   *  c.flip 在这一句说完前 0.15 s 擦板，新一页的第一行只比下一句早 0.1 s；这里提前 1 秒翻：画面上在最后一句说完前
   *  1.1 s 擦板、0.8 s 开始写新一页，新一页的第一行比下一句早约 1 s（这一页的字照样早 1 秒写，最后一句大都已经写完）。 */
  const FL = (c, id) => { const out = SG(id).end + (ENG.LEAD || 0) - 1.1; return { out, in: out + 0.3 }; };

  // ================================================================== 小工具
  /** 印刷小字（出处、补充说明）：.bNote，默认 26 px（手机上不小于 24） */
  function note(c, html, x, y, at, o = {}) {
    const e = c.div('bNote', x, y, o.w != null ? o.w : null, null, html, o.parent);
    e.style.fontSize = (o.size || 26) + 'px';
    if (o.align) e.style.textAlign = o.align;
    if (o.color) e.style.color = o.color;
    return { el: e, tr: c.show(e, at, o.until, 4) };
  }
  /** 白板上的一页：一个手写组 + 要一起擦掉的东西（组件的 tr / block、印刷卡片的 Track），out(t) 整页擦掉 */
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
  /** 横条 / 竖条 = 一笔粗记号笔 */
  const stroke = (c, g, x0, y0, x1, y1, at, color, w = 22, dur) =>
    c.handLine({ x0, y0, x1, y1, at, dur: dur != null ? dur : Math.min(0.5, 0.12 + Math.hypot(x1 - x0, y1 - y0) / 1600), w, color, parent: g });
  /** 手画的红叉（中心 cx, cy，半宽 s） */
  function redX(c, g, cx, cy, s, at) {
    c.handLine({ x0: cx - s, y0: cy - s, x1: cx + s, y1: cy + s, at, dur: 0.1, w: s * 0.26, color: RED, parent: g, cue: false });
    return c.handLine({ x0: cx + s, y0: cy - s, x1: cx - s, y1: cy + s, at: at + 0.12, dur: 0.1, w: s * 0.26, color: RED, parent: g, cue: false });
  }
  /** 手画的大括号 }（x 是竖线，开口朝左）：上钩、竖线、中间尖、下钩 */
  function brace(c, g, x, y0, y1, at, color = SOFT) {
    const ym = (y0 + y1) / 2, o = { w: 4, color, parent: g, cue: false };
    c.handLine(Object.assign({ x0: x - 22, y0, x1: x, y1: y0 + 18, at, dur: 0.1 }, o));
    c.handLine(Object.assign({ x0: x, y0: y0 + 18, x1: x, y1: ym - 14, at: at + 0.1, dur: 0.15 }, o));
    c.handLine(Object.assign({ x0: x, y0: ym - 14, x1: x + 18, y1: ym, at: at + 0.25, dur: 0.08 }, o));
    c.handLine(Object.assign({ x0: x + 18, y0: ym, x1: x, y1: ym + 14, at: at + 0.33, dur: 0.08 }, o));
    c.handLine(Object.assign({ x0: x, y0: ym + 14, x1: x, y1: y1 - 18, at: at + 0.41, dur: 0.15 }, o));
    return c.handLine(Object.assign({ x0: x, y0: y1 - 18, x1: x - 22, y1, at: at + 0.56, dur: 0.1 }, o));
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
  /** 卡片里的灰色“文字行”（示意报告正文）；flag 的几行涂浅红 = 被标成疑似 AI */
  function textLines(c, parent, x, y, widths, step, flag = []) {
    widths.forEach((w, i) => {
      const l = c.div('', x, y + i * step, w, 12, '', parent);
      Object.assign(l.style, { background: flag.includes(i) ? 'rgba(216,52,42,.38)' : '#D6D1C7', borderRadius: '6px' });
    });
  }
  /** 元素在舞台上的外框（搭场景时量，轨道还没动它；页面坐标减 ENG.OX） */
  function rectOf(e, pad = 0) {
    const r = e.getBoundingClientRect();
    return { x0: r.left - ENG.OX - pad, y0: r.top - pad, x1: r.right - ENG.OX + pad, y1: r.bottom + pad };
  }
  /** 卡片里某个 <span>（按文字找）在舞台上的外框 */
  function spanRect(root, text, pad = 4) {
    const sp = [...root.querySelectorAll('span')].find(s => s.textContent.trim() === text);
    if (!sp) { console.warn('scenes.js spanRect: no span ' + text); return null; }
    return rectOf(sp, pad);
  }
  /** 实心小圆点（时间线上的一个版本） */
  function dot(c, pg, x, y, r, at, color = ACC) {
    const d = c.div('', x - r, y - r, 2 * r, 2 * r, '');
    Object.assign(d.style, { borderRadius: '50%', background: color });
    pg.add(c.show(d, at, null, 0, 0.2));
    return d;
  }
  /** 小检测报告卡（示意）：kicker + 名字 + 大数字 + 几行灰线 */
  function miniReport(c, x, y, w, h, name, num, o = {}) {
    const cd = paper(c, x, y, w, h, { kicker: o.kicker || 'REPORT', shiyi: true, tape: o.tape || 0 });
    txt(c, cd, 28, 50, name, '700 26px var(--cjk)', { color: 'var(--grey)' });
    txt(c, cd, 26, 84, num, '900 68px var(--cjk)', { color: o.color || RED, lh: 76 });
    textLines(c, cd, 28, 176, [w - 64, w - 96, w - 80], 22, o.flag || []);
    return cd;
  }
  /** 手画的「≠」（中心 cx, cy，半宽 s） */
  function neq(c, g, cx, cy, s, at, color = RED) {
    c.handLine({ x0: cx - s, y0: cy - s * 0.32, x1: cx + s, y1: cy - s * 0.32, at, dur: 0.12, w: 7, color, parent: g, cue: false });
    c.handLine({ x0: cx - s, y0: cy + s * 0.32, x1: cx + s, y1: cy + s * 0.32, at: at + 0.15, dur: 0.12, w: 7, color, parent: g, cue: false });
    return c.handLine({ x0: cx + s * 0.45, y0: cy - s * 0.95, x1: cx - s * 0.45, y1: cy + s * 0.95, at: at + 0.32, dur: 0.14, w: 7, color, parent: g });
  }
  /** 开场的问题清单（手写，念到哪条写哪条），说完缩小飞进右上目录：map[i] = 第 i 条飞进目录的第几行。
   *  做法同 board.js 的 c.questionCards，只是条数（5）和目录行数（3）不一样：几条可以飞进同一行。 */
  function questionList(c, items, at, map, o = {}) {
    const n = items.length, tIn = ENG.tocInTime();
    const g = c.handGroup();
    const ta = o.titleAt != null ? o.titleAt : at[0] - 0.9;
    const tt = c.handText(o.title || '今天讲清楚', CX, 196, { size: 72, align: 'center', at: ta,
      until: Math.max(ta + 0.5, Math.min(ta + 1.2, at[0] - 0.05)), seed: 'q-title', parent: g });
    c.handUnderline({ x0: tt.x0 - 6, x1: tt.x1 + 10, y: tt.y1 + 18, at: tt.t1 + 0.03, dur: 0.3, parent: g });
    const size = o.size || 54, y0 = o.y0 || 330, step = o.step || 104;
    const bw = Math.max(...items.map(q => ENG.handWidth(q, size))) + size * 1.15;
    const x = Math.round(CX - bw / 2);
    items.forEach((q, i) => {
      const y = y0 + i * step, row = c.handGroup(g);
      const num = c.hand({ text: String(i + 1), x, y, size, color: ACC, at: at[i], until: at[i] + 0.25, seed: 'qn' + i, parent: row, cue: false });
      const next = i + 1 < n ? at[i + 1] : tIn;
      const t0 = num.t1 + 0.03;
      const tx = c.handText(q, x + size * 1.15, y, { size, maxW: bw - size * 1.15, at: t0,
        until: Math.max(t0 + 0.6, Math.min(t0 + 1.8, next - 0.1)), seed: 'q' + i, parent: row, cue: false });
      c.cue(at[i], 'question');
      const bx0 = Math.min(num.x0, tx.x0), by0 = Math.min(num.y0, tx.y0), bx1 = Math.max(num.x1, tx.x1), by1 = Math.max(num.y1, tx.y1);
      const r = ENG.tocRowRect(map[i]), s = Math.min((r.w - 44) / Math.max(1, bx1 - bx0), 22 / Math.max(1, by1 - by0));
      Object.assign(row.style, { transformBox: 'fill-box', transformOrigin: '0 0' });
      row.setAttribute('data-fly', String(tIn));
      c.T(row, { o: 1 }).to(tIn, { x: r.x + 36 - bx0, y: r.y + 2 - by0, s }, 0.7, E.inOut).to(tIn + 0.4, { o: 0 }, 0.3, E.sine);
    });
    g.setAttribute('data-out', String(tIn + 0.4));
    c.T(g, { o: 1 }).to(tIn + 0.4, { o: 0 }, 0.3, E.sine);
    return { tIn };
  }

  // ================================================================== S01 开场：手写大字「AIGC 检测」
  ENG.scene('S01', c => {
    // 念到「大家好」时开始写（画面早 1 秒）：说到「论文里的 AIGC 检测」时大字已经写完
    const at = P(c, 'S01-01', '今天想', 0.3) - 0.3;
    c.bigWord({ text: 'AIGC 检测', kicker: `原LAI如此 · #${ENG.pad2(EP.number)}`, at,
      sub: '论文 <span class="or">AI 率</span> · 到底在测什么' });
  });

  // ================================================================== S02 五个问题
  ENG.scene('S02', c => {
    // ---- A（S02-02）：大四、研三头疼 → 三个网站三个分数（示意）≠ 学校的检测 → 反复测，白花冤枉钱
    const A = page(c);
    const tHd = P(c, 'S02-02', '大四', 0.1) - 0.3;
    W(c, A.g, '大四、研三：头疼 AIGC 检测', CX, 298, 52, tHd, tHd + 2.2, { align: 'center' });
    c.cue(tHd, 'item');
    const CY = 392, CW = 250, CH = 232;
    const tWeb = P(c, 'S02-02', '不同的网址', 0.3) - 0.3;
    [['网站 A', '43%', 300], ['网站 B', '18%', 580], ['网站 C', '61%', 860]].forEach(([nm, v, x], i) => {
      const cd = miniReport(c, x, CY, CW, CH, nm, v, { tape: i });
      A.add(c.show(cd, tWeb + 0.45 * i, null, 10));
      c.cue(tWeb + 0.45 * i, 'card');
    });
    const tSch = P(c, 'S02-02', '学校官网', 0.6) - 0.3;
    const sc = miniReport(c, 1270, CY - 10, 300, CH + 20, '学校指定的系统', '29%', { kicker: 'SCHOOL', color: INK, tape: 1 });
    A.add(c.show(sc, tSch, null, 10));
    c.cue(tSch, 'card');
    const tNe = P(c, 'S02-02', '不一样', 0.75) - 0.3;
    neq(c, A.g, 1195, CY + CH / 2, 34, tNe);
    // 底下一行分两段写：“反复测”跟着“反复检测”，“→ 白花冤枉钱”在长句快说完前写完（这一句说完就翻页）
    const MS = 54, MT = '反复测 → 白花冤枉钱', mx0 = CX - ENG.handWidth(MT, MS) / 2;
    const tRe = P(c, 'S02-02', '反复检测', 0.5) - 0.3;
    W(c, A.g, '反复测', mx0, 780, MS, tRe, tRe + 0.9);
    const tMoney = P(c, 'S02-02', '白白花了', 0.85) - 1.0;
    const mn = W(c, A.g, '→ 白花冤枉钱', mx0 + ENG.handWidth('反复测 ', MS), 780, MS, tMoney, tMoney + 1.2);
    c.handMark(mn, 2, 7, { kind: 'underline', color: RED, w: 6 });
    c.cue(tRe, 'item');
    A.note('网站和分数都是示意', CX - 200, 668, tWeb + 1.4, { w: 400, align: 'center', size: 24 });
    c.cue(tMoney, 'item');
    const f = FL(c, 'S02-02');
    A.out(f.out);

    // ---- B（S02-03..07）：手写「今天讲清楚」+ 五个问题；说完缩小飞进右上目录（1、2、4 → ①，3 → ②，5 → ③）
    questionList(c,
      ['AIGC是什么？', 'AI率是什么？', 'AI在检测什么？', '为什么和学校测的不一样？', 'AI率太高怎么办？'],
      [P(c, 'S02-03', 'AIGC到底', 0.6), T('S02-04') + 0.05, T('S02-05') + 0.05, T('S02-06') + 0.05, T('S02-07') + 0.05],
      [0, 0, 1, 0, 2], { titleAt: f.in, title: '今天讲清楚' });
  });

  // ================================================================== S03 一、AI率是什么
  ENG.scene('S03', c => {
    c.autoTitle(SG('S03-08'));

    // ---- A（S03-09..14）大河报记者实验：《荷塘月色》→ 检测系统 → 62.88%；AIGC = AI 生成内容；2026 年 5 月又上热搜
    const A = page(c);
    const tHd = T('S03-09') + 0.05;
    const HD = '2025 年 5 月 · 大河报记者做实验', HS = 44;
    W(c, A.g, HD, CX, 292, HS, tHd, tHd + 2.0, { align: 'center' });
    c.cue(tHd, 'item');
    const chip = c.chip('2026 年 5 月又上热搜', CX + ENG.handWidth(HD, HS) / 2 + 28, 268, { kind: 'o', at: T('S03-13') + 0.1 });
    A.add(chip.tr);

    const RY = 440;
    const tBk = P(c, 'S03-10', '荷塘月色', 0.2) - 0.3;
    const bk = W(c, A.g, '《荷塘月色》', 470, RY, 60, tBk, tBk + 1.6, { align: 'center' });
    A.note('朱自清 · 1927 · 节选', 470 - 200, RY + 40, P(c, 'S03-10', '片段', 0.4), { w: 400, align: 'center' });
    const tNd = P(c, 'S03-10', '论文检测系统', 0.7) - 0.3;
    c.handArrow({ x0: bk.x1 + 18, y0: RY, x1: 784, y1: RY, at: tNd - 0.2, dur: 0.3, parent: A.g });
    A.add(c.handNode({ x: 800, y: RY - 70, w: 320, h: 140, text: '检测系统', size: 52, at: tNd, parent: A.g }));
    const t11 = T('S03-11') + 0.05;
    W(c, A.g, '哪一个？报道没说', 960, RY + 112, 34, t11, t11 + 1.4, { align: 'center', color: ACC });
    const tNum = P(c, 'S03-12', '62.88', 0.45) - 0.5;
    c.handArrow({ x0: 1138, y0: RY, x1: 1262, y1: RY, at: tNum - 0.3, dur: 0.3, parent: A.g });
    const num = W(c, A.g, '62.88%', 1480, RY, 100, tNum, tNum + 1.1, { align: 'center', color: RED });
    c.handMark(num, 0, 6, { kind: 'circle', at: num.t1 + 0.05 });
    A.note('AI 生成内容总体疑似度', 1480 - 240, 538, P(c, 'S03-12', '总体疑似度', 0.5), { w: 480, align: 'center' });
    const tAI = P(c, 'S03-12', '也就是', 0.7) - 0.2;
    W(c, A.g, '= AI 率', 1480, 618, 52, tAI, tAI + 0.9, { align: 'center' });
    // 开场问了“AIGC 到底是一个什么东西”，台词没有单独答：在这里写出来（AI 生成内容 = AIGC）。
    // 跟着“结果显示”先写（比说到“AI生成内容”早），写完再写 62.88%，一支笔不同时写两处
    const tG = Math.min(T('S03-12') - 0.2, tNum - 1.2);
    const gl = W(c, A.g, 'AIGC = AI 生成内容', CX, 748, 56, tG, tG + 0.9, { align: 'center' });
    c.handMark(gl, 0, 4, { kind: 'underline' });
    A.note('Artificial Intelligence Generated Content', CX - 400, 790, gl.t1, { w: 800, align: 'center', size: 24 });
    const t14 = T('S03-14') + 0.05;
    W(c, A.g, '不可能是 AI 写的', 470, 580, 44, t14, t14 + 1.6, { align: 'center' });
    [tBk, tNd, t11, tNum, tAI, tG, t14].forEach(t => c.cue(t, 'item'));
    const f1 = FL(c, 'S03-14');
    A.out(f1.out);

    // ---- B（S03-15..17）知网协议原文（印刷体节选，贴胶带）：念到哪句出哪句，框出「概率」「仅供参考」
    const B = page(c);
    const t15 = Math.max(f1.in, T('S03-15') + 0.05);
    W(c, B.g, '知网的协议写得很清楚', CX, 298, 56, t15, t15 + 1.8, { align: 'center' });
    B.note('知网毕业论文（设计）管理系统 AIGC 检测服务用户体验协议 · V1.0 · 2023-07', CX - 700, 340, t15 + 1.2, { w: 1400, align: 'center', size: 24 });
    c.cue(t15, 'item');
    const QX = CX - 680, QY = 410, QW = 1360, QH = 330;
    const qc = paper(c, QX, QY, QW, QH, { kicker: 'QUOTE · 协议原文（节选）', tape: 1 });
    txt(c, qc, 40, 70, '检测结果中的AIGC值表示的是文章内容存在AI生成的<span>概率</span>大小，<br>与文章质量无关。', '800 38px var(--cjk)', { lh: 62 });
    const q2 = txt(c, qc, 40, 222, '……因此可能存在漏检或误检，检测结果<span>仅供参考</span>。', '800 38px var(--cjk)', { lh: 62 });
    const tQ1 = T('S03-16') + 0.05, tQ2 = T('S03-17') + 0.05;
    B.add(c.show(qc, tQ1, null, 10));
    c.show(q2, tQ2, null, 6);
    c.cue(tQ1, 'card'); c.cue(tQ2, 'item');
    // 行距只有 62：c.handEllipse 的圈会外扩盖住左右的字，用贴身的手画框
    const rP = spanRect(qc, '概率', 5), rR = spanRect(qc, '仅供参考', 5);
    if (rP) c.handRect(Object.assign(rP, { at: P(c, 'S03-16', '概率', 0.6) - 0.1, dur: 0.35, color: ACC, w: 5, r: 10, parent: B.g }));
    if (rR) c.handRect(Object.assign(rR, { at: P(c, 'S03-17', '仅供参考', 0.8) - 0.1, dur: 0.35, color: ACC, w: 5, r: 10, parent: B.g }));
    const f2 = FL(c, 'S03-17');
    B.out(f2.out);

    // ---- C（S03-18..21）换个系统，数字就变：同一篇论文 → 三个系统（横条）→ 结论
    const C = page(c);
    const t18 = Math.max(f2.in, T('S03-18') + 0.05);
    W(c, C.g, '换个系统，数字就变', CX, 298, 58, t18, t18 + 1.8, { align: 'center' });
    C.note('每家的算法和口径不一样', CX - 300, 340, P(c, 'S03-18', '口径', 0.4), { w: 600, align: 'center' });
    c.cue(t18, 'item');
    const tPa = P(c, 'S03-19', '同一篇论文', 0.5) - 0.3;
    const nd = C.add(c.handNode({ x: 240, y: 452, w: 300, h: 140, text: '同一篇论文', size: 44, at: tPa, parent: C.g }));
    C.note('IT时报 2025-04 报道', 240, 604, tPa + 1.0, { w: 300, align: 'center', size: 24 });
    const LX = 640, BX = 900, K = 12, RY0 = 432, RS = 92;
    const tFan = P(c, 'S03-19', '送进了', 0.7) - 0.2;
    [['PaperYY', 50], ['PaperPass', 30], ['知网', 25]].forEach(([lab, v], i) => {
      const y = RY0 + i * RS;
      c.handArrow({ x0: nd.x1 + 14, y0: 522, x1: LX - 18, y1: y, at: tFan + 0.15 * i, dur: 0.3, w: 5, color: SOFT, parent: C.g });
      const at = P(c, 'S03-20', lab, 0.3 * i) - 0.25;
      W(c, C.g, lab, LX, y, 40, at, at + 0.6);
      stroke(c, C.g, BX, y, BX + v * K, y, at + 0.35, INK, 24);
      W(c, C.g, v + '%', BX + v * K + 24, y, 44, at + 0.65, at + 1.0, { color: ACC });
      c.cue(at, 'item');
    });
    // 章末最后一句：留到说完才擦（core.js boardPlan），提前一点写
    const t21 = T('S03-21') - 0.2;
    C.add(c.statement({ y: 690, size: 56, main: 'AI 率 = <span class="or">某个系统</span>打的分', at: t21, mainAt: t21 }));
  });

  // ================================================================== S04 二、检测在测什么
  ENG.scene('S04', c => {
    c.autoTitle(SG('S04-22'));

    // ---- A（S04-23..26）检测看三个方面：① 猜下一个字（语言模型读一句话，每个字一根“猜中把握”竖条）→ 越好猜越像 AI 写的
    const A = page(c);
    const t23 = P(c, 'S04-23', '三个方面', 0.3) - 0.3;
    W(c, A.g, '检测看三个方面：', 240, 288, 46, t23, t23 + 1.4);
    const t24 = P(c, 'S04-24', '第一个', 0.05) - 0.2;
    W(c, A.g, '① 猜下一个字', 240, 370, 58, t24, t24 + 1.2);
    const tLM = P(c, 'S04-24', '语言模型', 0.2) - 0.3;
    A.add(c.handNode({ x: 1260, y: 250, w: 440, h: 124, text: '语言模型', sub: 'LLM · 豆包、ChatGPT 这类', size: 46, at: tLM, parent: A.g }));
    c.cue(t23, 'item'); c.cue(t24, 'item');
    const DEMO = '我觉得这个结论还需要更多数据';
    const PROB = [0.22, 0.8, 0.95, 0.42, 0.86, 0.38, 0.9, 0.3, 0.5, 0.92, 0.45, 0.84, 0.48, 0.95];
    const DY = 490, DS = 58;
    const tDm = P(c, 'S04-24', '去读你的文章', 0.7) - 0.5;
    const dm = W(c, A.g, DEMO, CX, DY, DS, tDm, tDm + 2.2, { align: 'center' });
    c.handArrow({ x0: 1470, y0: 388, x1: Math.min(dm.x1 + 10, 1400), y1: DY - 44, at: tDm - 0.15, dur: 0.3, w: 5, color: SOFT, parent: A.g, cue: false });
    c.cue(tDm, 'item');
    const BASE = 662, BH = 116;
    const tBar = P(c, 'S04-25', '先猜', 0.4) - 0.3;
    c.handLine({ x0: dm.x0 - 14, y0: BASE + 4, x1: dm.x1 + 14, y1: BASE + 4, at: tBar - 0.2, dur: 0.3, w: 3, color: SOFT, parent: A.g, cue: false });
    [...DEMO].forEach((ch, i) => {
      const bx = dm.box(i, i + 1);
      if (!bx) return;
      const x = (bx[0] + bx[2]) / 2;
      stroke(c, A.g, x, BASE, x, BASE - Math.round(BH * PROB[i]), tBar + 0.12 * i, PROB[i] > 0.7 ? ACC : 'rgba(255,79,26,.42)', 20, 0.12);
    });
    A.note('每根竖条 = 模型猜中这个字的把握（示意）', CX - 400, BASE + 16, tBar + 0.6, { w: 800, align: 'center' });
    c.cue(tBar, 'chart');
    const t26 = P(c, 'S04-26', '猜得准', 0.1) - 0.2;
    const g26 = W(c, A.g, '猜得准 → 越好猜 → 越像 AI 写的', CX - 70, 786, 50, t26, P(c, 'S04-26', '越像是AI写', 0.8) + 0.3, { align: 'center' });
    c.handMark(g26, 12, 20, { kind: 'underline' });
    A.note('困惑度（Perplexity）低', g26.x1 + 22, 770, g26.t1);
    c.cue(t26, 'item');
    const fA = FL(c, 'S04-26');
    A.out(fA.out);

    // ---- B（S04-27..31）② 看起伏（左：每条线 = 一句话的长短）｜ ③ 训练分类模型（右）→ 变成黑盒 → 让人觉得被冤枉
    const B = page(c);
    const t27 = Math.max(fA.in, P(c, 'S04-27', '第二种', 0.3) - 0.3);
    W(c, B.g, '② 看起伏', 240, 300, 60, t27, t27 + 1.1);
    c.cue(t27, 'item');
    const HUM = [430, 150, 350, 90, 270], AIL = [300, 285, 312, 292, 305];
    const tH = P(c, 'S04-28', '人在写东西', 0.2) - 0.3, tAi = P(c, 'S04-28', 'AI写的', 0.6) - 0.3;
    W(c, B.g, '人', 268, 452, 48, tH, tH + 0.4, { align: 'center' });
    HUM.forEach((w, i) => stroke(c, B.g, 330, 400 + i * 26, 330 + w, 400 + i * 26, tH + 0.3 + 0.1 * i, INK, 12, 0.14));
    W(c, B.g, '起伏大', 800, 452, 40, tH + 0.9, tH + 1.6, { color: ACC });
    W(c, B.g, 'AI', 268, 662, 48, tAi, tAi + 0.4, { align: 'center' });
    AIL.forEach((w, i) => stroke(c, B.g, 330, 610 + i * 26, 330 + w, 610 + i * 26, tAi + 0.3 + 0.1 * i, SOFT, 12, 0.14));
    W(c, B.g, '更平均', 800, 662, 40, tAi + 0.9, tAi + 1.6, { color: ACC });
    B.note('AI 是概率模型', 800, 692, P(c, 'S04-28', '概率模型', 0.3), { size: 24 });
    B.note('每条线 = 一句话的长短（示意）', 240, 764, tAi + 1.2);
    c.cue(tH, 'item'); c.cue(tAi, 'item');

    const t29 = P(c, 'S04-29', '第三类', 0.3) - 0.3;
    c.handLine({ x0: 985, y0: 270, x1: 985, y1: 800, at: t29 - 0.15, dur: 0.35, w: 3, color: SOFT, parent: B.g, cue: false });
    W(c, B.g, '③ 训练分类模型', 1030, 300, 54, t29, t29 + 1.4);
    const tHw = P(c, 'S04-29', '大量人写的', 0.3) - 0.2, tAw = P(c, 'S04-29', 'AI写的', 0.5) - 0.2;
    W(c, B.g, '人写的', 1040, 444, 40, tHw, tHw + 0.8);
    W(c, B.g, 'AI 写的', 1040, 580, 40, tAw, tAw + 0.8);
    const tNd = P(c, 'S04-29', '训练一个模型', 0.6) - 0.3;
    const nd = c.handNode({ x: 1250, y: 432, w: 250, h: 160, text: '分类模型', size: 44, at: tNd, parent: B.g });
    c.handArrow({ x0: 1192, y0: 448, x1: 1238, y1: 490, at: tNd - 0.1, dur: 0.25, w: 5, parent: B.g, cue: false });
    c.handArrow({ x0: 1200, y0: 576, x1: 1238, y1: 540, at: tNd, dur: 0.25, w: 5, parent: B.g, cue: false });
    const tSc = P(c, 'S04-29', '给出一个分数', 0.8) - 0.3;
    c.handArrow({ x0: nd.x1 + 12, y0: 512, x1: 1580, y1: 512, at: tSc, dur: 0.25, w: 6, color: ACC, parent: B.g });
    W(c, B.g, '分数', 1592, 512, 46, tSc + 0.25, tSc + 0.9, { color: ACC });
    c.cue(tHw, 'item'); c.cue(tNd, 'node'); c.cue(tSc, 'item');
    // S04-30：分类模型变成黑盒（深色块盖住框，框里的字淡掉，写白色问号）
    const t30 = P(c, 'S04-30', '具体的算法', 0.3) - 0.3;
    const bb = c.div('', nd.x0 - 6, nd.y0 - 6, (nd.x1 - nd.x0) + 12, (nd.y1 - nd.y0) + 12, '');
    Object.assign(bb.style, { background: '#1A1A1A', borderRadius: '18px' });
    B.add(c.T(bb, { o: 0 }).to(t30, { o: 0.95 }, 0.35));
    nd.text.out(t30 + 0.1);
    W(c, B.g, '？', (nd.x0 + nd.x1) / 2, (nd.y0 + nd.y1) / 2, 92, t30 + 0.5, t30 + 0.8, { align: 'center', color: '#FFFFFF' });
    B.note('各家商业系统的算法都没公开', nd.x0 - 50, nd.y1 + 20, t30 + 0.5, { w: 350, align: 'center', size: 24 });
    c.cue(t30, 'item');
    const t31 = T('S04-31') - 0.3;             // 这一页最后一句：提前翻页（FL）前要写完、看清
    const g31 = W(c, B.g, '黑盒 → 让人觉得被冤枉', 1030, 724, 44, t31, t31 + 1.3);
    c.handMark(g31, 7, 12, { kind: 'underline', color: RED, w: 5 });
    c.cue(t31, 'item');
    const fB = FL(c, 'S04-31');
    B.out(fB.out);

    // ---- C（S04-32..47）左栏：哪些文字 AI 率容易高（写到这一章结束）｜ 右边按原因翻三页
    const L = c.handGroup();
    const t32 = Math.max(fB.in, P(c, 'S04-32', '有哪些文章', 0.1) - 0.2);
    const lh = W(c, L, '哪些文字 AI 率容易高？', 232, 300, 44, t32, t32 + 1.8);
    c.handUnderline({ x0: lh.x0 - 6, x1: lh.x1 + 10, y: lh.y1 + 14, at: lh.t1 + 0.05, parent: L });
    c.handLine({ x0: 700, y0: 380, x1: 700, y1: 860, at: lh.t1 + 0.1, dur: 0.35, w: 3, color: SOFT, parent: L, cue: false });
    c.cue(t32, 'item');
    [['① 很有名的文章', 'S04-33', '很有名', 420], ['② 规范、用词简单', 'S04-37', '规范', 540], ['③ 检测是黑盒、有误差', 'S04-42', '黑盒', 660]].forEach(([t, id, ph, y]) => {
      const at = P(c, id, ph, 0.2) - 0.3;
      W(c, L, t, 240, y, 42, at, at + 1.4);
      c.cue(at, 'item');
    });

    // R1（S04-33..36）很有名的文章：「弥望的是田田的 __」→「叶」，每个字都猜得准；专家解读
    const R1 = page(c);
    const tMw = P(c, 'S04-33', '很有名的文章', 0.6) - 0.1;
    const mw = W(c, R1.g, '弥望的是田田的', 770, 420, 62, tMw, tMw + 1.6);
    const bx0 = mw.x1 + 16;
    c.handLine({ x0: bx0, y0: 456, x1: bx0 + 64, y1: 456, at: mw.t1 + 0.05, dur: 0.15, w: 5, color: INK, parent: R1.g, cue: false });
    const tYe = P(c, 'S04-34', '猜到下一个字', 0.5) - 0.3;
    const ye = W(c, R1.g, '叶', bx0 + 2, 420, 62, tYe, tYe + 0.4, { color: ACC });
    const tBs = P(c, 'S04-34', '一定', 0.4) - 0.3, BS = 590;
    const cols = [...'弥望的是田田的'].map((_, i) => mw.box(i, i + 1)).concat([ye.box(0, 1)]).filter(Boolean);
    cols.forEach((b, i) => { const x = (b[0] + b[2]) / 2; stroke(c, R1.g, x, BS, x, BS - Math.round(96 * (0.9 + 0.08 * ((i * 7) % 3) / 2)), tBs + 0.1 * i, ACC, 20, 0.12); });
    W(c, R1.g, 'AI 读过，猜得到', 1330, 420, 42, tYe + 0.4, tYe + 1.6, { color: ACC });
    R1.note('每个字都好猜（示意）', 770, BS + 16, tBs + 0.8);
    c.cue(tMw, 'item'); c.cue(tYe, 'item'); c.cue(tBs, 'chart');
    const t35 = T('S04-35') + 0.1;
    R1.note('西湖大学 鲍光胜（Fast-DetectGPT 作者之一）的解读', 770, 668, t35, { size: 24 });
    const tCl = P(c, 'S04-35', '经典文章', 0.4) - 0.3;
    W(c, R1.g, '经典文章：训练时就读过', 770, 740, 48, tCl, tCl + 1.9);
    const t36 = P(c, 'S04-35', '模型对这些', 0.8) - 0.3;
    const r36 = W(c, R1.g, '模型很熟 → 容易被判成 AI', 770, 830, 48, t36, t36 + 2.0);
    c.handMark(r36, 7, 15, { kind: 'underline' });
    c.cue(tCl, 'item'); c.cue(t36, 'item');
    const e1 = FL(c, 'S04-36');
    R1.out(e1.out);

    // R2（S04-37..41）规范、用词简单：专家；项目计划 97%（离谱）；斯坦福托福作文 61.3%
    const R2 = page(c);
    const t38 = Math.max(e1.in, P(c, 'S04-38', '有专家说', 0.1) - 0.2);
    W(c, R2.g, '专家：学术书面表达误判高发', 770, 330, 46, t38, t38 + 2.4);
    const t39 = P(c, 'S04-39', '项目计划', 0.3) - 0.3;
    const pj = W(c, R2.g, '项目计划 97%', 770, 452, 60, t39, t39 + 1.3);
    c.handMark(pj, 5, 8, { kind: 'circle', at: Math.max(pj.t1 + 0.05, P(c, 'S04-39', '97%', 0.6)) });
    const tLp = P(c, 'S04-39', '离谱', 0.9) - 0.4;
    W(c, R2.g, '离谱', pj.x1 + 70, 452, 52, tLp, tLp + 0.6, { color: RED });
    R2.note('学生自述是原创 · 连时间安排都被标出（科技日报 2026-05）', 770, 522, P(c, 'S04-39', '时间安排', 0.8) - 0.4, { size: 24 });
    const t40 = T('S04-40') + 0.05;
    W(c, R2.g, '斯坦福：测了 7 个检测器', 770, 620, 44, t40, t40 + 1.6);
    const t40b = P(c, 'S04-40', '非英语母语者', 0.3) - 0.2;
    const to = W(c, R2.g, '非母语托福作文：61.3% 被误判', 770, 706, 48, t40b, t40b + 2.4);
    c.handMark(to, 8, 13, { kind: 'circle', at: Math.max(to.t1 + 0.05, P(c, 'S04-40', '61.3', 0.6)) });
    R2.note('团队的结论 · Liang 等 · Patterns 2023', 770, 760, T('S04-41') + 0.1, { size: 24 });
    const t41 = T('S04-41') - 0.1;
    W(c, R2.g, '词汇、语法有限 → 更好猜', 770, 842, 44, t41, t41 + 1.4);
    [t38, t39, t40, t40b, t41].forEach(t => c.cue(t, 'item'));
    const e2 = FL(c, 'S04-41');
    R2.out(e2.out);

    // R3（S04-42..47）检测是黑盒、有误差：大模型在升级；没公开测试标准；OpenAI 自家检测器 100 段里认出 26 / 冤枉 9；2023 年 7 月下线
    const R3 = page(c);
    const t43 = Math.max(e2.in, P(c, 'S04-43', 'AI大模型', 0.4) - 0.3);
    W(c, R3.g, '大模型在升级 → 检测跟着改', 770, 320, 46, t43, t43 + 2.2);
    const t44 = P(c, 'S04-44', '没有公开', 0.3) - 0.3;
    const g44 = W(c, R3.g, '没公开测试标准', 770, 404, 46, t44, t44 + 1.4);
    c.handMark(g44, 0, 3, { kind: 'underline', color: RED, w: 5 });
    const t45 = P(c, 'S04-45', 'OpenAI', 0.05) - 0.3;
    W(c, R3.g, 'OpenAI 自家检测器', 770, 494, 50, t45, t45 + 1.4);
    const B0 = 1100, BL = 380;
    const tR1 = P(c, 'S04-45', '100段AI写的', 0.4) - 0.3;
    W(c, R3.g, '100 段 AI 写的', 770, 592, 40, tR1, tR1 + 1.0);
    stroke(c, R3.g, B0, 592, B0 + BL, 592, tR1 + 0.6, GREY, 24, 0.3);
    const tHit = P(c, 'S04-45', '只认出', 0.6) - 0.2;
    stroke(c, R3.g, B0, 592, B0 + BL * 0.26, 592, tHit, ACC, 24, 0.2);
    W(c, R3.g, '认出 26', B0 + BL + 24, 592, 40, tHit + 0.2, tHit + 0.9, { color: ACC });
    const tR2 = P(c, 'S04-46', '另外100段', 0.05) - 0.3;
    W(c, R3.g, '100 段人写的', 770, 682, 40, tR2, tR2 + 1.0);
    stroke(c, R3.g, B0, 682, B0 + BL, 682, tR2 + 0.6, GREY, 24, 0.3);
    const tFp = P(c, 'S04-46', '有9段', 0.7) - 0.2;
    stroke(c, R3.g, B0, 682, B0 + BL * 0.09, 682, tFp, RED, 24, 0.15);
    W(c, R3.g, '冤枉 9', B0 + BL + 24, 682, 40, tFp + 0.2, tFp + 0.8, { color: RED });
    R3.note('OpenAI 在英文“挑战集”上的自测 · 2023-01', 770, 730, tFp + 0.5, { size: 24 });
    const t47 = T('S04-47') + 0.05;
    const off = W(c, R3.g, '2023 年 7 月下线', 770, 822, 56, t47, t47 + 1.4, { color: RED });
    c.handMark(off, 10, 12, { kind: 'underline' });
    [t43, t44, t45, tR1, tHit, tR2, tFp, t47].forEach(t => c.cue(t, 'item'));
  });

  // ================================================================== S05 三、被判高了怎么办
  ENG.scene('S05', c => {
    c.autoTitle(SG('S05-48'));

    // ---- A（S05-49..52）导师给修改意见；导师审阅（一遍遍）→ AI 检测 → 报告标出疑似段落 → 对照原理，逆向斟酌句子
    const A = page(c);
    const t49 = P(c, 'S05-49', '导师会给', 0.1) - 0.3;
    W(c, A.g, '导师会给修改意见', 240, 296, 50, t49, t49 + 1.6);
    c.cue(t49, 'item');
    const NY = 404, NH = 140;
    const tRv = P(c, 'S05-50', '导师一遍遍', 0.2) - 0.3;
    const nA = A.add(c.handNode({ x: 240, y: NY, w: 320, h: NH, text: '导师审阅', size: 50, at: tRv, parent: A.g }));
    W(c, A.g, '一遍遍', 400, NY - 26, 30, tRv + 0.6, tRv + 1.2, { align: 'center', color: ACC });
    const tOk = P(c, 'S05-50', '导师同意了', 0.4) - 0.2;
    c.handArrow({ x0: nA.x1 + 14, y0: NY + NH / 2, x1: 686, y1: NY + NH / 2, at: tOk, dur: 0.3, parent: A.g });
    W(c, A.g, '同意了', 623, NY + NH / 2 - 30, 28, tOk + 0.2, tOk + 0.8, { align: 'center', color: SOFT });
    const tDet = P(c, 'S05-50', '进入AI检测', 0.7) - 0.3;
    const nB = A.add(c.handNode({ x: 700, y: NY, w: 280, h: NH, text: 'AI 检测', size: 50, at: tDet, parent: A.g }));
    const tRep = P(c, 'S05-51', '报告', 0.3) - 0.3;
    c.handArrow({ x0: nB.x1 + 14, y0: NY + NH / 2, x1: 1106, y1: NY + NH / 2, at: tRep - 0.2, dur: 0.3, parent: A.g });
    const mr = paper(c, 1120, 350, 380, 250, { kicker: 'REPORT', shiyi: true, tape: 2 });
    textLines(c, mr, 32, 66, [316, 280, 300, 250, 300], 30, [1, 3]);
    txt(c, mr, 32, 214, '标红 = 疑似段落（示意）', '500 20px var(--cjk)', { color: 'var(--grey)' });
    A.add(c.show(mr, tRep, null, 10));
    const tFlag = P(c, 'S05-51', '疑似的段落', 0.5) - 0.3;
    [1, 3].forEach((k, i) => c.handRect({ x0: 1140, y0: 350 + 66 + k * 30 - 10, x1: 1140 + 300, y1: 350 + 66 + k * 30 + 22, at: tFlag + 0.2 * i, dur: 0.3, color: ACC, w: 4, r: 8, parent: A.g, cue: false }));
    c.cue(tRv, 'node'); c.cue(tDet, 'node'); c.cue(tRep, 'card'); c.cue(tFlag, 'item');
    const t52 = T('S05-52') + 0.1;
    const g52 = W(c, A.g, '对照原理，逆向斟酌句子', CX, 720, 58, t52, t52 + 1.6, { align: 'center' });
    c.handMark(g52, 5, 7, { kind: 'underline' });
    A.note('好不好猜 · 起伏大不大 · 像不像训练里的 AI 文本', CX - 450, 766, g52.t1, { w: 900, align: 'center', size: 24 });
    c.cue(t52, 'item');
    const f1 = FL(c, 'S05-52');
    A.out(f1.out);

    // ---- B（S05-53..56）评判维度会越来越完善；南航：AIGC 检测不应作为唯一依据；没通过的论文：评阅 + 答辩（答辩也很重要）
    const B = page(c);
    const t53 = Math.max(f1.in, P(c, 'S05-53', '评判论文', 0.2) - 0.4);
    W(c, B.g, '评判 AI 生成的维度，会越来越完善', CX, 330, 46, t53, t53 + 2.4, { align: 'center' });
    c.cue(t53, 'item');
    B.note('南京航空航天大学教务处副处长 · 2026-05（科技日报、央视网）', CX - 500, 414, T('S05-54') + 0.1, { w: 1000, align: 'center', size: 24 });
    const t54 = P(c, 'S05-54', 'AIGC检测', 0.5) - 0.4;
    const g54 = W(c, B.g, 'AIGC 检测不应作为唯一依据', CX, 500, 58, t54, t54 + 2.0, { align: 'center' });
    c.handMark(g54, 11, 15, { kind: 'underline' });
    const t55 = P(c, 'S05-55', '没有通过', 0.1) - 0.2;
    const g55 = W(c, B.g, '没通过检测的论文：论文评阅 + 答辩', CX - 60, 640, 46, t55, t55 + 2.4, { align: 'center' });
    const t56 = T('S05-56') - 0.2;
    c.handMark(g55, 16, 18, { kind: 'circle', at: Math.max(g55.t1 + 0.05, t56) });
    const t56b = Math.max(g55.t1 + 0.3, t56 + 0.35);
    W(c, B.g, '也很重要', g55.x1 + 40, 640, 40, t56b, t56b + 0.6, { color: ACC });
    [t54, t55, t56].forEach(t => c.cue(t, 'item'));
    const f2 = FL(c, 'S05-56');
    B.out(f2.out);

    // ---- C（S05-57）结论：AI 率只是一个方面；毕业审核：多方面、多维度评判（章末最后一句，留到说完才擦）
    const C = page(c);
    const t57 = Math.max(f2.in, P(c, 'S05-57', '只是一个方面', 0.2) - 0.8);
    const g57 = W(c, C.g, 'AI 率只是一个方面', CX, 470, 76, t57, t57 + 1.6, { align: 'center' });
    c.handMark(g57, 6, 10, { kind: 'underline' });
    const t57b = P(c, 'S05-57', '学生整个毕业', 0.2) - 0.3;
    W(c, C.g, '毕业审核：多方面、多维度评判', CX, 616, 50, t57b, t57b + 2.2, { align: 'center' });
    c.cue(t57, 'item'); c.cue(t57b, 'item');
  });

  // ================================================================== S06 总结（手写，逐条出现；最后一句落款）
  ENG.scene('S06', c => {
    c.summary({
      items: [
        ['AI 率 = 系统打的分', '每一家都不一样，都是黑盒 · 知网协议：仅供参考'],
        ['测的是：文字好不好猜', '确认不了是谁写的；名篇、规范文字易被误判，检测也有误差'],
        ['被判高了：先看原因，逐段检查', ''],
      ],
      at: [T('S06-59') + 0.1, T('S06-61') + 0.1, T('S06-64') + 0.1],
      cardAt: T('S06-58') + 0.05,
      signAt: T('S06-65') + 0.2,
    });
    const t65 = T('S06-65') - 0.1;
    const bt = c.hand({ text: '论文都能顺利通过！', x: CX, y: 806, size: 56, align: 'center', color: ACC, at: t65, until: t65 + 1.2 });
    c.handUnderline({ x0: bt.x0 - 6, x1: bt.x1 + 10, y: bt.y1 + 14, at: bt.t1 + 0.05 });
  });
})();
