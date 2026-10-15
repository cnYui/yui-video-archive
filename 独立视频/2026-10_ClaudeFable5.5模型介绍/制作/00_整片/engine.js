// 引擎：renderAt(t)。每帧：找场景 → 演示区（素材帧 / 卡片）→ 左栏（本期素材）→ 字幕 → 叠加层。全程画外音，没有出镜框。
const scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB');
const tocEl = document.getElementById('toc'), subEl = document.getElementById('subZh');

// 左栏：本期素材（缩略图 + 序号·模型 + 作品名）
tocEl.innerHTML = `<div class="t">本期素材<span>${TL.sub || ''}</span></div>` +
  TL.chapters.map((c, i) => `<div class="it" data-i="${i}"><div class="th"><img src="media/${c.thumb}"></div><div class="tx"><div class="n">${String(i + 1).padStart(2, '0')} · ${c.tag}</div><div class="nm">${c.name}</div></div></div>`).join('');
const tocIts = [...tocEl.querySelectorAll('.it')];
tocEl.querySelectorAll('img').forEach(i => PENDING.add(i));

// 叠加层：按需建
const built = new Map();
function overlay(o, t) {
  const fadeOut = 0.3;
  if (t < o.t0 - 0.01 || t > o.t1 + fadeOut) { const b = built.get(o); if (b) b.root.style.display = 'none'; return; }
  let b = built.get(o);
  if (!b) {
    const root = mk(ovBEl, 'pa', { position: 'absolute', inset: '0px' });
    b = { root, up: o.build(root) };
    built.set(o, b);
  }
  b.root.style.display = 'block';
  b.root.style.opacity = Math.min(easeOut((t - o.t0) / 0.3), 1 - easeIn((t - o.t1) / fadeOut));
  b.up(t - o.t0);
}

function segAt(t) { let i = 0; while (i + 1 < TL.segs.length && TL.segs[i + 1].s <= t + 1e-6) i++; return i; }

window.renderAt = async function (t) {
  const n = Math.min(TL.frames - 1, Math.max(0, Math.round(t * FPS)));
  const si = segAt(t), seg = TL.segs[si];

  // 演示区：素材帧（有帧就铺满）/ 卡片
  const sf = FR.scr[n];
  if (sf) { setSrc(scrImg, 'media/' + sf); scrImg.style.visibility = 'visible'; }
  else scrImg.style.visibility = 'hidden';

  // 左栏：开场（chapter −1）都不亮；收尾（chapter ≥ 章数）都标“已看”
  const nCh = TL.chapters.length;
  tocIts.forEach((e, i) => e.className = 'it' + (i === seg.chapter ? ' now' : (seg.chapter >= nCh || (seg.chapter >= 0 && i < seg.chapter)) ? ' done' : ''));

  // 字幕：开始前 0.1 s 出现，结束后留 0.45 s（不和下一条重叠）
  let html = '', op = 0, key = '';
  for (let i = 0; i < TL.cues.length; i++) {
    const c = TL.cues[i], nx = TL.cues[i + 1];
    const a = c.s - 0.1, b = Math.min(c.e + 0.45, nx ? nx.s - 0.1 : 1e9);
    if (t >= a && t < b) { key = c.id; html = c.zh; op = Math.min(1, (t - a) / 0.08, (b - t) / 0.08); break; }
  }
  if (subEl.dataset.key !== key) {   // 太长就缩小字号（一行放不下 2340 宽）
    subEl.dataset.key = key; subEl.innerHTML = html; subEl.style.fontSize = '';
    const w = subEl.scrollWidth; if (w > 2200) subEl.style.fontSize = Math.floor(52 * 2200 / w) + 'px';
  }
  subEl.style.opacity = op;

  for (const o of OV) overlay(o, t);
  await flush();
  return true;
};
window.META = { FPS, TOTAL: TL.total, W: 2340, H: 1080 };
