# -*- coding: utf-8 -*-
"""建一期《Way to AGI》目录：D:\\大疆\\Way to AGI\\NN_<标题>\\，拷入制作模板（02_出镜、03_成片、04_封面）和 README。

  python new_episode.py --number 3 --title "标题"

已存在的目录不覆盖（报错退出）。模板里的字幕条、画面、封面文字都是第 02 期的例子，按本期重写。
"""
import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
COLLECTION = Path(r"D:\大疆\Way to AGI")

README = """# {nn}_{title}

《Way to AGI》第 {nn} 期（悠一出镜；B 站合集「Way to AGI」+ YouTube 播放列表「Way to AGI」）。建于 {today}。

- 录像：SD 卡 `H:\\DCIM\\DJI_001\\`，编号：（填）
- 素材：`素材\\`
- 片尾制作清单：（问用户后填，写进 `制作\\03_成片\\outro.json`）
- 成片：`<{nn}_{title}>_成片.mp4`（= 悠一片头 3.8 s + 正片 + 悠一片尾 4.8 s）
- 发布：B 站（BV 号）、YouTube（链接）——发布后填，同时更新 `Way to AGI\\README.md`

流程见技能 `way-to-agi-episode`（`C:\\Users\\yui\\.claude\\skills\\way-to-agi-episode\\SKILL.md`）。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--number", type=int, required=True)
    ap.add_argument("--title", required=True)
    args = ap.parse_args()
    nn = f"{args.number:02d}"
    title = re.sub(r'[\\/:*?"<>|]', "", args.title).strip()
    ep = COLLECTION / f"{nn}_{title}"
    if ep.exists():
        sys.exit(f"已存在：{ep}")
    shutil.copytree(SKILL / "assets" / "template", ep)
    (ep / "素材").mkdir(exist_ok=True)
    (ep / "README.md").write_text(README.format(nn=nn, title=title, today=date.today().isoformat()), encoding="utf-8")
    print("created", ep)
    for p in sorted(ep.rglob("*")):
        if p.is_file():
            print("  ", p.relative_to(ep))


if __name__ == "__main__":
    main()
