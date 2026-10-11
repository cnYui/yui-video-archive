# -*- coding: utf-8 -*-
"""只对原声里指定的几段重新识别（不开 VAD、带上下文提示词），看含糊的地方到底说了什么。

  python transcribe_ranges.py 150.5-173.5 290-312 ...
"""
import sys
from pathlib import Path

import librosa
from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
AUDIO = HERE.parent / "素材" / "fHEIw5CcN5U_audio_en.webm"
PROMPT = ("A demo of dot, an always-on AI agent from OpenAI. The user phones her dot: flights on Southwest, Silver Lake Pool & Inn, Cara, Erewhon, "
          "LAX, Hollywood, Slack, Linear tickets, PR, retest, reliability, dashboard, feedback channel.")


def main():
    y, sr = librosa.load(str(AUDIO), sr=16000, mono=True)
    m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
    for r in sys.argv[1:]:
        a, b = (float(x) for x in r.split("-"))
        seg = y[int(a * sr): int(b * sr)]
        segs, _ = m.transcribe(seg, language="en", beam_size=8, word_timestamps=True, initial_prompt=PROMPT,
                               condition_on_previous_text=False, vad_filter=False, temperature=0.0)
        print(f"=== {a}-{b}")
        for s in segs:
            print(f"  [{a + s.start:7.2f}-{a + s.end:7.2f}] {s.text.strip()}")
            print("     " + " ".join(f"{w.word.strip()}@{a + w.start:.1f}" for w in s.words))


if __name__ == "__main__":
    main()
