// 引擎：renderAt(t)。每帧：找场景 → 左栏（目录 + 进度点 + 规则卡片）→ 中英字幕 → 叠加层（scenes.js：推文 / 书官网 / 规则对比 / 缩略图墙…）。全程画外音，没有出镜框。
const scrImg = document.getElementById('scrimg'), ovBEl = document.getElementById('ovB');
const tocEl = document.getElementById('toc'), ruleEl = document.getElementById('rule'), subEl = document.getElementById('subZh'), subEn = document.getElementById('subEn');
const NR = 20;

// 左栏上：本期目录（章名都是字符串，≤ 3 条、每条 ≤ 7 字）+ 20 个进度点
tocEl.innerHTML = `<div class="t">本期目录<span>${TL.sub || ''}</span></div>` +
  TL.chapters.map((c, i) => `<div class="it" data-i="${i}"><span class="b"></span><span class="n">${i + 1}</span>${c}</div>`).join('') +
  `<div class="dots">${Array.from({ length: NR }, () => '<i></i>').join('')}</div>`;
const tocIts = [...tocEl.querySelectorAll('.it')], dotEls = [...tocEl.querySelectorAll('.dots i')];

// 左栏下：规则卡片
ruleEl.innerHTML = `<div class="rk">RULE<span class="n"></span><span class="of">/ ${NR}</span></div><div class="rt"></div><div class="re"></div>` +
  `<div class="rtake"><span></span></div><div class="rcred">图：《Refactoring UI》· 龙海 @longhaiqwe123 的文章</div>`;
const rkN = ruleEl.querySelector('.rk .n'), rtEl = ruleEl.querySelector('.rt'), reEl = ruleEl.querySelector('.re');
const takeEl = ruleEl.querySelector('.rtake'), takeSp = takeEl.querySelector('span');
let shownRule = 0;

// 叠加层：按需建；页面类镜头（o.fast）之间快切，不然两页内容叠在一起
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

// 有规则卡片的场景 mix = 1（目录挪到顶部、下面放规则卡片），没有时 mix = 0（目录垂直居中）；进出场景时 0.5 s 渐变
function ruleMix(t, seg, si) {
  const prev = TL.segs[si - 1];
  const now = seg.rule ? 1 : 0, was = prev && prev.rule ? 1 : 0;
  if (now === was) return now;
  return was + (now - was) * easeIO((t - seg.s) / 0.5);
}

window.renderAt = async function (t) {
  const n = Math.min(TL.frames - 1, Math.max(0, Math.round(t * FPS)));
  const si = segAt(t), seg = TL.segs[si];

  // 演示区：这条没有素材视频，frames.js 里全空
  const sf = FR.scr[n];
  if (sf) { setSrc(scrImg, 'media/' + sf); scrImg.style.visibility = 'visible'; }
  else scrImg.style.visibility = 'hidden';

  // 左栏：目录（开场 chapter −1 都不亮；收尾 chapter ≥ 章数都标“已看”）+ 进度点
  const nCh = TL.chapters.length;
  tocIts.forEach((e, i) => e.className = 'it' + (i === seg.chapter ? ' now' : (seg.chapter >= nCh || (seg.chapter >= 0 && i < seg.chapter)) ? ' done' : ''));
  const cur = seg.rule || 0, allDone = seg.chapter >= nCh;
  dotEls.forEach((d, i) => d.className = allDone || (cur && i + 1 < cur) ? 'done' : (cur && i + 1 === cur ? 'now' : ''));

  // 左栏：目录位置 + 规则卡片
  const mix = ruleMix(t, seg, si), tocH = tocEl.offsetHeight, RT = 52;
  tocEl.style.top = lerp(470 - tocH / 2, RT, mix) + 'px';
  if (seg.rule && seg.rule !== shownRule) {
    shownRule = seg.rule;
    const r = RULES[seg.rule] || { title: '', en: '', page: '', take: '' };
    rkN.textContent = String(seg.rule).padStart(2, '0');
    rtEl.textContent = r.title;
    reEl.innerHTML = `${r.en}<i>p.${r.page}</i>`;
    takeSp.textContent = r.take;
  }
  ruleEl.style.top = (RT + tocH + 26) + 'px';
  const pop = easeOut((t - seg.s) / 0.3);
  ruleEl.style.opacity = mix * (0.2 + 0.8 * pop);
  ruleEl.style.visibility = mix < 0.01 ? 'hidden' : 'visible';
  ruleEl.style.transform = `translateY(${(1 - pop) * 14}px)`;
  if (seg.rule && RULE_T[seg.rule]) {
    const tt = RULE_T[seg.rule].take, a = easeOut((t - tt) / 0.35);
    takeEl.style.opacity = a; takeEl.style.transform = `translateY(${(1 - a) * 10}px)`;
  }

  // 字幕（项目的中英双语标准：中文一行 52 px + 英文一行 30 px，居中，y 922 起）：TL.subs 里每条已经按标准拆好，
  // [a, b) 是显示区间（开始前 0.1 s ~ 结束后 0.45 s，互不重叠，build_timeline.py 算好的）
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
