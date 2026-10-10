# -*- coding: utf-8 -*-
"""逐句核对曼波配音（tts/seg_raw/final/*.wav，一句一个文件）：有声音的起止 / 时长 / 响度；中文识别和 say 比对；带英文专名的句子再用英文识别器听一遍，看专名读成了什么。

  python qa_tts.py            # 全部
  python qa_tts.py --en-only  # 只做英文专名那一步

读法：中文分数 < 0.85 的句子看识别结果；英文识别里 Anthropic / Claude / Artifacts 读歪了（比如 Typhus 这类）就在台本里写中文音译再重生成（记忆 fish-tts-english-names-check-first）。
机器识别分低不等于读错（数字写法、繁体输出会拉低分数），要用耳朵听。
"""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
SR = 48000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def voiced(a, thr=-45):
    h = int(SR * 0.01)
    n = len(a) // h
    db = 20 * np.log10(np.sqrt((a[: n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
    idx = np.where(db > thr)[0]
    return (0.0, len(a) / SR) if len(idx) == 0 else (idx[0] * 0.01, (idx[-1] + 1) * 0.01), db


def main():
    lines = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))["lines"]
    files = sorted((HERE / "tts" / "seg_raw" / "final").glob("*.wav"))
    assert len(files) == len(lines)
    rows = []
    tot_raw = tot_v = 0.0
    for l, f in zip(lines, files):
        a = load(f)
        (s, e), db = voiced(a)
        seg = a[int(s * SR): int(e * SR)]
        lufs_like = 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)
        rows.append((l["id"], len(a) / SR, s, e, e - s, lufs_like))
        tot_raw += len(a) / SR
        tot_v += e - s
        # 句内停顿（> 0.15 s 低于 −42 dB）
        quiet = db[int(s * 100): int(e * 100)] < -42
        runs, cur = [], 0
        for k, q in enumerate(quiet):
            if q:
                cur += 1
            else:
                if cur >= 15:
                    runs.append((round(s + (k - cur) * 0.01, 2), round(cur * 0.01, 2)))
                cur = 0
        print(f"{l['id']}  原始 {len(a) / SR:5.2f} s  有声 {s:4.2f}–{e:4.2f}（{e - s:5.2f} s）  rms {lufs_like:6.1f} dB  句内停顿 {runs}  {l['say']}")
    print(f"合计：原始 {tot_raw:.2f} s，有声 {tot_v:.2f} s")
    from faster_whisper import WhisperModel
    n = lambda s: re.sub(r"[^\w]|_", "", s.lower().replace(" ", ""))
    if "--en-only" not in sys.argv:
        m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
        for l, f in zip(lines, files):
            segs, _ = m.transcribe(str(f), language="zh", beam_size=5, condition_on_previous_text=False, temperature=0,
                                   initial_prompt="以下是普通话的句子，使用简体中文。")
            hyp = "".join(s.text for s in segs)
            sc = difflib.SequenceMatcher(None, n(l["say"]), n(hyp)).ratio()
            print(f"[zh {sc:.2f}] {l['id']} {hyp}{'  <<<' if sc < 0.85 else ''}", flush=True)
    me = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
    for l, f in zip(lines, files):
        if not re.search(r"[A-Za-z]", l["say"]):
            continue
        segs, _ = me.transcribe(str(f), language="en", beam_size=5, condition_on_previous_text=False, temperature=0,
                                initial_prompt="Anthropic, Claude Design, Claude Code, Artifacts, Claude.")
        print(f"[en] {l['id']} {' '.join(s.text.strip() for s in segs)}", flush=True)


if __name__ == "__main__":
    main()
