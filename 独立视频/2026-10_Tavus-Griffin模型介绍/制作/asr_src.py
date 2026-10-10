# -*- coding: utf-8 -*-
r"""转写素材视频里说的话（只为了读懂内容 / 挑片段，不是配音）：faster-whisper large-v3-turbo，CPU，词级时间。

  python asr_src.py <视频.mp4> [<视频2.mp4> …] --out <目录>

每个视频出 <名>.words.json（词级）和 <名>.txt（带时间的句子）。转写稿是别人视频的全文，只放 素材/ 或 scratchpad，不进仓库。
"""
import argparse
import json
import os
from pathlib import Path

from faster_whisper import WhisperModel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--lang", default="en")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=int(os.environ.get("ASR_THREADS", "6")))
    for v in a.videos:
        stem = Path(v).stem
        segs, info = model.transcribe(v, language=a.lang, word_timestamps=True, vad_filter=True, beam_size=5)
        words, lines = [], []
        for s in segs:
            lines.append(f"[{s.start:7.2f} – {s.end:7.2f}] {s.text.strip()}")
            for w in s.words or []:
                words.append({"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 3)})
        (out / f"{stem}.words.json").write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
        (out / f"{stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(stem, "done", len(lines), "segments", flush=True)


if __name__ == "__main__":
    main()
