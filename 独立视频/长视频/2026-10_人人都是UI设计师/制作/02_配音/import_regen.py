# -*- coding: utf-8 -*-
"""重生成几句之后，把 Fish 故事工作室“导出项目 → 按段落拆分”的 zip 里的这几句放进 tts/seg_pick_v3/<句号>.wav（build_voice.py 会用它盖过 final/ 里同序号的那一句）。

  python import_regen.py <segments*.zip> R10d R19e R19f        句号按在工作室里键入的顺序写

按 metadata.csv 的顺序和这几句台本的 say 逐句核对文字（不一致就停）；mp3 自动转 44.1 kHz 单声道 wav；已有的同名文件先备份成 .bak_<时间>.wav（不删）。
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
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    z, ids = Path(sys.argv[1]), sys.argv[2:]
    say = {l["id"]: l["say"] for l in json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))["lines"]}
    out = HERE / "tts" / "seg_pick_v3"
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(z) as zf:
        rows = list(csv.DictReader(io.StringIO(zf.read("segments/metadata.csv").decode("utf-8-sig"))))
        if len(rows) != len(ids):
            sys.exit(f"metadata.csv 有 {len(rows)} 句，要放的有 {len(ids)} 句：{ids}")
        bad = [(i, r["text"], say[i]) for r, i in zip(rows, ids) if r["text"].strip() != say[i].strip()]
        if bad:
            sys.exit("工作室里的文字和台本 say 不一致：\n" + "\n".join(f"  {i}：工作室「{a}」≠ 台本「{b}」" for i, a, b in bad))
        names = sorted(n for n in zf.namelist() if n.startswith("segments/") and n.lower().endswith((".wav", ".mp3")) and "/metadata" not in n)
        assert len(names) == len(ids), f"zip 里有 {len(names)} 个音频文件，要放的有 {len(ids)} 句"
        for n, i in zip(names, ids):
            dst = out / f"{i}.wav"
            if dst.exists():
                shutil.copy2(dst, dst.with_name(f"{i}.bak_{time.strftime('%H%M%S')}.wav"))
            tmp = out / ("_tmp" + Path(n).suffix)
            tmp.write_bytes(zf.read(n))
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-ac", "1", "-ar", "44100", str(dst)], check=True)
            tmp.unlink()
            print(f"{i} ← {n}  {dst}")


if __name__ == "__main__":
    main()
