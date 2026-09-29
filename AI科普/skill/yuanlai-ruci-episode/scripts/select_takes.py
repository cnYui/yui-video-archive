"""Score every take of every chunk with ASR and pick the best one -> 配音/selection.json.

  python select_takes.py <episode_dir> [--hist 配音/urls_hist.txt] [--model small]
  python select_takes.py <episode_dir> [--take C01_v2.wav] [--user-voice]     # the user's own recording

--hist: a text file of extra take URLs (e.g. recovered from the Fish Audio history page, any order,
whitespace separated). Each is downloaded to 配音/raw/hist/, recognised, matched to the chunk whose text
it resembles most (similarity ≥0.6) and saved as the next 配音/raw/Cxx_vN.mp3; duplicates are skipped.

Then every 配音/raw/Cxx_v*.mp3 is scored against the chunk's tts_text and the best is written to
配音/selection.json {chunk: {file, score, duration, asr, alternatives}}. ASR results are cached by file
hash in 配音/raw/asr_cache.json, so re-running is cheap. Listen to any chunk with score < 0.95.

The user's own recording (episode.json "voice_source": "user", or --user-voice): the takes are the imported
配音/raw/Cxx_vN.wav (import_voice.py; AI takes .mp3 are ignored) and the NEWEST one is used (each import is a
deliberate new recording; --take picks another). Every take is scored against the subtitle text (what a person
reads, not the TTS spelling): score = share of the script's characters found in the recognition (retakes do not
lower it), plus the number of extra recognised characters (retakes, noise). The word-timed recognition is cached in
配音/raw/asr_words.json, which segment_audio.py reuses.
Next: segment_audio.py <episode_dir>
"""
import argparse
import hashlib
import difflib
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402
from fetch_check import ASR_PROMPT, duration, load_model, norm  # noqa: E402  (same normalisation)


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
    ap.add_argument("--hist", help="额外的录音地址列表文件（历史记录里找回的）")
    ap.add_argument("--model", default="small", help="faster-whisper 模型（默认 small）")
    ap.add_argument("--user-voice", action="store_true",
                    help="按用户自己的录音处理（不看 episode.json 的 voice_source；测试用）")
    ap.add_argument("--take", help="自己录音时指定用哪一版（例如 C01_v2.wav；默认最新导入的）")
    args = ap.parse_args()
    p = C.Paths(args.episode_dir, args.series)
    chunks = C.load_json(p.chunks)
    if not chunks:
        sys.exit(f"缺少 {p.chunks}：先运行 chunk_voice.py")
    if args.user_voice or user_voice_episode(p):
        return main_user(args, p, chunks)
    p.raw.mkdir(parents=True, exist_ok=True)
    refs = {c["chunk"]: norm(c["text"].replace(" ", "")) for c in chunks}
    cache_path = p.raw / "asr_cache.json"
    cache = C.load_json(cache_path, {})
    model = None

    def asr(path):
        nonlocal model
        h = hashlib.md5(path.read_bytes()).hexdigest()
        if h not in cache:
            if model is None:
                model = load_model(args.model)
            segs, _ = model.transcribe(str(path), language="zh", initial_prompt=ASR_PROMPT)
            cache[h] = "".join(s.text for s in segs)
            cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        return cache[h]

    def score(ref, hyp):
        return difflib.SequenceMatcher(None, ref, norm(hyp)).ratio()

    # 1) recovered history URLs -> identify chunk
    if args.hist:
        hf = Path(args.hist)
        hf = hf if hf.is_absolute() or hf.exists() else p.ep / hf
        hist = p.raw / "hist"
        hist.mkdir(exist_ok=True)
        known = {hashlib.md5(x.read_bytes()).hexdigest() for x in p.raw.glob("C*_v*.mp3")}
        for url in hf.read_text(encoding="utf-8").split():
            if not url.startswith("http"):
                continue
            name = url.split("/")[-1].split("?")[0]
            dst = hist / name
            if not dst.exists():
                subprocess.run(["curl", "-sS", "-L", "--max-time", "60", "-o", str(dst), url.split("?")[0]], check=True)
            h = hashlib.md5(dst.read_bytes()).hexdigest()
            if h in known:
                print("dup of existing take:", name)
                continue
            hyp = asr(dst)
            best = max(refs, key=lambda c: score(refs[c], hyp))
            s = score(refs[best], hyp)
            if s < 0.6:
                print("UNMATCHED", name, round(s, 3), hyp[:40])
                continue
            n = 1
            while (p.raw / f"{best}_v{n}.mp3").exists():
                n += 1
            dst_named = p.raw / f"{best}_v{n}.mp3"
            dst_named.write_bytes(dst.read_bytes())
            known.add(h)
            print(f"{name} -> {dst_named.name} score={s:.3f}")

    # 2) score every take of every chunk, pick best
    selection, missing = {}, []
    for c in chunks:
        cid = c["chunk"]
        scored = []
        for tk in sorted(p.raw.glob(f"{cid}_v*.mp3")):
            hyp = asr(tk)
            scored.append((score(refs[cid], hyp), tk.name, duration(tk), hyp))
        if not scored:
            print(cid, "NO TAKES")
            missing.append(cid)
            continue
        scored.sort(reverse=True)
        s, name, dur, hyp = scored[0]
        selection[cid] = dict(file=name, score=round(s, 3), duration=round(dur, 2), asr=hyp,
                              alternatives=[dict(file=n, score=round(x, 3)) for x, n, _, _ in scored[1:]])
        flag = "" if s >= 0.95 else "   <- 听一下"
        print(f"{cid}: best {name} score={s:.3f} dur={dur:.1f}s  (of {len(scored)}){flag}")
    C.write_json(p.selection, selection)
    print(f"-> {p.selection}")
    if missing:
        print(f"[提醒] 还没有录音的批次：{'、'.join(missing)}")


def main_user(args, p, chunks):
    """The user's own recording: newest imported take per chunk, scored against the subtitle text."""
    import uservoice as U
    if args.hist:
        print("[提醒] --hist 只用于 AI 配音（找回 Fish Audio 历史记录里的版本），自己录音时忽略")
    plan = C.load_json(p.voice_plan)
    if not plan:
        sys.exit(f"缺少 {p.voice_plan}：先运行 build_script.py")
    meta = {s["id"]: s for s in plan}
    stale = [i for c in chunks for i in c["ids"] if i not in meta]
    if stale:
        sys.exit(f"chunks.json 和 配音分段.json 对不上（{stale[:5]}…）：台本改过就要重新 chunk_voice --whole")
    cache = p.raw / "asr_words.json"
    selection, missing = {}, []
    for c in chunks:
        cid = c["chunk"]
        ref, _, gap = U.build_reference([meta[i]["text"] for i in c["ids"]])
        tk = U.takes(p.raw, cid)
        if not tk:
            print(cid, "还没有导入录音（import_voice.py）")
            missing.append(cid)
            continue
        scored = []
        for n, f in tk:
            asr = U.asr_words(f, cache, args.model)
            hyp, _, _ = U.char_stream(asr["words"])
            cover, extra = 0.0, 0
            if hyp:
                r2h, ins_at, _ = U.align(ref, hyp, gap)
                cover = sum(1 for i, j in enumerate(r2h) if j >= 0 and hyp[j] == ref[i]) / max(1, len(ref))
                extra = int((ins_at >= 0).sum())
            scored.append(dict(n=n, file=f.name, score=cover, extra=extra, dur=duration(f), asr=asr["text"]))
        pick = scored[-1]
        if args.take:
            pick = next((s for s in scored if s["file"] == args.take), None)
            if pick is None:
                sys.exit(f"{cid} 没有 {args.take}（有：{'、'.join(s['file'] for s in scored)}）")
        others = [s for s in scored if s is not pick]
        selection[cid] = dict(file=pick["file"], score=round(pick["score"], 3), duration=round(pick["dur"], 2),
                              asr=pick["asr"], source="user", extra_chars=pick["extra"],
                              alternatives=[dict(file=s["file"], score=round(s["score"], 3)) for s in reversed(others)])
        how = "指定的" if args.take else "最新导入的"
        flag = "" if pick["score"] >= 0.9 else "   <- 不少字没对上，看 segment_audio 的报告"
        print(f"{cid}: 用{how} {pick['file']}（共 {len(scored)} 版） 台本的字找到 {pick['score']:.1%}，"
              f"多出 {pick['extra']} 字（重读 / 噪音），{pick['dur']:.1f}s{flag}")
        better = max(others, key=lambda s: s["score"], default=None)
        if better and better["score"] > pick["score"] + 0.05:
            print(f"[提醒] {better['file']} 找到 {better['score']:.1%}，比这一版高不少：要用它就 --take {better['file']}")
    if not selection:
        sys.exit(f"配音/raw 里还没有导入的录音（C01_vN.wav）：先 import_voice.py；{p.selection.name} 没有改动")
    C.write_json(p.selection, selection)
    print(f"-> {p.selection}")
    if missing:
        print(f"[提醒] 还没有录音的批次：{'、'.join(missing)}")
    else:
        print(f"下一步：python {Path(__file__).resolve().parent / 'segment_audio.py'} {p.ep}"
              + ("" if user_voice_episode(p) else " --user-voice"))


if __name__ == "__main__":
    main()
