"""Import the user's own narration recording(s): 配音/raw/C01_v<N>.wav (+ C01_v<N>.json manifest).

  python import_voice.py <期目录> <文件1> [文件2 ...] [--gap 1.0] [--denoise] [--limit auto|on|off] [--no-level]
  python import_voice.py <期目录> --segment S03-12 <文件>      # 补录一句 -> 配音/raw/pickups/S03-12_v<N>.wav

《原LAI如此》 is voiced by the user from 2026-09-28 on (references/voice.md「自己录音」). The files (wav / m4a / mp3 /
anything ffmpeg reads, phone or microphone, also a phone video) are decoded in the given order, each converted to
44.1 kHz mono and lightly cleaned, then joined with --gap s of silence into one 16-bit WAV take. The next free N is
used (an AI take C01_v1.mp3 counts too); nothing is overwritten.

Cleanup (conservative): 70 Hz high-pass (rumble, handling noise, DC). Each file is brought to the same loudness
(-20 LUFS) with one linear gain, so files recorded at different levels (and pickups recorded another day) match.
That is not done twice: mix_audio.py only scales the whole voice track by its peak and loudness-normalises the
final mix; it does not even out files. --no-level skips the gain. The gain is capped so no sample goes above
-1 dBFS; only when that cap would leave the file more than 3 dB short (a pop or a bump on the mic far above the
speech) a peak limiter at -3 dBFS takes those few peaks instead (--limit auto, the default; on = always, off =
never): mix_audio normalises the voice by its PEAK, so one pop would make the whole voice quieter against the
music. Optional --denoise (ffmpeg afftdn, 12 dB; for fan / street noise). A stereo file whose channels differ by
more than 20 dB (one channel empty) uses the louder channel; otherwise the channels are averaged.

Needs 台本/配音分段.json and 配音/chunks.json = the single whole-episode chunk C01 whose ids are the script's
(chunk_voice.py --whole; run automatically when chunks.json is missing or out of date and no take exists yet).
Next: select_takes.py <期目录> -> segment_audio.py <期目录> (episode.json "voice_source": "user", or --user-voice).
"""
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402
import uservoice as U  # noqa: E402

SR = 44100
TARGET_LUFS = -20.0
PEAK_CEIL_DB = -1.0
LIMIT_DB = -3.0
HIGHPASS_HZ = 70
DENOISE = "afftdn=nr=12:nf=-50:tn=1"
HERE = Path(__file__).resolve().parent


def db(g):
    return 10 ** (g / 20)


def probe(path):
    """(duration s, channels) of the first audio stream, or None when ffprobe finds no audio."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                        "stream=channels,sample_rate,codec_name:format=duration", "-of", "json", str(path)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        info = json.loads(r.stdout or "{}")
        st = (info.get("streams") or [None])[0]
        if not st:
            return None
        return float(info.get("format", {}).get("duration") or 0), int(st.get("channels") or 1), st.get("codec_name", "?")
    except (ValueError, TypeError):
        return None


def decode(path, channels):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", str(channels),
                                   "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, channels).copy()


def to_mono(x):
    if x.shape[1] == 1:
        return x[:, 0], "单声道"
    lv = 20 * np.log10(np.sqrt(np.mean(x.astype(np.float64) ** 2, axis=0)) + 1e-12)
    keep = lv >= lv.max() - 20
    if keep.sum() < x.shape[1]:
        names = ["左", "右"] + [str(i + 1) for i in range(2, x.shape[1])]
        used = "、".join(n for n, k in zip(names, keep) if k)
        return x[:, keep].mean(axis=1), f"{x.shape[1]} 声道，只有{used}声道有声音，只用它"
    return x.mean(axis=1), f"{x.shape[1]} 声道，平均成单声道"


def ffilter(x, af):
    """Run an ffmpeg audio filter chain over a mono float32 signal (44.1 kHz)."""
    out = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                          "-af", af, "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"],
                         input=x.astype(np.float32).tobytes(), capture_output=True, check=True).stdout
    y = np.frombuffer(out, dtype=np.float32).copy()
    return y[:len(x)] if len(y) >= len(x) else np.pad(y, (0, len(x) - len(y)))


def loudness(x):
    """Integrated loudness (LUFS, ffmpeg loudnorm's measurement) or None for (near) silence."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       input=x.astype(np.float32).tobytes(), capture_output=True)
    err = r.stderr.decode("utf-8", "replace")
    try:
        v = float(json.loads(err[err.rindex("{"):err.rindex("}") + 1])["input_i"])
    except (ValueError, KeyError):
        return None
    return v if v > -70 else None


def save(path, x):
    x16 = (np.clip(x, -1, 1) * 32767).astype("<i2")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "pcm_s16le", str(path)], input=x16.tobytes(), check=True)


def process(path, args):
    """Decode + clean one file -> (mono signal, info dict)."""
    pr = probe(path)
    if not pr:
        sys.exit(f"读不出声音：{path}（不是音频 / 视频文件，或者文件坏了）")
    dur, ch, codec = pr
    x, chan_note = to_mono(decode(path, ch))
    if len(x) < int(0.3 * SR):
        sys.exit(f"文件太短（{len(x) / SR:.1f} s）：{path}")
    clipped = int(np.sum(np.abs(x) >= 0.999))
    chain = [f"highpass=f={HIGHPASS_HZ}"] + ([DENOISE] if args.denoise else [])
    x = ffilter(x, ",".join(chain))
    info = dict(name=Path(path).name, path=str(Path(path).resolve()), codec=codec, channels=chan_note,
                duration=round(len(x) / SR, 3), clipped_samples=clipped)
    li = loudness(x)
    peak = float(20 * np.log10(np.abs(x).max() + 1e-12))
    info.update(loudness_in=None if li is None else round(li, 1), peak_in=round(peak, 1))
    gain, capped, limited = 0.0, False, False
    if not args.no_level and li is not None:
        gain = float(np.clip(TARGET_LUFS - li, -30, 30))
        short = peak + gain - PEAK_CEIL_DB                 # dB the cap would take off the gain
        if args.limit == "on" and peak + gain > LIMIT_DB or args.limit == "auto" and short > 3:
            limited = True
        elif short > 0:
            gain, capped = PEAK_CEIL_DB - peak, True
        x = x * db(gain)
        if limited:
            x = ffilter(x, f"alimiter=limit={db(LIMIT_DB):.4f}:attack=3:release=60:level=disabled:latency=1")
    info.update(gain_db=round(gain, 1), peak_capped=capped, limited=limited,
                loudness_out=None if li is None else round(li + gain, 1),
                peak_to_loudness=None if li is None else round(peak - li, 1))
    return x.astype(np.float32), info


def check_chunks(p, args, plan):
    """配音/chunks.json must be the whole-episode chunk C01 with the script's ids; make it when that is safe."""
    ids = [s["id"] for s in plan]
    chunks = C.load_json(p.chunks)
    ok = bool(chunks) and len(chunks) == 1 and chunks[0].get("chunk") == "C01" and chunks[0].get("ids") == ids
    if ok:
        return
    takes = [f for f in p.raw.glob("C*_v*.*") if f.suffix.lower() in (".mp3", ".wav")] if p.raw.exists() else []
    cmd = [sys.executable, str(HERE / "chunk_voice.py"), str(p.ep), "--whole", "--series", str(p.series)]
    if chunks is None or not takes:
        why = "还没有 配音/chunks.json" if chunks is None else "配音/chunks.json 不是整期一批 C01 / 和台本的段号对不上"
        print(f"{why}：自动运行 chunk_voice.py --whole（还没有任何录音，不会丢东西）", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            sys.exit(f"chunk_voice.py 出错：\n{r.stdout}{r.stderr}")
        for line in r.stdout.splitlines():              # its voice / tts_api hints are for the AI voice: not shown
            if "->" in line or "移到" in line:
                print("  " + line.strip())
        return
    sys.exit(f"配音/chunks.json 不是整期一批 C01，或者和 台本/配音分段.json 的段号对不上（台本改过？），"
             f"而 配音/raw 里已经有 {len(takes)} 个录音。确认台本定稿后运行：\n"
             f"  python {HERE / 'chunk_voice.py'} {p.ep} --whole --force\n"
             "（旧的 chunks.json 会移到 _旧稿；台本改过的句子要重新录或补录）")


def describe(infos):
    return " + ".join(f"{i['name']} {U.mmss(i['duration'])}" for i in infos)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_common(ap)
    ap.add_argument("files", nargs="+", help="录音文件（wav / m4a / mp3 …），按顺序；可以整期一个文件，也可以按章节几个文件")
    ap.add_argument("--segment", metavar="段号", help="补录一句（例如 S03-12）：存到 配音/raw/pickups/<段号>_v<N>.wav")
    ap.add_argument("--gap", type=float, default=1.0, help="文件之间插入的静音秒数（默认 1.0）")
    ap.add_argument("--denoise", action="store_true", help="降噪（ffmpeg afftdn，12 dB；有风扇、街上的噪音时用）")
    ap.add_argument("--limit", choices=["auto", "on", "off"], default="auto",
                    help="把个别很响的瞬间（喷麦、碰到话筒）压到 -3 dBFS：auto（默认）= 只有它们让音量调不上去 3 dB 以上时；on = 总是；off = 不压")
    ap.add_argument("--no-level", action="store_true", help="不调音量（默认每个文件调到同样的响度 -20 LUFS）")
    args = ap.parse_args()
    p = C.Paths(args.episode_dir, args.series)
    plan = C.load_json(p.voice_plan)
    if not plan:
        sys.exit(f"缺少 {p.voice_plan}：先写好台本，运行 build_script.py")
    files = [Path(f) for f in args.files]
    bad = [str(f) for f in files if not f.is_file()]
    if bad:
        sys.exit("找不到这些文件：\n  " + "\n  ".join(bad))
    if len({f.resolve() for f in files}) < len(files):
        print("[提醒] 同一个文件给了不止一次（照给的顺序拼接）")
    ids = [s["id"] for s in plan]
    if args.segment and args.segment not in ids:
        near = [i for i in ids if i.split("-")[-1] == args.segment.split("-")[-1]]
        sys.exit(f"台本里没有段号 {args.segment}" + (f"（是不是 {near[0]}？）" if near else "") + "：段号见 配音/录音稿.md")
    if not args.segment:
        check_chunks(p, args, plan)
    p.raw.mkdir(parents=True, exist_ok=True)

    parts, infos, t = [], [], 0.0
    gap = np.zeros(int(round(max(0.0, args.gap) * SR)), dtype=np.float32)
    for k, f in enumerate(files):
        x, info = process(f, args)
        if k:
            parts.append(gap)
            t += len(gap) / SR
        info["start"] = round(t, 3)
        parts.append(x)
        t += len(x) / SR
        infos.append(info)
        lv = "" if info["loudness_in"] is None else f"，响度 {info['loudness_in']} LUFS → {info['loudness_out']}"
        print(f"  {info['name']}：{U.mmss(info['duration'])}，{info['channels']}{lv}"
              + ("（峰值限制，没调到 -20）" if info["peak_capped"] else "") + ("，压了峰值" if info["limited"] else ""))
    take = np.concatenate(parts)

    if args.segment:
        folder = p.raw / "pickups"
        folder.mkdir(exist_ok=True)
        stem = args.segment
    else:
        folder, stem = p.raw, "C01"
    n = U.next_version(folder, stem)
    out = folder / f"{stem}_v{n}.wav"
    save(out, take)
    manifest = dict(kind="user", chunk=None if args.segment else "C01", segment=args.segment, file=out.name,
                    created=time.strftime("%Y-%m-%d %H:%M:%S"), duration=round(len(take) / SR, 3),
                    gap=args.gap if len(files) > 1 else 0,
                    processing=dict(highpass_hz=HIGHPASS_HZ, denoise=DENOISE if args.denoise else None,
                                    level_lufs=None if args.no_level else TARGET_LUFS, peak_ceiling_dbfs=PEAK_CEIL_DB,
                                    limit=args.limit, limit_dbfs=LIMIT_DB),
                    sources=infos)
    C.write_json(out.with_suffix(".json"), manifest)
    print(f"-> {out}（{U.mmss(len(take) / SR)}，{len(files)} 个文件：{describe(infos)}）")

    # warnings
    for i in infos:
        if i["clipped_samples"] > 20:
            print(f"[提醒] {i['name']} 有 {i['clipped_samples']} 个样本到顶（爆音）：离话筒远一点或调低录音音量重录会更好")
        if i["loudness_in"] is None:
            print(f"[提醒] {i['name']} 几乎没有声音")
        elif i["loudness_in"] < -45:
            print(f"[提醒] {i['name']} 很小声（{i['loudness_in']} LUFS）：底噪也会一起放大，最好离话筒近一点重录")
        if i["peak_capped"] and i["loudness_out"] is not None and i["loudness_out"] < TARGET_LUFS - 1.5:
            print(f"[提醒] {i['name']} 有个别特别响的瞬间（喷麦 / 碰到话筒？），音量只调到 {i['loudness_out']} LUFS："
                  "要和别的文件一样响就加 --limit on 重新导入")
    if not args.segment:
        est = sum(float(s.get("est_seconds") or C.est_seconds(s.get("tts_text") or s["text"])) for s in plan)
        total = len(take) / SR
        if total < 0.6 * est:
            print(f"[提醒] 录音一共 {U.mmss(total)}，比台本估计的 {U.mmss(est)} 短很多：是不是少了文件？")
    if U.voice_source(p) != "user":
        print("[提醒] episode.json 里没有 \"voice_source\": \"user\"：下面两步要加 --user-voice（或者把这一项写进 episode.json）")
    flag = "" if U.voice_source(p) == "user" else " --user-voice"
    print("下一步：")
    if args.segment:
        print(f"  python {HERE / 'segment_audio.py'} {p.ep}{flag}    （{args.segment} 用这次补录的，其余不变）")
    else:
        print(f"  python {HERE / 'select_takes.py'} {p.ep}{flag}     （用最新导入的这一版，整期打分）")
        print(f"  python {HERE / 'segment_audio.py'} {p.ep}{flag}    （按句切开、对齐字幕；报告列出可能读错 / 漏读的句子和跳过的重读）")


if __name__ == "__main__":
    main()
