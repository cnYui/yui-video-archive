# -*- coding: utf-8 -*-
"""收尾镜头：官网 Home Link 组件的 Connection 页签（Muse VM → Home WiFi → Home Link → 灯 / 传感器 / 扬声器，小圆点沿线跑）
→ homelink_conn_hl.mp4：缓慢推向左上角的云端（Muse VM），到 hl_t 秒时橙色框出云 + 服务器并贴上“Meta 的云”标签（对应收尾金句“大脑还在 Meta 的云上”）。
时间从 conn_schedule.json 读（配音出来后用真实时间重渲，约 15 秒）：{"dur": 6.0, "hl_t": 0.4}。"""
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W_DIR = Path(r"D:\大疆\独立视频\素材\2026-10_MuseGadgets开源\官网与仓库\widget")
OUT = Path(r"D:\大疆\独立视频\素材\2026-10_MuseGadgets开源\官网与仓库\homelink_conn_hl.mp4")
SCHED = Path(__file__).with_name("conn_schedule.json")
FPS, OW, OH = 30, 1096, 1080
ORANGE = (255, 79, 26)
SRC_RECT = (172, 100, 438, 482)                  # 云 + 服务器 + “Muse VM”标签在 1095×1080 帧里的位置
meta = json.loads((W_DIR / "meta.json").read_text(encoding="utf-8"))
con = {n: t for n, t in meta["connection"]}
FONT = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 44)
_cache = {}


def load(n):
    if n not in _cache:
        _cache[n] = Image.open(W_DIR / f"connection_{n:03d}.png").convert("RGB")
    return _cache[n]


def frame_at(tau):
    t_mod = tau % (max(con.values()) + 0.05)            # 录了约 7.1 s，更长就循环
    best = max((n for n, t in con.items() if t <= t_mod + 1e-6), default=0)
    return load(best)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def main():
    sch = json.loads(SCHED.read_text(encoding="utf-8")) if SCHED.exists() else {"dur": 6.0, "hl_t": 0.4}
    D, hl_t = sch["dur"], sch["hl_t"]
    n_frames = int(round(D * FPS))
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", str(OUT)], stdin=subprocess.PIPE)
    for i in range(n_frames):
        T = i / FPS
        im = frame_at(T)
        w, h = im.size
        z = 1.0 + 0.10 * ease(T / max(D, 0.1))               # 缓推到 1.10 倍
        cw, ch = w / z, h / z
        cx, cy = 0.5 + (0.30 - 0.5) * (1 - 1 / z), 0.5 + (0.36 - 0.5) * (1 - 1 / z)   # 中心慢慢挪向左上
        x0 = min(max(cx * w - cw / 2, 0), w - cw)
        y0 = min(max(cy * h - ch / 2, 0), h - ch)
        out = im.resize((OW, OH), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")
        a = ease((T - hl_t) / 0.35)
        if a > 0.01:
            k = OW / cw
            r = [(SRC_RECT[0] - x0) * k, (SRC_RECT[1] - y0) * k, (SRC_RECT[2] - x0) * k, (SRC_RECT[3] - y0) * k]
            ov = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            d.rounded_rectangle(r, radius=22, outline=ORANGE + (int(255 * a),), width=12)
            d.rounded_rectangle((r[0] - 12, r[1] - 12, r[2] + 12, r[3] + 12), radius=30, outline=ORANGE + (int(80 * a),), width=10)
            label = "Meta 的云"
            tw = d.textlength(label, font=FONT)
            lx, ly = r[0] + 8, r[3] + 18                       # 标签贴在框下沿
            d.rounded_rectangle((lx, ly, lx + tw + 36, ly + 70), radius=12, fill=ORANGE + (int(255 * a),))
            d.text((lx + 18, ly + 8), label, font=FONT, fill=(255, 255, 255, int(255 * a)))
            out = Image.alpha_composite(out, ov)
        ff.stdin.write(np.asarray(out.convert("RGB")).tobytes())
    ff.stdin.close(); ff.wait()
    print("done", OUT, D, "s", n_frames, "frames; hl at", hl_t)


if __name__ == "__main__":
    main()
