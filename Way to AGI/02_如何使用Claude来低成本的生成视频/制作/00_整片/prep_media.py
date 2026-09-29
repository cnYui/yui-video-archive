# -*- coding: utf-8 -*-
"""整片的素材准备：抽帧、拷图、算波形和嘴型数据、铺音轨。先跑 build_timeline.py。

输出：media/（帧序列和图片）、data.js（波形、字幕行、嘴型）、audio/mix.wav（整片音轨，目前只有作品展示原声、BGM 示范和两个音效）。
"""
import json
import re
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                                  # 教程_Claude做视频/
SERIES = Path(r"D:\大疆\AI科普")
EP04 = SERIES / "第04期_大模型从夯到拉"
WHALE = SERIES / "素材/角色/大肥鱼像素素材包"
MEDIA = HERE / "media"
AUDIO = HERE / "audio"
TL = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
FPS = TL["fps"]


def run(args):
    subprocess.run(args, check=True, capture_output=True)


def frames(name, src, vf, ss=None, t=None, q=2, n=None):
    d = MEDIA / name
    d.mkdir(parents=True, exist_ok=True)
    args = ["ffmpeg", "-v", "error", "-y"]
    if ss is not None:
        args += ["-ss", str(ss)]
    if t is not None:
        args += ["-t", str(t)]
    tail = ["-frames:v", str(n)] if n else []      # 片头从 0 秒取时 -t 会多出帧（2026-09-28 实测 228 帧），按帧数截
    run(args + ["-i", str(src), "-vf", vf, *tail, "-q:v", str(q), str(d / "f_%03d.jpg")])
    n = len(list(d.glob("f_*.jpg")))
    print(f"{name}: {n} frames")
    return n


def still(src, ss, out, vf=None):
    args = ["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", str(src), "-frames:v", "1"]
    if vf:
        args += ["-vf", vf]
    run(args + [str(out)])


def read_wav_mono(p):
    with wave.open(str(p)) as w:
        sr, n, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype={2: np.int16, 4: np.int32}[sw]).astype(np.float32)
    a = a.reshape(-1, ch).mean(axis=1) / (32768.0 if sw == 2 else 2147483648.0)
    return a, sr


def units(text):   # 和 build_timeline.py 一样
    u = 0.0
    for m in re.finditer(r"[A-Za-z][A-Za-z\-]*|\d|[一-鿿]|[，、：；]|[。？！]", text):
        s = m.group(0)
        u += 1.5 if (s[0].isascii() and s[0].isalpha()) else 1.1 if s.isdigit() else 0.9 if s in "，、：；" else 1.6 if s in "。？！" else 1.0
    return u


def mention(pid, phrase):
    p = next(x for x in TL["paras"] if x["id"] == pid)
    i = p["text"].index(phrase)
    return p["start"] + units(p["text"][:i]) / units(p["text"]) * p["speech"]


def main():
    MEDIA.mkdir(exist_ok=True)
    AUDIO.mkdir(exist_ok=True)
    ep04 = EP04 / "第04期_大模型从夯到拉_成片.mp4"

    # ---- 帧序列
    frames("gpt6", ROOT / "素材/GPT6建模/GPT6建模_3倍速_10s.mp4", "scale=1474:830:flags=lanczos")
    # 屏幕录制：全部帧、原尺寸 1402×1020（页面按内容变速、放大，见 index.html 的 S.character）
    d = MEDIA / "sr_all"
    d.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "素材/画角色过程/03_屏幕录制_画侧面走路.mp4"), "-q:v", "3", str(d / "f_%04d.jpg")])
    print("sr_all:", len(list(d.glob("f_*.jpg"))), "frames")
    frames("intro", ep04, "fps=30,scale=1474:680:flags=lanczos", n=114)
    frames("outro", ep04, "fps=30,scale=1474:680:flags=lanczos", ss=382.333, t=4.8, n=144)

    # ---- 静帧和图片
    still(ep04, 162.4, MEDIA / "ep04_still.png")
    still(ROOT / "素材/GPT6建模/GPT6建模_原片30s.mp4", 21.0, MEDIA / "gpt6_still.jpg", "scale=1474:830:flags=lanczos")
    copies = {
        WHALE / "_review/round1.png": "round1.png",
        WHALE / "_review/round6.png": "round6.png",
        WHALE / "素材/palette.png": "palette.png",
        ROOT / "素材/画角色过程/01_鲸鱼娘表情表.webp": "expr.webp",
        ROOT / "素材/画角色过程/02_日报画面里的鲸鱼娘.webp": "daily.webp",
        EP04 / "封面/封面_16x9_1920x1080.png": "cover_16x9.png",
        EP04 / "封面/封面_4x3_1440x1080.png": "cover_4x3.png",
        EP04 / "封面/封面_预览.png": "cover_preview.png",
        EP04 / "制作/build/review/sheet_white.png": "review_sheet.png",
        SERIES / "第01期_什么是API/制作/audio/bgm_analysis.png": "bgm_analysis.png",
    }
    for src, name in copies.items():
        shutil.copy2(src, MEDIA / name)

    # ---- 字幕示意用的真实数据：第 4 期 S04-31 + S04-32 的配音波形和逐句时间、对应的嘴型
    ep_tl = json.loads((EP04 / "制作/timeline.json").read_text(encoding="utf-8"))
    segs = {s["id"]: s for s in ep_tl["segments"]}
    align = json.loads((EP04 / "制作/voice/alignment.json").read_text(encoding="utf-8"))
    ids = ["S04-31", "S04-32"]
    t0 = segs[ids[0]]["start"]
    t1 = segs[ids[-1]]["end"]
    sr_all = None
    env, lines = [], []
    for sid in ids:
        a, sr = read_wav_mono(EP04 / "配音/segments" / f"{sid}.wav")
        sr_all = sr
        off = segs[sid]["start"] - t0
        for ln in align[sid]:
            lines.append({"text": ln["text"], "start": round(off + ln["start"], 3), "end": round(off + ln["end"], 3)})
    # 按时间轴位置摆放两段，再算 20 ms 的 RMS 包络
    total_len = int((t1 - t0) * sr_all) + 1
    buf = np.zeros(total_len, dtype=np.float32)
    for sid in ids:
        a, sr = read_wav_mono(EP04 / "配音/segments" / f"{sid}.wav")
        i0 = int((segs[sid]["start"] - t0) * sr)
        buf[i0:i0 + len(a)] = a[: max(0, min(len(a), total_len - i0))]
    hop = int(sr_all * 0.02)
    rms = np.sqrt(np.convolve(buf ** 2, np.ones(hop) / hop, mode="same"))[::hop]
    env = (rms / (rms.max() + 1e-9)).round(3).tolist()
    mouth = ep_tl.get("mouth") or json.loads((EP04 / "制作/voice/mouth.json").read_text(encoding="utf-8"))
    m0 = int(round(t0 * FPS))
    m1 = int(round(t1 * FPS))
    data = {"wave": env, "waveStep": 0.02, "lines": lines, "clipDur": round(t1 - t0, 3), "mouth": mouth[m0:m1]}
    (HERE / "data.js").write_text("window.DATA = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    print("data.js: wave", len(env), "lines", len(lines), "mouth", m1 - m0, "clip", round(t1 - t0, 2))

    # ---- 整片音轨：作品展示原声 + BGM 示范 + “嗒”“叮”；其余静音，等口播进来再混
    total = TL["total"]
    sc = {s["type"]: s for s in TL["scenes"]}
    show = sc["showcase"]
    bgm = sc["bgm"]
    bgm_dur = round(bgm["end"] - bgm["start"] - 1.0, 3)
    pop_t = mention("P26", "“嗒”")
    tick_t = mention("P26", "“叮”")
    inputs = ["-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=48000:cl=stereo",
              "-i", str(ROOT / "制作/01_作品展示/audio/mix.wav"),
              "-i", str(SERIES / "素材/音频/bgm.wav"),
              "-i", str(SERIES / "素材/音频/sfx_pop.wav"),
              "-i", str(SERIES / "素材/音频/sfx_tick.wav")]
    ms = lambda x: int(round(x * 1000))
    graph = (
        f"[1:a]aresample=48000,adelay={ms(show['start'])}|{ms(show['start'])}[show];"
        f"[2:a]aresample=48000,atrim=30:{30 + bgm_dur},asetpts=PTS-STARTPTS,volume=-8dB,"
        f"afade=t=in:d=1.0,afade=t=out:st={bgm_dur - 1.2}:d=1.2,adelay={ms(bgm['start'] + 0.6)}|{ms(bgm['start'] + 0.6)}[bgm];"
        f"[3:a]aresample=48000,volume=-6dB,adelay={ms(pop_t)}|{ms(pop_t)}[pop];"
        f"[4:a]aresample=48000,volume=-6dB,adelay={ms(tick_t)}|{ms(tick_t)}[tick];"
        f"[0:a][show][bgm][pop][tick]amix=inputs=5:normalize=0:duration=first[out]"
    )
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[out]", "-ar", "48000", "-ac", "2",
         str(AUDIO / "mix.wav")])
    print(f"audio/mix.wav {total:.1f}s; showcase @{show['start']:.2f}, bgm @{bgm['start'] + 0.6:.2f} ({bgm_dur}s), 嗒 @{pop_t:.2f}, 叮 @{tick_t:.2f}")


if __name__ == "__main__":
    main()
