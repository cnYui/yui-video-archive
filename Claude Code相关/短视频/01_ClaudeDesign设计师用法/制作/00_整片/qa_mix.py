# -*- coding: utf-8 -*-
"""出片前自查（成片的音轨 + 画面参数）。

  python qa_mix.py [成片路径]        默认 成片_竖屏_中英字幕.mp4

1. ffprobe：时长（20–30 s）、分辨率（1080×2340）、帧率（30）、音频（AAC 48 kHz 立体声）；
2. 响度：整条 ebur128（目标 −16 LUFS）、真峰值；
3. 逐句：按 timeline.json 的开口时刻把成片的音轨切成一句一句，用 large-v3-turbo 识别，和台本的 say 比（< 0.85 的列出来；
   曼波声线的 sh/x、zh/j 常被听错，机器分低不等于读错，要用耳朵听）；同时量每句实际开口时刻和时间线差多少（> 60 ms 报警）；
4. 字幕：每条字幕的显示窗口是否盖住对应那句话的开口到结束。
"""
import difflib
import json
import re
import subprocess
import sys
import wave

import numpy as np

import config as C

BUILD = C.HERE / "build"
SR = 48000


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate,sample_rate,channels,duration:format=duration,size",
                        "-of", "json", str(path)], capture_output=True, text=True)
    return json.loads(r.stdout)


def load_audio(path, sr=SR):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    i = re.findall(r"\n\s+I:\s+(-?\d+\.\d) LUFS", r.stderr)
    p = re.findall(r"Peak:\s+(-?\d+\.\d) dBFS", r.stderr)
    return (i[-1] if i else "?"), (p[-1] if p else "?")


def first_onset(a, t0, t1, thr_db=-40):
    h = int(0.005 * SR)
    for p in range(int(t0 * SR), int(t1 * SR), h):
        seg = a[p: p + h]
        if len(seg) and 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9) > thr_db:
            return p / SR
    return None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else str(C.EP / "成片_竖屏_中英字幕.mp4")
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    pr = probe(path)
    v = next(s for s in pr["streams"] if s.get("width"))
    au = next(s for s in pr["streams"] if s.get("sample_rate"))
    dur = float(pr["format"]["duration"])
    print(f"画面 {v['width']}×{v['height']} {v['r_frame_rate']} fps；音频 {au['codec_name']} {au['sample_rate']} Hz {au['channels']} 声道；时长 {dur:.2f} s；{int(pr['format']['size']) / 1e6:.1f} MB")
    ok = (v["width"], v["height"]) == (C.W, C.H) and 20 <= dur <= 30 and au["channels"] == 2
    print("  规格：" + ("通过" if ok else "⚠ 不符（要 1080×2340、20–30 s、立体声）"))
    I, P = lufs(path)
    print(f"响度 {I} LUFS，真峰值 {P} dBFS（目标 −16 LUFS，峰值 ≤ −1）")
    a = load_audio(path)                     # 48 kHz：量开口时刻
    a16 = load_audio(path, 16000)            # 16 kHz：喂识别器（faster-whisper 对 numpy 数组按 16 kHz 解释，48 kHz 的会变成乱码）
    from faster_whisper import WhisperModel
    m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
    nrm = lambda s: re.sub(r"[^\w]|_", "", s.lower().replace(" ", ""))
    low = []
    for r, sub_lines in zip(tl["lines"], [[s for s in tl["subs"] if s["id"] == r["id"]] for r in tl["lines"]]):
        s0, s1 = r["onset"] - 0.05, r["onset"] + r["dur"] + 0.15
        seg = a16[int(max(0, s0) * 16000): int(s1 * 16000)]
        segs, _ = m.transcribe(seg, language="zh", beam_size=5, condition_on_previous_text=False, temperature=0, initial_prompt="以下是普通话的句子，使用简体中文。")
        hyp = "".join(x.text for x in segs)
        sc = difflib.SequenceMatcher(None, nrm(r["say"]), nrm(hyp)).ratio()
        on = first_onset(a, max(0.0, r["onset"] - 0.06), r["onset"] + 0.6)       # 上一句念完到这句开口之间空 0.12 s，从开口前 0.06 s 起找才不会量到上一句的尾巴
        d_ms = None if on is None else (on - r["onset"]) * 1000
        cover = all(s["a"] - 0.12 <= (r["onset"] if k == 0 else r["onset"] + r["cue_at"][k - 1]) + 0.03 and s["b"] >= (r["onset"] + r["dur"] if k == len(sub_lines) - 1 else r["onset"] + r["cue_at"][k]) - 0.05
                    for k, s in enumerate(sub_lines))
        flag = []
        if sc < 0.85:
            low.append(r["id"])
            flag.append("识别分低")
        if d_ms is not None and abs(d_ms) > 60:
            flag.append(f"开口偏 {d_ms:+.0f} ms")
        print(f"  {r['id']}  开口 {r['onset']:6.2f} s（实测偏 {'?' if d_ms is None else format(d_ms, '+.0f')} ms）  识别 {sc:.2f}  {hyp}  {'⚠ ' + '、'.join(flag) if flag else ''}")
    print("识别分低于 0.85 的：" + (" ".join(low) if low else "无"))


if __name__ == "__main__":
    main()
