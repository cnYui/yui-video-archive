# -*- coding: utf-8 -*-
"""从已验证的母片裁出可独立发布的短视频，并同步裁切双语字幕。"""
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "Wang感知比现实_成片.mp4"
SUB = ROOT / "Wang感知比现实_双语字幕.srt"

CLIPS = [
    ("03_Palantir半个表演剧团", "Palantir半个表演剧团", 47.01, 68.49),
    ("04_显得无害", "显得无害", 80.57, 91.07),
]


def parse_srt(path):
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip())
    rows = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        m = re.match(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", lines[1])
        if not m:
            continue
        rows.append((m.group(1), m.group(2), lines[2:]))
    return rows


def sec(ts):
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def stamp(value):
    value = max(0, value)
    h = int(value // 3600)
    m = int(value % 3600 // 60)
    s = int(value % 60)
    ms = int(round((value - int(value)) * 1000))
    if ms == 1000:
        s += 1
        ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_subtitle(out, start, end):
    result = []
    n = 1
    for a, b, text in parse_srt(SUB):
        left, right = sec(a), sec(b)
        if right <= start or left >= end:
            continue
        result.append(f"{n}\n{stamp(max(left, start) - start)} --> {stamp(min(right, end) - start)}\n" + "\n".join(text))
        n += 1
    out.write_text("\n\n".join(result) + "\n", encoding="utf-8")


def run():
    if not MASTER.exists():
        raise FileNotFoundError(MASTER)
    for folder, title, start, end in CLIPS:
        out_dir = ROOT.parent / folder
        out_dir.mkdir(parents=True, exist_ok=True)
        video = out_dir / f"{title}_成片.mp4"
        preview = out_dir / f"{title}_手机预览.mp4"
        sub = out_dir / f"{title}_双语字幕.srt"
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-ss", str(start), "-to", str(end),
            "-i", str(MASTER), "-c", "copy", "-movflags", "+faststart", str(video)
        ], check=True)
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", "scale=540:1170:flags=lanczos",
            "-c:v", "libx264", "-crf", "27", "-preset", "slow", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(preview)
        ], check=True)
        write_subtitle(sub, start, end)
        shutil.copy2(ROOT / "README.md", out_dir / "母片说明.md") if (ROOT / "README.md").exists() else None
        (out_dir / "README.md").write_text(
            f"# {title}\n\n从 `02_AlexandrWang感知比现实` 母片裁切，母片时间 {start:.2f}–{end:.2f} 秒，时长约 {end-start:.2f} 秒。\n\n"
            "保留母片已验证的画面、同传、原声压低混音和双语字幕；短视频不加片头片尾。\n",
            encoding="utf-8",
        )
        print(video)


if __name__ == "__main__":
    run()
