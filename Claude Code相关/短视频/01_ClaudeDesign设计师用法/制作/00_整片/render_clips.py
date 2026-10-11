# -*- coding: utf-8 -*-
"""把 timeline.json 里的每个子镜头从 4K 原片裁切 + 变速成小片段（972×547、30 fps、几乎无损），再把上下两路各自接成 build/top.mp4、build/bottom.mp4。

  python render_clips.py            # 渲染（参数没变的片段用缓存）
  python render_clips.py --sheet    # 另外出检查联系表 build/clip_sheet_*.png（每个子镜头首 / 中 / 尾三帧，标着句号、原片秒数、速度）
  python render_clips.py --force    # 全部重渲

裁切：shots.json 里 crop = [中心x, 中心y, 宽]（16:9，1920×1080 坐标；4K 原片按 2 倍取，超出画面会夹回来）；平移 = [[起], [终]]（同宽，随输出时间线性移动）。
变速：setpts=(PTS-STARTPTS)/speed → fps=30（丢 / 补帧）→ crop → scale；定格（hold）用 tpad 复制最后一帧。
"""
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import config as C

BUILD = C.HERE / "build"
CLIPS = BUILD / "clips"
WORKERS = 2


def crop_rect(cx, cy, w):
    """1080p 坐标的 [中心x, 中心y, 宽] → 4K 像素的 (x, y, w, h)（偶数，夹在画面里）。"""
    W4 = int(round(2 * w / 2)) * 2
    H4 = int(round(W4 * 9 / 16 / 2)) * 2
    W4, H4 = min(W4, 3840), min(H4, 2160)
    x = int(round(2 * cx - W4 / 2))
    y = int(round(2 * cy - H4 / 2))
    x = max(0, min(3840 - W4, x))
    y = max(0, min(2160 - H4, y))
    return x, y, W4, H4


def build_cmd(sub, out):
    a, b = sub["src"]
    n, speed = sub["nframes"], sub["speed"]
    dur = n / C.FPS
    crop = sub["crop"]
    if isinstance(crop[0], list):
        (x0, y0, W4, H4), (x1, y1, _, _) = crop_rect(*crop[0]), crop_rect(*crop[1])
        cexp = f"crop={W4}:{H4}:x='{x0}+({x1}-{x0})*min(t/{dur:.4f},1)':y='{y0}+({y1}-{y0})*min(t/{dur:.4f},1)'"
    else:
        x0, y0, W4, H4 = crop_rect(*crop)
        cexp = f"crop={W4}:{H4}:{x0}:{y0}"
    vf = f"setpts=(PTS-STARTPTS)/{speed},fps={C.FPS},{cexp},scale={C.INNER_W}:{C.INNER_H}:flags=lanczos,tpad=stop_mode=clone:stop_duration=1,format=yuv420p"
    take = (b - a) + 0.3
    return ["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{take:.3f}", "-i", str(C.SRC_4K), "-vf", vf, "-frames:v", str(n),
            "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(C.CRF_CLIP), "-pix_fmt", "yuv420p", "-r", str(C.FPS), "-g", str(C.FPS), str(out)]


def key(sub):
    return hashlib.md5(json.dumps([sub["src"], sub["crop"], sub["nframes"], sub["speed"], sub["hold"], str(C.FPS), C.INNER_W, C.INNER_H], sort_keys=True).encode()).hexdigest()[:12]


def run_one(job):
    sub, out = job
    subprocess.run(build_cmd(sub, out), check=True)
    return out


def concat(files, dst):
    lst = BUILD / (dst.stem + ".txt")
    lst.write_text("\n".join(f"file '{f.relative_to(BUILD).as_posix()}'" for f in files) + "\n", encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(dst)], check=True)


def nframes(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    return int(r.stdout.strip())


def sheet(jobs):
    """每个子镜头首 / 中 / 尾三帧一行，按 7 行一张图。"""
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 20)
    tw, th = 486, 273
    for track in ("top", "bottom"):
        rows = [(s, p) for t, s, p in jobs if t == track]
        for part in range(0, len(rows), 7):
            chunk = rows[part: part + 7]
            im = Image.new("RGB", (tw * 3 + 20, (th + 26) * len(chunk)), (30, 30, 30))
            d = ImageDraw.Draw(im)
            for r, (s, p) in enumerate(chunk):
                n = s["nframes"]
                d.text((6, r * (th + 26) + 2), f"{s['_label']}  src {s['src'][0]:.2f}–{s['src'][1]:.2f}  {s['speed']:.2f}×  {n} 帧  {s['note'][:40]}", fill=(255, 220, 0), font=font)
                for c, fi in enumerate((0, n // 2, n - 1)):
                    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vf", f"select=eq(n\\,{fi}),scale={tw}:{th}", "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
                    import io
                    im.paste(Image.open(io.BytesIO(raw)).convert("RGB"), (c * (tw + 10), r * (th + 26) + 24))
            out = BUILD / f"clip_sheet_{track}_{part // 7 + 1}.png"
            im.save(out)
            print(out)


def main():
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    CLIPS.mkdir(parents=True, exist_ok=True)
    cache_p = CLIPS / "_cache.json"
    cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() and "--force" not in sys.argv else {}
    jobs, todo = [], []
    for r in tl["lines"]:
        for track in ("top", "bottom"):
            for k, s in enumerate(r["tracks"][track]):
                s["_label"] = f"{r['id']} {track}{k}"
                out = CLIPS / f"{r['id']}_{track}{k}.mp4"
                jobs.append((track, s, out))
                if cache.get(out.name) != key(s) or not out.exists():
                    todo.append((s, out))
    print(f"{len(jobs)} 个子镜头，要渲染 {len(todo)} 个（缓存 {len(jobs) - len(todo)} 个）")
    with ThreadPoolExecutor(WORKERS) as ex:
        for out in ex.map(run_one, todo):
            print("  ok", out.name, flush=True)
    for s, out in todo:
        cache[out.name] = key(s)
    cache_p.write_text(json.dumps(cache, indent=1), encoding="utf-8")
    for track in ("top", "bottom"):
        files = [out for t, s, out in jobs if t == track]
        dst = BUILD / f"{track}.mp4"
        concat(files, dst)
        n = nframes(dst)
        print(f"{dst.name}：{n} 帧（时间线 {tl['frames']} 帧）" + ("" if n == tl["frames"] else "  ⚠ 帧数对不上"))
    if "--sheet" in sys.argv:
        sheet(jobs)


if __name__ == "__main__":
    main()
