# -*- coding: utf-8 -*-
"""把 Fish 故事工作室“导出项目 → 文件结构：按段落拆分”的 zip 放进 tts/seg_raw/final/（build_voice.py 读这里）。

  python import_segments.py <segments*.zip>        例：python import_segments.py "C:\\Users\\yui\\Downloads\\segments (4).zip"

zip 里是 segments/<章节名>/000000.wav、000001.wav … 和 segments/metadata.csv（每句的文字 + 文件名）。
- 顺序和文字以 metadata.csv 为准，和 ../../台本/录制稿.json 的 `say` 逐句核对（不一致就停）；
- 偶尔有一两句导出成 .mp3（这次最后一句就是），用 ffmpeg 转成 44.1 kHz 单声道 wav；
- 已有的 final/ 先备份成 final_旧_<时间>/（不删）。
"""
import csv
import io
import json
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    z = Path(sys.argv[1])
    lines = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))["lines"]
    with zipfile.ZipFile(z) as zf:
        rows = list(csv.DictReader(io.StringIO(zf.read("segments/metadata.csv").decode("utf-8-sig"))))
        if len(rows) != len(lines):
            sys.exit(f"metadata.csv 有 {len(rows)} 句，台本有 {len(lines)} 句：导出面板里“章节”要选整个项目（里面只放这一个章节）、文件结构选“按段落拆分”")
        bad = [(i + 1, r["text"], l["say"]) for i, (r, l) in enumerate(zip(rows, lines)) if r["text"].strip() != l["say"].strip()]
        if bad:
            sys.exit("工作室里的文字和台本 say 不一致：\n" + "\n".join(f"  第 {i} 句：工作室「{a}」≠ 台本「{b}」" for i, a, b in bad))
        final = HERE / "tts" / "seg_raw" / "final"
        if final.exists() and any(final.iterdir()):
            bak = final.with_name("final_旧_" + time.strftime("%Y%m%d-%H%M%S"))
            final.rename(bak)
            print("旧的 final/ 备份到", bak.name)
        final.mkdir(parents=True, exist_ok=True)
        shutil.copy2(z, HERE / "tts" / "seg_raw" / "segments_export.zip")
        conv = []
        for i, r in enumerate(rows):
            name = r["file_relative"]
            dst = final / f"{i:06d}.wav"
            if name.lower().endswith(".wav"):
                with zf.open(name) as src, open(dst, "wb") as out:
                    shutil.copyfileobj(src, out)
            else:                                                       # mp3 等：转 wav
                tmp = final / f"_tmp_{i:06d}{Path(name).suffix}"
                tmp.write_bytes(zf.read(name))
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-ac", "1", "-ar", "44100", str(dst)], check=True)
                tmp.unlink()
                conv.append(i + 1)
    print(f"-> {final}（{len(lines)} 句；文字和台本逐句一致" + (f"；第 {conv} 句原本不是 wav，已转成 wav" if conv else "") + "）。下一步：python build_voice.py --qa")


if __name__ == "__main__":
    main()
