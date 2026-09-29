/* scenes.js 的起点（新一期：复制成 制作/engine/scenes.js 再改写）。组件说明见 components.js 顶部，
 * 第 1 期的完整写法见 scenes.example.js。
 *
 * 原样运行时它是一份「分镜草稿」：开场大字、疑问卡飞进目录、每个讲解章节一个标题卡 + 按段出现的画面说明卡、
 * 最后一场总结卡 —— 全部由 timeline.json 和 episode 字段推出来，所以任何一期都能直接渲染出草稿。
 * 然后一场一场换成真正的画面（把 DRAFT 卡删掉）。
 *
 * 挂时间的三种方式（都不写死秒数，配音重做后自动跟上）：
 *   1. 按场内序号： const s = c.segs();  s[2].start / s[2].end          （第 3 段开始 / 结束）
 *   2. 按段号：     c.segId('S03-12').start                             （台本里的段号，全片唯一）
 *   3. 按台词短语： c.P(c.segId('S03-12'), '三件事', 0.5)               （这句里「三件事」开口的时刻；找不到用 50% 处）
 *                   c.at('三件事', 0.5)                                 （在本场所有段里找）
 *   另外：c.gap(seg) 是这一段后面的纯画面停顿；c.endTalk() 是本场讲完的时刻；ENG.tocInTime() 是疑问卡飞进目录的时刻。
 *
 * 版面：内容放在 x 440–1860、y 80–900；不要压到左下角色（x ≤ 380, y ≥ 690）、底部字幕（y 922–1000）、
 *   右上目录（3 题约 x ≥ 1540、y ≤ 162；题多或字长时更宽更高 —— 用 ENG.tocRect() 取实际大小，ENG.safeTop(y, right, left)
 *   把卡片顶推到目录下方；疑问场之后常驻）。标题卡收起后占左上 x 440–1300、y 84–130。
 */
(function () {
  'use strict';
  const { EP, SCENES } = ENG;
  if (!SCENES.length) return;
  const ids = SCENES.map(s => s.id);
  const OPEN = ids[0];                              // 开场
  const QS = EP.question_scene;                     // 疑问场（episode.json 的 question_scene）
  const LAST = ids[ids.length - 1];                 // 总结
  const clip = (s, n) => { s = String(s || '').replace(/【[^】]*】/g, '').trim(); return s.length > n ? s.slice(0, n) + '…' : s; };

  // ================================================================== 开场：大字 + 期号
  ENG.scene(OPEN, c => {
    const s0 = c.seg(0);
    // 挂在「今天」开口前一点；台词里没有「今天」就用第一段 40% 处
    const at = (c.find('今天') != null ? c.find('今天') : s0.start + (s0.end - s0.start) * 0.4) - 0.15;
    c.bigWord({
      text: EP.keyword || EP.title || '原LAI如此',       // 本期关键词（如 "Token"）；episode.json 里没有就用题目
      kicker: `原LAI如此 · #${ENG.pad2(EP.number)}`,
      sub: EP.keyword ? EP.title : '',
      at,
    });
  });

  // ================================================================== 疑问场：疑问卡逐张出现 → 飞进右上「本期目录」
  if (QS && QS !== OPEN && ids.includes(QS)) ENG.scene(QS, c => {
    const s = c.segs();
    // 每张卡挂在念到这个问题的那一刻：先按问题原文找台词，找不到就依次用第 2、3、4… 段的开头
    const at = (EP.questions || []).map((q, i) => {
      const t = c.find(q.text);
      return t != null ? t : s[Math.min(s.length - 1, 1 + i)].start + 0.05;
    });
    c.questionCards({ at, titleAt: s[Math.min(1, s.length - 1)].start + 0.25 });
    // 飞入时刻 = ENG.tocInTime()（本场最后一句结束前 0.75 s），目录的高亮 / 打勾由 core.js 按 questions[].scenes 自动完成
  });

  // ================================================================== 讲解章节：标题卡 + 分镜草稿（按段出现画面说明）
  ids.filter(id => id !== OPEN && id !== QS && id !== LAST).forEach(sid => ENG.scene(sid, c => {
    const s = c.segs();
    if (!s.length) return;
    c.autoTitle(s[0]);                                // '一、Token 是什么' + 'PART 01 · 第一个问题'（按 episode.questions 推）
    // ---- DRAFT：把下面整段换成本章真正的画面 ----
    const PAGE = 5;
    for (let p = 1; p < s.length; p += PAGE) {
      const page = s.slice(p, p + PAGE);
      const next = s[p + PAGE];
      c.pointList({
        x: 560, y: ENG.safeTop(190, 1760, 560), w: 1200, fs: 26, step: 60, mark: 'num',   // safeTop: 让开右上目录
        kicker: `DRAFT · 画面说明（${page[0].id} – ${page[page.length - 1].id}，待替换）`,
        title: '本段画面要点',
        at: page[0].start + 0.1,
        until: next ? next.start - 0.05 : undefined,
        items: page.map(sg => ({ text: esc2(clip(sg.visual || sg.text, 34)), sub: sg.id, at: sg.start + 0.1 })),
      });
    }
  }));

  // ================================================================== 总结：逐条出现（占位：用本期问题；换成真正的结论）
  if (LAST !== OPEN && LAST !== QS) ENG.scene(LAST, c => {
    const s = c.segs();
    const Q = EP.questions || [];
    const items = Q.length ? Q.map(q => [q.text, '（总结这一题的一句话）']) : s.slice(1, 5).map(sg => [clip(sg.text, 20), '']);
    c.summary({
      items: items.slice(0, 5),
      at: items.slice(0, 5).map((_, i) => s[Math.min(s.length - 1, 1 + i)].start + 0.1),
      cardAt: s[0].start + 0.1,
    });
  });

  function esc2(t) { return ENG.esc(t); }

  /* ------------------------------------------------------------------ 常用写法速查（复制到上面的场景里用）
  ENG.scene('S04', c => {
    const s = c.segs();
    c.autoTitle(s[0]);
    // 一句结论卡：大字在「接的是」开口时出现
    const st = c.statement({ x: 610, y: 320, kicker: 'MOSTLY · 多数情况下', lead: '接的是：',
      main: 'DeepSeek 大模型的 <span class="or">API</span>', at: s[1].start + 0.1, mainAt: c.P(s[1], '接的是', 0.3), until: s[2].start });
    // 流程图：手机 → 后台 → 模型，请求走上道、返回走下道
    const off = s[6].start;
    const f = c.flow({ until: off, nodes: [
        { id: 'app', x: 470, y: 200, w: 250, h: 250, icon: 'phone', title: '手机 App', sub: '（界面）', at: s[2].start + 0.1 },
        { id: 'srv', x: 1540, y: 200, w: 300, h: 250, icon: 'server', title: '服务器上的大模型', size: 30, at: c.P(s[2], '真正生成', 0.45) }],
      links: [
        { from: 'app', to: 'srv', lane: -40, label: 'API 请求', at: s[3].start + 0.1 },
        { from: 'srv', to: 'app', lane: 40, color: 'rgba(237,234,227,.8)', label: 'API 返回', labelKind: '', at: s[4].start + 0.1 }] });
    c.token({ text: '问题', kind: 'req', from: [736, 269], to: [1400, 269], at: c.P(s[3], '把问题', 0.35) });
    // 代码卡：先整体出现，再按台词高亮某几行
    const code = c.code({ x: 470, y: 200, w: 640, h: 300, title: '请求', kicker: 'REQUEST', lines: ['POST /chat/completions', 'Authorization: Bearer sk-••••', '', '{ "model": "…" }'] });
    code.tr.in(s[5].start + 0.15).out(off);
    c.focus(code, c.P(s[5], '每次都要', 0.4), [1]);
    // 对比表、步骤条、示意浏览器
    c.compareTable({ kicker: 'COMPARE · 对比', title: '三种格式对比', tip: '可截图保存', cols: ['格式', '地址结尾', 'Key 放在'],
      colX: [36, 420, 820], rows: [['Chat Completions', '/chat/completions', 'Authorization']], at: (c.gap(s[6]) || s[7]).start });
    c.steps({ items: [['注册并登录', '开放平台'], ['创建 API key', '起名 → 创建']], at: s[1].start, active: [s[1].start, s[3].start], done: [s[3].start, s[4].start] });
    const win = c.browser({ url: 'platform.example.com', at: s[1].start + 0.1, until: s[8].start });
    const v = win.view(s[1].start + 0.1, s[2].start);   // 窗口里的一屏内容
    c.div('ui-h', 40, 36, null, null, '登录', v);
  });
  ------------------------------------------------------------------ */
})();
