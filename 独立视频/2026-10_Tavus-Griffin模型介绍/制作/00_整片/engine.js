// 引擎：renderAt(t)。每帧：找场景 → 演示区（素材帧 / 官网页面镜头 / 卡片）→ 左栏（本期目录）→ 中英字幕（画外音 + 对白）→ 叠加层。全程画外音，没有出镜框。
const scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB');
const tocEl = document.getElementById('toc'), subEl = document.getElementById('subZh'), subEn = document.getElementById('subEn');

// 字体：官网的衬线标题用 Instrument Serif / Noto Serif SC（Google Fonts，OFL）。必须在第一帧之前加载完，否则会有几帧用后备字体；加载不到就报错，别悄悄渲出不一致的画面。
const SERIF_TXT = [TL.titleCard && Object.values(TL.titleCard).flat().join(''), TL.outroCard && (TL.outroCard.title || '')].filter(Boolean).join('') + '0123456789%+-.';
window.FONTS_READY = Promise.all([
  document.fonts.load('900 100px "Noto Serif SC"', SERIF_TXT),
  document.fonts.load('600 40px "Noto Serif SC"', SERIF_TXT),
  document.fonts.load('400 100px "Instrument Serif"', 'Griffin0123456789%'),
]).then(() => {
  const have = fam => [...document.fonts].some(f => f.family.replace(/["']/g, '') === fam && f.status === 'loaded');
  ['Noto Serif SC', 'Instrument Serif'].forEach(fam => { if (!have(fam)) window.__ERR.push('字体没加载：' + fam + '（Google Fonts 连不上？）'); });
});

// 左栏：本期目录（缩略图 + 序号·标签 + 名字）
tocEl.innerHTML = `<div class="hd"><div class="t">本期目录</div><div class="chip"><i></i>${TL.tocTag || 'TAVUS'}</div></div>` + (TL.sub ? `<div class="sub">${TL.sub}</div>` : '') +
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
  await window.FONTS_READY;
  const n = Math.min(TL.frames - 1, Math.max(0, Math.round(t * FPS)));
  const si = segAt(t), seg = TL.segs[si];

  // 演示区：素材帧（有帧就铺满）/ 官网页面镜头、卡片（叠加层画）
  const sf = FR.scr[n];
  if (sf) { setSrc(scrImg, 'media/' + sf); scrImg.style.visibility = 'visible'; }
  else scrImg.style.visibility = 'hidden';

  // 左栏：开场（chapter −1）都不亮；收尾（chapter ≥ 章数）都标“已看”
  const nCh = TL.chapters.length;
  tocIts.forEach((e, i) => e.className = 'it' + (i === seg.chapter ? ' now' : (seg.chapter >= nCh || (seg.chapter >= 0 && i < seg.chapter)) ? ' done' : ''));

  // 字幕（项目的中英双语标准：中文一行 52 px + 英文一行 30 px，居中，y 922 起）：TL.subs 里每条已经按标准拆好，
  // [a, b) 是显示区间（开始前 0.1 s ~ 结束后 0.45 s，互不重叠，build_timeline.py 算好的）；对白字幕前面带说话人小标签（who / whoCls）
  let cur = null, op = 0;
  for (const c of TL.subs) {
    if (t >= c.a && t < c.b) { cur = c; op = Math.min(1, (t - c.a) / 0.08, (c.b - t) / 0.08); break; }
  }
  const key = cur ? cur.id + '.' + cur.k : '';
  if (subEl.dataset.key !== key) {
    subEl.dataset.key = key;
    subEl.textContent = '';
    if (cur && cur.who) { const w = document.createElement('span'); w.className = 'w' + (cur.whoCls ? ' ' + cur.whoCls : ''); w.textContent = cur.who; subEl.appendChild(w); }
    if (cur) subEl.appendChild(document.createTextNode(cur.zh));
    subEn.textContent = cur ? cur.en : '';
  }
  subEl.style.opacity = op; subEn.style.opacity = op;

  for (const o of OV) overlay(o, t);
  await flush();
  return true;
};
window.META = { FPS, TOTAL: TL.total, W: 2340, H: 1080 };
