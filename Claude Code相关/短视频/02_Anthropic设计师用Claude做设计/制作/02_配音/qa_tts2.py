# -*- coding: utf-8 -*-
"""qa_tts.py 里分数低的句子的第二意见：带 initial_prompt（写上人名 / 产品名），用 large-v3-turbo 和 medium 各听一遍，两个模型都对不上的才是真问题。

  python qa_tts2.py            # 只复核第一遍 < 0.85 的句子（读 qa_tts_*.txt 最新一份太麻烦，这里直接全部句子都跑，只打印 < 0.9 的）

记忆 fish-tts-english-names-check-first：曼波声线把英文专名读歪时，识别器会听成另一个词；但识别器本身也会把 Nate / Claude 听成“内特 / 骷髅 / 库洛”，所以要带提示词再听一遍，别当成配音读错。
"""
import difflib
import json
import re
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
PROMPT = "这是一段中文解说。人名 Nate；产品和公司：Claude、Claude Code、Claude Design、Claude Slides、Anthropic、Artifacts、App。使用简体中文。"
n = lambda s: re.sub(r"[^\w]|_", "", s.lower().replace(" ", ""))


def main():
    lines = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))["lines"]
    files = sorted((HERE / "tts" / "seg_raw" / "final").glob("*.wav"))
    models = {"large-v3-turbo": WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8),
              "medium": WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)}
    low = []
    for l, f in zip(lines, files):
        row, best = [], 0.0
        for name, m in models.items():
            segs, _ = m.transcribe(str(f), language="zh", beam_size=5, condition_on_previous_text=False, temperature=0, initial_prompt=PROMPT)
            hyp = "".join(s.text for s in segs)
            sc = difflib.SequenceMatcher(None, n(l["say"]), n(hyp)).ratio()
            best = max(best, sc)
            row.append(f"[{name[:5]} {sc:.2f}] {hyp}")
        flag = "  <<<" if best < 0.85 else ""
        if best < 0.9:
            print(l["id"], "  |  ".join(row), flag, flush=True)
        if best < 0.85:
            low.append(l["id"])
    print("两个模型都低于 0.85 的：", " ".join(low) or "无")


if __name__ == "__main__":
    main()
