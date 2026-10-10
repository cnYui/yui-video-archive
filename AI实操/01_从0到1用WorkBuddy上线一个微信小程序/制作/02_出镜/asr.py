# -*- coding: utf-8 -*-
"""口播识别：faster-whisper large-v3-turbo（CPU int8），逐词时间。输出 asr/<编号>.json。

  python asr.py [编号…]          不写编号 = audio16/ 里全部
  python asr.py --threads 7 R1013 0161 …

提示词里放了本期的专有名词，也故意带了“嗯、那个、就是说”——这样模型会把口癖写出来，后面才好剪掉。
出镜（DJI）和录屏（OpenScreen 录的电脑麦克风）是同一段话录了两遍，两边都识别：录屏有些地方没有出镜，出镜有些地方没有录屏。
"""
import json
import sys
import time
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
PROMPT = ("嗯，那个，就是说，呃，大家好，我是悠一。今天用 WorkBuddy 从 0 到 1 做一个微信小程序。"
          "微信开发者工具，小程序开发者助手，CLI，HTTP，服务端口，安全设置，AppID，实名认证，"
          "云开发，云环境，云函数，数据库，CloudBase CLI，tcb，体验版，上传，预览，发布，审核，"
          "AI，Agent，Claude，Codex，Skill，MCP，loop，联调，调试，本地服务，localhost，Node.js，npm，"
          "WXML，WXSS，JSON，GitHub，Token。")


def main():
    args = sys.argv[1:]
    threads = 8
    if args[:1] == ["--threads"]:
        threads, args = int(args[1]), args[2:]
    ids = args or sorted(p.stem for p in (HERE / "audio16").glob("*.wav"))
    (HERE / "asr").mkdir(exist_ok=True)
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=threads)
    for i in ids:
        t0 = time.time()
        segs, info = model.transcribe(str(HERE / "audio16" / f"{i}.wav"), language="zh", beam_size=5, word_timestamps=True,
                                      initial_prompt=PROMPT, condition_on_previous_text=False, vad_filter=False)
        out = []
        for s in segs:
            out.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text,
                        "words": [{"w": w.word, "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)} for w in (s.words or [])]})
        (HERE / "asr" / f"{i}.json").write_text(json.dumps({"id": i, "duration": info.duration, "segments": out}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{i}: {info.duration:.1f}s audio, {len(out)} segs, {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
