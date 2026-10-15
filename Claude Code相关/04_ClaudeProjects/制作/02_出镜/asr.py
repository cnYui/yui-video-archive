# -*- coding: utf-8 -*-
"""出镜口播识别：faster-whisper large-v3-turbo（CPU int8），逐词时间。输出 asr/<编号>.json。
（拷自 Way to AGI 第 02 期的 asr.py，提示词换成本期的专有名词）

提示词里故意带了“嗯、那个、就是说”——这样模型会把口癖写出来，后面才好剪掉。
"""
import json
import sys
import time
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
PROMPT = ("嗯，那个，就是说，呃，我们今天讲 Claude Code Projects。Anthropic，Claude Code，Projects，Cowork，Opus，Sonnet，"
          "LCP，CLS，p75，PR，GitHub，Library，Overview，线程，协调员，项目说明，项目记忆，例程，routine，research preview，"
          "Remote Control，Sentry，agent view，agent teams，dynamic workflows，subagents，Claude Tag，CLAUDE.md，Core Web Vitals。")


def main():
    ids = sys.argv[1:] or sorted(p.stem for p in (HERE / "audio16").glob("*.wav"))
    (HERE / "asr").mkdir(exist_ok=True)
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
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
