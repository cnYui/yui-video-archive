# -*- coding: utf-8 -*-
r"""新建 Claude Code相关 合集的一期：目录骨架 + 引擎模板（中英双语字幕）+ 台本骨架 + 配音脚本 + 投稿信息脚本。

  python new_episode.py --num 04 --name 短名 [--root D:\大疆\Claude Code相关]

建出 <root>\NN_<短名>\：素材\X平台视频_ClaudeDevs\、素材\网页截图\、台本\（录制稿.json / plan.json 骨架）、制作\00_整片\（引擎模板，字幕是中英双语）、
制作\02_配音\（build_voice.py + import_segments.py：故事工作室逐句 wav 拼口播）、制作\04_封面\（封面候选.json 骨架，给 claude-code-cover 的 make_candidates.py 用）、make_submission.py（投稿信息）。已存在就不动。
建完照 SKILL.md 的步骤往下做；最后打印要补进 .gitignore 的几行。
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SK = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--num", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--root", default=r"D:\大疆\Claude Code相关")
    ap.add_argument("--bg", default=None, help="指定背景印花文件名（landscape_*.png），none = 不用；默认随机")
    a = ap.parse_args()
    ep = Path(a.root) / f"{a.num}_{a.name}"
    if ep.exists():
        sys.exit(f"{ep} 已经存在，不动")
    for d in ("素材/X平台视频_ClaudeDevs", "素材/网页截图", "台本", "制作/00_整片", "制作/02_配音/tts/seg_raw", "制作/02_配音/edit", "制作/04_封面"):
        (ep / d).mkdir(parents=True)
    for f in (SK / "assets" / "engine-template").iterdir():
        shutil.copy(f, ep / "制作" / "00_整片" / f.name)
    for f in (SK / "assets" / "voice-template").iterdir():
        shutil.copy(f, ep / "制作" / "02_配音" / f.name)
    for f in (SK / "assets" / "script-template").iterdir():
        shutil.copy(f, ep / "台本" / f.name)
    shutil.copy(SK / "assets" / "submission-template" / "make_submission.py", ep / "make_submission.py")
    shutil.copy(SK / "assets" / "cover-template" / "封面候选.json", ep / "制作" / "04_封面" / "封面候选.json")
    # 横版背景印花：随机挑一张 landscape_*.png → 本期 bg.png / bg.json（2026-10-05 用户定：之后横版视频都随机选一张）；--bg 指定、--bg none 不用
    subprocess.run([sys.executable, r"D:\大疆\短视频\skill\short-video\assets\backgrounds\pick_bg.py", str(ep / "制作" / "00_整片")] + (["--bg", a.bg] if getattr(a, "bg", None) else []), check=True)
    rel = ep.relative_to(Path(a.root).parent).as_posix()
    print(f"已建 {ep}")
    print("下一步（细节在 SKILL.md 和 references/）：\n"
          "  1) 下载官方视频：python scripts/fetch_x_video.py <推文链接> --out <本期>/素材/X平台视频_ClaudeDevs，并填 制作/00_整片/common.py 的素材表；\n"
          "  2) 后台起事实核对子代理（references/facts.md，15 分钟时间盒），同时 python scripts/tsheet.py 看素材；\n"
          "  3) 写台本（zh / say / en 三栏）和 plan.json；capture_pages.py 填 SPECS 录官方页面 / 推文；scenes.js 写叠加层；\n"
          "  4) 配音（references/voice.md）→ build_voice.py；5) build_timeline → check_subs → prep_frames → render_all --stills-segs（逐张看）→ mix_audio → render_all → qa_mix → finish；\n"
          "  6) 封面：填 制作/04_封面/封面候选.json 的 TODO → claude-code-cover/scripts/make_candidates.py（3 个候选 + 验收 + 总览图）→ 用户选 → --select；\n"
          "  7) make_submission.py → 投稿（references/publish.md）→ scripts/predeliver_check.py 自查。")
    print(f"\n公开仓库：往 D:/大疆/.gitignore 末尾补（路径前缀 /{rel}/）：")
    for x in ("制作/00_整片/frames.js", "制作/00_整片/timeline.js", "制作/00_整片/timeline.json", "制作/00_整片/media/", "制作/00_整片/audio/", "制作/00_整片/parts/",
              "制作/00_整片/stills/", "制作/02_配音/tts/", "制作/02_配音/edit/", "制作/04_封面/*.png"):
        print(f"/{rel}/{x}")


if __name__ == "__main__":
    main()
