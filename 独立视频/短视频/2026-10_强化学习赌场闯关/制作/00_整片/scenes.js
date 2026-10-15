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
    if (opt.fixed) hs.forEach(h => h.target = start);            // 本条加的：整条推文几乎都在框里，不滚动（滚了作者名就看不见了）
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

// ═════════════════════════════ 本条的叠加层：《Reinforcement Learning from scratch #1》（@goyal__pramod 的 X 长文）
// 全部是文章里的配图 + 作者的推文截图，没有视频素材。所有时间按字幕条算（S / E / P），换了配音自动跟着走。
// 配图镜头：imgShot(t0, t1, 图名, 镜头关键帧, {marks, bg})
//   镜头关键帧 [[相对 t0 的秒, [x, y, w, h]], …]：图片像素里要铺进素材框的那一块（整块都看得见，比例对不上就多露一点图），关键帧之间缓动（easeIO）；
//   marks：[{t, t1?, r: [x, y, w, h], kind: 'box' | 'hi'}]（t / t1 是成片秒；box = 橙色框，hi = 黄色荧光笔），坐标是图片像素。
const IMG = {
  cover:   ['img/cover.jpg', 1433, 573],          // 文章封面：REINFORCEMENT LEARNING: HOW WE GOT LLMS TO THINK
  casino:  ['img/img02_b10.jpg', 2340, 2084],     // 赌场招牌 “DOUBLE YOUR MONEY / CASINO / THE HOUSE NEVER CHEATS”
  mach3:   ['img/img04_b14.jpg', 1985, 1082],     // 三台老虎机
  mach10:  ['img/img06_b47.jpg', 2122, 1082],     // “THEY ADDED MORE MACHINES!!!” 十台
  logc:    ['img/img07_b68.jpg', 1835, 1068],     // 对数曲线 vs 直线（UCB 加分为什么是 ln t）
  manager: ['img/img08_b83.jpg', 998, 692],       // 经理：“We have had it with your maths…”
  map:     ['img/img09_b86.jpg', 1671, 1082],     // 迷宫地图 THE MAP
  agent:   ['img/img10_b90.jpg', 1190, 1082],     // Maurice = Agent / Environment / Actions / State
  vi:      ['img/img16_b178.png', 1516, 716],     // Sutton & Barto 的 Value Iteration 算法框
  john:    ['img/img17_b186.png', 998, 692],      // JOHN: “ANSWER ME!”
  grid:    ['img/img18_b192.png', 426, 578],      // 4×4 格子的值（随机策略）：0 exit、−14、−20、−22……
};
const FW = 1474, FH = 829;
const R = (x, y, w, h) => [x, y, w, h];
const fitR = r => ({ cx: r[0] + r[2] / 2, cy: r[1] + r[3] / 2, s: Math.min(FW / r[2], FH / r[3]) });
const SG = id => { const g = TL.segs.find(x => x.id === id); if (!g) throw new Error('没有场景 ' + id); return g; };
const sS = id => SG(id).s, sE = id => SG(id).e;
const bd = (a, b) => (E(a) + S(b)) / 2;                       // 两句之间的中点：镜头硬切点

function imgShot(t0, t1, key, views, opt = {}) {
  const m = IMG[key]; if (!m) throw new Error('没有配图 ' + key);
  const [src, W, H] = m;
  const vs = views.map(([t, r]) => Object.assign({ t }, fitR(r)));
  ovPage(t0, t1, p => {                                       // 页面镜头之间快切（淡入淡出 0.1 s）
    const win = at(p, 0, 0, FW, FH, '', { background: opt.bg || '#FFFFFF', overflow: 'hidden' });
    const sheet = mk(win, '', { position: 'absolute', left: 0, top: 0, width: W, height: H, transformOrigin: '0 0', willChange: 'transform' });
    const img = mk(sheet, '', { position: 'absolute', left: 0, top: 0, width: W, height: H, display: 'block' }, '', 'img');
    setSrc(img, 'media/' + src);
    const marks = (opt.marks || []).map(mm => {
      const el = mk(sheet, '', { position: 'absolute', visibility: 'hidden' });
      if (mm.kind === 'hi') { el.style.background = 'rgba(255,205,40,.64)'; el.style.mixBlendMode = 'multiply'; }
      else if (mm.kind === 'veil') { el.style.background = '#FFFFFF'; }                    // 白色遮罩：盖住图里这次不讲的部分
      else { el.style.borderStyle = 'solid'; el.style.borderColor = '#FF4F1A'; }
      return Object.assign({}, mm, { el });
    });
    return lt => {
      let a = vs[0], b = vs[0], u = 0;
      for (let i = 0; i + 1 < vs.length; i++) if (lt >= vs[i].t) { a = vs[i]; b = vs[i + 1]; u = clamp((lt - a.t) / Math.max(1e-6, b.t - a.t)); }
      const e = easeIO(u);
      const s = Math.exp(lerp(Math.log(a.s), Math.log(b.s), e)), cx = lerp(a.cx, b.cx, e), cy = lerp(a.cy, b.cy, e);
      sheet.style.transform = `translate(${FW / 2 - cx * s}px, ${FH / 2 - cy * s}px) scale(${s})`;
      const T = t0 + lt;
      for (const mm of marks) {
        const v = Math.min(easeOut((T - mm.t) / 0.22), mm.t1 == null ? 1 : 1 - easeIn((T - mm.t1) / 0.18));
        const el = mm.el, r = mm.r;
        el.style.visibility = v > 0.002 ? 'visible' : 'hidden';
        if (v <= 0.002) continue;
        el.style.opacity = v;
        if (mm.kind === 'veil') {
          Object.assign(el.style, { left: px(r[0]), top: px(r[1]), width: px(r[2]), height: px(r[3]) });
        } else if (mm.kind === 'hi') {
          Object.assign(el.style, { left: px(r[0] - 6 / s), top: px(r[1] - 3 / s), width: px(r[2] + 12 / s), height: px(r[3] + 6 / s), borderRadius: px(6 / s) });
        } else {
          const bw = 8 / s, pd = 6 / s;
          Object.assign(el.style, { left: px(r[0] - pd), top: px(r[1] - pd), width: px(r[2] + 2 * pd), height: px(r[3] + 2 * pd), borderWidth: px(bw), borderRadius: px(14 / s),
            boxShadow: `0 0 0 ${9 / s}px rgba(255,79,26,.2)`, transform: `scale(${lerp(1.05, 1, v)})` });
        }
      }
    };
  });
}

// ─── H0 钩子（N01）：赌场招牌，从招牌特写拉远到整栋楼
{
  const t0 = -0.4, t1 = sE('H0') + 0.05;
  imgShot(t0, t1, 'casino', [[0, R(800, 240, 1120, 630)], [E('N01') - t0 + 0.2, R(330, 200, 1980, 1114)]], {
    marks: [{ t: S('N01') + 1.2, t1: E('N01'), r: R(1040, 468, 250, 78) }],           // “CASINO”
  });
}

// ─── B1 背书（N02–N04）：作者的推文（真截图）→ 文章封面 → 推文底部（点赞）+ 收藏数
{
  const b1 = bd('N02', 'N03'), b2 = bd('N03', 'N04'), end = sE('B1') + 0.05;
  pageShot('N02', 'N02', 'X_t1', [['Oct 3, 2026', S('N02') + 0.5, '10 月 3 日发布'], ['almost an all-nighter', P('N02', '通宵') - 0.9, '几乎熬了个通宵']], { t0: sS('B1') - 0.05, t1: b1 + 0.05, start: 0, fixed: true });
  imgShot(b1 - 0.05, b2 + 0.05, 'cover', [[0, R(0, 0, 1433, 573)], [b2 - b1, R(40, 10, 760, 428)]], { marks: [{ t: S('N03') + 0.45, r: R(104, 42, 488, 74) }] });
  pageShot('N04', 'N04', 'X_t1', [['924', S('N04') + 0.6, '点赞 924']], { t0: b2 - 0.05, t1: end, start: 0, fixed: true });
  big(S('N04') + 0.4, E('N04') + 0.2, '1751', '收藏', '发出两天 · 点赞 924');
}

// ─── C1 第一关：三台老虎机（N05）：三台依次亮框
{
  const t0 = sS('C1') - 0.05, t1 = sE('C1') + 0.05;
  imgShot(t0, t1, 'mach3', [[0, R(0, 0, 1985, 1082)], [t1 - t0, R(200, 40, 1650, 928)]], {
    marks: [
      { t: S('N05') + 0.9, t1: S('N05') + 1.3, r: R(403, 118, 405, 625) },
      { t: S('N05') + 1.3, t1: S('N05') + 1.7, r: R(903, 118, 405, 625) },
      { t: S('N05') + 1.7, t1: S('N05') + 2.1, r: R(1473, 118, 410, 625) },
    ],
  });
  note(P('N05', '多试'), E('N05') + 0.15, '多试几次 → 求平均', '', { x: 480, y: 668 });
}

// ─── C2 十台和三个办法（N06–N09）：十台老虎机（数一遍 → ε-greedy → 乐观初值）→ 对数曲线（UCB）
{
  const a0 = sS('C2') - 0.05, m = bd('N08', 'N09'), a1 = m + 0.05, b0 = m - 0.05, b1 = sE('C2') + 0.05;
  const M = [R(403, 117, 250, 388), R(712, 119, 248, 385), R(1065, 119, 250, 385), R(1426, 136, 250, 383), R(1735, 136, 248, 383),
             R(403, 596, 250, 384), R(729, 585, 251, 385), R(1039, 585, 250, 385), R(1391, 585, 250, 385), R(1699, 581, 250, 386)];
  const marks = [];
  M.forEach((r, i) => marks.push({ t: S('N06') + 0.5 + i * 0.14, t1: S('N06') + 0.5 + i * 0.14 + 0.24, r }));                  // N06：十台依次亮一下
  marks.push({ t: S('N07') + 1.0, t1: P('N07', '偶尔') + 0.05, r: M[2] });                                                      // N07：先框住“最好的”
  marks.push({ t: P('N07', '偶尔') + 0.2, t1: E('N07') + 0.1, r: M[7] });                                                       //       说到“偶尔”换成随机的一台
  const w0 = P('N08', '逼自己'), step = Math.max(0.1, (E('N08') - 0.1 - w0) / 10);
  M.forEach((r, i) => marks.push({ t: w0 + i * step, t1: w0 + i * step + step * 1.4, r }));                                     // N08：从 1 号扫到 10 号，全试一遍
  imgShot(a0, a1, 'mach10', [[0, R(0, -210, 2122, 1292)], [a1 - a0, R(40, -190, 2042, 1272)]], { marks });          // 图上方留一条白边放标签
  note(S('N06') + 0.1, E('N06') + 0.25, '3 台 → 10 台', '', { x: 40, y: 22 });
  note(S('N07') + 0.1, E('N07') + 0.25, 'ε-greedy：多数押最好，偶尔随机', '', { x: 40, y: 22 });
  note(S('N08') + 0.1, E('N08') + 0.25, '乐观初值：先假设每台 = 10', '', { x: 40, y: 22 });
  imgShot(b0, b1, 'logc', [[0, R(0, 0, 1835, 1068)], [b1 - b0, R(100, 100, 1700, 956)]], { marks: [{ t: S('N09') + 0.5, r: R(170, 215, 690, 690) }, { t: P('N09', '额外') - 0.1, r: R(1120, 220, 590, 160), kind: 'hi' }] });
  note(S('N09') + 0.1, E('N09') + 0.25, 'UCB', '试得少的加分，涨得越来越慢', { x: 640, y: 640 });
}

// ─── C3 赌场改赔率（N10）：经理的气话 + 步长 1/n → 固定 α
{
  const t0 = sS('C3') - 0.05, t1 = sE('C3') + 0.05;
  imgShot(t0, t1, 'manager', [[0, R(0, 0, 998, 692)], [t1 - t0, R(40, 40, 920, 517)]], { marks: [{ t: S('N10') + 1.0, r: R(500, 205, 320, 305) }] });
  note(P('N10', '那就'), E('N10') + 0.2, '步长 1/n → 固定 α', '新数据权重永远更大', { x: 810, y: 40 });
}

// ─── M1 迷宫和地图（N11）
{
  const t0 = sS('M1') - 0.05, t1 = sE('M1') + 0.05;
  imgShot(t0, t1, 'map', [[0, R(0, 0, 1671, 1082)], [t1 - t0, R(30, 30, 1640, 1030)]], {
    marks: [{ t: P('N11', '迷宫') - 0.1, t1: P('N11', '地图') - 0.1, r: R(695, 75, 680, 675) }, { t: P('N11', '地图') - 0.05, r: R(150, 195, 215, 150) }],
  });
}

// ─── M2 机器人对着地图算（N12）：Maurice = 智能体，迷宫 = 环境
{
  const t0 = sS('M2') - 0.05, t1 = sE('M2') + 0.05;
  imgShot(t0, t1, 'agent', [[0, R(20, 20, 1150, 647)], [t1 - t0, R(60, 40, 1070, 602)]], {
    marks: [{ t: P('N12', '地图') - 0.1, t1: P('N12', '机器人') - 0.1, r: R(205, 335, 225, 215) }, { t: P('N12', '机器人') - 0.05, r: R(105, 55, 360, 170) }],
  });
  note(P('N12', '机器人') - 0.1, E('N12') + 0.2, 'Maurice = 智能体', '', { x: 40, y: 700 });
}

// ─── M3 一格值多少（N13：格子里的值）→ 贝尔曼方程（N14：封面里的公式）
{
  const m = bd('N13', 'N14'), g0 = sS('M3') - 0.05, g1 = m + 0.05, e0 = m - 0.05, e1 = sE('M3') + 0.05;
  // N13：格子里的值。文中 John 的问题：11 号格往下走一步 → 落在 15 号（出口）：眼前 −1，下一格价值 0，合计 −1
  imgShot(g0, g1, 'grid', [[0, R(0, 0, 426, 578)], [g1 - g0, R(0, 0, 426, 578)]], {
    marks: [{ t: S('N13') + 0.2, r: R(301, 299, 92, 125) },                                   // 11 号格
            { t: P('N13', '下一格') - 0.1, r: R(301, 426, 92, 124) }],                           // 15 号格（出口）
  });
  note(S('N13') + 0.15, g1, '11 号格', '往下走一步', { x: 36, y: 40 });
  note(P('N13', '眼前') - 0.1, g1, '眼前奖励 −1', '', { x: 1062, y: 250 });
  note(P('N13', '下一格') - 0.1, g1, '下一格价值 0', '', { x: 1062, y: 400 });
  note(P('N13', '打个折') - 0.15, g1, '合计 −1', '', { x: 1062, y: 550 });
  // N14：封面里的贝尔曼方程（第 4 行），用白色遮罩盖住下面的循环图
  imgShot(e0, e1, 'cover', [[0, R(570, 0, 740, 416)], [e1 - e0, R(570, 0, 740, 416)]], {
    marks: [{ t: e0 - 1, r: R(560, 181, 780, 392), kind: 'veil' },
            { t: S('N14') + 0.35, r: R(632, 124, 575, 54), kind: 'hi' },
            { t: P('N14', '一步') - 0.2, r: R(920, 128, 138, 46) }],
  });
  note(S('N14') + 0.1, E('N14') + 0.2, '贝尔曼方程', '只往前看一步', { x: 40, y: 560 });
}

// ─── M4 价值迭代（N15）：Sutton & Barto 的算法框，亮出“取最大”那一行
{
  const t0 = sS('M4') - 0.05, t1 = sE('M4') + 0.05;
  imgShot(t0, t1, 'vi', [[0, R(0, 0, 1516, 716)], [t1 - t0, R(40, 220, 1400, 788)]], { marks: [{ t: P('N15', '取最大') - 0.4, r: R(185, 400, 735, 66) }] });
  note(P('N15', '求平均') - 0.2, E('N15') + 0.2, '价值迭代：平均 → 取最大', '', { x: 40, y: 680 });
}

// ─── T1 圈套（N16）
{
  const t0 = sS('T1') - 0.05, t1 = sE('T1') + 0.05;
  imgShot(t0, t1, 'john', [[0, R(0, 0, 998, 692)], [t1 - t0, R(30, 30, 940, 528)]]);
  note(P('N16', '下一篇') - 0.1, E('N16') + 0.2, '下一篇：没有地图', '', { x: 40, y: 690 });
}

// ─── T2 封面写着（N17）：封面标题放大
{
  const t0 = sS('T2') - 0.05, t1 = sE('T2') + 0.05;
  imgShot(t0, t1, 'cover', [[0, R(0, 0, 1433, 573)], [t1 - t0, R(70, 10, 610, 343)]], { marks: [{ t: P('N17', '怎么') - 0.2, r: R(104, 42, 488, 74) }] });
}

// ─── E1 金句（N18）：回到赌场招牌
{
  const t0 = sS('E1') - 0.05, t1 = sE('E1') + 0.05;
  imgShot(t0, t1, 'casino', [[0, R(330, 200, 1980, 1114)], [t1 - t0, R(760, 360, 1300, 731)]], { marks: [{ t: S('N18') + 0.6, r: R(920, 650, 740, 66) }] });
}
