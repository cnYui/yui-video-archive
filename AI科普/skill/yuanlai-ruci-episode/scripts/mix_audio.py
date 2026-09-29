"""Build the voice track, the per-frame mouth levels and the final full-length audio mix.

  python mix_audio.py <episode_dir> [--series D:/大疆/AI科普]

Reads  制作/timeline.json, 配音/segments/<id>.wav, SERIES/素材/音频/bgm.wav, sfx_pop.wav, sfx_tick.wav
Writes 制作/build/voice_main.wav, timeline.json["mouth"] (+ 制作/voice/mouth.json),
       制作/build/mix_raw.wav, 制作/build/mix.wav (48 kHz stereo, whole video = intro + main + outro)

Mix (episode-1 final settings): voice peak -3 dBFS then -1 dB; BGM -17 dB with 1.5 s fade-in / 3 s fade-out,
ducked a further 7 dB while a segment is spoken (80 ms attack / 450 ms release); under the intro and
outro the BGM is lifted +16 dB with 1.2 s ramps; "嗒" pop (-20 dB) at every chapter start after the
first; tick (-18 dB) when a TOC question is checked (timeline toc.done) and on gaps whose note says 打勾.
Then two-pass *linear* loudnorm to -16 LUFS / -1.5 dBTP (single-pass dynamic mode would pump the
music-only intro/outro back up). Mouth: per video frame 0/1/2 from voice RMS (-24 / -9 dB vs 90th pct).
Run after build_timeline.py whenever it says so (it keeps `mouth` only if the mix inputs did not change).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402

SR = 48000


def load(path, channels=1):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-ac", str(channels), "-ar", str(SR),
                                   "-f", "f32le", "-"])
    x = np.frombuffer(raw, dtype=np.float32).copy()
    return x.reshape(-1, channels) if channels > 1 else x


def save(path, x):
    ch = 1 if x.ndim == 1 else x.shape[1]
    x16 = (np.clip(x, -1, 1) * 32767).astype("<i2")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", str(ch), "-i", "-", str(path)],
                   input=x16.tobytes(), check=True)


def db(g):
    return 10 ** (g / 20)


def smooth_env(active, attack=0.08, release=0.45):
    """One-pole envelope follower on a 0/1 per-sample activity signal."""
    a_up, a_dn = np.exp(-1 / (attack * SR)), np.exp(-1 / (release * SR))
    out = np.empty_like(active)
    v = 0.0
    for i, s in enumerate(active[:: 48]):          # 1 ms resolution, then upsample
        c = a_up ** 48 if s > v else a_dn ** 48
        v = s + (v - s) * c
        out[i * 48:(i + 1) * 48] = v
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_common(ap)
    args = ap.parse_args()
    p = C.Paths(args.episode_dir, args.series)
    tl = C.load_json(p.timeline)
    if tl is None:
        sys.exit(f"缺少 {p.timeline}：先运行 build_timeline.py")
    for f in ("bgm.wav", "sfx_pop.wav", "sfx_tick.wav"):
        if not (p.audio / f).exists():
            sys.exit(f"缺少系列音频 {p.audio / f}")
    missing = [s["id"] for s in tl["segments"] if not (p.segments / f"{s['id']}.wav").exists()]
    if missing:
        sys.exit(f"配音/segments 里缺少 {len(missing)} 段：{missing[:8]}…（先 segment_audio.py）")
    intro, main_d, total = tl["intro"], tl["main_duration"], tl["total_duration"]

    # --- voice track (main time) ---
    voice = np.zeros(int(main_d * SR) + SR, dtype=np.float32)
    over = []
    for s in tl["segments"]:
        clip = load(p.segments / f"{s['id']}.wav")
        a = int(s["start"] * SR)
        voice[a:a + len(clip)] += clip[: len(voice) - a]
        if len(clip) / SR > s["end"] - s["start"] + 0.05:
            over.append(s["id"])
    peak = np.abs(voice).max()
    voice *= db(-3) / peak
    voice = voice[: int(main_d * SR)]
    p.build.mkdir(parents=True, exist_ok=True)
    save(p.build / "voice_main.wav", voice)

    # --- mouth levels per video frame ---
    fps = tl["fps"]
    hop = SR // fps
    n = int(np.ceil(main_d * fps))
    pad = np.pad(voice, (0, n * hop - len(voice)))
    rms = np.sqrt(np.mean(pad.reshape(n, hop) ** 2, axis=1) + 1e-12)
    ref = np.percentile(rms[rms > 1e-4], 90) if np.any(rms > 1e-4) else 1.0
    lv = 20 * np.log10(rms / ref)
    mouth = np.where(lv > -9, 2, np.where(lv > -24, 1, 0)).astype(int)
    # no single-frame flicker: a level must hold at least 2 frames
    for i in range(1, n - 1):
        if mouth[i] != mouth[i - 1] and mouth[i] != mouth[i + 1]:
            mouth[i] = mouth[i - 1]
    tl["mouth"] = mouth.tolist()
    C.write_json(p.timeline, tl)
    p.prod_voice.mkdir(parents=True, exist_ok=True)
    (p.prod_voice / "mouth.json").write_text(json.dumps(tl["mouth"]), encoding="utf-8")

    # --- full mix ---
    N = int(total * SR)
    out = np.zeros((N, 2), dtype=np.float32)
    off = int(intro * SR)
    v = np.zeros(N, dtype=np.float32)
    v[off:off + len(voice)] = voice[: N - off]
    out += v[:, None] * db(-1.0)

    bgm = load(p.audio / "bgm.wav", channels=2)
    while len(bgm) < N:
        bgm = np.concatenate([bgm, bgm[: N - len(bgm)]])
    bgm = bgm[:N].copy()
    fi, fo = int(1.5 * SR), int(3.0 * SR)
    bgm[:fi] *= np.linspace(0, 1, fi)[:, None]
    bgm[-fo:] *= np.linspace(1, 0, fo)[:, None]
    # ducking: BGM sits at -17 dB, and a further -7 dB while the voice is talking
    active = np.zeros(N, dtype=np.float32)
    for s in tl["segments"]:
        a, b = off + int(s["start"] * SR), off + int(s["end"] * SR)
        active[a:b] = 1.0
    env = smooth_env(active)
    gain = db(-17) * (1 - env * (1 - db(-7)))
    # intro / outro carry no voice: lift the BGM +16 dB there, with 1.2 s ramps that finish before the
    # first / start after the last line
    lift = np.ones(N, dtype=np.float32)
    ramp = int(1.2 * SR)
    lift[:off] = db(16)
    lift[off:off + ramp] = np.linspace(db(16), 1, ramp)
    end_main = off + len(voice)
    lift[end_main:] = db(16)
    lift[max(0, end_main - ramp):end_main] = np.linspace(1, db(16), end_main - max(0, end_main - ramp))
    gain *= lift
    out += bgm * gain[:, None]

    def place(sfx, t, g):
        a = int(t * SR)
        seg = sfx[: max(0, N - a)]
        out[a:a + len(seg)] += seg * db(g)

    pop = load(p.audio / "sfx_pop.wav", channels=2)
    tick = load(p.audio / "sfx_tick.wav", channels=2)
    for sc in tl["scenes"][1:]:
        place(pop, intro + sc["start"] + 0.05, -20)
    ticks = C.tick_times(tl)
    for t in ticks:
        place(tick, intro + t + 0.1, -18)

    pk = np.abs(out).max()
    if pk > db(-1):
        out *= db(-1) / pk
    raw_path = p.build / "mix_raw.wav"
    save(raw_path, out)
    # loudness normalise for Bilibili (-16 LUFS, true peak -1.5 dB), two-pass linear
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw_path),
                            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    ln = ("loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:"
          f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw_path), "-af", ln, "-ar", str(SR),
                    str(p.build / "mix.wav")], check=True)
    print(f"voice {main_d:.1f}s, mix {total:.1f}s, mouth frames {n} (open {np.mean(mouth > 0):.0%}), "
          f"pops {len(tl['scenes']) - 1}, ticks {len(ticks)}, raw loudness {m['input_i']} LUFS")
    print(f"-> {p.build / 'mix.wav'}")
    if over:
        print(f"[提醒] 这些段的录音比时间轴里的时长长（durations.json 过期？）：{over[:8]}")


if __name__ == "__main__":
    main()
