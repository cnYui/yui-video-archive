/* 《AI每日日报》正片画面 —— 白板风格（episode.style = "board"；用户 2026-09-28：角色在左下角，内容边说边画）。
 * make_episode.py 在 style = board 时把它复制成 制作/engine/scenes.js（默认的深色版是 scenes.news.js，不动）。
 *
 * 数据和 scenes.news.js 一样来自 episode.json（news[i].headline / source / date / points / line_points / snap …）。
 * 手写组件在 hand.js（c.hand / c.handUnderline / c.handEllipse / c.handArrow / c.handCheck / c.handDash），
 * 需要的笔画由 hand_glyphs.py 生成 handdata.js。时间全部按配音的段 / 句取：念到哪句，就写到哪句。
 *   开场：手写日期大字 + 黄色波浪线 → 念串讲时，一条条写出今天的新闻（两栏）→ 结束时飞进右上目录（core.js）
 *   每条新闻：第一句话里写标题（中间），划波浪线；来源小字；原文截图像照片贴在右栏；
 *             念到第 k 个要点那句时，在左栏写出这个要点，要点里的第一个数字用黄笔圈起来
 *   回顾：手写「今日回顾」，各条新闻逐条出现，并打蓝色勾
 * 版面（2340×1080，白底）：内容以画面中线 ENG.CX = 1170 左右对称；左下角色 x ≤ 380、y ≥ 685；底部字幕 y 918–990；
 * 右上目录 ENG.tocRect()。
 * 时间：画面比声音早 ENG.LEAD 秒（默认 1 s，用户 2026-09-28：先看到字）。core.js 把场景的出现 / 消失提前，
 * 这里按配音算出来的时刻都减 L；字幕、口型、底部进度条、目录高亮和打勾（mix_audio 有打勾声）仍跟声音。
 */
(function () {
  'use strict';
  const { EP, SCENES, E } = ENG;
  if (!SCENES.length) return;
  const ids = SCENES.map(s => s.id);
  const OPEN = ids[0], LAST = ids[ids.length - 1];
  const NEWS = EP.news || [];
  const CX = ENG.CX, W = ENG.W;
  const BLUE = ENG.HAND ? ENG.HAND.BLUE : '#4A88DA';
  const esc = t => ENG.esc(String(t == null ? '' : t));
  // 要点里第一个数字（带单位）：用黄笔圈起来。前面紧挨字母或连字符的不算（M3.1、GPT-6 是型号）
  const NUM_RE = /(?<![A-Za-z\-.])\d+(?:\.\d+)?\s*(?:%|万|亿|GB|TB|B|倍|小时|分钟|秒|年|个月|月|日|天|种|条|张|款|人|元|美元)?/;
  // 画面比声音早 L 秒（用户 2026-09-28：先看到字，再听到声音）。core.js 已经把每个场景的出现 / 消失提前了 L 秒，
  // 这里凡是按配音算出来的时刻（段、句、短语）都减 L；由手写结束时刻推出来的（波浪线、照片、圈数字）自然跟着走
  const L = ENG.LEAD || 0;
  // 串讲清单一直留到开场结束；右上目录等第一条新闻开始才出现，不和清单重叠（core.js buildHud / tocSchedule 用它）
  if (SCENES.length > 1) ENG.tocInTime = () => SCENES[1].start + 0.1 - L;

  /** 原文截图像照片一样贴在白板上：白边、投影、两条胶带，微微歪一点 -> 外框 */
  function photo(c, img, x, y, w, maxH, at, seed) {
    const iw = img.naturalWidth || img.width || 1500, ih = img.naturalHeight || img.height || 840, pad = 12;
    let imgW = w - 2 * pad, imgH = Math.round(imgW * ih / iw);
    if (imgH > maxH - 2 * pad) { imgH = maxH - 2 * pad; imgW = Math.round(imgH * iw / ih); }
    const ow = imgW + 2 * pad, oh = imgH + 2 * pad, ox = x + (w - ow) / 2;
    const outer = c.div('bPhotoWrap', ox, y, ow, oh);
    const inner = c.div('bPhoto', 0, 0, ow, oh, '', outer);
    const tilt = (seed.length % 2 ? 1 : -1) * (0.8 + (seed.length % 5) * 0.2);
    inner.style.transform = `rotate(${tilt.toFixed(2)}deg)`;
    const holder = c.div('', pad, pad, imgW, imgH, '', inner);
    holder.style.overflow = 'hidden';
    const im = img.parentNode ? img.cloneNode() : img;      // 同一张截图用两次时，第二次起复制节点
    Object.assign(im.style, { width: imgW + 'px', height: 'auto', display: 'block' });
    holder.appendChild(im);
    c.div('bTape', ow * 0.12, -16, 120, 34, '', inner).style.transform = 'rotate(-7deg)';
    c.div('bTape', ow * 0.88 - 120, -14, 120, 34, '', inner).style.transform = 'rotate(6deg)';
    c.T(outer, { o: 0, s: 0.94 }).to(at, { o: 1, s: 1 }, 0.35, E.out);
    c.cue(at, 'snap');
    return { x0: ox, y0: y, x1: ox + ow, y1: y + oh };
  }

  // ================================================================== 开场
  ENG.scene(OPEN, c => {
    const s = c.segs();
    if (!s.length) return;
    const run = s[s.length - 1];                         // 最后一句 = 串讲「今天说 N 件事：……」
    const n = NEWS.length;
    const span = Math.max(0.6, run.end - run.start - 1.0);
    const at = NEWS.map((it, i) => {                     // 念到第 i 条的时刻，减 L = 写它的时刻
      const t = it.rundown_key ? c.find(it.rundown_key) : null;
      return (t != null ? t : run.start + 0.35 + (n > 1 ? span * i / (n - 1) : 0)) - L;
    });
    const runS = run.start - L, runE = run.end - L;
    // 最后一条往往在串讲快结束时才念到，而场景已经提前 L 秒淡出：整张清单的书写时刻按比例往前压，
    // 让最后一条在淡出前约 1.4 s 开始写（仍然是先出字、后出声）
    const lastStart = c.S.end - 0.4 - 1.4, latest = n ? Math.max(...at) : runS;
    if (n && latest > lastStart && lastStart > runS) for (let i = 0; i < n; i++) at[i] = runS + (at[i] - runS) * (lastStart - runS) / (latest - runS);
    const firstAt = n ? Math.min(...at) : runE;
    const tD = Math.max(0.1, s[0].start + 0.15 - L);
    const kick = c.div('bKick', CX - 700, 214, 1400, null, esc(`AI每日日报${EP.weekday ? ' · ' + EP.weekday : ''}`));
    const kTr = c.show(kick, tD, null, 8);
    const date = c.hand({ text: EP.date_label || '', x: CX, y: 410, size: 230, align: 'center', at: tD, until: tD + 1.4, seed: 'date' });
    const ul = c.handUnderline({ x0: date.x0 - 10, x1: date.x1 + 14, y: date.y1 + 34, at: date.t1 + 0.05, dur: 0.45, w: 16 });
    const sub = c.div('bSub', CX - 700, date.y1 + 78, 1400, null, esc(EP.subtitle || '鲸鱼娘带你看看 AI 圈发生了什么'));
    const sTr = c.show(sub, ul.t1 + 0.1, null, 8);
    if (!n) return;
    // 念串讲时换成今天的新闻清单
    const tClear = Math.max(ul.t1 + 0.5, Math.min(runS + 0.05, firstAt - 0.7));
    kTr.out(tClear); sTr.out(tClear); date.out(tClear); ul.out(tClear);
    const tTitle = tClear + 0.3;
    const title = c.hand({ text: EP.rundown_title || '今天说这几件事', x: CX, y: 160, size: 76, align: 'center', at: tTitle, until: tTitle + 1.2, seed: 'rundown' });
    c.handUnderline({ x0: title.x0, x1: title.x1 + 8, y: title.y1 + 18, at: title.t1 + 0.03, dur: 0.3, w: 11 });
    const two = n > 4, rows = two ? Math.ceil(n / 2) : n;
    const colW = two ? 880 : 1200, gap = 40, size = 54;
    const x0 = two ? CX - colW - gap / 2 : CX - colW / 2;
    const step = Math.min(118, Math.floor(470 / Math.max(1, rows - 1 || 1)));
    NEWS.forEach((it, i) => {
      const col = two ? Math.floor(i / rows) : 0, row = two ? i % rows : i;
      const x = x0 + col * (colW + gap), y = 318 + row * step;
      const t0 = Math.max(at[i] - 0.3, title.t1 - 0.2);
      const nxt = at.filter(t => t > at[i]).reduce((a, b) => Math.min(a, b), runE);
      const num = c.hand({ text: String(i + 1), x, y, size, color: BLUE, at: t0, until: t0 + 0.22, seed: 'n' + i });
      // 念到哪条写哪条；最后几条念完场景就结束了，要赶在串讲结束前写完（笔速上限放宽）
      c.hand({ text: it.headline, x: x + size * 0.95, y, size, maxW: colW - size * 1.1, at: num.t1 + 0.03,
        until: Math.max(num.t1 + 0.5, Math.min(nxt - 0.08, num.t1 + 2.0, c.S.end - 0.45)), vmax: 90, minPause: 0.12, minStroke: 0.008, seed: 'h' + i });
    });
  });

  // ================================================================== 每条新闻一场
  NEWS.forEach((it, i) => {
    const sid = ids[i + 1];
    if (!sid || sid === LAST) return;
    ENG.scene(sid, c => {
      const s = c.segs();
      if (!s.length) return;
      const toc = ENG.tocRect();
      const right = toc ? toc.x - 36 : W - 80;
      const half = Math.min(right - CX, 760);            // 以中线对称；右边不压目录，左边离角色很远
      const t0 = Math.max(c.S.start + 0.03, s[0].start + 0.05 - L);   // 场景已经提前 L 秒出现
      const title = c.hand({ text: `${ENG.cnNum(i + 1)}、${it.headline}`, x: CX, y: 110, size: 88, align: 'center', maxW: 2 * half,
        at: t0, until: Math.min(Math.max(t0 + 1.2, s[0].end - 0.1 - L), t0 + 2.6), seed: 't' });
      const ul = c.handUnderline({ x0: title.x0 - 6, x1: title.x1 + 10, y: title.y1 + 20, at: title.t1 + 0.04, dur: 0.35 });
      if (it.source || it.date) {
        const src = c.div('bSrc', CX - 800, title.y1 + 44, 1600, null,
          `<b>来源</b>　${esc(it.source || '')}${it.date ? `<span class="d">　·　${esc(it.date)}</span>` : ''}`);
        c.show(src, ul.t1 + 0.05, null, 6);
      }
      const top = title.y1 + 118;
      const pts = it.points || [];
      const snap = it.snap && ENG.snapImgs && ENG.snapImgs[it.snap];
      let lx, lw;
      if (snap) {                                        // 右栏：原文截图（照片）
        photo(c, snap, CX + 34, top, half - 34, 900 - top - 24, ul.t1 + 0.1, it.snap_src || String(i));
        lx = CX - half + 8; lw = half - 60;
      }
      if (!pts.length) return;
      const size = snap ? 56 : 64, step = Math.round(size * 1.9);
      if (!snap) {                                       // 没有截图：要点整块以中线居中（按最宽的一条）
        const bw = Math.min(1280, size * 0.72 + Math.max(...pts.map(p => ENG.handWidth(p, size))));
        lx = CX - bw / 2; lw = bw;
      }
      const lp = it.line_points || [];
      const times = pts.map((p, j) => {
        const k = lp.indexOf(j);
        const sg = k >= 0 && s[k] ? s[k] : s[Math.min(s.length - 1, j + 1)];
        return { t: Math.max(ul.t1 + 0.25, sg.start + 0.1 - L), end: sg.end - L };   // 比念到这句早 L 秒开始写
      });
      pts.forEach((p, j) => {
        const y = top + 44 + j * step;
        const tj = times[j].t;
        const nxt = times.slice(j + 1).map(x => x.t).reduce((a, b) => Math.min(a, b), Infinity);
        const dash = c.handDash({ x: lx, y: y + 3, len: size * 0.42, at: tj, dur: 0.1 });
        const tx = c.hand({ text: p, x: lx + size * 0.72, y, size, maxW: lw - size * 0.72, at: dash.t1 + 0.02,
          until: Math.max(dash.t1 + 0.8, Math.min(times[j].end, nxt - 0.1, dash.t1 + 2.3)), seed: 'p' + j });
        c.cue(tj, 'point');
        const m = NUM_RE.exec(p);
        if (m) {
          const b = tx.box(m.index, m.index + m[0].trimEnd().length);
          if (b) c.handEllipse({ x0: b[0], y0: b[1], x1: b[2], y1: b[3], at: tx.t1 + 0.1, dur: 0.4 });
        }
      });
    });
  });

  // ================================================================== 回顾
  if (LAST !== OPEN && NEWS.length) ENG.scene(LAST, c => {
    const s = c.segs();
    if (!s.length) return;
    const t0 = Math.max(c.S.start, s[0].start - L);
    ENG.tocHideAt = Math.max(t0 - 0.35, 0);             // 回顾列出了全部新闻：右上目录淡出（core.js buildHud）
    const title = c.hand({ text: EP.recap_title || '今日回顾', x: CX, y: 130, size: 88, align: 'center', at: t0 + 0.05, until: t0 + 1.0, seed: 'recap' });
    c.handUnderline({ x0: title.x0, x1: title.x1 + 8, y: title.y1 + 20, at: title.t1 + 0.03, dur: 0.3 });
    const n = NEWS.length, two = n > 4, rows = two ? Math.ceil(n / 2) : n;
    const colW = two ? 820 : 1100, gap = 60, x0 = two ? CX - colW - gap / 2 : CX - colW / 2;
    const step = Math.min(116, Math.floor(480 / Math.max(1, rows - 1 || 1)));
    NEWS.forEach((it, i) => {
      const col = two ? Math.floor(i / rows) : 0, row = two ? i % rows : i;
      const x = x0 + col * (colW + gap), y = 320 + row * step;
      const ta = t0 + 0.45 + 0.22 * i;
      const lab = c.div('bItem', x + 74, y - 30, colW - 84, null, esc(it.headline));
      c.show(lab, ta, null, 6);
      c.handCheck({ x: x + 26, y, size: 46, at: ta + 0.08, dur: 0.22 });
    });
    const sign = c.div('bSub', CX - 700, 320 + rows * step + 10, 1400, null, esc(EP.recap_sign || '来源都在简介里'));
    c.show(sign, t0 + 0.6 + 0.22 * n, null, 6);
  });
})();
