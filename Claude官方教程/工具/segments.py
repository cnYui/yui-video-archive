# -*- coding: utf-8 -*-
"""把官方教学视频切成“镜头段”并猜每段是什么（讲师 / 终端 / 图示 / 标题卡 / 其他），出一张每段一个缩略图的分镜表 + json，选画面时用。

  python segments.py <视频.mp4> [输出目录]        输出 <目录>/<视频名>.json 和 <视频名>_分镜.png
  python segments.py --all                         素材\2026-10_ClaudeAcademy\视频\*.mp4 全部，输出到 素材\2026-10_ClaudeAcademy\分镜\

做法：每秒 4 帧取小图，按颜色粗分类（讲师镜头背景是暖橙色、终端是深色、图示是近白、标题卡是米色）；硬切点用 ffmpeg 场景检测取精确时间；
类别变化（包括溶解过渡）按 0.25 s 粒度取。每段给出 safe_in / safe_out（离边界留 0.12 s；类别变化处留 0.4 s），选画面的范围写在 [safe_in, safe_out] 里面，就不会带上转场帧。
分类只是导航用的猜测，要看缩略图确认；段内内容变了（终端里换了一屏）看不出来的，要在 8 fps 的联系表里再看。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FPS = 4
W, H = 160, 90
ROOT = Path(r"D:\大疆\Claude官方教程\素材\2026-10_ClaudeAcademy")


def duration(v):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(v)],
                                check=True, capture_output=True, text=True).stdout.strip())


def small_frames(v):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(v), "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         check=True, capture_output=True).stdout
    n = len(raw) // (W * H * 3)
    return np.frombuffer(raw, np.uint8)[: n * W * H * 3].reshape(n, H, W, 3)


def classify(fr):
    f = fr.astype(np.int16)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    lum = (0.299 * r + 0.587 * g + 0.114 * b).mean()
    warm = ((r > g + 12) & (g > b + 8) & ((r - b) > 45)).mean()
    sat_std = f.std()
    beige = (abs(r.mean() - 233) < 14 and abs(g.mean() - 226) < 14 and abs(b.mean() - 214) < 16 and sat_std < 40)
    if warm > 0.22 and lum < 150:
        return "face"
    if beige:
        return "card"
    if lum > 232:
        return "diagram"
    if lum < 75:
        return "term"
    return "other"


def hard_cuts(v, thr=0.32):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(v), "-vf", f"select='gt(scene,{thr})',showinfo", "-an", "-f", "null", "-"], capture_output=True, text=True)
    return [float(m.group(1)) for m in re.finditer(r"pts_time:([\d.]+)", p.stderr)]


def build(v):
    dur = duration(v)
    fr = small_frames(v)
    types = [classify(x) for x in fr]
    # 类别变化边界（0.25 s 粒度）
    bounds = {0.0: "start"}
    for i in range(1, len(types)):
        if types[i] != types[i - 1]:
            bounds[round(i / FPS, 3)] = "type"
    for t in hard_cuts(v):
        # 用精确的硬切时间替换 0.3 s 内的类别变化边界
        for k in [k for k, why in bounds.items() if why == "type" and abs(k - t) < 0.3]:
            bounds.pop(k)
        bounds[round(t, 3)] = "cut"
    ts = sorted(bounds)
    # 合并太短的段（< 0.6 s，多半是转场帧）
    segs = []
    for i, t in enumerate(ts):
        e = ts[i + 1] if i + 1 < len(ts) else dur
        segs.append({"s": t, "e": round(e, 3), "why": bounds[t]})
    merged = []
    for sg in segs:
        if merged and (sg["e"] - sg["s"]) < 0.6:
            merged[-1]["e"] = sg["e"]
        else:
            merged.append(sg)
    for sg in merged:
        i0, i1 = int(sg["s"] * FPS), max(int(sg["s"] * FPS) + 1, int(sg["e"] * FPS))
        ty = [types[i] for i in range(i0, min(i1, len(types)))] or ["other"]
        sg["type"] = max(set(ty), key=ty.count)
        m_s = 0.12 if sg["why"] == "cut" else 0.4
        sg["safe_in"] = round(sg["s"] + m_s, 2)
        sg["safe_out"] = round(sg["e"] - 0.12, 2)
        sg["dur"] = round(sg["e"] - sg["s"], 2)
    # 相邻同类且中间是“类别变化”边界的段不再合并（保持原样，导航用）
    return dur, merged


def thumb(v, t, w=320):
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(v), "-frames:v", "1", "-vf", f"scale={w}:-1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(out)).convert("RGB")


def sheet(v, segs, path, cols=5, w=320):
    ims = [thumb(v, (sg["s"] + sg["e"]) / 2, w) for sg in segs]
    h = ims[0].size[1]
    rows = (len(ims) + cols - 1) // cols
    img = Image.new("RGB", (cols * w, rows * h), (20, 20, 20))
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
    d = ImageDraw.Draw(img)
    for i, (im, sg) in enumerate(zip(ims, segs)):
        x, y = (i % cols) * w, (i // cols) * h
        img.paste(im, (x, y))
        lab = f"#{i} {sg['s']:.1f}-{sg['e']:.1f} {sg['type']}"
        d.rectangle([x + 3, y + 3, x + 8 + 11 * len(lab), y + 30], fill=(0, 0, 0))
        d.text((x + 8, y + 5), lab, fill=(255, 220, 0), font=font)
    img.save(path)


def run(v, outdir):
    v = Path(v)
    outdir.mkdir(parents=True, exist_ok=True)
    dur, segs = build(v)
    for i, sg in enumerate(segs):
        sg["i"] = i
    (outdir / (v.stem + ".json")).write_text(json.dumps({"video": v.name, "duration": round(dur, 3), "segments": segs}, ensure_ascii=False, indent=1), encoding="utf-8")
    sheet(v, segs, outdir / (v.stem + "_分镜.png"))
    print(f"{v.name}: {dur:.1f}s -> {len(segs)} 段  ({', '.join(f'{t}:{sum(1 for s in segs if s['type'] == t)}' for t in sorted({s['type'] for s in segs}))})")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        for v in sorted((ROOT / "视频").glob("*.mp4")):
            run(v, ROOT / "分镜")
    else:
        run(sys.argv[1], Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "分镜")
