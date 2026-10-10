# -*- coding: utf-8 -*-
"""参考视频转文字：ffmpeg 抽 16 kHz 单声道 → faster-whisper large-v3-turbo（CPU int8）→ 转写/<名字>.json 和 .txt

用法：python transcribe_refs.py [--threads 7] [--out <目录>] <视频1> <视频2> …
输出目录默认是本期的 参考分析/转写/；已经有 .json 的视频会跳过（断点续跑）。
别人视频的转写稿只放 参考分析/（.gitignore 已忽略），不进公开仓库。
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE.parent / "参考分析" / "转写"
PROMPT = "以下是普通话的句子，使用简体中文和标点符号。内容是关于学生思维、职场、大学生、结果导向和 AI 的讲解。"


def mmss(sec):
    sec = int(sec)
    return f"{sec // 60:02d}:{sec % 60:02d}"


def main():
    args = sys.argv[1:]
    threads, out_dir, videos = 7, DEFAULT_OUT, []
    while args:
        a = args.pop(0)
        if a == "--threads":
            threads = int(args.pop(0))
        elif a == "--out":
            out_dir = Path(args.pop(0))
        else:
            videos.append(Path(a))
    out_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=threads)
    for v in videos:
        m = re.match(r"\d+", v.stem)
        name = m.group(0) if m else v.stem  # B 站下载文件名以 cid 开头
        if (out_dir / f"{name}.json").exists():
            print(f"{name}: 已有转写，跳过", flush=True)
            continue
        t0 = time.time()
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "a.wav"
            subprocess.run([ffmpeg, "-y", "-v", "error", "-i", str(v), "-vn", "-ac", "1", "-ar", "16000",
                            "-c:a", "pcm_s16le", str(wav)], check=True)
            segs, info = model.transcribe(str(wav), language="zh", beam_size=5, initial_prompt=PROMPT,
                                          condition_on_previous_text=False, vad_filter=True,
                                          vad_parameters={"min_silence_duration_ms": 500})
            out, last_print = [], 0
            for s in segs:
                out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
                if s.end - last_print >= 60:
                    last_print = s.end
                    print(f"{name}: {mmss(s.end)} / {mmss(info.duration)}  ({time.time() - t0:.0f}s)", flush=True)
        (out_dir / f"{name}.json").write_text(
            json.dumps({"name": name, "source": str(v), "duration": round(info.duration, 2),
                        "model": "faster-whisper large-v3-turbo int8", "segments": out}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        (out_dir / f"{name}.txt").write_text(
            "".join(f"[{mmss(x['start'])}] {x['text']}\n" for x in out), encoding="utf-8")
        print(f"{name}: 完成 {info.duration:.0f}s 音频，{len(out)} 段，用时 {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
