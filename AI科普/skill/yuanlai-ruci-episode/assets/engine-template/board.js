/* 白板版组件（episode.json "style": "board"；用户 2026-09-28：「原LAI如此也用手写白板，字提前一秒出现，字幕也同步放大」）。
 * 在 hand.js 之后加载；不是白板版（没写 style）时这个文件什么都不做。
 *
 * 手写的是说出来的要点：章节标题、开场大字、三个疑问、结论、要点、总结；印刷体只留小字（小标签、补充说明、落款）。
 * 下面这些组件在白板版里换成手写版，参数和返回值和卡片版兼容（scenes.js 照原来的写法调用）。
 * 淡出一律叫 until（和卡片版组件一样）；c.hand 的 until 是“写完的时间窗”，淡出叫 out（见 hand.js）。
 *   c.title / c.autoTitle  标题写在顶部正中（不再从中间缩上去，白板上的字不会动），黄色波浪线，下面一行橙色小字
 *                          （PART 0N · 第N个问题）。画在场景的“标题层”：这一章讲完前 1 秒左右先擦标题，好让下一章的标题
 *                          早 1 秒写出来，这一章的内容等最后一句说完再擦（core.js boardPlan）。
 *                          -> {el, left, right, bottom, morph (= 写完的时刻), item, out(t)}
 *   c.bigWord              开场大字：橙色小字 + 手写大字 + 波浪线 + 灰色一行 -> {el, trs: [可 out 的块], item}
 *   c.questionCards        手写「你可能也想问」+ 编号问题（念到哪题写哪题，整块以中线居中）；到 ENG.tocInTime()
 *                          （疑问场最后一句快说完）每一问缩小飞进右上目录对应的行，整块淡出 -> {cards: [{el, tr, item}], tIn}
 *                          at 要给每一问开口的时刻：台词和问题原文不一样时自己用 c.P / c.find 找，别依赖模板的兜底
 *   c.statement            橙色小字 kicker + 手写 lead + 手写大字 main（main 里 <span class="or">…</span> 那几个字划黄线）
 *                          -> {el, tr, main}
 *   c.pointList            橙色小字 kicker + 手写标题 + 细线 + 手写要点（mark：num 橙色编号 / dash 橙色小横 / check 橙色勾 /
 *                          x 红叉 / none），sub 印刷小字跟在后面（放不下就放在这一条下面）；字号按 fs × 1.25（或直接给 size）
 *                          draft: true = 分镜草稿（不查写字时间：hand-slow / hand-short）-> {el, tr, rows: [{el, tr, t, item}]}
 *   c.summary              手写「本期总结」+ 编号结论（主句手写、副句印刷小字）+ 落款；整块以中线居中 -> {el, rows, tr}
 * 新增：
 *   c.flip(sg) -> {out, in}    同一场里“擦掉这一页、写下一页”：out = 这一页最后一句 sg 说完前 0.15 s（画面时刻）对应的
 *                              场景时刻，in = out + 0.3。这一页 until: f.out，下一页的东西 at 不早于 f.in。画面整体早 1 秒，
 *                              照声音时刻擦板会把这一页最后一句的字在说出来之前就擦掉（第 3 期测试 D1）。
 *   c.handText(html, x, y, o)  = c.hand，先去掉 HTML 标签；<span class="or">…</span> / <b>…</b> 的字划黄线（o.mark: 'circle' 改成圈）
 *   c.handNode({x, y, w, h, text, sub, size, at, write, until, color, textColor, pen, parent})
 *                              手画框 + 框里手写字（流程图的节点）。w / h 是框的大小，pen 是框线粗细，write 是框里的字写完的
 *                              时刻（默认框画完后 1 秒左右，写不下会自动写快），until 是整个节点淡出的时刻
 *                              -> {el, rect, text, x0, y0, x1, y1, t1, tr}（接箭头用 x0..y1，擦掉用 tr.out(t) 或 until）
 *   c.tape(el, k)              给卡片 / 截图 / 示意窗口贴两条胶带（左上、右下，不压右上角的「示意」）；el 是元素本身，
 *                              例如 c.code(...) 返回值的 .el
 * 其余组件（代码卡、示意窗口、手机、对比表、步骤条、标签、箭头、chip）照旧是印刷体，白板上照样能用。
 * 时间：全部是声音时间；画面整体比声音早 ENG.LEAD 秒由 core.js 做（renderAt 用 t + LEAD 求值），这里不用减。
 * 坐标：内容舞台坐标；居中版面以 ENG.CX（960）为中线。
 */
(function () {
  'use strict';
  if (!ENG.BOARD) return;
  const { EP, E } = ENG;
  const HC = ENG.HAND || {};
  const ACC = HC.ACCENT || '#FF4F1A', RED = '#D8342A';
  const NS = 'http://www.w3.org/2000/svg';
  const esc = t => ENG.esc(String(t == null ? '' : t));
  const unesc = s => s.replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&');
  /** html -> {text, marks: [[i0, i1), …]}: tags dropped (<br> = space); the characters inside <span class="or">,
   *  <span class="t"> or <b> are marked. Indexes count code points, like hand.js (item.box(i0, i1)). */
  function parseHTML(html) {
    let text = '';
    const marks = [], stack = [], re = /<(\/?)([a-z0-9]+)([^>]*)>|([^<]+)/gi;
    let m;
    const len = () => [...text].length;
    while ((m = re.exec(String(html == null ? '' : html)))) {
      if (m[4] != null) { text += unesc(m[4]); continue; }
      const closing = m[1] === '/', tag = m[2].toLowerCase();
      if (tag === 'br') { text += ' '; continue; }
      if (!closing) stack.push(/class\s*=\s*"[^"]*\b(or|t)\b/.test(m[3]) || tag === 'b' ? len() : null);
      else { const st = stack.pop(); if (st != null && len() > st) marks.push([st, len()]); }
    }
    return { text: text.replace(/\s+$/, ''), marks };  // trailing blanks only: the marks' indexes stay valid
  }
  ENG.boardText = parseHTML;                             // for tests

  const baseCtx = ENG.ctx;
  ENG.ctx = S => {
    const c = baseCtx(S);
    const CX = () => (ENG.CX != null ? ENG.CX : 960);
    /** a block that fades as one: the hand group + printed elements (their show Tracks). Usable where a Track was
     *  returned before: .out(t, d), .to(t, props, d, e), .in() (no-op: hand ink appears by being written) */
    function block(g) {
      const tg = c.T(g, { o: 1 }), more = [];
      const blk = {
        g,
        add(tr) { if (tr) more.push(tr); return blk; },
        out(t, d = 0.3) {
          tg.out(t, d); more.forEach(tr => tr.out(t, d));
          const prev = g && g.getAttribute ? parseFloat(g.getAttribute('data-out')) : NaN;   // check_layout: when it is erased
          if (g && g.setAttribute && !(prev <= t)) g.setAttribute('data-out', String(t));
          return blk;
        },
        to(t, p, d, e) { tg.to(t, p, d, e); more.forEach(tr => tr.to(t, p, d, e)); return blk; },
        in() { return blk; },
      };
      return blk;
    }
    /** end of a writing window: before `next` (the next thing's start) but at least `min` s, at most `max` s, and never
     *  past the scene's fade (hand.js reports that as hand-late). A window too short for the text is fine: c.hand writes
     *  faster to fit it (hand.js) and reports what still does not fit (hand-slow). */
    const win = (t0, next, min = 0.6, max = 2.2) => {
      const u = Math.max(t0 + min, Math.min(t0 + max, (next != null ? next : t0 + max) - 0.1));
      return c.S ? Math.max(t0 + 0.25, Math.min(u, c.S.end - 0.45)) : u;
    };
    /** the scene's head layer (board: the chapter title leaves before the content, core.js boardPlan): an SVG ink layer
     *  in S.head, or null (then the title is drawn with the content) */
    function headInk() {
      if (!c.S || !c.S.head) return null;
      if (c._headInk) return c._headInk;
      const s = document.createElementNS(NS, 'svg');
      s.setAttribute('width', ENG.W); s.setAttribute('height', ENG.H); s.setAttribute('viewBox', `0 0 ${ENG.W} ${ENG.H}`);
      s.setAttribute('class', 'inkLayer');
      Object.assign(s.style, { position: 'absolute', left: '0px', top: '0px', overflow: 'visible', pointerEvents: 'none', zIndex: 5 });
      c.S.head.appendChild(s);
      return (c._headInk = s);
    }

    c.flip = sg => { const out = sg.end + (ENG.LEAD || 0) - 0.15; return { out, in: out + 0.3 }; };

    c.handText = (html, x, y, o = {}) => {
      const p = parseHTML(html);
      const it = c.hand(Object.assign({}, o, { text: p.text, x, y }));
      p.marks.forEach(([a, b]) => c.handMark(it, a, b, { kind: o.mark === 'circle' ? 'circle' : 'underline', parent: o.parent }));
      return it;
    };

    c.tape = (el, k = 0) => {
      const w = el.offsetWidth || parseFloat(el.style.width) || 400, h = el.offsetHeight || parseFloat(el.style.height) || 240;
      c.div('tape', -30, -12, 110, 30, '', el).style.transform = `rotate(${-38 + (k % 3) * 3}deg)`;          // top-left corner
      c.div('tape', w - 80, h - 18, 110, 30, '', el).style.transform = `rotate(${-38 - (k % 2) * 3}deg)`;     // bottom-right corner
      return el;
    };

    // ---------------------------------------------------------------- titles
    c.title = (text, kicker, sg, o = {}) => {
      const cx = o.cx || CX(), y = o.y || 108, size = o.size || 84;
      const at = o.at != null ? o.at : sg.start + 0.05;
      const hk = headInk(), g = c.handGroup(hk || undefined), blk = block(g);
      const tx = c.handText(text, cx, y, { size, align: 'center', maxW: 1400, at, until: win(at, sg.end, 1.1, 2.4), seed: 'title', parent: g });
      const ul = c.handUnderline({ x0: tx.x0 - 8, x1: tx.x1 + 12, y: tx.y1 + 18, at: tx.t1 + 0.04, dur: 0.35, parent: g });
      let bottom = tx.y1 + 34;
      if (kicker) {
        const k = c.div('bKick', cx - 500, tx.y1 + 36, 1000, null, kicker, hk ? c.S.head : undefined);
        blk.add(c.show(k, ul.t1 + 0.05, null, 6));
        bottom = tx.y1 + 72;
      }
      if (hk && c.S.titleOut != null) blk.out(c.S.titleOut);   // leaves before the content (core.js boardPlan)
      c.cue(at, 'title');
      const res = { el: g, left: tx.x0, right: tx.x1, bottom, morph: tx.t1, item: tx, out: t => blk.out(t) };
      return (ENG._lastTitle = res);
    };

    c.bigWord = (o) => {
      const cx = o.cx || CX(), cy = o.cy || 430, at = o.at;
      const g = c.handGroup(), blk = block(g);
      if (o.kicker) blk.add(c.show(c.div('bKick', cx - 500, cy - 196, 1000, null, o.kicker), at - 0.1, null, 6));
      const tx = c.handText(o.text, cx, cy, { size: o.size || 200, align: 'center', maxW: 1400, at, until: at + 1.4, seed: 'big', parent: g });
      const ul = c.handUnderline({ x0: tx.x0 - 10, x1: tx.x1 + 14, y: tx.y1 + 30, at: tx.t1 + 0.05, dur: 0.45, w: 14, parent: g });
      if (o.sub) blk.add(c.show(c.div('bSub', cx - 700, tx.y1 + 66, 1400, null, o.sub), ul.t1 + 0.1, null, 8));
      if (o.until != null) blk.out(o.until);
      c.cue(at, 'word');
      return { el: g, trs: [blk], item: tx };
    };

    // ---------------------------------------------------------------- the questions (-> TOC)
    c.questionCards = (o) => {
      const items = o.items || (EP.questions || []).map(q => /[？?]$/.test(q.text) ? q.text : q.text + '？');
      const n = items.length, cx = CX();
      const tIn = ENG.tocInTime(), hasToc = (EP.questions || []).length > 0;
      const g = c.handGroup(), blk = block(g);
      const at = items.map((_, i) => (o.at[i] != null ? o.at[i] : o.at[o.at.length - 1] + 0.3 * i) + 0.05);
      if (o.title !== false) {
        const ta = o.titleAt != null ? o.titleAt : at[0] - 0.9;
        const tt = c.handText(o.title || '你可能也想问', cx, 196, { size: 72, align: 'center', at: ta, until: win(ta, at[0] - 0.05, 0.5, 1.2), seed: 'q-title', parent: g });
        c.handUnderline({ x0: tt.x0 - 6, x1: tt.x1 + 10, y: tt.y1 + 18, at: tt.t1 + 0.03, dur: 0.3, parent: g });
      }
      const y0 = o.y || 350, size = o.size || (n > 3 ? 54 : 64);
      const step = Math.min(140, Math.floor((860 - y0) / Math.max(1, n)));
      const bw = Math.min(1500, Math.max(...items.map(q => ENG.handWidth(q, size))) + size * 1.15);
      const x = Math.round(cx - bw / 2);                 // the block is centred on the midline
      const cards = items.map((q, i) => {
        const y = y0 + i * step, row = c.handGroup(g);  // one group per question: it flies into its TOC row
        const num = c.hand({ text: String(i + 1), x, y, size, color: ACC, at: at[i], until: at[i] + 0.25, seed: 'qn' + i, parent: row, cue: false });
        const tx = c.handText(q, x + size * 1.15, y, { size, maxW: bw - size * 1.15, at: num.t1 + 0.03,
          until: win(num.t1 + 0.03, i + 1 < n ? at[i + 1] : tIn, 0.6, 1.8), seed: 'q' + i, parent: row, cue: false });
        c.cue(at[i], 'question');
        if (hasToc) {
          // fly into the TOC row (like the card version): the row's ink box -> the row rect, then fade
          const x0 = Math.min(num.x0, tx.x0), y0b = Math.min(num.y0, tx.y0), x1 = Math.max(num.x1, tx.x1), y1b = Math.max(num.y1, tx.y1);
          const r = ENG.tocRowRect(i), s = Math.min((r.w - 44) / Math.max(1, x1 - x0), 22 / Math.max(1, y1b - y0b));   // ~ the row's 19 px text
          Object.assign(row.style, { transformBox: 'fill-box', transformOrigin: '0 0' });
          row.setAttribute('data-fly', String(tIn));
          c.T(row, { o: 1 }).to(tIn, { x: r.x + 36 - x0, y: r.y + 2 - y0b, s }, 0.7, E.inOut).to(tIn + 0.4, { o: 0 }, 0.3, E.sine);
        }
        return { el: row, tr: blk, item: tx };
      });
      if (hasToc) blk.out(tIn + 0.4, 0.3); else if (o.until != null) blk.out(o.until);
      return { cards, tIn };
    };

    // ---------------------------------------------------------------- statement / lists / summary
    c.statement = (o) => {
      const w = o.w || 1300, cx = o.x != null ? o.x + w / 2 : CX(), y = o.y != null ? o.y : 330;
      const size = o.size ? Math.round(o.size * 1.1) : 76;
      const g = c.handGroup(), blk = block(g);
      let yy = y, tNext = o.at;
      if (o.kicker) { blk.add(c.show(c.div('bKick', cx - 600, yy, 1200, null, o.kicker), o.at, null, 6)); yy += 56; }
      const mAt = o.mainAt != null ? o.mainAt : null;
      if (o.lead) {
        const ld = c.handText(o.lead, cx, yy + 34, { size: 50, align: 'center', maxW: w, at: o.at, until: win(o.at, mAt, 0.5, 1.2), seed: 'lead', parent: g, cue: false });
        yy += 106; tNext = ld.t1 + 0.1;
      }
      const m0 = mAt != null ? mAt : tNext;
      const mn = c.handText(o.main, cx, yy + size * 0.62, { size, align: 'center', maxW: w, at: m0, until: win(m0, o.until, 0.8, 2.2), seed: 'main', parent: g, cue: false });
      if (o.until != null) blk.out(o.until);
      c.cue(o.at, 'statement');
      if (o.mainAt != null) c.cue(o.mainAt, 'statement');
      return { el: g, tr: blk, main: mn };
    };

    c.pointList = (o) => {
      const w = o.w || 1200, x = o.x != null ? o.x : Math.round(CX() - w / 2);
      const y = o.y != null ? o.y : ENG.safeTop(236, x + w, x);
      const size = o.size || Math.max(40, Math.round((o.fs || 38) * 1.25));
      const step = Math.max(o.step || 0, Math.round(size * 1.6));
      const g = c.handGroup(), blk = block(g);
      if (o.draft) g.setAttribute('data-draft', '1');   // the storyboard draft (scenes.template.js): not timing-checked
      const specs = o.items.map(it => (typeof it === 'string' ? { text: it } : it));
      const firstAt = specs.length ? (specs[0].at != null ? specs[0].at : o.at + 0.4) : null;
      let yy = y, tBody = o.at;
      if (o.kicker) { const k = c.div('bKick', x, yy - 6, w, null, o.kicker); k.style.textAlign = 'left'; blk.add(c.show(k, o.at, null, 6)); yy += 46; }
      if (o.title) {
        const ts = Math.round(size * 1.2);
        const tt = c.handText(o.title, x, yy + ts * 0.55, { size: ts, maxW: w, at: o.at, until: win(o.at, firstAt, 0.6, 1.8), seed: 'pl-title', parent: g, cue: false });
        c.handLine({ x0: x, y0: tt.y1 + 18, x1: Math.min(x + w, Math.max(tt.x1 + 60, x + w * 0.55)), y1: tt.y1 + 15, at: tt.t1 + 0.03, dur: 0.3, w: 3, color: 'rgba(26,26,26,.4)', parent: g, cue: false });
        yy = tt.y1 + 44 + size * 0.55; tBody = tt.t1;
      } else yy += size * 0.55;
      const starts = specs.map((sp, i) => Math.max(sp.at != null ? sp.at : o.at + 0.4 + 0.5 * i, tBody));
      const rows = specs.map((sp, i) => {
        const mk = sp.mark || o.mark || 'num', ym = yy + i * step, t0 = starts[i];
        let lead = null, tx0 = x + size * 1.05;
        if (mk === 'num') lead = c.hand({ text: String(i + 1), x: x + 4, y: ym, size, color: ACC, at: t0, until: t0 + 0.22, seed: 'pn' + i, parent: g, cue: false });
        else if (mk === 'check') lead = c.handCheck({ x: x + size * 0.42, y: ym, size: size * 0.8, at: t0, dur: 0.2, parent: g });
        else if (mk === 'x') {
          const s = size * 0.3, cx0 = x + size * 0.42;
          c.handLine({ x0: cx0 - s, y0: ym - s, x1: cx0 + s, y1: ym + s, at: t0, dur: 0.1, w: size * 0.11, color: RED, parent: g, cue: false });
          lead = c.handLine({ x0: cx0 + s, y0: ym - s, x1: cx0 - s, y1: ym + s, at: t0 + 0.12, dur: 0.1, w: size * 0.11, color: RED, parent: g, cue: false });
        } else if (mk === 'dash') lead = c.handDash({ x: x + 4, y: ym + 3, len: size * 0.5, at: t0, dur: 0.1, parent: g });
        else tx0 = x;
        const tStart = lead ? lead.t1 + 0.03 : t0;
        const next = i + 1 < specs.length ? starts[i + 1] : (o.until != null ? o.until : null);
        const tx = c.handText(sp.text, tx0, ym, { size, maxW: x + w - tx0, at: tStart, until: win(tStart, next, 0.7, 2.2), seed: 'pi' + i, parent: g, cue: false, draft: o.draft });
        if (sp.sub) {
          // the small print after the item; when it does not fit on the line, under the item
          const room = x + w - tx.x1 - 18, subW = [...parseHTML(sp.sub).text].length * 27;
          const sb = room >= Math.min(subW, 260) ? c.div('bNote', tx.x1 + 18, ym - 17, room, null, sp.sub)
            : c.div('bNote', tx0, tx.y1 + 4, x + w - tx0, null, sp.sub);
          blk.add(c.show(sb, tx.t1 + 0.05, null, 4));
        }
        return { el: tx.g, tr: blk, t: t0, item: tx };
      });
      if (o.until != null) blk.out(o.until);
      c.cue(o.at, 'list');
      rows.forEach(r => c.cue(r.t, 'item'));
      return { el: g, tr: blk, rows };
    };

    c.summary = (o) => {
      const cx = CX(), w = o.w || 1300;
      const n = o.items.length, g = c.handGroup(), blk = block(g);
      const at = o.items.map((_, i) => (o.at[i] != null ? o.at[i] : o.at[o.at.length - 1] + 0.5));
      const tAt = o.cardAt != null ? o.cardAt : at[0] - 0.8;
      const tt = c.handText(o.title || '本期总结', cx, (o.y || 150) + 20, { size: 76, align: 'center', at: tAt, until: win(tAt, at[0] - 0.05, 0.5, 1.4), seed: 'sum-title', parent: g, cue: false });
      c.handUnderline({ x0: tt.x0 - 8, x1: tt.x1 + 10, y: tt.y1 + 18, at: tt.t1 + 0.03, dur: 0.3, parent: g });
      const top = tt.y1 + 76;
      const rowH = Math.max(88, Math.min(140, Math.floor((840 - top) / Math.max(1, n))));   // the sign ends above the subtitles
      const size = rowH >= 120 ? 54 : 46;
      const mains = o.items.map(([a]) => parseHTML(a));
      const bw = Math.min(w, Math.max(...mains.map(p => ENG.handWidth(p.text, size))) + size * 1.2);
      const bx = Math.round(cx - bw / 2);
      const rows = o.items.map(([, b], i) => {
        const ym = top + i * rowH + size * 0.5;
        const num = c.hand({ text: String(i + 1), x: bx, y: ym, size, color: ACC, at: at[i], until: at[i] + 0.22, seed: 'sn' + i, parent: g, cue: false });
        const tx = c.handText(o.items[i][0], bx + size * 1.2, ym, { size, maxW: bw - size * 1.2, at: num.t1 + 0.03,
          until: win(num.t1 + 0.03, i + 1 < n ? at[i + 1] : null, 0.7, 2.0), seed: 'sm' + i, parent: g, cue: false });
        if (b) blk.add(c.show(c.div('bNote', bx + size * 1.2, ym + size * 0.6, bw, null, esc(b)), tx.t1 + 0.05, null, 4));
        c.cue(at[i], 'summary');
        return { el: tx.g, tr: blk, item: tx };
      });
      c.cue(tAt, 'summary');
      if (o.sign !== false) {
        const num = EP.number != null ? `#${ENG.pad2(EP.number)}` : '';
        const sig = c.div('bSign', bx + bw - 600, top + n * rowH + 6, 600, 40, o.sign || `原LAI如此 <span class="mono or">${num}</span> · 下期见`);
        blk.add(c.show(sig, o.signAt != null ? o.signAt : at[n - 1] + 1.0, null, 6));
      }
      if (o.until != null) blk.out(o.until);
      return { el: g, rows, tr: blk };
    };

    // ---------------------------------------------------------------- drawings
    c.handNode = (o) => {
      const g = c.handGroup(o.parent), blk = block(g);
      const x0 = o.x, y0 = o.y, x1 = o.x + (o.w || 300), y1 = o.y + (o.h || 140), size = o.size || 48;
      const rc = c.handRect({ x0, y0, x1, y1, at: o.at, dur: o.dur, color: o.color, w: o.pen, parent: g, cue: false });   // o.w is the box width
      const ty = o.sub ? (y0 + y1) / 2 - size * 0.32 : (y0 + y1) / 2;
      const w0 = rc.t1 - 0.1, fade = o.until != null ? o.until : o.out;
      const tx = c.handText(o.text || '', (x0 + x1) / 2, ty, { size, align: 'center', maxW: (x1 - x0) - 36, at: w0,
        until: o.write != null ? o.write : win(w0, fade, 0.6, 1.2), color: o.textColor, seed: `node|${o.x}|${o.y}`, parent: g, cue: false });
      if (o.sub) {
        const sb = c.div('bNote', x0, (y0 + y1) / 2 + size * 0.3, x1 - x0, null, o.sub);
        sb.style.textAlign = 'center';
        blk.add(c.show(sb, tx.t1, null, 4));
      }
      if (fade != null) blk.out(fade);
      c.cue(o.at, 'node');
      return { el: g, rect: rc, text: tx, x0, y0, x1, y1, t1: tx.t1, tr: blk };
    };
    return c;
  };
})();
