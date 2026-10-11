// 叠加层。用户 2026-10-02：“视频里多出现你下载的视频演示片段，而不是你一味的在说讲解”→ 不再用静态文字卡片：
//   · 演示区放 @ClaudeDevs 的官方演示视频（plan 里带 bg 的镜头），上面只加少量标注；
//   · 没有现成视频的地方放“官方页面录屏”（pageShot：capture_pages.py 录的 claude.dev / code.claude.com 文档截图，按解说时刻滚动，对应的句子刷荧光笔，底部一条中文译文）。
// 每个叠加层：[t0, t1] 显示（前后淡入淡出），t 用成片秒数；时间都按字幕条算：S('N07') = 这条开始说的时刻，P('N09', '输入') = 说到这个词的时刻。
// 字幕条：N01… = 画外音（Fish 网页版「赛马娘（曼波欧耶版）」S2 Pro）。
const FPS = TL.fps;
window.__ERR = [];
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const easeIn = x => Math.pow(clamp(x), 3);
const easeIO = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const lerp = (a, b, x) => a + (b - a) * x;
const px = v => v + 'px';

function mk(parent, cls = '', style = {}, html = '', tag = 'div') {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  for (const [k, v] of Object.entries(style)) if (v !== undefined && v !== null) e.style[k] = typeof v === 'number' && !['opacity', 'zIndex', 'fontWeight', 'lineHeight', 'flex'].includes(k) ? px(v) : v;
  if (html) e.innerHTML = html;
  parent.appendChild(e);
  return e;
}
const at = (parent, x, y, w, h, cls = '', style = {}, html = '') => mk(parent, 'abs ' + cls, Object.assign({ left: x, top: y, width: w, height: h }, style), html);
function show(el, lt, t0, o = {}) {
  const d = o.d ?? 0.4, dy = o.dy ?? 16, dx = o.dx ?? 0;
  const a = easeOut((lt - t0) / d);
  const b = o.t1 == null ? 1 : 1 - easeIn((lt - o.t1) / (o.d1 ?? 0.3));
  const v = Math.min(a, b) * (o.max ?? 1);
  el.style.opacity = v;
  el.style.visibility = v < 0.002 ? 'hidden' : 'visible';
  const rot = o.rot != null ? ` rotate(${o.rot}deg)` : '';
  el.style.transform = `translate(${dx * (1 - a)}px, ${dy * (1 - a)}px)` + (o.scale ? ` scale(${lerp(o.scale, 1, a)})` : '') + rot;
  return v;
}
const PENDING = new Set();
function setSrc(img, src) { if (img.dataset.src !== src) { img.dataset.src = src; img.src = src; PENDING.add(img); } }
async function flush() {
  const arr = [...PENDING]; PENDING.clear();
  await Promise.all(arr.map(i => i.decode().catch(() => window.__ERR.push('图片加载失败 ' + i.dataset.src))));
}

// ─── 字幕条时间
const CU = {}; TL.cues.forEach(q => CU[q.id] = q);
const S = id => { if (!CU[id]) throw new Error('没有字幕条 ' + id); return CU[id].s; };
const E = id => { if (!CU[id]) throw new Error('没有字幕条 ' + id); return CU[id].e; };
function P(id, phrase, off = 0) {
  const q = CU[id]; const k = q.zh.indexOf(phrase);
  if (k < 0) throw new Error(`「${phrase}」不在 ${id}`);
  return q.s + (q.e - q.s) * (k / q.zh.length) + off;
}
const SEG = {}; TL.segs.forEach(s => SEG[s.id] = s);

const OV = [];   // {t0, t1, build(root) → update(lt), clip?:true（演示视频上的叠加层）}
const ovB = (t0, t1, build) => OV.push({ t0, t1, build });
const ovClip = (t0, t1, build) => OV.push({ t0, t1, build, clip: true });
const ovPage = (t0, t1, build) => OV.push({ t0, t1, build, fast: true });

// ═════════════════════════════ 官方页面录屏
// pageShot(从哪句, 到哪句, 页面图名字, [[要高亮的句子, 刷上的时刻, 中文译文?], …], {start: 起始滚动位置（图片像素）})
// 图是 capture_pages.py 截的（800 CSS 宽 × 2 倍像素 = 1600 宽），铺满演示区宽度；每条高亮出现前 0.95 s 开始往它那里滚，滚到画面偏上三分之一的位置。
const PAGE_BAR = 46;
function pageShot(from, to, key, marks, opt = {}) {
  const m = PG[key]; if (!m) throw new Error('没有页面图 ' + key);
  const t0 = S(from) - 0.2, t1 = E(to) + 0.12;
  ovPage(t0, t1, p => {
    const VW = 1474, VH = 829 - PAGE_BAR, k = VW / m.w, IH = m.h * k, PADB = 200;
    const win = at(p, 0, 0, VW, 829, '', { background: m.bg, overflow: 'hidden' });
    const view = mk(win, '', { position: 'absolute', left: 0, top: PAGE_BAR, width: VW, height: VH, overflow: 'hidden', background: m.bg });
    const sheet = mk(view, '', { position: 'absolute', left: 0, top: 0, width: VW, height: IH + PADB, willChange: 'transform' });
    const img = mk(sheet, '', { position: 'absolute', left: 0, top: 0, width: VW, height: IH, display: 'block' }, '', 'img');
    setSrc(img, 'media/' + m.src);
    const url = m.url.replace(/^https?:\/\//, '').replace(/\/$/, '');
    mk(win, '', { position: 'absolute', left: 0, top: 0, width: VW, height: PAGE_BAR, background: '#E9EBEF', borderBottom: '1px solid #CFD3DA', display: 'flex', alignItems: 'center', gap: '10px', padding: '0 18px', zIndex: 3 },
      '<i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FF5F57"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#FEBC2E"></i><i style="flex:none;width:14px;height:14px;border-radius:50%;background:#28C840"></i>' +
      `<span style="margin-left:12px;flex:1;height:30px;line-height:30px;border-radius:15px;background:#fff;padding:0 18px;font:600 19px 'JetBrains Mono';color:#4B5563;white-space:nowrap;overflow:hidden">${url}</span>`);
    const zhBar = mk(win, '', { position: 'absolute', left: 0, right: 0, bottom: 0, height: 100, background: 'rgba(27,27,31,.93)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: "800 40px 'Noto Sans SC'", padding: '0 36px', zIndex: 4, opacity: 0, whiteSpace: 'nowrap' });
    const hs = marks.map(([needle, tm, zh]) => {
      const rects = m.marks[needle];
      if (!rects) throw new Error(`页面图 ${key} 里没有高亮句子「${needle}」`);
      const frame = needle.startsWith('#sel:');                  // 图表这类整块的东西：画橙色边框，不填色（填色会盖住图）
      const els = rects.map(([x, y, w, h]) => mk(sheet, '', frame
        ? { position: 'absolute', left: x * k - 6, top: y * k - 6, width: w * k + 12, height: h * k + 12, border: '6px solid #FF4F1A', borderRadius: '12px', boxShadow: '0 0 0 8px rgba(255,79,26,.16)', transformOrigin: '0 50%', visibility: 'hidden' }
        : { position: 'absolute', left: x * k - 5, top: y * k - 3, width: w * k + 10, height: h * k + 6, background: 'rgba(255,205,40,.64)', mixBlendMode: 'multiply', borderRadius: '5px', transformOrigin: '0 50%', visibility: 'hidden' }));
      return { els, t: tm - t0, cy: (rects[0][1] + rects[0][3] / 2) * k, top: rects[0][1] * k, tall: rects[0][3] * k > VH * 0.55, zh };
    });
    const maxS = Math.max(0, IH + PADB - VH);
    hs.forEach(h => h.target = clamp(h.tall ? h.top - VH * 0.05 : h.cy - VH * 0.34, 0, maxS));      // 比窗口还高的（图表）顶部对齐
    const start = opt.start != null ? clamp(opt.start * k, 0, maxS) : (hs.length ? hs[0].target : 0);
    const seq = [{ t: -99, target: start }, ...hs];
    let curZh = null;
    return lt => {
      let sc = start;
      for (let i = 1; i < seq.length; i++) {
        const a = seq[i].t - 0.95, b = seq[i].t - 0.2;
        if (lt >= a) sc = lerp(seq[i - 1].target, seq[i].target, easeIO((lt - a) / (b - a)));
      }
      sheet.style.transform = `translateY(${-sc}px)`;
      hs.forEach((h, i) => {
        const a = easeOut((lt - h.t) / 0.45), nxt = hs[i + 1] ? hs[i + 1].t : 1e9;
        h.els.forEach(e => { e.style.visibility = a > 0.001 ? 'visible' : 'hidden'; e.style.transform = `scaleX(${a})`; e.style.opacity = lt > nxt + 0.25 ? 0.4 : 1; });
      });
      let cur = null;                                            // 底部译文：最近一条带译文且已经刷上的
      for (const h of hs) if (h.zh && lt >= h.t) cur = h;
      if (cur !== curZh) { curZh = cur; if (cur) zhBar.textContent = cur.zh; }
      zhBar.style.opacity = cur ? easeOut((lt - cur.t) / 0.3) : 0;
    };
  });
}

// ═════════════════════════════ 演示视频上的通用叠加层：章节标签、来源角标、示例标签
{
  const seen = new Set();
  TL.segs.forEach(s => {
    if (seen.has(s.chapter)) return; seen.add(s.chapter);
    if (!s.bg) return;
    ovClip(s.s + 0.3, s.s + 3.6, p => {
      const c = at(p, 22, 20, null, null, 'chapchip', { position: 'absolute' }, `<span>${String(s.chapter + 1).padStart(2, '0')}</span>${TL.chapters[s.chapter]}`);
      return lt => show(c, lt, 0, { dy: -12 });
    });
  });
}
const TAGTXT = { B_tw: '示例 1 / 3 · Token Weather · 上下文天气预报', B_game: 'claude.dev · 新主页里的像素小游戏' };
Object.entries(TL.clips).forEach(([cid, k]) => {
  ovClip(k.s + 0.1, k.e, p => {
    const c = at(p, null, 20, null, null, 'credit', { position: 'absolute' }, '画面：' + k.credit);
    const tg = TAGTXT[cid] && at(p, 22, 78, null, null, 'tagpill', { position: 'absolute' }, TAGTXT[cid]);
    return lt => { show(c, lt, 0, { dy: -8 }); if (tg) show(tg, lt, 0.5, { dy: 8 }); };
  });
});

// ═════════════════════════════ 00 开场 N03–N04：今天讲的四件事（小标签排在左上角，不挡画面）
ovClip(S('N03') - 0.1, E('N04') + 0.1, p => {
  const t0 = S('N03') - 0.1;
  const row = at(p, 22, 20, null, null, '', { display: 'flex', gap: '12px', position: 'absolute' });
  const I = ['1 Claude Code 模组', '2 claude.dev', '3 Sonnet 5.5', '4 评测'];
  const els = I.map((tx, i) => mk(row, 'tagpill', { position: 'static', fontSize: '28px', padding: '8px 20px', borderLeft: 'none', background: i ? 'rgba(255,255,255,.94)' : '#FF4F1A', color: i ? '#1B1B1F' : '#fff' }, tx));
  return lt => {
    const dim = easeOut((lt - (S('N04') - t0 - 0.05)) / 0.4);              // 说到“先说最大的这个”，其余三个变淡
    els.forEach((e, i) => { const v = show(e, lt, 0.2 + i * 0.5, { dy: -8 }); if (i) e.style.opacity = v * (1 - 0.55 * dim); });
  };
});

// ═════════════════════════════ 02 Token Weather（B_tw = 深色终端里的真实演示）：标注 + 档位图例
{
  // 输入框上方那一行（原图 y≈895–945 → 演示区 687–727）
  ovClip(S('N16') - 0.2, E('N17') + 0.5, p => {
    const t0 = S('N16') - 0.2;
    const box = at(p, 10, 678, 1452, 52, '', { border: '4px solid #FF4F1A', borderRadius: '12px', boxShadow: '0 0 0 6px rgba(255,79,26,.18)' });
    const lab = at(p, 880, 624, null, null, 'tagpill', { position: 'absolute', fontSize: '28px' }, 'Token Weather：输入框上方的这一行');
    return lt => { show(box, lt, 0.05, { dy: 0, scale: 1.02 }); show(lab, lt, 0.25, { dy: 8 }); };
  });
  // 档位图例（右上角空白处）
  ovClip(S('N18') - 0.2, E('N19') + 0.05, p => {
    const t0 = S('N18') - 0.2;
    const R = [['#CA8A04', '晴 Clear', '< 25%'], ['#0891B2', '多云 Cloudy', '25–49%'], ['#2563EB', '阵雨 Showers', '50–74%'], ['#C026D3', '暴风雨 Storm', '75–89%'], ['#E11D48', '快压缩了', '≥ 90%']];
    const rows = R.map(([c, n, r], i) => at(p, 986, 90 + i * 72, 464, 62, 'lvl', {}, `<i style="background:${c}"></i>${n}<small>${r}</small>`));
    const ts = [P('N18', '不到'), P('N18', '往上依次'), P('N18', '往上依次') + 0.4, P('N18', '暴风雨'), P('N19', '到了')];
    return lt => rows.forEach((r, i) => show(r, lt, ts[i] - t0 - 0.2, { dx: 24, dy: 0 }));
  });
  ovClip(S('N20') - 0.05, E('N20') + 1.6, p => {
    const c = at(p, 986, 90, 464, 90, 'tagpill', { position: 'absolute', fontSize: '40px', textAlign: 'center', padding: '16px 24px' }, '整个模组 ≈ <span style="color:var(--orange)">80</span> 行');
    return lt => show(c, lt, 0.1, { dy: 10 });
  });
}

// ═════════════════════════════ 03 Claude Code Playground（N41）：演示视频上的小标签
ovClip(S('N41') - 0.1, E('N41') + 0.1, p => {
  const c = at(p, 0, 84, 1474, 70, '', { textAlign: 'center' }, '<span class="tagpill" style="position:static;display:inline-block;font-size:34px;border-left:none;background:#FF4F1A;color:#fff">没灵感？Claude Code Playground 仓库里，官方正在加现成的示例模组</span>');
  return lt => show(c, lt, 0.2, { dy: -8 });
});

// ═════════════════════════════ 04 像素小游戏（N45）：一句话说明
ovClip(S('N45') - 0.1, E('N45') + 0.1, p => {
  const c = at(p, 0, 722, 1474, 70, '', { textAlign: 'center' }, '<span class="bigpill" style="font-size:38px;padding:8px 30px 10px">像素小游戏：收集 5 个火花，把太阳叫醒</span>');
  return lt => show(c, lt, 0.15, { dy: 10 });
});

// ═════════════════════════════ 05 结尾：先更新、看版本号（N58）；来源 + 感谢观看（N60–N61）
ovClip(S('N58') - 0.1, E('N58') + 0.1, p => {
  const t0 = S('N58') - 0.1;
  const a = at(p, 22, 84, null, null, 'tagpill', { position: 'absolute', font: "700 34px 'JetBrains Mono'", borderLeft: 'none', background: '#fff', color: '#111' }, 'claude update');
  const b = at(p, 22, 150, null, null, 'tagpill', { position: 'absolute', font: "700 34px 'JetBrains Mono'", borderLeft: 'none', background: '#fff', color: '#111' }, 'claude --version');
  const c = at(p, 22, 216, null, null, 'tagpill', { position: 'absolute', fontSize: '34px', borderLeft: 'none', background: '#FF4F1A', color: '#fff' }, '版本号 ≥ 2.1.287');
  return lt => { show(a, lt, P('N58', '先更新') - t0 - 0.1, { dx: -16, dy: 0 }); show(b, lt, P('N58', '看一眼') - t0 - 0.1, { dx: -16, dy: 0 }); show(c, lt, P('N58', '2.1.287') - t0 - 0.1, { dy: 0, scale: .9 }); };
});
ovClip(S('N60') - 0.1, E('N61') + 1.4, p => {
  const t0 = S('N60') - 0.1;
  const src = at(p, 0, 640, 1474, 70, '', { textAlign: 'center' }, '<span class="tagpill" style="position:static;display:inline-block;font-size:30px;border-left:none">来源：@ClaudeDevs · claude.dev · code.claude.com/docs，链接在简介里</span>');
  const th = at(p, 0, 230, 1474, 130, '', { textAlign: 'center' }, '<span class="bigpill" style="font-size:96px;padding:12px 56px 18px">感谢<em>观看</em></span>');
  return lt => { show(src, lt, 0.2, { dy: 10 }); show(th, lt, S('N61') - t0 - 0.1, { scale: .92 }); };
});

// ═════════════════════════════ 官方页面录屏镜头
// 01 模组是什么
pageShot('N05', 'N05', 'T_intro', [['settings', P('N05', '设置')], ['permission rules', P('N05', '权限规则')], ['slash commands', P('N05', '斜杠命令')], ['skills', P('N05', '技能')], ['a status line', P('N05', '状态栏')]]);
pageShot('N07', 'N07', 'T_how', [['register(on, options)', S('N07') + 0.1, '模块导出 register()，用 on(事件) 挂钩子'], ['on("tool.call"', P('N07', '几行'), '一个钩子就这几行']]);
pageShot('N08', 'N08', 'T_shortcut', [['describe the one you want and let it do the work', S('N08') + 0.2, '直接说想要的模组，让 Claude 来写'], ['Make me a Claude Code mod called token-weather', P('N08', '你想要啥'), '官方给了现成的提示词']]);
pageShot('N09', 'N09', 'D_install', [['A mod installs as a plugin, from a marketplace', S('N09') + 0.1, '模组装在插件里，从市场安装'], ['/plugin install token-chart@your-org', P('N09', '输入'), '/plugin install 模组名@市场名']]);
pageShot('N10', 'N10', 'D_where', [['Mods work in the Claude Code CLI and in the Code tab of the Claude Desktop app', S('N10') + 0.1, '命令行版和桌面版的 Code 标签页都能用']]);
pageShot('N11', 'N11', 'D_turn', [['Mods require Claude Code v2.1.287 or later', S('N11') + 0.1, '需要 Claude Code 2.1.287 或更高版本'], ['on by default', P('N11', '默认'), '默认开着']]);
pageShot('N12', 'N12', 'D_builtin', [['cc-plugin-diff', P('N12', '/diff'), '内置模组：接管 /diff，画出对比窗格'], ['cc-plugin-agents-md', P('N12', 'AGENTS.md'), '内置模组：加载 AGENTS.md 当项目说明']]);
// 02 示例和注意事项
pageShot('N27', 'N28', 'T_safety', [['safety net, not a permission system', S('N27') + 0.6, '官方原话：这只是一道安全网，不能当权限系统用'], ['get past it', S('N28') + 0.5, '只看命令文字：$(…)、别名、脚本里的 rm 能绕过去'], ['Use permission rules for a hard block', P('N28', '真要硬拦'), '真要硬拦：用权限规则']]);
pageShot('N33', 'N35', 'D_reach', [['Mods aren', P('N34', '不在沙盒'), '模组不在沙盒里'], ['A mod runs with your permissions', P('N34', '权限和'), '用你的权限运行，和 Claude Code 一样大'], ['Act on your machine as you: read and write files', P('N35', '能读写'), '像你一样操作电脑：读写文件、启动程序、联网'], ['Read your secrets: environment variables', P('N35', '环境变量'), '能读到你的密钥：环境变量、设置文件']], { start: 0 });
pageShot('N36', 'N36', 'T_share', [['only install from people you trust', S('N36') + 0.3, '先读仓库，只装信得过的人写的']]);
pageShot('N37', 'N37', 'T_validate', [['claude plugin validate', S('N37') + 0.9, '装之前先“体检”一遍'], ['hooks:', P('N37', '事件'), 'hooks：它挂了哪些事件'], ['calls:', P('N37', '要调用'), 'calls：它要调用什么']]);
pageShot('N38', 'N38', 'D_turn', [['One mod: disable or uninstall its plugin from the Installed tab in /plugin', S('N38') + 0.3, '关掉一个：在 /plugin 的“已安装”里禁用或卸载']], { start: 0 });
pageShot('N39', 'N39', 'T_share', [['/plugin marketplace add', P('N39', '三条命令'), '1 添加市场（GitHub 仓库）'], ['/plugin install', P('N39', '三条命令', 0.6), '2 安装'], ['/reload-plugins', P('N39', '三条命令', 1.2), '3 重新加载'], ['The Claude directory accepts plugins that include mods', P('N39', '也能提交'), '也能提交到 Claude 目录']], { start: 0 });
// 03 顺带三件事
pageShot('N42', 'N44', 'H_top', [['Getting started with Claude Code mods', S('N42') + 0.4], ['Automating eval design and hillclimbing with Claude', S('N42') + 1.3], ['Building with Claude Sonnet 5.5', S('N42') + 2.1, '官方推荐的三篇：模组入门、评测命令、Sonnet 5.5 指南'],
  ['Sharing tips, tricks, and POVs', P('N43', '开发者'), 'claude.dev：给开发者的新主页'], ['ENGINEERING', P('N44', '工程'), '工程深度文章'], ['PLAYBOOKS', P('N44', '指南'), 'Claude Code 和 API 的指南'], ['TUTORIALS', P('N44', '经验'), '各个团队的经验和教程']], { start: 0 });
pageShot('N46', 'N49', 'S_hero', [['second model in the Claude 5.5 family', P('N46', '家族'), '5.5 家族的第二个模型（前面是 Opus 5.5）'], ['smarter, more efficient and 30% faster', S('N48') + 0.1, '更聪明、更省 token、快 30% 以上'], ['The per-token price is unchanged', S('N49') + 0.1, '每个 token 的单价没变'], ['costs up to 30% less for most work', P('N49', '最多便宜'), '大多数任务最多便宜 30%']]);
pageShot('N50', 'N50', 'S_choose', [['well-scoped everyday tasks like fixing bugs and quickly iterating on features', S('N50') + 0.3, '边界清楚的日常活：修 bug、快速改功能 → Sonnet 5.5'], ['Opus 5.5 is built for complex work', P('N50', '最难的'), '要把握分寸的复杂活 → Opus 5.5']]);
pageShot('N51', 'N51', 'S_cc', [['/model sonnet', P('N51', '输入'), 'Claude Code 里用 /model sonnet 切换'], ['The default model stays Opus 5.5', P('N51', '默认模型'), '默认模型仍是 Opus 5.5']]);
pageShot('N52', 'N56', 'E_intro', [['claude-api skill', S('N53') + 0.3, 'claude-api 技能里新增两个命令'], ['/claude-api build-eval', S('N54') + 0.2, '/claude-api build-eval：给你的应用建评测'], ['/claude-api hillclimb', S('N55') + 0.2, '/claude-api hillclimb：对着评测，一次改一处'], ['held-out set of examples', S('N56') + 0.4, '留一部分没见过的样例，防止光背题']]);
pageShot('N57', 'N57', 'E_fig8', [['#sel:figure.art-fig', S('N57') + 0.1, '官方示例：客服工单评测的成本和准确率'], ['at about one fifth of the cost', P('N57', '五分之一') + 0.1, '成本约五分之一，没见过的题上准确率 78.6% → 90.5%']], { start: 1000 });
pageShot('N59', 'N59', 'T_shortcut', [['Make me a Claude Code mod called token-weather', S('N59') + 0.8, '官方把提示词写好了，复制给 Claude Code']], { start: 0 });
