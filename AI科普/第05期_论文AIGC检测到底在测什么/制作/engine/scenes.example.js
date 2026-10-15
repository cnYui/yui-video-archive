/* 参考：第 1 期「什么是 API」的 scenes.js（原样保留各场画面，只把通用部分换成 components.js 的同名接口）。
 * 写新一期时不要直接复制这里的坐标和文字；起点用 scenes.template.js，组件说明看 components.js 顶部。
 * 这份文件里写死的内容（问题文字、#01、S02/S06/S07 的场景号等）都只属于第 1 期。
 *
 * 原注释：每个元素的出现时刻都挂在 segments[].start / 台词短语（ph）/ gaps 上。
 * 场内段落用「场 + 场内序号」取（c.seg(i)），短语时刻用 c.P(seg, '短语', 兜底比例) 取，改台本后只要短语还在就能对上。 */
(function () {
  'use strict';
  const { E, el, box, svg, esc, ph, gapAfter, lastGap, Track } = ENG;

  // 第 1 期原来在这里定义的 jsonHTML / codeHTML / ENG.ctx（c.seg / c.P / c.show / c.card / c.ring / c.arrow / c.title /
  // c.code / c.focus …）和 ICON 已经抽到 components.js（ENG.codeHTML、ENG.ctx、ENG.ICON），接口不变。
  const ICON = ENG.ICON;
  // 第 1 期的抬手锚点（只在没有 actions 的旧时间轴里生效）：S05-26 的抬手跟着要点卡出现在「平台靠它确认三件事」
  ENG.REACH_AT['S05-26'] = '平台靠它';

  // ================================================================== S01 开场白
  ENG.scene('S01', c => {
    const s0 = c.seg(0);
    const tA = c.P(s0, '今天', 0.45) - 0.15;
    const scrim = c.div('', 610, 250, 1080, 480, '');
    scrim.style.background = 'radial-gradient(closest-side, rgba(14,16,28,.55), rgba(14,16,28,.32) 55%, rgba(14,16,28,0))';
    c.show(scrim, tA - 0.1, null, 0, 0.5);
    const k = c.div('bigKick', 750, 322, 800, null, '原LAI如此 · #01');
    c.show(k, tA + 0.1, null, 8);
    const big = c.div('', 750, 360, 800, 240, '<span style="font:800 230px var(--mono);letter-spacing:.04em;color:var(--paper)">API</span><span style="display:inline-block;width:34px;height:170px;background:var(--orange);margin-left:26px;vertical-align:-6px"></span>');
    big.style.textAlign = 'center'; big.style.lineHeight = '240px'; big.style.whiteSpace = 'nowrap';
    c.show(big, tA, null, 16, 0.45);
    const sub = c.div('note', 750, 626, 800, null, '什么是 API');
    sub.style.textAlign = 'center'; sub.style.fontSize = '34px'; sub.style.fontWeight = '700';
    c.show(sub, tA + 0.35, null, 8);
  });

  // ================================================================== S02 三个疑问
  ENG.scene('S02', c => {
    const s = [0, 1, 2, 3, 4, 5].map(c.seg);
    // --- fictional phone (S02-02, first half)
    const phone = c.div('', 610, 140, 340, 660);
    Object.assign(phone.style, { background: '#141414', borderRadius: '46px', border: '3px solid rgba(237,234,227,.35)', boxShadow: '0 18px 40px rgba(0,0,0,.45)' });
    const scr = c.div('', 14, 14, 306, 626, '', phone);
    Object.assign(scr.style, { background: 'var(--paper)', borderRadius: '34px', overflow: 'hidden' });
    c.div('ui-h', 26, 40, null, null, 'AI 助手', scr).style.fontSize = '26px';
    c.div('shiyi', 222, 42, null, null, '示意', scr);
    c.div('', 20, 88, 266, 1, '', scr).style.background = '#CFC9BE';
    const banner = c.div('', 20, 106, 266, 58, '', scr);
    Object.assign(banner.style, { border: '3px solid var(--orange)', borderRadius: '14px', background: '#FFF6F0', textAlign: 'center', font: '800 25px var(--cjk)', color: 'var(--ink)', lineHeight: '52px' });
    banner.innerHTML = '<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--orange);margin-right:10px;vertical-align:2px"></span>已接入 DeepSeek';
    const bub = (x, y, w, h, dark) => { const b = c.div('', x, y, w, h, '', scr); Object.assign(b.style, { borderRadius: '14px', background: dark ? '#141414' : '#DAD5CB' }); return b; };
    bub(20, 196, 200, 54); bub(96, 270, 190, 44, true); bub(20, 334, 230, 86); bub(130, 440, 156, 44, true);
    const inp = c.div('', 20, 548, 266, 52, '', scr);
    Object.assign(inp.style, { borderRadius: '26px', border: '2px solid #BDB7AB', background: '#F6F4EF', font: '500 20px var(--cjk)', color: '#9A958C', lineHeight: '48px', paddingLeft: '20px' });
    inp.textContent = '输入问题…';
    const tPh = s[0].start + 0.1;
    const trPhone = c.show(phone, tPh, null, 16, 0.4);
    trPhone.to(s[1].start, { o: 0, s: 0.94 }, 0.4, E.sine);
    c.ring(647, 263, 266, 58, c.P(s[0], '已接入', 0.2), s[1].start - 0.1);
    // --- fictional tool settings (S02-02, second half)
    const win = c.div('win', 1030, 320, 610, 320);
    const wb = c.div('wbar', 0, 0, null, null, '', win);
    [24, 48, 72].forEach(x => c.div('dot', x, 22, null, null, '', wb));
    c.div('ui-t', 104, 16, null, null, '某 AI 工具 · 设置', wb).style.color = '#3A3833';
    c.div('shiyi', 540, 16, null, null, '示意', wb);
    c.div('ui-h', 40, 96, null, null, 'API Key', win).style.fontSize = '28px';
    const f = c.div('field', 40, 150, 530, 60, '<span style="color:#9A958C;font-family:var(--cjk)">请填写 API Key</span>', win);
    f.style.borderColor = 'var(--orange)'; f.style.lineHeight = '56px';
    c.div('ui-t', 40, 236, null, null, '填好后才能使用', win).style.color = '#8A857C';
    const trWin = c.show(win, c.P(s[0], '有些', 0.5), null, 16, 0.4);
    trWin.to(s[1].start, { o: 0, s: 0.94 }, 0.4, E.sine);
    // --- title + question cards
    const tIn = ENG.tocInTime();
    const title = c.div('', 650, 116, 1000, 70, '你可能也想问');
    Object.assign(title.style, { textAlign: 'center', font: '900 54px var(--cjk)', color: 'var(--paper)', letterSpacing: '.06em' });
    c.show(title, s[1].start + 0.25, tIn, 10);
    const tr = c.div('bigRule', 1110, 196, 80, 3);
    c.show(tr, s[1].start + 0.4, tIn, 0);
    const Q = ['API 是什么？', '“已接入”接的是什么？', 'API Key 是什么？怎么拿到？'];
    Q.forEach((q, i) => {
      const y = 236 + i * 162;
      const cd = c.card(650, y, 1000, 132);
      const nb = c.div('', 30, 26, 80, 80, String(i + 1), cd);
      Object.assign(nb.style, { background: 'var(--orange)', color: 'var(--paper)', font: '800 46px var(--mono)', textAlign: 'center', lineHeight: '80px', borderRadius: '6px' });
      const tx = c.div('', 140, 0, 820, 132, esc(q), cd);
      Object.assign(tx.style, { font: '800 46px var(--cjk)', lineHeight: '132px', whiteSpace: 'nowrap' });
      c.div('kicker', 800, 14, 180, null, `QUESTION 0${i + 1}`, cd).style.textAlign = 'right';
      cd.style.transformOrigin = '0 0';
      const r = ENG.tocRowRect(i);
      const trc = c.T(cd, { o: 0, y: 14 });
      trc.in(s[2 + i].start + 0.05, 0.38);
      trc.to(tIn, { x: r.x - 650, y: r.y - y, s: r.w / 1000 }, 0.7, E.inOut).to(tIn + 0.4, { o: 0 }, 0.3, E.sine);
    });
  });

  // ================================================================== S03 一、API 是什么
  ENG.scene('S03', c => {
    const s = [0, 1, 2, 3, 4, 5, 6, 7].map(c.seg);
    const T0 = c.title('一、API 是什么', 'PART 01 · 第一个问题', s[0]);
    // --- A / P / I
    const cols = [690, 1150, 1610];
    const words = [['A', 'pplication', '应用程序'], ['P', 'rogramming', '编程'], ['I', 'nterface', '接口']];
    const wT = [c.P(s[1], 'Application', 0.3), c.P(s[1], 'Programming', 0.55), c.P(s[1], 'Interface', 0.8)];
    const cT = [c.P(s[2], '应用程序', 0.2), c.P(s[2], '编程', 0.45), c.P(s[2], '接口', 0.65)];
    const out1 = s[3].start;
    words.forEach(([ini, rest, cn], i) => {
      const L = c.div('', cols[i] - 150, 176, 300, 170, ini);
      Object.assign(L.style, { textAlign: 'center', font: '800 150px var(--mono)', color: 'var(--orange)', lineHeight: '170px' });
      c.show(L, s[1].start + 0.1 + i * 0.14, out1, 12);
      const cd = c.card(cols[i] - 210, 392, 420, 230);
      const wd = c.div('', 0, 36, 420, 60, `<span style="color:var(--orange);border-bottom:4px solid var(--orange)">${ini}</span>${rest}`, cd);
      Object.assign(wd.style, { textAlign: 'center', font: '700 44px var(--mono)', lineHeight: '60px' });
      c.div('dash', 40, 122, 340, null, '', cd);
      const zh = c.div('', 0, 146, 420, 60, cn, cd);
      Object.assign(zh.style, { textAlign: 'center', font: '800 46px var(--cjk)', lineHeight: '60px' });
      c.show(cd, wT[i], out1, 14);
      c.show(zh, cT[i], null, 8);
    });
    // header chip that keeps the full name after the letters leave
    const chip = c.div('chip dark', T0.right + 28, 86, null, null, 'API ＝ Application Programming Interface · 应用程序编程接口');
    Object.assign(chip.style, { height: '38px', lineHeight: '36px', fontSize: '20px', fontWeight: '500' });
    c.show(chip, out1 + 0.3, null, 6);
    // --- program A / program B
    const node = (x, label) => {
      const n = c.div('node paper', x, 196, 300, 190);
      const ic = c.div('', 0, 26, 300, 60, '&lt;/&gt;', n); Object.assign(ic.style, { font: '800 44px var(--mono)', color: 'var(--orange)', lineHeight: '60px' });
      const tl = c.div('nt', 0, 102, 300, 60, label, n); tl.style.position = 'absolute'; tl.style.fontSize = '38px';
      return n;
    };
    const nA = node(480, '程序 A'), nB = node(1520, '程序 B');
    const tAB = c.P(s[3], '指的是', 0.25);
    c.show(nA, tAB, null, 12); c.show(nB, tAB + 0.15, null, 12);
    const link = c.svg(780, 289, 740, 4, '<line x1="0" y1="2" x2="740" y2="2" stroke="rgba(237,234,227,.55)" stroke-width="3" stroke-dasharray="10 9"/>');
    c.T(link, { o: 0 }).to(tAB + 0.3, { o: 1 }, 0.35).out(s[6].start);
    const rule = c.div('chip', 1020, 267, 260, 48, '');
    rule.innerHTML = `<svg width="26" height="30" viewBox="0 0 36 40" style="vertical-align:-7px;margin-right:10px">${ICON.doc()}</svg>调用规则`;
    Object.assign(rule.style, { textAlign: 'center', fontSize: '26px', lineHeight: '48px', height: '48px', borderTop: '2px solid var(--orange)' });
    c.show(rule, c.P(s[3], '调用规则', 0.55), s[6].start, 8);
    // USB, crossed out
    const usb = c.div('', 1640, 690, 200, 190);
    usb.innerHTML = `<svg width="200" height="130" viewBox="0 0 200 130"><rect x="40" y="30" width="120" height="70" rx="10" fill="none" stroke="#9A958C" stroke-width="5"/><rect x="62" y="50" width="22" height="16" fill="#9A958C"/><rect x="116" y="50" width="22" height="16" fill="#9A958C"/><path d="M28 118 L172 12" stroke="#D8342A" stroke-width="7" stroke-linecap="round"/></svg>`;
    const ul = c.div('lbl s', 0, 138, 200, null, '≠ USB 插口', usb); ul.style.textAlign = 'center'; ul.style.fontSize = '24px';
    c.show(usb, c.P(s[3], 'USB', 0.8), s[4].start, 8);
    // --- rules card → becomes 接口文档
    const rc = c.card(700, 466, 900, 390);
    const rk = c.div('kicker', 36, 22, 400, null, 'RULES · 调用规则', rc);
    const rt = c.div('', 36, 46, 800, 56, '调用规则主要规定：', rc); rt.style.font = '800 40px var(--cjk)';
    const dk = c.div('kicker', 36, 22, 400, null, 'API DOCS · 说明书', rc);
    const dt = c.div('', 36, 46, 800, 56, '<svg width="34" height="40" viewBox="0 0 36 40" style="vertical-align:-6px;margin-right:12px">' + ICON.doc('#FF4F1A') + '</svg>接口文档', rc); dt.style.font = '800 40px var(--cjk)';
    c.div('dash', 36, 112, 828, null, '', rc);
    const items = ['能调用哪些功能', '请求按什么格式发', '结果按什么格式返回'];
    const iT = [c.P(s[5], '能调用', 0.05), c.P(s[5], '请求按', 0.35), c.P(s[5], '结果按', 0.7)];
    items.forEach((it, i) => {
      const r = c.div('item', 40, 140 + i * 76, null, null, `<span class="no o">${i + 1}</span>${it}`, rc);
      c.show(r, iT[i], null, 8);
    });
    const trRc = c.show(rc, s[4].start + 0.1, null, 14);
    const vlink = c.svg(1148, 316, 4, 150, '<line x1="2" y1="0" x2="2" y2="150" stroke="rgba(237,234,227,.55)" stroke-width="3" stroke-dasharray="8 8"/>');
    c.T(vlink, { o: 0 }).to(s[4].start + 0.2, { o: 1 }, 0.3).out(s[6].start);
    // --- one API call: request A→B, result B→A
    const ln1 = c.arrow(800, 250, 1500, 250, '#FF4F1A', { w: 4 });
    const ln2 = c.arrow(1500, 334, 800, 334, 'rgba(237,234,227,.75)', { w: 4 });
    c.T(ln1, { o: 0 }).to(s[6].start + 0.15, { o: 1 }, 0.35);
    c.T(ln2, { o: 0 }).to(s[6].start + 0.3, { o: 1 }, 0.35);
    const req = c.div('token req', 808, 204, null, null, '请求');
    const res = c.div('token res', 1392, 288, null, null, '结果');
    const tq = c.P(s[6], '按规则', 0.12);
    c.T(req, { o: 0, x: 0 }).to(tq, { o: 1 }, 0.25).to(tq + 0.25, { x: 570 }, 1.3, E.inOut).to(tq + 1.6, { o: 0 }, 0.3);
    const busy = c.div('ring', 1514, 190, 312, 202); busy.style.borderRadius = '8px';
    c.T(busy, { o: 0 }).to(tq + 1.5, { o: 1 }, 0.25).to(c.P(s[6], '把结果', 0.45) + 0.1, { o: 0 }, 0.3);
    const tr0 = c.P(s[6], '把结果', 0.45);
    c.T(res, { o: 0, x: 0 }).to(tr0, { o: 1 }, 0.25).to(tr0 + 0.25, { x: -584 }, 1.3, E.inOut).to(tr0 + 1.6, { o: 0 }, 0.3);
    const brk = c.svg(800, 380, 700, 22, '<path d="M2 2 V 12 H 698 V 2" fill="none" stroke="#FF4F1A" stroke-width="3"/>');
    const bl = c.div('lbl', 800, 404, 700, null, '一来一回 ＝ <span class="or">一次 API 调用</span>'); bl.style.textAlign = 'center'; bl.style.fontSize = '30px';
    const tOne = c.P(s[6], '就是一次', 0.8);
    c.show(brk, tOne, null, 0); c.show(bl, tOne + 0.1, null, 8);
    // heading swap: rules → docs
    const tDoc = c.P(s[7], '接口文档', 0.3);
    c.T(rk, { o: 1 }).out(tDoc - 0.1, 0.25); c.T(rt, { o: 1 }).out(tDoc - 0.1, 0.25);
    c.T(dk, { o: 0 }).to(tDoc + 0.15, { o: 1 }, 0.3); c.T(dt, { o: 0, y: 8 }).in(tDoc + 0.15);
    const dev = c.div('chip o', 452, 632, null, null, '开发者照着写');
    c.show(dev, c.P(s[7], '开发者', 0.45), null, 8);
    const da = c.arrow(646, 654, 692, 654, '#FF4F1A', { w: 4, head: 12 });
    c.T(da, { o: 0 }).to(c.P(s[7], '开发者', 0.45) + 0.1, { o: 1 }, 0.3);
    const open = c.div('lbl o', 1520, 400, 300, null, '别人开放出来的功能'); open.style.textAlign = 'center'; open.style.fontSize = '26px';
    c.show(open, c.P(s[7], '就能调用', 0.75), null, 8);
  });

  // ================================================================== S04 二、“已接入”接的是什么
  ENG.scene('S04', c => {
    const s = [0, 1, 2, 3, 4, 5, 6, 7].map(c.seg);
    c.title('二、“已接入”接的是什么', 'PART 02 · 第二个问题', s[0]);
    // --- statement
    const st = c.card(610, 320, 1080, 270);
    c.div('kicker', 44, 26, 400, null, 'MOSTLY · 多数情况下', st);
    const l1 = c.div('', 44, 64, 900, 60, '接的是：', st); l1.style.font = '700 38px var(--cjk)'; l1.style.color = '#4A4741';
    const l2 = c.div('', 44, 130, 1000, 100, 'DeepSeek 大模型的 <span class="or">API</span>', st);
    Object.assign(l2.style, { font: '900 68px var(--cjk)', whiteSpace: 'nowrap' });
    c.show(st, s[1].start + 0.1, s[2].start, 14);
    c.show(l2, c.P(s[1], '接的是', 0.3), null, 8);
    const tOff = s[7].start;  // the flow diagram gives way to the "three apps" picture
    // --- nodes
    const nPh = c.div('node', 470, 200, 250, 250);
    c.svg(99, 26, 52, 82, ICON.phone(), nPh);
    const t1 = c.div('nt', 0, 124, 250, null, '手机 App', nPh); t1.style.position = 'absolute'; t1.style.fontSize = '32px';
    const t2 = c.div('ns', 0, 172, 250, null, '（界面）', nPh); t2.style.position = 'absolute';
    const ans = c.div('chip o', 470, 462, 250, 40, '屏幕上显示回答');
    Object.assign(ans.style, { fontSize: '21px', lineHeight: '40px', height: '40px', textAlign: 'center' });
    const nSv = c.div('node', 1540, 200, 300, 250);
    c.svg(112, 22, 76, 84, ICON.server(), nSv);
    const t3 = c.div('nt', 0, 124, 300, null, '服务器上的大模型', nSv); t3.style.position = 'absolute'; t3.style.fontSize = '30px';
    const t3b = c.div('ns', 0, 172, 300, null, '真正生成回答', nSv); t3b.style.position = 'absolute';
    const nBk = c.div('node', 1010, 245, 250, 160);
    nBk.style.borderStyle = 'dashed';
    const t4 = c.div('nt', 0, 36, 250, null, 'App 后台', nBk); t4.style.position = 'absolute'; t4.style.fontSize = '30px';
    const t5 = c.div('ns', 0, 88, 250, null, '（通常有）', nBk); t5.style.position = 'absolute';
    const tSv = c.P(s[2], '真正生成', 0.45);
    c.show(nPh, s[2].start + 0.1, tOff, 12);
    c.show(nSv, tSv, tOff, 12);
    c.show(nBk, tSv + 0.5, tOff, 12);
    // lanes
    const rq1 = c.arrow(724, 292, 1004, 292, '#FF4F1A'), rq2 = c.arrow(1264, 292, 1534, 292, '#FF4F1A');
    const rt1 = c.arrow(1534, 372, 1264, 372, 'rgba(237,234,227,.8)'), rt2 = c.arrow(1004, 372, 724, 372, 'rgba(237,234,227,.8)');
    [rq1, rq2].forEach(a => c.T(a, { o: 0 }).to(s[3].start + 0.1, { o: 1 }, 0.35).out(tOff));
    [rt1, rt2].forEach(a => c.T(a, { o: 0 }).to(s[4].start + 0.1, { o: 1 }, 0.35).out(tOff));
    // question token
    const q1 = c.div('token req', 736, 269, null, null, '问题'), q2 = c.div('token req', 1280, 269, null, null, '问题');
    const tq = c.P(s[3], 'App把问题', 0.35);
    c.T(q1, { o: 0 }).to(s[3].start + 0.3, { o: 1 }, 0.25).to(tq, { x: 170 }, 0.9, E.inOut).to(tq + 0.8, { o: 0 }, 0.2);
    c.T(q2, { o: 0 }).to(tq + 1.05, { o: 1 }, 0.2).to(tq + 1.15, { x: 150 }, 0.9, E.inOut).to(tq + 2.0, { o: 0 }, 0.25);
    const lq = c.div('lbl o', 1264, 222, 270, null, 'API 请求'); lq.style.textAlign = 'center';
    c.T(lq, { o: 0, y: 8 }).in(tq + 1.05).out(tOff);
    // answer token
    const a1 = c.div('token res', 1430, 349, null, null, '回答'), a2 = c.div('token res', 900, 349, null, null, '回答');
    const ta = s[4].start + 0.35;
    c.T(a1, { o: 0 }).to(ta, { o: 1 }, 0.25).to(ta + 0.25, { x: -150 }, 0.9, E.inOut).to(ta + 1.05, { o: 0 }, 0.2);
    c.T(a2, { o: 0 }).to(ta + 1.3, { o: 1 }, 0.2).to(ta + 1.4, { x: -160 }, 0.9, E.inOut).to(ta + 2.25, { o: 0 }, 0.25);
    const la = c.div('lbl', 1264, 404, 270, null, 'API 返回'); la.style.textAlign = 'center';
    c.T(la, { o: 0, y: 8 }).in(ta + 0.2).out(tOff);
    c.T(ans, { o: 0 }).to(c.P(s[4], '显示在', 0.6), { o: 1 }, 0.3).out(tOff);
    // deployment tags
    const tl = c.div('lbl s', 1540, 468, 300, null, '这台服务器可能是：');
    c.show(tl, s[5].start + 0.1, tOff, 6);
    const tags = ['DeepSeek 官方', '云厂商部署', 'App 厂商自己部署'];
    const tT = [c.P(s[5], 'DeepSeek官方', 0.25), c.P(s[5], '云厂商', 0.6), c.P(s[5], 'App厂商', 0.8)];
    tags.forEach((g, i) => {
      const e = c.div('chip', 1540, 506 + i * 60, 300, 48, g);
      Object.assign(e.style, { textAlign: 'center', lineHeight: '48px', fontSize: '24px' });
      c.show(e, tT[i], tOff, 8);
    });
    // conclusion
    const cc = c.card(470, 520, 1010, 150);
    c.div('kicker', 36, 22, 400, null, 'SO · 所以', cc);
    const ct = c.div('', 36, 58, 960, 60, '已接入 ＝ App 通过 <span class="or">API</span> 调用 DeepSeek 的模型', cc);
    Object.assign(ct.style, { font: '800 40px var(--cjk)', whiteSpace: 'nowrap' });
    c.show(cc, s[6].start + 0.1, tOff, 14);
    // --- three fictional apps → same model
    const tA = tOff + 0.35;
    const model = c.div('node', 1380, 380, 380, 190);
    c.svg(152, 20, 76, 84, ICON.server(), model);
    const mt = c.div('nt', 0, 118, 380, null, 'DeepSeek 模型', model); mt.style.position = 'absolute';
    c.show(model, tA + 0.2, null, 12);
    const shapes = [
      '<circle cx="30" cy="30" r="16" fill="#EDEAE3"/>',
      '<path d="M30 12 L48 46 H12 Z" fill="#EDEAE3"/>',
      '<rect x="14" y="14" width="32" height="32" rx="4" fill="#EDEAE3"/>'];
    const names = ['App 甲', 'App 乙', 'App 丙'];
    const tM = c.P(s[7], '型号', 0.2), tQ = c.P(s[7], '额度', 0.45), tJ = c.P(s[7], '所以同样', 0.65);
    names.forEach((nm, i) => {
      const y = 196 + i * 196;
      const cd = c.card(500, y, 480, 164);
      const ic = c.div('', 26, 26, 60, 60, `<svg width="60" height="60" viewBox="0 0 60 60"><rect width="60" height="60" rx="14" fill="#141414"/>${shapes[i]}</svg>`, cd);
      const n = c.div('', 110, 20, 240, 50, nm, cd); n.style.font = '800 32px var(--cjk)';
      const m1 = c.div('', 110, 72, 300, 36, '型号：<span class="mono">××</span>', cd); m1.style.font = '500 26px var(--cjk)';
      const m2 = c.div('', 110, 112, 300, 36, '额度：<span class="mono">××</span>', cd); m2.style.font = '500 26px var(--cjk)';
      const bd = c.div('', 330, 22, 124, 38, '已接入', cd);
      Object.assign(bd.style, { border: '2px solid var(--orange)', color: 'var(--orange)', borderRadius: '19px', textAlign: 'center', font: '700 20px var(--cjk)', lineHeight: '34px' });
      c.show(cd, tA + i * 0.12, null, 12);
      c.show(m1, tM, null, 6); c.show(m2, tQ, null, 6);
      c.T(bd, { o: 0 }).to(tJ, { o: 1 }, 0.3);
      const ln = c.arrow(984, y + 82, 1372, 475, 'rgba(237,234,227,.55)', { w: 3, dash: '9 8' });
      c.T(ln, { o: 0 }).to(tA + 0.3 + i * 0.12, { o: 1 }, 0.35);
    });
    const cap = c.div('lbl', 470, 812, 1390, null, '同样是“已接入”，用起来<span class="or">也会有差别</span>');
    Object.assign(cap.style, { textAlign: 'center', fontSize: '36px' });
    c.show(cap, c.P(s[7], '用起来', 0.85), null, 8);
  });

  // ================================================================== S05 三、API Key 是什么
  ENG.scene('S05', c => {
    const s = [0, 1, 2, 3, 4, 5, 6].map(c.seg);
    c.title('三、API Key 是什么', 'PART 03 · 第三个问题', s[0]);
    const off1 = s[2].start;
    // --- the key
    const kc = c.card(700, 262, 900, 124);
    c.svg(34, 38, 60, 48, ICON.key(), kc);
    const kt = c.div('', 128, 0, 760, 124, '<span id="skp">sk-</span><span style="color:#8A857C">••••••••••••••••</span>', kc);
    Object.assign(kt.style, { font: '700 56px var(--mono)', lineHeight: '124px', whiteSpace: 'nowrap' });
    c.show(kc, s[1].start + 0.1, off1, 14);
    const mi = c.div('chip o', 560, 302, null, null, '密钥'); mi.style.fontSize = '26px';
    c.show(mi, c.P(s[1], '密钥', 0.3), off1, 6);
    const br = c.svg(828, 398, 644, 22, '<path d="M2 2 V 12 H 642 V 2" fill="none" stroke="rgba(237,234,227,.8)" stroke-width="3"/>');
    const bl = c.div('lbl', 828, 426, 644, null, '一长串字符'); bl.style.textAlign = 'center'; bl.style.fontSize = '28px';
    const tLong = c.P(s[1], '一长串', 0.45);
    c.show(br, tLong, off1, 0); c.show(bl, tLong + 0.1, off1, 6);
    const tSk = c.P(s[1], '以sk开头', 0.85);
    const skl = c.div('', 828, 356, 104, 6, ''); skl.style.background = 'var(--orange)';
    c.T(skl, { o: 0 }).to(tSk, { o: 1 }, 0.25).out(off1);
    const skc = c.div('chip o', 828, 196, null, null, '以 sk 开头'); skc.style.fontSize = '24px';
    c.show(skc, tSk, off1, 6);
    const dsk = c.div('lbl s', 700, 486, 900, null, 'DeepSeek 的 Key（示意，全程打码）'); dsk.style.textAlign = 'center'; dsk.style.fontSize = '24px';
    c.show(dsk, c.P(s[1], '比如', 0.6), off1, 6);
    // --- request carries the key + points
    const rq = c.code({ x: 470, y: 200, w: 640, h: 300, title: '请求', kicker: 'REQUEST', lh: 42, fs: 23,
      lines: ['POST /chat/completions', 'Authorization: Bearer sk-••••', '', '{ "model": "…",', '  "messages": [ … ] }'] });
    rq.tr.in(s[2].start + 0.15);
    const tKey = c.P(s[2], '每次都要', 0.4);
    c.focus(rq, tKey, [1], 0.55);
    const kt2 = c.div('chip o', 912, 302, null, null, '← 带上 Key');
    kt2.style.fontSize = '22px'; kt2.style.height = '38px'; kt2.style.lineHeight = '38px';
    const F2 = [rq.tr];
    F2.push(c.show(kt2, tKey, null, 6));
    const pc = c.card(1170, 200, 670, 330);
    c.div('kicker', 36, 22, 400, null, 'CHECK · 确认', pc);
    const pt = c.div('', 36, 46, 600, 56, '平台用 <span class="or">Key</span> 确认：', pc); pt.style.font = '800 40px var(--cjk)';
    c.div('dash', 36, 110, 598, null, '', pc);
    F2.push(c.show(pc, c.P(s[2], '平台靠它', 0.7), null, 14));
    const pts = [['身份', '是谁在调用'], ['权限', '有没有权限'], ['计费', '费用记在谁的账上']];
    const pT = [c.P(s[3], '是谁', 0.02), c.P(s[3], '有没有权限', 0.4), c.P(s[3], '费用记在', 0.62)];
    pts.forEach(([a, b], i) => {
      const r = c.div('item', 40, 132 + i * 64, null, null, `<span class="no o">${i + 1}</span>${a}<span class="sub">${b}</span>`, pc);
      r.style.fontSize = '36px';
      c.show(r, pT[i], null, 8);
    });
    const ar = c.arrow(1116, 350, 1164, 350, '#FF4F1A', { head: 12 });
    F2.push(c.T(ar, { o: 0 }).to(c.P(s[2], '平台靠它', 0.7) + 0.1, { o: 1 }, 0.3));
    // billing chain
    const nk = c.div('node paper', 470, 590, 340, 170);
    const nk1 = c.div('', 0, 30, 340, 50, 'API Key', nk); nk1.style.font = '800 34px var(--cjk)';
    const nk2 = c.div('', 0, 92, 340, 44, 'sk-••••', nk); nk2.style.font = '700 32px var(--mono)'; nk2.style.color = '#6E6A63';
    const na = c.div('node paper', 900, 590, 300, 170);
    const na1 = c.div('', 0, 30, 300, 50, '账户', na); na1.style.font = '800 34px var(--cjk)';
    const na2 = c.div('', 0, 92, 300, 44, '按用量扣费', na); na2.style.font = '500 26px var(--cjk)'; na2.style.color = '#6E6A63';
    const nb = c.div('node paper', 1290, 590, 550, 170);
    const nb1 = c.div('', 36, 26, 200, 50, '余额', nb); Object.assign(nb1.style, { font: '800 34px var(--cjk)', textAlign: 'left' });
    const nb2 = c.div('', 150, 22, 360, 56, '¥ <span>××</span> <span class="or" style="font-family:var(--cjk)">↓</span>', nb);
    Object.assign(nb2.style, { font: '700 42px var(--mono)', textAlign: 'left' });
    const track = c.div('', 36, 104, 478, 22, '', nb); Object.assign(track.style, { background: '#D9D4CA', borderRadius: '11px' });
    const fill = c.div('', 36, 104, 478, 22, '', nb); Object.assign(fill.style, { background: 'var(--orange)', borderRadius: '11px' });
    const a1 = c.arrow(816, 675, 892, 675, '#FF4F1A', { head: 12 }), a2 = c.arrow(1206, 675, 1282, 675, '#FF4F1A', { head: 12 });
    const tB = s[4].start + 0.1;
    F2.push(c.show(nk, tB, null, 12), c.show(na, tB + 0.35, null, 12), c.show(nb, tB + 0.7, null, 12));
    F2.push(c.T(a1, { o: 0 }).to(tB + 0.3, { o: 1 }, 0.3), c.T(a2, { o: 0 }).to(tB + 0.65, { o: 1 }, 0.3));
    const tD = c.P(s[4], '钱就从', 0.5);
    c.T(fill, { w: 478 }).to(tD + 0.2, { w: 372 }, 0.5).to(tD + 1.1, { w: 262 }, 0.5).to(tD + 2.0, { w: 168 }, 0.5);
    const cap = c.div('lbl s', 470, 782, 1370, null, '大模型 API 一般按用量收费：用得越多，扣得越多'); cap.style.textAlign = 'center'; cap.style.fontSize = '26px';
    F2.push(c.show(cap, c.P(s[4], '按用量', 0.3), null, 6));
    // --- first half fades, then: don'ts + rotate
    const off2 = s[5].start;
    F2.forEach(tr => tr.out(off2 - 0.05));
    const dc = c.card(640, 196, 1040, 390);
    c.div('kicker', 40, 22, 400, null, "DON'T · 保管", dc);
    const dt = c.div('', 40, 48, 980, 56, '像密码一样保管 <span class="or">API Key</span>', dc); dt.style.font = '800 42px var(--cjk)';
    c.div('dash', 40, 116, 960, null, '', dc);
    c.show(dc, off2 + 0.15, null, 14);
    const dn = ['不要发给别人', '不要截图发到群里', '不要写进公开的代码'];
    const dT = [c.P(s[5], '不要发给', 0.4), c.P(s[5], '不要截图', 0.6), c.P(s[5], '也不要写进', 0.85)];
    dn.forEach((d, i) => {
      const r = c.div('item', 44, 142 + i * 76, null, null, `<svg class="x" viewBox="0 0 48 48">${ICON.x()}</svg>${d}`, dc);
      c.show(r, dT[i], null, 8);
    });
    const lk = c.div('lbl', 640, 628, 600, null, '怀疑泄露了？'); lk.style.fontSize = '30px';
    c.show(lk, s[6].start + 0.1, null, 6);
    const old = c.div('node paper', 640, 684, 440, 110);
    const ot = c.div('', 30, 0, 400, 110, '<span class="gy" style="font:700 22px var(--cjk);margin-right:14px">旧</span>sk-••••••••', old);
    Object.assign(ot.style, { font: '700 36px var(--mono)', lineHeight: '110px', textAlign: 'left' });
    const strike = c.div('', 660, 736, 400, 6, ''); strike.style.background = 'var(--red)';
    const del = c.div('lbl', 640, 802, 440, null, '<span class="rd">已删除</span>'); del.style.textAlign = 'center';
    const nw = c.div('node paper', 1240, 684, 440, 110);
    const nt = c.div('', 30, 0, 400, 110, '<span class="or" style="font:700 22px var(--cjk);margin-right:14px">新</span>sk-••••••••', nw);
    Object.assign(nt.style, { font: '700 36px var(--mono)', lineHeight: '110px', textAlign: 'left' });
    const nl = c.div('lbl o', 1240, 802, 440, null, '新建一个'); nl.style.textAlign = 'center';
    const ra = c.arrow(1098, 739, 1226, 739, '#FF4F1A');
    const trOld = c.show(old, s[6].start + 0.1, null, 10);
    const tDel = c.P(s[6], '删掉', 0.5), tNew = c.P(s[6], '再新建', 0.85);
    c.T(strike, { o: 0, w: 0 }).to(tDel, { o: 1, w: 400 }, 0.35);
    c.show(del, tDel + 0.2, null, 6);
    c.T(ra, { o: 0 }).to(tNew - 0.1, { o: 1 }, 0.3);
    c.show(nw, tNew, null, 10); c.show(nl, tNew + 0.2, null, 6);
  });

  // ================================================================== S06 四、主流的三种调用方式
  ENG.scene('S06', c => {
    const s = []; for (let i = 0; i < 22; i++) s.push(c.seg(i));
    c.title('四、主流的三种调用方式', 'PART 04 · 调用方式', s[0]);
    const g = i => c.gap(s[i]) || { start: s[i].end + 0.05, end: s[i + 1] ? s[i + 1].start : s[i].end + 0.4 };
    // --- HTTP + JSON overview
    const off1 = s[2].start;
    const url = c.div('chip dark', 0, 186, null, 44, '<span class="mono" style="font-weight:700">POST</span> <span class="mono">https://api.…/v1/…</span>');
    Object.assign(url.style, { left: '0px', fontWeight: '500', fontSize: '24px' });
    const uw = 420; url.style.left = (1150 - uw / 2) + 'px'; url.style.width = uw + 'px'; url.style.textAlign = 'center';
    const ul = c.div('lbl s', 1150 + uw / 2 + 16, 196, null, null, '← 一个网址');
    c.show(url, s[1].start + 0.1, off1, 8); c.show(ul, s[1].start + 0.3, off1, 6);
    const cl = c.div('node', 470, 300, 240, 290);
    const clt = c.div('nt', 0, 100, 240, null, '你的程序', cl); clt.style.position = 'absolute'; clt.style.fontSize = '32px';
    const cls = c.div('ns', 0, 150, 240, null, '（客户端）', cl); cls.style.position = 'absolute';
    const sv = c.div('node', 1590, 300, 250, 290);
    c.svg(87, 60, 76, 84, ICON.server(), sv);
    const svt = c.div('nt', 0, 170, 250, null, '服务器', sv); svt.style.position = 'absolute'; svt.style.fontSize = '32px';
    c.show(cl, s[1].start + 0.1, off1, 12); c.show(sv, s[1].start + 0.2, off1, 12);
    const la = c.arrow(716, 370, 1584, 370, '#FF4F1A'), lb = c.arrow(1584, 540, 716, 540, 'rgba(237,234,227,.8)');
    const tHttp = c.P(s[1], '发一个HTTP', 0.4);
    c.T(la, { o: 0 }).to(tHttp - 0.3, { o: 1 }, 0.3).out(off1);
    const hl = c.div('lbl o', 716, 262, 868, null, 'HTTP 请求'); hl.style.textAlign = 'center'; hl.style.fontSize = '28px';
    c.show(hl, tHttp, off1, 6);
    const rqc = c.code({ x: 760, y: 300, w: 400, h: 140, title: 'JSON', kicker: ' · 请求', fs: 21, lh: 32, top: 50,
      lines: ['{ "model": "…",', '  "messages": [ … ] }'] });
    rqc.tr.to(tHttp + 0.1, { o: 1, y: 0 }, 0.3).to(tHttp + 0.45, { x: 400 }, 1.1, E.inOut);
    const tRes = c.P(s[1], '请求和结果', 0.7);
    c.T(lb, { o: 0 }).to(tRes - 0.3, { o: 1 }, 0.3).out(off1);
    const rsc = c.code({ x: 1160, y: 470, w: 400, h: 140, title: 'JSON', kicker: ' · 结果', fs: 21, lh: 32, top: 50,
      lines: ['{ "choices": [', '    { "message": { … } } ] }'] });
    rsc.tr.to(tRes, { o: 1, y: 0 }, 0.3).to(tRes + 0.35, { x: -400 }, 1.1, E.inOut);
    rqc.tr.out(off1); rsc.tr.out(off1);
    const jl = c.div('lbl s', 716, 626, 868, null, '请求和结果都用 <span class="or" style="font-weight:700">JSON</span> 格式写'); jl.style.textAlign = 'center'; jl.style.fontSize = '26px';
    c.show(jl, c.P(s[1], 'JSON', 0.9), off1, 6);
    // --- three formats: big cards, then a tab bar
    const F = [['Chat Completions', 'OpenAI', '/chat/completions'], ['Responses', 'OpenAI', '/responses'], ['Claude Messages', 'Anthropic', '/v1/messages']];
    const tTabs = g(2).start;
    F.forEach(([n, v, p], i) => {
      const cd = c.card(480 + i * 460, 330, 420, 250);
      const k = c.div('', 36, 30, 80, 60, String(i + 1), cd); Object.assign(k.style, { font: '800 50px var(--mono)', color: 'var(--orange)' });
      const nm = c.div('', 36, 104, 360, 56, n, cd); nm.style.font = '800 38px var(--cjk)'; nm.style.whiteSpace = 'nowrap';
      const vd = c.div('', 36, 168, 360, 40, v, cd); vd.style.font = '500 26px var(--cjk)'; vd.style.color = '#6E6A63';
      const tr = c.show(cd, s[2].start + 0.25 + i * 0.35, null, 14);
      tr.to(tTabs, { o: 0, y: -40, s: 0.92 }, 0.4, E.sine);
    });
    const tabs = F.map(([n], i) => {
      const tb = c.div('', 440 + i * 372, 168, 356, 50, '');
      Object.assign(tb.style, { background: 'rgba(20,20,20,.8)', border: '1.5px solid rgba(237,234,227,.25)', borderRadius: '8px', overflow: 'hidden' });
      const band = el('div', 'band', tb); Object.assign(band.style, { position: 'absolute', left: 0, top: 0, right: 0, bottom: 0, background: 'var(--orange)', opacity: 0 });
      const tx = c.div('', 0, 0, 356, 50, `<span class="mono" style="font-weight:800;margin-right:12px">${i + 1}</span>${n}`, tb);
      Object.assign(tx.style, { textAlign: 'center', font: '700 23px var(--cjk)', color: 'rgba(237,234,227,.62)', whiteSpace: 'nowrap', lineHeight: '48px' });
      const tr = c.T(tb, { o: 0, y: 8, hl: 0 }, (p, tk) => { const on = p.hl > 0.5; if (tk._on !== on) { tx.style.color = on ? 'var(--paper)' : 'rgba(237,234,227,.62)'; tk._on = on; } });
      tr.in(tTabs + 0.15);
      return tr;
    });
    const sec = [tTabs, g(7).start, g(12).start, g(17).start];  // ① ② ③ then "all three" (stream + table)
    tabs.forEach((tr, i) => { tr.to(sec[i], { hl: 1 }, 0.3); if (sec[i + 1]) tr.to(sec[i + 1], { hl: 0 }, 0.3); tr.to(sec[3], { hl: 0.55 }, 0.3); });
    // --- card ① Chat Completions
    const off3 = g(7).start;
    const c1 = c.code({ x: 440, y: 240, w: 830, h: 590, title: '请求', kicker: 'REQUEST', lines: [
      'POST /v1/chat/completions', 'Authorization: Bearer sk-••••', '', '{', '  "model": "gpt-5.5",', '  "messages": [',
      { t: '    { "role": "system",    "content": "…" },', c: '  // 设定', cLate: true },
      { t: '    { "role": "user",      "content": "…" },', c: '  // 用户', cLate: true },
      { t: '    { "role": "assistant", "content": "…" }', c: '   // 模型的回复', cLate: true },
      '  ]', '}'] });
    c1.tr.in(s[3].start + 0.15).out(off3);
    c.focus(c1, c.P(s[3], '地址结尾', 0.6), [0]);
    c.focus(c1, c.P(s[4], 'model', 0.35), [4]);
    c.focus(c1, c.P(s[4], 'messages', 0.65), [5, 6, 7, 8, 9]);
    const tSys = c.P(s[5], 'system', 0.3), tUsr = c.P(s[5], 'user', 0.5), tAst = c.P(s[5], 'assistant', 0.75);
    c.focus(c1, s[5].start + 0.1, [6, 7, 8]);
    c1.L[6].ctr.to(tSys, { o: 1 }, 0.3); c1.L[7].ctr.to(tUsr, { o: 1 }, 0.3); c1.L[8].ctr.to(tAst, { o: 1 }, 0.3);
    c.focus(c1, tSys, [6]); c.focus(c1, tUsr, [7]); c.focus(c1, tAst, [8]);
    c.unfocus(c1, s[6].start);
    const r1 = c.code({ x: 1300, y: 240, w: 560, h: 590, title: '返回', kicker: 'RESPONSE', lines: [
      '{', '  "choices": [', '    {', '      "message": {', '        "role": "assistant",', '        "content": "……"', '      }', '    }', '  ],',
      { t: '  "usage": { … }', dim: true }, '}', { t: '// 回答在 choices[0].message.content', hide: true }] });
    r1.tr.in(s[6].start + 0.1).out(off3);
    const tCh = c.P(s[6], 'choices', 0.5);
    c.reveal(r1, 11, tCh);
    c.focus(r1, tCh, [1, 3, 5, 11]);
    c.unfocus(r1, s[7].start);
    const cmp = c.div('chip', 440, 846, null, 44, '用得最广 · 兼容：<b>DeepSeek</b> 等很多国产模型');
    Object.assign(cmp.style, { fontWeight: '500' });
    c.show(cmp, c.P(s[7], 'DeepSeek', 0.5), off3, 6);
    // --- card ② Responses
    const off4 = g(12).start;
    const c2 = c.code({ x: 440, y: 240, w: 660, h: 380, title: '请求', kicker: 'REQUEST', lines: [
      'POST /v1/responses', 'Authorization: Bearer sk-••••', '', '{', '  "model": "gpt-5.5",',
      { t: '  "instructions": "…",', c: '   // 设定', cLate: true }, { t: '  "input": "…"', c: '          // 用户输入', cLate: true }, '}'] });
    c2.tr.in(s[8].start + 0.15).out(s[12].start);
    c.focus(c2, c.P(s[8], '/responses', 0.6), [0]);
    c.unfocus(c2, s[9].start + 0.3);
    const badge = c.div('', 1566, 170, 294, 64, '官方：新项目推荐 <b class="or">Responses</b><br>Chat Completions 继续支持');
    Object.assign(badge.style, { font: '500 19px var(--cjk)', lineHeight: '28px', color: 'var(--ink)', background: 'var(--paper)', borderLeft: '4px solid var(--orange)', padding: '4px 12px', borderRadius: '3px', boxShadow: '0 6px 16px rgba(0,0,0,.3)', whiteSpace: 'nowrap' });
    c.show(badge, c.P(s[9], '官方推荐', 0.6), off4, 6);
    const tIn = c.P(s[10], 'input', 0.2), tIns = c.P(s[10], '设定写在', 0.6);
    c.focus(c2, tIn, [6]); c2.L[6].ctr.to(tIn, { o: 1 }, 0.3);
    c.focus(c2, tIns, [5, 6]); c2.L[5].ctr.to(tIns, { o: 1 }, 0.3);
    c.unfocus(c2, s[11].start);
    const map = c.card(440, 650, 660, 180);
    c.div('kicker', 30, 20, 500, null, 'VS ① · 对照 Chat Completions', map);
    const mr1 = c.div('', 30, 56, 620, 50, '<span class="mono gy" style="text-decoration:line-through">"messages"</span>  <span class="or">→</span>  <span class="mono">"input"</span>', map);
    const mr2 = c.div('', 30, 110, 620, 50, '<span class="gy">system 消息</span>  <span class="or">→</span>  <span class="mono">"instructions"</span>', map);
    [mr1, mr2].forEach(e => { e.style.font = '700 28px var(--cjk)'; e.style.whiteSpace = 'pre'; });
    c.show(map, tIn + 0.1, s[12].start, 12);
    c.show(mr1, tIn + 0.2, null, 6); c.show(mr2, tIns + 0.1, null, 6);
    const r2 = c.code({ x: 1140, y: 250, w: 720, h: 580, title: '返回', kicker: 'RESPONSE', lines: [
      '{', '  "id": "resp_…",', '  "output": [', '    {', { t: '      "type": "message",', c: '      // 文字消息', cLate: true },
      '      "content": [ { "text": "…" } ]', '    },', '    {', { t: '      "type": "function_call",', c: ' // 工具调用', cLate: true },
      '      "name": "…"', '    }', '  ]', '}'] });
    r2.tr.in(s[11].start + 0.1).out(s[12].start);
    const tOut = c.P(s[11], '一组条目', 0.3), tTx = c.P(s[11], '除了文字', 0.55), tTool = c.P(s[11], '工具调用', 0.8);
    c.focus(r2, tOut, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
    c.focus(r2, tTx, [3, 4, 5, 6]); r2.L[4].ctr.to(tTx, { o: 1 }, 0.3);
    c.focus(r2, tTool, [7, 8, 9, 10]); r2.L[8].ctr.to(tTool, { o: 1 }, 0.3);
    // previous_response_id
    const tP = s[12].start + 0.35;
    const p1 = c.code({ x: 440, y: 250, w: 700, h: 200, title: '第 1 次请求', kicker: '', fs: 23, lh: 42, top: 60,
      lines: ['{ "input": "问题 1" }', { t: '// 返回 "id": "resp_01"', hide: true }] });
    p1.tr.in(tP).out(off4);
    c.reveal(p1, 1, tP + 0.5);
    const tP2 = c.P(s[12], 'previous', 0.1) + 1.0;
    const p2 = c.code({ x: 440, y: 490, w: 700, h: 250, title: '第 2 次请求', kicker: '', fs: 23, lh: 42, top: 60,
      lines: ['{', '  "previous_response_id": "resp_01",', '  "input": "新问题"', '}'] });
    p2.tr.in(tP2).out(off4);
    c.focus(p2, tP2 + 0.4, [1], 0.7);
    const svc = c.card(1270, 300, 570, 380);
    c.div('kicker', 32, 22, 500, null, 'SERVER · 服务器', svc);
    const sh = c.div('', 32, 50, 500, 50, '服务器保存着上一轮', svc); sh.style.font = '800 34px var(--cjk)';
    c.div('dash', 32, 114, 506, null, '', svc);
    const bubble = (y, txt, dark) => { const b = c.div('', dark ? 190 : 32, y, 340, 58, txt, svc); Object.assign(b.style, { borderRadius: '14px', background: dark ? '#141414' : '#DAD5CB', color: dark ? 'var(--paper)' : 'var(--ink)', font: '700 24px var(--cjk)', lineHeight: '58px', paddingLeft: '22px' }); };
    bubble(140, '问题 1', false); bubble(214, '回答 1', true);
    const idl = c.div('', 32, 300, 500, 40, '<span class="mono">id: resp_01</span>', svc); idl.style.font = '600 24px var(--mono)'; idl.style.color = '#6E6A63';
    c.show(svc, tP + 0.3, off4, 12);
    const tLink = c.P(s[12], '接上一轮', 0.45);
    const lk = c.arrow(1148, 600, 1262, 540, '#FF4F1A', { dash: '10 8' });
    c.T(lk, { o: 0 }).to(tLink, { o: 1 }, 0.35).out(off4);
    const lkl = c.div('lbl o', 1176, 604, 90, null, '接上'); lkl.style.fontSize = '28px';
    c.show(lkl, tLink + 0.1, off4, 6);
    const nore = c.div('chip dark', 440, 780, null, 50, '<span style="text-decoration:line-through;color:#9A958C">每次把聊天记录全部重发</span>  <span class="or">不用了</span>');
    nore.style.fontSize = '26px'; nore.style.lineHeight = '48px';
    c.show(nore, c.P(s[12], '不用每次', 0.7), off4, 6);
    // --- card ③ Claude Messages
    const off5 = g(17).start;
    const c3 = c.code({ x: 440, y: 240, w: 680, h: 590, title: '请求', kicker: 'REQUEST', lines: [
      'POST https://api.anthropic.com/v1/messages', 'x-api-key: sk-ant-••••', 'anthropic-version: 2023-06-01', '', '{', '  "model": "claude-opus-5",',
      { t: '  "max_tokens": 1024,', c: '         // 必填', cLate: true }, '  "system": "…",', '  "messages": [', '    { "role": "user", "content": "…" }', '  ]', '}'] });
    c3.tr.in(s[13].start + 0.15).out(off5);
    c.focus(c3, c.P(s[13], '/v1/messages', 0.6), [0]);
    c.unfocus(c3, s[14].start + 0.2);
    const df = c.card(1160, 240, 700, 234);
    c.div('kicker', 30, 20, 500, null, 'DIFF · 对比 OpenAI', df);
    const dft = c.div('', 30, 44, 640, 50, '和 OpenAI 格式的不同', df); dft.style.font = '800 32px var(--cjk)';
    c.show(df, s[14].start + 0.1, off5, 12);
    const DR = [['认证', 'Key 放 <span class="mono">x-api-key</span>，另带版本号'], ['请求', '<span class="mono">max_tokens</span> 必填，<span class="mono">system</span> 单独写'], ['返回', '<span class="mono">content</span> 内容块']];
    const dStart = [s[15].start, s[16].start, s[17].start];
    DR.forEach(([a, b], i) => {
      const r = c.div('', 30, 106 + i * 40, 650, 38, `<span class="mono or" style="font-weight:800;margin-right:10px">${i + 1}</span><b>${a}</b>：${b}`, df);
      r.style.font = '500 23px var(--cjk)'; r.style.whiteSpace = 'nowrap';
      c.T(r, { o: 0 }).to(dStart[i] + 0.05, { o: 1 }, 0.3).to(dStart[i + 1] || off5, { o: 0.45 }, 0.3);
    });
    // ① auth headers
    const d1 = c.code({ x: 1160, y: 500, w: 700, h: 330, title: '请求头对比', kicker: '', fs: 22, lh: 40, top: 58, lines: [
      { t: '// OpenAI 格式', }, 'Authorization: Bearer sk-••••', '', '// Claude Messages', 'x-api-key: sk-ant-••••', 'anthropic-version: 2023-06-01'] });
    d1.tr.in(s[15].start + 0.2).out(s[16].start);
    const tXk = c.P(s[15], 'x-api-key', 0.3), tAv = c.P(s[15], 'anthropic-version', 0.55), tOa = c.P(s[15], 'OpenAI格式', 0.8);
    c.focus(c3, tXk, [1]); c.focus(d1, tXk, [3, 4]);
    c.focus(c3, tAv, [1, 2]); c.focus(d1, tAv, [3, 4, 5]);
    c.focus(d1, tOa, [0, 1]);
    c.unfocus(c3, s[16].start);
    // ② request body
    const d2 = c.code({ x: 1160, y: 500, w: 700, h: 330, title: '请求体对比', kicker: '', fs: 21, lh: 38, top: 58, lines: [
      '// OpenAI 格式：设定放进 messages', '"messages": [ { "role": "system", … }, … ]', '', '// Claude Messages', '"system": "…",', '"messages": [ … ]'] });
    d2.tr.in(s[16].start + 0.2).out(s[17].start);
    const tMt = c.P(s[16], 'max_tokens', 0.3), tSy = c.P(s[16], '设定用', 0.6);
    c.focus(c3, tMt, [6]); c3.L[6].ctr.to(tMt, { o: 1 }, 0.3);
    c.focus(c3, tSy, [7]); c.focus(d2, tSy, [3, 4, 5]);
    c.focus(c3, c.P(s[16], '不放进', 0.85), [7, 8]); c.focus(d2, c.P(s[16], '不放进', 0.85), [0, 1, 4]);
    c.unfocus(c3, s[17].start);
    // ③ response
    const r3 = c.code({ x: 1160, y: 500, w: 700, h: 330, title: '返回', kicker: 'RESPONSE', fs: 21, lh: 32, top: 54, lines: [
      '{', '  "content": [', { t: '    { "type": "text", "text": "…" },', c: '', cLate: true }, '    { "type": "tool_use", "name": "…", … }', '  ],',
      { t: '  "usage": { "input_tokens": …,', dim: true }, { t: '             "output_tokens": … }', dim: true }, '}'] });
    r3.tr.in(s[17].start + 0.2).out(off5);
    c.focus(r3, c.P(s[17], 'content数组', 0.3), [1, 2, 3, 4]);
    c.focus(r3, c.P(s[17], 'text是', 0.6), [2]);
    c.focus(r3, c.P(s[17], 'tool_use', 0.85), [3]);
    // --- stream: three mini cards side by side
    const tSm = off5 + 0.1;
    const M = [['1 Chat Completions', 'POST /v1/chat/completions', '  "messages": [ … ],'], ['2 Responses', 'POST /v1/responses', '  "input": "…",'], ['3 Claude Messages', 'POST /v1/messages', '  "messages": [ … ],']];
    const tSt = c.P(s[18], 'stream', 0.6);
    const off6 = g(20).start;
    M.forEach(([ttl, p, body], i) => {
      const mc = c.code({ x: 440 + i * 480, y: 240, w: 440, h: 256, title: ttl, kicker: '', fs: 21, lh: 36, top: 54,
        lines: [p, '{', body, { t: '  "stream": true', hide: true }, '}'] });
      mc.tr.to(tSm + i * 0.1, { o: 1, y: 0 }, 0.35).out(off6);
      c.reveal(mc, 3, tSt); mc.L[3].tr.to(tSt, { hl: 1 }, 0.3);
    });
    // SSE: server pushes small pieces to the phone
    const tSse = s[19].start;
    const sl = c.div('lbl o', 440, 530, 660, null, 'SSE <span style="color:var(--paper);font-weight:500">· 服务器推送事件</span>'); sl.style.fontSize = '28px';
    c.show(sl, c.P(s[19], 'SSE', 0.2), off6, 6);
    const svn = c.div('node', 450, 600, 190, 220);
    c.svg(57, 36, 76, 84, ICON.server(), svn);
    const svl = c.div('nt', 0, 144, 190, null, '服务器', svn); svl.style.position = 'absolute'; svl.style.fontSize = '28px';
    const ph = c.div('', 850, 580, 250, 290);
    Object.assign(ph.style, { background: '#141414', borderRadius: '30px', border: '3px solid rgba(237,234,227,.35)' });
    const phs = c.div('', 10, 10, 224, 264, '', ph); Object.assign(phs.style, { background: 'var(--paper)', borderRadius: '22px' });
    const bub = c.div('', 12, 24, 200, 220, '', phs);
    Object.assign(bub.style, { background: '#DAD5CB', borderRadius: '14px', padding: '12px 14px', font: '700 23px var(--cjk)', color: 'var(--ink)', lineHeight: '38px', whiteSpace: 'normal' });
    c.show(svn, tSse + 0.1, off6, 10); c.show(ph, tSse + 0.2, off6, 10);
    const lane = c.arrow(646, 700, 850, 700, 'rgba(237,234,227,.55)', { dash: '8 8' });
    c.T(lane, { o: 0 }).to(tSse + 0.3, { o: 1 }, 0.3).out(off6);
    const pieces = ['API ', '是程序', '之间的', '调用规则'];
    const span = Math.max(0.6, (s[19].end - tSse - 1.4) / pieces.length);
    pieces.forEach((pc, i) => {
      const t0 = tSse + 0.6 + i * span;
      const tk = c.div('token res', 646, 677, null, null, esc(pc.trim()));
      Object.assign(tk.style, { height: '36px', lineHeight: '36px', fontSize: '20px', padding: '0 12px' });
      c.T(tk, { o: 0, x: 0 }).to(t0, { o: 1 }, 0.15).to(t0 + 0.05, { x: 120 }, Math.min(0.7, span * 0.8), E.inOut).to(t0 + Math.min(0.7, span * 0.8), { o: 0 }, 0.15);
      const piece = el('span', '', bub, esc(pc));
      c.T(piece, { o: 0 }).to(t0 + Math.min(0.7, span * 0.8), { o: 1 }, 0.2);
    });
    // Claude's event stream
    const ev = c.code({ x: 1140, y: 540, w: 720, h: 340, title: 'Claude 的流式事件', kicker: '', fs: 22, lh: 42, top: 56, lines: [
      { t: 'event: message_start', c: '         // 开始', cLate: true, hide: true },
      { t: 'event: content_block_start', hide: true },
      { t: 'event: content_block_delta ×N', c: '  // 一段段文字', cLate: true, hide: true },
      { t: 'event: content_block_stop', hide: true },
      { t: 'event: message_delta', hide: true },
      { t: 'event: message_stop', c: '          // 结束', cLate: true, hide: true }] });
    ev.tr.in(s[20].start + 0.05).out(off6);
    const evT = [c.P(s[20], 'message_start', 0.3), c.P(s[20], 'content_block_delta', 0.55), c.P(s[20], 'message_stop', 0.85)];
    for (let i = 0; i < 6; i++) c.reveal(ev, i, s[20].start + 0.2 + i * Math.min(0.25, (evT[0] - s[20].start) / 6));
    [[0, evT[0]], [2, evT[1]], [5, evT[2]]].forEach(([i, t]) => { ev.L[i].tr.to(t, { hl: 1 }, 0.3); ev.L[i].ctr.to(t, { o: 1 }, 0.3); });
    // --- comparison table
    const tb = c.card(440, 250, 1420, 520);
    tb.classList.add('tbl');
    c.div('kicker', 36, 22, 500, null, 'COMPARE · 三种格式', tb);
    const tt = c.div('', 36, 46, 700, 50, '三种格式对比', tb); tt.style.font = '800 36px var(--cjk)';
    const tip = c.div('', 1060, 56, 320, 40, '可截图保存', tb); Object.assign(tip.style, { font: '500 22px var(--cjk)', color: '#6E6A63', textAlign: 'right' });
    const colX = [36, 360, 660, 900, 1200];
    const hdrs = ['格式', '地址结尾', 'Key 放在', '输入字段', '回答在哪'];
    const rows = [['Chat Completions', '/chat/completions', 'Authorization', 'messages', 'choices'],
      ['Responses', '/responses', 'Authorization', 'input', 'output'],
      ['Claude Messages', '/v1/messages', 'x-api-key', 'messages + system', 'content']];
    const hr = c.div('tr', 0, 118, null, 40, '', tb);
    hdrs.forEach((h, i) => c.div('c hd', colX[i], 0, null, null, h, hr));
    c.div('', 36, 160, 1348, 3, '', tb).style.background = 'var(--ink)';
    const tT = s[21].start + 0.1;
    c.show(tb, tT, null, 14);
    rows.forEach((r, j) => {
      const row = c.div('tr', 0, 178 + j * 92, null, 80, '', tb);
      r.forEach((v, i) => c.div('c ' + (i === 0 ? 'fm' : 'fv'), colX[i], 18, null, null, esc(v), row));
      if (j < 2) c.div('dash', 36, 84, 1348, null, '', row);
      c.show(row, tT + 0.3 + j * 0.25, null, 8);
    });
    const foot = c.div('', 36, 462, 1348, 40, '三种都可以把 <span class="mono">"stream"</span> 设成 <span class="mono">true</span>，用 SSE 一段段推送结果', tb);
    Object.assign(foot.style, { font: '500 23px var(--cjk)', color: '#6E6A63' });
    c.show(foot, tT + 1.2, null, 6);
  });

  // ================================================================== S07 实操：获取 DeepSeek API Key
  ENG.scene('S07', c => {
    const s = []; for (let i = 0; i < 10; i++) s.push(c.seg(i));
    c.title('实操：获取 DeepSeek API Key', 'PRACTICE · 问题 ③ 后半：怎么拿到', s[0]);
    const g = i => c.gap(s[i]) || { start: s[i].end + 0.05, end: s[i + 1] ? s[i + 1].start : s[i].end + 0.4 };
    // --- stepper (right)
    const ST = [['注册并登录', '开放平台'], ['创建 API key', '起名 → 创建'], ['复制并保存', '只显示一次'], ['实名 + 充值', '余额不足会报错']];
    const TT = ENG._lastTitle;
    const tStep = Math.max(c.P(s[0], '一共四步', 0.7), TT.morph + 0.3);
    const act = [s[1].start, s[3].start, s[4].start, s[6].start];
    const done = [s[3].start, s[4].start, s[6].start, g(7).start];
    ST.forEach(([a, b], i) => {
      const y = 236 + i * 118;
      const st = c.div('step', 1604, y);
      const sc = c.div('sc', 0, 10, null, null, String(i + 1), st);
      const ck = c.svg(7, 17, 32, 28, ICON.check('#FF4F1A', 4.5), st);
      ck.innerHTML = `<path d="M5 14 L 12 21 L 25 6" fill="none" stroke="#FF4F1A" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`;
      ck.style.left = '10px'; ck.style.top = '22px';
      const path = ck.querySelector('path');
      const t1 = c.div('st', 68, 8, null, null, a, st), t2 = c.div('ss', 68, 44, null, null, b, st);
      if (i < 3) { const ln = c.div('', 25, 70, 3, 52, '', st); ln.style.background = 'rgba(237,234,227,.25)'; }
      const tr = c.T(st, { o: 0, y: 10, a: 0, d: 0 }, (p, tk) => {
        const on = p.a > 0.5, dn = p.d > 0.02;
        const key = (on ? 1 : 0) + (dn ? 2 : 0);
        if (tk._k !== key) {
          sc.classList.toggle('fillo', on && !dn);
          sc.style.borderColor = dn ? 'var(--orange)' : '';
          sc.style.color = dn ? 'transparent' : '';
          t1.style.color = on || dn ? 'var(--paper)' : '';
          t2.style.color = on ? 'rgba(237,234,227,.8)' : '';
          tk._k = key;
        }
        const dd = Math.round(p.d * 100) / 100; if (tk._d !== dd) { path.style.strokeDashoffset = 1 - dd; tk._d = dd; }
      });
      tr.in(tStep + i * 0.12).to(act[i], { a: 1 }, 0.2).to(done[i], { a: 0 }, 0.2).to(done[i] + 0.05, { d: 1 }, 0.25);
    });
    // --- fictional browser window (示意)
    const offW = s[8].start;
    const win = c.div('win', 440, 170, 1120, 700);
    const wb = c.div('wbar', 0, 0, null, null, '', win);
    [22, 46, 70].forEach(x => c.div('dot', x, 22, null, null, '', wb));
    const addr = c.div('addr', 110, 11, null, null, `<svg class="lk" viewBox="0 0 14 16">${ICON.lock()}</svg>platform.deepseek.com`, wb);
    c.div('shiyi', 1040, 17, null, null, '示意', wb);
    c.show(win, s[1].start + 0.1, offW, 14);
    const tUrl = c.P(s[1], 'platform', 0.45);
    c.ringOn(addr, tUrl, s[2].start);
    const zoom = c.div('chip o', 560, 250, null, 70, 'platform.deepseek.com');
    Object.assign(zoom.style, { font: '700 40px var(--mono)', lineHeight: '70px', padding: '0 28px' });
    c.show(zoom, tUrl + 0.15, s[1].end, 8);
    const V = (t0, t1) => { const v = c.div('view', null, null, null, null, '', win); v.style.left = '0'; v.style.top = '58px'; c.T(v, { o: 0 }).to(t0, { o: 1 }, 0.3).to(t1, { o: 0 }, 0.25); return v; };
    // V1 login
    const v1 = V(s[1].start + 0.1, s[2].start);
    const lf = c.div('', 330, 110, 460, 440, '', v1);
    Object.assign(lf.style, { background: '#FBFAF7', borderRadius: '12px', border: '1.5px solid #CFC9BE' });
    c.div('ui-h', 40, 36, null, null, '开放平台 · 登录', lf);
    c.div('ui-t', 40, 86, null, null, '没有账号？先注册', lf);
    c.div('field', 40, 140, 380, 56, '<span class="mask" style="width:190px"></span>', lf);
    c.div('field', 40, 216, 380, 56, '<span class="mask" style="width:120px"></span>', lf);
    const lb = c.div('btn', 40, 318, 380, 56, '注册 / 登录', lf); lb.style.textAlign = 'center';
    c.ring(811, 657, 380, 56, c.P(s[1], '注册并登录', 0.9), s[2].start);
    // S07-55 compare cards over a dimmed window
    const dim = c.div('dimmer', 0, 58, null, null, '', win);
    dim.style.background = 'rgba(20,20,20,.5)';
    c.T(dim, { o: 0 }).to(s[2].start + 0.1, { o: 1 }, 0.3).to(g(2).start, { o: 0 }, 0.3);
    const cA = c.card(520, 380, 470, 230), cB = c.card(1030, 380, 470, 230);
    const ca1 = c.div('', 30, 40, 420, 50, 'chat.deepseek.com', cA); ca1.style.font = '700 30px var(--mono)';
    const ca2 = c.div('', 30, 110, 420, 50, '日常聊天用', cA); ca2.style.font = '700 32px var(--cjk)'; ca2.style.color = '#6E6A63';
    const cb1 = c.div('', 30, 40, 420, 50, 'platform.deepseek.com', cB); cb1.style.font = '700 30px var(--mono)';
    const cb2 = c.div('', 30, 110, 420, 50, '开放平台', cB); cb2.style.font = '800 32px var(--cjk)';
    const cb3 = c.div('', 30, 160, 420, 40, '本期用这个', cB); cb3.style.font = '700 24px var(--cjk)'; cb3.style.color = 'var(--orange)';
    cB.style.outline = '4px solid var(--orange)';
    c.svg(166, 164, 30, 28, ICON.check(), cB);
    const neq = c.div('', 984, 469, 52, 52, '≠'); Object.assign(neq.style, { font: '800 38px var(--cjk)', lineHeight: '50px', textAlign: 'center', color: 'var(--paper)', background: 'var(--ink)', borderRadius: '50%', boxShadow: '0 4px 12px rgba(0,0,0,.3)' });
    c.show(cA, s[2].start + 0.15, g(2).start, 12); c.show(cB, c.P(s[2], '不是同一个', 0.5), g(2).start, 12); c.show(neq, c.P(s[2], '不是同一个', 0.5), g(2).start, 0);
    // console: sidebar + views
    const tCon = g(2).start;
    const side = c.div('side', 0, 58, null, null, '', win);
    const MENU = ['概览', 'API keys', '用量信息', '充值', '实名认证', '文档'];
    const mEl = MENU.map((m, i) => c.div('menu', 14, 24 + i * 60, null, null, esc(m), side));
    c.T(side, { o: 0 }).to(tCon, { o: 1 }, 0.3);
    const tKeys = c.P(s[3], 'API keys', 0.35);
    const tRz = c.P(s[6], '实名认证', 0.4), tPay = c.P(s[6], '账户里没余额', 0.6), tDoc = c.P(s[7], '价格可以看', 0.6);
    const menuOn = [[tCon, tKeys, 0], [tKeys, s[6].start + 0.2, 1], [s[6].start + 0.2, tRz, 3], [tRz, tPay, 4], [tPay, tDoc, 3], [tDoc, 1e9, 5]];
    menuOn.forEach(([a, b, i]) => {
      const hlr = c.div('', 14, 24 + i * 60, 202, 48, '', side);
      Object.assign(hlr.style, { background: 'rgba(255,79,26,.16)', borderRadius: '8px', borderLeft: '4px solid var(--orange)' });
      c.T(hlr, { o: 0 }).to(a, { o: 1 }, 0.2).to(b, { o: 0 }, 0.2);
    });
    const MX = 230;  // main area x inside the view
    // V2 overview (masked account info)
    const v2 = V(tCon, tKeys + 0.3);
    c.div('ui-h', MX + 50, 40, null, null, '概览', v2);
    c.div('ui-t', MX + 50, 110, null, null, '账户：<span class="mask" style="width:180px"></span>', v2);
    c.div('ui-t', MX + 50, 160, null, null, '余额：<span class="mask" style="width:120px"></span>', v2);
    const blk = (v, x, y, w, h) => { const b = c.div('', x, y, w, h, '', v); Object.assign(b.style, { background: '#E3DFD6', borderRadius: '10px' }); };
    blk(v2, MX + 50, 230, 380, 170); blk(v2, MX + 460, 230, 380, 170);
    c.ring(454, 312, 202, 48, tKeys, tKeys + 1.2);
    // V3 API keys page
    const tMod = c.P(s[3], '起一个名字', 0.75);
    const v3 = V(tKeys + 0.3, s[6].start + 0.4);
    c.div('ui-h', MX + 50, 40, null, null, 'API keys', v3);
    const cb = c.div('btn', MX + 610, 34, null, null, '创建 API key', v3);
    const TH = ['名称', 'Key', '创建时间', '操作'], THX = [MX + 50, MX + 250, MX + 560, MX + 740];
    TH.forEach((h, i) => c.div('th', THX[i], 126, null, null, h, v3));
    c.div('', MX + 50, 162, 790, 2, '', v3).style.background = '#CFC9BE';
    const empty = c.div('ui-t', MX + 50, 186, null, null, '暂无 API key', v3); empty.style.color = '#9A958C';
    c.T(empty, { o: 1 }).to(s[5].start, { o: 0 }, 0.2);
    const row = c.div('', 0, 0, 1120, 640, '', v3);
    c.div('td', THX[0], 188, null, null, '测试用', row);
    c.div('td', THX[1], 188, null, null, '<span class="mono">sk-••••••••••</span>', row);
    c.div('td', THX[2], 188, null, null, '今天', row);
    c.div('btn danger', THX[3], 178, null, 48, '删除', row).style.lineHeight = '44px';
    c.T(row, { o: 0 }).to(s[5].start + 0.1, { o: 1 }, 0.3);
    c.ring(1280, 262, 184, 52, c.P(s[3], '创建API', 0.5), tMod);
    c.ring(1410, 406, 102, 48, c.P(s[5], '删掉', 0.4), s[6].start);
    // modals
    const md = c.div('dimmer', 0, 58, null, null, '', win);
    c.T(md, { o: 0 }).to(tMod, { o: 1 }, 0.3).to(s[5].start, { o: 0 }, 0.3);
    const m1 = c.div('modal', 330, 180, 560, 320, '', win);
    c.div('ui-h', 36, 30, null, null, '创建 API key', m1);
    c.div('ui-t', 36, 96, null, null, '名称', m1);
    c.div('field', 36, 134, 488, 56, '<span style="font-family:var(--cjk)">测试用</span>', m1);
    c.div('btn lite', 280, 230, null, null, '取消', m1);
    c.div('btn', 400, 230, null, null, '创建', m1);
    c.show(m1, tMod + 0.05, g(3).start, 10);
    c.ring(1171, 581, 98, 52, c.P(s[3], '点创建', 0.9), g(3).start);
    const m2 = c.div('modal', 280, 180, 660, 330, '', win);
    c.div('ui-h', 36, 30, null, null, 'API key 已创建', m2);
    c.div('ui-t', 36, 90, null, null, '请复制并保存到安全的地方', m2);
    c.div('field', 36, 140, 460, 56, 'sk-••••••••••••••••', m2);
    const cpy = c.div('btn', 516, 144, null, null, '复制', m2);
    c.div('btn lite', 36, 238, null, null, '完成', m2);
    c.show(m2, g(3).start + 0.05, s[5].start, 10);
    c.ring(1237, 495, 98, 52, s[4].start + 0.3, c.P(s[4], '只在创建时', 0.5) + 1.5);
    const tipb = c.div('', 280, 528, 660, 56, '只显示一次，先保存', win);
    Object.assign(tipb.style, { background: 'var(--orange)', color: 'var(--paper)', font: '800 28px var(--cjk)', textAlign: 'center', lineHeight: '56px', borderRadius: '10px', boxShadow: '0 10px 24px rgba(0,0,0,.3)' });
    c.T(tipb, { o: 0 }).to(c.P(s[4], '只在创建时', 0.5), { o: 1 }, 0.3).to(s[5].start, { o: 0 }, 0.3);
    // V4 实名认证
    const v4 = V(tRz, tPay);
    c.div('ui-h', MX + 50, 40, null, null, '实名认证', v4);
    c.div('ui-t', MX + 50, 96, null, null, '充值前，请先按页面提示完成实名认证', v4);
    c.div('ui-t', MX + 50, 170, null, null, '姓名', v4);
    c.div('field', MX + 200, 158, 460, 56, '<span class="mask" style="width:110px"></span>', v4);
    c.div('ui-t', MX + 50, 262, null, null, '证件号', v4);
    c.div('field', MX + 200, 250, 460, 56, '<span class="mask" style="width:330px"></span>', v4);
    c.div('btn', MX + 200, 350, null, null, '提交认证', v4);
    // V5 充值
    const v5 = V(tPay, tDoc);
    c.div('ui-h', MX + 50, 40, null, null, '充值', v5);
    c.div('ui-t', MX + 50, 136, null, null, '金额', v5);
    c.div('field', MX + 200, 124, 360, 56, '¥ ××', v5);
    c.div('ui-t', MX + 50, 228, null, null, '支付方式', v5);
    c.div('field', MX + 200, 216, 360, 56, '<span class="mask" style="width:160px"></span>', v5);
    c.div('btn', MX + 200, 316, null, null, '去充值', v5);
    const few = c.div('chip o', MX + 590, 124 + 58 + 6, null, 50, '自己测试：少充一点就够');
    few.style.fontSize = '24px'; few.style.lineHeight = '50px';
    v5.appendChild(few);
    c.show(few, c.P(s[7], '少充', 0.2), null, 6);
    const err = c.div('', 1080, 690, 440, 150, '');
    Object.assign(err.style, { background: 'rgba(20,20,20,.94)', border: '3px solid var(--red)', borderRadius: '10px', boxShadow: '0 12px 30px rgba(0,0,0,.4)' });
    const e1 = c.div('', 26, 22, 400, 44, '账户余额不足', err); e1.style.font = '800 32px var(--cjk)';
    const e2 = c.div('', 26, 80, 400, 44, '→ 调用报错 <span style="color:var(--red)">402</span>', err); e2.style.font = '700 30px var(--cjk)';
    c.show(err, c.P(s[6], '调用就会报错', 0.7), tDoc, 10);
    // V6 docs: models & prices (no real numbers)
    const v6 = V(tDoc, offW);
    c.div('ui-h', MX + 50, 40, null, null, '文档 · 模型 & 价格', v6);
    c.div('ui-t', MX + 50, 96, null, null, '价格以官网价格页为准（示意，不列数字）', v6);
    const PH = ['模型', '输入价格', '输出价格'], PX = [MX + 50, MX + 400, MX + 620];
    PH.forEach((h, i) => c.div('th', PX[i], 160, null, null, h, v6));
    c.div('', MX + 50, 196, 790, 2, '', v6).style.background = '#CFC9BE';
    [['deepseek-flash', '××', '××'], ['其他模型', '××', '××']].forEach((r, j) => r.forEach((v, i) => c.div('td', PX[i], 218 + j * 60, null, null, i === 0 && j === 0 ? `<span class="mono">${v}</span>` : v, v6)));
    // --- settings card (fictional tool)
    const tSet = s[8].start + 0.3;
    const sw = c.div('win', 440, 190, 1120, 650);
    const swb = c.div('wbar', 0, 0, null, null, '', sw);
    [22, 46, 70].forEach(x => c.div('dot', x, 22, null, null, '', swb));
    c.div('ui-t', 104, 16, null, null, '某 AI 工具 · 模型设置', swb).style.color = '#3A3833';
    c.div('shiyi', 1040, 17, null, null, '示意', swb);
    c.show(sw, tSet, null, 14);
    const LBX = 50, VX = 250;
    const rowL = (y, t) => { const l = c.div('ui-t', LBX, y + 14, null, null, t, sw); l.style.font = '700 26px var(--cjk)'; l.style.color = 'var(--ink)'; return l; };
    rowL(96, '服务商'); c.div('field', VX, 96, 820, 58, '<span style="font-family:var(--cjk)">DeepSeek</span>', sw);
    rowL(180, 'API Key'); c.div('field', VX, 180, 820, 58, 'sk-••••••••••••••••', sw);
    const lUrl = rowL(264, '接口地址'), lMod = rowL(430, '模型名');
    const ph0 = c.div('field', VX, 264, 820, 58, '<span style="color:#9A958C">https://…</span>', sw);
    const u1 = c.div('field', VX, 264, 820, 58, '<span class="kt">OpenAI 格式</span>https://api.deepseek.com', sw);
    const u2 = c.div('field', VX, 340, 820, 58, '<span class="kt">Anthropic 格式</span>https://api.deepseek.com/anthropic', sw);
    [u1, u2].forEach(u => { u.querySelector('.kt').setAttribute('style', 'display:inline-block;font:700 18px var(--cjk);background:#141414;color:#EDEAE3;border-radius:5px;padding:0 10px;line-height:30px;margin-right:18px;vertical-align:3px'); u.style.borderColor = 'var(--orange)'; });
    const mf = c.div('field', VX, 430, 820, 58, 'deepseek-flash', sw);
    const note = c.div('', 50, 540, 1020, 60, '截至 2026 年 9 月，以官方文档为准');
    note.style.font = '500 22px var(--cjk)'; note.style.color = '#6E6A63'; note.style.textAlign = 'right';
    sw.appendChild(note);
    const tFill = c.P(s[8], '填上它', 0.3), tMore = c.P(s[8], '接口地址', 0.7);
    c.ring(690, 370, 820, 58, tFill, tMore);
    const tU1 = c.P(s[9], 'OpenAI格式', 0.35), tU2 = Math.max(tU1 + 0.5, c.P(s[9], 'Anthropic', 0.5) + 0.3);
    [lUrl, lMod, mf].forEach(e => c.show(e, tMore, null, 6));
    c.T(ph0, { o: 0 }).to(tMore, { o: 1 }, 0.3).to(tU1, { o: 0 }, 0.2);
    c.show(u1, tU1, null, 6); c.show(u2, tU2, null, 6);
    c.show(note, tSet + 0.8, null, 6);
    c.ring(690, 454, 820, 58, tMore, s[9].start);
    c.ring(690, 620, 820, 58, tMore + 0.2, s[9].start);
  });

  // ================================================================== S08 总结
  ENG.scene('S08', c => {
    const s = [0, 1, 2, 3, 4, 5].map(c.seg);
    const cd = c.card(540, 180, 1220, 672);
    c.div('kicker', 44, 26, 600, null, 'SUMMARY · 原LAI如此 #01', cd);
    const tt = c.div('', 44, 50, 600, 66, '本期总结', cd); tt.style.font = '900 50px var(--cjk)';
    const dbl = c.div('', 44, 128, 1132, 7, '', cd);
    dbl.style.background = 'linear-gradient(var(--ink),var(--ink)) 0 0/100% 3px no-repeat, linear-gradient(var(--ink),var(--ink)) 0 100%/100% 1.5px no-repeat';
    c.show(cd, s[0].start + 0.1, null, 14);
    const R = [
      ['<span class="or">API</span> ＝ 程序之间的调用规则', '全称 Application Programming Interface，应用程序编程接口'],
      ['“已接入 DeepSeek”', '一般就是 App 通过 API 调用了 DeepSeek 的模型'],
      ['<span class="or">API Key</span> ＝ 调用 API 的密钥', '认身份、算费用，一定要保管好'],
      ['主流调用格式有三种', 'Chat Completions · Responses · Claude Messages']];
    R.forEach(([a, b], i) => {
      const y = 158 + i * 128;
      const r = c.div('', 44, y, 1132, 118, '', cd);
      const no = c.div('', 0, 12, 56, 56, String(i + 1), r);
      Object.assign(no.style, { borderRadius: '50%', background: 'var(--orange)', color: 'var(--paper)', font: '800 30px var(--mono)', textAlign: 'center', lineHeight: '56px' });
      const m = c.div('', 80, 4, 1050, 54, a, r); Object.assign(m.style, { font: '800 36px var(--cjk)', whiteSpace: 'nowrap' });
      const sb = c.div('', 80, 58, 1050, 44, esc(b), r); Object.assign(sb.style, { font: '500 26px var(--cjk)', color: '#5A564F', whiteSpace: 'nowrap' });
      if (i < 3) c.div('dash', 0, 114, 1132, null, '', r);
      c.show(r, s[1 + i].start + 0.1, null, 10);
    });
    const sig = c.div('', 1360, 866, 500, 40, '原LAI如此 <span class="mono or">#01</span> · 下期见');
    Object.assign(sig.style, { font: '700 26px var(--cjk)', textAlign: 'right', color: 'rgba(237,234,227,.85)' });
    c.show(sig, s[5].start + 0.2, null, 6);
  });
})();
