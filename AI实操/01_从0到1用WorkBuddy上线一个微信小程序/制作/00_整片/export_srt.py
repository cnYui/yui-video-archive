# -*- coding: utf-8 -*-
"""字幕导出：读 ../02_出镜/edit/edit.json 的字幕条，显示时间和页面里一样（开始前 0.1 s 出现，结束后留 0.45 s，不和下一条重叠）。

  python export_srt.py   → 整片_v4_中文字幕.srt（对应不带片头片尾的整片）、整片_v4_中文字幕_加片头.srt（时间 + 片头 3.8 s，对应加完片头片尾的成片）
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INTRO = 3.8


def ts(t):
    t = max(0.0, t)
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}".replace(",1000", ",999")


def main():
    cues = json.loads((HERE.parent / "02_出镜" / "edit" / "edit.json").read_text(encoding="utf-8"))["cues"]
    for name, off in (("整片_v4_中文字幕.srt", 0.0), ("整片_v4_中文字幕_加片头.srt", INTRO)):
        lines = []
        for i, q in enumerate(cues):
            nx = cues[i + 1] if i + 1 < len(cues) else None
            a = q["out_s"] - 0.1
            b = min(q["out_e"] + 0.45, nx["out_s"] - 0.1) if nx else q["out_e"] + 0.45
            lines.append(f"{i + 1}\n{ts(a + off)} --> {ts(b + off)}\n{q['zh']}\n")
        (HERE / name).write_text("\n".join(lines), encoding="utf-8")
        print(name, len(cues), "条")


if __name__ == "__main__":
    main()
