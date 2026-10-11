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
    const VW = 1474, VH = 829 - PAGE_BAR, k = VW / m.w, IH = m.h * k, PADB = 200;
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

// ═════════════════════════════ 开场（演示的前 12.7 s）：左上角报名字；第 10 秒起官方自己在这一行上标了 “Glossed over”
ovB(S('N01') + 0.3, S('N02') + 0.2, p => {
  const el = at(p, null, null, null, null, 'tagpill fill', { left: 22, top: 20 }, 'Claude Code 新插件 · You should know');
  return lt => show(el, lt, 0, { dy: -10 });
});
{
  const a = V('d1', 10.1), b = V('d1', 12.6);
  box(a, b, 62, 254, 1298, 54);                                // 总结里 “Added automatic retries …” 那一行
  note(a, b, '演示视频在这一行上标了：一笔带过', 'Glossed over');
}

// ═════════════════════════════ 演示 1：提醒弹出（插件在总结下面加了一条 Heads up）
{
  const a = S('N06') + 0.25, b = E('N07') + 0.5;
  box(a + 0.2, b, 24, 470, 1366, 140);
  note(a, b, '提醒：加了自动重试，但重试可能让顾客被扣两次钱', '1 了解更多　2 早就知道　0 忽略');
}
// ═════════════════════════════ 演示 2：按 1 看详情
{
  note(S('N08') + 0.2, E('N09') + 0.4, '超时的付款仍可能成功：回信丢了，重试会再扣一次', '解法：幂等键 = 每笔付款一个随机 ID，每次重试都带着，对方只算一笔');
  box(P('N09', '幂等键') - 0.2, E('N09') + 0.4, 54, 432, 1330, 84);       // “The usual fix is an idempotency key …”
}
// ═════════════════════════════ 演示 3：按 2 带回主会话，再追问一句（单行译文条放在引用块和输入行之间的空档里，别盖住输入）
note(S('N10') + 0.2, E('N10') + 0.3, '按 2：提醒带回主会话，标明是“旁路智能体的备注”', '', { y: 636 });
box(S('N10') + 0.6, E('N10') + 0.6, 54, 38, 770, 46);                    // “Here is a note offered by a side agent:”
note(S('N11') + 0.1, E('N11') + 0.5, '追问：这个键会不会过期？', '', { y: 636 });
// ═════════════════════════════ 演示 4：Claude 回答并改好
note(S('N12') + 0.1, E('N12') + 0.4, 'Claude：旁路智能体说得对，我现在就改', '', { y: 668 });
note(S('N13') + 0.1, E('N13') + 0.8, '改好了：每笔付款一个随机键，创建一次，每次重试都带着', '', { y: 668 });

// ═════════════════════════════ 收尾：演示的最后一个画面（Claude 改好、窗口缩回去），底下放开启命令
ovB(S('N22') + 0.1, TL.total - 0.05, p => {
  const el = at(p, null, null, null, null, 'cmd', { left: 0, right: 0, margin: '0 auto', width: 'max-content', top: 700 }, '<span class="p">/plugin</span> enable cc-plugin-you-should-know@builtin');
  return lt => show(el, lt, 0, { dy: 10 });
});

// ═════════════════════════════ 官方推文 / 官方文档 / 更新日志（页面录屏，高亮句子的位置是 capture_pages.py 量出来的）
pageShot('N04', 'N05', 'X_t1', [
  ['new plugin to Claude Code', S('N04') + 0.2, '官方推文：Claude Code 新增插件 You should know'],
  ["It scans Claude's output for important information you might miss", P('N05', '扫描'), '扫描 Claude 的输出，挑出你可能漏掉的重要信息'],
  ['to help keep you in the loop', P('N05', '让你跟得上'), '让你一直在状况内（keep you in the loop）']]);
pageShot('N14', 'N15', 'X_t2', [
  ['Read more about mods in our newest blog post', S('N14') + 0.2, '官方：想了解模组，看最新的博客'],
  ["is a mod that works by spinning off a sideagent to observe Claude's output", P('N15', '派出'), '它是个模组：派出一个旁路智能体（sideagent），观察 Claude 的输出']]);
// 官方文档的“内置模组表”：6 行，最后一行是它。画面按解说时刻往下滚到这一行，再逐句刷：说明 → 默认关闭 / 组织可用 → 开启命令 → 关闭 / 不能卸载
pageShot('N16', 'N20', 'Y_list', [
  ['cc-plugin-you-should-know', S('N16') + 1.0, '官方文档的内置模组表：现在一共 6 个，最后一行就是它'],
  ['Runs a side agent that watches your back while Claude works on longer tasks.', S('N17') + 0.3, '较长的任务里，旁路智能体在旁边替你盯着'],
  ['it shows you a note above the prompt', P('N17', '输入框上方'), '有你可能漏掉的，就在输入框上方留一条便条'],
  ['Disabled by default.', S('N18') + 0.2, '默认关闭'],
  ['if available for your org', P('N18', '你的组织'), '要看你的组织有没有开放'],
  ['/plugin enable cc-plugin-you-should-know@builtin', S('N19') + 0.4, '开启：/plugin enable cc-plugin-you-should-know@builtin'],
  ['@row:cc-plugin-you-should-know|Disable it in /plugin', S('N20') + 0.2, '关闭：在 /plugin 里 Disable'],
  ["You can't update or uninstall a built-in mod", P('N20', '不能卸载') - 0.4, '内置模组不能更新，也不能卸载']]);
pageShot('N21', 'N21', 'Y_cl287', [
  ['Added You should know, a built-in mod where a side agent watches your back', S('N21') + 0.2, '更新日志 2.1.287：加入 You should know（内置模组）'],
  ['(for first-party sessions with telemetry on)', P('N21', '第一方'), '前提：第一方会话、遥测开着（for first-party sessions with telemetry on）']]);
