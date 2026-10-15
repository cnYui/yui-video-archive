# -*- coding: utf-8 -*-
"""建系列引擎库 engine_lib/：从《人人都是 UI 设计师》短视频的引擎副本（贴纸 / 来源小字 / 每场景小标题 / 温柔男生估时 / BGM −9 dB）快照出来，
改成单框版式用（index.html 去掉面板样式、来源小字挪到单框上方、加照片镜头样式）；scenes_lib.js 是系列自己写的（页面录屏的深色页高亮、照片镜头、大数字卡）。

  python make_engine_lib.py        只会覆盖 engine_lib 里“从别处快照来的”那几个文件，scenes_lib.js 不动
"""
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE / "engine_lib"
UI = Path(r"D:\大疆\独立视频\短视频\2026-10_人人都是UI设计师\制作\00_整片")
LIB.mkdir(exist_ok=True)

for name in ("engine.js", "check_subs.py", "build_timeline.py", "mix_audio.py"):
    shutil.copy(UI / name, LIB / name)

html = (UI / "index.html").read_text(encoding="utf-8")
# 去掉对比图面板 / 缩略图墙的样式（本系列用不到），只留贴纸和来源小字
a = html.index("/* 对比图面板镜头")
b = html.index("</style>")
html = html[:a] + '''/* 照片镜头（作者照 / 文章配图 / X 横幅）：框里放一张图，缓慢推近 */
.ph { position:absolute; max-width:none; display:block; will-change:transform; }
''' + html[b:]
html = re.sub(r"#credit \{[^}]*\}", "#credit { position:absolute; left:56px; top:722px; font:700 24px/30px 'Noto Sans SC'; color:var(--gray); letter-spacing:.03em; white-space:nowrap; z-index:6; }", html)
html = html.replace('<script src="panels.js"></script>\n', '<script src="photos.js"></script>\n')
html = html.replace("<!-- 【本条改动，模板原样见 技能 assets/engine-template/】《人人都是 UI 设计师》：没有视频素材，画面全是静态图。",
                    "<!-- 【系列改动，模板原样见 技能 assets/engine-template/】《Tim Denning 的 36 条忠告》系列（单框）：没有视频素材，画面全是页面录屏 / 照片。")
(LIB / "index.html").write_text(html, encoding="utf-8")
assert 'src="photos.js"' in html and "panels.js" not in html
print("engine_lib 里的快照文件：", ", ".join(sorted(p.name for p in LIB.iterdir())))
