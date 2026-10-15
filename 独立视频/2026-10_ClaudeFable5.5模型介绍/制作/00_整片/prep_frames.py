# -*- coding: utf-8 -*-
"""按时间轴给每一帧准备好画面素材：素材片段按 30 fps 抽成演示区大小（1636×920），宽高比对不上的放大铺满做模糊底、原片居中叠上。
输出 media/（scr/ 逐帧、thumb/ 左栏缩略图、card/ 卡片用图、qr.png）和 frames.js。

  python prep_frames.py

素材在成片里按原速放，所以第 n 帧 = 这段素材里 in + (n − range.s×30)/30 秒；话比画面长而延长的段落，延长部分接着原片往下放，素材放完了就定格最后一帧。
缩略图和卡片图的取帧时刻写在 ../../台本/plan.json 的 "thumbs" / "card_imgs" 里。
"""
import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

from common import EP, FPS, HERE, SH, SRC, SW

MEDIA = HERE / "media"


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + [str(a) for a in args], check=True)


def vf_for(w, h):
    """演示区 SW×SH：比例一致直接缩放；不一致放大铺满做模糊底，原片按比例缩进去居中。"""
    if abs(w / h - SW / SH) < 0.01:
        return f"fps={FPS},scale={SW}:{SH}:flags=lanczos"
    return (f"fps={FPS},split[a][b];[a]scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH},boxblur=36:6,eq=brightness=-0.10:saturation=0.9[bg];"
            f"[b]scale={SW}:{SH}:force_original_aspect_ratio=decrease:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")


def size_of(key):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(SRC[key])],
                       check=True, capture_output=True, text=True).stdout.strip().split(",")
    return int(o[0]), int(o[1])


def main():
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    plan = json.loads((EP / "台本" / "plan.json").read_text(encoding="utf-8"))
    d = MEDIA / "scr"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    sizes = {k: size_of(k) for k in SRC}

    jobs = []
    for cid, c in T["clips"].items():
        for i, r in enumerate(c["ranges"]):
            jobs.append((cid, i, r))

    def work(job):
        cid, i, r = job
        n = int(round((r["e"] - r["s"]) * FPS)) + 2
        extra = 0.12
        ff(["-ss", f"{r['in']:.3f}", "-i", SRC[r["src"]], "-t", f"{r['out'] - r['in'] + extra:.3f}", "-an", "-filter_threads", "1",
            "-vf", vf_for(*sizes[r["src"]]), "-q:v", "3", "-start_number", "0", d / f"{cid}_{i}_%05d.jpg"])
        return (cid, i), len(list(d.glob(f"{cid}_{i}_*.jpg")))

    with ThreadPoolExecutor(2) as ex:
        counts = dict(ex.map(work, jobs))

    scr = [None] * T["frames"]
    seg_e = {s["id"]: s["e"] for s in T["segs"]}
    for cid, c in T["clips"].items():
        if not c["ranges"]:
            continue
        end_n = min(T["frames"], int(round(seg_e[cid] * FPS)))
        for i, r in enumerate(c["ranges"]):
            a = int(round(r["s"] * FPS))
            b = int(round(r["e"] * FPS)) if i + 1 < len(c["ranges"]) else end_n      # 最后一段铺到场景结束（定格）
            for n in range(a, min(b, T["frames"])):
                j = min(counts[(cid, i)] - 1, n - a)
                scr[n] = f"scr/{cid}_{i}_{j:05d}.jpg"
        # 场景第一段前面如果因为取整空了一帧，用第一段的第一帧补
        a0 = int(round(c["ranges"][0]["s"] * FPS))
        if a0 > 0 and scr[a0 - 1] is None and a0 - 1 >= int(round(c["s"] * FPS)):
            scr[a0 - 1] = f"scr/{cid}_0_00000.jpg"
    (HERE / "frames.js").write_text("window.FR = " + json.dumps({"scr": scr}, separators=(",", ":")) + ";\n", encoding="utf-8")

    # 左栏缩略图（352×198，页面里显示 176×99）、卡片用图
    (MEDIA / "thumb").mkdir(exist_ok=True)
    (MEDIA / "card").mkdir(exist_ok=True)
    for name, spec in (plan.get("thumbs") or {}).items():
        w, h = sizes[spec["src"]]
        ff(["-ss", f"{spec['t']:.3f}", "-i", SRC[spec["src"]], "-frames:v", "1", "-vf", f"scale=352:198:force_original_aspect_ratio=increase,crop=352:198", "-q:v", "2", MEDIA / "thumb" / f"{name}.jpg"])
    for name, spec in (plan.get("card_imgs") or {}).items():
        ff(["-ss", f"{spec['t']:.3f}", "-i", SRC[spec["src"]], "-frames:v", "1", "-vf", f"scale={spec.get('w', 1100)}:-2:flags=lanczos", "-q:v", "2", MEDIA / "card" / f"{name}.jpg"])
    qr = EP / "素材" / "superman_artifact_qr.png"
    if qr.exists():
        shutil.copy(qr, MEDIA / "qr.png")
    total = sum(1 for x in scr if x)
    print("素材帧：" + "，".join(f"{k[0]}#{k[1]} {v} 张" for k, v in counts.items()) + f"；frames.js 共 {T['frames']} 帧，其中 {total} 帧是素材画面")


if __name__ == "__main__":
    main()
