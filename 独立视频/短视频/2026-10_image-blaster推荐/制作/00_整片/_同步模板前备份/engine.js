// 引擎：renderAt(t)。每帧：找场景 → 素材框（素材帧 / 卡片）→ 标题（一直在）→ 中英字幕 → 叠加层（素材框里的 + 整页的）。全程画外音，没有出镜框、没有目录。
const scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB'), ovPEl = document.getElementById('ovP');
const scrImg2 = document.getElementById('scrimg2'), ovB2El = document.getElementById('ovB2');
if (TL.layout === 'dual') document.body.classList.add('dual');   // 双分镜：下框（ranges2）显示出来
const subEl = document.getElementById('subZh'), subEn = document.getElementById('subEn');

// 标题：录制稿.json 的 kicker（小字，可以有 <b>强调</b>）和 hook = [第一行, 第二行]
const H = TL.hook || ['', ''];
document.getElementById('kicker').innerHTML = TL.kicker || '';
document.getElementById('t1').textContent = H[0] || '';
document.getElementById('t2').innerHTML = H[1] ? `<span>${H[1]}</span>` : '';
const headEl = document.getElementById('head');
const demoEl = document.getElementById('demo');

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

  // 边框右上角的贴纸 = 当前场景的来源（clip 场景的 credit；页面场景不贴）
  const sg = TL.segs[segAt(t)], ck = TL.clips[sg.id], tag = ck && ck.overlay === 'clip' && ck.credit ? ck.credit : '';
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
