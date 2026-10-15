# -*- coding: utf-8 -*-
"""把本条副本的引擎文件同步到技能模板的最新版（技能 2026-10-04 一天里改了好几次：版式 B、边框 6、随机背景、who、变速、mix_audio 修复……）。
保留本条自己的：common.py（素材表）、capture_pages.py（GitHub 页面 SPECS）、scenes.js 里的「本条」叠加层。
改之前的文件备份在 _同步模板前备份\\。背景按技能的规矩随机挑一张（assets/backgrounds → bg.png + bg.json）。
"""
import json
import random
import shutil
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TPL = Path(r"D:\大疆\短视频\skill\short-video\assets\engine-template")
BG = Path(r"D:\大疆\短视频\skill\short-video\assets\backgrounds")
BAK = HERE / "_同步模板前备份"
BAK.mkdir(exist_ok=True)

# 1) 本条的 scenes.js：模板最新版 + 本条的叠加层
cur = (HERE / "scenes.js").read_text(encoding="utf-8")
a = cur.index("// ═════════════════════════════ 本条（image-blaster 推荐")
b = cur.index("\n// GitHub 链接条（字幕下面，y 1658）")                   # 旧副本里追加的 linkPill 函数，模板里已有
mine = cur[a:b].rstrip() + "\n"
for f in ("index.html", "engine.js", "check_subs.py", "build_timeline.py", "prep_frames.py", "mix_audio.py", "render_all.py", "finish.py", "qa_mix.py", "scenes.js"):
    if (HERE / f).exists():
        shutil.copy2(HERE / f, BAK / f)
tpl_scenes = (TPL / "scenes.js").read_text(encoding="utf-8").rstrip() + "\n\n"
(HERE / "scenes.js").write_text(tpl_scenes + mine, encoding="utf-8")
for f in ("index.html", "engine.js", "check_subs.py", "build_timeline.py", "prep_frames.py", "mix_audio.py", "render_all.py", "finish.py", "qa_mix.py"):
    shutil.copy2(TPL / f, HERE / f)

# 2) 背景：技能规定每条随机挑一张（color / ink / orange）
pool = sorted(BG.glob("pattern_*.png"))
pool = [p for p in pool if p.stem != "pattern_none"]
pick = random.choice(pool)
shutil.copy2(pick, HERE / "bg.png")
(HERE / "bg.json").write_text(json.dumps({"file": pick.name, "how": "随机", "time": time.strftime("%Y-%m-%d %H:%M:%S")}, ensure_ascii=False, indent=1), encoding="utf-8")
print("同步完成；背景随机挑到", pick.name)
