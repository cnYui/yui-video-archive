// 引擎：renderAt(t)。每帧：找场景 → 出镜位（A / B 两种版式，版式切换时移动 0.7 s）→ 演示区（官方演示视频帧 / 卡片 / 页面录屏）→ 左栏目录 → 中英字幕 → 叠加层。
// 「录制用」无声版：出镜位是空的占位框（录好口播后换成出镜画面）。
//   B 版式：出镜位 (48,48) 696×402 + 左下目录 + 右边演示区（官方演示视频 / 官方页面 / 推文录屏）。
//   A 版式：出镜大框 (120,150) 1156×666 在左，右边写要点（plan.json 里该场景的 ui：kick / h1 / items / verdict，每一行在对应那句话说出口时出现）；用来放口播为主的段落。
const scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB');
const tocEl = document.getElementById('toc'), subEl = document.getElementById('subZh'), subEn = document.getElementById('subEn');
const camEl = document.getElementById('cam'), apanel = document.getElementById('apanel'), demoEl = document.getElementById('demo');
const camImg = document.getElementById('camimg'), nameEl = document.getElementById('nametag');
const NCAM = Math.max(1, Math.round((TL.narTotal || TL.total) * FPS));          // 出镜画面的帧数（facecam.mp4 逐帧抽在 media/cam/f_00001.jpg …，和时间轴逐帧对齐）
const ZOOM_A = 1.06, ZOOM_B = 1.35;

// 左栏：本期目录（章名都是字符串，≤ 3 条、每条 ≤ 7 字）
tocEl.innerHTML = `<div class="t">本期目录<span>${TL.sub || ''}</span></div>` +
  TL.chapters.map((c, i) => `<div class="it" data-i="${i}"><span class="b"></span><span class="n">${i + 1}</span>${c}</div>`).join('');
const tocIts = [...tocEl.querySelectorAll('.it')];

// ── 出镜位的两种位置
const RB = { x: 48, y: 48, w: 696, h: 402 }, RA = { x: 120, y: 150, w: 1156, h: 666 };
const rectLerp = (a, b, k) => ({ x: lerp(a.x, b.x, k), y: lerp(a.y, b.y, k), w: lerp(a.w, b.w, k), h: lerp(a.h, b.h, k) });
const layOf = s => s.layout || 'B';

// ── A 版式右侧的要点：每个 A 场景建一个 pane，行 / 结论框在 S(line) 时刻出现
const panes = {};
TL.segs.forEach(sg => {
  const ui = (TL.clips[sg.id] || {}).ui || {};
  if (layOf(sg) !== 'A' || !(ui.h1 || ui.items || ui.verdict)) return;
  const pane = mk(apanel, 'pane');
  if (ui.kick) mk(pane, 'kick', {}, ui.kick);
  if (ui.h1) mk(pane, 'h1', {}, ui.h1);
  const rows = [];
  (ui.items || []).forEach(it => {
    const row = mk(pane, 'row', {}, `<span class="b"></span><span class="tx">${it.t}${it.s ? `<small>${it.s}</small>` : ''}</span>`);
    rows.push({ el: row, t: S(it.line) + (it.off || 0) });
  });
  if (ui.verdict) {
    const v = mk(pane, 'verdict');
    ui.verdict.forEach(it => {
      const bx = mk(v, 'vbox ' + (it.cls || 'no'), {}, `${it.t}${it.s ? `<small>${it.s}</small>` : ''}`);
      rows.push({ el: bx, t: S(it.line) + (it.off || 0) });
    });
  }
  panes[sg.id] = { pane, rows };
});

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

  // 版式：当前场景和上一个场景的版式不同，就在场景开头 0.7 s 内移动出镜位、淡入 / 淡出演示区和要点
  const cur = layOf(seg), prev = si > 0 ? layOf(TL.segs[si - 1]) : cur;
  const k = cur === prev ? 1 : easeIO((t - seg.s) / 0.7);
  const r = cur === prev ? (cur === 'A' ? RA : RB) : rectLerp(prev === 'A' ? RA : RB, cur === 'A' ? RA : RB, k);
  Object.assign(camEl.style, { left: r.x + 'px', top: r.y + 'px', width: r.w + 'px', height: r.h + 'px' });
  const wB = cur === 'B' ? (prev === 'B' ? 1 : k) : (prev === 'B' ? 1 - k : 0);
  // 出镜画面：第 n 帧；小框放大对着脸，大框放大少一点（版式切换时一起插值）
  camImg.style.transform = `scale(${lerp(ZOOM_A, ZOOM_B, wB)})`;
  setSrc(camImg, 'media/cam/f_' + String(clamp(n, 0, NCAM - 1) + 1).padStart(5, '0') + '.jpg');
  // 开场左下角“悠一 Yui”名字条（0.4–5.8 s，贴着出镜大框的左下角）
  const nv = Math.min(easeOut((t - 0.4) / 0.4), 1 - easeIn((t - 5.4) / 0.4));
  nameEl.style.opacity = clamp(nv);
  nameEl.style.left = (r.x + 22) + 'px'; nameEl.style.top = (r.y + r.h - 96) + 'px';
  demoEl.style.opacity = wB; tocEl.style.opacity = wB; apanel.style.opacity = 1 - wB;
  const paneSeg = cur === 'A' ? seg : (prev === 'A' ? TL.segs[si - 1] : null);
  Object.entries(panes).forEach(([id, p]) => p.pane.style.display = (paneSeg && paneSeg.id === id) ? 'block' : 'none');
  if (paneSeg && panes[paneSeg.id]) {
    panes[paneSeg.id].rows.forEach(rw => {
      const a = easeOut((t - rw.t + 0.05) / 0.4);
      rw.el.style.opacity = a; rw.el.style.transform = `translateY(${(1 - a) * 18}px)`;
    });
  }

  // 演示区：官方演示视频的帧（有帧就铺满）/ 卡片 / 页面录屏（叠加层盖住）
  const sf = FR.scr[n];
  if (sf) { setSrc(scrImg, 'media/' + sf); scrImg.style.visibility = 'visible'; }
  else scrImg.style.visibility = 'hidden';

  // 左栏：开场（chapter −1）都不亮；收尾（chapter ≥ 章数）都标“已看”
  const nCh = TL.chapters.length;
  tocIts.forEach((e, i) => e.className = 'it' + (i === seg.chapter ? ' now' : (seg.chapter >= nCh || (seg.chapter >= 0 && i < seg.chapter)) ? ' done' : ''));

  // 字幕（项目的中英双语标准：中文一行 52 px + 英文一行 30 px，居中，y 922 起）：TL.subs 里每条已经按标准拆好，
  // [a, b) 是显示区间（开始前 0.1 s ~ 结束后 0.45 s，互不重叠，build_timeline.py 算好的）
  // 录制用版的字幕 = 稿子（预览，按估的语速排时间）；录完口播后换成按实际口播识别出来的字幕。
  let curSub = null, op = 0;
  for (const c of TL.subs) {
    if (t >= c.a && t < c.b) { curSub = c; op = Math.min(1, (t - c.a) / 0.08, (c.b - t) / 0.08); break; }
  }
  const key = curSub ? curSub.id + '.' + curSub.k : '';
  if (subEl.dataset.key !== key) {
    subEl.dataset.key = key;
    subEl.textContent = '';
    if (curSub && curSub.who) { const w = document.createElement('span'); w.className = 'w'; w.textContent = curSub.who; subEl.appendChild(w); }
    if (curSub) subEl.appendChild(document.createTextNode(curSub.zh));
    subEn.textContent = curSub ? curSub.en : '';
  }
  subEl.style.opacity = op; subEn.style.opacity = op;

  for (const o of OV) overlay(o, t);
  await flush();
  return true;
};
window.META = { FPS, TOTAL: TL.total, W: 2340, H: 1080 };
