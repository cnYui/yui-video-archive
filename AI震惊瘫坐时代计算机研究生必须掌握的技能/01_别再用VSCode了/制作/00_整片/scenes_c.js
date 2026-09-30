// 画面（白板版）：第二章（Claude Code 桌面版实操）+ 结尾（S22–S34）。
// 录屏是贴在白板上的卡片（右边演示区，出镜框在左上角，不压）；上面手写这一项的标题。录屏里没有的几项（HTML 可视化、computer use）用代码模拟。

// 盖在录屏上的卡片：白卡片（贴胶带）+ 一层手写（层在卡片上面，一起淡入淡出），录屏整体压暗
function overCard(root, sh, x, y, w, h, t0, t1) {
  const dim = mk(root, 'abs', { left: SX + 98 + 14, top: 150 + 14, width: 1278, height: 719, background: 'rgba(0,0,0,.45)', zIndex: 18, borderRadius: 4 });
  const card = mk(root, 'abs wcard', { left: x, top: y, width: w, height: h, zIndex: 20 }); tape(card, 1);
  const L = layer(root); L.style.zIndex = 21;
  sh(dim, t0, { dy: 0, t1 }); sh(card, t0, { scale: 0.97, t1 }); sh(L, t0, { dy: 0, t1 });
  return L;
}
function recScene(type, title, extra) {
  return (root, s) => {
    const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows();
    const L = layer(root);
    hTitle(H, L, title, { x: BX, y: 86, size: 50, at: 0, sh, maxW: 1400 });
    const rp = recPlayer(L, type, SX + 98, 150, 1306, 747);   // 内框 1278×719（16:9），下沿 897
    tape(rp.fb.f, 0);
    sh(rp.fb.f, 0, { scale: 0.985, dy: 0 });
    rp.plan(tm, LEAD + 0.2, s.end - s.start + LEAD - 0.3);
    const cap = mk(rp.fb.inner, 'abs capbar', {});
    const ex = extra ? extra(root, s, tm, H, sh) : null;
    return {
      H,
      update(lv) {
        sh.run(lv); rp.update(lv);
        const c = ex && ex.caption ? ex.caption(lv) : '';
        cap.innerHTML = c; cap.style.opacity = c ? 1 : 0;
        if (ex && ex.update) ex.update(lv);
      },
    };
  };
}

// ---- S22 第二章（A）
S.ch2 = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows();
  const L = layer(root);
  sh(bKick(L, RX, 200, '第二章'), 0);
  H.text({ text: 'Claude Code', x: RX, y: 320, size: 96, at: 0, until: 1.4, parent: L });
  const b = H.text({ text: '桌面版实操', x: RX, y: 470, size: 96, at: 1.4, until: 2.8, parent: L });
  H.underline({ x0: b.x0, x1: b.x1 + 10, y: b.y1 + 18, at: b.t1 + 0.05, parent: L });
  const tC = tm.at('P65', 'Codex 桌面版');
  const r = sh(mk(L, 'abs', { left: RX, top: 600, display: 'flex', gap: '20px' }), tC - 0.3); appIcon(r, 'claude', 80); appIcon(r, 'codex', 80);
  H.text({ text: 'Codex 桌面版思路差不多', x: RX, y: 760, size: 44, at: tC, until: tC + 2.0, parent: L });
  return { H, update(lv) { sh.run(lv); } };
};

S.sessions = recScene('sessions', '① 同时开好几个会话', (root, s, tm, H, sh) => ({
  caption: lv => lv < tm.at('P66', '每个会话') ? '左边：会话列表' : lv < tm.pe('P66') + 1.5 ? '每个会话可以有自己的 Git worktree，互不干扰' : '分支 · worktree',
}));
S.diff = recScene('diff', '② 右边看 diff', (root, s, tm) => ({
  caption: lv => lv < tm.at('P67', '点某一行') ? '右边：这次改了什么' : lv < tm.at('P67', '也能用') ? '点某一行写评论 → 一次提交 → Claude 按评论改' : '也能用 @ 引用文件',
}));
S.termbrowser = recScene('termbrowser', '③ 内置终端和浏览器', (root, s, tm) => ({
  caption: lv => lv < tm.at('P68', '它能自己起服务') ? '内置终端' : lv < tm.at('P68', '生成的 PDF') ? '浏览器面板：它自己起服务、打开页面' : 'PDF、HTML 也直接在右边打开',
}));

// ---- S26 HTML 可视化（模拟：录屏里没有这一项）
S.html = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), f69 = flipOf(tm, 'P69');
  const L0 = page(root, sh, 0, f69.out);
  hTitle(H, L0, '④ 善用 HTML 可视化', { x: BX, y: 86, size: 50, at: 0, sh });
  const app = win(L0, SX, 160, SW, 720, 'Claude Code 桌面版（模拟）', true); tape(app.el, 0);
  const chat = mk(app.body, 'abs', { left: 0, top: 0, bottom: 0, width: 540, padding: '22px 24px', borderRight: '1px solid #3A3B40' });
  const chB = mk(chat, 'chatb dark');
  const pane = mk(app.body, 'abs', { left: 540, top: 0, right: 0, bottom: 0, background: '#2B2D31' });
  mk(pane, 'abs', { left: 16, top: 12, right: 16, height: 40, borderRadius: 8, background: '#1E1F22', color: '#AEB3BB', font: "500 20px 'JetBrains Mono'", padding: '8px 14px' }, 'changes.html');
  const REP = `<div class="h">GitHub Star 实时同步：这次改了什么</div>
    <div class="cols"><div class="files"><div class="st">改了哪些文件</div>
      ${[['github-contributions.js', 245, 0], ['server.js', 32, 2], ['launch.json', 19, 2], ['其他 9 个文件', 60, 58]].map(([n, a, d]) => `<div class="f"><span>${n}</span><i style="width:${a * 0.6}px"></i><b>+${a} −${d}</b></div>`).join('')}</div>
    <div class="flow"><div class="st">流程</div><div class="fl"><span>访客打开主页</span>→<span>server.js</span>→<span>GitHub API</span></div><div class="fl"><span class="o">15 分钟缓存</span>→<span>主页卡片</span></div></div></div>
    <div class="cmp"><div class="b"><div class="st">改前</div>数字写死在页面里，<br>要手动更新</div><div class="a"><div class="st">改后</div>服务器定时去 GitHub 拉，<br>过 15 分钟自动刷新</div></div>`;
  const rep = mk(pane, 'abs htmlrep', { left: 16, top: 62, right: 16, bottom: 16 }, REP);
  const tHtml = tm.at('P69', '我一般让 AI'), tOpen = tm.at('P69', '在右边的浏览器');
  sh(bNote(L0, SX + 1160, 890, '模拟演示'), 0.3);
  // P70：一段文字 vs 一张图
  const L1 = page(root, sh, f69.in, null);
  const t70 = bg(tm.p0('P70'), f69.in);
  H.text({ text: '同一件事：一段文字，还是一张图？', x: BX, y: 110, size: 50, align: 'center', at: t70, until: t70 + 2.6, parent: L1 });
  const txt = mk(L1, 'abs wcard', { left: SX, top: 220, width: 660, height: 560, padding: '30px 34px', font: "500 26px/1.8 'Noto Sans SC'", color: 'var(--gray)' },
    '这次修改了 github-contributions.js、server.js、launch.json 等 12 个文件。服务器端新增了一个接口，每隔 15 分钟从 GitHub 获取一次公开贡献数据并缓存，页面加载时读取缓存中的数据并渲染到主页的贡献卡片上；原来卡片上的数字是写死在页面里的，需要手动更新……');
  tape(txt, 2);
  const pic = mk(L1, 'abs', { left: SX + 800, top: 220, width: 702, height: 560, borderRadius: 14, overflow: 'hidden', boxShadow: '0 10px 24px rgba(0,0,0,.12)', background: '#fff' });
  const mini = mk(pic, 'abs htmlrep', { left: 0, top: 0, width: 924, height: 737, transform: 'scale(0.76)', transformOrigin: '0 0' }, REP);
  const picT = mk(L1, 'abs', { left: SX + 800, top: 220, width: 702, height: 560 }); tape(picT, 3);
  const tTx = tm.at('P70', '给我一段文字'), tPic = tm.at('P70', '和一张图');
  sh(txt, bg(tTx, t70 + 1.0), { scale: 0.97 }); sh(pic, bg(tPic, t70 + 1.6), { scale: 0.97 }); sh(picT, bg(tPic, t70 + 1.6), { scale: 0.97 });
  H.text({ text: 'vs', x: SX + 730, y: 500, size: 60, align: 'center', color: H.ACCENT, at: bg(tPic, t70 + 1.6), until: bg(tPic, t70 + 1.6) + 0.5, parent: L1 });
  const tMe = tm.at('P70', '我肯定先看图');
  H.ellipse({ x0: SX + 800, y0: 220, x1: SX + 1502, y1: 780, at: tMe, color: H.HILITE, w: 10, padX: 6, padY: 6, parent: L1 });
  [['颜色', '图有颜色'], ['字有大有小', '字有大有小'], ['有主有次', '有主有次']].forEach(([t, ph], i) => {
    const at = bg(tm.at('P70', ph), t70 + 2.5 + i * 0.4);
    H.dash({ x: SX + 700 + i * 290, y: 850, len: 26, at, parent: L1 });
    H.text({ text: t, x: SX + 740 + i * 290, y: 850, size: 40, at: at + 0.1, until: at + 1.0, parent: L1 });
  });
  return {
    H,
    update(lv) {
      sh.run(lv);
      chatRender(chB, [[tHtml, 'me', '把这次的改动做成一页 HTML：改了哪些文件、流程图、改前改后对比'], [tHtml + 1.6, 'ai', '好的，已生成 changes.html，在右边打开了。']], lv);
      show(rep, lv, tOpen, { scale: 0.97 });
    },
  };
};

S.perms = recScene('perms', '⑤ 权限分几档', (root, s, tm) => {
  const M = [['Manual', '每一步都问你'], ['Accept edits', '改文件不问'], ['Plan', '只出方案，不动代码'], ['Auto', '由另一个模型替你审批'], ['Bypass', '全放开（要先在设置里打开开关）']];
  const tt = M.map(([k]) => tm.at('P71', k));
  return { caption: lv => { let k = -1; tt.forEach((t, i) => { if (lv >= t - 0.1) k = i; }); return k < 0 ? '输入框下面：选权限模式' : `<b>${M[k][0]}</b>　${M[k][1]}`; } };
});

S.ssh = recScene('ssh', '⑥ SSH：在实验室服务器上干活', (root, s, tm, H, sh) => {
  const t73 = tm.p0('P73');
  const L = overCard(root, sh, SX + 200, 260, 1100, 520, t73, null);
  H.text({ text: '注意两点', x: SX + 250, y: 330, size: 50, at: t73 + 0.1, until: t73 + 1.0, parent: L });
  hPoint(H, L, 1, '服务器要是 <span class="or">Linux 或 macOS</span>', SX + 260, 450, { size: 46, at: tm.at('P73', '服务器要是') });
  hPoint(H, L, 2, '服务器要能连上<span class="or">模型的 API</span>', SX + 260, 560, { size: 46, at: tm.at('P73', '服务器要能连上') });
  const tCx = tm.at('P73', 'Codex 桌面版');
  H.text({ text: 'Codex：要先在服务器上装好 Codex', x: SX + 260, y: 670, size: 40, color: '#6E6A63', at: tCx, until: tCx + 2.4, parent: L });
  mk(L, 'abs note', { left: SX + 240, top: 718, width: 1020, whiteSpace: 'normal' }, '来源：Claude Code 官方文档《Desktop application》；OpenAI Codex 文档《Remote connections》（2026-09 读取）');
  return { caption: lv => lv < tm.at('P72', '它会在服务器上') ? '环境：本地 / 云端 / Remote Control / WSL / SSH' : '选一台 SSH 主机（第一次连会自动装好 Claude Code）' };
});

S.routines = recScene('routines', '⑦ Routines 定时任务', (root, s, tm, H, sh) => {
  const tC = tm.at('P74', '云端任务') - 0.2;
  const L = overCard(root, sh, SX + 160, 230, 1180, 580, tC, null);
  const a = tm.at('P74', '本地任务'), b = tm.at('P74', '云端任务');
  H.text({ text: '本地任务', x: SX + 220, y: 300, size: 50, at: bg(a, tC), until: bg(a, tC) + 0.9, parent: L });
  H.check({ x: SX + 240, y: 390, size: 34, at: bg(a, tC) + 0.8, parent: L }); H.text({ text: '能读你的文件', x: SX + 280, y: 390, size: 40, at: bg(a, tC) + 0.9, until: bg(a, tC) + 1.8, parent: L });
  H.cross({ x: SX + 240, y: 470, size: 30, at: bg(a, tC) + 1.8, parent: L }); H.text({ text: '电脑、App 要开着', x: SX + 280, y: 470, size: 40, at: bg(a, tC) + 1.9, until: bg(a, tC) + 3.0, parent: L });
  H.text({ text: '云端任务', x: SX + 800, y: 300, size: 50, at: b + 0.4, until: b + 1.3, parent: L });
  H.check({ x: SX + 820, y: 390, size: 34, at: b + 1.2, parent: L }); H.text({ text: '关机也能跑', x: SX + 860, y: 390, size: 40, at: b + 1.3, until: b + 2.1, parent: L });
  H.cross({ x: SX + 820, y: 470, size: 30, at: b + 2.1, parent: L }); H.text({ text: '读不到本地文件', x: SX + 860, y: 470, size: 40, at: b + 2.2, until: b + 3.2, parent: L });
  const m = tm.at('P74', '我用本地任务');
  H.html('我的用法：超过一个月的记录，<span class="or">移到归档</span>', { x: SX + 220, y: 620, size: 42, at: m, until: m + 3.0, parent: L });
  mk(L, 'abs note', { left: SX + 200, top: 760 }, '来源：Claude Code 官方文档《Schedule recurring tasks in Claude Code Desktop》（2026-09 读取）');
  return { caption: lv => lv < a ? '左边栏：Routines' : '新建本地任务：写说明、选时间' };
});

// ---- S30 computer use（模拟：录屏里没有这一项）
S.computeruse = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows();
  const L = layer(root);
  hTitle(H, L, '⑧ computer use：直接操作电脑上的软件', { x: BX, y: 86, size: 46, at: 0, sh });
  const app = win(L, SX, 160, SW, 720, 'Claude Code 桌面版 · 设置（模拟）', false); tape(app.el, 0);
  const body = mk(app.body, 'abs settings', { left: 0, top: 0, right: 0, bottom: 0 });
  body.innerHTML = `<div class="nav"><div>通用</div><div>权限</div><div class="on">Computer use</div><div>SSH</div><div>Routines</div></div>
    <div class="pane"><div class="t">Computer use <span class="badge">研究预览</span></div>
    <div class="d">让 Claude 直接操作你电脑上的软件：看屏幕、点鼠标、打字。</div>
    <div class="row"><span>启用 computer use</span><span class="sw" id="sw"><i></i></span></div>
    <div class="d2">需要 Pro 或 Max · Mac 和 Windows</div></div>`;
  const sw = body.querySelector('#sw');
  const dlg = mk(L, 'abs wcard dlg', { left: SX + 480, top: 420, width: 620, height: 300, zIndex: 20 },
    `<div style="font:800 34px 'Noto Sans SC'">允许 Claude 控制「记事本」？</div><div style="font:600 24px/1.6 'Noto Sans SC';color:var(--gray);margin-top:14px">每个 App 第一次用都要你点允许</div>
     <div style="display:flex;gap:18px;justify-content:flex-end;margin-top:40px"><span class="btn gray">拒绝</span><span class="btn">允许</span></div>`);
  const cur = cursor(L);
  const tOn = tm.at('P75', '默认关着') + 0.8, tAsk = tm.at('P75', '每个 App'), tWin = tm.at('P75', '在 Windows 上');
  sh(dlg, tAsk, { t1: tWin - 0.3 + LEAD, scale: 0.9 });
  const W = overCardPlain(root, sh, SX + 100, 560, 1300, 280, tWin);
  H.text({ text: 'Windows 上：', x: SX + 150, y: 630, size: 48, at: tWin + 0.1, until: tWin + 1.0, parent: W });
  const w2 = H.html('命令行版用不了 computer use，<span class="or">用桌面版</span>', { x: SX + 150, y: 740, size: 46, at: tWin + 1.0, until: tWin + 3.4, parent: W });
  sh(bNote(L, SX + 1340, 118, '模拟演示'), 0.3);
  sh(srcNote(L, '来源：Claude Code 官方文档《Desktop application》《Let Claude use your computer from the CLI》（2026-09 读取）', 886), 0.3);
  return {
    H,
    update(lv) {
      sh.run(lv);
      sw.classList.toggle('on', lv > tOn);
      const bx = SX + 480;
      cur.update(lv, [[0, SX + 900, 750], [tOn - 1.0, SX + 900, 750], [tOn - 0.1, SX + 1160, 412, true], [tAsk + 0.3, SX + 1160, 412], [tAsk + 1.5, bx + 540, 602, true], [tWin, bx + 560, 700]]);
    },
  };
};
// 盖在示意窗口上的白卡片（不压暗）+ 一层手写
function overCardPlain(root, sh, x, y, w, h, t0) {
  const card = mk(root, 'abs wcard', { left: x, top: y, width: w, height: h, zIndex: 20 }); tape(card, 2);
  const L = layer(root); L.style.zIndex = 21;
  sh(card, t0, { scale: 0.97 }); sh(L, t0, { dy: 0 });
  return L;
}

S.chrome = recScene('chrome', '⑨ 浏览器插件 Claude in Chrome', (root, s, tm, H, sh) => {
  const t77 = tm.p0('P77');
  const L = overCard(root, sh, SX + 140, 190, 1220, 680, t77, null);
  H.text({ text: '几条限制', x: SX + 190, y: 250, size: 48, at: t77 + 0.1, until: t77 + 1.0, parent: L });
  [['不做股票交易', '不做股票交易'], ['不绕验证码', '不绕验证码'], ['不替你输入敏感信息', '不替你输入敏感信息']].forEach(([t, ph], i) => {
    const at = bg(tm.at('P77', ph), t77 + 1.0 + i * 0.4);
    H.cross({ x: SX + 210, y: 340 + i * 70, size: 28, at, parent: L });
    H.text({ text: t, x: SX + 250, y: 340 + i * 70, size: 40, at: at + 0.1, until: at + 1.3, parent: L });
  });
  const tF = tm.at('P77', '进金融网站前'), tA = tm.at('P77', '成人网站');
  H.text({ text: '金融网站：先问你', x: SX + 780, y: 340, size: 40, at: tF, until: tF + 1.4, parent: L });
  H.text({ text: '成人、盗版网站：拦截', x: SX + 780, y: 410, size: 40, at: tA, until: tA + 1.6, parent: L });
  const tD = tm.at('P77', '它默认'), tS = tm.at('P77', '建议改成');
  H.text({ text: '默认：它自己审自己', x: SX + 190, y: 580, size: 44, at: tD, until: tD + 1.6, parent: L });
  const sug = H.html('建议：<span class="or">每一步都要你批准</span>', { x: SX + 190, y: 670, size: 44, at: tS, until: tS + 2.0, parent: L });
  const tR = tm.at('P77', '把登录状态');
  H.text({ text: '把登录状态交给 AI，风险自己掂量', x: SX + 190, y: 770, size: 40, color: H.ACCENT, at: tR, until: tR + 2.6, parent: L });
  mk(L, 'abs note', { left: SX + 180, top: 820 }, '来源：Claude 帮助中心《Use Claude in Chrome safely》（2026-08-12 更新）');
  return { caption: lv => lv < tm.at('P76', '也能替你发消息') ? '用你浏览器的登录状态：查信息、比价、整理网页' : '也能替你发消息、下单 —— 责任算你的' };
});

S.gpt6 = recScene('gpt6', 'GPT-6 Astra（2026.09）· 可选', (root, s, tm) => ({
  caption: lv => lv < tm.at('P78', '发布演示里') ? '官方定位：电脑操作和长任务' : '发布演示：在 Blender 里建一整栋房子，再导进虚幻引擎　｜　视频来源：待补',
}));

// ---- S33 一句话总结（A）
S.summary = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows();
  const L = layer(root);
  sh(bKick(L, RX, 180, '一句话总结'), 0);
  hPoint(H, L, 1, '所有东西<span class="or">放进一个界面</span>', RX, 300, { size: 52, at: tm.at('P79', '它把前面') });
  hPoint(H, L, 2, '门槛很低，上手就能用', RX, 440, { size: 52, at: tm.at('P79', '门槛很低') });
  hPoint(H, L, 3, '编程软件，也是<span class="or">办公软件</span>', RX, 580, { size: 52, at: tm.at('P79', '说它是编程软件') });
  return { H, update(lv) { sh.run(lv); } };
};

// ---- S34 结尾（A）
S.outro = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows();
  const L = layer(root);
  sh(bKick(L, RX, 220, '结尾'), 0);
  H.text({ text: '这就是 AI 写代码', x: RX, y: 340, size: 66, at: 0, until: 1.6, parent: L });
  H.text({ text: '这五年的变化', x: RX, y: 450, size: 66, at: 1.6, until: 3.0, parent: L });
  const b = H.text({ text: '我是悠一，拜拜', x: RX, y: 640, size: 84, color: H.ACCENT, at: tm.p0('P81'), until: tm.p0('P81') + 1.6, parent: L });
  return { H, update(lv) { sh.run(lv); } };
};
