# -*- coding: utf-8 -*-
r"""新建 OpenAI相关 合集的一期：目录骨架 + 引擎模板 + 台本骨架 + 封面规格。

  python new_episode.py --num 02 --name 短名 [--root D:\大疆\OpenAI相关]

建出 <root>\NN_<短名>\：素材\X平台视频\、台本\（录制稿.json / plan.json 骨架）、制作\00_整片\（引擎模板，字幕是中英双语）、
制作\02_配音\（build_voice.py，故事工作室逐句 wav 拼口播）、制作\04_封面\cover.json（openai-cover 技能的规格骨架）。已存在就不动。
建完照 SKILL.md 的步骤往下做；最后打印要补进 .gitignore 的几行。
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SK = Path(__file__).resolve().parents[1]
COVER_SK = SK.parent / "openai-cover"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--num", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--root", default=r"D:\大疆\OpenAI相关")
    ap.add_argument("--bg", default=None, help="指定背景印花文件名（landscape_*.png），none = 不用；默认随机")
    a = ap.parse_args()
    ep = Path(a.root) / f"{a.num}_{a.name}"
    if ep.exists():
        sys.exit(f"{ep} 已经存在，不动")
    for d in ("素材/X平台视频", "台本", "制作/00_整片", "制作/02_配音/tts/seg_raw", "制作/02_配音/edit", "制作/04_封面"):
        (ep / d).mkdir(parents=True)
    for f in (SK / "assets" / "engine-template").iterdir():
        shutil.copy(f, ep / "制作" / "00_整片" / f.name)
    shutil.copy(SK / "assets" / "voice-template" / "build_voice.py", ep / "制作" / "02_配音" / "build_voice.py")
    for f in (SK / "assets" / "script-template").iterdir():
        shutil.copy(f, ep / "台本" / f.name)
    spec = COVER_SK / "assets" / "cover.example.json"
    if spec.exists():
        shutil.copy(spec, ep / "制作" / "04_封面" / "cover.json")
    # 横版背景印花：随机挑一张 landscape_*.png → 本期 bg.png / bg.json（2026-10-05 用户定：之后横版视频都随机选一张）；--bg 指定、--bg none 不用
    subprocess.run([sys.executable, r"D:\大疆\短视频\skill\short-video\assets\backgrounds\pick_bg.py", str(ep / "制作" / "00_整片")] + (["--bg", a.bg] if getattr(a, "bg", None) else []), check=True)
    rel = ep.relative_to(Path(a.root).parent).as_posix()
    print(f"已建 {ep}\n下一步：1) 下载素材到 素材/X平台视频/ 并填 制作/00_整片/common.py 的素材表；2) 事实核对（references/facts.md）→ 写台本（zh / say / en 三栏）和 plan.json；"
          f"3) 配音（references/voice.md）；4) build_timeline → check_subs → prep_frames → mix_audio → render_all → qa_mix → finish；5) 封面（openai-cover 技能）；6) 投稿（references/publish.md）。")
    print(f"\n公开仓库：往 D:/大疆/.gitignore 末尾补（路径前缀 /{rel}/）：")
    for x in ("制作/00_整片/frames.js", "制作/00_整片/timeline.js", "制作/00_整片/timeline.json", "制作/00_整片/media/", "制作/00_整片/parts/", "制作/00_整片/stills/",
              "制作/02_配音/tts/", "制作/02_配音/edit/", "制作/04_封面/*.png"):
        print(f"/{rel}/{x}")


if __name__ == "__main__":
    main()
