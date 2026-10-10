// 引擎：renderAt(t)。每帧：找段 → 版式（换版式时出镜框移动 0.7 s）→ 出镜框（真人出镜 / 画外音卡）→ 演示区（录屏原片 / 打码静帧 / 手机）→ 目录 → 字幕 → 叠加层。
const CAM = { A: { x: 120, y: 150, w: 1156, h: 666 }, B: { x: 160, y: 180, w: 1060, h: 610 } };   // B：演示段不显示出镜框，切换时原地缩一点淡出
const MOVE = 0.7;
const camEl = document.getElementById('cam'), nameEl = document.getElementById('nametag'), camImg = document.getElementById('camimg');
const phEl = document.getElementById('camph'), phId = document.getElementById('phid'), phTxt = document.getElementById('phtxt'), phNx = document.getElementById('phnx'), phPb = document.getElementById('phpb');
const voEl = document.getElementById('vo'), voLab = document.getElementById('volab'), voBars = document.getElementById('vobars');
const demoEl = document.getElementById('demo'), scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB'), ovAEl = document.getElementById('ovA');
const ntst = document.getElementById('ntst');
const stEl = document.getElementById('stst'), phst = document.getElementById('phst'), phImg = document.getElementById('phimg'), iapImg = document.getElementById('iapimg');
const tocEl = document.getElementById('toc'), subEl = document.getElementById('subZh');
const BARS = 9;
for (let i = 0; i < BARS; i++) mk(voBars, '', {}, '', 'i');

// 目录
tocEl.innerHTML = '<div class="t">本期目录<span>订阅正版 Codex / Claude</span></div>' +
  TL.chapters.map((c, i) => `<div class="it" data-i="${i}"><span class="b"></span><span class="n">${i + 1}</span>${c}</div>`).join('');
const tocIts = [...tocEl.querySelectorAll('.it')];

// 打码静帧
const stImgs = STILLS.map(sh => { const i = mk(stEl, '', { width: '1920px', height: '1080px' }, '', 'img'); i.src = sh.src; return i; });

// 叠加层：按需建
const built = new Map();
function overlay(o, t) {
  const fadeOut = 0.35;
  if (t < o.t0 - 0.01 || t > o.t1 + fadeOut) { const b = built.get(o); if (b) b.root.style.display = 'none'; return; }
  let b = built.get(o);
  if (!b) {
    const root = mk(o.where === 'A' ? ovAEl : ovBEl, 'pa', { position: 'absolute', inset: '0px' });
    b = { root, up: o.build(root) };
    built.set(o, b);
  }
  b.root.style.display = 'block';
  b.root.style.opacity = Math.min(easeOut((t - o.t0) / 0.35), 1 - easeIn((t - o.t1) / fadeOut));
  b.up(t - o.t0);
}

function segAt(t) { let i = 0; while (i + 1 < TL.segs.length && TL.segs[i + 1].s <= t + 1e-6) i++; return i; }
function cueAt(t) {   // 正在说的一条（没有就取下一条）
  for (let i = 0; i < TL.cues.length; i++) { const q = TL.cues[i]; if (t < q.e + 0.15) return i; }
  return TL.cues.length - 1;
}

window.renderAt = async function (t) {
  const n = Math.min(TL.frames - 1, Math.max(0, Math.round(t * FPS)));
  const si = segAt(t), seg = TL.segs[si], prev = TL.segs[si - 1];
  const moving = prev && prev.layout !== seg.layout && t - seg.s < MOVE;
  const g = moving ? easeIO((t - seg.s) / MOVE) : 1;
  const ra = moving ? CAM[prev.layout] : CAM[seg.layout], rb = CAM[seg.layout];
  const r = { x: lerp(ra.x, rb.x, g), y: lerp(ra.y, rb.y, g), w: lerp(ra.w, rb.w, g), h: lerp(ra.h, rb.h, g) };
  Object.assign(camEl.style, { left: px(r.x), top: px(r.y), width: px(r.w), height: px(r.h), fontSize: px(r.w / 1156 * 46) });
  // 演示段没有出镜框：从开场切过来时淡出（略缩小），之后藏起来
  const camVis = seg.layout === 'A' ? (moving ? 1 - g : 1) : (moving ? 1 - g : 0);
  camEl.style.opacity = camVis; camEl.style.visibility = camVis < 0.002 ? 'hidden' : 'visible';
  const isB = seg.layout === 'B';
  const aB = isB ? (moving ? g : 1) : (moving ? 1 - g : 0);
  demoEl.style.opacity = aB; demoEl.style.visibility = aB < 0.002 ? 'hidden' : 'visible';
  tocEl.style.opacity = aB; tocEl.style.visibility = aB < 0.002 ? 'hidden' : 'visible';
  ovAEl.style.opacity = 1 - aB;

  // 出镜框：开场 = 真人出镜（DJI 0163）；演示段 = 画外音卡（电平条跟着配音）；都没有才用占位提词
  const ci = cueAt(t), q = TL.cues[ci];
  const cf = FR.cam[n];
  if (cf && (seg.layout === 'A' || moving)) {
    setSrc(camImg, 'media/' + cf);
    const z = lerp(1.04, 1.24, aB), f = TL.cam.face;
    camImg.style.transformOrigin = `${f[0] * 100}% ${f[1] * 100}%`;
    camImg.style.transform = `scale(${z})`;
    camImg.style.visibility = 'visible'; phEl.style.opacity = 0; voEl.style.opacity = 0;
  } else if (seg.layout === 'B') {
    camImg.style.visibility = 'hidden'; phEl.style.opacity = 0; voEl.style.opacity = 0;
    voLab.innerHTML = '画外音<small>悠一</small>';
    const lv = FR.env[n] || 0;
    [...voBars.children].forEach((b, i) => { const w = 0.35 + 0.65 * Math.abs(Math.sin(n * 0.37 + i * 1.7)); b.style.height = (0.2 + 1.2 * lv * w).toFixed(3) + 'em'; });
  } else {
    camImg.style.visibility = 'hidden';
    voEl.style.opacity = 0; phEl.style.opacity = 1;
    const kindTxt = seg.layout === 'A' ? '出镜占位 · 待录' : '画外音 · 待录（可出镜）';
    phEl.querySelector('.tag').textContent = kindTxt;
    phId.textContent = q.id;
    if (phTxt.textContent !== q.zh) phTxt.textContent = q.zh;
    const nx = TL.cues[ci + 1];
    phNx.textContent = nx && nx.seg === q.seg ? '下一句：' + nx.zh : '';
    phPb.style.width = (clamp((t - q.s) / Math.max(0.1, q.e - q.s)) * 100).toFixed(1) + '%';
  }
  nameEl.style.opacity = si === 0 ? Math.min(easeOut((t - 0.5) / 0.4), 1 - easeIn((t - 5.6) / 0.4)) : 0;

  // 演示区
  const sf = FR.scr[n], pf = FR.ph[n];
  const kind = seg.kind;
  scrImg.style.visibility = 'hidden'; stEl.style.visibility = 'hidden'; phst.style.visibility = 'hidden';
  ntst.style.visibility = kind === 'note' ? 'visible' : 'hidden';
  if (kind === 'pc' && sf) { setSrc(scrImg, 'media/' + sf); scrImg.style.visibility = 'visible'; }
  else if (kind === 'pc') {
    stEl.style.visibility = 'visible';
    STILLS.forEach((sh, i) => {
      const img = stImgs[i];
      const on = t >= sh.t0 - 0.3 && t < sh.t1 + 0.3;
      if (!on) { img.style.opacity = 0; return; }
      const gg = easeIO((t - sh.t0) / (sh.t1 - sh.t0));
      const a = stillXf(sh.k0), b = stillXf(sh.k1);
      img.style.transform = `translate(${lerp(a.x, b.x, gg)}px, ${lerp(a.y, b.y, gg)}px) scale(${lerp(a.s, b.s, gg)})`;
      img.style.opacity = i === 0 ? clamp((sh.t1 + 0.3 - t) / 0.3) : Math.min(clamp((t - sh.t0 + 0.3) / 0.3), i === STILLS.length - 1 ? 1 : clamp((sh.t1 + 0.3 - t) / 0.3));
    });
    // 从录屏原片切到静帧：0.3 s 内静帧淡入（底下垫着最后一帧原片）
    if (t < STILL_T0 + 0.3) { const last = FR.scr[Math.round(STILL_T0 * FPS) - 1]; if (last) { setSrc(scrImg, 'media/' + last); scrImg.style.visibility = 'visible'; stImgs[0].style.opacity = clamp((t - STILL_T0) / 0.3); } }
  }
  if (kind === 'phone1' || kind === 'phone2') {
    phst.style.visibility = 'visible';
    if (pf === 'iap') { iapImg.style.opacity = 1; }
    else { iapImg.style.opacity = 0; if (pf) setSrc(phImg, 'media/' + pf); }
  }

  // 目录
  tocIts.forEach((e, i) => e.className = 'it' + (i === seg.chapter ? ' now' : i < seg.chapter ? ' done' : ''));

  // 字幕：开始前 0.1 s 出现，结束后留 0.45 s（不和下一条重叠）；待录的灰色
  let txt = '', op = 0, todo = false;
  for (let i = 0; i < TL.cues.length; i++) {
    const c = TL.cues[i], nx = TL.cues[i + 1];
    const a = c.s - 0.1, b = Math.min(c.e + 0.45, nx ? nx.s - 0.1 : 1e9);
    if (t >= a && t < b) { txt = c.zh; todo = c.todo; op = Math.min(1, (t - a) / 0.08, (b - t) / 0.08); break; }
  }
  if (subEl.textContent !== txt) {   // 太长就缩小字号（一行放不下 2340 宽）
    subEl.textContent = txt; subEl.style.fontSize = '';
    subEl.classList.toggle('todo', todo);
    const w = subEl.scrollWidth; if (w > 2200) subEl.style.fontSize = Math.floor(52 * 2200 / w) + 'px';
  }
  subEl.classList.toggle('todo', todo);
  subEl.style.opacity = op;

  for (const o of OV) overlay(o, t);
  await flush();
  return true;
};
window.META = { FPS, TOTAL: TL.total, W: 2340, H: 1080 };
