/* ================================================================================================================
 * 白板版 scenes.js 的完整例子（技能里的参考文件，不会被加载；新一期从 scenes.template.js 开始写）。
 * 出处：第 3 期「Jev 模型是什么」的白板版（2026-09-28），由日报会话的子任务只看技能文档写成（文档可用性测试），
 *   按第二轮引擎修改过（删掉了指向目录的箭头：疑问现在自己飞进目录）。check_layout 0 issues。用户看过样片：
 *   「就是这个风格的，没问题」；这一版没有发布（第 3 期线上仍是卡片版，整套在第 3 期 _旧稿/白板版_未发布_20260928-191806/）。
 * 读的时候注意：它写于 c.flip 之前，文件里自己的 FLIP(段号) 就是 c.flip(上一句).out（上一句说完前 0.15 s 擦板，
 *   新一页从 FLIP + 0.3 写），P() 包一层是因为当时 c.P 找不到短语不提示（现在 c.P 会 warn，并记进 ENG.phraseMiss）。
 *   新写的 scenes.js 直接用 c.flip / c.P。时间、坐标、组件的规矩见 references/visuals.md「白板版」。
 * ================================================================================================================ */
/* 《原LAI如此》第 3 期「Jev 模型是什么」— 白板手写版 scenes.js（技能文档可用性测试，2026-09-28）
 *
 * 依据：台本/script_data.py 的画面说明（原本给印刷体卡片版写的），按 references/visuals.md「白板版」改成“边说边画”：
 *   说到的要点手写：章节标题 c.autoTitle、开场大字 c.bigWord、三个疑问 c.questionCards、要点 c.pointList（S05 适合 / 不适合）、
 *   结论 c.statement（S03 末尾）、总结 c.summary（board.js 自动手写）；
 *   流程图、对比表、横条、圈重点用 hand.js / board.js 的 c.hand / c.handText / c.handNode / c.handRect / c.handLine /
 *   c.handArrow / c.handMark / c.handEllipse / c.handUnderline / c.handCheck；
 *   “贴在白板上的东西”（新闻标题、客服工单、代码卡、控制台示意窗口）是印刷体卡片 + c.tape()；印刷小字（出处、补充）用 .bNote。
 * 时间：全部按声音写（段号 / 台词短语），画面整体提前 ENG.LEAD 秒由引擎做。
 *   页内翻页用 FLIP(段号)：白板比声音早 LEAD 秒，照声音时刻在下一句开头擦板，上一页最后一句会在说出来之前就被擦掉，
 *   所以擦板时刻 = 上一句声音结束 + LEAD - 0.15（画面上：上一句快说完时擦），新一页从 FLIP + 0.3 开始写。
 * 坐标：1920×1080 内容舞台，居中版面（ENG.CX = 960）。标题占 y 60–220，内容 y 240–890、x 200–1720
 *   （左下讲解员：舞台 x ≤ 170；底部字幕：y ≥ 906；右上目录：舞台 x ≥ 1748 且 y ≤ 164）。
 */
(function () {
  'use strict';
  if (!ENG.SCENES.length) return;
  const { E, EP } = ENG;
  const CX = ENG.CX;
  const HC = ENG.HAND || {};
  const ACC = HC.ACCENT || '#FF4F1A', INK = HC.INK || '#1A1A1A', RED = '#D8342A', SOFT = 'rgba(26,26,26,.45)';
  const LEAD = ENG.LEAD || 0;

  // ================================================================== 时间（声音时钟）
  const SG = id => ENG.segId(id);
  const T = id => SG(id).start;
  const MISS = ENG.phraseMiss = [];
  /** 段 id 里说到 phrase 的时刻；找不到用段内 frac 处，并记进 ENG.phraseMiss（c.P 找不到时不提示，所以自己包一层） */
  function P(id, phrase, frac = 0) {
    const sg = SG(id), t = ENG.phraseTime(sg, phrase);
    if (t == null) { MISS.push(`${id}「${phrase}」`); console.warn(`scenes.js: 「${phrase}」 not in ${id} (fallback ${frac})`); }
    return t != null ? t : sg.start + (sg.end - sg.start) * frac;
  }
  /** 在段 id 之前擦板的时刻（声音时钟）：画面上是上一句快说完的时候（见文件头）；新一页从 FLIP(id) + 0.3 写 */
  function FLIP(id) {
    const sg = SG(id), k = ENG.SEGS.indexOf(sg), prev = k > 0 ? ENG.SEGS[k - 1] : null;
    const pe = prev && prev.scene === sg.scene ? prev.end : sg.start - 0.25;
    return Math.max(sg.start - 0.2, pe + LEAD - 0.15);
  }

  // ================================================================== 小工具
  /** 调试：页面有 window.__BOARD_LOG__ 时，记下每一行手写字的时间窗和墨迹外框（自查脚本用；成片不受影响） */
  function logHand(c) {
    const L = window.__BOARD_LOG__;
    if (!Array.isArray(L)) return;
    const h0 = c.hand;
    c.hand = o => {
      const it = h0(o);
      L.push({ scene: c.sid, text: String(o.text), at: o.at, until: o.until, t0: it.t0, t1: it.t1,
        x0: Math.round(it.x0), y0: Math.round(it.y0), x1: Math.round(it.x1), y1: Math.round(it.y1), size: Math.round(it.size) });
      if (it.g) it.g.setAttribute('data-t1', it.t1.toFixed(2));        // 自查：和所在那一页的擦板时刻（data-out）比
      return it;
    };
  }
  /** 印刷小字（出处、补充说明）：.bNote，默认 24 px */
  function note(c, html, x, y, at, o = {}) {
    const e = c.div('bNote', x, y, o.w != null ? o.w : null, null, html, o.parent);
    e.style.fontSize = (o.size || 24) + 'px';
    if (o.align) e.style.textAlign = o.align;
    if (o.color) e.style.color = o.color;
    return { el: e, tr: c.show(e, at, o.until, 4) };
  }
  /** 白板上的一页：一个手写组 + 要一起擦掉的东西（board.js 组件的 tr、印刷卡片的 Track、handNode 等），out(t) 整页擦掉 */
  function page(c) {
    const g = c.handGroup(), outs = [];
    const pg = {
      g,
      add(x) { const o = x && (typeof x.out === 'function' ? x : x.tr); if (o && typeof o.out === 'function') outs.push(o); return x; },
      note(html, x, y, at, o = {}) { const n = note(c, html, x, y, at, o); outs.push(n.tr); return n.el; },
      out(t, d = 0.3) { g.setAttribute('data-out', t.toFixed(2)); c.T(g, { o: 1 }).to(t, { o: 0 }, d, E.sine); outs.forEach(x => x.out(t, d)); },
    };
    return pg;
  }
  /** 手写一行（html：<span class="or">…</span> 的字划黄线）；at..until = 写的时间窗 */
  const W = (c, g, html, x, y, size, at, until, o = {}) => c.handText(html, x, y, Object.assign({ size, at, until, parent: g }, o));
  /** 手画的「≠」 */
  function neq(c, g, cx, cy, s, at, color = ACC) {
    c.handLine({ x0: cx - s, y0: cy - s * 0.32, x1: cx + s, y1: cy - s * 0.32, at, dur: 0.12, w: 7, color, parent: g });
    c.handLine({ x0: cx - s, y0: cy + s * 0.32, x1: cx + s, y1: cy + s * 0.32, at: at + 0.15, dur: 0.12, w: 7, color, parent: g });
    return c.handLine({ x0: cx + s * 0.45, y0: cy - s * 0.95, x1: cx - s * 0.45, y1: cy + s * 0.95, at: at + 0.32, dur: 0.14, w: 7, color, parent: g });
  }
  /** 横条 = 一笔粗记号笔 */
  const bar = (c, g, x, y, len, at, color, w = 24) =>
    c.handLine({ x0: x, y0: y, x1: x + Math.max(6, len), y1: y, at, dur: Math.min(0.6, 0.15 + len / 1400), w, color, parent: g });
  /** 盖章：斜着的框 + 字（手画，橙色） */
  function stamp(c, g, text, cx, cy, at, o = {}) {
    const sg = c.handGroup(g);
    sg.setAttribute('transform', `rotate(${o.rot != null ? o.rot : -7} ${cx} ${cy})`);
    const size = o.size || 50, w = ENG.handWidth(text, size) + 64, h = size * 1.7, col = o.color || ACC;
    c.handRect({ x0: cx - w / 2, y0: cy - h / 2, x1: cx + w / 2, y1: cy + h / 2, at, dur: 0.35, w: 6, color: col, parent: sg });
    return c.hand({ text, x: cx, y: cy, size, align: 'center', color: col, at: at + 0.3, until: at + 0.3 + 0.28 * [...text].length, parent: sg });
  }
  /** 卡片里某个 <span>（按文字找）在舞台上的外框：搭场景时量（轨道还没动它），页面坐标减 ENG.OX */
  function spanRect(root, txt, pad = 3) {
    const sp = [...root.querySelectorAll('span')].find(s => s.textContent.trim() === txt);
    if (!sp) { console.warn('scenes.js spanRect: no span ' + txt); return null; }
    const r = sp.getBoundingClientRect();
    return { x0: r.left - ENG.OX - pad, y0: r.top - pad, x1: r.right - ENG.OX + pad, y1: r.bottom + pad };
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

  // ================================================================== S01 开场：手写大字「Jev」
  ENG.scene('S01', c => {
    logHand(c);
    // 念到「鲸鱼娘」时开始写（画面早 1 秒）：说到「Jev 模型」时大字已经写完；开场场景很短，写得晚会在说到 Jev 之前就淡出
    const at = P('S01-01', '鲸鱼娘', 0.3);
    c.bigWord({ text: 'Jev', kicker: `原LAI如此 · #${ENG.pad2(EP.number)}`, at,
      sub: 'TypeSafe AI 的 <span class="or">System One</span> 模型 · 2026-09' });
  });

  // ================================================================== S02 三个疑问
  ENG.scene('S02', c => {
    logHand(c);
    // ---- A（S02-02..04）：贴一张新闻标题（示意）→ 划掉「聊天 / 写文章 / 生成文字」、写「只做判断」→ 官网的两句宣传语
    const A = page(c);
    const tNews = T('S02-02') + 0.1;
    const NW = 760, NH = 170, NX = CX - NW / 2, NY = 170;
    const nw = paper(c, NX, NY, NW, NH, { kicker: 'HEADLINE · 新闻标题', shiyi: true });
    txt(c, nw, 32, 50, '新模型 <span class="or">Jev</span> 刷屏', '900 56px var(--cjk)', { lh: 76 });
    [[32, 134, 540], [590, 134, 110]].forEach(([x, y, w]) => { const l = c.div('', x, y, w, 10, '', nw); Object.assign(l.style, { background: '#D6D1C7', borderRadius: '5px' }); });
    A.add(c.show(nw, tNews, null, 10));
    c.cue(tNews, 'card');

    const RY = 440, RS = 56, JS = 64, GAP = 60;
    const words = [['聊天', P('S02-03', '不聊天', 0.05)], ['写文章', P('S02-03', '不写文章', 0.25)], ['生成文字', P('S02-03', '一个字都不生成', 0.5)]];
    const tJ = P('S02-03', '只做判断', 0.8) - 0.15;
    const ww = words.map(([w]) => ENG.handWidth(w, RS)), jw = ENG.handWidth('只做判断', JS) + 76;
    let x = CX - (ww.reduce((a, b) => a + b, 0) + jw + GAP * words.length) / 2;
    words.forEach(([w, at], i) => {
      const next = i + 1 < words.length ? words[i + 1][1] : tJ;
      const it = W(c, A.g, w, x, RY, RS, at, Math.max(at + 0.45, next - 0.05));
      c.handLine({ x0: it.x0 - 10, y0: RY + 5, x1: it.x1 + 10, y1: RY - 3, at: it.t1 + 0.04, dur: 0.16, w: 6, color: RED, parent: A.g });
      c.cue(at, 'item');
      x += ww[i] + GAP;
    });
    const jd = W(c, A.g, '只做判断', x, RY, JS, tJ, tJ + 1.0);
    c.handCheck({ x: jd.x1 + 40, y: RY - 4, size: 50, at: jd.t1 + 0.05, parent: A.g });
    c.handUnderline({ x0: jd.x0 - 6, x1: jd.x1 + 8, y: jd.y1 + 14, at: jd.t1 + 0.1, parent: A.g });
    c.cue(tJ, 'item');

    const tC = T('S02-04') + 0.1;
    A.note('官网宣传语 · 只用文字（示意）· 2026-09-28', CX - 400, 560, tC, { w: 800, align: 'center' });
    const tFast = P('S02-04', '比大模型', 0.35);
    const fast = W(c, A.g, '快 193.6 倍', CX - 300, 670, 76, tFast, tFast + 1.2, { align: 'center' });
    c.handMark(fast, 2, 7, { kind: 'circle', at: fast.t1 + 0.08 });
    const tZero = Math.max(fast.t1 + 0.3, P('S02-04', '零幻觉', 0.8) - 0.35);
    W(c, A.g, '零幻觉', CX + 300, 670, 76, tZero, tZero + 0.9, { align: 'center' });
    c.cue(tFast, 'item'); c.cue(tZero, 'item');
    A.out(FLIP('S02-05'));

    // ---- B（S02-05..09）：手写「你可能也想问」+ 三个问题（文字取 episode.questions）；到 ENG.tocInTime() 每一问飞进右上目录
    //      （2026-09-28 引擎第二轮：白板版疑问自己飞进目录，原来补的那支指向目录的箭头删掉了）
    c.questionCards({ at: [P('S02-06', '第一'), P('S02-07', '第二'), P('S02-08', '第三')], titleAt: FLIP('S02-05') + 0.3 });
  });

  // ================================================================== S03 一、Jev 是什么
  ENG.scene('S03', c => {
    logHand(c);
    c.autoTitle(SG('S03-10'));

    // ---- A（S03-11..12）流程：材料 + 问题 → Jev → 答案 + 概率；公司、发布时间
    const A = page(c);
    const NY = 300, NH = 140, NW = 320;
    const tJ = T('S03-11') + 0.1, tIn = P('S03-11', '材料和问题', 0.4) - 0.1, tOut = P('S03-11', '返回答案', 0.7) - 0.15;
    const nJ = A.add(c.handNode({ x: CX - 130, y: NY, w: 260, h: NH, text: 'Jev', sub: '只做判断', size: 64, at: tJ, color: ACC, pen: 6 }));
    const nA = A.add(c.handNode({ x: CX - 620, y: NY, w: NW, h: NH, text: '材料 + 问题', size: 46, at: tIn }));
    const nB = A.add(c.handNode({ x: CX + 300, y: NY, w: NW, h: NH, text: '答案 + 概率', size: 46, at: tOut }));
    c.handArrow({ x0: nA.x1 + 14, y0: NY + NH / 2, x1: nJ.x0 - 14, y1: NY + NH / 2, at: nA.t1 + 0.05, parent: A.g });
    c.handArrow({ x0: nJ.x1 + 14, y0: NY + NH / 2, x1: nB.x0 - 14, y1: NY + NH / 2, at: tOut - 0.3, parent: A.g });
    W(c, A.g, '不生成文字', (nJ.x1 + nB.x0) / 2, NY - 30, 30, nB.t1 + 0.05, nB.t1 + 1.3, { align: 'center', color: ACC });
    const tCo = P('S03-12', 'TypeSafe', 0.4) - 0.3;
    W(c, A.g, 'TypeSafe AI', CX, 570, 66, tCo, tCo + 1.2, { align: 'center' });
    const tDt = P('S03-12', '2026年', 0.6) - 0.1;
    W(c, A.g, '2026 年 9 月中旬发布', CX, 660, 48, tDt, tDt + 1.9, { align: 'center' });
    A.note('美国创业公司 · 旧金山 · CEO 是 InstructGPT 论文作者之一', CX - 700, 712, tDt + 0.5, { w: 1400, align: 'center' });
    A.note('名字取自经济学家杰文斯 · 和 LeCun 的 JEPA 没有关系', CX - 700, 748, tDt + 0.9, { w: 1400, align: 'center' });
    c.cue(tCo, 'item'); c.cue(tDt, 'item');
    A.out(FLIP('S03-13'));

    // ---- B（S03-13..16）System One = 系统一；卡尼曼；系统一 / 系统二两个框；Jev 落在系统一
    const B = page(c);
    const t13 = FLIP('S03-13') + 0.3;
    W(c, B.g, '<span class="or">System One</span> 模型 = 系统一模型', CX, 292, 60, t13, P('S03-13', '也就是系统一模型', 0.6) + 0.9, { align: 'center' });
    c.cue(t13, 'item');
    const t14 = T('S03-14') + 0.1;
    W(c, B.g, '灵感：卡尼曼《思考，快与慢》', CX, 392, 50, t14, T('S03-15') - 0.25, { align: 'center' });
    B.note('“系统一 / 系统二”的叫法最早由 Stanovich 和 West 提出，这本书让它出了名', CX - 700, 428, P('S03-14', '思考', 0.7) + 0.2, { w: 1400, align: 'center', size: 22 });
    c.cue(t14, 'item');
    const BX = [CX - 600, CX + 40], BW = 560, BY0 = 490, BY1 = 800;
    const cols = [
      [P('S03-15', '人凭直觉', 0.05), '系统一', '快 · 直觉', '凭直觉，一眼做出判断', ACC],
      [P('S03-15', '慢慢想', 0.5), '系统二', '慢 · 推理', '慢慢想，一步步推理', INK],
    ];
    const heads = cols.map(([at, a, b, n, col], i) => {
      const x0 = BX[i], cx = x0 + BW / 2;
      c.handRect({ x0, y0: BY0, x1: x0 + BW, y1: BY1, at, w: 5, parent: B.g });
      const h1 = W(c, B.g, a, cx, BY0 + 62, 60, at + 0.25, at + 1.2, { align: 'center' });
      const h2 = W(c, B.g, b, cx, BY0 + 142, 50, h1.t1 + 0.05, h1.t1 + 1.3, { align: 'center', color: col });
      B.note(n, x0, BY0 + 178, h2.t1, { w: BW, align: 'center', size: 22 });
      c.cue(at, 'item');
      return h1;
    });
    const tJv = T('S03-16') + 0.1;
    c.handMark(heads[0], 0, 3, { kind: 'underline', at: P('S03-16', '系统一的事', 0.4) - 0.1 });
    const jv = W(c, B.g, 'Jev', BX[0] + 120, BY0 + 258, 58, tJv, tJv + 0.6, { align: 'center', color: ACC });
    B.note('官方文档：快速、聚焦的判断', jv.x1 + 26, BY0 + 242, P('S03-16', '懂行的人', 0.3), { size: 22 });
    c.cue(tJv, 'item');
    B.out(FLIP('S03-17'));

    // ---- C（S03-17..21）state = 材料（贴一张客服工单）；三种题型
    const C = page(c);
    const t17 = FLIP('S03-17') + 0.3;
    const TKX = 320;                          // 左：工单 x 320–860；右：题型 x 950 起（整页以中线为中）
    W(c, C.g, '<span class="or">state</span> = 材料', TKX + 10, 300, 56, t17, P('S03-17', 'state', 0.5) + 0.7);
    c.cue(t17, 'item');
    const tTk = P('S03-17', '比如一张', 0.6) - 0.15;
    const tk = paper(c, TKX, 370, 540, 250, { kicker: 'TICKET · 客服工单', shiyi: true, tape: 1 });
    txt(c, tk, 32, 58, '我前天买的耳机还没发货，<br>明天出差前必须收到，<br>不然就退款！', '800 32px var(--cjk)', { lh: 50 });
    txt(c, tk, 32, 214, '（虚构内容）', '500 18px var(--cjk)', { color: 'var(--grey)' });
    C.add(c.show(tk, tTk, null, 10));
    c.cue(tTk, 'card');
    const QX = 950;
    const tTy = P('S03-18', '题型只有三种', 0.6) - 0.9;
    W(c, C.g, '题型只有三种', QX, 300, 56, tTy, T('S03-19') - 0.1);
    C.note('问题可以一次问好几道', QX + ENG.handWidth('题型只有三种', 56) + 26, 286, T('S03-18') + 0.2, { size: 22 });
    c.cue(tTy, 'item');
    [
      { n: '1', zh: '选择题', en: 'Choice · 最多 255 个选项', opt: '物流组 · 退款组 · 技术组', id: 'S03-19', ph: '比如这张工单' },
      { n: '2', zh: '打分题', en: 'Score · 2–10 个等级', opt: '平静 → 不满 → 非常愤怒', id: 'S03-20', ph: '比如客户' },
      { n: '3', zh: '是非题', en: 'Noul · 取自 Bernoulli（伯努利）', opt: '紧急吗？→ 概率', id: 'S03-21', ph: '比如这张工单' },
    ].forEach((r, i) => {
      // 选项行在题型写完后接着写（写不完会和下一行、翻页挤在一起：c.hand 最快也要约 0.3 秒一个汉字）
      const y = 400 + i * 150, at = T(r.id) + 0.05, oAt = Math.min(P(r.id, r.ph, 0.55) - 0.1, at + 1.3);
      const num = c.hand({ text: r.n, x: QX, y, size: 52, color: ACC, at, until: at + 0.2, parent: C.g });
      const zh = W(c, C.g, r.zh, QX + 50, y, 52, num.t1 + 0.03, num.t1 + 1.0);
      C.note(r.en, zh.x1 + 22, y - 16, zh.t1 + 0.05, { size: 22 });
      W(c, C.g, r.opt, QX + 50, y + 64, 42, oAt, oAt + 2.3);
      c.cue(at, 'item'); c.cue(oAt, 'item');
    });
    C.out(FLIP('S03-22'));

    // ---- D（S03-22..24）贴两张代码卡（示意）：请求（框出三道题）→ 返回（念到哪个值框哪个：shipping、0.72、0.96）→ 请求卡换成手画的校准小图
    const D = page(c);
    const t22 = FLIP('S03-22') + 0.3;
    const rq = c.code({ x: 200, y: 256, w: 700, h: 560, title: '发给 Jev 的请求', kicker: 'REQUEST', lines: [
      'POST /v1/systemone',
      'Authorization: Bearer ••••••••',
      '',
      '{',
      '  "model": "jev-latest",',
      '  "state": "我前天买的耳机还没发货……",',
      '  "questions": {',
      '    "team":   { "type": "choice", … },',
      '    "anger":  { "type": "score", … },',
      '    "urgent": { "type": "noul", … }',
      '  }',
      '}',
    ] });
    c.tape(rq.el, 0);
    rq.tr.in(t22).out(FLIP('S03-24'));
    const tQs = P('S03-22', '三道题一起', 0.1) + 0.7;
    c.handRect({ x0: 214, y0: 256 + 58 + 7 * 40 - 4, x1: 740, y1: 256 + 58 + 10 * 40 + 2, at: tQs, w: 5, color: ACC, parent: D.g, out: FLIP('S03-24') });
    const t23 = T('S03-23') + 0.1;
    const rs = c.code({ x: 960, y: 256, w: 740, h: 490, title: 'Jev 返回', kicker: 'RESPONSE · 数值虚构', lines: [
      '{',
      '  "team": {',
      { t: '    "choice": "shipping",', c: '  // 物流组' },
      '    "probabilities": {',
      '      "shipping": 0.72,',
      '      "refund": 0.28, "tech": 0.00 } },',
      '  "anger":  { "score": 1.3 },',
      '  // 0 平静 · 1 不满 · 2 非常愤怒',
      '  "urgent": { "noul": 0.96 }',
      '}',
    ] });
    c.tape(rs.el, 1);
    rs.tr.in(t23);
    D.add(rs.tr);
    // 念到哪个值框哪个值：代码卡行距只有 40，c.handEllipse / handMark 的圈会外扩 20–30 px 盖住上下行，这里用贴身的手画框
    [['"shipping"', P('S03-23', '交给物流组', 0.6)], ['0.72', P('S03-23', '0.72', 0.75)], ['0.96', P('S03-23', '0.96', 0.9)]].forEach(([s, at]) => {
      const r = spanRect(rs.el, s, 5);
      if (r) c.handRect(Object.assign(r, { at: at - 0.1, dur: 0.35, color: ACC, w: 4, r: 8, parent: D.g }));
      c.cue(at, 'item');
    });
    // 校准小图（S03-24）：手画坐标轴 + 对角线 + 0.8 那一点
    const t24 = FLIP('S03-24') + 0.3;
    const GX = 330, GY = 740, GW = 470, GH = 330;
    W(c, D.g, '校准过的概率', 210, 300, 50, t24, t24 + 1.5);
    c.handLine({ x0: GX, y0: GY, x1: GX + GW, y1: GY, at: t24 + 0.3, dur: 0.3, w: 4, parent: D.g });
    c.handLine({ x0: GX, y0: GY, x1: GX, y1: GY - GH, at: t24 + 0.55, dur: 0.3, w: 4, parent: D.g });
    D.note('给出的概率 →', GX, GY + 10, t24 + 0.8, { size: 22 });
    D.note('↑ 实际对的比例', GX - 20, GY - GH - 40, t24 + 0.8, { size: 22 });
    const tDg = P('S03-24', '校准过的', 0.3) + 0.3;
    c.handLine({ x0: GX, y0: GY, x1: GX + GW, y1: GY - GH, at: tDg, dur: 0.5, w: 6, color: ACC, parent: D.g });
    const tPt = P('S03-24', '标0.8', 0.6) - 0.1, px = GX + 0.8 * GW, py = GY - 0.8 * GH;
    c.handLine({ x0: px, y0: GY, x1: px, y1: py, at: tPt, dur: 0.18, w: 2.5, color: SOFT, parent: D.g });
    c.handLine({ x0: GX, y0: py, x1: px, y1: py, at: tPt + 0.2, dur: 0.18, w: 2.5, color: SOFT, parent: D.g });
    const dot = c.div('', px - 10, py - 10, 20, 20, '');
    Object.assign(dot.style, { borderRadius: '50%', background: ACC });
    D.add(c.show(dot, tPt + 0.35, null, 0));
    W(c, D.g, '0.8', px, GY + 32, 32, tPt + 0.3, tPt + 0.7, { align: 'center' });
    W(c, D.g, '80%', GX - 46, py, 30, tPt + 0.5, tPt + 0.9, { align: 'center' });
    const tEt = P('S03-24', '大约八成', 0.8) - 0.1;
    W(c, D.g, '约八成是对的', px - 30, py - 56, 40, tEt, tEt + 1.3, { align: 'right', color: ACC });
    D.note('官方定义：说的是大量预测的整体情况，不保证单个答案', 210, GY + 52, tEt + 0.5, { size: 22 });
    c.cue(t24, 'chart'); c.cue(tPt, 'item');
    D.out(FLIP('S03-25'));

    // ---- E（S03-25..29）新东西？传统分类模型 vs Jev；结论
    const Ep = page(c);
    const t25 = FLIP('S03-25') + 0.3;
    W(c, Ep.g, '新东西？', CX, 296, 80, t25, t25 + 1.1, { align: 'center' });
    c.cue(t25, 'word');
    const LX = 250, RX = 1050;
    const t26 = Math.max(t25 + 1.0, P('S03-26', '分类模型', 0.6) - 1.0);
    W(c, Ep.g, '传统分类模型', LX, 440, 54, t26, t26 + 1.6);
    const tFl = P('S03-26', '早就有了', 0.9) - 0.1;
    W(c, Ep.g, '文本 → 类别概率', LX, 528, 44, tFl, tFl + 1.3);
    Ep.note('例如 2018 年的 BERT，常用来做分类', LX, 562, tFl + 0.9, { size: 22 });
    const t27 = T('S03-27') + 0.4;
    const lk = W(c, Ep.g, '能分哪几类：训练时定好', LX, 640, 44, t27, P('S03-27', '训练时就定好', 0.7) + 0.9);
    c.handMark(lk, 6, 11, { kind: 'underline', at: P('S03-27', '训练时就定好', 0.7) + 0.2 });
    c.cue(t26, 'item'); c.cue(t27, 'item');
    c.handLine({ x0: 990, y0: 400, x1: 990, y1: 680, at: T('S03-28') + 0.05, dur: 0.3, w: 3, color: SOFT, parent: Ep.g });
    const t28 = T('S03-28') + 0.15;
    W(c, Ep.g, 'Jev', RX, 440, 60, t28, t28 + 0.5, { color: ACC });
    W(c, Ep.g, '题目、选项：每次现写', RX, 528, 44, t28 + 0.5, P('S03-28', '不用重新训练', 0.7) - 0.2);
    const tNt = P('S03-28', '不用重新训练', 0.7);
    c.handCheck({ x: RX + 20, y: 620, size: 40, at: tNt, parent: Ep.g });
    W(c, Ep.g, '不用重新训练', RX + 60, 620, 44, tNt + 0.2, tNt + 1.5);
    Ep.note('类似思路的开源模型：Laya（别人做的；Jev 本身没开源）', RX, 656, tNt + 0.9, { size: 22 });
    c.cue(t28, 'item'); c.cue(tNt, 'item');
    // 结论用 c.statement（手写大字，<span class="or"> 划黄线）；章末最后一句，场景比声音早 1 秒淡出，提前一点开写
    const t29 = T('S03-29') - 0.3;
    Ep.add(c.statement({ y: 722, size: 58, main: 'Jev = <span class="or">通用的判断模型</span>', at: t29, mainAt: t29 }));
  });

  // ================================================================== S04 二、和 LLM 的区别
  ENG.scene('S04', c => {
    logHand(c);
    c.autoTitle(SG('S04-30'));

    // ---- A（S04-31..33）LLM 全称 ≠ Jev；Jev 也是从预训练语言模型训练出来的（RLCD）
    const A = page(c);
    const LCX = 560, RCX = 1370;
    const t31 = T('S04-31') + 0.05;
    W(c, A.g, 'LLM', LCX, 320, 130, t31, t31 + 0.8, { align: 'center', color: ACC });
    const tLg = P('S04-31', 'Large', 0.2) + 0.1;
    W(c, A.g, 'Large Language Model', LCX, 448, 50, tLg, P('S04-31', '大语言模型', 0.45) - 0.1, { align: 'center' });
    const tZh = P('S04-31', '大语言模型', 0.45);
    W(c, A.g, '大语言模型', LCX, 530, 58, tZh, tZh + 1.4, { align: 'center' });
    A.note('ChatGPT、DeepSeek、Claude…… 背后都是它', LCX - 350, 572, P('S04-31', 'ChatGPT', 0.6), { w: 700, align: 'center' });
    c.cue(t31, 'word'); c.cue(tZh, 'item');
    const tJv = T('S04-32') + 0.1;
    A.add(c.handNode({ x: RCX - 170, y: 250, w: 340, h: 160, text: 'Jev', sub: '只做判断，不生成语言', size: 72, at: tJv, color: ACC, pen: 6 }));
    neq(c, A.g, CX, 322, 38, P('S04-32', '不算LLM', 0.4) - 0.1);
    A.note('官方 FAQ · CEO：不生成语言，所以不算 LLM', RCX - 300, 424, P('S04-32', '不生成语言', 0.7), { w: 600, align: 'center', size: 22 });
    c.cue(tJv, 'node');
    const tBase = T('S04-33') + 0.1;          // handNode 框里的字只给 1 秒的窗，长一点的字会顺延，早点开始
    const base = A.add(c.handNode({ x: RCX - 220, y: 650, w: 440, h: 110, text: '预训练语言模型', size: 46, at: tBase }));
    c.handArrow({ x0: RCX, y0: base.y0 - 12, x1: RCX, y1: 476, at: base.t1 + 0.05, dur: 0.35, w: 7, color: ACC, parent: A.g });
    const tRl = P('S04-33', '训练目标', 0.6) - 0.3;
    W(c, A.g, 'RLCD', RCX + 28, 540, 44, tRl, tRl + 0.6, { color: ACC });
    W(c, A.g, '→ 判断 + 概率', RCX + 28, 598, 38, tRl + 0.7, P('S04-33', '判断和概率', 0.9) + 0.4);
    A.note('Reinforcement Learning for Calibrated Decisions（校准决策强化学习）', RCX - 350, 774, tRl + 0.5, { w: 700, align: 'center', size: 20 });
    A.note('官方文档 · 底座是哪个模型没公开', RCX - 350, 804, tRl + 0.9, { w: 700, align: 'center', size: 20 });
    c.cue(tBase, 'node'); c.cue(tRl, 'item');
    A.out(FLIP('S04-34'));

    // ---- T（S04-34..38，S04-44..47）手画对比表：LLM | Jev × 输出 / 速度和价格 / 出错的方式（S04-47 的「理由」并进第 3 行）
    //   S04-39..43 横条图那一页整张表先擦掉（整组淡出），S04-44 再回来填第 3 行
    const tab = c.handGroup(), early = [];
    const tnote = (html, x, y, at, o = {}) => { const n = note(c, html, x, y, at, Object.assign({ size: 22 }, o)); return n.tr; };
    const X0 = 220, X1 = 1710, V1 = 540, V2 = 1130, LLX = 565, JVX = 1155;
    const tTb = FLIP('S04-34') + 0.3;
    W(c, tab, 'LLM', (V1 + V2) / 2, 268, 58, tTb, tTb + 0.5, { align: 'center' });
    W(c, tab, 'Jev', (V2 + X1) / 2, 268, 58, tTb + 0.25, tTb + 0.75, { align: 'center', color: ACC });
    c.handLine({ x0: X0, y0: 312, x1: X1, y1: 310, at: tTb + 0.5, dur: 0.4, w: 4, parent: tab });
    c.handLine({ x0: V1, y0: 236, x1: V1, y1: 830, at: tTb + 0.7, dur: 0.35, w: 3, color: SOFT, parent: tab });
    c.handLine({ x0: V2, y0: 236, x1: V2, y1: 830, at: tTb + 0.85, dur: 0.35, w: 3, color: SOFT, parent: tab });
    c.cue(tTb, 'table');
    const rowLabel = (n, label, y, at) => {
      const nn = c.hand({ text: n, x: X0 + 10, y, size: 46, color: ACC, at, until: at + 0.2, parent: tab });
      return W(c, tab, label, X0 + 56, y, 44, nn.t1 + 0.03, nn.t1 + 0.35 * [...label].length);
    };
    // 第 1 行：输出（S04-35..37）
    const r1 = 364;
    rowLabel('1', '输出', r1, P('S04-35', '第一', 0) + 0.05);
    const t35 = P('S04-35', 'LLM是一个词', 0.4) + 0.1;
    W(c, tab, '一个词一个词往外写', LLX, r1, 44, t35, t35 + 2.3);
    early.push(tnote('输出的是文字（“词”指 token）', LLX, r1 + 26, P('S04-35', '输出的是文字', 0.8), { size: 20 }));
    const t36 = T('S04-36') + 0.05;
    W(c, tab, '一起算完 → 选项 + 概率', JVX, r1, 44, t36, P('S04-36', '选项和概率', 0.8) + 0.3);
    early.push(tnote('例：物流组 0.72 · 1.3 · 0.96（数值虚构）', JVX, r1 + 26, P('S04-36', '选项和概率', 0.8) + 0.2, { size: 20 }));
    early.push(tnote('只问“急不急”：先写一段话，程序再取出答案', LLX, r1 + 54, T('S04-37') + 0.1, { size: 20 }));
    early.push(tnote('直接给出 0.96，不用再取', JVX, r1 + 54, P('S04-37', '程序再从', 0.5) + 0.3, { size: 20 }));
    c.handLine({ x0: X0, y0: 464, x1: X1, y1: 462, at: T('S04-38') - 0.1, dur: 0.35, w: 2, color: SOFT, parent: tab });
    c.cue(t35, 'row'); c.cue(t36, 'row');
    // 第 2 行：速度和价格（S04-38）
    const r2 = 510;
    rowLabel('2', '速度和价格', r2, P('S04-38', '第二', 0) + 0.05);
    const t38 = P('S04-38', 'LLM输入', 0.3) - 0.1;
    W(c, tab, '输入、输出都收钱', LLX, r2, 44, t38, t38 + 1.9);
    early.push(tnote('输出还更贵（约 5 倍）· 官方博客对照表', LLX, r2 + 28, P('S04-38', '输出还更贵', 0.6) + 0.1));
    const t38j = P('S04-38', 'Jev只收', 0.8) - 0.2;
    W(c, tab, '只收输入的钱', JVX, r2, 44, t38j, t38j + 1.7);
    early.push(tnote('$0.042 / 百万 token · 输出免费', JVX, r2 + 28, t38j + 1.2));
    c.cue(t38, 'row'); c.cue(t38j, 'row');
    const tHide = FLIP('S04-39'), tBack = FLIP('S04-44') + 0.3;
    c.T(tab, { o: 1 }).to(tHide, { o: 0 }, 0.3, E.sine).to(tBack, { o: 1 }, 0.4, E.out);
    early.forEach(tr => tr.to(tHide, { o: 0 }, 0.3, E.sine).to(tBack, { o: 1 }, 0.4, E.out));

    // ---- B（S04-39..43）官方评测横条（Jev 橙 / GPT-5.6 Terra 黑）+「厂商自测」章 + 193.6 倍偏高 + 客户最多快 4 倍
    const B = page(c);
    const t39 = FLIP('S04-39') + 0.3;
    const h1 = W(c, B.g, 'Jev', 230, 296, 52, t39, t39 + 0.4, { color: ACC });
    W(c, B.g, 'vs  GPT-5.6 Terra', h1.x1 + 20, 296, 52, h1.t1 + 0.05, P('S04-39', 'Terra', 0.6) + 0.3);
    B.note('官方评测站 · 四类实际业务：安全告警、智能体记录审查、发票、客服', 230, 334, P('S04-39', '四类', 0.3) + 0.3, { size: 20 });
    c.cue(t39, 'chart');
    const BX0 = 400, BL = 400;
    const G = [
      { y: 430, lab: '准确率', v: [67.8, 67.9], mx: 100, s: ['67.8%', '67.9%'], at: P('S04-40', '准确率', 0.05) },
      { y: 560, lab: '用时', v: [0.4, 10.1], s: ['0.4 秒', '10.1 秒'], at: P('S04-40', '速度', 0.35) - 0.2, call: '快二十多倍', callAt: P('S04-40', '二十多倍', 0.5) - 0.3 },
      { y: 690, lab: '成本', v: [0.0004, 0.0304], s: ['$0.0004', '$0.0304'], at: P('S04-40', '成本', 0.7) - 0.1, call: '百分之一多一点', callAt: P('S04-40', '百分之一', 0.8) - 0.4 },
    ];
    G.forEach(g => {
      W(c, B.g, g.lab, 230, g.y, 40, g.at, g.at + 0.8);
      const mx = g.mx || Math.max(...g.v);
      let jEnd = 0;
      g.v.forEach((v, k) => {
        const len = Math.max(6, Math.round(BL * v / mx)), y = g.y - 18 + k * 38, at = g.at + 0.35 + 0.2 * k;
        bar(c, B.g, BX0, y, len, at, k ? INK : ACC, 22);
        const vl = W(c, B.g, g.s[k], BX0 + len + 22, y, 30, at + 0.3, at + 0.9, { color: k ? INK : ACC });
        if (!k) jEnd = vl.x1;
      });
      if (g.call) W(c, B.g, g.call, jEnd + 26, g.y - 18, 34, Math.max(g.callAt, g.at + 1.2), Math.max(g.callAt, g.at + 1.2) + 1.4, { color: ACC });
      c.cue(g.at, 'item');
    });
    B.note('准确率以 GPT-6 Astra 和 Claude Fable 5.1 的平均答案为准 · 最高的模型 74.1%', 230, 752, P('S04-40', '百分之一', 0.9) + 0.4, { size: 20 });
    B.note('分开看：发票 61.8% vs 74.7%、安全告警 61.7% vs 51.2% · 大模型套了 TypeSafe 的适配器', 230, 780, P('S04-40', '百分之一', 0.9) + 0.7, { size: 20 });
    const tSt = P('S04-41', '厂商自己测', 0.3) - 0.3;
    stamp(c, B.g, '厂商自测', 950, 410, tSt);
    c.cue(tSt, 'stamp');
    const RX = 1100;
    const t42 = T('S04-42') + 0.1;
    const f193 = W(c, B.g, '官网：快 193.6 倍', RX, 470, 54, t42, P('S04-42', '官方博客', 0.5) - 0.2);
    c.handMark(f193, 5, 10, { kind: 'circle', at: f193.t1 + 0.05 });
    const tHi = P('S04-42', '官方博客', 0.5) + 0.1;
    const hi = W(c, B.g, '官方博客：偏高', RX, 556, 46, tHi, P('S04-42', '偏高', 0.9) + 0.4, { color: RED });
    c.handMark(hi, 5, 7, { kind: 'underline', at: hi.t1 + 0.05 });
    c.cue(t42, 'item');
    const t43 = T('S04-43') + 0.1;
    const f4 = W(c, B.g, '真实客户：最多快 4 倍', RX, 660, 46, t43, P('S04-43', '最多快4倍', 0.5) + 0.3);
    c.handMark(f4, 9, 10, { kind: 'circle', at: f4.t1 + 0.05 });
    B.note('一家客户（Deel）跟跑线上请求 · 离线测试 2–3 倍', RX, 700, f4.t1, { size: 20 });
    B.note('官方 X 转述，2026-09-25', RX, 728, f4.t1 + 0.2, { size: 20 });
    c.cue(t43, 'item');
    B.out(FLIP('S04-44'));

    // ---- 表回来，第 3 行：出错的方式（S04-44..46），S04-47「不给理由」接在第 3 行的第三行字里
    c.handLine({ x0: X0, y0: 582, x1: X1, y1: 580, at: tBack + 0.1, dur: 0.35, w: 2, color: SOFT, parent: tab });
    const r3 = 628;
    rowLabel('3', '出错的方式', r3, tBack + 0.2);
    const t44 = P('S04-44', '把格式写错', 0.4) - 0.4;
    W(c, tab, '可能写错格式', LLX, r3, 44, t44, t44 + 1.4);
    const t44b = P('S04-44', '编出一个', 0.6) - 0.4;
    const bian = W(c, tab, '可能编出新选项', LLX, r3 + 58, 44, t44b, t44b + 1.8);
    c.handUnderline({ x0: bian.x0 - 4, x1: bian.x1 + 6, y: bian.y1 + 10, at: bian.t1 + 0.05, color: RED, w: 5, parent: tab });
    tnote('例：冒出没给的 “marketing”（示意）', LLX, r3 + 144, bian.t1 + 0.3, { size: 20 });
    tnote('加上结构化输出，也能限定在选项里', LLX, r3 + 170, bian.t1 + 0.7, { size: 20 });
    const t45 = T('S04-45') + 0.1;
    W(c, tab, '只在给的选项里选', JVX, r3, 44, t45, t45 + 1.9);
    const tZ = P('S04-45', '零幻觉', 0.5) - 0.4;
    W(c, tab, '“零幻觉” = 不越界', JVX, r3 + 58, 44, tZ, tZ + 1.6);
    const t46 = T('S04-46') + 0.1;
    const wr = W(c, tab, '但照样会选错', JVX, r3 + 116, 44, t46, t46 + 1.5, { color: RED });
    tnote('官网 FAQ：只保证答案的格式，不保证每个判断都对', JVX, r3 + 144, P('S04-46', '只保证', 0.3), { size: 20 });
    c.cue(t44, 'row'); c.cue(t45, 'row'); c.cue(t46, 'row');
    // S04-47：LLM 能写出理由 ｜ Jev 不给理由
    const t47 = T('S04-47') + 0.1;
    W(c, tab, '能写出理由', LLX, r3 + 116, 44, t47, t47 + 1.3);
    const tNo = P('S04-47', '不给理由', 0.4) - 0.2;
    W(c, tab, '，也不给理由', wr.x1 + 4, r3 + 116, 44, tNo, tNo + 1.5, { color: RED });
    tnote('Simon Willison：比 LLM 更像黑箱', JVX, r3 + 170, P('S04-47', '选错了', 0.5), { size: 20 });
    c.cue(t47, 'row'); c.cue(tNo, 'row');
  });

  // ================================================================== S05 三、能取代大模型吗
  ENG.scene('S05', c => {
    logHand(c);
    c.autoTitle(SG('S05-48'));

    // ---- A（S05-49..54）不能；适合 ✓ / 不适合 ✗ 两栏
    const A = page(c);
    const t49 = T('S05-49') + 0.05;
    const no = W(c, A.g, '不能', 230, 300, 110, t49, t49 + 0.7);
    c.handUnderline({ x0: no.x0 - 6, x1: no.x1 + 10, y: no.y1 + 14, at: no.t1 + 0.05, parent: A.g });
    c.cue(t49, 'word');
    // 两栏用 board.js 的 c.pointList（手写标题 + 细线 + 手写要点；mark: check 橙勾 / x 红叉 / dash 小横）
    const LX = 230, RX = 1000;
    const tFit = P('S05-49', '高频', 0.35) - 0.4;
    A.add(c.pointList({ x: LX, y: 398, w: 680, size: 44, step: 76, mark: 'check', title: '适合：高频 · 简单 · 标准明确', at: tFit,
      items: [
        { text: '工单分类', at: P('S05-50', '工单分类', 0.1) },
        { text: '内容审核', at: P('S05-50', '审核内容', 0.35) },
        { text: '检索相关性', at: P('S05-50', '资料相不相关', 0.8) - 0.9, sub: '官方文档：用例地图' },
      ] }));
    // 这一页最后一句（中文）：提前一点写、写短一点，翻页前能看完整（见文件头 FLIP）
    A.add(c.pointList({ x: RX, y: 398, w: 720, size: 44, step: 76, mark: 'x', title: '不适合', at: T('S05-51') + 0.05,
      items: [
        { text: '写文章 · 聊天 · 写代码', at: T('S05-51') + 0.5 },
        { text: '算数、比日期 → 交给代码', at: T('S05-52') + 0.1 },
        { text: '多步推理 → 拆成小题', at: T('S05-53') + 0.1 },
        { text: '中文能用，但不如英文', at: T('S05-54') - 0.2, mark: 'dash' },
      ] }));
    A.note('官方文档：Jev 1.13 已知短板（太难的题交给推理模型）· Models 页', RX, 812, P('S05-54', '不如英文', 0.6), { size: 20 });
    A.out(FLIP('S05-55'));

    // ---- B（S05-55..59）选项要设计好：《杀戮尖塔》横条；没有正确选项也硬选；留一个「以上都不是」
    const B = page(c);
    const t55 = FLIP('S05-55') + 0.3;
    const hd = W(c, B.g, '选项要自己设计好', CX, 290, 58, t55, T('S05-56') + 0.1, { align: 'center' });
    c.handMark(hd, 0, 2, { kind: 'underline', at: hd.t1 + 0.05 });
    c.cue(t55, 'word');
    const t56 = T('S05-56') + 0.1;
    const sts = W(c, B.g, '《杀戮尖塔》', 230, 380, 44, t56, t56 + 1.5);
    B.note('卡牌游戏 · 数据来自差评X.PIN 实测（2026-09-27）· 示意', sts.x1 + 20, 366, t56 + 1.0, { size: 20 });
    const SX = 430, K = 18;
    const tBars = P('S05-56', '三张防御牌', 0.5) - 0.2;
    const OPT = [['防御 A', 17], ['防御 B', 20], ['防御 C', 18], ['结束回合', 21]];
    const VX = SX + 21 * K + 34;              // 数值一列写在「结束回合」那条竖线右边，不和竖线挤在一起
    const rows = OPT.map(([lab, v], i) => {
      const y = 480 + i * 64, at = tBars + 0.55 * i;
      const lb = W(c, B.g, lab, 230, y, 38, at, at + 0.5);
      bar(c, B.g, SX, y, v * K, at + 0.3, i < 3 ? INK : SOFT, 22);
      W(c, B.g, String(v), VX, y, 34, at + 0.55, at + 0.8);
      return lb;
    });
    c.cue(tBars, 'chart');
    const tLow = P('S05-57', '每份都比', 0.3) - 0.1;
    c.handLine({ x0: SX + 21 * K, y0: 440, x1: SX + 21 * K, y1: 700, at: tLow, dur: 0.3, w: 4, color: ACC, parent: B.g });
    const tPick = P('S05-57', '选了结束回合', 0.5) - 0.3;
    c.handMark(rows[3], 0, 4, { kind: 'circle', at: tPick });
    c.handCheck({ x: VX + 76, y: 480 + 3 * 64, size: 40, at: tPick + 0.35, parent: B.g });
    B.note('三张防御牌合起来 55，拆成三份后每份都比 21 低', 230, 734, tPick + 0.3, { size: 22 });
    B.note('选项怎么列，会影响它的判断', 230, 764, tPick + 0.8, { size: 22, color: ACC });
    c.cue(tLow, 'item'); c.cue(tPick, 'item');
    const QX = 1060;
    const t58 = T('S05-58') + 0.1;
    W(c, B.g, '没有正确选项时', QX, 470, 44, t58, t58 + 1.8);
    const tHard = P('S05-58', '硬选一个', 0.4) - 0.3;
    W(c, B.g, '也会硬选一个', QX, 540, 44, tHard, tHard + 1.2);
    const tSure = P('S05-58', '很自信', 0.8) - 0.3;
    const sure = W(c, B.g, '置信度 0.99', QX, 610, 48, tSure, tSure + 0.9, { color: RED });
    c.handMark(sure, 4, 8, { kind: 'circle', at: sure.t1 + 0.05 });
    // 圈会比字外扩 20–40 px（handEllipse 的外扩是固定的），出处小字放到圈的下面
    B.note('PriorBench 独立评测（GitHub，2026-09-20）：30 条都被硬分进某一类', QX, 668, sure.t1 + 0.3, { size: 20 });
    c.cue(t58, 'item'); c.cue(tSure, 'item');
    const tNone = P('S05-59', '以上都不是', 0.5) - 0.5;
    const none = W(c, B.g, '+ 以上都不是', QX, 752, 50, tNone, tNone + 1.1, { color: ACC });
    c.handCheck({ x: none.x1 + 36, y: 748, size: 44, at: none.t1 + 0.05, parent: B.g });
    B.note('官方文档 Primitives / Choice 页也这么建议', QX, 788, P('S05-59', '官方文档', 0.8), { size: 20 });
    c.cue(tNone, 'item');
    B.out(FLIP('S05-60'));

    // ---- C（S05-60..61）置信度要打折听：说的 0.81 vs 实际 53%
    const C = page(c);
    const t60 = FLIP('S05-60') + 0.3;
    const cf = W(c, C.g, '置信度要打折听', CX, 300, 64, t60, T('S05-61') - 0.1, { align: 'center' });
    c.handMark(cf, 4, 7, { kind: 'underline', at: cf.t1 + 0.05 });
    C.note('它给的把握 = 置信度', CX - 300, 346, cf.t1, { w: 600, align: 'center', size: 22 });
    c.cue(t60, 'word');
    const CB = 700, CL = 700;
    const tb1 = P('S05-61', '八成把握', 0.4) - 0.5, tb2 = P('S05-61', '实际只对了', 0.3) - 0.3;
    W(c, C.g, '它说的把握', 360, 460, 48, tb1 - 0.6, tb1 + 0.3);
    bar(c, C.g, CB, 460, 0.81 * CL, tb1 + 0.3, ACC, 30);
    W(c, C.g, '0.81', CB + 0.81 * CL + 30, 460, 44, tb1 + 0.8, tb1 + 1.2, { color: ACC });
    W(c, C.g, '实际答对', 360, 570, 48, tb2 - 0.3, tb2 + 0.5);
    bar(c, C.g, CB, 570, 0.53 * CL, tb2 + 0.5, INK, 30);
    const r53 = W(c, C.g, '53%', CB + 0.53 * CL + 30, 570, 44, tb2 + 0.9, tb2 + 1.3);
    c.handMark(r53, 0, 3, { kind: 'circle', at: r53.t1 + 0.05 });
    C.note('置信度 0.7–0.9 的那一段 · Towards Data Science 作者在 Banking77 上实测', CX - 600, 640, r53.t1 + 0.3, { w: 1200, align: 'center', size: 22 });
    c.cue(tb1, 'item'); c.cue(tb2, 'item');
    C.out(FLIP('S05-62'));

    // ---- D（S05-62..65）流程图：请求 → Jev 判断 → 按置信度分流；两条时间条；挡掉一部分才省钱
    const D = page(c);
    const t62 = FLIP('S05-62') + 0.3;
    W(c, D.g, '怎么配合？', 230, 300, 56, t62, t62 + 1.1);
    D.note('官方推荐 · 意图路由、置信度分档（官方文档）· 示意', 230 + ENG.handWidth('怎么配合？', 56) + 30, 286, t62 + 1.0, { size: 20 });
    const tRq = P('S05-62', '官方推荐', 0.5) - 0.1, tJd = P('S05-62', '先让Jev判断', 0.7) - 0.1;
    const nR = D.add(c.handNode({ x: 230, y: 430, w: 250, h: 150, text: '请求', sub: 'state + 选项', size: 52, at: tRq }));
    const nJ = D.add(c.handNode({ x: 600, y: 420, w: 320, h: 170, text: 'Jev 判断', sub: '给出概率（置信度）', size: 54, at: tJd, color: ACC, pen: 6 }));
    c.handArrow({ x0: nR.x1 + 12, y0: 505, x1: nJ.x0 - 12, y1: 505, at: tJd - 0.2, parent: D.g });
    c.cue(tRq, 'node'); c.cue(tJd, 'node');
    const tHiN = P('S05-63', '直接按结果分流', 0.3) - 0.4, tLoN = P('S05-63', '转给人或大模型', 0.3) - 0.3;
    c.handArrow({ x0: 934, y0: 470, x1: 1108, y1: 388, at: P('S05-63', '有把握', 0.05), dur: 0.35, color: ACC, parent: D.g });
    W(c, D.g, '有把握', 944, 356, 38, P('S05-63', '有把握', 0.05) + 0.3, P('S05-63', '有把握', 0.05) + 1.1, { color: ACC });
    const nC = D.add(c.handNode({ x: 1120, y: 320, w: 520, h: 120, text: '代码 / 专门的模型', size: 44, at: tHiN }));
    c.handArrow({ x0: 934, y0: 545, x1: 1108, y1: 632, at: P('S05-63', '没把握', 0.6) - 0.2, dur: 0.35, parent: D.g });
    W(c, D.g, '没把握', 944, 668, 38, P('S05-63', '没把握', 0.6) + 0.1, P('S05-63', '没把握', 0.6) + 0.9);
    D.add(c.handNode({ x: 1120, y: 590, w: 520, h: 120, text: '人 / 大模型', size: 44, at: tLoN }));
    c.cue(tHiN, 'node'); c.cue(tLoN, 'node');
    // S05-64：两条时间条（示意）
    const TB = 560, t64 = T('S05-64') + 0.1;
    W(c, D.g, '只用大模型', 230, 780, 38, t64, t64 + 1.1);
    bar(c, D.g, TB, 780, 380, t64 + 0.9, INK, 22);
    const tJq = P('S05-64', '先问Jev', 0.4) - 0.2, tLq = P('S05-64', '再问大模型', 0.5) - 0.2;
    W(c, D.g, 'Jev + 大模型', 230, 846, 38, tJq - 0.6, tJq + 0.4);
    bar(c, D.g, TB, 846, 230, tJq + 0.4, ACC, 22);
    bar(c, D.g, TB + 250, 846, 380, tLq + 0.3, INK, 22);
    const tSlow = P('S05-64', '更慢更贵', 0.4) - 0.3;
    W(c, D.g, '更慢更贵', TB + 660, 846, 40, tSlow, tSlow + 1.1, { color: RED });
    D.note('有人在检索实验里加了 Jev：总延迟 649 → 1087 毫秒（据腾讯科技）', TB + 400, 766, tSlow + 0.5, { size: 20 });
    c.cue(t64, 'chart'); c.cue(tSlow, 'item');
    // S05-65：一部分请求在「代码 / 专门的模型」这里结束
    const tCk = T('S05-65') + 0.1;
    W(c, D.g, '挡掉一部分 → 省钱', 1130, 500, 38, tCk, tCk + 2.2, { color: ACC });
    c.handCheck({ x: nC.x1 + 34, y: 380, size: 50, at: P('S05-65', '挡掉一部分请求', 0.3), parent: D.g });
    c.cue(tCk, 'item');
    D.out(FLIP('S05-66'));

    // ---- E（S05-66）分工：大模型 想和写 ｜ Jev 又快又多的小判断
    const Fp = page(c);
    const t66 = FLIP('S05-66') + 0.3;
    W(c, Fp.g, '分工', CX, 486, 72, t66, t66 + 0.7, { align: 'center', color: ACC });
    const tLm = P('S05-66', '大模型负责', 0.3) - 0.4, tJm = P('S05-66', 'Jev负责', 0.3) - 0.3;
    c.handRect({ x0: 250, y0: 370, x1: 790, y1: 610, at: tLm, w: 5, parent: Fp.g });
    W(c, Fp.g, '大模型', 520, 444, 64, tLm + 0.3, tLm + 1.1, { align: 'center' });
    W(c, Fp.g, '负责想和写', 520, 540, 50, tLm + 1.1, tJm - 0.1, { align: 'center' });
    c.handRect({ x0: 1130, y0: 370, x1: 1670, y1: 610, at: tJm, w: 5, color: ACC, parent: Fp.g });
    W(c, Fp.g, 'Jev', 1400, 444, 64, tJm + 0.3, tJm + 0.8, { align: 'center', color: ACC });
    W(c, Fp.g, '又快又多的小判断', 1400, 540, 50, tJm + 0.8, tJm + 2.8, { align: 'center' });
    c.cue(t66, 'word'); c.cue(tLm, 'item'); c.cue(tJm, 'item');
  });

  // ================================================================== S06 四、怎么用上 Jev
  ENG.scene('S06', c => {
    logHand(c);
    c.autoTitle(SG('S06-67'));
    // ---- 没开源（S06-67，翻到第一步前擦掉）
    const A = page(c);
    const tApi = P('S06-67', '只能通过API', 0.3) - 0.3;
    W(c, A.g, '没开源 · 只能通过 API 调用', CX, 292, 50, tApi, tApi + 2.2, { align: 'center' });
    A.note('没公开权重、参数量、训练数据 · 也可以通过 OpenRouter、Vercel 等平台调用', CX - 700, 330, tApi + 1.4, { w: 1400, align: 'center', size: 22 });
    c.cue(tApi, 'item');
    A.out(FLIP('S06-68'));
    // ---- 右栏三步（整场留着）：念到「分三步」写编号，每一步念到时写字，做完打勾
    const S = c.handGroup();
    const SX = 1340, SY = [430, 560, 690];
    const tSteps = P('S06-67', '分三步', 0.5) - 0.3;
    const STEP = [['注册拿 Key', tSteps + 0.5], ['写代码调用', T('S06-70') + 0.1], ['用自己的数据测', T('S06-71') + 0.1]];
    STEP.forEach(([t, at], i) => {
      c.hand({ text: String(i + 1), x: SX, y: SY[i], size: 52, color: ACC, at: tSteps + 0.15 * i, until: tSteps + 0.15 * i + 0.2, parent: S });
      if (i < 2) c.handArrow({ x0: SX + 14, y0: SY[i] + 34, x1: SX + 14, y1: SY[i + 1] - 36, at: tSteps + 0.5 + 0.2 * i, dur: 0.2, w: 4, color: SOFT, parent: S });
      W(c, S, t, SX + 50, SY[i], 44, at, at + 1.4);
      c.cue(at, 'step');
    });
    [T('S06-70') + 0.05, T('S06-71') + 0.05, T('S06-72') + 0.05].forEach((at, i) => c.handCheck({ x: SX - 44, y: SY[i], size: 40, at, parent: S }));

    // ---- S06-68..69 控制台示意窗口（不用真实截图，Key 打码）
    const t68 = FLIP('S06-68') + 0.3;
    const win = c.browser({ x: 200, y: 250, w: 1040, h: 560, url: 'console.typesafe.ai', at: t68, until: FLIP('S06-70') });
    c.tape(win.el, 2);
    const side = c.div('side', 0, 58, null, null, '', win.el);
    ['API Keys', 'Playground', '用量', '文档'].forEach((m, i) => c.div('menu', 14, 24 + i * 60, null, null, ENG.esc(m), side));
    const tPg = P('S06-69', '试用页', 0.3) - 0.2;
    [[t68, tPg, 0], [tPg, T('S06-70') + 1, 1]].forEach(([a, b, i]) => {
      const hl = c.div('', 14, 24 + i * 60, 202, 48, '', side);
      Object.assign(hl.style, { background: 'rgba(255,79,26,.16)', borderRadius: '8px', borderLeft: '4px solid var(--orange)' });
      c.T(hl, { o: 0 }).to(a, { o: 1 }, 0.2).to(b, { o: 0 }, 0.2);
    });
    const MX = 230;
    const v1 = win.view(t68, tPg);
    c.div('ui-h', MX + 40, 36, null, null, 'API Keys', v1);
    c.div('btn', MX + 560, 30, null, null, '创建 Key', v1);
    ['名称', 'Key', '创建时间'].forEach((h, i) => c.div('th', [MX + 40, MX + 240, MX + 540][i], 120, null, null, h, v1));
    c.div('', MX + 40, 156, 740, 2, '', v1).style.background = '#CFC9BE';
    const tKey = P('S06-68', '创建API Key', 0.5);
    const krow = c.div('', 0, 0, 1040, 300, '', v1);
    c.div('td', MX + 40, 182, null, null, '测试用', krow);
    c.div('td', MX + 240, 182, null, null, '<span class="mono">••••••••••••</span>', krow);
    c.div('td', MX + 540, 182, null, null, '今天', krow);
    c.T(krow, { o: 0 }).to(tKey + 0.2, { o: 1 }, 0.3);
    c.handEllipse({ x0: 200 + MX + 230, y0: 250 + 58 + 178, x1: 200 + MX + 470, y1: 250 + 58 + 222, at: tKey + 0.6, color: ACC, w: 5, out: tPg });
    c.div('ui-t', MX + 40, 440, null, null, 'API Key：调用它用的密钥（示意，已打码）', v1).style.color = '#6E6A63';
    c.cue(tKey, 'item');
    const v2 = win.view(tPg, null);
    c.div('ui-h', MX + 40, 30, null, null, 'Playground', v2);
    c.div('btn', MX + 620, 26, null, null, '运行', v2);
    c.div('ui-t', MX + 40, 94, null, null, '<span class="mono">state</span>（材料）', v2);
    const sbox = c.div('', MX + 40, 130, 340, 230, '', v2);
    Object.assign(sbox.style, { border: '2px solid #BDB7AB', borderRadius: '8px', background: '#F6F4EF' });
    const stx = txt(c, sbox, 16, 12, '我前天买的耳机还没发货，<br>明天出差前必须收到，<br>不然就退款！', '600 22px var(--cjk)', { lh: 36 });
    c.T(stx, { o: 0 }).to(P('S06-69', '填材料', 0.5) - 0.2, { o: 1 }, 0.3);
    c.div('ui-t', MX + 420, 94, null, null, '题目 → 结果', v2);
    const tQs = P('S06-69', '加几道题', 0.2), tRes = P('S06-69', '就能看结果', 0.3);
    [['<span class="mono">team</span> · 选择题', '物流组', 0.72], ['<span class="mono">urgent</span> · 是非题', '紧急', 0.96]].forEach(([q, a, pv], i) => {
      const qb = c.div('', MX + 420, 130 + i * 110, 360, 96, '', v2);
      Object.assign(qb.style, { border: '2px solid #CFC9BE', borderRadius: '8px', background: '#FBFAF7' });
      txt(c, qb, 16, 8, q, '700 22px var(--cjk)', { lh: 32 });
      const bw = 176, bg = c.div('', 16, 54, bw, 24, '', qb);
      Object.assign(bg.style, { background: '#E4DFD5', borderRadius: '4px' });
      const fg = c.div('', 16, 54, Math.round(bw * pv), 24, '', qb);
      Object.assign(fg.style, { background: 'var(--orange)', borderRadius: '4px', transformOrigin: '0 50%' });
      c.T(fg, { o: 0 }).to(tRes + 0.15 * i, { o: 1 }, 0.3);
      c.show(txt(c, qb, 16 + bw + 12, 48, `${a} <span class="mono">${pv.toFixed(2)}</span>`, '800 22px var(--cjk)', { lh: 32 }), tRes + 0.15 * i + 0.3, null, 4);
      c.T(qb, { o: 0, y: 8 }).in(tQs + 0.2 * i, 0.3);
    });
    c.div('ui-t', MX + 40, 440, null, null, 'Playground · 示意，数值虚构', v2).style.color = '#6E6A63';
    c.cue(tPg, 'ui'); c.cue(tQs, 'item'); c.cue(tRes, 'item');

    // ---- S06-70 代码卡（示意·已简化）
    const t70 = FLIP('S06-70') + 0.3;
    const cd = c.code({ x: 200, y: 250, w: 1040, h: 460, title: 'Python 调用', kicker: '也有 JavaScript 工具包', fs: 23, lh: 42, lines: [
      '$ pip install typesafe-sdk',
      '',
      '# Key 放在环境变量 TYPESAFE_API_KEY，不写进代码',
      { t: 'client = …', c: '            # 用官方工具包创建，Key 从环境变量读取' },
      '',
      'result = client.system_one(',
      '    state="我前天买的耳机还没发货……",',
      { t: '    questions=[ … ],', c: '    # 几道题，一起发' },
      ')',
    ] });
    c.tape(cd.el, 0);
    cd.tr.in(t70).out(FLIP('S06-71'));
    const tCall = P('S06-70', '发一份材料', 0.5) - 0.2;
    c.handRect({ x0: 212, y0: 250 + 58 + 5 * 42 - 4, x1: 900, y1: 250 + 58 + 9 * 42 + 2, at: tCall, w: 5, color: ACC, out: FLIP('S06-71') });
    c.cue(tCall, 'item');

    // ---- S06-71..73 上线前测一遍（尤其是中文）；价格；免费额度
    const Cq = c.handGroup();
    const t71 = FLIP('S06-71') + 0.3;
    note(c, '上线前：用自己的数据测准确率、定置信度门槛', 220, 286, t71, { size: 26 });
    const tCn = P('S06-71', '尤其是中文', 0.4) - 0.5;
    const cn = W(c, Cq, '尤其是中文', 220, 380, 64, tCn, tCn + 1.3);
    c.handUnderline({ x0: cn.x0 - 6, x1: cn.x1 + 10, y: cn.y1 + 16, at: cn.t1 + 0.05, parent: Cq });
    c.cue(tCn, 'item');
    const t72 = T('S06-72') + 0.1;
    const pr = W(c, Cq, '输入 $0.042 / 百万 token', 220, 540, 58, t72, P('S06-72', '输出免费', 0.3) - 0.3);
    c.handMark(pr, 3, 9, { kind: 'circle', at: pr.t1 + 0.05 });
    const tFree = P('S06-72', '输出免费', 0.3) - 0.2;
    const fr = W(c, Cq, '输出 免费', 220, 636, 58, tFree, tFree + 0.9);
    c.handMark(fr, 3, 5, { kind: 'underline', at: fr.t1 + 0.05 });
    note(c, '官方文档 · 2026-09-28 查询', 220, 680, fr.t1 + 0.1, { size: 20 });
    c.cue(t72, 'item'); c.cue(tFree, 'item');
    const t73 = T('S06-73') - 0.2;            // 这一场最后一句：场景比声音早 1 秒淡出，早点开写
    W(c, Cq, '新用户暂不送免费额度', 220, 770, 44, t73, t73 + 2.6);
    note(c, '官方说会尽快恢复 · 官方 X 2026-09-27（美国时间）', 220, 802, t73 + 2.0, { size: 20 });
    c.cue(t73, 'item');
  });

  // ================================================================== S07 总结（手写，逐条出现；最后一句落款）
  ENG.scene('S07', c => {
    logHand(c);
    const s = c.segs();
    c.summary({
      items: [
        ['<span class="or">Jev</span>：只做判断的系统一模型', '材料 + 问题 → 答案 + 概率'],
        ['和 LLM 比：不写字，更快更便宜', '按厂商的测试 · 答案不会越出选项，但也会选错'],
        ['取代不了大模型', '高频的小判断交给 Jev，想和写交给大模型'],
      ],
      at: [1, 2, 3].map(i => s[i].start + 0.1),
      cardAt: s[0].start + 0.1,
      signAt: s[4].start + 0.2,
    });
  });
})();
