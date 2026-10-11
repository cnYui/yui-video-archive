# -*- coding: utf-8 -*-
"""把 transcribe_live.py / transcribe_talk.py 分段转出的 part_*.json 合并成整段的 json / txt / 英文 srt。
part_*_fine.json（对一小段 beam 5 精转的）不合并，查词用 words.py。

  python merge_transcripts.py iv      访谈（素材/转写/ → interview.json / interview.txt / interview_en.srt）
  python merge_transcripts.py tk      Lauren 的 X 演讲（素材/转写_演讲/ → talk.json / talk.txt / talk_en.srt）
"""
import json
import sys
from pathlib import Path

MAT = Path("D:/大疆/独立视频/素材/2026-10_不再Review")
CFG = {"iv": (MAT / "转写", "interview"), "tk": (MAT / "转写_演讲", "talk")}


def stamp(sec, srt=False):
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
    return f"{int(h)}:{int(m):02d}:{int(s):02d}"


def main():
    D, name = CFG[sys.argv[1]]
    parts = sorted(p for p in D.glob("part_*.json") if "_fine" not in p.stem and "_" not in p.stem[5:])
    segs = []
    for p in parts:
        d = json.loads(p.read_text(encoding="utf-8"))
        a, b = d["range"]
        segs = [s for s in segs if s["start"] < a] + d["segments"]      # 两段交界处：后一段从自己的起点开始算
    segs.sort(key=lambda s: s["start"])
    out = {"model": "faster-whisper large-v3-turbo int8", "language": "en", "segments": segs}
    (D / f"{name}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (D / f"{name}.txt").write_text("".join(f"[{stamp(s['start'])}] {s['text']}\n" for s in segs), encoding="utf-8")
    (D / f"{name}_en.srt").write_text("".join(f"{i}\n{stamp(s['start'], True)} --> {stamp(s['end'], True)}\n{s['text']}\n\n" for i, s in enumerate(segs, 1)), encoding="utf-8")
    n_words = sum(len(s["words"]) for s in segs)
    print(f"合并 {len(parts)} 段 → {len(segs)} 句、{n_words} 词，最后一句结束于 {stamp(segs[-1]['end'])}")


if __name__ == "__main__":
    main()
