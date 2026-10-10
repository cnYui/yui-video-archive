/* 日报竖屏版引擎：window.TL（tl_v.js）→ DOM，renderAt(t) 只由 t 决定画面。 */
(function () {
  'use strict';
  const TL = window.TL, FPS = TL.fps;
  window.META = { FPS, FRAMES: TL.frames, TOTAL: TL.total };
  window.__ERR = [];
  window.__WARN = [];
  window.addEventListener('error', e => window.__ERR.push(String(e.message || e)));
  window.addEventListener('unhandledrejection', e => window.__ERR.push('rejection: ' + String(e.reason)));
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  const fadeWin = (t, s, e, f = 0.2) => clamp((t - s) / f) * clamp((e - t) / f);

  // ---------------------------------------------------------------- 场景
  const scenesEl = document.getElementById('scenes');
  const FRAME_W = 986;                                   // 框内宽 = 1000 − 2×7
  const S = TL.scenes.map((sc, idx) => {
    const root = el('div', 'sc');
    const head = el('div', 'head', `<div class="kicker">${sc.kicker}</div><div class="t1">${sc.t1}</div><div class="t2"><span>${sc.t2}</span></div>`);
    const frame = el('div', 'frame');
    frame.dataset.tag = sc.tag;
    const inner = el('div', 'inner');
    frame.appendChild(inner);
    const o = { sc, idx, root, head, frame, hl: null, chips: [], bigs: [], rows: [], checks: [] };
    if (sc.kind === 'news') {
      const img = el('img', 'snap'); img.src = sc.snap; inner.appendChild(img);
      const k = FRAME_W / sc.wh[0], [x, y, w, h] = sc.hl;
      const hl = el('div', 'hl'); hl.style.cssText = `left:${x * k}px;top:${y * k}px;width:${w * k}px;height:${h * k}px`;
      inner.appendChild(hl); o.hl = hl;
    } else {
      const ag = el('div', 'agenda');
      TL.agenda.forEach((a, i) => {
        const row = el('div', 'row', `<div class="th"><img src="${a.snap}"><s>✓</s></div><div class="tx"><b>${a.n}</b><span>${a.head}</span></div>`);
        ag.appendChild(row); o.rows.push(row); o.checks.push(row.querySelector('s'));
      });
      inner.appendChild(ag);
    }
    root.appendChild(head); root.appendChild(frame);
    if (sc.kind === 'news') {
      const wrap = el('div', 'cardwrap');
      const pts = el('div', 'pts');
      sc.pts.forEach((p, i) => { const c = el('div', 'pt', `<i>${i + 1}</i>${p}`); pts.appendChild(c); o.chips.push(c); });
      wrap.appendChild(pts); o.ptsEl = pts;
      sc.bigs.forEach(b => {
        const e = el('div', 'bigcard', `<div class="n">${b.n}${b.small ? `<small>${b.small}</small>` : ''}</div><div class="d">${b.d}</div>`);
        wrap.appendChild(e); o.bigs.push({ b, e });
      });
      root.appendChild(wrap);
    } else {
      const wrap = el('div', 'cardwrap');
      const bc = el('div', 'bigcard', sc.kind === 'open'
        ? '<div class="n">8<small>件事</small></div><div class="d">约 6 分钟 · 每条都附来源</div>'
        : '<div class="n">✓ 8<small>条看完</small></div><div class="d">来源都在简介里 · 明天见</div>');
      bc.style.opacity = 1; wrap.appendChild(bc); root.appendChild(wrap);
    }
    scenesEl.appendChild(root);
    return o;
  });

  // ---------------------------------------------------------------- 鲸鱼娘（日报的待机呼吸 12 帧 × 嘴型 m0/m1/m2 × 表情）
  const IDLE_D = [600, 140, 400, 140, 140, 520, 140, 60, 150, 70, 140, 140];
  const IDLE_TOT = IDLE_D.reduce((a, b) => a + b, 0);
  const IDLE_CUM = IDLE_D.reduce((acc, d) => { acc.push((acc.length ? acc[acc.length - 1] : 0) + d); return acc; }, []);
  const whalesEl = document.getElementById('whales');
  const W = {};
  ['idle', 'idle_happy', 'idle_surprised', 'idle_determined'].forEach(base => [0, 1, 2].forEach(m => {
    for (let i = 0; i < 12; i++) {
      const k = `${base}_m${m}/${String(i).padStart(2, '0')}`;
      const img = el('img', 'whale'); img.src = `assets/sprites/${base}_m${m}/${String(i).padStart(2, '0')}.png`;
      whalesEl.appendChild(img); W[k] = img;
    }
  }));
  let lastW = null;
  function whaleAt(t) {
    const mi = Math.max(0, Math.min(TL.mouth.length - 1, Math.round(t * FPS)));
    const m = TL.mouth[mi] | 0;
    let ex = null;
    for (const a of TL.expr) if (t >= a.s && t < a.e) ex = a.name;
    const base = ex ? `idle_${ex}` : 'idle';
    const ms = (t * 1000) % IDLE_TOT;
    let fi = 0; while (fi < 11 && ms >= IDLE_CUM[fi]) fi++;
    const key = `${base}_m${m}/${String(fi).padStart(2, '0')}`;
    if (key !== lastW) { if (lastW) W[lastW].style.visibility = 'hidden'; W[key].style.visibility = 'visible'; lastW = key; }
  }

  // ---------------------------------------------------------------- 进度条
  const progEl = document.getElementById('prog');
  const PR = []; for (let i = 0; i < 10; i++) { const e = el('i'); progEl.appendChild(e); PR.push(e); }
  const SCN_BY_PROG = {}; TL.scenes.forEach(s => { SCN_BY_PROG[s.prog] = s; });

  // ---------------------------------------------------------------- 字幕
  const subZh = document.getElementById('subZh'), subEn = document.getElementById('subEn');
  let lastSub = -2;
  function subAt(t) {
    let k = -1;
    for (let i = 0; i < TL.subs.length; i++) { const x = TL.subs[i]; if (t >= x.a && t < x.b) { k = i; break; } }
    if (k !== lastSub) {
      lastSub = k;
      if (k < 0) { subZh.textContent = ''; subEn.textContent = ''; }
      else { subZh.textContent = TL.subs[k].zh; subEn.textContent = TL.subs[k].en; }
    }
  }

  // ---------------------------------------------------------------- 第 0 帧 = 封面
  document.getElementById('coverImg').src = TL.cover;
  const cover0 = document.getElementById('cover0');

  // ---------------------------------------------------------------- 一次性的字宽适配（字体加载后）；用文字范围量真实宽度（块级元素的 scrollWidth 至少是容器宽）
  function textW(node) { const r = document.createRange(); r.selectNodeContents(node); return r.getBoundingClientRect().width; }
  function shrinkFont(node, maxW, min, what) {                 // 改 font-size（标题：里面没有别的字号）
    let k = 1; const base = parseFloat(getComputedStyle(node).fontSize);
    while (textW(node) > maxW && k > min) { k -= 0.03; node.style.fontSize = (base * k).toFixed(2) + 'px'; }
    if (k < 1) window.__WARN.push(`${what} 缩到 ${(k * 100).toFixed(0)}%`);
  }
  function shrinkZoom(node, maxW, min, what) {                 // 改 zoom（数字卡：数字里还套着单位小字）
    let k = 1;
    while (textW(node) > maxW && k > min) { k -= 0.03; node.style.zoom = k.toFixed(2); }
    if (k < 1) window.__WARN.push(`${what} 缩到 ${(k * 100).toFixed(0)}%`);
  }
  function fitAll() {
    S.forEach(o => {
      shrinkFont(o.head.querySelector('.t1'), 960, 0.6, `${o.sc.id} t1`);
      shrinkFont(o.head.querySelector('.t2'), 960, 0.6, `${o.sc.id} t2`);
      o.chips.forEach((c, i) => { let k = 1, base = parseFloat(getComputedStyle(c).fontSize); while (c.scrollWidth > c.clientWidth + 1 && k > 0.7) { k -= 0.03; c.style.fontSize = (base * k).toFixed(2) + 'px'; } if (k < 1) window.__WARN.push(`${o.sc.id} 要点${i + 1} 缩到 ${(k * 100).toFixed(0)}%`); });
      o.bigs.forEach(({ b, e }) => { shrinkZoom(e.querySelector('.n'), 680, 0.5, `${o.sc.id} 数字 ${b.n}`); shrinkZoom(e.querySelector('.d'), 680, 0.55, `${o.sc.id} 说明 ${b.d}`); });
    });
  }
  const imgs = Array.from(document.images);
  window.READY = (async () => {
    await document.fonts.ready;
    await Promise.all(imgs.map(i => i.complete ? Promise.resolve() : new Promise(r => { i.onload = i.onerror = r; })));
    await Promise.all(imgs.map(i => i.decode ? i.decode().catch(() => {}) : null));
    fitAll();
    return true;
  })();

  // ---------------------------------------------------------------- renderAt
  window.renderAt = function (t) {
    cover0.style.display = t < 0.5 / FPS ? 'block' : 'none';
    let curScene = TL.scenes[0];
    S.forEach((o, i) => {
      const sc = o.sc;
      const last = i === S.length - 1;
      const ti = i === 0 ? 1 : clamp((t - sc.s) / 0.22);
      const to = last ? 1 : clamp((sc.e + 0.12 - t) / 0.22);
      const op = ti * to;
      if (op <= 0.001) { o.root.style.visibility = 'hidden'; return; }
      if (t >= sc.s && t < sc.e) curScene = sc;
      o.root.style.visibility = 'visible';
      o.root.style.opacity = op.toFixed(3);
      o.root.style.transform = `translateY(${((1 - ti) * 16).toFixed(1)}px)`;
      if (sc.kind === 'news') {
        o.hl.style.opacity = clamp((t - (sc.s + 0.7)) / 0.3).toFixed(3);
        // 要点：按配音一句句亮；说过的变黑、当前的黄底
        let cur = -1; const seen = new Set();
        for (const p of sc.ptTimes) if (t >= p.s) { cur = p.pt; seen.add(p.pt); }
        o.chips.forEach((c, k) => { c.className = 'pt' + (k === cur ? ' cur' : seen.has(k) ? ' done' : ''); });
        let bo = 0;
        o.bigs.forEach(({ b, e }) => { const f = fadeWin(t, b.s, b.e); e.style.opacity = f.toFixed(3); bo = Math.max(bo, f); });
        o.ptsEl.style.opacity = (1 - bo).toFixed(3);
      } else if (sc.kind === 'open') {
        o.rows.forEach((r, k) => {
          const [a, b] = sc.agendaTimes[k];
          const state = t < a ? 'wait' : t < b ? 'cur' : 'done';
          r.className = 'row' + (state === 'cur' ? ' cur' : '');
          r.style.opacity = state === 'wait' ? '0.45' : '1';
        });
      } else {
        o.checks.forEach((c, k) => { c.style.opacity = clamp((t - (sc.s + 0.5 + k * 0.28)) / 0.2).toFixed(3); });
      }
    });
    whaleAt(t);
    subAt(t);
    // 进度条：已播黑、当前橙（按场景进度填充）、未播灰
    PR.forEach((e, i) => {
      const sc = SCN_BY_PROG[i];
      if (t >= sc.e) { e.className = 'done'; e.style.background = ''; }
      else if (t >= sc.s) {
        const p = clamp((t - sc.s) / (sc.e - sc.s)) * 100;
        e.className = 'cur';
        e.style.background = `linear-gradient(90deg, #FF4F1A ${p.toFixed(1)}%, rgba(20,20,19,.16) ${p.toFixed(1)}%)`;
      } else { e.className = ''; e.style.background = ''; }
    });
  };
})();
