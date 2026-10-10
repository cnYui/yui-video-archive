# -*- coding: utf-8 -*-
"""给一条视频随机挑一张背景印花：复制成 <目录>\\bg.png，把挑了哪张写进 <目录>\\bg.json（以后重渲不会换）。

  python pick_bg.py <目录> [--pool landscape|pattern] [--bg 文件名|none]

--pool landscape（默认）= 横版视频（2340×1080）：从 landscape_*.png 里随机挑（三张：原色 / 墨色 / 橙色，2026-10-05 用户定：“之后横板视频也要随机选一张图片”）；
--pool pattern        = 竖屏短视频（1080×2340）：从 pattern_*.png 里随机挑（short-video 的 new_short.py 自己也是这么挑的，这里给手工用）；
--bg <文件名>         = 指定这一张；--bg none = 这条不用印花（bg.json 记 none，不拷 bg.png）。
目录里已经有 bg.json 就不再随机（要换就加 --bg 指定，或删掉 bg.json）。横版引擎的 index.html 用 `background:#fff url(bg.png) 0 0/2340px 1080px no-repeat`，
所以**用了这个脚本的目录里一定要有 bg.png**（选 none 时要把 index.html 里的 url(bg.png) 去掉）。PNG 不进公开仓库。
"""
import argparse
import json
import random
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dest")
    ap.add_argument("--pool", default="landscape", choices=["landscape", "pattern"])
    ap.add_argument("--bg", default=None)
    a = ap.parse_args()
    dest = Path(a.dest)
    dest.mkdir(parents=True, exist_ok=True)
    meta = dest / "bg.json"
    if meta.exists() and a.bg is None:
        print("已经挑过：", json.loads(meta.read_text(encoding="utf-8")))
        return
    pool = sorted(p.name for p in HERE.glob(f"{a.pool}_*.png") if p.name != "pattern_none.png")
    if not pool:
        raise SystemExit(f"{HERE} 里没有 {a.pool}_*.png")
    if a.bg == "none":
        meta.write_text(json.dumps({"file": "none", "pool": pool}, ensure_ascii=False, indent=1), encoding="utf-8")
        print("这条不用印花（index.html 里去掉 url(bg.png)）")
        return
    pick = a.bg or random.SystemRandom().choice(pool)
    assert pick in pool, f"{pick} 不在池里：{pool}"
    shutil.copy2(HERE / pick, dest / "bg.png")
    meta.write_text(json.dumps({"file": pick, "pool": pool, "how": "指定" if a.bg else "随机"}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"背景印花：{pick}（{'指定' if a.bg else '随机'}，池 {pool}）→ {dest / 'bg.png'}")


if __name__ == "__main__":
    main()
