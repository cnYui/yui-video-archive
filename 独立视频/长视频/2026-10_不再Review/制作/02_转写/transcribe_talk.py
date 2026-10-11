# -*- coding: utf-8 -*-
"""Lauren Tan（poteto）在 X 上发的 38 分钟演讲转写（英文，推文：here's how i shipped 2,500 PRs last month to production）：ffmpeg 抽 16 kHz 单声道 → faster-whisper large-v3-turbo（CPU int8，词级时间戳）。
照 OpenAI-DevDay 那条的 transcribe_keynote.py 改的：可以只转一段（--range 起 止，秒），几段并行跑完再 merge_transcripts.py 合并。

用法：
  python transcribe_live.py --range 0 1312 --threads 4                     → 素材/转写/part_00000.json / .txt
  python transcribe_live.py --range 2380 2440 --beam 5 --tag fine --threads 4   → 对一小段用 beam 5 精转（定同传锚点用）
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

SRC = Path("D:/大疆/独立视频/素材/2026-10_不再Review/X推文/poteto_演讲视频_2102050467505430555/poteto_2102050467505430555.mp4")
OUT = Path("D:/大疆/独立视频/素材/2026-10_不再Review/转写_演讲")
DUR = 2282.0

# 专名提示：这场访谈里出现的产品名、人名，帮 ASR 拼对
PROMPT = ("Lauren Tan (poteto) talk for Cursor Compile: I shipped 2000 PRs last month. Matt Pocock interviews Lauren Tan, poteto, creator of pstack, at SpaceX AI, formerly Cursor and the React team at Meta. "
          "pstack, Cursor, SpaceXAI, Grok Bot, Opus 5.5, Total TypeScript, Michelin kitchen, software factory, dark factory, "
          "verification skill, Dune, Next.js, Electron, TypeScript, lint rules, Playwright, Chrome DevTools, hill climbing, "
          "Andrej Karpathy auto research, Bend, Lean, TLA+, Netflix, Slack, Linear, Noodle, Wayfinder, grill me, recall, full autopilot.")


def stamp(sec):
    h, r = divmod(int(sec), 3600)
    m, s = divmod(r, 60)
    return f"{h:d}:{m:02d}:{s:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", nargs=2, type=float)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--beam", type=int, default=1)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    a, b = args.range if args.range else (0.0, DUR)
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
