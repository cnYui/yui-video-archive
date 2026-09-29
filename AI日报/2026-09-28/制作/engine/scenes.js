/* 《AI每日日报》正片画面 —— 数据驱动，每期通用，不用手写（make_episode.py 把它复制成 制作/engine/scenes.js）。
 *
 * 数据都在 episode.json（build_timeline 抄进 timeline.episode）：
 *   date_label '9月27日'、weekday '周日'、ai_notice '本期配音由 AI 合成'
 *   news[i] = {headline（≤14 字，目录 / 标题卡 / 进度条都用它）, org, source（来源，卡片底部）, date（'9月26日'）,
 *              points[]（2–4 条要点，≤22 字）, line_points[]（本条每一句对应第几个要点，null = 不出新要点）,
 *              rundown_key（开场串讲里念到这条的短语，可选）}
 * 场景：第一场 = 开场（日期大字 → 今日要闻卡逐张出现 → 飞进右上目录）；中间每条新闻一场（标题卡 → 来源 → 要点卡按句出现）；
 * 最后一场 = 回顾（今日回顾卡）。时间全部按段取，配音重做后自动跟上。
 * 版面（2340×1080）：标题、来源、正文都以画面中线 ENG.CX = 1170 居中（和字幕一致）；右上目录除外。
 *   正文左右对称：左栏要点、右栏截图，右边不压目录、左边不压角色（x ≤ 380, y ≥ 690）；底部字幕 y 918–990。
 */
(function () {
  'use strict';
  const { EP, SCENES } = ENG;
  if (!SCENES.length) return;
  const ids = SCENES.map(s => s.id);
  const OPEN = ids[0], LAST = ids[ids.length - 1];
  const NEWS = EP.news || [];
  const esc = t => ENG.esc(String(t == null ? '' : t));

  // ================================================================== 开场
  ENG.scene(OPEN, c => {
    const s = c.segs();
    if (!s.length) return;
    const run = s[s.length - 1];                         // 最后一句 = 串讲「今天说 N 件事：……」
    const n = NEWS.length;
    const span = Math.max(0.6, run.end - run.start - 1.0);
    const at = NEWS.map((it, i) => {
      const t = it.rundown_key ? c.find(it.rundown_key) : null;
      return t != null ? t : run.start + 0.35 + (n > 1 ? span * i / (n - 1) : 0);
    });
    const firstCard = n ? Math.min(...at) : run.end;
    c.bigWord({
      text: EP.date_label || EP.title || 'AI每日日报',
      kicker: `AI每日日报${EP.weekday ? ' · ' + EP.weekday : ''}`,
      sub: EP.subtitle || '鲸鱼娘带你看看 AI 圈发生了什么',
      at: s[0].start + 0.1,
      until: Math.max(s[0].start + 1.2, firstCard - 0.5),
      size: 170,                                          // 230 的日期会压到下面那行副标题
    });
    // AI 合成提示：念「本期配音由 AI 合成」那一句时显示，至少 2.5 秒
    if (EP.ai_notice) {
      const k = s.findIndex(sg => /AI\s*合成/.test(sg.text || ''));
      const t0 = k >= 0 ? s[k].start : s[0].start + 0.2;
      const t1 = Math.max(t0 + 2.5, k >= 0 ? s[k].end + 0.3 : t0 + 2.5);
      const chip = c.div('chip dark', 0, 0, null, null, esc(EP.ai_notice));
      Object.assign(chip.style, { fontSize: '30px', height: '56px', lineHeight: '56px', padding: '0 22px' });
      chip.style.left = (ENG.CX - chip.offsetWidth / 2) + 'px';
      chip.style.top = '760px';
      c.show(chip, t0, t1, 6);
    }
    if (n) c.questionCards({ items: NEWS.map(it => it.headline), at, title: EP.rundown_title || '今天这几件事', titleAt: firstCard - 0.3, kicker: 'NEWS', y: n > 5 ? 200 : 236 });
  });

  // ================================================================== 每条新闻一场
  NEWS.forEach((it, i) => {
    const sid = ids[i + 1];
    if (!sid || sid === LAST) return;
    ENG.scene(sid, c => {
      const s = c.segs();
      if (!s.length) return;
      const title = c.title(`${ENG.cnNum(i + 1)}、${esc(it.headline)}`, `NEWS ${ENG.pad2(i + 1)}${it.org ? ' · ' + esc(it.org) : ''}`, s[0]);
      const tMorph = title.morph + 0.3;
      // 来源 + 日期：标题收到左上以后，放在标题下面
      if (it.source || it.date) {
        const src = c.div('note', ENG.CX - 700, 158, 1400, null,
          `<span style="color:var(--orange);font-weight:700">来源</span>　${esc(it.source || '')}${it.date ? `<span style="opacity:.7">　·　${esc(it.date)}</span>` : ''}`);
        Object.assign(src.style, { fontSize: '30px', overflow: 'hidden', textOverflow: 'ellipsis', textAlign: 'center' });
        c.show(src, tMorph, null, 6);
      }
      const pts = it.points || [];
      const snap = it.snap && ENG.snapImgs && ENG.snapImgs[it.snap];
      // 以中线对称：半宽不超过 690，右边留到目录左边 24 px（目录在右上）
      const toc = ENG.tocRect();
      const half = Math.min(690, (toc ? toc.x - 24 : 1900) - ENG.CX);
      // 有原文截图：右栏截图卡（标题收起时滑入），左栏要点；没有截图：要点卡占整行
      if (snap) {
        const sx = ENG.CX + 20, sw = half - 20, sy = ENG.safeTop(236, sx + sw, sx);   // 右栏截图：中线右边
        const iw = snap.naturalWidth || snap.width || 1500, ih = snap.naturalHeight || snap.height || 840;
        const imgW = sw - 28, imgH = Math.min(Math.round(imgW * ih / iw), 900 - sy - 64);
        const cd = c.card(sx, sy, sw, imgH + 60);
        c.div('kicker', 18, 14, sw - 36, null, `SOURCE · ${esc(it.snap_src || it.source || '')}`, cd);
        const holder = c.div('', 14, 44, imgW, imgH, '', cd);
        Object.assign(holder.style, { overflow: 'hidden', background: '#fff', border: '1px solid #D8D3CA' });
        // 两条新闻用同一张截图时，同一个 <img> 只能挂在一个地方：第二次起用复制的节点
        const im = snap.parentNode ? snap.cloneNode() : snap;
        Object.assign(im.style, { width: imgW + 'px', height: 'auto', display: 'block' });
        holder.appendChild(im);
        c.show(cd, tMorph, null, 14);
        c.cue(tMorph, 'snap');
      }
      if (!pts.length) return;
      const lp = it.line_points || [];
      const items = pts.map((p, j) => {
        const k = lp.indexOf(j);
        const sg = k >= 0 && s[k] ? s[k] : s[Math.min(s.length - 1, j + 1)];
        return { text: esc(p), at: Math.max(tMorph + 0.2, sg.start + 0.1) };
      });
      const x = ENG.CX - half, w = snap ? half - 20 : 2 * half;   // 左栏要点：中线左边；没截图时整行居中
      const widest = Math.max(8, ...pts.map(p => [...String(p)].reduce((a, ch) => a + (ch.charCodeAt(0) < 128 ? 0.55 : 1), 0)));
      const fs = snap ? Math.max(36, Math.min(52, Math.floor((w - 150) / widest))) : 56;   // 要点 ≤12 字宽时约 41–52 px
      c.pointList({
        x, w, y: ENG.safeTop(236, x + w, x), fs, step: Math.round(fs * 2.1),
        kicker: `KEY POINTS · ${esc(it.org || 'AI')}`,
        at: Math.max(tMorph, items[0].at - 0.35),
        items,
        mark: 'num',
      });
    });
  });

  // ================================================================== 回顾
  if (LAST !== OPEN && NEWS.length) ENG.scene(LAST, c => {
    const s = c.segs();
    if (!s.length) return;
    const t0 = s[0].start;
    // 回顾卡列出了全部新闻：右上目录在这里淡出，把位置让给回顾卡
    ENG.tocHideAt = Math.max(t0 - 0.35, 0);           // core.js buildHud 建目录时加上淡出
    c.summary({
      y: 150,
      ...(NEWS.length > 5 ? { x: ENG.CX - 780, w: 1560, cols: 2 } : { x: ENG.CX - 720, w: 1440 }),   // 居中；6–8 条分两栏，否则超出屏幕底部
      kicker: `TODAY · AI每日日报 ${esc(EP.date_label || '')}`,
      title: EP.recap_title || '今日回顾',
      items: NEWS.map(it => [esc(it.headline), it.source_short || it.source || '']),
      at: NEWS.map((_, i) => t0 + 0.2 + 0.25 * i),
      cardAt: t0 + 0.05,
      sign: EP.recap_sign || '来源都在简介里',
    });
  });
})();
