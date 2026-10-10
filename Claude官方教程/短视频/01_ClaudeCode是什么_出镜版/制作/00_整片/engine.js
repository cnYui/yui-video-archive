// 引擎：renderAt(t)。每帧：找场景 → 素材框（素材帧 / 卡片）→ 标题（一直在）→ 中英字幕 → 叠加层（素材框里的 + 整页的）。全程画外音，没有出镜框、没有目录。
const scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB'), ovPEl = document.getElementById('ovP');
const scrImg2 = document.getElementById('scrimg2'), ovB2El = document.getElementById('ovB2');
if (TL.faceph) document.body.classList.add('faceph');             // 草稿：最下面画出镜位占位框
if (TL.bg) document.body.classList.add('hasbg');                   // 背景印花（bg.png，new_short.py 随机挑的）
const subEl = document.getElementById('subZh'), subEn = document.getElementById('subEn');

// 标题：录制稿.json 的 kicker（小字，可以有 <b>强调</b>）和 hook = [第一行, 第二行]
const H = TL.hook || ['', ''];
document.getElementById('kicker').innerHTML = TL.kicker || '';
document.getElementById('t1').textContent = H[0] || '';
document.getElementById('t2').innerHTML = H[1] ? `<span>${H[1]}</span>` : '';
const headEl = document.getElementById('head');
const demoEl = document.getElementById('demo'), demo2El = document.getElementById('demo2');
const demoIn = demoEl.querySelector('.demoin'), demoIn2 = demo2El.querySelector('.demoin');
// 三种窗口（plan.json 每个场景写 mode）：one = 单个横屏窗口居中；two = 两个横屏窗口上下叠；big = 单个窗口拉成两个窗口合并的大小（内容 1474×1725，看清文字用）
const MODES = {      // 位置照技能的固定版式（references/layout.md）：单窗 = single 版式；双窗、大窗 = dual 版式（大窗 = 两个窗口合并：x 110–970、y 680–1684）
  one: { A: [40, 770, 1000, 569], B: null, cw: 1474, ch: 829, subs: 1498 },
  two: { A: [110, 680, 860, 490], B: [110, 1194, 860, 490], cw: 1474, ch: 829, subs: 1764 },
  big: { A: [110, 680, 860, 1004], B: null, cw: 1474, ch: 1725, subs: 1764 },
};
function place(el, inner, r, cw, ch) {
  el.style.left = r[0] + 'px'; el.style.top = r[1] + 'px'; el.style.width = r[2] + 'px'; el.style.height = r[3] + 'px';
  inner.style.width = cw + 'px'; inner.style.height = ch + 'px';
  inner.style.transform = `scale(${(r[2] - 14) / cw})`;
}

// 叠加层：按需建；o.layer = 'page' 的放整页（1080×2340 坐标），'b2' 的放下框（双分镜），其余放上框（都是 1474×829 坐标）；页面镜头（o.fast）之间快切
const built = new Map();
function overlay(o, t) {
  const fadeOut = o.fast ? 0.1 : 0.3, fadeIn = o.fast ? 0.1 : 0.3;
  if (t < o.t0 - 0.01 || t > o.t1 + fadeOut) { const b = built.get(o); if (b) b.root.style.display = 'none'; return; }
  let b = built.get(o);
  if (!b) {
    const root = mk(o.layer === 'page' ? ovPEl : o.layer === 'b2' ? ovB2El : ovBEl, 'pa', { position: 'absolute', inset: '0px' });
    b = { root, up: o.build(root) };
    built.set(o, b);
  }
  b.root.style.display = 'block';
  b.root.style.opacity = Math.min(easeOut((t - o.t0) / fadeIn), 1 - easeIn((t - o.t1) / fadeOut));
  b.up(t - o.t0);
}

function segAt(t) { let i = 0; while (i + 1 < TL.segs.length && TL.segs[i + 1].s <= t + 1e-6) i++; return i; }

window.renderAt = async function (t) {
  const n = Math.min(TL.frames - 1, Math.max(0, Math.round(t * FPS)));

  // 素材框：素材帧（有帧就铺满）/ 卡片 / 页面录屏（叠加层盖住）
  const sf = FR.scr[n];
  if (sf) { setSrc(scrImg, 'media/' + sf); scrImg.style.visibility = 'visible'; }
  else scrImg.style.visibility = 'hidden';
  const sf2 = FR.scr2 && FR.scr2[n];                                    // 双分镜的下框
  if (sf2) { setSrc(scrImg2, 'media/' + sf2); scrImg2.style.visibility = 'visible'; }
  else scrImg2.style.visibility = 'hidden';

  // 标题：第一帧就在（封面、抖音预览都取得到），不做入场动画
  headEl.style.opacity = 1;

  // 窗口：按场景的 mode 摆好（one / two / big），场景开头 0.18 s 淡入 + 轻微放大（硬切之间不突兀）
  const sg = TL.segs[segAt(t)], ck = TL.clips[sg.id], M = MODES[(ck && ck.mode) || 'two'];
  place(demoEl, demoIn, M.A, M.cw, M.ch);
  document.getElementById('subs').style.top = M.subs + 'px';           // 字幕在窗口下面：单窗 1498、双窗 / 大窗 1764（出镜小窗的位置也按这个换，见 compose_face_mixed.py）
  demo2El.style.display = M.B ? 'block' : 'none';
  if (M.B) place(demo2El, demoIn2, M.B, M.cw, M.ch);
  const pop = Math.min(1, Math.max(0, (t - sg.s) / 0.18)), pe = 1 - Math.pow(1 - pop, 3);
  for (const el of [demoEl, demo2El]) { el.style.opacity = 0.35 + 0.65 * pe; el.style.transform = `scale(${0.975 + 0.025 * pe})`; }
  // 边框右上角的贴纸 = 当前场景的来源（clip 场景的 credit；自己画的说明卡不贴）
  const tag = ck && ck.credit ? ck.credit : '';
  if (demoEl.dataset.tag !== tag) demoEl.dataset.tag = tag;

  // 字幕（项目中英双语标准：中文一行 52 px + 英文一行 30 px，竖屏 y 1195 起）：TL.subs 里每条已经按竖屏的字数上限拆好，
  // [a, b) 是显示区间（开始前 0.1 s ~ 结束后 0.45 s，互不重叠，build_timeline.py 算好的）
  let cur = null, op = 0;
  for (const c of TL.subs) {
    if (t >= c.a && t < c.b) { cur = c; op = Math.min(1, (t - c.a) / 0.08, (c.b - t) / 0.08); break; }
  }
  const key = cur ? cur.id + '.' + cur.k : '';
  if (subEl.dataset.key !== key) {
    subEl.dataset.key = key;
    subEl.textContent = '';
    if (cur && cur.who) { const w = document.createElement('span'); w.className = 'w'; w.textContent = cur.who; subEl.appendChild(w); }
    if (cur) subEl.appendChild(document.createTextNode(cur.zh));
    subEn.textContent = cur ? cur.en : '';
  }
  subEl.style.opacity = op; subEn.style.opacity = op;

  for (const o of OV) overlay(o, t);
  await flush();
  return true;
};
window.META = { FPS, TOTAL: TL.total, W: 1080, H: 2340 };
