// ═════════════════════════════ 本条：Claude官方教程 第 1 期（悠一出镜版，字幕 = 他实际说的话）的叠加层（scenes.js 之后、engine.js 之前加载）
// 版式：标题 → 中间窗口（one 单窗 / two 双窗 / big 大窗）→ 字幕 → 出镜小窗（compose_face_mixed.py 渲完后叠）。窗口内容坐标：one / two = 1474×829，big = 1474×1725。
// 大窗里的出镜小窗在左下角：内容坐标 x < 320 且 y > 1335 的地方留空 —— 所以 big 的说明卡内容都放在 y ≤ 1330 以内。
// 画面 = 官方课（Claude Academy）的屏幕 / 动画镜头 + 悠一自己的录屏 + 下面自己画的说明卡（官方课里没有中文版的：顾问 / 助手、文件夹、新闻聚合、循环图、一来一回、四样东西、泼冷水）。
// 时间都按字幕行算：S('T20') = 这一行开始说的时刻，P('T20', '词') = 说到这个词的时刻（按字数估）；词必须真在那一行的字幕里（check_phrases.py 会查）。
const SEG = id => { const g = TL.segs.find(x => x.id === id); if (!g) throw new Error('没有场景 ' + id); return g; };
const BEIGE = '#F3EEE4', INK = '#1F1B16', GRAY = '#7A7367', CORAL = '#D97757', ORG = '#FF4F1A', LINEC = '#E2DACA', WHITE = '#FFFFFF', GREEN = '#2F8F5B', RED = '#C8402F', SOFT = '#FFF6EE';
const EMO = "'Segoe UI Emoji','Noto Color Emoji','Noto Sans SC',sans-serif";
const FEMO = "'Noto Sans SC'," + EMO;

// 说明卡：整个窗口内容区一张米色底；build(root, sg) 返回 update(T)，T = 成片绝对秒（和 S() / P() 同一套）
function card(sid, build) {
  const sg = SEG(sid);
  OV.push({ t0: sg.s, t1: sg.e - 0.12, fast: true, build: p => {
    const root = mk(p, '', { position: 'absolute', inset: '0px', background: BEIGE, overflow: 'hidden', fontFamily: "'Noto Sans SC'" });
    const up = build(root, sg);
    return lt => up(lt + sg.s);
  } });
}
const fx = (el, T, t0, o = {}) => show(el, T, t0, Object.assign({ d: 0.35, dy: 22 }, o));
const txt = (r, x, y, w, size, color, html, o = {}) => at(r, x, y, w, 'auto', '', Object.assign({ font: `${o.weight || 800} ${size}px/${o.lh || 1.25} 'Noto Sans SC'`, color, textAlign: o.align || 'left', whiteSpace: o.nowrap ? 'nowrap' : 'normal' }, o.style || {}), html);
const panel = (r, x, y, w, h, o = {}) => at(r, x, y, w, h, '', Object.assign({ background: o.bg || WHITE, border: `${o.bw || 5}px solid ${o.bc || LINEC}`, borderRadius: (o.r || 36) + 'px', boxShadow: o.shadow === false ? 'none' : '0 14px 0 rgba(31,27,22,.10)', transition: 'none' }, o.style || {}));
const pill = (r, x, y, w, h, html, o = {}) => at(r, x, y, w, h, '', { background: o.bg || WHITE, border: `${o.bw || 4}px solid ${o.bc || LINEC}`, borderRadius: (o.r || 28) + 'px', display: 'flex', alignItems: 'center', justifyContent: 'center', font: `${o.weight || 800} ${o.size || 48}px/1.2 'Noto Sans SC'`, color: o.color || INK, textAlign: 'center', padding: '0 14px', boxShadow: '0 8px 0 rgba(31,27,22,.08)', fontFamily: FEMO }, html);
const kcap = (r, x, y, w, h, label, size = 110) => at(r, x, y, w, h, '', { background: WHITE, border: `7px solid ${INK}`, borderBottomWidth: '18px', borderRadius: '30px', display: 'flex', alignItems: 'center', justifyContent: 'center', font: `900 ${size}px 'JetBrains Mono','Noto Sans SC'`, color: INK }, label);
const lit = (e, on, c = ORG) => { e.style.borderColor = on ? c : LINEC; e.style.background = on ? SOFT : WHITE; e.style.transform = on ? 'scale(1.03)' : 'scale(1)'; };
const svgAt = (r, x, y, w, h, body, color = CORAL, sw = 12) => at(r, x, y, w, h, '', { pointerEvents: 'none' }, `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" fill="none" stroke="${color}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`);
// 官方课镜头上的中文小标签（窗口左上角；只放在上窗）。结束时间提前 0.25 s，免得淡出时压到下一个场景
const chip = (t0, t1, text, o = {}) => note(t0, Math.max(t0 + 0.9, t1 - 0.25), text, '', Object.assign({ x: 40, y: 34, w: 1000 }, o));

// ─────────── S07 顾问 vs 助手（big）：T20–T24
card('S07', r => {
  const top = panel(r, 70, 50, 1334, 590);
  txt(top, 36, 22, 170, 120, INK, '📞', { align: 'center', style: { fontFamily: EMO } });
  const topT0 = txt(top, 220, 20, 900, 110, INK, '聊天窗口', { weight: 900 });         // 开头先写“聊天窗口”（他先说的是它），说到“顾问”再换
  const topT = txt(top, 220, 20, 800, 110, INK, '顾问', { weight: 900 });
  const topS = txt(top, 220, 140, 1080, 62, GRAY, '隔着电话，给你出主意<br><span style="color:' + CORAL + '">＝ 聊天窗口里的 Claude</span>', { weight: 800, lh: 1.3 });
  const p1 = pill(top, 40, 340, 340, 100, '我问问题'), p2 = pill(top, 420, 340, 340, 100, '它回答', { bc: CORAL }), p3 = pill(top, 800, 340, 490, 100, '我得自己粘贴 📋', { bc: ORG, bg: SOFT });
  const p4 = pill(top, 40, 470, 340, 100, '有报错'), p5 = pill(top, 420, 470, 870, 100, '→ 粘贴回它的窗口，再问一遍', { bc: ORG, bg: SOFT });
  const bot = panel(r, 70, 710, 1334, 620, { bc: CORAL });
  txt(bot, 36, 22, 170, 120, INK, '💻', { align: 'center', style: { fontFamily: EMO } });
  const botT = txt(bot, 220, 20, 1000, 110, CORAL, '助手 · 同事', { weight: 900 });
  const botS = txt(bot, 220, 140, 1080, 62, GRAY, '直接坐在你的电脑前<br><span style="color:' + CORAL + '">＝ Claude Code</span>', { weight: 800, lh: 1.3 });
  const WORK = ['找代码', '改代码', '跑命令', '搜索整个项目', '创建文件', '删除文件'];
  const chips = WORK.map((w, i) => pill(bot, 40 + (i % 3) * 430, 320 + Math.floor(i / 3) * 140, 410, 120, w, { bc: CORAL, size: 52 }));
  return T => {
    fx(top, T, S('T20') + 0.05);
    fx(topT0, T, S('T20') + 0.1, { dy: 0, t1: P('T20', '顾问') - 0.12, d1: 0.2 });
    fx(topT, T, P('T20', '顾问') - 0.12, { dy: 0 }); fx(topS, T, P('T20', '隔着电话') - 0.1, { dy: 0 });
    fx(p1, T, S('T21') - 0.05); fx(p2, T, P('T21', '它会给我回答') - 0.1); fx(p3, T, P('T21', '我必须要粘贴') - 0.1);
    fx(p4, T, S('T22') - 0.05); fx(p5, T, P('T22', '我得粘贴') - 0.1);
    fx(bot, T, S('T23') - 0.05);
    fx(botT, T, P('T23', '请了一个助手') - 0.1, { dy: 0 }); fx(botS, T, P('T23', '直接坐在') - 0.1, { dy: 0 });
    chips.forEach((c, i) => fx(c, T, P('T24', WORK[i]) - 0.1, { dy: 18 }));
  };
});

// ─────────── S08a 活动范围（one 1474×829）：T25
card('S08a', r => {
  const proj = panel(r, 70, 60, 820, 710, { bc: ORG, bw: 8, bg: SOFT });
  txt(proj, 40, 30, 130, 120, INK, '📂', { align: 'center', style: { fontFamily: EMO } });
  txt(proj, 180, 28, 620, 74, INK, '你启动它的文件夹', { weight: 900 });
  txt(proj, 180, 116, 620, 52, GRAY, '默认只在这里干活', { weight: 800 });
  ['src/', 'docs/', 'tests/'].forEach((n, i) => pill(proj, 50 + (i % 2) * 370, 250 + Math.floor(i / 2) * 150, 340, 120, '📁 ' + n, { bc: CORAL, size: 54 }));
  const sub = txt(proj, 50, 560, 720, 60, ORG, '＋ 里面所有的子文件夹', { weight: 900 });
  const out = panel(r, 940, 60, 470, 710, { bc: LINEC, bg: '#EDE7DA', shadow: false });
  txt(out, 0, 170, 460, 140, GRAY, '🔒', { align: 'center', style: { fontFamily: EMO } });
  txt(out, 0, 350, 460, 70, GRAY, '别的地方', { weight: 900, align: 'center' });
  return T => { fx(proj, T, S('T25') + 0.05); fx(sub, T, P('T25', '子文件夹') - 0.5, { dy: 10 }); fx(out, T, E('T25') - 0.9, { dy: 10 }); };
});

// ─────────── S14d 上网查资料（big）：T46–T47
card('S14d', r => {
  const lead = at(r, 0, 300, 1474, 700);                                            // 开头（T46）：大地球 + 上网查资料 + 例子
  txt(lead, 0, 0, 1474, 330, INK, '🌐', { align: 'center', style: { fontFamily: EMO, fontSize: '290px' } });
  txt(lead, 0, 360, 1474, 140, INK, '上网查资料', { weight: 900, align: 'center', style: { fontSize: '124px' } });
  const tag = pill(lead, 437, 540, 600, 100, '例：新闻聚合', { bc: CORAL, size: 54, color: CORAL });
  const head = txt(r, 0, 60, 1474, 100, INK, '④ 上网查资料', { weight: 900, align: 'center' });
  const ROWS = [['⏰', '每天定时定点', '每天定时定点'], ['🔎', '去搜这些新闻', '去搜这些新闻'], ['🗂️', '把它整理好', '把它整理好'], ['📄', '创建一个新的文档 → 给我看', '创建一个新的文档']];
  const els = ROWS.map((x, i) => {
    const e = panel(r, 150, 220 + i * 250, 1174, 180);
    txt(e, 26, 18, 150, 130, INK, x[0], { align: 'center', style: { fontFamily: EMO } });
    txt(e, 200, 44, 940, 86, INK, x[1], { weight: 900, nowrap: true });
    return e;
  });
  const arrows = svgAt(r, 0, 0, 1474, 1330, [0, 1, 2].map(i => `<path d="M737 ${406 + i * 250} L737 ${464 + i * 250} M711 ${442 + i * 250} L737 ${468 + i * 250} L763 ${442 + i * 250}"/>`).join(''));
  return T => {
    fx(lead, T, S('T46') + 0.05, { t1: S('T47') - 0.12, d1: 0.25 });
    fx(tag, T, P('T46', '新闻聚合') - 0.2, { dy: 10, t1: S('T47') - 0.12, d1: 0.25 });
    fx(head, T, S('T47') - 0.05, { dy: 0 });
    els.forEach((e, i) => fx(e, T, P('T47', ROWS[i][2]) - 0.1, { dy: 26 }));
    arrows.style.opacity = easeOut((T - P('T47', '去搜这些新闻')) / 0.5);
  };
});

// ─────────── 循环图（S17 / S19）：big
// 三张节点卡：outer 管淡入 / 位置，inner 管高亮
function buildLoop(r) {
  const small = txt(r, 0, 36, 1474, 50, GRAY, '代理循环  agentic loop', { weight: 800, align: 'center', style: { letterSpacing: '.12em' } });
  const req = panel(r, 150, 100, 1080, 120, { bc: CORAL, r: 60, bg: SOFT });
  txt(req, 0, 24, 1070, 64, INK, '你：登录页点了没反应，帮我修一下', { weight: 900, align: 'center' });
  const goal = panel(r, 160, 250, 1160, 112, { bc: LINEC, r: 56 });
  const goalT = txt(goal, 0, 26, 1150, 56, INK, '🎯 目标：修好登录页（必须完成）', { weight: 900, align: 'center', nowrap: true, style: { fontFamily: FEMO } });
  const NODE = [['①', '找线索', '查看代码文件 · 读报错', '🔍'], ['②', '动手', '改文件 · 跑命令', '🛠️'], ['③', '验结果', '再去跑 · 看有没有修好', '✅']];
  const outer = [], inner = [];
  NODE.forEach((n, i) => {
    const o = at(r, 150, 410 + i * 290, 1080, 240, '', {});
    const e = panel(o, 0, 0, 1080, 240);
    at(e, 38, 56, 126, 126, '', { borderRadius: '63px', background: CORAL, color: WHITE, display: 'flex', alignItems: 'center', justifyContent: 'center', font: "900 76px 'Noto Sans SC'" }, n[0]);
    txt(e, 205, 30, 700, 96, INK, n[1], { weight: 900 });
    txt(e, 205, 138, 810, 56, GRAY, n[2], { weight: 800 });
    txt(e, 880, 50, 170, 130, INK, n[3], { align: 'center', style: { fontFamily: EMO } });
    outer.push(o); inner.push(e);
  });
  const arrows = svgAt(r, 0, 0, 1474, 1330, [0, 1].map(i => `<path d="M690 ${654 + i * 290} L690 ${698 + i * 290} M664 ${676 + i * 290} L690 ${700 + i * 290} L716 ${676 + i * 290}"/>`).join('') + `<path d="M690 366 L690 402 M664 380 L690 404 L716 380"/>`);
  const back = svgAt(r, 0, 0, 1474, 1330, `<path d="M1236 1110 C1410 1110 1410 530 1242 530 M1278 500 L1242 530 L1278 560"/>`, ORG);
  const backT = txt(r, 1330, 640, 100, 56, ORG, '没做好 再来一圈', { weight: 900, lh: 1.5, style: { writingMode: 'vertical-rl', letterSpacing: '.08em' } });
  const know = pill(r, 250, 1245, 980, 84, 'ℹ 这些只需要了解，Claude 自己会做', { bc: GRAY, size: 46, color: GRAY });
  return { small, req, goal, goalT, outer, inner, arrows, back, backT, know };
}
card('S17', r => {
  const L = buildLoop(r);
  return T => {
    fx(L.small, T, S('T54') + 0.05, { dy: 0 });
    fx(L.req, T, P('T54', '你跟他说了') - 0.1);
    fx(L.goal, T, P('T55', '它就会列为') - 0.2);
    L.outer.forEach((e, i) => fx(e, T, S('T56') - 0.4 + i * 0.25, { dy: 30, max: i === 0 ? 1 : 0.55 }));
    L.arrows.style.opacity = easeOut((T - S('T56') + 0.3) / 0.5);
    L.back.style.opacity = 0; L.backT.style.opacity = 0;
    lit(L.inner[0], T >= P('T56', '去查看') - 0.3); lit(L.inner[1], false); lit(L.inner[2], false);
    fx(L.know, T, S('T57') - 0.05, { dy: 10 });
  };
});
card('S19', r => {
  const L = buildLoop(r);
  const done = txt(L.goal, 0, 26, 1150, 56, GREEN, '🎯 目标达成 ✓', { weight: 900, align: 'center', nowrap: true, style: { fontFamily: FEMO } });
  L.know.style.display = 'none';
  return T => {
    const tFix = P('T61', '如果修好了'), tNo = S('T62'), tBlend = S('T63');
    L.inner.forEach((e, i) => {
      let on;
      if (T < tFix) on = i === 2;
      else if (T < tNo) on = false;
      else if (T < tBlend) on = Math.floor((T - tNo) / 1.1) % 3 === i;
      else on = true;
      lit(e, on);
      const blend = easeOut((T - tBlend) / 0.8);                       // “不是死板的流水线，会混在一起”：三张卡叠在一起、错开一点
      L.outer[i].style.top = (410 + i * 290 - blend * i * 120) + 'px'; L.outer[i].style.left = (150 + (i - 1) * 46 * blend) + 'px';
    });
    L.goalT.style.opacity = T >= tFix && T < tNo ? 0 : 1; done.style.opacity = T >= tFix && T < tNo ? 1 : 0;       // 修好了 → 绿色“目标达成”；没修好 → 目标还在
    L.goal.style.borderColor = T >= tFix && T < tNo ? GREEN : LINEC; L.goal.style.background = T >= tFix && T < tNo ? '#EEF8F1' : WHITE;
    const bk = easeOut((T - tNo) / 0.5) * (T < tBlend ? 1 : 1 - easeOut((T - tBlend) / 0.4));
    L.back.style.opacity = bk; L.backT.style.opacity = bk;
    L.arrows.style.opacity = 1 - easeOut((T - tBlend) / 0.5);
  };
});

// ─────────── S20 转半圈 vs 连着做几十步（big）：T64–T67
card('S20', r => {
  const a = panel(r, 70, 50, 1334, 560);
  txt(a, 40, 26, 140, 120, INK, '❓', { align: 'center', style: { fontFamily: EMO } });
  txt(a, 200, 30, 1000, 100, INK, '问一个问题', { weight: 900 });
  svgAt(a, 90, 170, 500, 320, `<path d="M70 260 C70 70 450 70 450 260"/><path d="M420 222 L450 262 L488 232"/>`, ORG, 16);
  txt(a, 640, 190, 650, 110, ORG, '转半圈', { weight: 900 });
  const ok = pill(a, 640, 330, 630, 120, '一步完成 ✓　没有循环', { bc: GREEN, color: GREEN, size: 50 });
  const b = panel(r, 70, 680, 1334, 650, { bc: CORAL });
  txt(b, 40, 26, 140, 120, INK, '🐛', { align: 'center', style: { fontFamily: EMO } });
  txt(b, 200, 30, 1100, 100, INK, '一个比较难的毛病', { weight: 900 });
  const rep = pill(b, 50, 190, 600, 110, '反复地修改', { bc: ORG, size: 54 }), rep2 = pill(b, 690, 190, 590, 110, '反复地执行命令', { bc: ORG, size: 54 });
  const dz = txt(b, 50, 350, 700, 150, ORG, '连着做 几十步', { weight: 900, nowrap: true, style: { fontSize: '96px' } });
  const spin = txt(b, 1060, 330, 200, 180, ORG, '↻', { weight: 900, align: 'center', style: { fontSize: '170px', transformOrigin: '50% 55%' } });
  const fix = pill(b, 50, 520, 1230, 100, '一边做，一边纠正自己', { bc: GREEN, color: GREEN, size: 54 });
  return T => {
    fx(a, T, S('T64') + 0.05); fx(ok, T, P('T65', '一步它就完成了') - 0.2);
    fx(b, T, S('T66') - 0.05); fx(rep, T, P('T66', '反复地去修改') - 0.1); fx(rep2, T, P('T66', '反复地去执行命令') - 0.1);
    fx(dz, T, P('T67', '几十步') - 0.3, { dy: 14 }); fx(spin, T, P('T67', '几十步') - 0.3, { dy: 0 });
    spin.style.transform = `rotate(${(T - S('T67')) * 200}deg)`;
    fx(fix, T, P('T67', '一边做') - 0.1);
  };
});

// ─────────── S21 你也在圈里（big）：T68–T71
card('S21', r => {
  const lab = txt(r, 0, 36, 1474, 56, GRAY, '循环里，你也在', { weight: 800, align: 'center', style: { letterSpacing: '.08em' } });
  const MINI = [['🔍', '找线索'], ['🛠️', '动手'], ['✅', '验结果']];
  const nodes = MINI.map((n, i) => { const e = panel(r, 70 + i * 470, 130, 400, 270, { r: 30 }); txt(e, 0, 24, 390, 104, INK, n[0], { align: 'center', style: { fontFamily: EMO } }); txt(e, 0, 150, 390, 80, INK, n[1], { weight: 900, align: 'center' }); return e; });
  const lines = svgAt(r, 0, 0, 1474, 560, `<path d="M474 265 L536 265 M514 243 L538 265 L514 287"/><path d="M944 265 L1006 265 M984 243 L1008 265 L984 287"/><path d="M1270 412 C1270 490 205 490 205 414 M185 442 L205 408 L235 436" stroke="${ORG}"/>`, CORAL, 10);
  const you = panel(r, 250, 540, 980, 130, { bc: INK, r: 65 });
  txt(you, 0, 26, 970, 76, INK, '🙋 你，随时可以打断它', { weight: 900, align: 'center', style: { fontFamily: FEMO } });
  const row1 = at(r, 0, 740, 1474, 200), row2 = at(r, 0, 980, 1474, 200);
  const k1 = kcap(row1, 110, 0, 250, 180, 'Esc', 90);
  txt(row1, 420, 0, 980, 76, INK, '让它停止', { weight: 900 });
  txt(row1, 420, 92, 1020, 56, GRAY, '发现做错了，或者有新想法', { weight: 800 });
  const k2 = kcap(row2, 70, 0, 280, 180, '打字', 76);
  at(row2, 360, 30, 90, 110, '', { font: "900 76px 'Noto Sans SC'", color: GRAY, textAlign: 'center' }, '＋');
  kcap(row2, 460, 0, 300, 180, 'Enter', 64);
  txt(row2, 810, 0, 640, 76, INK, '插进它的循环', { weight: 900 });
  txt(row2, 810, 92, 640, 56, GRAY, '把你的新内容发给它', { weight: 800 });
  const note2 = pill(r, 150, 1210, 1180, 112, '它做完手头这批，就会读到你的话，再调整', { bc: GREEN, color: GREEN, size: 52 });
  return T => {
    fx(lab, T, S('T68') + 0.05, { dy: 0 });
    nodes.forEach((e, i) => { fx(e, T, S('T68') + 0.1 + i * 0.2, { dy: 30 }); e.style.borderColor = (Math.floor((T - S('T68')) / 1.0) % 3 === i) ? ORG : LINEC; });
    lines.style.opacity = easeOut((T - S('T68') - 0.5) / 0.5);
    fx(you, T, P('T68', '你就可以随时地打断它') - 0.3);
    fx(row1, T, S('T69') - 0.05); fx(row2, T, P('T70', '你想要在它的循环里') - 0.1); fx(note2, T, S('T71') - 0.05);
    const pulse = (el, t0) => { el.style.transform = `translateY(${T > t0 && T < t0 + 0.3 ? 12 : 0}px)`; };
    pulse(k1, P('T69', '按 ESC')); pulse(k2, P('T70', '打字'));
  };
});

// ─────────── S22 四个点（big）：T72–T74
card('S22', r => {
  const q = txt(r, 0, 60, 1474, 90, INK, '这个循环是怎么跑起来的？', { weight: 900, align: 'center' });
  const T4 = [['🧠', '大脑', 'Claude 模型', '大脑'], ['🤲', '双手', '工具', '双手'], ['🗂️', '记忆', '上下文窗口', '记忆'], ['🔑', '钥匙', '权限', '钥匙']];
  const tiles = T4.map((t, i) => {
    const e = panel(r, 70 + (i % 2) * 694, 190 + Math.floor(i / 2) * 560, 640, 520, { bc: LINEC });
    txt(e, 0, 30, 630, 180, INK, t[0], { align: 'center', style: { fontFamily: EMO } });
    txt(e, 0, 230, 630, 120, INK, t[1], { weight: 900, align: 'center' });
    txt(e, 0, 380, 630, 62, GRAY, t[2], { weight: 800, align: 'center' });
    return e;
  });
  return T => {
    fx(q, T, S('T72') + 0.05);
    tiles.forEach((e, i) => {
      const t0 = P('T74', T4[i][3]) - 0.15, a = easeOut((T - t0) / 0.35);
      e.style.opacity = 0.2 + 0.8 * a; e.style.visibility = 'visible';
      e.style.transform = `translateY(${(1 - a) * 18}px) scale(${0.97 + 0.03 * a})`;
      e.style.borderColor = a > 0.5 ? (i === 0 ? CORAL : ORG) : LINEC;
    });
  };
});

// ─────────── S23 大脑在云端 / 双手是工具（big）：T75–T80
card('S23', r => {
  const brain = panel(r, 70, 40, 1334, 620, { bc: CORAL });
  txt(brain, 36, 20, 160, 130, INK, '🧠', { align: 'center', style: { fontFamily: EMO } });
  txt(brain, 210, 22, 1000, 110, INK, '大脑 = Claude 模型', { weight: 900 });
  const cloud = pill(brain, 40, 160, 640, 90, '☁ 在云端，不在本地', { bc: CORAL, size: 50, color: CORAL });
  const SK = ['听懂你的话', '看懂代码', '决定下一步'];
  const sk = SK.map((s, i) => pill(brain, 40 + i * 430, 285, 410, 110, s, { size: 48 }));
  const no = pill(brain, 40, 440, 1250, 120, '✗ 没办法在本地执行这些任务、命令', { bc: RED, color: RED, size: 52, bg: '#FDECEA' });
  const hands = panel(r, 70, 790, 1334, 530, { bc: INK });
  txt(hands, 36, 20, 160, 130, INK, '🤲', { align: 'center', style: { fontFamily: EMO } });
  txt(hands, 210, 22, 1000, 110, INK, '双手 = 工具', { weight: 900 });
  const run = pill(hands, 40, 170, 600, 110, '用来执行这些命令', { size: 50 });
  const dumb = pill(hands, 680, 170, 610, 110, '自己不知道执行什么', { size: 48, bc: GRAY, color: GRAY });
  const res = pill(hands, 40, 320, 1250, 130, '听大脑的 → 才能修改本地的内容', { bc: GREEN, color: GREEN, size: 54 });
  const ar = svgAt(r, 0, 0, 1474, 800, `<path d="M737 668 L737 772 M705 736 L737 776 L769 736"/>`, INK, 14);
  const arT = txt(r, 790, 690, 600, 56, INK, '去执行什么命令', { weight: 900 });
  return T => {
    fx(brain, T, S('T75') + 0.05); fx(cloud, T, S('T76') - 0.05, { dy: 10 });
    sk.forEach((e, i) => fx(e, T, P('T77', ['听懂', '看懂', '决定'][i]) - 0.1, { dy: 14 }));
    fx(no, T, S('T78') + 0.3, { dy: 10 });
    fx(hands, T, S('T79') - 0.05); fx(run, T, P('T79', '用来执行') - 0.2, { dy: 10 });
    fx(dumb, T, S('T80') - 0.05, { dy: 10 });
    ar.style.opacity = easeOut((T - P('T80', '通过它的大脑') + 0.2) / 0.4); fx(arT, T, P('T80', '通过它的大脑'), { dy: 0 });
    fx(res, T, P('T80', '它才能修改') - 0.1, { dy: 10 });
  };
});

// ─────────── S24 大脑和双手怎么配合（big）：T81–T87 —— 一来一回
card('S24', r => {
  const LH = txt(r, 0, 30, 460, 62, INK, '💻 本地', { weight: 900, align: 'center', style: { fontFamily: FEMO } });
  const LS = txt(r, 0, 94, 460, 44, GRAY, 'Claude Code ＋ 工具', { weight: 800, align: 'center' });
  const RH = txt(r, 1014, 30, 460, 62, CORAL, '🧠 云端', { weight: 900, align: 'center', style: { fontFamily: FEMO } });
  const RS = txt(r, 1014, 94, 460, 44, GRAY, 'Claude 模型', { weight: 800, align: 'center' });
  at(r, 227, 150, 6, 1150, '', { background: LINEC, borderRadius: '3px' }); at(r, 1241, 150, 6, 1150, '', { background: LINEC, borderRadius: '3px' });
  const i1 = pill(r, 10, 160, 520, 104, '📁 本地有一份代码', { size: 46 });                       // 开头（T81）：先有代码，你再提需求
  const i2 = pill(r, 560, 160, 900, 104, '🙋 你：提出“修复它”的需求', { size: 46, bc: ORG, bg: SOFT });
  const ROWS = [
    { dir: '→', t: '修复 bug 的需求（prompt）', at: () => S('T82') },
    { dir: '←', t: '先找 bug 在哪些文件里', at: () => P('T83', '我要找一下'), pill: ['🔧 用工具读代码', () => P('T83', '来查看')] },
    { dir: '→', t: '你的请求 ＋ 这些代码', at: () => S('T84') },
    { dir: '←', t: '判断之后：这样改', at: () => S('T85'), pill: ['✏️ 改代码 · 跑一遍', () => P('T86', '把代码修改')] },
    { dir: '→', t: '跑通了', at: () => P('T86', '如果说跑通了') },
    { dir: '←', t: 'OK，任务完成', at: () => P('T86', '他大脑说'), pill: ['👀 你看到结果 ✓', () => P('T87', '这样你就能看到')] },
  ];
  const els = ROWS.map((o, i) => {
    const y = 290 + i * 168;
    const row = at(r, 0, y, 1474, 166);
    const right = o.dir === '→', x0 = right ? 250 : 1220, x1 = right ? 1220 : (o.pill ? 470 : 250), hd = right ? -32 : 32;
    svgAt(row, 0, 0, 1474, 166, `<path d="M${x0} 104 L${x1} 104 M${x1 + hd} 78 L${x1} 104 L${x1 + hd} 130"/>`, right ? ORG : INK, 12);
    txt(row, Math.min(x0, x1) + 20, 8, Math.abs(x1 - x0) - 40, 48, right ? ORG : INK, o.t, { weight: 900, align: 'center', nowrap: true });
    const pl = o.pill ? pill(row, 10, 46, 450, 114, o.pill[0], { size: 42, bc: GREEN, color: GREEN, bg: '#EEF8F1' }) : null;
    return { row, pl, o };
  });
  return T => {
    fx(LH, T, S('T81'), { dy: 0 }); fx(LS, T, S('T81'), { dy: 0 }); fx(RH, T, S('T81') + 0.1, { dy: 0 }); fx(RS, T, S('T81') + 0.1, { dy: 0 });
    fx(i1, T, S('T81') + 0.2, { dy: 14 }); fx(i2, T, P('T81', '你提出了') - 0.1, { dy: 14 });
    els.forEach(({ row, pl, o }) => { fx(row, T, o.at() - 0.1, { dy: 16 }); if (pl) fx(pl, T, o.pill[1]() - 0.05, { dy: 10 }); });
  };
});

// ─────────── S35 四个零件合起来 = 本地的智能体（big）：T109–T110
card('S35', r => {
  const T4 = [['🧠', '大脑', '大脑'], ['🤲', '双手', '双手'], ['🗂️', '记忆', '记忆'], ['🔑', '钥匙', '权限钥匙']];
  const tiles = T4.map((t, i) => {
    const e = panel(r, 70 + (i % 2) * 694, 60 + Math.floor(i / 2) * 390, 640, 360, { bc: LINEC });
    txt(e, 0, 20, 630, 150, INK, t[0], { align: 'center', style: { fontFamily: EMO } });
    txt(e, 0, 190, 630, 110, INK, t[1], { weight: 900, align: 'center' });
    return e;
  });
  const eq = txt(r, 0, 850, 1474, 100, GRAY, '＝', { weight: 900, align: 'center' });
  const ag = panel(r, 200, 970, 1074, 320, { bc: ORG, bg: SOFT, bw: 8 });
  txt(ag, 0, 30, 1064, 130, INK, '🤖 本地的智能体', { weight: 900, align: 'center', style: { fontFamily: FEMO } });
  txt(ag, 0, 180, 1064, 68, GRAY, '按你的要求，去完成任务', { weight: 800, align: 'center' });
  return T => {
    tiles.forEach((e, i) => {
      const t0 = P('T109', T4[i][2]) - 0.12, a = easeOut((T - t0) / 0.35);
      e.style.opacity = 0.25 + 0.75 * a; e.style.visibility = 'visible'; e.style.borderColor = a > 0.5 ? ORG : LINEC; e.style.transform = `scale(${0.98 + 0.02 * a})`;
    });
    fx(eq, T, S('T110') - 0.1); fx(ag, T, P('T110', '本地的智能体') - 0.6);
  };
});

// ─────────── S36 泼冷水（big）：T111–T114
card('S36', r => {
  const good = at(r, 0, 170, 1474, 460);                                            // T111 前半句“说完了这么好用的好处”：把四样好处回顾一遍
  txt(good, 0, 0, 1474, 100, GREEN, '👍 刚才讲的好处', { weight: 900, align: 'center', style: { fontFamily: FEMO } });
  ['读项目', '改代码', '跑命令', '上网查资料'].forEach((g, i) => pill(good, 160 + (i % 2) * 580, 140 + Math.floor(i / 2) * 150, 560, 126, '✓ ' + g, { bc: GREEN, color: GREEN, size: 58, bg: '#EEF8F1' }));
  const head1 = txt(r, 0, 70, 1474, 100, INK, '那不好的是什么？', { weight: 900, align: 'center' });
  const head2 = txt(r, 0, 70, 1474, 100, INK, '🧊 泼点冷水', { weight: 900, align: 'center', style: { fontFamily: FEMO } });
  const ROWS = [['🌀', '会有幻觉', '幻觉'], ['🎲', '是一个概率模型', '概率模型'], ['🐛', '可能会有 bug', 'bug']];
  const rows = ROWS.map((x, i) => {
    const e = panel(r, 150, 230 + i * 200, 1174, 170, { bc: LINEC });
    txt(e, 26, 16, 150, 130, INK, x[0], { align: 'center', style: { fontFamily: EMO } });
    txt(e, 210, 36, 930, 90, INK, x[1], { weight: 900, nowrap: true });
    return e;
  });
  const trend = at(r, 150, 850, 1174, 460);
  svgAt(trend, 0, 0, 1174, 380, `<path d="M40 50 C300 60 500 180 760 250 S1000 320 1120 340"/><path d="M1086 306 L1124 342 L1074 356"/>`, GREEN, 14);
  txt(trend, 20, 380, 1140, 66, GREEN, '模型越来越强，bug 越来越少', { weight: 900, nowrap: true });
  return T => {
    const tBad = P('T111', '那么不好是什么');
    fx(good, T, S('T111') + 0.1, { dy: 14, t1: tBad - 0.15, d1: 0.25 });
    fx(head1, T, tBad - 0.1, { t1: S('T112') - 0.1, dy: 0 }); fx(head2, T, S('T112') - 0.1, { dy: 0 });
    rows.forEach((e, i) => fx(e, T, P('T113', ROWS[i][2]) - 0.15, { dy: 22 }));
    fx(trend, T, P('T114', '随着模型越来越强') - 0.1, { dy: 18 });
  };
});

// ─────────── 官方课镜头上的中文小标签（窗口左上角，只在上窗；每条都是他那一句话的意思）
chip(S('T06'), E('T07'), 'Anthropic 官网 · 免费课程');                                   // S02
chip(S('T09'), E('T10'), 'Chat · Cowork · Code');                                       // S03：桌面应用顶上的三个标签
chip(S('T11'), E('T12'), '聊天窗口：只能回答，改不了文件');                              // S04
chip(S('T16'), E('T16'), '创建 · 修改 · 删除');                                          // S05
chip(S('T18'), E('T19'), 'Anthropic 官方做的 AI 助手');                                  // S06
chip(S('T26'), E('T26'), '要经过你的同意');                                              // S08b
chip(S('T28'), E('T28'), '在终端里输入 claude');                                         // S09
chip(S('T29'), E('T29'), '终端：只能敲命令的窗口');                                      // S10
chip(S('T31'), E('T31'), '用自然语言跟它沟通');                                          // S11
chip(P('T32', '智能体'), E('T33'), '智能体 = AI Agent');                                // S12
chip(S('T35'), E('T35'), '写文档 · 跑程序 · 搜文件 · 查资料', { w: 1300 });                // S13
chip(S('T38'), E('T40'), '① 读项目');                                                   // S14a
chip(S('T41'), E('T43'), '② 改代码');                                                   // S14b
chip(S('T44'), E('T45'), '③ 跑命令');                                                   // S14c
chip(S('T48'), E('T48'), '告诉它目标，它自己去做');                                      // S14e
chip(S('T50'), E('T50'), '一个循环的概念');                                              // S15
chip(P('T51', 'agent loop'), E('T53'), 'agent loop · 代理循环');                         // S16
chip(S('T59'), E('T59'), '找代码 → 读报错 → 动手改');                                    // S18
chip(S('T60'), E('T60'), '改好 → 再去跑');
chip(S('T88'), E('T89'), '记忆 = 上下文窗口');                                           // S25
chip(S('T90'), E('T92'), '记忆满了 → 自动压缩，旧细节会丢', { w: 1300 });                 // S26
chip(S('T93'), E('T94'), '新开一场对话，记忆是空的', { w: 1300 });                        // S27
chip(S('T95'), E('T96'), '每次都要守的规则 → 写进 CLAUDE.md', { w: 1300 });               // S28
chip(S('T98'), E('T100'), '钥匙 = 权限');                                               // S29：五种模式
chip(S('T101'), E('T101'), '手动档：改文件先问你');                                      // S30
chip(S('T102'), E('T103'), '接受编辑档：改文件不问');                                    // S31
chip(S('T104'), E('T104'), '别的命令还是会问');
chip(S('T105'), E('T105'), '计划档：只研究，不碰代码');                                  // S32
chip(S('T106'), E('T106'), '自动档：后台有安全检查');                                    // S33
chip(S('T107'), E('T107'), '全部放开：不再询问');                                        // S34
chip(S('T108'), E('T108'), '不建议新手开');
chip(S('T116'), E('T116'), '权限别开最大');                                              // S37
chip(P('T118', '终端里用'), P('T118', '然后你登录'), '终端里用', { w: 900 });            // S38（单窗，镜头按他说的顺序走：终端 → 启动 → 登录 → 编辑器插件 → 桌面 → 网页）
chip(P('T118', '然后你登录'), E('T118'), '登录账号就能用', { w: 900 });
chip(S('T119'), P('T119', '桌面'), '代码编辑器里的插件', { w: 1300 });
chip(P('T119', '桌面'), P('T119', '网页版') - 0.3, '桌面应用');
chip(P('T119', '网页版') - 0.3, E('T119'), '网页版');
chip(S('T121'), E('T121'), '先看状态栏，确认权限', { w: 1300 });                          // S39a
chip(S('T122'), E('T122'), '先问问题，再让它改东西', { w: 1300 });                        // S39b
