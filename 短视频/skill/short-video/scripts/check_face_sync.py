# -*- coding: utf-8 -*-
r"""核对成片里出镜小窗的脸和口播原片是不是帧对帧（没漂、没错位）。

  python check_face_sync.py <本条目录> [成片.mp4] [--n 6]

在成片的单框（居中 360×360、不缩放）时刻取小窗中央 60%，和 face.json 里那段口播（同样的 start / crop / 镜像）前后 ±8 帧逐帧比，找最像的帧。
结果 偏移 0 = 对得上，±1 以内正常（seek 取整）；超过 2 帧要查：compose 之前的 base 帧数是否变了、口播剪辑和 timeline 是不是同一版。
只比单框时刻：双框 / 大窗的小窗缩到 240，缩放后的像素和原片对不上（比出来差值大、偏移乱跳，不是不同步）。
2026-10-06《Claude官方教程》第 1 期出镜版：9 个时刻比，偏移全是 0，片尾少了 3 帧的合成也没有漂。
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compose_face as cf  # noqa: E402


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    ep = Path(args[0])
    slug = json.loads((ep / "台本" / "录制稿.json").read_text(encoding="utf-8"))["slug"]
    vid = Path(args[1]) if len(args) > 1 and not args[1].startswith("--") else ep / f"{slug}_成片.mp4"
    n_pts = int(args[args.index("--n") + 1]) if "--n" in args else 6
    here = ep / "制作" / "00_整片"
    if not vid.is_file():                              # finish.py 之前：compose_face.py 的输出 整片_v1.mp4 也能核
        alt = here / "整片_v1.mp4"
        if not alt.is_file():
            print(f"找不到 {vid.name}，也没有 {alt.name}：先跑 compose_face.py / finish.py（或把成片路径作第二个参数）")
            return 2
        print(f"找不到 {vid.name}，改用 {alt.name}（finish.py 之前的整片）")
        vid = alt
    cfg = json.loads((here / "face.json").read_text(encoding="utf-8"))
    tl = json.loads((here / "timeline.json").read_text(encoding="utf-8"))
    size = int(cfg.get("size", 360))
    x, y, _ = cf.POS["single"]["center"]
    c = cfg.get("crop", {"cx": 0.515, "cy": 0.449, "side": 0.787})
    mirror = ",hflip" if cfg.get("mirror", True) else ""
    start = float(cfg.get("start", 0) or 0)
    tmp = ep / "_sync_tmp"
    tmp.mkdir(exist_ok=True)

    # 单框时刻：mode == one（多窗版式）或整条 layout == single
    cand = []
    for sg in tl["segs"]:
        mode = (tl["clips"].get(sg["id"]) or {}).get("mode")
        if mode == "one" or (mode is None and tl.get("layout") == "single"):
            cand.append((sg["s"] + 1.0, sg["e"] - 1.0))
    cand = [(a, b) for a, b in cand if b - a > 1.0]
    if not cand:
        print("没有单框场景可比（整条都是双框 / 大窗）")
        return 0
    times = [round((cand[int(i * (len(cand) - 1) / max(1, n_pts - 1))][0] + cand[int(i * (len(cand) - 1) / max(1, n_pts - 1))][1]) / 2, 2) for i in range(n_pts)]
    times = sorted(set(times))

    def grab(src, t, vf, out, pre=""):
        subprocess.run(["ffmpeg", "-v", "error", "-y", *(["-ss", f"{t:.4f}"] if t else []), "-i", str(src), "-frames:v", "1", "-vf", vf, str(out)], check=True)
        return np.asarray(Image.open(out).convert("L")).astype(float)

    c0, cs = int(size * 0.2), int(size * 0.6)
    crop = f"crop=w='in_h*{c['side']}':h='in_h*{c['side']}':x='in_w*{c['cx']}-in_h*{c['side']}/2':y='in_h*{c['cy']}-in_h*{c['side']}/2'"
    worst = 0
    for t in times:
        n0 = int(round(t * 30))
        a = grab(vid, (n0 - 0.5) / 30, f"crop={cs}:{cs}:{x + c0}:{y + c0},scale=48:48", tmp / "a.png")
        best = None
        for k in range(-8, 9):
            ref = grab(cfg["src"], start + (n0 + k - 0.5) / 30, f"fps=30,{crop},scale={size}:{size}:flags=lanczos{mirror},crop={cs}:{cs}:{c0}:{c0},scale=48:48", tmp / "b.png")
            d = float(np.abs(a - ref).mean())
            if best is None or d < best[0]:
                best = (d, k)
        worst = max(worst, abs(best[1]))
        print(f"t={t:7.2f}s  最像的帧偏移 {best[1]:+d}（差 {best[0]:.1f}）")
    print(f"最大偏移 {worst} 帧" + ("" if worst <= 1 else "  ⚠ 超过 1 帧，查一下"))
    for f in tmp.glob("*.png"):
        f.unlink()
    try:
        tmp.rmdir()
    except OSError:
        pass
    return 0 if worst <= 2 else 1


if __name__ == "__main__":
    sys.exit(main())
