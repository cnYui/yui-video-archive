// 工具 + 叠加层（演示区 1474×829 内的坐标）。素材为主：@ClaudeDevs 的官方演示视频 + 官方页面 / 推文录屏（pageShot），上面只加少量标注和中文译文；不放静态文字卡片。
// 每个叠加层 [t0, t1] 显示（前后淡入淡出），t 用成片秒数；时间都按字幕条算：S('N07') = 这条开始说的时刻，P('N09', '词') = 说到这个词的时刻；
// V('d1', 14.0) = 官方演示视频（素材 d1）第 14.0 秒在成片里的时刻（用来把标注钉在演示的某一刻上）。
// 字幕条：N01… = 画外音（Fish 网页版「赛马娘（曼波欧耶版）」S2 Pro）；字幕是中英双语，见 engine.js / build_timeline.py。
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
// 素材 key 的第 ts 秒在成片里是第几秒（素材按原速放；同一个素材的各段互不重叠）
function V(key, ts) {
  for (const c of Object.values(TL.clips)) for (const r of c.ranges) if (r.src === key && ts >= r.in - 1e-6 && ts <= r.out + 1e-6) return r.s + (ts - r.in);
  throw new Error(`素材 ${key} 的 ${ts} s 没有放进成片`);
}

const OV = [];   // {t0, t1, build(root) → update(lt), fast?:true（官方页面镜头之间快切）}
const ovB = (t0, t1, build) => OV.push({ t0, t1, build });
const ovPage = (t0, t1, build) => OV.push({ t0, t1, build, fast: true });

// ═════════════════════════════ 官方页面 / 推文录屏
// pageShot(从哪句, 到哪句, 页面图名字, [[要高亮的句子, 刷上的时刻, 中文译文?], …], {start: 起始滚动位置（图片像素）, pad: 比最后一句再多留的秒数})
// 图是 capture_pages.py 截的（800 CSS 宽 × 2 倍像素 = 1600 宽；推文是它自己的宽度），铺满演示区宽度；每条高亮出现前 0.95 s 开始往它那里滚，滚到画面偏上三分之一的位置。
const PAGE_BAR = 46;
function pageShot(from, to, key, marks, opt = {}) {
  const m = PG[key]; if (!m) throw new Error('没有页面图 ' + key);
  // 页面镜头铺满整个场景（卡片场景的前后各有零点几秒的空档，不铺满会闪一下空白的底）
  const sg0 = TL.segs.find(g => g.s <= S(from) + 1e-6 && S(from) < g.e), sg1 = TL.segs.find(g => g.s <= E(to) + 1e-6 && E(to) < g.e + 1e-6);
  const t0 = sg0 ? Math.min(S(from) - 0.2, sg0.s) : S(from) - 0.2, t1 = Math.max(E(to) + 0.12, sg1 ? sg1.e - 0.02 : 0) + (opt.pad || 0);
  ovPage(t0, t1, p => {
    const VW = 1474, IW = Math.round(VW * (opt.scale || 1)), VH = 829 - PAGE_BAR, k = IW / m.w, IH = m.h * k, PADB = 200;   // opt.scale < 1：整张图缩小居中（图表框比窗口还高时用，整框才放得下）
    const win = at(p, 0, 0, VW, 829, '', { background: m.bg, overflow: 'hidden' });
    const view = mk(win, '', { position: 'absolute', left: 0, top: PAGE_BAR, width: VW, height: VH, overflow: 'hidden', background: m.bg });
    const sheet = mk(view, '', { position: 'absolute', left: (VW - IW) / 2, top: 0, width: IW, height: IH + PADB, willChange: 'transform' });
    const img = mk(sheet, '', { position: 'absolute', left: 0, top: 0, width: IW, height: IH, display: 'block' }, '', 'img');
    setSrc(img, 'media/' + m.src);
    const url = m.url.replace(/^https?:\/\//, '').replace(/\/$/, '');
    mk(win, '', { position: 'absolute', left: 0, top: 0, width: VW, height: PAGE_BAR, background: '#E9EBEF', borderBottom: '1px solid #CFD3DA', display: 'flex', alignItems: 'center', gap: '10px', padding: '0 18px', zIndex: 3 },
      '<i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FF5F57"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FEBC2E"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#28C840"></i>' +
      `<span style="margin-left:12px;flex:1;height:30px;line-height:30px;border-radius:15px;background:#fff;padding:0 18px;font:600 19px 'JetBrains Mono';color:#4B5563;white-space:nowrap;overflow:hidden">${url}</span>`);
    const zhBar = mk(win, '', { position: 'absolute', left: 0, right: 0, bottom: 0, height: 100, background: 'rgba(27,27,31,.93)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: "800 40px 'Noto Sans SC'", padding: '0 36px', zIndex: 4, opacity: 0, whiteSpace: 'nowrap' });
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
function note(t0, t1, zh, small, o = {}) {                    // 中文译文条（默认左下，盖在终端输入框那一带，不挡正文）
  ovB(t0, t1, p => {
    const el = at(p, null, null, null, null, 'zhnote', { left: o.x ?? 40, top: o.y ?? NOTE_Y, maxWidth: o.w ?? 1394 }, zh + (small ? `<small>${small}</small>` : ''));
    return lt => show(el, lt, 0, { dy: 10 });
  });
}
function box(t0, t1, x, y, w, h) {                            // 橙色高亮框
  ovB(t0, t1, p => { const el = at(p, x, y, w, h, 'hl', {}); return lt => show(el, lt, 0.05, { dy: 0, scale: 1.02 }); });
}

// ═════════════════════════════ 本期的叠加层（写在这里；时间都按字幕条算）
// 写法（S / E / P / V 的意思见文件开头）：
//   note(t0, t1, '中文译文', '小字（可选）', {x, y, w})   演示视频上的中文译文条，默认放在左下（y 648，终端输入框那一带，不挡正文）
//   box(t0, t1, x, y, w, h)                            橙色高亮框（坐标是演示区 1474×829 里的；源视频 1920×1080 的坐标 × 0.7677）
//   pageShot('N04', 'N05', 'X_t1', [[要高亮的句子, 刷上的时刻, 底部中文译文], …], {start, pad})   官方页面 / 推文录屏（页面图名字在 capture_pages.py 的 SPECS 里）
// 例：
//   const a = V('d1', 10.1), b = V('d1', 12.6);                       // 演示视频第 10.1–12.6 秒在成片里的时刻
//   box(a, b, 62, 254, 1298, 54);  note(a, b, '演示视频在这一行上标了：一笔带过', 'Glossed over');
//   pageShot('N04', 'N05', 'X_t1', [['new plugin to Claude Code', S('N04') + 0.2, '官方推文：Claude Code 新增插件'], ["It scans Claude's output", P('N05', '扫描'), '扫描 Claude 的输出']]);
// 经验：终端演示里右上角有来源角标，别把译文条放在那儿；输入框那一带（y 640–740）和引用块与输入行之间的空档最干净；
//       被引用 / 追问的内容在输入行里时，译文条改放 y 636 的单行，别盖住输入。最后一个场景的叠加层要盖到片尾（TL.total）。

// ═════════════════════════════ 第 04 期：Sonnet 5.5 与 Haiku 5.5（价格 + 能力）
// 画面：官方 @ClaudeDevs 护蛋演示 + 官方发布页 / 价格页 / 模型总览 / 推文的页面录屏；叠加层只做译文、高亮和一张“账单”对比。

// ── 开场：护蛋演示自带英文说明，这里把底部那行官方说明译成中文，再给出结果对比
note(S('N02') - 0.1, E('N05') + 0.1, '官方说明：用一套家用物品给鸡蛋做护具，从越来越高处扔下，目标 32 米', 'Opus 带 Haiku 子智能体更快、更省 · 画面回放 3.5 倍，标注处 20 倍', { x: 40, y: 716, w: 1394 });
note(S('N06') + 0.05, E('N07') + 0.4, '右 58 秒 · 86 个 · $0.14　　左 3 分 37 秒 · 25 个 · $0.47', '“快近四倍、便宜七成”是按画面里的计时器自己算的', { x: 40, y: 716, w: 1394 });

// ── 收尾前回看演示：框出右边“Opus 5.5 + 10 个 Haiku 5.5 子智能体”的标题
{ const a = V('d1', 10.2), b = V('d1', 15.8); box(a, b, 752, 96, 692, 76); }               // H0 里（V 只认素材第一次出现的那一段）
{ const c = TL.clips.C9.s; box(c + 0.4, c + 5.6, 752, 96, 692, 76); }                          // C9 里再框一次

// ── 来源角标挪到演示框上沿（默认在右上角，会盖住护蛋演示顶上的标题）
{ const st = document.createElement('style'); st.textContent = '.credit{display:none !important}'; document.head.appendChild(st); }
Object.entries(TL.clips).forEach(([cid, k]) => {                 // 来源角标：放在左栏目录下面（演示框里放哪都会盖住护蛋演示顶上的标题；position:fixed 才不被演示框裁掉）
  if (k.overlay !== 'clip' || !k.credit) return;
  ovB(k.s + 0.1, (TL.segs.find(g => g.id === cid) || k).e - 0.05, p => {
    const el = mk(p, '', { position: 'fixed', left: 118, top: 672, background: 'rgba(17,17,17,.86)', color: '#fff', font: "700 26px 'Noto Sans SC'", padding: '8px 20px', borderRadius: '12px', whiteSpace: 'nowrap', zIndex: 5 }, '画面：' + k.credit);
    return lt => show(el, lt, 0, { dy: -8 });
  });
});

// ── 页面录屏（页面图名字在 capture_pages.py 的 SPECS 里；下方中文条 ≤ 28 字）
pageShot('N08', 'N09', 'S_head', [['September 28, 2026', S('N09') + 0.1, 'Sonnet 5.5 官方发布页：美国时间 2026-09-28']], { start: 0 });
pageShot('N09b', 'N09b', 'H_head', [['October 7, 2026', S('N09b') + 0.1, 'Haiku 5.5 官方发布页：美国时间 2026-10-07']], { start: 0 });

// 第 1 章：价格
pageShot('N10', 'N11', 'X_t1', [
  ['around 75% less to run', P('N10', '平均'), '官方推文：平均便宜约 75%'],
  ['than Claude Haiku 4.5', S('N11') + 0.2, '对比的是上一代 Haiku 4.5']], { start: 0 });

pageShot('N12', 'N22', 'Y_models', [
  ['@row:Pricing|$10 / input MTok$50 / output MTok', S('N14') + 0.4, 'Fable 5.1：输入 $10 / 输出 $50'],
  ['@row:Pricing|$4 / input MTok$20 / output MTok', S('N15') + 0.4, 'Opus 5.5：输入 $4 / 输出 $20'],
  ['@row:Pricing|$2 / input MTok$10 / output MTok', S('N16') + 0.4, 'Sonnet 5.5：输入 $2 / 输出 $10'],
  ['@row:Pricing|From $0.10 / input MTokFrom $0.50 / output MTok', S('N17') + 0.4, 'Haiku 5.5：输入 $0.10 / 输出 $0.50']], { start: 0 });

// 账单：输入 100 万 + 输出 20 万 token（按官方标价自己算的；Haiku 的每次提示都在 10 万以内）
ovB(S('N19') - 0.05, E('N22') + 0.25, p => {
  const T0 = S('N19') - 0.05, X0 = 770, Y0 = 96, W = 660, H = 452;
  const card = at(p, X0, Y0, W, H, '', { background: '#fff', border: '5px solid #141413', borderRadius: '18px', boxShadow: '9px 9px 0 #FF4F1A', overflow: 'hidden' });
  mk(card, '', { position: 'absolute', left: 28, top: 18, width: W - 56, font: "800 32px/1.3 'Noto Sans SC'", color: '#141413' }, '同样跑：输入 100 万 + 输出 20 万 token');
  mk(card, '', { position: 'absolute', left: 28, top: 62, width: W - 56, font: "600 21px/1.35 'Noto Sans SC'", color: '#6B7280' }, '按官方标价自己算的 · 不含缓存和批量折扣 · Haiku 的提示都在 10 万以内');
  const rows = [['Haiku 5.5', 0.2, '#FF4F1A', P('N20', 'Haiku')], ['Sonnet 5.5', 4, '#141413', P('N20', 'Sonnet')], ['Opus 5.5', 8, '#141413', P('N21', 'Opus')], ['Fable 5.1', 20, '#141413', P('N21', 'Fable')]];
  const els = rows.map(([name, cost, col, tm], i) => {
    const y = 124 + i * 80;
    const lab = mk(card, '', { position: 'absolute', left: 28, top: y, width: 190, font: "800 30px/44px 'Noto Sans SC'", color: '#141413', opacity: 0 }, name);
    const bar = mk(card, '', { position: 'absolute', left: 224, top: y + 3, height: 38, width: 6, background: col, borderRadius: '8px', opacity: 0 });
    const val = mk(card, '', { position: 'absolute', left: 240, top: y, font: "800 32px/44px 'Space Grotesk','Noto Sans SC'", color: col, opacity: 0, whiteSpace: 'nowrap' }, '$' + cost);
    return { lab, bar, val, cost, tm: tm + 0.15 - T0, w: Math.max(6, 300 * cost / 20) };
  });
  const tag = mk(card, '', { position: 'absolute', left: 224 + 300 * 4 / 20 + 120, top: 124 + 80 + 7, font: "800 24px 'Noto Sans SC'", color: '#fff', background: '#FF4F1A', padding: '2px 14px 4px', borderRadius: '10px', whiteSpace: 'nowrap', opacity: 0 }, '= Haiku 的 20 倍');
  return lt => {
    els.forEach(e => {
      const a = easeOut((lt - e.tm) / 0.7);
      e.lab.style.opacity = Math.min(1, a * 3);
      e.bar.style.opacity = Math.min(1, a * 3);
      e.bar.style.width = (6 + (e.w - 6) * a) + 'px';
      e.val.style.opacity = Math.min(1, a * 3);
      e.val.style.left = (224 + 6 + (e.w - 6) * a + 14) + 'px';
    });
    tag.style.opacity = easeOut((lt - els[1].tm - 0.7) / 0.4);
  };
});

pageShot('N23', 'N27', 'S_price', [
  ['$2 per million input tokens', S('N23') + 0.6, 'Sonnet 5.5：$2 / $10，和 Sonnet 5 一样'],
  ['$2 per million input tokens', S('N24') + 0.2, '价格页脚注：Sonnet 5 原定涨到 $3 / $15，取消'],
  ['up to 30% less per task', S('N25') + 0.3, '官方：同样的活最多便宜 30%'],
  ['far fewer tokens to do the same work', S('N26') + 0.3, '单价没降：用的 token 少得多'],
  ['30%+ faster than Sonnet 5', S('N27') + 0.3, '输出比 Sonnet 5 快 30% 以上']], { pad: 0 });

pageShot('N28', 'N30', 'H_cache', [
  ['Cache reads now cost 50% less', S('N28') + 0.6, 'Sonnet 5.5 缓存读取价格减半'],
  ['$0.10 per million tokens rather than $0.20', S('N29') + 0.2, '每百万 token：$0.20 → $0.10'],
  ['around 20%', S('N30') + 0.4, '官方：多数智能体任务再省约 20%']], { pad: 0 });

pageShot('N31', 'N34', 'H_price', [
  ['up to 100,000 tokens', S('N31') + 0.5, 'Haiku 5.5 按提示长度分两档（10 万为界）'],
  ['@row:Input tokens|$0.10 / $0.50', S('N32') + 0.3, '输入 $0.10（超过 10 万：$0.50）'],
  ['@row:Output tokens|$0.50 / $2.50', P('N32', '输出'), '输出 $0.50（超过 10 万：$2.50）'],
  ['@row:Input tokens|$0.10 / $0.50', S('N33') + 0.2, '超过 10 万 token：$0.50 / $2.50'],
  ['@row:Input tokens|$1.00', S('N34') + 0.4, 'Haiku 4.5：输入 $1.00'],
  ['@row:Output tokens|$5.00', P('N34', '输出'), 'Haiku 4.5：输出 $5.00']], { start: 130 });

pageShot('N35', 'N39', 'H_foot', [
  ['priced 90% lower than Claude Haiku 4.5', S('N35') + 0.3, '10 万以内的请求：便宜 90%'],
  ['50% lower for requests over 100,000 tokens', P('N35', '长提示'), '超过 10 万的请求：便宜 50%'],
  ['On Haiku 4.5, 90% of requests fell into the former category', S('N36') + 0.3, 'Haiku 4.5 九成请求在 10 万以内'],
  ['priced 90% lower than Claude Haiku 4.5', S('N37') + 0.2, '官方：平均约便宜 75%'],
  ['slightly more tokens per task', S('N38') + 0.3, '新分词器多用一点 token，已算进去']], { start: 0 });

pageShot('N40', 'N43', 'H_credit', [
  ["this week, we'll roll out", S('N40') + 0.3, '每月 API 额度：Max 和 Team 订阅者'],
  ['Max 5x users will get $100', S('N41') + 0.2, 'Max 5 倍档：每月 $100'],
  ['Max 20x users will get $200', P('N41', 'Max 20'), 'Max 20 倍档：每月 $200'],
  ['up to $500, pooled across their users', S('N42') + 0.2, 'Team：最多 $500，全团队共用'],
  ['They can be used on any of our models', S('N43') + 0.2, '额度可用在任何一款模型上'],
  ["this week, we'll roll out", P('N43', '到账'), '“本周起”发放，到账时间官方没写']], { start: 0 });

// 第 2 章：能力
pageShot('N45', 'N52', 'S_perf', [
  ['#sel:table', S('N45') + 0.3, 'Sonnet 5.5 官方基准表'],
  ['@row:Terminal-Bench 4.0|70.6%', S('N46') + 0.5, '终端编程 Terminal-Bench 4.0：70.6%'],
  ['@row:Terminal-Bench 4.0|10.3%', S('N47') + 0.1, 'Sonnet 5：10.3%'],
  ['@row:Terminal-Bench 4.0|66.4%', P('N47', 'Opus'), 'Opus 5.5：66.4%'],
  ['@row:Terminal-Bench 4.0|66.4%', S('N48') + 0.2, 'Opus 取最高的 Xhigh 档（官方脚注）'],
  ['@row:GDPval-AA v2.1|1844', S('N49') + 0.6, '知识工作 GDPval-AA：1844'],
  ['@row:GDPval-AA v2.1|1846', P('N49', '对'), 'Opus 5.5：1846'],
  ['@row:OSWorld 2.1|80.1%', S('N51') + 0.5, '电脑操作 OSWorld 2.1：80.1%'],
  ['@row:OSWorld 2.1|81.8%', P('N51', '对'), 'Opus 5.5：81.8%'],
  ['@row:Chartography|61.6%', S('N52') + 0.5, '看图表 Chartography：61.6%'],
  ['@row:Chartography|15.6%', P('N52', 'Sonnet 5 是'), 'Sonnet 5：15.6%']], { start: 0 });

pageShot('N53', 'N53', 'S_price', [['first Sonnet model to beat', S('N53') + 0.4, '官方：第一个只看截图通关《宝可梦 红》的 Sonnet']], { start: 0 });

pageShot('N54', 'N57', 'S_perf', [
  ['#sel:table', S('N54') + 0.2, 'Opus 5.5 领先八项里的七项'],
  ['Opus 5.5 remains clearly stronger', S('N56') + 0.3, '官方：开放、复杂的任务 Opus 5.5 更强']], { start: 0 });

pageShot('N58', 'N61', 'H_intro', [
  ['high-volume, cost-sensitive tasks', S('N58') + 0.6, '官方定位：大批量、成本敏感的任务'],
  ['summaries, compactions, database queries', S('N59') + 0.2, '摘要、压缩、查数据库、分类'],
  ['as a subagent on coding work', S('N60') + 0.3, '搭配 Opus / Sonnet，当编码子智能体'],
  ['live customer support and browser use', S('N61') + 0.3, '够快：实时客服、浏览器操作']], { start: 0 });

pageShot('N63', 'N67', 'H_bench', [
  ['@row:GDPval-AA v2.1|1620', S('N63') + 0.7, '知识工作 GDPval-AA：1620'],
  ['@row:GDPval-AA v2.1|735', P('N63', '上一代'), 'Haiku 4.5：735'],
  ['@row:OSWorld 2.1|72.4%Offline subset', S('N64') + 0.7, 'OSWorld（离线子集）：72.4%'],
  ['@row:OSWorld 2.1|15.7%Offline subset', P('N64', '上一代'), 'Haiku 4.5：15.7%'],
  ['@row:Terminal-Bench 4.0|39.2%', S('N65') + 0.6, 'Terminal-Bench：39.2%'],
  ['@row:Terminal-Bench 4.0|0.0%', P('N65', '上一代'), 'Haiku 4.5：0.0%'],
  ['GPT-6 Luna', S('N66') + 0.3, 'GPT-6 Luna 有成绩的六项，Haiku 全部更高'],
  ['@row:Terminal-Bench 4.0|39.2%', S('N67') + 0.3, 'Haiku 5.5：39.2%'],
  ['@row:Terminal-Bench 4.0|70.6%', P('N67', '对'), 'Sonnet 5.5：70.6%，差 31.4 个点']], { start: 0 });

pageShot('N68', 'N68', 'H_remain', [['remain better choices for complex agentic coding tasks', S('N68') + 0.5, '官方：复杂的编码智能体任务，仍选 Sonnet / Opus']], { start: 0 });

pageShot('N62', 'N70', 'H_charts', [
  ['first Haiku-class model to come with an adjustable effort setting', S('N62') + 0.4, '官方：第一个带思考力度档位的 Haiku'],
  ['#sel:chart1', S('N69') + 0.6, 'OSWorld：成绩 vs 成本（按思考力度）'],
  ['#sel:chart2', E('N69') + 0.2, 'GDPval-AA：成绩 vs 成本'],
  ['#sel:chart3', S('N70') + 0.5, 'Humanity’s Last Exam：成绩 vs 成本']], { start: 0, scale: 0.62 });

pageShot('N71', 'N71', 'X_t2', [['Claude Platform and Claude Code', S('N71') + 0.5, '官方推文：Haiku 5.5 已在 Claude Code 可用']], { start: 0 });

// 第 3 章：怎么选
pageShot('N73', 'N77', 'Y_models', [
  ['@@start with Claude Opus 5.5 for most workloads', S('N74') + 0.3, '文档：拿不准，先用 Opus 5.5'],
  ['The best combination of speed and intelligence', S('N75') + 0.4, 'Sonnet 5.5：速度和智能的最佳组合'],
  ['For high-volume, latency-sensitive tasks', S('N76') + 0.3, 'Haiku 5.5：大批量、低延迟的任务'],
  ['#sel:table', S('N77') + 0.3, '四款上下文都是 100 万 token']], { start: 0 });
