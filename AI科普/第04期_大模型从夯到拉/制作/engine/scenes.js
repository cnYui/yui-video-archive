/* 《原LAI如此》第 4 期「大模型从夯到拉」— scenes.js（本期画面）
 *
 * 依据：台本/script_data.py 每一行的第 4 个字段（画面说明）。组件见 components.js。
 * 时间：一律按段号 / 台词短语取（P('S04-17', '顶级')、st('S04-18')、c.seg / c.P / c.endTalk），不写死秒数。
 *
 * 版面（舞台坐标 1920×1080）：
 *   · 左：五档榜单（全片常驻，S03 起；挂在 #scenes 层、轨道放 ENG.global，在 S03 的 builder 里建好）
 *     x 440–1200、y 160–812，下面一行图例（国外蓝条 / 国产红条）。章节大标题居中时榜单压暗，标题收到左上角后恢复。
 *   · 右：当前模型的数据卡 x 1250–1860、y 190–850（分数、标价 / 考一次 2×2、优缺点、印章）。
 *     说到“给到：X”时盖章，0.45 s 后名字卡从数据卡飞进榜单对应那一档（飞行层在 S07 的 builder 里建，压在所有场景上面）。
 *   · S07：榜单移到中间放大，Opus 5.5「最强」、Muse Spark「最值」加橙框；随后回到左边，右边出总结卡。
 * 不压：左下角色（舞台 x < 380）、字幕（y > 900）、右上目录（ENG.tocRect()，舞台 x ≥ 1750、y ≤ 162）。
 * 品牌只写文字，不画 logo；图表标「示意」。
 */
(function () {
  'use strict';
  const { E, esc } = ENG;
  if (!ENG.SCENES.length) return;

  // ================================================================== 本期样式（模板 style.css 不改，在这里补）
  const CSS = `
  .tb { position: absolute; }
  .tbRow { position: absolute; }
  .tbLab { position: absolute; display: flex; align-items: center; justify-content: center; font: 400 44px var(--fun);
    border-radius: 6px 0 0 6px; letter-spacing: .02em; }
  .tbLab.sm { font-size: 34px; }
  .tbBody { position: absolute; background: rgba(20,20,20,.64); border-radius: 0 6px 6px 0; border: 1.5px solid rgba(237,234,227,.14); }
  .tbDef { position: absolute; display: flex; align-items: center; white-space: nowrap; font: 700 30px var(--cjk); color: rgba(237,234,227,.94); }
  .tbLegend { position: absolute; white-space: nowrap; font: 500 18px var(--cjk); color: rgba(237,234,227,.74); }
  .tbLegend i { display: inline-block; width: 5px; height: 20px; border-radius: 3px; vertical-align: -3px; margin: 0 8px 0 18px; }
  .tbLegend i.f { margin-left: 0; }
  .mchip { position: absolute; height: 46px; padding: 0 12px 0 19px; border-radius: 6px; background: var(--paper); color: var(--ink);
    white-space: nowrap; font: 700 20px var(--cjk); line-height: 46px; box-shadow: 0 5px 12px rgba(0,0,0,.32); }
  .mchip .bar { position: absolute; left: 7px; top: 11px; width: 5px; height: 24px; border-radius: 3px; }
  .mchip .tg { display: inline-block; margin-left: 8px; padding: 0 6px; height: 22px; line-height: 19px; border-radius: 4px;
    font: 700 13px var(--cjk); color: var(--grey); border: 1.5px solid var(--rule); vertical-align: 2px; }
  .hlr { position: absolute; border: 4px solid var(--orange); border-radius: 10px; }
  .hlt { position: absolute; padding: 0 10px; height: 28px; line-height: 28px; border-radius: 14px; background: var(--orange);
    color: var(--paper); font: 800 17px var(--cjk); white-space: nowrap; }
  .mk { position: absolute; font: 500 16px var(--mono); letter-spacing: .2em; color: var(--grey); white-space: nowrap; }
  .mk b { font: 700 17px var(--cjk); letter-spacing: .06em; color: var(--ink); }
  .mk2 { position: absolute; font: 500 14px var(--cjk); color: var(--grey); white-space: nowrap; }
  .mnm { position: absolute; font: 900 54px var(--cjk); line-height: 1.12; white-space: nowrap; color: var(--ink); }
  .msub { position: absolute; font: 500 20px var(--cjk); color: var(--grey); white-space: nowrap; }
  .mdash { position: absolute; height: 2px; background-image: repeating-linear-gradient(90deg, var(--rule) 0 9px, transparent 9px 16px); }
  .mfl { position: absolute; font: 700 19px var(--cjk); color: var(--grey); letter-spacing: .06em; white-space: nowrap; }
  .mfl small { font: 500 14px var(--cjk); letter-spacing: .04em; margin-left: 10px; color: var(--grey2); }
  .mbig { position: absolute; font: 800 62px var(--mono); line-height: 1; color: var(--ink); white-space: nowrap; }
  .mbig.cn { font: 900 42px var(--cjk); line-height: 62px; }
  .mmeter { position: absolute; border-radius: 9px; background: #D5D0C6; overflow: hidden; }
  .mmeter i { position: absolute; left: 0; top: 0; bottom: 0; background: var(--ink); border-radius: 9px; }
  .mmeter u { position: absolute; top: 0; bottom: 0; width: 3px; background: var(--orange); }
  .mtk { position: absolute; font: 600 12px var(--mono); color: var(--orange); white-space: nowrap; }
  .mrk { position: absolute; font: 700 18px var(--cjk); color: var(--grey); white-space: nowrap; }
  .mstat { position: absolute; white-space: nowrap; line-height: 44px; }
  .mstat span { font: 500 18px var(--cjk); color: var(--grey); margin-right: 10px; }
  .mstat b { font: 800 30px var(--mono); color: var(--ink); }
  .mstat b.cn { font: 900 26px var(--cjk); }
  .mstat.hot b { color: var(--orange); }
  .mstat.bad b { color: var(--red); }
  .mstat em { font-style: normal; font: 500 15px var(--cjk); color: var(--grey2); margin-left: 8px; }
  .mpc { position: absolute; font: 700 24px var(--cjk); white-space: nowrap; color: var(--ink); line-height: 34px; }
  .mpc b { display: inline-block; width: 30px; height: 30px; border-radius: 50%; margin-right: 12px; text-align: center;
    font: 800 18px var(--mono); line-height: 30px; vertical-align: 2px; color: var(--paper); }
  .mpc b.y { background: var(--ink); }
  .mpc b.n { background: var(--red); }
  .mpc b.m { background: var(--grey2); }
  .mpc em { font-style: normal; font: 500 16px var(--cjk); color: var(--grey); margin-left: 10px; }
  .mfoot { position: absolute; font: 500 14px var(--cjk); letter-spacing: .04em; color: var(--grey); white-space: nowrap; }
  .mstamp { position: absolute; }
  .mstamp .in { position: absolute; left: 0; top: 0; right: 0; bottom: 0; border-radius: 50%; border: 6px solid var(--c); color: var(--c);
    display: flex; flex-direction: column; align-items: center; justify-content: center; font: 400 50px var(--fun);
    transform: rotate(-12deg); background: rgba(237,234,227,.6); line-height: 1; }
  .mstamp .in::after { content: ''; position: absolute; left: 5px; top: 5px; right: 5px; bottom: 5px; border-radius: 50%; border: 2px solid var(--c); }
  .mstamp .in small { font: 800 15px var(--cjk); margin-top: 6px; }
  .mstamp.mini .in { border-width: 4px; font-size: 30px; }
  .mstamp.mini .in small { font-size: 12px; margin-top: 3px; }
  .minset { position: absolute; background: #E6E1D7; border-left: 5px solid var(--orange); border-radius: 4px; }
  .mi-t { position: absolute; font: 900 26px var(--cjk); color: var(--ink); white-space: nowrap; }
  .mi-s { position: absolute; font: 600 18px var(--cjk); color: #4A4741; white-space: nowrap; }
  .mi-s.o { color: var(--orange); font-weight: 800; }
  .rk { position: absolute; font: 500 15px var(--mono); letter-spacing: .24em; color: var(--grey); white-space: nowrap; }
  .rt { position: absolute; font: 900 40px var(--cjk); color: var(--ink); white-space: nowrap; }
  .rs { position: absolute; font: 500 20px var(--cjk); color: #4A4741; white-space: nowrap; }
  .ro { position: absolute; font: 800 24px var(--cjk); color: var(--orange); white-space: nowrap; }
  .rn { display: inline-block; width: 34px; height: 34px; border-radius: 50%; background: var(--orange); color: var(--paper);
    font: 800 20px var(--mono); line-height: 34px; text-align: center; margin-right: 12px; vertical-align: 3px; }
  .pile { position: absolute; height: 52px; padding: 0 18px; border-radius: 8px; background: var(--paper); color: var(--ink);
    font: 800 24px var(--cjk); line-height: 52px; white-space: nowrap; box-shadow: 0 8px 20px rgba(0,0,0,.35); }
  .crown { position: absolute; height: 30px; padding: 0 12px; border-radius: 15px; background: var(--orange); color: var(--paper);
    font: 800 17px var(--cjk); line-height: 30px; white-space: nowrap; box-shadow: 0 4px 10px rgba(0,0,0,.3); }
  .dstamp { position: absolute; padding: 4px 12px; border: 3px solid var(--orange); border-radius: 8px; color: var(--orange);
    font: 800 20px var(--cjk); background: rgba(255,246,240,.85); white-space: nowrap; }
  .sy2 { position: absolute; font: 500 14px var(--cjk); letter-spacing: .1em; color: var(--grey2); white-space: nowrap; }
  `;
  const styleEl = document.createElement('style');
  styleEl.textContent = CSS;
  document.head.appendChild(styleEl);

  // ================================================================== 白底（episode.json 的 bg_color；2026-09-28 用户：“背景图片使用纯白色，这次不用图片了”）
  // 背景层 #bg 不画图、整层涂成 bg_color（开头 0.8 s 从深藏青淡入照旧）。原来按深色背景配的字改成深色，章节标题和开场大字
  // 后面的深色光晕去掉（chapterTitle、S01），疑问卡标题自己画（S02）。右上目录保留深色底板（加深一点），字幕不变；
  // 卡片阴影减轻、加一圈细边，榜单每档的底改成实心深灰（半透明的深色压在白底上会发灰）。
  const BGC = ENG.EP.bg_color || null, LIGHT = !!BGC;
  if (LIGHT) {
    const lt = document.createElement('style');
    lt.textContent = `
    #bg { background: ${BGC}; }
    #bg canvas { display: none !important; }
    #badge .b2 { color: rgba(20,20,20,.78); }
    #toc { background: rgba(20,20,20,.9); box-shadow: 0 6px 18px rgba(0,0,0,.16); }
    #barShade { display: none; }
    .bLab { color: rgba(20,20,20,.5); }
    .bLab.cur { color: var(--ink); }
    .hdr { color: var(--ink); }
    .note { color: #4A4741; }
    .card { box-shadow: 0 0 0 1px rgba(20,20,20,.08), 0 10px 26px rgba(0,0,0,.14), 0 2px 6px rgba(0,0,0,.08); }
    .pile { box-shadow: 0 0 0 1px rgba(20,20,20,.1), 0 6px 16px rgba(0,0,0,.16); }
    .crown { box-shadow: 0 3px 8px rgba(0,0,0,.18); }
    .tbBody { background: #2A2926; border-color: rgba(20,20,20,.25); }
    .tbLegend { color: var(--grey); }
    `;
    document.head.appendChild(lt);
  }
  /** 章节标题（c.autoTitle）；白底时藏掉标题后面那块深色光晕（c.title 在标题前一个元素里画的径向渐变） */
  function chapterTitle(c, sg, o) {
    const t = c.autoTitle(sg, o);
    const pool = t && t.el && t.el.previousElementSibling;
    if (LIGHT && pool && /rgba\(14,\s*16,\s*28/.test(pool.style.backgroundImage || '')) pool.style.display = 'none';
    return t;
  }

  // ================================================================== 时间工具（按段号 / 台词短语）
  const SG = id => ENG.segId(id);
  const st = id => SG(id).start;
  /** 段 id 里说到 phrase 的时刻；找不到时用段内 frac 处，并在控制台 warn */
  function P(id, phrase, frac = 0) {
    const sg = SG(id), t = ENG.phraseTime(sg, phrase);
    if (t == null) console.warn(`scenes.js: phrase "${phrase}" not found in ${id} (fallback ${frac})`);
    return t != null ? t : sg.start + (sg.end - sg.start) * frac;
  }

  // ================================================================== 五档
  const TIERS = [
    { n: '夯', col: '#E2463F', lab: 'var(--ink)', def: '又强又值' },
    { n: '顶级', col: '#FF7A2F', lab: 'var(--ink)', def: '很强，但贵' },
    { n: '人上人', col: '#F6C945', lab: 'var(--ink)', def: '有一项特别突出' },
    { n: 'NPC', col: '#8FB3E8', lab: 'var(--ink)', def: '能用，没亮点' },
    { n: '拉完了', col: '#8A857C', lab: 'var(--paper)', def: '同样的钱，别人强一大截' },
  ];
  const B = { x: 440, y: 160, w: 760, rowH: 124, gap: 8, labW: 128 };
  B.bodyX = B.labW + 4; B.bodyW = B.w - B.bodyX;
  const rowY = i => i * (B.rowH + B.gap);
  B.h = rowY(5) - B.gap;
  const MC = { x: 1250, y: 190, w: 610, h: 660 };          // 右侧数据卡
  const FROM_MAIN = [MC.x + 36, MC.y + 62];                   // 名字卡起飞点：数据卡的名字处
  const FROM_INSET = [MC.x + 46, MC.y + 462];                 // 数据卡里小卡（Fable、3.1 Pro）的名字处
  const NPC_Y = [190, 404, 618];                              // S05 三张小卡的 y
  // 名字卡：飞进哪一档、在哪句哪个词盖章（盖章后 0.45 s 起飞，+delay）
  const CHIPS = [
    { name: 'GPT-6 Astra', tier: 1, cn: false, seg: 'S04-17', ph: '顶级' },
    { name: 'Claude Opus 5.5', tier: 1, cn: false, seg: 'S04-22', ph: '顶级', hl: '最强', hlUp: true },
    { name: 'Claude Fable 5.1', tier: 1, cn: false, seg: 'S04-22', ph: '顶级', delay: 0.35, from: FROM_INSET },
    { name: 'Gemini 3.8 Flash', tier: 2, cn: false, seg: 'S04-26', ph: '人上人' },
    { name: 'Gemini 3.1 Pro', tier: 4, cn: false, seg: 'S04-26', ph: '拉完了', from: FROM_INSET },
    { name: 'Grok 4.7', tier: 1, cn: false, seg: 'S04-29', ph: '顶级' },
    { name: 'Muse Spark 1.3', tier: 0, cn: false, seg: 'S04-32', ph: '夯', hl: '最值' },
    { name: 'DeepSeek V4.1 Flash', tier: 2, cn: true, seg: 'S05-37', ph: '人上人' },
    { name: 'Qwen3.8 Max', tier: 1, cn: true, seg: 'S05-40', ph: '顶级' },
    { name: 'Kimi K3', tier: 2, cn: true, seg: 'S05-43', ph: '人上人' },
    { name: 'GLM-5.3', tier: 0, cn: true, seg: 'S05-48', ph: '夯' },
    { name: 'MiniMax M3', tier: 4, cn: true, seg: 'S05-51', ph: '拉完了' },
    { name: '豆包 Seed 2.1', tier: 3, cn: true, seg: 'S05-56', ph: 'NPC', tag: '暂定', from: [MC.x + 36, NPC_Y[0] + 52] },
    { name: '混元 Hy4', tier: 3, cn: true, seg: 'S05-56', ph: 'NPC', tag: '暂定', delay: 0.3, from: [MC.x + 36, NPC_Y[1] + 52] },
    { name: '文心 5.1', tier: 3, cn: true, seg: 'S05-56', ph: 'NPC', tag: '暂定', delay: 0.6, from: [MC.x + 36, NPC_Y[2] + 52] },
    { name: 'MiMo-V2.6-Pro', tier: 0, cn: true, seg: 'S06-60', ph: '夯', hl: '国产最高' },
    { name: 'Step 5 Preview', tier: 2, cn: true, seg: 'S06-64', ph: '人上人' },
    { name: 'Jev', tier: 2, cn: false, seg: 'S06-69', ph: '人上人', tag: '赛道不同' },
  ];
  const verdictT = ch => P(ch.seg, ch.ph, 0.9);

  // ================================================================== 小工具
  /** 文字太宽就缩字号（最小 60%） */
  function fit(e, maxW, px) {
    let s = px;
    while (e.offsetWidth > maxW && s > px * 0.6) { s -= 2; e.style.fontSize = s + 'px'; }
    return e;
  }
  /** 数据格太宽：先缩灰色小字，再缩数字 */
  function fitStat(e, maxW) {
    const b = e.querySelector('b'), em = e.querySelector('em');
    let bs = parseFloat(getComputedStyle(b).fontSize), es = em ? parseFloat(getComputedStyle(em).fontSize) : 0;
    while (e.offsetWidth > maxW && em && es > 12) { es -= 1; em.style.fontSize = es + 'px'; }
    while (e.offsetWidth > maxW && bs > 18) { bs -= 2; b.style.fontSize = bs + 'px'; }
    return e;
  }
  const chipHTML = ch => `<span class="bar" style="background:${ch.cn ? 'var(--kred)' : 'var(--blue)'}"></span>${esc(ch.name)}` +
    (ch.tag ? `<span class="tg">${esc(ch.tag)}</span>` : '');

  // ================================================================== 全片常驻：五档榜单（在 S03 的 builder 里建）
  let BD = null;
  function buildBoard() {
    const layer = document.getElementById('scenes');
    const G = (e, init, fx) => ENG.T(ENG.global, e, init, fx);
    const wrap = ENG.box('div', 'tb', layer, B.x, B.y, B.w, B.h);
    wrap.style.transformOrigin = '50% 50%';
    const rows = TIERS.map((t, i) => {
      const r = ENG.box('div', 'tbRow', wrap, 0, rowY(i), B.w, B.rowH);
      const lab = ENG.box('div', 'tbLab' + (t.n.length > 2 ? ' sm' : ''), r, 0, 0, B.labW, B.rowH, esc(t.n));
      lab.style.background = t.col; lab.style.color = t.lab;
      const body = ENG.box('div', 'tbBody', r, B.bodyX, 0, B.bodyW, B.rowH);
      const def = ENG.box('div', 'tbDef', body, 26, 0, null, B.rowH, esc(t.def));
      return { r, lab, body, def, cx: 10, cy: 12 };
    });
    ENG.box('div', 'tbLegend', wrap, B.bodyX, B.h + 12, null, null,
      '<i class="f" style="background:var(--blue)"></i>国外<i style="background:var(--kred)"></i>国产');

    // ---- 出现：S03 标题收到左上角时；每档在念到档名时亮起并写上定义（S03 讲完后定义淡出）
    const tIn = P('S03-07', '一共五档', 0.3), tDefOut = ENG.endTalk('S03');
    const lit = [P('S03-07', '夯', 0.35), P('S03-07', '顶级', 0.7), P('S03-08', '人上人', 0.05), P('S03-08', 'NPC', 0.35), P('S03-08', '拉完了', 0.65)];
    rows.forEach((rw, i) => {
      G(rw.lab, { o: 0.3 }).to(lit[i], { o: 1 }, 0.3);
      G(rw.def, { o: 0, x: -10 }).to(lit[i] + 0.08, { o: 1, x: 0 }, 0.35).to(tDefOut - 0.3, { o: 0 }, 0.35);
    });
    // ---- 章节大标题居中时压暗（S04–S07：场景开始 → 标题收到左上角），S07 放大到中间再回来。
    //      白底时标题是深色字，缩到左上角要 0.6 s、一路压在榜单上：等它移走（+0.55 s）榜单再亮，不然深字压深底看不清
    //      S03 也一样：白底时等「先定规则」收到左上角（0.6 s）才出榜单，念到“夯”时正好出齐
    const wt = G(wrap, { o: 0, y: 10, x: 0, s: 1 }).to(tIn + (LIGHT ? 0.5 : -0.2), { o: 1, y: 0 }, 0.45);
    const back = LIGHT ? 0.55 : 0.15;
    [['S04', P('S04-14', '先上', 0.5)], ['S05', P('S05-33', '先说', 0.5)], ['S06', P('S06-57', '先上', 0.5)], ['S07', P('S07-70', '国外最强', 0.3)]]
      .forEach(([sid, tm]) => { wt.to(ENG.SC[sid].start - 0.1, { o: 0.22 }, 0.3).to(tm + back, { o: 1 }, 0.4); });
    const tZ = P('S07-70', '国外最强', 0.3) + 0.1, tBack = st('S07-71');
    wt.to(tZ, { x: 1150 - (B.x + B.w / 2), s: 1.14 }, 0.7, E.inOut).to(tBack, { x: 0, s: 1 }, 0.6, E.inOut);
    BD = { wrap, rows };
  }

  // ================================================================== 名字卡 + 飞行层（在 S07 的 builder 里建：飞行层要压在所有场景上面）
  function buildChips() {
    const layer = document.getElementById('scenes');
    const fly = ENG.box('div', '', layer, 0, 0, 1920, 1080);
    fly.style.pointerEvents = 'none';
    const G = (e, init, fx) => ENG.T(ENG.global, e, init, fx);
    const out = {};
    CHIPS.forEach(ch => {
      const row = BD.rows[ch.tier];
      const e = ENG.box('div', 'mchip', row.body, 0, 0, null, null, chipHTML(ch));
      const w = e.offsetWidth;
      if (row.cx + w > B.bodyW - 10) { row.cx = 10; row.cy += 56; }
      e.style.left = row.cx + 'px'; e.style.top = row.cy + 'px';
      const sx = B.x + B.bodyX + row.cx, sy = B.y + rowY(ch.tier) + row.cy;
      row.cx += w + 10;
      const tV = verdictT(ch), tFly = tV + 0.45 + (ch.delay || 0), tLand = tFly + 0.74;
      const from = ch.from || FROM_MAIN;
      const f = ENG.box('div', 'mchip', fly, sx, sy, null, null, chipHTML(ch));
      G(f, { o: 0, x: from[0] - sx, y: from[1] - sy, s: 1.3 }).to(tFly, { o: 1 }, 0.12).to(tFly + 0.1, { x: 0, y: 0, s: 1 }, 0.62, E.inOut).to(tLand, { o: 0 }, 0.02);
      G(e, { o: 0 }).to(tLand - 0.02, { o: 1 }, 0.02);
      // 总结时的橙框 + 小标签（名字卡旁边的独立元素，不挂在名字卡里）
      if (ch.hl) {
        const x0 = parseFloat(e.style.left), y0 = parseFloat(e.style.top), h = e.offsetHeight;
        const r = ENG.box('div', 'hlr', row.body, x0 - 7, y0 - 7, w + 14, h + 14);
        const l = ENG.box('div', 'hlt', row.body, 0, 0, null, null, esc(ch.hl));
        l.style.left = (x0 + w / 2 - l.offsetWidth / 2) + 'px';
        l.style.top = (ch.hlUp ? y0 - 7 - 6 - l.offsetHeight : y0 + h + 10) + 'px';   // 这一档有第二行时标签放上面
        r.style.zIndex = l.style.zIndex = '5';
        out[ch.name] = { r, l };
      }
    });
    // S07：Opus「最强」、Muse Spark「最值」（放大时）；MiMo「国产最高」（第二句）
    const hl = (name, t0, t1) => { const h = out[name]; G(h.r, { o: 0 }).to(t0, { o: 1 }, 0.25).to(t1, { o: 0 }, 0.3); G(h.l, { o: 0 }).to(t0 + 0.1, { o: 1 }, 0.25).to(t1, { o: 0 }, 0.3); };
    const tBack = st('S07-71');
    hl('Claude Opus 5.5', P('S07-70', '国外最强', 0.3) + 0.8, tBack - 0.1);
    hl('Muse Spark 1.3', P('S07-70', '最值', 0.6), tBack - 0.1);
    hl('MiMo-V2.6-Pro', P('S07-71', '小米', 0.2) + 0.3, st('S07-72') + 1.2);
  }

  // ================================================================== 右侧数据卡
  /** o: {at, until, no, region, vendor, name, sub, corner} -> api {score, noScore, stat, pc, inset, stamp, flow, scatter} */
  function modelCard(c, o) {
    const cd = c.card(MC.x, MC.y, MC.w, MC.h);
    c.show(cd, o.at, o.until, 14);
    c.cue(o.at, 'card');
    c.div('mk', 34, 22, 540, null, `NO.${o.no} · <b>${o.region}</b> · ${esc(o.vendor)}`, cd);
    if (o.corner) { const k = c.div('mk2', 0, 24, null, null, o.corner, cd); k.style.left = ''; k.style.right = '30px'; }
    fit(c.div('mnm', 32, 50, null, null, esc(o.name), cd), 546, 54);
    fit(c.div('msub', 34, 122, null, null, o.sub, cd), 546, 20);
    c.div('mdash', 34, 166, MC.w - 68, 2, '', cd);
    c.div('mdash', 34, 316, MC.w - 68, 2, '', cd);
    c.div('mdash', 34, 440, MC.w - 68, 2, '', cd);
    c.div('mfoot', 34, MC.h - 28, null, null, o.foot || '分数：AA 智能指数 v4.3.2（按模型计）· 标价：美元 / 百万 token · 截至 2026-09-28', cd);
    const A = { cd };
    /** 分数：大字 + 0–100 进度条（橙线 = 强线 44）+ 名次 */
    A.score = (v, t, rank) => {
      const lbl = c.div('mfl', 34, 182, null, null, '智能指数<small>满分 100</small>', cd);
      const big = c.div('mbig', 32, 214, null, null, v.toFixed(1), cd);
      const mt = c.div('mmeter', 204, 232, 206, 18, '<i></i><u></u>', cd);
      mt.querySelector('i').style.width = v + '%';
      mt.querySelector('u').style.left = 'calc(44% - 1px)';
      const tk = c.div('mtk', 204 + 206 * 0.44 - 8, 252, null, null, '44', cd);
      const rk = c.div('mrk', 204, 272, null, null, rank || '', cd);
      [lbl, big, mt, tk, rk].forEach((e, i) => c.show(e, t + i * 0.05, null, 8));
      c.cue(t, 'score');
    };
    /** 没有分数（Jev）：一行大字 + 说明 */
    A.noScore = (text, t, note) => {
      const lbl = c.div('mfl', 34, 182, null, null, '智能指数', cd);
      const big = c.div('mbig cn', 34, 212, null, null, esc(text), cd);
      const rk = c.div('mrk', 34, 276, null, null, note || '', cd);
      [lbl, big, rk].forEach((e, i) => c.show(e, t + i * 0.08, null, 8));
      c.cue(t, 'score');
    };
    /** 2×2 数据格：i = 0..3；cls ''|'hot'|'bad'；em = 灰色小字 */
    A.stat = (i, label, value, t, cls = '', em = '') => {
      const x = 34 + (i % 2) * 284, y = 328 + Math.floor(i / 2) * 54;
      const isCn = /[一-鿿]/.test(value);
      const e = c.div('mstat' + (cls ? ' ' + cls : ''), x, y, null, 44,
        `<span>${esc(label)}</span><b${isCn ? ' class="cn"' : ''}>${esc(value)}</b>${em ? `<em>${esc(em)}</em>` : ''}`, cd);
      fitStat(e, 272);
      c.show(e, t, null, 6);
      return e;
    };
    /** 优缺点一行：k 'y' ✓ / 'n' ✗ / 'm' ·；i = 行号（0..2，2.6 = 小卡下面那一行） */
    A.pc = (i, k, text, t, em = '') => {
      const e = c.div('mpc', 34, 456 + i * 48, null, null,
        `<b class="${k}">${k === 'y' ? '✓' : k === 'n' ? '✗' : '·'}</b>${esc(text)}${em ? `<em>${esc(em)}</em>` : ''}`, cd);
      fit(e, 546, 24);
      c.show(e, t, null, 6);
      c.cue(t, 'line');
      return e;
    };
    /** 卡里的小卡（Fable 5.1、Gemini 3.1 Pro、GLM-5.3 Flash），占 y 452–568 */
    A.inset = (io) => {
      const b = c.div('minset', 34, 452, MC.w - 68, 116, '', cd);
      c.show(b, io.at, io.until, 8);
      c.cue(io.at, 'card');
      fit(c.div('mi-t', 20, 10, null, null, esc(io.title), b), 400, 26);
      const lines = (io.lines || []).map((s, k) => { const e = c.div('mi-s', 20, 50 + k * 30, null, null, esc(s), b); fit(e, 400, 18); return e; });
      const api = {
        line: (k, text, t, cls = '') => { const e = c.div('mi-s' + (cls ? ' ' + cls : ''), 20, 50 + k * 30, null, null, esc(text), b); fit(e, 400, 18); c.show(e, t, null, 4); return e; },
        stamp: (tier, t, tag) => stampAt(c, b, MC.w - 68 - 104, 12, 92, tier, t, tag, true),
        lines,
      };
      return api;
    };
    A.stamp = (tier, t, tag) => stampAt(c, cd, 428, 170, 150, tier, t, tag, false);
    return A;
  }
  /** 印章：tier 0..4；轻微放大落下（0.22 s），不弹跳 */
  function stampAt(c, parent, x, y, d, tier, t, tag, mini) {
    const T = TIERS[tier];
    const s = c.div('mstamp' + (mini ? ' mini' : ''), x, y, d, d, `<div class="in">${esc(T.n)}${tag ? `<small>${esc(tag)}</small>` : ''}</div>`, parent);
    s.style.setProperty('--c', tier === 4 ? '#6E6A63' : tier === 3 ? '#4A6FD0' : tier === 2 ? '#C99A12' : T.col);
    if (T.n.length > 2) s.querySelector('.in').style.fontSize = (mini ? 24 : 40) + 'px';
    c.T(s, { o: 0, s: 1.35 }).to(t, { o: 1, s: 1 }, 0.22, E.out);
    c.cue(t, 'stamp');
    return s;
  }

  // ================================================================== S01 开场
  ENG.scene('S01', c => {
    const s0 = c.seg(0);
    const at = (c.find('今天') != null ? c.find('今天') : s0.start + 1) - 0.15;
    const bw = c.bigWord({ text: '从夯到拉', kicker: `原LAI如此 · #${ENG.pad2(ENG.EP.number)}`, sub: '2026 下半年 · 国内外大模型锐评', size: 190, at, until: ENG.SC.S01.end - 0.35,
      scrim: !LIGHT });
    const w = bw.el.querySelector('.bw');
    if (w) {
      w.innerHTML = `从<span style="color:#E2463F">夯</span>到<span style="color:${LIGHT ? '#8A857C' : '#9A958C'}">拉</span>`;
      if (LIGHT) w.style.color = 'var(--ink)';
    }
  });

  // ================================================================== S02 三个疑问：一堆模型名 + 「榜首」跳来跳去 → 疑问卡飞进目录
  ENG.scene('S02', c => {
    const s = c.segs();
    const t0 = s[0].start + 0.05, tOut = s[1].start - 0.35;
    const NAMES = ['GPT-6 Astra', 'Claude Opus 5.5', 'Gemini 3.8 Flash', 'Grok 4.7', 'DeepSeek V4.1', 'Qwen3.8 Max',
      'Kimi K3', 'GLM-5.3', 'MiMo-V2.6-Pro', 'Step 5 Preview', 'Muse Spark 1.3', 'MiniMax M3'];
    const POS = [[640, 250], [960, 226], [1320, 262], [700, 372], [1010, 350], [1360, 396], [620, 500], [940, 478], [1250, 520],
      [720, 628], [1060, 606], [1410, 650]];
    const els = NAMES.map((n, i) => {
      const e = c.div('pile', POS[i][0], POS[i][1], null, null, esc(n));
      c.show(e, t0 + i * 0.12, tOut, 10, 0.3);
      return e;
    });
    c.cue(t0, 'card');
    // 「榜首」标签：说到“榜首天天换”时在几张卡之间跳（每 0.45 s 一次）
    const crown = c.div('crown', 0, 0, null, null, '榜首');
    const tC = P('S02-02', '榜首', 0.5);
    const hop = [4, 1, 8, 2, 10];
    const cp = i => ({ x: POS[hop[i]][0] + els[hop[i]].offsetWidth - 34, y: POS[hop[i]][1] - 18 });
    const ctr = c.T(crown, { o: 0, x: cp(0).x, y: cp(0).y });
    ctr.to(tC - 0.1, { o: 1 }, 0.2);
    hop.forEach((_, i) => { if (i) ctr.to(tC + i * 0.45, cp(i), 0.22, E.inOut); });
    ctr.to(tOut, { o: 0 }, 0.3);
    // 疑问卡（白底：标题「你可能也想问」自己画成深色字，位置、出入时间和 c.questionCards 的默认标题一样，先建好压在卡片下面）
    const qAt = s[1].start - 0.2;
    if (LIGHT) {
      const tIn = ENG.tocInTime();
      const qt = c.div('', 650, 116, 1000, 70, '你可能也想问');
      Object.assign(qt.style, { textAlign: 'center', font: '900 54px var(--cjk)', color: 'var(--ink)', letterSpacing: '.06em' });
      c.show(qt, qAt, tIn, 10);
      c.show(c.div('bigRule', 1110, 196, 80, 3), qAt + 0.15, tIn, 0);
    }
    c.questionCards({ at: [s[1].start + 0.05, s[2].start + 0.05, s[3].start + 0.05], titleAt: qAt, title: LIGHT ? false : undefined });
  });

  // ================================================================== S03 先定规则：五档榜单出现 + 右边三张规则卡
  ENG.scene('S03', c => {
    const s = c.segs();
    chapterTitle(c, s[0], { morph: P('S03-07', '一共五档', 0.3) });
    buildBoard();
    const tEnd = c.endTalk();
    // ① 分数
    const A = c.card(MC.x, 190, MC.w, 196);
    const tA = st('S03-09') + 0.05;
    c.show(A, tA, tEnd, 12); c.cue(tA, 'card');
    c.div('rk', 34, 22, null, null, 'SCORE · 分数', A);
    c.div('rt', 32, 46, null, null, '智能指数', A);
    c.div('rs', 34, 106, null, null, '独立评测机构 Artificial Analysis · v4.3.2', A);
    c.div('rs', 34, 140, null, null, '10 项考试：智能体 / 编程 / 通用 / 科学推理', A);
    const full = c.div('ro', 250, 56, null, null, '满分 100 · 目前最高 57.6', A);
    c.show(full, st('S03-10') + 0.05, null, 6);
    // ② 钱看两样
    const Bc = c.card(MC.x, 404, MC.w, 254);
    const tB = st('S03-11') + 0.05;
    c.show(Bc, tB, tEnd, 12); c.cue(tB, 'card');
    c.div('rk', 34, 22, null, null, 'PRICE · 钱看两样', Bc);
    c.div('rt', 32, 48, null, null, '<span class="rn">1</span>标价', Bc);
    c.div('rs', 176, 62, null, null, '美元 / 百万 token（输入 · 输出）', Bc);
    const r2 = c.div('rt', 32, 116, null, null, '<span class="rn">2</span>考一次', Bc);
    const r2s = c.div('rs', 216, 130, null, null, '跑完整套考试的总花费', Bc);
    const t2 = P('S03-11', '考一次', 0.45);
    c.show(r2, t2, null, 6); c.show(r2s, t2 + 0.1, null, 6);
    c.div('sy2', 34, 176, null, null, 'token ≈ 模型计费用的“字”', Bc);
    const note = c.div('ro', 34, 206, null, null, '话多 = token 多 = 花得多', Bc);
    c.show(note, st('S03-12') + 0.1, null, 6); c.cue(st('S03-12') + 0.1, 'line');
    // ③ 这期的线 + 数据截止印章
    const Cc = c.card(MC.x, 676, MC.w, 150);
    const tC = st('S03-13') + 0.05;
    c.show(Cc, tC, tEnd, 12); c.cue(tC, 'card');
    c.div('rk', 34, 22, null, null, 'LINE · 这期的线', Cc);
    const b1 = c.div('rt', 32, 52, null, null, '强：<span style="color:var(--orange)">≥ 44 分</span>', Cc);
    const b2 = c.div('rt', 290, 52, null, null, '贵：<span style="color:var(--red)">&gt; $4,000</span>', Cc);
    b1.style.fontSize = b2.style.fontSize = '34px';
    const l1 = c.div('rs', 34, 104, null, null, '贵 = 最高档跑完整套考试超过 4000 美元', Cc); l1.style.fontSize = '17px';
    const l2 = c.div('sy2', 34, 126, null, null, '数据：AA 9-28 · 盲投 9-25 · OpenRouter 9-27', Cc);
    const ds = c.div('dstamp', 356, 12, null, null, '截至 2026-09-28', Cc);
    const tDs = P('S03-13', '档位', 0.6);
    c.show(ds, tDs, null, 0); c.show(l2, tDs + 0.1, null, 4); void l1;
  });

  // ================================================================== S04 一、国外几家
  ENG.scene('S04', c => {
    const tM = P('S04-14', '先上', 0.5);
    chapterTitle(c, c.seg(0), { morph: tM });
    // ---- GPT-6 Astra
    const A = modelCard(c, { at: tM + 0.25, until: st('S04-18') - 0.12, no: '01', region: '国外', vendor: 'OpenAI', name: 'GPT-6 Astra',
      sub: '2026-09-03 发布 · 闭源', corner: '同门 GPT-6 Sol 47.5 · 本期不单评' });
    A.score(52.7, P('S04-15', '智能指数', 0.1), '全榜 #3');
    const tP = P('S04-15', '输入', 0.6);
    A.stat(0, '输入', '$10', tP); A.stat(1, '输出', '$50', tP + 0.35, 'bad');
    A.stat(2, '考一次', '$5,324', tP + 0.7);
    A.pc(0, 'n', '这期最贵', P('S04-15', '这期最贵', 0.5), '和 Claude Fable 5.1 同价');
    A.pc(1, 'm', 'LMArena：蒙住名字，两个回答选一个', st('S04-16') + 0.1, '用户盲投');
    A.stat(3, '盲投', '#26', P('S04-16', '在这儿', 0.6), 'bad', 'OpenAI 最高 #19');
    A.pc(2, 'n', '盲投还不如自家旧模型', P('S04-16', '还不如', 0.8));
    A.stamp(1, verdictT(CHIPS[0]));
    // ---- Claude Opus 5.5（+ Fable 5.1 小卡）
    const Bk = modelCard(c, { at: st('S04-18') + 0.05, until: st('S04-23') - 0.12, no: '02', region: '国外', vendor: 'Anthropic',
      name: 'Claude Opus 5.5', sub: '2026-09-22 发布 · 闭源' });
    Bk.score(57.6, P('S04-18', '智能指数', 0.5), '全榜 #1');
    Bk.stat(3, '盲投', '#1', P('S04-19', '用户盲投', 0.1), 'hot', '票少 · 暂列');
    Bk.stat(0, '输入', '$4', P('S04-19', '标价', 0.6)); Bk.stat(1, '输出', '$20', P('S04-19', '标价', 0.6) + 0.2, '', 'Astra $10/$50');
    Bk.stat(2, '考一次', '$8,708', P('S04-20', '考一次', 0.3), 'bad', 'Astra $5,324');
    const fb = Bk.inset({ at: st('S04-21') + 0.05, title: 'Claude Fable 5.1', lines: ['53.4 分 · $10 / $50 · 考一次 $13,129', '2026-09-01 发布，比 Opus 5.5 早三周'] });
    Bk.pc(2.6, 'n', '官方不对中国大陆提供服务', P('S04-22', '官方', 0.5));
    Bk.stamp(1, verdictT(CHIPS[1]));
    fb.stamp(1, verdictT(CHIPS[1]) + 0.3);
    // ---- Gemini 3.8 Flash（+ 3.1 Pro 小卡）
    const Gm = modelCard(c, { at: st('S04-23') + 0.05, until: st('S04-27') - 0.12, no: '03', region: '国外', vendor: 'Google',
      name: 'Gemini 3.8 Flash', sub: '2026-09-02 发布 · 闭源' });
    Gm.score(40.9, P('S04-23', '智能指数', 0.5), '全榜 #15');
    const tG = P('S04-23', '出字速度', 0.7);
    Gm.stat(2, '速度', '285/秒', tG, 'hot', 'AA 实测 · 这期最快');
    Gm.stat(0, '输入', '$0.75', tG + 0.3, '', '优惠价'); Gm.stat(1, '输出', '$3.75', tG + 0.45, '', '2027 起翻倍');
    Gm.stat(3, '考一次', '$1,623', tG + 0.6);
    const gp = Gm.inset({ at: st('S04-24') + 0.05, title: 'Gemini 3.1 Pro Preview', lines: ['29.7 分 · $2 / $12 · 2026-02-19 起一直是预览版'] });
    gp.line(1, '3.5 Pro：五月官宣，官网还写着“即将推出”', st('S04-25') + 0.1, 'o');
    Gm.pc(2.6, 'y', 'Flash 够快', P('S04-26', '够快', 0.2));
    Gm.stamp(2, verdictT(CHIPS[3]));
    gp.stamp(4, verdictT(CHIPS[4]));
    // ---- Grok 4.7
    const Gk = modelCard(c, { at: st('S04-27') + 0.05, until: st('S04-30') - 0.12, no: '04', region: '国外', vendor: 'SpaceXAI（原 xAI）',
      name: 'Grok 4.7', sub: '2026-09-21 发布 · 闭源' });
    Gk.score(46.4, P('S04-27', '智能指数', 0.4), '全榜 #6');
    Gk.stat(0, '输入', '$2', P('S04-27', '标价', 0.8)); Gk.stat(1, '输出', '$6', P('S04-27', '标价', 0.8) + 0.2);
    Gk.stat(2, '考一次', '$4,967', P('S04-28', '考一次', 0.3), 'bad');
    Gk.pc(0, 'n', '话多：跑一遍指数输出 2.4 亿 token', P('S04-28', '话多', 0.1), '中位数 8800 万');
    Gk.stat(3, '盲投', '#92', P('S04-28', '用户盲投', 0.6), 'bad');
    Gk.pc(1, 'n', '考试分高，大家不爱它的回答', st('S04-29') + 0.1);
    Gk.stamp(1, verdictT(CHIPS[5]));
    // ---- Muse Spark 1.3
    const Ms = modelCard(c, { at: st('S04-30') + 0.05, until: null, no: '05', region: '国外', vendor: 'Meta', name: 'Muse Spark 1.3',
      sub: '2026-09-02 发布 · 闭源' });
    Ms.score(48.1, P('S04-30', '智能指数', 0.4), '全榜 #4');
    const tS = st('S04-31') + 0.05;
    Ms.stat(0, '输入', '$1.25', tS); Ms.stat(1, '输出', '$4.25', tS + 0.15, '', 'Grok $2/$6');
    Ms.stat(2, '考一次', '$2,000', P('S04-31', '考一次', 0.5), 'hot', 'Grok $4,967');
    Ms.stat(3, '盲投', '#9', tS + 0.3);
    Ms.pc(0, 'y', '分数比 Grok 高，花费不到一半', P('S04-31', '考一次', 0.5) + 0.3);
    Ms.pc(1, 'n', '官方接口只在部分国家开放', st('S04-32') + 0.05);
    Ms.stamp(0, verdictT(CHIPS[6]));
  });

  // ================================================================== S05 二、国产八家
  ENG.scene('S05', c => {
    const tM = P('S05-33', '先说', 0.5);
    chapterTitle(c, c.seg(0), { morph: tM });
    // ---- DeepSeek V4.1 Flash
    const Ds = modelCard(c, { at: tM + 0.25, until: st('S05-38') - 0.12, no: '06', region: '国产', vendor: 'DeepSeek', name: 'DeepSeek V4.1 Flash',
      sub: '2026-09-10 发布 · 开源 MIT · 标价分闲时 / 高峰两档', corner: '鲸鱼娘的原型：打分不放水' });
    Ds.pc(0, 'm', '自家大杯 V4 Pro 0813 只有 36.0', P('S05-34', '大杯', 0.5));
    Ds.score(39.5, P('S05-35', '智能指数', 0.2), '全榜 #18');
    const tD = P('S05-35', '价格', 0.5);
    Ds.stat(0, '输入', '$0.15–0.30', tD); Ds.stat(1, '输出', '$0.60–1.20', tD + 0.15);
    Ds.stat(2, '考一次', '$477', tD + 0.3, 'hot');
    Ds.stat(3, '周用量', '#1', P('S05-35', '一周用量', 0.8), 'hot', 'OpenRouter · 按 token');
    Ds.pc(1, 'n', '嘴硬：不瞎编率只有 3.5%', P('S05-36', '嘴硬', 0.2), 'AA-Omniscience');
    Ds.pc(2, 'm', '不会的题，一百道里九十六道硬答', P('S05-36', '不会的题', 0.5));
    Ds.stamp(2, verdictT(CHIPS[7]));
    // ---- Qwen3.8 Max
    const Qw = modelCard(c, { at: st('S05-38') + 0.05, until: st('S05-41') - 0.12, no: '07', region: '国产', vendor: '阿里', name: 'Qwen3.8 Max',
      sub: '0902 快照 · 闭源' });
    Qw.score(45.4, st('S05-38') + 0.4, '全榜 #8 · 国产闭源第一');
    Qw.pc(0, 'm', '分数、标价都和 Grok 差不多', P('S05-38', '分数', 0.5), 'Grok 46.4 · $2/$6');
    Qw.stat(0, '输入', '$2', P('S05-38', '标价', 0.6)); Qw.stat(1, '输出', '$6', P('S05-38', '标价', 0.6) + 0.15);
    Qw.stat(2, '考一次', '$4,935', P('S05-39', '考一次', 0.4), 'bad', 'Grok $4,967');
    Qw.stat(3, '速度', '39/秒', P('S05-39', '还慢', 0.3), 'bad');
    Qw.pc(1, 'n', '话多还慢', P('S05-39', '话多', 0.2));
    Qw.stamp(1, verdictT(CHIPS[8]));
    // ---- Kimi K3
    const Km = modelCard(c, { at: st('S05-41') + 0.05, until: st('S05-44') - 0.12, no: '08', region: '国产', vendor: '月之暗面', name: 'Kimi K3',
      sub: '2026-07-16 发布 · 开源 · 2.8 万亿参数' });
    Km.pc(0, 'y', '开源：模型谁都能下载', P('S05-41', '开源', 0.2));
    Km.score(43.6, P('S05-41', '智能指数', 0.5), '全榜 #12');
    Km.stat(3, '盲投', '#16', P('S05-41', '用户盲投', 0.6), 'hot', '国产第一');
    const tK = st('S05-42') + 0.05;
    Km.stat(0, '输入', '$3', tK, 'bad'); Km.stat(1, '输出', '$15', tK + 0.15, 'bad', '开源里最贵');
    Km.stat(2, '考一次', '$3,658', tK + 0.3);
    Km.pc(1, 'n', '最贵的开源模型', P('S05-42', '最贵', 0.3));
    Km.pc(2, 'n', '动手编程测试只有 12.6%', P('S05-42', '动手写代码', 0.5), 'Terminal-Bench 4.0');
    Km.stamp(2, verdictT(CHIPS[9]));
    // ---- GLM-5.3（+ Flash 小卡）
    const Gl = modelCard(c, { at: st('S05-44') + 0.05, until: st('S05-49') - 0.12, no: '09', region: '国产', vendor: '智谱', name: 'GLM-5.3',
      sub: '2026-08 发布 · 开源' });
    Gl.score(44.8, P('S05-44', '智能指数', 0.4), '全榜 #9 · 开源第二');
    Gl.stat(3, '动手编程', '41.9%', P('S05-44', '动手编程', 0.5), 'hot', '国产第一');
    const tL = st('S05-45') + 0.05;
    Gl.stat(0, '输入', '$1.4', tL); Gl.stat(1, '输出', '$4.4', tL + 0.15);
    Gl.stat(2, '考一次', '$2,503', P('S05-45', '考一次', 0.2), 'hot', 'Grok、千问的一半');
    Gl.inset({ at: st('S05-46') + 0.05, title: 'GLM-5.3 Flash（小杯）', lines: ['41.8 分 · $0.15 / $0.50 · 考一次 $280', 'OpenRouter 周用量 #2（按 token）'] });
    Gl.pc(2.6, 'n', '大杯只收文本（小杯能看图）', P('S05-47', '缺点', 0.3));
    Gl.stamp(0, verdictT(CHIPS[10]));
    // ---- MiniMax M3
    const Mm = modelCard(c, { at: st('S05-49') + 0.05, until: st('S05-52') - 0.12, no: '10', region: '国产', vendor: 'MiniMax', name: 'MiniMax M3',
      sub: '2026-06-01 发布 · 开源' });
    Mm.score(29.2, P('S05-49', '智能指数', 0.4), '全榜 #30');
    const tMm = P('S05-49', '高峰价', 0.5);
    Mm.stat(0, '输入', '$0.30', tMm, '', '同 DeepSeek 高峰价'); Mm.stat(1, '输出', '$1.20', tMm + 0.15);
    Mm.stat(2, '考一次', '$538', tMm + 0.3);
    Mm.pc(0, 'n', '同价的 DeepSeek V4.1 Flash：39.5', P('S05-49', '分数低了', 0.4));
    Mm.stat(3, '动手编程', '2%', st('S05-50') + 0.1, 'bad');
    Mm.pc(1, 'n', '发布当天，编程套餐改按 token 计费', P('S05-50', '发布当天', 0.3));
    Mm.pc(2, 'y', '不瞎编率 81.6%，这期最高', st('S05-51') + 0.1);
    Mm.stamp(4, verdictT(CHIPS[11]));
    // ---- 豆包 / 混元 / 文心：三张小卡
    const tN = st('S05-52') + 0.05;
    const NPC = [
      { no: '11', vendor: '字节', name: '豆包 Seed 2.1 Pro', line: '6 月 App 月活 3.24 亿 · 国内第一', sub: '盲投：上一代 Seed 2.0 Pro #64', at: st('S05-53') + 0.05 },
      { no: '12', vendor: '腾讯', name: '混元 Hy4 预览版', line: '开源 Apache-2.0 · OpenRouter 周用量 #4', sub: '上一代 Hy3：智能指数 25.3', at: st('S05-54') + 0.05 },
      { no: '13', vendor: '百度', name: '文心 ERNIE 5.1', line: '盲投 #45（1 月的 5.0 还是 #8）', sub: '开源停在 2025 年的 4.5', at: st('S05-55') + 0.05 },
    ];
    NPC.forEach((m, i) => {
      const cd = c.card(MC.x, NPC_Y[i], MC.w, 196);
      c.show(cd, tN + i * 0.15, null, 12);
      c.div('mk', 34, 20, null, null, `NO.${m.no} · <b>国产</b> · ${esc(m.vendor)}`, cd);
      fit(c.div('mnm', 32, 44, null, null, esc(m.name), cd), 380, 40);
      const na = c.div('msub', 34, 100, null, null, '智能指数：最新版未测', cd);
      na.style.color = 'var(--grey2)';
      const l1 = c.div('mpc', 34, 128, null, null, esc(m.line), cd); fit(l1, 400, 24);
      const l2 = c.div('msub', 34, 160, null, null, esc(m.sub), cd); fit(l2, 400, 20);
      c.show(l1, m.at, null, 6); c.show(l2, m.at + 0.15, null, 6);
      c.cue(m.at, 'card');
      stampAt(c, cd, MC.w - 150, 36, 124, 3, verdictT(CHIPS[12 + i]), '暂定', false);
    });
    c.cue(tN, 'card');
  });

  // ================================================================== S06 三、九月新面孔
  ENG.scene('S06', c => {
    const tM = P('S06-57', '先上', 0.5);
    chapterTitle(c, c.seg(0), { morph: tM });
    // ---- MiMo-V2.6-Pro
    const tMiEnd = st('S06-61') - 0.12;
    const Mi = modelCard(c, { at: tM + 0.25, until: tMiEnd, no: '14', region: '国产', vendor: '小米', name: 'MiMo-V2.6-Pro',
      sub: '2026-09-22 发布 · 开源 MIT · 1.02 万亿参数' });
    Mi.score(46.3, P('S06-58', '智能指数', 0.2), '全榜 #7 · 开源第一');
    Mi.pc(0, 'y', '开源第一，和 Grok 4.7（46.4）打平', P('S06-58', '开源第一', 0.4));
    const tMi = st('S06-59') + 0.05;
    Mi.stat(0, '输入', '$0.435', tMi, '', '¥3'); Mi.stat(1, '输出', '$0.87', tMi + 0.15, '', '¥6');
    Mi.stat(2, '考一次', '$207', P('S06-59', '考一次', 0.4), 'hot', 'Grok $4,967');
    Mi.stat(3, '速度', '42/秒', P('S06-60', '缺点是慢', 0.2), 'bad');
    Mi.pc(1, 'n', '首个答案要等约 49 秒', P('S06-60', '缺点是慢', 0.2) + 0.2, 'AA 实测');
    Mi.pc(2, 'y', 'MIT 协议，随便商用', P('S06-60', '随便商用', 0.5));
    Mi.stamp(0, verdictT(CHIPS[15]));
    // 好耶那一下：数据卡边上一圈橙光
    const g = c.gap(SG('S06-60'));
    if (g) c.ring(MC.x, MC.y, MC.w, MC.h, g.start + 0.1, g.end - 0.1);
    // ---- Step 5 Preview
    const St = modelCard(c, { at: st('S06-61') + 0.05, until: st('S06-65') - 0.12, no: '15', region: '国产', vendor: '阶跃星辰', name: 'Step 5 Preview',
      sub: '2026-09-20 发布 · 6000 亿参数 · 说好 10-15 开源' });
    St.score(43.7, P('S06-61', '智能指数', 0.5), '全榜 #11 · Kimi K3 43.6');
    const tSt = P('S06-61', '打平', 0.6);
    St.stat(0, '输入', '$1', tSt); St.stat(1, '输出', '$2.7', tSt + 0.15);
    scatter(c, St.cd, st('S06-62') + 0.05, st('S06-63') + 0.05, P('S06-62', '两天后', 0.6));
    St.stat(3, '许可证', '未公布', st('S06-63') + 0.15, 'bad', '截至 9-28');
    St.stat(2, '考一次', '$929', P('S06-64', '考一次', 0.4), 'hot', 'Kimi $3,658');
    St.pc(0, 'n', '“帕累托前沿”只守了两天', st('S06-63') + 0.3);
    St.pc(1, 'y', '和 Kimi 同分，考一次只要四分之一', P('S06-64', '四分之一', 0.3));
    St.stamp(2, verdictT(CHIPS[16]));
    // ---- Jev
    const Jv = modelCard(c, { at: st('S06-65') + 0.05, until: null, no: '16', region: '国外', vendor: 'TypeSafe AI', name: 'Jev',
      sub: '2026-09-15 发布 · 闭源 · 决策模型' });
    Jv.noScore('不参加考试', P('S06-65', '不会聊天', 0.3), '不聊天、不写代码，只做选择题');
    decide(c, Jv.cd, st('S06-66') + 0.05, st('S06-67') + 0.05);
    Jv.stat(0, '输入', '$42', P('S06-66', '不收钱', 0.5), '', '/ 十亿 token');
    Jv.stat(1, '输出', '免费', P('S06-66', '不收钱', 0.5) + 0.2, 'hot');
    Jv.stat(3, '上下文', '64K', P('S06-66', '不收钱', 0.5) + 0.4);
    Jv.pc(0, 'm', '官方：最多快 193.6 倍、便宜 444.6 倍', st('S06-67') + 0.2, '自家 4 个工作流');
    Jv.stat(2, '周请求', '8.13 亿', P('S06-68', '八亿', 0.3), 'hot', 'OpenRouter');
    Jv.pc(1, 'y', '一周被调用八亿多次', P('S06-68', '八亿', 0.3) + 0.2, '按请求数全站第一');
    Jv.pc(2, 'm', 'CEO：InstructGPT 论文作者之一', st('S06-69') + 0.05);
    Jv.stamp(2, verdictT(CHIPS[17]), '赛道不同');
  });

  /** Step 5：帕累托前沿散点图（示意），画在数据卡 y 452–628（优缺点区），t0 出现、t1 收起；tMove = “两天后”：MiMo 出现在左上方 */
  function scatter(c, cd, t0, t1, tMove) {
    const W = MC.w - 68, H = 176, X0 = 58, X1 = W - 18, Y0 = 16, Y1 = H - 34;
    const lx = v => X0 + (Math.log(v) - Math.log(150)) / (Math.log(6000) - Math.log(150)) * (X1 - X0);
    const ly = s => Y1 - (s - 42.5) / (47.5 - 42.5) * (Y1 - Y0);
    const box = c.div('minset', 34, 452, W, H, '', cd);
    box.style.borderLeftColor = 'var(--ink)';
    c.show(box, t0, t1, 8); c.cue(t0, 'chart');
    const pts = { s5: [929, 43.7], km: [3658, 43.6], glm: [2503, 44.8], grok: [4967, 46.4], mimo: [207, 46.3] };
    const P2 = k => `${lx(pts[k][0]).toFixed(1)},${ly(pts[k][1]).toFixed(1)}`;
    const axes = `<path d="M${X0} ${Y0} V${Y1} H${X1}" fill="none" stroke="#9A958C" stroke-width="2"/>` +
      `<text x="${X0 - 8}" y="${Y0 + 12}" font-size="14" text-anchor="end" fill="#6E6A63" font-family="Noto Sans SC">分数</text>` +
      `<text x="${X1}" y="${Y1 + 24}" font-size="14" text-anchor="end" fill="#6E6A63" font-family="Noto Sans SC">考一次（越往右越贵）</text>` +
      `<text x="${X0 + 6}" y="${Y1 + 24}" font-size="14" fill="#9A958C" font-family="Noto Sans SC">示意</text>`;
    const base = c.svg(0, 0, W, H, axes, box);
    const oldF = c.svg(0, 0, W, H, `<polyline points="${P2('s5')} ${P2('glm')} ${P2('grok')}" fill="none" stroke="#FF4F1A" stroke-width="3" stroke-dasharray="7 6"/>`, box);
    const dot = (k, lbl, col, dx = 10, dy = -10) => c.svg(0, 0, W, H,
      `<circle cx="${lx(pts[k][0])}" cy="${ly(pts[k][1])}" r="7" fill="${col}"/><text x="${lx(pts[k][0]) + dx}" y="${ly(pts[k][1]) + dy}" font-size="15" font-weight="700" fill="${col}" font-family="Noto Sans SC">${lbl}</text>`, box);
    const dS = dot('s5', 'Step 5', '#FF4F1A', -22, 26), dK = dot('km', 'Kimi', '#6E6A63', 10, 18), dG = dot('glm', 'GLM', '#6E6A63', -14, 24), dR = dot('grok', 'Grok', '#6E6A63', -46, 22);
    const dM = dot('mimo', 'MiMo（两天后）', '#E2463F', 12, 24);
    const newF = c.svg(0, 0, W, H, `<polyline points="${P2('mimo')} ${lx(6000 * 0.97).toFixed(1)},${ly(47.3).toFixed(1)}" fill="none" stroke="#E2463F" stroke-width="3"/>`, box);
    void base; void dK; void dG; void dR;
    c.T(oldF, { o: 0 }).to(t0 + 0.4, { o: 1 }, 0.3).to(tMove + 0.2, { o: 0.25 }, 0.4);
    c.T(dS, { o: 1 }).to(tMove + 0.2, { o: 0.45 }, 0.4);
    c.T(dM, { o: 0, s: 1 }).to(tMove, { o: 1 }, 0.3);
    c.T(newF, { o: 0 }).to(tMove + 0.35, { o: 1 }, 0.4);
    c.cue(tMove, 'chart');
  }
  /** Jev：一次决策的示意（软件把问题和选项发给它 → 它回“选哪个 + 几成把握”），画在数据卡 y 452–628 */
  function decide(c, cd, t0, t1) {
    const W = MC.w - 68, H = 176;
    const box = c.div('minset', 34, 452, W, H, '', cd);
    box.style.borderLeftColor = 'var(--ink)';
    c.show(box, t0, t1, 8); c.cue(t0, 'chart');
    c.div('sy2', W - 60, 10, null, null, '示意', box);
    const inp = c.div('mi-s', 20, 16, null, null, '输入：一封邮件 ＋ 问题「紧急吗？」选项：是 / 否', box);
    fit(inp, W - 90, 18);
    const arr = c.arrow(40, 56, 40, 96, '#6E6A63', { w: 3, head: 10, parent: box });
    const out = c.div('mi-t', 20, 102, null, null, '输出：是 · 把握 97%', box);
    const n2 = c.div('mi-s', 20, 142, null, null, '不写一句话，几十到几百毫秒答完', box);
    c.show(inp, t0 + 0.15, null, 4); c.show(arr, t0 + 0.6, null, 0); c.show(out, P(SG_ID_JEV, '选哪个', 0.5), null, 4); c.show(n2, P(SG_ID_JEV, '几成把握', 0.7), null, 4);
  }
  const SG_ID_JEV = 'S06-66';

  // ================================================================== S07 总结
  ENG.scene('S07', c => {
    const s = c.segs();
    const tM = P('S07-70', '国外最强', 0.3);
    chapterTitle(c, s[0], { morph: tM });
    buildChips();
    // 总结卡（榜单回到左边以后）
    const tIn = st('S07-71') + 0.45;
    const cd = c.card(MC.x, 190, MC.w, 520);
    c.show(cd, tIn, null, 12); c.cue(tIn, 'card');
    c.div('rk', 34, 22, null, null, 'SUMMARY · 三个问题', cd);
    const item = (y, n, main, sub, t) => {
      const m = c.div('rt', 32, y, null, null, `<span class="rn">${n}</span>${main}`, cd);
      m.style.fontSize = '32px'; fit(m, 546, 32);
      const sb = c.div('rs', 80, y + 50, null, null, sub, cd); fit(sb, 500, 20);
      c.show(m, t, null, 6); c.show(sb, t + 0.1, null, 6); c.cue(t, 'line');
    };
    item(58, 1, '国外最强：Claude Opus 5.5', '但用起来贵（顶级）；最值：Meta Muse Spark 1.3（夯）', tIn + 0.1);
    item(186, 2, '国产最高：MiMo-V2.6-Pro', '全榜 #7 · 差第一 11.3 分 · 考一次 $207 对 $8,708', tIn + 0.5);
    item(314, 3, '九月新面孔', 'MiMo 夯 · Step 5 人上人 · Jev 赛道不同', st('S07-72') + 0.05);
    const last = c.div('ro', 34, 470, null, null, '选模型看三样：分数 · 标价 · 考一次', cd);
    last.style.fontSize = '30px';
    c.show(last, st('S07-73') + 0.1, null, 6); c.cue(st('S07-73') + 0.1, 'line');
  });
})();
