// 工具 + 叠加层（版式 A 右侧要点；版式 B 演示区上的章节标签、提示、手机演示的步骤卡）+ 演示①邮件段的打码静帧推近。
// 每个叠加层：[t0, t1] 显示（前后淡入淡出），t 用成片秒数；时间都按字幕条算：S('C07') = 这条开始说的时刻，P('C07', '数据') = 说到这个词的时刻。
// 字幕条：C01–C28 开场真人出镜（DJI 0163），R01–R22 录屏口播、M01–M09 手机画外音（都是克隆声音「悠一」）。
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
  const v = Math.min(a, b);
  el.style.opacity = v;
  el.style.visibility = v < 0.002 ? 'hidden' : 'visible';
  el.style.transform = `translate(${dx * (1 - a)}px, ${dy * (1 - a)}px)` + (o.scale ? ` scale(${lerp(o.scale, 1, a)})` : '');
  return v;
}
const PENDING = new Set();
function setSrc(img, src) { if (img.dataset.src !== src) { img.dataset.src = src; img.src = src; PENDING.add(img); } }
async function flush() {
  const arr = [...PENDING]; PENDING.clear();
  await Promise.all(arr.map(i => i.decode().catch(() => window.__ERR.push('图片加载失败 ' + i.dataset.src))));
}
function image(parent, src, style = {}) { const i = mk(parent, '', style, '', 'img'); setSrc(i, src); return i; }

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

const OV = [];   // {where:'A'|'B', t0, t1, build(root) → update(lt)}
const ovA = (t0, t1, build) => OV.push({ where: 'A', t0, t1, build });
const ovB = (t0, t1, build) => OV.push({ where: 'B', t0, t1, build });
function arrow(p, x0, y0, x1, y1, color) {
  const L = Math.hypot(x1 - x0, y1 - y0) - 30, ang = Math.atan2(y1 - y0, x1 - x0) * 180 / Math.PI;
  const w = at(p, 0, 0, 0, 0, '', { overflow: 'visible' });
  const a = at(w, x0, y0 - 4, L, 8, 'arrow', { transform: `rotate(${ang}deg)` });
  if (color) { a.style.background = color; a.style.setProperty('--c', color); }
  return w;
}

// ═════════════════════════════ 版式 A：开场（真人出镜，C01–C28 = 用户实际说的）
// SA1 开场白
ovA(S('C01') - 0.3, S('C05') - 0.35, p => {
  const k = at(p, 0, 96, 880, 40, 'kick', {}, '悠一 · 2026 年 10 月');
  const b = at(p, 0, 150, 880, 110, 'big', {}, '订阅正版');
  const h = at(p, 0, 268, 880, 90, 'h1', {}, '<span class="mark">Codex</span> / <span class="mark">Claude Code</span>');
  const c = at(p, 0, 400, 880, 60, '', {}, '<span class="chip fill">两种方式</span>&nbsp;&nbsp;<span class="chip">非中转</span>&nbsp;&nbsp;<span class="chip">非代充</span>');
  const d = at(p, 0, 486, 880, 60, 'cap', { fontSize: '30px' }, '自己就能操作，钱直接付给官方');
  const t0 = S('C01') - 0.3;
  return lt => { show(k, lt, 0); show(b, lt, 0.15); show(h, lt, P('C03', 'Codex') - t0); show(c, lt, S('C04') - t0); show(d, lt, S('C04') - t0 + 0.4); };
});
// SA2 为什么不推荐中转、代充
ovA(S('C05'), S('C16') - 0.35, p => {
  const t0 = S('C05');
  const h = at(p, 0, 0, 880, 60, 'h2', {}, '为什么<span class="mark">不推荐</span>中转、代充');
  const c1 = at(p, 0, 92, 880, 262, 'card2 bad');
  mk(c1, 'tt', {}, '中转');
  const fl = mk(c1, '', { position: 'relative', height: '112px', marginTop: '14px' });
  const n1 = at(fl, 0, 10, 170, 92, 'node', {}, '你');
  const n2 = at(fl, 300, 0, 210, 112, 'node mid', {}, '中转站');
  const n3 = at(fl, 640, 10, 170, 92, 'node', {}, '官方');
  const a1 = arrow(fl, 178, 56, 296, 56, '#9AA1AC'), a2 = arrow(fl, 518, 56, 636, 56, '#9AA1AC');
  const d1 = mk(c1, 'dd', { color: '#9F1239' }, '数据先从中转站转一遍 → 有厂商会贩卖你的聊天记录');
  const c2 = at(p, 0, 380, 880, 214, 'card2 bad');
  mk(c2, 'tt', {}, '代充');
  const l = ['凭证安全泄露', '别人跑路了，没法续费', '信息内容要导出来很麻烦'].map(x => mk(c2, 'dd', { color: '#9F1239', marginTop: '2px' }, '· ' + x));
  const tip = at(p, 0, 612, 880, 60, '', {}, '<span class="chip fill">小白别轻易走代充</span>');
  return lt => {
    show(h, lt, 0);
    show(c1, lt, S('C07') - t0 - 0.1);
    [n1, a1, n2, a2, n3].forEach((e, i) => show(e, lt, P('C07', '数据') - t0 + i * 0.16, { dy: 0, dx: -10 }));
    show(d1, lt, P('C10', '贩卖') - t0);
    show(c2, lt, S('C11') - t0 - 0.1);
    show(l[0], lt, P('C11', '凭证') - t0, { dy: 0 }); show(l[1], lt, P('C12', '跑路') - t0, { dy: 0 }); show(l[2], lt, S('C14') - t0, { dy: 0 });
    show(tip, lt, P('C15', '小白') - t0, { scale: .9 });
  };
});
// SA3 只推荐两种方法
ovA(S('C16'), S('C22') - 0.35, p => {
  const t0 = S('C16');
  const h = at(p, 0, 0, 880, 60, 'h2', {}, '只推荐<span class="mark">两种方法</span>');
  const o1 = at(p, 0, 92, 880, 270, 'opt', { height: '270px' }, '<div class="k">01 · 苹果用户</div><div class="tt">美区 Apple ID</div><div class="dd">买美金的 Apple Card（礼品卡）</div><div class="dd">→ 走苹果的官方支付</div>');
  const o2 = at(p, 0, 392, 880, 270, 'opt', { height: '270px' }, '<div class="k">02 · 安卓用户</div><div class="tt">Google Play</div><div class="dd">绑定国内的 Visa 卡等</div><div class="dd">→ 在商店里购买</div>');
  return lt => { show(h, lt, 0); show(o1, lt, S('C17') - t0, { scale: .96 }); show(o2, lt, S('C20') - t0, { scale: .96 }); };
});
// SA4 推荐 UP 主（安卓）
ovA(S('C22'), S('C26') - 0.35, p => {
  const t0 = S('C22');
  const h = at(p, 0, 0, 880, 60, 'h2', {}, '安卓：参考这位 UP 主');
  const v = at(p, 0, 84, 430, 337, 'img', { overflow: 'hidden' });
  image(v, 'media/up_video.png', { width: '100%', height: '100%', display: 'block' });
  const a = at(p, 452, 84, 428, 98, 'img', { overflow: 'hidden' });
  image(a, 'media/up_account.png', { width: '100%', height: '100%', display: 'block' });
  const cap = at(p, 452, 200, 428, 230, 'cap', { color: 'var(--ink2)' },
    '<b style="color:var(--ink);font-size:30px">AI引导世界</b><br>《国内安卓手机直订 ChatGPT plus | Google Play渠道》<br><span style="font:600 22px Space Grotesk;color:var(--gray2)">BV16uhN68EgX · 2026-08-25</span>');
  const dis = at(p, 0, 450, 880, 60, '', {}, '<span class="chip ink" style="font-size:24px">仅做方法推荐，不代表推荐他店铺内的任何商品</span>');
  const ok = at(p, 0, 530, 880, 120, 'card2 ok', { padding: '20px 26px' }, '<div class="tt" style="font-size:34px">这种方法是可以的</div><div class="dd">国内 Visa 卡绑定 Google Play，在商店里订阅</div>');
  return lt => {
    show(h, lt, 0); show(v, lt, P('C22', '参考') - t0, { scale: .96 }); show(a, lt, P('C22', 'UP') - t0, { scale: .96 }); show(cap, lt, P('C22', 'UP') - t0 + 0.3);
    show(dis, lt, S('C23') - t0); show(ok, lt, S('C25') - t0);
  };
});
// SA5 接下来演示苹果 + 我自己的订阅截图（用量页 Max (5x)、苹果内购弹窗，账户邮箱已打码）
ovA(S('C26'), SEG.SA5.e + 0.3, p => {
  const t0 = S('C26');
  const h = at(p, 0, 0, 880, 60, 'h2', {}, '下面演示：<span class="mark">苹果的方式</span>');
  const u = at(p, 0, 92, 516, 323, 'img', { overflow: 'hidden' });
  image(u, 'media/usage.png', { width: '100%', height: '100%', display: 'block' });
  const uc = at(p, 0, 428, 516, 80, 'cap', {}, 'Claude 用量页：<b style="color:var(--ink)">Max (5x)</b>');
  const iw = 330, ih = 560;
  const iv = at(p, 550, 70, iw, ih, 'img', { overflow: 'hidden', background: '#9a9a9a' });
  image(iv, 'media/iap.jpg', { position: 'absolute', left: '0px', top: px(-440 * iw / 920), width: px(iw), display: 'block' });
  const ic = at(p, 550, 640, iw, 40, 'cap', { textAlign: 'center' }, '苹果内购：Claude Max 5x');
  const me = at(p, 0, 520, 516, 80, '', {}, '<span class="chip fill">我自己就是这么订的</span>');
  return lt => {
    show(h, lt, 0); show(u, lt, S('C28') - t0 - 0.2, { scale: .96 }); show(uc, lt, S('C28') - t0);
    show(iv, lt, S('C28') - t0 + 0.3, { scale: .96 }); show(ic, lt, S('C28') - t0 + 0.5); show(me, lt, S('C28') - t0 + 0.6, { scale: .9 });
  };
});

// ═════════════════════════════ 版式 B：演示区
// 章节标签：每个版式 B 段开头 3 秒
TL.segs.forEach(s => {
  if (s.layout !== 'B') return;
  ovB(s.s + 0.5, s.s + 3.8, p => {
    const c = at(p, 22, 20, null, null, 'chapchip', { position: 'absolute' }, `<span>${String(s.chapter + 1).padStart(2, '0')}</span>${TL.chapters[s.chapter]}`);
    return lt => show(c, lt, 0, { dy: -12 });
  });
});

// 演示①：录屏原片部分的步骤提示（右上角）
const PC_T0 = TL.pc.t0;
const STILL_T0 = TL.pc.still_t0;     // 邮件段（打码静帧）从这里开始（录屏按新配音伸缩过，build_timeline.py 换算好的）
[
  [S('R01'), S('R09'), '① 先搜：美区礼品卡在哪买'],
  [S('R09'), S('R12'), '② 我用的：<b>Pockyt Shop</b> · App Store & iTunes US'],
  [S('R12'), S('R15'), '③ 支付宝 / 微信付款，按当天汇率'],
  [S('R15'), STILL_T0, '④ 最低 2 美元 · 登录后付款'],
].forEach(([t0, t1, txt]) => ovB(t0 - 0.1, t1 - 0.2, p => {
  const c = at(p, null, 22, null, null, 'pill', { right: '22px', position: 'absolute' }, txt);
  return lt => show(c, lt, 0, { dy: -10 });
}));
// 购卡须知（画面上能看到那几秒）
ovB(S('R14') - 0.2, E('R15') + 0.2, p => {
  const c = at(p, 22, null, null, null, 'pill warn', { bottom: '22px', position: 'absolute' }, '页面须知：这张卡只能用在<b style="color:#B45309">美区 Apple ID</b>');
  return lt => show(c, lt, 0);
});

// 演示①：邮件段换成打码静帧，做推近（录屏里卡号、邮箱一直在缩放滚动，逐帧打码不可靠）
// 静帧原图 1920×1080，演示区 1474×829；镜头 = 焦点（原图像素）+ 放大倍数（1 = 刚好铺满）
const STILLS = [
  { src: 'media/still_list.jpg', t0: STILL_T0, t1: S('R19') - 0.1, k0: [960, 540, 1.0], k1: [930, 330, 1.45] },
  { src: 'media/still_mail.jpg', t0: S('R19') - 0.1, t1: S('R21') - 0.1, k0: [1060, 560, 1.25], k1: [1062, 650, 1.9] },
  { src: 'media/still_zoom.jpg', t0: S('R21') - 0.1, t1: SEG.S6.e + 0.01, k0: [720, 640, 1.08], k1: [720, 640, 1.22] },
];
const STW = 1474, STH = 829;
function stillXf(k) {
  const [cx, cy, z] = k, s = z * STW / 1920;
  let x = STW / 2 - cx * s, y = STH / 2 - cy * s;
  x = Math.min(0, Math.max(STW - 1920 * s, x)); y = Math.min(0, Math.max(STH - 1080 * s, y));
  return { x, y, s };
}
// 原图上的一个框 → 演示区坐标（跟着当前镜头）
function stillBox(sh, t, x0, y0, x1, y1) {
  const g = easeIO((t - sh.t0) / (sh.t1 - sh.t0));
  const a = stillXf(sh.k0), b = stillXf(sh.k1);
  const x = lerp(a.x, b.x, g), y = lerp(a.y, b.y, g), s = lerp(a.s, b.s, g);
  return { left: x + x0 * s, top: y + y0 * s, width: (x1 - x0) * s, height: (y1 - y0) * s };
}
ovB(STILL_T0 - 0.05, STILL_T0 + 2.6, p => {
  const c = at(p, null, 22, null, null, 'pill', { right: '22px', position: 'absolute' }, '⑤ 打开邮箱，搜 <b>Pockyt</b>');
  return lt => show(c, lt, 0.2, { dy: -10 });
});
ovB(S('R18'), S('R19') - 0.15, p => {     // 列表里两封“Here's your Gift Card!”
  const b1 = at(p, 0, 0, 0, 0, 'hl'), b2 = at(p, 0, 0, 0, 0, 'hl');
  return lt => {
    const t = S('R18') + lt;
    Object.assign(b1.style, Object.fromEntries(Object.entries(stillBox(STILLS[0], t, 432, 355, 1100, 380)).map(([k, v]) => [k, px(v)])));
    Object.assign(b2.style, Object.fromEntries(Object.entries(stillBox(STILLS[0], t, 432, 430, 1100, 455)).map(([k, v]) => [k, px(v)])));
    show(b1, lt, 0.6, { dy: 0 }); show(b2, lt, 0.9, { dy: 0 });
  };
});
ovB(S('R21') - 0.1, SEG.S6.e - 0.4, p => {     // 卡号那一行（已打码）
  const b = at(p, 0, 0, 0, 0, 'hl');
  const c = at(p, 0, 0, null, null, 'pill', { position: 'absolute' }, '兑换码（已打码）');
  return lt => {
    const r = stillBox(STILLS[2], S('R21') - 0.1 + lt, 496, 602, 962, 650);
    Object.assign(b.style, { left: px(r.left - 10), top: px(r.top - 8), width: px(r.width + 20), height: px(r.height + 16) });
    Object.assign(c.style, { left: px(r.left + r.width + 30), top: px(r.top - 6) });
    show(b, lt, 0.3, { dy: 0, scale: 1.08 }); show(c, lt, 0.6, { dx: -12, dy: 0 });
  };
});
ovB(S('R22') - 0.1, SEG.S6.e - 0.4, p => {
  const c = at(p, 22, null, null, null, 'pill', { bottom: '22px', position: 'absolute' }, '复制兑换码 → 去手机上兑换');
  return lt => show(c, lt, 0);
});

// 手机演示：右边的步骤卡（手机在演示区左边 150–540）
function steps(p, list, x = 600, y0 = 120, gap = 150) {
  return list.map(([no, tt, dd], i) => at(p, x, y0 + i * gap, 800, null, 'step', {},
    `<div class="no">${no}</div><div><div class="tt">${tt}</div>${dd ? `<div class="dd">${dd}</div>` : ''}</div>`));
}
function stepState(els, lt, times, base) {
  els.forEach((e, i) => {
    show(e, lt, times[i] - base, { dx: 20, dy: 0 });
    const on = lt >= times[i] - base && (i + 1 >= times.length || lt < times[i + 1] - base);
    e.classList.toggle('on', on); e.classList.toggle('done', !on && lt >= times[i] - base);
  });
}
ovB(S('M01') - 0.3, SEG.S7.e - 0.4, p => {
  const t0 = S('M01') - 0.3;
  const els = steps(p, [['1', 'App Store → 右上角头像', '账户页能看到余额'], ['2', '兑换代码 → 手动输入兑换码', ''], ['3', '填入邮件里的兑换码', '余额到账']], 600, 130, 170);
  return lt => stepState(els, lt, [S('M01'), S('M02'), S('M03')], t0);
});
ovB(S('M04') - 0.3, SEG.S8.e, p => {
  const t0 = S('M04') - 0.3;
  const els = steps(p, [['1', 'Claude App 里选好套餐', '弹出苹果的付款窗口'], ['2', '按两下侧边按钮确认', '先扣账户余额'], ['3', '设置 → 账单 → 管理订阅', '能看到 Claude Max 5x']], 600, 60, 160);
  const price = at(p, 600, 560, 800, null, 'note', {}, 'Max 5x：App 内 <b>$124.99 / 月</b>，官网 <b>$100 / 月</b>');
  const tip = at(p, 600, 680, 800, null, 'note', { fontSize: '27px' }, '没绑卡：余额要够<b>一整个月</b>，续费也一样');
  const cx = at(p, 22, null, null, null, 'pill', { bottom: '22px', position: 'absolute' }, 'Codex：打开 <b>ChatGPT App</b> 订阅，步骤一样');
  return lt => { stepState(els, lt, [S('M04'), S('M05'), S('M06')], t0); show(price, lt, S('M07') - t0); show(tip, lt, S('M08') - t0); show(cx, lt, S('M04') - t0 + 0.6, { t1: S('M06') - t0 }); };
});
// 提醒（克隆声音 W01–W03；事实 2026-10-01 查：两家支持地区列表、苹果美区礼品卡条款）
ovB(SEG.S9.s + 0.05, TL.total + 1, p => {
  const t0 = SEG.S9.s + 0.05;
  const c = at(p, 137, 96, 1200, null, 'warn', { position: 'absolute' }, '<div class="tt">⚠ 最后提醒一句</div>');
  const l1 = mk(c, 'ln', {}, '<i></i><div>Claude、ChatGPT 官方支持的地区<br><b>都不包括中国大陆</b></div>');
  const l2 = mk(c, 'ln', {}, '<i></i><div>在国内用有<b>封号的风险</b></div>');
  const l3 = mk(c, 'ln', {}, '<i></i><div>礼品卡买了<b>不能退</b>，大家自己评估<small>苹果美区礼品卡条款：不能兑换现金、不能退款</small></div>');
  const src = at(p, 137, 712, 1200, null, 'src', { position: 'absolute' }, '来源（2026-10-01 查）：anthropic.com/supported-countries · OpenAI 支持国家和地区列表 · Apple Gift Card 条款');
  return lt => { show(c, lt, 0, { scale: .97 }); show(l1, lt, S('W01') - t0 + 0.6, { dy: 0 }); show(l2, lt, P('W02', '在国内') - t0, { dy: 0 }); show(l3, lt, S('W03') - t0, { dy: 0 }); show(src, lt, S('W03') - t0 + 0.8); };
});
