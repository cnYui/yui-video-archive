// 工具 + 叠加层（版式 A 右侧要点、版式 B 演示区上的截图卡片 / 提示条）。
// 每个叠加层：[t0, t1] 显示（前后淡入淡出），t 用成片秒数；时间都按字幕条算：S('O17') = 这条开始说的时刻，P('O21', 'CLI') = 说到“CLI”的时刻。
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
function P(id, phrase, off = 0) {   // 这条字幕里说到某个词的时刻（按字数比例估）
  const q = CU[id]; const k = q.zh.indexOf(phrase);
  if (k < 0) throw new Error(`「${phrase}」不在 ${id}`);
  return q.s + (q.e - q.s) * (k / q.zh.length) + off;
}

// ─── 截图（素材\截图）
const SHOT = {
  s01: { src: '../../素材/截图/01_开发者工具安全设置_服务端口.png', w: 1075, h: 811 },
  s02: { src: '../../素材/截图/02_CloudBase_CLI查数据库和云函数.png', w: 1095, h: 757 },
  s03: { src: '../../素材/截图/03_能否使用微信开发者工具CLI.png', w: 881, h: 731 },
  s04: { src: '../../素材/截图/04_云开发入口_工具栏.png', w: 523, h: 194 },
};
// 截图卡：返回卡片元素；k = 缩放
function shotCard(p, key, x, y, k) {
  const s = SHOT[key];
  const c = at(p, x, y, s.w * k + 24, s.h * k + 24, 'shot');
  image(c, s.src);
  return c;
}
// 红箭头：从 (x0,y0) 指到 (x1,y1)（箭头尖在终点）。外层给 show() 做淡入位移，里层负责旋转（show 会改 transform）
function arrow(p, x0, y0, x1, y1, color) {
  const L = Math.hypot(x1 - x0, y1 - y0) - 40, ang = Math.atan2(y1 - y0, x1 - x0) * 180 / Math.PI;
  const w = at(p, 0, 0, 0, 0, '', { overflow: 'visible' });
  const a = at(w, x0, y0 - 5, L, 10, 'arrow', { transform: `rotate(${ang}deg)` });
  if (color) { a.style.background = color; a.style.setProperty('--ac', color); a.classList.add('c'); }
  return w;
}

const OV = [];   // {where:'A'|'B', t0, t1, build(root) → update(lt)}
const ovA = (t0, t1, build) => OV.push({ where: 'A', t0, t1, build });
const ovB = (t0, t1, build) => OV.push({ where: 'B', t0, t1, build });

// ═════════════════════════════ 版式 A：开场口播的要点（右侧 880×666）
ovA(S('O01') - 0.3, E('O03') + 0.5, p => {
  const k = at(p, 0, 120, 880, 40, 'kick', {}, '悠一 · AI 实操');
  const b = at(p, 0, 176, 880, 110, 'big', {}, '从 0 到 1');
  const h = at(p, 0, 304, 880, 150, 'h1', {}, '用 WorkBuddy<br>上线一个<span class="mark">微信小程序</span>');
  const c = at(p, 0, 486, 880, 60, '', {}, '<span class="chip fill">完整实操</span>');
  return lt => { show(k, lt, 0); show(b, lt, 0.15); show(h, lt, 0.35); show(c, lt, 0.6); };
});
ovA(S('O04') - 0.2, E('O08') + 0.3, p => {
  const t0 = S('O04') - 0.2;
  const h = at(p, 0, 40, 880, 60, 'h2', {}, '为什么用 <span class="mark">WorkBuddy</span>？');
  const l1 = at(p, 0, 130, 880, 120, 'li', {}, '<i class="dot"></i><div>Codex、Claude Code：很多朋友不知道怎么下载、怎么用</div>');
  const l2 = at(p, 0, 270, 880, 120, 'li', {}, '<i class="dot"></i><div>WorkBuddy：国内现在很火，直接能用</div>');
  const l3 = at(p, 0, 410, 880, 120, 'li', {}, '<i class="dot"></i><div>免费额度多，做小程序门槛很低</div>');
  return lt => { show(h, lt, 0); show(l1, lt, S('O05') - t0); show(l2, lt, S('O06') - t0); show(l3, lt, S('O07') - t0); };
});
ovA(S('O09') - 0.2, E('O12') + 0.3, p => {
  const t0 = S('O09') - 0.2;
  const h = at(p, 0, 40, 880, 60, 'h2', {}, '小程序 = 一个<span class="mark">应用程序</span>');
  const row = at(p, 0, 140, 880, 170, 'boxrow', { marginTop: 0 });
  const bs = ['前端', '后端', '数据库'].map(t => mk(row, 'bx', {}, t));
  const c = at(p, 0, 380, 880, 200, 'card2', {}, '<div class="tt">给别人用 → 要<span class="mark">上云</span></div><div class="dd">后端、数据库都放到云上，别人才能访问</div>');
  return lt => { show(h, lt, 0); bs.forEach((b, i) => show(b, lt, S('O10') - t0 + i * 0.35)); show(c, lt, S('O12') - t0); };
});
// 克隆声音补的说明（V01–V04）
ovA(S('V01') - 0.3, E('V04') + 0.4, p => {
  const t0 = S('V01') - 0.3;
  const h = at(p, 0, 40, 880, 60, 'h2', {}, '先说明一下');
  const c1 = at(p, 0, 140, 880, 170, 'card2', {}, '<div class="tt">实名认证注册过的小程序太多</div><div class="dd">没办法再新建 AppID</div>');
  const c2 = at(p, 0, 340, 880, 170, 'card2', {}, '<div class="tt">例一用<span class="mark">测试号</span>，只在本地跑</div><div class="dd">没法带大家一起上线，非常抱歉</div>');
  return lt => { show(h, lt, 0); show(c1, lt, S('V01') - t0 + 0.6); show(c2, lt, S('V03') - t0); };
});
// 克隆声音：下面有两个步骤（引出两个 CLI）
ovA(S('V06') - 0.3, E('V06') + 0.5, p => {
  const t0 = S('V06') - 0.3;
  const h = at(p, 0, 40, 880, 60, 'h2', {}, '开发之前，先打开<span class="mark">两样</span>');
  const c1 = at(p, 0, 150, 880, 170, 'card2', {}, '<div class="tt">① 微信开发者工具的 CLI</div><div class="dd">设置 → 安全 → 服务端口</div>');
  const c2 = at(p, 0, 350, 880, 170, 'card2', {}, '<div class="tt">② CloudBase CLI</div><div class="dd">查云函数、数据库</div>');
  return lt => { show(h, lt, 0); show(c1, lt, 0.6); show(c2, lt, 1.4); };
});
ovA(S('O13') - 0.2, E('O14') + 0.4, p => {
  const t0 = S('O13') - 0.2;
  const h = at(p, 0, 40, 880, 60, 'h2', {}, '要用的<span class="mark">两个软件</span>');
  const c1 = at(p, 0, 150, 880, 170, 'card2', {}, '<div class="tt">① WorkBuddy</div><div class="dd">腾讯的 AI 智能体：帮你写代码、改代码</div>');
  const c2 = at(p, 0, 350, 880, 170, 'card2', {}, '<div class="tt">② 微信开发者工具</div><div class="dd">编译、预览、调试、上传小程序</div>');
  return lt => { show(h, lt, 0); show(c1, lt, P('O14', 'Work') - t0); show(c2, lt, P('O14', '微信') - t0); };
});
ovA(S('O15') - 0.2, E('O18') + 0.3, p => {
  const t0 = S('O15') - 0.2;
  const h = at(p, 0, 30, 880, 60, 'h2', {}, '想用云环境：先注册 <span class="mark">AppID</span>');
  const k = 1.62, sx = 0, sy = 150;
  const card = shotCard(p, 's04', sx, sy, k);
  const ar = arrow(p, sx + 12 + 210 * k, sy + 12 + 175 * k, sx + 12 + 377 * k, sy + 12 + 26 * k);
  const cap = at(p, 0, sy + 194 * k + 60, 880, 120, 'card2', { padding: '20px 26px' }, '<div class="tt" style="font-size:34px">点工具栏的「云开发」</div><div class="dd">进去就能看到云函数、数据库的集合</div>');
  return lt => { show(h, lt, 0); show(card, lt, S('O17') - t0, { scale: .96 }); show(ar, lt, S('O17') - t0 + 0.5, { dy: 0, dx: -20 }); show(cap, lt, S('O18') - t0); };
});
ovA(S('O20') - 0.3, E('O22') + 0.6, p => {
  const t0 = S('O20') - 0.3;
  const h = at(p, 0, 0, 880, 60, 'h2', {}, '开发者工具：设置 → <span class="mark">安全</span>');
  const k = 0.76, sx = 26, sy = 76;
  const card = shotCard(p, 's01', sx, sy, k);
  const box = (x0, y0, x1, y1) => at(p, sx + 12 + x0 * k, sy + 12 + y0 * k, (x1 - x0) * k, (y1 - y0) * k, 'hl');
  const h1 = box(262, 118, 412, 168), h2 = box(262, 234, 662, 278), h3 = box(262, 318, 454, 358);
  return lt => {
    show(h, lt, 0); show(card, lt, 0.2, { scale: .97 });
    show(h1, lt, P('O21', '服务') - t0, { dy: 0, scale: 1.15 }); show(h2, lt, P('O21', 'CLI') - t0, { dy: 0, scale: 1.1 }); show(h3, lt, S('O22') - t0, { dy: 0, scale: 1.15 });
  };
});
ovA(S('O23') - 0.2, E('O34') + 0.3, p => {
  const t0 = S('O23') - 0.2;
  const h = at(p, 0, 20, 880, 60, 'h2', {}, '打开以后：AI 能直接用开发者工具');
  const n1 = at(p, 0, 150, 300, 170, 'node ai', {}, 'AI<small>WorkBuddy</small>');
  const n2 = at(p, 580, 150, 300, 170, 'node wx', {}, '微信<br>开发者工具');
  const br = arrow(p, 312, 235, 568, 235, 'var(--orange)');
  const bl = at(p, 300, 176, 280, 40, 'lnk', { textAlign: 'center', fontSize: '26px' }, 'CLI · 服务端口');
  const chips = ['自己编译', '自己截图看界面', '直接拿到报错'].map((t, i) => at(p, [0, 220, 520][i], 380, [200, 290, 360][i], 60, '', {}, `<span class="chip">${t}</span>`));
  const fin = at(p, 0, 500, 880, 120, 'card2', { padding: '18px 26px' }, '<div class="tt" style="font-size:36px">= 在调试软件和 AI 之间<span class="mark">加了一座桥</span></div>');
  const times = [S('O26'), S('O27'), S('O29')];
  return lt => {
    show(h, lt, 0); show(n1, lt, 0.2); show(n2, lt, 0.4); show(br, lt, P('O23', 'AI') - t0, { dy: 0, dx: -30 }); show(bl, lt, P('O23', 'AI') - t0);
    chips.forEach((c, i) => show(c, lt, times[i] - t0)); show(fin, lt, S('O33') - t0);
  };
});
ovA(S('O35') - 0.2, E('O40') + 0.6, p => {
  const t0 = S('O35') - 0.2;
  const h = at(p, 0, 0, 880, 60, 'h2', {}, '再加上 <span class="mark">CloudBase CLI</span>');
  const ai = at(p, 290, 90, 300, 130, 'node ai', {}, 'AI<small>写代码、改代码</small>');
  const wx = at(p, 0, 420, 370, 160, 'node wx', {}, '开发者工具 CLI<small>编译 · 截图 · 报错</small>');
  const cb = at(p, 510, 420, 370, 160, 'node cb', {}, 'CloudBase CLI<small>云函数 · 数据库</small>');
  const a1 = arrow(p, 330, 225, 200, 410, '#9AA1AC'), a2 = arrow(p, 380, 500, 500, 500, '#9AA1AC'), a3 = arrow(p, 690, 410, 560, 228, '#9AA1AC');
  const ctr = at(p, 300, 270, 280, 110, '', { textAlign: 'center', font: "800 34px/1.35 'Noto Sans SC'", color: 'var(--orange)' }, 'AI 自己联调<br><span style="font:700 26px Space Grotesk">loop ↻</span>');
  return lt => {
    show(h, lt, 0); show(ai, lt, 0.1); show(wx, lt, 0.3); show(cb, lt, P('O35', 'Cloud') - t0, { scale: .9 });
    [a1, a2, a3].forEach((a, i) => show(a, lt, S('O37') - t0 + i * 0.3, { dy: 0 })); show(ctr, lt, S('O39') - t0, { scale: .8 });
  };
});
// 开场口播最后一句：两种实操
ovA(S('O41') - 0.3, E('O45') + 0.4, p => {
  const t0 = S('O41') - 0.3;
  const h = at(p, 0, 40, 880, 60, 'h2', {}, '下面是<span class="mark">两种实操</span>');
  const c1 = at(p, 0, 150, 880, 190, 'card2', {}, '<div class="tt">① 本地跑的小程序</div><div class="dd">测试号 · 不联网 · 前端在本地</div>');
  const c2 = at(p, 0, 370, 880, 190, 'card2', {}, '<div class="tt">② 上了云的小程序</div><div class="dd">云开发 CloudBase · 云函数 + 数据库</div>');
  return lt => { show(h, lt, 0); show(c1, lt, S('O42') - t0); show(c2, lt, S('O43') - t0); };
});
// 结尾（版式 A）
ovA(S('E01') - 0.3, E('E03') + 0.3, p => {
  const t0 = S('E01') - 0.3;
  const h = at(p, 0, 60, 880, 60, 'h2', {}, '做小程序，<span class="mark">门槛很低</span>');
  const l1 = at(p, 0, 170, 880, 80, 'li', {}, '<i class="dot"></i><div>知道有哪些工具</div>');
  const l2 = at(p, 0, 270, 880, 80, 'li', {}, '<i class="dot"></i><div>会用这些工具</div>');
  const l3 = at(p, 0, 370, 880, 80, 'li', {}, '<i class="dot"></i><div>就能做你想做的东西</div>');
  return lt => { show(h, lt, 0); show(l1, lt, S('E02') - t0); show(l2, lt, P('E02', '然后') - t0); show(l3, lt, S('E03') - t0); };
});
ovA(S('E04') - 0.3, E('E07') + 0.3, p => {
  const t0 = S('E04') - 0.3;
  const row = at(p, 0, 30, 880, 170, 'boxrow', { marginTop: 0 });
  const bs = ['前端', '后端', '数据库'].map(t => mk(row, 'bx', {}, t));
  const c1 = at(p, 0, 250, 880, 170, 'card2', {}, '<div class="tt">后端 + 数据库 → <span class="mark">CloudBase</span></div><div class="dd">上云，用 CloudBase CLI 让 AI 去查、去改</div>');
  const c2 = at(p, 0, 450, 880, 170, 'card2', {}, '<div class="tt">前端 → 本地 AI 写</div><div class="dd">模型越厉害，设计越精美</div>');
  return lt => {
    bs.forEach((b, i) => show(b, lt, 0.1 + i * 0.3));
    const on = lt >= S('E05') - t0; bs[1].classList.toggle('on', on); bs[2].classList.toggle('on', on); bs[0].classList.toggle('on', lt >= S('E06') - t0);
    show(c1, lt, S('E05') - t0); show(c2, lt, S('E06') - t0);
  };
});
ovA(S('E08') - 0.3, TL.total + 1, p => {
  const t0 = S('E08') - 0.3;
  const q = at(p, 0, 120, 880, 70, 'h2', {}, '看完有收获吗？');
  const b = at(p, 0, 230, 880, 230, 'big', { lineHeight: 1.25 }, '自己动手<br><span class="mark">试一试！</span>');
  const c = at(p, 0, 520, 880, 60, '', {}, '<span class="chip fill">谢谢观看</span>');
  return lt => { show(q, lt, 0); show(b, lt, S('E10') - t0); show(c, lt, S('E11') - t0); };
});

// ═════════════════════════════ 版式 B：演示区（1474×829）上的叠加
// 章节标签：版式 B 的段，章节和前一段不同时，开头 3 秒
TL.segs.forEach((s, i) => {
  const prev = TL.segs[i - 1];
  if (s.layout !== 'B' || (prev && prev.chapter === s.chapter && prev.layout === 'B')) return;
  ovB(s.s + 0.5, s.s + 3.6, p => {
    const c = at(p, 22, 20, null, null, 'chapchip', { position: 'absolute' }, `<span>${String(s.chapter + 1).padStart(2, '0')}</span>${TL.chapters[s.chapter]}`);
    return lt => show(c, lt, 0, { dy: -12 });
  });
});
// 开发者工具 CLI：WorkBuddy 的回答（截图 03）
ovB(S('T16') - 0.2, E('T18') + 0.5, p => {
  const d = at(p, 0, 0, 1474, 829, 'dim');
  const k = 0.93, w = SHOT.s03.w * k + 24;
  const cap = at(p, 0, 22, 1474, 60, 'shotcap', {}, '<span class="chip fill">WorkBuddy 的回答：可以，本机环境是通的（用时 49 秒）</span>');
  const c = shotCard(p, 's03', (1474 - w) / 2, 96, k);
  const hl = at(p, (1474 - w) / 2 + 12 + 22 * k, 96 + 12 + 340 * k, 830 * k, 248 * k, 'hl');
  return lt => { show(d, lt, 0, { dy: 0 }); show(cap, lt, 0.1); show(c, lt, 0.2, { scale: .95 }); show(hl, lt, 1.2, { dy: 0, scale: 1.05 }); };
});
// 上传版本：说一句 → AI 上传 → 公众平台选版本 → 发布
ovB(S('T19') - 0.1, E('T25') + 0.6, p => {
  const st = at(p, 0, 0, 1474, 829, '');
  const strip = at(st, 40, 829 - 150, 1394, 120, 'strip');
  const steps = ['跟 AI 说一句', 'AI 上传版本', '公众平台里选版本', '发布'];
  const els = [];
  steps.forEach((t, i) => { if (i) mk(strip, 'ar', {}, '→'); els.push(mk(strip, 'st', {}, t)); });
  const tt = [S('T22'), S('T23'), S('T24'), S('T25')];
  return lt => { show(strip, lt, 0, { dy: 30 }); els.forEach((e, i) => e.classList.toggle('on', lt >= tt[i] - (S('T19') - 0.1))); };
});
// CloudBase CLI 的结果（截图 02）
ovB(S('T26') - 0.2, E('T27') + 1.2, p => {
  const d = at(p, 0, 0, 1474, 829, 'dim');
  const k = 0.9, w = SHOT.s02.w * k + 24;
  const cap = at(p, 0, 22, 1474, 60, 'shotcap', {}, '<span class="chip fill">CloudBase CLI 查到的：4 个云函数、25 个集合（这次跑了 8 分 36 秒）</span>');
  const c = shotCard(p, 's02', (1474 - w) / 2, 96, k);
  return lt => { show(d, lt, 0, { dy: 0 }); show(cap, lt, 0.1); show(c, lt, 0.2, { scale: .95 }); };
});
// 提示词的出处
ovB(S('C28') - 0.2, E('C29') + 0.3, p => {
  const c = at(p, 22, 829 - 86, null, null, 'pill', { position: 'absolute' }, '提示词来自公众号<b>「十字路口Crossing」</b>的文章');
  return lt => show(c, lt, 0);
});
// 例二：云开发入口（截图 04）
ovB(S('H02') - 0.2, S('H03') + 1.2, p => {
  const d = at(p, 0, 0, 1474, 829, 'dim');
  const k = 2.2, w = SHOT.s04.w * k + 24, x = (1474 - w) / 2, y = 190;
  const cap = at(p, 0, 90, 1474, 60, 'shotcap', {}, '<span class="chip fill">云开发入口：开发者工具工具栏的「云开发」</span>');
  const c = shotCard(p, 's04', x, y, k);
  const ar = arrow(p, x + 12 + 230 * k, y + 12 + 178 * k, x + 12 + 377 * k, y + 12 + 26 * k);
  return lt => { show(d, lt, 0, { dy: 0 }); show(cap, lt, 0.1); show(c, lt, 0.2, { scale: .95 }); show(ar, lt, 0.7, { dy: 0, dx: -20 }); };
});
