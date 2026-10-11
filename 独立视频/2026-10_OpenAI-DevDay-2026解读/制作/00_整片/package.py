# -*- coding: utf-8 -*-
"""给渲好的正片加悠一片头片尾（三个合集共用的模板，AI科普/skill/yuanlai-ruci-episode/scripts/add_to_video.py：正片不重编码），
成片放到 ../../成片/<V?>_<名>_成片.mp4。

  python package.py V1 [V2 …]         不带参数 = 全部
片尾清单 outro.json 是草稿，按规矩每期都要用户确认（现场画面 / 资料 / 配音 / 剪辑 / 视频剪辑模型）。
同时按“项目的中英双语字幕标准”导出三份 SRT：成片/<V?>_<名>_双语字幕.srt / _中文字幕.srt / _英文字幕.srt
（时间 = timeline.json 的 subs 显示区间 + 片头时长，只对得上加完片头片尾的成片；内容和烧进画面的字幕一致）。
"""
import json
import re
import subprocess
import sys

from common import EP, HERE, all_eps, out_dir, script_path

sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
import bilingual_std as B  # noqa: E402

ADD = r"D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py"


def export_srt(ep, name, intro):
    T = json.loads((out_dir(ep) / "timeline.json").read_text(encoding="utf-8"))
    rows = [(x["a"] + intro, x["b"] + intro, (x["who"] + "：" if x["who"] else "") + x["zh"], x["en"]) for x in T["subs"]]
    B.write_srts(str(EP / "成片" / name), rows)
    return len(rows)


def main():
    eps = sys.argv[1:] or all_eps()
    dst = EP / "成片"
    dst.mkdir(exist_ok=True)
    for ep in eps:
        name = script_path(ep).stem            # 例：V1_Dots
        src = out_dir(ep) / f"{ep}_整片.mp4"
        out = dst / f"{name}_成片.mp4"
        r = subprocess.run([sys.executable, ADD, str(src), "-o", str(out), "--outro-data", str(HERE / "outro.json")], check=True, capture_output=True, text=True)
        print(r.stdout.strip())
        intro = float(re.search(r"intro: ([0-9.]+)s rendered", r.stdout).group(1))
        n = export_srt(ep, name, intro)
        print(ep, "->", out, f"+ 三份 SRT（{n} 条，时间含片头 {intro:.2f} s）")


if __name__ == "__main__":
    main()
