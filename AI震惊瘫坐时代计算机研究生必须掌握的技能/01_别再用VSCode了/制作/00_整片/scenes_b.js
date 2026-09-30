// 画面（白板版）：第一章第 4–6 节（S13–S21）。第 4 节按稿子的要求，全部用代码模拟操作来演示（示意窗口是贴在白板上的印刷卡片）。

// ======================================================================= 第 4 节（上）：Agent loop（S13）
S.sec4a = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), T = pid => tm.p0(pid);
  const t35 = T('P35'), t36 = T('P36'), f36 = flipOf(tm, 'P36');
  // P34–36：loop 环 + 终端 + 验收
  const L1 = page(root, sh, 0, f36.out);
  hTitle(H, L1, '答案是 Agent loop', { x: BX, y: 96, size: 60, at: tm.at('P34', '答案是'), kicker: '一次做完靠不住，怎么办？', sh });
  const CX = SX + 380, CY = 540, R = 190;
  H.ellipse({ x0: CX - R, y0: CY - R, x1: CX + R, y1: CY + R, at: 0.4, dur: 0.8, color: '#B8BDC6', w: 6, padX: 0, padY: 0, parent: L1 });
  H.text({ text: 'loop', x: CX, y: CY, size: 70, align: 'center', color: H.ACCENT, at: 1.0, until: 1.6, parent: L1 });
  const ST = ['需求文档', '写测试', '写代码', '跑测试', '没过就改'];
  const pos = ST.map((t, i) => { const a = -Math.PI / 2 + i * 2 * Math.PI / 5; return [CX + (R + 30) * Math.cos(a), CY + (R + 30) * Math.sin(a)]; });
  ST.forEach((t, i) => {
    const [x, y] = pos[i], al = Math.abs(x - CX) < 40 ? 'center' : x > CX ? 'left' : 'right';
    const at = i === 0 ? 1.2 : bg(tm.at('P35', ['需求文档', '先写测试', '再写代码', '跑测试', '没过就改'][i]), 1.2 + i * 0.3);
    H.text({ text: t, x: x + (al === 'left' ? 20 : al === 'right' ? -20 : 0), y: y + (i === 0 ? -30 : 0), size: 40, align: al, at, until: at + 0.9, parent: L1 });
  });
  const dot = mk(L1, 'abs', { width: 34, height: 34, marginLeft: -17, marginTop: -17, borderRadius: '50%', background: 'var(--orange)', boxShadow: '0 0 0 8px rgba(255,79,26,.2)', zIndex: 8 });
  const tw = win(L1, SX + 740, 230, 762, 470, 'Terminal — 登录接口（模拟）', true); tape(tw.el, 0);
  tw.body.classList.add('term'); tw.body.style.fontSize = '21px';
  const EV = [
    [t35 + 0.2, 'claude "按 docs/PRD.md 实现登录接口，先写测试"', 'cmd', 34, 0],
    [t35 + 2.0, '<span class="ai">●</span> 写测试 tests/test_login.py（3 个用例）', 'out', 0, 1],
    [t35 + 3.2, '<span class="ai">●</span> 运行 pytest -q', 'out', 0, 3],
    [t35 + 4.0, '<span class="err">✗ 3 failed</span>', 'out', 0, 3],
    [t35 + 5.0, '<span class="ai">●</span> 写代码 app/login.py', 'out', 0, 2],
    [t35 + 6.2, '<span class="ai">●</span> 运行 pytest -q', 'out', 0, 3],
    [t35 + 7.0, '<span class="err">✗ 1 failed: test_wrong_password</span>', 'out', 0, 4],
    [t35 + 7.9, '<span class="ai">●</span> 修改 app/login.py', 'out', 0, 2],
    [t35 + 9.1, '<span class="ai">●</span> 运行 pytest -q', 'out', 0, 3],
    [t35 + 9.9, '<span class="ok">✓ 3 passed</span>', 'out', 0, 0],
  ];
  sh(tw.el, t35 - 0.2, { scale: 0.97 });
  sh(srcNote(L1, '来源：Anthropic《Claude Code: Best practices for agentic coding》2025-04：先写测试、确认失败，再写代码，直到测试通过'), tm.at('P35', 'Anthropic'));
  // P36：人最后验收（卡片贴在终端上）
  const card = sh(mk(L1, 'abs wcard', { left: SX + 680, top: 300, width: 800, height: 470, zIndex: 9 }), t36, { scale: 0.96 });
  tape(card, 1);
  const CL = layer(card);                             // 卡片里的手写：这层跟着卡片淡入淡出，左上角挪回画布原点，坐标照旧用画布坐标
  Object.assign(CL.style, { left: -(SX + 680) + 'px', top: '-300px' });
  H.text({ text: '大 loop 套小 loop', x: SX + 720, y: 370, size: 50, at: t36 + 0.1, until: t36 + 1.6, parent: CL });
  H.text({ text: '人不用中途盯着，', x: SX + 720, y: 470, size: 46, at: tm.at('P36', '人不用中途盯着'), until: tm.at('P36', '人不用中途盯着') + 1.5, parent: CL });
  const ys = H.html('最后<span class="or">验收</span>就行', { x: SX + 720, y: 560, size: 46, at: tm.at('P36', '最后验收'), until: tm.at('P36', '最后验收') + 1.2, parent: CL });
  const tB = tm.at('P36', '这样 AI');
  H.line({ x0: SX + 720, y0: 680, x1: SX + 720 + 0.85 * 560, y1: 680, at: tB, dur: 1.2, color: H.ACCENT, w: 30, parent: CL });
  H.line({ x0: SX + 720 + 0.85 * 560 + 20, y0: 680, x1: SX + 720 + 560, y1: 680, at: tB + 1.2, dur: 0.2, color: '#DADDE2', w: 30, parent: CL });
  H.text({ text: '八九成', x: SX + 1310, y: 680, size: 46, color: H.ACCENT, at: tm.at('P36', '八九成'), until: tm.at('P36', '八九成') + 0.8, parent: CL });
  // P37：长任务（功能清单一项一项做）
  const L2 = page(root, sh, f36.in, null);
  const t37 = bg(T('P37'), f36.in);
  hTitle(H, L2, '长任务：跑几小时，甚至几天', { x: BX, y: 96, size: 56, at: t37, kicker: 'Anthropic · 2025.11', sh });
  const fl = mk(L2, 'abs wcard', { left: SX, top: 240, width: 470, height: 520, padding: '24px 28px' }); tape(fl, 2);
  mk(fl, '', { font: "800 26px 'JetBrains Mono','Noto Sans SC'" }, 'feature_list.json');
  const FEAT = ['用户注册', '登录', '发帖', '评论', '搜索', '通知'];
  const fEls = FEAT.map(t => mk(fl, 'feat', {}, `<span class="bx"></span>${t}`));
  const pg = mk(L2, 'abs', { left: SX + 500, top: 240, width: 380, height: 520, background: '#1E1F22', borderRadius: 14, padding: '24px 22px', color: '#D4D4D4', font: "500 21px/1.7 'JetBrains Mono','Noto Sans SC'", overflow: 'hidden', boxShadow: '0 10px 24px rgba(0,0,0,.12)' });
  tape(pg, 0);
  sh(fl, t37 + 0.3, { scale: 0.97 }); sh(pg, t37 + 0.6, { scale: 0.97 });
  const clock = sh(mk(L2, 'abs', { left: SX, top: 790, width: 900, font: "800 32px 'Space Grotesk','Noto Sans SC'" }), tm.at('P37', '这类任务要跑'));
  const STEPS = [['拆成功能清单', '先把需求拆成'], ['每次只做一项', '每次只做一项'], ['浏览器测一遍', '做完用浏览器'], ['写进度文件', '写进度文件'], ['下一轮接着做', '下一轮接着做']];
  STEPS.forEach(([t, ph], i) => hPoint(H, L2, i + 1, t, SX + 950, 290 + i * 110, { size: 44, at: bg(tm.at('P37', ph), t37 + 1.0 + i * 0.3) }));
  const tRounds = tm.at('P37', '先把需求拆成'), roundLen = (T('P37') + PARA.P37.speech - tRounds) / 6.5;
  sh(srcNote(L2, '来源：Anthropic《Effective harnesses for long-running agents》2025-11-26（功能清单、每轮只做一项、浏览器端到端测试、进度文件）'), t37 + 0.5);
  return {
    H,
    update(lv) {
      sh.run(lv);
      termRender(tw.body, EV.map(e => e.slice(0, 4)), lv, 14);
      // 橙点沿着环走到当前这一站（顺时针，0.4 秒）
      let k = -1; EV.forEach((e, i) => { if (lv >= e[0]) k = i; });
      const cur = k < 0 ? 0 : EV[k][4], prev = k < 1 ? 0 : EV[k - 1][4];
      let steps = (cur - prev + 5) % 5; const g = k < 0 ? 1 : easeIO((lv - EV[k][0]) / 0.4);
      const ang = -Math.PI / 2 + (prev + steps * g) * 2 * Math.PI / 5;
      dot.style.left = px(CX + R * Math.cos(ang)); dot.style.top = px(CY + R * Math.sin(ang));
      dot.style.opacity = lv > t35 ? 1 : 0;
      const r = (lv - tRounds) / roundLen;
      fEls.forEach((e, i) => { e.classList.toggle('done', r >= i + 1); e.classList.toggle('now', r >= i && r < i + 1); });
      const logs = []; for (let i = 0; i < 6; i++) if (r >= i + 1) logs.push(`<div>第 ${i + 1} 轮：${FEAT[i]} <span style="color:#4ADE80">✓ 测试通过</span></div>`);
      pg.innerHTML = `<div style="color:#FDBA74;font-weight:800">progress.md</div>` + logs.join('');
      const hrs = clamp((lv - t37) / PARA.P37.speech) * 30;
      clock.innerHTML = `已运行 <span style="color:var(--orange)">${Math.floor(hrs)} 小时 ${pad(Math.floor((hrs % 1) * 60), 2)} 分</span>`;
    },
  };
};

// ======================================================================= 第 4 节：早期卡在前端（S14）
S.sec4b = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), f38 = flipOf(tm, 'P38');
  const L = layer(root);
  hTitle(H, L, '早期卡在前端', { x: BX, y: 96, size: 60, at: 0.2, sh });
  const L0 = page(root, sh, 0, f38.out);
  const a1 = tm.at('P38', '前后端分开'), a2 = tm.at('P38', '写两个 PRD');
  H.node({ x: SX + 150, y: 300, w: 360, h: 170, text: '前端 PRD', size: 54, at: a1, parent: L0 });
  H.node({ x: SX + 990, y: 300, w: 360, h: 170, text: '后端 PRD', size: 54, at: bg(a2, a1 + 1.2), parent: L0 });
  const tj = tm.at('P38', '最后人来联调');
  H.arrow({ x0: SX + 330, y0: 490, x1: SX + 680, y1: 650, at: tj, dur: 0.35, parent: L0 });
  H.arrow({ x0: SX + 1170, y0: 490, x1: SX + 820, y1: 650, at: tj + 0.2, dur: 0.35, parent: L0 });
  H.html('<span class="or">人来联调</span>', { x: BX, y: 720, size: 64, align: 'center', at: tj + 0.5, until: tj + 1.6, parent: L0 });
  // P39：管理后台点不动（模拟）
  const L1 = page(root, sh, f38.in, null);
  const t39 = bg(tm.p0('P39'), f38.in);
  const bw = win(L1, SX, 220, 960, 600, '', false, { url: 'localhost:5173/admin/users' }); tape(bw.el, 0);
  bw.body.innerHTML = `<div class="admin"><div class="nav">管理后台</div><div class="main"><div class="row1"><b>用户列表</b><span class="btn">＋ 新增用户</span></div>
    <table><tr><th>ID</th><th>姓名</th><th>邮箱</th><th>状态</th></tr><tr><td>1</td><td>张三</td><td>zhang@lab.edu</td><td>正常</td></tr>
    <tr><td>2</td><td>李四</td><td>li@lab.edu</td><td>正常</td></tr><tr><td>3</td><td>王五</td><td>wang@lab.edu</td><td>停用</td></tr></table></div></div>`;
  const cur = cursor(L1);
  const tClick = tm.at('P39', '经常点不动');
  H.ellipse({ x0: SX + 780, y0: 290, x1: SX + 930, y1: 330, at: tClick + 0.7, color: H.RED, w: 7, parent: L1 });
  H.text({ text: '点不动！', x: SX + 560, y: 182, size: 56, color: H.RED, at: tClick + 1.0, until: tClick + 1.8, parent: L1 });
  [['浏览器里点、输入', '数据要在浏览器里点'], ['后端查数据库', '后端再去查'], ['边界条件多', '边界条件又多']].forEach(([t, ph], i) => {
    const at = bg(tm.at('P39', ph), t39 + 1.0 + i * 0.5);
    H.dash({ x: SX + 1000, y: 330 + i * 150, len: 30, at, parent: L1 });
    H.text({ text: t, x: SX + 1045, y: 330 + i * 150, size: 44, at: at + 0.1, until: wwin(at + 0.1, t, null, 2.0), maxW: 450, parent: L1 });
  });
  return { H, update(lv) { sh.run(lv); cur.update(lv, [[t39, SX + 400, 700], [tClick - 1.0, SX + 400, 700], [tClick - 0.1, SX + 850, 318, true], [tClick + 1.2, SX + 850, 318, true], [tClick + 2.0, SX + 840, 330]]); } };
};

// ======================================================================= 第 4 节：浏览器控制（S15）
S.sec4c = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), T = pid => tm.p0(pid);
  const tl = hTimeline(H, layer(root), [
    { d: '2024.10', ic: ['claude'], t1: 'computer use', t2: '看屏幕、动鼠标、打字', at: tm.at('P40', 'Anthropic 推出') },
    { d: '2024.11', ic: ['mcp'], t1: 'MCP', t2: '连外部工具的标准接口', at: T('P41') },
    { d: '2025.03', ic: ['playwright'], t1: 'Playwright MCP', t2: '微软 · AI 操作浏览器做测试', at: tm.at('P41', '微软基于它') },
    { d: '2026.03', ic: ['openai'], t1: 'GPT-5.4', t2: 'OSWorld 75%', at: T('P42') },
  ]);
  const f40 = flipOf(tm, 'P40'), f41 = flipOf(tm, 'P41'), f42 = flipOf(tm, 'P42');
  // P40 computer use（模拟）
  const L0 = page(root, sh, 0.4, f40.out);
  const bw = win(L0, SX, 360, 1000, 500, '', false, { url: 'flights.example.com' }); tape(bw.el, 0);
  bw.body.innerHTML = `<div class="fly"><div class="t">查航班</div><div class="inp" id="q"></div><span class="btn">搜索</span><div class="res"></div></div>`;
  const q = bw.body.querySelector('#q'), res = bw.body.querySelector('.res');
  const cur = cursor(L0);
  const tS = tm.at('P40', '模型能看屏幕'), tM = tm.at('P40', '动鼠标'), tK = tm.at('P40', '打字');
  [['看屏幕', tS], ['动鼠标', tM], ['打字', tK]].forEach(([t, at], i) => hPoint(H, L0, i + 1, t, SX + 1080, 460 + i * 120, { size: 50, at }));
  sh(srcNote(L0, '来源：Anthropic《Developing a computer use model》2024-10-22'), 0.8);
  // P41 MCP：AI 连外部工具
  const L1 = page(root, sh, f40.in, f41.out);
  const t41 = bg(T('P41'), f40.in), hx = BX, hy = 600;
  const TOOLS = [['浏览器', SX + 250, 440], ['数据库', SX + 1250, 440], ['GitHub', SX + 250, 780], ['本地文件', SX + 1250, 780]];
  TOOLS.forEach(([t, x, y], i) => {
    H.line({ x0: hx + (x < hx ? -110 : 110), y0: hy + (y < hy ? -40 : 40), x1: x + (x < hx ? 150 : -150), y1: y, at: t41 + 0.6 + i * 0.2, dur: 0.3, color: '#9AA1AC', w: 4, parent: L1 });
    H.node({ x: x - 140, y: y - 60, w: 280, h: 120, text: t, size: 44, at: t41 + 0.8 + i * 0.3, parent: L1 });
  });
  H.ellipse({ x0: hx - 90, y0: hy - 70, x1: hx + 90, y1: hy + 70, at: t41 + 0.2, color: H.INK, w: 8, padX: 0, padY: 0, parent: L1 });
  H.text({ text: 'AI', x: hx, y: hy, size: 80, align: 'center', at: t41 + 0.4, until: t41 + 0.9, parent: L1 });
  const tMcp = bg(tm.at('P41', '一个让 AI'), t41 + 1.5);
  H.html('<span class="or">MCP</span>：统一的接口', { x: hx, y: hy + 150, size: 46, align: 'center', at: tMcp, until: tMcp + 1.6, parent: L1 });
  const tPw = tm.at('P41', 'Playwright MCP');
  H.ellipse({ x0: SX + 110, y0: 380, x1: SX + 390, y1: 500, at: tPw, color: H.HILITE, w: 9, parent: L1 });
  H.text({ text: 'Playwright MCP', x: SX + 250, y: 552, size: 34, align: 'center', color: H.ACCENT, at: tPw + 0.3, until: tPw + 1.3, parent: L1 });
  sh(srcNote(L1, '来源：Anthropic《Introducing the Model Context Protocol》2024-11-25；GitHub microsoft/playwright-mcp（2025-03）'), t41);
  // P42 OSWorld + 速度
  const L2 = page(root, sh, f41.in, f42.out);
  const t42 = bg(T('P42'), f41.in);
  H.text({ text: 'OSWorld：让 AI 操作真实电脑', x: SX, y: 380, size: 44, at: t42, until: t42 + 1.8, parent: L2 });
  const a75 = bg(tm.at('P42', '拿到 75%'), t42 + 1.0), a72 = bg(tm.at('P42', '人类基线'), a75 + 0.8);
  H.text({ text: 'GPT-5.4', x: SX + 220, y: 480, size: 40, align: 'right', at: a75, until: a75 + 0.6, parent: L2 });
  H.line({ x0: SX + 250, y0: 480, x1: SX + 250 + 0.75 * 1000, y1: 480, at: a75 + 0.3, dur: 0.8, color: H.ACCENT, w: 34, parent: L2 });
  H.text({ text: '75.0%', x: SX + 1030, y: 480, size: 42, color: H.ACCENT, at: a75 + 1.0, until: a75 + 1.5, parent: L2 });
  H.text({ text: '人类', x: SX + 220, y: 560, size: 40, align: 'right', at: a72, until: a72 + 0.5, parent: L2 });
  H.line({ x0: SX + 250, y0: 560, x1: SX + 250 + 0.724 * 1000, y1: 560, at: a72 + 0.3, dur: 0.8, color: '#B8BDC6', w: 34, parent: L2 });
  H.text({ text: '72.4%', x: SX + 1000, y: 560, size: 42, at: a72 + 1.0, until: a72 + 1.5, parent: L2 });
  const tSp = tm.at('P42', '速度还差'), tB = tm.at('P42', '最好的智能体');
  H.html('速度还差：多走 <span class="or">2.7–4.3 倍</span>步骤', { x: SX, y: 680, size: 44, at: tSp, until: tSp + 2.2, parent: L2 });
  H.text({ text: '必要', x: SX + 150, y: 760, size: 36, align: 'right', at: tB, until: tB + 0.5, parent: L2 });
  H.line({ x0: SX + 180, y0: 760, x1: SX + 180 + 280, y1: 760, at: tB + 0.2, dur: 0.4, color: '#B8BDC6', w: 26, parent: L2 });
  H.text({ text: '智能体', x: SX + 150, y: 820, size: 36, align: 'right', at: tB + 0.4, until: tB + 1.0, parent: L2 });
  H.line({ x0: SX + 180, y0: 820, x1: SX + 180 + 1100, y1: 820, at: tB + 0.6, dur: 1.0, color: H.ACCENT, w: 26, parent: L2 });
  const tMin = tm.at('P42', '人几分钟');
  H.text({ text: '人几分钟，它几十分钟', x: SX + 1500, y: 760, size: 38, align: 'right', at: tMin, until: tMin + 2.0, parent: L2 });
  sh(srcNote(L2, '来源：OpenAI《Introducing GPT-5.4》2026-03-05（OSWorld-Verified）；arXiv 2506.16042《OSWorld-Human》2025-06'), t42);
  // P43 Meta（可删）
  const L3 = page(root, sh, f42.in, null);
  const t43 = bg(T('P43'), f42.in);
  H.text({ text: '大公司在收集人操作电脑的数据', x: SX, y: 400, size: 50, at: t43, until: t43 + 2.4, parent: L3 });
  const m1 = bg(tm.at('P43', 'Meta 今年 4 月'), t43 + 1.5);
  const mi = sh(mk(L3, 'abs', { left: SX + 1320, top: 350, width: 100, height: 100 }), m1); appIcon(mi, 'meta', 100);
  H.text({ text: 'Meta 2026.04', x: SX, y: 520, size: 46, color: H.ACCENT, at: m1, until: m1 + 1.0, parent: L3 });
  H.text({ text: '记录员工的鼠标、键盘、截图', x: SX + 360, y: 520, size: 46, at: m1 + 1.0, until: m1 + 2.6, parent: L3 });
  const m2 = bg(tm.at('P43', '6 月因为'), m1 + 2.8);
  H.text({ text: '2026.06', x: SX, y: 630, size: 46, color: H.RED, at: m2, until: m2 + 0.6, parent: L3 });
  H.text({ text: '数据在内部泄露，暂停', x: SX + 360, y: 630, size: 46, at: m2 + 0.6, until: m2 + 2.2, parent: L3 });
  sh(bNote(L3, SX + 1260, 760, '（这段可删）'), t43 + 0.5);
  sh(srcNote(L3, '来源：TechCrunch 2026-04-21；Engadget 2026-06'), t43);
  return {
    H,
    update(lv) {
      sh.run(lv); tl.update(lv);
      const bx = SX, by = 360 + 44;
      cur.update(lv, [[0, bx + 700, by + 380], [tM - 0.6, bx + 700, by + 380], [tM + 0.4, bx + 330, by + 152, true], [tK + 1.9, bx + 330, by + 152], [tK + 2.5, bx + 745, by + 152, true], [tK + 4, bx + 760, by + 200]]);
      const Q = '东京 → 上海　10 月 3 日';
      q.innerHTML = esc(Q.slice(0, Math.floor(clamp((lv - tK) / 1.6) * Q.length))) + (lv > tM + 0.4 && lv < tK + 2.2 ? '<span class="caret" style="width:3px;height:30px"></span>' : '');
      res.innerHTML = lv > tK + 2.8 ? ['MU 522　08:05 → 10:35', 'NH 919　09:30 → 12:10', 'CA 930　13:15 → 15:40'].map(r => `<div>${r}</div>`).join('') : '';
    },
  };
};

// ======================================================================= 第 4 节：前端、后端、数据库连起来测（S16，模拟演示）
S.sec4d = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows();
  const L = layer(root);
  hTitle(H, L, '前端、后端、数据库连起来测', { x: BX, y: 96, size: 56, at: 0.2, kicker: '浏览器跑通以后', sh });
  const lg = win(L, SX, 230, 560, 620, 'Agent（模拟）', true); tape(lg.el, 0);
  lg.body.classList.add('term'); lg.body.style.fontSize = '21px';
  const bw = win(L, SX + 620, 230, 882, 390, '', false, { url: 'localhost:5173 · 打卡小程序（本地预览）' }); tape(bw.el, 1);
  bw.body.innerHTML = `<div class="app"><div class="hd">我的打卡</div><div class="list"></div><span class="btn">＋ 新增打卡</span>
    <div class="form"><div class="fl">标题</div><div class="inp"></div><span class="btn ok">提交</span></div></div>`;
  const list = bw.body.querySelector('.list'), form = bw.body.querySelector('.form'), inp = bw.body.querySelector('.inp');
  const db = mk(L, 'abs dbp', { left: SX + 620, top: 650, width: 882, height: 210 });
  const cur = cursor(L);
  sh(lg.el, 0.4); sh(bw.el, 0.6); sh(db, 0.8);
  sh(bNote(L, SX + 1300, 866, '模拟演示'), 1.0);
  const T0 = 0.8, tType = T0 + 5.2, tSub = T0 + 7.4, tDb = T0 + 9.0, tEdge = T0 + 11.0;
  [['前端：本地跑', '前端在本地跑', SX + 1180, 205], ['后端：云函数', '后端是微信云函数', SX + 40, 880], ['数据库：CloudBase', '数据库用腾讯的', SX + 640, 890]].forEach(([t, ph, x, y]) => {
    const at = tm.at('P45', ph);
    H.text({ text: t, x, y, size: 38, color: H.ACCENT, at, until: at + 1.4, parent: L });
  });
  const ROWS0 = [['早起背单词', '09-27'], ['跑步 3km', '09-28']];
  return {
    H,
    update(lv) {
      sh.run(lv);
      termRender(lg.body, [[T0, 'npm run dev', 'cmd', 16], [T0 + 1.0, '<span class="ok">➜</span> localhost:5173'],
        [T0 + 1.6, '<span class="ai">●</span> 打开浏览器（Playwright）'], [T0 + 3.0, '<span class="ai">●</span> 点击「新增打卡」'], [tType, '<span class="ai">●</span> 输入标题、提交'],
        [tSub + 0.3, '<span class="ai">●</span> 云函数 addCheckin → <span class="ok">200</span>'], [tDb, '<span class="ai">●</span> 查数据库 checkins'], [tDb + 0.6, '<span class="ok">✓ 新记录已写入</span>'],
        [tEdge, '<span class="ai">●</span> 边界：标题为空'], [tEdge + 0.8, '<span class="ok">✓ 前端提示，没写入</span>'], [tEdge + 1.8, '<span class="ok">✓ 端到端测试 6/6 通过</span>']], lv, 21);
      const added = lv >= tSub + 0.4;
      const rows = ROWS0.concat(added ? [['早起跑步 5km', '09-29']] : []);
      list.innerHTML = rows.map((r, i) => `<div class="it${added && i === 2 ? ' new' : ''}"><span>${r[0]}</span><i>${r[1]}</i></div>`).join('');
      form.style.display = lv > T0 + 3.4 && lv < tSub + 0.3 ? 'block' : 'none';
      inp.textContent = '早起跑步 5km'.slice(0, Math.floor(clamp((lv - tType) / 1.2) * 8));
      const bx = SX + 620, by = 230 + 44;
      cur.update(lv, [[0, bx + 700, by + 300], [T0 + 2.4, bx + 700, by + 300], [T0 + 3.1, bx + 90, by + 300, true], [tType - 0.3, bx + 540, by + 156, true], [tSub - 0.4, bx + 540, by + 156], [tSub, bx + 370, by + 222, true], [tSub + 1.0, bx + 600, by + 300]]);
      cur.c.style.opacity = lv > T0 + 2 && lv < tDb + 1 ? 1 : 0;
      const drow = added && lv >= tDb ? `<tr class="new"><td>3</td><td>早起跑步 5km</td><td>2026-09-29</td><td>o7x…3f</td></tr>` : '';
      db.innerHTML = `<div class="dh">CloudBase · 集合 checkins</div><table><tr><th>_id</th><th>title</th><th>date</th><th>openid</th></tr>
        <tr><td>1</td><td>早起背单词</td><td>2026-09-27</td><td>o7x…3f</td></tr><tr><td>2</td><td>跑步 3km</td><td>2026-09-28</td><td>o7x…3f</td></tr>${drow}</table>`;
    },
  };
};

// ======================================================================= 第 5 节（上）：为什么各家都改界面（S17）
S.sec5a = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), T = pid => tm.p0(pid);
  const f47 = flipOf(tm, 'P47'), f48 = flipOf(tm, 'P48');
  // P46–47 METR（示意，手画）
  const L0 = page(root, sh, 0, f47.out);
  hTitle(H, L0, 'AI 能独立干的活越来越长', { x: BX, y: 96, size: 56, at: tm.at('P46', '因为 AI'), kicker: '为什么各家都改界面', sh });
  const X0 = SX + 190, Y0 = 820, CW = 1180, CH = 520;
  const tA = tm.at('P47', '他们的结论是');
  H.line({ x0: X0, y0: Y0, x1: X0 + CW, y1: Y0, at: tA, dur: 0.4, color: '#9AA1AC', w: 4, parent: L0 });
  H.line({ x0: X0, y0: Y0, x1: X0, y1: Y0 - CH, at: tA, dur: 0.3, color: '#9AA1AC', w: 4, parent: L0 });
  ['几秒', '几分钟', '1 小时', '几小时'].forEach((t, i) => sh(bNote(L0, X0 - 140, Y0 - 20 - i * CH / 3.3, t, { width: 120, textAlign: 'right', fontSize: 22 }), tA));
  ['2019', '2021', '2023', '2025'].forEach((t, i) => sh(bNote(L0, X0 + i * CW / 3.3 - 24, Y0 + 8, t, { fontSize: 22 }), tA));
  sh(bNote(L0, X0 + CW - 360, Y0 - CH - 10, 'METR · 纵轴按对数画（示意）', { fontSize: 22 }), tA);
  const t7 = tm.at('P47', '大约每 7 个月'), t23 = tm.at('P47', '2023 年以后');
  H.curve([[X0 + 20, Y0 - 30], [X0 + 0.6 * CW, Y0 - 0.52 * CH]], { at: t7, dur: 1.4, color: '#7E7A72', w: 7, parent: L0 });
  H.curve([[X0 + 0.6 * CW, Y0 - 0.52 * CH], [X0 + 0.95 * CW, Y0 - 0.97 * CH]], { at: t23, dur: 1.0, color: H.ACCENT, w: 8, parent: L0 });
  H.text({ text: '约每 7 个月翻一倍', x: X0 + 80, y: Y0 - 250, size: 40, at: t7 + 0.5, until: t7 + 2.2, parent: L0 });
  H.text({ text: '2023 年后：约 4 个月', x: X0 + 360, y: Y0 - 470, size: 40, color: H.ACCENT, at: t23 + 0.6, until: t23 + 2.2, parent: L0 });
  sh(srcNote(L0, '来源：METR 2025-03-19；METR《Time Horizon 1.1》2026-01-29（曲线示意）'), tA);
  // P48 C 编译器
  const L1 = page(root, sh, f47.in, f48.out);
  const t48 = bg(T('P48'), f47.in);
  hTitle(H, L1, '写代码本身也很强了', { x: BX, y: 96, size: 56, at: t48, sh });
  const grid = mk(L1, 'abs', { left: SX, top: 250, width: 520, height: 520, display: 'grid', gridTemplateColumns: 'repeat(4, 110px)', gap: '20px' });
  const cls = Array.from({ length: 16 }, () => appIcon(grid, 'claude', 110));
  const t16 = bg(tm.at('P48', '16 个 Claude'), t48 + 0.8);
  H.text({ text: '16 个 Claude 并行', x: SX + 250, y: 820, size: 44, align: 'center', at: t16, until: t16 + 1.6, parent: L1 });
  const tC = bg(tm.at('P48', 'C 编译器'), t16 + 1.0);
  H.text({ text: 'C 编译器', x: SX + 640, y: 330, size: 72, at: tC - 1.0, until: tC, parent: L1 });
  H.text({ text: '能编译 Linux 内核', x: SX + 640, y: 440, size: 50, at: tC, until: tC + 1.6, parent: L1 });
  const t10 = tm.at('P48', '大约 10 万行');
  const big = H.text({ text: '约 10 万行代码', x: SX + 640, y: 590, size: 64, color: H.ACCENT, at: t10, until: t10 + 1.6, parent: L1 });
  H.underline({ x0: big.x0, x1: big.x1 + 10, y: big.y1 + 16, at: big.t1 + 0.05, parent: L1 });
  sh(bNote(L1, SX + 640, 680, '近 2000 个会话 · 约 2 万美元 API 费用'), t10 + 1.0);
  sh(srcNote(L1, '来源：Anthropic《Building a C compiler with a team of parallel Claudes》2026-02-05'), t48);
  // P49 vibe coding
  const L2 = page(root, sh, f48.in, null);
  const t49 = bg(T('P49'), f48.in);
  hTitle(H, L2, 'vibe coding：靠说', { x: BX, y: 96, size: 60, at: t49, kicker: 'Karpathy · 2025.02', sh });
  [['用语音输入', '用语音输入'], ['改动全部接受', '改动全部接受'], ['diff 都不看', 'diff 都不看']].forEach(([t, ph], i) => {
    const at = bg(tm.at('P49', ph), t49 + 1.0 + i * 0.5);
    H.dash({ x: SX + 100, y: 320 + i * 100, len: 32, at, parent: L2 });
    H.text({ text: t, x: SX + 150, y: 320 + i * 100, size: 50, at: at + 0.1, until: at + 1.2, parent: L2 });
  });
  const tDm = tm.at('P49', '做个 demo'), tRs = tm.at('P49', '做研究不行');
  H.text({ text: '做 demo', x: SX + 150, y: 700, size: 60, at: tDm, until: tDm + 0.9, parent: L2 });
  H.check({ x: SX + 460, y: 700, size: 56, at: tDm + 1.0, parent: L2 });
  H.text({ text: '做研究', x: SX + 750, y: 700, size: 60, at: tRs, until: tRs + 0.9, parent: L2 });
  H.cross({ x: SX + 1020, y: 700, size: 50, at: tRs + 1.0, parent: L2 });
  sh(bNote(L2, SX + 750, 770, '（后面说为什么）'), tm.at('P49', '后面说为什么'));
  sh(srcNote(L2, '来源：维基百科《Vibe coding》（Karpathy 2025-02-02）'), t49);
  return { H, update(lv) { sh.run(lv); cls.forEach((e, i) => show(e, lv, t16 + i * 0.06, { scale: 0.6, dy: 0 })); } };
};

// ======================================================================= 第 5 节（下）：界面跟着变了（S18）
S.sec5b = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), T = pid => tm.p0(pid), f53 = flipOf(tm, 'P53');
  const tl = hTimeline(H, layer(root), [
    { d: '2025.10', ic: ['cursor'], t1: 'Cursor 2.0', t2: '以智能体为中心', at: tm.at('P50', '2025 年 10 月') },
    { d: '2025.11', ic: ['antigravity'], t1: 'Antigravity', t2: '同时管多个智能体', at: T('P51') },
    { d: '约 2025 年底', ic: ['claude'], t1: 'Claude Code<br>桌面版', at: T('P52') },
    { d: '2026.02', ic: ['codex'], t1: 'Codex App', at: tm.at('P52', '2026 年 2 月') },
    { d: '2026.06', ic: ['copilot'], t1: 'Copilot App', at: T('P53') },
    { d: '2026.06', ic: ['devin'], t1: 'Devin Desktop', t2: '原 Windsurf', at: tm.at('P53', 'Windsurf 改名') },
    { d: '2026.06–08', ic: ['traework', 'trae'], t1: 'TRAE Work<br>TraeCode', at: tm.at('P53', '字节把 Trae') },
  ]);
  const L0 = page(root, sh, 0, f53.out);
  const tS = tm.at('P50', '把界面换成');
  const a = win(L0, SX, 470, 640, 390, '以文件为中心', true); tape(a.el, 0);
  a.body.innerHTML = `<div class="ide"><div class="side"><div class="st">文件</div><div class="on">&nbsp;&nbsp;main.py</div><div>&nbsp;&nbsp;model.py</div><div>&nbsp;&nbsp;data/</div></div>
    <div class="ed"><pre><span class="k">def</span> <span class="f">train</span>():
    ...</pre></div></div><div class="minichat">AI 聊天</div>`;
  const b = win(L0, SX + 862, 470, 640, 390, '以智能体为中心', true); tape(b.el, 1);
  const sess = mk(b.body, 'abs', { left: 0, top: 0, bottom: 0, width: 640, padding: '18px 20px' });
  const sEls = [['修复登录 bug', '运行中'], ['写实验脚本', '等你审批'], ['整理论文图表', '已完成'], ['重构数据加载', '运行中']].map(([t, st]) => mk(sess, 'sess', {}, `<b>${t}</b><i>${st}</i>`));
  sh(a.el, tS); sh(b.el, tS + 1.0);
  H.text({ text: '以文件为中心', x: SX + 320, y: 420, size: 40, align: 'center', at: tS, until: tS + 1.2, color: '#7E7A72', parent: L0 });
  H.arrow({ x0: SX + 660, y0: 660, x1: SX + 840, y1: 660, at: tS + 0.8, dur: 0.3, parent: L0 });
  const ag = H.text({ text: '以智能体为中心', x: SX + 1182, y: 420, size: 40, align: 'center', at: tS + 1.2, until: tS + 2.4, parent: L0 });
  H.underline({ x0: ag.x0, x1: ag.x1 + 8, y: ag.y1 + 14, at: ag.t1 + 0.05, parent: L0 });
  const tM = tm.at('P50', '能同时跑');
  sh(srcNote(L0, '来源：Cursor 博客 2025-10-29；Google 2025-11-18；Claude Code 桌面版文档；OpenAI 2026-02-02；GitHub 博客 2026-06-02；Digital Applied 2026-06；TRAE 博客 2026-06-09、论坛 2026-08-04'), tS);
  // P54 两层
  const L1 = page(root, sh, f53.in, null);
  const t54 = bg(T('P54'), f53.in);
  const back = mk(L1, 'abs layer', { left: SX + 480, top: 380, width: 620, height: 280, background: '#E9EBEF', color: 'var(--gray)', alignItems: 'flex-start', justifyContent: 'flex-end', padding: '24px 34px', fontSize: 44 }, '编辑器');
  const front = mk(L1, 'abs layer', { left: SX + 300, top: 500, width: 620, height: 280, background: 'var(--ink)', color: '#fff', fontSize: 52 }, '智能体');
  sh(back, t54 + 0.1); sh(front, t54 + 0.4, { dy: -20 });
  const c1 = bg(tm.at('P54', '编辑器还在'), t54 + 0.3);
  H.text({ text: '编辑器还在，', x: SX + 1000, y: 780, size: 50, at: c1, until: c1 + 1.2, parent: L1 });
  const c2 = H.html('只是退到了<span class="or">第二层</span>', { x: SX + 1000, y: 860, size: 50, at: c1 + 1.3, until: c1 + 3.0, parent: L1 });
  return { H, update(lv) { sh.run(lv); tl.update(lv); sEls.forEach((e, i) => { show(e, lv, tM + i * 0.3, { dx: 20, dy: 0 }); e.classList.toggle('run', ((Math.floor(lv * 2) + i) % 3) === 0); }); } };
};

// ======================================================================= 第 6 节：AI 走出编辑器（S19）
S.sec6 = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), T = pid => tm.p0(pid);
  const [t56, t57, t58, t59, t60, t61] = ['P56', 'P57', 'P58', 'P59', 'P60', 'P61'].map(T);
  const tl = hTimeline(H, layer(root), [
    { d: '2026.01', ic: ['claude'], t1: 'Cowork', t2: '给不写代码的人用', at: t56 },
    { d: '2026.01', ic: ['openclaw'], t1: 'OpenClaw 爆火', t2: '“养龙虾”', at: t57 },
    { d: '2026.02', ic: ['openclaw'], t1: '作者加入 OpenAI', at: t59 },
    { d: '2026.03', ic: ['workbuddy'], t1: '腾讯 WorkBuddy', at: tm.at('P60', '3 月腾讯') },
    { d: '2026.06', ic: ['traework'], t1: 'TRAE Work', t2: '原 TRAE SOLO', at: tm.at('P60', '6 月字节') },
    { d: '2026.08', ic: ['doubao'], t1: '豆包 Work', at: tm.at('P60', '8 月又出了') },
    { d: '2026.09', ic: ['claude'], t1: 'Cowork<br>并入 Claude', at: t61 },
  ]);
  const f55 = flipOf(tm, 'P55'), f56 = flipOf(tm, 'P56'), f57 = flipOf(tm, 'P57'), f58 = flipOf(tm, 'P58'), f59 = flipOf(tm, 'P59');
  // P55
  const L0 = page(root, sh, 0.2, f55.out);
  const bi = sh(mk(L0, 'abs', { left: SX + 200, top: 470, width: 160, height: 160 }), 0.3); appIcon(bi, 'openclaw', 160);
  H.text({ text: 'OpenClaw', x: SX + 420, y: 560, size: 110, at: 0.3, until: 1.8, parent: L0 });
  const why = H.html('今年 Agent 火的<span class="or">导火索</span>', { x: SX + 420, y: 720, size: 52, at: 1.6, until: 3.2, parent: L0 });
  // P56 Cowork
  const L1 = page(root, sh, f55.in, f56.out);
  const cw = sh(mk(L1, 'abs', { left: SX + 200, top: 430, width: 110, height: 110 }), bg(t56, f55.in)); appIcon(cw, 'claude', 110);
  H.text({ text: 'Cowork', x: SX + 340, y: 490, size: 80, at: bg(t56, f55.in), until: bg(t56, f55.in) + 1.0, parent: L1 });
  const tg = bg(tm.at('P56', '把 Claude Code'), bg(t56, f55.in) + 1.1);
  H.html('把 Claude Code 这套能力，', { x: SX + 200, y: 640, size: 50, at: tg, until: tg + 2.0, parent: L1 });
  H.html('给<span class="or">不写代码的人</span>用', { x: SX + 200, y: 730, size: 50, at: tg + 2.0, until: tg + 3.4, parent: L1 });
  // P57 聊天软件里指挥（模拟）
  const L2 = page(root, sh, f56.in, f57.out);
  const ph = win(L2, SX, 360, 620, 500, '聊天软件 · OpenClaw（模拟）', false); tape(ph.el, 0);
  const chB = mk(ph.body, 'chatb', { padding: '18px 20px' });
  [['装在自己电脑上', '它装在你自己的电脑上'], ['聊天软件里发一句话', '你在 Telegram'], ['记得之前的事', '它能记住之前的事'], ['自己连续执行任务', '还会自己连续执行']].forEach(([t, ph2], i) => {
    const at = bg(tm.at('P57', ph2), bg(t57, f56.in) + i * 0.4);
    H.dash({ x: SX + 700, y: 420 + i * 110, len: 32, at, parent: L2 });
    H.text({ text: t, x: SX + 750, y: 420 + i * 110, size: 46, at: at + 0.1, until: wwin(at + 0.1, t, null, 2.2), maxW: 740, parent: L2 });
  });
  const tC = tm.at('P57', '你在 Telegram');
  // P58 星数
  const L3 = page(root, sh, f57.in, f58.out);
  const t58b = bg(t58, f57.in);
  H.text({ text: 'GitHub 星数', x: BX, y: 380, size: 50, align: 'center', at: t58b, until: t58b + 1.2, parent: L3 });
  const num = sh(mk(L3, 'abs', { left: SX, top: 440, width: SW, textAlign: 'center', font: "800 150px 'Space Grotesk','Noto Sans SC'", color: 'var(--ink)' }), t58b + 0.3);
  const when = sh(bNote(L3, SX, 640, '', { width: SW, textAlign: 'center', fontSize: 26 }), t58b + 0.3);
  const tLob = tm.at('P58', '国内叫它');
  const lob = H.text({ text: '国内叫它：养龙虾', x: BX, y: 780, size: 60, align: 'center', at: tLob, until: tLob + 1.6, parent: L3 });
  H.mark(lob, 5, 8, { kind: 'circle', parent: L3 });
  // P59 作者加入 OpenAI
  const L4 = page(root, sh, f58.in, f59.out);
  const t59b = bg(t59, f58.in);
  const ic1 = sh(mk(L4, 'abs', { left: BX - 300, top: 420, width: 120, height: 120 }), t59b); appIcon(ic1, 'openclaw', 120);
  H.arrow({ x0: BX - 150, y0: 480, x1: BX + 150, y1: 480, at: t59b + 0.3, dur: 0.35, parent: L4 });
  const ic2 = sh(mk(L4, 'abs', { left: BX + 180, top: 420, width: 120, height: 120 }), t59b + 0.5); appIcon(ic2, 'openai', 120);
  H.text({ text: '作者加入了 OpenAI', x: BX, y: 660, size: 56, align: 'center', at: t59b + 0.4, until: t59b + 2.2, parent: L4 });
  // P60–61 国内跟上 + Cowork 并入 Claude
  const L5 = page(root, sh, f59.in, null);
  const t60b = bg(t60, f59.in);
  [['workbuddy', '腾讯 WorkBuddy', '2026.03', '3 月腾讯'], ['traework', 'TRAE Work', '2026.06', '6 月字节'], ['doubao', '豆包 Work', '2026.08', '8 月又出了']].forEach(([k, n, d, ph], i) => {
    const at = bg(tm.at('P60', ph), t60b + i * 0.6), x = SX + 60 + i * 500;
    if (k) { const e = sh(mk(L5, 'abs', { left: x, top: 380, width: 84, height: 84 }), at); appIcon(e, k, 84); }
    H.text({ text: n, x: k ? x + 100 : x, y: 422, size: 42, at: at + 0.1, until: at + 1.3, maxW: k ? 360 : 440, parent: L5 });
    H.text({ text: d, x, y: 520, size: 40, color: H.ACCENT, at: at + 1.2, until: at + 1.7, parent: L5 });
  });
  const tM = bg(t61, t60b + 1.5);
  const mg = H.html('Cowork 并进 <span class="or">Claude 的主界面</span>', { x: BX, y: 700, size: 54, align: 'center', at: tM, until: tM + 2.2, parent: L5 });
  const src = srcNote(root, '');
  return {
    H,
    update(lv) {
      sh.run(lv); tl.update(lv);
      chatRender(chB, [[tC, 'me', '把桌面上的发票整理成一张表'], [tC + 1.4, 'ai', '收到，开始处理：共 23 张'], [tC + 3.0, 'ai', '✓ 已完成：桌面/发票汇总.xlsx'], [tm.at('P57', '它能记住'), 'me', '跟上个月的放一起'], [tm.at('P57', '它能记住') + 1.2, 'ai', '好的，已合并到 9 月的表里']], lv);
      const tN = tm.at('P58', '现在已经超过'), n = lv < tN ? 24.7 : lerp(24.7, 39.0, easeOut((lv - tN) / 1.5));
      num.innerHTML = `${n.toFixed(1)}${lv >= tN + 1.5 ? '+' : ''} 万`;
      when.textContent = lv < tN ? '2026.03.02' : '2026.09.29 查询（390,757）';
      src.innerHTML = lv < t57 ? '来源：TechCrunch 2026-01-12' : lv < t59 ? '来源：维基百科《OpenClaw》；GitHub openclaw/openclaw（2026-09-29 查询）；观察者网、中新网 2026-03-11'
        : lv < t60 ? '来源：TechCrunch 2026-02-15' : '来源：TechNode 2026-03-09；TRAE 博客 2026-06-09；BigGo 财经 2026-08；VentureBeat 2026-09-16';
      show(src, lv, 0.8);
    },
  };
};

// ---- S20 方向很清楚（A）
S.direction = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows();
  const L = layer(root);
  sh(bKick(L, RX, 210, '方向很清楚'), 0.1);
  const a = tm.at('P62', 'AI 从帮你写代码'), b = tm.at('P62', '变成'), c = tm.at('P62', '替你干活');
  H.text({ text: 'AI 帮你写代码', x: RX, y: 340, size: 62, color: '#7E7A72', at: a, until: a + 1.4, parent: L });
  H.arrow({ x0: RX + 150, y0: 400, x1: RX + 150, y1: 500, at: b, dur: 0.3, parent: L });
  const w = H.text({ text: '替你干活', x: RX, y: 610, size: 120, at: bg(c, b + 0.3), until: bg(c, b + 0.3) + 1.4, parent: L });
  H.underline({ x0: w.x0, x1: w.x1 + 10, y: w.y1 + 18, at: w.t1 + 0.05, parent: L });
  return { H, update(lv) { sh.run(lv); } };
};

// ---- S21 风险（B）
S.risk = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), f63 = flipOf(tm, 'P63');
  const L0 = page(root, sh, 0, f63.out);
  hTitle(H, L0, '风险也很清楚', { x: BX, y: 96, size: 60, at: 0.2, sh });
  const c1 = mk(L0, 'abs wcard', { left: SX, top: 220, width: 730, height: 560 }); tape(c1, 0);
  const c2 = mk(L0, 'abs wcard', { left: SX + 772, top: 220, width: 730, height: 560 }); tape(c2, 1);
  const a1 = tm.at('P63', '2 月'), a2 = tm.at('P63', '3 月');
  sh(c1, a1, { scale: 0.96 }); sh(c2, a2, { scale: 0.96 });
  sh(bKick(L0, SX + 40, 250, '2026.02 · OPENCLAW 技能市场'), a1);
  H.text({ text: '341 / 2857', x: SX + 40, y: 390, size: 96, color: H.RED, at: a1 + 0.2, until: a1 + 1.6, parent: L0 });
  H.text({ text: '个技能是恶意的', x: SX + 40, y: 520, size: 50, at: a1 + 1.6, until: a1 + 3.0, parent: L0 });
  const steal = tm.at('P63', '会偷你电脑上');
  const st = H.text({ text: '偷你的账号密码', x: SX + 40, y: 620, size: 50, at: bg(steal, a1 + 3.0), until: bg(steal, a1 + 3.0) + 1.5, parent: L0 });
  H.mark(st, 1, 7, { kind: 'underline', parent: L0 });
  sh(bNote(L0, SX + 40, 700, '2 月 16 日增加到 824 个以上'), a1 + 2.0);
  sh(bKick(L0, SX + 812, 250, '2026.03 · 工信部风险提示'), a2);
  H.text({ text: '默认配置', x: SX + 812, y: 390, size: 60, at: a2 + 0.2, until: a2 + 1.2, parent: L0 });
  const d2 = tm.at('P63', '很容易被攻击');
  H.text({ text: '容易被攻击、', x: SX + 812, y: 500, size: 56, at: bg(d2, a2 + 1.2), until: bg(d2, a2 + 1.2) + 1.2, parent: L0 });
  const lk = H.text({ text: '泄露信息', x: SX + 812, y: 600, size: 56, at: bg(d2, a2 + 1.2) + 1.2, until: bg(d2, a2 + 1.2) + 2.2, parent: L0 });
  H.mark(lk, 0, 4, { kind: 'circle', parent: L0 });
  sh(bNote(L0, SX + 812, 690, '“六要六不要”'), a2 + 1.0);
  sh(srcNote(L0, '来源：The Hacker News 2026-02；观察者网、中新网 2026-03-11'), 0.8);
  const L1 = page(root, sh, f63.in, null);
  const t64 = bg(tm.p0('P64'), f63.in);
  H.text({ text: '给 AI 的权限越大，', x: BX, y: 440, size: 72, align: 'center', at: t64, until: t64 + 2.0, parent: L1 });
  const w2 = H.html('出事的<span class="or">代价越大</span>', { x: BX, y: 600, size: 80, align: 'center', at: t64 + 2.0, until: t64 + 3.4, parent: L1 });
  return { H, update(lv) { sh.run(lv); } };
};
