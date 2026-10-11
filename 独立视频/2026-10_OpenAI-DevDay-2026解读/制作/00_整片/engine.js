// 引擎：renderAt(t)。每帧：找段 → 演示区（发布会画面的帧 / 卡片）→ 左栏要点 → 中英字幕 → 叠加层。全程画外音，没有出镜框。
const demoEl = document.getElementById('demo'), scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB');
const tocEl = document.getElementById('toc'), subEl = document.getElementById('subZh'), subEn = document.getElementById('subEn');
const MEDIA = 'out/' + EPID + '/media/';

// 左栏：本条要点
tocEl.innerHTML = '<div class="t">本条要点<span>' + TL.short + '</span></div>' +
  TL.chapters.map((c, i) => `<div class="it" data-i="${i}"><span class="b"></span><span class="n">${i + 1}</span>${c}</div>`).join('');
const tocIts = [...tocEl.querySelectorAll('.it')];

// 叠加层：按需建
const built = new Map();
function overlay(o, t, seg) {
  const fadeOut = 0.35;
  // 发布会画面播放时只显示画面上的角标（o.clip），卡片让位；卡片段则相反
  const wrongKind = seg.kind === 'clip' ? !o.clip : (o.clip && !o.always);
  if (wrongKind || t < o.t0 - 0.01 || t > o.t1 + fadeOut) { const b = built.get(o); if (b) b.root.style.display = 'none'; return; }
  let b = built.get(o);
  if (!b) {
    const root = mk(ovBEl, 'pa', { position: 'absolute', inset: '0px' });
    b = { root, up: o.build(root) };
    built.set(o, b);
  }
  b.root.style.display = 'block';
  b.root.style.opacity = Math.min(easeOut((t - o.t0) / 0.35), 1 - easeIn((t - o.t1) / fadeOut));
  b.up(t - o.t0);
}

function segAt(t) { let i = 0; while (i + 1 < TL.segs.length && TL.segs[i + 1].s <= t + 1e-6) i++; return i; }

window.renderAt = async function (t) {
  const n = Math.min(TL.frames - 1, Math.max(0, Math.round(t * FPS)));
  const si = segAt(t), seg = TL.segs[si];

  // 演示区：发布会画面（有帧就铺满）/ 卡片
  const sf = FR.scr[n];
  if (sf) { setSrc(scrImg, MEDIA + sf); scrImg.style.visibility = 'visible'; }
  else scrImg.style.visibility = 'hidden';

  // 左栏
  tocIts.forEach((e, i) => e.className = 'it' + (i === seg.chapter ? ' now' : i < seg.chapter ? ' done' : ''));

  // 字幕（项目的中英双语标准：中文一行 52 px + 英文一行 30 px，居中，y 922 起）：TL.subs 里每条已经按标准拆好，
  // [a, b) 是显示区间（开始前 0.1 s ~ 结束后 0.45 s，互不重叠，build_timeline.py 算好的）；现场原话的同传，中文前面带橙色人名胶囊
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

  for (const o of OV) overlay(o, t, seg);
  await flush();
  return true;
};
window.META = { FPS, TOTAL: TL.total, W: 2340, H: 1080 };
