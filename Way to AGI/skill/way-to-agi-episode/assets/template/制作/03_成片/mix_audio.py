# -*- coding: utf-8 -*-
"""成片混音 → audio/mix.wav（48 kHz 立体声，长度 = timeline 的 total）。

- 口播：02_出镜/edit/narration.wav，高通 70 Hz，响度两遍法统一到 −16 LUFS（录音本身底噪约 −64 dBFS、动态 4 LU，不另外降噪压缩）；
- 作品片段原声：各自先统一到 −18 LUFS；有人声时压低 SHOW_DUCK dB，口播里留的停顿（edit.json 的 holds）抬回原音量；
- BGM：系列 BGM（AI科普/素材/音频/bgm.wav，母带 −20 LUFS），全程很轻地垫在人声下面；作品展示时让开，
  讲 BGM 的那一段抬高一点（“正在播放这首 BGM”），片尾动画时抬到比人声低 7 dB（和 add_to_video.py 一样）后淡出；
- 音效：讲 BGM 那一段说到“音效”时放一次“嗒”“叮”。
最后整体限幅到 −1 dBTP。
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERIES = Path(r"D:\大疆\AI科普")                     # 《原LAI如此》系列目录（BGM、音效）
SR = 48000
TL = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
NARR_LUFS = -16.0
SHOW_LUFS, SHOW_DUCK, EP04_DUCK = -18.0, -13.0, -17.0     # 片段原声；有人声时压低多少 dB（第 4 期里也有人声，压得更低）
BGM_BED, BGM_DEMO, BGM_OUTRO = -15.0, -8.0, -3.0          # BGM 相对母带（−20 LUFS）的增益：平时、讲 BGM 时、片尾


def run(args, **kw):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True, **kw)


def load(path, ss=None, dur=None, af=None):
    """任意音频 → float32 (n, 2) @ 48 kHz。"""
    args = ["ffmpeg", "-v", "error"]
    if ss is not None:
        args += ["-ss", f"{ss:.3f}"]
    if dur is not None:
        args += ["-t", f"{dur:.3f}"]
    args += ["-i", path, "-vn"]
    if af:
        args += ["-af", af]
    args += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = run(args).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def lufs(path_or_array):
    if isinstance(path_or_array, np.ndarray):
        tmp = HERE / "audio" / "_tmp_lufs.wav"
        write_wav(tmp, path_or_array)
        path_or_array = tmp
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path_or_array), "-af", "ebur128=framelog=quiet:peak=true",
                          "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    i = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])
    tp = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", err)
    return i, (float(tp[-1]) if tp and tp[-1] != "-inf" else None)


def write_wav(path, a):
    import wave
    a = np.clip(a, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


def db(x):
    return 10 ** (x / 20)


def ramp_env(n, spans, base, up, r=0.3):
    """包络：平时 base dB，spans 里的时间段 up dB，边上 r 秒线性过渡。返回线性增益 (n,)。"""
    t = np.arange(n) / SR
    g = np.full(n, float(base))
    for a, b in spans:
        k = np.clip(np.minimum((t - (a - r)) / r, ((b + r) - t) / r), 0, 1)
        g = np.maximum(g, base + (up - base) * k)
    return db(g)


def units(text):
    u = 0.0
    for m in re.finditer(r"[A-Za-z][A-Za-z\-]*|\d|[一-鿿]|[，、：；,]|[。？！?!]", text):
        s = m.group(0)
        u += 1.5 if (s[0].isascii() and s[0].isalpha()) else 1.1 if s.isdigit() else 0.9 if s in "，、：；," else 1.6 if s in "。？！?!" else 1.0
    return u


def phrase_time(i, phrase):
    """第 i 句字幕里说到 phrase 的时刻（和页面里的 cueT 一样）。"""
    c = TL["cues"][i]
    k = c["zh"].index(phrase)
    f = units(c["zh"][:k]) / units(c["zh"])
    m = c["map"]
    for j in range(1, len(m)):
        if f <= m[j][0] + 1e-9:
            a, b = m[j - 1], m[j]
            return a[1] + (b[1] - a[1]) * ((f - a[0]) / (b[0] - a[0]) if b[0] > a[0] else 0)
    return c["e"]


def place(out, a, t0):
    i0 = int(round(t0 * SR))
    n = min(len(a), len(out) - i0)
    if n > 0:
        out[i0:i0 + n] += a[:n]


def main():
    (HERE / "audio").mkdir(exist_ok=True)
    total = TL["total"]
    N = int(round(total * SR))
    out = np.zeros((N, 2), dtype=np.float32)

    # ---- 口播（两遍法 loudnorm，线性增益，不改动态）
    narr_src = HERE.parent / "02_出镜" / "edit" / "narration.wav"
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(narr_src), "-af",
                          f"highpass=f=70,loudnorm=I={NARR_LUFS}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(err[err.rindex("{"): err.rindex("}") + 1])
    af = (f"highpass=f=70,loudnorm=I={NARR_LUFS}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    narr = load(narr_src, af=af + f",aresample={SR}")
    place(out, narr, 0.0)
    speech_i, speech_tp = lufs(narr)
    print(f"narration: in {m['input_i']} LUFS / TP {m['input_tp']} → {speech_i:.1f} LUFS / TP {speech_tp}")

    # ---- 作品片段原声
    import importlib.util
    spec = importlib.util.spec_from_file_location("prep_media", HERE / "prep_media.py")
    pm = importlib.util.module_from_spec(spec); spec.loader.exec_module(pm)
    show = TL.get("show") or {"pages": [0, 0], "items": []}
    holds = [(h["out_s"], h["out_e"]) for h in TL["holds"] if h["out_e"] < show["pages"][-1] + 1]
    for it in show["items"]:
        src, ss, _ = pm.show_ss(it["key"], it)
        dur = it["t1"] - it["t0"]
        a = load(src, ss=ss, dur=dur)
        li, _ = lufs(a)
        a *= db(SHOW_LUFS - li)
        # 淡入淡出（和画面换片的 0.4 秒交叉一致）
        fi, fo = int(0.25 * SR), int(0.35 * SR)
        a[:fi] *= np.linspace(0, 1, fi)[:, None]
        a[-fo:] *= np.linspace(1, 0, fo)[:, None]
        # 有人声压低，停顿里抬起（停顿时间换算到片段自己的时间）
        duck = EP04_DUCK if it["key"] == "ep04" else SHOW_DUCK
        spans = [(max(0, h0 - it["t0"]), h1 - it["t0"]) for h0, h1 in holds if h1 > it["t0"] and h0 < it["t1"]]
        a *= ramp_env(len(a), spans, duck, 0.0, r=0.25)[:, None]
        place(out, a, it["t0"])
        print(f"show {it['key']}: {it['t0']:.2f}-{it['t1']:.2f} src {ss}+{dur:.2f}s, {li:.1f} LUFS → {SHOW_LUFS}, duck {duck} dB, up {spans}")

    # ---- BGM
    bgm = load(SERIES / "素材" / "音频" / "bgm.wav", dur=total + 1)
    bgm = bgm[:N] if len(bgm) >= N else np.pad(bgm, ((0, N - len(bgm)), (0, 0)))
    t = np.arange(N) / SR
    g = np.full(N, BGM_BED)
    p0, p1 = show["pages"][0], show["pages"][-1]
    sc = {s["type"]: s for s in TL["scenes"]}
    # 作品展示时让开（前后 0.8 秒淡出淡入）
    if show["items"]:
        k = np.clip(np.minimum((t - p0) / 0.8, (p1 + 0.8 - t) / 0.8), 0, 1)
        g = g + (-60 - BGM_BED) * k
    # 讲 BGM 的那一段抬高（02 期的例子）
    b0 = b1 = 0.0
    if "bgm" in sc:
        b0, b1 = sc["bgm"]["start"] + 0.3, sc["bgm"]["end"] - 0.3
        k = np.clip(np.minimum((t - b0) / 0.8, (b1 - t) / 0.8), 0, 1)
        g = g + (BGM_DEMO - BGM_BED) * k
    # 页面里画片尾时（默认不画）：比人声低 7 dB，最后 1.2 秒淡出
    c0 = sc["credits"]["start"] if "credits" in sc else total
    if "credits" in sc:
        k = np.clip((t - (c0 - 0.3)) / 0.6, 0, 1)
        g = g + (BGM_OUTRO - BGM_BED) * k
    lin = db(g)
    lin *= np.clip(t / 1.0, 0, 1)                       # 开头 1 秒淡入
    lin *= np.clip((total - t) / 1.2, 0, 1)             # 结尾 1.2 秒淡出
    out += bgm * lin[:, None].astype(np.float32)
    print(f"bgm: bed {BGM_BED} dB, demo {BGM_DEMO} dB ({b0:.1f}-{b1:.1f}), outro {BGM_OUTRO} dB from {c0:.1f}; off {p0:.1f}-{p1:.1f}")

    # ---- 音效：02 期讲 BGM 时说到“音效”放一次“嗒”“叮”（例子）
    if "bgm" in sc:
        ts = phrase_time(sc["bgm"]["cue0"], "音效") + 0.4
        pop = load(SERIES / "素材" / "音频" / "sfx_pop.wav") * db(-6)
        tick = load(SERIES / "素材" / "音频" / "sfx_tick.wav") * db(-6)
        place(out, pop, ts)
        place(out, tick, ts + 0.45)
        print(f"sfx: 嗒 @{ts:.2f}, 叮 @{ts + 0.45:.2f}")

    # ---- 限幅、写出
    run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", SR, "-ac", 2, "-i", "-",
         "-af", "alimiter=limit=0.891:level=false:attack=5:release=60", "-c:a", "pcm_s16le", HERE / "audio" / "mix.wav"],
        input=out.astype(np.float32).tobytes())
    i, tp = lufs(HERE / "audio" / "mix.wav")
    print(f"mix.wav: {total:.2f}s, {i:.1f} LUFS, true peak {tp} dBFS")


if __name__ == "__main__":
    main()
