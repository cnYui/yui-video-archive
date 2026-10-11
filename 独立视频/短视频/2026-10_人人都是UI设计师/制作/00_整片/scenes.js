// 工具 + 叠加层（短视频竖屏版）。素材框里的坐标仍是 1474×829（显示时缩到 0.57，dual 的框 860×490）；整页的叠加层用 1080×2340 的坐标。
// 【本条改动，模板原样见 技能 assets/engine-template/scenes.js】《人人都是 UI 设计师》：没有视频素材，画面全是静态图——
//   ① panelShot：对比图的 ✕ 面板放进上框、✓ 面板放进下框（面板按 marks / VIEWS 取景，contain 进框，框底色 = 面板边缘色），叠高亮框 + 小标签，
//      讲到哪一边另一边蒙一层米白（focus），缓慢推近；数据在 panels.js（build_panels.py 生成）；
//   ② pageShot 合并了长视频的改动（深色页面画橙框、@rect: 手动框选）并加了 opt.fit（整张页面缩进框里，不滚动）；
//   ③ wallShot：20 条 ✓ 面板铺成 5×4 缩略图墙（下框），本期讲的几条亮起来。
// 每个叠加层 [t0, t1] 显示（前后淡入淡出），t 用成片秒数；时间都按字幕条算：S('N07') = 这条开始说的时刻，P('N09', '词') = 说到这个词的时刻。
// 字幕条：N01… = 画外音（Fish 网页版「温柔男生」S2 Pro）；字幕是竖屏版中英双语，见 engine.js / build_timeline.py。
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
  if (k < 0) throw new Error(`「${phrase}」不在 ${id}：${q.zh}`);
  return q.s + (q.e - q.s) * (k / q.zh.length) + off;
}
// 素材 key 的第 ts 秒在成片里是第几秒（变速段按 speed 换算；同一个素材的各段互不重叠；只查上框 ranges）——本条没有视频素材，用不到
function V(key, ts) {
  for (const c of Object.values(TL.clips)) for (const r of c.ranges) if (r.src === key && ts >= r.in - 1e-6 && ts <= r.out + 1e-6) return r.s + (ts - r.in) / (r.speed || 1);
  throw new Error(`素材 ${key} 的 ${ts} s 没有放进成片`);
}
const segOf = id => { const g = TL.segs.find(x => x.id === id); if (!g) throw new Error('没有场景 ' + id); return g; };

const OV = [];   // {t0, t1, build(root) → update(lt), fast?:true（官方页面镜头之间快切）, layer?:'page'（整页坐标）}
const ovB = (t0, t1, build) => OV.push({ t0, t1, build });
const ovPage = (t0, t1, build) => OV.push({ t0, t1, build, fast: true });
const ovPageB2 = (t0, t1, build) => OV.push({ t0, t1, build, fast: true, layer: 'b2' });   // 页面录屏放在 dual 的下框（pageShot 的 {lower: true}）
const ovP = (t0, t1, build) => OV.push({ t0, t1, build, layer: 'page' });
const ovB2 = (t0, t1, build) => OV.push({ t0, t1, build, layer: 'b2' });     // 双分镜的下框
const ovBF = ovPage, ovB2F = ovPageB2;                                         // 本条的面板 / 墙：和页面镜头一样快切（0.1 s 淡入淡出），别让上一场的面板和下一场的叠在一起 0.3 s
const DW = 1474, DH = 829;                                                     // 素材框里的原生坐标
const RL = window.RULES || {};

// ═════════════════════════════ 页面截图（推文 / 官网）
// pageShot(从哪句, 到哪句, 页面图名字, [[要高亮的句子, 刷上的时刻, 底部中文译文?], …], {start: 起始滚动位置（图片像素）, pad, lower: true = 放在 dual 的下框, t0 / t1: 自定义起止时刻（成片秒）, fit: true = 整张页面缩进框里、不滚动})
// 图是 capture_pages.py 截的（本条用的是长视频截好的），默认铺满框的宽度，每条高亮出现前 0.95 s 开始往它那里滚；fit 时页面整张缩进框里（居中，两边填页面底色），不滚动。
// 深色页面（书官网首屏）里荧光笔看不见，改成橙色边框；@rect: 开头的是手动框选（也画边框）。
const PAGE_BAR = 46;
function pageShot(from, to, key, marks, opt = {}) {
  const m = PG[key]; if (!m) throw new Error('没有页面图 ' + key);
  const sg0 = TL.segs.find(g => g.s <= S(from) + 1e-6 && S(from) < g.e), sg1 = TL.segs.find(g => g.s <= E(to) + 1e-6 && E(to) < g.e + 1e-6);
  let t0 = sg0 ? Math.min(S(from) - 0.2, sg0.s) : S(from) - 0.2, t1 = Math.max(E(to) + 0.12, sg1 ? sg1.e - 0.02 : 0) + (opt.pad || 0);
  if (opt.t0 != null) t0 = opt.t0;
  if (opt.t1 != null) t1 = opt.t1;
  const dark = (() => { const c = parseInt(m.bg.slice(1), 16); return ((c >> 16) * .3 + ((c >> 8) & 255) * .59 + (c & 255) * .11) < 90; })();
  (opt.lower ? ovPageB2 : ovPage)(t0, t1, p => {
    const VW = DW, VH = DH - PAGE_BAR, k = opt.fit ? Math.min(VW / m.w, VH / m.h) : VW / m.w, IW = m.w * k, IH = m.h * k, PADB = opt.fit ? 0 : 200;
    const ZB = TL.layout === 'dual' ? [124, 56, 30] : [100, 40, 36];     // 底部中文译文条：[高, 字号, 左右内边距]；dual 的框缩到 0.57，字要大一档才读得清
    const win = at(p, 0, 0, VW, DH, '', { background: m.bg, overflow: 'hidden' });
    const view = mk(win, '', { position: 'absolute', left: 0, top: PAGE_BAR, width: VW, height: VH, overflow: 'hidden', background: m.bg });
    const sheet = mk(view, '', { position: 'absolute', left: (VW - IW) / 2, top: opt.fit ? (VH - IH) / 2 : 0, width: IW, height: IH + PADB, willChange: 'transform' });
    const img = mk(sheet, '', { position: 'absolute', left: 0, top: 0, width: IW, height: IH, display: 'block' }, '', 'img');
    setSrc(img, 'media/' + m.src);
    const url = m.url.replace(/^https?:\/\//, '').replace(/\/$/, '');
    mk(win, '', { position: 'absolute', left: 0, top: 0, width: VW, height: PAGE_BAR, background: '#E9EBEF', borderBottom: '1px solid #CFD3DA', display: 'flex', alignItems: 'center', gap: '10px', padding: '0 18px', zIndex: 3 },
      '<i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FF5F57"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FEBC2E"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#28C840"></i>' +
      `<span style="margin-left:12px;flex:1;height:30px;line-height:30px;border-radius:15px;background:#fff;padding:0 18px;font:600 19px 'JetBrains Mono';color:#4B5563;white-space:nowrap;overflow:hidden">${url}</span>`);
    const zhBar = mk(win, '', { position: 'absolute', left: 0, right: 0, bottom: 0, height: ZB[0], background: 'rgba(27,27,31,.93)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: `800 ${ZB[1]}px 'Noto Sans SC'`, padding: `0 ${ZB[2]}px`, zIndex: 4, opacity: 0, whiteSpace: 'nowrap' });
    const hs = marks.map(([needle, tm, zh]) => {
      const rects = m.marks[needle];
      if (!rects) throw new Error(`页面图 ${key} 里没有高亮句子「${needle}」`);
      const frame = needle.startsWith('#sel:') || needle.startsWith('@rect:') || dark;     // 图表 / 手动框选 / 深色页面：画橙色边框，不填色（填色会盖住图）
      const els = rects.map(([x, y, w, h]) => mk(sheet, '', frame
        ? { position: 'absolute', left: x * k - 6, top: y * k - 6, width: w * k + 12, height: h * k + 12, border: '6px solid #FF4F1A', borderRadius: '12px', boxShadow: '0 0 0 8px rgba(255,79,26,.16)', transformOrigin: '0 50%', visibility: 'hidden' }
        : { position: 'absolute', left: x * k - 5, top: y * k - 3, width: w * k + 10, height: h * k + 6, background: 'rgba(255,205,40,.64)', mixBlendMode: 'multiply', borderRadius: '5px', transformOrigin: '0 50%', visibility: 'hidden' }));
      return { els, t: tm - t0, cy: (rects[0][1] + rects[0][3] / 2) * k, top: rects[0][1] * k, tall: rects[0][3] * k > VH * 0.55, zh };
    });
    const maxS = opt.fit ? 0 : Math.max(0, IH + PADB - VH);
    hs.forEach(h => h.target = clamp(h.tall ? h.top - VH * 0.05 : h.cy - VH * 0.34, 0, maxS));      // 比窗口还高的（图表）顶部对齐
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

// ═════════════════════════════ 对比图面板镜头
// panelShot(场景 id, 规则号, {set: 第几套面板（图 13 有上下两层）, up: {hl: […]}, low: {hl: […]}, focus: [[时刻, 'up' | 'low' | 'both'], …], zoom})
//   上框 = ✕ 面板（L），下框 = ✓ 面板（R）。hl 里每项 {k: marks 里的第几个高亮框（build_panels.py 会打印编号，_check/panels_check.png 里也标了）, t: 出现的时刻（成片秒）, t1?: 消失的时刻,
//   label?: 标签文字（≤ 8 个字，数字最好有）, pos?: 标签位置（'tl' 框上方靠左 / 'tr' / 'bl' 框下方 / 'br' / 'r' 框右边 / 'l' / 'in' 框内偏左（dx 调缩进）/ 数组 = 按顺序试）, role?: 换色（'problem' 红 / 'fix' 绿 / 'q' 蓝）}。
//   focus：讲到哪边，另一边蒙一层米白（0.35 s 渐变）；整个面板另外缓慢推近 3%。
const TAG_FONT = "800 46px 'Noto Sans SC'", TAG_H = 70, TAG_PX = 18;
const _cv = document.createElement('canvas').getContext('2d');
function textW(text, font) { _cv.font = font; return _cv.measureText(text).width; }
function placeTags(boxes, tags, maxR = 6) {          // boxes: 所有高亮框 [{x, y, w, h}]；tags: [{i, w, pos, dx}] → {i: [x, y]}：先试偏好的位置，要求在框内（右边留 maxR）、不压别的高亮框和已放的标签
  const out = {}, placed = [], G = 10, B = 6;
  const hit = (a, b, m) => a.x < b.x + b.w + m && a.x + a.w > b.x - m && a.y < b.y + b.h + m && a.y + a.h > b.y - m;
  for (const tg of tags) {
    const bx = boxes[tg.i], lw = tg.w, lh = TAG_H;
    const cand = {
      tl: [bx.x, bx.y - lh - G], tr: [bx.x + bx.w - lw, bx.y - lh - G], bl: [bx.x, bx.y + bx.h + G], br: [bx.x + bx.w - lw, bx.y + bx.h + G],
      r: [bx.x + bx.w + G, bx.y + (bx.h - lh) / 2], l: [bx.x - lw - G, bx.y + (bx.h - lh) / 2], in: [bx.x + (tg.dx ?? 16), bx.y + (bx.h - lh) / 2],
    };
    const order = [].concat(tg.pos || [], ['tl', 'bl', 'tr', 'br', 'r', 'l']);
    const fits = ([x, y]) => x >= B && y >= B && x + lw <= DW - maxR && y + lh <= DH - B;
    const free = ([x, y]) => { const r = { x, y, w: lw, h: lh }; return !boxes.some((o, j) => j !== tg.i && hit(r, o, 4)) && !placed.some(q => hit(r, q, 6)); };   // 不压别的高亮框（自己的框不管：'in' 本来就在框里）和已经放好的标签
    let pos = null;
    for (const name of order) { const c = cand[name]; if (c && fits(c) && free(c)) { pos = c; break; } }
    if (!pos) for (const name of order) { const c = cand[name]; if (c && fits(c)) { pos = c; break; } }
    if (!pos) { const c = cand[order[0]]; pos = [clamp(c[0], B, DW - maxR - lw), clamp(c[1], B, DH - B - lh)]; }
    placed.push({ x: pos[0], y: pos[1], w: lw, h: lh });
    out[tg.i] = pos;
  }
  return out;
}
function buildPanel(root, R, st, side, o, t0, t1, focus) {
  const rect = side === 'L' ? st.L : st.R, bg = side === 'L' ? st.bgL : st.bgR, mine = side === 'L' ? 'up' : 'low';
  const k = Math.min(DW / rect[2], DH / rect[3]), pw = rect[2] * k, ph = rect[3] * k, ox = (DW - pw) / 2, oy = (DH - ph) / 2;
  const grp = at(root, 0, 0, DW, DH, '', { background: bg, transformOrigin: '50% 50%' });
  const pn = at(grp, ox, oy, pw, ph, 'pn', {});
  const img = mk(pn, 'pimg', { left: -rect[0] * k, top: -rect[1] * k, width: R.size[0] * k, height: R.size[1] * k }, '', 'img');
  setSrc(img, R.url);
  const veil = at(root, 0, 0, DW, DH, 'veil', { opacity: 0 });
  const PD = 7;
  const items = (o.hl || []).map(h => {
    const m = st.hl[h.k]; if (!m) throw new Error(`规则 ${R.n} 的这套面板没有第 ${h.k} 个高亮框`);
    if (m.p !== side) throw new Error(`规则 ${R.n} 的高亮框 ${h.k} 在 ${m.p} 面板，放错框了（上框 = L，下框 = R）`);
    return Object.assign({ role: m.role }, h, { x: ox + (m.r[0] - rect[0]) * k - PD, y: oy + (m.r[1] - rect[1]) * k - PD, w: m.r[2] * k + 2 * PD, h: m.r[3] * k + 2 * PD });
  });
  const tags = items.map((h, i) => h.label ? { i, w: textW(h.label, TAG_FONT) + 2 * TAG_PX, pos: h.pos, dx: h.dx } : null).filter(Boolean);
  const where = placeTags(items, tags, side === 'R' ? 50 : 6);      // 下框（R）右边留 50（≈ 29 px）：抖音的点赞 / 评论按钮在 x ≥ 940、y 1170 起，会盖住下框最右边约 40 个框内坐标
  items.forEach((h, i) => {
    h.box = at(grp, h.x, h.y, h.w, h.h, 'pbox ' + h.role, { visibility: 'hidden' });
    const tg = tags.find(q => q.i === i);
    if (tg) { h.tag = at(grp, where[i][0], where[i][1], tg.w, TAG_H, 'ptag ' + h.role, { visibility: 'hidden' }); h.tag.textContent = h.label; }
  });
  const dur = t1 - t0;
  return lt => {
    const T = lt + t0;
    let cur = 'both', prev = 'both', tc = -1e9;
    for (const [tt, f] of focus) if (T >= tt) { prev = cur; cur = f; tc = tt; }
    const vt = f => (f === 'both' || f === mine) ? 0 : 1;
    veil.style.opacity = lerp(vt(prev), vt(cur), easeIO((T - tc) / 0.35));
    items.forEach(h => {
      const v = easeOut((T - h.t) / 0.28) * (h.t1 != null ? 1 - easeIn((T - h.t1) / 0.25) : 1), vis = v > 0.002 ? 'visible' : 'hidden';
      h.box.style.visibility = vis; h.box.style.opacity = v; h.box.style.transform = `scale(${1 + 0.05 * (1 - v)})`;
      if (h.tag) { h.tag.style.visibility = vis; h.tag.style.opacity = v; h.tag.style.transform = `translateY(${(1 - v) * 10}px)`; }
    });
    grp.style.transform = `scale(${1 + (o.zoom ?? 0.03) * clamp(lt / dur)})`;
  };
}
function panelShot(sceneId, n, spec = {}) {
  const R = RL[n]; if (!R) throw new Error('没有规则 ' + n);
  const st = R.sets[spec.set || 0], sg = segOf(sceneId);
  const t0 = sg === TL.segs[0] ? -0.5 : sg.s, t1 = sg === TL.segs[TL.segs.length - 1] ? TL.total + 0.5 : sg.e;       // 第一个场景从 −0.5 s 起（第 0 帧就要有画面），最后一个盖到片尾
  const focus = (spec.focus || []).slice().sort((a, b) => a[0] - b[0]);
  ovBF(t0, t1, p => buildPanel(p, R, st, 'L', spec.up || {}, t0, t1, focus));
  ovB2F(t0, t1, p => buildPanel(p, R, st, 'R', spec.low || {}, t0, t1, focus));
}

// ═════════════════════════════ 缩略图墙（下框）：20 条规则的 ✓ 面板铺成 5×4，来一张亮一张；used = 本期讲的规则号，usedT 起亮（橙色描边），capT 起出底部说明条
function wallShot(sceneId, used, o = {}) {
  const sg = segOf(sceneId), t0 = sg.s, t1 = sg === TL.segs[TL.segs.length - 1] ? TL.total + 0.5 : sg.e;
  ovB2F(t0, t1, p => {
    const cols = 5, rows = 4, gap = 12, M = 14, CAP = 96, tw = (DW - 2 * M - (cols - 1) * gap) / cols, th = (DH - 2 * M - CAP - (rows - 1) * gap) / rows;
    const bg = at(p, 0, 0, DW, DH, '', { background: '#EDEFF3' });
    const tiles = [];
    for (let n = 1; n <= 20; n++) {
      const Rn = RL[n]; if (!Rn) continue;
      const st = Rn.sets[Rn.sets.length - 1], rr = st.R, col = (n - 1) % cols, row = Math.floor((n - 1) / cols);
      const el = at(bg, M + col * (tw + gap), M + row * (th + gap), tw, th, 'tile', {});
      const sc = Math.max(tw / rr[2], th / rr[3]);
      const im = mk(el, '', { left: -(rr[0] + rr[2] / 2) * sc + tw / 2, top: -(rr[1] + rr[3] / 2) * sc + th / 2, width: Rn.size[0] * sc, height: Rn.size[1] * sc }, '', 'img');
      setSrc(im, Rn.url);
      mk(el, 'no', {}, String(n).padStart(2, '0'));
      tiles.push({ el, n });
    }
    const cap = at(p, 0, DH - CAP - 0, DW, CAP, 'wallcap', { opacity: 0, bottom: null }, o.cap || '');
    cap.style.top = (DH - CAP) + 'px'; cap.style.height = CAP + 'px';
    return lt => {
      const T = lt + t0;
      tiles.forEach((tl, i) => {
        const a = easeOut((lt - 0.1 - i * 0.045) / 0.3), u = used.includes(tl.n) && T >= (o.usedT ?? 1e9);
        tl.el.style.opacity = a; tl.el.style.transform = `translateY(${(1 - a) * 16}px) scale(${u ? 1 + 0.05 * easeOut((T - o.usedT) / 0.3) : 1})`;
        tl.el.classList.toggle('used', u);
      });
      cap.style.opacity = easeOut((T - (o.capT ?? 1e9)) / 0.3);
    };
  });
}

// ═════════════════════════════ 小工具（模板原有，本条没用到，留着方便以后复制）
const NOTE_Y = 648;
function note(t0, t1, zh, small, o = {}) {                    // 中文译文条（默认左下，不挡正文）；o.lower = true 放到双分镜的下框
  (o.lower ? ovB2 : ovB)(t0, t1, p => {
    const el = at(p, null, null, null, null, 'zhnote', { left: o.x ?? 40, top: o.y ?? NOTE_Y, maxWidth: o.w ?? 1394 }, zh + (small ? `<small>${small}</small>` : ''));
    return lt => show(el, lt, 0, { dy: 10 });
  });
}
function box(t0, t1, x, y, w, h, o = {}) {                    // 橙色高亮框；o.lower = true 放到双分镜的下框
  (o.lower ? ovB2 : ovB)(t0, t1, p => { const el = at(p, x, y, w, h, 'hl', {}); return lt => show(el, lt, 0.05, { dy: 0, scale: 1.02 }); });
}

// ═════════════════════════════ 本条：5 条设计规则
// 画面：上框 = ✕（错的做法）、下框 = ✓（对的做法）；台词里的“上面 / 下面”就是这两个框。
// 钩子和收尾用同一对画面（图 13 下层：5 个色码硬套出来的界面 / 按色阶取色的同一个界面），首尾呼应。
const mid = (a, b) => (E(a) + S(b)) / 2;

// H0 钩子（N01）
panelShot('H0', 13, {
  set: 1,
  up: { hl: [{ k: 0, t: P('N01', '五个颜色', 0.1) }] },
  low: { hl: [{ k: 3, t: P('N01', '什么像样', 0.0) }] },
});

// B1 背书（N02–N04）：上框推文，下框书官网
pageShot('N02', 'N04', 'X_t1', [
  ['2026年10月3日', P('N02', '10 月 3', 0.0)],
  ['龙海', P('N02', '龙海', -0.1)],
  ['@rect:《Refactoring UI》', P('N03', 'Refactoring', -0.2)],
  ['20 条设计军规', P('N03', '二十条', 0.3)],
], { fit: true });
pageShot('N02', 'N04', 'Y_hero', [
  ['@rect:1000,170,430,610', P('N03', 'Refactoring', -0.1)],
], { fit: true, lower: true });

// S06 按钮分主次（N05–N07）
panelShot('S06', 6, {
  focus: [[S('N05') - 0.1, 'up'], [S('N06') - 0.1, 'low']],
  up: { hl: [{ k: 0, t: P('N05', '红蓝绿', 0.0) }, { k: 1, t: P('N05', '红蓝绿', 0.25) }, { k: 2, t: P('N05', '红蓝绿', 0.5), label: '三个都是实心', pos: 'tr' }] },
  low: { hl: [{ k: 3, t: P('N06', '主操作', -0.2), label: '主操作', pos: 'tl' }, { k: 5, t: P('N07', '删除', 0.0), label: '文字链接', pos: 'bl' }] },
});

// S09 间距有亲疏（N08–N09）
panelShot('S09', 9, {
  focus: [[S('N08') - 0.1, 'up'], [S('N09') - 0.1, 'low']],
  up: { hl: [{ k: 0, t: P('N08', '标签', 0.2), label: '上 20 · 下 20 px', pos: 'r' }] },
  low: { hl: [{ k: 1, t: P('N09', '改成', 0.1), label: '上 20 · 下 10 px', pos: 'r' }] },
});

// S13 颜色比想象的多（N10–N11）：上层 = 在线调色板的 5 个色块 / 完整色阶
panelShot('S13', 13, {
  set: 0,
  focus: [[S('N10') - 0.1, 'up'], [S('N11') - 0.1, 'low']],
  up: { hl: [{ k: 0, t: S('N10') + 0.5, label: '只有 5 个色码', pos: 'tl' }] },
  low: { hl: [
    { k: 1, t: P('N11', '主色', -0.1), label: '主色 5–10 档', pos: 'in', dx: 150 },
    { k: 2, t: P('N11', '灰色', -0.1), label: '灰色 8–10 档', pos: 'in', dx: 150 },
    { k: 3, t: P('N11', '强调色', -0.1), label: '强调色各 5–10 档', pos: 'in', dx: 150 },
  ] },
});

// S14 浅底深字（N12–N13）：上框左面板的角标是蓝色“？”（合格，但抢眼），高亮框用蓝色，不是红
panelShot('S14', 14, {
  focus: [[S('N12') - 0.1, 'up'], [S('N13') - 0.1, 'low']],
  up: { hl: [{ k: 0, t: S('N12') + 0.3, role: 'q', label: '深底白字', pos: 'tr' }, { k: 1, t: P('N12', '对比度', -0.1), role: 'q', label: '对比度 5.07–5.97', pos: 'bl' }] },
  low: { hl: [{ k: 2, t: S('N13') + 0.3, label: '浅底深字', pos: 'tr' }, { k: 3, t: P('N13', '对比度', -0.1), label: '对比度 9.01–12.32', pos: 'bl' }] },
});

// S17 图上文字（N14–N15）
panelShot('S17', 17, {
  focus: [[S('N14') - 0.1, 'up'], [S('N15') - 0.1, 'low']],
  up: { hl: [{ k: 0, t: P('N14', '白字', 0.0), label: '字被照片吃掉', pos: 'tl' }] },
  low: { hl: [{ k: 3, t: P('N15', '垫', -0.1), label: '半透明黑蒙版', pos: 'tl' }, { k: 4, t: P('N15', '不透明度', -0.1), label: '0.55', pos: 'tl' }] },
});

// C1 泼冷水（N16–N18）：上框官网“The Book”一节（50 章），下框 20 条的缩略图墙，本期讲的 5 条亮起来
pageShot('N16', 'N18', 'Y_book', [
  ['50 incredibly visual chapters', P('N16', '五十章', -0.2)],
], { start: 0 });
wallShot('C1', [6, 9, 13, 14, 17], { usedT: S('N16') + 0.6, capT: P('N16', '一半', -0.3), cap: '亮的是这期讲的 <b>5</b> 条' });

// E1 金句（N19）：和钩子同一对画面
panelShot('E1', 13, {
  set: 1,
  up: { hl: [] },
  low: { hl: [{ k: 3, t: P('N19', '审美', -0.1) }] },
});
