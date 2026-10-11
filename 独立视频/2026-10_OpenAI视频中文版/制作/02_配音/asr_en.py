# -*- coding: utf-8 -*-
"""识别原片的英文原声：faster-whisper large-v3-turbo（CPU int8），逐词时间 → ../../台本/en_asr.json，另出一份好读的 en_transcript.txt。

  python asr_en.py ../../素材/fHEIw5CcN5U_audio_en.webm

开了 VAD（原片可能有配乐 / 掌声，没有人声的地方别让模型瞎编）；提示词放产品名，帮识别拼对。
"""
import json
import sys
import time
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
PROMPT = "OpenAI DevDay 2026. dots, always-on agents, ChatGPT, Codex, Slack, OpenAI."


def main():
    src = (HERE / sys.argv[1]).resolve()
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
    t0 = time.time()
    segs, info = model.transcribe(str(src), language="en", beam_size=5, word_timestamps=True, initial_prompt=PROMPT,
                                  condition_on_previous_text=False, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=300))
    out = []
    for s in segs:
        out.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(),
                    "words": [{"w": w.word, "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)} for w in (s.words or [])]})
        print(f"{s.start:7.2f}-{s.end:7.2f} {s.text.strip()}", flush=True)
    (EP / "台本").mkdir(exist_ok=True)
    (EP / "台本" / "en_asr.json").write_text(json.dumps({"src": src.name, "duration": info.duration, "segments": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    (EP / "台本" / "en_transcript.txt").write_text("\n".join(f"[{x['start']:7.2f}-{x['end']:7.2f}] {x['text']}" for x in out) + "\n", encoding="utf-8")
    print(f"done: {info.duration:.1f}s audio, {len(out)} segs, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
