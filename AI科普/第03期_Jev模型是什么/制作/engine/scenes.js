/* 《原LAI如此》第 3 期「Jev 模型是什么？和 LLM 有什么区别？」— scenes.js（本期画面）
 *
 * 依据：台本/script_data.py 每一行的第 4 个字段（画面说明）；画面上的小字、数字以同一文件的 CHECKLIST 为准。
 * 组件见 components.js，写法参考 scenes.example.js（第 1 期）和第 2 期的 scenes.js。
 * 时间：一律按段号 / 台词短语取（P('S03-12', '2026年') / c.P / c.gap / c.endTalk），不写死秒数。
 * 版面：内容 x 440–1860、y ≤ 900；章节标题收起后占左上 x 440–1300、y 84–130；S02 之后右上是本期目录（舞台 x ≥ ~1750、
 *   y ≤ ~162，用 ENG.tocRect() / ENG.safeTop() 避让：右边到 1860 的卡片都从 y ≥ 180 开始）；左下角色、底部字幕不压。
 * 视觉：终端小票（纸白 / 墨黑 / 橙；红只用于错误——S04 里 LLM 编出来的「marketing」）；品牌只写文字不画 logo；
 *   官网宣传语、新闻标题、工单、代码卡、控制台、图表都标「示意」，Key 打码，虚构数值注明。
 * 复用：S02 的两张官网宣传语卡（promoCard）在 S04-42「快 193.6 倍」、S04-45「零幻觉」里用同一个画法回来。
 */
(function () {
  'use strict';
  const { E, esc } = ENG;
  const ICON = ENG.ICON;
  if (!ENG.SCENES.length) return;

  // ================================================================== 本期样式（模板 style.css 不改，在这里补）
  const CSS = `
  .tagp { position: absolute; white-space: nowrap; font: 700 17px var(--cjk); line-height: 26px; padding: 0 10px; border-radius: 5px; border: 2px solid var(--orange); color: var(--orange); background: #FFF6F0; }
  .inbox { position: absolute; background: #E4DFD5; border-radius: 10px; }
  .opt { position: absolute; white-space: nowrap; height: 46px; padding: 0 18px; border-radius: 8px; background: #E4DFD5; color: var(--ink); font: 700 24px var(--cjk); line-height: 46px; }
  .opt.on { background: var(--orange); color: var(--paper); }
  .opt.dk { background: #1E1E1D; color: var(--paper); }
  .qph { position: absolute; border: 2.5px dashed rgba(237,234,227,.5); border-radius: 8px; background: rgba(20,20,20,.35); }
  .stamp { position: absolute; border: 5px solid var(--orange); border-radius: 10px; color: var(--orange); font: 900 42px var(--cjk); letter-spacing: .14em; text-align: center; background: rgba(255,246,240,.92); box-shadow: 0 6px 18px rgba(0,0,0,.18); white-space: nowrap; }
  .tok { display: inline-block; padding: 0 5px; margin-right: 4px; border-radius: 5px; background: #E4DFD5; line-height: 42px; }
  .tok.b { background: #D3CCBF; }
  .errtag { position: absolute; white-space: nowrap; height: 40px; padding: 0 12px; border-radius: 6px; border: 2px solid var(--red); background: #FFF1EF; color: var(--red); font: 800 20px var(--cjk); line-height: 36px; }
  .dimnote { position: absolute; white-space: nowrap; font: 600 21px var(--cjk); color: rgba(237,234,227,.86); }
  `;
  const styleEl = document.createElement('style');
  styleEl.textContent = CSS;
  document.head.appendChild(styleEl);

  // ================================================================== 白底（episode.json 的 bg_color；2026-09-28 用户：“背景修改为纯白色”，做法同第 4 期）
  // 背景层 #bg 不画图、整层涂成 bg_color（开头 0.8 s 从深藏青淡入照旧，片头片尾本来就是深色，接得上）。原来按深色背景配的浅色字
  // 改成深色；章节标题、开场大字、「新东西？」「不能」「LLM」后面的深色光晕去掉；疑问卡标题自己画成深色；c.label / c.bracket
  // 自动配色时“背后什么都没画”按白色算。右上目录保留深色底板（加深一点），字幕不变；卡片阴影减轻、加一圈细边。
  const BGC = ENG.EP.bg_color || null, LIGHT = !!BGC;
  const FG = LIGHT ? 'var(--ink)' : 'var(--paper)';                       // 直接压在背景上的主文字
  const FG2 = LIGHT ? 'rgba(20,20,20,.72)' : 'rgba(237,234,227,.86)';     // 直接压在背景上的次要文字
  const FG3 = LIGHT ? 'rgba(20,20,20,.5)' : 'rgba(237,234,227,.72)';      // 更淡的注释
  const LINE = LIGHT ? 'rgba(20,20,20,.55)' : 'rgba(237,234,227,.85)';    // 背景上的灰箭头
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
    .chip { box-shadow: 0 0 0 1px rgba(20,20,20,.12), 0 4px 10px rgba(0,0,0,.12); }
    .chip.o { box-shadow: 0 4px 10px rgba(0,0,0,.14); }
    .chip.line { color: var(--ink); border-color: rgba(20,20,20,.45); box-shadow: none; }
    .chip.dark { border-color: rgba(20,20,20,.25); }
    .qph { border-color: rgba(20,20,20,.3); background: rgba(20,20,20,.04); }
    .dimnote { color: #4A4741; }
    .step .sc { border-color: rgba(20,20,20,.3); color: rgba(20,20,20,.5); }
    .step .st { color: rgba(20,20,20,.45); }
    .step .ss { color: rgba(20,20,20,.4); }
    `;
    document.head.appendChild(lt);
    // components.js 的 ENG.surfaceUnder 在“什么都没画”的地方返回深藏青（27, 35, 64），白底时换成背景色，标签就会配深色字
    const surf = ENG.surfaceUnder;
    const n = parseInt((BGC.match(/^#([0-9a-f]{6})$/i) || [0, 'FFFFFF'])[1], 16);
    const bgRGB = { r: n >> 16, g: (n >> 8) & 255, b: n & 255 };
    ENG.surfaceUnder = (e, root) => { const u = surf(e, root); return (u.r === 27 && u.g === 35 && u.b === 64) ? bgRGB : u; };
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
  const T = id => SG(id).start;
  /** 换下一屏时旧内容的淡出时刻：下一段开口前 0.2 s（段间 0.25 s 的换气里），新内容开口后再淡入，两屏不叠在一起 */
  const OUT = id => SG(id).start - 0.2;
  /** 段 id 里说到 phrase（按字幕原文匹配）的时刻；找不到时用段内 frac 处，并在控制台 warn */
  function P(id, phrase, frac = 0) {
    const sg = SG(id), t = ENG.phraseTime(sg, phrase);
    if (t == null) console.warn(`scenes.js: phrase "${phrase}" not found in ${id} (fallback ${frac})`);
    return t != null ? t : sg.start + (sg.end - sg.start) * frac;
  }

  // ================================================================== 小工具
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
    if (o.kicker) c.div('kicker', o.kx || 36, 22, w - 150, null, o.kicker, cd);
    if (o.shiyi) c.div('shiyi', w - 78, 16, null, null, typeof o.shiyi === 'string' ? o.shiyi : '示意', cd);
    return cd;
  }
  /** 橙框小标签 */
  function tagp(c, parent, html, x, y) { return c.div('tagp', x, y, null, null, html, parent); }
  /** 选项小块（浅底 / on 橙 / dk 深） */
  function opt(c, parent, html, x, y, o = {}) {
    const e = c.div('opt' + (o.kind ? ' ' + o.kind : ''), x, y, null, o.h || 46, html, parent);
    if (o.size) e.style.fontSize = o.size + 'px';
    if (o.h) e.style.lineHeight = (o.h - (o.border ? 4 : 0)) + 'px';
    if (o.border) e.style.border = o.border;
    return e;
  }
  const checkSvg = (col = '#FF4F1A', w = 4.5, size = 26, mr = 10) =>
    `<svg width="${size}" height="${Math.round(size * 28 / 30)}" viewBox="0 0 30 28" style="vertical-align:-3px;margin-right:${mr}px">${ICON.check(col, w)}</svg>`;
  /** 深色径向底（大字下面垫一层，背景再花也看得清） */
  function scrim(c, cx, cy, w, h, t0, t1, a = 0.6) {
    if (LIGHT) return null;                               // 白底不垫
    const e = c.div('', cx - w / 2, cy - h / 2, w, h, '');
    e.style.background = `radial-gradient(closest-side, rgba(14,16,28,${a}), rgba(14,16,28,${(a * 0.56).toFixed(2)}) 55%, rgba(14,16,28,0))`;
    return c.show(e, t0, t1, 0, 0.45);
  }
  /** 小节标题（左上，章节标题下面）：橙竖条 + 大字 */
  function heading(c, html, at, until, o = {}) {
    const e = tx(c, null, o.x || 470, o.y || 184, `<span style="display:inline-block;width:8px;height:40px;background:var(--orange);margin-right:18px;vertical-align:-5px"></span>${html}`,
      `900 ${o.size || 46}px var(--cjk)`, { lh: 62, color: FG });
    c.show(e, at, until, 10);
    c.cue(at, 'word');
    return e;
  }
  /** 从左往右长出来的横条（外层 wrap 可以另挂透明度轨道，内层只做 scaleX） */
  function grow(c, parent, x, y, w, h, col, at, d = 0.55, r = 4) {
    const wr = c.div('', x, y, Math.max(2, w), h, '', parent);
    const b = c.div('', 0, 0, Math.max(2, w), h, '', wr);
    Object.assign(b.style, { background: col, borderRadius: r + 'px', transformOrigin: '0 50%', transform: 'scaleX(0)' });
    c.T(null, { g: 0 }, p => { b.style.transform = `scaleX(${p.g.toFixed(3)})`; }).to(at, { g: 1 }, d, E.out);
    return { wrap: wr, bar: b };
  }
  /** 画出来的线（SVG path，按 pathLength 描出来）。pts 是 parent 里的坐标 */
  function drawLine(c, parent, pts, col, w, at, d = 0.5, until) {
    const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
    const mnx = Math.min(...xs) - 12, mny = Math.min(...ys) - 12;
    const W = Math.max(...xs) - mnx + 12, H = Math.max(...ys) - mny + 12;
    const dd = pts.map((p, i) => `${i ? 'L' : 'M'}${(p[0] - mnx).toFixed(1)} ${(p[1] - mny).toFixed(1)}`).join(' ');
    const sv = c.svg(mnx, mny, W, H, `<path d="${dd}" fill="none" stroke="${col}" stroke-width="${w}" stroke-linecap="butt" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`, parent);
    const pth = sv.querySelector('path');
    c.T(null, { p: 0 }, q => { pth.style.strokeDashoffset = (1 - q.p).toFixed(4); }).to(at, { p: 1 }, d, E.inOut);
    const tr = c.T(sv, { o: 0 }).to(at, { o: 1 }, 0.1);
    if (until != null) tr.out(until);
    return sv;
  }
  /** 盖章（外层做淡入 + 轻微缩放，内层带旋转） */
  function stamp(c, parent, text, x, y, at, o = {}) {
    const w = o.w || 230, h = o.h || 84;
    const outer = c.div('', x, y, w, h, '', parent);
    const inner = c.div('stamp', 0, 0, w, h, text, outer);
    inner.style.lineHeight = (h - 10) + 'px';
    inner.style.transform = `rotate(${o.rot != null ? o.rot : -8}deg)`;
    c.T(outer, { o: 0, s: 1.08 }).to(at, { o: 1, s: 1 }, 0.25, E.out);
    c.cue(at, 'stamp');
    return outer;
  }
  /** 官网宣传语卡（示意，只用文字，不用官网截图）：kind 'speed' =「快 193.6 倍」，'zero' =「零幻觉 Zero Hallucinations」 */
  function promoCard(c, o) {
    const w = o.w || 520, h = 230;
    const cd = c.card(o.x, o.y, w, h, o.parent);
    cd.style.transformOrigin = '0 0';
    tagp(c, cd, '官网宣传语 · 2026-09-28', 28, 22);
    c.div('shiyi', w - 78, 20, null, null, '示意', cd);
    if (o.kind === 'speed') {
      tx(c, cd, 28, 78, '快 <span class="mono or">193.6</span> 倍', '900 80px var(--cjk)', { lh: 116 });
    } else {
      tx(c, cd, 28, 64, '零幻觉', '900 80px var(--cjk)', { lh: 104 });
      tx(c, cd, 31, 168, 'Zero Hallucinations', '700 30px var(--mono)', { lh: 40, color: '#4A4741' });
    }
    return cd;
  }
  /** 一排「A → B → …」小块（深色背景上）：items [{html, cls, at, size}]，箭头随后一块出现 */
  function lane(c, parent, x, y, items, h = 46) {
    let xx = x;
    return items.map((it, i) => {
      if (i) {
        const a = c.arrow(xx + 10, y + h / 2, xx + 48, y + h / 2, LINE, { w: 3.5, head: 11, parent });
        c.T(a, { o: 0 }).to(it.at - 0.05, { o: 1 }, 0.25);
        xx += 58;
      }
      const e = c.div(it.cls || 'chip', xx, y, null, h, it.html, parent);
      e.style.fontSize = (it.size || 24) + 'px';
      c.show(e, it.at, null, 6);
      c.cue(it.at, 'item');
      xx += e.offsetWidth;
      return e;
    });
  }
  /** 竖向步骤条（和 c.steps 同一套样式 .step/.sc/.st/.ss）：active[i] 起橙色实心，done[i] 起打勾。
   *  和 c.steps 的区别只有一处：打勾后数字用 visibility 藏起来（c.steps 把数字设成透明色，layout 检查会当成低对比度文字） */
  function stepper(c, o) {
    const x = o.x, y0 = o.y, step = o.step || 118, n = o.items.length;
    return o.items.map(([a, b], i) => {
      const st = c.div('step', x, y0 + i * step);
      const sc = c.div('sc', 0, 10, null, null, '', st);
      const num = ENG.el('span', '', sc, String(i + 1));
      const ck = c.svg(10, 22, 32, 28, '<path d="M5 14 L 12 21 L 25 6" fill="none" stroke="#FF4F1A" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>', st);
      const path = ck.querySelector('path');
      const t1 = c.div('st', 68, 8, null, null, a, st), t2 = c.div('ss', 68, 44, null, null, b || '', st);
      if (i < n - 1) { const ln = c.div('', 25, 70, 3, step - 66, '', st); ln.style.background = LIGHT ? 'rgba(20,20,20,.18)' : 'rgba(237,234,227,.25)'; }
      const tr = c.T(st, { o: 0, y: 10, a: 0, d: 0 }, (p, tk) => {
        const on = p.a > 0.5, dn = p.d > 0.02, key = (on ? 1 : 0) + (dn ? 2 : 0);
        if (tk._k !== key) {
          sc.classList.toggle('fillo', on && !dn);
          sc.style.borderColor = dn ? 'var(--orange)' : '';
          num.style.visibility = dn ? 'hidden' : '';
          t1.style.color = on || dn ? FG : '';
          t2.style.color = on ? (LIGHT ? 'rgba(20,20,20,.7)' : 'rgba(237,234,227,.8)') : '';
          tk._k = key;
        }
        const dd = Math.round(p.d * 100) / 100;
        if (tk._d !== dd) { path.style.strokeDashoffset = 1 - dd; tk._d = dd; }
      });
      tr.in(o.at + i * 0.12);
      c.cue(o.at + i * 0.12, 'step');
      if (o.active && o.active[i] != null) { tr.to(o.active[i], { a: 1 }, 0.2); c.cue(o.active[i], 'step'); }
      if (o.done && o.done[i] != null) tr.to(o.done[i], { a: 0 }, 0.2).to(o.done[i] + 0.05, { d: 1 }, 0.25);
      if (o.until != null) tr.out(o.until);
      return { el: st, tr };
    });
  }
  /** 「A → B」一行（纸白卡片里）：A 浅底，B 橙底，tail 是 B 后面的灰色补充 */
  function arrowRow(c, parent, x, y, a, b, tA, tB, tail) {
    const ea = opt(c, parent, a, x, y, { h: 52, size: 26 });
    const ax0 = x + ea.offsetWidth + 12;
    const ar = c.arrow(ax0, y + 26, ax0 + 62, y + 26, '#FF4F1A', { w: 4, head: 13, parent });
    const eb = opt(c, parent, b, ax0 + 78, y, { h: 52, size: 26, kind: 'on' });
    c.show(ea, tA, null, 6); c.cue(tA, 'item');
    c.T(ar, { o: 0 }).to(tB - 0.15, { o: 1 }, 0.25);
    c.show(eb, tB, null, 6); c.cue(tB, 'item');
    if (tail) c.show(tx(c, parent, ax0 + 78 + eb.offsetWidth + 14, y + 10, tail, '600 22px var(--cjk)', { color: '#4A4741', lh: 32 }), tB + 0.2, null, 6);
    return { ea, eb };
  }

  // ================================================================== S01 开场白：大字「Jev」
  ENG.scene('S01', c => {
    const s0 = c.seg(0), g = c.gap(s0);
    const at = c.P(s0, '今天', 0.3) - 0.15, tOut = g ? g.start : s0.end;   // 结尾停顿里：大字缩小、淡出
    const bw = c.bigWord({
      text: 'Jev', kicker: `原LAI如此 · #${ENG.pad2(ENG.EP.number)}`, at,
      sub: '<span class="mono">TypeSafe AI</span> 的 <span class="mono or">System One</span> 模型 · <span class="mono">2026-09</span>',
      scrim: !LIGHT,
    });
    if (LIGHT) { const w = bw.el.querySelector('.bw'); if (w) w.style.color = 'var(--ink)'; }
    bw.trs.forEach(tr => tr.to(tOut, { o: 0, s: 0.92 }, 0.4, E.sine));
    c.cue(at + 0.35, 'word');
  });

  // ================================================================== S02 三个疑问
  ENG.scene('S02', c => {
    const s = c.segs();                                   // s[0] S02-02 … s[7] S02-09
    const tNews = s[0].start + 0.15;
    const tAway = s[3].start + 0.15;                      // 「你可能会有三个疑问」：前面的卡片缩小移到左边
    const SC = 0.42, COLX = 460;                          // 缩小后的左栏
    // ---- 新闻标题卡（示意：不写真实媒体名、不用 logo）
    const NX = 750, NY = 196, NW = 800, NH = 214;
    const nw = paper(c, NX, NY, NW, NH, { kicker: 'HEADLINE · 新闻标题', shiyi: true });
    nw.style.transformOrigin = '0 0';
    tx(c, nw, 36, 52, '新模型 <span class="or">Jev</span> 刷屏', '900 60px var(--cjk)', { lh: 84 });
    [[36, 150, 620], [36, 178, 440]].forEach(([x, y, w]) => { const l = c.div('', x, y, w, 12, '', nw); Object.assign(l.style, { background: '#D6D1C7', borderRadius: '6px' }); });
    c.T(nw, { o: 0, y: 14 }).in(tNews, 0.4).to(tAway, { x: COLX - NX, y: 236 - NY, s: SC }, 0.6, E.inOut);
    c.cue(tNews, 'card');

    // ---- 标题卡下：三个划掉的标签 + 橙色「只做判断 ✓」
    const tTag = [P('S02-03', '不聊天', 0.05), P('S02-03', '不写文章', 0.25), P('S02-03', '一个字都不生成', 0.45)];
    const tJudge = P('S02-03', '只做判断', 0.8) - 0.05;
    const TY = 440;
    const tags = ['聊天', '写文章', '生成文字'].map(t => { const e = c.div('chip line', 0, TY, null, 56, t); Object.assign(e.style, { fontSize: '30px', padding: '0 22px' }); return e; });
    const jd = c.div('chip o', 0, TY, null, 56, `只做判断 ${checkSvg('#EDEAE3', 5, 28, 0)}`);
    Object.assign(jd.style, { fontSize: '30px', padding: '0 22px' });
    const row = [...tags, jd];
    let xx = 1150 - (row.reduce((a, e) => a + e.offsetWidth, 0) + 18 * (row.length - 1)) / 2;
    row.forEach(e => { e.style.left = xx + 'px'; xx += e.offsetWidth + 18; });
    tags.forEach((e, i) => {
      const st = c.div('', 14, 24, e.offsetWidth - 32, 4, '', e);                  // 删除线（从左往右划）
      Object.assign(st.style, { background: LIGHT ? 'rgba(20,20,20,.85)' : 'rgba(237,234,227,.95)', transformOrigin: '0 50%', borderRadius: '2px' });
      c.T(null, { g: 0 }, p => { st.style.transform = `scaleX(${p.g.toFixed(3)})`; }).to(tTag[i] + 0.3, { g: 1 }, 0.3);
      c.T(e, { o: 0, y: 8 }).in(tTag[i], 0.3).to(tTag[i] + 0.65, { o: 0.62 }, 0.3).to(tAway, { o: 0 }, 0.3);
      c.cue(tTag[i], 'item');
    });
    c.T(jd, { o: 0, y: 8 }).in(tJudge, 0.3).to(tAway, { o: 0 }, 0.3);
    c.cue(tJudge, 'item');

    // ---- 两张官网宣传语卡（示意，只用文字）
    const tP1 = P('S02-04', '比大模型', 0.3) - 0.05, tP2 = P('S02-04', '零幻觉', 0.8) - 0.25;
    const p1 = promoCard(c, { x: 610, y: 540, kind: 'speed' });
    const p2 = promoCard(c, { x: 1170, y: 540, kind: 'zero' });
    c.T(p1, { o: 0, y: 14 }).in(tP1, 0.4).to(tAway + 0.1, { x: COLX - 610, y: 342 - 540, s: SC }, 0.6, E.inOut);
    c.T(p2, { o: 0, y: 14 }).in(tP2, 0.4).to(tAway + 0.35, { x: COLX - 1170, y: 456 - 540, s: SC }, 0.6, E.inOut);   // 晚一点走：不从上一张卡片上面划过
    c.cue(tP1, 'card'); c.cue(tP2, 'card');

    // ---- 右侧「你可能也想问」+ 疑问卡（文字取 episode.questions）→ 本场最后一句结束时飞进右上目录
    // 白底：标题「你可能也想问」自己画成深色字（位置、出入时间和 c.questionCards 的默认标题一样）
    const qAt = s[3].start + 0.4;
    if (LIGHT) {
      const tIn = ENG.tocInTime();
      const qt = c.div('', 850, 116, 990, 70, '你可能也想问');
      Object.assign(qt.style, { textAlign: 'center', font: '900 54px var(--cjk)', color: 'var(--ink)', letterSpacing: '.06em' });
      c.show(qt, qAt, tIn, 10);
      c.show(c.div('bigRule', 850 + 990 / 2 - 40, 196, 80, 3), qAt + 0.15, tIn, 0);
    }
    c.questionCards({ at: [4, 5, 6].map(i => s[i].start + 0.05), titleAt: qAt, x: 850, w: 990, title: LIGHT ? false : undefined });
  });

  // ================================================================== S03 一、Jev 是什么
  ENG.scene('S03', c => {
    chapterTitle(c, SG('S03-10'));
    const t12 = T('S03-12'), t14 = T('S03-14'), t16 = T('S03-16'), t17 = T('S03-17');
    const t18 = T('S03-18'), t22 = T('S03-22'), t23 = T('S03-23'), t24 = T('S03-24'), t25 = T('S03-25'), t26 = T('S03-26'), t28 = T('S03-28');

    // ---- (a) S03-11 流程「材料 + 问题 → Jev → 答案 + 概率」；S03-12 缩到上方；S03-14 收起
    const fg = c.div('', 0, 0, null, null, '');
    fg.style.transformOrigin = '0 0';
    const tJ = T('S03-11') + 0.15, tA = P('S03-11', '材料和问题', 0.4) - 0.1, tB = P('S03-11', '返回答案', 0.8) - 0.15;
    const nA = c.card(470, 360, 360, 140, fg);
    tx(c, nA, 0, 0, '材料 + 问题', '800 40px var(--cjk)', { w: 360, align: 'center', lh: 138 });
    const nJ = c.div('node', 970, 346, 280, 168, '', fg);
    Object.assign(nJ.style, { border: '3px solid var(--orange)', background: 'rgba(20,20,20,.9)' });
    tx(c, nJ, 0, 20, 'Jev', '800 66px var(--mono)', { w: 274, align: 'center', lh: 82, color: 'var(--paper)' });
    tx(c, nJ, 0, 104, '只做判断', '700 24px var(--cjk)', { w: 274, align: 'center', lh: 34, color: 'rgba(237,234,227,.82)' });
    const nB = c.card(1430, 360, 400, 140, fg);
    tx(c, nB, 0, 0, '答案 + 概率', '800 40px var(--cjk)', { w: 400, align: 'center', lh: 138 });
    const a1 = c.arrow(842, 430, 960, 430, '#FF4F1A', { w: 5, head: 16, parent: fg });
    const a2 = c.arrow(1262, 430, 1420, 430, '#FF4F1A', { w: 5, head: 16, parent: fg });
    const l2 = tx(c, fg, 1256, 374, '不生成文字', '800 24px var(--cjk)', { w: 170, align: 'center', color: 'var(--orange)', lh: 34 });
    c.show(nJ, tJ, null, 12);
    c.show(nA, tA, null, 12); c.T(a1, { o: 0 }).to(tA + 0.25, { o: 1 }, 0.3);
    c.show(nB, tB, null, 12); c.T(a2, { o: 0 }).to(tB - 0.2, { o: 1 }, 0.3); c.show(l2, tB - 0.05, null, 6);
    c.cue(tJ, 'node'); c.cue(tA, 'node'); c.cue(tB, 'node');
    // 缩到上方（中心 x 1150、y 150–234），S03-14 淡出
    c.T(fg, { o: 1 }).to(t12, { x: 575, y: -23, s: 0.5 }, 0.6, E.inOut).to(OUT('S03-14'), { o: 0 }, 0.3, E.sine);

    // ---- (b) S03-12 信息卡：TypeSafe AI · 2026-09-15 发布（美国时间）+ 一行小字
    const tInfo = t12 + 0.5, tDate = P('S03-12', '2026年', 0.55) - 0.1;
    const ic = paper(c, 560, 300, 1180, 344, { kicker: 'COMPANY · 开发公司' });
    tx(c, ic, 40, 50, 'TypeSafe AI', '800 76px var(--mono)', { lh: 96 });
    const dt = tx(c, ic, 40, 152, '<span class="mono">2026-09-15</span> 发布<span style="font:600 26px var(--cjk);color:var(--grey);margin-left:16px">（美国时间）</span>', '800 50px var(--cjk)', { lh: 66 });
    c.div('dash', 40, 234, 1100, null, '', ic);
    const i1 = tx(c, ic, 40, 252, '旧金山 · CEO 是 InstructGPT 论文作者之一', '600 24px var(--cjk)', { color: '#4A4741', lh: 34 });
    const i2 = tx(c, ic, 40, 290, '名字取自经济学家杰文斯 · 和 LeCun 的 JEPA 没有关系', '600 24px var(--cjk)', { color: '#4A4741', lh: 34 });
    c.show(ic, tInfo, OUT('S03-13'), 14); c.cue(tInfo, 'card');
    c.show(dt, tDate, null, 8); c.cue(tDate, 'item');
    c.show(i1, tDate + 0.5, null, 6); c.show(i2, tDate + 0.9, null, 6);

    // ---- (c) S03-13「System One 模型 ＝ 系统一模型」
    const tNm = P('S03-13', 'System One', 0.3) - 0.3, tNm2 = P('S03-13', '也就是系统一模型', 0.6) - 0.05;
    const nm = paper(c, 560, 330, 1180, 200, { kicker: 'NAME · 他们的叫法' });
    const nmA = tx(c, nm, 0, 62, '<span class="mono or">System One</span> 模型', '900 64px var(--cjk)', { lh: 100 });
    const nmB = tx(c, nm, 0, 62, '＝ 系统一模型', '900 64px var(--cjk)', { lh: 100 });
    const nx0 = Math.round((1180 - nmA.offsetWidth - 30 - nmB.offsetWidth) / 2);
    nmA.style.left = nx0 + 'px'; nmB.style.left = (nx0 + nmA.offsetWidth + 30) + 'px';
    c.show(nm, tNm, OUT('S03-14'), 14); c.cue(tNm, 'card');
    c.show(nmB, tNm2, null, 8); c.cue(tNm2, 'item');

    // ---- (d) S03-14–16 卡尼曼《思考，快与慢》两栏：系统一 / 系统二；「Jev」落到系统一下面
    const kc = paper(c, 500, 196, 1300, 572, { kicker: 'INSPIRATION · 名字的灵感' });
    tx(c, kc, 40, 48, '《思考，快与慢》<span style="color:var(--grey)"> · </span>丹尼尔·卡尼曼<span style="font:600 26px var(--cjk);color:#4A4741">（心理学家）</span>', '900 40px var(--cjk)', { lh: 56 });
    const kn = tx(c, kc, 40, 112, '“系统一 / 系统二”的叫法最早由 Stanovich 和 West 提出，这本书让它出了名', '500 21px var(--cjk)', { color: 'var(--grey)', lh: 30 });
    c.div('dash', 40, 156, 1220, null, '', kc);
    const cL = c.div('inbox', 40, 180, 596, 352, '', kc), cR = c.div('inbox', 664, 180, 596, 352, '', kc);
    const colText = (col, a, b, d, orange) => {
      const g = c.div('', 0, 0, 596, 230, '', col);
      tx(c, g, 36, 30, a, '900 60px var(--cjk)', { lh: 76 });
      tx(c, g, 36, 114, b, '800 40px var(--cjk)', { lh: 52, color: orange ? 'var(--orange)' : 'var(--ink)' });
      tx(c, g, 36, 176, d, '500 24px var(--cjk)', { lh: 34, color: '#4A4741' });
      return g;
    };
    const gL = colText(cL, '系统一', '快 · 直觉', '凭直觉，一眼做出判断', true);
    const gR = colText(cR, '系统二', '慢 · 推理', '慢慢想，一步步推理', false);
    const tK = t14 + 0.1, tL = P('S03-15', '人凭直觉', 0.05), tR = P('S03-15', '慢慢想', 0.5);
    c.show(kc, tK, OUT('S03-17'), 14); c.cue(tK, 'card');
    c.show(kn, P('S03-14', '卡尼曼', 0.5) + 0.3, null, 6);
    c.show(gL, tL, null, 10); c.cue(tL, 'item');
    c.show(gR, tR, null, 10); c.cue(tR, 'item');
    const tJd = t16 + 0.1;
    const jrow = c.div('', 36, 246, 540, 64, '', cL);
    const jchip = c.div('', 0, 0, null, 60, 'Jev', jrow);
    Object.assign(jchip.style, { background: 'var(--ink)', color: 'var(--orange)', font: '800 38px var(--mono)', lineHeight: '60px', padding: '0 24px', borderRadius: '8px', whiteSpace: 'nowrap' });
    const jl = tx(c, jrow, jchip.offsetWidth + 18, 14, '官方文档：快速、聚焦的判断', '700 24px var(--cjk)', { lh: 34, color: '#4A4741' });
    c.T(jchip, { o: 0, y: -36 }).to(tJd, { o: 1, y: 0 }, 0.4, E.out);
    c.show(jl, P('S03-16', '懂行的人', 0.3), null, 6);
    c.cue(tJd, 'item');
    c.ring(540, 376, 596, 352, tJd, OUT('S03-17') - 0.1);

    // ---- (e) S03-17 左：客服工单（示意，虚构）＝ state；S03-18–21 右：三个题框
    const WX = 470, WY = 236, WW = 540, WH = 270;
    const tWo = t17 + 0.15, tSt = P('S03-17', 'state', 0.4);
    const wo = paper(c, WX, WY, WW, WH, { kicker: 'TICKET · 客服工单', shiyi: true });
    tx(c, wo, 36, 50, '用户留言（虚构内容）', '600 20px var(--cjk)', { color: 'var(--grey)', lh: 28 });
    tx(c, wo, 36, 88, '我前天买的耳机还没发货，<br>明天出差前必须收到，<br>不然就退款！', '800 34px var(--cjk)', { lh: 50 });
    c.show(wo, tWo, OUT('S03-22'), 14); c.cue(tWo, 'card');
    c.bracket(WX, WY + WH + 14, WW, '<span class="mono or">state</span>（材料）', { at: tSt, until: OUT('S03-22'), size: 32 });
    c.cue(tSt, 'item');
    const QX = 1070, QW = 770, QH = 150, QY = [206, 376, 546];
    const QB = [
      { zh: '选择题', en: 'Choice', note: '最多 255 个选项', at: T('S03-19') + 0.05, cAt: P('S03-19', '选项里挑一个', 0.3) },
      { zh: '打分题', en: 'Score', note: '2–10 个等级', at: T('S03-20') + 0.05, cAt: P('S03-20', '等级打分', 0.3) },
      { zh: '是非题', en: 'Noul', note: 'Noul 取自 Bernoulli（伯努利）', at: T('S03-21') + 0.05, cAt: P('S03-21', '急不急', 0.7) - 0.25 },
    ];
    const tPh = t18 + 0.15;
    c.cue(tPh, 'card');
    QB.forEach((q, i) => {
      const ph = c.div('qph', QX, QY[i], QW, QH, '');
      tx(c, ph, 0, 0, `题 <span class="mono">${'①②③'[i]}</span>`, '800 40px var(--cjk)', { w: QW - 5, align: 'center', lh: QH - 5, color: LIGHT ? 'rgba(20,20,20,.35)' : 'rgba(237,234,227,.62)' });
      c.T(ph, { o: 0, y: 10 }).in(tPh + 0.12 * i, 0.35).to(q.at + 0.1, { o: 0 }, 0.3);
      const cd = c.card(QX, QY[i], QW, QH);
      badge(c, cd, 26, 22, i + 1, 44, 24);
      tx(c, cd, 86, 16, `${q.zh}<span style="font:700 26px var(--mono);color:var(--grey);margin-left:14px">${q.en}</span>`, '900 38px var(--cjk)', { lh: 54 });
      const nt = tx(c, cd, QW - 380, 28, q.note, '600 19px var(--cjk)', { w: 354, align: 'right', color: 'var(--grey)', lh: 28 });
      const rw = c.div('', 30, 84, QW - 60, 50, '', cd);
      if (i === 0) {
        let ox = 0;
        ['物流组', '退款组', '技术组'].forEach(t => { const e = opt(c, rw, t, ox, 0, { h: 48, size: 26 }); ox += e.offsetWidth + 14; });
      } else if (i === 1) {
        let ox = 0;
        [['0', '平静', '#E4DFD5'], ['1', '不满', '#F6C9B3'], ['2', '非常愤怒', '#FF9A73']].forEach(([n, t, bg], k) => {
          const e = opt(c, rw, `<span class="mono" style="color:#6E6A63;margin-right:10px">${n}</span>${t}`, ox, 0, { h: 48, size: 26 });
          e.style.background = bg;
          e.style.borderRadius = k === 0 ? '8px 0 0 8px' : k === 2 ? '0 8px 8px 0' : '0';
          ox += e.offsetWidth + 3;
        });
        tx(c, rw, ox + 16, 8, '由轻到重', '600 20px var(--cjk)', { color: 'var(--grey)', lh: 32 });
      } else {
        const e = opt(c, rw, '紧急吗？', 0, 0, { h: 48, size: 26, kind: 'dk' });
        tx(c, rw, e.offsetWidth + 18, 8, '<span class="or">→</span> “是”的概率有多大', '700 24px var(--cjk)', { color: '#4A4741', lh: 32 });
      }
      c.show(cd, q.at, OUT('S03-22'), 12); c.cue(q.at, 'card');
      c.show(rw, q.cAt, null, 6); c.cue(q.cAt, 'item');
      c.show(nt, q.cAt + 0.45, null, 6);
    });

    // ---- (f) S03-22 请求代码卡（示意·已简化，Key 打码）→ S03-23 右边返回体（数值虚构），念到哪行亮哪行
    const rq = c.code({ x: 440, y: 190, w: 700, h: 560, title: '发给 Jev 的请求', kicker: 'REQUEST', lines: [
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
    rq.tr.in(t22 + 0.1).out(OUT('S03-24'));
    c.focus(rq, P('S03-22', '三道题一起', 0.1) + 0.35, [7, 8, 9]);        // 三道题同时亮起
    c.unfocus(rq, t23);
    const rs = c.code({ x: 1180, y: 190, w: 680, h: 520, title: 'Jev 返回', kicker: 'RESPONSE · 数值虚构', lines: [
      '{',
      '  "team": {',
      { t: '    "choice": "shipping",', c: '   // 物流组' },
      '    "probabilities": {',
      '      "shipping": 0.72, "refund": 0.28,',
      '      "tech": 0.00 },',
      '    "confidence": … },',
      '  "anger": { "score": 1.3 },',
      '  // 刻度：0 平静 · 1 不满 · 2 非常愤怒',
      '  "urgent": { "noul": 0.96 }',
      '}',
    ] });
    rs.tr.in(t23 + 0.1).out(OUT('S03-25'));
    c.focus(rs, P('S03-23', '交给物流组', 0.6) - 0.1, [2]);
    c.focus(rs, P('S03-23', '0.72', 0.75) - 0.1, [4]);
    c.focus(rs, P('S03-23', '紧急的概率', 0.85) - 0.1, [9]);
    c.unfocus(rs, t24 + 0.2);

    // ---- (g) S03-24 校准小图（示意）：对角线 + 标 0.8 约八成对（换掉左边的请求卡）
    const cal = paper(c, 440, 190, 700, 600, { kicker: 'CALIBRATION · 校准', shiyi: true });
    tx(c, cal, 36, 48, '校准：说几成把握，就大约对几成', '800 32px var(--cjk)', { lh: 46 });
    const GX = 150, GY = 440, GW = 380, GH = 280;
    let ax = '';
    [0.5, 1].forEach(f => {
      ax += `<line x1="${GX}" y1="${GY - f * GH}" x2="${GX + GW}" y2="${GY - f * GH}" stroke="#D2CCC1" stroke-width="1.5" stroke-dasharray="5 6"/>`;
      ax += `<line x1="${GX + f * GW}" y1="${GY}" x2="${GX + f * GW}" y2="${GY - GH}" stroke="#D2CCC1" stroke-width="1.5" stroke-dasharray="5 6"/>`;
    });
    ax += `<line x1="${GX}" y1="${GY}" x2="${GX + GW}" y2="${GY}" stroke="#141414" stroke-width="2.5"/><line x1="${GX}" y1="${GY}" x2="${GX}" y2="${GY - GH}" stroke="#141414" stroke-width="2.5"/>`;
    c.svg(0, 0, 700, 600, ax, cal);
    [['0', 0], ['0.5', 0.5], ['1', 1]].forEach(([l, f]) => tx(c, cal, GX + f * GW - 30, GY + 8, l, '600 18px var(--mono)', { w: 60, align: 'center', color: 'var(--grey)', lh: 24 }));
    [['0', 0], ['50%', 0.5], ['100%', 1]].forEach(([l, f]) => tx(c, cal, GX - 80, GY - f * GH - 12, l, '600 18px var(--mono)', { w: 66, align: 'right', color: 'var(--grey)', lh: 24 }));
    tx(c, cal, GX, GY + 38, '给出的概率 →', '700 21px var(--cjk)', { w: GW, align: 'center', color: '#4A4741', lh: 28 });
    tx(c, cal, 36, 112, '↑ 实际对的比例', '700 21px var(--cjk)', { color: '#4A4741', lh: 28 });
    const tDg = P('S03-24', '校准过的', 0.5) - 0.2, tPt = P('S03-24', '标0.8', 0.6) - 0.1;
    drawLine(c, cal, [[GX, GY], [GX + GW, GY - GH]], '#FF4F1A', 5, tDg, 0.9);
    const px = GX + 0.8 * GW, py = GY - 0.8 * GH;
    const gd = c.svg(0, 0, 700, 600, `<path d="M${px} ${GY} V${py} H${GX}" fill="none" stroke="#FF4F1A" stroke-width="2" stroke-dasharray="5 5"/>`, cal);
    c.T(gd, { o: 0 }).to(tPt, { o: 1 }, 0.3);
    const dot = c.div('', px - 11, py - 11, 22, 22, '', cal);
    Object.assign(dot.style, { borderRadius: '50%', background: 'var(--paper)', border: '5px solid var(--orange)' });
    c.show(dot, tPt, null, 0);
    const pl = tx(c, cal, px + 18, py + 8, '标 0.8 → 约八成对', '800 22px var(--cjk)', { color: 'var(--orange)', lh: 30 });
    c.show(pl, tPt + 0.15, null, 6);
    const cn = tx(c, cal, 36, 540, '官方定义：说的是大量预测的整体情况，不保证单个答案', '600 19px var(--cjk)', { color: 'var(--grey)', lh: 28 });
    c.show(cn, P('S03-24', '大约八成', 0.8) + 0.2, null, 6);
    c.show(cal, t24 + 0.1, OUT('S03-25'), 14); c.cue(t24 + 0.1, 'chart'); c.cue(tPt, 'item');

    // ---- (h) S03-25「新东西？」→ S03-26 缩到左上当小标题
    const tNew = t25 + 0.05;
    scrim(c, 1150, 455, 1000, 360, tNew - 0.1, t26, 0.55);
    const nq = tx(c, null, 0, 380, '新东西<span class="or">？</span>', '900 120px var(--cjk)', { lh: 150, color: FG });
    const nqx = Math.round(1150 - nq.offsetWidth / 2);
    nq.style.left = nqx + 'px'; nq.style.transformOrigin = '0 0';
    c.T(nq, { o: 0, y: 14 }).in(tNew, 0.35).to(t26, { x: 470 - nqx, y: 176 - 380, s: 0.4 }, 0.6, E.inOut);
    c.cue(tNew, 'word');

    // ---- (i) S03-26–28 对比卡：传统分类模型 vs Jev
    const cc = paper(c, 470, 256, 1360, 430, { kicker: 'COMPARE · 以前的分类模型 vs Jev' });
    c.svg(678, 60, 4, 282, '<line x1="2" y1="0" x2="2" y2="282" stroke="#B9B3A8" stroke-width="2" stroke-dasharray="8 7"/>', cc);
    tx(c, cc, 40, 54, '传统分类模型', '900 42px var(--cjk)', { lh: 58 });
    const fl = c.div('', 40, 138, 600, 52, '', cc);
    const fa = opt(c, fl, '文本', 0, 0, { h: 52, size: 28 });
    c.arrow(fa.offsetWidth + 12, 26, fa.offsetWidth + 72, 26, '#141414', { w: 4, head: 13, parent: fl });
    opt(c, fl, '类别概率', fa.offsetWidth + 88, 0, { h: 52, size: 28, kind: 'dk' });
    const bert = tx(c, cc, 40, 204, '例如 2018 年的 BERT，常用来做分类', '600 21px var(--cjk)', { color: 'var(--grey)', lh: 30 });
    const lk = tx(c, cc, 40, 262, `<svg width="26" height="30" viewBox="0 0 14 16" style="vertical-align:-3px;margin-right:14px">${ICON.lock()}</svg>类别：训练时定好`, '800 32px var(--cjk)', { lh: 46 });
    const hR = tx(c, cc, 724, 48, 'Jev', '800 52px var(--mono)', { lh: 64, color: 'var(--orange)' });
    const RI = [
      ['题目、选项用文字现写<span style="font:600 21px var(--cjk);color:var(--grey);margin-left:14px">不用重新训练</span>', P('S03-28', '题目和选项', 0.2) + 0.3],
      ['一次问多道题', P('S03-28', '不用重新训练', 0.8) + 0.1],
    ];
    RI.push(['概率经过校准', RI[1][1] + 0.45]);
    const ri = RI.map(([h, at], i) => { const e = tx(c, cc, 724, 138 + i * 62, `${checkSvg('#FF4F1A', 4.5, 28, 14)}${h}`, '800 30px var(--cjk)', { lh: 46 }); c.show(e, at, null, 6); c.cue(at, 'item'); return e; });
    c.div('dash', 40, 356, 1280, null, '', cc);
    const laya = tx(c, cc, 40, 372, '类似思路的开源模型：<span class="mono">Laya</span>（别人做的，不是 Jev；Jev 本身没开源）', '600 21px var(--cjk)', { color: 'var(--grey)', lh: 30 });
    const tCc = t26 + 0.45;
    c.show(cc, tCc, null, 14); c.cue(tCc, 'card');
    c.show(fl, P('S03-26', '分类模型', 0.5) - 0.1, null, 6);
    c.show(bert, P('S03-26', '早就有了', 0.9) + 0.1, null, 6);
    c.show(lk, P('S03-27', '训练时就定好', 0.7) - 0.2, null, 6); c.cue(P('S03-27', '训练时就定好', 0.7) - 0.2, 'item');
    c.show(hR, t28 + 0.05, null, 8);
    c.show(laya, RI[2][1] + 0.5, null, 6);


    // ---- (j) S03-29 结论条「Jev ＝ 通用的判断模型」
    const tC = P('S03-29', '通用的判断模型', 0.5) - 0.3;
    const cb = c.div('', 0, 718, null, 84, '<span class="mono or">Jev</span> ＝ 通用的判断模型');
    Object.assign(cb.style, { background: 'var(--ink)', color: 'var(--paper)', font: '900 44px var(--cjk)', lineHeight: '84px', padding: '0 42px', borderRadius: '8px', borderLeft: '8px solid var(--orange)', whiteSpace: 'nowrap', boxShadow: '0 12px 30px rgba(0,0,0,.34)' });
    cb.style.left = Math.round(1150 - cb.offsetWidth / 2) + 'px';
    c.show(cb, tC, null, 12); c.cue(tC, 'card');
  });

  // ================================================================== S04 二、和 LLM 的区别
  ENG.scene('S04', c => {
    chapterTitle(c, SG('S04-30'));
    const t31 = T('S04-31'), t32 = T('S04-32'), t33 = T('S04-33'), t34 = T('S04-34'), t37 = T('S04-37'), t38 = T('S04-38');
    const t39 = T('S04-39'), t42 = T('S04-42'), t43 = T('S04-43'), t44 = T('S04-44');

    // ---- (a) S04-31「LLM」三个大字母 + 全称；S04-32 缩成左边的 LLM 卡
    const lg = c.div('', 0, 0, null, null, '');
    lg.style.transformOrigin = '0 0';
    const lsc = c.div('', 1150 - 680, 180, 1360, 470, '', lg);
    lsc.style.background = 'radial-gradient(closest-side, rgba(14,16,28,.6), rgba(14,16,28,.34) 55%, rgba(14,16,28,0))';
    if (LIGHT) lsc.style.display = 'none'; else c.show(lsc, t31, null, 0, 0.45);
    ['L', 'L', 'M'].forEach((L, i) => c.show(tx(c, lg, 1150 + (i - 1) * 150 - 70, 196, L, '800 170px var(--mono)', { w: 140, align: 'center', lh: 190, color: 'var(--orange)' }), t31 + 0.1 + 0.12 * i, null, 12));
    c.cue(t31 + 0.1, 'word');
    const tFn = P('S04-31', 'Large', 0.3) - 0.1, tZh = P('S04-31', '大语言模型', 0.4) - 0.1, tEx = P('S04-31', 'ChatGPT', 0.6) - 0.1;
    c.show(tx(c, lg, 450, 400, '<span class="or">L</span>arge <span class="or">L</span>anguage <span class="or">M</span>odel', '700 52px var(--mono)', { w: 1400, align: 'center', lh: 66, color: FG }), tFn, null, 8);
    c.show(tx(c, lg, 450, 474, '大语言模型', '900 58px var(--cjk)', { w: 1400, align: 'center', lh: 76, color: FG }), tZh, null, 8);
    c.show(tx(c, lg, 450, 566, 'ChatGPT、DeepSeek、Claude……', '600 28px var(--cjk)', { w: 1400, align: 'center', lh: 40, color: FG2 }), tEx, null, 8);
    c.cue(tFn, 'word'); c.cue(tZh, 'word'); c.cue(tEx, 'word');
    c.T(lg, { o: 1 }).to(t32, { o: 0, x: 250, y: 158, s: 0.4 }, 0.5, E.inOut);

    // ---- S04-32 LLM 卡 ≠ Jev 卡
    const tL = t32 + 0.15, tJv = t32 + 0.45, tNe = P('S04-32', '不算LLM', 0.4) - 0.1, tNt = P('S04-32', '不生成语言', 0.7) - 0.1;
    const lc = paper(c, 480, 200, 460, 236, { kicker: 'LARGE LANGUAGE MODEL' });
    tx(c, lc, 36, 44, 'LLM', '800 84px var(--mono)', { lh: 100 });
    tx(c, lc, 36, 148, '大语言模型', '800 32px var(--cjk)', { lh: 44 });
    tx(c, lc, 36, 194, 'ChatGPT、DeepSeek、Claude……', '500 20px var(--cjk)', { color: 'var(--grey)', lh: 28 });
    const jc = paper(c, 1260, 200, 460, 236, { kicker: 'SYSTEM ONE MODEL' });
    tx(c, jc, 36, 44, 'Jev', '800 84px var(--mono)', { lh: 100, color: 'var(--orange)' });
    tx(c, jc, 36, 148, '只做判断，不生成语言', '800 32px var(--cjk)', { lh: 44 });
    tx(c, jc, 36, 194, 'System One 模型', '500 20px var(--cjk)', { color: 'var(--grey)', lh: 28 });
    const ne = c.div('', 1056, 274, 88, 88, '≠');
    Object.assign(ne.style, { font: '800 56px var(--cjk)', lineHeight: '82px', textAlign: 'center', color: 'var(--paper)', background: 'var(--ink)', border: '3px solid var(--orange)', borderRadius: '50%', boxShadow: '0 6px 16px rgba(0,0,0,.35)' });
    const nt = tx(c, null, 950, 378, '官方 FAQ · CEO：<br>不生成语言，所以不算 LLM', '600 20px var(--cjk)', { w: 300, align: 'center', lh: 30, color: LIGHT ? 'rgba(20,20,20,.78)' : 'rgba(237,234,227,.9)' });
    c.show(lc, tL, OUT('S04-34'), 14); c.cue(tL, 'card');
    c.show(jc, tJv, OUT('S04-34'), 14); c.cue(tJv, 'card');
    c.show(ne, tNe, OUT('S04-34'), 0); c.show(nt, tNt, OUT('S04-34'), 6); c.cue(tNe, 'item');

    // ---- S04-33 Jev 卡下面长出一根线 → 「预训练语言模型」底座；线旁标 RLCD
    const tLn = t33 + 0.1, tBase = P('S04-33', '语言模型的基础上', 0.4) - 0.1, tRl = P('S04-33', '训练出来的', 0.8), tGoal = P('S04-33', '训练目标', 0.6) - 0.1;
    drawLine(c, null, [[1490, 442], [1490, 632]], '#FF4F1A', 5, tLn, 0.5, OUT('S04-34'));
    c.node({ x: 1240, y: 640, w: 500, h: 120, title: '预训练语言模型', sub: '官方文档 · 底座是哪个模型没公开', size: 34, at: tBase, until: OUT('S04-34') });
    const rl = c.div('', 900, 470, 570, 160, '');
    tx(c, rl, 0, 0, 'RLCD', '800 34px var(--mono)', { w: 570, align: 'right', lh: 44, color: 'var(--orange)' });
    tx(c, rl, 0, 46, 'Reinforcement Learning for Calibrated Decisions', '600 19px var(--mono)', { w: 570, align: 'right', lh: 28, color: FG });
    tx(c, rl, 0, 76, '校准决策强化学习', '800 24px var(--cjk)', { w: 570, align: 'right', lh: 34, color: FG });
    const gl = tx(c, rl, 0, 116, '训练目标：给出判断和概率', '600 21px var(--cjk)', { w: 570, align: 'right', lh: 30, color: FG2 });
    c.show(rl, tRl, OUT('S04-34'), 8); c.show(gl, tGoal, null, 6);
    c.cue(tRl, 'item');

    // ---- (b) S04-34 起：三行对比表（输出 / 速度和价格 / 出错的方式 × LLM / Jev），逐行填
    const TX = 440, TY = 180, TW = 1420, TH = 488;
    const C0 = 36, C1 = 330, C2 = 912;
    const RY = [110, 214, 318], RH = [104, 104, 156];
    const tb = c.card(TX, TY, TW, TH);
    c.div('kicker', 36, 20, 900, null, 'THREE DIFFERENCES · 三点区别', tb);
    const tR = [P('S04-35', '第一', 0) - 0.05, P('S04-38', '第二', 0) - 0.05, P('S04-44', '第三', 0) - 0.05];
    RY.forEach((y, i) => {                               // 正在讲的那一行：浅橙底 + 左侧橙条
      const b = c.div('', 12, y, TW - 24, RH[i] - 6, '', tb);
      Object.assign(b.style, { background: 'rgba(255,79,26,.10)', borderLeft: '5px solid var(--orange)', borderRadius: '4px' });
      const tr = c.T(b, { o: 0 }).to(tR[i], { o: 1 }, 0.3);
      if (i < 2) tr.to(tR[i + 1], { o: 0 }, 0.3);
    });
    tx(c, tb, C1, 46, 'LLM', '800 36px var(--mono)', { lh: 48 });
    tx(c, tb, C2, 46, 'Jev', '800 36px var(--mono)', { lh: 48, color: 'var(--orange)' });
    c.div('', 36, 100, TW - 72, 3, '', tb).style.background = 'var(--ink)';
    [C1 - 20, C2 - 20].forEach(x => c.svg(x, 110, 4, 358, '<line x1="2" y1="0" x2="2" y2="358" stroke="#C9C3B8" stroke-width="2" stroke-dasharray="6 6"/>', tb));
    ['输出', '速度和价格', '出错的方式'].forEach((l, i) => {
      badge(c, tb, C0, RY[i] + 16, i + 1, 38, 21);
      tx(c, tb, C0 + 52, RY[i] + 12, l, '800 29px var(--cjk)', { lh: 44 });
      if (i < 2) c.div('dash', 36, RY[i] + RH[i] - 2, TW - 72, null, '', tb);
    });
    const tTb = t34 + 0.1;
    c.T(tb, { o: 0, y: 14 }).in(tTb, 0.4).to(OUT('S04-39'), { o: 0, y: -12 }, 0.3, E.sine).to(t44 + 0.1, { o: 1, y: 0 }, 0.4);
    c.cue(tTb, 'table'); c.cue(t44 + 0.1, 'table');
    tR.forEach(t => c.cue(t + 0.05, 'row'));

    // 第 1 行 · LLM：一行字逐个 token 出现（示意）
    const r1 = RY[0];
    const TOK = ['是', '，', '这条', '比较', '急', '，', '客户', '明天', '要', '出差', '……'];
    const tS0 = P('S04-35', '一个词一个词', 0.3), dTok = 0.17;
    const stream = c.div('', C1, r1 + 12, 552, 46, '', tb);
    Object.assign(stream.style, { font: '700 28px var(--cjk)', lineHeight: '46px', whiteSpace: 'nowrap' });
    TOK.forEach((w, i) => { const sp = ENG.el('span', 'tok' + (i % 2 ? ' b' : ''), stream, esc(w)); c.T(sp, { o: 0 }).to(tS0 + dTok * i, { o: 1 }, 0.08); });
    for (let fs = 28; stream.scrollWidth > 552 && fs > 20;) stream.style.fontSize = (--fs) + 'px';   // 一行放进 LLM 这一格
    c.cue(tS0, 'item');
    c.show(tx(c, tb, C1, r1 + 64, '这里的“词”指 token（词元）· 示意', '600 18px var(--cjk)', { color: 'var(--grey)', lh: 26 }), P('S04-35', '输出的是文字', 0.5), null, 6);
    // 第 1 行 · Jev：三个结果同时出现
    const tRs = P('S04-36', '一起算完', 0.3) - 0.1;
    const rsRow = c.div('', C2, r1 + 12, 480, 84, '', tb);
    let rx = 0;
    const rsEls = [['物流组 <span class="mono">0.72</span>', 'team'], ['<span class="mono">1.3</span>', 'anger'], ['<span class="mono">0.96</span>', 'urgent']].map(([h, k]) => {
      const e = opt(c, rsRow, h, rx, 0, { kind: 'dk', size: 26 });
      tx(c, rsRow, rx, 52, k, '600 15px var(--mono)', { w: e.offsetWidth, align: 'center', color: 'var(--grey)', lh: 22 });
      rx += e.offsetWidth + 14;
      return e;
    });
    tx(c, rsRow, rx + 2, 12, '数值虚构', '600 17px var(--cjk)', { color: 'var(--grey)', lh: 24 });
    c.show(rsRow, tRs, null, 8); c.cue(tRs, 'item');

    // S04-37 下方小示意：只问“急不急”——LLM 先写文字、程序再取答案；Jev 直接给 0.96
    const tGen = P('S04-37', '先生成文字', 0.5) - 0.15, tProg = P('S04-37', '程序再从', 0.3), tYes = P('S04-37', '取出来', 0.9) - 0.2;
    const tJ1 = tYes + 0.5, tMiniOff = t38 + 1.6;
    const ms = c.div('', 0, 0, null, null, '');
    c.show(tx(c, ms, 470, 686, `只问“急不急”：<span style="font:600 20px var(--cjk);color:${FG3};margin-left:10px">示意</span>`, '800 28px var(--cjk)', { lh: 40, color: FG }), t37 + 0.1, null, 6);
    lane(c, ms, 470, 736, [
      { html: '<span class="mono">LLM</span>', cls: 'chip dark', at: t37 + 0.35 },
      { html: '“是，这条比较急……”', at: tGen },
      { html: '程序：取出答案', cls: 'chip line', at: tProg },
      { html: '是', at: tYes, size: 26 },
    ]);
    lane(c, ms, 470, 810, [
      { html: '<span class="mono">Jev</span>', cls: 'chip o', at: tJ1 },
      { html: '<span class="mono">0.96</span>', at: tJ1 + 0.25, size: 26 },
    ]);
    const mj = tx(c, ms, 470 + 250, 818, '直接给出概率，不用再从文字里取', '600 22px var(--cjk)', { lh: 30, color: FG2 });
    c.show(mj, tJ1 + 0.45, null, 6);
    c.T(ms, { o: 1 }).out(tMiniOff);
    c.ringOn(rsEls[2], tJ1 + 0.25, tMiniOff, 2);

    // 第 2 行：输入输出都收费（输出约贵 5 倍） ｜ 只收输入 · $0.042 / 百万 token · 输出免费
    const r2 = RY[1];
    const tL2 = P('S04-38', 'LLM输入', 0.3), tL2b = P('S04-38', '输出还更贵', 0.6), tJ2 = P('S04-38', 'Jev只收', 0.8) - 0.1;
    c.show(tx(c, tb, C1, r2 + 12, '输入、输出都收费', '800 29px var(--cjk)', { lh: 42 }), tL2, null, 6);
    c.show(tx(c, tb, C1, r2 + 56, '输出约贵 <span class="mono">5</span> 倍', '700 24px var(--cjk)', { lh: 34, color: '#4A4741' }), tL2b, null, 6);
    c.show(tx(c, tb, C2, r2 + 12, '只收输入 · <span class="or">输出免费</span>', '800 29px var(--cjk)', { lh: 42 }), tJ2, null, 6);
    c.show(tx(c, tb, C2, r2 + 56, '<span class="mono">$0.042</span> / 百万 token', '700 24px var(--cjk)', { lh: 34, color: '#4A4741' }), tJ2 + 0.25, null, 6);
    c.show(tx(c, tb, C0 + 52, r2 + 56, '官方博客对照表 · 官方文档', '500 17px var(--cjk)', { color: 'var(--grey)', lh: 24 }), tL2 + 0.4, null, 6);
    c.cue(tL2, 'item'); c.cue(tJ2, 'item');

    // ---- (c) S04-39–43 表格让位：官方评测站横条（示意）+ 厂商自测章；右边「快 193.6 倍」回来、客户 Deel
    const bc = paper(c, 440, 180, 880, 640, { kicker: 'OFFICIAL EVALS · 官方评测站', shiyi: true });
    tx(c, bc, 36, 48, '四类实际业务：<span class="or">Jev</span> vs <span class="mono">GPT-5.6 Terra</span>', '800 32px var(--cjk)', { lh: 46 });
    tx(c, bc, 36, 100, '<span class="mono">evals.typesafe.ai</span> · 四类：安全告警、智能体记录审查、发票、客服', '500 18px var(--cjk)', { color: 'var(--grey)', lh: 26 });
    const sw = col => `<span style="display:inline-block;width:18px;height:18px;background:${col};border-radius:3px;vertical-align:-2px;margin-right:8px"></span>`;
    tx(c, bc, 36, 140, `${sw('var(--orange)')}Jev<span style="display:inline-block;width:30px"></span>${sw('#3A3833')}<span class="mono">GPT-5.6 Terra</span>`, '700 20px var(--cjk)', { lh: 28 });
    const BX0 = 210, BL = 470;
    const G = [
      { y: 196, lab: '准确率', a: [67.8, 67.9], mx: 100, v: ['67.8%', '67.9%'], at: P('S04-40', '准确率', 0.1), note: '以 GPT-6 Astra 和 Claude Fable 5.1 的平均答案为准' },
      { y: 336, lab: '每例用时', a: [0.4, 10.1], v: ['0.4 秒', '10.1 秒'], at: P('S04-40', '速度', 0.4) - 0.1, call: '← 快二十多倍' },
      { y: 456, lab: '每例成本', a: [0.0004, 0.0304], v: ['$0.0004', '$0.0304'], at: P('S04-40', '成本', 0.7) - 0.1, call: '← 百分之一多一点' },
    ];
    G.forEach(g => {
      tx(c, bc, 36, g.y + 20, g.lab, '800 26px var(--cjk)', { lh: 36 });
      const mx = g.mx || Math.max(...g.a);
      g.a.forEach((v, k) => {
        const len = Math.max(6, Math.round(BL * v / mx)), by = g.y + k * 44;
        grow(c, bc, BX0, by, len, 34, k ? '#3A3833' : 'var(--orange)', g.at + 0.15 * k, 0.6);
        const vl = tx(c, bc, BX0 + len + 12, by, g.v[k], '800 24px var(--mono)', { lh: 34, color: k ? 'var(--ink)' : 'var(--orange)' });
        c.show(vl, g.at + 0.15 * k + 0.4, null, 4);
        if (!k && g.call) c.show(tx(c, bc, BX0 + len + 12 + vl.offsetWidth + 16, by + 2, g.call, '800 22px var(--cjk)', { lh: 30, color: 'var(--orange)' }), g.at + 0.8, null, 4);
      });
      if (g.note) c.show(tx(c, bc, BX0, g.y + 88, g.note, '500 18px var(--cjk)', { color: 'var(--grey)', lh: 24 }), g.at + 0.6, null, 4);
      c.cue(g.at, 'item');
    });
    const tBn = P('S04-40', '百分之一多一点', 0.9) + 0.3;
    c.show(tx(c, bc, 36, 566, '最高的模型 <span class="mono">74.1%</span> · 分开看：发票 <span class="mono">61.8% vs 74.7%</span>、安全告警 <span class="mono">61.7% vs 51.2%</span>', '500 18px var(--cjk)', { color: 'var(--grey)', lh: 26 }), tBn, null, 4);
    c.show(tx(c, bc, 36, 596, '被比较的大模型套了 TypeSafe 的适配器，官方说这样往往更慢更贵', '500 18px var(--cjk)', { color: 'var(--grey)', lh: 26 }), tBn + 0.2, null, 4);
    c.show(bc, t39 + 0.1, OUT('S04-44'), 14); c.cue(t39 + 0.1, 'chart');
    stamp(c, bc, '厂商自测', 626, 200, P('S04-41', '厂商自己测', 0.3) - 0.1, { w: 220, h: 82, rot: -8 });
    // 「快 193.6 倍」卡回来 +「官方博客：偏高的一端」
    const tPc = t42 + 0.1, tHi = P('S04-42', '偏高', 0.5) - 0.25;
    const pc = promoCard(c, { x: 1350, y: 196, w: 510, kind: 'speed' });
    c.T(pc, { o: 0, x: -40 }).to(tPc, { o: 1, x: 0 }, 0.45, E.out).out(OUT('S04-44'));
    c.cue(tPc, 'card');
    c.chip('官方博客：偏高的一端', 1350, 440, { kind: 'o', size: 24, h: 46, at: tHi, until: OUT('S04-44') });
    c.cue(tHi, 'item');
    // 客户 Deel
    const tD = t43 + 0.1, tD4 = P('S04-43', '最多快4倍', 0.3) - 0.1;
    const dc = paper(c, 1350, 512, 510, 290, { kicker: 'CUSTOMER · 真实客户' });
    tx(c, dc, 32, 46, '客户 <span class="mono">Deel</span>', '900 38px var(--cjk)', { lh: 52 });
    tx(c, dc, 32, 104, '跟跑真实线上请求：', '700 24px var(--cjk)', { lh: 34, color: '#4A4741' });
    const d4 = tx(c, dc, 32, 138, '最多快 <span class="mono or">4</span> 倍', '900 52px var(--cjk)', { lh: 68 });
    tx(c, dc, 32, 210, '（离线测试 <span class="mono">2–3</span> 倍）', '700 24px var(--cjk)', { lh: 34, color: '#4A4741' });
    tx(c, dc, 32, 252, '官方 X 转述，2026-09-25', '500 18px var(--cjk)', { lh: 24, color: 'var(--grey)' });
    c.show(dc, tD, OUT('S04-44'), 14); c.cue(tD, 'card');
    c.show(d4, tD4, null, 8); c.cue(tD4, 'item');

    // ---- (d) S04-44 起表格回来：第 3 行 · LLM 编出「marketing」（红）｜ Jev 只落在给的选项里
    const r3 = RY[2];
    const tJs = P('S04-44', '编出一个', 0.7) - 0.3;
    const js = c.div('', C1, r3 + 12, null, 46, '{ "team": "<span class="mk">marketing</span>" }', tb);
    Object.assign(js.style, { background: '#1E1E1D', color: 'var(--paper)', font: '600 23px var(--mono)', lineHeight: '46px', padding: '0 16px', borderRadius: '8px', whiteSpace: 'nowrap' });
    Object.assign(js.querySelector('.mk').style, { color: '#FF6A5C', textDecoration: 'underline wavy #FF6A5C', textUnderlineOffset: '5px' });
    const er = c.div('errtag', C1 + js.offsetWidth + 14, r3 + 15, null, 40, `<svg width="20" height="20" viewBox="0 0 48 48" style="vertical-align:-3px;margin-right:6px">${ICON.x('#D8342A')}</svg>选项里没有`, tb);
    c.show(js, tJs, null, 6); c.show(er, tJs + 0.35, null, 4); c.cue(tJs, 'item');
    c.show(tx(c, tb, C1, r3 + 66, 'JSON 为示意 · LLM 加上结构化输出，也能限定在选项里', '600 18px var(--cjk)', { color: 'var(--grey)', lh: 24 }), tJs + 0.9, null, 6);
    const tOp = P('S04-45', '只能在你给的选项里', 0.2), tPick = tOp + 0.9;
    const opRow = c.div('', C2, r3 + 12, 480, 50, '', tb);
    let ox = 0;
    const ops = ['物流组', '退款组', '技术组'].map(t => { const e = opt(c, opRow, t, ox, 0, { h: 46, size: 24, border: '2px solid #BDB7AB' }); ox += e.offsetWidth + 12; return e; });
    c.T(null, { w: 0 }, p => { const on = p.w > 0.5; ops[0].classList.toggle('on', on); ops[0].style.borderColor = on ? 'var(--orange)' : '#BDB7AB'; }).to(tPick, { w: 1 }, 0.1);
    c.show(opRow, tOp, null, 6); c.cue(tOp, 'item'); c.cue(tPick, 'item');
    c.show(tx(c, tb, C2, r3 + 66, '结果只落在给的选项之一', '600 18px var(--cjk)', { color: 'var(--grey)', lh: 24 }), tPick + 0.3, null, 6);
    // 「零幻觉」卡回来 +「＝ 不越界」
    const tZ = P('S04-45', '零幻觉', 0.5) - 0.35;
    const zc = promoCard(c, { x: 440, y: 684, kind: 'zero' });
    c.T(zc, { o: 0, x: -40, s: 0.9 }).to(tZ, { o: 1, x: 0 }, 0.45, E.out);
    c.cue(tZ, 'card');
    c.chip('＝ 不越界', 924, 760, { kind: 'o', size: 30, h: 56, at: tZ + 0.7 });
    c.cue(tZ + 0.7, 'item');
    // S04-46 官网 FAQ 引语卡（原句一字不改）+ 中文
    const tQ = P('S04-46', '官方自己也说', 0.3) - 0.2, tQz = P('S04-46', '只保证答案的格式', 0.3) - 0.1;
    const qc = c.card(1100, 684, 760, 200);
    tx(c, qc, 30, 18, '“Jev guarantees the shape of its answers, not that every decision is correct.”', '700 23px var(--cjk)', { w: 700, wrap: true, lh: 32 });
    const qz = tx(c, qc, 30, 94, '只保证答案的格式，不保证每个判断都对', '900 30px var(--cjk)', { lh: 42 });
    tx(c, qc, 30, 148, '— TypeSafe 官网 FAQ（2026-09-28 查询）', '500 18px var(--cjk)', { color: 'var(--grey)', lh: 26 });
    c.show(qc, tQ, null, 12); c.cue(tQ, 'card');
    c.show(qz, tQz, null, 6); c.cue(tQz, 'item');
    // S04-47 第 3 行加一句「理由：LLM 能写出来 ｜ Jev 没有」
    const tWhy = P('S04-47', '不给理由', 0.5) - 0.2;
    const why = c.div('', 0, r3 + 104, TW, 44, '', tb);
    c.div('dash', C1 - 8, 0, TW - C1 - 28, null, '', why);
    tx(c, why, C0 + 52, 8, '理由', '800 25px var(--cjk)', { lh: 36 });
    tx(c, why, C1, 8, '能写出来', '800 25px var(--cjk)', { lh: 36 });
    tx(c, why, C2, 8, '没有<span style="font:500 18px var(--cjk);color:var(--grey);margin-left:16px">Simon Willison：比 LLM 更像黑箱</span>', '800 25px var(--cjk)', { lh: 36 });
    c.show(why, tWhy, null, 6); c.cue(tWhy, 'item');
  });

  // ================================================================== S05 三、能取代大模型吗
  ENG.scene('S05', c => {
    chapterTitle(c, SG('S05-48'));
    const t49 = T('S05-49'), t50 = T('S05-50'), t51 = T('S05-51'), t55 = T('S05-55'), t56 = T('S05-56'), t58 = T('S05-58'), t59 = T('S05-59');
    const t60 = T('S05-60'), t62 = T('S05-62'), t64 = T('S05-64'), t66 = T('S05-66');

    // ---- (a) S05-49 大字「不能」→ 缩小；标题「适合：高频 · 简单 · 标准明确」
    const tNo = t49 + 0.05, tHi = P('S05-49', '高频', 0.35) - 0.05;
    scrim(c, 1150, 450, 1040, 420, tNo - 0.1, tHi + 0.3, 0.6);
    const no = tx(c, null, 0, 336, '不能', '900 190px var(--cjk)', { lh: 230, color: FG });
    no.style.left = Math.round(1150 - no.offsetWidth / 2) + 'px';
    c.T(no, { o: 0, y: 16 }).in(tNo, 0.35).to(tHi, { o: 0, s: 0.4 }, 0.45, E.inOut);
    c.cue(tNo, 'word');
    heading(c, '适合：<span class="or">高频</span> · <span class="or">简单</span> · <span class="or">标准明确</span>', tHi + 0.1, OUT('S05-55'));

    // ---- (b) S05-50–54 适合 / 不适合 两栏 + 箭头；语言小卡
    const ok = c.card(470, 272, 460, 400);
    tx(c, ok, 32, 26, `${checkSvg('#FF4F1A', 5, 34, 12)}适合`, '900 40px var(--cjk)', { lh: 56 });
    const okI = [['工单分类', P('S05-50', '工单分类', 0.2)], ['内容审核', P('S05-50', '审核内容', 0.4)], ['检索相关性', P('S05-50', '资料相不相关', 0.8) - 0.3]];
    okI.forEach(([t, at], i) => { const e = opt(c, ok, t, 32, 104 + i * 76, { h: 60, size: 30 }); e.style.padding = '0 26px'; c.show(e, at, null, 8); c.cue(at, 'item'); });
    c.show(tx(c, ok, 32, 344, '官方文档：用例地图', '500 19px var(--cjk)', { color: 'var(--grey)', lh: 28 }), okI[2][1] + 0.5, null, 6);
    c.show(ok, t50 + 0.05, OUT('S05-55'), 14); c.cue(t50 + 0.05, 'card');
    const ng = c.card(970, 272, 870, 400);
    tx(c, ng, 32, 26, `<svg width="34" height="34" viewBox="0 0 48 48" style="vertical-align:-5px;margin-right:12px">${ICON.x('#3A3833')}</svg>不适合`, '900 40px var(--cjk)', { lh: 56 });
    let ax = 32;
    [['写文章', P('S05-51', '写文章', 0.1)], ['聊天', P('S05-51', '聊天', 0.3)], ['写代码', P('S05-51', '写代码', 0.5)]].forEach(([t, at]) => {
      const e = opt(c, ng, t, ax, 104, { h: 52, size: 26 }); ax += e.offsetWidth + 14; c.show(e, at, null, 6); c.cue(at, 'item');
    });
    c.show(tx(c, ng, ax + 8, 114, '它都不做', '700 24px var(--cjk)', { color: 'var(--grey)', lh: 32 }), P('S05-51', '它都不做', 0.8), null, 6);
    const rbB = P('S05-52', '交给代码', 0.8) - 0.1;
    arrowRow(c, ng, 32, 190, '算数、比日期', '交给代码', P('S05-52', '算数', 0.05), rbB);
    c.show(tx(c, ng, 32, 250, '官方文档：Jev 1.13 已知短板', '500 18px var(--cjk)', { color: 'var(--grey)', lh: 26 }), rbB + 0.4, null, 6);
    arrowRow(c, ng, 32, 300, '多步推理', '拆成小题', P('S05-53', '推理好几步', 0.3) - 0.1, P('S05-53', '拆成几道小题', 0.4), '（太难就交给推理模型）');
    c.show(ng, t51 + 0.05, OUT('S05-55'), 14); c.cue(t51 + 0.05, 'card');
    const tLg = P('S05-54', '中文也能用', 0.1);
    const lgc = paper(c, 970, 694, 870, 120, { kicker: 'LANGUAGE · 语言' });
    tx(c, lgc, 36, 50, '语言：英语最好 · 中文能用、效果较差', '800 30px var(--cjk)', { lh: 44 });
    tx(c, lgc, 870 - 36 - 300, 18, '官方文档 Models 页', '500 18px var(--cjk)', { w: 300, align: 'right', color: 'var(--grey)', lh: 26 });
    c.show(lgc, tLg, OUT('S05-55'), 14); c.cue(tLg, 'card');

    // ---- (c) S05-55–59 选项要设计好：《杀戮尖塔》横条（示意）；PriorBench；选项框加「以上都不是」
    heading(c, '选项要<span class="or">设计好</span>', t55 + 0.15, OUT('S05-60'));
    const sp = paper(c, 470, 262, 720, 540, { kicker: 'SLAY THE SPIRE · 选项的概率', shiyi: true });
    tx(c, sp, 36, 48, '卡牌游戏《杀戮尖塔》：三张防御牌和“结束回合”', '800 30px var(--cjk)', { lh: 44 });
    tx(c, sp, 36, 96, '数据来自差评X.PIN 实测（2026-09-27）', '500 18px var(--cjk)', { color: 'var(--grey)', lh: 26 });
    const OPT = [['防御牌 A', 17], ['防御牌 B', 20], ['防御牌 C', 18], ['结束回合', 21]];
    const SX = 200, K = 7.4, RY0 = 150, RP = 58, BH = 38, VX = SX + Math.round(21 * K) + 26;
    const tBars = P('S05-56', '三张防御牌', 0.5) - 0.3;
    const bars = OPT.map(([lab, v], i) => {
      const y = RY0 + i * RP, len = Math.round(v * K);
      const lb = tx(c, sp, 36, y + 1, lab, '700 26px var(--cjk)', { lh: 36 });
      const g = grow(c, sp, SX, y, len, BH, i < 3 ? '#3A3833' : '#9A958C', tBars + 0.12 * i, 0.5);
      const vl = tx(c, sp, VX, y + 1, String(v), '800 26px var(--mono)', { lh: 36 });
      c.show(vl, tBars + 0.12 * i + 0.35, null, 4);
      return { lb, g, vl, y, len };
    });
    c.cue(tBars, 'chart');
    // S05-57：三条防御并到一起成一条虚线框「防御 合计」；每条都比「结束回合」短；选了结束回合
    const tMg = P('S05-57', '拆成三份', 0.5) - 0.2, tLow = P('S05-57', '每份都比', 0.3), tPick = P('S05-57', '选了结束回合', 0.5) - 0.15;
    const MY = RY0 + 4 * RP + 26;
    c.show(c.div('dash', 36, MY - 16, 648, null, '', sp), tMg, null, 0);
    c.show(tx(c, sp, 36, MY + 1, '防御 合计', '800 26px var(--cjk)', { lh: 36 }), tMg + 0.2, null, 4);
    let mx = SX;
    [0, 1, 2].forEach(i => {
      const b = bars[i];
      const cp = c.div('', SX, b.y, b.len, BH, '', sp);
      Object.assign(cp.style, { background: '#3A3833', borderRadius: '4px', boxShadow: 'inset 0 0 0 2px #EDEAE3' });
      c.T(cp, { o: 0, x: 0, y: 0 }).to(tMg + 0.12 * i, { o: 1 }, 0.15).to(tMg + 0.12 * i + 0.2, { x: mx - SX, y: MY - b.y }, 0.6, E.inOut);
      c.T(b.g.wrap, { o: 1 }).to(tMg + 0.9, { o: 0.35 }, 0.3);
      c.T(b.vl, { o: 1 }).to(tMg + 0.9, { o: 0.45 }, 0.3);
      mx += b.len;
    });
    const mbox = c.div('', SX - 6, MY - 6, mx - SX + 12, BH + 12, '', sp);
    Object.assign(mbox.style, { border: '3px dashed var(--orange)', borderRadius: '8px' });
    c.show(mbox, tMg + 1.0, null, 0);
    c.cue(tMg, 'item');
    const eX = SX + bars[3].len;                          // 「结束回合」的长度：一条竖虚线，三条防御都够不着
    const vg = c.svg(eX - 2, RY0 - 10, 4, 3 * RP + BH + 20, `<line x1="2" y1="0" x2="2" y2="${3 * RP + BH + 20}" stroke="#FF4F1A" stroke-width="3" stroke-dasharray="6 5"/>`, sp);
    c.T(vg, { o: 0 }).to(tLow, { o: 1 }, 0.3);
    c.cue(tLow, 'item');
    const eb = bars[3];
    c.T(null, { w: 0 }, p => { const on = p.w > 0.5; eb.g.bar.style.background = on ? 'var(--orange)' : '#9A958C'; eb.lb.style.color = on ? 'var(--orange)' : ''; eb.lb.style.fontWeight = on ? '900' : ''; }).to(tPick, { w: 1 }, 0.1);
    const ck = c.div('', eb.vl.offsetLeft + eb.vl.offsetWidth + 14, eb.y + 1, 36, 36, checkSvg('#EDEAE3', 5, 22, 0));
    sp.appendChild(ck);
    Object.assign(ck.style, { borderRadius: '50%', background: 'var(--orange)', textAlign: 'center', lineHeight: '34px' });
    c.show(ck, tPick + 0.1, null, 4);
    c.show(tx(c, sp, 36, 480, '<span class="or">▍</span>选项怎么列，会影响它的判断', '800 26px var(--cjk)', { lh: 36 }), tPick + 0.8, null, 6);
    c.cue(tPick, 'item');
    c.show(sp, t56 + 0.1, OUT('S05-60'), 14); c.cue(t56 + 0.1, 'card');
    // S05-58 PriorBench 小卡
    const pb = paper(c, 1230, 262, 610, 250, { kicker: 'PRIORBENCH · 独立评测' });
    tx(c, pb, 32, 48, '<span class="mono">30</span> 条哪一类都不属于的消息', '800 27px var(--cjk)', { lh: 40 });
    const pb2 = tx(c, pb, 32, 94, '<span class="or">→</span> 每条都被分进某一类', '800 27px var(--cjk)', { lh: 40 });
    c.chip('置信度 <span class="mono">0.99</span>', 32, 144, { kind: 'o', size: 26, h: 48, parent: pb, at: P('S05-58', '很自信', 0.6) - 0.1 });
    tx(c, pb, 32, 204, 'PriorBench 独立评测（GitHub，2026-09-20）', '500 18px var(--cjk)', { color: 'var(--grey)', lh: 26 });
    c.show(pb, t58 + 0.1, OUT('S05-60'), 14); c.cue(t58 + 0.1, 'card');
    c.show(pb2, P('S05-58', '硬选一个', 0.5) - 0.1, null, 6);
    c.cue(P('S05-58', '很自信', 0.6), 'item');
    // S05-59 选项框：加一项橙色「以上都不是」
    const tNone = P('S05-59', '以上都不是', 0.5) - 0.1;
    const ob = paper(c, 1230, 540, 610, 262, { kicker: 'OPTIONS · 选项（示意）' });
    let oxx = 32;
    ['物流组', '退款组', '技术组'].forEach(t => { const e = opt(c, ob, t, oxx, 56, { h: 52, size: 26 }); oxx += e.offsetWidth + 14; });
    const none = opt(c, ob, '＋ 以上都不是', 32, 124, { h: 52, size: 26, kind: 'on' });
    c.show(none, tNone, null, 8);
    const obs = tx(c, ob, 32, 202, '官方文档 Primitives / Choice 页', '500 18px var(--cjk)', { color: 'var(--grey)', lh: 26 });
    c.show(obs, tNone + 0.4, null, 6);
    c.show(ob, t59 + 0.05, OUT('S05-60'), 14); c.cue(t59 + 0.05, 'card'); c.cue(tNone, 'item');

    // ---- (d) S05-60–61 把握（置信度）要打折听：0.81 vs 53%
    heading(c, '把握（<span class="or">置信度</span>）要打折听', t60 + 0.15, OUT('S05-62'));
    const cf = paper(c, 560, 300, 1180, 340, { kicker: 'CONFIDENCE · 说的把握 vs 实际答对', shiyi: true });
    const CB = 300, CL = 700;
    tx(c, cf, 36, 72, '它说的把握', '800 30px var(--cjk)', { lh: 44 });
    tx(c, cf, 36, 152, '实际答对', '800 30px var(--cjk)', { lh: 44 });
    const tb1 = P('S05-61', '八成把握', 0.4) - 0.15, tb2 = P('S05-61', '实际只对了', 0.3) - 0.05;
    const L1 = Math.round(0.81 * CL), L2 = Math.round(0.53 * CL);
    grow(c, cf, CB, 74, L1, 40, 'var(--orange)', tb1, 0.6);
    grow(c, cf, CB, 154, L2, 40, '#3A3833', tb2, 0.6);
    c.show(tx(c, cf, CB + L1 + 16, 72, '平均 <span class="mono">0.81</span>', '800 30px var(--cjk)', { lh: 44, color: 'var(--orange)' }), tb1 + 0.45, null, 4);
    c.show(tx(c, cf, CB + L2 + 16, 152, '<span class="mono">53%</span>', '800 30px var(--cjk)', { lh: 44 }), tb2 + 0.45, null, 4);
    const cfs = tx(c, cf, 36, 256, '置信度 0.7–0.9 的那一段 · Towards Data Science 作者在 Banking77 上实测', '500 19px var(--cjk)', { color: 'var(--grey)', lh: 28 });
    c.show(cfs, tb2 + 0.8, null, 6);
    c.show(cf, t60 + 0.5, OUT('S05-62'), 14); c.cue(t60 + 0.5, 'card'); c.cue(tb1, 'item'); c.cue(tb2, 'item');

    // ---- (e) S05-62–65 路由流程图：请求 → Jev 判断 → 高置信度：代码 / 专门的模型；低置信度：人 / 大模型；两条时间条
    const tRq = t62 + 0.15, tJd = P('S05-62', '先让Jev判断', 0.3) - 0.15;
    const tHiN = P('S05-63', '直接按结果分流', 0.3) - 0.1, tLoN = P('S05-63', '转给人或大模型', 0.3) - 0.1;
    const f = c.flow({ until: OUT('S05-66'), nodes: [
      { id: 'rq', x: 470, y: 300, w: 200, h: 120, title: '请求', size: 34, at: tRq },
      { id: 'jv', x: 760, y: 280, w: 290, h: 160, title: 'Jev 判断', size: 38, at: tJd },
      { id: 'hi', x: 1250, y: 196, w: 480, h: 116, title: '代码 / 专门的模型', size: 32, at: tHiN },
      { id: 'lo', x: 1250, y: 412, w: 480, h: 116, title: '人 / 大模型', size: 32, at: tLoN },
    ], links: [{ from: 'rq', to: 'jv', at: tJd - 0.1 }] });
    Object.assign(f.nodes.jv.el.style, { borderColor: 'var(--orange)', borderWidth: '3px' });
    const aH = c.arrow(1058, 330, 1242, 262, '#FF4F1A', { w: 4, head: 14 });
    const aL = c.arrow(1058, 392, 1242, 462, LINE, { w: 4, head: 14 });
    c.T(aH, { o: 0 }).to(tHiN - 0.15, { o: 1 }, 0.3).out(OUT('S05-66'));
    c.T(aL, { o: 0 }).to(tLoN - 0.15, { o: 1 }, 0.3).out(OUT('S05-66'));
    c.label('高置信度', 1040, 230, { w: 190, align: 'center', size: 24, kind: 'o', at: tHiN - 0.1, until: OUT('S05-66') });
    c.label('低置信度', 1040, 450, { w: 190, align: 'center', size: 24, at: tLoN - 0.1, until: OUT('S05-66') });
    c.label('官方文档：意图路由、置信度分档 · 示意', 470, 440, { size: 20, kind: 's', at: tJd + 0.5, until: OUT('S05-66') });
    // S05-64 两条时间条（示意）：只用大模型 ｜ Jev + 大模型（两段接起来更长）
    const lt = paper(c, 470, 578, 1370, 280, { kicker: 'LATENCY · 延迟（示意）' });
    const LB = 290, LL = 820, LA = Math.round(LL * 649 / 1087), LJ = LL - LA - 4;
    tx(c, lt, 36, 58, '只用大模型', '800 26px var(--cjk)', { lh: 40 });
    tx(c, lt, 36, 122, '<span class="mono">Jev</span> + 大模型', '800 26px var(--cjk)', { lh: 40 });
    const tA1 = t64 + 0.35, tJ1 = P('S05-64', '先问Jev', 0.4) - 0.1, tL1 = P('S05-64', '再问大模型', 0.5) - 0.1, tSlow = P('S05-64', '更慢更贵', 0.5) - 0.1;
    const segLab = (x, y, w, t, at) => c.show(tx(c, lt, x, y, t, '700 19px var(--cjk)', { w, align: 'center', lh: 38, color: 'var(--paper)' }), at, null, 4);
    grow(c, lt, LB, 60, LA, 38, '#3A3833', tA1, 0.6); segLab(LB, 60, LA, '大模型', tA1 + 0.5);
    grow(c, lt, LB, 124, LJ, 38, 'var(--orange)', tJ1, 0.5); segLab(LB, 124, LJ, 'Jev', tJ1 + 0.4);
    grow(c, lt, LB + LJ + 4, 124, LA, 38, '#3A3833', tL1, 0.6); segLab(LB + LJ + 4, 124, LA, '大模型', tL1 + 0.5);
    c.show(tx(c, lt, LB + LL + 18, 124, '更慢', '800 26px var(--cjk)', { lh: 38, color: 'var(--orange)' }), tSlow, null, 4);
    c.show(tx(c, lt, 36, 200, '有人在检索实验里加了 Jev：总延迟 <span class="mono">649 → 1087</span> 毫秒（据腾讯科技）', '500 20px var(--cjk)', { color: 'var(--grey)', lh: 30 }), tSlow + 0.3, null, 6);
    c.show(lt, t64 + 0.1, OUT('S05-66'), 14); c.cue(t64 + 0.1, 'card'); c.cue(tJ1, 'item'); c.cue(tSlow, 'item');
    // S05-65 一部分请求在「代码 / 专门的模型」这里结束（橙色勾），不再进大模型
    const tCk = P('S05-65', '挡掉一部分请求', 0.4) - 0.1;
    const okc = c.div('', 1694, 172, 56, 56, checkSvg('#EDEAE3', 5, 30, 0));
    Object.assign(okc.style, { borderRadius: '50%', background: 'var(--orange)', textAlign: 'center', lineHeight: '54px', boxShadow: '0 6px 16px rgba(0,0,0,.35)' });
    c.show(okc, tCk, OUT('S05-66'), 0);
    c.label('在这里结束，不再进大模型', 1250, 324, { size: 22, kind: 'o', at: tCk + 0.2, until: OUT('S05-66') });
    c.cue(tCk, 'item');

    // ---- (f) S05-66 分工：大模型 想、写、推理 ｜ Jev 又快又多的小判断
    const tDv = t66 + 0.1, tLm = P('S05-66', '大模型负责', 0.3) - 0.1, tJm = P('S05-66', 'Jev负责', 0.3) - 0.1, tFg = tDv + 0.25;
    const dv = c.card(520, 300, 1260, 330);
    c.svg(628, 40, 4, 250, '<line x1="2" y1="0" x2="2" y2="250" stroke="#B9B3A8" stroke-width="2" stroke-dasharray="8 7"/>', dv);
    const dl = c.div('', 60, 70, 520, 200, '', dv);
    tx(c, dl, 0, 0, '大模型', '900 58px var(--cjk)', { lh: 76 });
    tx(c, dl, 0, 96, '想、写、推理', '800 36px var(--cjk)', { lh: 50, color: '#4A4741' });
    const dr = c.div('', 740, 70, 480, 200, '', dv);
    tx(c, dr, 0, 0, 'Jev', '800 62px var(--mono)', { lh: 76, color: 'var(--orange)' });
    tx(c, dr, 0, 96, '又快又多的小判断', '800 36px var(--cjk)', { lh: 50, color: '#4A4741' });
    const fgc = c.div('', 630 - 70, 125, 140, 80, '分工', dv);
    Object.assign(fgc.style, { background: 'var(--orange)', color: 'var(--paper)', font: '900 40px var(--cjk)', lineHeight: '80px', textAlign: 'center', borderRadius: '10px' });
    c.show(dv, tDv, null, 14); c.cue(tDv, 'card');
    c.show(fgc, tFg, null, 6); c.show(dl, tLm, null, 8); c.show(dr, tJm, null, 8);
    c.cue(tLm, 'item'); c.cue(tJm, 'item');
  });

  // ================================================================== S06 四、怎么用上 Jev
  ENG.scene('S06', c => {
    const tM = P('S06-67', '只能通过API', 0.3) - 0.1;
    chapterTitle(c, SG('S06-67'), { morph: tM });
    const t68 = T('S06-68'), t69 = T('S06-69'), t70 = T('S06-70'), t71 = T('S06-71'), t72 = T('S06-72'), t73 = T('S06-73');
    const g = c.gap(SG('S06-73'));
    const tEnd = g ? g.start : c.endTalk();
    // 小字：没开源
    c.show(c.div('dimnote', 470, 146, null, null, '没公开权重、参数量、训练数据 · 也可以通过 OpenRouter、Vercel 等平台调用'), tM + 0.5, null, 6);
    c.cue(tM + 0.5, 'note');
    // 步骤条（三格空）→ 按台词逐步亮起；结尾停顿里收起
    stepper(c, { x: 1604, y: 236, items: [['注册拿 Key', '在控制台创建'], ['写代码调用', '官方工具包'], ['用自己的数据测', '上线前测一遍']],
      at: P('S06-67', '分三步', 0.5) - 0.2, active: [t68, t70, t71], done: [t70, t71], until: tEnd });

    // ---- S06-68 控制台示意界面（不用真实截图）：API Keys 页，Key 打码；S06-69 切到 Playground
    const tPg = P('S06-69', '试用页', 0.3) - 0.2;
    const win = c.browser({ x: 440, y: 196, w: 1120, h: 640, url: 'console.typesafe.ai', at: t68 + 0.1, until: OUT('S06-70') });
    const side = c.div('side', 0, 58, null, null, '', win.el);
    ['API Keys', 'Playground', '用量', '文档'].forEach((m, i) => c.div('menu', 14, 24 + i * 60, null, null, esc(m), side));
    [[t68 + 0.1, tPg, 0], [tPg, t70 + 1, 1]].forEach(([a, b, i]) => {
      const hl = c.div('', 14, 24 + i * 60, 202, 48, '', side);
      Object.assign(hl.style, { background: 'rgba(255,79,26,.16)', borderRadius: '8px', borderLeft: '4px solid var(--orange)' });
      c.T(hl, { o: 0 }).to(a, { o: 1 }, 0.2).to(b, { o: 0 }, 0.2);
    });
    const MX = 230;
    const v1 = win.view(t68 + 0.1, tPg);
    c.div('ui-h', MX + 50, 36, null, null, 'API Keys', v1);
    const cbtn = c.div('btn', MX + 640, 30, null, null, '创建 Key', v1);
    ['名称', 'Key', '创建时间'].forEach((h, i) => c.div('th', [MX + 50, MX + 270, MX + 600][i], 120, null, null, h, v1));
    c.div('', MX + 50, 156, 790, 2, '', v1).style.background = '#CFC9BE';
    const tKey = P('S06-68', '创建API Key', 0.5);
    const krow = c.div('', 0, 0, 1120, 300, '', v1);
    c.div('td', MX + 50, 182, null, null, '测试用', krow);
    c.div('td', MX + 270, 182, null, null, '<span class="mono">••••••••••••</span>', krow);
    c.div('td', MX + 600, 182, null, null, '今天', krow);
    c.T(krow, { o: 0 }).to(tKey + 0.4, { o: 1 }, 0.3);
    c.ringOn(cbtn, tKey - 0.2, tKey + 1.2, 2);
    c.div('ui-t', MX + 50, 470, null, null, '<span class="mono">console.typesafe.ai</span> · API Key：调用它用的密钥（示意，已打码）', v1).style.color = '#6E6A63';
    c.cue(tKey, 'item');
    // Playground：左边 state 输入框，右边题目和返回的概率条（示意，数值虚构）
    const v2 = win.view(tPg, null);
    c.div('ui-h', MX + 50, 30, null, null, 'Playground', v2);
    c.div('btn', MX + 700, 26, null, null, '运行', v2);
    c.div('ui-t', MX + 50, 94, null, null, '<span class="mono">state</span>（材料）', v2);
    const sbox = c.div('', MX + 50, 130, 380, 250, '', v2);
    Object.assign(sbox.style, { border: '2px solid #BDB7AB', borderRadius: '8px', background: '#F6F4EF' });
    const stx = tx(c, sbox, 18, 14, '我前天买的耳机还没发货，<br>明天出差前必须收到，<br>不然就退款！', '600 24px var(--cjk)', { lh: 38, color: 'var(--ink)' });
    c.T(stx, { o: 0 }).to(P('S06-69', '填材料', 0.5) - 0.2, { o: 1 }, 0.3);
    c.div('ui-t', MX + 470, 94, null, null, '题目 → 结果', v2);
    const tQs = P('S06-69', '加几道题', 0.2), tRes = P('S06-69', '就能看结果', 0.3);
    [['<span class="mono">team</span> · 选择题', '物流组', 0.72], ['<span class="mono">urgent</span> · 是非题', '紧急', 0.96]].forEach(([q, a, pv], i) => {
      const qy = 130 + i * 110;
      const qb = c.div('', MX + 470, qy, 400, 96, '', v2);
      Object.assign(qb.style, { border: '2px solid #CFC9BE', borderRadius: '8px', background: '#FBFAF7' });
      tx(c, qb, 16, 8, q, '700 22px var(--cjk)', { lh: 32, color: 'var(--ink)' });
      const bw = 240;
      const bg = c.div('', 16, 52, bw, 26, '', qb); Object.assign(bg.style, { background: '#E4DFD5', borderRadius: '4px' });
      grow(c, qb, 16, 52, Math.round(bw * pv), 26, 'var(--orange)', tRes + 0.15 * i, 0.5);
      c.show(tx(c, qb, 16 + bw + 12, 48, `${a} <span class="mono">${pv.toFixed(2)}</span>`, '800 22px var(--cjk)', { lh: 32, color: 'var(--ink)' }), tRes + 0.15 * i + 0.4, null, 4);
      c.T(qb, { o: 0, y: 8 }).in(tQs + 0.2 * i, 0.3);
    });
    c.div('btn lite', MX + 470, 360, null, null, '＋ 添加题目', v2);
    c.div('ui-t', MX + 50, 470, null, null, 'Playground · 示意，数值虚构', v2).style.color = '#6E6A63';
    c.cue(tPg, 'ui'); c.cue(tQs, 'item'); c.cue(tRes, 'item');

    // ---- S06-70 代码卡（示意·已简化）：pip install typesafe-sdk / client.system_one(state=…, questions=…)；Key 从环境变量读
    const cd = c.code({ x: 440, y: 206, w: 1120, h: 470, title: 'Python 调用', kicker: '也有 JavaScript 工具包', fs: 24, lh: 44, lines: [
      '$ pip install typesafe-sdk',
      '',
      '# Key 放在环境变量 TYPESAFE_API_KEY，不写进代码',
      { t: 'client = …', c: '                # 用官方工具包创建，Key 从环境变量读取' },
      '',
      'result = client.system_one(',
      '    state="我前天买的耳机还没发货……",',
      { t: '    questions=[ … ],', c: '        # 几道题，一起发' },
      ')',
    ] });
    cd.tr.in(t70 + 0.1).out(OUT('S06-71'));
    c.focus(cd, P('S06-70', 'Python', 0.2), [0]);
    c.focus(cd, P('S06-70', '发一份材料', 0.5) - 0.2, [5, 6, 7, 8]);
    c.unfocus(cd, P('S06-70', '再加几道题', 0.8) + 0.4);

    // ---- S06-71 上线前小卡；S06-72 价格卡；S06-73 免费额度小字卡
    const bl = paper(c, 470, 206, 1060, 150, { kicker: 'BEFORE LAUNCH · 上线前' });
    tx(c, bl, 36, 56, '用自己的数据测准确率、定置信度门槛', '800 36px var(--cjk)', { lh: 52 });
    c.chip('尤其是中文', 1060 - 36 - 170, 60, { kind: 'o', size: 26, h: 48, w: 170, center: true, parent: bl, at: P('S06-71', '尤其是中文', 0.3) - 0.1 });
    c.show(bl, t71 + 0.1, null, 14); c.cue(t71 + 0.1, 'card');
    const pr = paper(c, 470, 386, 720, 250, { kicker: 'PRICE · 价格' });
    const p1 = tx(c, pr, 36, 54, '输入<span style="display:inline-block;width:26px"></span><span class="mono">$0.042</span> / 百万 token', '900 42px var(--cjk)', { lh: 60 });
    const p2 = tx(c, pr, 36, 122, '输出<span style="display:inline-block;width:26px"></span><span class="or">免费</span>', '900 42px var(--cjk)', { lh: 60 });
    tx(c, pr, 36, 200, '官方文档 · 2026-09-28 查询', '500 18px var(--cjk)', { color: 'var(--grey)', lh: 26 });
    c.show(pr, t72 + 0.1, null, 14); c.cue(t72 + 0.1, 'card');
    c.show(p1, P('S06-72', '输入每百万', 0.2) - 0.1, null, 6); c.show(p2, P('S06-72', '输出免费', 0.3) - 0.1, null, 6);
    const fc = c.card(470, 666, 900, 84);
    tx(c, fc, 30, 0, '新用户暂不送免费额度（官方说会尽快恢复）<span style="font:500 18px var(--cjk);color:var(--grey);margin-left:16px">官方 X 2026-09-27（美国时间）</span>', '700 24px var(--cjk)', { lh: 82 });
    const tFc = P('S06-73', '新注册的用户', 0.2) - 0.1;
    c.show(fc, tFc, null, 12); c.cue(tFc, 'card');
  });

  // ================================================================== S07 总结
  ENG.scene('S07', c => {
    const s = c.segs();                                   // s[0] S07-74 … s[4] S07-78
    c.summary({
      items: [
        ['<span class="or">Jev</span>：只做判断的系统一模型', '材料 + 问题 → 答案 + 概率'],
        ['和 <span class="or">LLM</span> 比：不写字 · 快、便宜（厂商自测）', '不越界，但会选错'],
        ['取代不了大模型', '高频小判断交给 Jev，想和写交给大模型'],
      ],
      at: [1, 2, 3].map(i => s[i].start + 0.1),
      cardAt: s[0].start + 0.1,
      signAt: s[4].start + 0.2,
      sign: LIGHT ? `<span style="color:#4A4741">原LAI如此 <span class="mono or">#${ENG.pad2(ENG.EP.number)}</span> · 下期见</span>` : undefined,
    });
  });
})();
