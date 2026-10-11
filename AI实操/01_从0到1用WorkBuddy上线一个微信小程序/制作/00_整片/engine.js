// 引擎：renderAt(t)。每帧：找片段 → 版式（换版式时出镜框移动 0.7 s）→ 出镜帧 / 画外音卡 → 录屏帧 → 目录 → 字幕 → 叠加层。
const CAM = { A: { x: 120, y: 150, w: 1156, h: 666 }, B: { x: 48, y: 48, w: 696, h: 402 } };
const ZOOM = { A: 1.04, B: 1.24 };
const MOVE = 0.7;
const camEl = document.getElementById('cam'), camImg = document.getElementById('camimg'), nameEl = document.getElementById('nametag');
const voEl = document.getElementById('vo'), voLab = document.getElementById('volab'), voBars = document.getElementById('vobars');
const demoEl = document.getElementById('demo'), scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB'), ovAEl = document.getElementById('ovA');
const tocEl = document.getElementById('toc'), subEl = document.getElementById('subZh');
const BARS = 9;
for (let i = 0; i < BARS; i++) mk(voBars, '', {}, '', 'i');

// 目录
tocEl.innerHTML = '<div class="t">本期目录<span>从 0 到 1 上线微信小程序</span></div>' +
  TL.chapters.map((c, i) => `<div class="it" data-i="${i}"><span class="b"></span><span class="n">${i + 1}</span>${c}</div>`).join('');
const tocIts = [...tocEl.querySelectorAll('.it')];

const clipStarts = TL.clips.map(c => c[0]);
function clipAt(n) { let lo = 0, hi = clipStarts.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (clipStarts[m] <= n) lo = m; else hi = m - 1; } return TL.clips[lo]; }

// 叠加层：按需建
const built = new Map();
function overlay(o, t) {
  const fadeIn = 0.35, fadeOut = 0.35;
  if (t < o.t0 - 0.01 || t > o.t1 + fadeOut) { const b = built.get(o); if (b) b.root.style.display = 'none'; return; }
  let b = built.get(o);
  if (!b) {
    const root = mk(o.where === 'A' ? ovAEl : ovBEl, 'pa', { position: 'absolute', inset: '0px' });
    b = { root, up: o.build(root) };
    built.set(o, b);
  }
  b.root.style.display = 'block';
  b.root.style.opacity = Math.min(easeOut((t - o.t0) / fadeIn), 1 - easeIn((t - o.t1) / fadeOut));
  b.up(t - o.t0);
}

function lastLayoutChange(t) {   // 当前段、上一段的版式
  let i = 0; while (i + 1 < TL.segs.length && TL.segs[i + 1].s <= t + 1e-6) i++;
  return { seg: TL.segs[i], prev: TL.segs[i - 1] };
}

window.renderAt = async function (t) {
  const n = Math.min(TL.frames - 1, Math.max(0, Math.round(t * FPS)));
  const c = clipAt(n);
  const [out0, cn, layout, chapter, kind, speed] = c;
  const { seg, prev } = lastLayoutChange(t);
  const moving = prev && prev.layout !== seg.layout;
  const g = moving ? easeIO((t - seg.s) / MOVE) : 1;
  const ra = moving ? CAM[prev.layout] : CAM[seg.layout], rb = CAM[seg.layout];
  const r = { x: lerp(ra.x, rb.x, g), y: lerp(ra.y, rb.y, g), w: lerp(ra.w, rb.w, g), h: lerp(ra.h, rb.h, g) };
  Object.assign(camEl.style, { left: px(r.x), top: px(r.y), width: px(r.w), height: px(r.h), fontSize: px(r.w / 1156 * 46) });
  const isB = seg.layout === 'B';
  const aB = isB ? (moving ? g : 1) : (moving ? 1 - g : 0);
  demoEl.style.opacity = aB; demoEl.style.visibility = aB < 0.002 ? 'hidden' : 'visible';
  tocEl.style.opacity = aB; tocEl.style.visibility = aB < 0.002 ? 'hidden' : 'visible';
  ovAEl.style.opacity = 1 - aB;

  // 出镜
  const cf = FR.cam[n];
  if (cf) {
    setSrc(camImg, 'media/' + cf);
    const id = cf.split('/')[1].split('_')[0], f = TL.camFace[id] || [0.55, 0.3];
    const z = lerp(moving ? ZOOM[prev.layout] : ZOOM[seg.layout], ZOOM[seg.layout], g);
    camImg.style.transformOrigin = `${f[0] * 100}% ${f[1] * 100}%`;
    camImg.style.transform = `scale(${z})`;
    camImg.style.visibility = 'visible';
    voEl.style.opacity = 0;
  } else {
    camImg.style.visibility = 'hidden';
    voEl.style.opacity = 1;
    const fast = kind === 'fast';
    voLab.innerHTML = fast ? `快进中<small>× ${Math.round(speed)}</small>` : '画外音<small>悠一</small>';
    const lv = fast ? 0 : TL.env[n];
    [...voBars.children].forEach((b, i) => { const w = 0.35 + 0.65 * Math.abs(Math.sin(n * 0.37 + i * 1.7)); b.style.height = (0.2 + 1.2 * lv * w).toFixed(3) + 'em'; b.style.opacity = fast ? 0.35 : 1; });
  }
  nameEl.style.opacity = TL.segs[0] === seg ? Math.min(easeOut((t - 0.5) / 0.4), 1 - easeIn((t - (S('O03') + 0.8)) / 0.4)) : 0;

  // 录屏
  const sf = FR.scr[n];
  if (sf && isB) setSrc(scrImg, 'media/' + sf);

  // 目录
  tocIts.forEach((e, i) => e.className = 'it' + (i === chapter ? ' now' : i < chapter ? ' done' : ''));

  // 快进角标
  let badge = document.getElementById('badge');
  if (!badge) badge = mk(demoEl.querySelector('.inner'), 'badge', { zIndex: 5 }, '', 'div'), badge.id = 'badge';
  if (kind === 'fast' && isB && speed >= 1.5) { badge.style.display = 'block'; badge.innerHTML = `快进<b>×${speed < 10 ? speed.toFixed(1) : Math.round(speed)}</b>`; }
  else badge.style.display = 'none';

  // 字幕：开始前 0.1 s 出现，结束后留 0.45 s（不和下一条重叠）
  let txt = '', op = 0;
  for (let i = 0; i < TL.cues.length; i++) {
    const q = TL.cues[i], nx = TL.cues[i + 1];
    const a = q.s - 0.1, b = Math.min(q.e + 0.45, nx ? nx.s - 0.1 : 1e9);
    if (t >= a && t < b) { txt = q.zh; op = Math.min(1, (t - a) / 0.08, (b - t) / 0.08); break; }
  }
  if (subEl.textContent !== txt) subEl.textContent = txt;
  subEl.style.opacity = op;

  // 叠加层
  for (const o of OV) overlay(o, t);
  await flush();
  return true;
};
window.META = { FPS, TOTAL: TL.total, W: 2340, H: 1080 };
