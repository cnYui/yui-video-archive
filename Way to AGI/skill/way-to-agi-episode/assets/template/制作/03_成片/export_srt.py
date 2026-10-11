# -*- coding: utf-8 -*-
"""导出字幕文件（和画面里烧进去的字幕同一套时间）：双语、中文、英文三份 SRT，放在成片旁边。
成片前面有悠一片头（add_to_video.py 加的，2026-10-03 起 4.8 s），所以时间整体往后挪 INTRO 秒；INTRO 从共用模板读，模板换了不用改这里。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"D:\大疆\AI科普\片头片尾")
from pack_info import intro_seconds   # noqa: E402  共用片头片尾的时长（读 intro/index.html 的 window.DURATION）

HERE = Path(__file__).resolve().parent
NAME = HERE.parents[1].name                    # 期目录名，例如 03_<标题>
INTRO = intro_seconds()                       # 片头时长（AI科普/片头片尾/intro；2026-10-03 起 4.8 s，以前 3.8）
TL = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))


def ts(x):
    ms = int(round(max(0.0, x) * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    cues = TL["cues"]
    rows = []
    for i, c in enumerate(cues):
        nx = cues[i + 1] if i + 1 < len(cues) else None
        a = c["s"] - 0.1                                   # 和页面 subAt() 一样
        b = min(c["e"] + 0.45, nx["s"] - 0.1 if nx else TL["narr"])
        rows.append((a + INTRO, b + INTRO, c["zh"], c["en"]))
    for tag, fmt in (("双语字幕", lambda z, e: f"{z}\n{e}"), ("中文字幕", lambda z, e: z), ("英文字幕", lambda z, e: e)):
        text = "".join(f"{k + 1}\n{ts(a)} --> {ts(b)}\n{fmt(z, e)}\n\n" for k, (a, b, z, e) in enumerate(rows))
        out = HERE / f"{NAME}_{tag}.srt"
        out.write_text(text, encoding="utf-8-sig")
        print(out.name, len(rows), "条")


if __name__ == "__main__":
    main()
