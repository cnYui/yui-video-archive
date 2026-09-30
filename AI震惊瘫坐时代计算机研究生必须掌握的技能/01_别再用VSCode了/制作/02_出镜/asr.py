# -*- coding: utf-8 -*-
"""出镜口播识别：faster-whisper large-v3-turbo（CPU int8），逐词时间。输出 asr/<编号>.json。

提示词里放了本期的专有名词，也故意带了“嗯、那个、就是说”——这样模型会把口癖写出来，后面才好剪掉。
专有名词按本期术语表写（写法和字幕一致）；常见误识别（Opus→OPS/OPPO、Claude→Cloud、OpenClaw→OpenCloud、3A→三 D3A）见技能 references/subtitles.md，识别完搜一遍。
"""
import json
import sys
import time
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
PROMPT = ("嗯，那个，就是说，呃，我们今天讲 VS Code、Copilot、Cursor、Trae、Claude Code、Codex、WorkBuddy。"
          "IDE，CLI，SSH，Agent，GitHub，ChatGPT，Stack Overflow，CSDN，Windsurf，SOLO，PRD，Kiro，"
          "Anthropic，OpenAI，Google，Gemini CLI，MCP，Playwright，OSWorld，GPT-5.4，Meta，CloudBase，"
          "METR，Karpathy，vibe coding，OpenClaw，Cowork，Telegram，WhatsApp，WorkBuddy，TRAE Work，豆包 Work，"
          "Routines，computer use，Claude in Chrome，GPT-6 Astra，Blender，Unity，悠一。")


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
