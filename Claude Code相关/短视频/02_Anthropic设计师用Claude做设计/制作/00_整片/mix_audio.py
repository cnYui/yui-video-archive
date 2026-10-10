# -*- coding: utf-8 -*-
"""混音：原片原声（说话 + 界面音效 + Slides 自带的 BGM）+ 曼波同传 + **系列 BGM** → build/audio.wav（48 kHz 立体声，长度 = 全片）。

  python mix_audio.py

- 同传：02_配音/edit/lines/<id>.wav 按 timeline.json 里的开口时刻放（单声道复制成双声道），整条拉到 −16 LUFS（线性增益）。
- 原声：每段取原片音轨 [cin, cin + audio.len]（Design 是单声道，复制成双声道；Slides 是立体声，自带的 BGM 在里面分不开，整条一起用），放在该段起点；
  同一个来源用到的所有片段拼起来量一次响度，用同一个线性增益拉到 FOOT_LUFS（−21）；每个片段首尾各 20 ms 淡入淡出。
- 同传说话时把原声压 DUCK_DB（−8 dB）：10 ms 一格的同传包络，前 0.12 s、后 0.40 s 保持，再平滑 0.15 s；没人说话时原声照常（界面音效、Slides 自带的 BGM 都听得见）。
- **系列 BGM（用户 2026-10-04：“按照skill中的要求，还需要给视频加上bgm”；技能 short-video 的 mix_audio 规则）**：`AI科普/素材/音频/bgm.wav`（lo-fi 轻爵士，F 大调 80 BPM，492 s，
  原件 −20 LUFS、LRA 3.0、没有底鼓和军鼓、1–4 kHz 比主体低约 28 dB，给配音让位），从文件开头起全程垫在下面：BGM_BED_DB = −16 dB（≈ −36 LUFS，比配音低约 20 dB，
  文件自带的混音建议是 18–22 dB），头 1 s 淡入、尾 BGM_OUT s 淡出；同传停下来的空档（≥ 0.3 s）回升 BGM_SWELL_DB（+5 dB，文件建议 3–4 dB、技能引擎 +8 dB），
  升降都用 0.5 s 以上的平滑斜坡（不要泵动感）。**Slides 那一章原声里自带 BGM**（分不开），系列 BGM 在那几段再降 SLIDES_EXTRA_DB（−6 dB）、交界处 0.8 s 渐变，让自带的音乐领头、
  不要两首叠在一起一样响。（技能引擎的规则是“有原声的素材段 BGM 压到 ×0.05”——这条每一段都有原声，照搬等于听不见，所以改成上面的整条垫底 + 说话时压低。）
- 整体再拉到 −16 LUFS（同传主导，BGM 对总响度的影响 < 0.05 LU），峰值超过 −1 dBFS 的少数采样点软限幅压回去。
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

import config as C

SR = 48000
VOICE_LUFS, FOOT_LUFS, FINAL_LUFS, DUCK_DB = -16.0, -21.0, -16.0, -8.0
BGM_FILE = Path(r"D:\大疆\AI科普\素材\音频\bgm.wav")
BGM_BED_DB, BGM_SWELL_DB, SLIDES_EXTRA_DB = -16.0, 5.0, -6.0
BGM_IN, BGM_OUT = 1.0, 2.5


def run(args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True)


def load(path, ss=None, t=None):
    args = ["ffmpeg", "-v", "error"]
    if ss is not None:
        args += ["-ss", f"{ss:.4f}"]
    args += ["-i", str(path)]
    if t is not None:
        args += ["-t", f"{t:.4f}"]
    args += ["-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(run(args).stdout, dtype=np.float32).reshape(-1, 2).copy()


def lufs_of(a):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                       input=a.astype(np.float32).tobytes(), capture_output=True)
    err = p.stderr.decode("utf-8", "replace")
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def voice_activity(voice, n, pre=0.12, post=0.40):
    """同传活动包络：10 ms 一格的能量 > −50 dB 算在说话，前 pre 秒、后 post 秒保持 → (act 0/1 的细粒度数组, hop)。"""
    hop = SR // 100
    k = n // hop
    m = voice[: k * hop].mean(1)
    rms = 20 * np.log10(np.sqrt((m.reshape(k, hop) ** 2).mean(1)) + 1e-9)
    act = (rms > -50).astype(np.float32)
    a, b = int(pre * 100), int(post * 100)
    pad = np.pad(act, (a, b))
    dil = np.array([pad[i: i + a + b + 1].max() for i in range(k)], np.float32)
    return dil


def voice_duck(voice, n):
    hop = SR // 100
    dil = voice_activity(voice, n)
    sm = np.convolve(dil, np.ones(15) / 15, mode="same")
    g = 1 - (1 - 10 ** (DUCK_DB / 20)) * sm
    return np.interp(np.arange(n) / hop, np.arange(len(g)), g).astype(np.float32)


def smooth(x, secs):
    w = max(1, int(secs * 100))                       # x 是 10 ms 一格
    return np.convolve(x, np.ones(w) / w, mode="same")


def bgm_track(voice, n, tl):
    """系列 BGM：整条垫底，同传空档回升，Slides 章再降一点；返回 (n, 2)。"""
    b = load(BGM_FILE, t=n / SR + 1.0)
    assert len(b) >= n, "BGM 不够长（需要循环再写）"
    b = b[:n]
    hop = SR // 100
    k = n // hop
    # 同传空档：说话包络再膨胀 0.3 s（短于 0.3 s 的小停顿不回升），取反，平滑 0.5 s
    act = voice_activity(voice, n, pre=0.3, post=0.3)
    gap = smooth(1 - act, 0.5)
    swell = 10 ** (BGM_SWELL_DB / 20)
    g100 = 1 + (swell - 1) * gap
    # Slides 章：整段 −6 dB，交界处 0.8 s 渐变
    sl = np.zeros(k, np.float32)
    for p in tl["passages"]:
        if p["src"] == "slides":
            a, bb = int(p["t0"] * 100), int(min(k, (p["t0"] + p["dur"]) * 100))
            sl[a:bb] = 1.0
    sl = smooth(sl, 0.8)
    g100 = g100 * (1 + (10 ** (SLIDES_EXTRA_DB / 20) - 1) * sl)
    g = np.interp(np.arange(n) / hop, np.arange(k), g100[:k]).astype(np.float32)
    out = b * (10 ** (BGM_BED_DB / 20)) * g[:, None]
    fi, fo = int(BGM_IN * SR), int(BGM_OUT * SR)
    out[:fi] *= np.linspace(0, 1, fi)[:, None]
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return out


def main():
    tl = json.loads((C.BUILD / "timeline.json").read_text(encoding="utf-8"))
    n = int(round((tl["total"] + 0.3) * SR))
    voice = np.zeros((n, 2), np.float32)
    for p in tl["passages"]:
        for t in p["tts"]:
            a = load(C.EP / "制作" / "02_配音" / "edit" / "lines" / f"{t['id']}.wav")
            k = int(round(t["start"] * SR))
            voice[k: k + len(a)] += a[: max(0, n - k)]
    v_cur = lufs_of(voice)
    voice *= 10 ** ((VOICE_LUFS - v_cur) / 20)

    pieces = []
    for p in tl["passages"]:
        au = p["audio"]
        seg = load(C.AUD[au["src"]], ss=au["cin"], t=au["len"])
        pieces.append((p["id"], au["src"], int(round(p["t0"] * SR)), seg))
    gains, info = {}, []
    for src in sorted({x[1] for x in pieces}):
        cat = np.concatenate([x[3] for x in pieces if x[1] == src])
        cur = lufs_of(cat)
        gains[src] = 10 ** ((FOOT_LUFS - cur) / 20)
        info.append(f"{src} 原始 {cur:.1f} LUFS → {FOOT_LUFS}（{20 * np.log10(gains[src]):+.1f} dB）")
    foot = np.zeros((n, 2), np.float32)
    f = int(0.02 * SR)
    for pid, src, k, seg in pieces:
        a = seg * gains[src]
        if len(a) > 2 * f:
            a[:f] *= np.linspace(0, 1, f)[:, None]
            a[-f:] *= np.linspace(1, 0, f)[:, None]
        foot[k: k + len(a)] += a[: max(0, n - k)]
    foot *= voice_duck(voice, n)[:, None]
    bgm = bgm_track(voice, n, tl)

    mix = voice + foot + bgm
    cur = lufs_of(mix)
    gfin = 10 ** ((FINAL_LUFS - cur) / 20)
    mix *= gfin
    lim = 10 ** (-1.0 / 20)
    over = np.abs(mix) > lim
    mix[over] = np.sign(mix[over]) * (lim + (np.abs(mix[over]) - lim) * 0.2)
    mix = np.clip(mix, -lim, lim)
    out = C.BUILD / "audio.wav"
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    # 报告：各条轨在整条里的响度（单独量），BGM 比配音低多少
    bg_l = lufs_of(bgm * gfin)
    print(f"audio.wav {n / SR:.2f} s；同传 {v_cur:.1f} → {VOICE_LUFS} LUFS；原声 {'；'.join(info)}；整条 {lufs_of(mix):.1f} LUFS，峰值 {20 * np.log10(float(np.abs(mix).max())):.1f} dBFS")
    print(f"系列 BGM 单独 {bg_l:.1f} LUFS（整条积分，含淡入淡出和空档回升）；比配音（{VOICE_LUFS:.0f} LUFS）低 {VOICE_LUFS - bg_l:.1f} dB；BGM 文件 {BGM_FILE.name} 从 0 s 起")


if __name__ == "__main__":
    main()
