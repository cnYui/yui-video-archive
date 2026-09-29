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
 * 角色不在这里画（动作在台本【动作：…】里写，core.js 播）。自动层会在卡片、列表条目、代码卡等出现时让角色朝内容轻摊、
 *   看过去（components 已自动登记这些时刻）；自己用 c.div + c.show 搭的内容要补一句 c.cue(t)；
 *   想让角色在某段时间看着某张卡片：c.look(t0, t1)。
 *
 * 坐标：这里所有 x / y 都是 1920×1080「内容舞台」的坐标。视频画布更宽时（episode.json canvas，第 2 期起 2340×1080）
 *   舞台在画布里水平居中，坐标照写不变；徽标、目录、讲解员、字幕、进度条、背景是引擎的全局层，铺满画布，这里不管。
 * 版面：y 80–900。水平方向看 episode.json 的 "layout"：
 *   "center"（新一期默认）= 内容以画面中线 ENG.CX（舞台 x 960，和字幕同一条线）左右对称；组件不写 x 就自动居中，
 *     自己摆的用 ENG.CX - w / 2；章节标题收起后停在顶部正中（y 84–130）。
 *   没写 layout（第 1–4 期）= 内容区 x 440–1860（ENG.CX = 1150），标题卡收起后占左上 x 440–1300、y 84–130。
 *   不要压到左下角色（1920 宽时 x ≤ 380, y ≥ 690；2340 宽时舞台 x ≤ 170）、底部字幕（y 922–1000）、
 *   右上目录（1920 宽 3 题约 x ≥ 1540、2340 宽约 x ≥ 1750，y ≤ 162；题多或字长时更宽更高 ——
 *   用 ENG.tocRect() 取实际大小（舞台坐标），ENG.safeTop(y, right, left) 把卡片顶推到目录下方；疑问场之后常驻）。
 *   不要写死目录的位置。
 * 背景：episode.json 的 "bg_color"（新一期默认 "#FFFFFF"）= 纯色背景，浅色时引擎换浅色主题（ENG.LIGHT）：直接画在
 *   背景上的字用深色，自己写颜色时写 ENG.LIGHT ? 'var(--ink)' : 'var(--paper)'；卡片、代码卡、深色节点照旧。
 * 白板版（episode.json "style": "board"，新一期默认；用户 2026-09-28：「原LAI如此也用手写白板，字提前一秒出现」）：
 *   c.title / c.autoTitle / c.bigWord / c.questionCards / c.statement / c.pointList / c.summary 自动变成手写（board.js，
 *   参数照旧）；标题写在顶部正中（y 60–220 归标题），内容从 y 250 左右开始。自己画：c.hand（写一行字）、c.handText（带
 *   HTML 的字，橙色 span 划线）、c.handUnderline / c.handEllipse / c.handMark（划线、圈字）、c.handArrow、c.handRect、
 *   c.handLine、c.handNode（框 + 字）、c.handCheck、c.handDash，见 hand.js / board.js 顶部和 references/visuals.md「白板版」。
 *   时间照旧按声音写：画面整体比声音早 ENG.LEAD 秒（默认 1 s）是引擎做的，这里不要减。
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
    // 每张卡挂在念到这个问题的那一刻：先按问题原文找台词，再找「第一 / 第二 / 第三…」，都找不到就依次用第 2、3、4… 段的开头。
    // 台词和问题原文不一样（“Jev到底是什么”）又没说“第一”时，这里会挂错：自己用 c.P(c.segId('S02-05'), '到底是什么') 给
    const at = (EP.questions || []).map((q, i) => {
      const t = c.find(q.text);
      if (t != null) return t;
      const k = c.find('第' + '一二三四五六七八九'[i]);
      return k != null ? k : s[Math.min(s.length - 1, 1 + i)].start + 0.05;
    });
    c.questionCards({ at, titleAt: s[Math.min(1, s.length - 1)].start + 0.25 });
    // 飞入时刻 = ENG.tocInTime()（本场最后一句结束前 0.75 s；白板版 0.1 s，边说“把这三个问题讲清楚”边飞进目录），
    // 目录的高亮 / 打勾由 core.js 按 questions[].scenes 自动完成
  });

  // ================================================================== 讲解章节：标题卡 + 分镜草稿（按段出现画面说明）
  ids.filter(id => id !== OPEN && id !== QS && id !== LAST).forEach(sid => ENG.scene(sid, c => {
    const s = c.segs();
    if (!s.length) return;
    c.autoTitle(s[0]);                                // 大字 = 台本的场景 title（如 '三、学会思考'，编号照台本写）；
                                                      // 属于第 N 题时加 'PART 0N · 第N个问题'（按 episode.questions）
    // ---- DRAFT：把下面整段换成本章真正的画面 ----
    const PAGE = 5;
    const PX = ENG.CENTER ? Math.round(ENG.CX - 600) : 560;   // 居中版面（episode.json "layout": "center"）以画面中线为中
    const PY = ENG.BOARD ? 250 : ENG.safeTop(190, PX + 1200, PX);   // 白板版：标题占顶部，要点从 y 250 写起
    const CLIP = ENG.BOARD ? 10 : 34;                          // 白板版是手写（约 0.3 秒一个字），草稿每条只写 10 个字
    let pageIn = null;                                  // 白板版：上一页擦掉后，这一页最早从什么时候写（c.flip）
    for (let p = 1; p < s.length; p += PAGE) {
      const page = s.slice(p, p + PAGE);
      const next = s[p + PAGE];
      // 翻页：卡片版在下一页开口前换；白板版画面早 1 秒，要等这一页最后一句说完再擦（c.flip），不然最后一句的字没说到就没了
      const flip = next && ENG.BOARD ? c.flip(page[page.length - 1]) : null;
      const t0 = pageIn != null ? Math.max(page[0].start + 0.1, pageIn) : page[0].start + 0.1;
      c.pointList({
        x: PX, y: PY, w: 1200, fs: 26, step: 60, mark: 'num',   // safeTop: 让开右上目录
        kicker: `DRAFT · 画面说明（${page[0].id} – ${page[page.length - 1].id}，待替换）`,
        title: '本段画面要点', draft: true,         // 白板版：草稿不查写字时间（换成真画面后才查）
        at: t0,
        until: flip ? flip.out : next ? next.start - 0.05 : undefined,
        items: page.map(sg => ({ text: esc2(clip(sg.visual || sg.text, CLIP)), sub: sg.id, at: Math.max(sg.start + 0.1, t0) })),
      });
      pageIn = flip ? flip.in : null;
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
  // ---- 白板版（episode.json "style": "board"）：自己画。时间照声音写；翻页用 c.flip；淡出用 until（组件）/ out（c.hand*）
  ENG.scene('S04', c => {
    const s = c.segs(), T = i => s[Math.min(s.length - 1, i)].start, CX = ENG.CX;
    c.autoTitle(s[0]);                                   // 手写标题，顶部正中
    const f = c.flip(s[7]);                              // 第一页讲到 s[7]，说完再擦
    const a = c.handNode({ x: CX - 620, y: 300, w: 480, h: 190, text: 'LLM 大语言模型', sub: '一个字一个字往下写', at: T(1) + 0.1, until: f.out });
    const b = c.handNode({ x: CX + 140, y: 300, w: 480, h: 190, text: 'Jev 决策模型', sub: '只在选项里挑一个', at: T(2) + 0.1, until: f.out });
    c.hand({ text: 'vs', x: CX, y: 395, size: 72, align: 'center', color: ENG.HAND.ACCENT, at: b.t1 + 0.05, until: b.t1 + 0.5, out: f.out });
    c.handArrow({ x0: (a.x0 + a.x1) / 2, y0: a.y1 + 20, x1: CX - 150, y1: 560, at: T(3) + 0.1, out: f.out });
    const st = c.statement({ y: 580, lead: '区别在输出', main: 'Jev <span class="or">不生成文字</span>，只给答案',
      at: T(3) + 0.6, mainAt: T(4) + 0.1, until: f.out });
    c.handMark(st.main, 0, 3, { kind: 'circle' });      // 圈出 main 的第 0–2 个字，跟着它一起擦
    const code = c.code({ x: CX - 700, y: 290, w: 640, h: 250, title: '请求', lines: ['POST /v1/decide', '{ "options": ["A", "B"] }'] });
    c.tape(code.el);                                    // 像贴在白板上
    code.tr.in(Math.max(T(8) + 0.1, f.in));             // 第二页：不早于 f.in
    c.pointList({ x: CX + 20, y: 290, w: 680, title: '它会返回', at: Math.max(T(8) + 0.3, f.in), items: [
      { text: '选了哪一个', at: T(9) + 0.1 }, { text: '有多确定', at: T(10) + 0.1, sub: '置信度' }, { text: '不写解释', at: T(11) + 0.1, mark: 'x' }] });
  });
  ------------------------------------------------------------------ */
})();
