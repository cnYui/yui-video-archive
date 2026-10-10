# -*- coding: utf-8 -*-
"""识别：faster-whisper large-v3-turbo（CPU int8），逐词时间。输出 asr/<编号>.json。

  python asr.py 0163                出镜（audio16/0163.wav）
  python asr.py tts/raw/R_v1.mp3    克隆配音的一个版本（输出 asr/R_v1.json）

提示词里放了本期的专有名词，也故意带了“嗯、那个、就是说”——这样模型会把口癖写出来，后面才好剪掉。
"""
import json
import sys
import time
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
PROMPT = ("嗯，那个，就是说，呃，大家好，我是悠一。很多后台的朋友在问我怎么订阅 Codex 和 Claude Code。"
          "中转，代充，安全凭证，苹果礼品卡，Apple Gift Card，Google Play，美区 Apple ID，App Store，兑换，余额，"
          "Claude App，ChatGPT，UP 主，AI引导世界，Visa 信用卡，Pockyt，支付宝，B站。")


def main():
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
    (HERE / "asr").mkdir(exist_ok=True)
    for a in sys.argv[1:]:
        p = Path(a)
        src, name = (HERE / "audio16" / f"{a}.wav", a) if not p.suffix else (HERE / p, p.stem)
        t0 = time.time()
        segs, info = model.transcribe(str(src), language="zh", beam_size=5, word_timestamps=True,
                                      initial_prompt=PROMPT, condition_on_previous_text=False, vad_filter=False)
        out = [{"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text,
                "words": [{"w": w.word, "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)} for w in (s.words or [])]}
               for s in segs]
        (HERE / "asr" / f"{name}.json").write_text(json.dumps({"id": name, "duration": info.duration, "segments": out}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{name}: {info.duration:.1f}s, {len(out)} segs, {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
