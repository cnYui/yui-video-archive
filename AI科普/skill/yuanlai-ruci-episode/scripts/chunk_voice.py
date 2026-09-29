"""Group the voice script into Fish Audio requests: 台本/配音分段.json -> 配音/chunks.json.

  python chunk_voice.py <episode_dir> --whole [--force] [--series ...]     # 《原LAI如此》: API, whole episode in one request
  python chunk_voice.py <episode_dir> [--max-bytes 480] [--force]          # batches (old web workflow; 《AI每日日报》 calls this)

--whole (the normal case since 2026-09-27, user: generate with the API, the whole episode at once so the voice does not
change between batches): one chunk C01 (scene "ALL") = every segment's tts_text joined in script order. Next:
tts_api.py <episode_dir> (references/voice.md).

Without --whole: segments are packed greedily in script order, never across a scene boundary, while the joined tts_text
stays <= --max-bytes (default 480: the Fish Audio web page takes at most 500 UTF-8 bytes, one Chinese character = 3).
A single segment that is already too long is an error: split it in 台本/script_data.py. Also writes chunks_paste.txt.

配音/chunks.json      [{chunk: "C01", scene, ids: [segment ids], text: joined tts_text, count: bytes}]

After takes exist in 配音/raw/, changing the chunking would mismatch them: the script then refuses unless
--force (the old chunks.json is moved to SERIES/_旧稿/ first; tts_api.py moves takes whose text no longer matches).
The voice is the presenter's (episode.json "presenter": voice_id / voice_name; no presenter = 山田凉).
"""
import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402


def nbytes(s):
    return len(s.encode("utf-8"))


def make_chunks(segs, limit):
    chunks, cur = [], None
    for s in segs:
        text = s["tts_text"].strip()
        if nbytes(text) > limit:
            sys.exit(f"{s['id']} 一段就有 {nbytes(text)} 字节（上限 {limit}）：请在 script_data.py 里拆成两段")
        if cur and cur["scene"] == s["scene"] and nbytes(cur["text"] + text) <= limit:
            cur["ids"].append(s["id"])
            cur["text"] += text
        else:
            cur = dict(chunk="", scene=s["scene"], ids=[s["id"]], text=text)
            chunks.append(cur)
    for i, c in enumerate(chunks, 1):
        c["chunk"] = f"C{i:02d}"
        c["count"] = nbytes(c["text"])
    return [dict(chunk=c["chunk"], scene=c["scene"], ids=c["ids"], text=c["text"], count=c["count"]) for c in chunks]


def whole_chunk(segs):
    text = "".join(s["tts_text"].strip() for s in segs)
    return [dict(chunk="C01", scene="ALL", ids=[s["id"] for s in segs], text=text, count=nbytes(text))]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_common(ap)
    ap.add_argument("--whole", action="store_true", help="整期一批（API 一次生成，《原LAI如此》的正常做法）")
    ap.add_argument("--max-bytes", type=int, default=480, help="分批时每批 UTF-8 字节上限（默认 480；网页版单次 500）")
    ap.add_argument("--force", action="store_true", help="配音/raw 里已有录音时也重新分批（旧 chunks.json 移到 _旧稿）")
    args = ap.parse_args()
    p = C.Paths(args.episode_dir, args.series)
    segs = C.load_json(p.voice_plan)
    if not segs:
        sys.exit(f"缺少 {p.voice_plan}：先运行 build_script.py")
    chunks = whole_chunk(segs) if args.whole else make_chunks(segs, args.max_bytes)

    old = C.load_json(p.chunks)
    if old is not None and old != chunks:
        takes = list(p.raw.glob("C*_v*.mp3")) if p.raw.exists() else []
        if takes and not args.force:
            sys.exit(f"配音/raw 里已有 {len(takes)} 个录音，而新的分批和现有 chunks.json 不一样。"
                     "确认要重新分批（旧录音将对不上）就加 --force")
        moved = C.archive(p.chunks, p, "chunks")
        print(f"旧 chunks.json 已移到 {moved}")
    p.voice.mkdir(exist_ok=True)
    C.write_json(p.chunks, chunks)
    pr = C.presenter_of(C.load_episode(p, required=False) or {})
    voice = f"Fish Audio「{pr.get('voice_name') or '？'}」（本期讲解员 {pr['name']}，模型 id {C.voice_id_of(pr) or '？'}）"
    if not args.whole:
        paste = [f"# 音色 {voice}  生成器 {pr.get('voice_app') or '（episode.json presenter.voice_app 没写）'}  模型 S1\n"]
        for c in chunks:
            paste.append(f"==== {c['chunk']}  {c['scene']}  {'、'.join(c['ids'])}  ({c['count']} 字节)\n{c['text']}\n")
        (p.voice / "chunks_paste.txt").write_text("\n".join(paste), encoding="utf-8")
    for c in chunks:
        print(f"{c['chunk']} {c['scene']} {len(c['ids']):2d} 段 {c['count']:3d} 字节  {c['ids'][0]}…{c['ids'][-1]}")
    print(f"{len(chunks)} 批，{len(segs)} 段 -> {p.chunks}")
    print(f"音色：{voice}\n  音色页 {pr.get('voice_page') or '？'}")
    if args.whole:
        total = sum(c["count"] for c in chunks)
        if total > 20000:
            print(f"[提醒] 整期 {total} 字节，比平常（6–8 千字节）长很多：确认台本没有重复，生成后重点听后半段")
        print(f"下一步：python tts_api.py {p.ep}  （Fish Audio API，一次请求生成整期）")


if __name__ == "__main__":
    main()
