/* 《原LAI如此》正片画面引擎 — 可复用画面组件（每期通用；从第 1 期 scenes.js 抽出来的）。
 *
 * 用法（scenes.js）：
 *   ENG.scene('S03', c => {                       // c = 本场的上下文，下面所有 c.xxx 都在这里
 *     const s0 = c.seg(0), s1 = c.seg(1);          // 本场第 0、1 段（按场内顺序）；c.segId('S03-12') 按段号取
 *     c.autoTitle(s0);                             // 章节标题卡：大字居中 → 收成左上角标题
 *     c.pointList({ x: 640, y: 300, w: 1040, kicker: 'KEY POINTS · 要点', title: 'Token 的三个特点',
 *       at: s1.start + 0.1, items: [{ text: '按片段切分', at: c.P(s1, '切分', 0.2) }, ...] });
 *   });
 *
 * 时间一律从数据推：c.seg(i).start / .end、c.P(seg, '台词短语', 兜底比例)、c.at('短语')（在本场里找）、c.gap(seg)、c.endTalk()。
 * 不许写死秒数（配音重做后时间会变）。短语找不到时用兜底比例，并在控制台 warn（不会让 render.py 失败）。
 *
 * 版面（1920×1080）：内容区 x 440–1860、y 80–900；左下 x ≤ 380、y ≥ 690 是角色；底部 y 922–1000 是字幕；
 *   右上 x ≥ 1538、y ≤ 170 是本期目录（出现后）。组件的默认坐标都在内容区内。
 * 动效克制：淡入 + 轻微上移 0.3–0.4 s，列表逐条出现，打勾 0.25 s；没有弹跳 / 闪烁 / 抖动。
 *
 * 通用返回值：多数组件返回 { el, tr, ... }：el 是根元素，tr 是它的 Track（可以继续 .to(t, {...}) / .out(t)）。
 * 参数里的 at = 出现时刻，until = 消失时刻（可省略：一直留到本场结束，场尾统一淡出）。
 *
 * 组件一览（详见各函数上方注释）：
 *   时间：c.seg  c.segs  c.segId  c.P  c.find  c.at  c.gap  c.endTalk
 *   基础：c.div  c.svg  c.T  c.show  c.card  c.ring  c.ringOn  c.arrow  c.chip  c.label  c.bracket  c.outAll
 *   标题：c.title  c.autoTitle  c.bigWord
 *   疑问：c.questionCards（疑问卡逐张出现，在 question_scene 最后一句结束时飞进右上目录）
 *   卡片：c.statement  c.pointList  c.summary
 *   代码：c.code  c.focus  c.unfocus  c.reveal（+ ENG.codeHTML 语法着色）
 *   图示：c.node  c.link  c.flow  c.token  c.compareTable  c.steps
 *   避让：ENG.safeTop(y, right, left) — 内容横跨 left..right 时，把 y 推到右上目录下方（pointList / summary / compareTable 不给 y 时自动用）
 *   角色：c.cue(t, kind) 登记内容提示点（下面的卡片、列表条目、代码卡、节点、表格行、步骤、疑问卡、示意界面出现时已自动登记；
 *         自动层据此让角色朝内容轻摊手 / 看过去）；c.look(t0, t1, 'right'|'up') 让角色在这段时间看向内容（只在 v2 时间轴生效）
 *   示意界面：c.browser（浏览器 / 应用窗口，带「示意」角标）  c.phone（手机）
 *   图标：ENG.ICON.doc/phone/server/key/x/check/lock/user/chat/cloud/chip（SVG 片段，自己画的，不用品牌 logo）
 */
(function () {
  'use strict';
  const { E, el, box, svg, esc, ph, phraseTime, gapAfter, EP } = ENG;

  // ------------------------------------------------------------------ syntax colouring for code cards
  function jsonHTML(s) {
    const re = /("(?:[^"\\]|\\.)*")(\s*:)?|(\btrue\b|\bfalse\b|\bnull\b|-?\b\d+(?:\.\d+)?\b)|(\{…\}|…+|×N)|([{}\[\],:])/g;
    let out = '', last = 0, m;
    while ((m = re.exec(s))) {
      out += esc(s.slice(last, m.index));
      if (m[1]) out += m[2] ? `<span class="k-key">${esc(m[1])}</span><span class="k-pun">${m[2]}</span>` : `<span class="k-str">${esc(m[1])}</span>`;
      else if (m[3]) out += `<span class="k-num">${m[3]}</span>`;
      else if (m[4]) out += `<span class="k-dim">${esc(m[4])}</span>`;
      else out += `<span class="k-pun">${esc(m[5])}</span>`;
      last = re.lastIndex;
    }
    return out + esc(s.slice(last));
  }
  /** one code line -> coloured HTML: // comments, "POST /path", "Header: value", else JSON-ish */
  function codeHTML(s) {
    let m;
    if (/^\s*(\/\/|#)/.test(s)) return `<span class="k-com">${esc(s)}</span>`;
    if ((m = s.match(/^(POST|GET|PUT|DELETE|PATCH)(\s+)(.*)$/))) return `<span class="k-kw">${m[1]}</span>${m[2]}<span class="k-path">${esc(m[3])}</span>`;
    if ((m = s.match(/^([A-Za-z][\w-]*)(:)(\s+)(.*)$/))) return `<span class="k-hdr">${esc(m[1])}</span><span class="k-pun">:</span>${m[3]}<span class="k-url">${esc(m[4])}</span>`;
    return jsonHTML(s);
  }
  ENG.codeHTML = codeHTML;
  ENG.jsonHTML = jsonHTML;

  // ------------------------------------------------------------------ icons (drawn, no brand logos)
  // Each returns SVG inner markup; put it in c.svg(x, y, w, h, ENG.ICON.server()) with the viewBox size noted.
  const ICON = ENG.ICON = {
    doc: (col = '#141414') => `<path d="M6 3 H22 L30 11 V37 H6 Z" fill="none" stroke="${col}" stroke-width="3" stroke-linejoin="round"/><path d="M22 3 V11 H30" fill="none" stroke="${col}" stroke-width="3" stroke-linejoin="round"/><path d="M11 19 H25 M11 25 H25 M11 31 H20" stroke="${col}" stroke-width="2.6" stroke-linecap="round"/>`,  // 36x40
    phone: (col = '#EDEAE3') => `<rect x="4" y="2" width="44" height="78" rx="9" fill="none" stroke="${col}" stroke-width="3.5"/><path d="M19 71 H33" stroke="${col}" stroke-width="3.5" stroke-linecap="round"/><rect x="11" y="13" width="30" height="8" rx="4" fill="${col}" opacity=".5"/><rect x="11" y="27" width="22" height="8" rx="4" fill="#3D8BFF"/>`,  // 52x82
    server: (col = '#EDEAE3') => `<rect x="3" y="3" width="70" height="22" rx="4" fill="none" stroke="${col}" stroke-width="3.5"/><rect x="3" y="31" width="70" height="22" rx="4" fill="none" stroke="${col}" stroke-width="3.5"/><rect x="3" y="59" width="70" height="22" rx="4" fill="none" stroke="${col}" stroke-width="3.5"/><circle cx="14" cy="14" r="3.2" fill="#3D8BFF"/><circle cx="14" cy="42" r="3.2" fill="#3D8BFF"/><circle cx="14" cy="70" r="3.2" fill="#3D8BFF"/><path d="M50 14 H64 M50 42 H64 M50 70 H64" stroke="${col}" stroke-width="3" stroke-linecap="round"/>`,  // 76x84
    key: (col = '#3D8BFF') => `<circle cx="16" cy="24" r="12" fill="none" stroke="${col}" stroke-width="5"/><path d="M28 24 H58 M50 24 V34 M42 24 V32" stroke="${col}" stroke-width="5" stroke-linecap="round"/>`,  // 60x48
    x: (col = '#D8342A') => `<circle cx="24" cy="24" r="22" fill="${col}"/><path d="M15 15 L33 33 M33 15 L15 33" stroke="#EDEAE3" stroke-width="5" stroke-linecap="round"/>`,  // 48x48
    check: (col = '#3D8BFF', w = 4) => `<path d="M5 14 L 12 21 L 25 6" fill="none" stroke="${col}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`,  // 30x28
    lock: () => `<rect x="1" y="7" width="12" height="9" rx="2" fill="#6E6A63"/><path d="M3.5 7 V5 A3.5 3.5 0 0 1 10.5 5 V7" fill="none" stroke="#6E6A63" stroke-width="2"/>`,  // 14x16
    user: (col = '#EDEAE3') => `<circle cx="30" cy="22" r="14" fill="none" stroke="${col}" stroke-width="4"/><path d="M6 76 C 8 52 20 44 30 44 C 40 44 52 52 54 76" fill="none" stroke="${col}" stroke-width="4" stroke-linecap="round"/>`,  // 60x80
    chat: (col = '#EDEAE3') => `<path d="M6 8 H66 Q72 8 72 14 V46 Q72 52 66 52 H30 L16 64 V52 H6 Q0 52 0 46 V14 Q0 8 6 8 Z" fill="none" stroke="${col}" stroke-width="3.5" stroke-linejoin="round"/><path d="M14 24 H58 M14 36 H44" stroke="${col}" stroke-width="3.5" stroke-linecap="round"/>`,  // 72x66
    cloud: (col = '#EDEAE3') => `<path d="M20 58 H66 A16 16 0 0 0 64 26 A22 22 0 0 0 22 22 A18 18 0 0 0 20 58 Z" fill="none" stroke="${col}" stroke-width="3.5" stroke-linejoin="round"/>`,  // 84x62
    chip: (col = '#EDEAE3') => `<rect x="14" y="14" width="48" height="48" rx="6" fill="none" stroke="${col}" stroke-width="3.5"/><rect x="28" y="28" width="20" height="20" rx="3" fill="#3D8BFF"/><path d="M26 4 V14 M38 4 V14 M50 4 V14 M26 62 V72 M38 62 V72 M50 62 V72 M4 26 H14 M4 38 H14 M4 50 H14 M62 26 H72 M62 38 H72 M62 50 H72" stroke="${col}" stroke-width="3" stroke-linecap="round"/>`,  // 76x76
  };
  const ICON_SIZE = { doc: [36, 40], phone: [52, 82], server: [76, 84], key: [60, 48], x: [48, 48], check: [30, 28], lock: [14, 16], user: [60, 80], chat: [72, 66], cloud: [84, 62], chip: [76, 76] };
  ENG.ICON_SIZE = ICON_SIZE;
  const CN = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];
  ENG.cnNum = n => (n <= 10 ? CN[n] : String(n));

  // ------------------------------------------------------------------ per-scene helper context
  ENG.ctx = S => {
    const root = S.root, sid = S.id, SCX = ENG.SC[sid];
    const c = {
      root, S, sid, sc: SCX,
      /** i-th segment of this scene (0-based; 99 = last) */
      seg: i => ENG.seg(sid, i),
      /** all segments of this scene */
      segs: () => SCX.segs.slice(),
      /** segment by 段号, e.g. c.segId('S03-12') */
      segId: id => ENG.segId(id),
      /** time the phrase is spoken in segment sg; fallback frac (0..1) of the segment */
      P: (sg, phrase, frac) => ph(sg, phrase, frac == null ? 0 : frac),
      /** gap (pure-visual pause) right after segment sg, or null */
      gap: sg => gapAfter(sg),
      /** end of the talking in this scene (closing gap start, else scene end - 0.4) */
      endTalk: () => ENG.endTalk(sid),
      /** new Track in this scene (evaluated only while the scene is on screen) */
      T: (e, init, fx) => ENG.T(S.tracks, e, init, fx),
      /** absolutely positioned <div class=cls> at (x, y) [w × h] with innerHTML (parent default: the scene root) */
      div: (cls, x, y, w, h, html, parent) => {
        const e = box('div', cls, parent || root, x, y, w, h, html);
        if (h != null && /(field|btn|chip)/.test(cls || '')) {
          const cs = getComputedStyle(e);
          e.style.lineHeight = (h - parseFloat(cs.borderTopWidth) - parseFloat(cs.borderBottomWidth)) + 'px';
        }
        return e;
      },
      /** absolutely positioned <svg> w × h with the given inner markup */
      svg: (x, y, w, h, inner, parent) => svg(parent || root, x, y, w, h, inner),
      /** content cue at t (something new appears; kind is a free label).  Cues within 0.5 s of an earlier cue of this
       *  scene merge.  The components below call it themselves; call it for hand-made content (c.div + c.show …) */
      cue: (t, kind = 'card') => (ENG.cue ? ENG.cue(t, kind, sid) : null),
      /** the character looks at the content from t0 to t1 (dir 'right' | 'up'); v2 timelines only */
      look: (t0, t1, dir = 'right') => (ENG.look ? ENG.look(t0, t1, dir) : undefined),
    };
    /** time of `phrase` in this scene's segments (searching from segment index `from`), or null — no warning */
    c.find = (phrase, from = 0) => {
      const ss = SCX.segs;
      for (let i = Math.max(0, from); i < ss.length; i++) { const t = phraseTime(ss[i], phrase); if (t != null) return t; }
      return null;
    };
    /** time of `phrase` searched through this scene's segments (from segment index `from`); fallback: `frac` of
     *  segment `from` (with a console warning).  Use when you do not want to name the segment: c.at('三件事', 0.5) */
    c.at = (phrase, frac = 0, from = 0) => {
      const t = c.find(phrase, from);
      if (t != null) return t;
      console.warn(`scene ${sid}: phrase not found "${phrase}" (using fallback)`);
      const sg = c.seg(from);
      return sg.start + (sg.end - sg.start) * frac;
    };
    /** element fades in (with a small rise dy) at t0, optionally fades out at t1 -> its Track */
    c.show = (e, t0, t1, dy = 12, d = 0.35) => {
      const tr = c.T(e, { o: 0, y: dy });
      tr.in(t0, d);
      if (t1 != null) tr.out(t1);
      return tr;
    };
    /** fade out a list of Tracks at t (e.g. clear the first half of a scene) */
    c.outAll = (tracks, t, d = 0.3) => tracks.forEach(tr => tr && tr.out(t, d));
    /** paper card (小票：顶部 2px 橙线 + 投影) */
    c.card = (x, y, w, h, parent) => c.div('card', x, y, w, h, '', parent);
    /** orange ring around a rect, visible t0..t1 */
    c.ring = (x, y, w, h, t0, t1, parent) => { const r = c.div('ring', x - 6, y - 6, w + 12, h + 12, '', parent); c.T(r, { o: 0 }).to(t0, { o: 1 }, 0.25).to(t1, { o: 0 }, 0.25); return r; };
    /** ring around an already laid-out element (measured at build time, before any track transform) */
    c.ringOn = (e, t0, t1, pad = 0) => { const r = e.getBoundingClientRect(); return c.ring(r.left - pad, r.top - pad, r.width + 2 * pad, r.height + 2 * pad, t0, t1); };
    /** straight arrow (x1,y1) -> (x2,y2).  o: {w: stroke, head: size, dash: '9 8', noHead, parent}. Returns the <svg>. */
    c.arrow = (x1, y1, x2, y2, col = '#3D8BFF', o = {}) => {
      const pad = 16, minx = Math.min(x1, x2) - pad, miny = Math.min(y1, y2) - pad;
      const w = Math.abs(x2 - x1) + 2 * pad, h = Math.abs(y2 - y1) + 2 * pad;
      const ax = x1 - minx, ay = y1 - miny, bx = x2 - minx, by = y2 - miny;
      const ang = Math.atan2(by - ay, bx - ax), hl = o.head || 16;
      const p1 = [bx - hl * Math.cos(ang - 0.45), by - hl * Math.sin(ang - 0.45)], p2 = [bx - hl * Math.cos(ang + 0.45), by - hl * Math.sin(ang + 0.45)];
      const sw = o.w || 4, dash = o.dash ? `stroke-dasharray="${o.dash}"` : '';
      const ex = o.noHead ? bx : bx - (hl * 0.6) * Math.cos(ang), ey = o.noHead ? by : by - (hl * 0.6) * Math.sin(ang);
      return c.svg(minx, miny, w, h,
        `<line x1="${ax}" y1="${ay}" x2="${ex}" y2="${ey}" stroke="${col}" stroke-width="${sw}" stroke-linecap="round" ${dash}/>` +
        (o.noHead ? '' : `<path d="M${p1[0]} ${p1[1]} L${bx} ${by} L${p2[0]} ${p2[1]}" fill="none" stroke="${col}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round"/>`), o.parent);
    };
    /** chip (pill label). o: {kind: ''|'o' (orange)|'dark'|'line', at, until, size (px), h, w, center} -> {el, tr} */
    c.chip = (html, x, y, o = {}) => {
      const e = c.div('chip' + (o.kind ? ' ' + o.kind : ''), x, y, o.w, o.h, html, o.parent);
      if (o.size) e.style.fontSize = o.size + 'px';
      if (o.center) e.style.textAlign = 'center';
      const tr = o.at != null ? c.show(e, o.at, o.until, 6) : null;
      return { el: e, tr };
    };
    /** free text label. o: {w, align: 'left'|'center'|'right', size, kind: ''|'o' (orange)|'s' (small grey), weight, at, until} */
    c.label = (html, x, y, o = {}) => {
      const e = c.div('lbl' + (o.kind ? ' ' + o.kind : ''), x, y, o.w, null, html, o.parent);
      if (o.align) e.style.textAlign = o.align;
      if (o.size) e.style.fontSize = o.size + 'px';
      if (o.weight) e.style.fontWeight = o.weight;
      const tr = o.at != null ? c.show(e, o.at, o.until, 6) : null;
      return { el: e, tr };
    };
    /** ⎵ bracket under a span (x..x+w at y) with a centred label below: "一来一回 ＝ 一次 API 调用" */
    c.bracket = (x, y, w, html, o = {}) => {
      const col = o.color || '#3D8BFF';
      const b = c.svg(x, y, w, 22, `<path d="M2 2 V 12 H ${w - 2} V 2" fill="none" stroke="${col}" stroke-width="3"/>`, o.parent);
      const l = c.div('lbl', x, y + 24, w, null, html, o.parent); l.style.textAlign = 'center'; l.style.fontSize = (o.size || 30) + 'px';
      const trs = o.at != null ? [c.show(b, o.at, o.until, 0), c.show(l, o.at + 0.1, o.until, 8)] : [];
      return { el: b, label: l, trs };
    };

    // ---------------------------------------------------------------- titles
    /** chapter title: big in the middle (cx, cy), then shrinks into the scene header (top-left, x 440 y 84) at o.morph
     *  (default: end of segment sg).  kicker: small orange mono line above ('PART 01 · 第一个问题'). */
    c.title = (text, kicker, sg, o = {}) => {
      const cx = o.cx || 1150, cy = o.cy || 450;
      const morph0 = o.morph != null ? o.morph : sg.end;
      // soft dark pool behind the centred title so the kicker never sits on a bright part of the background
      const pool = c.div('', cx - 640, cy - 190, 1280, 380, '');
      pool.style.background = 'radial-gradient(closest-side, rgba(14,16,28,.68), rgba(14,16,28,.4) 58%, rgba(14,16,28,0))';
      c.T(pool, { o: 0 }).to(sg.start, { o: 1 }, 0.45).to(morph0 - 0.05, { o: 0 }, 0.45, E.sine);
      const hdr = c.div('hdr', 440, 84, null, null, `<span class="sq"></span>${text}`);
      const w = hdr.offsetWidth, h = hdr.offsetHeight;
      const bx = cx - w / 2 - 440, by = cy - h / 2 - 84;
      const morph = o.morph != null ? o.morph : sg.end;
      c.T(hdr, { o: 0, x: bx, y: by + 16 }).to(sg.start + 0.05, { o: 1, y: by }, 0.45).to(morph, { x: 0, y: 0, s: 0.45 }, 0.6, E.inOut);
      const k = c.div('bigKick', cx - 400, cy - h / 2 - 44, 800, null, kicker || '');
      c.show(k, sg.start + 0.2, morph - 0.05, 10);
      const r = c.div('bigRule', cx - 60, cy + h / 2 + 22, 120, 3);
      c.T(r, { o: 0, s: 0.2 }).to(sg.start + 0.3, { o: 1, s: 1 }, 0.4).out(morph - 0.05, 0.25);
      return (ENG._lastTitle = { el: hdr, right: 440 + w * 0.45, morph });
    };
    /** c.title with text / kicker from episode.json: chapters[sid] (or the scene title); a question chapter gets
     *  '一、…' and 'PART 0N · 第N个问题'.  o.text / o.kicker override; other o as c.title. */
    c.autoTitle = (sg, o = {}) => {
      const n = ENG.questionOf(sid), name = ENG.chapterTitle(sid);
      const text = o.text || (n ? `${ENG.cnNum(n)}、${name}` : name);
      const kicker = o.kicker != null ? o.kicker : (n ? `PART ${ENG.pad2(n)} · 第${ENG.cnNum(n)}个问题` : 'MORE · 延伸');
      return c.title(text, kicker, sg || c.seg(0), o);
    };
    /** opening word: kicker + huge mono word + orange bar + subtitle line, centred at (cx, cy).
     *  o: {text, kicker, sub, at, until, cx=1150, cy=480, size=230 (px, auto-shrinks to fit 1100 px), scrim=true} */
    c.bigWord = (o) => {
      const cx = o.cx || 1150, cy = o.cy || 480, at = o.at;
      const trs = [];
      if (o.scrim !== false) {
        const scrim = c.div('', cx - 540, cy - 230, 1080, 480, '');
        scrim.style.background = 'radial-gradient(closest-side, rgba(14,16,28,.55), rgba(14,16,28,.32) 55%, rgba(14,16,28,0))';
        trs.push(c.show(scrim, at - 0.1, o.until, 0, 0.5));
      }
      if (o.kicker) { const k = c.div('bigKick', cx - 400, cy - 158, 800, null, o.kicker); trs.push(c.show(k, at + 0.1, o.until, 8)); }
      const big = c.div('', cx - 700, cy - 120, 1400, 240, '');
      big.innerHTML = `<span class="bw">${esc(o.text)}</span><span style="display:inline-block;width:34px;height:170px;background:var(--orange);margin-left:26px;vertical-align:-6px"></span>`;
      Object.assign(big.style, { textAlign: 'center', lineHeight: '240px', whiteSpace: 'nowrap' });
      const bw = big.querySelector('.bw');
      let size = o.size || 230;
      bw.style.font = `800 ${size}px var(--mono)`; bw.style.letterSpacing = '.04em'; bw.style.color = 'var(--paper)';
      const fontFor = s => `800 ${s}px ${/[一-鿿]/.test(o.text) ? 'var(--cjk)' : 'var(--mono)'}`;
      bw.style.font = fontFor(size);
      while (bw.offsetWidth > 1100 && size > 60) { size -= 10; bw.style.font = fontFor(size); }
      trs.push(c.show(big, at, o.until, 16, 0.45));
      c.cue(at, 'word');
      if (o.sub) {
        const sub = c.div('note', cx - 500, cy + 146, 1000, null, o.sub);
        Object.assign(sub.style, { textAlign: 'center', fontSize: '34px', fontWeight: '700' });
        trs.push(c.show(sub, at + 0.35, o.until, 8));
      }
      return { el: big, trs };
    };

    // ---------------------------------------------------------------- question cards -> TOC
    /** The question scene's cards: a title ('你可能也想问') and one numbered paper card per question, each appearing at
     *  at[i]; at ENG.tocInTime() (end of question_scene's last line) they shrink and fly into the top-right TOC rows.
     *  o: {items (default: episode.questions[].text + '？'), at: [t...] (required), title, titleAt, x=650, y=236, w=1000} */
    c.questionCards = (o) => {
      const items = o.items || (EP.questions || []).map(q => /[？?]$/.test(q.text) ? q.text : q.text + '？');
      const n = items.length, x = o.x || 650, y0 = o.y || 236, w = o.w || 1000;
      const step = Math.min(162, Math.floor((880 - y0) / Math.max(1, n))), h = Math.min(132, step - 24);
      const tIn = ENG.tocInTime(), hasToc = (EP.questions || []).length > 0;
      if (o.title !== false) {
        const title = c.div('', x, y0 - 120, w, 70, o.title || '你可能也想问');
        Object.assign(title.style, { textAlign: 'center', font: '900 54px var(--cjk)', color: 'var(--paper)', letterSpacing: '.06em' });
        const ta = o.titleAt != null ? o.titleAt : o.at[0] - 0.3;
        c.show(title, ta, tIn, 10);
        c.show(c.div('bigRule', x + w / 2 - 40, y0 - 40, 80, 3), ta + 0.15, tIn, 0);
      }
      const cards = items.map((q, i) => {
        const y = y0 + i * step;
        const cd = c.card(x, y, w, h);
        const fs = Math.min(46, Math.floor(h * 0.36));
        const nb = c.div('', 30, (h - fs * 1.75) / 2, fs * 1.75, fs * 1.75, String(i + 1), cd);
        Object.assign(nb.style, { background: 'var(--orange)', color: 'var(--paper)', font: `800 ${fs}px var(--mono)`, textAlign: 'center', lineHeight: fs * 1.75 + 'px', borderRadius: '6px' });
        const tx = c.div('', 60 + fs * 1.75, 0, w - 200 - fs * 1.75, h, esc(q), cd);
        Object.assign(tx.style, { font: `800 ${fs}px var(--cjk)`, lineHeight: h + 'px', whiteSpace: 'nowrap' });
        while (tx.scrollWidth > tx.clientWidth + 1 && parseFloat(tx.style.fontSize || fs) > 26) tx.style.fontSize = (parseFloat(getComputedStyle(tx).fontSize) - 2) + 'px';
        c.div('kicker', w - 200, 14, 180, null, `QUESTION ${ENG.pad2(i + 1)}`, cd).style.textAlign = 'right';
        cd.style.transformOrigin = '0 0';
        const trc = c.T(cd, { o: 0, y: 14 });
        const tCard = (o.at[i] != null ? o.at[i] : o.at[o.at.length - 1] + 0.3 * i) + 0.05;
        trc.in(tCard, 0.38);
        c.cue(tCard, 'question');
        if (hasToc) {
          const r = ENG.tocRowRect(i);
          trc.to(tIn, { x: r.x - x, y: r.y - y, s: r.w / w }, 0.7, E.inOut).to(tIn + 0.4, { o: 0 }, 0.3, E.sine);
        } else trc.out(tIn);
        return { el: cd, tr: trc };
      });
      return { cards, tIn };
    };

    // ---------------------------------------------------------------- cards
    /** statement card: small lead line + one big line ('接的是：' / 'DeepSeek 大模型的 API').
     *  o: {x=610, y=320, w=1080, kicker, lead, main, size=68, at, mainAt, until} -> {el, tr} */
    c.statement = (o) => {
      const x = o.x != null ? o.x : 610, y = o.y != null ? o.y : 320, w = o.w || 1080, size = o.size || 68;
      const hh = 64 + (o.lead ? 66 : 0) + size * 1.45 + 34;
      const st = c.card(x, y, w, hh);
      if (o.kicker) c.div('kicker', 44, 26, w - 88, null, o.kicker, st);
      let yy = o.kicker ? 64 : 34;
      if (o.lead) { const l1 = c.div('', 44, yy, w - 88, 60, o.lead, st); l1.style.font = '700 38px var(--cjk)'; l1.style.color = '#4A4741'; yy += 66; }
      const l2 = c.div('', 44, yy, w - 88, size * 1.45, o.main, st);
      Object.assign(l2.style, { font: `900 ${size}px var(--cjk)`, whiteSpace: 'nowrap', lineHeight: size * 1.45 + 'px' });
      const tr = c.show(st, o.at, o.until, 14);
      c.cue(o.at, 'statement');
      if (o.mainAt != null) { c.show(l2, o.mainAt, null, 8); c.cue(o.mainAt, 'statement'); }
      return { el: st, tr, main: l2 };
    };
    /** key-point list card: kicker, title, dashed rule, then items appearing one by one.
     *  o: {x=640, y=220, w=1040, kicker, title, at, until, items: [{text, sub, at, mark: 'num'|'x'|'check'|'none'}],
     *      mark (default for items: 'num'), fs=38, step=76} -> {el, tr, rows[]} */
    c.pointList = (o) => {
      const x = o.x != null ? o.x : 640, w = o.w || 1040, y = o.y != null ? o.y : ENG.safeTop(220, x + w, x);
      const fs = o.fs || 38, step = o.step || Math.round(fs * 2);
      const top = o.title ? 142 : (o.kicker ? 64 : 30);
      const hh = top + o.items.length * step + 30;
      const cd = c.card(x, y, w, hh);
      if (o.kicker) c.div('kicker', 40, 22, w - 80, null, o.kicker, cd);
      if (o.title) {
        const tt = c.div('', 40, 48, w - 80, 56, o.title, cd); tt.style.font = '800 42px var(--cjk)'; tt.style.whiteSpace = 'nowrap';
        c.div('dash', 40, 116, w - 80, null, '', cd);
      }
      const rows = o.items.map((it, i) => {
        const spec = typeof it === 'string' ? { text: it } : it;
        const mk = spec.mark || o.mark || 'num';
        const lead = mk === 'num' ? `<span class="no o">${i + 1}</span>`
          : mk === 'x' ? `<svg class="x" viewBox="0 0 48 48">${ICON.x()}</svg>`
          : mk === 'check' ? `<svg class="x" viewBox="0 0 30 28">${ICON.check('#3D8BFF', 4)}</svg>` : '';
        const r = c.div('item', 44, top + i * step, null, null, `${lead}${spec.text}${spec.sub ? `<span class="sub">${spec.sub}</span>` : ''}`, cd);
        r.style.fontSize = fs + 'px';
        const tItem = spec.at != null ? spec.at : (o.at + 0.4 + 0.5 * i);
        const tr = c.show(r, tItem, null, 8);
        return { el: r, tr, t: tItem };
      });
      const tr = c.show(cd, o.at, o.until, 14);
      c.cue(o.at, 'list');
      rows.forEach(r => c.cue(r.t, 'item'));
      return { el: cd, tr, rows };
    };
    /** summary card (本期总结): numbered rows [main html, sub text] appearing at at[i].
     *  o: {x=540, y=180, w=1220, kicker ('SUMMARY · 原LAI如此 #NN'), title='本期总结', items: [[main, sub]], at: [t...],
     *      cardAt, sign (bottom-right line, default '原LAI如此 #NN · 下期见'), signAt} -> {el, rows[]} */
    c.summary = (o) => {
      const x = o.x != null ? o.x : 540, w = o.w || 1220, y = o.y != null ? o.y : ENG.safeTop(180, x + w, x);
      // rows share the height between the header and y 870 (the sign line must end above the subtitles at 922)
      const n = o.items.length, rowH = Math.max(76, Math.min(128, Math.floor((870 - y - 178) / Math.max(1, n))));
      const compact = rowH < 110;
      const num = EP.number != null ? `#${ENG.pad2(EP.number)}` : '';
      const cd = c.card(x, y, w, 158 + n * rowH + 20);
      c.div('kicker', 44, 26, w - 88, null, o.kicker || `SUMMARY · 原LAI如此 ${num}`, cd);
      const tt = c.div('', 44, 50, 600, 66, o.title || '本期总结', cd); tt.style.font = '900 50px var(--cjk)';
      const dbl = c.div('', 44, 128, w - 88, 7, '', cd);
      dbl.style.background = 'linear-gradient(var(--ink),var(--ink)) 0 0/100% 3px no-repeat, linear-gradient(var(--ink),var(--ink)) 0 100%/100% 1.5px no-repeat';
      c.show(cd, o.cardAt != null ? o.cardAt : o.at[0] - 0.4, null, 14);
      c.cue(o.cardAt != null ? o.cardAt : o.at[0] - 0.4, 'summary');
      const rows = o.items.map(([a, b], i) => {
        const r = c.div('', 44, 158 + i * rowH, w - 88, rowH - 10, '', cd);
        const nd = compact ? 46 : 56;
        const no = c.div('', 0, compact ? 8 : 12, nd, nd, String(i + 1), r);
        Object.assign(no.style, { borderRadius: '50%', background: 'var(--orange)', color: 'var(--paper)', font: `800 ${compact ? 26 : 30}px var(--mono)`, textAlign: 'center', lineHeight: nd + 'px' });
        const m = c.div('', 80, compact ? 2 : 4, w - 180, 54, a, r); Object.assign(m.style, { font: `800 ${compact ? 30 : 36}px var(--cjk)`, whiteSpace: 'nowrap' });
        if (b) { const sb = c.div('', 80, compact ? 46 : 58, w - 180, 40, esc(b), r); Object.assign(sb.style, { font: `500 ${compact ? 22 : 26}px var(--cjk)`, color: '#5A564F', whiteSpace: 'nowrap' }); }
        if (i < n - 1) c.div('dash', 0, rowH - 14, w - 88, null, '', r);
        const tRow = o.at[i] != null ? o.at[i] : o.at[o.at.length - 1] + 0.5;
        c.cue(tRow, 'summary');
        return { el: r, tr: c.show(r, tRow, null, 10) };
      });
      if (o.sign !== false) {
        const sig = c.div('', x + w - 500, y + 158 + n * rowH + 32, 500, 40, o.sign || `原LAI如此 <span class="mono or">${num}</span> · 下期见`);
        Object.assign(sig.style, { font: '700 26px var(--cjk)', textAlign: 'right', color: 'rgba(237,234,227,.85)' });
        c.show(sig, o.signAt != null ? o.signAt : o.at[n - 1] + 1.0, null, 6);
      }
      return { el: cd, rows };
    };

    // ---------------------------------------------------------------- code cards
    /** code card (ink background, JetBrains Mono, '示意·已简化' top-right).
     *  o: {x, y, w, h, title, kicker, sy (false = no 示意 tag), fs=22, lh=40, top=58, parent,
     *      lines: [string | {t, c (comment, CJK), cLate (comment starts hidden), hide (line starts hidden), dim}]}
     *  -> {el, tr (starts hidden: call card.tr.in(t)), L: [{el, tr, ctr (comment track)}]} */
    c.code = o => {
      const fs = o.fs || 22, lh = o.lh || 40, top = o.top || 58;
      const cardEl = c.div('code', o.x, o.y, o.w, o.h, '', o.parent);
      if (o.title !== false) el('div', 'ctitle', cardEl, `<b>${o.title || ''}</b>${o.kicker || ''}`);
      if (o.sy !== false) el('div', 'csy', cardEl, '示意·已简化');
      const L = (o.lines || []).map((ln, i) => {
        const spec = typeof ln === 'string' ? { t: ln } : ln;
        const d = box('div', 'cl', cardEl, null, top + i * lh, null, lh);
        d.style.lineHeight = lh + 'px'; d.style.fontSize = fs + 'px';
        el('div', 'band', d);
        el('span', 'tx' + (spec.dim ? ' k-dim' : ''), d, spec.dim ? esc(spec.t) : codeHTML(spec.t));
        const tr = c.T(d, { o: spec.hide ? 0 : 1, hl: 0 });
        let ctr = null;
        if (spec.c) { const cs = el('span', 'tx k-com k-cn', d, esc(spec.c)); ctr = c.T(cs, { o: spec.cLate ? 0 : 1 }); }
        return { el: d, tr, ctr, hide: !!spec.hide };
      });
      const tr = c.T(cardEl, { o: 0, y: 14 });
      const tin = tr.in;                      // the caller shows the card with card.tr.in(t): that moment is a cue
      tr.in = function (t, d, extra) { c.cue(t, 'code'); return tin.call(this, t, d, extra); };
      return { el: cardEl, tr, L };
    };
    const vis = (ln, t) => !ln.hide || (ln.showT != null && t >= ln.showT);
    /** from t: highlight lines idxs of a code card (orange band), dim the others to dimTo */
    c.focus = (card, t, idxs, dimTo = 0.42) => card.L.forEach((ln, i) => {
      if (!vis(ln, t)) return;
      ln.tr.to(t, idxs.includes(i) ? { hl: 1, o: 1 } : { hl: 0, o: dimTo }, 0.3);
    });
    /** from t: all visible lines back to normal */
    c.unfocus = (card, t) => card.L.forEach(ln => { if (vis(ln, t)) ln.tr.to(t, { hl: 0, o: 1 }, 0.3); });
    /** from t: show a line that started hidden ({hide: true}) */
    c.reveal = (card, i, t) => { const ln = card.L[i]; ln.showT = t; ln.tr.to(t, { o: 1 }, 0.3); c.cue(t, 'line'); };

    // ---------------------------------------------------------------- diagrams
    /** box node (dark translucent, or paper).  o: {x, y, w=260, h=200, title, sub, icon ('server' | ENG.ICON key),
     *  iconColor, paper, dashed, size (title px), at, until, parent} -> {el, tr, rect} */
    c.node = (o) => {
      const w = o.w || 260, h = o.h || 200;
      const n = c.div('node' + (o.paper ? ' paper' : ''), o.x, o.y, w, h, '', o.parent);
      if (o.dashed) n.style.borderStyle = 'dashed';
      let ty = h / 2 - 22;
      if (o.icon && ICON[o.icon]) {
        const [iw, ih] = ICON_SIZE[o.icon] || [60, 60];
        const sc = Math.min(1, (h * 0.42) / ih);
        c.svg((w - iw * sc) / 2, 22, iw * sc, ih * sc, `<g transform="scale(${sc})">${ICON[o.icon](o.iconColor || (o.paper ? '#141414' : '#EDEAE3'))}</g>`, n);
        ty = 22 + ih * sc + 14;
      } else if (o.sub) ty = h / 2 - 40;
      if (o.title) { const t1 = c.div('nt', 0, ty, w, null, o.title, n); t1.style.position = 'absolute'; if (o.size) t1.style.fontSize = o.size + 'px'; }
      if (o.sub) { const t2 = c.div('ns', 0, ty + (o.size || 34) + 16, w, null, o.sub, n); t2.style.position = 'absolute'; }
      const tr = o.at != null ? c.show(n, o.at, o.until, 12) : null;
      if (o.at != null) c.cue(o.at, 'node');
      return { el: n, tr, rect: { x: o.x, y: o.y, w, h } };
    };
    /** arrow between two nodes (their rects) on the facing edges.  o: {lane (px offset from the centre line, e.g. -40 /
     *  +40 for a request / response pair), color, dash, label, labelKind ('o' | ''), at, until, gap=6}
     *  -> {el, tr, a:[x,y], b:[x,y], label} */
    c.link = (A, B, o = {}) => {
      const ra = A.rect || A, rb = B.rect || B, gap = o.gap != null ? o.gap : 6, lane = o.lane || 0;
      const acx = ra.x + ra.w / 2, acy = ra.y + ra.h / 2, bcx = rb.x + rb.w / 2, bcy = rb.y + rb.h / 2;
      let a, b;
      if (Math.abs(bcx - acx) >= Math.abs(bcy - acy)) {   // side by side
        const dir = bcx > acx ? 1 : -1;
        a = [dir > 0 ? ra.x + ra.w + gap : ra.x - gap, acy + lane];
        b = [dir > 0 ? rb.x - gap : rb.x + rb.w + gap, bcy + lane];
      } else {                                             // stacked
        const dir = bcy > acy ? 1 : -1;
        a = [acx + lane, dir > 0 ? ra.y + ra.h + gap : ra.y - gap];
        b = [bcx + lane, dir > 0 ? rb.y - gap : rb.y + rb.h + gap];
      }
      const e = c.arrow(a[0], a[1], b[0], b[1], o.color || '#3D8BFF', { dash: o.dash, w: o.w, head: o.head });
      const tr = c.T(e, { o: 0 });
      if (o.at != null) tr.to(o.at, { o: 1 }, 0.35);
      if (o.until != null) tr.out(o.until);
      let label = null;
      if (o.label) {
        const lx = Math.min(a[0], b[0]), lw = Math.max(120, Math.abs(b[0] - a[0]));
        label = c.label(o.label, lx, Math.min(a[1], b[1]) - 46 + (lane > 0 ? 64 : 0), { w: lw, align: 'center', kind: o.labelKind != null ? o.labelKind : 'o', at: o.at != null ? o.at + 0.1 : null, until: o.until });
      }
      return { el: e, tr, a, b, label };
    };
    /** a pill token moving from -> to (e.g. '请求' along a request arrow).  o: {text, kind: 'req'|'res', from:[x,y],
     *  to:[x,y] (token's top-left positions), at, dur=1.2} -> {el, tr} */
    c.token = (o) => {
      const tk = c.div('token ' + (o.kind || 'req'), o.from[0], o.from[1], null, null, esc(o.text));
      const dur = o.dur || 1.2;
      const tr = c.T(tk, { o: 0, x: 0, y: 0 }).to(o.at, { o: 1 }, 0.25)
        .to(o.at + 0.25, { x: o.to[0] - o.from[0], y: o.to[1] - o.from[1] }, dur, E.inOut).to(o.at + 0.3 + dur, { o: 0 }, 0.3);
      return { el: tk, tr };
    };
    /** nodes + links in one call.  o: {nodes: [{id, ...c.node options}], links: [{from, to, ...c.link options}], until}
     *  -> {nodes: {id: node}, links: [...]}.  Node/link `until` defaults to o.until. */
    c.flow = (o) => {
      const nodes = {};
      for (const n of o.nodes) nodes[n.id] = c.node(Object.assign({ until: o.until }, n));
      const links = (o.links || []).map(l => c.link(nodes[l.from], nodes[l.to], Object.assign({ until: o.until }, l)));
      return { nodes, links };
    };
    /** comparison table on a paper card.  o: {x=440, y=250, w=1420, kicker, title, tip ('可截图保存'), cols: [header...],
     *  colX: [x...] (optional; default equal split), rows: [[cell...]] (first column bold CJK, others mono), rowH=92,
     *  foot, at, rowStep=0.25 (s between rows), until} -> {el, tr, rows[]} */
    c.compareTable = (o) => {
      const x = o.x != null ? o.x : 440, w = o.w || 1420, y = o.y != null ? o.y : ENG.safeTop(250, x + w, x), rowH = o.rowH || 92;
      const n = o.rows.length, hh = 178 + n * rowH + (o.foot ? 70 : 20);
      const tb = c.card(x, y, w, hh);
      tb.classList.add('tbl');
      if (o.kicker) c.div('kicker', 36, 22, w - 72, null, o.kicker, tb);
      if (o.title) { const tt = c.div('', 36, 46, w - 400, 50, o.title, tb); tt.style.font = '800 36px var(--cjk)'; }
      if (o.tip) { const tip = c.div('', w - 360, 56, 320, 40, o.tip, tb); Object.assign(tip.style, { font: '500 22px var(--cjk)', color: '#6E6A63', textAlign: 'right' }); }
      const colX = o.colX || o.cols.map((_, i) => 36 + i * Math.floor((w - 72) / o.cols.length));
      const hr = c.div('tr', 0, 118, null, 40, '', tb);
      o.cols.forEach((h, i) => c.div('c hd', colX[i], 0, null, null, h, hr));
      c.div('', 36, 160, w - 72, 3, '', tb).style.background = 'var(--ink)';
      const tr = c.show(tb, o.at, o.until, 14);
      c.cue(o.at, 'table');
      const rows = o.rows.map((r, j) => {
        const row = c.div('tr', 0, 178 + j * rowH, null, rowH - 12, '', tb);
        r.forEach((v, i) => { const cell = c.div('c ' + (i === 0 ? 'fm' : 'fv'), colX[i], 18, null, null, v, row); if (/[一-鿿]/.test(v) && i) cell.style.fontFamily = 'var(--cjk)'; });
        if (j < n - 1) c.div('dash', 36, rowH - 8, w - 72, null, '', row);
        const tRow = o.at + 0.3 + j * (o.rowStep != null ? o.rowStep : 0.25);
        c.cue(tRow, 'row');
        return { el: row, tr: c.show(row, tRow, null, 8) };
      });
      if (o.foot) {
        const foot = c.div('', 36, 178 + n * rowH + 6, w - 72, 40, o.foot, tb);
        Object.assign(foot.style, { font: '500 23px var(--cjk)', color: '#6E6A63' });
        c.show(foot, o.at + 0.5 + n * 0.25, null, 6);
      }
      return { el: tb, tr, rows };
    };
    /** vertical stepper (步骤条): circles 1..N, active = orange filled, done = ✓.
     *  o: {x=1604, y=236, items: [[title, sub]], at (appear), active: [t...], done: [t...], step=118}
     *  step i is active from active[i] until done[i], then ticked. -> {steps[]} */
    c.steps = (o) => {
      const x = o.x != null ? o.x : 1604, y0 = o.y != null ? o.y : 236, step = o.step || 118, n = o.items.length;
      const steps = o.items.map(([a, b], i) => {
        const st = c.div('step', x, y0 + i * step);
        const sc = c.div('sc', 0, 10, null, null, String(i + 1), st);
        const ck = c.svg(10, 22, 32, 28, `<path d="M5 14 L 12 21 L 25 6" fill="none" stroke="#3D8BFF" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`, st);
        const path = ck.querySelector('path');
        const t1 = c.div('st', 68, 8, null, null, a, st), t2 = c.div('ss', 68, 44, null, null, b || '', st);
        if (i < n - 1) { const ln = c.div('', 25, 70, 3, step - 66, '', st); ln.style.background = 'rgba(237,234,227,.25)'; }
        const tr = c.T(st, { o: 0, y: 10, a: 0, d: 0 }, (p, tk) => {
          const on = p.a > 0.5, dn = p.d > 0.02;
          const key = (on ? 1 : 0) + (dn ? 2 : 0);
          if (tk._k !== key) {
            sc.classList.toggle('fillo', on && !dn);
            sc.style.borderColor = dn ? 'var(--orange)' : '';
            sc.style.color = dn ? 'transparent' : '';
            t1.style.color = on || dn ? 'var(--paper)' : '';
            t2.style.color = on ? 'rgba(237,234,227,.8)' : '';
            tk._k = key;
          }
          const dd = Math.round(p.d * 100) / 100; if (tk._d !== dd) { path.style.strokeDashoffset = 1 - dd; tk._d = dd; }
        });
        tr.in(o.at + i * 0.12);
        c.cue(o.at + i * 0.12, 'step');
        if (o.active && o.active[i] != null) tr.to(o.active[i], { a: 1 }, 0.2);
        if (o.done && o.done[i] != null) tr.to(o.done[i], { a: 0 }, 0.2).to(o.done[i] + 0.05, { d: 1 }, 0.25);
        return { el: st, tr };
      });
      return { steps };
    };

    // ---------------------------------------------------------------- mock UI (示意界面 — fictional, never a real site)
    /** browser / app window with a '示意' tag.  o: {x=440, y=170, w=1120, h=700, url (address bar with lock) | title
     *  (plain title text), at, until} -> {el, tr, bar, addr, view(t0, t1) -> a content layer (below the bar) visible t0..t1}.
     *  Inside use the style classes: ui-h, ui-t, field, btn (lite / danger), mask, side + menu, modal, dimmer, th, td. */
    c.browser = (o) => {
      const x = o.x != null ? o.x : 440, y = o.y != null ? o.y : 170, w = o.w || 1120, h = o.h || 700;
      const win = c.div('win', x, y, w, h);
      const wb = c.div('wbar', 0, 0, null, null, '', win);
      [22, 46, 70].forEach(dx => c.div('dot', dx, 22, null, null, '', wb));
      let addr = null;
      if (o.url) addr = c.div('addr', 110, 11, null, null, `<svg class="lk" viewBox="0 0 14 16">${ICON.lock()}</svg>${esc(o.url)}`, wb);
      else if (o.title) c.div('ui-t', 104, 16, null, null, esc(o.title), wb).style.color = '#3A3833';
      if (o.label !== false) c.div('shiyi', w - 80, 17, null, null, o.label || '示意', wb);
      const tr = o.at != null ? c.show(win, o.at, o.until, 14) : null;
      if (o.at != null) c.cue(o.at, 'ui');
      const view = (t0, t1) => {
        const v = c.div('view', null, null, null, null, '', win); v.style.left = '0'; v.style.top = '58px';
        const vt = c.T(v, { o: 0 }).to(t0, { o: 1 }, 0.3); if (t1 != null) vt.to(t1, { o: 0 }, 0.25);
        return v;
      };
      return { el: win, tr, bar: wb, addr, view };
    };
    /** fictional phone.  o: {x=610, y=140, w=340, h=660, title='AI 助手', banner (html, orange-framed), at, until,
     *  bubbles=true (grey/dark chat bubbles), input='输入问题…'} -> {el, tr, screen, banner} */
    c.phone = (o) => {
      const x = o.x != null ? o.x : 610, y = o.y != null ? o.y : 140, w = o.w || 340, h = o.h || 660;
      const phone = c.div('', x, y, w, h);
      Object.assign(phone.style, { background: '#141414', borderRadius: '46px', border: '3px solid rgba(237,234,227,.35)', boxShadow: '0 18px 40px rgba(0,0,0,.45)' });
      const sw = w - 34, shh = h - 34;
      const scr = c.div('', 14, 14, sw, shh, '', phone);
      Object.assign(scr.style, { background: 'var(--paper)', borderRadius: '34px', overflow: 'hidden' });
      c.div('ui-h', 26, 40, null, null, esc(o.title || 'AI 助手'), scr).style.fontSize = '26px';
      c.div('shiyi', sw - 84, 42, null, null, '示意', scr);
      c.div('', 20, 88, sw - 40, 1, '', scr).style.background = '#CFC9BE';
      let banner = null, by = 106;
      if (o.banner) {
        banner = c.div('', 20, by, sw - 40, 58, '', scr);
        Object.assign(banner.style, { border: '3px solid var(--orange)', borderRadius: '14px', background: '#FFF6F0', textAlign: 'center', font: '800 25px var(--cjk)', color: 'var(--ink)', lineHeight: '52px', whiteSpace: 'nowrap', overflow: 'hidden' });
        banner.innerHTML = `<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--orange);margin-right:10px;vertical-align:2px"></span>${o.banner}`;
        by += 90;
      }
      if (o.bubbles !== false) {
        const bub = (bx, byy, bw, bh, dark) => { const b = c.div('', bx, byy, bw, bh, '', scr); Object.assign(b.style, { borderRadius: '14px', background: dark ? '#141414' : '#DAD5CB' }); };
        bub(20, by, sw * 0.65, 54); bub(sw * 0.31, by + 74, sw * 0.62, 44, true); bub(20, by + 138, sw * 0.75, 86); bub(sw * 0.42, by + 244, sw * 0.51, 44, true);
      }
      const inp = c.div('', 20, shh - 78, sw - 40, 52, '', scr);
      Object.assign(inp.style, { borderRadius: '26px', border: '2px solid #BDB7AB', background: '#F6F4EF', font: '500 20px var(--cjk)', color: '#9A958C', lineHeight: '48px', paddingLeft: '20px' });
      inp.textContent = o.input || '输入问题…';
      const tr = o.at != null ? c.show(phone, o.at, o.until, 16, 0.4) : null;
      if (o.at != null) c.cue(o.at, 'ui');
      return { el: phone, tr, screen: scr, banner };
    };
    return c;
  };
})();
