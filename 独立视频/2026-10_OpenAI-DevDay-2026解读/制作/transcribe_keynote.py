# -*- coding: utf-8 -*-
"""OpenAI DevDay 2026 主题演讲转写（英文）：ffmpeg 抽 16 kHz 单声道 → faster-whisper large-v3-turbo（CPU int8，词级时间戳）。
照 白宫那条的 transcribe_live.py 改的：输入是单独的音频文件 素材/keynote_audio.weba，可以只转一段（--range 起 止，秒），
两段并行跑完再 merge_transcripts.py 合并。

用法：
  python transcribe_keynote.py --range 0 1607 --threads 6          → 素材/转写/part_00000.json / .txt
  python transcribe_keynote.py --range 1607 3215 --threads 6       → 素材/转写/part_01607.json / .txt
  python transcribe_keynote.py --range 1380 1420 --beam 5 --tag fine --threads 4   → 对一小段用 beam 5 精转（定同传锚点用）
时间戳是原片里的秒（已加上 --range 的起点）。素材/ 整个不进 git。
"""
import argparse
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
EP = HERE.parent
SRC = EP / "素材" / "keynote_audio.weba"
OUT = EP / "素材" / "转写"

# 专名提示：这场发布会里出现的产品名、人名，帮 ASR 拼对（拼写取自 ChatCut 的转写稿）
PROMPT = ("OpenAI DevDay 2026 keynote at Fort Mason, San Francisco. Sam Altman, Holly, Tejal, Romain, Jakob, Thibault. "
          "Dots, Dottie, ChatGPT Space, Astra, GPT 6.1 Sol, Ultra Fast, Decisions API, Luna, Agents API, Codex, Codex Security Cloud, "
          "OpenAI Private Intelligence, plugin extensions, OpenAI Marketplace, Sign in with ChatGPT, Figma, Adobe, Base10, "
          "Hugging Face, AWS Bedrock, Agent 365, Responses API, Blossom Music, GPT Live, GPT Image 2.5, Lavender.")


def stamp(sec):
    h, r = divmod(int(sec), 3600)
    m, s = divmod(r, 60)
    return f"{h:d}:{m:02d}:{s:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", nargs=2, type=float)
    ap.add_argument("--threads", type=int, default=6)
    ap.add_argument("--beam", type=int, default=1)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    a, b = args.range if args.range else (0.0, 3215.0)
    name = f"part_{int(a):05d}" + (f"_{args.tag}" if args.tag else "")
    OUT.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=args.threads)
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "a.wav"
        subprocess.run([ffmpeg, "-y", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", str(SRC), "-vn", "-ac", "1", "-ar", "16000",
                        "-c:a", "pcm_s16le", str(wav)], check=True)
        segs, info = model.transcribe(str(wav), language="en", beam_size=args.beam, initial_prompt=PROMPT,
                                      condition_on_previous_text=False, vad_filter=True,
                                      vad_parameters={"min_silence_duration_ms": 500}, word_timestamps=True)
        out, last_print = [], 0
        for s in segs:
            out.append({"start": round(s.start + a, 2), "end": round(s.end + a, 2), "text": s.text.strip(),
                        "words": [{"w": w.word, "s": round(w.start + a, 2), "e": round(w.end + a, 2)} for w in (s.words or [])]})
            if s.end - last_print >= 60:
                last_print = s.end
                print(f"{name}: {stamp(s.end + a)} / {stamp(b)}  ({time.time() - t0:.0f}s)", flush=True)
    (OUT / f"{name}.json").write_text(
        json.dumps({"name": name, "source": str(SRC), "range": [a, b], "model": f"faster-whisper large-v3-turbo int8 beam{args.beam}", "segments": out},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / f"{name}.txt").write_text("".join(f"[{stamp(x['start'])}] {x['text']}\n" for x in out), encoding="utf-8")
    print(f"{name}: 完成 {b - a:.0f}s 音频，{len(out)} 段，用时 {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
