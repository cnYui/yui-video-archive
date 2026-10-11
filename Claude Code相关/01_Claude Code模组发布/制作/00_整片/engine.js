// 引擎：renderAt(t)。每帧：找段 → 演示区（官方演示视频的帧 / 卡片）→ 中文说明条 → 目录 → 字幕 → 叠加层。全程画外音，没有出镜框。
const demoEl = document.getElementById('demo'), scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB');
const tocEl = document.getElementById('toc'), subEl = document.getElementById('subZh'), capEl = document.getElementById('capbar');

// 目录
tocEl.innerHTML = '<div class="t">本期目录<span>Claude 官方新功能</span></div>' +
  TL.chapters.map((c, i) => `<div class="it" data-i="${i}"><span class="b"></span><span class="n">${i + 1}</span>${c}</div>`).join('');
const tocIts = [...tocEl.querySelectorAll('.it')];

// 叠加层：按需建。seg.bg（这一段演示区放着官方演示视频）时只显示 clip 叠加层，卡片让位；卡片段则相反；always 的两边都显示
const built = new Map();
function overlay(o, t, seg) {
  const fadeOut = o.fast ? 0.1 : 0.35, fadeIn = o.fast ? 0.1 : 0.35;      // 官方页面镜头之间快切，不然两页文字叠在一起
  const wrongKind = seg.bg ? !(o.clip || o.always) : (o.clip && !o.always);
  if (wrongKind || t < o.t0 - 0.01 || t > o.t1 + fadeOut) { const b = built.get(o); if (b) b.root.style.display = 'none'; return; }
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
const CLIPS = Object.entries(TL.clips).map(([id, c]) => ({ id, ...c }));

window.renderAt = async function (t) {
  const n = Math.min(TL.frames - 1, Math.max(0, Math.round(t * FPS)));
  const si = segAt(t), seg = TL.segs[si];

  // 演示区：官方演示视频有帧就铺满，否则是卡片
  const sf = FR.scr[n];
  if (sf) { setSrc(scrImg, 'media/' + sf); scrImg.style.visibility = 'visible'; }
  else scrImg.style.visibility = 'hidden';

  // 底部中文说明条（盖住演示视频自带的英文）
  let cap = null;
  for (const c of CLIPS) {
    if (t < c.s || t >= c.e) continue;
    const q = (c.caps || []).find(q => t >= q.t0 && t < q.t1);
    if (q) { cap = { ...q, tag: c.tag, nav: c.nav }; break; }
    if (c.bar) { cap = { name: c.bar[0], zh: c.bar[1], nav: null }; break; }       // 开场快剪：底部这条当标题
  }
  if (cap) {
    capEl.style.display = 'flex';
    if (capEl.dataset.key !== cap.zh) {
      capEl.dataset.key = cap.zh;
      capEl.querySelector('.nm').textContent = cap.name;
      capEl.querySelector('.zh').textContent = cap.zh;
      capEl.querySelector('.no').textContent = cap.nav != null ? `示例 ${cap.nav + 1} / 3` : '';
    }
  } else capEl.style.display = 'none';

  // 目录
  tocIts.forEach((e, i) => e.className = 'it' + (i === seg.chapter ? ' now' : i < seg.chapter ? ' done' : ''));

  // 字幕：开始前 0.1 s 出现，结束后留 0.45 s（不和下一条重叠）
  let html = '', op = 0, key = '';
  for (let i = 0; i < TL.cues.length; i++) {
    const c = TL.cues[i], nx = TL.cues[i + 1];
    const a = c.s - 0.1, b = Math.min(c.e + 0.45, nx ? nx.s - 0.1 : 1e9);
    if (t >= a && t < b) {
      key = c.id; html = c.zh;
      op = Math.min(1, (t - a) / 0.08, (b - t) / 0.08); break;
    }
  }
  if (subEl.dataset.key !== key) {   // 太长就缩小字号（一行放不下 2340 宽）
    subEl.dataset.key = key; subEl.innerHTML = html; subEl.style.fontSize = '';
    const w = subEl.scrollWidth; if (w > 2200) subEl.style.fontSize = Math.floor(52 * 2200 / w) + 'px';
  }
  subEl.style.opacity = op;

  for (const o of OV) overlay(o, t, seg);
  await flush();
  return true;
};
window.META = { FPS, TOTAL: TL.total, W: 2340, H: 1080 };
