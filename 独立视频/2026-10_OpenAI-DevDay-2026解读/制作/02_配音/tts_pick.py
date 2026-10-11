# -*- coding: utf-8 -*-
"""逐句挑版本：每句在 v1、v2 里各切出来单独识别（不带提示词），和原文比，分高的用；平手用 v1。输出 edit/choice.json 和 edit/pick_report.txt。

  python tts_pick.py [--batch A]

切句用 tts_build 里同一套（逐词对齐 + 静音中点）。分数 < 0.8 的句子会在报告里列出来，要重点听。
"""
import difflib
import json
import re
import sys
import wave
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tts_build as B  # noqa: E402

HERE = B.HERE
n = lambda s: re.sub(r"[^\w]|_", "", s.lower())


def main():
    batch = sys.argv[sys.argv.index("--batch") + 1] if "--batch" in sys.argv else "A"
    lines = json.loads((HERE / "tts" / "lines.json").read_text(encoding="utf-8"))
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=6)
    scores = {v: {} for v in ("v1", "v2")}
    hyps = {v: {} for v in ("v1", "v2")}
    for v in ("v1", "v2"):
        a = B.load_audio(HERE / "tts" / "raw" / f"{batch}_{v}.mp3")
        asr = json.loads((HERE / "asr" / f"{batch}_{v}.json").read_text(encoding="utf-8"))
        db = B.env_db(a)
        spans = B.align(lines, asr)
        cs = B.cuts(db, spans, len(a) / B.SR)
        mono = (a.mean(1) * 32767).astype(np.int16)
        for i, l in enumerate(lines):
            s, e = cs[i]
            seg = mono[int(max(0, s - 0.1) * B.SR): int((e + 0.1) * B.SR)]
            with wave.open(str(HERE / "tts" / "_p.wav"), "wb") as o:
                o.setnchannels(1)
                o.setsampwidth(2)
                o.setframerate(B.SR)
                o.writeframes(seg.tobytes())
            segs, _ = model.transcribe(str(HERE / "tts" / "_p.wav"), language="zh", beam_size=5, condition_on_previous_text=False, temperature=0)
            hyp = "".join(x.text for x in segs)
            ref = n(l["say"]).replace("ai", "ai")
            sc = difflib.SequenceMatcher(None, ref, n(hyp)).ratio()
            scores[v][l["id"]] = round(sc, 3)
            hyps[v][l["id"]] = hyp
        print(v, "done", flush=True)
    choice, rep = {}, []
    for l in lines:
        i = l["id"]
        s1, s2 = scores["v1"][i], scores["v2"][i]
        if s2 > s1 + 0.03:
            choice[i] = "v2"
        rep.append(f"{i} v1 {s1:.2f} v2 {s2:.2f} → {choice.get(i, 'v1')}{'  <<<' if max(s1, s2) < 0.8 else ''}\n    v1: {hyps['v1'][i]}\n    v2: {hyps['v2'][i]}")
    (HERE / "edit").mkdir(exist_ok=True)
    (HERE / "edit" / "choice.json").write_text(json.dumps(choice, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "edit" / "pick_report.txt").write_text("\n".join(rep), encoding="utf-8")
    low = [i for i in scores["v1"] if max(scores["v1"][i], scores["v2"][i]) < 0.8]
    print(f"用 v2 的 {len(choice)} 句；两版都 < 0.8 的 {len(low)} 句：{low}")


if __name__ == "__main__":
    main()
