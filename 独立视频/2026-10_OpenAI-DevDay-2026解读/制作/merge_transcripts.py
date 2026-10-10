# -*- coding: utf-8 -*-
"""把 transcribe_keynote.py 分段转出的 part_*.json 合并成整场的 素材/转写/keynote.json、keynote.txt、keynote_en.srt（ASR 字幕，英文，带词级时间戳的在 json 里）。
part_*_fine.json（对一小段 beam 5 精转的）不合并，查词用 words.py。

  python merge_transcripts.py
"""
import json
from pathlib import Path

EP = Path(__file__).resolve().parent.parent
D = EP / "素材" / "转写"


def stamp(sec, srt=False):
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
    return f"{int(h)}:{int(m):02d}:{int(s):02d}"


def main():
    parts = sorted(p for p in D.glob("part_*.json") if "_fine" not in p.stem and "_" not in p.stem[5:])
    segs = []
    for p in parts:
        d = json.loads(p.read_text(encoding="utf-8"))
        a, b = d["range"]
        # 两段交界处：后一段从自己的起点开始算，前一段超出起点的丢掉
        segs = [s for s in segs if s["start"] < a] + d["segments"]
    segs.sort(key=lambda s: s["start"])
    out = {"source": "素材/keynote_audio.weba", "model": "faster-whisper large-v3-turbo int8", "language": "en", "segments": segs}
    (D / "keynote.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (D / "keynote.txt").write_text("".join(f"[{stamp(s['start'])}] {s['text']}\n" for s in segs), encoding="utf-8")
    (D / "keynote_en.srt").write_text("".join(f"{i}\n{stamp(s['start'], True)} --> {stamp(s['end'], True)}\n{s['text']}\n\n" for i, s in enumerate(segs, 1)), encoding="utf-8")
    n_words = sum(len(s["words"]) for s in segs)
    print(f"合并 {len(parts)} 段 → {len(segs)} 句、{n_words} 词，最后一句结束于 {stamp(segs[-1]['end'])}")


if __name__ == "__main__":
    main()
