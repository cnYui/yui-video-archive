"""Helpers for episodes the user voices himself (episode.json "voice_source": "user"); not a command itself.

《原LAI如此》 is voiced by the user from 2026-09-28 on (user: 「原LAI如此配音之后需要我来配音，ai配音用来做每日日报」).
import_voice.py, and select_takes.py / segment_audio.py in user mode (voice_source "user" or --user-voice), use
this module; the AI-voice path of those two scripts (also run unattended every day by 《AI每日日报》) never imports it.

Files under 配音/:
  raw/C01_v<N>.wav (+ .json)            one imported take: the user's files concatenated (import_voice.py) + manifest
  raw/pickups/<id>_v<N>.wav (+ .json)   a re-recording of one sentence; segment_audio uses the newest N
  raw/asr_words.json                    faster-whisper word timings, cached by file hash + model + ASR_VERSION

Alignment (segment_audio.py): global alignment (Needleman-Wunsch) of the whole reference = normalised subtitle
text, against the recognised character stream. Recognised characters that are not in the reference (false
starts, sentences read twice, coughs, noise words) are cheap to skip at a sentence boundary, dearer at a comma,
dearest inside a phrase, so a retake ends up between two sentences; on equal scores the traceback prefers the
diagonal, which picks the LATER of two complete readings. Rows are vectorised with numpy: with a constant gap
cost per row, the insertion chain is max_k<=j (T[k] + (j-k) g) = j g + cummax(T - j g), so ~2000 x 2500 cells take
well under a second. prefer_later() then makes "the last complete reading wins" hold also when the later reading
has a recognition slip.

Cutting (segment_audio.py): 10 ms frames below the recording's own pause level (noise floor + 6 dB, at least
25 dB under the speech) are pause. A sentence's clip starts just before the last pause and ends just after the
first pause around its reading, so nothing of a skipped retake is inside it; whisper often stretches or shifts the
word next to a pause over / into the pause, so the cut trusts the inner edges of the reading and checks the audio
(start_anchor / end_anchor, pull_back / push_forward). A pause of >= 0.6 s inside one reading can be "stop, read
the sentence again" that whisper wrote down once: segment_audio.check_restart() re-recognises the part after it.
Then the AI path's trim() (-42 dB re. the clip's peak, 30 / 60 ms pads, 10 ms fades).
"""
import difflib
import hashlib
import re
import sys
import time
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402
from fetch_check import ASR_PROMPT, load_model, norm  # noqa: E402

SR = 44100
HOP = 441                        # 10 ms analysis frames
ASR_VERSION = "uv1"              # part of the ASR cache key: bump when ASR_OPTS change
ASR_OPTS = dict(language="zh", word_timestamps=True, initial_prompt=ASR_PROMPT)
LOW_MATCH = 0.8                  # per-sentence match below this -> 可能读错 / 漏读
SKIP_REPORT = 0.8                # skipped sound (retake / noise) at least this long is listed in the report

# alignment scores (integers, so ties are exact and the traceback's preference decides them). A substitution costs
# more than leaving the reference char out plus skipping a recognised char at a sentence boundary (-8 -1), so a
# sentence that was not read is left out instead of being matched onto retake junk; inside a phrase (-8 -6) a
# recognition slip stays a substitution and keeps the timing continuous.
MATCH, MISMATCH, DELETE = 10, -12, -8
GAP_SEG, GAP_PUNCT, GAP_IN = 0, 1, 2
INSERT = {GAP_SEG: -1, GAP_PUNCT: -3, GAP_IN: -6}
DIAG, UP, LEFT = 0, 1, 2
BREAKS = set("，。！？；：、…—,!?;:")


# ---------------------------------------------------------------- mode, files
def voice_source(p):
    """episode.json "voice_source" ("user" / "tts"); absent or unreadable = "tts"."""
    try:
        ep = C.load_json(p.episode_json, {})
    except (OSError, ValueError):
        return "tts"
    v = ep.get("voice_source") if isinstance(ep, dict) else None
    return str(v).strip().lower() if v else "tts"


def takes(raw, cid="C01"):
    """User takes [(N, path)] of a chunk, oldest first (配音/raw/C01_v<N>.wav)."""
    out = []
    for f in Path(raw).glob(f"{cid}_v*.wav"):
        m = re.fullmatch(rf"{re.escape(cid)}_v(\d+)\.wav", f.name, re.I)
        if m:
            out.append((int(m.group(1)), f))
    return sorted(out)


def next_version(folder, stem):
    """Next free N for <stem>_v<N>.* in folder (counts .wav, .mp3 and .json, so an AI take C01_v1.mp3 is never
    shadowed by a user take C01_v1.wav)."""
    n = 0
    for f in Path(folder).glob(f"{stem}_v*.*"):
        m = re.fullmatch(rf"{re.escape(stem)}_v(\d+)\.[A-Za-z0-9]+", f.name)
        if m:
            n = max(n, int(m.group(1)))
    return n + 1


def pickups(raw):
    """{segment id: (N, path)} newest re-recording of each sentence (配音/raw/pickups/<id>_v<N>.wav)."""
    best = {}
    for f in (Path(raw) / "pickups").glob("*_v*.wav"):
        m = re.fullmatch(r"(.+)_v(\d+)\.wav", f.name)
        if m:
            sid, n = m.group(1), int(m.group(2))
            if sid not in best or n > best[sid][0]:
                best[sid] = (n, f)
    return best


def mmss(t):
    m, s = divmod(max(0.0, float(t)), 60)
    return f"{int(m)}:{s:04.1f}"


# ---------------------------------------------------------------- ASR (cached)
_MODELS = {}


def asr_words(path, cache_path, model_name="small", log=print):
    """faster-whisper with word timestamps -> {"text", "words": [[word, start, end], ...]}; cached by file hash."""
    path = Path(path)
    key = f"{hashlib.md5(path.read_bytes()).hexdigest()}|{model_name}|{ASR_VERSION}"
    cache = C.load_json(cache_path, {}) or {}
    if key in cache:
        return cache[key]
    if model_name not in _MODELS:
        _MODELS[model_name] = load_model(model_name)
    log(f"  语音识别 {path.name}（faster-whisper {model_name}，CPU，大约是录音时长的 1/3）…")
    t0 = time.time()
    segs, _ = _MODELS[model_name].transcribe(str(path), **ASR_OPTS)
    words, text = [], []
    for s in segs:
        text.append(s.text)
        for w in s.words or []:
            words.append([w.word, round(float(w.start), 3), round(float(w.end), 3)])
    res = dict(file=path.name, text="".join(text), words=words, seconds=round(time.time() - t0, 1))
    cache = C.load_json(cache_path, {}) or {}
    cache[key] = res
    C.write_json(cache_path, cache)
    return res


def asr_array(y, cache_path, model_name="small"):
    """faster-whisper on a piece of audio (float32, 44.1 kHz; resampled to 16 kHz with ffmpeg); same result dict
    as asr_words, cached by the samples' hash. Used for the restart check in segment_audio.py."""
    import subprocess
    y16 = np.frombuffer(subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-ar", "16000", "-f", "f32le", "-"],
        input=np.asarray(y, dtype=np.float32).tobytes(), capture_output=True, check=True).stdout, dtype=np.float32)
    key = f"{hashlib.md5(y16.tobytes()).hexdigest()}|{model_name}|{ASR_VERSION}|piece"
    cache = C.load_json(cache_path, {}) or {}
    if key in cache:
        return cache[key]
    if model_name not in _MODELS:
        _MODELS[model_name] = load_model(model_name)
    segs, _ = _MODELS[model_name].transcribe(y16, **ASR_OPTS)
    words, text = [], []
    for s_ in segs:
        text.append(s_.text)
        for w in s_.words or []:
            words.append([w.word, round(float(w.start), 3), round(float(w.end), 3)])
    res = dict(file="(piece)", text="".join(text), words=words)
    cache = C.load_json(cache_path, {}) or {}
    cache[key] = res
    C.write_json(cache_path, cache)
    return res


def char_stream(words):
    """Words -> (normalised chars as one string, start times, end times); a word's time is shared evenly."""
    chars, t0, t1 = [], [], []
    for w, s, e in words:
        cs = norm(w)
        if not cs:
            continue
        step = (e - s) / len(cs)
        for i, ch in enumerate(cs):
            chars.append(ch)
            t0.append(s + i * step)
            t1.append(s + (i + 1) * step)
    return "".join(chars), np.array(t0, dtype=float), np.array(t1, dtype=float)


# ---------------------------------------------------------------- reference
def ref_of(text):
    """Normalised characters of a subtitle text + the positions inside it that follow a pause mark (，。？ …)."""
    chars, brk = [], set()
    for k, c in enumerate(text):
        nc = norm(c)
        if nc:
            chars.extend(nc)
        elif c in BREAKS or (c == "." and not (k + 1 < len(text) and text[k + 1].isdigit())):
            if chars:
                brk.add(len(chars))
    brk.discard(len(chars))
    return "".join(chars), brk


def build_reference(texts):
    """texts: subtitle texts in reading order -> (ref, [(a, b) per text], gap kind per position 0..len(ref))."""
    ref, bounds, marks = [], [], []
    for t in texts:
        s, brk = ref_of(t)
        a = len(ref)
        ref.extend(s)
        bounds.append((a, len(ref)))
        marks.extend(a + x for x in brk)
    gap = np.full(len(ref) + 1, GAP_IN, dtype=np.int8)
    for x in marks:
        gap[x] = GAP_PUNCT
    for a, b in bounds:
        gap[a] = GAP_SEG
        gap[b] = GAP_SEG
    return "".join(ref), bounds, gap


# ---------------------------------------------------------------- alignment
def align(ref, hyp, gap):
    """Global alignment of ref (n chars) to hyp (m chars), insertion cost per ref gap position.
    Returns (r2h: hyp index per ref char or -1, ins_at: for every hyp char the ref gap position it was skipped at
    or -1 when it is aligned, score)."""
    n, m = len(ref), len(hyp)
    alphabet = {c: k for k, c in enumerate(sorted(set(ref) | set(hyp)))}
    h = np.fromiter((alphabet[c] for c in hyp), dtype=np.int32, count=m)
    ins = np.array([INSERT[int(g)] for g in gap], dtype=np.int64)
    jj = np.arange(m + 1, dtype=np.int64)
    S = jj * ins[0]
    D = np.empty((n + 1, m + 1), dtype=np.int8)
    D[0, :] = LEFT
    for i in range(1, n + 1):
        sub = np.where(h == alphabet[ref[i - 1]], MATCH, MISMATCH)
        up = S + DELETE
        diag = S[:-1] + sub
        take_diag = diag >= up[1:]                      # ties -> diagonal
        T = up.copy()
        T[1:] = np.where(take_diag, diag, up[1:])
        g = ins[i]
        best = np.maximum.accumulate(T - jj * g) + jj * g
        row = np.full(m + 1, UP, dtype=np.int8)
        row[1:][take_diag] = DIAG
        row[best > T] = LEFT                            # strict: a tie keeps the diagonal / up move
        D[i] = row
        S = best
    r2h = np.full(n, -1, dtype=np.int64)
    ins_at = np.full(m, -1, dtype=np.int64)
    i, j = n, m
    while i > 0 or j > 0:
        d = D[i, j]
        if d == DIAG:
            r2h[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif d == UP:
            i -= 1
        else:
            ins_at[j - 1] = i
            j -= 1
    return r2h, ins_at, int(S[m])


def complete(ref_k, hyp, r2):
    """Is this a complete reading of the sentence ref_k (r2: hyp index per ref char, -1 = not found)?
    It must start at the sentence's start (the first character found, or -- a recognition slip on it -- the next
    two found with something recognised before them) and end at its end (half of the last third found). A reading
    that begins after a pause in the middle of the sentence is not complete, however well the rest matches."""
    n = len(ref_k)
    if n == 0:
        return False
    ok = np.array([r2[i] >= 0 and hyp[int(r2[i])] == ref_k[i] for i in range(n)])
    if not ok.any():
        return False
    third = max(1, n // 3)
    ends = ok[n - third:].mean() >= 0.5
    first = int(r2[np.where(r2 >= 0)[0][0]])
    starts = bool(ok[0]) or (n >= 3 and bool(ok[1] and ok[2]) and first > 0)
    return bool(starts and ends)


def prefer_later(ref, hyp, gap, r2h, bounds, t0=None, t1=None):
    """"The last complete reading wins", also when the later reading has a recognition slip (the alignment alone
    would then keep the cleaner earlier one): for every sentence, re-align it inside the skipped stretch that follows
    its reading (up to the next sentence's reading). It takes over when it is complete: match >= min(0.8, current
    - 0.05), complete() (starts at the sentence's start -- a restart from a comma does not count -- and has the
    ending, which a false start lacks), and (with times) 0.5-2.5x as long as the current reading. Repeats, so the
    third of three readings wins. Updates r2h in place; returns the indices of the texts that moved."""
    moved = []
    n = len(ref)
    for k, (a, b) in enumerate(bounds):
        if b <= a:
            continue
        ref_k = ref[a:b]
        gk = gap[a:b + 1].copy()
        gk[0] = gk[-1] = GAP_SEG
        while True:
            idx = r2h[a:b]
            hit = idx[idx >= 0]
            if len(hit) == 0:
                break
            lo = int(hit[-1]) + 1
            later = r2h[b:n]
            later = later[later >= 0]
            hi = int(later[0]) if len(later) else len(hyp)
            if hi - lo < max(2, int(0.6 * (b - a))):
                break
            r2, _, _ = align(ref_k, hyp[lo:hi], gk)
            h2 = np.where(r2 >= 0)[0]
            if len(h2) == 0:
                break
            j0, j1 = lo + int(r2[h2[0]]), lo + int(r2[h2[-1]])
            new = match_ratio(ref_k, hyp[j0:j1 + 1])
            cur = match_ratio(ref_k, hyp[int(hit[0]):int(hit[-1]) + 1])
            ok = new >= min(LOW_MATCH, cur - 0.05) and complete(ref_k, hyp[lo:hi], r2)
            if ok and t0 is not None:
                d_new, d_cur = t1[j1] - t0[j0], t1[int(hit[-1])] - t0[int(hit[0])]
                ok = 0.5 * d_cur <= d_new <= 2.5 * d_cur + 0.3
            if not ok:
                break
            r2h[a:b] = np.where(r2 >= 0, r2 + lo, -1)
            moved.append(k)
    return moved


def spans(ref, hyp, t0, t1, r2h, bounds):
    """Per text: None (nothing recognised) or dict(j0, j1, start, end, in_start, in_end, hyp, lead, trail) where
    j0..j1 is the aligned hyp range, start/end its time, in_start / in_end the end of its first and the start of its
    last recognised character (whisper often stretches the word next to a pause over the pause, so these inner
    edges are what the cutting trusts), lead / trail = reference chars before the first / after the last aligned
    one (not heard)."""
    out = []
    for a, b in bounds:
        idx = r2h[a:b]
        hit = np.where(idx >= 0)[0]
        if len(hit) == 0:
            out.append(None)
            continue
        j0, j1 = int(idx[hit[0]]), int(idx[hit[-1]])
        out.append(dict(j0=j0, j1=j1, start=float(t0[j0]), end=float(t1[j1]), in_start=float(t1[j0]),
                        in_end=float(t0[j1]), hyp=hyp[j0:j1 + 1], lead=int(hit[0]), trail=int(b - a - 1 - hit[-1])))
    return out


def inner_extra(hyp, aligned, j0, j1, ref_k, min_run=3):
    """Runs of >= min_run recognised characters inside one reading that are not aligned to the sentence but repeat
    its own words (>= 60 % of them occur in the sentence): a restart in the middle of the sentence ("不写文张，不写
    文章"). Other extra characters are mostly how the recogniser spelled a name or a number, and are not listed."""
    own = set(ref_k)
    out, run = [], []
    for j in list(range(j0, j1 + 1)) + [None]:
        if j is not None and not aligned[j]:
            run.append(hyp[j])
            continue
        if len(run) >= min_run and sum(c in own for c in run) >= 0.6 * len(run):
            out.append("".join(run))
        run = []
    return out


def match_ratio(ref_k, hyp_k, tts_k=None):
    """0-1 similarity of one sentence to what was recognised in its span; the better of the subtitle text and the
    TTS spelling (someone may say 杰夫 for Jev, 一百九十三点六 for 193.6)."""
    if not hyp_k:
        return 0.0
    r = difflib.SequenceMatcher(None, ref_k, hyp_k, autojunk=False).ratio()
    if tts_k:
        r = max(r, difflib.SequenceMatcher(None, tts_k, hyp_k, autojunk=False).ratio())
    return r


def ref_times(r2h, t0, t1, a, b):
    """Start / end time of every reference char a..b-1, interpolated over chars that were not recognised."""
    idx = r2h[a:b]
    k = np.where(idx >= 0)[0]
    pos = np.arange(b - a)
    if len(k) == 0:
        return None, None
    s = np.interp(pos, k, t0[idx[k]])
    e = np.interp(pos, k, t1[idx[k]])
    return s, e


# ---------------------------------------------------------------- cutting
def frames_db(x):
    n = len(x) // HOP
    r = np.sqrt(np.mean(x[: n * HOP].reshape(n, HOP) ** 2, axis=1) + 1e-12)
    return 20 * np.log10(r + 1e-12)


def quiet_mask(fdb):
    """True for 10 ms frames that are pause (room tone), from the recording's own noise floor and speech level."""
    live = fdb[fdb > -100]                  # leave out the digital silence import_voice puts between files
    if len(live) < 50:
        return fdb < -60, -60.0
    floor, loud = np.percentile(live, 10), np.percentile(live, 95)
    thr = min(max(floor + 6.0, loud - 40.0), loud - 25.0)   # a file with hardly any pause (a tight pickup)
    return fdb < thr, float(thr)


def runs(mask, f0, f1, min_len):
    """Runs (start, end) of True frames inside [f0, f1) at least min_len frames long."""
    f0, f1 = max(0, f0), min(len(mask), f1)
    if f1 <= f0:
        return []
    d = np.diff(np.concatenate([[0], mask[f0:f1].astype(np.int8), [0]]))
    st, en = np.where(d == 1)[0], np.where(d == -1)[0]
    return [(f0 + int(s), f0 + int(e)) for s, e in zip(st, en) if e - s >= min_len]


def quietest(fdb, f0, f1):
    f0, f1 = max(0, f0), min(len(fdb), f1)
    return f0 + int(np.argmin(fdb[f0:f1])) if f1 > f0 else max(0, f0)


PAD = 12            # frames of pause kept next to the speech before trim() (120 ms)
MIN_RUN = 15        # a pause of >= 150 ms ends a reading
MIN_RUN_WIDE = 45   # when the sentence's first / last characters were not recognised, only >= 450 ms counts


def pauses(quiet):
    """All pauses (start_frame, end_frame) of >= MIN_RUN frames in a recording."""
    return runs(quiet, 0, len(quiet), MIN_RUN)


def _pad(r):
    return min(PAD, (r[1] - r[0]) // 2)


def _speech_frames(quiet, f0, f1):
    f0, f1 = max(0, int(f0)), min(len(quiet), int(f1))
    return int(np.sum(~quiet[f0:f1])) if f1 > f0 else 0


def start_anchor(quiet, all_pauses, sp):
    """Frame that a reading's separating pause must begin before: the end of its first recognised character.
    Whisper stretches the word next to a pause over that pause, in either direction. When that end lies inside a
    pause and there is speech (>= 150 ms) between the character's start and that pause, the word was said before
    the pause and its END was stretched ("所以，⏸ 可以…"): anchor at the character's start instead. Otherwise the
    word's START was pulled back over the pause before it, and that pause (taken whole) separates the readings."""
    R = sp["in_start"] * 100
    P = next((r for r in all_pauses if r[0] <= R < r[1]), None)
    if P and _speech_frames(quiet, sp["start"] * 100, P[0]) >= MIN_RUN:
        return sp["start"] * 100 + 5
    return R


def end_anchor(quiet, all_pauses, sp):
    """Mirror of start_anchor for the end: the start of the last recognised character, or its end when that start
    lies in a pause with speech (>= 150 ms) between the pause and the character's end (its START was stretched)."""
    L = sp["in_end"] * 100
    P = next((r for r in all_pauses if r[0] <= L < r[1]), None)
    if P and _speech_frames(quiet, P[1], sp["end"] * 100) >= MIN_RUN:
        return sp["end"] * 100 - 5
    return L


def cut_between(fdb, quiet, all_pauses, sa, sb, need_prev=MIN_RUN, need_next=MIN_RUN):
    """Cut points (s) between reading sa and the next reading sb (spans() dicts). The pauses that overlap the
    window between sa's end anchor and sb's start anchor separate them: sa's clip ends just after the first such
    pause, sb's clip starts just before the last one, and whatever lies between (a false start, an earlier reading,
    noise) belongs to neither. A pause is taken whole even when it reaches past the window. No pause -> one shared
    cut at the quietest 10 ms near the recognised boundary (like the AI-voice path)."""
    fL, fR = end_anchor(quiet, all_pauses, sa), start_anchor(quiet, all_pauses, sb)
    cand = [r for r in all_pauses if r[1] > fL and r[0] < fR] if fR > fL else []
    rp = next((r for r in cand if r[1] - r[0] >= need_prev), None)
    rn = next((r for r in reversed(cand) if r[1] - r[0] >= need_next), None)
    if rp is None or rn is None:
        g0, g1 = sorted((sa["end"], sb["start"]))
        c = quietest(fdb, int(g0 * 100) - 8, int(g1 * 100) + 9)
        return c / 100, c / 100
    end_prev = rp[0] + _pad(rp)
    start_next = rn[1] - _pad(rn)
    return end_prev / 100, max(end_prev, start_next) / 100


def cut_head(fdb, quiet, all_pauses, sp, need=MIN_RUN):
    """Start of the first reading in a file: just before the last pause that begins before its start anchor;
    no pause -> the start of the file."""
    fR = start_anchor(quiet, all_pauses, sp)
    cand = [r for r in all_pauses if r[0] < fR and r[1] - r[0] >= need]
    return (cand[-1][1] - _pad(cand[-1])) / 100 if cand else 0.0


def cut_tail(fdb, quiet, all_pauses, sp, n_frames, need=MIN_RUN):
    """End of the last reading in a file: just after the first pause that ends after its end anchor; no pause ->
    the end of the file."""
    fL = end_anchor(quiet, all_pauses, sp)
    cand = [r for r in all_pauses if r[1] > fL and r[1] - r[0] >= need]
    return (cand[0][0] + _pad(cand[0])) / 100 if cand else n_frames / 100


def pull_back(quiet, all_pauses, sp, ca, lo):
    """Clip start after a check on whisper's timing. When the reading's first recognised character lies entirely in a
    pause before the clip start ca (whisper shifted the word into the silence after it: "所以，⏸ 可以…" with 所以
    time-stamped inside the pause), the speech just before that pause (>= 150 ms, after lo = the previous reading's
    clip end) is taken as its audio and the clip starts before it. segment_audio.py then re-checks the extension
    (without it, is the reading already complete? then the speech was noise and the extension is dropped)."""
    f0, f1 = sp["start"] * 100, sp["in_start"] * 100
    if f0 >= ca * 100 - 5:
        return ca
    P = next((r for r in all_pauses if r[0] <= f0 and f1 <= r[1]), None)
    if P is None:
        return ca
    prev = [r for r in all_pauses if r[1] <= P[0]]
    start = prev[-1][1] if prev else 0
    if start < lo * 100 or _speech_frames(quiet, start, P[0]) < MIN_RUN:
        return ca
    return min(ca, (start - (_pad(prev[-1]) if prev else 0)) / 100)


def push_forward(quiet, all_pauses, sp, cb, hi, n_frames):
    """Mirror of pull_back for the end: the last recognised character lies entirely in a pause after the clip end
    cb -> the speech just after that pause (>= 150 ms, before hi = the next reading's clip start) is its audio."""
    f0, f1 = sp["in_end"] * 100, sp["end"] * 100
    if f1 <= cb * 100 + 5:
        return cb
    P = next((r for r in all_pauses if r[0] <= f0 and f1 <= r[1]), None)
    if P is None:
        return cb
    nxt = [r for r in all_pauses if r[0] >= P[1]]
    end = nxt[0][0] if nxt else n_frames
    if end > hi * 100 or _speech_frames(quiet, P[1], end) < MIN_RUN:
        return cb
    return max(cb, (end + (_pad(nxt[0]) if nxt else 0)) / 100)


RESTART_PAUSE = 60  # frames: a pause this long inside one reading may be "stop, read the sentence again"


def long_pauses(all_pauses, a, b):
    """Pauses of >= RESTART_PAUSE frames strictly inside the clip [a, b] (s)."""
    return [r for r in all_pauses if r[0] > a * 100 + 10 and r[1] < b * 100 - 10 and r[1] - r[0] >= RESTART_PAUSE]


def sound_extent(quiet, a, b):
    """(first, last) time with sound (not pause) inside [a, b) seconds, or None."""
    f0, f1 = int(a * 100), int(b * 100)
    live = np.where(~quiet[max(0, f0):max(0, f1)])[0]
    if len(live) == 0:
        return None
    return (f0 + live[0]) / 100, (f0 + live[-1] + 1) / 100


def line_bounds(lines_len, r_end, clip_start, dur):
    """Subtitle line boundaries inside a clip: line i starts when the last char of line i-1 has been said.
    lines_len: normalised length of each line; r_end: end time per reference char of the sentence."""
    L = len(lines_len)
    seg_len = len(r_end)
    tot = sum(lines_len) or 1
    b = [0.0]
    acc = 0
    for li in range(L - 1):
        acc += lines_len[li]
        q = min(seg_len - 1, max(0, int(acc * seg_len / tot) - 1))
        b.append(float(r_end[q]) - clip_start)
    b.append(dur)
    for i in range(1, L):                    # monotonic, >= 0.3 s per line when the clip is long enough
        lo = b[i - 1] + 0.3
        hi = dur - 0.3 * (L - i)
        b[i] = min(max(b[i], lo), hi) if lo <= hi else b[i - 1] + (dur - b[i - 1]) / (L - i + 1)
        b[i] = min(max(b[i], 0.0), dur)
    return b
