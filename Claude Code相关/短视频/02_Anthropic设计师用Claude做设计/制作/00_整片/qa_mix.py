# -*- coding: utf-8 -*-
"""出片前自查（成片的音轨 + 画面参数）。

  python qa_mix.py [成片路径]        默认 成片_竖屏_中英字幕.mp4

1. ffprobe：分辨率（1080×2340）、帧率（30）、音频（AAC 48 kHz 立体声）、时长和 timeline 对不对；
2. 响度：整条 ebur128（目标 −16 LUFS）、真峰值；
3. 逐句：按 timeline.json 里每块同传的开口时刻，把成片音轨切出来用 large-v3-turbo 识别（原声压低垫在下面，这一步同时验证压得够不够），和台本 say 比（< 0.85 的列出来；
   曼波声线的 sh/x、zh/j 常被听错，Nate / Claude 也常被听成“内特 / 骷髅”，机器分低不等于读错，要用耳朵听）；
4. 整体对齐：成片音轨和混音原件 build/audio.wav 做互相关，量 mp4 / AAC 编码带来的整体错位（毫秒）。
（原声一直垫在下面，逐句量“同传开口时刻”的能量阈值会被原声先触发——第一版这么量出来全是 −80 ms 的假警报，已去掉。）
"""
import difflib
import json
import re
import subprocess
import sys

import numpy as np

import config as C

SR = 48000
BUILD = C.BUILD
TL = json.loads((C.BUILD / "timeline.json").read_text(encoding="utf-8"))


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate,sample_rate,channels,duration,nb_frames:format=duration,size",
                        "-of", "json", str(path)], capture_output=True, text=True)
    return json.loads(r.stdout)


def load_audio(path, sr):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    i = re.findall(r"\n\s+I:\s+(-?\d+\.\d) LUFS", r.stderr)
    p = re.findall(r"Peak:\s+(-?\d+\.\d) dBFS", r.stderr)
    return (i[-1] if i else "?"), (p[-1] if p else "?")


def global_lag_ms(a_mp4, ref_wav, secs=90):
    """成片音轨和 build/audio.wav（混音原件）的整体错位（毫秒）：FFT 互相关取峰。AAC 编码有约 21–46 ms 的起始延迟，是否被 mp4 的编辑列表补掉，看这里。
    （同传开口时刻不再逐句量：原声一直垫在下面，能量阈值会被原声先触发，量出来是窗口起点而不是同传开口。）"""
    ref = load_audio(ref_wav, SR)
    n = min(len(a_mp4), len(ref), secs * SR)
    x, y = a_mp4[:n].astype(np.float64), ref[:n].astype(np.float64)
    m = 1 << int(np.ceil(np.log2(2 * n)))
    cc = np.fft.irfft(np.fft.rfft(x, m) * np.conj(np.fft.rfft(y, m)), m)
    cc = np.concatenate([cc[-SR // 5:], cc[: SR // 5]])            # 只看 ±200 ms
    k = int(np.argmax(cc)) - SR // 5
    return k * 1000.0 / SR


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else str(C.EP / "成片_竖屏_中英字幕.mp4")
    pr = probe(path)
    v = next(s for s in pr["streams"] if s.get("width"))
    au = next(s for s in pr["streams"] if s.get("sample_rate"))
    dur = float(pr["format"]["duration"])
    print(f"画面 {v['width']}×{v['height']} {v['r_frame_rate']} fps；音频 {au['codec_name']} {au['sample_rate']} Hz {au['channels']} 声道；时长 {dur:.2f} s（timeline {TL['total']:.2f} s）；{int(pr['format']['size']) / 1e6:.1f} MB")
    ok = (v["width"], v["height"]) == (C.W, C.H) and au["channels"] == 2 and abs(dur - TL["total"]) < 0.2
    print("  规格：" + ("通过" if ok else "⚠ 不符"))
    I, P = lufs(path)
    print(f"响度 {I} LUFS，真峰值 {P} dBFS（目标 −16 LUFS，峰值 ≤ −1）")
    a = load_audio(path, SR)                 # 48 kHz：和混音原件 build/audio.wav 做互相关
    lag = global_lag_ms(a, BUILD / "audio.wav")
    a16 = load_audio(path, 16000)            # 16 kHz：喂识别器（faster-whisper 对 numpy 数组按 16 kHz 解释，48 kHz 的会变成乱码）
    from faster_whisper import WhisperModel
    m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
    nrm = lambda s: re.sub(r"[^\w]|_", "", s.lower().replace(" ", ""))
    voice = {l["id"]: l for l in json.loads((C.EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))["lines"]}
    low = []
    for p in TL["passages"]:
        for t in p["tts"]:
            say = voice[t["id"]]["say"]
            s0, s1 = t["start"] - 0.05, t["start"] + t["dur"] + 0.15
            seg = a16[int(max(0, s0) * 16000): int(s1 * 16000)]
            segs, _ = m.transcribe(seg, language="zh", beam_size=5, condition_on_previous_text=False, temperature=0, initial_prompt="以下是普通话的句子，使用简体中文。")
            hyp = "".join(x.text for x in segs)
            sc = difflib.SequenceMatcher(None, nrm(say), nrm(hyp)).ratio()
            flag = []
            if sc < 0.85:
                low.append(t["id"])
                flag.append("识别分低")
            print(f"  {t['id']}  开口 {t['start']:7.2f} s  识别 {sc:.2f}  {hyp}  {'⚠ ' + '、'.join(flag) if flag else ''}")
    print("识别分低于 0.85 的：" + (" ".join(low) if low else "无") + "（Nate / Claude 的同音误听、sh/x 的老毛病会把分数拉低；用 qa_tts2.py 带提示词再听，仍要耳朵听）")
    print(f"成片音轨相对混音原件 build/audio.wav 的整体错位：{lag:+.1f} ms（±50 ms 内算对得上）")


if __name__ == "__main__":
    main()
