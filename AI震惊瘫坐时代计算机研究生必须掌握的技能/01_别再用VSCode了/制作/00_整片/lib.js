// 工具和组件。基础部分（timer / mk / show / setSrc / frameBox / header）和第 02 期一样。
// ======================================================================= 基础
const TLD = window.TL, FPS = TLD.fps;
const SX = 790, SY = 40, SW = 1502, SB = 900;           // 版式 B 的演示区（下沿 900，下面留给字幕）
const RX = 1400, RW = 880;                             // 版式 A 的右侧要点区
const CAM = { A: { x: 120, y: 150, w: 1156, h: 666 }, P: { x: 48, y: 48, w: 696, h: 402 } };
const MOVE = 0.7, FIN = 0.45, FOUT = 0.3;
const CY0 = 330;                                       // 有时间线的画面：内容区从这里开始
window.__ERR = [];

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const easeIn = x => Math.pow(clamp(x), 3);
const easeIO = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const lerp = (a, b, x) => a + (b - a) * x;
const px = v => v + 'px';
const pad = (n, k) => String(n).padStart(k, '0');
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const PARA = {}; TLD.paras.forEach(p => PARA[p.id] = p);

function spoken(text) { return text.replace(/（[^（）]*）/g, ''); }
function units(text) {   // 和 build_timeline.py 的 units() 一样（先去掉不念的注释）
  let u = 0;
  for (const m of spoken(text).matchAll(/[A-Za-z][A-Za-z\-]*|\d|[一-鿿]|[，、：；]|[。？！]/g)) {
    const s = m[0];
    if (/^[A-Za-z]/.test(s)) u += 1.5; else if (/^\d$/.test(s)) u += 1.1;
    else if ('，、：；'.includes(s)) u += 0.9; else if ('。？！'.includes(s)) u += 1.6; else u += 1;
  }
  return u;
}
function timer(s) {
  const tm = {
    dur: s.end - s.start,
    p0: pid => PARA[pid].start - s.start,
    pe: pid => PARA[pid].start - s.start + PARA[pid].speech,
    at(pid, phrase, off = 0) {
      const p = PARA[pid], i = p.say.indexOf(phrase);
      if (i < 0) throw new Error(`「${phrase}」不在 ${pid}`);
      return p.start - s.start + units(p.say.slice(0, i)) / units(p.say) * p.speech + off;
    },
    ref(r, off = 0) { const k = r.indexOf(':'); return tm.at(r.slice(0, k), r.slice(k + 1), off); },
  };
  return tm;
}

function mk(parent, cls = '', style = {}, html = '', tag = 'div') {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  for (const [k, v] of Object.entries(style)) if (v !== undefined && v !== null) e.style[k] = typeof v === 'number' && !['opacity', 'zIndex', 'fontWeight', 'lineHeight', 'flex'].includes(k) ? px(v) : v;
  if (html) e.innerHTML = html;
  parent.appendChild(e);
  return e;
}
const at = (parent, x, y, w, h, cls = '', style = {}, html = '') => mk(parent, 'abs ' + cls, Object.assign({ left: x, top: y, width: w, height: h }, style), html);

// 出现 / 消失：t0 开始淡入，t1（可选）开始淡出
function show(el, lt, t0, o = {}) {
  const d = o.d ?? 0.4, dy = o.dy ?? 18, dx = o.dx ?? 0;
  const a = easeOut((lt - t0) / d);
  const b = o.t1 == null ? 1 : 1 - easeIn((lt - o.t1) / (o.d1 ?? 0.3));
  const v = Math.min(a, b);
  el.style.opacity = v;
  el.style.visibility = v < 0.002 ? 'hidden' : 'visible';
  el.style.transform = `translate(${dx * (1 - a)}px, ${dy * (1 - a)}px)` + (o.scale ? ` scale(${lerp(o.scale, 1, a)})` : '');
  return v;
}

const PENDING = new Set();
function setSrc(img, src) {
  if (img.dataset.src !== src) { img.dataset.src = src; img.src = src; PENDING.add(img); }
}
function image(parent, src, style = {}) { const i = mk(parent, '', style, '', 'img'); setSrc(i, src); return i; }
async function flush() {
  const arr = [...PENDING]; PENDING.clear();
  await Promise.all(arr.map(i => i.decode().catch(() => window.__ERR.push('图片加载失败 ' + i.dataset.src))));
}
// 带胶带的画框，返回 inner
function frameBox(parent, x, y, w, h, tape = true) {
  const f = at(parent, x, y, w, h, 'frame');
  if (tape) { mk(f, 'tape l'); mk(f, 'tape r'); }
  const inner = mk(f, 'inner');
  return { f, inner };
}
// 顶部标题：chip + 大标题
function header(root, chip, title) {
  const h = at(root, SX, SY + 6, SW, 130);
  mk(h, 'chip', {}, chip);
  const t = mk(h, 'h1', { marginTop: 14 }, title);
  return { el: h, title: t };
}
// 画面下方的出处（字幕带上面）
function srcNote(root, text, y = 866) { return at(root, SX, y, SW, 30, 'note', {}, text); }
// 按段落切换的内容组：在 t0 淡入，t1 淡出
function group(root, x = SX, y = CY0, w = SW, h = SB - CY0) { return at(root, x, y, w, h); }

// ======================================================================= App 图标
// 这台电脑上装着的 App 用它们自带的图标（icons.js）；其他的先画字母占位，等用户同意再换官方图标。
const ICON = {
  vscode: ['VS Code', '#0065A9', '#fff', 'VS'], copilot: ['GitHub Copilot', '#1F2328', '#fff', 'Co'],
  cursor: ['Cursor', '#0A0A0A', '#fff', 'Cu'], windsurf: ['Windsurf', '#0B4F4A', '#7FF5E0', 'Ws'],
  kiro: ['Kiro', '#6B3FD9', '#fff', 'Ki'], gemini: ['Gemini CLI', '#1B63E8', '#fff', 'Ge'],
  antigravity: ['Antigravity', '#202124', '#8AB4F8', 'AG'], devin: ['Devin Desktop', '#0F172A', '#E2E8F0', 'De'],
  openclaw: ['OpenClaw', '#E5412D', '#fff', 'OC'], doubao: ['豆包', '#2F6BFF', '#fff', '豆'],
  so: ['Stack Overflow', '#F48024', '#fff', 'SO'], csdn: ['CSDN', '#FC5531', '#fff', 'C'],
  mcp: ['MCP', '#1B1B1F', '#fff', 'MCP'], playwright: ['Playwright', '#2D4552', '#7DD87D', 'PW'],
  meta: ['Meta', '#0866FF', '#fff', 'M'], metr: ['METR', '#374151', '#fff', 'METR'],
  chroma: ['Chroma', '#FFCD2E', '#1B1B1F', 'Ch'], github: ['GitHub', '#1F2328', '#fff', 'GH'],
  claude: ['Claude', '#D97757', '#fff', 'Cl'], codex: ['Codex', '#111', '#fff', 'Cx'], chatgpt: ['ChatGPT', '#10A37F', '#fff', 'GPT'],
  openai: ['OpenAI', '#111', '#fff', 'AI'], trae: ['Trae', '#17181C', '#32F08C', 'Tr'], traework: ['TRAE Work', '#fff', '#111', 'TW'],
  workbuddy: ['WorkBuddy', '#10C08A', '#fff', 'WB'], chrome: ['Chrome', '#fff', '#1A73E8', 'Ch'],
};
function appIcon(parent, key, size, style = {}) {
  const f = (window.ICON_FILES || {})[key];
  const box = mk(parent, 'appicon', Object.assign({ width: size, height: size, flex: 'none' }, style));
  if (f && (window.ICON_ORIG || []).includes(key)) box.classList.add('orig');
  if (f) { const i = mk(box, '', { width: '100%', height: '100%', objectFit: 'contain', display: 'block' }, '', 'img'); setSrc(i, f); }
  else {
    // 没有官方图标（还没下载，或者商标规定不许用标志）：中性的名字牌，不仿品牌配色
    const d = ICON[key] || [key];
    const name = d[0].replace('GitHub ', '');
    Object.assign(box.style, { background: '#fff', color: '#374151', fontSize: px(Math.min(size * 0.22, size * 1.6 / Math.max(3, name.length))), fontWeight: 700, textAlign: 'center', lineHeight: 1.1, padding: '4px' });
    box.classList.add('ph');
    box.textContent = name;
  }
  return box;
}

// ======================================================================= 时间线（节点等距排开；日期、圆点、图标、名字、一行说明）
// nodes: [{ d: '2021.06', ic: ['copilot'], t1: 'Copilot 预览', t2: '在 VS Code 里补全', at: 秒 }]
function timeline(parent, nodes, o = {}) {
  const x = o.x ?? SX, y = o.y ?? 56, w = o.w ?? SW, n = nodes.length, cw = w / n;
  const root = at(parent, x, y, w, 270);
  const axis = mk(root, 'abs', { left: cw / 2, top: 62, width: w - cw, height: 4, background: '#E3E6EA', borderRadius: 2 });
  const first = Math.min(...nodes.map(n => n.at));
  const prog = mk(root, 'abs', { left: cw / 2, top: 62, width: 0, height: 4, background: 'var(--orange)', borderRadius: 2 });
  const fs = cw >= 290 ? 28 : cw >= 230 ? 25 : 23;
  const els = nodes.map((nd, i) => {
    const g = mk(root, 'abs', { left: cw * i, top: 0, width: cw, height: 270 });
    const date = mk(g, 'tl-date', {}, nd.d);
    const dot = mk(g, 'tl-dot');
    const icons = mk(g, 'tl-icons');
    nd.ic.forEach(k => appIcon(icons, k, nd.ic.length > 1 ? 58 : 70));
    const lines = (nd.t1.match(/<br>/g) || []).length + 1;
    mk(g, 'tl-t1', { fontSize: fs }, nd.t1);
    if (nd.t2) mk(g, 'tl-t2', { top: 178 + lines * fs * 1.22 }, nd.t2);
    return { g, date, dot, cx: cw * (i + 0.5), at: nd.at };
  });
  return {
    root,
    update(lt) {
      let cur = -1, maxX = cw / 2;
      els.forEach((e, i) => {
        show(e.g, lt, e.at, { d: 0.35, dy: 14, scale: 0.9 });
        if (lt >= e.at) { if (cur < 0 || e.at >= els[cur].at) cur = i; maxX = Math.max(maxX, e.cx); }
      });
      els.forEach((e, i) => {
        const c = i === cur;
        e.date.style.color = c ? 'var(--orange)' : 'var(--ink2)';
        e.dot.style.background = c ? 'var(--orange)' : '#9AA1AC';
        e.dot.style.boxShadow = c ? '0 0 0 7px rgba(255,79,26,.2)' : 'none';
      });
      const target = maxX - cw / 2;
      prog.style.width = px(Math.max(0, target));
      axis.style.opacity = clamp((lt - first + 0.3) / 0.4);
    },
  };
}

// ======================================================================= 窗口：终端、浏览器、编辑器（都是示意）
function win(parent, x, y, w, h, title = '', dark = false, o = {}) {
  const el = at(parent, x, y, w, h, 'win' + (dark ? ' dark' : ''));
  const bar = mk(el, 'bar', {}, `<i></i><i></i><i></i><b>${title}</b>`);
  const body = mk(el, 'wbody', { top: 44 });
  if (o.url != null) {
    bar.innerHTML = `<i></i><i></i><i></i><span class="url">${o.url}</span>`;
  }
  return { el, bar, body };
}
// 终端内容：lines = [[t, 文本, 类型, 每秒打字数], …]；类型：cmd（带 $ 提示符）/ in（带 › 提示符）/ out / ok / err / dim / ai / hi
function termRender(body, lines, lt, maxLines = 99) {
  const out = [];
  for (const [t, text, cls = 'out', cps = 0] of lines) {
    if (lt < t) break;
    let s = text, typing = false;
    if (cps) { const k = Math.floor((lt - t) * cps); if (k < text.length) { s = text.slice(0, k); typing = true; } }
    const pre = cls === 'cmd' ? '<span class="ps">$</span> ' : cls === 'in' ? '<span class="ps">›</span> ' : '';
    out.push(`<div class="l ${cls}">${pre}${cps ? esc(s) : s}${typing ? '<span class="tcaret"></span>' : ''}</div>`);
    if (typing) break;
  }
  body.innerHTML = out.slice(-maxLines).join('');
}
// 聊天气泡：msgs = [[t, 'me' | 'ai', html]]
function chatRender(body, msgs, lt, maxN = 99) {
  const vis = msgs.filter(m => lt >= m[0]);
  body.innerHTML = vis.slice(-maxN).map(([t, who, html]) => {
    const a = easeOut((lt - t) / 0.3);
    return `<div class="bub ${who}" style="opacity:${a};transform:translateY(${(1 - a) * 10}px)">${html}</div>`;
  }).join('');
}

// ======================================================================= 模拟鼠标：keys = [[t, x, y, 点击?]]
function cursor(parent) {
  const c = mk(parent, 'abs', { left: 0, top: 0, width: 34, height: 44, zIndex: 30, pointerEvents: 'none' },
    `<svg viewBox="0 0 24 32" width="34" height="44"><path d="M2 2 L2 26 L8 20 L12 30 L16 28 L12 18 L20 18 Z" fill="#111" stroke="#fff" stroke-width="2" stroke-linejoin="round"/></svg>`);
  const ring = mk(parent, 'abs', { width: 60, height: 60, marginLeft: -30, marginTop: -30, borderRadius: '50%', border: '4px solid var(--orange)', zIndex: 29, opacity: 0 });
  return {
    c, ring,
    update(lt, keys) {
      let x = keys[0][1], y = keys[0][2];
      for (let i = 0; i < keys.length; i++) {
        const [t, kx, ky] = keys[i];
        if (lt >= t) { x = kx; y = ky; const nx = keys[i + 1]; if (nx && lt < nx[0]) { const g = easeIO((lt - t) / Math.max(0.01, nx[0] - t)); x = lerp(kx, nx[1], g); y = lerp(ky, nx[2], g); } }
      }
      c.style.left = px(x); c.style.top = px(y);
      let r = 0, rx = x, ry = y;
      for (const [t, kx, ky, click] of keys) if (click && lt >= t && lt < t + 0.5) { r = (lt - t) / 0.5; rx = kx; ry = ky; }
      ring.style.opacity = r ? 1 - r : 0; ring.style.left = px(rx + 3); ring.style.top = px(ry + 3);
      ring.style.transform = `scale(${0.4 + r})`;
    },
  };
}

// ======================================================================= 条形图：rows = [{ label, v, color, at, text }]
function hbars(parent, x, y, rows, o = {}) {
  const lw = o.labelW ?? 300, bw = o.barW ?? 900, max = o.max ?? 100, rh = o.rowH ?? 76;
  const els = rows.map((r, i) => {
    const yy = y + i * rh;
    const l = at(parent, x, yy, lw, 50, '', { textAlign: 'right', font: `${r.bold ? 800 : 600} 32px 'Noto Sans SC'`, color: r.bold ? 'var(--ink)' : 'var(--ink2)', lineHeight: '50px' }, r.label);
    const b = at(parent, x + lw + 30, yy + 3, 0, 44, '', { borderRadius: 8, background: r.color || '#C9CED6' });
    const v = at(parent, x + lw + 30, yy, 400, 50, '', { font: "800 34px 'Space Grotesk','Noto Sans SC'", color: r.color || 'var(--gray)', lineHeight: '50px', whiteSpace: 'nowrap' }, r.text ?? String(r.v));
    return { l, b, v, r };
  });
  return {
    update(lt) {
      els.forEach(({ l, b, v, r }) => {
        const g = easeOut((lt - r.at) / 1.0);
        l.style.opacity = clamp((lt - r.at + 0.2) / 0.3);
        b.style.width = px(g * r.v / max * bw);
        v.style.left = px(x + lw + 30 + g * r.v / max * bw + 18);
        v.style.opacity = g;
      });
    },
  };
}

// ======================================================================= 折线（示意）：pts 是 0–1 的坐标，按 prog 画出来
function lineSvg(parent, x, y, w, h, pts, o = {}) {
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${(p[0] * w).toFixed(1)} ${((1 - p[1]) * h).toFixed(1)}`).join(' ');
  const el = at(parent, x, y, w, h, '', {}, `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="overflow:visible">
    <path d="${d}" pathLength="1" fill="none" stroke="${o.color || 'var(--orange)'}" stroke-width="${o.sw || 6}" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1 1" stroke-dashoffset="1"/></svg>`);
  const path = el.querySelector('path');
  return { el, set(prog) { path.setAttribute('stroke-dashoffset', String(1 - clamp(prog))); } };
}

// ======================================================================= 录屏播放器
// 按 timeline.json 里的剪辑表（build_timeline.py 的 RECS，已换算成去停顿版的秒数）把画面时间映射到录屏的帧。
// 某一段留的时间比片段长：按 1 倍速放完停在最后一帧；比片段短：加速。换段时交叉淡化 0.25 s。
function recPlayer(parent, type, x, y, w, h, o = {}) {
  const rec = TLD.recs[type];
  const fb = frameBox(parent, x, y, w, h, o.tape ?? false);
  fb.inner.style.background = '#111';
  const B = mk(fb.inner, 'recimg', {}, '', 'img'), A = mk(fb.inner, 'recimg', {}, '', 'img');
  const frame = tt => `media/rec/${rec.src}/f_${pad(Math.round(tt * FPS), 5)}.jpg`;
  let plan = [];
  const srcAt = (c, u) => { const span = c.n1 - c.n0, dur = Math.max(0.01, c.u1 - c.u0), sp = Math.max(1, span / dur); return Math.min(c.n1 - 1 / FPS, c.n0 + (u - c.u0) * sp); };   // 最后一帧是 n1 前一帧（片子正好在 n1 结束时没有第 n1×30 帧）
  return {
    fb, rec,
    plan(tm, t0, t1) {
      const cuts = rec.cuts.map(c => Object.assign({}, c, { len: c.n1 - c.n0 }));
      const st = cuts.map((c, i) => c.at ? tm.ref(c.at) : (i === 0 ? t0 : null));
      let i = 0;
      while (i < cuts.length) {
        let j = i + 1; while (j < cuts.length && st[j] == null) j++;
        const a = st[i], b = j < cuts.length ? st[j] : t1, tot = cuts.slice(i, j).reduce((s, c) => s + c.len, 0);
        let acc = a;
        for (let k = i; k < j; k++) { st[k] = acc; acc += (b - a) * cuts[k].len / tot; }
        i = j;
      }
      plan = cuts.map((c, k) => Object.assign(c, { u0: st[k], u1: k + 1 < cuts.length ? st[k + 1] : t1 }));
      return plan;
    },
    cutAt(lt) { let k = 0; for (let i = 0; i < plan.length; i++) if (lt >= plan[i].u0) k = i; return k; },
    update(lt) {
      const k = this.cutAt(lt), c = plan[k];
      const u = Math.max(lt, c.u0);
      setSrc(A, frame(srcAt(c, u)));
      const xf = k > 0 ? clamp((u - c.u0) / 0.25) : 1;
      if (xf < 1) { const p = plan[k - 1]; setSrc(B, frame(srcAt(p, p.u1))); B.style.opacity = 1; A.style.opacity = xf; }
      else { A.style.opacity = 1; B.style.opacity = 0; }
      return k;
    },
  };
}

// 画框里左上角的标签
function frameLab(inner, html, o = {}) { return mk(inner, 'abs', Object.assign({ left: 16, top: 14, zIndex: 3 }, o), `<span class="lab" style="position:static">${html}</span>`); }

// 编号小圆 + 文字（版式 A 右侧要点）
function bullet(parent, n, html, style = {}) { return mk(parent, 'bl', style, `<span class="num">${n}</span><span>${html}</span>`); }

// ======================================================================= 白板版（2026-09-30 用户：“这里的视频我也想使用手写版本的”）
// 画面整体比声音早 LEAD 秒（engine.js：场景按声音时间选，场景里按 lv = lt + LEAD 求值；组件时间都按声音写）。
// 同一场景里翻页用 tm.flip(这一页最后一段)：这一页在那段说完前 0.15 s 擦掉（声音时刻），下一页从 in 开始写（同原LAI如此 c.flip）。
const LEAD = 1.0;
function flipOf(tm, pid) { const out = tm.pe(pid) + LEAD - 0.15; return { out, in: out + 0.3 }; }
// 一页：铺满画布的层（手写墨迹和印刷元素放在一起，整页一起淡出）
function layer(root) { return mk(root, 'abs', { left: 0, top: 0, width: 2340, height: 1080 }); }
// 印刷小字（白板上只留小字：小标签、补充说明、出处）
function bNote(parent, x, y, text, o = {}) { return mk(parent, 'abs bNote', Object.assign({ left: x, top: y }, o), text); }
function bKick(parent, x, y, text, o = {}) { return mk(parent, 'abs bKick', Object.assign({ left: x, top: y }, o), text); }
// 给卡片 / 窗口 / 录屏贴两条胶带（左上、右下，同原LAI如此 c.tape）
function tape(el, k = 0) {
  const w = parseFloat(el.style.width) || el.offsetWidth || 400, h = parseFloat(el.style.height) || el.offsetHeight || 240;
  mk(el, 'btape', { left: -30, top: -12, width: 110, height: 30, transform: `rotate(${-38 + (k % 3) * 3}deg)` });
  mk(el, 'btape', { left: w - 80, top: h - 18, width: 110, height: 30, transform: `rotate(${-38 - (k % 2) * 3}deg)` });
  return el;
}
// 写字的时间窗：从 at 开始，按字数给时间（约 0.28 s 一个字，最少 0.6 s，最多 max），不越过 next
function wwin(at, text, next = null, max = 3.0) {
  const n = [...String(text).replace(/<[^>]+>/g, '')].filter(ch => ch.trim()).length;
  let u = at + Math.min(max, Math.max(0.6, n * 0.28));
  if (next != null) u = Math.min(u, Math.max(at + 0.35, next - 0.1));
  return u;
}
// 手写标题：居中，写完划黄色波浪线；kicker 是橙色印刷小字（放在标题上面）
function hTitle(H, L, text, o) {
  const size = o.size || 60, at = o.at, until = o.until || wwin(at, text, o.next, 2.4);
  const it = H.html(text, { x: o.x, y: o.y, size, align: o.align || 'center', maxW: o.maxW || 1400, at, until, parent: L, seed: 'title' });
  if (o.underline !== false) H.underline({ x0: it.x0 - 6, x1: it.x1 + 10, y: it.y1 + 16, at: it.t1 + 0.05, dur: 0.35, parent: L });
  if (o.kicker && o.sh) o.sh(bKick(L, o.x - 500, it.y1 + 38, o.kicker, { width: 1000, textAlign: 'center' }), at + 0.3);   // 橙色小字在标题下面（同原LAI如此）
  return it;
}
// 编号要点：橙色手写编号 + 黑色手写字；sub 是印刷小字（跟在后面）
function hPoint(H, L, n, html, x, y, o) {
  const size = o.size || 44, at = o.at;
  const num = H.text({ text: String(n), x, y, size: size * 1.05, color: H.ACCENT, at, until: at + 0.2, parent: L, seed: 'num' + n });
  const it = H.html(html, { x: x + size * 0.95, y, size, at: at + 0.25, until: o.until || wwin(at + 0.25, html, o.next), maxW: o.maxW, parent: L, seed: 'pt' + n + y });
  if (o.sub) { const e = bNote(L, it.x1 + 18, y - 14, o.sub); o.shows && o.shows.push([e, it.t1]); }
  return it;
}
// 手写的时间线：轴线、每个节点的日期（橙）、圆点、图标（图片）、名字（黑）、一行说明（印刷小字）
function hTimeline(H, L, nodes, o = {}) {
  const x = o.x ?? SX, y = o.y ?? 60, w = o.w ?? SW, n = nodes.length, cw = w / n;
  const first = Math.min(...nodes.map(nd => nd.at));
  H.line({ x0: x + cw * 0.5 - 20, y0: y + 62, x1: x + w - cw * 0.5 + 20, y1: y + 62, at: first - 0.3, dur: 0.5, color: '#B8BDC6', w: 5, parent: L });
  const fs = cw >= 290 ? 30 : cw >= 230 ? 27 : 25;
  const icons = [];
  nodes.forEach((nd, i) => {
    const cx = x + cw * (i + 0.5), at0 = nd.at;
    H.text({ text: nd.d, x: cx, y: y + 26, size: 34, align: 'center', color: H.ACCENT, at: at0, until: at0 + 0.45, maxW: cw - 16, parent: L, seed: 'd' + i });
    H.line({ x0: cx - 1, y0: y + 62, x1: cx + 1, y1: y + 62, at: at0 + 0.1, dur: 0.06, color: H.INK, w: 18, parent: L });
    const row = mk(L, 'abs', { left: cx - cw / 2, top: y + 92, width: cw, height: 76, display: 'flex', justifyContent: 'center', gap: '10px' });
    nd.ic.forEach(k => appIcon(row, k, nd.ic.length > 1 ? 62 : 80));
    icons.push([row, at0 + 0.2]);
    const lines = nd.t1.split('<br>');
    lines.forEach((t, j) => H.text({ text: t, x: cx, y: y + 196 + j * fs * 1.2, size: fs, align: 'center', maxW: cw - 14, at: at0 + 0.35 + j * 0.5, until: wwin(at0 + 0.35 + j * 0.5, t, null, 1.6), parent: L, seed: 'n' + i + j }));
    if (nd.t2) { const e = bNote(L, cx - cw / 2 + 4, y + 196 + lines.length * fs * 1.2 - 4, nd.t2, { width: cw - 8, textAlign: 'center', whiteSpace: 'normal', fontSize: 20 }); icons.push([e, at0 + 0.8]); }
  });
  return { update(lv) { icons.forEach(([e, t]) => show(e, lv, t, { d: 0.3, dy: 10, scale: 0.9 })); } };
}

// 登记淡入淡出：sh(el, t0, o) 记下来，sh.run(lv) 每帧调用
function Shows() { const a = []; const f = (el, t0, o) => { a.push([el, t0, o || {}]); return el; }; f.run = lv => a.forEach(([e, t, o]) => show(e, lv, t, o)); return f; }
// 一页：层 + 淡入淡出（dy 0）
function page(root, sh, tIn, tOut) { const L = layer(root); sh(L, tIn, { t1: tOut, dy: 0, d: 0.25 }); return L; }
