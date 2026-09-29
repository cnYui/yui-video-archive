"""Build the voice track, the per-frame mouth levels and the final full-length audio mix.

Reads  timeline.json, ../配音/segments/<id>.wav, audio/bgm.wav, audio/sfx_pop.wav, audio/sfx_tick.wav
Writes build/voice_main.wav, timeline.json["mouth"] (+ voice/mouth.json), build/mix.wav (48 kHz stereo)

Full-length = intro + main + outro, so voice and SFX are offset by the intro length.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
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
    tl_path = HERE / "timeline.json"
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    intro, main_d, total = tl["intro"], tl["main_duration"], tl["total_duration"]
    seg_dir = HERE.parent / "配音" / "segments"

    # --- voice track (main time) ---
    voice = np.zeros(int(main_d * SR) + SR, dtype=np.float32)
    for s in tl["segments"]:
        clip = load(seg_dir / f"{s['id']}.wav")
        a = int(s["start"] * SR)
        voice[a:a + len(clip)] += clip[: len(voice) - a]
    peak = np.abs(voice).max()
    voice *= db(-3) / peak
    voice = voice[: int(main_d * SR)]
    (HERE / "build").mkdir(exist_ok=True)
    save(HERE / "build" / "voice_main.wav", voice)

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
    tl_path.write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "voice").mkdir(exist_ok=True)
    (HERE / "voice" / "mouth.json").write_text(json.dumps(tl["mouth"]), encoding="utf-8")

    # --- full mix ---
    N = int(total * SR)
    out = np.zeros((N, 2), dtype=np.float32)
    off = int(intro * SR)
    v = np.zeros(N, dtype=np.float32)
    v[off:off + len(voice)] = voice[: N - off]
    out += v[:, None] * db(-1.0)

    bgm = load(HERE / "audio" / "bgm.wav", channels=2)
    if len(bgm) < N:
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
    # intro / outro carry no voice: lift the BGM +16 dB there (music-only brand stings), with 1.2 s ramps that finish before the first/after the last line
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

    pop = load(HERE / "audio" / "sfx_pop.wav", channels=2)
    tick = load(HERE / "audio" / "sfx_tick.wav", channels=2)
    for sc in tl["scenes"][1:]:
        place(pop, intro + sc["start"] + 0.05, -20)
    for g in tl["gaps"]:
        if "打勾" in g["visual"]:
            place(tick, intro + g["start"] + 0.1, -18)

    pk = np.abs(out).max()
    if pk > db(-1):
        out *= db(-1) / pk
    save(HERE / "build" / "mix_raw.wav", out)
    # loudness normalise for Bilibili (-16 LUFS, true peak -1.5 dB). Two-pass *linear* loudnorm: a single
    # pass runs in dynamic mode and would pump the music-only intro/outro back up, undoing the mix balance.
    raw_path = HERE / "build" / "mix_raw.wav"
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw_path),
                            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    ln = ("loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:"
          f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw_path), "-af", ln, "-ar", str(SR),
                    str(HERE / "build" / "mix.wav")], check=True)
    print(f"voice {main_d:.1f}s, mix {total:.1f}s, mouth frames {n} (open {np.mean(mouth > 0):.0%})")


if __name__ == "__main__":
    main()
