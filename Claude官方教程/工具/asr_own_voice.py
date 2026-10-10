# -*- coding: utf-8 -*-
r"""悠一自己录的口播（DJI 多段原片）批量 ASR：模型只加载一次，逐段转写（large-v3-turbo 带逐词时间 + medium 对照），写 JSON。
比技能的 own_voice.py asr 多的：一次处理好几段；每段另存 16 kHz 单声道 wav（后面剪辑 / 对时间用）。

  python asr_own_voice.py <输出目录> <原片1> <原片2> …
输出：<输出目录>\<原片名>\{voice16k.wav, asr.json（turbo，逐词）, asr_medium.json}，并在控制台打印每段的分句。
"""
import json
import subprocess
import sys
from pathlib import Path

PROMPT = ("Claude Code，Claude，Anthropic，CLAUDE.md，Shift+Tab，Esc，agentic loop，AI Agent，Claude Academy，Claude Code 101，"
          "代理循环，智能体，终端，上下文窗口，权限，Console，VS Code，JetBrains，Opus，Sonnet，Learn，Pro，Max，Team，API，bug，Git。")


def main():
    out = Path(sys.argv[1])
    clips = [Path(p) for p in sys.argv[2:]]
    from faster_whisper import WhisperModel
    models = {n: WhisperModel(n, device="cpu", compute_type="int8") for n in ("large-v3-turbo", "medium")}
    for c in clips:
        d = out / c.stem
        d.mkdir(parents=True, exist_ok=True)
        wav = d / "voice16k.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(c), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
        for name, model in models.items():
            segs, info = model.transcribe(str(wav), language="zh", word_timestamps=(name != "medium"), vad_filter=True,
                                          vad_parameters={"min_silence_duration_ms": 300}, initial_prompt=PROMPT)
            rows = [{"s": round(s.start, 2), "e": round(s.end, 2), "text": s.text.strip(),
                     "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 2)} for w in (s.words or [])]} for s in segs]
            (d / ("asr.json" if name != "medium" else "asr_medium.json")).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"── {c.name}  {name}（时长 {info.duration:.1f} s）", flush=True)
            for r in rows:
                print(f'{r["s"]:7.2f} {r["e"]:7.2f}  {r["text"]}', flush=True)
        print(f"DONE {c.name}", flush=True)


if __name__ == "__main__":
    main()
