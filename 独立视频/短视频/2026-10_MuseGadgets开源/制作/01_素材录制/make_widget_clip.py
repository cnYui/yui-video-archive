# -*- coding: utf-8 -*-
"""把 Home Link 小组件的高清帧合成一段 mp4：Device 转台（步进，约 7.7 fps → 30 fps 重采样）→ What's inside（静帧缓推）→ Connection（小圆点沿线跑，7.3 fps）。
段与段之间交叉淡化 0.35 s；每段带缓慢推镜。输出 1096×1080、30 fps。"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

W_DIR = Path(r"D:\大疆\独立视频\素材\2026-10_MuseGadgets开源\官网与仓库\widget")
OUT = Path(r"D:\大疆\独立视频\素材\2026-10_MuseGadgets开源\官网与仓库\homelink_widget.mp4")
FPS, OW, OH = 30, 1096, 1080
meta = json.loads((W_DIR / "meta.json").read_text(encoding="utf-8"))
dev = {n: t for n, t in meta["device"]}
con = {n: t for n, t in meta["connection"]}
_cache = {}


def load(p):
    if p not in _cache:
        _cache[p] = Image.open(p).convert("RGB")
    return _cache[p]


def frame_at(seq_prefix, times, tau, t_start):
    """times: {n: t}；取不晚于 t_start+tau 的最近一帧。"""
    want = t_start + tau
    best = max((n for n, t in times.items() if t <= want + 1e-6), default=min(times))
    return load(W_DIR / f"{seq_prefix}_{best:03d}.png")


def kb(im, z0, z1, u, cx=0.5, cy=0.5):
    """缓推：u∈[0,1]；视野缩到 1/z，中心从画面中心慢慢挪向 (cx, cy)；亚像素裁切 + Lanczos。"""
    z = z0 + (z1 - z0) * u
    w, h = im.size
    cw, ch = w / z, h / z
    ccx = w / 2 + (cx * w - w / 2) * (1 - 1 / z) * 1.0
    ccy = h / 2 + (cy * h - h / 2) * (1 - 1 / z) * 1.0
    x0 = min(max(ccx - cw / 2, 0), w - cw)
    y0 = min(max(ccy - ch / 2, 0), h - ch)
    return im.resize((OW, OH), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def seg_device(tau, D):
    u = tau / D
    return kb(frame_at("device", dev, tau, dev[30]), 1.00, 1.07, u, 0.5, 0.5)


def seg_inside(tau, D):
    return kb(load(W_DIR / "inside.png"), 1.00, 1.16, tau / D, 0.36, 0.52)


def seg_conn(tau, D):
    return kb(frame_at("connection", con, tau, con[0]), 1.00, 1.08, tau / D, 0.52, 0.52)


XF = 0.35
SCHED = Path(__file__).with_name("widget_schedule.json")        # 配音出来后按 N06 的时刻排：{"segs": [Device 秒数, 内部 秒数, 连线 秒数]}（含交叉淡化的重叠）
_d = json.loads(SCHED.read_text(encoding="utf-8"))["segs"] if SCHED.exists() else [3.0, 4.5, 7.0]
segs = [("device", seg_device, _d[0]), ("inside", seg_inside, _d[1]), ("conn", seg_conn, _d[2])]
total = sum(d for _, _, d in segs) - XF * (len(segs) - 1)
starts, t = [], 0.0
for _, _, d in segs:
    starts.append(t); t += d - XF
n_frames = int(round(total * FPS))
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", str(OUT)], stdin=subprocess.PIPE)
for i in range(n_frames):
    T = i / FPS
    parts = []
    for (name, fn, D), s in zip(segs, starts):
        if s - 1e-9 <= T <= s + D + 1e-9:
            parts.append((s, D, fn(min(max(T - s, 0), D), D)))
    if len(parts) == 1:
        arr = np.asarray(parts[0][2])
    else:                                         # 交叉淡化：后一段的淡入进度
        (s0, D0, a), (s1, D1, b) = parts[0], parts[1]
        k = min(max((T - s1) / XF, 0), 1)
        arr = (np.asarray(a).astype(np.float32) * (1 - k) + np.asarray(b).astype(np.float32) * k).astype(np.uint8)
    ff.stdin.write(arr.tobytes())
ff.stdin.close(); ff.wait()
print("done", OUT, round(total, 2), "s", n_frames, "frames; segment starts", [round(x, 2) for x in starts])
