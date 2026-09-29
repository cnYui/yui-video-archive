/* 《原LAI如此》正片画面引擎 — 核心（每期通用，不要写任何一期的内容进来）。
 *
 * 数据契约：window.__DATA__ = timeline.json（render.py --data 注入）；window.__ASSETS__ = assets.js（sync_assets.py 生成）。
 *   页面设置 window.DURATION = main_duration，并提供 window.renderAt(t)（纯函数，可任意顺序 seek；不用 rAF / setTimeout / Date.now）。
 * 本文件负责全局层：背景（按章节切换）、像素角色（动作）、字幕、章节进度条、左上徽标、右上本期目录、片尾淡出，
 *   以及时间轴工具和轨道系统（Track）。每一场的画面在 scenes.js 里用 components.js 的组件搭。
 * 所有时刻都从 __DATA__ 的 segments / gaps / scenes / episode 推出来，不写死秒数。
 *
 * 读取的 episode 字段（timeline.json 的 episode；缺省时用 assets.js 里 sync_assets.py 从 episode.json 读到的副本）：
 *   number, title, question_scene, questions[{text, scenes[]}], chapters{sid: 标题}, backgrounds{sid: 文件}, bg_alpha, bg_blur, terms[],
 *   auto_gestures（true | false | {gesture: 倍率, nod, look, weight}）
 * 角色动作：segments[].actions / gaps[].actions = [{type: body|expr|pose|anim|head|fx|auto, name, start, end}]（正片秒）。
 *   timeline.json 没有 episode 字段（第 1 期旧时间轴）：v1 行为逐像素不变 —— 没有任何 actions 时 segments[].pose === 'reach'
 *   的段首抬手 1.2 s；不读动作注册表、没有自动层。
 *   有 episode 字段（动作 v2，规格 _skilltest/actions_v2/SPEC.md「最终定稿」）：动作注册表（anims.json actions）、眼睛补丁、
 *   头部动作、特效层、自动层（手势 / 句末点头 / 看向内容，确定性，碰到显式动作让开）。
 *   scenes.js 可用 ENG.cue(t) 登记内容提示点（components 已自动登记）、ENG.look(t0, t1) 让角色看向内容。 */
(function () {
  'use strict';
  const D = window.__DATA__ || null;
  const A = window.__ASSETS__ || null;
  const AS = A || { anims: null, bg: {}, bgList: [], bgScenes: {}, spriteBase: '' };
  const EP = Object.assign({}, (A && A.episode) || {}, (D && D.episode) || {});
  window.DURATION = D && D.main_duration > 0 ? D.main_duration : 1;
  window.__READY__ = false;

  const W = 2340, H = 1080;   // AI每日日报：iPhone 全面屏 19.5:9（原 1920x1080）
  const CX = W / 2;           // 1170：标题和正文跟字幕一样以画面中线居中（用户 2026-09-27；右上角目录除外）
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
    D, A: AS, EP, W, H, CX, SC, SEGS, GAPS, SCENES, E, clamp, lerp, el, css, box, svg, esc, pad2,
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
        FRAMES[name].meta = a;   // extra fields (v2: kind, head [dx, dy], patch …)
        FRAMES[name].forEach(fr => jobs.push(loadImg(fr.src).then(img => { fr.img = img; })));
      }
    }
    resolveBackgrounds();
    const bgImgs = {};
    for (const k of BG.keys) if (AS.bg && AS.bg[k]) jobs.push(loadImg(AS.bg[k]).then(img => { bgImgs[k] = img; }));
    // AI每日日报: source screenshots (episode.json news[].snap, relative to this page) are loaded before scenes are built,
    // so scenes.js can append the decoded <img> itself and the first frame never shows an empty card
    ENG.snapImgs = {};
    for (const n of EP.news || []) if (n && n.snap) jobs.push(loadImg(n.snap).then(img => { if (img) ENG.snapImgs[n.snap] = img; }));
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
  // Two modes, chosen ONLY by whether timeline.json has an `episode` block (D.episode; never the assets.js copy):
  //  * legacy (no D.episode — 第 1 期的旧时间轴): exactly the v1 behaviour. Priority walk-in > anim > pose > body + expr,
  //    the expression is drawn over rows 0..35, no action registry (抬手 plays reach_m* with no transition / gaze),
  //    no auto layer.  Kept verbatim so old timelines render pixel-identical.
  //  * v2 (D.episode present): action registry (anims.json `actions`, defaults in ACTION_DEFAULTS), eye patches,
  //    head variants (nod / shake), fx layer, legs patch, scene looks (ENG.look) and the deterministic auto layer
  //    (planAuto, SPEC F.3) unless episode.auto_gestures === false.
  // All breathing frames (idle / body / expression eyes / head variants / stickers) share ONE clock (t * 1000 ms), so
  // switching between them never makes the head jump; anims (walk / hop) and fx run on their own clock from their start.
  const V2 = !!(D && D.episode);
  const SPEAK = [], ACT = V2 ? { body: [], expr: [], pose: [], anim: [], head: [], fx: [], auto: [] }
    : { body: [], expr: [], pose: [], anim: [] };
  const AUTOP = { body: [], head: [], look: [], legs: [] };   // auto layer, split by channel (sorted by start)
  const SCENE_LOOKS = [];                                     // ENG.look(t0, t1) from scenes.js (v2 only)
  ENG.sceneLooks = SCENE_LOOKS;
  let charKey = '', hasActions = false;

  /** built-in action registry (SPEC F.6 + F.7). anims.json `actions` replaces an entry of the same name.
   *  body: frames (base name, or list = alternate every phase_ms), via / via_ms (transition frames at both ends),
   *        look (eyes idle_<look>_m* while the action runs), fx (fx layer between the transitions, own clock)
   *  head: steps [[frames|null, ms], ...] (null = back to normal), eyes (eye patch during non-null steps)
   *  legs: frames (1 frame, pasted into patch_rects.legs).  Names not listed play as {frames: name}. */
  const ACTION_DEFAULTS = {
    reach: { type: 'body', frames: 'reach', via: 'palm', via_ms: 80, look: 'look_r' },
    chest: { type: 'body', frames: 'chest', via: 'chest_mid', via_ms: 90, auto: true },
    palm: { type: 'body', frames: 'palm', auto: true },
    palm_r: { type: 'body', frames: 'palm', look: 'look_r', auto: true },
    hold: { type: 'body', frames: 'hold', via: 'chest_mid', via_ms: 90, auto: true },
    point: { type: 'body', frames: 'point', via: 'palm', via_ms: 80, look: 'look_r' },
    wave: { type: 'body', frames: ['wave_a', 'wave_b'], phase_ms: 280, via: 'reach', via_ms: 80 },
    count1: { type: 'body', frames: 'count1', via: 'reach', via_ms: 80, fx: 'fx_digit1' },
    count2: { type: 'body', frames: 'count2', via: 'reach', via_ms: 80, fx: 'fx_digit2' },
    count3: { type: 'body', frames: 'count3', via: 'reach', via_ms: 80, fx: 'fx_digit3' },
    finger_up: { type: 'body', frames: 'count1', via: 'reach', via_ms: 80, fx: 'fx_exclaim' },
    think: { type: 'body', frames: 'think', via: 'chest', via_ms: 100, look: 'look_ur', fx: 'fx_think' },
    shrug: { type: 'body', frames: 'shrug' },
    thumb: { type: 'body', frames: 'thumb', via: 'reach', via_ms: 80, fx: 'fx_glint' },
    hip: { type: 'body', frames: 'hip', via: 'hip_mid', via_ms: 90 },
    ear: { type: 'body', frames: 'ear', via: 'reach', via_ms: 80, look: 'look_r', fx: 'fx_listen' },
    nod: { type: 'head', steps: [['head_nod', 220]], eyes: 'half', auto: true },
    nod2: { type: 'head', steps: [['head_nod', 180], [null, 120], ['head_nod', 180]], eyes: 'half' },
    shake: { type: 'head', steps: [['head_l', 150], ['head_r', 150], ['head_l', 150]] },
    turnout: { type: 'legs', frames: 'legs_turnout', auto: true },
  };
  const HEAD_OFF = { head_nod: [0, 1], head_l: [-1, 0], head_r: [1, 0] };   // fallback when anims.json has no `head`
  let REG = {}, PATCH = { eyes: [21, 20, 43, 29], legs: [32, 58, 45, 63] };  // PIL-style boxes [x0, y0, x1, y1)
  const BODY_OK = {};
  const AUTO_ON = { gesture: false, nod: false, look: false, weight: false };

  /** default auto-layer parameters (== planner_final.py AUTO). scenes.js may change ENG.AUTO before boot;
   *  episode.auto_gestures {gesture: 0.6 | {...}, nod: false | {...}, look, weight} overrides per channel. */
  ENG.AUTO = {
    margin: 0.35, tail_block: 1.0,
    gesture: {
      min_seg: 2.4, lead: 0.35, jitter: 0.6, slot: 4.5, p: 0.65, max_per_seg: 3, per_min: 7, via: 0.09, tail: 0.25,
      gap_after: 1.6, min_len: 0.9, max_repeat: 2, weights: { chest: 0.45, hold: 0.35, palm: 0.20 },
      hold: { chest: [1.1, 1.8], palm: [0.9, 1.4], hold: [1.6, 2.6], palm_r: [0.9, 1.4] },
      cue_keep: 0.6, cue_lead: 0.05, cue_room: 1.4, mult: 1.0,
    },
    nod: { p: 0.35, lead: 0.10, dur: 0.22, min_gap: 5.0, per_min: 4, min_line: 0.8 },
    look: { cue_p: 0.6, gap_p: 0.5, dur: [0.6, 0.9], min_gap: 5.0, per_min: 5, gap_min: 0.7, cue_delay: 0.08 },
    weight: { first: 25.0, force: 40.0, back_min: 15.0, back_force: 30.0, p: 0.5 },
  };
  ENG.autoPlan = [];
  ENG.autoInfo = { on: false, channels: AUTO_ON, notes: [] };

  // ---- content cues + scene looks (called by components.js / scenes.js while the scenes are built)
  ENG.cues = [];
  const CUE_N = {};
  /** content cue: something new appears on screen at t (card, list item, code card, node, table row, step …).
   *  scene: the calling scene (default: the scene at t).  A cue within 0.5 s of an earlier cue of the same scene is
   *  merged into it (a card and its first item are one event).  The auto layer turns cues into palm_r / look_r. */
  ENG.cue = (t, kind = 'card', scene) => {
    t = +t;
    if (!isFinite(t)) return null;
    const sid = scene || (SCENES.length ? SCENES[sceneAt(t)].id : '');
    if (ENG.cues.some(c => c.scene === sid && Math.abs(c.t - t) < 0.5)) return null;
    CUE_N[sid] = CUE_N[sid] == null ? 0 : CUE_N[sid] + 1;
    const c = { t, kind, scene: sid, i: CUE_N[sid] };
    ENG.cues.push(c);
    return c;
  };
  /** scenes.js: the character looks at the content from t0 to t1 (dir 'right' = look_r, 'up' = look_ur).
   *  Only on timelines with `episode` (v2); an explicit script expression (吃惊 / 认真 …) still wins.
   *  The auto layer keeps its own looks clear of it. */
  ENG.look = (t0, t1, dir = 'right') => {
    if (!(isFinite(t0) && isFinite(t1) && t1 > t0)) return;
    SCENE_LOOKS.push({ name: dir === 'up' || dir === 'upright' ? 'look_ur' : 'look_r', start: +t0, end: +t1 });
  };

  // ---- deterministic randomness (== planner_ref.py: mulberry32(fnv1a("<期号>:<key>")))
  function fnv1a(s) {
    let h = 0x811C9DC5;
    for (const b of new TextEncoder().encode(s)) { h ^= b; h = Math.imul(h, 0x01000193); }
    return h >>> 0;
  }
  function mulberry32(a) {
    return () => {
      a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  const rngOf = (ep, key) => mulberry32(fnv1a(`${ep}:${key}`));
  const r3 = x => +(+x).toFixed(3);                     // == Python round(x, 3) except exact binary ties
  const overlaps = (a0, a1, spans, mg = 0) => spans.some(([s, e]) => a0 < e + mg && a1 > s - mg);
  const rateOk = (times, t, perMin) => times.filter(x => t - 60 < x && x <= t).length < perMin;
  const SENT_END = /[。！!.]["”’）)]*\s*$/;
  const FAMILY = { palm_r: 'palm' };                   // same arm frames: one gesture for "at most 2 in a row"

  /** The auto layer (SPEC F.3), a line-by-line port of _skilltest/actions_v2/planner_final.py plan_auto():
   *  same timeline + cues + explicit actions -> the same plan (times rounded to ms).  ch: channels on/off.
   *  acts: every explicit action [{type, name, start, end}].  Pure function of its inputs. */
  function planAuto(cfg, ch, cues, acts) {
    const ep = D.episode && D.episode.number != null ? D.episode.number : 0;
    const segs = D.segments.map(s => Object.assign({}, s, { start: +s.start, end: +s.end }));
    const gaps = (D.gaps || []).map(g => Object.assign({}, g, { start: +g.start, end: +g.end }));
    const main = +D.main_duration;
    const wi = D.walk_in || { start: 0, end: 0 };
    const mg = cfg.margin, span = a => [+a.start, +a.end];
    const off = acts.filter(a => a.type === 'auto').map(span);
    const blkBody = acts.filter(a => ['body', 'pose', 'anim', 'head', 'shift'].includes(a.type)).map(span);
    blkBody.push([+wi.start, +wi.end], [main - cfg.tail_block, main + 1], ...off);
    const blkEyes = acts.filter(a => ['expr', 'pose', 'anim'].includes(a.type)).map(span);
    blkEyes.push(...acts.filter(a => a.type === 'body' && ['reach', 'point', 'think'].includes(a.name)).map(span));
    blkEyes.push([+wi.start, +wi.end], [main - cfg.tail_block, main + 1], ...off);
    const cueTs = cues.map(c => +c.t).sort((a, b) => a - b);
    const plan = [];

    // 1 -- gestures (a content cue in the first slot -> palm_r) --------------------------------------
    const G = cfg.gesture, mult = ch.gesture ? G.mult : 0;
    let lastEnd = -1e9;
    const hist = [], gTimes = [];
    if (ch.gesture) for (const s of segs) {
      const d = s.end - s.start;
      if (d < G.min_seg || overlaps(s.start, s.end, blkBody, 0)) continue;
      const n = Math.min(G.max_per_seg, 1 + Math.floor((d - G.min_seg) / G.slot));
      for (let k = 0; k < n; k++) {
        const r = rngOf(ep, `${s.id}:g${k}`);
        const keepR = r(), jit = r(), pickR = r(), holdR = r();
        let cueT = null;
        if (k === 0) {
          const hiT = Math.min(s.start + d / n, s.end - G.cue_room);
          const hit = cueTs.find(t => s.start + 0.15 <= t && t <= hiT);
          cueT = hit === undefined ? null : hit;
        }
        const fam = hist.slice(-G.max_repeat).map(x => FAMILY[x] || x);
        const repeatBlock = fam.length >= G.max_repeat && new Set(fam).size === 1;
        let t0, name;
        if (cueT !== null && !(repeatBlock && fam[fam.length - 1] === 'palm')) {
          if (keepR >= G.cue_keep * mult) continue;
          t0 = Math.max(s.start + 0.1, cueT - G.cue_lead); name = 'palm_r';
        } else {
          const keep = keepR < G.p * mult || (k === 0 && d >= 6.0 && mult >= 1.0);
          if (!keep) continue;
          t0 = s.start + G.lead + k * d / n + jit * G.jitter;
          let names = Object.keys(G.weights);
          if (repeatBlock) names = names.filter(x => (FAMILY[x] || x) !== fam[fam.length - 1]);
          let tot = 0; for (const x of names) tot += G.weights[x];
          let acc = 0; name = names[names.length - 1];
          for (const x of names) { acc += G.weights[x] / tot; if (pickR < acc) { name = x; break; } }
        }
        const [lo, hi] = G.hold[name];
        const t1 = Math.min(t0 + 2 * G.via + lo + (hi - lo) * holdR, s.end - G.tail);
        if (t1 - t0 < G.min_len || t0 < lastEnd + G.gap_after) continue;
        if (overlaps(t0, t1, blkBody, mg) || !rateOk(gTimes, t0, G.per_min)) continue;
        plan.push({ type: 'body', name, start: r3(t0), end: r3(t1), src: 'auto', key: `${s.id}:g${k}` });
        hist.push(name); gTimes.push(t0); lastEnd = t1;
      }
    }
    const bodySpans = blkBody.concat(plan.filter(p => p.type === 'body').map(span));
    const palmR = plan.filter(p => p.type === 'body' && p.name === 'palm_r').map(span);
    blkEyes.push(...palmR);

    // 2 -- nods at sentence ends (shown with half-closed eyes) ----------------------------------
    const N = cfg.nod;
    if (ch.nod) {
      let last = -1e9; const times = [];
      for (const s of segs) {
        if (acts.some(a => a.type === 'head' && a.start < s.end && a.end > s.start)) continue;
        const lines = Array.isArray(s.lines) && s.lines.length ? s.lines : [{ text: s.text || '', start: s.start, end: s.end }];
        lines.forEach((ln, j) => {
          const txt = String(ln.text == null ? '' : ln.text).trim();
          if (!SENT_END.test(txt) || +ln.end - +ln.start < N.min_line) return;
          const r = rngOf(ep, `${s.id}:n${j}`);
          if (r() >= N.p) return;
          const t0 = +ln.end - N.lead, t1 = t0 + N.dur;
          if (t0 < last + N.min_gap || overlaps(t0, t1, bodySpans, 0.05) || !rateOk(times, t0, N.per_min)) return;
          plan.push({ type: 'head', name: 'nod', start: r3(t0), end: r3(t1), src: 'auto', key: `${s.id}:n${j}` });
          times.push(t0); last = t0;
        });
      }
    }

    // 3 -- looks at the content (cues already covered by a palm_r are skipped) ------------------
    const L = cfg.look;
    if (ch.look) {
      const cands = [];
      cues.slice().sort((a, b) => a.t - b.t).forEach((c, k) => {
        const t = +c.t;
        if (palmR.some(([a, b]) => a - 0.1 <= t && t <= b)) return;
        cands.push([t + L.cue_delay, null, L.cue_p, `${c.scene == null ? '' : c.scene}:cue${'i' in c ? c.i : k}`]);
      });
      for (const g of gaps) {
        if (g.end - g.start < L.gap_min) continue;
        let ps = null;
        for (const s of segs) if (s.end <= g.start + 0.01 && (!ps || s.end > ps.end)) ps = s;
        cands.push([g.start + 0.1, g.end - 0.25, L.gap_p, `${ps ? ps.id : 'S00'}:gap`]);
      }
      cands.sort((a, b) => (a[0] - b[0]) || ((a[1] == null ? -Infinity : a[1]) - (b[1] == null ? -Infinity : b[1]) || 0)
        || (a[2] - b[2]) || (a[3] < b[3] ? -1 : a[3] > b[3] ? 1 : 0));
      let last = -1e9; const times = [];
      for (const [t0, cap, p, key] of cands) {
        const r = rngOf(ep, key);
        if (r() >= p) continue;
        let t1 = t0 + L.dur[0] + (L.dur[1] - L.dur[0]) * r();
        if (cap != null) t1 = Math.min(t1, cap);
        if (t1 - t0 < 0.35 || t0 < last + L.min_gap || overlaps(t0, t1, blkEyes, 0.1) || !rateOk(times, t0, L.per_min)) continue;
        plan.push({ type: 'look', name: 'look_r', start: r3(t0), end: r3(t1), src: 'auto', key });
        times.push(t0); last = t1;
      }
    }

    // 4 -- weight shift (P2; stickers and anims never get the legs patch) -----------------------
    const Wt = cfg.weight;
    if (ch.weight) {
      const blkLegs = acts.filter(a => ['anim', 'shift', 'pose'].includes(a.type)).map(span);
      const pts = segs.map(s => [s.start, s.id]).concat(gaps.map((g, i) => [g.start, `gap@${i}`]))
        .sort((a, b) => (a[0] - b[0]) || (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : 0));
      let state = 'stand', since = +wi.end, on = null;
      for (const [t, key] of pts) {
        if (t < +wi.end || t > main - cfg.tail_block || overlaps(t, t + 0.05, blkLegs, 0.2)) continue;
        const rr = rngOf(ep, `${key}:w`)();
        const dt = t - since;
        if (state === 'stand' && dt >= Wt.first && (rr < Wt.p || dt >= Wt.force)) { state = 'turnout'; since = t; on = t; }
        else if (state === 'turnout' && dt >= Wt.back_min && (rr < Wt.p || dt >= Wt.back_force)) {
          plan.push({ type: 'legs', name: 'turnout', start: r3(on), end: r3(t), src: 'auto', key });
          state = 'stand'; since = t; on = null;
        }
      }
      if (on !== null) plan.push({ type: 'legs', name: 'turnout', start: r3(on), end: r3(main - cfg.tail_block), src: 'auto', key: 'end' });
    }
    plan.sort((a, b) => (a.start - b.start) || (a.type < b.type ? -1 : a.type > b.type ? 1 : 0));
    return plan;
  }
  ENG.planAuto = planAuto;   // exposed for tests (the engine calls it once in buildChar)

  const has = n => FRAMES[n] && FRAMES[n].length;
  /** a breathing set <base>_m0/_m1/_m2 is complete */
  const breathOK = base => !!base && has(base + '_m0') && has(base + '_m1') && has(base + '_m2');
  const regOf = name => REG[name] || { type: 'body', frames: name };
  const bodyFrames = r => (Array.isArray(r.frames) ? r.frames : [r.frames]);
  /** all core frames of body action `name` exist (memoised; filled for the registry in buildV2) */
  const okBody = name => (name in BODY_OK ? BODY_OK[name] : (BODY_OK[name] = bodyFrames(regOf(name)).every(breathOK)));

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
    if (V2) { buildV2(); return; }
    if (SCENE_LOOKS.length) console.warn('ENG.look ignored: this timeline has no episode block (legacy mode)');
    // warn once for actions whose frames are missing (they fall back to idle)
    const need = new Set();
    ACT.expr.forEach(a => [0, 1, 2].forEach(m => need.add(`idle_${a.name}_m${m}`)));
    ACT.pose.forEach(a => need.add(`pose_${a.name}`));
    ACT.anim.forEach(a => need.add(a.name));
    ACT.body.forEach(a => [0, 1, 2].forEach(m => need.add(`${a.name}_m${m}`)));
    const miss = [...need].filter(n => !FRAMES[n]);
    if (miss.length && AS.anims) console.warn('character frames missing (falling back to idle): ' + miss.join(', '));
  }

  /** v2 setup: registry, frame checks (missing frames -> idle / channel off, one console.warn each), auto layer */
  function buildV2() {
    const an = AS.anims || {};
    REG = Object.assign({}, ACTION_DEFAULTS, an.actions || {});
    if (an.patch_rects) PATCH = Object.assign({}, PATCH, an.patch_rects);
    for (const [k, r] of Object.entries(REG)) if ((r.type || 'body') === 'body') okBody(k);
    SCENE_LOOKS.sort((a, b) => a.start - b.start);
    // explicit actions whose frames are missing: listed once, they fall back to idle / plain eyes
    const miss = new Set(), opt = new Set();
    const needB = (b, set) => { if (!breathOK(b)) set.add(b + '_m*'); };
    ACT.expr.forEach(a => needB('idle_' + a.name, miss));
    SCENE_LOOKS.forEach(a => needB('idle_' + a.name, miss));
    ACT.pose.forEach(a => { if (!has('pose_' + a.name)) miss.add('pose_' + a.name); });
    ACT.anim.forEach(a => { if (!has(a.name)) miss.add(a.name); });
    ACT.fx.forEach(a => { if (!has(a.name)) miss.add(a.name); });
    ACT.body.forEach(a => {
      const r = regOf(a.name);
      bodyFrames(r).forEach(b => needB(b, miss));
      if (r.via) needB(r.via, opt);
      if (r.look) needB('idle_' + r.look, opt);
      if (r.fx && !has(r.fx)) opt.add(r.fx);
    });
    ACT.head.forEach(a => {
      const r = regOf(a.name);
      (r.steps || [[a.name]]).forEach(([f]) => { if (f) needB(f, miss); });
      if (r.eyes) needB('idle_' + r.eyes, opt);
    });
    const acts = [];
    for (const k of Object.keys(ACT)) for (const a of ACT[k]) acts.push({ type: k, name: a.name, start: a.start, end: a.end });
    for (const a of SCENE_LOOKS) acts.push({ type: 'expr', name: a.name, start: a.start, end: a.end });
    ENG.charActs = acts;    // every explicit action the character plays (+ scene looks as expr): stats / tests
    if (miss.size && AS.anims) console.warn('character frames missing (these actions fall back to idle): ' + [...miss].join(', '));
    if (opt.size && AS.anims) console.warn('character frames missing (played without transition / gaze / fx): ' + [...opt].join(', '));
    // ---- auto layer
    const info = ENG.autoInfo, ag = D.episode.auto_gestures;
    if (ag === false) { info.notes.push('episode.auto_gestures = false'); return; }
    const cfg = JSON.parse(JSON.stringify(ENG.AUTO));
    const ch = { gesture: true, nod: true, look: true, weight: false };
    if (ag && typeof ag === 'object') {
      for (const k of Object.keys(ch)) {
        if (!(k in ag)) continue;
        const v = ag[k];
        if (k === 'gesture' && typeof v === 'number') { cfg.gesture.mult = v; ch.gesture = v > 0; }
        else if (v && typeof v === 'object') { Object.assign(cfg[k], v); ch[k] = true; }
        else ch[k] = !!v;
      }
    }
    const need = {
      gesture: ['chest', 'palm', 'hold'].filter(n => !BODY_OK[n]).map(n => bodyFrames(regOf(n)).join('/') + '_m*'),
      nod: (regOf('nod').steps || []).filter(([f]) => f && !breathOK(f)).map(([f]) => f + '_m*'),
      look: breathOK('idle_look_r') ? [] : ['idle_look_r_m*'],
      weight: has(regOf('turnout').frames || 'legs_turnout') ? [] : [regOf('turnout').frames || 'legs_turnout'],
    };
    const CN = { gesture: '手势', nod: '点头', look: '看向内容', weight: '换脚' };
    for (const k of Object.keys(ch)) {
      if (ch[k] && need[k].length) {
        ch[k] = false;
        const msg = `自动层「${CN[k]}」通道关闭：缺帧 ${need[k].join(', ')}`;
        info.notes.push(msg);
        console.warn(msg);
      }
    }
    Object.assign(AUTO_ON, ch);
    info.on = Object.values(ch).some(Boolean);
    info.mult = cfg.gesture.mult;
    info.cfg = cfg;
    if (!info.on) return;
    ENG.autoPlan = planAuto(cfg, ch, ENG.cues, acts);
    for (const p of ENG.autoPlan) if (AUTOP[p.type]) AUTOP[p.type].push(p);
    for (const k in AUTOP) AUTOP[k].sort((a, b) => a.start - b.start);
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
  /** legacy (v1) state at t: {anim, ms, loop, head (anim whose rows 0..35 go on top), x, pose, m} */
  function charStateV1(t) {
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
  function renderCharV1(t) {
    const st = charStateV1(t);
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

  /** v2 state at t (SPEC F.3 priority): walk-in > anim > sticker pose (auto layer paused) > body (explicit > auto
   *  gesture > idle) > head (explicit > auto nod; only while the body is idle) ; eyes: script expr > scene look >
   *  the body's own gaze > the head's eyes (nod: half) > auto look ; legs patch ; fx.
   *  -> {base, ms, loop, x, pose, m, body, head, eyes, esrc, patch: {src, dx, dy}, legs, fx: {name, ms}} */
  function charStateV2(t) {
    const m = mouthAt(t);
    const wi = D.walk_in || { start: 0, end: 0 };
    if (t < wi.end) {
      const p = clamp((t - wi.start) / Math.max(0.01, wi.end - wi.start));
      return { base: 'walk', ms: (t - wi.start) * 1000, loop: true, x: lerp(-400, 0, 1 - Math.pow(1 - p, 1.25)), pose: 'walk', m: 0 };
    }
    const an = activeAt(ACT.anim, t);
    if (an && has(an.name)) {
      let x = 0;
      if (an.name === 'walk') x = ENG.WALK_DRIFT * Math.sin(Math.PI * clamp((t - an.start) / Math.max(0.1, an.end - an.start)));
      return { base: an.name, ms: (t - an.start) * 1000, loop: FRAMES[an.name].loop, x, pose: an.name, m: 0 };
    }
    const ms = t * 1000;
    const po = activeAt(ACT.pose, t);
    if (po && has('pose_' + po.name)) return { base: 'pose_' + po.name, ms, loop: true, x: 0, pose: po.name, m: 0 };
    // body
    let bd = activeAt(ACT.body, t), bsrc = 'explicit';
    if (!bd) { bd = activeAt(AUTOP.body, t); bsrc = 'auto'; }
    let body = null, look = null, fx = null;
    if (bd && okBody(bd.name)) {
      const r = regOf(bd.name);
      const via = r.via && breathOK(r.via) ? r.via : null;
      const vs = via ? Math.min((r.via_ms || 80) / 1000, (bd.end - bd.start) / 3) : 0;
      const c0 = bd.start + vs, c1 = bd.end - vs;
      let fb;
      if (t < c0 || t >= c1) fb = via;
      else if (Array.isArray(r.frames)) fb = r.frames[Math.floor((t - c0) * 1000 / (r.phase_ms || 280)) % r.frames.length];
      else fb = r.frames;
      body = { name: bd.name, src: bsrc, frames: fb, phase: t < c0 ? 'in' : t >= c1 ? 'out' : 'core' };
      if (r.look) look = r.look;
      if (r.fx && t >= c0 && t < c1 && has(r.fx)) fx = { name: r.fx, ms: (t - c0) * 1000 };
    }
    // head (nod / shake): only while the body is idle
    let head = null;
    if (!body) {
      let hd = activeAt(ACT.head, t), hsrc = 'explicit';
      if (!hd) { hd = activeAt(AUTOP.head, t); hsrc = 'auto'; }
      if (hd) {
        const r = regOf(hd.name);
        let el = (t - hd.start) * 1000, step = null;
        for (const [f, dur] of r.steps || [[hd.name, Infinity]]) { if (el < dur) { step = f; break; } el -= dur; }
        if (step && breathOK(step)) {
          const meta = FRAMES[step + '_m0'].meta || {};
          const off = Array.isArray(meta.head) ? meta.head : HEAD_OFF[step] || [0, 0];
          head = { name: hd.name, src: hsrc, frames: step, off, eyes: r.eyes || null };
        }
      }
    }
    // eyes
    const ex = activeAt(ACT.expr, t), sl = activeAt(SCENE_LOOKS, t), al = activeAt(AUTOP.look, t);
    let eyes = null, esrc = null;
    for (const [e, src] of [[ex && ex.name, 'expr'], [sl && sl.name, 'scene'], [look, 'body'], [head && head.eyes, 'head'], [al && al.name, 'auto']]) {
      if (e && breathOK('idle_' + e)) { eyes = e; esrc = src; break; }
    }
    // legs (P2) + explicit fx
    const lg = AUTO_ON.weight ? activeAt(AUTOP.legs, t) : null;
    const legsKey = regOf('turnout').frames || 'legs_turnout';
    const legs = lg && has(legsKey) ? legsKey : null;
    if (!fx) { const fa = activeAt(ACT.fx, t); if (fa && has(fa.name)) fx = { name: fa.name, ms: (t - fa.start) * 1000 }; }
    let base, patch = null;
    if (head) { base = `${head.frames}_m${m}`; if (eyes) patch = { src: `idle_${eyes}_m${m}`, dx: head.off[0], dy: head.off[1] }; }
    else if (body) { base = `${body.frames}_m${m}`; if (eyes) patch = { src: `idle_${eyes}_m${m}`, dx: 0, dy: 0 }; }
    else base = eyes ? `idle_${eyes}_m${m}` : `idle_m${m}`;    // idle + eyes: the eye frame itself (as v1)
    return { base, ms, loop: true, x: 0, pose: body ? body.name : head ? head.name : eyes || 'idle', m, body, head, eyes, esrc, patch, legs, fx };
  }
  function renderCharV2(t) {
    const st = charStateV2(t);
    const tf = st.x ? `translateX(${st.x.toFixed(1)}px)` : '';
    if (charCv._tf !== tf) { charCv.style.transform = tf; charShadow.style.transform = tf; charCv._tf = tf; }
    let key;
    if (has(st.base)) {
      const i = frameAt(FRAMES[st.base], st.ms, st.loop);
      key = st.base + '#' + i;
      let pi = 0, fi = 0;
      if (st.patch) { pi = Math.min(i, FRAMES[st.patch.src].length - 1); key += `|eyes:${st.patch.src}#${pi}@${st.patch.dx},${st.patch.dy}`; }
      if (st.legs) key += '|' + st.legs;
      if (st.fx) { fi = frameAt(FRAMES[st.fx.name], st.fx.ms, FRAMES[st.fx.name].loop); key += `|${st.fx.name}#${fi}`; }
      if (key !== charKey) {
        const g = charCtx;
        g.clearRect(0, 0, 64, 64);
        const fr = FRAMES[st.base][i];
        if (fr.img) g.drawImage(fr.img, 0, 0);
        // patches REPLACE their rectangle (like PIL paste): clear it, then copy the same rectangle of the source frame
        const paste = (img, box, dx, dy) => {
          const [x0, y0, x1, y1] = box, w = x1 - x0, h = y1 - y0;
          g.clearRect(x0 + dx, y0 + dy, w, h);
          if (img) g.drawImage(img, x0, y0, w, h, x0 + dx, y0 + dy, w, h);
        };
        if (st.patch) paste(FRAMES[st.patch.src][pi].img, PATCH.eyes, st.patch.dx, st.patch.dy);
        if (st.legs) paste(FRAMES[st.legs][0].img, PATCH.legs, 0, 0);
        if (st.fx) { const ff = FRAMES[st.fx.name][fi]; if (ff.img) g.drawImage(ff.img, 0, 0); }
        charKey = key;
      }
    } else {
      const pose = st.pose === 'walk' ? 'walk' : st.body ? 'reach' : 'idle';
      const wp = pose === 'walk' ? Math.floor(st.ms / 145) % 2 : 0;
      key = `ph${pose}${st.m}${wp}`;
      if (key !== charKey) { drawPlaceholder(charCtx, pose, pose === 'walk' ? 0 : st.m, wp); charKey = key; }
    }
    ENG.charKey = charKey;  // exposed for tests (the canvas itself is tainted by file:// images)
  }
  const renderChar = V2 ? renderCharV2 : renderCharV1;
  /** for tests / check_layout: what the character shows at t (no drawing) */
  ENG.charState = t => (V2 ? charStateV2(t) : charStateV1(t));
  ENG.charMode = V2 ? 'v2' : 'legacy';

  // ---------------------------------------------------------------- subtitles (centred on the whole frame, x = 960)
  const SUB_MAXW = 1500;   // 1170 ± 750 -> x 420..1920: never reaches the character (x <= 380)
  const SUB_FS = 56;       // AI每日日报：字幕 56 px（原 44 px，用户要求手机上看得清）
  const SUBS = [];
  let subIdx = -2, TERM_RE = null;
  function buildSubs() {
    subsBox = el('div', '', stage); subsBox.id = 'subs';
    subStroke = el('div', 's stroke', subsBox); subFill = el('div', 's fill', subsBox);
    const terms = [...new Set([...(ENG.TERMS || []), ...(EP.terms || [])])].filter(Boolean).sort((a, b) => b.length - a.length);
    if (terms.length) TERM_RE = new RegExp('(?<![A-Za-z_\\-/.])(' + terms.map(s => s.replace(/[.*+?^${}()|[\]\\\/]/g, '\\$&')).join('|') + ')(?![A-Za-z_\\-])', 'g');
    const probe = el('span', '', stage); css(probe, { position: 'absolute', left: -9999, top: 0, whiteSpace: 'nowrap', font: `700 ${SUB_FS}px "Noto Sans SC"`, letterSpacing: '.02em' });
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
      s.fs = w > SUB_MAXW ? Math.max(32, Math.floor(SUB_FS * SUB_MAXW / w)) : SUB_FS;
      if (w * s.fs / SUB_FS > SUB_MAXW + 1) console.warn(`subtitle too long even at ${s.fs}px (may reach the character): ${s.text}`);
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
        const fs = s.fs + 'px', top = ((SUB_FS - s.fs) * 0.94) + 'px';
        subStroke.style.fontSize = subFill.style.fontSize = fs;
        subStroke.style.top = subFill.style.top = top;
      }
    }
  }

  // ---------------------------------------------------------------- chapter bar (Bocchi the Rock! palette), whole-video time
  const BAR_COLORS = (EP.bar_colors && EP.bar_colors.length) ? EP.bar_colors : ['#F2A0BD', '#F6C945', '#4A6FD0', '#E2463F'];   // AI每日日报: episode.json bar_colors
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
      const short = (EP.bar_labels && EP.bar_labels[c.id]) || title;   // AI每日日报：进度条用 ≤8 字宽的短标签，不写时间段
      const x0 = barX(c.start), x1 = barX(c.end), col = BAR_COLORS[i % BAR_COLORS.length];
      const bl = x0 + 2, bw = Math.max(4, x1 - x0 - 4);
      const bu = box('div', 'bBlk', U, bl, null, bw); bu.style.background = hexA(col, 0.46);
      const bp = box('div', 'bBlk', barP, bl, null, bw); bp.style.background = col;
      const full = title;
      const cands = [[short, 22], [short, 20], [short, 18], [String(i + 1), 18]].map(([t, f]) => ({ t, f, w: measure(t, f) }));
      chap.push({ c, bu, bp, full, short, x0: bl, x1: bl + bw, cx: bl + bw / 2, cands, lv: 0 });
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
      ch.abbrev = cd.t !== ch.short;     // 只有短标签也放不下、退成编号时，才在上方显示完整标题
    });
    pickEl = svg(bar, 0, 45, 24, 30,
      '<path d="M12 28 C 7 22 2 14 2 8 C 2 3 6 1.5 12 1.5 C 18 1.5 22 3 22 8 C 22 14 17 22 12 28 Z" fill="#EDEAE3" stroke="#141414" stroke-width="2.5" stroke-linejoin="round"/>' +
      '<path d="M8 8 L 16 8" stroke="#3D8BFF" stroke-width="2.4" stroke-linecap="round"/>');
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
  const TOC = { x: 1500, y: 20, w: 400, rowY: 50, rowH: 42, rowW: 380 };   // AI每日日报：目录字 25 px（原 19 px）
  ENG.tocRowRect = i => ({ x: TOC.x + 10, y: TOC.y + TOC.rowY + i * TOC.rowH, w: TOC.rowW, h: 40 });
  /** the TOC box once it is on screen ({x, y, w, h}), or null when the episode has no questions */
  ENG.tocRect = () => ((EP.questions || []).length ? { x: TOC.x, y: TOC.y, w: TOC.w, h: TOC.rowY + EP.questions.length * TOC.rowH + 5 } : null);
  /** top y for content spanning x left..right that must stay clear of the TOC (18 px gap); y itself when no overlap */
  ENG.safeTop = (y, right = W - 60, left = 440) => {
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
    // width: fit the longest question (row text at 25 px starts 50 px into a row)
    const probe = el('span', 'tocRow', stage); css(probe, { position: 'absolute', left: -9999, top: 0, width: 'auto', paddingLeft: 0 });
    let maxw = 0; for (const q of Q) { probe.textContent = q.text; maxw = Math.max(maxw, probe.offsetWidth); }
    probe.remove();
    TOC.rowW = Math.max(360, Math.min(620, Math.ceil(maxw) + 50 + 18));
    TOC.w = TOC.rowW + 20; TOC.x = W - 40 - TOC.w;
  }
  function buildHud() {
    const b = el('div', '', stage); b.id = 'badge';
    const num = EP.number != null ? '#' + pad2(EP.number) : '';
    el('div', 'b2', b, EP.badge_html || `原LAI如此${num ? `<span class="n">${num}</span>` : ''}`);   // AI每日日报: episode.json badge_html
    ENG.T(ENG.global, b, { o: 0 }).to(0.2, { o: 1 }, 0.6);

    const Q = EP.questions || [];
    if (!Q.length) return;
    const toc = el('div', '', stage); toc.id = 'toc';
    css(toc, { left: TOC.x, top: TOC.y, width: TOC.w, height: TOC.rowY + Q.length * TOC.rowH + 5 });
    el('div', 'kick', toc, EP.toc_kicker_html || '<b>本期目录</b>CONTENTS');   // AI每日日报: episode.json toc_kicker_html
    ENG.tocEl = toc;
    const rows = Q.map((q, i) => {
      const r = box('div', 'tocRow', toc, 10, TOC.rowY + i * TOC.rowH, TOC.rowW);
      el('div', 'bar', r);
      const num = el('div', 'num', r, String(i + 1));
      const ck = svg(r, 12, 8, 24, 24, '<path d="M4 12.5 L 10 18 L 20 6" fill="none" stroke="#3D8BFF" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>');
      el('span', 'txt', r, esc(q.text));
      return { r, num, path: ck.querySelector('path'), bar: r.querySelector('.bar') };
    });
    const tIn = ENG.tocInTime();
    ENG.tocTrack = ENG.T(ENG.global, toc, { o: 0 }).to(tIn + 0.35, { o: 1 }, 0.4);
    // AI每日日报：回顾场（scenes.js 在 buildScenes 时设 ENG.tocHideAt，那时目录还没建）淡出目录，给回顾卡让位
    if (ENG.tocHideAt != null && ENG.tocHideAt > tIn + 0.8) ENG.tocTrack.to(ENG.tocHideAt, { o: 0 }, 0.35);
    ENG.tocTimes = [];
    rows.forEach((row, i) => {
      const fx = (p, tr) => {
        const hl = Math.round(p.hl * 100) / 100, dd = Math.round(p.d * 100) / 100;
        // the text colour depends on hl AND d: cache the colour itself, so a seek straight past a tick (hl stays 0,
        // d jumps 0 -> 1) cannot leave a stale colour behind (renderAt stays a pure function of t in any seek order)
        const col = `rgba(237,234,227,${(0.5 + 0.5 * hl + 0.2 * p.d * (1 - hl)).toFixed(3)})`;
        if (tr._c2 !== col) { row.r.style.color = col; tr._c2 = col; }
        if (tr._h2 !== hl) {
          row.bar.style.opacity = hl;
          row.num.style.background = hl > 0.5 ? '#3D8BFF' : 'rgba(237,234,227,.5)';
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
