# -*- coding: utf-8 -*-
r"""第二批配音：整稿（120 句）出来之后新加的句子（id ≥ N13）+ 要重配的句子（redo.txt：每行 `期号:句号`，例 `3:N06`），一个小 Fish 项目一次做完。

  python voice_extra.py list            打印要键入的句子（一行一句）、哈希，写 fish_extra_lines.txt
  python voice_extra.py split <zip>     把导出的 zip 逐句核对文字后放进各期 制作\02_配音\tts\seg_pick_v3\<句号>.wav
  python voice_extra.py rebuild         每期按现在的台词顺序重排 tts\seg_raw\final\（旧句取第一批的对应文件，新句 / 重配句取 seg_pick_v3），旧的先备份成 final_第一批
之后每期：cd 制作\02_配音 && python build_voice.py
"""
import csv
import hashlib
import io
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from series_data import EPISODES, EP_ROOT  # noqa: E402


def redo_list():
    p = HERE / "redo.txt"
    out = set()
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            ln = ln.split("#")[0].strip()
            if ln:
                a, b = ln.split(":")
                out.add((int(a), b.strip()))
    return out


def extra_rows():
    redo = redo_list()
    rows = []
    for n in sorted(EPISODES):
        for l in EPISODES[n]["lines"]:
            if int(l["id"][1:]) >= 13 or (n, l["id"]) in redo:
                rows.append((n, l["id"], l["say"]))
    return rows


def ep_dir(n):
    return EP_ROOT / EPISODES[n]["folder"] / "制作" / "02_配音" / "tts"


def cmd_list():
    rows = extra_rows()
    text = "\n".join(r[2] for r in rows)
    (HERE / "fish_extra_lines.txt").write_text(text + "\n", encoding="utf-8")
    print(f"{len(rows)} 句，{len(text)} 字符；SHA-256 = {hashlib.sha256(text.encode('utf-8')).hexdigest()}")
    for n, i, s in rows:
        print(f"  {n}:{i}  {s}")


def cmd_split(z):
    rows_want = extra_rows()
    with zipfile.ZipFile(z) as zf:
        rows = list(csv.DictReader(io.StringIO(zf.read("segments/metadata.csv").decode("utf-8-sig"))))
        if len(rows) != len(rows_want):
            sys.exit(f"metadata.csv 有 {len(rows)} 句，要的是 {len(rows_want)} 句")
        bad = [(i + 1, r["text"], w[2]) for i, (r, w) in enumerate(zip(rows, rows_want)) if r["text"].strip() != w[2].strip()]
        if bad:
            sys.exit("文字不一致：\n" + "\n".join(f"  第 {i} 句：工作室「{a}」≠ 台本「{b}」" for i, a, b in bad[:20]))
        for r, (n, i, s) in zip(rows, rows_want):
            d = ep_dir(n) / "seg_pick_v3"
            d.mkdir(parents=True, exist_ok=True)
            dst = d / f"{i}.wav"
            if dst.exists():
                dst.rename(d / f"{i}_旧_{time.strftime('%H%M%S')}.wav")
            name = r["file_relative"]
            if name.lower().endswith(".wav"):
                with zf.open(name) as src, open(dst, "wb") as out:
                    shutil.copyfileobj(src, out)
            else:
                tmp = d / f"_tmp{Path(name).suffix}"
                tmp.write_bytes(zf.read(name))
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-ac", "1", "-ar", "44100", str(dst)], check=True)
                tmp.unlink()
            print(f"第 {n} 期 {i} → {dst}")


def cmd_rebuild():
    for n in sorted(EPISODES):
        t = ep_dir(n)
        final, orig = t / "seg_raw" / "final", t / "seg_raw" / "final_第一批"
        if not orig.exists():
            final.rename(orig)
            final.mkdir()
        else:                                                             # 已经重排过：清掉 final 重来
            for f in final.glob("*.wav"):
                f.unlink()
        lines = EPISODES[n]["lines"]
        src_orig = sorted(orig.glob("*.wav"))
        for pos, l in enumerate(lines):
            k = int(l["id"][1:]) - 1
            pick = t / "seg_pick_v3" / f"{l['id']}.wav"
            if int(l["id"][1:]) >= 13:
                assert pick.exists(), f"第 {n} 期 {l['id']} 没有新配音：{pick}"
                shutil.copy2(pick, final / f"{pos:06d}.wav")
            else:
                shutil.copy2(pick if pick.exists() else src_orig[k], final / f"{pos:06d}.wav")
        print(f"第 {n} 期：{len(lines)} 句 → {final}（旧的在 {orig.name}）")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    {"list": cmd_list, "split": lambda: cmd_split(sys.argv[2]), "rebuild": cmd_rebuild}[sys.argv[1]]()
