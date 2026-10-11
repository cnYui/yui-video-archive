// 工具 + 叠加层（演示区 1474×829 内的坐标）。素材为主：视频素材场景只有左上角“来源 | 名称”、右上角来源、小字注释；官网页面镜头 = 截图 + 相机推拉 + 高亮框；开场标题盖在快剪上；收尾卡片放二维码和链接。
// 每个叠加层 [t0, t1] 显示（前后淡入淡出），t 用成片秒数；时间都按字幕条算：S('N07') = 这条开始说的时刻，P('N09', '词') = 说到这个词的时刻。
// 每个场景的 ui（plan.json 里写）：nt = 名称标签（'tl' 左上 / 'none'）、cr = 来源标签（'tr' 右上 / 'br' 右下 / 'none'）、cap = 小字注释位置（'bl' 左下 / 'br' 右下 / 'tl' 左上 / 'tl2' / 'tr'）。
const FPS = TL.fps;
window.__ERR = [];
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const easeIn = x => Math.pow(clamp(x), 3);
const easeIO = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
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

// ═════════════════════════════ 视频素材 / 官网页面镜头：左上角“来源 | 名称”、右上角来源、小字注释
Object.entries(TL.clips).forEach(([cid, k]) => {
  if (k.overlay !== 'clip') return;
  const u = k.ui || {};
  ovB(k.s + 0.1, k.e - 0.05, p => {
    const nt = u.nt === 'none' ? null : at(p, null, null, null, null, 'nametag', {}, `<span class="m">${k.tag}</span><span class="e">${k.name}</span>`);
    const cr = u.cr === 'none' ? null : at(p, null, null, null, null, 'credit' + (u.cr === 'br' ? ' br' : ''), {}, k.credit);
    return lt => { if (nt) show(nt, lt, 0, { dy: -10 }); if (cr) show(cr, lt, 0.12, { dy: -10 }); };
  });
  k.caps.forEach(c => ovB(c.s, c.e, p => {
    const el = at(p, null, null, null, null, 'cappill' + (u.cap && u.cap !== 'bl' ? ' ' + u.cap : ''), {}, `<b>${c.zh}</b>` + (c.sub ? `<small>${c.sub}</small>` : ''));
    return lt => show(el, lt, 0, { dy: 12 });
  }));
});

// ═════════════════════════════ 官网页面镜头：一张截图（2 倍像素）+ 相机推拉（cam 关键帧）+ 高亮框（hl）
function camAt(cam, lt) {
  if (!cam || !cam.length) return { x: .5, y: .5, z: 1 };
  if (lt <= cam[0].t) return cam[0];
  for (let i = 0; i + 1 < cam.length; i++) {
    const a = cam[i], b = cam[i + 1];
    if (lt <= b.t) { const u = easeIO((lt - a.t) / Math.max(1e-6, b.t - a.t)); return { x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u), z: lerp(a.z, b.z, u) }; }
  }
  return cam[cam.length - 1];
}
Object.entries(TL.clips).forEach(([cid, k]) => {
  if (k.kind !== 'shot') return;
  const sh = k.shot;
  ovB(k.s, k.e, p => {
    const stage = at(p, 0, 0, 1474, 829, 'shotstage', {}, '');
    const im = mk(stage, 'shotimg', {}, '', 'img');
    im.src = 'media/shots/' + sh.img + '.png'; PENDING.add(im);
    const hls = sh.hl.map(h => ({ h, el: mk(stage, 'hl', {}, h.label ? `<div class="tag${h.in ? ' in' : ''}">${h.label}</div>` : '') }));
    const fit = Math.min(1474 * sh.fit / sh.w, 829 * sh.fit / sh.h);          // z = 1：整张放进演示区（留 6% 边）
    return lt => {
      const c = camAt(sh.cam, lt);
      const W = sh.w * fit * c.z, H = sh.h * fit * c.z;
      const L = 737 - c.x * W, T = 414.5 - c.y * H;
      im.style.left = px(L); im.style.top = px(T); im.style.width = px(W); im.style.height = px(H);
      hls.forEach(({ h, el }) => {
        const v = clamp(Math.min(easeOut((lt - h.a) / 0.35), 1 - easeIn((lt - h.b) / 0.3)));
        const [x0, y0, x1, y1] = h.box, pad = h.pad;
        el.style.left = px(L + x0 * W - pad); el.style.top = px(T + y0 * H - pad);
        el.style.width = px((x1 - x0) * W + 2 * pad); el.style.height = px((y1 - y0) * H + 2 * pad);
        el.style.opacity = v; el.style.visibility = v < 0.01 ? 'hidden' : 'visible';
        el.style.transform = `scale(${lerp(1.05, 1, easeOut((lt - h.a) / 0.35))})`;
      });
    };
  });
});

// ═════════════════════════════ 开场：标题盖在几段素材的快剪上
Object.entries(TL.clips).forEach(([cid, k]) => {
  if (k.overlay !== 'title') return;
  const T = TL.titleCard || {};
  ovB(k.s + ((k.ui && k.ui.titleAt != null) ? k.ui.titleAt : 0.2), k.e - 0.15, p => {      // ui.titleAt：先看几秒素材再出标题
    at(p, 0, 0, 1474, 829, 'dim', {});
    const kick = at(p, 0, 168, 1474, 40, 'ttl', {}, `<div class="k"><i></i>${T.kick || ''}</div>`);
    const a = at(p, 0, 224, 1474, 140, 'ttl', {}, `<div class="a">${T.a || ''}</div>`);
    const b = at(p, 0, 352, 1474, 240, 'ttl', {}, `<div class="b">${T.b || ''}</div>`);
    const chips = at(p, 0, 628, 1474, 60, 'ttl', {}, (T.chips || []).map((c, i) => `<span class="chip${i === 0 ? ' fill' : ''}">${c}</span>`).join(''));
    return lt => { show(kick, lt, 0.05, { dy: -10 }); show(a, lt, 0.15, { dy: 14 }); show(b, lt, 0.3, { dy: 20, scale: .94 }); show(chips, lt, 0.8, { dy: 12 }); };
  });
});

// ═════════════════════════════ 收尾卡片：官网页面的画面 + 二维码 + 链接 + 全部来源
Object.entries(TL.clips).forEach(([cid, k]) => {
  if (k.overlay !== 'outro') return;
  const O = TL.outroCard || {};
  ovB(k.s + 0.05, k.e + 6, p => {                                  // 收尾卡片一直留到正片最后一帧（后面接悠一片尾），不提前淡出
    const kk = at(p, 0, 20, 1474, 34, 'kick', { textAlign: 'center' }, O.kick || '');
    const h = at(p, 0, 52, 1474, 80, 'h1', { textAlign: 'center' }, O.title || '');
    const ph = at(p, 120, 150, 720, null, 'photo', {}, `<img src="media/card/${O.img || 'page'}.jpg">`);      // 实际高约 409
    PENDING.add(ph.querySelector('img'));
    const phc = at(p, 120, 580, 720, 30, 'cap', { textAlign: 'center', fontSize: '24px' }, O.imgCap || '');
    const qr = at(p, 1000, 150, 380, 380, 'qrtile', {}, '<img src="media/qr.png">');
    PENDING.add(qr.querySelector('img'));
    const qc = at(p, 1000, 552, 380, 40, 'cap', { textAlign: 'center', fontSize: '26px' }, O.qrCap || '扫码，或在浏览器里打开链接');
    const url = at(p, 0, 628, null, null, 'urlpill', { width: 'max-content', height: 'auto', left: '0px', right: '0px' }, O.url || '');
    const fine = at(p, 0, 716, 1474, 30, 'credits', {}, O.fine || '');
    const src = at(p, 0, 748, 1474, 66, 'credits', {}, O.sources || '');
    return lt => { show(kk, lt, 0.05); show(h, lt, 0.12, { dy: -12 }); show(ph, lt, 0.3, { dy: 22, rot: -1.5 }); show(phc, lt, 0.5); show(qr, lt, 0.5, { dy: 22, rot: 1.5 }); show(qc, lt, 0.7); show(url, lt, 0.9, { dy: 14 }); show(fine, lt, 1.1); show(src, lt, 1.3); };
  });
});
