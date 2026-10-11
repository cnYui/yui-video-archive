# -*- coding: utf-8 -*-
"""剪辑表 → 页面用的 timeline.js：片段（每帧属于哪段、版式、章节、倍速）、字幕条、段落起止、出镜放大中心、每帧人声电平（画外音卡的电平条用）。

  python build_page.py
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CUT = HERE.parent / "02_出镜"
sys.path.insert(0, str(CUT))
from takes import CAM_FACE  # noqa: E402

FPS = 30


def main():
    d = json.loads((CUT / "edit" / "edit.json").read_text(encoding="utf-8"))
    clips = [[c["out0"], c["n"], c["layout"], c["chapter"], c["kind"], c["speed"], c["seg"], c["take"]] for c in d["clips"]]
    segs = []
    for i, s in enumerate(d["segs"]):
        cs = [c for c in d["clips"] if c["seg"] == i]
        segs.append({"take": s["take"], "layout": s["layout"], "chapter": s["chapter"],
                     "s": round(cs[0]["out0"] / FPS, 3), "e": round((cs[-1]["out0"] + cs[-1]["n"]) / FPS, 3)})
    cues = [{"id": q["id"], "zh": q["zh"], "s": q["out_s"], "e": q["out_e"], "seg": q["seg"]} for q in d["cues"]]
    # 每帧人声电平（0–1）
    with wave.open(str(CUT / "edit" / "narration.wav")) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32).mean(1) / 32768
    hop = sr // FPS
    n = d["frames"]
    a = np.pad(a, (0, max(0, n * hop - len(a))))[: n * hop]
    db = 20 * np.log10(np.sqrt((a.reshape(n, hop) ** 2).mean(1)) + 1e-9)
    lev = np.clip((db + 50) / 35, 0, 1)
    tl = {"fps": FPS, "frames": n, "total": d["total"], "chapters": d["chapters"], "clips": clips, "segs": segs,
          "cues": cues, "camFace": CAM_FACE, "env": [round(float(x), 2) for x in lev]}
    (HERE / "timeline.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"timeline.js：{n} 帧，{len(clips)} 个片段，{len(segs)} 段，{len(cues)} 条字幕")


if __name__ == "__main__":
    main()
