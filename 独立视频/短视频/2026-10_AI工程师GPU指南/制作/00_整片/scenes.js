// 工具 + 叠加层（短视频竖屏版）。素材框里的坐标仍是 1474×829（显示时缩到 0.66）；整页的叠加层（big()）用 1080×2340 的坐标。
// 素材为主：演示视频 / 新闻画面 + 官方页面 / 推文 / 论文录屏（pageShot），上面只加少量标注；不放静态文字卡片。
// 每个叠加层 [t0, t1] 显示（前后淡入淡出），t 用成片秒数；时间都按字幕条算：S('N07') = 这条开始说的时刻，P('N09', '词') = 说到这个词的时刻；
// V('d1', 14.0) = 官方演示视频（素材 d1）第 14.0 秒在成片里的时刻（用来把标注钉在演示的某一刻上）。
// 字幕条：N01… = 画外音（Fish 网页版「赛马娘（曼波欧耶版）」S2 Pro）；字幕是竖屏版中英双语，见 engine.js / build_timeline.py。
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
// 素材 key 的第 ts 秒在成片里是第几秒（变速段按 speed 换算；同一个素材的各段互不重叠；只查上框 ranges）
function V(key, ts) {
  for (const c of Object.values(TL.clips)) for (const r of c.ranges) if (r.src === key && ts >= r.in - 1e-6 && ts <= r.out + 1e-6) return r.s + (ts - r.in) / (r.speed || 1);
  throw new Error(`素材 ${key} 的 ${ts} s 没有放进成片`);
}

const OV = [];   // {t0, t1, build(root) → update(lt), fast?:true（官方页面镜头之间快切）, layer?:'page'（整页坐标）}
const ovB = (t0, t1, build) => OV.push({ t0, t1, build });
const ovPage = (t0, t1, build) => OV.push({ t0, t1, build, fast: true });
const ovPageB2 = (t0, t1, build) => OV.push({ t0, t1, build, fast: true, layer: 'b2' });   // 页面录屏放在 dual 的下框（pageShot 的 {lower: true}）
const ovP = (t0, t1, build) => OV.push({ t0, t1, build, layer: 'page' });
const ovB2 = (t0, t1, build) => OV.push({ t0, t1, build, layer: 'b2' });     // 双分镜的下框

// ═════════════════════════════ 官方页面 / 推文录屏
// pageShot(从哪句, 到哪句, 页面图名字, [[要高亮的句子, 刷上的时刻, 中文译文?], …], {start: 起始滚动位置（图片像素）, pad: 比最后一句再多留的秒数, lower: true = 放在 dual 的下框, t0 / t1: 自定义起止时刻（成片秒）})
// 图是 capture_pages.py 截的（800 CSS 宽 × 2 倍像素 = 1600 宽；推文是它自己的宽度），铺满演示区宽度；每条高亮出现前 0.95 s 开始往它那里滚，滚到画面偏上三分之一的位置。
const PAGE_BAR = 46;
function pageShot(from, to, key, marks, opt = {}) {
  const m = PG[key]; if (!m) throw new Error('没有页面图 ' + key);
  // 页面镜头铺满整个场景（卡片场景的前后各有零点几秒的空档，不铺满会闪一下空白的底）
  const sg0 = TL.segs.find(g => g.s <= S(from) + 1e-6 && S(from) < g.e), sg1 = TL.segs.find(g => g.s <= E(to) + 1e-6 && E(to) < g.e + 1e-6);
  let t0 = sg0 ? Math.min(S(from) - 0.2, sg0.s) : S(from) - 0.2, t1 = Math.max(E(to) + 0.12, sg1 ? sg1.e - 0.02 : 0) + (opt.pad || 0);
  if (opt.t0 != null) t0 = opt.t0;                           // 自定义起止（一个场景里连着放好几个页面时必须写，不然每个页面都铺满整个场景、互相盖住；2026-10 text-to-cad 那条加的）
  if (opt.t1 != null) t1 = opt.t1;
  (opt.lower ? ovPageB2 : ovPage)(t0, t1, p => {
    const VW = 1474, VH = 829 - PAGE_BAR, k = VW / m.w, IH = m.h * k, PADB = 200;
    const ZB = TL.layout === 'dual' ? [124, 56, 30] : [100, 40, 36];     // 底部中文译文条：[高, 字号, 左右内边距]；dual 的框缩到 0.57，字要大一档才读得清
    const win = at(p, 0, 0, VW, 829, '', { background: m.bg, overflow: 'hidden' });
    const view = mk(win, '', { position: 'absolute', left: 0, top: PAGE_BAR, width: VW, height: VH, overflow: 'hidden', background: m.bg });
    const sheet = mk(view, '', { position: 'absolute', left: 0, top: 0, width: VW, height: IH + PADB, willChange: 'transform' });
    const img = mk(sheet, '', { position: 'absolute', left: 0, top: 0, width: VW, height: IH, display: 'block' }, '', 'img');
    setSrc(img, 'media/' + m.src);
    const url = m.url.replace(/^https?:\/\//, '').replace(/\/$/, '');
    mk(win, '', { position: 'absolute', left: 0, top: 0, width: VW, height: PAGE_BAR, background: '#E9EBEF', borderBottom: '1px solid #CFD3DA', display: 'flex', alignItems: 'center', gap: '10px', padding: '0 18px', zIndex: 3 },
      '<i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FF5F57"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FEBC2E"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#28C840"></i>' +
      `<span style="margin-left:12px;flex:1;height:30px;line-height:30px;border-radius:15px;background:#fff;padding:0 18px;font:600 19px 'JetBrains Mono';color:#4B5563;white-space:nowrap;overflow:hidden">${url}</span>`);
    const zhBar = mk(win, '', { position: 'absolute', left: 0, right: 0, bottom: 0, height: ZB[0], background: 'rgba(27,27,31,.93)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: `800 ${ZB[1]}px 'Noto Sans SC'`, padding: `0 ${ZB[2]}px`, zIndex: 4, opacity: 0, whiteSpace: 'nowrap' });
    const hs = marks.map(([needle, tm, zh]) => {
      const rects = m.marks[needle];
      if (!rects) throw new Error(`页面图 ${key} 里没有高亮句子「${needle}」`);
      const frame = needle.startsWith('#sel:');                  // 图表这类整块的东西：画橙色边框，不填色（填色会盖住图）
      const els = rects.map(([x, y, w, h]) => mk(sheet, '', frame
        ? { position: 'absolute', left: x * k - 6, top: y * k - 6, width: w * k + 12, height: h * k + 12, border: '6px solid #FF4F1A', borderRadius: '12px', boxShadow: '0 0 0 8px rgba(255,79,26,.16)', transformOrigin: '0 50%', visibility: 'hidden' }
        : { position: 'absolute', left: x * k - 5, top: y * k - 3, width: w * k + 10, height: h * k + 6, background: 'rgba(255,205,40,.64)', mixBlendMode: 'multiply', borderRadius: '5px', transformOrigin: '0 50%', visibility: 'hidden' }));
      return { els, t: tm - t0, cy: (rects[0][1] + rects[0][3] / 2) * k, top: rects[0][1] * k, tall: rects[0][3] * k > VH * 0.55, zh };
    });
    const maxS = Math.max(0, IH + PADB - VH);
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

// ═════════════════════════════ 演示视频上的来源角标（右上角）
Object.entries(TL.clips).forEach(([cid, k]) => {
  if (k.overlay !== 'clip' || !k.credit) return;
  ovB(k.s + 0.1, (TL.segs.find(g => g.id === cid) || k).e - 0.05, p => {            // 最后一个场景要盖到片尾（场景结束后还有一小段尾巴）
    const cr = at(p, null, null, null, null, 'credit', {}, '画面：' + k.credit);
    return lt => show(cr, lt, 0, { dy: -8 });
  });
});

// ═════════════════════════════ 本期的叠加层（剧本定稿后补）
// 小工具：演示视频上的中文说明条 / 高亮框 / 键帽
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
// 大数字卡片（整页坐标，版式 B：字幕下面 y 1658 起，紧凑版 205 px 高；不要和 linkPill 同时出现）：big(t0, t1, '70.8', '%', '最大的模型选择删照片换止痛', {y})
// 一条短视频里最多两三张，只放钩子里那个数和最关键的对照数；别贴右边（抖音按钮在 x ≥ 940）。
function big(t0, t1, num, unit, desc, o = {}) {
  ovP(t0, t1, p => {
    const el = at(p, null, null, null, null, 'bigcard', { top: o.y ?? 1658 }, `<div class="n">${num}<small>${unit || ''}</small></div>` + (desc ? `<div class="d">${desc}</div>` : ''));
    return lt => show(el, lt, 0, { dy: 24, scale: 0.96 });
  });
}

// GitHub 链接条（整页坐标，字幕下面 y 1658，96 px 高）：展示 GitHub 页面的几秒里把链接亮出来（用户 2026-10-04）
//   linkPill(S('N02') + 0.05, E('N02') + 0.35, 'github.com/', 'neilsonnn/<b>image-blaster</b>')   和 big() 的位置相同，不要同时出现
function linkPill(t0, t1, host, path, o = {}) {
  ovP(t0, t1, p => {
    const el = at(p, null, null, null, null, 'linkpill', { top: o.y ?? 1658 }, `<i>${host}</i>${path}`);
    return lt => show(el, lt, 0, { dy: 24, scale: 0.96 });
  });
}

// ═════════════════════════════ 文章配图镜头（本条加的：作者 @kmeanskaran 的长文里有 9 张手绘风示意图，数字和结论都在图里）
// figShot(从哪句, 到哪句, 图名, 镜头关键帧, 高亮框, {t0, t1, move})
//   图名：figs.js 里的（build_figs.py）；坐标一律是原图像素（1600 宽）。
//   镜头 cams = [[t, cx, cy, w], …]：t = 成片秒，镜头在这一刻到位；(cx, cy) = 取景中心，w = 取景宽（高 = w × 829/1474）；第一项的 t 不用（开场取景），
//                之后每一项在 t 前 move 秒（默认 0.85）开始从上一个取景缓动过来。fit([x, y, w, h]) 把一个矩形换成 cx, cy, w。
//   高亮框 marks = [{t, r: [x, y, w, h] 或 图里量好的名字, tag: '框边上的小标签', until}]：t 起出现、until（默认到镜头结束）撤掉。
//   t0 / t1：自定义起止（一个场景里连着放几张图时写；前一个的 t1 比后一个的 t0 多 0.12，让后一个盖在前一个上面渐入，不闪底色）。
const FIG_RAT = 829 / 1474;
const fit = (r, o = {}) => {
  const w = Math.max(o.minW ?? 760, r[2] * (o.margin ?? 1.3), r[3] * (o.margin ?? 1.3) / FIG_RAT);
  return [r[0] + r[2] / 2 + (o.dx || 0), r[1] + r[3] / 2 + (o.dy || 0), w];
};
function figShot(from, to, key, cams, marks = [], opt = {}) {
  const m = FG[key]; if (!m) throw new Error('没有配图 ' + key);
  const sg0 = TL.segs.find(g => g.s <= S(from) + 1e-6 && S(from) < g.e), sg1 = TL.segs.find(g => g.s <= E(to) + 1e-6 && E(to) < g.e + 1e-6);
  let t0 = sg0 ? Math.min(S(from) - 0.2, sg0.s) : S(from) - 0.2, t1 = Math.max(E(to) + 0.12, sg1 ? sg1.e - 0.02 : 0);
  if (opt.t0 != null) t0 = opt.t0;
  if (opt.t1 != null) t1 = opt.t1;
  ovPage(t0, t1, p => {
    const SWD = 1474, SHT = 829, MV = opt.move ?? 0.85;
    const stage = at(p, 0, 0, SWD, SHT, '', { background: m.bg, overflow: 'hidden' });
    const world = mk(stage, '', { position: 'absolute', left: 0, top: 0, width: m.w, height: m.h, transformOrigin: '0 0', willChange: 'transform' });
    const img = mk(world, '', { position: 'absolute', left: 0, top: 0, width: m.w, height: m.h, display: 'block' }, '', 'img');
    setSrc(img, 'media/figs/' + m.src);
    const K = cams.map(([t, cx, cy, w], i) => ({ t: i === 0 ? -99 : t - t0, cx, cy, w }));
    const camAt = lt => {
      let c = K[0];
      for (let i = 1; i < K.length; i++) {
        const b = K[i].t, a = b - Math.min(MV, Math.max(0.2, b - (i === 1 ? -99 : K[i - 1].t)));
        if (lt >= b) { c = K[i]; continue; }
        if (lt > a) { const e = easeIO((lt - a) / (b - a)); return { cx: lerp(c.cx, K[i].cx, e), cy: lerp(c.cy, K[i].cy, e), w: Math.exp(lerp(Math.log(c.w), Math.log(K[i].w), e)) }; }
        break;
      }
      return c;
    };
    const place = c => {
      const w = c.w, h = w * FIG_RAT;
      let x0 = c.cx - w / 2, y0 = c.cy - h / 2;
      x0 = w <= m.w ? clamp(x0, 0, m.w - w) : (m.w - w) / 2;
      y0 = h <= m.h ? clamp(y0, 0, m.h - h) : (m.h - h) / 2;
      return { x0, y0, s: SWD / w };
    };
    const hs = marks.map(mm => {
      const rects = typeof mm.r === 'string' ? m.marks[mm.r] : [mm.r];
      if (!rects) throw new Error(`图 ${key} 里没有量好的框「${mm.r}」`);
      const boxes = rects.map(() => mk(stage, '', { position: 'absolute', border: '7px solid #FF4F1A', borderRadius: '12px', boxShadow: '0 0 0 9px rgba(255,79,26,.2)', visibility: 'hidden', zIndex: 4 }));
      const tagEl = mm.tag ? mk(stage, 'tagpill', { visibility: 'hidden', zIndex: 5 }, mm.tag) : null;
      return { t: mm.t - t0, until: mm.until != null ? mm.until - t0 : null, rects, boxes, tagEl, pad: mm.pad ?? 10, side: mm.side };
    });
    return lt => {
      const c = camAt(lt), v = place(c);
      world.style.transform = `translate(${-v.x0 * v.s}px, ${-v.y0 * v.s}px) scale(${v.s})`;
      for (const h of hs) {
        const aIn = easeOut((lt - h.t) / 0.35), aOut = h.until != null ? 1 - easeIn((lt - h.until) / 0.25) : 1;
        const vis = lt < h.t ? 0 : Math.min(aIn, aOut);
        h.boxes.forEach((b, i) => {
          const [x, y, w, hh] = h.rects[i], P = h.pad;
          b.style.left = ((x - v.x0) * v.s - P) + 'px'; b.style.top = ((y - v.y0) * v.s - P) + 'px';
          b.style.width = (w * v.s + 2 * P) + 'px'; b.style.height = (hh * v.s + 2 * P) + 'px';
          b.style.opacity = vis; b.style.visibility = vis < 0.002 ? 'hidden' : 'visible';
        });
        if (h.tagEl) {
          const [x, y, w, hh] = h.rects[0], P = h.pad, bl = (x - v.x0) * v.s - P, bt = (y - v.y0) * v.s - P, bh = hh * v.s + 2 * P;
          const tw = h.tagEl.offsetWidth, th = h.tagEl.offsetHeight;
          let ty = h.side === 'below' ? bt + bh + 16 : bt - th - 16; if (ty < 12) ty = bt + bh + 16;
          h.tagEl.style.left = clamp(bl, 12, SWD - tw - 12) + 'px'; h.tagEl.style.top = clamp(ty, 12, SHT - th - 12) + 'px';
          h.tagEl.style.opacity = vis; h.tagEl.style.visibility = vis < 0.002 ? 'hidden' : 'visible';
        }
      }
    };
  });
}

// ═════════════════════════════ 本条的叠加层（写在这里；时间都按字幕条算）
// 写法（S / E / P / V 的意思见文件开头）：
//   big(t0, t1, '36.3', '度', '霸王龙的体温，和人几乎一样')   整页的大数字卡片（字幕下面），一条最多两三张
//   note(t0, t1, '中文译文', '小字（可选）', {x, y, w, lower})   素材上的中文说明条，默认放在左下（y 648）；竖屏上字会缩到 0.66，一条 ≤ 16 字；lower = 双分镜的下框
//   box(t0, t1, x, y, w, h, {lower})                   橙色高亮框（坐标是素材框 1474×829 里的；源视频 1920×1080 的坐标 × 0.7677；带 crop 的段要按裁出来的那块换算）
//   pageShot('N04', 'N05', 'X_t1', [[要高亮的句子, 刷上的时刻, 底部中文译文], …], {start, pad})   官方页面 / 推文录屏（页面图名字在 capture_pages.py 的 SPECS 里）
// 例：
//   const a = V('d1', 10.1), b = V('d1', 12.6);                       // 演示视频第 10.1–12.6 秒在成片里的时刻
//   box(a, b, 62, 254, 1298, 54);  note(a, b, '演示视频在这一行上标了：一笔带过', 'Glossed over');
//   pageShot('N04', 'N05', 'X_t1', [['new plugin to Claude Code', S('N04') + 0.2, '官方推文：Claude Code 新增插件'], ["It scans Claude's output", P('N05', '扫描'), '扫描 Claude 的输出']]);
// 经验：终端演示里右上角有来源角标，别把译文条放在那儿；输入框那一带（y 640–740）和引用块与输入行之间的空档最干净；
//       被引用 / 追问的内容在输入行里时，译文条改放 y 636 的单行，别盖住输入。最后一个场景的叠加层要盖到片尾（TL.total）。

// 图里量好的矩形（原图像素；用 render_all.py --stills 出静帧核对）
const R = {
  dec: { sub: [58, 96, 548, 38], tensor: [358, 168, 644, 104], active: [158, 838, 504, 136], kv: [698, 838, 504, 136], dash: [1258, 796, 306, 208],
         ms15: [1280, 822, 270, 78], ms001: [1280, 906, 270, 84], cap: [376, 1058, 852, 64] },
  inside: { pipe: [452, 776, 366, 76], hbm: [58, 868, 1484, 176], cap: [360, 1076, 884, 58] },
  trainvs: { mem: [86, 494, 500, 142], bar: [360, 966, 884, 52] },
  quant: { top: [58, 166, 1018, 170], half: [476, 350, 656, 46] },
};

// ── S1 钩子：搬权重 1.5 ms / 算数 0.01 ms 那个虚线框；N02 把镜头摇到图左上角的条件（gpt-oss-120b、一张 H100、batch of one）
figShot('N01', 'N02', 'dec',
  [[0, 1280, 870, 640], [S('N02') + 0.6, ...fit(R.dec.sub, { minW: 1000, margin: 1.4, dy: 160 })]],
  [{ t: S('N01') + 0.35, r: R.dec.dash, until: S('N02') - 0.1 }, { t: S('N02') + 0.6, r: R.dec.sub }],
  { move: 0.8 });
big(P('N01', '145 倍') - 0.15, E('N01') + 0.6, '145', '倍', '等数据的时间 ÷ 算数的时间（作者按规格表算）');

// ── S2 背书：推文卡（作者、日期）→ 往下摇到文章封面
figShot('N03', 'N03', 'card',
  [[0, ...fit([252, 70, 1096, 446], { margin: 1.08, minW: 1100 })], [P('N03', '发长文') - 0.2, 800, 960, 1600]],
  [{ t: S('N03') + 0.3, r: '@kmeanskaran', until: P('N03', '发长文') - 0.4 }, { t: P('N03', '10 月') - 0.1, r: 'Oct 1, 2026', until: P('N03', '发长文') - 0.4 },
   { t: P('N03', '发长文'), r: 'cover_title' }]);

// ── S3 怎么算：N04–N05 在 06 图上（算数 0.01 ms → 要搬的 5 GB 权重），N06 前半句换 03 图（3.35 TB/s 的细管子），后半句和 N07 回到 06 图
figShot('N04', 'N05', 'dec',
  [[0, 680, 400, 1000], [P('N04', '约 0.01') - 0.3, ...fit(R.dec.ms001, { minW: 800, margin: 1.5 })], [S('N05') - 0.15, 660, 930, 1160]],
  [{ t: S('N04') + 0.6, r: R.dec.tensor, until: P('N04', '约 0.01') - 0.2 }, { t: P('N04', '约 0.01'), r: R.dec.ms001, until: S('N05') - 0.1 }, { t: S('N05') + 0.35, r: R.dec.active, tag: '作者估算' }],
  { t1: S('N06') + 0.06 });
figShot('N06', 'N06', 'inside',
  [[0, 800, 860, 1000]],
  [{ t: S('N06') + 0.25, r: R.inside.pipe }],
  { t0: S('N06') - 0.06, t1: P('N06', '搬一趟') + 0.06 });
figShot('N06', 'N07', 'dec',
  [[0, ...fit(R.dec.ms15, { minW: 800, margin: 1.5 })], [P('N07', '理论上') - 0.4, 660, 930, 1160]],
  [{ t: P('N06', '搬一趟'), r: R.dec.ms15, until: P('N07', '理论上') - 0.3 }, { t: P('N07', '每秒'), r: R.dec.cap }],
  { t0: P('N06', '搬一趟') - 0.06 });
big(P('N07', '670') - 0.2, E('N07') + 0.5, '670', 'token / 秒', '一个用户的理论上限（按规格表算，没实测）');

// ── S4 H200：NVIDIA 官网那句 141 GB / 4.8 TB/s
pageShot('N08', 'N08', 'Y_h200', [['141', P('N08', '141 GB') - 0.35, 'H200：141 GB 显存，每秒 4.8 TB']]);

// ── S5 训练 vs 推理：每参数 18 字节 → 2.1 TB vs 65 GB
figShot('N09', 'N10', 'trainvs',
  [[0, ...fit(R.trainvs.mem, { minW: 880, margin: 1.4 })], [S('N10') - 0.2, 800, 880, 1100]],
  [{ t: S('N09') + 0.4, r: R.trainvs.mem, until: S('N10') - 0.3 }, { t: P('N10', '训练约'), r: R.trainvs.bar }]);
big(P('N10', '训练约') - 0.1, E('N10') + 0.5, '2.1 TB vs 65 GB', '', '训练 vs 部署（粗算，训练不含激活）');

// ── S6 量化：BF16 → 4 位
figShot('N11', 'N12', 'quant',
  [[0, 580, 360, 1160]],
  [{ t: S('N11') + 1.2, r: R.quant.top, until: S('N12') - 0.3 }, { t: P('N12', '压成'), r: R.quant.half }]);
big(P('N12', '234') - 0.2, E('N12') + 0.5, '234 → 65 GB', '', 'gpt-oss-120b：BF16 vs 4 位量化');

// ── S7 租卡：Hugging Face 价格表（AWS）的 A100 x1 一行、H200 x8 一行
pageShot('N13', 'N15', 'Y_price', [['a100', P('N13', '2.5 美元') - 0.3, 'A100 80GB：每小时 2.5 美元'], ['h200x8', P('N15', '8 张') - 0.3, '8 张 H200：1128 GB，每小时 40 美元']]);
big(P('N15', '1.56') - 0.2, E('N15') + 0.5, '1.56 TB > 1128 GB', '', 'Kimi K3 的权重 > 8 张 H200 的总显存');

// ── S8 泼冷水：回到 06 图的“exact math”（作者自己都叫它规格表算术）
figShot('N16', 'N16', 'dec',
  [[0, ...fit(R.dec.sub, { minW: 1000, margin: 1.4, dy: 160 })]],
  [{ t: S('N16') + 0.5, r: R.dec.sub, tag: '没实测，规格表算的', side: 'below' }]);

// ── S9 收尾：权重 ÷ 显存（80 GB 的 HBM）→ 活跃权重 ÷ 带宽（3.35 TB/s 的细管子）→ 金句落在 06 图的结论上
figShot('N17', 'N18', 'inside',
  [[0, ...fit(R.inside.hbm, { minW: 1300, margin: 1.05, dy: -100 })], [S('N18') - 0.2, 800, 860, 1000]],
  [{ t: P('N17', '权重除以显存'), r: R.inside.hbm, until: S('N18') - 0.3 }, { t: S('N18') + 0.2, r: R.inside.pipe }],
  { t1: S('N19') + 0.06 });
figShot('N19', 'N19', 'dec',
  [[0, 660, 930, 1160]],
  [{ t: S('N19') + 0.3, r: R.dec.cap }],
  { t0: S('N19') - 0.06, t1: TL.total + 0.5 });
