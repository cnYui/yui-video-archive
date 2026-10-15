# -*- coding: utf-8 -*-
"""现场视频转写（英文）：ffmpeg 抽 16 kHz 单声道 → faster-whisper large-v3-turbo（CPU int8，词级时间戳）
→ 视频同目录的 转写/<名>.json 和 .txt

用法：python transcribe_live.py [--threads 7] <视频1> <视频2> …
已经有 .json 的视频会跳过（断点续跑）。素材/ 整个不进 git，别人视频的转写稿只放这里。
"""
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from faster_whisper import WhisperModel

# 专名提示：这场活动里会出现的人名和公司名，帮 ASR 拼对
PROMPT = ("White House luncheon on Super Intelligence. President Trump, Speaker Mike Johnson, "
          "Dario Amodei of Anthropic, Greg Brockman of OpenAI, Mark Zuckerberg of Meta, Jensen Huang of Nvidia, "
          "Elon Musk, Sundar Pichai of Google, xAI, SI, the White House Accord on Super Intelligence, self-policing.")


def stamp(sec):
    m, s = divmod(sec, 60)
    return f"{int(m):02d}:{s:04.1f}"


def main():
    args = sys.argv[1:]
    threads, videos, fast, rng, tag = 7, [], False, None, ""
    while args:
        a = args.pop(0)
        if a == "--threads":
            threads = int(args.pop(0))
        elif a == "--range":         # 只转这一段（秒），时间戳加上偏移；输出名后缀 _<起>
            rng = (float(args.pop(0)), float(args.pop(0)))
            tag = f"_{int(rng[0]):05d}"
        elif a == "--fast":          # beam 1、不要词级时间戳：先粗定位，选好片段后再对短片段精转
            fast = True
        else:
            videos.append(Path(a))
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=threads)
    for v in videos:
        out_dir = v.parent / "转写"
        out_dir.mkdir(exist_ok=True)
        name = v.stem + tag
        off = rng[0] if rng else 0.0
        if (out_dir / f"{name}.json").exists():
            print(f"{name}: 已有转写，跳过", flush=True)
            continue
        t0 = time.time()
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "a.wav"
            cmd = [ffmpeg, "-y", "-v", "error"] + (["-ss", str(rng[0]), "-t", str(rng[1] - rng[0])] if rng else []) +                   ["-i", str(v), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)]
            subprocess.run(cmd, check=True)
            segs, info = model.transcribe(str(wav), language="en", beam_size=1 if fast else 5, initial_prompt=PROMPT,
                                          condition_on_previous_text=False, vad_filter=True,
                                          vad_parameters={"min_silence_duration_ms": 500},
                                          word_timestamps=not fast)
            out, last_print = [], 0
            for s in segs:
                out.append({"start": round(s.start + off, 2), "end": round(s.end + off, 2), "text": s.text.strip(),
                            "words": [{"w": w.word, "s": round(w.start + off, 2), "e": round(w.end + off, 2)} for w in (s.words or [])]})
                if s.end - last_print >= 60:
                    last_print = s.end
                    print(f"{name}: {stamp(s.end + off)} / {stamp(info.duration + off)}  ({time.time() - t0:.0f}s)", flush=True)
        (out_dir / f"{name}.json").write_text(
            json.dumps({"name": name, "source": str(v), "duration": round(info.duration, 2),
                        "model": "faster-whisper large-v3-turbo int8", "segments": out}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        (out_dir / f"{name}.txt").write_text(
            "".join(f"[{stamp(x['start'])}] {x['text']}\n" for x in out), encoding="utf-8")
        print(f"{name}: 完成 {info.duration:.0f}s 音频，{len(out)} 段，用时 {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
