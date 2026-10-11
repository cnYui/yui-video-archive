# -*- coding: utf-8 -*-
"""配音（Fish 网页版·故事工作室，声音「赛马娘（曼波欧耶版）」，模型 S2 Pro）→ 逐句 WAV 拼成一条口播。

  python build_voice.py [--qa]

输入：tts/seg_raw/final/NNNNNN.wav（工作室「导出项目 → 文件结构：按段落拆分」的 zip 解出来、按顺序改名的，一句一个文件，顺序 = ../../台本/录制稿.json 的 lines；单声道 44.1 kHz；tts/seg_raw/segments/ 是第一版导出，对应改台本之前的旧稿，别用）。
      要换某一句（工作室里重新生成了那个区块）：把新导出的那一句 wav 放进 tts/seg_pick_v3/<句号>.wav，会盖过 final 里同序号的那一个（tts/seg_pick/ 里的 N03、N06 是改稿中途的临时导出，已作废，不读）。
输出：edit/tts_narration.wav（48 kHz 立体声）、edit/tts_edit.json（每句：s/e = 有声音的起止，n0/n1 = 这句在口播里的切点；build_timeline.py / mix_audio.py 读）、tts/lines.json。
每句：转 48 kHz 立体声 → 找真正有声音的起止（> −45 dB）→ 前留 PAD_A、后留 PAD_B 的静音当切点 → 音量拉到各句的中位数（最多 ±MAXADJ dB，工作室是逐区块生成的，音量会有起伏）→ 首尾 5 ms 淡入淡出 → 首尾相接。
--qa：把每句单独识别（large-v3-turbo，不带提示词）和台本比，低于 0.85 的列出来（这个声线的 sh/x、q/x 常被听错，机器分低的句子仍要用耳朵听）。
"""
import difflib
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
SR = 48000
PAD_A, PAD_B = 0.12, 0.25
MAXADJ = 4.0


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def env_db(a, hop=0.01):
    h = int(SR * hop)
    m = a.mean(1)
    n = len(m) // h
    return 20 * np.log10(np.sqrt((m[: n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)


def voiced(a):
    """有声音的起止（秒）：包络 > −45 dB 的第一格和最后一格。"""
    db = env_db(a)
    idx = np.where(db > -45)[0]
    return (0.0, len(a) / SR) if len(idx) == 0 else (idx[0] * 0.01, (idx[-1] + 1) * 0.01)


def main():
    sc = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))
    lines = [{"id": l["id"], "zh": l["zh"], "say": l["say"]} for l in sc["lines"]]
    (HERE / "tts").mkdir(exist_ok=True)
    (HERE / "tts" / "lines.json").write_text(json.dumps(lines, ensure_ascii=False, indent=1), encoding="utf-8")
    raw_dir = HERE / "tts" / "seg_raw" / "final"
    files = sorted(raw_dir.glob("*.wav"))
    assert len(files) == len(lines), f"导出了 {len(files)} 个文件，台本有 {len(lines)} 句"
    clips, srcs = [], []
    for i, l in enumerate(lines):
        pick = HERE / "tts" / "seg_pick_v3" / f"{l['id']}.wav"
        p = pick if pick.exists() else files[i]
        a = load(p)
        vs, ve = voiced(a)
        a = a[int(max(0, vs - PAD_A) * SR): int(min(len(a) / SR, ve + PAD_B) * SR)].copy()
        clips.append((a, vs - max(0, vs - PAD_A), ve - vs))
        srcs.append("seg_pick" if pick.exists() else "seg_raw")
    rms = []
    for a, v0, dur in clips:
        seg = a[int(v0 * SR): int((v0 + dur) * SR)]
        rms.append(20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9))
    med = float(np.median(rms))
    out, segs, t = [], [], 0.0
    fade = int(0.005 * SR)
    r = np.linspace(0, 1, fade)[:, None]
    for l, (a, v0, dur), lv, src in zip(lines, clips, rms, srcs):
        adj = float(np.clip(med - lv, -MAXADJ, MAXADJ))
        a = a * (10 ** (adj / 20))
        a[:fade] *= r
        a[-fade:] *= r[::-1]
        segs.append({"id": l["id"], "zh": l["zh"], "take": src, "src": [0.0, round(len(a) / SR, 3)], "n0": round(t, 3), "n1": round(t + len(a) / SR, 3),
                     "s": round(t + v0, 3), "e": round(t + v0 + dur, 3), "gain_db": round(adj, 2)})
        out.append(a)
        t += len(a) / SR
    y = np.concatenate(out)
    (HERE / "edit").mkdir(exist_ok=True)
    with wave.open(str(HERE / "edit" / "tts_narration.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    (HERE / "edit" / "tts_edit.json").write_text(json.dumps({"total": round(len(y) / SR, 3), "lines": segs}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"tts_narration.wav {len(y) / SR:.2f} s，{len(segs)} 句；各句有声音部分的响度中位数 {med:.1f} dB（最多拉 ±{MAXADJ} dB）；换过的句子：" + (", ".join(s["id"] for s in segs if s["take"] == "seg_pick") or "无"))
    for s in segs:
        print(f"  {s['id']}  {s['e'] - s['s']:5.2f} s  调 {s['gain_db']:+5.2f} dB  {s['zh']}")
    if "--qa" in sys.argv:
        qa(lines, clips, out)


def qa(lines, clips, out):
    from faster_whisper import WhisperModel
    n = lambda s: re.sub(r"[^\w]|_", "", s.lower().replace(" ", ""))
    m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=6)
    low = []
    for l, a in zip(lines, out):
        p = HERE / "tts" / "_q.wav"
        mono = (a.mean(1) * 32767).astype(np.int16)
        with wave.open(str(p), "wb") as o:
            o.setnchannels(1)
            o.setsampwidth(2)
            o.setframerate(SR)
            o.writeframes(mono.tobytes())
        segs, _ = m.transcribe(str(p), language="zh", beam_size=5, condition_on_previous_text=False, temperature=0)
        hyp = "".join(s.text for s in segs)
        sc = difflib.SequenceMatcher(None, n(l["say"]), n(hyp)).ratio()
        if sc < 0.85:
            low.append(l["id"])
        print(f"{l['id']} {sc:.2f} {hyp}{'  <<<' if sc < 0.85 else ''}", flush=True)
    print("低于 0.85 的：", " ".join(low) or "无")


if __name__ == "__main__":
    main()
