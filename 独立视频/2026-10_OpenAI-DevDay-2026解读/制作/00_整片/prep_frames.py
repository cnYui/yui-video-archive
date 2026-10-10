# -*- coding: utf-8 -*-
"""按时间轴给每一帧准备好画面素材：发布会视频（1920×1080，29.97 fps）按 30 fps 抽成演示区大小。输出 out/<ep>/media/scr/ 和 out/<ep>/frames.js。

  python prep_frames.py V1

发布会画面在成片里按原速放，所以第 n 帧 = 片段里 in + (n − seg.s×30)/30 秒。
演示区放大后的实际像素 1636×920（页面里按 1474×829 写、整体 scale 1.1099）；原片 16:9，直接铺满，不裁、不加边。
片段后面的空隙（gap）接着原片多抽 0.2 s，再定格最后一帧，不要闪空白。
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from common import FPS, SH, SRC_VIDEO, SW, out_dir


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + [str(a) for a in args], check=True)


def main():
    ep = sys.argv[1]
    od = out_dir(ep)
    T = json.loads((od / "timeline.json").read_text(encoding="utf-8"))
    d = od / "media" / "scr"
    d.mkdir(parents=True, exist_ok=True)

    def work(item):
        cid, c = item
        for f in d.glob(f"{cid}_*.jpg"):
            f.unlink()
        extra = 0.0 if c.get("cap") else 0.2          # 封顶（片段后面就是镜头切换）的不多抽，不然定格的那一帧是下一个镜头
        cr = c.get("crop")                            # 裁切放大（小字幻灯片）：按整帧比例裁出一块 16:9 再放大到演示区
        vf = (f"fps={FPS},crop=iw*{cr[2] - cr[0]:.4f}:ih*{cr[3] - cr[1]:.4f}:iw*{cr[0]:.4f}:ih*{cr[1]:.4f},scale={SW}:{SH}:flags=lanczos"
              if cr else f"fps={FPS},scale={SW}:{SH}:flags=lanczos")
        ff(["-ss", f"{c['in']:.3f}", "-i", SRC_VIDEO, "-t", f"{c['out'] - c['in'] + extra:.3f}", "-an", "-filter_threads", "1",
            "-vf", vf, "-q:v", "3", "-start_number", "0", d / f"{cid}_%05d.jpg"])
        return cid, len(list(d.glob(f"{cid}_*.jpg")))

    for f in d.glob("*.jpg"):                         # 台本改过、不再用的片段 id 留下的旧抽帧
        if f.name.rsplit("_", 1)[0] not in T["clips"]:
            f.unlink()
    with ThreadPoolExecutor(2) as ex:
        counts = dict(ex.map(work, T["clips"].items()))
    scr = [None] * T["frames"]
    seg_e = {s["id"]: s["e"] for s in T["segs"]}
    for cid, c in T["clips"].items():
        a = int(round(c["s"] * FPS))
        b = min(T["frames"], int(round(seg_e[cid] * FPS)))
        for n in range(a, b):
            scr[n] = f"scr/{cid}_{min(counts[cid] - 1, n - a):05d}.jpg"
    (od / "frames.js").write_text("window.FR = " + json.dumps({"scr": scr}, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"{ep} 发布会画面：" + "，".join(f"{k} {v} 张" for k, v in counts.items()) + f"；frames.js 共 {T['frames']} 帧，其中 {sum(1 for x in scr if x)} 帧是发布会画面")


if __name__ == "__main__":
    main()
