// 引擎：renderAt(t)。每帧：找段 → 演示区（现场片段的帧 / 文件卡片）→ 目录 → 字幕 → 叠加层。全程画外音，没有出镜框。
const demoEl = document.getElementById('demo'), scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB');
const tocEl = document.getElementById('toc'), subEl = document.getElementById('subZh');

// 目录
tocEl.innerHTML = '<div class="t">本期目录<span>白宫《超级智能协定》</span></div>' +
  TL.chapters.map((c, i) => `<div class="it" data-i="${i}"><span class="b"></span><span class="n">${i + 1}</span>${c}</div>`).join('');
const tocIts = [...tocEl.querySelectorAll('.it')];

// 叠加层：按需建
const built = new Map();
function overlay(o, t, seg) {
  const fadeOut = 0.35;
  // 现场片段播放时只显示片段上的角标（o.clip），文件卡片让位；卡片段则相反
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

  // 演示区：现场片段（有帧就铺满）/ 文件卡片
  const sf = FR.scr[n];
  if (sf) { setSrc(scrImg, 'media/' + sf); scrImg.style.visibility = 'visible'; }
  else scrImg.style.visibility = 'hidden';

  // 目录
  tocIts.forEach((e, i) => e.className = 'it' + (i === seg.chapter ? ' now' : i < seg.chapter ? ' done' : ''));

  // 字幕：开始前 0.1 s 出现，结束后留 0.45 s（不和下一条重叠）；现场片段的字幕是翻译，橙色底的人名标签 + 深橙字
  let html = '', op = 0, isClip = false, key = '';
  for (let i = 0; i < TL.cues.length; i++) {
    const c = TL.cues[i], nx = TL.cues[i + 1];
    const a = c.s - 0.1, b = Math.min(c.e + 0.45, nx ? nx.s - 0.1 : 1e9);
    if (t >= a && t < b) {
      isClip = c.kind === 'clip'; key = c.id;
      html = (isClip && c.who ? `<span class="w">${c.who}</span>` : '') + c.zh;
      op = Math.min(1, (t - a) / 0.08, (b - t) / 0.08); break;
    }
  }
  if (subEl.dataset.key !== key) {   // 太长就缩小字号（一行放不下 2340 宽）
    subEl.dataset.key = key; subEl.innerHTML = html; subEl.style.fontSize = '';
    subEl.classList.toggle('clip', isClip);
    const w = subEl.scrollWidth; if (w > 2200) subEl.style.fontSize = Math.floor(52 * 2200 / w) + 'px';
  }
  subEl.style.opacity = op;

  for (const o of OV) overlay(o, t, seg);
  await flush();
  return true;
};
window.META = { FPS, TOTAL: TL.total, W: 2340, H: 1080 };
