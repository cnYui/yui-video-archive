// 《Tim Denning 的 36 条忠告》系列的场景库（竖屏单框；gen_episode.py 把它和本期生成的叠加层拼成 scenes.js）。
// 素材框里的坐标是 1474×829（显示时缩到 0.6689）；整页的叠加层（big()）用 1080×2340 的坐标。
// 画面全是真实页面 / 照片：Substack 文章页录屏（pageShot，深色页用橙色荧光 + 底部黄色中文译文条）、作者主页、X 推文卡片、作者照 / 文章配图 / X 横幅（photoShot，缓慢推近）。
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
const segOf = id => { const g = TL.segs.find(x => x.id === id); if (!g) throw new Error('没有场景 ' + id); return g; };

const OV = [];   // {t0, t1, build(root) → update(lt), fast?:true（页面镜头之间快切）, layer?:'page'（整页坐标）}
const ovPage = (t0, t1, build) => OV.push({ t0, t1, build, fast: true });
const ovP = (t0, t1, build) => OV.push({ t0, t1, build, layer: 'page' });
const DW = 1474, DH = 829;                                  // 素材框里的原生坐标

// ═════════════════════════════ 页面录屏（Substack 文章 / 作者主页 / X 推文卡片）
// pageShot(从哪句, 到哪句, 页面图名字, [[要高亮的英文句子, 刷上的时刻, 底部中文译文?], …], {fit: true = 整张页面缩进框里不滚动, start: 起始滚动位置（图片像素）, pad, t0 / t1: 自定义起止})
// 图是 capture_series_pages.py 截的（视口 640 CSS 宽 × 2.4 倍像素 = 1536 宽；推文是它自己的宽度）；每条高亮出现前 0.95 s 开始往它那里滚，滚到画面偏上三分之一的位置。
// 深色页面（Substack 是黑底）：荧光笔看不见，改成橙色半透明底 + 橙色下划线；底部中文译文条是黄底（和边框贴纸同色）；浅色页面（推文卡片）用黄色荧光笔 + 深色译文条。
const PAGE_BAR = 46;
function pageShot(from, to, key, marks, opt = {}) {
  const m = PG[key]; if (!m) throw new Error('没有页面图 ' + key);
  const sg0 = TL.segs.find(g => g.s <= S(from) + 1e-6 && S(from) < g.e), sg1 = TL.segs.find(g => g.s <= E(to) + 1e-6 && E(to) < g.e + 1e-6);
  let t0 = sg0 ? Math.min(S(from) - 0.2, sg0.s) : S(from) - 0.2, t1 = Math.max(E(to) + 0.12, sg1 ? sg1.e - 0.02 : 0) + (opt.pad || 0);
  if (opt.t0 != null) t0 = opt.t0;
  if (opt.t1 != null) t1 = opt.t1;
  const dark = (() => { const c = parseInt(m.bg.slice(1), 16); return ((c >> 16) * .3 + ((c >> 8) & 255) * .59 + (c & 255) * .11) < 90; })();
  ovPage(t0, t1, p => {
    const VW = DW, VH = DH - PAGE_BAR, k = opt.fit ? Math.min(VW / m.w, VH / m.h) : VW / m.w, IW = m.w * k, IH = m.h * k, PADB = opt.fit ? 0 : 130;
    const ZB = [100, 42, 36];                                  // 底部中文译文条：[高, 字号, 左右内边距]
    const win = at(p, 0, 0, VW, DH, '', { background: m.bg, overflow: 'hidden' });
    const view = mk(win, '', { position: 'absolute', left: 0, top: PAGE_BAR, width: VW, height: VH, overflow: 'hidden', background: m.bg });
    const sheet = mk(view, '', { position: 'absolute', left: (VW - IW) / 2, top: opt.fit ? (VH - IH) / 2 : 0, width: IW, height: IH + PADB, willChange: 'transform' });
    const img = mk(sheet, '', { position: 'absolute', left: 0, top: 0, width: IW, height: IH, display: 'block' }, '', 'img');
    setSrc(img, 'media/' + m.src);
    const url = m.url.replace(/^https?:\/\//, '').replace(/\/$/, '');
    mk(win, '', { position: 'absolute', left: 0, top: 0, width: VW, height: PAGE_BAR, background: '#E9EBEF', borderBottom: '1px solid #CFD3DA', display: 'flex', alignItems: 'center', gap: '10px', padding: '0 18px', zIndex: 3 },
      '<i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FF5F57"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FEBC2E"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#28C840"></i>' +
      `<span style="margin-left:12px;flex:1;height:30px;line-height:30px;border-radius:15px;background:#fff;padding:0 18px;font:600 19px 'JetBrains Mono';color:#4B5563;white-space:nowrap;overflow:hidden">${url}</span>`);
    const zhBar = mk(win, '', Object.assign({ position: 'absolute', left: 0, right: 0, bottom: 0, height: ZB[0], display: 'flex', alignItems: 'center', justifyContent: 'center', font: `800 ${ZB[1]}px 'Noto Sans SC'`, padding: `0 ${ZB[2]}px`, zIndex: 4, opacity: 0, whiteSpace: 'nowrap' },
      dark ? { background: '#FFD84D', color: '#141413', borderTop: '5px solid #141413' } : { background: 'rgba(27,27,31,.93)', color: '#fff' }));
    const hs = marks.map(([needle, tm, zh]) => {
      const rects = m.marks[needle];
      if (!rects) throw new Error(`页面图 ${key} 里没有高亮句子「${needle}」`);
      const els = rects.map(([x, y, w, h]) => mk(sheet, '', dark
        ? { position: 'absolute', left: x * k - 7, top: y * k - 4, width: w * k + 14, height: h * k + 8, background: 'rgba(255,106,43,.38)', borderBottom: '5px solid #FF6A2B', borderRadius: '6px', transformOrigin: '0 50%', visibility: 'hidden' }
        : { position: 'absolute', left: x * k - 5, top: y * k - 3, width: w * k + 10, height: h * k + 6, background: 'rgba(255,205,40,.64)', mixBlendMode: 'multiply', borderRadius: '5px', transformOrigin: '0 50%', visibility: 'hidden' }));
      return { els, t: tm - t0, cy: (rects[0][1] + rects[0][3] / 2) * k, top: rects[0][1] * k, tall: rects[0][3] * k > VH * 0.55, zh };
    });
    const maxS = opt.fit ? 0 : Math.max(0, IH + PADB - VH);
    hs.forEach(h => h.target = clamp(h.tall ? h.top - VH * 0.05 : h.cy - VH * 0.34, 0, maxS));      // 高亮落在画面偏上三分之一处（下面留给译文条）
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

// ═════════════════════════════ 照片镜头：photoShot(场景 id, 照片名, {zoom: 推近幅度, fx / fy: 取景焦点（占整图的比例）})
// 照片按“铺满框”放（cover），焦点尽量放在框中央，整场缓慢推近；第一个场景从 −0.5 s 起（第 0 帧就有画面），最后一个场景盖到片尾。
function photoShot(sceneId, key, o = {}) {
  const P0 = PH[key]; if (!P0) throw new Error('没有照片 ' + key);
  const sg = segOf(sceneId);
  const t0 = sg === TL.segs[0] ? -0.5 : sg.s, t1 = sg === TL.segs[TL.segs.length - 1] ? TL.total + 0.5 : sg.e;
  ovPage(t0, t1, p => {
    const win = at(p, 0, 0, DW, DH, '', { background: '#141413', overflow: 'hidden' });
    const k0 = Math.max(DW / P0.w, DH / P0.h) * (o.base ?? 1), W = P0.w * k0, H = P0.h * k0;
    const fx = o.fx ?? 0.5, fy = o.fy ?? 0.5;
    const left = clamp(DW / 2 - fx * W, DW - W, 0), top = clamp(DH / 2 - fy * H, DH - H, 0);
    const img = mk(win, 'ph', { left, top, width: W, height: H, transformOrigin: `${fx * 100}% ${fy * 100}%` }, '', 'img');
    setSrc(img, 'media/' + P0.src);
    const dur = t1 - t0;
    return lt => { img.style.transform = `scale(${1 + (o.zoom ?? 0.06) * clamp(lt / dur)})`; };
  });
}

// ═════════════════════════════ 大数字卡片（整页坐标，版式 B：字幕下面 y 1658 起，紧凑版 205 px 高）：big(t0, t1, '2800万+', '次浏览', '一句说明')
// 一条短视频里最多两三张，只放钩子里那个数和最关键的对照数；别贴右边（抖音按钮在 x ≥ 940）。
function big(t0, t1, num, unit, desc, o = {}) {
  ovP(t0, t1, p => {
    const el = at(p, null, null, null, null, 'bigcard', { top: o.y ?? 1658 }, `<div class="n">${num}<small>${unit || ''}</small></div>` + (desc ? `<div class="d">${desc}</div>` : ''));
    return lt => show(el, lt, 0, { dy: 24, scale: 0.96 });
  });
}

// ═════════════════════════════ 本期的叠加层（gen_episode.py 从 series_data.py 生成，别手改；要改去改数据）

// H0 钩子（N01–N01）
pageShot("N01", "N01", "A_top", [
  ["When you turn 35 you'll see the difference", P("N01", "35 岁", -0.3), "35 岁那年，你会看出冒险的人和没冒险的人的差别"],
]);

// B1 背书·简介（N02–N03）
pageShot("N02", "N03", "P_bio", [
  ["Aussie writer with 1B+ views that made me $6M+", P("N02", "10 亿阅读", -0.6), "简介原话：10 亿+ 阅读的澳洲作家，赚了 600 万美元+"],
  ["Quit my banking job in 2021", P("N03", "2021 年", -0.3), "简介原话：2021 年辞掉了银行的工作"],
]);

// B2 背书·数据（N04–N04）
pageShot("N04", "N04", "X_t1", [
  ["@Tim_Denning", P("N04", "36 条", -0.2), "X 账号 @Tim_Denning（已认证）"],
  ["Jan 20, 2026", P("N04", "浏览", -0.4), "2026 年 1 月 20 日，以 X 长文重发（正文没改）"],
], { fit: true });
{ const t = P("N04", "浏览", -0.2); big(t, t + 2.2, "2800万+", "次浏览", "X 上这篇长文（2026-10-05 读取）"); }

// L1 第1条（N05–N08）
pageShot("N05", "N08", "A_1", [
  ["When you turn 35 you'll see the difference", P("N05", "第一条", 0.0), "第 1 条：35 岁，你会看出谁冒过险、谁没有"],
  ["Not taking risks leads to regrets which ages you faster", P("N06", "后悔", -0.6), "不冒险只会攒下后悔，后悔让人老得更快"],
  ["You always move decisions to the future", P("N07", "推到以后", -0.2), "决定总被推到以后，到时没人为它负责"],
  ["overthinking $100 purchases", P("N08", "100 美元", -0.1), "连 100 美元的东西都要纠结？醒醒"],
]);

// L4 第4条（N09–N11）
pageShot("N09", "N11", "A_4", [
  ["Raise your standards so high", P("N09", "第四条", 0.0), "第 4 条：标准高到别人觉得你是疯子，也别当平均人"],
  ["It helps them feel good about where they're at in life", P("N10", "找台阶", -0.7), "这是自我安慰，让人对现状好受些"],
  ["A lot of decisions are automated for you", P("N11", "自动做完", -0.2), "标准一高，很多决定自动替你做完"],
]);

// L5 第5条（N12–N15）
pageShot("N12", "N15", "A_5", [
  ["Never follow the conventional path", P("N12", "第五条", 0.0), "第 5 条：别走常规路，它最无聊，竞争也最多"],
  ["Get a degree, get into debt, choose a job you pretend is your life's work", P("N13", "标准路线", -0.2), "拿学位、欠一身债、挑一份假装是毕生事业的工作"],
  ["I could predict what would happen in a week", P("N14", "猜得到", -0.9), "下周会发生什么，一眼就能预测"],
  ["Mighty Melbourne burger with beef or the Simon Says chicken burger", P("N15", "牛肉堡", -0.5), "唯一的惊喜：吃牛肉堡还是鸡肉堡"],
]);

// L6 第6条（N16–N17）
pageShot("N16", "N17", "A_6", [
  ["One of the clearest signs of intelligence", P("N16", "第六条", 0.0), "第 6 条：听到不同意见还不上头，是聪明的标志"],
  ["Labels have dumbed us right down", P("N17", "贴标签", -0.1), "标签让我们变笨：“不是这个，就是那个”"],
]);

// C1 泼冷水（N18–N18）
pageShot("N18", "N18", "A_top", [
  ["I'm not that smart but these experiences", P("N18", "不算聪明", -0.9), "我不算聪明，只是这些经历给了我一些有力的教训"],
]);

// E1 金句（N19–N19）
photoShot("E1", "face", { zoom: 0.07, fx: 0.5, fy: 0.42 });
