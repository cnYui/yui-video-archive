/* 《原LAI如此》正片画面引擎 — 核心（每期通用，不要写任何一期的内容进来）。
 *
 * 数据契约：window.__DATA__ = timeline.json（render.py --data 注入）；window.__ASSETS__ = assets.js（sync_assets.py 生成）。
 *   页面设置 window.DURATION = main_duration，并提供 window.renderAt(t)（纯函数，可任意顺序 seek；不用 rAF / setTimeout / Date.now）。
 * 本文件负责全局层：背景（按章节切换）、像素角色（动作）、字幕、章节进度条、左上徽标、右上本期目录、片尾淡出，
 *   以及时间轴工具和轨道系统（Track）。每一场的画面在 scenes.js 里用 components.js 的组件搭。
 * 所有时刻都从 __DATA__ 的 segments / gaps / scenes / episode 推出来，不写死秒数。
 *
 * 读取的 episode 字段（timeline.json 的 episode；缺省时用 assets.js 里 sync_assets.py 从 episode.json 读到的副本）：
 *   number, title, question_scene, questions[{text, scenes[]}], chapters{sid: 标题}, backgrounds{sid: 文件}, bg_alpha, bg_blur, terms[]
 * 角色动作：segments[].actions / gaps[].actions = [{type: body|expr|pose|anim, name, start, end}]（正片秒）。
 *   没有任何 actions 时退回第 1 期行为：segments[].pose === 'reach' 的段首抬手 1.2 s。 */
(function () {
  'use strict';
  const D = window.__DATA__ || null;
  const A = window.__ASSETS__ || null;
  const AS = A || { anims: null, bg: {}, bgList: [], bgScenes: {}, spriteBase: '' };
  const EP = Object.assign({}, (A && A.episode) || {}, (D && D.episode) || {});
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
  const pad2 = n => String(n == null ? '' : n).padStart(2, '0');

  // ---------------------------------------------------------------- timeline helpers
  const SC = {};
  const SEGS = D ? D.segments.slice().sort((a, b) => a.start - b.start) : [];
  const GAPS = D ? (D.gaps || []).slice().sort((a, b) => a.start - b.start) : [];
  const SCENES = D ? D.scenes.slice().sort((a, b) => a.start - b.start) : [];
  const SEG_BY_ID = {};
  if (D) {
    for (const s of SCENES) SC[s.id] = Object.assign({}, s, { segs: [], gaps: [] });
    for (const s of SEGS) { SEG_BY_ID[s.id] = s; if (SC[s.scene]) SC[s.scene].segs.push(s); }
    for (const g of GAPS) if (SC[g.scene]) SC[g.scene].gaps.push(g);
  }
  const NOSEG = { start: 0, end: 0.1, lines: [], text: '', missing: true };
  /** i-th segment (0-based) of scene sid; out-of-range i is clamped (99 = last) */
  function seg(sid, i) {
    const s = SC[sid];
    if (!s || !s.segs.length) return NOSEG;
    return s.segs[Math.max(0, Math.min(i, s.segs.length - 1))];
  }
  /** segment by its 段号 ('S03-12'); unknown id -> a warning and a harmless dummy */
  function segId(id) {
    if (SEG_BY_ID[id]) return SEG_BY_ID[id];
    console.warn('segId: unknown segment ' + id);
    return NOSEG;
  }
  /** time at which `phrase` starts being spoken inside segment sg, or null when the phrase is not in it.
   *  Matching ignores spaces and punctuation, so 'API Key' also finds 'APIKey' / 'API key，'. */
  const norm = s => String(s || '').replace(/[\s，。、！？：；“”‘’"'（）()《》「」【】,.!?:;…·—\-]/g, '').toLowerCase();
  function phraseTime(sg, phrase) {
    if (!phrase || !sg || !sg.lines) return null;
    const want = norm(phrase);
    if (!want) return null;
    let acc = ''; const spans = [];
    for (const ln of sg.lines) { const t = norm(ln.text); spans.push([acc.length, acc.length + t.length, ln]); acc += t; }
    const i = acc.indexOf(want);
    if (i < 0) return null;
    for (const [a, b, ln] of spans) if (i >= a && i < b) return ln.start + (ln.end - ln.start) * (i - a) / Math.max(1, b - a);
    return null;
  }
  /** phrase time in segment sg; fallback: `frac` of the way through the segment */
  function ph(sg, phrase, frac = 0) {
    const t = phraseTime(sg, phrase);
    return t != null ? t : sg.start + (sg.end - sg.start) * frac;
  }
  /** the pure-visual gap right after segment sg (if any) */
  function gapAfter(sg) {
    for (const g of GAPS) if (g.start >= sg.end - 0.01 && g.start <= sg.end + 0.6) return g;
    return null;
  }
  function lastGap(sid) { const s = SC[sid]; return s && s.gaps.length ? s.gaps[s.gaps.length - 1] : null; }
  /** moment the talking of a scene is over: start of its closing gap (after the last line), else end - 0.4 s */
  function endTalk(sid) {
    const s = SC[sid];
    if (!s) return 0;
    const lg = lastGap(sid), ls = s.segs.length ? s.segs[s.segs.length - 1] : null;
    if (lg && (!ls || lg.start >= ls.end - 0.01)) return lg.start;
    return s.end - 0.4;
  }
  function sceneAt(t) {
    let k = 0;
    for (let i = 0; i < SCENES.length; i++) if (t >= SCENES[i].start) k = i;
    return k;
  }
  const fmt = x => `${Math.floor(x / 60)}:${String(Math.floor(x % 60)).padStart(2, '0')}`;
  const chapterTitle = sid => (EP.chapters && EP.chapters[sid]) || (SC[sid] && SC[sid].title) || sid;
  /** 1-based question number whose scenes include sid (0 = none) */
  const questionOf = sid => { const q = EP.questions || []; for (let i = 0; i < q.length; i++) if ((q[i].scenes || []).includes(sid)) return i + 1; return 0; };

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
    D, A: AS, EP, W, H, SC, SEGS, GAPS, SCENES, E, clamp, lerp, el, css, box, svg, esc, pad2,
    seg, segId, ph, phraseTime, gapAfter, lastGap, endTalk, sceneAt, fmt, chapterTitle, questionOf, Track,
    builders: [], scenes: [], global: [],
    /** extra subtitle terms (orange) — scenes.js may push more before boot */
    TERMS: ['API Key', 'API key', 'API', 'Token', 'token', 'JSON', 'HTTP', 'SSE', 'LLM', 'Prompt', 'prompt'],
    /** legacy (no actions in the timeline): per-segment phrase at which the 抬手 starts, e.g. {'S05-26': '平台靠它'} */
    REACH_AT: {},
    /** 走动 action: horizontal drift of the character (px, out and back) */
    WALK_DRIFT: 30,
  };
  ENG.scene = (id, fn) => ENG.builders.push({ id, fn });
  ENG.T = (list, e, init, fx) => { const tr = new Track(e, init, fx); list.push(tr); return tr; };
  /** moment the question cards fly into the top-right TOC: end of question_scene's last line */
  ENG.tocInTime = () => {
    const qs = EP.question_scene;
    if (qs && SC[qs] && SC[qs].segs.length) { const s = seg(qs, 99); return Math.max(s.start + 0.8, s.end - 0.75); }
    const q0 = (EP.questions || [])[0];
    const s0 = q0 && (q0.scenes || []).map(id => SC[id]).filter(Boolean)[0];
    return s0 ? Math.max(0, s0.start - 0.4) : 1e9;
  };

  let stage, subsBox, subStroke, subFill, charCv, charCtx, charShadow, barP, pickEl, barTag, fadeEl, bgLayer;

  // ---------------------------------------------------------------- loading
  function loadImg(src) {
    return new Promise(res => { const i = new Image(); i.onload = () => res(i); i.onerror = () => { console.warn('image failed: ' + src); res(null); }; i.src = src; });
  }
  const FRAMES = {};  // anim -> [{img, dur}] ; FRAMES[anim].loop
  const BG = { keys: [], sceneKey: [], cv: {} };
  function bgFileOf(v) { return v ? String(v).split(/[\\/]/).pop() : null; }
  function resolveBackgrounds() {
    // per scene: episode.backgrounds (timeline) -> assets.js bgScenes (from episode.json) -> scenes[].bg -> gallery rotation
    const map = AS.bg || {}, list = AS.bgList || Object.keys(map);
    const epb = EP.backgrounds || {};
    SCENES.forEach((s, i) => {
      let k = null;
      for (const cand of [bgFileOf(epb[s.id]), (AS.bgScenes || {})[s.id], s.bg, bgFileOf(s.bg)]) {
        if (cand && map[cand]) { k = cand; break; }
      }
      if (!k && (epb[s.id] || (AS.bgScenes || {})[s.id])) console.warn(`scene ${s.id}: background ${epb[s.id] || AS.bgScenes[s.id]} not in assets.js (run sync_assets.py)`);
      if (!k && list.length) k = list[i % list.length];
      BG.sceneKey.push(k || '__placeholder__');
    });
    BG.keys = [...new Set(BG.sceneKey)];
  }
  async function loadAssets() {
    const fontJobs = [
      '700 44px "Noto Sans SC"', '900 80px "Noto Sans SC"', '500 22px "Noto Sans SC"', '800 30px "Noto Sans SC"',
      '500 16px "KuaiLe Han"', '700 22px "JetBrains Mono"', '500 22px "JetBrains Mono"', '800 150px "JetBrains Mono"',
    ].map(f => document.fonts.load(f, 'API 接口 sk-•… 0:33').catch(() => null));
    const jobs = [...fontJobs];
    if (AS.anims && AS.anims.anims) {
      for (const [name, a] of Object.entries(AS.anims.anims)) {
        FRAMES[name] = a.frames.map((f, i) => ({ img: null, dur: a.durations[i], src: AS.spriteBase + f }));
        FRAMES[name].loop = a.loop !== false;
        FRAMES[name].forEach(fr => jobs.push(loadImg(fr.src).then(img => { fr.img = img; })));
      }
    }
    resolveBackgrounds();
    const bgImgs = {};
    for (const k of BG.keys) if (AS.bg && AS.bg[k]) jobs.push(loadImg(AS.bg[k]).then(img => { bgImgs[k] = img; }));
    await Promise.all(jobs);
    await document.fonts.ready;
    return bgImgs;
  }

  // ---------------------------------------------------------------- background (per chapter, 0.8 s crossfade)
  const BG_ALPHA = +(EP.bg_alpha != null ? EP.bg_alpha : AS.bgAlpha != null ? AS.bgAlpha : 0.22);
  const BG_BLUR = +(EP.bg_blur != null ? EP.bg_blur : AS.bgBlur != null ? AS.bgBlur : 10);
  const BGX = 0.8;  // crossfade seconds
  function paintBg(cv, img, idx) {
    const g = cv.getContext('2d');
    g.fillStyle = '#1B2340'; g.fillRect(0, 0, W, H);
    if (img) {
      // cover: fill the frame whatever the aspect (2000x1080, 2000x1125, 1200x675 ...); overscan by the blur
      // radius so the blurred edge never shows a dark fringe
      const pad = BG_BLUR * 3;
      const iw = img.naturalWidth, ih = img.naturalHeight, sc = Math.max((W + 2 * pad) / iw, (H + 2 * pad) / ih);
      g.save(); g.filter = BG_BLUR > 0 ? `blur(${BG_BLUR}px)` : 'none'; g.globalAlpha = BG_ALPHA;
      g.drawImage(img, (W - iw * sc) / 2, (H - ih * sc) / 2, iw * sc, ih * sc);
      g.restore();
    } else {
      // placeholder: soft dark gradient until real stills exist
      const warm = idx % 2 === 0;
      let gr = g.createRadialGradient(1250, 360, 60, 1250, 360, 1300);
      gr.addColorStop(0, warm ? 'rgba(150,96,70,.30)' : 'rgba(80,130,190,.28)');
      gr.addColorStop(1, 'rgba(27,35,64,0)');
      g.fillStyle = gr; g.fillRect(0, 0, W, H);
    }
    const vg = g.createRadialGradient(W / 2, H / 2, H * 0.42, W / 2, H / 2, H * 1.05);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,.15)');
    g.fillStyle = vg; g.fillRect(0, 0, W, H);
  }
  function buildBg(bgImgs) {
    bgLayer = el('div', 'layer', stage); bgLayer.id = 'bg';
    BG.keys.forEach((k, i) => {
      const cv = el('canvas', '', bgLayer); cv.width = W; cv.height = H; cv.dataset.bg = k;
      cv.style.display = 'none'; cv._state = 'none';
      paintBg(cv, bgImgs[k] || null, i); BG.cv[k] = cv;
    });
  }
  /** {from, to, w}: layers to show at t (w = opacity of `to` over `from`) */
  function bgMix(t) {
    const k = sceneAt(t), cur = BG.sceneKey[k];
    const s = SCENES[k];
    if (k > 0 && t - s.start < BGX / 2 && BG.sceneKey[k - 1] !== cur) {
      return { from: BG.sceneKey[k - 1], to: cur, w: E.sine(clamp((t - s.start + BGX / 2) / BGX)) };
    }
    const nx = SCENES[k + 1];
    if (nx && nx.start - t < BGX / 2 && BG.sceneKey[k + 1] !== cur) {
      return { from: cur, to: BG.sceneKey[k + 1], w: E.sine(clamp((t - nx.start + BGX / 2) / BGX)) };
    }
    return { from: cur, to: null, w: 0 };
  }
  function renderBg(t) {
    const bo = clamp(t / 0.8).toFixed(3);   // the very first background fades in from navy
    if (bgLayer._o !== bo) { bgLayer.style.opacity = bo; bgLayer._o = bo; }
    const m = bgMix(t);
    for (const k of BG.keys) {
      const cv = BG.cv[k];
      const st = k === m.from ? 'from' : k === m.to ? 'to:' + m.w.toFixed(3) : 'none';
      if (cv._state === st) continue;
      cv._state = st;
      if (st === 'none') { cv.style.display = 'none'; continue; }
      cv.style.display = '';
      cv.style.zIndex = st === 'from' ? 0 : 1;
      cv.style.opacity = st === 'from' ? 1 : m.w.toFixed(3);
    }
    ENG.bgNow = m;  // exposed for tests
  }

  // ---------------------------------------------------------------- character
  // Priority at time t: walk-in > anim (hop / walk) > pose > body (reach) + expr.  idle / reach / expr / pose frames
  // share ONE breathing clock (t * 1000 ms), so switching between them never makes the head jump; anims run on
  // their own clock from the action start.
  const SPEAK = [], ACT = { body: [], expr: [], pose: [], anim: [] };
  let charKey = '', hasActions = false;
  function buildChar() {
    charShadow = el('div', '', stage); charShadow.id = 'charShadow';
    charCv = el('canvas', '', stage); charCv.id = 'char'; charCv.width = 64; charCv.height = 64;
    charCtx = charCv.getContext('2d'); charCtx.imageSmoothingEnabled = false;
    for (const s of SEGS) SPEAK.push([s.start, s.end]);
    for (const x of [...SEGS, ...GAPS]) for (const a of x.actions || []) {
      if (!a || !ACT[a.type] || !(a.end > a.start)) { if (a) console.warn('ignored action ' + JSON.stringify(a)); continue; }
      ACT[a.type].push({ name: a.name, start: +a.start, end: +a.end });
      hasActions = true;
    }
    if (!hasActions) {
      // 第 1 期兼容：segments[].pose === 'reach' → 段首（或 REACH_AT 短语处）抬手 1.2 s
      for (const s of SEGS) {
        if (s.pose !== 'reach') continue;
        const t0 = ENG.REACH_AT[s.id] ? Math.max(s.start, ph(s, ENG.REACH_AT[s.id], 0)) : s.start;
        ACT.body.push({ name: 'reach', start: t0, end: Math.min(s.end, t0 + 1.2) });
      }
    }
    for (const k in ACT) ACT[k].sort((a, b) => a.start - b.start);
    // warn once for actions whose frames are missing (they fall back to idle)
    const need = new Set();
    ACT.expr.forEach(a => [0, 1, 2].forEach(m => need.add(`idle_${a.name}_m${m}`)));
    ACT.pose.forEach(a => need.add(`pose_${a.name}`));
    ACT.anim.forEach(a => need.add(a.name));
    ACT.body.forEach(a => [0, 1, 2].forEach(m => need.add(`${a.name}_m${m}`)));
    const miss = [...need].filter(n => !FRAMES[n]);
    if (miss.length && AS.anims) console.warn('character frames missing (falling back to idle): ' + miss.join(', '));
  }
  function activeAt(list, t) {
    let r = null;
    for (const a of list) { if (a.start > t) break; if (t < a.end) r = a; }
    return r;
  }
  function inRanges(list, t) {
    let lo = 0, hi = list.length - 1;
    while (lo <= hi) { const m = (lo + hi) >> 1; if (list[m][1] <= t) lo = m + 1; else if (list[m][0] > t) hi = m - 1; else return true; }
    return false;
  }
  function frameAt(frames, ms, loop = true) {
    let total = 0; for (const f of frames) total += f.dur;
    let x;
    if (loop) x = ((ms % total) + total) % total;
    else { if (ms >= total) return frames.length - 1; x = Math.max(0, ms); }
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
  const has = n => FRAMES[n] && FRAMES[n].length;
  /** what to draw at t: {anim, ms, loop, head (anim whose rows 0..35 go on top), x, pose, m} */
  function charState(t) {
    const m = mouthAt(t);
    const wi = D.walk_in || { start: 0, end: 0 };
    if (t < wi.end) {
      const p = clamp((t - wi.start) / Math.max(0.01, wi.end - wi.start));
      return { anim: 'walk', ms: (t - wi.start) * 1000, loop: true, x: lerp(-400, 0, 1 - Math.pow(1 - p, 1.25)), pose: 'walk', m: 0 };
    }
    const an = activeAt(ACT.anim, t);
    if (an && has(an.name)) {
      const ms = (t - an.start) * 1000;
      let x = 0;
      if (an.name === 'walk') x = ENG.WALK_DRIFT * Math.sin(Math.PI * clamp((t - an.start) / Math.max(0.1, an.end - an.start)));
      return { anim: an.name, ms, loop: FRAMES[an.name].loop, x, pose: an.name, m: 0 };
    }
    const ms = t * 1000;
    const po = activeAt(ACT.pose, t);
    if (po && has('pose_' + po.name)) return { anim: 'pose_' + po.name, ms, loop: true, x: 0, pose: po.name, m: 0 };
    const bd = activeAt(ACT.body, t);
    const body = bd && has(`${bd.name}_m${m}`) ? bd.name : 'idle';
    const ex = activeAt(ACT.expr, t);
    const exAnim = ex && has(`idle_${ex.name}_m${m}`) ? `idle_${ex.name}_m${m}` : null;
    if (body === 'idle') return { anim: exAnim || `idle_m${m}`, ms, loop: true, x: 0, pose: ex ? ex.name : 'idle', m };
    // reach + expression: the reach frame with the expression's head (rows 0..35 are identical between idle and reach)
    return { anim: `${body}_m${m}`, head: exAnim, ms, loop: true, x: 0, pose: body, m };
  }
  function renderChar(t) {
    const st = charState(t);
    const tf = st.x ? `translateX(${st.x.toFixed(1)}px)` : '';
    if (charCv._tf !== tf) { charCv.style.transform = tf; charShadow.style.transform = tf; charCv._tf = tf; }
    let key;
    if (has(st.anim)) {
      const i = frameAt(FRAMES[st.anim], st.ms, st.loop);
      key = st.anim + '#' + i + (st.head ? '+' + st.head : '');
      if (key !== charKey) {
        charCtx.clearRect(0, 0, 64, 64);
        const fr = FRAMES[st.anim][i];
        if (fr.img) charCtx.drawImage(fr.img, 0, 0);
        if (st.head && has(st.head)) {
          const hf = FRAMES[st.head][Math.min(i, FRAMES[st.head].length - 1)];
          if (hf.img) { charCtx.clearRect(0, 0, 64, 36); charCtx.drawImage(hf.img, 0, 0, 64, 36, 0, 0, 64, 36); }
        }
        charKey = key;
      }
    } else {
      const pose = st.pose === 'walk' ? 'walk' : st.pose === 'reach' ? 'reach' : 'idle';
      const wp = pose === 'walk' ? Math.floor(st.ms / 145) % 2 : 0;
      key = `ph${pose}${st.m}${wp}`;
      if (key !== charKey) { drawPlaceholder(charCtx, pose, pose === 'walk' ? 0 : st.m, wp); charKey = key; }
    }
    ENG.charKey = charKey;  // exposed for tests (the canvas itself is tainted by file:// images)
  }

  // ---------------------------------------------------------------- subtitles (centred on the whole frame, x = 960)
  const SUB_MAXW = 1240;   // 960 ± 620 -> x 340..1580: never reaches the character (x <= 320)
  const SUBS = [];
  let subIdx = -2, TERM_RE = null;
  function buildSubs() {
    subsBox = el('div', '', stage); subsBox.id = 'subs';
    subStroke = el('div', 's stroke', subsBox); subFill = el('div', 's fill', subsBox);
    const terms = [...new Set([...(ENG.TERMS || []), ...(EP.terms || [])])].filter(Boolean).sort((a, b) => b.length - a.length);
    if (terms.length) TERM_RE = new RegExp('(?<![A-Za-z_\\-/.])(' + terms.map(s => s.replace(/[.*+?^${}()|[\]\\\/]/g, '\\$&')).join('|') + ')(?![A-Za-z_\\-])', 'g');
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
      s.fs = w > SUB_MAXW ? Math.max(26, Math.floor(44 * SUB_MAXW / w)) : 44;
      if (w * s.fs / 44 > SUB_MAXW + 1) console.warn(`subtitle too long even at ${s.fs}px (may reach the character): ${s.text}`);
      s.html = subHTML(s.text);
    }
    probe.remove();
  }
  /** subtitle markup: orange terms + optically hung edge punctuation. Full-width 。，”？ etc. carry their ink in one
   *  half of the em box, so a line ending in 。 looked ~14 px left of centre; a negative margin on that glyph
   *  (style.css .hr / .hr2 / .hl) centres the visible ink on x = 960 instead of the layout box. */
  function subHTML(text) {
    let mid = String(text), pre = '', post = '';
    const cls = /[。，、：；”’」』）]$/.test(mid) ? 'hr' : /[？！]$/.test(mid) ? 'hr2' : '';
    if (cls) { post = `<span class="${cls}">${esc(mid.slice(-1))}</span>`; mid = mid.slice(0, -1); }
    if (/^[“‘「『（]/.test(mid)) { pre = `<span class="hl">${esc(mid[0])}</span>`; mid = mid.slice(1); }
    return pre + (TERM_RE ? esc(mid).replace(TERM_RE, '<span class="t">$1</span>') : esc(mid)) + post;
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

  // ---------------------------------------------------------------- chapter bar (Bocchi the Rock! palette), whole-video time
  const BAR_COLORS = ['#F2A0BD', '#F6C945', '#4A6FD0', '#E2463F'];
  const BM = 6;
  let barX, chap = [], curChap = -2;
  function hexA(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
  function buildBar() {
    const total = D.total_duration || (D.intro || 0) + D.main_duration + (D.outro || 0);
    barX = tt => BM + (W - 2 * BM) * clamp(tt / total);
    el('div', '', stage).id = 'barShade';
    const bar = el('div', '', stage); bar.id = 'bar';
    const U = el('div', 'layer', bar); U.id = 'barU'; css(U, { height: 80 });
    barP = el('div', '', bar); barP.id = 'barP';
    const probe = el('span', 'bLab', stage); css(probe, { position: 'absolute', left: -9999, top: 0, whiteSpace: 'nowrap' });
    const measure = (txt, fs) => { probe.style.fontSize = fs + 'px'; probe.textContent = txt; return probe.offsetWidth; };
    (D.chapters || []).forEach((c, i) => {
      const title = c.title || chapterTitle(c.id);
      const x0 = barX(c.start), x1 = barX(c.end), col = BAR_COLORS[i % 4];
      const bl = x0 + 2, bw = Math.max(4, x1 - x0 - 4);
      const bu = box('div', 'bBlk', U, bl, null, bw); bu.style.background = hexA(col, 0.46);
      const bp = box('div', 'bBlk', barP, bl, null, bw); bp.style.background = col;
      const full = `${fmt(c.start)}–${fmt(c.end)} ${title}`;
      const cands = [[full, 16], [full, 15], [full, 14], [title, 15], [title, 13], [String(i + 1), 14]].map(([t, f]) => ({ t, f, w: measure(t, f) }));
      chap.push({ c, bu, bp, full, x0: bl, x1: bl + bw, cx: bl + bw / 2, cands, lv: 0 });
    });
    probe.remove();
    // 1-D label layout: centre each label on its chapter, push neighbours apart (gap 12 px), and shorten a label
    // (smaller font -> title only -> number) only when it can no longer overlap its own chapter enough.
    for (let iter = 0; iter < 40 && chap.length; iter++) {
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

  // ---------------------------------------------------------------- badge + table of contents
  const TOC = { x: 1540, y: 20, w: 340, rowY: 38, rowH: 33, rowW: 320 };
  ENG.tocRowRect = i => ({ x: TOC.x + 10, y: TOC.y + TOC.rowY + i * TOC.rowH, w: TOC.rowW, h: 32 });
  /** the TOC box once it is on screen ({x, y, w, h}), or null when the episode has no questions */
  ENG.tocRect = () => ((EP.questions || []).length ? { x: TOC.x, y: TOC.y, w: TOC.w, h: TOC.rowY + EP.questions.length * TOC.rowH + 5 } : null);
  /** top y for content spanning x left..right that must stay clear of the TOC (18 px gap); y itself when no overlap */
  ENG.safeTop = (y, right = 1860, left = 440) => {
    const r = ENG.tocRect();
    return r && right > r.x && left < r.x + r.w ? Math.max(y, r.y + r.h + 18) : y;
  };
  /** TOC schedule of question i: [{on, off}] highlight runs + done time. Rules (same as 第 1 期):
   *  a run of consecutive scenes of the question lights up when the talking of the previous scene ends (if that scene
   *  is the question scene or belongs to a question), otherwise at the run's first scene start; it goes dark at the
   *  next scene when the question continues later; after its last scene's talking ends it is ticked. */
  function tocSchedule(qi) {
    const q = EP.questions[qi], ids = new Set(q.scenes || []);
    const idx = SCENES.map((s, i) => (ids.has(s.id) ? i : -1)).filter(i => i >= 0);
    const runs = [];
    for (const i of idx) { const r = runs[runs.length - 1]; if (r && r[1] === i - 1) r[1] = i; else runs.push([i, i]); }
    const tIn = ENG.tocInTime() + 0.35;
    const out = { runs: [], done: null };
    runs.forEach(([a, b], ri) => {
      const prev = SCENES[a - 1];
      let on = SCENES[a].start;
      if (prev && (prev.id === EP.question_scene || questionOf(prev.id))) on = endTalk(prev.id);
      on = Math.max(on, tIn + 0.3);
      const last = ri === runs.length - 1;
      const off = last ? endTalk(SCENES[b].id) : SCENES[b].end;
      out.runs.push({ on, off });
      if (last) out.done = off;
    });
    return out;
  }
  /** TOC geometry from the question texts (before the scenes are built, so c.questionCards flies to the right rows) */
  function layoutToc() {
    const Q = (EP.questions || []).filter(q => q && q.text);
    EP.questions = Q;
    if (!Q.length) return;
    // width: fit the longest question (row text at 19 px starts 44 px into a row)
    const probe = el('span', 'tocRow', stage); css(probe, { position: 'absolute', left: -9999, top: 0, width: 'auto', paddingLeft: 0 });
    let maxw = 0; for (const q of Q) { probe.textContent = q.text; maxw = Math.max(maxw, probe.offsetWidth); }
    probe.remove();
    TOC.rowW = Math.max(320, Math.min(560, Math.ceil(maxw) + 44 + 16));
    TOC.w = TOC.rowW + 20; TOC.x = 1880 - TOC.w;
  }
  function buildHud() {
    const b = el('div', '', stage); b.id = 'badge';
    const num = EP.number != null ? '#' + pad2(EP.number) : '';
    el('div', 'b2', b, `原LAI如此${num ? `<span class="n">${num}</span>` : ''}`);
    ENG.T(ENG.global, b, { o: 0 }).to(0.2, { o: 1 }, 0.6);

    const Q = EP.questions || [];
    if (!Q.length) return;
    const toc = el('div', '', stage); toc.id = 'toc';
    css(toc, { left: TOC.x, top: TOC.y, width: TOC.w, height: TOC.rowY + Q.length * TOC.rowH + 5 });
    el('div', 'kick', toc, '<b>本期目录</b>CONTENTS');
    ENG.tocEl = toc;
    const rows = Q.map((q, i) => {
      const r = box('div', 'tocRow', toc, 10, TOC.rowY + i * TOC.rowH, TOC.rowW);
      el('div', 'bar', r);
      const num = el('div', 'num', r, String(i + 1));
      const ck = svg(r, 10, 4, 24, 24, '<path d="M4 12.5 L 10 18 L 20 6" fill="none" stroke="#FF4F1A" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>');
      el('span', 'txt', r, esc(q.text));
      return { r, num, path: ck.querySelector('path'), bar: r.querySelector('.bar') };
    });
    const tIn = ENG.tocInTime();
    ENG.tocTrack = ENG.T(ENG.global, toc, { o: 0 }).to(tIn + 0.35, { o: 1 }, 0.4);
    ENG.tocTimes = [];
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
      const sch = tocSchedule(i);
      sch.runs.forEach((r, ri) => {
        tr.to(r.on, { hl: 1 }, 0.35);
        if (ri < sch.runs.length - 1) tr.to(r.off, { hl: 0 }, 0.35);
      });
      if (sch.done != null) tr.to(sch.done, { hl: 0 }, 0.3).to(sch.done + 0.05, { d: 1 }, 0.25, E.out);
      ENG.tocTimes.push(sch);
    });
  }

  // ---------------------------------------------------------------- scene building
  function buildScenes() {
    const root = el('div', 'layer', stage); root.id = 'scenes';
    for (const b of ENG.builders) {
      const sc = SC[b.id];
      if (!sc) { console.warn('scene ' + b.id + ' is not in the timeline (builder skipped)'); continue; }
      const r = el('div', 'scene', root); r.id = 'scene_' + b.id;
      const S = { id: b.id, sc, root: r, tracks: [], start: sc.start, end: sc.end, shown: null };
      const c = ENG.ctx ? ENG.ctx(S) : null;
      try { b.fn(c); } catch (e) { console.error('scene ' + b.id + ': ' + (e && e.stack || e)); }
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
    renderBg(t);
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
    const lg = SCENES.length ? lastGap(SCENES[SCENES.length - 1].id) : null;
    const f0 = lg && lg.end >= window.DURATION - 0.05 ? lg.start : window.DURATION - 0.5;
    const fo = clamp((t - f0) / Math.max(0.1, window.DURATION - f0));
    const fos = fo.toFixed(3);
    if (fadeEl._o !== fos) { fadeEl.style.opacity = fos; fadeEl._o = fos; }
  }

  async function boot() {
    stage = el('div', '', document.body); stage.id = 'stage';
    if (!D) { el('div', '', stage, '缺少 window.__DATA__（请用 render.py --data timeline.json 打开）').id = 'nodata'; window.renderAt = () => {}; window.__READY__ = true; return; }
    if (!A) console.error('assets.js 缺失或为空：先运行 python engine/sync_assets.py');
    const bgImgs = await loadAssets();
    buildBg(bgImgs);
    layoutToc();
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
