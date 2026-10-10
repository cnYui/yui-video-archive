// 工具 + 通用卡片（演示区 1474×829 内的坐标）+ 发布会画面上的角标。
// 卡片内容写在台本 plan 里（card：hook / list / stat / table），build_timeline.py 把它放进 TL.segs[i].card，这里按类型画。
// 元素出现的时刻：at = 字幕条号（'N05'，说这句开始时出现）/ 'N05@短语'（说到这个词）/ 数字（离本段开始的秒数）；不写就按顺序错开。
// 字幕条：画外音 = N…；现场原话的中文同传 = K…（Fish 网页版「赛马娘（曼波欧耶版）」，同一个声音）。
const FPS = TL.fps;
window.__ERR = [];
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const easeIn = x => Math.pow(clamp(x), 3);
const lerp = (a, b, x) => a + (b - a) * x;
const px = v => v + 'px';

function mk(parent, cls = '', style = {}, html = '', tag = 'div') {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  for (const [k, v] of Object.entries(style)) if (v !== undefined && v !== null) e.style[k] = typeof v === 'number' && !['opacity', 'zIndex', 'fontWeight', 'lineHeight', 'flex'].includes(k) ? px(v) : v;
  if (html) e.innerHTML = html;
  parent.appendChild(e);
  return e;
}
const at = (parent, x, y, w, h, cls = '', style = {}, html = '') => mk(parent, 'abs ' + cls, Object.assign({ left: x, top: y, width: w, height: h }, style), html);
function show(el, lt, t0, o = {}) {
  const d = o.d ?? 0.4, dy = o.dy ?? 16, dx = o.dx ?? 0;
  const a = easeOut((lt - t0) / d);
  const b = o.t1 == null ? 1 : 1 - easeIn((lt - o.t1) / (o.d1 ?? 0.3));
  const v = Math.min(a, b) * (o.max ?? 1);
  el.style.opacity = v;
  el.style.visibility = v < 0.002 ? 'hidden' : 'visible';
  el.style.transform = `translate(${dx * (1 - a)}px, ${dy * (1 - a)}px)` + (o.scale ? ` scale(${lerp(o.scale, 1, a)})` : '');
  return v;
}
const PENDING = new Set();
function setSrc(img, src) { if (img.dataset.src !== src) { img.dataset.src = src; img.src = src; PENDING.add(img); } }
async function flush() {
  const arr = [...PENDING]; PENDING.clear();
  await Promise.all(arr.map(i => i.decode().catch(() => window.__ERR.push('图片加载失败 ' + i.dataset.src))));
}

// ─── 字幕条时间
const CU = {}; TL.cues.forEach(q => CU[q.id] = q);
const S = id => { if (!CU[id]) throw new Error('没有字幕条 ' + id); return CU[id].s; };
const E = id => { if (!CU[id]) throw new Error('没有字幕条 ' + id); return CU[id].e; };
function P(id, phrase, off = 0) {
  const q = CU[id]; const k = q.zh.indexOf(phrase);
  if (k < 0) throw new Error(`「${phrase}」不在 ${id}`);
  return q.s + (q.e - q.s) * (k / q.zh.length) + off;
}
const md = s => String(s).replace(/\*\*(.+?)\*\*/g, '<span class="mark">$1</span>');
const mb = s => String(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
// 元素出现时刻（卡片里的局部时间，0 = 本段开始）
function when(seg, spec, dflt) {
  if (spec == null) return dflt;
  if (typeof spec === 'number') return spec;
  const [id, ph] = String(spec).split('@');
  return (ph ? P(id, ph) : S(id)) - seg.s;
}

const OV = [];   // {t0, t1, build(root) → update(lt), clip?:true（发布会画面上的角标）}
const ovB = (t0, t1, build) => OV.push({ t0, t1, build });
const ovClip = (t0, t1, build) => OV.push({ t0, t1, build, clip: true });

// ═════════════════════════════ 卡片
function buildCard(p, seg) {
  const c = seg.card, els = [];             // els: [元素, 出现时刻, show 选项]
  const kick = (txt, y = 70) => els.push([at(p, 0, y, 1474, 40, 'kick', { textAlign: 'center' }, txt), 0.1, {}]);
  if (c.type === 'hook') {
    const n = c.lines.length, sz = c.size || 112, pitch = Math.round(sz * 1.45), y0 = 250 + (c.dy || 0) - (n - 2) * 40;
    kick(c.kicker || TL.kicker, y0 - 100);
    c.lines.forEach((tx, i) => els.push([at(p, 0, y0 + i * pitch, 1474, pitch, 'big', { textAlign: 'center', fontSize: sz + 'px', lineHeight: pitch + 'px' }, md(tx)),
      when(seg, c.at && c.at[i], 0.25 + i * 0.4), { scale: 0.94 }]));
    if (c.chips) els.push([at(p, 0, y0 + n * pitch + 50, 1474, 70, '', { textAlign: 'center' },
      c.chips.map(([tx, cls]) => `<span class="chip lg ${cls || ''}">${tx}</span>`).join('&nbsp;&nbsp;&nbsp;')), when(seg, c.chipAt, 0.25 + n * 0.4 + 0.2), {}]);
  } else if (c.type === 'list') {
    els.push([at(p, 0, 40, 1474, 70, 'h2', { textAlign: 'center' }, md(c.title)), 0.1, {}]);
    const n = c.items.length, lg = n <= 3, pitch = lg ? 188 : Math.min(138, Math.floor(660 / n));
    c.items.forEach((it, i) => {
      const row = at(p, null, (lg ? 170 : 140) + i * pitch, null, null, 'row' + (lg ? ' lg' : '') + (it.hot ? ' hot' : ''), {},
        `<span class="n">${it.n ?? (i + 1)}</span><div><div class="tt">${md(it.tt)}</div>${it.dd ? `<div class="dd">${it.dd}</div>` : ''}</div>` +
        (it.tag ? `<span class="chip tag ${it.hot ? 'fill' : ''}">${it.tag}</span>` : ''));
      els.push([row, when(seg, it.at, 0.5 + i * 0.5), { dy: 14 }]);
    });
  } else if (c.type === 'stat') {
    kick(c.kicker || TL.kicker);
    els.push([at(p, 0, 120, 1474, 330, 'stat', { color: c.color || 'var(--orange)' }, `${c.num}<small>${c.unit || ''}</small>`), when(seg, c.numAt, 0.2), { scale: 0.9 }]);
    els.push([at(p, 0, 470, 1474, 80, 'h1', { textAlign: 'center' }, md(c.cap)), when(seg, c.capAt, 0.7), {}]);
    (c.sub || []).forEach(([k, v], i, a) => els.push([at(p, 0, 610 + i * 80, 1474, 70, 'h2', { textAlign: 'center' }, `<span style="color:var(--gray)">${k}</span>　<span style="color:var(--orange)">${v}</span>`),
      when(seg, c.subAt && c.subAt[i], 1.1 + i * 0.5), {}]));
  } else if (c.type === 'table') {
    els.push([at(p, 0, 40, 1474, 70, 'h2', { textAlign: 'center' }, md(c.title)), 0.1, {}]);
    const box = at(p, null, 130, null, null, 'tbl', {});
    const mkRow = (cls, y, k, vs) => mk(box, 'tr ' + cls, { top: y }, `<div class="c0">${k}</div>` + vs.map(v => `<div class="cv">${v}</div>`).join(''));
    els.push([mkRow('hd', 0, '', c.cols), 0.2, {}]);
    c.rows.forEach((r, i) => els.push([mkRow('' + (r.hot ? 'hot' : ''), 80 + i * 144, r.k, r.v), when(seg, r.at, 0.5 + i * 0.6), { dy: 14 }]));
    if (c.note) els.push([at(p, 0, 130 + 80 + c.rows.length * 144 + 20, 1474, 50, 'cap', { textAlign: 'center' }, c.note), when(seg, c.noteAt, 0.5 + c.rows.length * 0.6), {}]);
  }
  return lt => els.forEach(([e, t0, o]) => show(e, lt, t0, o));
}
TL.segs.forEach(seg => { if (seg.kind === 'vo' && seg.card) ovB(seg.s, seg.e, p => buildCard(p, seg)); });

// ═════════════════════════════ 要点标签：每个要点第一次出现在发布会画面上时，左上角显示 3 秒
{
  const seen = new Set();
  TL.segs.forEach(s => {
    if (s.kind !== 'clip' || seen.has(s.chapter)) return; seen.add(s.chapter);
    ovClip(s.s + 0.3, Math.min(s.e, s.s + 3.6), p => {
      const c = at(p, 22, 20, null, null, 'chapchip', { position: 'absolute' }, `<span>${String(s.chapter + 1).padStart(2, '0')}</span>${TL.chapters[s.chapter]}`);
      return lt => show(c, lt, 0, { dy: -12 });
    });
  });
}

// ═════════════════════════════ 发布会画面：来源角标 + 讲话人（同传时跟着当前这句走）
Object.entries(TL.clips).forEach(([cid, k]) => {
  const mine = TL.cues.filter(q => q.kind === 'clip' && q.seg === cid);
  const dub = k.mode === 'dub';
  ovClip(k.s + 0.1, k.e, p => {
    const c = at(p, null, 20, null, null, 'credit', { position: 'absolute' }, '画面：' + k.credit + (dub ? ' · 原声压低，中文同传' : ' · 原声压低'));
    const w = (dub || k.where) ? at(p, null, null, null, null, 'who', { position: 'absolute' }, '') : null;
    let last = '';
    return lt => {
      show(c, lt, 0, { dy: -8 });
      if (!w) return;
      const t = k.s + 0.1 + lt;
      const cur = dub ? (mine.find(q => t >= q.s - 0.25 && t < q.e + 0.6) || mine.find(q => q.s > t) || mine[mine.length - 1]) : null;
      const key = (cur && cur.who || '') + '|' + k.where;
      if (key !== last) { last = key; w.innerHTML = cur && cur.who ? `${cur.who}<small>${k.where || ''}</small>` : (k.where || ''); }
      show(w, lt, 0.3, { dy: 8 });
    };
  });
});

// ═════════════════════════════ 画面上的小标注（台本 plan 的 callouts：{t 离片段开头秒, d 显示几秒, text, pos}）
const POS = { tl: { left: 22, top: 84 }, tr: { right: 22, top: 84 }, bl: { left: 22, bottom: 96 }, br: { right: 22, bottom: 96 }, bc: { left: 0, right: 0, bottom: 96, margin: '0 auto', width: 'fit-content' } };
Object.entries(TL.clips).forEach(([cid, k]) => (k.callouts || []).forEach(co => {
  ovClip(k.s + co.t, Math.min(k.e, k.s + co.t + (co.d || 3)), p => {
    const e = co.hook ? at(p, null, null, null, null, 'hook', co.size ? { fontSize: co.size + 'px' } : {}, mb(co.text)) : at(p, null, null, null, null, 'pill', Object.assign({ position: 'absolute', fontSize: (co.size || 32) + 'px' }, POS[co.pos || 'tl']), mb(co.text));
    return lt => show(e, lt, 0, { dy: 10 });
  });
}));
