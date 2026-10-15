# -*- coding: utf-8 -*-
r"""出镜口播版混音 → audio/mix.wav（48 kHz 立体声，长度 = 时间轴 total）。
（Way to AGI 第 02 期 mix_audio.py 的简化版：这期官方演示画面全部静音，没有作品原声要处理）

- 口播：02_出镜/edit/narration.wav，高通 70 Hz，响度两遍法统一到 −16 LUFS（线性增益，不改动态）；
- BGM：系列 BGM（AI科普/素材/音频/bgm.wav，母带 −20 LUFS）全程很轻地垫在人声下面（−15 dB），开头 1 s 淡入、结尾 1.2 s 淡出；
- 最后限幅到 −1 dBTP。
"""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
NARR = EP / "制作" / "02_出镜" / "edit" / "narration.wav"
BGM = Path(r"D:\大疆\AI科普\素材\音频\bgm.wav")
BED_DB = -15.0
TL = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
TOTAL = TL["total"]


def run(args):
    return subprocess.run([str(a) for a in args], capture_output=True, text=True, encoding="utf-8", errors="replace")


def measure():
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", NARR, "-af", "highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
    j = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S).group(0))
    return j


def main():
    m = measure()
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    fc = (f"[0:a]highpass=f=70,{ln},apad=whole_dur={TOTAL:.3f}[v];"
          f"[1:a]volume={BED_DB}dB,afade=t=in:d=1,afade=t=out:st={TOTAL - 1.2:.3f}:d=1.2,atrim=0:{TOTAL:.3f}[b];"
          f"[v][b]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89:level=0[o]")
    (HERE / "audio").mkdir(exist_ok=True)
    out = HERE / "audio" / "mix.wav"
    r = run(["ffmpeg", "-v", "error", "-y", "-i", NARR, "-stream_loop", "-1", "-i", BGM, "-filter_complex", fc, "-map", "[o]", "-t", f"{TOTAL:.3f}",
             "-ar", "48000", "-ac", "2", out])
    assert out.exists(), r.stderr
    e = run(["ffmpeg", "-hide_banner", "-nostats", "-i", out, "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"]).stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1]
    tp = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", e)[-1]
    print(f"mix.wav 写好：{TOTAL:.1f} s，响度 {i} LUFS，真峰值 {tp} dBFS（口播原始 {m['input_i']} LUFS）")


if __name__ == "__main__":
    main()
