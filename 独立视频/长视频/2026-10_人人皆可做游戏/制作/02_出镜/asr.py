# -*- coding: utf-8 -*-
"""口播识别：faster-whisper large-v3-turbo（CPU int8），逐词时间。输出 asr/<编号>.json。

  python asr.py [编号…]          不写编号 = audio16/ 里全部
  python asr.py --threads 12 0190 0191

提示词里放了本期的专有名词，也故意带了“嗯、那个、就是说”——这样模型会把口癖写出来，后面才好剪掉。
"""
import json
import sys
import time
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
PROMPT = ("嗯，那个，就是说，呃，欢迎来到人人皆可做游戏的时代。这个游戏是从一条视频里长出来的。"
          "9 月 25 号，我让 Claude 做了一条像素动画，《300 秒看完〈银魂〉》，开了 Ultra Code 模式，用的 Opus 5.5 模型。"
          "银魂，银时，高杉，神乐，新八，定春，桂小太郎，松阳，虚，十五章，四十二个角色，剧情，台词，代码，JavaScript，"
          "Canvas，浏览器，384 乘 216，会话，临时文件夹，图集，13124 帧，8 位配乐，音效，分镜，镜头表，"
          "自动通关，无职转生，巨人，火影，强化学习，官方课，提示词，AI，Claude Code。")


def main():
    args = sys.argv[1:]
    threads = 12
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
