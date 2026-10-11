// ═════════════════════════════ 本条（出镜多窗版）的叠加层：自己画的说明卡 + 官方镜头上的中文小标签（scenes.js 之后、engine.js 之前加载）
// 骨架。第 1 期真实的 12 张说明卡（顾问 / 助手、文件夹、新闻聚合、循环图、一来一回、四样东西、泼冷水）在 assets/oncam-multiclip/example_ep1/scenes_ep.js，抄它的写法。
// 版式：标题 → 中间窗口（one 单窗 / two 双窗 / big 大窗）→ 字幕 → 出镜小窗（渲完后 scripts/compose_face.py 叠）。窗口内容坐标：one / two = 1474×829，big = 1474×1725。
// 大窗里的出镜小窗在左下角：内容坐标 x < 320 且 y > 1335 的地方留空 —— 所以 big 的说明卡内容都放在 y ≤ 1330 以内。
// 时间都按字幕行算：S('T20') = 这一行开始说的时刻，E('T20') = 说完的时刻，P('T20', '词') = 说到这个词的时刻（按字数估）；
// 词必须真在那一行的字幕里（scripts/check_phrases.py 会查——P() 找不到词整条渲染会抛错）。字幕行 id 就是 talk_lines.py 里的 T01…。
const SEG = id => { const g = TL.segs.find(x => x.id === id); if (!g) throw new Error('没有场景 ' + id); return g; };
const BEIGE = '#F3EEE4', INK = '#1F1B16', GRAY = '#7A7367', CORAL = '#D97757', ORG = '#FF4F1A', LINEC = '#E2DACA', WHITE = '#FFFFFF', GREEN = '#2F8F5B', RED = '#C8402F', SOFT = '#FFF6EE';
const EMO = "'Segoe UI Emoji','Noto Color Emoji','Noto Sans SC',sans-serif";
const FEMO = "'Noto Sans SC'," + EMO;

// 说明卡：整个窗口内容区一张米色底；build(root, sg) 返回 update(T)，T = 成片绝对秒（和 S() / P() 同一套）
function card(sid, build) {
  const sg = SEG(sid);
  OV.push({ t0: sg.s, t1: sg.e - 0.12, fast: true, build: p => {
    const root = mk(p, '', { position: 'absolute', inset: '0px', background: BEIGE, overflow: 'hidden', fontFamily: "'Noto Sans SC'" });
    const up = build(root, sg);
    return lt => up(lt + sg.s);
  } });
}
const fx = (el, T, t0, o = {}) => show(el, T, t0, Object.assign({ d: 0.35, dy: 22 }, o));
const txt = (r, x, y, w, size, color, html, o = {}) => at(r, x, y, w, 'auto', '', Object.assign({ font: `${o.weight || 800} ${size}px/${o.lh || 1.25} 'Noto Sans SC'`, color, textAlign: o.align || 'left', whiteSpace: o.nowrap ? 'nowrap' : 'normal' }, o.style || {}), html);
const panel = (r, x, y, w, h, o = {}) => at(r, x, y, w, h, '', Object.assign({ background: o.bg || WHITE, border: `${o.bw || 5}px solid ${o.bc || LINEC}`, borderRadius: (o.r || 36) + 'px', boxShadow: o.shadow === false ? 'none' : '0 14px 0 rgba(31,27,22,.10)', transition: 'none' }, o.style || {}));
const pill = (r, x, y, w, h, html, o = {}) => at(r, x, y, w, h, '', { background: o.bg || WHITE, border: `${o.bw || 4}px solid ${o.bc || LINEC}`, borderRadius: (o.r || 28) + 'px', display: 'flex', alignItems: 'center', justifyContent: 'center', font: `${o.weight || 800} ${o.size || 48}px/1.2 'Noto Sans SC'`, color: o.color || INK, textAlign: 'center', padding: '0 14px', boxShadow: '0 8px 0 rgba(31,27,22,.08)', fontFamily: FEMO }, html);
const kcap = (r, x, y, w, h, label, size = 110) => at(r, x, y, w, h, '', { background: WHITE, border: `7px solid ${INK}`, borderBottomWidth: '18px', borderRadius: '30px', display: 'flex', alignItems: 'center', justifyContent: 'center', font: `900 ${size}px 'JetBrains Mono','Noto Sans SC'`, color: INK }, label);
const lit = (e, on, c = ORG) => { e.style.borderColor = on ? c : LINEC; e.style.background = on ? SOFT : WHITE; e.style.transform = on ? 'scale(1.03)' : 'scale(1)'; };
const svgAt = (r, x, y, w, h, body, color = CORAL, sw = 12) => at(r, x, y, w, h, '', { pointerEvents: 'none' }, `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" fill="none" stroke="${color}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`);
// 官方镜头上的中文小标签（窗口左上角；只放在上窗）。结束时间提前 0.25 s，免得淡出时压到下一个场景
const chip = (t0, t1, text, o = {}) => note(t0, Math.max(t0 + 0.9, t1 - 0.25), text, '', Object.assign({ x: 40, y: 34, w: 1000 }, o));

// ─────────── 例子（big 场景 S03，讲 T05–T08；把注释打开、改成你的场景和字幕行）
// card('S03', r => {
//   const head = txt(r, 0, 60, 1474, 100, INK, '标题', { weight: 900, align: 'center' });
//   const a = pill(r, 150, 220, 1174, 150, '第一点', { bc: CORAL, size: 64 });
//   const b = pill(r, 150, 420, 1174, 150, '第二点', { bc: ORG, bg: SOFT, size: 64 });
//   return T => {
//     fx(head, T, S('T05') + 0.05, { dy: 0 });                     // 这一行开始说的时候出现
//     fx(a, T, P('T06', '第一点') - 0.1);                           // 说到“第一点”这个词之前 0.1 s 出现
//     fx(b, T, P('T07', '第二点') - 0.1);
//   };
// });

// ─────────── 官方镜头上的中文小标签（有英文界面 / 没中文讲解的官方镜头才加；窗口左上角）
// chip(S('T01'), E('T01'), '官方课：什么是 Claude Code');
