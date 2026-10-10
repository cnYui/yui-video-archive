// 工具 + 叠加层（演示区 1474×829 内的坐标）。素材全是真实画面：推文 / 书官网 / 墨问页面录屏（pageShot）+ 文章里的 20 张前后对比图（ruleShot）；上面只加少量标注，不放整屏文字卡片。
// 每个叠加层 [t0, t1] 显示（前后淡入淡出），t 用成片秒数；时间都按字幕条算：S('A01') = 这条开始说的时刻，P('A02', '词') = 说到这个词的时刻。
// 字幕条：A / R / Z 开头的 id = 画外音（Fish 网页版「温柔男生」S2 Pro）；字幕是中英双语，见 engine.js / build_timeline.py。
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
const segOf = id => { const g = TL.segs.find(x => x.id === id); if (!g) throw new Error('没有场景 ' + id); return g; };

const OV = [];   // {t0, t1, build(root) → update(lt), fast?:true（页面类镜头之间快切）}
const ovPage = (t0, t1, build) => OV.push({ t0, t1, build, fast: true });

const DW = 1474, DH = 829, M = 14;                         // 演示区内容尺寸、内边距
const IMGDIR = 'media/img/';
const IMS = window.IMGS || {};                              // 图片名 → [宽, 高]（build_rules.py 写进 rules.js）

// ═════════════════════════════ 规则卡片里“记住”一句出现的时刻（engine.js 用）：默认是这条规则的最后一句开口时
const RULE_T = {};
for (const n of Object.keys(RULES)) {
  const sid = 'S' + String(n).padStart(2, '0');
  const cues = TL.cues.filter(q => q.seg === sid);
  RULE_T[n] = { take: RULES[n].takeAt ? S(RULES[n].takeAt) : (cues.length ? cues[cues.length - 1].s : segOf(sid).e - 2) };
}

// ═════════════════════════════ 官方页面 / 推文录屏
// pageShot(从哪句, 到哪句, 页面图名字, [[要高亮的句子, 刷上的时刻, 底部中文译文?], …], {start: 起始滚动位置（图片像素）, pad: 比最后一句再多留的秒数})
// 图是 capture_pages.py 截的，铺满演示区宽度；每条高亮出现前 0.95 s 开始往它那里滚，滚到画面偏上三分之一的位置。
// 深色页面（书官网首屏）里荧光笔看不见，改成橙色边框。
const PAGE_BAR = 46;
function pageShot(from, to, key, marks, opt = {}) {
  const m = PG[key]; if (!m) throw new Error('没有页面图 ' + key);
  const sg0 = TL.segs.find(g => g.s <= S(from) + 1e-6 && S(from) < g.e), sg1 = TL.segs.find(g => g.s <= E(to) + 1e-6 && E(to) < g.e + 1e-6);
  const t0 = sg0 ? Math.min(S(from) - 0.2, sg0.s) : S(from) - 0.2, t1 = Math.max(E(to) + 0.12, sg1 ? sg1.e - 0.02 : 0) + (opt.pad || 0);
  const dark = (() => { const c = parseInt(m.bg.slice(1), 16); return ((c >> 16) * .3 + ((c >> 8) & 255) * .59 + (c & 255) * .11) < 90; })();
  ovPage(t0, t1, p => {
    const VW = DW, VH = 829 - PAGE_BAR, k = VW / m.w, IH = m.h * k, PADB = opt.padb ?? 200;
    const win = at(p, 0, 0, VW, 829, '', { background: m.bg, overflow: 'hidden' });
    const view = mk(win, '', { position: 'absolute', left: 0, top: PAGE_BAR, width: VW, height: VH, overflow: 'hidden', background: m.bg });
    const sheet = mk(view, '', { position: 'absolute', left: 0, top: 0, width: VW, height: IH + PADB, willChange: 'transform' });
    const img = mk(sheet, '', { position: 'absolute', left: 0, top: 0, width: VW, height: IH, display: 'block' }, '', 'img');
    setSrc(img, 'media/' + m.src);
    const url = m.url.replace(/^https?:\/\//, '').replace(/\/$/, '');
    mk(win, '', { position: 'absolute', left: 0, top: 0, width: VW, height: PAGE_BAR, background: '#E9EBEF', borderBottom: '1px solid #CFD3DA', display: 'flex', alignItems: 'center', gap: '10px', padding: '0 18px', zIndex: 3 },
      '<i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FF5F57"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FEBC2E"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#28C840"></i>' +
      `<span style="margin-left:12px;flex:1;height:30px;line-height:30px;border-radius:15px;background:#fff;padding:0 18px;font:600 19px 'JetBrains Mono';color:#4B5563;white-space:nowrap;overflow:hidden">${url}</span>`);
    const zhBar = mk(win, '', { position: 'absolute', left: 0, right: 0, bottom: 0, height: 100, background: 'rgba(27,27,31,.93)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: "800 40px 'Noto Sans SC'", padding: '0 36px', zIndex: 4, opacity: 0, whiteSpace: 'nowrap' });
    const hs = marks.map(([needle, tm, zh]) => {
      const rects = m.marks[needle];
      if (!rects) throw new Error(`页面图 ${key} 里没有高亮句子「${needle}」`);
      const frame = needle.startsWith('#sel:') || needle.startsWith('@rect:') || dark;            // 图表 / 手动框选 / 深色页面：画橙色边框，不填色
      const els = rects.map(([x, y, w, h]) => mk(sheet, '', frame
        ? { position: 'absolute', left: x * k - 6, top: y * k - 6, width: w * k + 12, height: h * k + 12, border: '6px solid #FF4F1A', borderRadius: '12px', boxShadow: '0 0 0 8px rgba(255,79,26,.16)', transformOrigin: '0 50%', visibility: 'hidden' }
        : { position: 'absolute', left: x * k - 5, top: y * k - 3, width: w * k + 10, height: h * k + 6, background: 'rgba(255,205,40,.64)', mixBlendMode: 'multiply', borderRadius: '5px', transformOrigin: '0 50%', visibility: 'hidden' }));
      return { els, t: tm - t0, cy: (rects[0][1] + rects[0][3] / 2) * k, top: rects[0][1] * k, tall: rects[0][3] * k > VH * 0.55, zh };
    });
    const maxS = Math.max(0, IH + PADB - VH);
    hs.forEach(h => h.target = clamp(h.tall ? h.top - VH * 0.05 : h.cy - VH * 0.34, 0, maxS));      // 比窗口还高的顶部对齐
    const start = opt.start != null ? clamp(opt.start * k, 0, maxS) : (hs.length ? hs[0].target : 0);
    const seq = [{ t: -99, target: start }, ...hs];
    let curZh = null;
    return lt => {
      let sc = start;
      for (let i = 1; i < seq.length; i++) {
        const a = seq[i].t - 0.95, b = seq[i].t - 0.2;
        if (lt >= a) sc = lerp(seq[i - 1].target, seq[i].target, easeIO((lt - a) / (b - a)));
      }
      sheet.style.transform = `translateY(${-sc}px)`;
      hs.forEach((h, i) => {
        const a = easeOut((lt - h.t) / 0.45), nxt = hs[i + 1] ? hs[i + 1].t : 1e9;
        h.els.forEach(e => { e.style.visibility = a > 0.001 ? 'visible' : 'hidden'; e.style.transform = `scaleX(${a})`; e.style.opacity = lt > nxt + 0.25 ? 0.4 : 1; });
      });
      let cur = null;                                            // 底部译文：最近一条带译文且已经刷上的
      for (const h of hs) if (h.zh && lt >= h.t) cur = h;
      if (cur !== curZh) { curZh = cur; if (cur) zhBar.textContent = cur.zh; }
      zhBar.style.opacity = cur ? easeOut((lt - cur.t) / 0.3) : 0;
    };
  });
}

// ═════════════════════════════ 书官网的完整目录：整页往下滚，规则对应的章名依次亮起（来一个亮一个），右上角计数
// tocShot(从哪句, 到哪句, 页面图名字, {scale, a, b, count})：scale = 页面图缩放（默认 0.8，图宽 1600）；a / b = 滚动开始 / 结束距场景开头 / 结尾的秒数
function tocShot(from, to, key, opt = {}) {
  const m = PG[key]; if (!m) throw new Error('没有页面图 ' + key);
  const sg0 = TL.segs.find(g => g.s <= S(from) + 1e-6 && S(from) < g.e), sg1 = TL.segs.find(g => g.s <= E(to) + 1e-6 && E(to) < g.e + 1e-6);
  const t0 = sg0.s, t1 = sg1.e;
  ovPage(t0, t1, p => {
    const VW = DW, VH = 829 - PAGE_BAR, k = (opt.scale ?? 0.8), IW = m.w * k, IH = m.h * k;
    const win = at(p, 0, 0, VW, 829, '', { background: m.bg, overflow: 'hidden' });
    const view = mk(win, '', { position: 'absolute', left: 0, top: PAGE_BAR, width: VW, height: VH, overflow: 'hidden', background: m.bg });
    const sheet = mk(view, '', { position: 'absolute', left: (VW - IW) / 2, top: 0, width: IW, height: IH, willChange: 'transform' });
    const img = mk(sheet, '', { position: 'absolute', left: 0, top: 0, width: IW, height: IH, display: 'block' }, '', 'img');
    setSrc(img, 'media/' + m.src);
    const url = m.url.replace(/^https?:\/\//, '').replace(/\/$/, '');
    mk(win, '', { position: 'absolute', left: 0, top: 0, width: VW, height: PAGE_BAR, background: '#E9EBEF', borderBottom: '1px solid #CFD3DA', display: 'flex', alignItems: 'center', gap: '10px', padding: '0 18px', zIndex: 3 },
      '<i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FF5F57"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FEBC2E"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#28C840"></i>' +
      `<span style="margin-left:12px;flex:1;height:30px;line-height:30px;border-radius:15px;background:#fff;padding:0 18px;font:600 19px 'JetBrains Mono';color:#4B5563;white-space:nowrap;overflow:hidden">${url}</span>`);
    const dur = t1 - t0, a = opt.a ?? 0.5, b = dur - (opt.b ?? 1.0), maxS = Math.max(0, IH - VH + 60);
    const first = Object.values(m.marks).map(r => r[0][1] * k).sort((x, y) => x - y)[0];
    const s0 = clamp(first - VH * 0.25, 0, maxS);
    const scroll = lt => lerp(s0, maxS, easeIO((lt - a) / (b - a)));
    // 每个章名什么时候进入画面偏下三分之二的位置：数值扫一遍
    const items = Object.entries(m.marks).map(([name, rects]) => {
      const cy = (rects[0][1] + rects[0][3] / 2) * k;
      let tt = dur;
      for (let lt = 0; lt <= dur; lt += 1 / 60) if (cy - scroll(lt) <= VH * 0.62) { tt = lt; break; }
      const els = rects.map(([x, y, w, h]) => mk(sheet, '', { position: 'absolute', left: x * k - 5, top: y * k - 3, width: w * k + 10, height: h * k + 6, background: 'rgba(255,205,40,.7)', mixBlendMode: 'multiply', borderRadius: '5px', transformOrigin: '0 50%', visibility: 'hidden' }));
      return { els, t: tt + 0.15 };
    }).sort((x, y) => x.t - y.t);
    const cnt = at(p, null, null, null, null, 'credit', { top: PAGE_BAR + 20, right: 22 }, '');
    cnt.style.background = 'rgba(255,79,26,.96)';
    return lt => {
      sheet.style.transform = `translateY(${-scroll(lt)}px)`;
      let n = 0;
      items.forEach(it => { const v = easeOut((lt - it.t) / 0.4); if (v > 0.001) n++; it.els.forEach(e => { e.style.visibility = v > 0.001 ? 'visible' : 'hidden'; e.style.transform = `scaleX(${v})`; }); });
      cnt.textContent = `文章覆盖 ${n} / 50 章`;
      cnt.style.opacity = n ? 1 : 0;
    };
  });
}

// ═════════════════════════════ 单张图片（文章封面 / 反面例子）：铺进演示区，缓慢推近，可加高亮框和说明条
// imgStill(场景 id, 图片名, {crop: [x, y, w, h]（图片像素）, credit, boxes: [{r: [x, y, w, h], t, t1}], pills: [{t, t1, text, sub, x, y}], zoom})
function imgStill(sceneId, name, o = {}) {
  const sg = segOf(sceneId), IM = IMS[name]; if (!IM) throw new Error('没有图片尺寸 ' + name);
  ovPage(sg.s, sg.e, p => {
    const crop = o.crop || [0, 0, IM[0], IM[1]];
    const UW = DW - 2 * M, UH = DH - 2 * M, s = Math.min(UW / crop[2], UH / crop[3], o.maxScale || 3);
    const bw = crop[2] * s, bh = crop[3] * s, bx = (DW - bw) / 2, by = (DH - bh) / 2 + (o.dy || 0);
    const grp = at(p, 0, 0, DW, DH, '', { transformOrigin: '50% 50%' });
    const box = at(grp, bx, by, bw, bh, 'panel', {});
    const img = mk(box, '', { left: -crop[0] * s, top: -crop[1] * s, width: IM[0] * s, height: IM[1] * s }, '', 'img');
    setSrc(img, IMGDIR + name);
    const hls = (o.boxes || []).map(b => ({ el: at(grp, bx + (b.r[0] - crop[0]) * s - 6, by + (b.r[1] - crop[1]) * s - 6, b.r[2] * s + 12, b.r[3] * s + 12, 'hl', { visibility: 'hidden' }), t: b.t, t1: b.t1 ?? 1e9 }));
    const pills = (o.pills || []).map(q => ({ el: at(grp, null, null, null, null, 'zhnote', { left: q.x ?? 40, top: q.y ?? (DH - 130), maxWidth: q.w ?? 1300, visibility: 'hidden' }, q.text + (q.sub ? `<small>${q.sub}</small>` : '')), t: q.t, t1: q.t1 ?? 1e9 }));
    const cr = o.credit ? at(p, null, null, null, null, 'credit', {}, o.credit) : null;
    return lt => {
      const t = lt + sg.s, k = lt / (sg.e - sg.s);
      grp.style.transform = `scale(${1 + (o.zoom ?? 0.03) * k})`;
      hls.forEach(h => { const v = easeOut((t - h.t) / 0.4) * (1 - easeIn((t - h.t1) / 0.3)); h.el.style.visibility = v > 0.002 ? 'visible' : 'hidden'; h.el.style.opacity = v; });
      pills.forEach(q => { const v = easeOut((t - q.t) / 0.4) * (1 - easeIn((t - q.t1) / 0.3)); q.el.style.visibility = v > 0.002 ? 'visible' : 'hidden'; q.el.style.opacity = v; q.el.style.transform = `translateY(${(1 - v) * 12}px)`; });
      if (cr) cr.style.opacity = easeOut(lt / 0.5);
    };
  });
}

// ═════════════════════════════ 缩略图墙：20 张对比图的“✓”那一半排成 5×4，来一张亮一张；pulses = [[规则号, 时刻], …] 放大一下，pills 同 imgStill
function wall(fromScene, toScene, pulses = [], pills = []) {
  const sg0 = segOf(fromScene), sg1 = segOf(toScene);
  ovPage(sg0.s, sg1.e, p => {
    const cols = 5, rows = 4, gap = 14, tw = (DW - 2 * M - (cols - 1) * gap) / cols, th = (DH - 2 * M - (rows - 1) * gap) / rows;
    const tiles = [];
    for (let n = 1; n <= 20; n++) {
      if (!RULES[n]) continue;
      const R = RULES[n], st = R.sets[R.sets.length - 1], rr = st.R, col = (n - 1) % cols, row = Math.floor((n - 1) / cols);
      const el = at(p, M + col * (tw + gap), M + row * (th + gap), tw, th, 'tile', {});
      const sc = Math.max(tw / rr[2], th / rr[3]);
      const img = mk(el, '', { left: -(rr[0] + rr[2] / 2) * sc + tw / 2, top: -(rr[1] + rr[3] / 2) * sc + th / 2, width: R.size[0] * sc, height: R.size[1] * sc }, '', 'img');
      setSrc(img, IMGDIR + R.img);
      mk(el, 'no', {}, String(n).padStart(2, '0')); mk(el, 'nm', {}, R.title);
      tiles.push({ el, n });
    }
    const pl = pills.map(q => ({ el: at(p, null, null, null, null, 'zhnote', { left: q.x ?? 40, top: q.y ?? (DH - 120), maxWidth: q.w ?? 1300, visibility: 'hidden', zIndex: 8 }, q.text + (q.sub ? `<small>${q.sub}</small>` : '')), t: q.t, t1: q.t1 ?? 1e9 }));
    return lt => {
      const t = lt + sg0.s;
      tiles.forEach((tl, i) => {
        const a = easeOut((lt - 0.15 - i * 0.06) / 0.35);
        let sc = 1, glow = 0;
        for (const [n, tp] of pulses) if (n === tl.n) { const d = t - tp; if (d > -0.05 && d < 2.4) glow = Math.max(glow, easeOut(d / 0.3) * (1 - easeIn((d - 1.8) / 0.6))); }
        sc = 1 + 0.08 * glow;
        tl.el.style.opacity = a; tl.el.style.transform = `translateY(${(1 - a) * 18}px) scale(${sc})`; tl.el.style.zIndex = glow > 0.01 ? 3 : 1;
        tl.el.style.boxShadow = glow > 0.01 ? `0 0 0 ${6 * glow}px rgba(255,79,26,${0.9 * glow}), 0 12px 28px rgba(15,23,42,.35)` : '';
      });
      pl.forEach(q => { const v = easeOut((t - q.t) / 0.4) * (1 - easeIn((t - q.t1) / 0.3)); q.el.style.visibility = v > 0.002 ? 'visible' : 'hidden'; q.el.style.opacity = v; q.el.style.transform = `translateY(${(1 - v) * 12}px)`; });
    };
  });
}

// ═════════════════════════════ 规则段：把对比图里的 ✕ / ✓ 两个面板分别裁出来，三种视图：
//   both = 两个面板叠放（宽横幅）或并排（接近方形的），右侧 / 下方是说明栏；
//   L / R = 讲到哪边就把那个面板放大到铺满演示区（说明条在下方），从 both 里的位置“推”过去，讲完缩回；放大不到 1.25 倍的图不做这个视图，改成另一边变暗。
// 数据在 rules.js（build_rules.py 合并：面板和高亮框坐标 = 标注子代理量的；steps = 每一步从哪句（或哪个词）开始讲、焦点在哪边、亮哪几个高亮框）。
function planLayout(L, R) {
  const mw = Math.max(L[2], R[2]), mh = Math.max(L[3], R[3]), UW = DW - 2 * M, UH = DH - 2 * M;
  const labW = 340, gx = 28, gy = 22, sA = Math.min((UW - labW - gx) / mw, (UH - gy) / (L[3] + R[3]));    // A：上下叠放 + 右侧说明栏（高度按两个面板之和算）
  const labH = 150, gB = 30, sB = Math.min((UW - gB) / (L[2] + R[2]), (UH - labH) / mh);                  // B：左右并排 + 下方说明（宽度按两个面板之和算）
  if (sA >= sB * 0.95) {
    const s = Math.min(sA, 1.7), wL = L[2] * s, hL = L[3] * s, wR = R[2] * s, hR = R[3] * s;
    const colW = Math.max(wL, wR), y0 = M + (UH - (hL + gy + hR)) / 2, lx = M + colW + gx, lw = DW - M - lx;
    return { mode: 'A', s, pL: [M, y0, wL, hL], pR: [M, y0 + hL + gy, wR, hR], lL: [lx, y0, lw, hL], lR: [lx, y0 + hL + gy, lw, hR] };
  }
  const s = Math.min(sB, 1.7), wL = L[2] * s, hL = L[3] * s, wR = R[2] * s, hR = R[3] * s;
  const x0 = M + (UW - (wL + gB + wR)) / 2, y0 = M + (UH - labH - Math.max(hL, hR)) / 2;
  return { mode: 'B', s, pL: [x0, y0, wL, hL], pR: [x0 + wL + gB, y0, wR, hR], lL: [x0, y0 + hL + 14, wL, labH - 14], lR: [x0 + wL + gB, y0 + hR + 14, wR, labH - 14] };
}
function planFocus(rect) {                                    // 放大视图：面板铺满演示区（下方留一条说明）
  const UW = DW - 2 * M, UH = DH - 2 * M, labH = 100, s = Math.min(UW / rect[2], (UH - labH) / rect[3], 2.2), w = rect[2] * s, h = rect[3] * s;
  const x = M + (UW - w) / 2, y = M + (UH - labH - h) / 2;
  return { s, pos: [x, y, w, h], lab: [x, y + h + 12, Math.max(w, 560), labH - 12] };
}
const ICON = {
  bad: '<svg viewBox="0 0 24 24" width="34" height="34" style="margin:13px"><path d="M6 6l12 12M18 6L6 18" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/></svg>',
  good: '<svg viewBox="0 0 24 24" width="34" height="34" style="margin:13px"><path d="M4.5 12.8l4.8 4.8L19.5 7" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  q: '?',
};
function mkPanel(parent, name, size, rect, box, s) {
  const el = at(parent, box[0], box[1], box[2], box[3], 'panel', {});
  const img = mk(el, '', { left: -rect[0] * s, top: -rect[1] * s, width: size[0] * s, height: size[1] * s }, '', 'img');
  setSrc(img, IMGDIR + name);
  return el;
}
function mkLab(parent, tag, cap, box, side) {
  const kind = tag[0], icon = kind === 'neutral' ? (side === 'L' ? 'A' : 'B') : ICON[kind];
  return at(parent, box[0], box[1], box[2], box[3], 'lab ' + kind, {}, `<div class="ic">${icon}</div><div class="tx"><b>${tag[1]}</b><span>${cap}</span></div>`);
}
function mkHlSet(parent, items, s) {                          // items: [{k, h, P0, B}]（P0 = 面板在整张图里的位置，B = 面板在这个视图里的位置）→ {k: {box, tag}}
  // 标签优先放在框的右边（文字行的右边通常是空的），不行再试上 / 下 / 左；避开别的高亮框和已经放好的标签；都放不下就放框上方、撞了往上错开
  const pad = 7, TH = 40, rects = items.map(({ h, P0, B }) => ({ x: B[0] + (h.r[0] - P0[0]) * s - pad, y: B[1] + (h.r[1] - P0[1]) * s - pad, w: h.r[2] * s + 2 * pad, h: h.r[3] * s + 2 * pad }));
  const placed = [], out = {};
  items.forEach(({ k, h, B }, i) => {
    const r = rects[i], cls = ['fix', 'neutral', 'warn'].includes(h.role) ? h.role : 'problem';
    const box = at(parent, r.x, r.y, r.w, r.h, 'hl2 ' + cls, { visibility: 'hidden' });
    let tag = null;
    if (h.zh) {
      const tw = h.zh.length * 25 + 30, others = rects.filter((_, j) => j !== i);
      const cand = [[r.x + r.w + 10, r.y + (r.h - TH) / 2], [r.x, r.y - TH - 2], [r.x, r.y + r.h + 6], [r.x - tw - 10, r.y + (r.h - TH) / 2]];
      let pos = cand.find(([tx, ty]) => tx >= B[0] + 2 && ty >= B[1] + 2 && tx + tw <= B[0] + B[2] - 2 && ty + TH <= B[1] + B[3] - 2
        && !others.some(o => tx < o.x + o.w + 4 && tx + tw > o.x - 4 && ty < o.y + o.h + 4 && ty + TH > o.y - 4)
        && !placed.some(q => tx < q.x + q.w + 6 && tx + tw > q.x - 6 && Math.abs(ty - q.y) < TH));
      if (!pos) {
        const up = r.y - TH - 2 >= B[1] - 6; let ty = up ? r.y - TH - 2 : r.y + r.h + 6;
        for (let t2 = 0; t2 < 4; t2++) { if (!placed.some(q => r.x < q.x + q.w + 6 && r.x + tw > q.x - 6 && Math.abs(ty - q.y) < TH)) break; ty += up ? -TH : TH; }
        pos = [r.x, Math.max(4, ty)];
      }
      placed.push({ x: pos[0], y: pos[1], w: tw });
      tag = mk(parent, 'hltag ' + cls, { left: pos[0], top: pos[1], visibility: 'hidden' }, h.zh);
    }
    out[k] = { box, tag };
  });
  return out;
}
function buildSet(parent, R, st) {
  const tagOf = side => st['tag' + side] || R['tag' + side], capOf = side => st['cap' + side] || R['cap' + side];
  const lay = planLayout(st.L, st.R), s = lay.s, hl = st.hl || [];
  const rectOf = side => side === 'L' ? st.L : st.R;
  // both 视图
  const vb = at(parent, 0, 0, DW, DH, '', {});
  const both = { el: vb, hl: {}, pL: mkPanel(vb, R.img, R.size, st.L, lay.pL, s), pR: mkPanel(vb, R.img, R.size, st.R, lay.pR, s),
                 lL: mkLab(vb, tagOf('L'), capOf('L'), lay.lL, 'L'), lR: mkLab(vb, tagOf('R'), capOf('R'), lay.lR, 'R') };
  both.hl = mkHlSet(vb, hl.map((h, k) => ({ k, h, P0: rectOf(h.p), B: h.p === 'L' ? lay.pL : lay.pR })), s);
  // 放大视图（放大不到 1.25 倍的图不做）
  const fL = planFocus(st.L), fR = planFocus(st.R), useFocus = Math.min(fL.s / s, fR.s / s) >= 1.25;
  const views = { both };
  if (useFocus) {
    for (const side of ['L', 'R']) {
      const F = side === 'L' ? fL : fR, Bp = side === 'L' ? lay.pL : lay.pR, el = at(parent, 0, 0, DW, DH, '', { opacity: 0, visibility: 'hidden', transformOrigin: `${F.pos[0]}px ${F.pos[1]}px` });
      const v = { el, F, Bp, side, lab: mkLab(el, tagOf(side), capOf(side), F.lab, side) };
      mkPanel(el, R.img, R.size, rectOf(side), F.pos, F.s);
      v.hl = mkHlSet(el, hl.map((h, k) => ({ k, h, P0: rectOf(side), B: F.pos })).filter(x => x.h.p === side), F.s);
      views[side] = v;
    }
  }
  return { views, useFocus, lay };
}
function ruleShot(n) {
  const R = RULES[n], sg = TL.segs.find(g => g.rule === n);
  if (!sg) throw new Error('没有规则 ' + n + ' 的场景');
  ovPage(sg.s, sg.e, p => {
    const grp = at(p, 0, 0, DW, DH, '', { transformOrigin: '50% 50%' });
    const sets = R.sets.map(st => buildSet(grp, R, st));
    let curSet = 0;
    const steps = R.steps.map(s => { if (s.set != null) curSet = s.set; return { t: s.phrase ? P(s.at, s.phrase, -0.25) : S(s.at) + (s.off ?? -0.2), focus: s.focus || 'both', hl: s.hl || [], set: curSet }; }).sort((a, b) => a.t - b.t);
    // 每个高亮框的显示区间：同一套面板里连续几步都亮它就合成一段
    const ivs = sets.map((g, si) => R.sets[si].hl.map((_, k) => {
      const iv = []; let open = null;
      steps.forEach(s => {
        const has = s.set === si && s.hl.includes(k);
        if (has && !open) open = [s.t, 1e9];
        else if (!has && open) { open[1] = s.t; iv.push(open); open = null; }
      });
      if (open) iv.push(open);
      return iv;
    }));
    const lv = f => f === 'L' ? [1, 0.34] : f === 'R' ? [0.34, 1] : [1, 1];
    const setHl = (h, v) => { if (!h) return; [h.box, h.tag].forEach(e => { if (e) { e.style.visibility = v > 0.002 ? 'visible' : 'hidden'; e.style.opacity = v; } }); };
    return lt => {
      const t = lt + sg.s;
      let idx = -1; for (let j = 0; j < steps.length; j++) if (t >= steps[j].t) idx = j;
      const cur = steps[Math.max(idx, 0)], prv = idx > 0 ? steps[idx - 1] : cur;
      const kk = idx < 1 ? 1 : easeIO((t - cur.t) / 0.45);
      grp.style.transform = `scale(${1 + 0.02 * clamp(lt / (sg.e - sg.s))})`;
      sets.forEach((g, si) => {
        let alpha;
        if (idx < 1 || cur.set === prv.set) alpha = cur.set === si ? 1 : 0;
        else alpha = si === cur.set ? easeOut((t - cur.t) / 0.35) : si === prv.set ? 1 - easeOut((t - cur.t) / 0.35) : 0;
        const { both, L, R: VR } = g.views;
        const zL = L ? lerp(prv.focus === 'L' ? 1 : 0, cur.focus === 'L' ? 1 : 0, kk) : 0, zR = VR ? lerp(prv.focus === 'R' ? 1 : 0, cur.focus === 'R' ? 1 : 0, kk) : 0;
        // both 视图：入场动画（只给第一套）+ 放大时淡出 / 没有放大视图时另一边变暗
        const first = si === 0, eL = easeOut((lt - 0.05) / 0.4), eR = easeOut((lt - 0.30) / 0.4), lbL = easeOut((lt - 0.30) / 0.4), lbR = easeOut((lt - 0.55) / 0.4);
        const [dimL, dimR] = g.useFocus ? [1, 1] : (() => { const a = lv(prv.focus), b = lv(cur.focus); return [lerp(a[0], b[0], kk), lerp(a[1], b[1], kk)]; })();
        const ob = alpha * (1 - Math.max(zL, zR));
        both.el.style.opacity = ob; both.el.style.visibility = ob < 0.002 ? 'hidden' : 'visible';
        both.pL.style.opacity = dimL * (first ? eL : 1); both.pR.style.opacity = dimR * (first ? eR : 1);
        both.pL.style.transform = first ? `translateY(${(1 - eL) * 22}px)` : ''; both.pR.style.transform = first ? `translateY(${(1 - eR) * 22}px)` : '';
        both.lL.style.opacity = dimL * (first ? lbL : 1); both.lR.style.opacity = dimR * (first ? lbR : 1);
        // 放大视图：从 both 里的位置推到铺满，zoom = 0..1
        [[L, zL], [VR, zR]].forEach(([v, z]) => {
          if (!v) return;
          const k = lerp(v.Bp[2] / v.F.pos[2], 1, z), dx = (v.Bp[0] - v.F.pos[0]) * (1 - z), dy = (v.Bp[1] - v.F.pos[1]) * (1 - z);
          v.el.style.opacity = alpha * z; v.el.style.visibility = alpha * z < 0.002 ? 'hidden' : 'visible';
          v.el.style.transform = `translate(${dx}px, ${dy}px) scale(${k})`;
          v.lab.style.opacity = clamp((z - 0.55) / 0.45);
        });
        // 高亮框
        R.sets[si].hl.forEach((_, k) => {
          let v = 0;
          for (const [a0, a1] of ivs[si][k]) v = Math.max(v, easeOut((t - a0 - 0.12) / 0.3) * (1 - easeIn((t - a1) / 0.22)));
          setHl(both.hl[k], v); if (L) setHl(L.hl[k], v); if (VR) setHl(VR.hl[k], v);
        });
      });
    };
  });
}

// ═════════════════════════════ 本期的叠加层（时间都按字幕条算）
// ── 开场
pageShot('A01', 'A02', 'X_t1', [
  ['默认 UI 丑陋依旧是硬伤', P('A01', '界面', -0.1)],
  ['2026年10月3日', S('A02') + 0.2],
  ['龙海', P('A02', '龙海', -0.1)],
], { start: 0 });
imgStill('O2', '图00_封面.jpg', { credit: '文章封面 · 龙海 @longhaiqwe123', boxes: [{ r: [232, 446, 1274, 80], t: S('A04') - 0.1 }] });
pageShot('A05', 'A07', 'Y_hero', [
  ['@rect:1000,170,430,610', S('A05') + 0.3, '书名：Refactoring UI'],
  ['@rect:1055,610,285,90', S('A06') + 0.2, '作者：Adam Wathan · Steve Schoger'],
  ['creators of', S('A07') + 0.2, '官网：Tailwind CSS 的作者出品'],
  ['tailwind css', S('A07') + 0.2],
], { start: 0 });
pageShot('A08', 'A08', 'Y_book', [
  ['50 incredibly visual chapters', S('A08') + 0.2, '50 章，配大量图示'],
  ['200+ painstakingly typeset pages', P('A08', '218', -0.1), '200 多页的精排 PDF（官网另标：218 页）'],
]);
imgStill('O5', '图13_颜色比想象多.jpg', {
  crop: RULES[13].sets[1].L, credit: '图：《Refactoring UI》', maxScale: 1.9, dy: -20,
  pills: [{ t: S('A10'), text: '丑界面长这样', sub: '《Refactoring UI》里的反面例子', x: 40, y: DH - 128 }],
});
pageShot('A13', 'A15', 'Y_tactics', [
  ['Design with tactics, not talent.', S('A14') + 0.1, '用方法，不靠天赋'],
], { start: 20 });

// ── 二十条规则
for (let n = 1; n <= 20; n++) if (RULES[n]) ruleShot(n);

// ── 结尾
wall('C1', 'C2', [[2, P('Z02', '先灰度')], [9, P('Z03', '间距')], [12, P('Z03', '基线')]], [
  { t: S('Z05'), t1: E('Z05') + 0.4, text: '追问：字重多少？组间距是组内的几倍？' },
  { t: S('Z06'), t1: E('Z06') + 0.8, text: '练习：不看源码，一比一复刻' },
]);
tocShot('Z07', 'Z08', 'Y_toc', { scale: 0.8, a: 0.4, b: 0.9 });
pageShot('Z09', 'Z09', 'M_skill', [
  ['把一本书做成随叫随到的 Skill', S('Z09') + 0.5],
  ['做成了一个 Skill', P('Z09', 'Skill', -0.2)],
]);
imgStill('C5', '图00_封面.jpg', { credit: '原文：龙海 @longhaiqwe123 · X　图：Refactoring UI', zoom: 0.02 });
