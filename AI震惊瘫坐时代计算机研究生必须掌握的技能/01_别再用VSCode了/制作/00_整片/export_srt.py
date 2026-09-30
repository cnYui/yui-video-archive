# -*- coding: utf-8 -*-
"""导出字幕文件（和画面里烧进去的字幕同一套时间）：双语、中文、英文三份 SRT，放在成片旁边。
时间 = edit.json 里的 out_s/out_e + 片头 3.8 s。"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EDIT = HERE.parent / "02_出镜/edit/edit.json"
NAME = "别再用VSCode了_v2"
INTRO = 3.8                                               # 片头时长（s）


def ts(x):
    ms = int(round(max(0.0, x) * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    d = json.loads(EDIT.read_text(encoding="utf-8"))
    cues = d["cues"]
    rows = []
    for i, c in enumerate(cues):
        nx = cues[i + 1] if i + 1 < len(cues) else None
        a = c["out_s"] - 0.1 + INTRO                     # 字幕提前 0.1 s 出现
        b_raw = c["out_e"] + 0.45 + INTRO                 # 字幕延迟 0.45 s 消失
        b_cap = (nx["out_s"] - 0.1 + INTRO) if nx else (d["total"] + INTRO)
        b = min(b_raw, b_cap)
        rows.append((a, b, c["zh"], c["en"]))
    for tag, fmt in (("双语字幕", lambda z, e: f"{z}\n{e}"),
                     ("中文字幕", lambda z, e: z),
                     ("英文字幕", lambda z, e: e)):
        text = "".join(
            f"{k + 1}\n{ts(a)} --> {ts(b)}\n{fmt(z, e)}\n\n"
            for k, (a, b, z, e) in enumerate(rows)
        )
        out = HERE / f"{NAME}_{tag}.srt"
        out.write_text(text, encoding="utf-8-sig")
        print(out.name, len(rows), "条")


if __name__ == "__main__":
    main()
