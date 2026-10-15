# -*- coding: utf-8 -*-
"""把 Fish 故事工作室“导出项目 → 按段落拆分”的 zip（6 期合成一份整稿）拆回各期：核对文字 → 每期的 制作/02_配音/tts/seg_raw/final/NNNNNN.wav。

  python split_voice_export.py "C:\\Users\\yui\\Downloads\\segments (N).zip"

- 顺序和文字以 metadata.csv 为准，和 series_data.py 里每句的 say 逐句核对（不一致就停，不写任何文件）；
- 偶尔有一两句导出成 mp3，用 ffmpeg 转成 44.1 kHz 单声道 wav；
- 各期已有的 final/ 先备份成 final_旧_<时间>/（不删）；整份 zip 拷一份到每期的 tts/seg_raw/segments_export.zip 备查。
之后每期照常：cd 制作\\02_配音 && python build_voice.py --qa
"""
import csv
import io
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import series_data as D  # noqa: E402
from gen_episode import ep_dir  # noqa: E402
from build_fish_doc import all_lines  # noqa: E402


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    z = Path(sys.argv[1])
    rows_want = all_lines()
    with zipfile.ZipFile(z) as zf:
        rows = list(csv.DictReader(io.StringIO(zf.read("segments/metadata.csv").decode("utf-8-sig"))))
        if len(rows) != len(rows_want):
            sys.exit(f"metadata.csv 有 {len(rows)} 句，台本合计 {len(rows_want)} 句：导出面板里“章节”要选整个项目、文件结构选“按段落拆分”")
        bad = [(i + 1, r["text"], w[2]) for i, (r, w) in enumerate(zip(rows, rows_want)) if r["text"].strip() != w[2].strip()]
        if bad:
            sys.exit("工作室里的文字和台本 say 不一致：\n" + "\n".join(f"  第 {i} 句：工作室「{a}」≠ 台本「{b}」" for i, a, b in bad[:20]))
        stamp = time.strftime("%Y%m%d-%H%M%S")
        k = 0
        for ep in D.EPISODES:
            n_lines = sum(1 for r in rows_want if r[0] == ep["num"])
            raw = ep_dir(ep) / "制作" / "02_配音" / "tts" / "seg_raw"
            final = raw / "final"
            if final.exists() and any(final.iterdir()):
                final.rename(final.with_name("final_旧_" + stamp))
            final.mkdir(parents=True, exist_ok=True)
            shutil.copy2(z, raw / "segments_export.zip")
            conv = []
            for j in range(n_lines):
                r = rows[k + j]
                name = r["file_relative"]
                dst = final / f"{j:06d}.wav"
                if name.lower().endswith(".wav"):
                    with zf.open(name) as src, open(dst, "wb") as out:
                        shutil.copyfileobj(src, out)
                else:
                    tmp = final / f"_tmp_{j:06d}{Path(name).suffix}"
                    tmp.write_bytes(zf.read(name))
                    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-ac", "1", "-ar", "44100", str(dst)], check=True)
                    tmp.unlink()
                    conv.append(j + 1)
            k += n_lines
            print(f"第 {ep['num']} 期：{n_lines} 句 → {final}" + (f"（第 {conv} 句原本不是 wav，已转）" if conv else ""))
    print("下一步：每期 cd 制作\\02_配音 && python build_voice.py --qa，再 build_timeline.py（不带 --est）")


if __name__ == "__main__":
    main()
