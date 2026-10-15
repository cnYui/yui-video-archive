// 引擎：renderAt(t)。每帧：找场景 → 素材框（素材帧 / 卡片）→ 标题（一直在）→ 中英字幕 → 叠加层（素材框里的 + 整页的）。全程画外音，没有出镜框、没有目录。
// 【本条改动，模板原样见 技能 assets/engine-template/engine.js】《人人都是 UI 设计师》：画面全是静态图，没有 clip 场景——
//   ① 上下两个框各一张真元素贴纸（#stk1 / #stk2）：内容取当前场景 plan.json 的 ui.tag / ui.tag2，写法 "x|文字"（红 ✕）/ "ok|文字"（绿 ✓）/ "?|文字"（蓝 ?），不带竖线就只放文字；
//   ② 小标题 #kicker 按场景换：ui.kicker 有就用它，没有用 录制稿.json 的 kicker；③ 来源小字 #credit（上框左上角外面）取 ui.credit。其余同模板。
const scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB'), ovPEl = document.getElementById('ovP');
const scrImg2 = document.getElementById('scrimg2'), ovB2El = document.getElementById('ovB2');
if (TL.layout === 'dual') document.body.classList.add('dual');   // 双分镜：下框（ranges2）显示出来
if (TL.bg) document.body.classList.add('hasbg');                   // 背景印花（bg.png，new_short.py 随机挑的）
const subEl = document.getElementById('subZh'), subEn = document.getElementById('subEn');

// 标题：录制稿.json 的 kicker（小字，可以有 <b>强调</b>）和 hook = [第一行, 第二行]
const H = TL.hook || ['', ''];
const kickEl = document.getElementById('kicker');
kickEl.innerHTML = TL.kicker || '';
document.getElementById('t1').textContent = H[0] || '';
document.getElementById('t2').innerHTML = H[1] ? `<span>${H[1]}</span>` : '';
const headEl = document.getElementById('head');
const demoEl = document.getElementById('demo');
const stk1 = document.getElementById('stk1'), stk2 = document.getElementById('stk2');
const creditEl = document.getElementById('credit');

// 贴纸：图标（SVG）+ 文字
const STK_ICON = {
  x: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="12" fill="#EF4444"/><path d="M7.6 7.6l8.8 8.8M16.4 7.6l-8.8 8.8" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/></svg>',
  ok: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="12" fill="#16A34A"/><path d="M6.6 12.6l3.9 3.9 7-8.6" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  '?': '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="12" fill="#2563EB"/><path d="M8.9 9.3a3.2 3.2 0 1 1 4.6 2.9c-1 .6-1.5 1.1-1.5 2.3" fill="none" stroke="#fff" stroke-width="2.8" stroke-linecap="round"/><circle cx="12" cy="18.2" r="1.7" fill="#fff"/></svg>',
};
function stickerHTML(spec) {
  if (!spec) return '';
  const i = spec.indexOf('|');
  if (i < 0) return `<span>${spec}</span>`;
  return (STK_ICON[spec.slice(0, i)] || '') + `<span>${spec.slice(i + 1)}</span>`;
}
function setSticker(el, spec) {
  const key = spec || '';
  if (el.dataset.s !== key) { el.dataset.s = key; el.innerHTML = stickerHTML(key); }
  el.style.display = key ? 'flex' : 'none';
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

  // 本条：贴纸 + 小标题按当前场景的 ui 换
  const sg = TL.segs[segAt(t)], ck = TL.clips[sg.id], ui = (ck && ck.ui) || {};
  setSticker(stk1, ui.tag);
  setSticker(stk2, ui.tag2);
  if (creditEl.dataset.c !== (ui.credit || '')) { creditEl.dataset.c = ui.credit || ''; creditEl.textContent = ui.credit || ''; }
  const kk = ui.kicker || TL.kicker || '';
  if (kickEl.dataset.k !== kk) { kickEl.dataset.k = kk; kickEl.innerHTML = kk; }
  if (demoEl.dataset.tag) demoEl.dataset.tag = '';                      // 模板的 ::after 贴纸不用（改成上面的真元素）

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
