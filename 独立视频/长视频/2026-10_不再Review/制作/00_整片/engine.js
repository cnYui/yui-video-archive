// 引擎：renderAt(t)。每帧：找场景 → 演示区（官方演示视频帧 / 卡片）→ 左栏目录 → 中英字幕 → 叠加层（含官方页面录屏）。全程画外音，没有出镜框。
const scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB');
const tocEl = document.getElementById('toc'), subEl = document.getElementById('subZh'), subEn = document.getElementById('subEn');

// 左栏：本期目录（章名都是字符串，≤ 3 条、每条 ≤ 7 字）
tocEl.innerHTML = `<div class="t">本期目录<span>${TL.sub || ''}</span></div>` +
  TL.chapters.map((c, i) => `<div class="it" data-i="${i}"><span class="b"></span><span class="n">${i + 1}</span>${c}</div>`).join('');
const tocIts = [...tocEl.querySelectorAll('.it')];

// 叠加层：按需建；官方页面镜头（o.fast）之间快切，不然两页文字叠在一起
const built = new Map();
function overlay(o, t) {
  const fadeOut = o.fast ? 0.1 : 0.3, fadeIn = o.fast ? 0.1 : 0.3;
  if (t < o.t0 - 0.01 || t > o.t1 + fadeOut) { const b = built.get(o); if (b) b.root.style.display = 'none'; return; }
  let b = built.get(o);
  if (!b) {
    const root = mk(ovBEl, 'pa', { position: 'absolute', inset: '0px' });
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
  const si = segAt(t), seg = TL.segs[si];

  // 演示区：官方演示视频的帧（有帧就铺满）/ 卡片 / 页面录屏（叠加层盖住）
  const sf = FR.scr[n];
  if (sf) { setSrc(scrImg, 'media/' + sf); scrImg.style.visibility = 'visible'; }
  else scrImg.style.visibility = 'hidden';

  // 左栏：开场（chapter −1）都不亮；收尾（chapter ≥ 章数）都标“已看”
  const nCh = TL.chapters.length;
  tocIts.forEach((e, i) => e.className = 'it' + (i === seg.chapter ? ' now' : (seg.chapter >= nCh || (seg.chapter >= 0 && i < seg.chapter)) ? ' done' : ''));

  // 字幕（项目的中英双语标准：中文一行 52 px + 英文一行 30 px，居中，y 922 起）：TL.subs 里每条已经按标准拆好，
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
window.META = { FPS, TOTAL: TL.total, W: 2340, H: 1080 };
