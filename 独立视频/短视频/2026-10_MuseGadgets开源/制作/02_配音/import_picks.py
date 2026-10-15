# -*- coding: utf-8 -*-
"""台本改了、只重配了其中几句（本条第 2 轮）：把 Fish 导出的 segments zip 里的这几句按句号放进 tts/seg_pick_v3/<句号>.wav。

  python import_picks.py "C:\\Users\\yui\\Downloads\\segments (2).zip" N01 N02 N03 N05 N06 N07 N08

zip 里是 segments/<章节>/000000.wav … 和 segments/metadata.csv；顺序 = 你键入的顺序 = 命令行里写的句号顺序；
文字和 录制稿.json 的 say 逐句核对，不一致就停；mp3 自动转 44.1 kHz 单声道 wav；已有的 seg_pick_v3/<句号>.wav 先备份成 _旧_<时间>。"""
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
    z, ids = Path(sys.argv[1]), sys.argv[2:]
    say = {l["id"]: l["say"] for l in json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))["lines"]}
    out = HERE / "tts" / "seg_pick_v3"
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(z) as zf:
        rows = list(csv.DictReader(io.StringIO(zf.read("segments/metadata.csv").decode("utf-8-sig"))))
        assert len(rows) == len(ids), f"zip 里 {len(rows)} 句，命令行写了 {len(ids)} 个句号"
        bad = [(i, r["text"], say[i]) for i, r in zip(ids, rows) if r["text"].strip() != say[i].strip()]
        if bad:
            sys.exit("文字和台本 say 不一致：\n" + "\n".join(f"  {i}：Fish「{a}」≠ 台本「{b}」" for i, a, b in bad))
        stamp = time.strftime("%H%M%S")
        for lid, r in zip(ids, rows):
            dst = out / f"{lid}.wav"
            if dst.exists():
                dst.rename(out / f"{lid}_旧_{stamp}.wav")
            name = r["file_relative"]
            if name.lower().endswith(".wav"):
                with zf.open(name) as src, open(dst, "wb") as f:
                    shutil.copyfileobj(src, f)
            else:
                tmp = out / f"_tmp{Path(name).suffix}"
                tmp.write_bytes(zf.read(name))
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-ac", "1", "-ar", "44100", str(dst)], check=True)
                tmp.unlink()
            print(lid, "←", name)
    print("好了：下一步 python build_voice.py --qa")


if __name__ == "__main__":
    main()
