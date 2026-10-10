# -*- coding: utf-8 -*-
"""把「版式 B + 边框 6（粗描边硬阴影）+ 链接条」移植进技能模板 short-video/assets/engine-template（只改版式，不碰背景印花机制 hasbg / bg.png、变速、pageShot 等别人加的东西）。
  python port_to_template.py            改模板（改之前把原文件备份成 *.bak_版式前）
  python port_to_template.py --episode  同样的注释块也同步到 image-blaster 那条的 index.html
"""
import shutil
import sys
from pathlib import Path

TPL = Path(r"D:\大疆\短视频\skill\short-video\assets\engine-template")
EP = Path(r"D:\大疆\独立视频\短视频\2026-10_image-blaster推荐\制作\00_整片")

HEADER = """     两种版式（plan.json 顶层 "layout"）——2026-10-04 用户选定「版式 B + 边框 6」（样图见 D:\\大疆\\短视频\\版式方案_20261004\\）：
       single（单框，新闻短条）            dual（两个横屏视频：长视频二次剪辑、对照；两框叠在一起，字幕在下）
       0–250     留空：手机状态栏 + 抖音 / B 站顶上的标签栏会盖住（两种一样）
       280–570   标题（整条视频一直在）：kicker 小字 + 两行大字（第一行黑 76 px ≤ 12 字，第二行橙 60 px ≤ 15 字），照 AI大圆镜 的做法（两种一样）
       single：770–1339 视频框 1000×569（7 px 黑描边 + 橙色硬阴影，右上角黄色贴纸 = 当前场景的来源 credit），里面按 1474×829 的坐标写、整体缩放 0.6689
               1498–1608 字幕（中文一行 52 px ≤ 约 17 字 + 英文一行 30 px ≤ 约 60 字符，居中，左右各留 ≥ 70 px）
               1658 起   信息条：大数字卡 big()（紧凑版 205 px 高）或 GitHub 链接条 linkPill()（96 px 高），不要同时出现
       dual：  680–1170 上框 860×490、1194–1684 下框 860×490（x 110–970，同一种边框，缩放 0.5739），字幕 1764–1876
       间距：标题 → 视频框 200（dual 110）、视频框 → 字幕 160（dual 80）；背景印花 bg.png（assets/backgrounds，每条随机挑一张）
       1950–2340 留空：抖音的账号名、文案、音乐条会盖住
     右边 x ≥ 940、y 1170–1990 一带是抖音的点赞 / 评论按钮：长字幕、卡片别贴右边（视频框下半截会被按钮栏盖住一点，不放关键内容在右下角）。
     没有悠一片头片尾（用户 2026-10-04：“短视频开头和结尾不要用开场和收尾的视频片段”），也没有左栏目录。 -->"""

CSS_FRAME = """.frame { position:absolute; background:#141413; padding:0; border:7px solid #141413; border-radius:14px; box-shadow:14px 14px 0 var(--accent); }
.frame::after { content:attr(data-tag); position:absolute; right:-8px; top:-40px; background:var(--marker); color:var(--ink); border:5px solid #141413; border-radius:10px; padding:0 16px; font:900 26px/38px 'Noto Sans SC'; transform:rotate(3deg); white-space:nowrap; z-index:6; }
.frame[data-tag='']::after, .frame:not([data-tag])::after { display:none; }
.frame .inner { position:relative; width:100%; height:100%; border-radius:4px; overflow:hidden; background:#111; }
"""
CSS_POS = """#demo { left:40px; top:770px; width:1000px; height:569px; }
#demo2 { left:110px; top:1194px; width:860px; height:490px; display:none; }
body.dual #demo { left:110px; top:680px; width:860px; height:490px; }
body.dual #demo2 { display:block; }
"""
CSS_CARD = """.bigcard { position:absolute; left:90px; width:900px; text-align:center; background:#fff; border:1px solid var(--line); border-top:8px solid var(--accent); border-radius:22px; box-shadow:0 16px 40px rgba(0,0,0,.12); padding:14px 30px 18px; }
.bigcard .n { font:900 92px/1.05 'Space Grotesk','Noto Sans SC'; color:var(--accent); white-space:nowrap; }
.bigcard .n small { font:800 42px 'Noto Sans SC'; color:var(--ink); margin-left:8px; }
.bigcard .d { margin-top:4px; font:700 34px/1.4 'Noto Sans SC'; color:var(--ink2); }
.linkpill { position:absolute; left:90px; width:900px; box-sizing:border-box; text-align:center; background:#16181D; color:#fff; border-radius:26px; padding:20px 24px 22px; font:700 42px/1.2 'JetBrains Mono','Noto Sans SC'; box-shadow:0 14px 34px rgba(0,0,0,.28); white-space:nowrap; }
.linkpill i { font-style:normal; color:#9CA3AF; } .linkpill b { color:#FFD84D; font-weight:800; }

"""

LINKPILL_JS = """
// GitHub 链接条（整页坐标，字幕下面 y 1658，96 px 高）：展示 GitHub 页面的几秒里把链接亮出来（用户 2026-10-04）
//   linkPill(S('N02') + 0.05, E('N02') + 0.35, 'github.com/', 'neilsonnn/<b>image-blaster</b>')   和 big() 的位置相同，不要同时出现
function linkPill(t0, t1, host, path, o = {}) {
  ovP(t0, t1, p => {
    const el = at(p, null, null, null, null, 'linkpill', { top: o.y ?? 1658 }, `<i>${host}</i>${path}`);
    return lt => show(el, lt, 0, { dy: 24, scale: 0.96 });
  });
}
"""


def patch_index(path):
    s = path.read_text(encoding="utf-8")
    a = s.index('     两种版式（plan.json 顶层 "layout"）')
    b = s.index("-->", a) + 3
    s = s[:a] + HEADER + s[b:]
    a, b = s.index(".frame { position:absolute;"), s.index("#demo { left:")
    s = s[:a] + CSS_FRAME + s[b:]
    a, b = s.index("#demo { left:"), s.index(".demoin {")
    s = s[:a] + CSS_POS + s[b:]
    assert "transform:scale(0.659430); transform-origin:0 0; }" in s
    s = s.replace("transform:scale(0.659430); transform-origin:0 0; }", "transform:scale(0.668928); transform-origin:0 0; }   /* 单框：(1000 − 2×7)/1474；dual：(860 − 14)/1474 */\nbody.dual .demoin { transform:scale(0.573948); }", 1)
    assert ".credit {" in s
    s = s.replace(".credit {", ".credit { display:none !important;", 1)       # 来源改成边框贴纸，框里的角标不再画
    a, b = s.index(".bigcard {"), s.index("/* 字幕")
    s = s[:a] + CSS_CARD + s[b:]
    assert "#subs { position:absolute; left:0; top:1195px;" in s
    s = s.replace("#subs { position:absolute; left:0; top:1195px;", "#subs { position:absolute; left:0; top:1498px;", 1)
    s = s.replace("#subZh {", "body.dual #subs { top:1764px; }\n#subZh {", 1)
    path.write_text(s, encoding="utf-8")


def patch_engine(path):
    t = path.read_text(encoding="utf-8")
    if "demoEl" in t:
        return
    t = t.replace("const headEl = document.getElementById('head');", "const headEl = document.getElementById('head');\nconst demoEl = document.getElementById('demo');", 1)
    key = "  headEl.style.opacity = 1;\n"
    assert key in t
    t = t.replace(key, key + "\n  // 边框右上角的贴纸 = 当前场景的来源（clip 场景的 credit；页面场景不贴）\n  const sg = TL.segs[segAt(t)], ck = TL.clips[sg.id], tag = ck && ck.overlay === 'clip' && ck.credit ? ck.credit : '';\n  if (demoEl.dataset.tag !== tag) demoEl.dataset.tag = tag;\n", 1)
    path.write_text(t, encoding="utf-8")


def patch_scenes(path):
    u = path.read_text(encoding="utf-8")
    if "function linkPill" in u:
        return
    assert "top: o.y ?? 1440 }" in u
    u = u.replace("top: o.y ?? 1440 }", "top: o.y ?? 1658 }", 1)
    u = u.replace("// 大数字卡片（整页坐标，放在字幕下面 y 1420–1900 那一带）", "// 大数字卡片（整页坐标，版式 B：字幕下面 y 1658 起，紧凑版 205 px 高；不要和 linkPill 同时出现）", 1)
    marker = "// ═════════════════════════════ 本条的叠加层"
    assert marker in u
    u = u.replace(marker, LINKPILL_JS.lstrip("\n") + "\n" + marker, 1)
    path.write_text(u, encoding="utf-8")


def main():
    for name in ("index.html", "engine.js", "scenes.js", "check_subs.py"):
        shutil.copy2(TPL / name, TPL / (name + ".bak_版式前"))
    patch_index(TPL / "index.html")
    patch_engine(TPL / "engine.js")
    patch_scenes(TPL / "scenes.js")
    shutil.copy2(EP / "check_subs.py", TPL / "check_subs.py")              # 模板里的 check_subs.py 和我的旧快照一模一样，直接换
    print("模板已改：index.html / engine.js / scenes.js / check_subs.py（原文件在 *.bak_版式前）")


if __name__ == "__main__":
    main()
