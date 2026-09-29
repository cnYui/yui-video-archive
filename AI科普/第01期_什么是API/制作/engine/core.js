/* 第 1 期「什么是 API」正片画面引擎 — 核心：时间轴工具、轨道系统、全局层（背景/角色/字幕/进度条/角标/目录）。
 * 数据契约见 ../PRODUCTION.md：window.__DATA__ = timeline.json；window.DURATION；window.renderAt(t)。
 * 所有时刻都从 __DATA__ 的 segments / gaps / scenes 推出来，不写死秒数；不使用真实时间。 */
(function () {
  'use strict';
  const D = window.__DATA__ || null;
  const A = window.__ASSETS__ || { anims: null, bg: {}, spriteBase: '../assets/sprites/' };
  window.DURATION = D && D.main_duration > 0 ? D.main_duration : 1;
  window.__READY__ = false;

  const W = 1920, H = 1080;
  const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
  const lerp = (a, b, p) => a + (b - a) * p;
  const E = {
    lin: x => x,
    out: x => 1 - Math.pow(1 - x, 3),
    inOut: x => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
    sine: x => -(Math.cos(Math.PI * x) - 1) / 2,
  };

  function el(tag, cls, parent, html) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    if (parent) parent.appendChild(e);
    return e;
  }
  function css(e, o) { for (const k in o) e.style[k] = typeof o[k] === 'number' && !/opacity|zIndex|fontWeight/.test(k) ? o[k] + 'px' : o[k]; return e; }
  function box(tag, cls, parent, x, y, w, h, html) {
    const e = el(tag, cls, parent, html);
    e.style.position = 'absolute';
    if (x != null) e.style.left = x + 'px';
    if (y != null) e.style.top = y + 'px';
    if (w != null) e.style.width = w + 'px';
    if (h != null) e.style.height = h + 'px';
    return e;
  }
  const SVGNS = 'http://www.w3.org/2000/svg';
  function svg(parent, x, y, w, h, inner) {
    const s = document.createElementNS(SVGNS, 'svg');
    s.setAttribute('width', w); s.setAttribute('height', h); s.setAttribute('viewBox', `0 0 ${w} ${h}`);
    s.style.position = 'absolute'; s.style.left = x + 'px'; s.style.top = y + 'px'; s.style.overflow = 'visible';
    s.innerHTML = inner || '';
    parent.appendChild(s);
    return s;
  }
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // ---------------------------------------------------------------- timeline helpers
  const SC = {};
  const SEGS = D ? D.segments.slice().sort((a, b) => a.start - b.start) : [];
  const GAPS = D ? D.gaps.slice().sort((a, b) => a.start - b.start) : [];
  if (D) {
    for (const s of D.scenes) SC[s.id] = Object.assign({}, s, { segs: [], gaps: [] });
    for (const s of SEGS) if (SC[s.scene]) SC[s.scene].segs.push(s);
    for (const g of GAPS) if (SC[g.scene]) SC[g.scene].gaps.push(g);
  }
  function seg(sid, i) {
    const s = SC[sid];
    if (!s || !s.segs.length) return { start: 0, end: 0.1, lines: [], text: '' };
    return s.segs[Math.max(0, Math.min(i, s.segs.length - 1))];
  }
  /** time at which `phrase` starts being spoken inside segment sg (via its subtitle lines); fallback: fraction of the segment */
  function ph(sg, phrase, frac = 0) {
    const lines = sg.lines || [];
    let acc = ''; const spans = [];
    for (const ln of lines) { spans.push([acc.length, acc.length + ln.text.length, ln]); acc += ln.text; }
    const i = phrase ? acc.indexOf(phrase) : -1;
    if (i < 0) return sg.start + (sg.end - sg.start) * frac;
    for (const [a, b, ln] of spans) if (i >= a && i < b) return ln.start + (ln.end - ln.start) * (i - a) / Math.max(1, b - a);
    return sg.start + (sg.end - sg.start) * frac;
  }
  /** the pure-visual gap right after segment sg (if any) */
  function gapAfter(sg) {
    for (const g of GAPS) if (g.start >= sg.end - 0.01 && g.start <= sg.end + 0.6) return g;
    return null;
  }
  function lastGap(sid) { const s = SC[sid]; return s && s.gaps.length ? s.gaps[s.gaps.length - 1] : null; }
  const fmt = x => `${Math.floor(x / 60)}:${String(Math.floor(x % 60)).padStart(2, '0')}`;

  // ---------------------------------------------------------------- track system
  // A track owns one element and a time-sorted list of steps "from t, move to props over d seconds".
  // Evaluation is a pure function of t (seekable in any order).
  const DEF = { o: 1, x: 0, y: 0, s: 1 };
  class Track {
    constructor(el, init, fx) {
      this.el = el; this.init = Object.assign({}, DEF, init); this.steps = []; this.fx = fx || null;
      this.st = {}; this.res = {}; this._o = null; this._tf = null; this._w = null; this._hl = null; this._d = null;
      this.band = el && el.querySelector ? el.querySelector(':scope > .band') : null;
    }
    to(t, p, d = 0.35, e = E.out) { if (isFinite(t)) this.steps.push({ t, p, d, e }); return this; }
    set(t, p) { return this.to(t, p, 0); }
    in(t, d = 0.35, extra) { return this.to(t, Object.assign({ o: 1, y: 0 }, extra || {}), d); }
    out(t, d = 0.3, extra) { return this.to(t, Object.assign({ o: 0 }, extra || {}), d, E.sine); }
    finalize() {
      this.steps.sort((a, b) => a.t - b.t);
      for (const s of this.steps) for (const k in s.p) if (!(k in this.init)) this.init[k] = 0;
      for (const k in this.init) this.st[k] = { v0: 0, v1: 0, t0: 0, d: 0, e: E.lin };
    }
    eval(t) {
      const st = this.st, init = this.init;
      for (const k in st) { const a = st[k]; a.v0 = a.v1 = init[k]; a.t0 = -1e9; a.d = 0; }
      for (const s of this.steps) {
        if (s.t > t) break;
        for (const k in s.p) { const a = st[k]; const v = val(a, s.t); a.v0 = v; a.v1 = s.p[k]; a.t0 = s.t; a.d = s.d; a.e = s.e; }
      }
      for (const k in st) this.res[k] = val(st[k], t);
      apply(this, this.res);
    }
  }
  function val(a, t) {
    if (a.d <= 0 || t >= a.t0 + a.d) return a.v1;
    if (t <= a.t0) return a.v0;
    return a.v0 + (a.v1 - a.v0) * a.e((t - a.t0) / a.d);
  }
  function apply(tr, p) {
    const e = tr.el;
    if (e) {
      const o = Math.round(p.o * 1000) / 1000;
      if (o !== tr._o) { e.style.opacity = o; e.style.visibility = o <= 0.001 ? 'hidden' : ''; tr._o = o; }
      const tf = (p.x || p.y ? `translate(${p.x.toFixed(2)}px,${p.y.toFixed(2)}px)` : '') + (p.s !== 1 ? ` scale(${p.s.toFixed(4)})` : '');
      if (tf !== tr._tf) { e.style.transform = tf; tr._tf = tf; }
      if ('w' in p) { const w = p.w.toFixed(1); if (w !== tr._w) { e.style.width = w + 'px'; tr._w = w; } }
      if ('hl' in p && tr.band) { const h = Math.round(p.hl * 1000) / 1000; if (h !== tr._hl) { tr.band.style.opacity = h; tr._hl = h; } }
    }
    if (tr.fx) tr.fx(p, tr);
  }

  // ---------------------------------------------------------------- engine state
  const ENG = window.ENG = {
    D, A, W, H, SC, SEGS, GAPS, E, clamp, lerp, el, css, box, svg, esc, seg, ph, gapAfter, lastGap, fmt, Track,
    builders: [], scenes: [], global: [],
  };
  ENG.scene = (id, fn) => ENG.builders.push({ id, fn });
  /** moment the three question cards fly into the top-right TOC (end of S02's last line) */
  ENG.tocInTime = () => { const s = seg('S02', 99); return Math.max(s.start + 0.8, s.end - 0.75); };
  ENG.T = (list, e, init, fx) => { const tr = new Track(e, init, fx); list.push(tr); return tr; };

  let stage, subsBox, subStroke, subFill, charCv, charCtx, barP, pickEl, barTag, fadeEl, bgLayer, bgCv = {};

  // ---------------------------------------------------------------- loading
  function loadImg(src) {
    return new Promise(res => { const i = new Image(); i.onload = () => res(i); i.onerror = () => res(null); i.src = src; });
  }
  const FRAMES = {};  // anim -> [{img, dur}]
  async function loadAssets() {
    const fontJobs = [
      '700 44px "Noto Sans SC"', '900 80px "Noto Sans SC"', '500 22px "Noto Sans SC"', '800 30px "Noto Sans SC"',
      '500 16px "KuaiLe Han"', '700 22px "JetBrains Mono"', '500 22px "JetBrains Mono"', '800 150px "JetBrains Mono"',
    ].map(f => document.fonts.load(f, 'API 接口 sk-•… 0:33').catch(() => null));
    const jobs = [...fontJobs];
    if (A.anims && A.anims.anims) {
      for (const [name, a] of Object.entries(A.anims.anims)) {
        FRAMES[name] = a.frames.map((f, i) => ({ img: null, dur: a.durations[i], src: A.spriteBase + f }));
        FRAMES[name].forEach(fr => jobs.push(loadImg(fr.src).then(img => { fr.img = img; })));
      }
    }
    const bgImgs = {};
    for (const k of ['bg1', 'bg2']) if (A.bg && A.bg[k]) jobs.push(loadImg(A.bg[k]).then(img => { bgImgs[k] = img; }));
    await Promise.all(jobs);
    await document.fonts.ready;
    return bgImgs;
  }

  // ---------------------------------------------------------------- background
  function paintBg(cv, key, img) {
    const g = cv.getContext('2d');
    g.fillStyle = '#1B2340'; g.fillRect(0, 0, W, H);
    if (img) {
      // brighter artwork (e.g. a single episode background) can ask for more dimming via the manifest
      g.save(); g.filter = `blur(${A.bgBlur || 6}px)`; g.globalAlpha = A.bgAlpha || 0.45;
      const iw = img.naturalWidth, ih = img.naturalHeight, sc = Math.max(W / iw, H / ih) * 1.02;
      g.drawImage(img, (W - iw * sc) / 2, (H - ih * sc) / 2, iw * sc, ih * sc);
      g.restore();
    } else {
      // placeholder: soft dark gradient (warm for bg1 / cool for bg2) until the real stills exist
      const warm = key === 'bg1';
      let gr = g.createRadialGradient(1250, 360, 60, 1250, 360, 1300);
      gr.addColorStop(0, warm ? 'rgba(150,96,70,.30)' : 'rgba(80,130,190,.28)');
      gr.addColorStop(1, 'rgba(27,35,64,0)');
      g.fillStyle = gr; g.fillRect(0, 0, W, H);
      gr = g.createLinearGradient(0, 0, 0, H);
      gr.addColorStop(0, 'rgba(255,255,255,.03)'); gr.addColorStop(1, 'rgba(0,0,0,.18)');
      g.fillStyle = gr; g.fillRect(0, 0, W, H);
    }
    const vg = g.createRadialGradient(W / 2, H / 2, H * 0.42, W / 2, H / 2, H * 1.05);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,.15)');
    g.fillStyle = vg; g.fillRect(0, 0, W, H);
  }
  function buildBg(bgImgs) {
    bgLayer = el('div', 'layer', stage); bgLayer.id = 'bg';
    for (const k of ['bg1', 'bg2']) {
      const cv = el('canvas', '', bgLayer); cv.width = W; cv.height = H;
      paintBg(cv, k, bgImgs[k] || null); bgCv[k] = cv;
    }
  }
  const BGX = 0.6;  // crossfade seconds
  function bgWeight2(t) {  // weight of bg2 layer (bg1 below is always opaque)
    const sc = D.scenes;
    let w = 0;
    for (let i = 0; i < sc.length; i++) {
      const s = sc[i];
      const isB = s.bg === 'bg2' ? 1 : 0;
      if (t >= s.start && t < s.end) w = isB;
    }
    for (let i = 1; i < sc.length; i++) {
      const b = sc[i].start, pa = sc[i - 1].bg === 'bg2' ? 1 : 0, pb = sc[i].bg === 'bg2' ? 1 : 0;
      if (pa !== pb && Math.abs(t - b) < BGX / 2) w = lerp(pa, pb, E.sine(clamp((t - b + BGX / 2) / BGX)));
    }
    return w;
  }

  // ---------------------------------------------------------------- character
  const SPEAK = [], REACH = [];
  let charKey = '';
  function buildChar() {
    el('div', '', stage).id = 'charShadow';
    charCv = el('canvas', '', stage); charCv.id = 'char'; charCv.width = 64; charCv.height = 64;
    charCtx = charCv.getContext('2d'); charCtx.imageSmoothingEnabled = false;
    for (const s of SEGS) {
      SPEAK.push([s.start, s.end]);
      if (s.pose !== 'reach') continue;
      // the raise goes with the key-point card; where the台本 puts that card mid-segment, anchor on its phrase
      const t0 = REACH_AT[s.id] ? Math.max(s.start, ph(s, REACH_AT[s.id], 0)) : s.start;
      REACH.push([t0, Math.min(s.end, t0 + 1.2)]);
    }
    REACH.sort((a, b) => a[0] - b[0]);
  }
  const REACH_AT = { 'S05-26': '平台靠它' };  // S05-26: 【抬手】要点卡「平台用 Key 确认」 appears at 「平台靠它确认三件事」
  function inRanges(list, t) {
    let lo = 0, hi = list.length - 1;
    while (lo <= hi) { const m = (lo + hi) >> 1; if (list[m][1] <= t) lo = m + 1; else if (list[m][0] > t) hi = m - 1; else return true; }
    return false;
  }
  function frameAt(frames, ms) {
    let total = 0; for (const f of frames) total += f.dur;
    let x = ((ms % total) + total) % total;
    for (let i = 0; i < frames.length; i++) { if (x < frames[i].dur) return i; x -= frames[i].dur; }
    return frames.length - 1;
  }
  function mouthAt(t) {
    if (D.mouth && D.mouth.length) {
      const i = Math.max(0, Math.min(D.mouth.length - 1, Math.round(t * (D.fps || 30))));
      return D.mouth[i] | 0;
    }
    return inRanges(SPEAK, t) ? (Math.floor(t * 8) % 2 ? 2 : 1) : 0;
  }
  function drawPlaceholder(g, pose, mouth, walkPhase) {
    g.clearRect(0, 0, 64, 64);
    g.fillStyle = '#3F63C8'; g.fillRect(16, 6, 32, 30);           // hair
    g.fillStyle = '#F2D2B6'; g.fillRect(20, 14, 24, 20);          // face
    g.fillStyle = '#141414'; g.fillRect(24, 20, 4, 3); g.fillRect(36, 20, 4, 3);
    g.fillStyle = '#7A2E2E'; g.fillRect(29, 28, 6, mouth === 0 ? 1 : mouth === 1 ? 2 : 3);
    g.fillStyle = '#EDEAE3'; g.fillRect(20, 36, 24, 10);          // shirt
    g.fillStyle = '#2E3A78'; g.fillRect(19, 46, 26, 9);           // skirt
    g.fillStyle = '#EDEAE3';
    if (pose === 'reach') g.fillRect(44, 38, 12, 4); else g.fillRect(16, 37, 4, 9);
    g.fillRect(44, pose === 'reach' ? 42 : 37, 4, pose === 'reach' ? 4 : 9);
    const lift = walkPhase ? 1 : 0;
    g.fillStyle = '#6B3B24'; g.fillRect(24, 55 - lift, 6, 7); g.fillRect(34, 55 - (1 - lift), 6, 7);
  }
  function renderChar(t) {
    const wi = D.walk_in || { start: 0, end: 0 };
    let anim, ms, x = 0, pose = 'idle';
    const m = mouthAt(t);
    if (t < wi.end) {
      const p = clamp((t - wi.start) / Math.max(0.01, wi.end - wi.start));
      x = lerp(-400, 0, 1 - Math.pow(1 - p, 1.25));
      anim = 'walk'; ms = (t - wi.start) * 1000; pose = 'walk';
    } else {
      pose = inRanges(REACH, t) ? 'reach' : 'idle';
      anim = `${pose}_m${m}`; ms = t * 1000;
    }
    const tf = x ? `translateX(${x.toFixed(1)}px)` : '';
    if (charCv._tf !== tf) { charCv.style.transform = tf; charCv._tf = tf; }
    let key;
    if (FRAMES[anim] && FRAMES[anim].length) {
      const i = frameAt(FRAMES[anim], ms); key = anim + i;
      if (key !== charKey) {
        const fr = FRAMES[anim][i];
        charCtx.clearRect(0, 0, 64, 64);
        if (fr.img) charCtx.drawImage(fr.img, 0, 0);
        charKey = key;
      }
    } else {
      const wp = pose === 'walk' ? Math.floor(ms / 145) % 2 : 0;
      key = `ph${pose}${m}${wp}`;
      if (key !== charKey) { drawPlaceholder(charCtx, pose, pose === 'walk' ? 0 : m, wp); charKey = key; }
    }
    ENG.charKey = charKey;  // exposed for tests (the canvas itself is tainted by file:// images)
  }

  // ---------------------------------------------------------------- subtitles
  const TERMS = ['platform.deepseek.com', 'previous_response_id', 'content_block_delta', 'Chat Completions', 'anthropic-version',
    '/chat/completions', 'message_start', 'message_stop', 'Authorization', '/v1/messages', 'instructions', '/responses',
    'x-api-key', 'max_tokens', 'Responses', 'Messages', 'assistant', 'tool_use', 'messages', 'API keys', 'API Key', 'API key', '接口文档',
    'choices', 'content', 'output', 'stream', 'system', 'input', 'model', 'HTTP', 'JSON', 'text', 'true', 'user', 'SSE', 'API', '密钥', 'sk'];
  const TERM_RE = new RegExp('(?<![A-Za-z_\\-/.])(' + TERMS.map(s => s.replace(/[.*+?^${}()|[\]\\\/]/g, '\\$&')).join('|') + ')(?![A-Za-z_\\-])', 'g');
  const SUBS = [];
  let subIdx = -2;
  function buildSubs() {
    subsBox = el('div', '', stage); subsBox.id = 'subs';
    subStroke = el('div', 's stroke', subsBox); subFill = el('div', 's fill', subsBox);
    const probe = el('span', '', stage); css(probe, { position: 'absolute', left: -9999, top: 0, whiteSpace: 'nowrap', font: '700 44px "Noto Sans SC"', letterSpacing: '.02em' });
    for (const sg of SEGS) {
      let cur = null;
      for (const ln of sg.lines || []) {
        // re-join words that the timeline builder hard-wrapped at 18 chars (e.g. "Application Progra" + "mming Interface。")
        if (cur && cur.text.length >= 18 && /[A-Za-z0-9_.\-]$/.test(cur.text) && /^[A-Za-z0-9_.\-]/.test(ln.text)) {
          cur.text += ln.text; cur.end = ln.end;
        } else { cur = { text: ln.text, start: ln.start, end: ln.end }; SUBS.push(cur); }
      }
    }
    SUBS.sort((a, b) => a.start - b.start);
    for (let i = 0; i < SUBS.length; i++) {
      const s = SUBS[i], nx = SUBS[i + 1];
      if (nx && nx.start - s.end > 0 && nx.start - s.end <= 0.3) s.end = nx.start;   // no flicker across the 0.25 s breath
      probe.textContent = s.text;
      const w = probe.offsetWidth;
      s.fs = w > 1380 ? Math.max(32, Math.floor(44 * 1380 / w)) : 44;
      s.html = esc(s.text).replace(TERM_RE, '<span class="t">$1</span>');
    }
    probe.remove();
  }
  function renderSubs(t) {
    let lo = 0, hi = SUBS.length - 1, k = -1;
    while (lo <= hi) { const m = (lo + hi) >> 1; if (SUBS[m].start <= t) { k = m; lo = m + 1; } else hi = m - 1; }
    if (k >= 0 && t >= SUBS[k].end) k = -1;
    if (k !== subIdx) {
      subIdx = k;
      if (k < 0) { subStroke.innerHTML = ''; subFill.innerHTML = ''; }
      else {
        const s = SUBS[k];
        subStroke.innerHTML = s.html; subFill.innerHTML = s.html;
        const fs = s.fs + 'px', top = ((44 - s.fs) * 0.94) + 'px';
        subStroke.style.fontSize = subFill.style.fontSize = fs;
        subStroke.style.top = subFill.style.top = top;
      }
    }
  }

  // ---------------------------------------------------------------- chapter bar (Bocchi the Rock! palette)
  const BAR_COLORS = ['#F2A0BD', '#F6C945', '#4A6FD0', '#E2463F'];
  const BM = 6;
  let barX, chap = [], curChap = -2;
  function hexA(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
  function buildBar() {
    const total = D.total_duration;
    barX = tt => BM + (W - 2 * BM) * clamp(tt / total);
    el('div', '', stage).id = 'barShade';
    const bar = el('div', '', stage); bar.id = 'bar';
    const U = el('div', 'layer', bar); U.id = 'barU'; css(U, { height: 80 });
    barP = el('div', '', bar); barP.id = 'barP';
    const probe = el('span', 'bLab', stage); css(probe, { position: 'absolute', left: -9999, top: 0, whiteSpace: 'nowrap' });
    const measure = (txt, fs) => { probe.style.fontSize = fs + 'px'; probe.textContent = txt; return probe.offsetWidth; };
    D.chapters.forEach((c, i) => {
      const x0 = barX(c.start), x1 = barX(c.end), col = BAR_COLORS[i % 4];
      const bl = x0 + 2, bw = Math.max(4, x1 - x0 - 4);
      const bu = box('div', 'bBlk', U, bl, null, bw); bu.style.background = hexA(col, 0.46);
      const bp = box('div', 'bBlk', barP, bl, null, bw); bp.style.background = col;
      const full = `${fmt(c.start)}–${fmt(c.end)} ${c.title}`;
      const cands = [[full, 16], [full, 15], [full, 14], [c.title, 15], [c.title, 13], [String(i + 1), 14]].map(([t, f]) => ({ t, f, w: measure(t, f) }));
      chap.push({ c, bu, bp, full, x0: bl, x1: bl + bw, cx: bl + bw / 2, cands, lv: 0 });
    });
    probe.remove();
    // 1-D label layout: centre each label on its chapter, push neighbours apart (gap 12 px), and shorten a label
    // (smaller font -> title only -> number) only when it can no longer overlap its own chapter enough.
    for (let iter = 0; iter < 40; iter++) {
      const L = chap.map(ch => { const cd = ch.cands[ch.lv]; return { w: cd.w, x: ch.cx - cd.w / 2 }; });
      for (let pass = 0; pass < 30; pass++) {
        for (let i = 0; i < L.length - 1; i++) {
          const ov = L[i].x + L[i].w + 12 - L[i + 1].x;
          if (ov > 0) { L[i].x -= ov / 2; L[i + 1].x += ov / 2; }
        }
        L[0].x = Math.max(6, L[0].x); const z = L[L.length - 1]; z.x = Math.min(W - 6 - z.w, z.x);
        for (let i = 1; i < L.length; i++) L[i].x = Math.max(L[i].x, L[i - 1].x + L[i - 1].w + 12);
        for (let i = L.length - 2; i >= 0; i--) L[i].x = Math.min(L[i].x, L[i + 1].x - 12 - L[i].w);
      }
      let worst = -1, worstBw = 1e9;
      chap.forEach((ch, i) => {
        const ov = Math.min(ch.x1, L[i].x + L[i].w) - Math.max(ch.x0, L[i].x);
        // at least 60 % of the label must sit over its own chapter, and its centre inside the chapter
        const need = 0.6 * Math.min(L[i].w, Math.max(ch.x1 - ch.x0, 0.6 * L[i].w)), mid = L[i].x + L[i].w / 2;
        const bad = ov < need - 0.5 || mid < ch.x0 || mid > ch.x1;
        if (bad && ch.lv < ch.cands.length - 1 && ch.x1 - ch.x0 < worstBw) { worst = i; worstBw = ch.x1 - ch.x0; }
      });
      chap.forEach((ch, i) => { ch.lx = L[i].x; });
      if (worst < 0) break;
      chap[worst].lv++;
    }
    chap.forEach(ch => {
      const cd = ch.cands[ch.lv];
      ch.lab = box('div', 'bLab', bar, ch.lx, null, Math.ceil(cd.w) + 2); ch.lab.textContent = cd.t; ch.lab.style.fontSize = cd.f + 'px';
      ch.abbrev = cd.t !== ch.full;
    });
    pickEl = svg(bar, 0, 45, 24, 30,
      '<path d="M12 28 C 7 22 2 14 2 8 C 2 3 6 1.5 12 1.5 C 18 1.5 22 3 22 8 C 22 14 17 22 12 28 Z" fill="#EDEAE3" stroke="#141414" stroke-width="2.5" stroke-linejoin="round"/>' +
      '<path d="M8 8 L 16 8" stroke="#FF4F1A" stroke-width="2.4" stroke-linecap="round"/>');
    pickEl.id = 'pick';
    barTag = el('div', '', bar); barTag.id = 'barTag'; barTag.style.visibility = 'hidden';
  }
  function renderBar(t) {
    const tt = (D.intro || 0) + t, px = barX(tt);
    const w = px.toFixed(1);
    if (barP._w !== w) { barP.style.width = w + 'px'; barP._w = w; }
    const tf = `translateX(${(px - 12).toFixed(1)}px)`;
    if (pickEl._tf !== tf) { pickEl.style.transform = tf; pickEl._tf = tf; }
    let k = chap.length - 1;
    for (let i = 0; i < chap.length; i++) if (tt < chap[i].c.end) { k = i; break; }
    if (k !== curChap) {
      chap.forEach((ch, i) => { const on = i === k; ch.bu.classList.toggle('cur', on); ch.bp.classList.toggle('cur', on); ch.lab.classList.toggle('cur', on); });
      curChap = k;
      const ch = chap[k];
      if (ch && ch.abbrev) { barTag.textContent = ch.full; barTag.style.left = Math.max(8, ch.x0) + 'px'; barTag.style.visibility = ''; }
      else barTag.style.visibility = 'hidden';
    }
  }

  // ---------------------------------------------------------------- badges + table of contents
  let tocTracks = [];
  const TOC_ITEMS = ['API 是什么', '“已接入”接的是什么', 'API Key 是什么，怎么拿到'];
  ENG.tocRowRect = i => ({ x: 1550, y: 20 + 38 + i * 33, w: 320, h: 32 });
  function buildHud() {
    const b = el('div', '', stage); b.id = 'badge';
    el('div', 'b1', b, '配音：AI 合成');
    el('div', 'b2', b, '原LAI如此<span class="n">#01</span>');
    ENG.T(ENG.global, b, { o: 0 }).to(0.2, { o: 1 }, 0.6);

    const toc = el('div', '', stage); toc.id = 'toc';
    el('div', 'kick', toc, '<b>本期目录</b>CONTENTS');
    ENG.tocEl = toc;
    const rows = TOC_ITEMS.map((txt, i) => {
      const r = box('div', 'tocRow', toc, 10, 38 + i * 33);
      el('div', 'bar', r);
      const num = el('div', 'num', r, String(i + 1));
      const ck = svg(r, 10, 4, 24, 24, '<path d="M4 12.5 L 10 18 L 20 6" fill="none" stroke="#FF4F1A" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>');
      el('span', 'txt', r, esc(txt));
      const path = ck.querySelector('path');
      return { r, num, path, bar: r.querySelector('.bar') };
    });
    // timing (all from the data): the TOC appears at the end of S02; ① is highlighted in S03, ② in S04, ③ from S05 to the end of S07
    const s2last = seg('S02', 99);
    const tIn = ENG.tocInTime();
    const trToc = ENG.T(ENG.global, toc, { o: 0 }).to(tIn + 0.35, { o: 1 }, 0.4);
    const g2 = gapAfter(s2last);
    const act = [g2 ? g2.start : SC.S03.start, (lastGap('S03') || { start: SC.S03.end - 0.5 }).start,
      (lastGap('S04') || { start: SC.S04.end - 0.5 }).start];
    const done = [act[1], act[2], (lastGap('S07') || { start: SC.S07.end - 0.4 }).start];
    // S06 (三种调用方式) is an extra section outside the three questions: ③ goes back to "pending" while it plays and
    // lights up again when S07 (怎么拿到 = the second half of ③) starts.
    const aside = SC.S06 && SC.S07 ? [SC.S06.start, SC.S07.start] : null;
    rows.forEach((row, i) => {
      const fx = (p, tr) => {
        const hl = Math.round(p.hl * 100) / 100, dd = Math.round(p.d * 100) / 100;
        if (tr._h2 !== hl) {
          row.r.style.color = `rgba(237,234,227,${(0.5 + 0.5 * hl + 0.2 * p.d * (1 - hl)).toFixed(3)})`;
          row.bar.style.opacity = hl;
          row.num.style.background = hl > 0.5 ? '#FF4F1A' : 'rgba(237,234,227,.5)';
          row.num.style.color = hl > 0.5 ? '#EDEAE3' : '#141414';
          row.r.style.transform = `scale(${1 + 0.05 * hl})`;
          tr._h2 = hl;
        }
        if (tr._d2 !== dd) { row.path.style.strokeDashoffset = 1 - dd; row.num.style.visibility = dd > 0.02 ? 'hidden' : ''; tr._d2 = dd; }
      };
      const tr = ENG.T(ENG.global, null, { hl: 0, d: 0 }, fx);
      tr.to(act[i], { hl: 1 }, 0.35);
      if (i === 2 && aside && aside[0] > act[i] && aside[1] < done[i]) tr.to(aside[0], { hl: 0 }, 0.35).to(aside[1], { hl: 1 }, 0.35);
      tr.to(done[i], { hl: 0 }, 0.3).to(done[i] + 0.05, { d: 1 }, 0.25, E.out);
    });
    tocTracks = rows;
    ENG.tocTrack = trToc;
  }

  // ---------------------------------------------------------------- scene building
  function buildScenes() {
    const root = el('div', 'layer', stage); root.id = 'scenes';
    for (const b of ENG.builders) {
      const sc = SC[b.id];
      if (!sc) continue;
      const r = el('div', 'scene', root); r.id = 'scene_' + b.id;
      const S = { id: b.id, sc, root: r, tracks: [], start: sc.start, end: sc.end, shown: null };
      const c = ENG.ctx(S);
      try { b.fn(c); } catch (e) { console.error('scene ' + b.id + ': ' + e.message); }
      // whole scene fades out at its end (content only; TOC / bar / character are global)
      ENG.T(S.tracks, r, { o: 1 }).to(sc.end - 0.36, { o: 0 }, 0.3, E.sine);
      S.tracks.forEach(tr => tr.finalize());
      r.style.display = 'none';
      ENG.scenes.push(S);
    }
  }

  // ---------------------------------------------------------------- frame
  function renderAt(t) {
    if (!D) return;
    t = Math.max(0, Math.min(t, window.DURATION));
    // background
    const w2 = bgWeight2(t);
    const bo = clamp(t / 0.8);
    if (bgLayer._o !== bo) { bgLayer.style.opacity = bo; bgLayer._o = bo; }
    const w2s = w2.toFixed(3);
    if (bgCv.bg2._o !== w2s) { bgCv.bg2.style.opacity = w2s; bgCv.bg2._o = w2s; }
    // scenes
    for (const S of ENG.scenes) {
      const on = t >= S.start - 0.001 && t < S.end + 0.001;
      if (on !== S.shown) { S.root.style.display = on ? '' : 'none'; S.shown = on; }
      if (on) for (const tr of S.tracks) tr.eval(t);
    }
    for (const tr of ENG.global) tr.eval(t);
    renderChar(t);
    renderSubs(t);
    renderBar(t);
    // fade to the outro during the last gap
    const lg = lastGap(D.scenes[D.scenes.length - 1].id);
    const f0 = lg && lg.end >= window.DURATION - 0.05 ? lg.start : window.DURATION - 0.5;
    const fo = clamp((t - f0) / Math.max(0.1, window.DURATION - f0));
    const fos = fo.toFixed(3);
    if (fadeEl._o !== fos) { fadeEl.style.opacity = fos; fadeEl._o = fos; }
  }

  async function boot() {
    stage = el('div', '', document.body); stage.id = 'stage';
    if (!D) { el('div', '', stage, '缺少 window.__DATA__（请用 render.py --data timeline.json 打开）').id = 'nodata'; window.renderAt = () => {}; window.__READY__ = true; return; }
    const bgImgs = await loadAssets();
    buildBg(bgImgs);
    buildScenes();
    buildChar();
    buildHud();
    buildSubs();
    buildBar();
    fadeEl = el('div', '', stage); fadeEl.id = 'fade';
    ENG.global.forEach(tr => tr.finalize());
    window.renderAt = renderAt;
    renderAt(0);
    window.__READY__ = true;
  }
  ENG.boot = () => { boot().catch(e => { console.error('engine boot failed: ' + (e && e.stack || e)); window.__READY__ = true; }); };
})();
