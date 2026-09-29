# -*- coding: utf-8 -*-
"""作品展示段：从四条展示视频里各取 5 秒，抽成画框大小的帧（JPEG），切出声音并统一响度，再按时间轴混成一条音轨。

用法：python prep.py            （输出到本文件夹的 clips/、audio/）
片段、时间点、出场时刻都在 CLIPS 里改；改完重跑 prep.py，再跑 render.py。
"""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # 教程_Claude做视频/
SERIES = Path(r"D:\大疆\AI科普")

FPS = 30
DUR = 5.0                                   # 每个片段播 5 秒（用户 2026-09-28）
INNER_W = 1474                              # 画框内宽，和 index.html 一致
TARGET_LUFS = -18.0                         # 片段原声的统一响度；之后口播进来再压

# t0 = 在本段里开始播放的时刻（秒），和 index.html 的 ITEMS 一致
CLIPS = [
    dict(key="gintama", src=ROOT / "素材/展示视频/03_银魂_像素风.mp4",       ss=60.5,  t0=0.5,  aspect=16 / 9),
    dict(key="naruto",  src=ROOT / "素材/展示视频/01_火影_像素风.mp4",       ss=228.5, t0=6.0,  aspect=16 / 9),
    dict(key="jojo",    src=ROOT / "素材/展示视频/02_JoJo第三部_像素风.mp4", ss=254.5, t0=12.0, aspect=16 / 9),
    dict(key="ep04",    src=SERIES / "第04期_大模型从夯到拉/第04期_大模型从夯到拉_成片.mp4", ss=160.8, t0=17.5, aspect=2340 / 1080),
]
TOTAL = 23.0                                # 本段总长，和 index.html 的 TOTAL 一致


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")


def measure_lufs(wav):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(wav), "-af", "ebur128=framelog=quiet",
                          "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    return float(m[-1])


def main():
    (HERE / "clips").mkdir(exist_ok=True)
    (HERE / "audio").mkdir(exist_ok=True)
    report = []
    for c in CLIPS:
        h = round(INNER_W / c["aspect"])
        h += h % 2
        d = HERE / "clips" / c["key"]
        d.mkdir(parents=True, exist_ok=True)
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(c["ss"]), "-t", str(DUR + 0.3), "-i", str(c["src"]),
             "-vf", f"fps={FPS},scale={INNER_W}:{h}:flags=lanczos", "-frames:v", str(int(DUR * FPS)),
             "-q:v", "2", str(d / "f_%03d.jpg")])
        n = len(list(d.glob("f_*.jpg")))
        (HERE / "audio" / "raw").mkdir(exist_ok=True)
        raw = HERE / "audio" / "raw" / f"{c['key']}.wav"      # 原声（未调响度），重跑时覆盖
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(c["ss"]), "-t", str(DUR), "-i", str(c["src"]),
             "-vn", "-ac", "2", "-ar", "48000", str(raw)])
        lufs = measure_lufs(raw)
        gain = TARGET_LUFS - lufs
        out = HERE / "audio" / f"{c['key']}.wav"
        run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
             f"volume={gain:.2f}dB,afade=t=in:d=0.06,afade=t=out:st={DUR - 0.08:.2f}:d=0.08,alimiter=limit=0.89",
             str(out)])
        report.append(dict(key=c["key"], frames=n, size=f"{INNER_W}x{h}", src_lufs=round(lufs, 1), gain_db=round(gain, 1)))

    # 按出场时刻摆好四段原声，混成一条（其余时间静音）
    inputs, chains = [], []
    for i, c in enumerate(CLIPS):
        inputs += ["-i", str(HERE / "audio" / f"{c['key']}.wav")]
        ms = int(round(c["t0"] * 1000))
        chains.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(len(CLIPS)))
    graph = ";".join(chains) + f";{mix}amix=inputs={len(CLIPS)}:normalize=0:duration=longest,apad=whole_dur={TOTAL},atrim=0:{TOTAL}[out]"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[out]", "-ar", "48000", "-ac", "2",
         str(HERE / "audio" / "mix.wav")])
    (HERE / "clips" / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in report:
        print(r)
    print("mix.wav lufs", measure_lufs(HERE / "audio" / "mix.wav"))


if __name__ == "__main__":
    main()
