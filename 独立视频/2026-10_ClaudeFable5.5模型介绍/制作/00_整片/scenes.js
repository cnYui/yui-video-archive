// 工具 + 叠加层（演示区 1474×829 内的坐标）。素材为主：素材场景只有左上角“模型 | 作品名”、右上角来源、左下角小字注释；开场标题盖在快剪上；收尾卡片放二维码和链接。
// 每个叠加层 [t0, t1] 显示（前后淡入淡出），t 用成片秒数；时间都按字幕条算：S('N07') = 这条开始说的时刻，P('N09', '词') = 说到这个词的时刻。
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
  const rot = o.rot != null ? ` rotate(${o.rot}deg)` : '';
  el.style.transform = `translate(${dx * (1 - a)}px, ${dy * (1 - a)}px)` + (o.scale ? ` scale(${lerp(o.scale, 1, a)})` : '') + rot;
  return v;
}
const PENDING = new Set();
function setSrc(img, src) { if (img.dataset.src !== src) { img.dataset.src = src; img.src = src; PENDING.add(img); } }
async function flush() {
  const arr = [...PENDING]; PENDING.clear();
  await Promise.all(arr.map(i => i.decode().catch(() => window.__ERR.push('图片加载失败 ' + (i.dataset.src || i.src)))));
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

const OV = [];   // {t0, t1, build(root) → update(lt)}
const ovB = (t0, t1, build) => OV.push({ t0, t1, build });

// ═════════════════════════════ 素材场景：左上角“模型 | 作品名”、右上角来源、左下角小字注释
Object.entries(TL.clips).forEach(([cid, k]) => {
  if (k.overlay !== 'clip') return;
  ovB(k.s + 0.1, k.e - 0.05, p => {
    const nt = at(p, null, null, null, null, 'nametag', {}, `<span class="m">${k.tag}</span><span class="e">${k.name}</span>`);
    const cr = at(p, null, null, null, null, 'credit', {}, '画面：' + k.credit);
    return lt => { show(nt, lt, 0, { dy: -10 }); show(cr, lt, 0.12, { dy: -10 }); };
  });
  k.caps.forEach(c => ovB(c.s, c.e, p => {
    const el = at(p, null, null, null, null, 'cappill', {}, `<b>${c.zh}</b>` + (c.sub ? `<small>${c.sub}</small>` : ''));
    return lt => show(el, lt, 0, { dy: 12 });
  }));
});

// ═════════════════════════════ 开场：标题盖在四段素材的快剪上
Object.entries(TL.clips).forEach(([cid, k]) => {
  if (k.overlay !== 'title') return;
  const T = TL.titleCard || {};
  ovB(k.s + 0.2, k.e - 0.15, p => {
    at(p, 0, 0, 1474, 829, 'dim', {});
    const kick = at(p, 0, 168, 1474, 40, 'ttl', {}, `<div class="k">${T.kick || ''}</div>`);
    const a = at(p, 0, 224, 1474, 140, 'ttl', {}, `<div class="a">Claude</div>`);
    const b = at(p, 0, 352, 1474, 240, 'ttl', {}, `<div class="b">Fable 5.5</div>`);
    const chips = at(p, 0, 628, 1474, 60, 'ttl', {}, (T.chips || []).map((c, i) => `<span class="chip${i === 0 ? ' fill' : ''}">${c}</span>`).join('&nbsp;&nbsp;'));
    return lt => { show(kick, lt, 0.05, { dy: -10 }); show(a, lt, 0.15, { dy: 14 }); show(b, lt, 0.3, { dy: 20, scale: .94 }); show(chips, lt, 0.8, { dy: 12 }); };
  });
});

// ═════════════════════════════ 官方现状卡片：已公布 / 未公布 / 传闻，每一行跟着对应那句话出现
Object.entries(TL.clips).forEach(([cid, k]) => {
  if (k.overlay !== 'facts') return;
  const F = TL.factsCard || {};
  const t0 = k.s + 0.05;
  ovB(t0, k.e - 0.1, p => {
    const kk = at(p, 0, 34, 1474, 34, 'kick', { textAlign: 'center' }, F.kick || '');
    const h = at(p, 0, 70, 1474, 80, 'h1', { textAlign: 'center' }, F.title || '');
    const rows = (F.rows || []).map((r, i) => at(p, 90, 186 + i * 190, 1294, 168, 'frow ' + (r.cls || ''), {},
      `<span class="fl">${r.label}</span><span class="fv">${r.text}${r.src ? `<small>${r.src}</small>` : ''}</span>`));
    return lt => {
      show(kk, lt, 0.05); show(h, lt, 0.12, { dy: -12 });
      rows.forEach((e, i) => show(e, lt, (F.rows[i].cue ? S(F.rows[i].cue) : k.s + 0.6 + i * 2.6) - t0 - 0.15, { dy: 18 }));
    };
  });
});

// ═════════════════════════════ 收尾卡片：超人飞行的页面 + 二维码 + 链接
Object.entries(TL.clips).forEach(([cid, k]) => {
  if (k.overlay !== 'outro') return;
  const O = TL.outroCard || {};
  ovB(k.s + 0.05, k.e - 0.1, p => {
    const kk = at(p, 0, 30, 1474, 34, 'kick', { textAlign: 'center' }, O.kick || '');
    const h = at(p, 0, 66, 1474, 80, 'h1', { textAlign: 'center' }, O.title || '');
    const ph = at(p, 90, 168, 800, null, 'photo', {}, `<img src="media/card/${O.img || 'superman'}.jpg">`);      // 16:9，实际高约 464
    PENDING.add(ph.querySelector('img'));
    const phc = at(p, 90, 646, 800, 34, 'cap', { textAlign: 'center', fontSize: '24px' }, O.imgCap || '');
    const qr = at(p, 990, 168, 400, 400, 'qrtile', {}, '<img src="media/qr.png">');
    PENDING.add(qr.querySelector('img'));
    const qc = at(p, 990, 584, 400, 40, 'cap', { textAlign: 'center', fontSize: '28px' }, O.qrCap || '扫码，或在浏览器里打开链接');
    const url = at(p, 0, 702, null, null, 'urlpill', { width: 'max-content', height: 'auto', left: '0px', right: '0px' }, O.url || '');
    const fine = at(p, 0, 784, 1474, 34, 'cap', { textAlign: 'center', fontSize: '22px', color: '#9AA1AC' }, O.fine || '');
    return lt => { show(kk, lt, 0.05); show(h, lt, 0.12, { dy: -12 }); show(ph, lt, 0.3, { dy: 22, rot: -1.5 }); show(phc, lt, 0.5); show(qr, lt, 0.5, { dy: 22, rot: 1.5 }); show(qc, lt, 0.7); show(url, lt, 0.9, { dy: 14 }); show(fine, lt, 1.1); };
  });
});
