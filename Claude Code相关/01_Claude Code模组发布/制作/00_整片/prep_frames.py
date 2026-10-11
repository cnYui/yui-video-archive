# -*- coding: utf-8 -*-
"""按时间轴给每一帧准备好演示区的画面：官方演示视频（@ClaudeDevs）按 30 fps、按 rate 变速抽成演示区大小（1636×920）。输出 media/scr 和 frames.js。

  python prep_frames.py

素材都是 1920×1080（16:9），和演示区同比例，直接铺满。timeline.json 的 clips[id].parts 每段单独抽（setpts=PTS/rate），
第 n 帧 = 所在 part 的第 round((t − part.t0) × 30) 张；part 之间无缝；播完（hold_from）后定格最后一张。
"""
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
MEDIA = HERE / "media"
FPS = 30
SW, SH = 1636, 920


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + [str(a) for a in args], check=True)


def main():
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    PL = json.loads((EP / "台本" / "plan_v1.json").read_text(encoding="utf-8"))
    SRC = {k: EP / v["file"] for k, v in PL["sources"].items()}
    d = MEDIA / "scr"
    d.mkdir(parents=True, exist_ok=True)
    jobs = []
    for cid, c in T["clips"].items():
        for f in d.glob(f"{cid}_*.jpg"):
            f.unlink()
        for k, p in enumerate(c["parts"]):
            jobs.append((cid, k, p, c["rate"]))

    def work(job):
        cid, k, p, rate = job
        dur_out = p["t1"] - p["t0"]
        vf = f"setpts=PTS/{rate:.5f},fps={FPS},scale={SW}:{SH}:flags=lanczos"
        ff(["-ss", f"{p['in']:.3f}", "-i", SRC[p["src"]], "-t", f"{dur_out + 0.1:.3f}", "-an", "-filter_threads", "1",
            "-vf", vf, "-q:v", "3", "-start_number", "0", d / f"{cid}_{k}_%05d.jpg"])
        return (cid, k), len(list(d.glob(f"{cid}_{k}_*.jpg")))

    with ThreadPoolExecutor(3) as ex:
        counts = dict(ex.map(work, jobs))
    scr = [None] * T["frames"]
    seg_e = {s["id"]: s["e"] for s in T["segs"]}
    for cid, c in T["clips"].items():
        a = int(round(c["s"] * FPS))
        b = min(T["frames"], int(round(c["e"] * FPS)))
        for n in range(a, b):
            t = n / FPS
            k = None
            for i, p in enumerate(c["parts"]):
                if p["t0"] - 1e-6 <= t < p["t1"] - 1e-6:
                    k = i
                    break
            if k is None:                                    # 播完：定格最后一张；开头对不上（不会发生）就取第一张
                k = len(c["parts"]) - 1 if t >= c["parts"][-1]["t1"] - 1e-6 else 0
            p = c["parts"][k]
            i = int(round((t - p["t0"]) * FPS)) if t < p["t1"] else counts[(cid, k)] - 1
            i = max(0, min(counts[(cid, k)] - 1, i))
            scr[n] = f"scr/{cid}_{k}_{i:05d}.jpg"
    (HERE / "frames.js").write_text("window.FR = " + json.dumps({"scr": scr}, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("演示视频：" + "，".join(f"{c}-{k} {v} 张" for (c, k), v in counts.items()) + f"；frames.js 共 {T['frames']} 帧，其中 {sum(1 for x in scr if x)} 帧是演示视频画面")


if __name__ == "__main__":
    main()
