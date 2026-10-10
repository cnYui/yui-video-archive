# -*- coding: utf-8 -*-
r"""用户自己录的口播（DJI 等，好几段原片）批量 ASR：模型只加载一次，逐段转写（large-v3-turbo 带逐词时间 + medium 对照）。
比 own_voice.py asr 多的：一次处理好几段；每段另存 16 kHz 单声道 wav（build_talk.py 按能量找静音、对时间用）。

  python asr_clips.py <输出目录> <原片1> <原片2> … [--prompt "专名，专名，…"]

输出：<输出目录>\<原片名>\{voice16k.wav, asr.json（turbo，逐词）, asr_medium.json}，控制台打印每段的分句。
--prompt：这期会出现的专名 / 术语（Whisper 的 initial_prompt，写得全，专名就少听错；例：Claude Code，CLAUDE.md，Shift+Tab，上下文窗口）。
两遍对照专名 / 同音（“Clouder / Claude”“钓鱼之法 / 钓鱼执法”）；Whisper 会把重复短语合并（“执行这些任务，执行这些命令”只出一遍），
低分 / 对不上的地方回到逐词时间和原片对。输出放素材层：<合集>\素材\<YYYY-MM_主题>\出镜_ASR\。
用在：多段口播 + 官方素材 + 说明卡（技能 assets/oncam-multiclip/README.md）；只有一段口播用 own_voice.py asr 就够。
2026-10-06《Claude官方教程》第 1 期出镜版：5 段 645.8 s，CPU int8 约十几分钟，后台跑（cmd /c start /B /BELOWNORMAL）别和渲染同时占满。
"""
import json
import subprocess
import sys
from pathlib import Path

BASE_PROMPT = "Claude，Anthropic，GPT，ChatGPT，AI，Agent，API，bug，Git，"


def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    prompt = ""
    if "--prompt" in args:
        i = args.index("--prompt")
        prompt = args[i + 1]
        del args[i:i + 2]
    out = Path(args[0])
    clips = [Path(p) for p in args[1:]]
    missing = [str(c) for c in clips if not c.is_file()]
    if missing:
        print("找不到原片：", *missing, sep="\n  ")
        return 2
    from faster_whisper import WhisperModel
    models = {n: WhisperModel(n, device="cpu", compute_type="int8") for n in ("large-v3-turbo", "medium")}
    for c in clips:
        d = out / c.stem
        d.mkdir(parents=True, exist_ok=True)
        wav = d / "voice16k.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(c), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
        for name, model in models.items():
            segs, info = model.transcribe(str(wav), language="zh", word_timestamps=(name != "medium"), vad_filter=True,
                                          vad_parameters={"min_silence_duration_ms": 300}, initial_prompt=BASE_PROMPT + prompt)
            rows = [{"s": round(s.start, 2), "e": round(s.end, 2), "text": s.text.strip(),
                     "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 2)} for w in (s.words or [])]} for s in segs]
            (d / ("asr.json" if name != "medium" else "asr_medium.json")).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"── {c.name}  {name}（时长 {info.duration:.1f} s）", flush=True)
            for r in rows:
                print(f'{r["s"]:7.2f} {r["e"]:7.2f}  {r["text"]}', flush=True)
        print(f"DONE {c.name}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
