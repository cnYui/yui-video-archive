// 工具 + 文件卡片（演示区 1474×829 内的坐标）+ 现场片段的角标。v2：稿子压缩、少术语；现场片段用中文同声传译。
// 每个叠加层：[t0, t1] 显示（前后淡入淡出），t 用成片秒数；时间都按字幕条算：S('N07') = 这条开始说的时刻，P('N09', '不改法律') = 说到这个词的时刻。
// 字幕条：N01… = 画外音；K1a… = 现场片段里的中文同传（Fish 网页版「赛马娘（曼波欧耶版）」，两种都是同一个声音）。
const FPS = TL.fps;
window.__ERR = [];
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const easeIn = x => Math.pow(clamp(x), 3);
const easeIO = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const lerp = (a, b, x) => a + (b - a) * x;
const px = v => v + 'px';

function mk(parent, cls = '', style = {}, html = '', tag = 'div') {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  for (const [k, v] of Object.entries(style)) if (v !== undefined && v !== null) e.style[k] = typeof v === 'number' && !['opacity', 'zIndex', 'fontWeight', 'lineHeight', 'flex'].includes(k) ? px(v) : v;
  if (html) e.innerHTML = html;
  parent.appendChild(e);
  return e;
}
const at = (parent, x, y, w, h, cls = '', style = {}, html = '') => mk(parent, 'abs ' + cls, Object.assign({ left: x, top: y, width: w, height: h }, style), html);
function show(el, lt, t0, o = {}) {
  const d = o.d ?? 0.4, dy = o.dy ?? 16, dx = o.dx ?? 0;
  const a = easeOut((lt - t0) / d);
  const b = o.t1 == null ? 1 : 1 - easeIn((lt - o.t1) / (o.d1 ?? 0.3));
  const v = Math.min(a, b) * (o.max ?? 1);
  el.style.opacity = v;
  el.style.visibility = v < 0.002 ? 'hidden' : 'visible';
  const rot = o.rot != null ? ` rotate(${o.rot}deg)` : '';
  el.style.transform = `translate(${dx * (1 - a)}px, ${dy * (1 - a)}px)` + (o.scale ? ` scale(${lerp(o.scale, 1, a)})` : '') + rot;
  return v;
}
const PENDING = new Set();
function setSrc(img, src) { if (img.dataset.src !== src) { img.dataset.src = src; img.src = src; PENDING.add(img); } }
async function flush() {
  const arr = [...PENDING]; PENDING.clear();
  await Promise.all(arr.map(i => i.decode().catch(() => window.__ERR.push('图片加载失败 ' + i.dataset.src))));
}

// ─── 字幕条时间
const CU = {}; TL.cues.forEach(q => CU[q.id] = q);
const S = id => { if (!CU[id]) throw new Error('没有字幕条 ' + id); return CU[id].s; };
const E = id => { if (!CU[id]) throw new Error('没有字幕条 ' + id); return CU[id].e; };
function P(id, phrase, off = 0) {
  const q = CU[id]; const k = q.zh.indexOf(phrase);
  if (k < 0) throw new Error(`「${phrase}」不在 ${id}`);
  return q.s + (q.e - q.s) * (k / q.zh.length) + off;
}
const SEG = {}; TL.segs.forEach(s => SEG[s.id] = s);

const OV = [];   // {t0, t1, build(root) → update(lt), clip?:true（现场片段上的角标）}
const ovB = (t0, t1, build) => OV.push({ t0, t1, build });
const ovClip = (t0, t1, build) => OV.push({ t0, t1, build, clip: true });
function arrow(p, x0, y0, x1, y1, color) {
  const L = Math.hypot(x1 - x0, y1 - y0) - 30, ang = Math.atan2(y1 - y0, x1 - x0) * 180 / Math.PI;
  const w = at(p, 0, 0, 0, 0, '', { overflow: 'visible' });
  const a = at(w, x0, y0 - 4, L, 8, 'arrow', { transform: `rotate(${ang}deg)` });
  if (color) a.style.background = color;
  return w;
}

// ═════════════════════════════ 章节标签：每章第一段开头 3 秒（现场片段上也显示）
{
  const seen = new Set();
  TL.segs.forEach(s => {
    if (seen.has(s.chapter)) return; seen.add(s.chapter);
    ovClip(s.s + 0.3, s.s + 3.6, p => {
      const c = at(p, 22, 20, null, null, 'chapchip', { position: 'absolute' }, `<span>${String(s.chapter + 1).padStart(2, '0')}</span>${TL.chapters[s.chapter]}`);
      return lt => show(c, lt, 0, { dy: -12 });
    });
  });
}

// ═════════════════════════════ 现场片段：来源角标 + 讲话人 + “中文同传”（讲话人跟着当前的同传字幕走）
Object.entries(TL.clips).forEach(([cid, k]) => {
  const mine = TL.cues.filter(q => q.kind === 'clip' && q.seg === cid);
  ovClip(k.s + 0.1, k.e, p => {
    const narrow = !!(k.ui && k.ui.badgeRight != null);                    // 竖屏视频：只占中间一条，角标字短一点
    const c = at(p, null, 20, null, null, 'credit', { position: 'absolute', right: (narrow ? k.ui.badgeRight : 22) + 'px', fontSize: narrow ? '22px' : undefined }, '画面：' + k.credit + (narrow ? ' · 中文同传' : ' · 原声压低，中文同传'));
    const w = at(p, null, null, null, null, 'who', { position: 'absolute' }, '');
    if (k.ui && k.ui.whoLeft != null) w.style.left = k.ui.whoLeft + 'px';     // 竖屏视频居中，标签跟着视频左边缘走
    let last = '';
    return lt => {
      show(c, lt, 0, { dy: -8 });
      const t = k.s + 0.1 + lt;
      const cur = mine.find(q => t >= q.s - 0.25 && t < q.e + 0.6) || mine.find(q => q.s > t) || mine[mine.length - 1];
      const key = (cur && cur.who || '') + '|' + k.where;
      if (key !== last) { last = key; w.innerHTML = `${cur && cur.who || ''}<small>${k.where || ''}</small>`; }
      show(w, lt, 0.3, { dy: 8 });
    };
  });
});

// 片段上的小标签（例：片尾彩蛋）：片段开头 3 秒，位置跟着 ui.whoLeft 走
Object.entries(TL.clips).forEach(([cid, k]) => {
  if (!k.tag) return;
  ovClip(k.s + 0.25, k.s + 3.6, p => {
    const c = at(p, (k.ui && k.ui.whoLeft != null) ? k.ui.whoLeft : 22, (k.ui && k.ui.whoLeft != null) ? 78 : 20, null, null, 'chapchip', { position: 'absolute' }, `<span>${k.tag}</span>${k.where.split(' · ').pop()}`);
    return lt => show(c, lt, 0, { dy: -12 });
  });
});

// 文件原图：白底小相纸，贴在卡片旁（原图 525×680，用户给的；做了 2 倍放大 + 轻锐化）
function docPhoto(p, src, x, y, w) {
  const box = at(p, x, y, w + 14, null, '', { background: '#fff', padding: '7px', borderRadius: '6px', boxShadow: '0 16px 34px rgba(0,0,0,.28), 0 0 0 2px rgba(0,0,0,.07)' });
  const img = mk(box, '', { display: 'block', width: w + 'px', height: 'auto' }, '', 'img');
  setSrc(img, src);
  return box;
}

// ═════════════════════════════ 01 开场：300 字 + 六位签字人（N01–N02）
ovB(S('N01') - 0.3, E('N02') + 0.4, p => {
  const t0 = S('N01') - 0.3;
  const k = at(p, 0, 70, 1474, 40, 'kick', { textAlign: 'center' }, '白宫 · 2026年9月29日');
  const b = at(p, 0, 120, 1474, 260, 'big', { textAlign: 'center', fontSize: '230px', lineHeight: '1.1' }, '<span class="mark">300</span>字');
  const h = at(p, 0, 395, 1474, 80, 'h1', { textAlign: 'center' }, '《超级智能协定》· 一页纸');
  const ppl = [['皮查伊', '谷歌'], ['阿莫迪', 'Anthropic'], ['扎克伯格', 'Meta'], ['布罗克曼', 'OpenAI 总裁'], ['马斯克', 'xAI'], ['黄仁勋', '英伟达']]
    .map(([n, c], i) => at(p, 40 + (i % 3) * 470, 520 + Math.floor(i / 3) * 120, 440, 96, 'person', {}, `${n}<small>${c}</small>`));
  const tr = at(p, 0, 752, 1474, 60, '', { textAlign: 'center' }, '<span class="chip fill">+ 川普</span>&nbsp;&nbsp;<span class="chip">自愿签署</span>');
  return lt => {
    show(k, lt, 0.1); show(b, lt, 0.2, { scale: .92 }); show(h, lt, S('N01') - t0 + 0.6);
    ppl.forEach((e, i) => show(e, lt, S('N01') - t0 + 0.9 + i * 0.28, { dy: 12 }));
    show(tr, lt, S('N02') - t0);
  };
});

// ═════════════════════════════ 01 两份东西（N04–N05）
ovB(S('N04') - 0.2, E('N05') + 0.1, p => {
  const t0 = S('N04') - 0.2;
  const h = at(p, 0, 36, 1474, 70, 'h2', { textAlign: 'center' }, '签了<span class="mark">两份</span>东西');
  const c1 = at(p, 50, 130, 650, 560, 'card hot', {},
    '<span class="no">①</span><span class="tt">总统命令</span>' +
    '<div class="dd" style="font-size:34px;color:var(--ink);font-weight:800;margin-top:16px">川普一个人签的</div>' +
    '<div class="dd"><b>内容</b>　把“人工智能”改叫“超级智能”</div>' +
    '<div class="dd"><b>管谁</b>　只管联邦政府自己的文件</div>' +
    '<div class="dd"><b>约束</b>　不改法律，管不到公司</div>');
  const c2 = at(p, 774, 130, 650, 560, 'card', {},
    '<span class="no">②</span><span class="tt">《超级智能协定》</span>' +
    '<div class="dd" style="font-size:34px;color:var(--ink);font-weight:800;margin-top:16px">川普 + 6位负责人一起签</div>' +
    '<div class="dd"><b>内容</b>　给 AI 公司定四条规矩</div>' +
    '<div class="dd"><b>篇幅</b>　一页纸，300字</div>' +
    '<div class="dd"><b>约束</b>　自愿，没有处罚和期限</div>');
  const m2 = at(p, 1130, 118, null, null, 'chip fill', { position: 'absolute' }, '这份才是重点');
  const sgn = docPhoto(p, 'media/doc/协定签字页.png', 1140, 452, 258);      // 用户给的签字页：6 位负责人 + 川普的签名
  const sgcap = at(p, 790, 640, 330, 50, 'cap', { textAlign: 'right' }, '签字页：七个签名 →');
  return lt => {
    show(h, lt, 0);
    show(c1, lt, S('N04') - t0 - 0.2, { scale: .96 }); show(c2, lt, S('N05') - t0 - 0.2, { scale: .96 });
    show(sgn, lt, S('N05') - t0 + 0.45, { dy: 24, rot: 3 });
    show(sgcap, lt, S('N05') - t0 + 0.9, { dy: 8 });
    show(m2, lt, E('N05') - t0 - 0.2, { dy: -8 });
  };
});

// ═════════════════════════════ 02 第一份：总统命令（N07 起，K1 播放时自动让位）
ovB(S('N07') - 0.2, E('N11') + 0.9, p => {
  const t0 = S('N07') - 0.2;
  const hd = at(p, 0, 16, 1474, 70, 'h2', { textAlign: 'center' }, '第一份：<span class="mark">总统命令</span>，只是改名');
  const row = (y, no, tt, dd, hot) => at(p, 70, y, 1334, 150, 'card' + (hot ? ' hot' : ''), {}, `<span class="no">${no}</span><span class="tt">${tt}</span><div class="dd">${dd}</div>`);
  const r1 = row(130, '1', '只管政府自己', '美国联邦政府自己的文件里，“人工智能”改叫“超级智能”', true);
  const r2 = row(310, '2', '不改法律', '也管不到任何一家公司');
  const r3 = row(490, '3', '60 天内', '拿出一份建议：法律里的叫法，改不改？（11月28日前）');
  const gag = at(p, 960, 700, null, null, 'chip ink', { position: 'absolute', background: '#fff' }, '本视频不受此令约束');
  const st = at(p, 760, 330, null, null, 'stamp o', { fontSize: '86px' }, '改名不改法');
  return lt => {
    show(hd, lt, 0.1);
    show(r1, lt, S('N09') - t0, { dy: 14 }); show(r2, lt, P('N09', '不改法律') - t0 - 0.2, { dy: 14 });
    show(gag, lt, S('N10') - t0, { dy: 8 });
    show(r3, lt, S('N11') - t0, { dy: 14 });
    show(st, lt, E('N11') - t0 - 0.3, { scale: 1.5, dy: 0, rot: -8 });
    [r1, r2, r3].forEach(e => e.classList.toggle('dim', lt >= E('N11') - t0 - 0.3));
  };
});

// ═════════════════════════════ 03 第二份：协定写了啥（N12–N19，K2 播放时自动让位）
// 左边四层卡片，右边是协定原文那一页（用户给的图），读到哪一条，原文里对应的那一段就刷上荧光笔
ovB(S('N12') - 0.2, E('N19') + 0.5, p => {
  const t0 = S('N12') - 0.2;
  const LW = 800;                                   // 左栏宽度
  const PW = 556;                                   // 原文那一页的宽度（原图 525×680）
  const hd = at(p, 40, 28, LW, 70, 'h2', {}, '协定要求的<span class="mark">四件事</span>');
  const tc = at(p, 0, 170, 900, 460, '', {}, '');
  mk(tc, '', { textAlign: 'center' }, '<div class="kick" style="font-size:28px">第二份 · 重点</div>');
  mk(tc, '', { textAlign: 'center', marginTop: '26px', font: "900 80px/1.25 'Noto Sans SC'" }, '《超级智能协定》');
  mk(tc, '', { textAlign: 'center', marginTop: '10px', font: "800 46px/1.35 'Noto Sans SC'", color: 'var(--ink2)' }, '做最强 AI 的公司，<br>要自己管好自己');
  mk(tc, '', { textAlign: 'center', marginTop: '44px' }, '<span class="chip fill">一页纸</span>&nbsp;&nbsp;<span class="chip">约300字</span>&nbsp;&nbsp;<span class="chip ink">自愿</span>');
  const L = (y, cls, n, tt, dd, dd2) => at(p, 40, y, LW, 150, 'layer ' + cls, { left: '40px', width: LW + 'px' }, `<div class="n">${n}</div><div><div class="tt">${tt}</div><div class="dd">${dd}</div>${dd2 ? `<div class="dd" style="color:#9F1239;font-weight:800">${dd2}</div>` : ''}</div>`);
  const l1 = L(110, 'l1', '1', '自己先检查', '盯着网络、生物、化学这几类危险', 'AI 别乱闯别人的系统');
  const l2 = L(275, 'l2', '2', '专门的团队', '确认这些检查，是真的在做');
  const l3 = L(440, 'l3', '3', '外面的人再查', '请独立的第三方，再检查一遍');
  const l4 = L(605, 'l4', '4', '董事会盯着', '董事会里设一个小组：听汇报，督促改正');
  const st = at(p, 540, 44, null, null, 'stamp o', { fontSize: '50px' }, '别越狱');
  const ft = at(p, 40, 772, LW, 56, '', { textAlign: 'center' }, '<span class="chip fill">+ 各家定期开会，一起定标准</span>&nbsp;&nbsp;<span class="chip fill">+ 以后，可能写进法律</span>');
  // 原文那一页 + 荧光笔（坐标是原图像素：第 y0–y1 行）
  const pg = docPhoto(p, 'media/doc/协定正文页.png', 1474 - 40 - PW - 14, 36, PW);
  const sc = PW / 525;
  const hl = (y0, y1, x0 = 54, x1 = 472) => mk(pg, '', { position: 'absolute', left: (7 + x0 * sc) + 'px', top: (7 + y0 * sc) + 'px', width: ((x1 - x0) * sc) + 'px', height: ((y1 - y0) * sc) + 'px',
    background: 'rgba(255,205,40,.62)', mixBlendMode: 'multiply', borderRadius: '5px', transformOrigin: '0 50%', visibility: 'hidden' });
  const h1 = hl(242, 294, 88, 468), h2 = hl(307, 335, 88, 468), h3 = hl(346, 388, 88, 468), h4 = hl(398, 437, 88, 468);
  const hA = hl(489, 515), hB = hl(528, 580);       // “定期开会、定标准” / “以后写进法律”
  const marks = [[h1, 'N14'], [h2, 'N15'], [h3, 'N16'], [h4, 'N17']].map(([e, id]) => ({ e, t: S(id) - t0 + 0.1 }));
  marks.push({ e: hA, t: S('N18') - t0 + 0.2 }, { e: hB, t: P('N18', '以后') - t0 - 0.1 });
  return lt => {
    const lay = S('N13') - t0 - 0.1;
    show(tc, lt, 0.2, { dy: 10, t1: lay, d1: 0.3 });
    show(hd, lt, lay + 0.1);
    show(l1, lt, S('N14') - t0 - 0.1, { dy: 14 }); show(l2, lt, S('N15') - t0 - 0.1, { dy: 14 }); show(l3, lt, S('N16') - t0 - 0.1, { dy: 14 }); show(l4, lt, S('N17') - t0 - 0.1, { dy: 14 });
    l1.children[1].children[2].style.opacity = clamp((lt - (P('N14', 'AI 别乱闯') - t0)) / 0.3);
    show(st, lt, P('N14', '别越狱') - t0 + 0.2, { scale: 1.5, dy: 0, rot: -6 });
    show(ft, lt, S('N18') - t0 + 0.2);
    show(pg, lt, S('N12') - t0 + 0.5, { dx: 70, dy: 0, rot: 1.2 });
    marks.forEach((m, i) => {                        // 刷上去（从左往右 0.45 s），后面的出来时前面的变淡
      const a = easeOut((lt - m.t) / 0.45), nxt = marks[i + 1] ? marks[i + 1].t : 1e9;
      m.e.style.visibility = a > 0.001 ? 'visible' : 'hidden';
      m.e.style.transform = `scaleX(${a})`;
      m.e.style.opacity = i < 4 && lt > nxt ? 0.38 : 1;
    });
  };
});

// ═════════════════════════════ 04 没写的，才是重点（N20–N26）
ovB(S('N20') - 0.2, E('N26') + 0.5, p => {
  const t0 = S('N20') - 0.2;
  const SRC = [
    ['01', '什么算“最强的 AI”', ['N21', '什么算'], ''],
    ['02', '找谁来检查、谁挑、谁出钱', ['N21', '找谁来检查'], ''],
    ['03', '结果公不公开', ['N21', '结果公不公开'], ''],
    ['04', '做不到怎么办', ['N22', '做不到'], '没有处罚 · 没有期限 · 没有“下次一定”'],
    ['05', '出事要不要上报，政府管不管', ['N23', '出了事'], ''],
  ];
  const items = SRC.map(([k, tt, [id, ph], sub], i) => {
    const last = i === SRC.length - 1 && i % 2 === 0;   // 落单的最后一条：通栏，文字不会压到“没写”章下面
    const el = at(p, 50 + (last ? 0 : (i % 2) * 706), 100 + Math.floor(i / 2) * 192, last ? 1374 : 668, 172, 'miss', {},
      `<div class="k">${k}</div><div class="tt">${tt}</div>${sub ? `<div style="font:600 24px 'Noto Sans SC';color:var(--gray);margin-top:6px">${sub}</div>` : ''}<div class="st">没写</div>`);
    return { el, t: P(id, ph), stamp: el.querySelector('.st') };
  });
  const hd = at(p, 0, 22, 1474, 64, 'h2', { textAlign: 'center' }, '协定里<span class="mark">没写</span>的');
  const bn = at(p, 70, 690, 1334, 110, 'banner', {}, '执行方式：<em>全靠自觉</em>');
  return lt => {
    show(hd, lt, S('N20') - t0);
    items.forEach(it => { show(it.el, lt, it.t - t0 - 0.35, { dy: 12 }); show(it.stamp, lt, it.t - t0 + 0.7, { scale: 1.8, dy: 0, rot: -7 }); });
    show(bn, lt, S('N24') - t0, { scale: .96 });
  };
});
// 出卷 = 判卷 = 监考（N27）
ovB(S('N27') - 0.3, E('N27') + 1.2, p => {
  const t0 = S('N27') - 0.3;
  const mkn = (x, tt, sm) => at(p, x, 230, 380, 230, 'node bad', {}, `${tt}<small>${sm}</small>`);
  const n1 = mkn(70, '出卷', '公司自己'), n2 = mkn(547, '判卷', '自己请的老师'), n3 = mkn(1024, '监考', '公司自己');
  const a1 = arrow(p, 462, 345, 540, 345, '#9AA1AC'), a2 = arrow(p, 939, 345, 1017, 345, '#9AA1AC');
  const bn = at(p, 70, 560, 1334, 120, 'banner', {}, '出卷、判卷、监考，<em>都在同一家</em>');
  // 开头先放川普对这份协定的说法，等说到“可是”再换成三个角色（不然前三秒演示区是空的）
  const q = at(p, 0, 150, 1474, 400, '', { textAlign: 'center' },
    '<div class="kick" style="font-size:28px">川普这样形容这份协定</div>' +
    '<div style="margin-top:26px;font:900 104px/1.25 \'Noto Sans SC\'">“<span class="mark">道德上</span>有约束力”</div>' +
    '<div style="margin-top:14px;font:800 56px/1.3 \'Noto Sans SC\';color:var(--ink2)">“几乎像一部宪法”</div>');
  return lt => {
    show(q, lt, 0.1, { dy: 10, t1: P('N27', '可是') - t0 - 0.1, d1: 0.3 });
    show(n1, lt, P('N27', '出卷的') - t0, { scale: .92 }); show(a1, lt, P('N27', '判卷的') - t0 - 0.2, { dy: 0, dx: -10 });
    show(n2, lt, P('N27', '判卷的') - t0, { scale: .92 }); show(a2, lt, P('N27', '监考的') - t0 - 0.2, { dy: 0, dx: -10 });
    show(n3, lt, P('N27', '监考的') - t0, { scale: .92 }); show(bn, lt, E('N27') - t0 - 0.3);
  };
});

// ═════════════════════════════ 05 为啥现在签（N28–N32）
ovB(S('N28') - 0.2, E('N32') + 0.8, p => {
  const t0 = S('N28') - 0.2;
  const hd = at(p, 0, 30, 1474, 64, 'h2', { textAlign: 'center' }, '为啥偏偏<span class="mark">现在</span>签');
  const rows = [
    ['今年', 'OpenAI 和 Anthropic 的 AI，先后在测试里，闯进了别人的系统', '', 'N29', ''],
    ['9月30日', '美国联邦贸易委员会，开始调查这些公司', '管市场和消费者的部门', 'N30', ''],
    ['民调', '<b style="color:var(--orange)">86%</b> 的美国人要有独立的安全标准，哪怕拖慢发展', '昆尼皮亚克大学，9月下旬，1,202名成年人', 'N31', 'fin'],
  ].map(([d, x, sm, id, cls], i) => ({ id, el: at(p, 60, 150 + i * 170, 1350, 140, 'tl ' + cls, { height: '140px' }, `<div class="d">${d}</div><div class="x">${x}${sm ? `<small>${sm}</small>` : ''}</div>`) }));
  const bn = at(p, 70, 690, 1334, 100, 'banner', { fontSize: '46px' }, '这份协定，是被这些事<em>推出来</em>的');
  return lt => { show(hd, lt, 0.1); rows.forEach(r => show(r.el, lt, S(r.id) - t0 - 0.2, { dy: 14 })); show(bn, lt, S('N32') - t0 - 0.1, { scale: .96 }); };
});

// ═════════════════════════════ 05 会改变啥：三个看点（N33–N40，K6 播放时自动让位）
ovB(S('N33') - 0.2, E('N40') + 0.5, p => {
  const t0 = S('N33') - 0.2;
  const bn = at(p, 70, 40, 1334, 100, 'banner', { fontSize: '44px' }, '短期：<em>几乎不改变</em>任何公司要遵守的法律');
  const mkc = (x, y, w, k, tt, dd) => at(p, x, y, w, 300, 'sig', { width: w + 'px' }, `<div class="k">${k}</div><div class="tt">${tt}</div><div class="dd">${dd}</div>`);
  const c1 = mkc(40, 168, 690, '看点 1', '谁来定标准，被推迟了', '夏天想成立统一的行业组织（据报道）<br>最后：<b>各家自己管，没有统一机构</b>');
  const c2 = mkc(744, 168, 690, '看点 2', '真正能管事的，在别处', '<b>监管部门的调查</b> · <b>加州已有的法律</b> · <b>OpenAI 被告上法院</b>');
  const c3 = mkc(40, 498, 1394, '看点 3', '管得有限', '只管签字的6家：微软、亚马逊的老板在场，<b>但没签</b>；<b>开源模型、美国以外的公司</b>都不在里面');
  const end = at(p, 70, 300, 1334, 230, 'banner', { fontSize: '80px', lineHeight: '1.5', paddingTop: '30px' }, '纸上有四条规矩，<em>地上没人查</em>');
  return lt => {
    show(bn, lt, 0, { dy: -10 });
    show(c1, lt, S('N35') - t0 - 0.1, { dy: 14 }); show(c2, lt, S('N38') - t0 - 0.1, { dy: 14 }); show(c3, lt, S('N39') - t0 - 0.1, { dy: 14 });
    const d = easeOut((lt - (S('N40') - t0 - 0.1)) / 0.4);
    [c1, c2, c3, bn].forEach(e => e.style.filter = d > 0 ? `opacity(${1 - 0.8 * d})` : '');
    show(end, lt, S('N40') - t0, { scale: .94 });
  };
});

// ═════════════════════════════ 05 接下来看三件事（N41–N45，K7 播放时自动让位）
ovB(S('N41') - 0.3, E('N45') + 1.6, p => {
  const t0 = S('N41') - 0.3;
  const hd = at(p, 0, 12, 1474, 64, 'h2', { textAlign: 'center' }, '接下来，看<span class="mark">三件事</span>');
  const items = [
    ['管 AI 的总负责人', '美国叫“AI 沙皇”，川普说几天内公布', 'N42'],
    ['约十人的委员会', '会不会成立，来监督整个行业', 'N43'],
    ['微软、亚马逊这些没签的', '会不会跟着签', 'N44'],
  ].map(([tt, sm, id], i) => ({ id, el: at(p, 120, 130 + i * 150, 1234, 120, 'watch', { height: '120px' }, `<div class="n">${i + 1}</div><div>${tt}<small>${sm}</small></div>`) }));
  const bn = at(p, 70, 640, 1334, 120, 'banner', { fontSize: '52px' }, '这份文件，挡得住 AI 的洪流吗？');
  return lt => {
    show(hd, lt, 0);
    items.forEach(r => show(r.el, lt, S(r.id) - t0 - 0.1, { dy: 12, dx: 20 }));
    show(bn, lt, S('N45') - t0 + 0.4, { scale: .95 });
  };
});
