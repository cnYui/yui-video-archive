# -*- coding: utf-8 -*-
"""识别配音：faster-whisper large-v3-turbo（CPU int8），逐词时间。输出 asr/<名>.json。

  python asr.py tts/raw/N_v1.mp3 tts/raw/N_v2.mp3

提示词放了本期的专有名词，帮识别拼对（Anthropic、Hugging Face 这类）。
"""
import json
import sys
import time
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
PROMPT = ("Claude Fable 5.5，Anthropic，Opus 5.5，Fable 5.2，JS，纯代码，一次生成，超人，漫威，DC，英雄，画风，岩画，像素游戏，终端，小生物。")


def main():
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=6)
    (HERE / "asr").mkdir(exist_ok=True)
    for a in sys.argv[1:]:
        p = HERE / a
        t0 = time.time()
        segs, info = model.transcribe(str(p), language="zh", beam_size=5, word_timestamps=True,
                                      initial_prompt=PROMPT, condition_on_previous_text=False, vad_filter=False)
        out = [{"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text,
                "words": [{"w": w.word, "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)} for w in (s.words or [])]}
               for s in segs]
        (HERE / "asr" / f"{p.stem}.json").write_text(json.dumps({"id": p.stem, "duration": info.duration, "segments": out}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{p.stem}: {info.duration:.1f}s, {len(out)} segs, {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
