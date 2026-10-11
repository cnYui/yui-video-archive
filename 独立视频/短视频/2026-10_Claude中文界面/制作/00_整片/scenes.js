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

// ═════════════════════════════ 本条：Claude 中文界面（悠一出镜原声版：画面 = 语言选择框 / 官方页面；悠一的镜像小窗由 compose_face.py 在渲完后叠到下方）
// 台本 = 悠一自己说的话（ASR 转写，只改了听错的专名），画面只配合他说的内容；没有第三方推文。底部黑条 = 说明。
const mid = (a, b) => (E(a) + S(b)) / 2;

// A1 语言列表多了中文（N01）：圈出简体 / 繁體
pageShot('N01', 'N01', 'P_picker', [
  ['title', S('N01') + 0.1],
  ['#sel:zh_s', P('N01', '多了中文') - 0.05],
  ['#sel:zh_t', P('N01', '繁体') - 0.05],
]);

// A2 怎么选（N02）：官网和 APP，左下角头像 → 语言
pageShot('N02', 'N02', 'P_picker', [
  ['lang_top', S('N02') + 0.1],
  ['#sel:zh_s', P('N02', '选语言') - 0.1],
]);
note(S('N02') + 0.05, E('N02') + 0.1, '左下角头像 → 语言', '', { y: 600, x: 40 });

// A3 之前一直不支持中文（N03）：只是他的判断，画面不放“证据”，留着语言选择框
pageShot('N03', 'N03', 'P_picker', [
  ['#sel:all', S('N03') + 0.1],
]);

// A4 大规模封号（N04）：官方透明度页 1–6 月封号 1140 万（全球数据）
pageShot('N04', 'N04', 'A_trust', [
  ['num114', P('N04', '大规模封号') - 0.1, '官方透明度页：1–6 月封号 1140 万个账号（全球数据）'],
  ['updated', P('N04', '从来') - 0.1, '最后更新：2026 年 7 月 23 日'],
]);

// A5 官方帮助页只有 11 种（N05–N07）
pageShot('N05', 'N07', 'R_help', [
  ['intro', S('N05') + 0.1, '官方帮助页：Claude 有多种界面语言（web / desktop）'],
  ['#sel:.intercom-interblocks-unordered-nested-list', S('N06') + 0.1, '八月那一版：11 种语言，没有中文'],
  ['howto', S('N07') + 0.2, '更新日志、官方博客、官方 X：10 月 6 日核对时都没有这条'],
]);

// A6 钓鱼执法？（N08–N09）：圈出简体 / 繁體，说明这只是个人担心
pageShot('N08', 'N09', 'P_picker', [
  ['#sel:zh_s', S('N08') + 0.1],
  ['#sel:zh_t', S('N09') + 0.1],
]);
note(S('N08') + 0.05, E('N09') + 0.2, '个人担心，官方没有这么说', '', { y: 600, x: 40 });

// A7 语言不等于地区（N10、N11）：支持地区页（先标题，再是 Claude.ai 名单：按字母排，Chile 后面是 Colombia）
pageShot('N10', 'N10', 'R_regions', [
  ['policy', S('N10') + 0.1, '官方：支持地区名单（Claude.ai）'],
], { t1: mid('N10', 'N11') });
pageShot('N11', 'N11', 'R_regions2', [
  ['chile', S('N11') + 0.1, 'Claude.ai 名单按字母排：Chile 后面是 Colombia'],
  ['colombia', P('N11', '没有包含') - 0.1, '中间没有 China（中国大陆）；香港、澳门也不在名单里'],
], { t0: mid('N10', 'N11') });

// A8 官方封号理由（N12）：帮助中心——封号理由之一：从不受支持的地点创建账号
pageShot('N12', 'N12', 'R_ban', [
  ['intro', S('N12') + 0.1, '官方帮助中心：可能封号的理由'],
  ['unsupported', P('N12', '封号') - 0.5, '其中一条：从不受支持的地点创建账号'],
]);

// A9 拜托 Claude（N13、N14）：收尾留在语言选择框
pageShot('N13', 'N14', 'P_picker', [
  ['#sel:all', S('N13') + 0.1],
]);
