"""Cut the selected chunk takes into one clip per script segment, and time the subtitle lines.

Inputs : selection.json, chunks.json, ../配音分段_v3.json
Outputs: segments/<id>.wav, ../制作/voice/durations.json, ../制作/voice/alignment.json, segments/report.txt

Method: faster-whisper word timestamps -> per-character times -> difflib alignment of the reference
(tts_text, normalised) to the recognised text -> segment boundaries -> cut at the quietest 10 ms frame
between the two segments -> trim silence, pad, fade.
"""
import difflib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
PROD = HERE.parent / "制作"
SR = 44100
from fetch_check import norm

spec = importlib.util.spec_from_file_location("bt", PROD / "build_timeline.py")
bt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bt)

chunks = json.loads((HERE / "chunks.json").read_text(encoding="utf-8"))
selection = json.loads((HERE / "selection.json").read_text(encoding="utf-8"))
segs_meta = {s["id"]: s for s in json.loads((HERE.parent / "配音分段_v3.json").read_text(encoding="utf-8"))}

from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8")


def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
                                   "-f", "f32le", "-"])
    return np.frombuffer(raw, dtype=np.float32).copy()


def save(path, x):
    x16 = (np.clip(x, -1, 1) * 32767).astype("<i2")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", str(path)],
                   input=x16.tobytes(), check=True)


def rms_frames(x, hop=441):
    n = len(x) // hop
    return np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)


def char_times(words):
    """Expand words to (normalised char, start, end) triples."""
    out = []
    for w in words:
        cs = norm(w.word)
        if not cs:
            continue
        step = (w.end - w.start) / len(cs)
        for i, ch in enumerate(cs):
            out.append((ch, w.start + i * step, w.start + (i + 1) * step))
    return out


def ref_to_hyp_map(ref, hyp):
    """For every ref index return an index into hyp (monotonic)."""
    m = [None] * len(ref)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_opcodes():
        if tag in ("equal", "replace"):
            for k in range(i1, i2):
                m[k] = min(j2 - 1, j1 + int((k - i1) * (j2 - j1) / max(1, i2 - i1)))
        elif tag == "delete":
            for k in range(i1, i2):
                m[k] = max(0, j1 - 1) if j1 > 0 else 0
    last = 0
    for k in range(len(m)):
        m[k] = last if m[k] is None else max(m[k], last)
        last = m[k]
    return m


def trim(x, thresh_db=-42):
    r = rms_frames(x, 220)
    peak = r.max()
    on = np.where(20 * np.log10(r / peak + 1e-12) > thresh_db)[0]
    if len(on) == 0:
        return x
    a = max(0, on[0] * 220 - int(0.03 * SR))
    b = min(len(x), (on[-1] + 1) * 220 + int(0.06 * SR))
    y = x[a:b].copy()
    f = int(0.01 * SR)
    y[:f] *= np.linspace(0, 1, f)
    y[-f:] *= np.linspace(1, 0, f)
    return y


def main():
    out_dir = HERE / "segments"
    out_dir.mkdir(exist_ok=True)
    (PROD / "voice").mkdir(exist_ok=True)
    durations, alignment, report = {}, {}, []
    for c in chunks:
        cid = c["chunk"]
        take = HERE / "raw" / selection[cid]["file"]
        x = load(take)
        seg_ids = c["ids"]
        ref_parts = [norm(segs_meta[i]["tts_text"].replace(" ", "")) for i in seg_ids]
        ref = "".join(ref_parts)
        words = []
        segs, _ = model.transcribe(str(take), language="zh", word_timestamps=True,
                                   initial_prompt="以下是普通话的句子。")
        for s in segs:
            words.extend(s.words or [])
        ct = char_times(words)
        hyp = "".join(ch for ch, _, _ in ct)
        mp = ref_to_hyp_map(ref, hyp) if hyp else [0] * len(ref)

        def t_start(ri):
            return ct[mp[min(ri, len(ref) - 1)]][1]

        def t_end(ri):
            return ct[mp[min(ri, len(ref) - 1)]][2]

        # boundaries between segments
        bounds = [0]
        pos = 0
        for p in ref_parts[:-1]:
            pos += len(p)
            bounds.append(pos)
        r = rms_frames(x)                                  # 10 ms frames
        cuts = [0.0]
        for b in bounds[1:]:
            a_t, b_t = t_end(b - 1), t_start(b)
            lo, hi = min(a_t, b_t) - 0.08, max(a_t, b_t) + 0.08
            i0, i1 = max(0, int(lo * 100)), min(len(r), int(hi * 100) + 1)
            cut = (i0 + int(np.argmin(r[i0:i1]))) / 100 if i1 > i0 else (a_t + b_t) / 2
            cuts.append(cut)
        cuts.append(len(x) / SR)

        for k, sid in enumerate(seg_ids):
            a, b = int(cuts[k] * SR), int(cuts[k + 1] * SR)
            raw_clip = x[a:b]
            clip = trim(raw_clip)
            # where the trimmed clip starts inside the chunk (same rule as trim()), for subtitle timing
            r_seg = rms_frames(raw_clip, 220)
            on = np.where(20 * np.log10(r_seg / (r_seg.max() + 1e-12) + 1e-12) > -42)[0]
            clip_start_in_chunk = cuts[k] + max(0, on[0] * 220 - int(0.03 * SR)) / SR if len(on) else cuts[k]
            save(out_dir / f"{sid}.wav", clip)
            dur = len(clip) / SR
            durations[sid] = round(dur, 3)

            # subtitle lines timed on the aligned speech
            text = segs_meta[sid]["text"]
            lines = bt.split_lines(text)
            seg_ref0 = bounds[k]
            seg_len = len(ref_parts[k])
            tot = sum(len(norm(l)) for l in lines) or 1
            acc, out = 0, []
            for li, ln in enumerate(lines):
                f0 = acc / tot
                acc += len(norm(ln))
                f1 = acc / tot
                ri0 = seg_ref0 + int(f0 * seg_len)
                ri1 = seg_ref0 + max(0, int(f1 * seg_len) - 1)
                s0 = 0.0 if li == 0 else t_start(ri0) - clip_start_in_chunk
                s1 = dur if li == len(lines) - 1 else t_end(ri1) - clip_start_in_chunk
                out.append(dict(text=ln, start=round(max(0.0, s0), 3), end=round(min(dur, max(s1, s0 + 0.3)), 3)))
            # make lines contiguous
            for i in range(1, len(out)):
                out[i]["start"] = out[i - 1]["end"]
            alignment[sid] = out
            report.append(f"{sid}\t{dur:.2f}s\t{text}")
        print(f"{cid}: {len(seg_ids)} segments, take {selection[cid]['file']}")

    (PROD / "voice" / "durations.json").write_text(json.dumps(durations, ensure_ascii=False, indent=1), encoding="utf-8")
    (PROD / "voice" / "alignment.json").write_text(json.dumps(alignment, ensure_ascii=False, indent=1), encoding="utf-8")
    (out_dir / "report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("total voice", round(sum(durations.values()), 1), "s")


if __name__ == "__main__":
    main()
