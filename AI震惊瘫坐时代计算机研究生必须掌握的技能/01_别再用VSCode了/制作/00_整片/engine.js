// 引擎：renderAt(t)。和第 02 期一样，另加：出镜框里的提词和进度条、开场的“悠一 Yui”名字条、目录可以不显示（toc 为 null）或全部算讲过（toc = -1）。
// 白板版：场景按声音时间 t 选；场景内容按 lv = lt + LEAD 求值（画面比声音早 LEAD 秒）；出镜、提词、目录跟声音。
const stage = document.getElementById('stage'), tocEl = document.getElementById('toc'), camEl = document.getElementById('cam');
const camPid = document.getElementById('campid'), camImg = document.getElementById('camimg'), nameEl = document.getElementById('nametag');
let cur = null, tocChap = null;
const sceneIdx = t => { const sc = TLD.scenes; for (let i = sc.length - 1; i >= 0; i--) if (t >= sc[i].start - 1e-6) return i; return 0; };
const camRect = L => L === 'A' ? CAM.A : CAM.P;
const tocOn = s => s && s.layout === 'B' && s.toc !== null;

function buildToc(s) {
  const ch = TLD.chapters[s.chapter];
  tocEl.innerHTML = `<div class="t">${ch.title}</div>` + ch.items.map((t, i) => `<div class="it" data-i="${i}"><span class="b"></span>${t}</div>`).join('');
  tocChap = s.chapter;
}

window.renderAt = async function (t) {
  const i = sceneIdx(t), s = TLD.scenes[i], prev = TLD.scenes[i - 1], next = TLD.scenes[i + 1];
  const lt = t - s.start, dur = s.end - s.start;
  if (!cur || cur.s !== s) {
    stage.innerHTML = '';
    const root = mk(stage, 'root');
    const api = await S[s.type](root, s);
    cur = { s, root, api };
  }
  // 出镜位：版式变化时移动 0.7 秒
  const a = prev ? camRect(prev.layout) : camRect(s.layout), b = camRect(s.layout), g = easeIO(lt / MOVE);
  const r = a === b ? b : { x: lerp(a.x, b.x, g), y: lerp(a.y, b.y, g), w: lerp(a.w, b.w, g), h: lerp(a.h, b.h, g) };
  Object.assign(camEl.style, { left: px(r.x), top: px(r.y), width: px(r.w), height: px(r.h), fontSize: px(r.w / 1156 * 46) });
  const pNow = s.paras.map(p => PARA[p]).filter(p => t >= p.start - 1e-6).pop();
  camPid.textContent = '';
  setSrc(camImg, `media/cam/f_${pad(Math.round(t * FPS), 5)}.jpg`);
  nameEl.style.opacity = s.type === 'intro' ? Math.min(easeOut((lt - 0.4) / 0.4), 1 - easeIn((lt - (dur - 0.5)) / 0.4)) : 0;
  // 左下目录（版式 B 且 toc 不为 null）
  if (tocOn(s)) {
    if (tocChap !== s.chapter) buildToc(s);
    const inA = (tocOn(prev) && prev.chapter === s.chapter) ? 1 : easeOut((lt - 0.3) / 0.4);
    const outA = (tocOn(next) && next.chapter === s.chapter) ? 1 : 1 - easeIn((lt - (dur - 0.3)) / 0.3);
    tocEl.style.opacity = Math.min(inA, outA);
    tocEl.querySelectorAll('.it').forEach(e => { const k = +e.dataset.i; e.className = 'it' + (k === s.toc ? ' now' : (s.toc === -1 || k < s.toc) ? ' done' : ''); });
  } else tocEl.style.opacity = 0;
  // 画面内容淡入淡出
  const delay = prev && prev.layout !== s.layout ? 0.3 : 0;
  const ain = easeOut((lt - delay) / FIN), aout = 1 - easeIn((lt - (dur - FOUT)) / FOUT);
  cur.root.style.opacity = Math.min(ain, aout);
  cur.root.style.transform = `translateY(${(1 - ain) * 14}px)`;
  const lv = lt + LEAD;
  cur.api.update(lv);
  if (cur.api.H) cur.api.H.update(lv);
  await flush();
  return true;
};
window.META = { FPS, TOTAL: TLD.total, W: 2340, H: 1080 };
