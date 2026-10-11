# -*- coding: utf-8 -*-
"""接着 build_voice.py --qa 没跑完的地方继续逐句识别（后台任务有时间上限）。

  python qa_rest.py R15d            从句号 R15d 开始，到最后；结果追加到 qa_log.txt 末尾
识别方式和 build_voice.py 的 qa() 一样（large-v3-turbo、中文、不带提示词），每句取 seg_pick_v3/ 里换过的、否则 seg_raw/final/ 里导出的那一句。
"""
import difflib
import json
import re
import sys
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
lines = json.loads((HERE.parents[1] / "台本" / "录制稿.json").read_text(encoding="utf-8"))["lines"]
files = sorted((HERE / "tts" / "seg_raw" / "final").glob("*.wav"))
start = [l["id"] for l in lines].index(sys.argv[1])
n = lambda s: re.sub(r"[^\w]|_", "", s.lower().replace(" ", ""))
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=6)
with open(HERE / "qa_log.txt", "a", encoding="utf-8") as log:
    for i in range(start, len(lines)):
        l = lines[i]
        pick = HERE / "tts" / "seg_pick_v3" / f"{l['id']}.wav"
        p = pick if pick.exists() else files[i]
        segs, _ = m.transcribe(str(p), language="zh", beam_size=5, condition_on_previous_text=False, temperature=0)
        hyp = "".join(s.text for s in segs)
        sc = difflib.SequenceMatcher(None, n(l["say"]), n(hyp)).ratio()
        row = f"{l['id']} {sc:.2f} {hyp}{'  <<<' if sc < 0.85 else ''}"
        print(row, flush=True)
        log.write(row + "\n")
        log.flush()
