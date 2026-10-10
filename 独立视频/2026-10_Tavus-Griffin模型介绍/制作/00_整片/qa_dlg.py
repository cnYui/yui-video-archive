# -*- coding: utf-8 -*-
r"""混音复核（对白版）：把 audio/mix.wav 里每条【对白字幕】对应的时间段单独切出来识别（英文原话），和字幕的英文行比。
画外音（中文）仍用 qa_mix.py。目的：确认原片台词的声音真的落在对应字幕的时刻（原片时间码 → 成片时间的换算没错），没有放错位置 / 叠音。

  python qa_dlg.py            逐条核对
"""
import difflib
import json
import re
import sys
from pathlib import Path

from faster_whisper import WhisperModel

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_mix import HERE, asr, load16  # noqa: E402

n = lambda s: re.sub(r"[^\w]|_", "", s.lower().replace(" ", ""))


def asr_en(m, a, t0, t1):
    import wave
    seg = a[int(max(0, t0) * 16000): int(t1 * 16000)]
    p = HERE / "audio" / "_qa_en.wav"
    with wave.open(str(p), "wb") as o:
        o.setnchannels(1)
        o.setsampwidth(2)
        o.setframerate(16000)
        o.writeframes(seg.tobytes())
    segs, _ = m.transcribe(str(p), language="en", beam_size=5, condition_on_previous_text=False, temperature=0)
    return " ".join(s.text.strip() for s in segs)


def main():
    m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    a = load16(HERE / "audio" / "mix.wav")
    low = []
    dl = [x for x in T["subs"] if x["kind"] == "dlg"]
    for x in dl:
        hyp = asr_en(m, a, x["s"] - 0.25, x["e"] + 0.25)
        sc = difflib.SequenceMatcher(None, n(x["en"]), n(hyp)).ratio()
        if sc < 0.7:
            low.append(x["id"])
        print(f"{x['id']:5s} {x['s']:7.2f}–{x['e']:7.2f} {sc:.2f} | 字幕：{x['en'][:60]} | 听到：{hyp[:70]}{'  <<<' if sc < 0.7 else ''}", flush=True)
    print(f"共 {len(dl)} 条对白，低于 0.7 的 {len(low)} 条：{' '.join(low) or '无'}")


if __name__ == "__main__":
    main()
