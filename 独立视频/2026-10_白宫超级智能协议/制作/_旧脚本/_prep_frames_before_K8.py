# -*- coding: utf-8 -*-
"""按时间轴给每一帧准备好画面素材：现场片段（白宫官方 1920×1080、PBS 1280×720）按 30 fps 抽成演示区大小。输出 media/ 和 frames.js。

  python prep_frames.py

现场片段在成片里按原速放（原声保留），所以第 n 帧 = 片段里 in + (n − seg.s×30)/30 秒。
演示区放大后的实际像素 1636×920（页面里按 1474×829 写、整体 scale 1.1099）；PBS 原片 720p，放大 1.28 倍会软一点，字幕在片段外面，不影响。
PBS 片段左下角有 PBS NEWS 台标：原样保留（来源标注），不去水印。
"""
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
LIVE = EP / "素材" / "现场视频"
MEDIA = HERE / "media"
FPS = 30
SW, SH = 1636, 920
SRC = {"wh": LIVE / "wh_official_6UBA8iL3x54.mp4", "pbs": LIVE / "pbs_1XVhpiRSHv8.mp4"}


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + [str(a) for a in args], check=True)


def main():
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    d = MEDIA / "scr"
    d.mkdir(parents=True, exist_ok=True)

    def work(item):
        cid, c = item
        for f in d.glob(f"{cid}_*.jpg"):
            f.unlink()
        n = int(round((c["e"] - c["s"]) * FPS)) + 2
        ff(["-ss", f"{c['in']:.3f}", "-i", SRC[c["src"]], "-t", f"{c['out'] - c['in'] + 0.2:.3f}", "-an", "-filter_threads", "1",
            "-vf", f"fps={FPS},scale={SW}:{SH}:flags=lanczos", "-q:v", "3", "-start_number", "0", d / f"{cid}_%05d.jpg"])
        return cid, len(list(d.glob(f"{cid}_*.jpg")))

    with ThreadPoolExecutor(2) as ex:
        counts = dict(ex.map(work, T["clips"].items()))
    scr = [None] * T["frames"]
    seg_e = {s["id"]: s["e"] for s in T["segs"]}
    for cid, c in T["clips"].items():
        a = int(round(c["s"] * FPS))
        b = min(T["frames"], int(round(seg_e[cid] * FPS)))   # 一直铺到这一段结束：片段后面的 0.35 s 空隙接着原片多走一点，再定格最后一帧，不要闪空白
        for n in range(a, b):
            i = min(counts[cid] - 1, n - a)
            scr[n] = f"scr/{cid}_{i:05d}.jpg"
    (HERE / "frames.js").write_text("window.FR = " + json.dumps({"scr": scr}, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("现场片段：" + "，".join(f"{k} {v} 张" for k, v in counts.items()) + f"；frames.js 共 {T['frames']} 帧，其中 {sum(1 for x in scr if x)} 帧是现场画面")


if __name__ == "__main__":
    main()
