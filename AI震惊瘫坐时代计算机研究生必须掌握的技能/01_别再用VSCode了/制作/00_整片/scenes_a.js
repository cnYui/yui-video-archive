// 画面（白板版）：开场 + 第一章第 1–3 节（S01–S12）。
// 说到的要点边说边手写（hand.js），示意窗口、录屏是贴在白板上的印刷卡片（贴胶带），印刷体只留小字（出处、小标签）。
// 时间都按声音写（tm.*），engine.js 让画面整体早 LEAD 秒；同一场景里翻页用 flipOf(tm, 这一页最后一段)。
const S = {};
const BX = SX + SW / 2;                 // 版式 B 演示区的中线
const bg = (t, next) => Math.max(t, next);   // 翻页后：不早于下一页开始的时刻

// ---- S01 开场（A）：别再用 VS Code 了
S.intro = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), tQ = tm.at('P01', '求求大家');
  const L = layer(root);
  sh(bKick(L, RX, 180, 'AI 时代 · 计算机研究生必须掌握 · 之一'), 0.2);
  H.text({ text: 'Hello，我是悠一', x: RX, y: 290, size: 54, at: 0.1, until: 1.6, parent: L });
  H.text({ text: '别再用', x: RX, y: 470, size: 112, at: tQ, until: tQ + 1.0, parent: L });
  const b = H.text({ text: 'VS Code 了', x: RX, y: 630, size: 112, at: tQ + 1.05, until: tQ + 2.4, parent: L });
  H.underline({ x0: b.x0 - 4, x1: b.box(0, 7)[2] + 8, y: b.y1 + 18, at: b.t1 + 0.05, dur: 0.35, parent: L });
  const ic = sh(mk(L, 'abs', { left: RX + 560, top: 350, width: 150, height: 150 }), tQ + 0.3, { scale: 0.8 });
  appIcon(ic, 'vscode', 150);
  H.cross({ x: RX + 780, y: 470, size: 70, at: tQ + 2.5, dur: 0.35, parent: L });     // 叉画在图标旁边，不压图标（VS Code 使用规范）
  return { H, update(lv) { sh.run(lv); } };
};

// ---- S02 新系列（A）
S.series = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), f = flipOf(tm, 'P02');
  const L1 = page(root, sh, 0, f.out);
  sh(bKick(L1, RX, 170, '新系列'), 0.2);
  let t = 0.2;
  ['AI 时代', '计算机研究生', '必须掌握的技能'].forEach((x, i) => { const it = H.text({ text: x, x: RX, y: 270 + i * 110, size: 76, at: t, until: wwin(t, x), parent: L1 }); t = it.t1 + 0.15; });
  sh(bNote(L1, RX, 610, '给搞科研的同学、写代码的朋友'), tm.at('P02', '搞科研的朋友'));
  const tA = tm.at('P02', '如何在 AI 时代');
  H.html('和 <span class="or">Agent</span> 一起写代码、做研究', { x: RX, y: 720, size: 50, at: tA, until: wwin(tA, '和Agent一起写代码做研究'), parent: L1 });
  const L2 = page(root, sh, f.in, null);
  sh(bKick(L2, RX, 190, '这期'), f.in);
  hPoint(H, L2, 1, '为什么别再用 VS Code', RX, 300, { size: 54, at: bg(tm.at('P03', '为什么不用'), f.in) });
  hPoint(H, L2, 2, '用什么新形态写代码', RX, 420, { size: 54, at: bg(tm.at('P03', '我们应该用什么'), f.in) });
  hPoint(H, L2, 3, '这种新形态怎么用', RX, 540, { size: 54, at: bg(tm.at('P03', '以及如何去使用'), f.in) });
  return { H, update(lv) { sh.run(lv); } };
};

// ---- S03 这些名字你都听过（A）：图标墙 → IDE？CLI？ → SSH 该用哪个？
S.names = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows();
  const L = layer(root);
  sh(bKick(L, RX, 150, '你可能听过'), 0.1);
  [['copilot', 'GitHub Copilot', 'Copilot'], ['cursor', 'Cursor', 'Cursor'], ['trae', 'Trae', 'Trae'], ['claude', 'Claude Code', 'Claude Code'], ['codex', 'Codex', 'Codex'], ['workbuddy', 'WorkBuddy', 'WorkBuddy']].forEach(([k, n, ph], i) => {
    const cell = mk(L, 'abs', { left: RX + (i % 3) * 290, top: 200 + Math.floor(i / 3) * 190, width: 270, height: 180, textAlign: 'center' });
    appIcon(cell, k, 110, { margin: '0 auto' });
    mk(cell, '', { marginTop: 10, font: "700 28px 'Noto Sans SC'", color: 'var(--ink2)' }, n);
    sh(cell, tm.at('P04', ph) - 0.1, { scale: 0.85 });
  });
  const tI = tm.at('P04', 'IDE、CLI');
  const q = H.text({ text: 'IDE？ CLI？', x: RX, y: 640, size: 86, at: tI, until: tI + 1.3, parent: L });
  H.mark(q, 0, 3, { kind: 'circle', parent: L }); H.mark(q, 5, 8, { kind: 'circle', parent: L, at: q.t1 + 0.35 });
  const tS = tm.at('P04', '远程 SSH');
  H.text({ text: 'SSH 连服务器跑实验，用哪个？', x: RX, y: 770, size: 44, at: tS, until: wwin(tS, 'SSH连服务器跑实验用哪个', null, 2.6), parent: L });
  return { H, update(lv) { sh.run(lv); } };
};

// ---- S04 我的结论（A）
S.conclusion = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows();
  const L = layer(root);
  sh(bKick(L, RX, 200, '我的结论'), 0.1);
  const t0 = tm.at('P05', '写代码的主工作台');
  H.text({ text: '写代码的主工作台', x: RX, y: 300, size: 62, at: t0, until: t0 + 1.8, parent: L });
  const tA = tm.at('P05', '已经从'), tB = tm.at('P05', '换成了');
  const ed = H.text({ text: '代码编辑器', x: RX, y: 450, size: 66, at: tA, until: tA + 1.1, color: '#7E7A72', parent: L });
  H.line({ x0: ed.x0 - 10, y0: 452, x1: ed.x1 + 14, y1: 440, at: tB, dur: 0.3, color: H.RED, w: 8, parent: L });
  H.arrow({ x0: RX + 120, y0: 510, x1: RX + 120, y1: 590, at: tB + 0.2, dur: 0.3, parent: L });
  const ag = H.text({ text: '智能体', x: RX, y: 680, size: 116, at: tB + 0.4, until: tB + 1.4, parent: L });
  H.underline({ x0: ag.x0, x1: ag.x1 + 10, y: ag.y1 + 18, at: ag.t1 + 0.05, parent: L });
  return { H, update(lv) { sh.run(lv); } };
};

// ---- S05 两个词：IDE / CLI（B，不显示目录；左下放手写名词卡）
S.terms = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows();
  const t7 = tm.p0('P07'), t8 = tm.p0('P08'), t9 = tm.p0('P09');
  const f6 = flipOf(tm, 'P06'), f7 = flipOf(tm, 'P07'), f8 = flipOf(tm, 'P08');
  const L = layer(root);
  hTitle(H, L, 'IDE 和 CLI', { x: BX, y: 96, size: 60, at: 0.2, kicker: '先认识两个词', sh });
  // IDE 窗口、终端（示意，贴胶带）
  const ide = win(L, SX, 210, 730, 420, 'main.py — 编辑器', true);
  tape(ide.el, 0);
  ide.body.innerHTML = `<div class="ide">
    <div class="side"><div class="st">资源管理器</div><div>▾ project</div><div class="on">&nbsp;&nbsp;main.py</div><div>&nbsp;&nbsp;utils.py</div><div>&nbsp;&nbsp;data.csv</div></div>
    <div class="ed"><div class="tabs"><span class="on">main.py</span><span>utils.py</span></div>
      <pre><span class="c"># 读取实验数据</span>
<span class="k">import</span> pandas <span class="k">as</span> pd

<span class="k">def</span> <span class="f">load</span>(path):
    df = pd.read_csv(path)
    <span class="k">return</span> df.dropna()</pre>
      <div class="panel">终端 · 问题 · 调试控制台</div></div></div>`;
  const aiIde = mk(ide.body, 'abs', { right: 0, top: 0, width: 230, bottom: 0, background: '#25262B', borderLeft: '1px solid #3A3B40', padding: '14px 14px', font: "600 19px/1.5 'Noto Sans SC'", color: '#C9CDD4' },
    `<div style="color:#FDBA74;font-weight:800">AI 助手</div><div class="bub ai" style="font-size:18px;margin-top:10px">这段代码读取 CSV，再去掉空值……</div>`);
  const cli = win(L, SX + 772, 210, 730, 420, 'Terminal', true);
  tape(cli.el, 1);
  cli.body.classList.add('term');
  sh(ide.el, tm.at('P06', 'IDE'), { scale: 0.97 }); sh(cli.el, t7, { scale: 0.97 }); sh(aiIde, t9 + 0.3, { dx: 30, dy: 0 });
  const tI = tm.at('P06', '集成开发环境');
  H.text({ text: 'IDE：集成开发环境', x: SX, y: 690, size: 44, at: tI, until: tI + 1.8, parent: L });
  sh(bNote(L, SX, 726, 'Integrated Development Environment'), tI + 0.5);
  const tC = tm.at('P07', '命令行界面');
  H.text({ text: 'CLI：命令行界面', x: SX + 772, y: 690, size: 44, at: tC, until: tC + 1.6, parent: L });
  sh(bNote(L, SX + 772, 726, 'Command-Line Interface'), tC + 0.5);
  const ex = sh(mk(L, 'abs', { left: SX, top: 780, width: 730, height: 70, display: 'flex', alignItems: 'center', gap: '14px' }), tm.at('P06', 'VS Code、Cursor'));
  appIcon(ex, 'vscode', 56); appIcon(ex, 'cursor', 56); appIcon(ex, 'trae', 56); mk(ex, 'bNote', { position: 'static' }, 'VS Code · Cursor · Trae');
  const tS = tm.at('P07', '平时用的');
  sh(bNote(L, SX + 772, 796, 'git、ssh 都是命令行工具', { fontSize: 26 }), tS);
  const lines = [[t7 + 0.5, 'git status', 'cmd', 14], [t7 + 1.5, 'On branch main'], [t7 + 1.7, 'Changes not staged: <span class="err">modified: main.py</span>'],
    [tS, 'ssh lab-server', 'cmd', 14], [tS + 1.2, 'Welcome to Ubuntu 24.04 LTS', 'dim'], [tS + 1.5, 'user@lab-server:~$', 'ok']];
  const aiCli = [[t9 + 0.6, '帮我把 load() 改成支持 Excel', 'in', 22], [t9 + 2.4, '<span class="ai">● AI 正在改 main.py …</span>']];
  // 左下：手写名词卡（贴在白板上的卡片），一个词一页
  const card = sh(mk(L, 'abs wcard', { left: 60, top: 500, width: 672, height: 380 }), 0.6);
  tape(card, 2);
  const defs = [[0.8, f6.out, ['IDE：图形界面里', '写代码、调试、看改动']], [f6.in, f7.out, ['CLI：没有按钮，', '敲命令，回你文字']],
    [f7.in, f8.out, ['Agent：自己读文件、', '改代码、跑命令的 AI']], [f8.in, null, ['AI 编程工具：', '住在 IDE 或 CLI 里']]];
  defs.forEach(([a, b, ls]) => {
    const P = page(root, sh, a, b);
    ls.forEach((x, j) => H.text({ text: x, x: 100, y: 590 + j * 90, size: 46, at: a + 0.1 + j * 0.9, until: wwin(a + 0.1 + j * 0.9, x, null, 1.6), parent: P, maxW: 600 }));
  });
  return { H, update(lv) { sh.run(lv); termRender(cli.body, lv >= t9 ? lines.concat(aiCli) : lines, lv, 11); } };
};

// ---- S06 这期怎么讲（A）
S.roadmap = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), tJ = tm.at('P10', '想直接看怎么用的');
  const L = layer(root);
  sh(bKick(L, RX, 150, '这期怎么讲'), 0.1);
  H.text({ text: '第一章：AI 写代码这五年', x: RX, y: 250, size: 50, at: 0.2, until: 2.2, parent: L });
  sh(bNote(L, RX, 296, '补全、聊天 → 编辑器里的智能体 → 终端 → loop → 桌面工作台 → 走出编辑器', { fontSize: 22, whiteSpace: 'normal', width: 860 }), 1.2);
  const c2 = H.text({ text: '第二章：Claude Code 桌面版', x: RX, y: 450, size: 50, at: 2.2, until: 4.3, parent: L });
  sh(bNote(L, RX, 496, '会话、diff、终端、权限、SSH、定时任务……', { fontSize: 22 }), 3.4);
  H.text({ text: '想直接看怎么用：', x: RX, y: 660, size: 50, color: H.ACCENT, at: tJ, until: tJ + 1.6, parent: L });
  H.arrow({ x0: RX + 430, y0: 630, x1: RX + 330, y1: 520, at: tJ + 1.7, dur: 0.35, color: H.ACCENT, parent: L });
  H.ellipse({ x0: c2.x0, y0: c2.y0, x1: c2.box(0, 3)[2], y1: c2.y1, at: tJ + 2.0, parent: L });
  return { H, update(lv) { sh.run(lv); } };
};

// ======================================================================= 第一章 第 1 节：补全和聊天（S07）
S.sec1 = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), T = pid => tm.p0(pid);
  const tl = hTimeline(H, layer(root), [
    { d: '2021.06', ic: ['copilot'], t1: 'Copilot 预览', t2: '在 VS Code 里补全', at: 0.4 },
    { d: '2022.06', ic: ['copilot'], t1: '正式上线', at: tm.at('P11', '第二年正式上线') },
    { d: '2022.11', ic: ['chatgpt'], t1: 'ChatGPT 发布', t2: '开始“复制粘贴”', at: T('P12') },
    { d: '2023.12', ic: ['copilot'], t1: 'Copilot Chat', t2: '聊天进了侧边栏', at: T('P14') },
  ]);
  const f11 = flipOf(tm, 'P11'), f12 = flipOf(tm, 'P12'), f13 = flipOf(tm, 'P13'), f14 = flipOf(tm, 'P14');
  // P11 补全：编辑器里的灰色建议
  const L1 = page(root, sh, 0.5, f11.out);
  const ed = win(L1, SX, 360, 1000, 470, 'fib.py — VS Code', true); tape(ed.el, 0);
  const code = mk(ed.body, 'abs', { left: 0, top: 0, right: 0, bottom: 0, padding: '22px 30px', font: "500 30px/1.6 'JetBrains Mono','Noto Sans SC'", color: '#D4D4D4', whiteSpace: 'pre' });
  const TYPED = 'def fibonacci(n):\n    """返回第 n 个斐波那契数"""\n';
  const GHOST = '    if n < 2:\n        return n\n    a, b = 0, 1\n    for _ in range(n - 1):\n        a, b = b, a + b\n    return b';
  const tg = tm.at('P11', '补一行'), tf = tm.at('P11', '或者补一整个函数'), tt = tm.at('P11', '你敲代码');
  H.text({ text: '补一行', x: SX + 1080, y: 470, size: 52, at: tg, until: tg + 0.9, parent: L1 });
  H.arrow({ x0: SX + 1070, y0: 480, x1: SX + 640, y1: 520, at: tg + 0.9, dur: 0.3, parent: L1 });
  const fw = H.text({ text: '补一整个函数', x: SX + 1080, y: 640, size: 52, at: tf, until: tf + 1.6, parent: L1 });
  H.underline({ x0: fw.x0, x1: fw.x1 + 8, y: fw.y1 + 14, at: fw.t1 + 0.05, parent: L1 });
  sh(bNote(L1, SX + 1080, 720, '按 Tab 接受'), tf + 1.5);
  // P12 复制粘贴
  const L2 = page(root, sh, f11.in, f12.out);
  const chat = win(L2, SX, 360, 600, 440, 'ChatGPT', false); tape(chat.el, 1);
  const chatB = mk(chat.body, 'chatb');
  const vsc = win(L2, SX + 902, 360, 600, 440, 'VS Code', true); tape(vsc.el, 2);
  vsc.body.classList.add('term');
  const tC = bg(tm.at('P12', '在聊天框里要代码'), f11.in), tP = tm.at('P12', '粘贴到 VS Code'), tE = tm.at('P12', '报错了'), tCp = bg(tm.at('P12', '复制'), f11.in);
  H.text({ text: '复制', x: SX + 751, y: 440, size: 44, align: 'center', at: tCp, until: tCp + 0.6, parent: L2 });
  H.arrow({ x0: SX + 640, y0: 490, x1: SX + 870, y1: 490, at: tCp + 0.6, dur: 0.3, parent: L2 });
  H.text({ text: '报错', x: SX + 751, y: 640, size: 44, align: 'center', color: H.RED, at: tE + 0.3, until: tE + 0.9, parent: L2 });
  H.arrow({ x0: SX + 870, y0: 690, x1: SX + 640, y1: 690, at: tE + 0.9, dur: 0.3, color: H.RED, parent: L2 });
  sh(bNote(L2, SX, 820, '网页 · App · 手机：都一样'), tm.at('P12', '网页、App'));
  const tV = tm.at('P12', 'CV 工程师');
  const cv = H.text({ text: 'CV 工程师', x: SX + 1200, y: 850, size: 58, align: 'center', at: tV, until: tV + 1.2, parent: L2 });
  H.mark(cv, 0, 6, { kind: 'circle', parent: L2 });
  // P13 以前抄 SO / CSDN；月提问量（示意，手画）
  const L3 = page(root, sh, f12.in, f13.out);
  const t13 = bg(T('P13'), f12.in), tNow = bg(tm.at('P13', '只是换了个地方抄'), f12.in);
  const oi = sh(mk(L3, 'abs', { left: SX, top: 360, display: 'flex', gap: '12px' }), t13); appIcon(oi, 'csdn', 64); appIcon(oi, 'so', 64);
  H.text({ text: '以前：搜、抄、跑', x: SX, y: 480, size: 46, at: t13, until: t13 + 1.6, parent: L3 });
  const ni = sh(mk(L3, 'abs', { left: SX, top: 560, display: 'flex', gap: '12px' }), tNow); appIcon(ni, 'chatgpt', 64);
  const sw = H.text({ text: '现在：换个地方抄', x: SX, y: 680, size: 46, at: tNow, until: tNow + 1.6, parent: L3 });
  H.mark(sw, 3, 8, { kind: 'underline', parent: L3 });
  const cx0 = SX + 600, cy0 = 420, cw = 860, chH = 330, yr = y => (y - 2008.5) / (2025.5 - 2008.5);
  const tD = bg(tm.at('P13', '数据上也看得出来'), f12.in);
  H.text({ text: 'Stack Overflow 每月新提问', x: cx0, y: 380, size: 34, at: tD, until: tD + 1.4, parent: L3 });
  sh(bNote(L3, cx0 + 640, 364, '（示意）'), tD);
  H.line({ x0: cx0, y0: cy0 + chH, x1: cx0 + cw, y1: cy0 + chH, at: tD, dur: 0.4, color: '#9AA1AC', w: 4, parent: L3 });
  H.line({ x0: cx0, y0: cy0 + chH, x1: cx0, y1: cy0 + 20, at: tD, dur: 0.3, color: '#9AA1AC', w: 4, parent: L3 });
  const SO = [[2008.6, .02], [2009.4, .12], [2010, .3], [2011, .5], [2012, .68], [2013, .85], [2014.2, 1], [2015, .97], [2016, .95], [2017, .92], [2018, .83], [2019, .75], [2020.3, .8], [2021, .7], [2022, .6], [2022.9, .55], [2023.3, .38], [2024, .24], [2024.8, .17], [2025.4, .12]];
  H.curve(SO.map(([y, v]) => [cx0 + yr(y) * cw, cy0 + chH - v * (chH - 40)]), { at: tD + 0.4, dur: 2.2, color: H.ACCENT, w: 7, parent: L3 });
  [2009, 2014, 2019, 2025].forEach(y => sh(bNote(L3, cx0 + yr(y) * cw - 30, cy0 + chH + 8, String(y), { fontSize: 22 }), tD + 0.4));
  H.text({ text: '2014 见顶', x: cx0 + yr(2014.2) * cw, y: cy0 + 8, size: 30, align: 'center', at: tD + 1.2, until: tD + 2.0, parent: L3 });
  const tG = bg(tm.at('P13', '在 ChatGPT 出来后'), f12.in);
  H.line({ x0: cx0 + yr(2022.9) * cw, y0: cy0 + 40, x1: cx0 + yr(2022.9) * cw, y1: cy0 + chH, at: tG, dur: 0.3, color: '#10A37F', w: 4, parent: L3 });
  H.text({ text: 'ChatGPT', x: cx0 + yr(2022.9) * cw - 14, y: cy0 + 200, size: 30, align: 'right', color: '#0E8A6C', at: tG + 0.3, until: tG + 1.0, parent: L3 });
  const tL = bg(tm.at('P13', '到 2025 年 5 月'), f12.in), ly = cy0 + chH - 0.12 * (chH - 40);
  H.line({ x0: cx0 + yr(2009.4) * cw, y0: ly, x1: cx0 + yr(2025.4) * cw, y1: ly, at: tL, dur: 0.6, color: H.ACCENT, w: 3, parent: L3 });
  H.text({ text: '2025.05 跌回 2009 年水平', x: cx0 + yr(2011) * cw, y: ly - 32, size: 28, color: H.ACCENT, at: tL + 0.3, until: tL + 1.8, parent: L3 });
  sh(srcNote(L3, '来源：The Pragmatic Engineer《Stack overflow is almost dead》2025-05-15（Stack Exchange Data Explorer）；曲线按文中走势示意'), t13);
  // P14 Copilot Chat
  const L4 = page(root, sh, f13.in, f14.out);
  const vs = win(L4, SX, 360, 1100, 420, 'VS Code', true); tape(vs.el, 3);
  vs.body.innerHTML = `<div class="ide"><div class="side"><div class="st">资源管理器</div><div class="on">&nbsp;&nbsp;train.py</div><div>&nbsp;&nbsp;model.py</div><div>&nbsp;&nbsp;config.yaml</div></div>
    <div class="ed"><div class="tabs"><span class="on">train.py</span></div><pre><span class="k">for</span> epoch <span class="k">in</span> range(cfg.epochs):
    loss = model(batch).mean()
    loss.backward()
    opt.step()</pre></div></div>`;
  const side = mk(vs.body, 'abs', { right: 0, top: 0, bottom: 0, width: 440, background: '#25262B', borderLeft: '1px solid #3A3B40', padding: '16px 18px' });
  mk(side, '', { font: "800 22px 'Space Grotesk','Noto Sans SC'", color: '#C9CDD4', letterSpacing: '2px' }, 'COPILOT CHAT');
  const sideB = mk(side, 'chatb', { top: 50 });
  const t14 = bg(T('P14'), f13.in), tq = bg(tm.at('P14', '能问'), f13.in);
  [['能问', 'ok', tq], ['能解释代码', 'ok', bg(tm.at('P14', '能解释代码'), f13.in)], ['改文件', 'x', tm.at('P14', '但还不能')], ['跑命令', 'x', tm.at('P14', '跑命令')]].forEach(([t, k, at], i) => {
    const y = 420 + i * 100;
    if (k === 'ok') H.check({ x: SX + 1170, y, size: 40, at, parent: L4 }); else H.cross({ x: SX + 1170, y, size: 34, at, parent: L4 });
    H.text({ text: t, x: SX + 1210, y, size: 44, at: at + 0.2, until: at + 1.0, parent: L4 });
  });
  sh(srcNote(L4, '来源：GitHub 博客 2021-06-29；TechCrunch 2022-06-21；OpenAI 2022-11-30；TechCrunch 2023-12-29'), t14);
  // P15 这一阶段：人是主角
  const L5 = page(root, sh, f14.in, null);
  const t15 = bg(T('P15'), f14.in);
  H.html('人是<span class="or">主角</span>', { x: BX, y: 500, size: 80, align: 'center', at: t15, until: t15 + 1.2, parent: L5 });
  const t15b = bg(tm.at('P15', 'AI 是一个'), t15 + 1.2);
  H.html('AI 是更聪明的<span class="or">聊天框</span>', { x: BX, y: 660, size: 70, align: 'center', at: t15b, until: t15b + 2.0, parent: L5 });
  return {
    H,
    update(lv) {
      sh.run(lv); tl.update(lv);
      const k = Math.floor(clamp((lv - tt + 1.5) / 2.0) * TYPED.length), acc = lv > tf + 1.2, gShow = lv > tg - 0.3;
      code.innerHTML = `<span style="color:#D4D4D4">${esc(TYPED.slice(0, k))}</span>` + (gShow ? `<span style="color:${acc ? '#D4D4D4' : '#6B7280'};font-style:${acc ? 'normal' : 'italic'}">${esc(GHOST.slice(0, acc ? GHOST.length : Math.floor(clamp((lv - tg + 0.3) / 0.6) * GHOST.length)))}</span>` : '') + (k < TYPED.length || !acc ? '<span class="caret" style="width:3px"></span>' : '');
      chatRender(chatB, [[tC, 'me', '帮我写一个读取 CSV 的函数'], [tC + 0.9, 'ai', '<pre style="margin:0;font:500 20px/1.5 \'JetBrains Mono\'">def load(path):\n    return pd.read_csv(path)</pre>'],
        [tE + 1.0, 'me', '<span style="font-family:JetBrains Mono;font-size:20px">NameError: name \'pd\' is not defined</span>'], [tE + 1.9, 'ai', '抱歉，需要先 import pandas as pd ……']], lv);
      termRender(vsc.body, [[tP, 'def load(path):'], [tP + 0.1, '    return pd.read_csv(path)'], [tP + 0.8, 'python load.py', 'cmd', 16], [tE, 'NameError: name \'pd\' is not defined', 'err']], lv);
      chatRender(sideB, [[tq, 'me', '这段代码是做什么的？'], [bg(tm.at('P14', '能解释代码'), f13.in), 'ai', '这是训练循环：每个 epoch 算一次损失、反向传播、更新参数……']], lv);
    },
  };
};

// ======================================================================= 第 2 节（上）：编辑器里的智能体（S08）
S.sec2a = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), T = pid => tm.p0(pid);
  const tl = hTimeline(H, layer(root), [
    { d: '2024.11', ic: ['windsurf'], t1: 'Windsurf', t2: '自称第一个“智能体 IDE”', at: tm.at('P17', 'Windsurf 发布') },
    { d: '2024.11', ic: ['cursor'], t1: 'Cursor Agent', at: tm.at('P17', 'Cursor 上线') },
    { d: '2024.11', ic: ['copilot'], t1: '多文件编辑', t2: 'VS Code 的 Copilot', at: tm.at('P17', 'VS Code 的 Copilot') },
    { d: '2025.01', ic: ['trae'], t1: '字节发布 Trae', t2: '国际版免费 · Claude 3.5 Sonnet', at: T('P18') },
    { d: '2025.02', ic: ['copilot'], t1: 'Copilot Agent', at: tm.at('P18', '2 月') },
  ]);
  const f16 = flipOf(tm, 'P16'), f18 = flipOf(tm, 'P18');
  // P16 大字
  const L0 = page(root, sh, 0.2, f16.out);
  H.html('2024 年底：AI 能<span class="or">自己动手</span>了', { x: BX, y: 460, size: 70, align: 'center', at: 0.3, until: 2.8, parent: L0 });
  ['读文件', '改多个文件', '跑终端命令', '看报错再改'].forEach((t, i) => {
    H.dash({ x: SX + 60 + i * 370, y: 640, len: 30, at: 1.5 + i * 0.35, parent: L0 });
    H.text({ text: t, x: SX + 105 + i * 370, y: 640, size: 42, at: 1.6 + i * 0.35, until: 2.4 + i * 0.35, parent: L0 });
  });
  // P17–18 编辑器里的智能体（示意）
  const L1 = page(root, sh, f16.in, f18.out);
  const ide = win(L1, SX, 360, 1502, 480, 'app.py — 编辑器 + 智能体（示意）', true); tape(ide.el, 0);
  ide.body.innerHTML = `<div class="ide"><div class="side"><div class="st">资源管理器</div><div class="on">&nbsp;&nbsp;app.py</div><div>&nbsp;&nbsp;utils.py</div><div>&nbsp;&nbsp;tests/</div></div>
    <div class="ed"><div class="tabs"><span class="on">app.py</span><span>utils.py</span></div><pre><span class="k">def</span> <span class="f">login</span>(user, pwd):
    row = db.find_user(user)
    <span class="dif">+   if row is None:</span>
    <span class="dif">+       return error("用户不存在")</span>
    <span class="k">return</span> check(row, pwd)</pre></div></div>`;
  const ag = mk(ide.body, 'abs', { right: 0, top: 0, bottom: 0, width: 560, background: '#25262B', borderLeft: '1px solid #3A3B40', padding: '16px 20px' });
  mk(ag, '', { font: "800 22px 'Space Grotesk','Noto Sans SC'", color: '#FDBA74', letterSpacing: '2px' }, 'AGENT');
  const agB = mk(ag, 'term', { position: 'relative', padding: '10px 0 0', fontSize: 22 });
  const t17 = bg(T('P17'), f16.in);
  sh(srcNote(L1, '来源：Windsurf 发布帖 2024-11-13；Cursor 0.43 更新日志 2024-11-24；VS Code 博客 2024-11-12、2025-02-24；Visual Studio Magazine 2025-01-27；AIbase 2025-01'), t17);
  // P19 VS Code 分叉 + TraeCode 录屏
  const L2 = page(root, sh, f18.in, null);
  const t19 = bg(T('P19'), f18.in);
  const vsI = sh(mk(L2, 'abs', { left: SX + 200, top: 330, width: 120, height: 120 }), t19); appIcon(vsI, 'vscode', 120);
  H.text({ text: 'VS Code', x: SX + 260, y: 482, size: 36, align: 'center', at: t19 + 0.2, until: t19 + 0.9, parent: L2 });
  H.line({ x0: SX + 260, y0: 510, x1: SX + 260, y1: 548, at: t19 + 0.6, dur: 0.2, parent: L2 });
  H.line({ x0: SX + 80, y0: 548, x1: SX + 440, y1: 548, at: t19 + 0.8, dur: 0.3, parent: L2 });
  [['cursor', 'Cursor', 80, 'Cursor'], ['windsurf', 'Windsurf', 260, 'Windsurf'], ['trae', 'Trae', 440, 'Trae 都是']].forEach(([k, n, x, ph]) => {
    const at = bg(tm.at('P19', ph), t19 + 1.0);
    H.arrow({ x0: SX + x, y0: 548, x1: SX + x, y1: 596, at, dur: 0.25, parent: L2 });
    const ic = sh(mk(L2, 'abs', { left: SX + x - 45, top: 604, width: 90, height: 90 }), at + 0.2, { scale: 0.8 }); appIcon(ic, k, 90);
    H.text({ text: n, x: SX + x, y: 726, size: 32, align: 'center', at: at + 0.3, until: at + 1.0, parent: L2 });
  });
  const tCap = bg(tm.at('P19', '都是从 VS Code'), t19 + 1.2);
  H.html('都从 VS Code <span class="or">改出来</span>', { x: SX + 260, y: 805, size: 44, align: 'center', at: tCap, until: tCap + 1.8, parent: L2 });
  const rp = recPlayer(L2, 'sec2a', SX + 570, 350, 932, 537);
  tape(rp.fb.f, 1);
  frameLab(rp.fb.inner, 'TraeCode · 今天的 Trae IDE（录屏）');
  sh(rp.fb.f, t19, { scale: 0.97 });
  rp.plan(tm, t19, s.end - s.start + LEAD - 0.3);
  sh(srcNote(L2, '来源：Cursor 文档《VS Code Migration》；Maginative 2024-11-13；Visual Studio Magazine 2025-01-27'), t19);
  return {
    H,
    update(lv) {
      sh.run(lv); tl.update(lv); rp.update(lv);
      termRender(agB, [[t17 + 0.6, '<span class="ok">✓</span> 读取 app.py、utils.py、tests/'], [t17 + 2.0, '<span class="ai">✎</span> 修改 app.py（+2）'], [t17 + 3.4, '<span class="ai">▶</span> 运行 pytest'],
        [t17 + 4.6, '<span class="err">✗ 1 个测试失败</span>'], [t17 + 5.8, '<span class="ai">✎</span> 再改 app.py'], [t17 + 7.0, '<span class="ai">▶</span> 运行 pytest'], [t17 + 8.2, '<span class="ok">✓ 全部通过</span>']], lv);
    },
  };
};

// ======================================================================= 第 2 节（中）：写好需求文档，让 AI 一次做完（S09）
S.sec2b = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), T = pid => tm.p0(pid);
  const L = layer(root);
  hTitle(H, L, '写好需求文档，让 AI 一次做完', { x: BX, y: 96, size: 56, at: 0.2, kicker: '2025.07', sh });
  const f20 = flipOf(tm, 'P20'), f21 = flipOf(tm, 'P21'), f22 = flipOf(tm, 'P22');
  // P20
  const L0 = page(root, sh, 0.3, f20.out);
  H.node({ x: SX + 160, y: 380, w: 320, h: 200, text: '需求文档', size: 56, at: 1.2, parent: L0 });
  H.arrow({ x0: SX + 520, y0: 480, x1: SX + 740, y1: 480, at: 2.8, dur: 0.35, parent: L0 });
  H.html('AI <span class="or">一次做完</span>', { x: SX + 790, y: 480, size: 76, at: 3.2, until: 4.6, parent: L0 });
  sh(bNote(L0, SX + 160, 640, '不想再一轮一轮地指挥 AI'), 2.0);
  // P21 SOLO + 我的使用记录
  const L1 = page(root, sh, f20.in, f21.out);
  const t21 = bg(T('P21'), f20.in);
  const si = sh(mk(L1, 'abs', { left: SX, top: 250, width: 96, height: 96 }), t21); appIcon(si, 'traework', 96);
  H.text({ text: 'Trae SOLO', x: SX + 120, y: 300, size: 54, at: t21, until: t21 + 1.2, parent: L1 });
  sh(bNote(L1, SX, 370, '2025 年 7 月预览 · 国际版 Pro'), t21 + 0.4);
  const tInv = bg(tm.at('P21', '要邀请码'), t21 + 1.0);
  const inv = H.text({ text: '要邀请码', x: SX, y: 470, size: 54, at: tInv, until: tInv + 1.2, parent: L1 });
  H.mark(inv, 0, 4, { kind: 'circle', parent: L1 });
  const tMe = tm.at('P21', '我当时拿到了资格');
  H.text({ text: '我拿到了资格', x: SX, y: 620, size: 56, color: H.ACCENT, at: tMe, until: tMe + 1.6, parent: L1 });
  const hm = frameBox(L1, SX + 520, 250, 982, 470, false); tape(hm.f, 0);
  hm.inner.style.background = '#1E1F22';
  image(hm.inner, 'media/trae_heatmap.png', { position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', objectFit: 'contain' });
  sh(hm.f, tMe + 0.3, { scale: 0.96 });
  sh(bNote(L1, SX + 520, 740, '悠一的 TraeCode 使用记录：第 435 天'), tMe + 0.6);
  // P22 PRD → 拆任务 → 写代码 → 跑起来 + SOLO 录屏
  const L2 = page(root, sh, f21.in, f22.out);
  const t22 = bg(T('P22'), f21.in);
  [['PRD', t22], ['拆任务', tm.at('P22', 'AI 自己拆任务')], ['写代码', tm.at('P22', '写代码')], ['跑起来', tm.at('P22', '跑起来')]].forEach(([t, at], i) => {
    const a2 = bg(at, t22 + i * 0.9);
    H.node({ x: SX, y: 220 + i * 160, w: 330, h: 110, text: t, size: 46, at: a2, write: a2 + 0.8, parent: L2 });
    if (i) H.arrow({ x0: SX + 165, y0: 220 + i * 160 - 45, x1: SX + 165, y1: 220 + i * 160 - 5, at: a2 - 0.15, dur: 0.2, parent: L2 });
  });
  sh(bNote(L2, SX, 184, 'PRD = 产品需求文档'), t22 + 0.6);
  const rp = recPlayer(L2, 'sec2b', SX + 400, 230, 1102, 620);
  tape(rp.fb.f, 1);
  frameLab(rp.fb.inner, 'TraeCode 里切到 SOLO 模式（录屏）');
  sh(rp.fb.f, t22, { scale: 0.97 });
  rp.plan(tm, t22, f22.out);
  // P23 Kiro 规格驱动
  const L3 = page(root, sh, f22.in, null);
  const t23 = bg(T('P23'), f22.in);
  const ki = sh(mk(L3, 'abs', { left: SX + 60, top: 280, width: 100, height: 100 }), t23); appIcon(ki, 'kiro', 100);
  H.html('亚马逊 Kiro：<span class="or">规格驱动开发</span>', { x: SX + 190, y: 330, size: 58, at: t23, until: bg(tm.at('P23', '先出需求') - 0.1, t23 + 1.0), parent: L3 });
  [['需求', '先出需求'], ['设计', '设计'], ['任务清单', '任务清单'], ['写代码', '再写代码']].forEach(([t, ph], i) => {
    const at = bg(tm.at('P23', ph), t23 + 0.6 + i * 0.5);
    H.node({ x: SX + 30 + i * 370, y: 480, w: 300, h: 130, text: t, size: 48, at, write: at + 0.9, parent: L3 });
    if (i) H.arrow({ x0: SX + 30 + i * 370 - 64, y0: 545, x1: SX + 30 + i * 370 - 12, y1: 545, at: at - 0.2, dur: 0.2, parent: L3 });
  });
  sh(srcNote(L, '来源：AIbase《Trae 2.0 Officially Upgraded with SOLO Mode》2025-07-22；Kiro 官方博客 2025-07-14；使用记录为悠一本人截图'), 0.5);
  return { H, update(lv) { sh.run(lv); rp.update(lv); } };
};

// ======================================================================= 第 2 节（下）：自主性强了，但一次做太多会跑偏；上下文腐烂（S10）
S.sec2c = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), T = pid => tm.p0(pid);
  const f24 = flipOf(tm, 'P24'), f25 = flipOf(tm, 'P25');
  // P24
  const L0 = page(root, sh, 0, f24.out);
  hTitle(H, L0, '自主性一下子强了很多', { x: BX, y: 96, size: 58, at: 0.2, kicker: '体感', sh });
  hPoint(H, L0, 1, '不用每一轮都告诉它', SX + 120, 380, { size: 56, at: tm.at('P24', '人不用每一轮') });
  hPoint(H, L0, 2, '定好文档，<span class="or">一口气做完</span>', SX + 120, 530, { size: 56, at: tm.at('P24', '定好一份文档') });
  // P25 越做越偏
  const L1 = page(root, sh, f24.in, f25.out);
  const t25 = bg(T('P25'), f24.in);
  hTitle(H, L1, '一次做太多，越做越偏', { x: BX, y: 96, size: 58, at: t25, sh });
  const tx = SX + 1330, ty = 380;
  H.ellipse({ x0: tx - 60, y0: ty - 60, x1: tx + 60, y1: ty + 60, at: t25 + 0.6, color: H.ACCENT, w: 10, padX: 0, padY: 0, parent: L1 });
  H.line({ x0: tx - 1, y0: ty, x1: tx + 1, y1: ty, at: t25 + 0.9, dur: 0.06, color: H.ACCENT, w: 40, parent: L1 });
  H.text({ text: 'PRD 的目标', x: tx, y: ty + 120, size: 38, align: 'center', at: t25 + 1.0, until: t25 + 2.0, parent: L1 });
  H.line({ x0: SX + 40, y0: ty, x1: tx - 90, y1: ty, at: t25 + 1.2, dur: 0.6, color: '#B8BDC6', w: 4, parent: L1 });
  sh(bNote(L1, SX + 40, ty - 50, '应该这样走'), t25 + 1.4);
  const tD = bg(tm.at('P25', '一次做太多'), t25 + 1.5);
  const PTS = [[0, 0], [.2, 0], [.4, .02], [.55, .08], [.7, .2], [.82, .36], [.92, .52], [1, .62]].map(([u, d]) => [SX + 40 + u * (tx - 160 - SX - 40), ty + d * 400]);
  H.curve(PTS, { at: tD, dur: 2.2, color: H.RED, w: 8, parent: L1 });
  const d1 = bg(tm.at('P25', '刹不住车'), tD + 1.0);
  H.html('刹不住车，<span class="or">越做越偏</span>', { x: SX + 300, y: 800, size: 50, at: d1, until: d1 + 2.2, parent: L1 });
  // P26 20 万 → 100 万；上下文腐烂
  const L2 = page(root, sh, f25.in, null);
  const t26 = bg(T('P26'), f25.in);
  hTitle(H, L2, '任务一长就乱', { x: BX, y: 96, size: 58, at: t26, sh });
  const b1 = bg(tm.at('P26', '20 万'), t26 + 1.0), b2 = bg(tm.at('P26', '100 万'), b1 + 1.4);
  H.text({ text: 'Claude 3', x: SX + 250, y: 250, size: 40, align: 'right', at: b1, until: b1 + 0.8, parent: L2 });
  H.line({ x0: SX + 290, y0: 250, x1: SX + 290 + 180, y1: 250, at: b1 + 0.4, dur: 0.4, color: '#B8BDC6', w: 34, parent: L2 });
  H.text({ text: '20 万', x: SX + 500, y: 250, size: 40, at: b1 + 0.8, until: b1 + 1.3, parent: L2 });
  H.text({ text: '现在', x: SX + 250, y: 330, size: 40, align: 'right', at: b2, until: b2 + 0.6, parent: L2 });
  H.line({ x0: SX + 290, y0: 330, x1: SX + 290 + 900, y1: 330, at: b2 + 0.3, dur: 0.8, color: H.ACCENT, w: 34, parent: L2 });
  H.text({ text: '100 万 token', x: SX + 1210, y: 330, size: 40, color: H.ACCENT, at: b2 + 1.0, until: b2 + 1.8, parent: L2 });
  const tR = tm.at('P26', '麻烦在于'), t7 = tm.at('P26', '2025 年 7 月');
  const gx = SX + 60, gy = 420, gw = 820, gh = 380;
  H.line({ x0: gx, y0: gy + gh, x1: gx + gw, y1: gy + gh, at: tR, dur: 0.4, color: '#9AA1AC', w: 4, parent: L2 });
  H.line({ x0: gx, y0: gy + gh, x1: gx, y1: gy + 10, at: tR, dur: 0.3, color: '#9AA1AC', w: 4, parent: L2 });
  sh(bNote(L2, gx + 10, gy + gh + 8, '输入越来越长 →', { fontSize: 22 }), tR);
  sh(bNote(L2, gx + 14, gy - 4, '表现', { fontSize: 22 }), tR);
  const R = [[0, .95], [.15, .93], [.3, .86], [.45, .8], [.55, .68], [.65, .7], [.75, .5], [.85, .52], [1, .3]].map(([u, v]) => [gx + 20 + u * (gw - 40), gy + gh - v * (gh - 30)]);
  H.curve(R, { at: t7, dur: 1.8, color: H.ACCENT, w: 7, parent: L2 });
  const tRot = tm.at('P26', '上下文腐烂');
  const rot = H.text({ text: '上下文腐烂', x: gx + gw + 80, y: 520, size: 60, at: tRot, until: tRot + 1.4, parent: L2 });
  H.mark(rot, 0, 5, { kind: 'circle', parent: L2 });
  const t18 = tm.at('P26', '18 个模型');
  H.text({ text: '18 个模型都这样', x: gx + gw + 80, y: 660, size: 44, at: t18, until: t18 + 1.6, parent: L2 });
  sh(bNote(L2, gx + gw + 80, 720, '输入越长，表现越不稳定（示意）'), t18 + 0.8);
  sh(srcNote(L2, '来源：Anthropic Claude 3 发布 2024-03-04；Claude 博客 1M context GA 2026-03-13；Chroma《Context Rot》2025-07-14（曲线示意）'), t26 + 0.4);
  return { H, update(lv) { sh.run(lv); } };
};

// ======================================================================= 第 3 节：终端里的智能体（S11）
S.sec3 = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows(), T = pid => tm.p0(pid);
  const tl = hTimeline(H, layer(root), [
    { d: '2025.02', ic: ['claude'], t1: 'Claude Code', t2: '研究预览', at: T('P28') },
    { d: '2025.04', ic: ['codex'], t1: 'Codex CLI', t2: '开源', at: T('P29') },
    { d: '2025.05', ic: ['claude'], t1: 'Claude Code', t2: '正式上线', at: tm.at('P28', '5 月正式上线') },
    { d: '2025.06', ic: ['gemini'], t1: 'Gemini CLI', at: tm.at('P29', 'Google 出了') },
    { d: '2025.08', ic: ['cursor'], t1: 'Cursor CLI', at: tm.at('P29', 'Cursor 也出了') },
  ]);
  const f29 = flipOf(tm, 'P29'), f31 = flipOf(tm, 'P31');
  // P27–29 终端智能体（示意）
  const L0 = page(root, sh, 0.3, f29.out);
  const tw = win(L0, SX, 380, 1100, 470, 'Terminal — ~/project（示意）', true); tape(tw.el, 0);
  tw.body.classList.add('term');
  const t1 = tm.at('P28', '在终端里说一句话');
  ['读代码', '改文件', '跑命令'].forEach((t, i) => {
    const at = tm.at('P28', ['它自己读代码', '改文件', '跑命令'][i]);
    H.check({ x: SX + 1170, y: 470 + i * 110, size: 40, at, parent: L0 });
    H.text({ text: t, x: SX + 1210, y: 470 + i * 110, size: 50, at: at + 0.2, until: at + 1.0, parent: L0 });
  });
  sh(srcNote(L0, '来源：Anthropic 2025-02-24、2025-05-22；Slashdot 2025-04-16；Google 博客 2025-06-25；Cursor 论坛 2025-08-07'), 0.8);
  // P30–31 喜欢 / 门槛
  const L1 = page(root, sh, f29.in, f31.out);
  const t30 = bg(T('P30'), f29.in), t31 = bg(T('P31'), f29.in);
  H.text({ text: '程序员很喜欢 CLI', x: SX, y: 400, size: 50, at: t30, until: t30 + 1.6, parent: L1 });
  ['看起来很极客', '敲命令比点界面快', '和 git、SSH、脚本接得上'].forEach((t, i) => {
    const at = bg(tm.at('P30', ['看起来很极客', '敲命令比点界面快', '和 git'][i]), t30 + 0.8 + i * 0.4);
    H.check({ x: SX + 20, y: 510 + i * 90, size: 36, at, parent: L1 });
    H.text({ text: t, x: SX + 60, y: 510 + i * 90, size: 40, at: at + 0.15, until: wwin(at + 0.15, t, null, 1.8), maxW: 640, parent: L1 });
  });
  H.text({ text: '门槛也在这', x: SX + 800, y: 400, size: 50, at: t31, until: t31 + 1.2, parent: L1 });
  [['各家命令不一样', '换一个就要重学'], ['没有界面', '看结果都得敲命令']].forEach(([a, b], i) => {
    const at = bg(tm.at('P31', ['各家命令不一样', '没有界面'][i]), t31 + 0.6 + i * 0.5);
    H.cross({ x: SX + 820, y: 510 + i * 170, size: 32, at, parent: L1 });
    H.text({ text: a, x: SX + 860, y: 510 + i * 170, size: 40, at: at + 0.15, until: at + 1.3, parent: L1 });
    H.text({ text: b, x: SX + 860, y: 570 + i * 170, size: 36, color: '#6E6A63', at: at + 1.3, until: at + 2.4, parent: L1 });
  });
  // P32 两个终端（示意）
  const L2 = page(root, sh, f31.in, null);
  const t32 = bg(T('P32'), f31.in);
  const tA = win(L2, SX, 380, 700, 380, 'Codex CLI', true), tB = win(L2, SX + 802, 380, 700, 380, 'Claude Code CLI', true);
  tape(tA.el, 1); tape(tB.el, 2);
  tA.body.classList.add('term'); tB.body.classList.add('term');
  const tq = bg(tm.at('P32', '发现有些命令不一样'), t32);
  H.html('命令不一样，<span class="or">经常打错</span>', { x: BX, y: 830, size: 50, align: 'center', at: tq, until: tq + 2.4, parent: L2 });
  const tTry = bg(tm.at('P32', '后来尝试了一下'), t32);
  return {
    H,
    update(lv) {
      sh.run(lv); tl.update(lv);
      termRender(tw.body, [[0.6, 'cd ~/project', 'cmd', 16], [1.6, 'claude', 'cmd', 12], [2.4, '<span class="dim">Claude Code（示意） · 在终端里说一句话就行</span>'],
        [t1, '登录页点了没反应，帮我修一下', 'in', 16], [t1 + 1.6, '<span class="ai">●</span> 读取 src/login.js、src/api.js'], [t1 + 2.8, '<span class="ai">●</span> 修改 src/login.js <span class="ok">+3</span> <span class="err">−1</span>'],
        [t1 + 4.0, '<span class="ai">●</span> 运行 npm test'], [t1 + 5.2, '<span class="ok">✓ 12 passed</span>'], [t1 + 6.0, '<span class="dim">已修复：按钮的点击事件没绑上。</span>']], lv, 12);
      termRender(tA.body, [[t32 + 0.4, 'codex', 'cmd', 12], [t32 + 1.2, '<span class="dim">› 输入 / 看命令</span>'], [t32 + 1.8, '/…', 'in', 6]], lv);
      termRender(tB.body, [[tTry, 'claude', 'cmd', 12], [tTry + 0.8, '<span class="dim">› 输入 / 看命令</span>'], [tq, '/…', 'in', 6], [tm.at('P32', '经常打错命令'), '<span class="err">✕ 命令打错了</span>']], lv);
    },
  };
};

// ---- S12 有句话我很认同（A）
S.quote = (root, s) => {
  const tm = timer(s), H = HAND.ctx(root, s.id, s.end - s.start + LEAD), sh = Shows();
  const L = layer(root);
  sh(bKick(L, RX, 150, '有句话我很认同'), 0.1);
  [['学得快的人，', '学得快的人'], ['会发现<span class="or">什么都要学</span>；', '会发现什么都要学'], ['学得慢的人，', '学得慢的人'], ['会发现很多<span class="or">不用学了</span>。', '会发现很多东西不用学了']].forEach(([t, ph], i) => {
    const at = tm.at('P33', ph);
    H.html(t, { x: RX, y: 260 + i * 110, size: 58, at, until: at + 1.6, parent: L });
  });
  const tA = tm.at('P33', '因为 AI');
  H.text({ text: 'AI 一直在降低门槛', x: RX, y: 720, size: 56, color: H.ACCENT, at: tA, until: tA + 2.0, parent: L });
  sh(bNote(L, RX, 780, 'CLI 的门槛怎么被抹平？第二章', { fontSize: 26 }), tm.at('P33', 'CLI 就是个例子'));
  return { H, update(lv) { sh.run(lv); } };
};
