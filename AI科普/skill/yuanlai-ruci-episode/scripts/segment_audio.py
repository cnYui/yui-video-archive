"""Cut the selected chunk takes into one clip per script segment, and time the subtitle lines.

  python segment_audio.py <episode_dir> [--model small] [--series ...] [--user-voice]

Inputs : 配音/selection.json, 配音/chunks.json, 台本/配音分段.json
Outputs: 配音/segments/<id>.wav (44.1 kHz mono), 配音/segments/report.txt,
         制作/voice/durations.json {id: seconds}, 制作/voice/alignment.json {id: [{text, start, end}]}

AI voice (default; also what 《AI每日日报》 runs): faster-whisper word timestamps -> per-character times ->
difflib alignment of the reference (tts_text, normalised) to the recognised text -> segment boundaries -> cut
at the quietest 10 ms frame between two segments -> trim silence, pad, 10 ms fades. Subtitle lines use
build_timeline.split_lines so the timeline builder can retime them exactly.

The user's own recording (episode.json "voice_source": "user", or --user-voice; take = 配音/raw/C01_vN.wav from
import_voice.py): the reference is the subtitle text (what a person reads), aligned GLOBALLY and retake-tolerant
to the recognised characters (uservoice.py: false starts, sentences read twice, noise are skipped, and of two
complete readings the later one is used). Each sentence is cut from its own span (just before / after the
pauses around it, never into a neighbour's span), then the same trim(); a re-recorded sentence
(配音/raw/pickups/<id>_vN.wav, import_voice.py --segment) replaces the cut from the main take. report.txt (and
report.json) list every sentence's match (< 0.8 = 可能读错 / 漏读 -> 补录) and the skipped stretches (retakes /
noise > 0.8 s) with their times in the take and in the user's own file.
Next: build_timeline.py <episode_dir>
"""
import argparse
import difflib
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402
from build_timeline import split_lines  # noqa: E402
from fetch_check import ASR_PROMPT, load_model, norm  # noqa: E402

SR = 44100


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


def user_voice_episode(p):
    """episode.json "voice_source": "user" -> the user recorded the narration himself. Absent / "tts" / an unreadable
    episode.json = AI voice, exactly the old behaviour (《AI每日日报》 runs this path unattended)."""
    try:
        ep = C.load_json(p.episode_json, {})
    except (OSError, ValueError):
        return False
    return isinstance(ep, dict) and str(ep.get("voice_source") or "").strip().lower() == "user"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_common(ap)
    ap.add_argument("--model", default="small", help="faster-whisper 模型（默认 small）")
    ap.add_argument("--user-voice", action="store_true",
                    help="按用户自己的录音处理（不看 episode.json 的 voice_source；测试用）")
    args = ap.parse_args()
    p = C.Paths(args.episode_dir, args.series)
    if args.user_voice or user_voice_episode(p):
        return main_user(args, p)
    chunks = C.load_json(p.chunks)
    selection = C.load_json(p.selection)
    plan = C.load_json(p.voice_plan)
    if not chunks or selection is None or not plan:
        sys.exit("需要 配音/chunks.json、配音/selection.json、台本/配音分段.json（依次运行 chunk_voice → fetch_check → select_takes）")
    segs_meta = {s["id"]: s for s in plan}
    missing = [c["chunk"] for c in chunks if c["chunk"] not in selection]
    if missing:
        sys.exit(f"selection.json 里还没有这些批次的录音：{'、'.join(missing)}")
    stale = [i for c in chunks for i in c["ids"] if i not in segs_meta]
    if stale:
        sys.exit(f"chunks.json 和 配音分段.json 对不上（{stale[:5]}…）：台本改过就要重新 chunk_voice 和配音")

    model = load_model(args.model)
    out_dir = p.segments
    out_dir.mkdir(parents=True, exist_ok=True)
    p.prod_voice.mkdir(parents=True, exist_ok=True)
    durations, alignment, report = {}, {}, []
    for c in chunks:
        cid = c["chunk"]
        take = p.raw / selection[cid]["file"]
        x = load(take)
        seg_ids = c["ids"]
        ref_parts = [norm(segs_meta[i]["tts_text"].replace(" ", "")) for i in seg_ids]
        ref = "".join(ref_parts)
        words = []
        segs, _ = model.transcribe(str(take), language="zh", word_timestamps=True, initial_prompt=ASR_PROMPT)
        for s in segs:
            words.extend(s.words or [])
        ct = char_times(words)
        hyp = "".join(ch for ch, _, _ in ct)
        if not ct:
            sys.exit(f"{cid}: 语音识别没有结果（{take.name}），换一个版本")
        mp = ref_to_hyp_map(ref, hyp)

        def t_start(ri):
            return ct[mp[min(ri, len(ref) - 1)]][1]

        def t_end(ri):
            return ct[mp[min(ri, len(ref) - 1)]][2]

        # boundaries between segments
        bounds = [0]
        pos = 0
        for part in ref_parts[:-1]:
            pos += len(part)
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
            lines = split_lines(text)
            seg_ref0 = bounds[k]
            seg_len = len(ref_parts[k])
            tot = sum(len(norm(ln)) for ln in lines) or 1
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
            for i in range(1, len(out)):                   # make lines contiguous
                out[i]["start"] = out[i - 1]["end"]
            alignment[sid] = out
            report.append(f"{sid}\t{dur:.2f}s\t{text}")
        print(f"{cid}: {len(seg_ids)} segments, take {selection[cid]['file']}")

    C.write_json(p.durations, durations)
    C.write_json(p.alignment, alignment)
    (out_dir / "report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("total voice", round(sum(durations.values()), 1), "s")


# ---------------------------------------------------------------- the user's own recording (voice_source "user")
def trim_offset(raw_clip, thresh_db=-42):
    """Where trim() starts inside raw_clip (s), same rule as trim(): for the subtitle timing."""
    r = rms_frames(raw_clip, 220)
    if not len(r):
        return 0.0
    on = np.where(20 * np.log10(r / (r.max() + 1e-12) + 1e-12) > thresh_db)[0]
    return max(0, on[0] * 220 - int(0.03 * SR)) / SR if len(on) else 0.0


def user_lines(text, r_end, clip_start, dur):
    """Subtitle lines of one clip: split_lines(text), boundaries where the previous line's last character ends."""
    import uservoice as U
    lines = split_lines(text)
    if len(lines) == 1:
        return [dict(text=lines[0], start=0.0, end=round(dur, 3))]
    lens = [len(norm(ln)) for ln in lines]
    if r_end is None:                                   # nothing recognised: proportional to the text
        tot = sum(lens) or 1
        b = [0.0]
        for n_ in lens[:-1]:
            b.append(b[-1] + dur * n_ / tot)
        b.append(dur)
    else:
        b = U.line_bounds(lens, r_end, clip_start, dur)
    return [dict(text=ln, start=round(b[i], 3), end=round(b[i + 1], 3)) for i, ln in enumerate(lines)]


def said_in(words, a, b):
    """What the recogniser heard between a and b (s): the words whose middle lies inside."""
    return "".join(w for w, s_, e in words if a <= (s_ + e) / 2 < b).strip()


def cut_single(y, words, text, tts, asr_fn=None):
    """One sentence in a piece of audio y (a pickup file, or what follows a restart): align, cut at the pauses,
    trim, time the lines -> dict(clip, lines, match, complete, said, a, b, pauses, note) or None. When whisper's
    timing makes the cut reach over speech before / after the reading (pull_back / push_forward) and asr_fn is
    given, the reading without that speech is recognised on its own first; if it is complete, the speech was noise."""
    import uservoice as U
    hyp, t0, t1 = U.char_stream(words)
    if not hyp:
        return None
    ref, bounds, gap = U.build_reference([text])
    r2h, _, _ = U.align(ref, hyp, gap)
    U.prefer_later(ref, hyp, gap, r2h, bounds, t0, t1)
    sp = U.spans(ref, hyp, t0, t1, r2h, bounds)[0]
    if sp is None:
        return None
    fdb = U.frames_db(y)
    quiet, _ = U.quiet_mask(fdb)
    ps = U.pauses(quiet)
    a = U.cut_head(fdb, quiet, ps, sp, U.MIN_RUN_WIDE if sp["lead"] >= 2 else U.MIN_RUN)
    b = U.cut_tail(fdb, quiet, ps, sp, len(fdb), U.MIN_RUN_WIDE if sp["trail"] >= 2 else U.MIN_RUN)
    a2, b2 = U.pull_back(quiet, ps, sp, a, 0.0), U.push_forward(quiet, ps, sp, b, len(y) / SR, len(fdb))
    note = ""
    if (a2, b2) != (a, b) and asr_fn is not None:
        plain = cut_single(y[int(a * SR):int(b * SR)], asr_fn(y[int(a * SR):int(b * SR)]), text, tts)
        if plain and plain["complete"] and plain["match"] >= U.LOW_MATCH:
            plain["a"], plain["b"] = plain["a"] + a, plain["b"] + a
            plain["note"] = "旁边的声音不是这一句（噪音？），没有用"
            return plain
        note = "识别把句首 / 句尾的字标到了停顿里，按声音把前后那一小段算进来"
    a, b = a2, b2
    raw_clip = y[int(a * SR):int(b * SR)]
    clip = trim(raw_clip)
    _, r_end = U.ref_times(r2h, t0, t1, 0, len(ref))
    lines = user_lines(text, r_end, a + trim_offset(raw_clip), len(clip) / SR)
    said = "".join(w for w, s_, e in words if e > sp["start"] and s_ < sp["end"]).strip()
    return dict(clip=clip, lines=lines, match=U.match_ratio(ref, sp["hyp"], norm((tts or "").replace(" ", ""))),
                complete=U.complete(ref, hyp, r2h), said=said, a=a, b=b, pauses=ps, note=note)


def check_restart(y, a, b, all_pauses, text, tts, match, model, cache):
    """A long pause (>= 0.6 s) inside the clip y[a:b] may be "stop, read the sentence again" that the recogniser wrote
    down only once (it tends to drop repeated words and stretch a word over the pause). The audio after each long
    pause (last first) is recognised on its own: when it is a complete reading (starts again from the sentence's
    first character, has the ending, match >= max(0.8, match - 0.05)) the clip becomes that part -- a natural long
    pause after "所以，" is not taken for a restart, since what follows it does not start the sentence again; else,
    when the part before the first long pause is complete, that part. Returns (result of cut_single with a / b in
    y's time, what happened) or (None, "")."""
    import uservoice as U
    lp = U.long_pauses(all_pauses, a, b)
    if not lp:
        return None, ""
    need = max(U.LOW_MATCH, match - 0.05)
    for r in reversed(lp):
        p = max(a, r[1] / 100 - 0.15)
        piece = y[int(p * SR):int(b * SR)]
        res = cut_single(piece, U.asr_array(piece, cache, model)["words"], text, tts)
        if res and res["complete"] and res["match"] >= need:
            res["a"], res["b"] = res["a"] + p, res["b"] + p
            return res, (f"{r[0] / 100:.1f}–{r[1] / 100:.1f} s 的停顿后是完整的一遍，只用这一遍"
                         "（前面是读了一半的重读或噪音，识别只写了一遍）")
    q = min(b, lp[0][0] / 100 + 0.15)
    piece = y[int(a * SR):int(q * SR)]
    res = cut_single(piece, U.asr_array(piece, cache, model)["words"], text, tts)
    if res and res["complete"] and res["match"] >= need:
        res["a"], res["b"] = res["a"] + a, res["b"] + a
        return res, f"{lp[0][0] / 100:.1f} s 的停顿之后是没读完的重读，只用前面完整的一遍"
    return None, ""


def cut_pickup(path, text, tts, model, cache):
    """A re-recorded sentence (import_voice.py --segment) -> (result dict, note) or (None, why)."""
    import uservoice as U
    y = load(path)
    res = cut_single(y, U.asr_words(path, cache, model)["words"], text, tts,
                     lambda piece: U.asr_array(piece, cache, model)["words"])
    if res is None:
        return None, "没找到这一句（没有识别出和台本对得上的字）"
    fixed, note = check_restart(y, res["a"], res["b"], res["pauses"], text, tts, res["match"], model, cache)
    return (fixed, note) if fixed else (res, res.get("note", ""))


def main_user(args, p):
    import time
    import uservoice as U
    chunks = C.load_json(p.chunks)
    selection = C.load_json(p.selection)
    plan = C.load_json(p.voice_plan)
    if not chunks or selection is None or not plan:
        sys.exit("需要 配音/chunks.json、配音/selection.json、台本/配音分段.json"
                 "（自己录音：依次运行 chunk_voice --whole → import_voice → select_takes）")
    segs_meta = {s["id"]: s for s in plan}
    missing = [c["chunk"] for c in chunks if c["chunk"] not in selection]
    if missing:
        sys.exit(f"selection.json 里还没有这些批次的录音：{'、'.join(missing)}（先 import_voice.py，再 select_takes.py）")
    stale = [i for c in chunks for i in c["ids"] if i not in segs_meta]
    if stale:
        sys.exit(f"chunks.json 和 配音分段.json 对不上（{stale[:5]}…）：台本改过就要重新 chunk_voice --whole，"
                 "改了的句子重新录（或补录）")
    wrong = [c["chunk"] for c in chunks if not str(selection[c["chunk"]].get("file", "")).lower().endswith(".wav")]
    if wrong:
        sys.exit(f"selection.json 里 {'、'.join(wrong)} 选的不是自己的录音（{selection[wrong[0]].get('file')}，AI 配音？）："
                 "先 import_voice.py 导入录音，再 select_takes.py（episode.json 要有 \"voice_source\": \"user\"，或加 --user-voice）")
    here = Path(__file__).resolve().parent
    fix_cmd = f"python {here / 'import_voice.py'} {p.ep} --segment <段号> <文件>"
    out_dir = p.segments
    out_dir.mkdir(parents=True, exist_ok=True)
    p.prod_voice.mkdir(parents=True, exist_ok=True)
    cache = p.raw / "asr_words.json"
    picks = U.pickups(p.raw)
    known = {i for c in chunks for i in c["ids"]}
    for sid in sorted(set(picks) - known):
        print(f"[提醒] 补录 {picks[sid][1].name} 的段号台本里没有，不用")
    durations, alignment, rows, flagged, skipped, used_picks, inner, restarts = {}, {}, [], [], [], [], [], []
    report_json = dict(mode="user", segments={}, flagged=[], skipped=[], takes=[])
    for c in chunks:
        cid = c["chunk"]
        take = p.raw / selection[cid]["file"]
        manifest = C.load_json(take.with_suffix(".json"), {}) or {}
        sources = manifest.get("sources") or []

        def where(t0_, t1_=None, _src=sources):
            s = f"{U.mmss(t0_)}" + (f"–{U.mmss(t1_)}" if t1_ is not None else "")
            for f in _src:
                if f["start"] - 0.5 <= t0_ < f["start"] + f["duration"] + 0.5:
                    return s + f"（{f['name']} {U.mmss(max(0.0, t0_ - f['start']))}）"
            return s

        x = load(take)
        seg_ids = c["ids"]
        texts = [segs_meta[i]["text"] for i in seg_ids]
        ref, bounds, gap = U.build_reference(texts)
        asr = U.asr_words(take, cache, args.model)
        words = asr["words"]
        hyp, t0, t1 = U.char_stream(words)
        if not hyp:
            sys.exit(f"{cid}: 语音识别没有结果（{take.name}）：录音是空的？")
        r2h, _, _ = U.align(ref, hyp, gap)
        moved = U.prefer_later(ref, hyp, gap, r2h, bounds, t0, t1)
        sp = U.spans(ref, hyp, t0, t1, r2h, bounds)
        aligned = np.zeros(len(hyp), dtype=bool)
        aligned[r2h[r2h >= 0]] = True
        heard = float((r2h >= 0).mean())
        if heard < 0.5:
            sys.exit(f"{cid}: 录音里只找到台本 {heard:.0%} 的字（{take.name}）：录的是不是别的稿子 / 别的期？")
        fdb = U.frames_db(x)
        quiet, _thr = U.quiet_mask(fdb)
        n_frames = len(fdb)
        total = len(x) / SR

        def need(n_missing):
            return U.MIN_RUN_WIDE if n_missing >= 2 else U.MIN_RUN

        present = [k for k, s in enumerate(sp) if s]
        ps = U.pauses(quiet)
        cuts = {k: [0.0, total] for k in present}
        cuts[present[0]][0] = U.cut_head(fdb, quiet, ps, sp[present[0]], need(sp[present[0]]["lead"]))
        for ka, kb in zip(present, present[1:]):
            e, s = U.cut_between(fdb, quiet, ps, sp[ka], sp[kb], need(sp[ka]["trail"]), need(sp[kb]["lead"]))
            cuts[ka][1], cuts[kb][0] = e, s
        cuts[present[-1]][1] = U.cut_tail(fdb, quiet, ps, sp[present[-1]], n_frames, need(sp[present[-1]]["trail"]))

        def asr_fn(piece):
            return U.asr_array(piece, cache, args.model)["words"]

        # final clip of every reading: whisper-timing fixes (checked), then "stopped and read it again"
        final, notes = {}, {}
        for i, k in enumerate(present):
            sid = seg_ids[k]
            text, tts = segs_meta[sid]["text"], segs_meta[sid].get("tts_text")
            a, b = bounds[k]
            ca, cb = cuts[k]
            lo = final[present[i - 1]]["b"] if i else 0.0
            hi = cuts[present[i + 1]][0] if i + 1 < len(present) else total
            ca2 = U.pull_back(quiet, ps, sp[k], ca, lo)
            cb2 = U.push_forward(quiet, ps, sp[k], cb, hi, n_frames)
            res = None
            if (ca2, cb2) != (ca, cb):
                plain = cut_single(x[int(ca * SR):int(cb * SR)], asr_fn(x[int(ca * SR):int(cb * SR)]), text, tts)
                if plain and plain["complete"] and plain["match"] >= U.LOW_MATCH:
                    plain["a"], plain["b"] = plain["a"] + ca, plain["b"] + ca
                    res = plain
                    notes[k] = "旁边的声音不是这一句（噪音？），没有用"
                else:
                    ca, cb = ca2, cb2
                    notes[k] = "识别把句首 / 句尾的字标到了停顿里，按声音把前后那一小段算进来"
            if res is None:
                match = U.match_ratio(ref[a:b], sp[k]["hyp"], norm(str(tts or "").replace(" ", "")))
                fixed, note = check_restart(x, ca, cb, ps, text, tts, match, args.model, cache)
                if fixed:
                    res, notes[k] = fixed, note
            final[k] = dict(a=res["a"] if res else ca, b=res["b"] if res else cb, res=res)

        # sentences not found at all: share the stretch between the neighbours' clips, in proportion to the text
        lost = {}
        k = 0
        while k < len(seg_ids):
            if sp[k]:
                k += 1
                continue
            k1 = k
            while k1 < len(seg_ids) and not sp[k1]:
                k1 += 1
            lo = final[k - 1]["b"] if k > 0 else 0.0
            hi = final[k1]["a"] if k1 < len(seg_ids) else total
            lens = [max(1, bounds[i][1] - bounds[i][0]) for i in range(k, k1)]
            acc = lo
            for i, n_ in zip(range(k, k1), lens):
                span = (hi - lo) * n_ / sum(lens)
                lost[i] = (acc, acc + span)
                acc += span
            k = k1

        # skipped stretches (between the final clips of two neighbouring readings, and before / after all of them)
        edges = [(None, present[0], 0.0, final[present[0]]["a"])]
        edges += [(ka, kb, final[ka]["b"], final[kb]["a"]) for ka, kb in zip(present, present[1:])]
        edges.append((present[-1], None, final[present[-1]]["b"], total))
        ins_idx = np.where(~aligned)[0]
        for ka, kb, ga, gb in edges:
            ext = U.sound_extent(quiet, ga, gb)
            if not ext:
                continue
            said = said_in(words, ga, gb)
            n_ins = int(np.sum((t0[ins_idx] >= ga) & (t0[ins_idx] < gb))) if len(ins_idx) else 0
            if ext[1] - ext[0] >= U.SKIP_REPORT or n_ins >= 4:
                between = (f"{seg_ids[ka]} 之后" if kb is None else f"{seg_ids[kb]} 之前" if ka is None
                           else f"{seg_ids[ka]} 和 {seg_ids[kb]} 之间")
                skipped.append(dict(chunk=cid, start=round(ext[0], 2), end=round(ext[1], 2), where=where(*ext),
                                    between=between, said=said))

        for k, sid in enumerate(seg_ids):
            meta = segs_meta[sid]
            text = meta["text"]
            tts_n = norm(str(meta.get("tts_text") or "").replace(" ", ""))
            a, b = bounds[k]
            clip = None
            if sid in picks:
                res, why = cut_pickup(picks[sid][1], text, meta.get("tts_text"), args.model, cache)
                if res:
                    clip, lines, ratio, said = res["clip"], res["lines"], res["match"], res["said"]
                    src, pos = f"补录 {picks[sid][1].name}", f"补录里 {U.mmss(res['a'])}–{U.mmss(res['b'])}"
                    used_picks.append(sid)
                    if why:
                        restarts.append(dict(id=sid, what=f"补录：{why}"))
                else:
                    print(f"[提醒] {sid} 的补录 {picks[sid][1].name} {why}，还是用主录音里的")
            if clip is None and sp[k]:
                fk = final[k]
                ca, cb = fk["a"], fk["b"]
                if fk["res"]:
                    clip, lines, ratio, said = fk["res"]["clip"], fk["res"]["lines"], fk["res"]["match"], fk["res"]["said"]
                else:
                    raw_clip = x[int(ca * SR):int(cb * SR)]
                    clip = trim(raw_clip)
                    _, r_end = U.ref_times(r2h, t0, t1, a, b)
                    lines = user_lines(text, r_end, ca + trim_offset(raw_clip), len(clip) / SR)
                    ratio = U.match_ratio(ref[a:b], sp[k]["hyp"], tts_n)
                    said = said_in(words, ca, cb)
                    extra = U.inner_extra(hyp, aligned, sp[k]["j0"], sp[k]["j1"], ref[a:b])
                    if extra and ratio >= U.LOW_MATCH:
                        inner.append(dict(id=sid, extra=extra, said=said, text=text))
                if k in notes:
                    restarts.append(dict(id=sid, what=f"{where(ca, cb)}：{notes[k]}"))
                src, pos = f"{take.stem}", where(ca, cb)
            elif clip is None:                              # not found in the take
                lo, hi = lost[k]
                ext = U.sound_extent(quiet, lo, hi)
                if ext and ext[1] - ext[0] >= 0.25:
                    lo, hi = max(lo, ext[0] - 0.1), min(hi, ext[1] + 0.1)
                raw_clip = x[int(lo * SR):int(hi * SR)]
                clip = trim(raw_clip) if len(raw_clip) >= int(0.3 * SR) else np.zeros(int(0.5 * SR), dtype=np.float32)
                lines = user_lines(text, None, 0.0, len(clip) / SR)
                ratio, said = 0.0, said_in(words, lo, hi)
                src, pos = f"{take.stem}（没找到）", where(lo, hi)
            save(out_dir / f"{sid}.wav", clip)
            dur = len(clip) / SR
            durations[sid] = round(dur, 3)
            alignment[sid] = lines
            rows.append(f"{sid}\t{dur:.2f}s\t{ratio:.2f}\t{pos}\t{src}\t{text}")
            report_json["segments"][sid] = dict(dur=round(dur, 3), match=round(ratio, 3), source=src, where=pos)
            if ratio < U.LOW_MATCH:
                what = ("没找到这一句（漏读？）" + (f"这里识别到「{said}」" if said else "")) if ratio == 0 \
                    else f"这一段识别成「{said}」"
                flagged.append(dict(id=sid, match=round(ratio, 3), what=what, text=text))
        report_json["takes"].append(dict(chunk=cid, file=take.name, duration=round(total, 2), heard=round(heard, 3),
                                         sources=[f["name"] for f in sources],
                                         later_reading=[seg_ids[k] for k in moved]))
        print(f"{cid}: {len(seg_ids)} 句，录音 {take.name}（{U.mmss(total)}），识别出台本 {heard:.0%} 的字"
              + (f"；补录 {len(used_picks)} 句（{'、'.join(used_picks)}）" if used_picks else ""))

    C.write_json(p.durations, durations)
    C.write_json(p.alignment, alignment)
    report_json["flagged"], report_json["skipped"], report_json["inner_extra"] = flagged, skipped, inner
    report_json["restarts"] = restarts
    C.write_json(out_dir / "report.json", report_json)
    rep = [f"# 切句报告：用户自己的录音（segment_audio.py，{time.strftime('%Y-%m-%d %H:%M')}）",
           "# 匹配 = 这一句识别出来的字和台本的吻合度（0–1，和台本字幕、TTS 读法两种写法比，取高的）；"
           f"< {U.LOW_MATCH} 可能读错 / 漏读",
           "# 段号\t时长\t匹配\t在录音里的位置（原文件里的位置）\t来源\t字幕"] + rows
    rep += ["", f"## 可能读错 / 漏读（匹配 < {U.LOW_MATCH}）：{len(flagged)} 句。先听；要重录就单录这一句，然后",
            f"##   {fix_cmd}", "##   再跑一次 segment_audio.py（补录的会替换主录音里的这一句）"]
    rep += [f"{f['id']}\t{f['match']:.2f}\t{f['what']}\t台本：{f['text']}" for f in flagged] or ["（没有）"]
    rep += ["", f"## 按声音修正过切点的句子（句中停下重读、识别的时间标错了、旁边有噪音）：{len(restarts)} 句，听一下"]
    rep += [f"{x['id']}\t{x['what']}" for x in restarts] or ["（没有）"]
    rep += ["", f"## 句子里多出来的字（句中停下重读？）：{len(inner)} 句，听一下；有问题就补录这一句"]
    rep += [f"{x['id']}\t多出「{'」「'.join(x['extra'])}」\t识别成：{x['said']}" for x in inner] or ["（没有）"]
    rep += ["", f"## 跳过的声音（重读、读错的半句、噪音；≥ {U.SKIP_REPORT} s 或识别出 4 个字以上）：{len(skipped)} 段，"
            "听一下确认里面没有要用的句子"]
    rep += [f"{s['where']}\t{s['end'] - s['start']:.1f}s\t{s['between']}\t"
            + (f"识别到：{s['said']}" if s["said"] else "（没识别出文字：噪音 / 咳嗽 / 杂音？）") for s in skipped] or ["（没有）"]
    (out_dir / "report.txt").write_text("\n".join(rep) + "\n", encoding="utf-8")
    if flagged:
        print(f"可能读错 / 漏读 {len(flagged)} 句（匹配 < {U.LOW_MATCH}），建议补录：")
        for f in flagged:
            print(f"  {f['id']}  {f['match']:.2f}  {f['what']}")
        print(f"  补录：{fix_cmd}")
    else:
        print(f"每一句的匹配都 ≥ {U.LOW_MATCH}")
    if restarts:
        print(f"按声音修正过切点的 {len(restarts)} 句（句中重读 / 时间标错 / 噪音，听一下）：" + "、".join(x["id"] for x in restarts))
    if inner:
        print(f"句子里多出来的字 {len(inner)} 句（句中停下重读？听一下）：" + "、".join(x["id"] for x in inner))
    if skipped:
        print(f"跳过的声音 {len(skipped)} 段（重读 / 噪音，已经不在任何一句里）：")
        for s in skipped:
            print(f"  {s['where']}  {s['end'] - s['start']:.1f}s  {s['between']}  {s['said'][:30] or '（无文字）'}")
    print(f"-> {out_dir / 'report.txt'}")
    print("total voice", round(sum(durations.values()), 1), "s")
    print(f"下一步：试听 配音/segments 里的句子（重点听上面列出来的），没问题就 build_timeline.py {p.ep}")


if __name__ == "__main__":
    main()
