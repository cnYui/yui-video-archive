# -*- coding: utf-8 -*-
"""按 build/timeline.json 渲染每一段（passage）的整帧小片 build/scenes/<id>.mp4：先把每个子镜头从原片裁切 + 变速成 972×546 的小片段（有缓存），再和该段的底图合成。

  python render_scenes.py                 # 全部（参数没变的用缓存）
  python render_scenes.py D05 S02         # 只渲这几段
  python render_scenes.py --force         # 全部重渲
  python render_scenes.py --sheet D05     # 另外给这几段出子镜头检查联系表 build/sheets/<id>.png（每个子镜头首 / 中 / 尾三帧）

裁切：c = (中心x, 中心y, 宽)，16:9，按 1920×1080 画面算（Design 原片是 4K，自动 ×2）；(起, 终) 两个三元组 = 同宽平移（视频）或平移 + 缩放（静帧 freeze）。
orig / broll：ffmpeg 输入 seek + 变速 + crop + scale；片段比需要的短就定格最后一帧（tpad clone）。freeze：先抽一帧原片，再用 OpenCV 逐帧裁切缩放（缓动），管道喂给 x264。
合成：底图（循环）→ 上框（圆角蒙版）→ 下框 → 来源角标，一次 ffmpeg，x264 crf 14，整段帧数 = timeline 里的 nf。
"""
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

import config as C

TL = json.loads((C.BUILD / "timeline.json").read_text(encoding="utf-8"))
CLIPS = C.BUILD / "clips"
SCENES = C.BUILD / "scenes"
FRAMES = CLIPS / "_frames"
NATIVE_SIZE = {"design": (3840, 2160), "slides": (1920, 1080)}
IW, IH = C.INNER_W, C.INNER_H


def md5(obj):
    return hashlib.md5(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()[:12]


def src_sig(src):
    st = C.SRC[src].stat()
    return [src, st.st_size, int(st.st_mtime)]


def box(src, c):
    """c = (cx, cy, w)（1080p 坐标）→ 原片像素的 (x, y, w, h)，16:9、偶数、夹在画面里。"""
    k = C.NATIVE[src]
    fw, fh = NATIVE_SIZE[src]
    w = int(round(k * c[2] / 2)) * 2
    h = int(round(w * 9 / 16 / 2)) * 2
    w, h = min(w, fw), min(h, fh)
    x = max(0, min(fw - w, int(round(k * c[0] - w / 2))))
    y = max(0, min(fh - h, int(round(k * c[1] - h / 2))))
    return x, y, w, h


def is_pair(c):
    return isinstance(c[0], (tuple, list))


def clip_name(sub):
    return f"{sub['kind']}_{md5([sub, src_sig(sub['src']), C.FPS, IW, IH])}.mp4"


def video_cmd(sub, out):
    src = sub["src"]
    speed, nf = sub["speed"], sub["nf"]
    c = sub["c"]
    if is_pair(c):
        (x0, y0, w0, h0), (x1, y1, w1, h1) = box(src, c[0]), box(src, c[1])
        if (w0, h0) != (w1, h1):
            raise ValueError(f"视频子镜头不支持变宽缩放（只有 freeze 可以）：{sub}")
        dur = nf / C.FPS
        cexp = f"crop={w0}:{h0}:x='{x0}+({x1}-{x0})*min(t/{dur:.4f},1)':y='{y0}+({y1}-{y0})*min(t/{dur:.4f},1)'"
    else:
        x, y, w, h = box(src, c)
        cexp = f"crop={w}:{h}:{x}:{y}"
    vf = f"setpts=(PTS-STARTPTS)/{speed},fps={C.FPS},{cexp},scale={IW}:{IH}:flags=lanczos,tpad=stop_mode=clone:stop_duration=8,setsar=1,format=yuv420p"
    return ["ffmpeg", "-v", "error", "-y", "-ss", f"{sub['t']:.3f}", "-t", f"{max(sub['src_len'], 0.05):.3f}", "-i", str(C.SRC[src]), "-vf", vf, "-frames:v", str(nf),
            "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-pix_fmt", "yuv420p", "-r", str(C.FPS), "-g", str(C.FPS), str(out)]


def freeze_clip(sub, out):
    src, nf = sub["src"], sub["nf"]
    FRAMES.mkdir(parents=True, exist_ok=True)
    png = FRAMES / f"{src}_{sub['t']:.3f}.png"
    if not png.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sub['t']:.3f}", "-i", str(C.SRC[src]), "-frames:v", "1", str(png)], check=True)
    img = cv2.imread(str(png))
    c = sub["c"]
    c0, c1 = (c[0], c[1]) if is_pair(c) else (c, c)
    k = C.NATIVE[src]
    fh, fw = img.shape[:2]
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{IW}x{IH}", "-r", str(C.FPS), "-i", "-",
                             "-vf", "scale=out_color_matrix=bt709:out_range=tv,setsar=1,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "12",
                             "-pix_fmt", "yuv420p", "-r", str(C.FPS), "-g", str(C.FPS), str(out)], stdin=subprocess.PIPE)
    for i in range(nf):
        u = (i + 0.5) / nf
        s = u * u * (3 - 2 * u)
        cx = c0[0] + (c1[0] - c0[0]) * s
        cy = c0[1] + (c1[1] - c0[1]) * s
        w = c0[2] + (c1[2] - c0[2]) * s
        wn = max(8, int(round(k * w)))
        hn = int(round(wn * 9 / 16))
        x = int(round(k * cx - wn / 2))
        y = int(round(k * cy - hn / 2))
        x, y = max(0, min(fw - wn, x)), max(0, min(fh - hn, y))
        crop = img[y: y + hn, x: x + wn]
        proc.stdin.write(cv2.resize(crop, (IW, IH), interpolation=cv2.INTER_AREA).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"freeze 渲染失败：{sub}")


def render_clip(sub):
    out = CLIPS / clip_name(sub)
    if out.exists() and out.stat().st_size > 0:
        return out, False
    tmp = out.with_suffix(".part.mp4")
    if sub["kind"] == "freeze":
        freeze_clip(sub, tmp)
    else:
        subprocess.run(video_cmd(sub, tmp), check=True)
    tmp.replace(out)
    return out, True


def scene_cmd(p, bg_idx, top, bot, out):
    inputs = ["-loop", "1", "-framerate", str(C.FPS), "-i", str(C.BUILD / f"bg_{bg_idx}.png")]
    for f in top + bot:
        inputs += ["-i", str(f)]
    nm = len(top) + len(bot) + 1
    inputs += ["-loop", "1", "-framerate", str(C.FPS), "-i", str(C.BUILD / "mask_inner.png"),
               "-loop", "1", "-framerate", str(C.FPS), "-i", str(C.BUILD / "badge.png")]
    mask_i, badge_i = nm, nm + 1

    def chain(idx, label):
        ids = list(range(idx, idx + (len(top) if label == "t" else len(bot))))
        pre = "".join(f"[{i}:v]setsar=1[{label}{n}];" for n, i in enumerate(ids))
        if len(ids) == 1:
            return pre + f"[{label}0]null[{label}c];"
        return pre + "".join(f"[{label}{n}]" for n in range(len(ids))) + f"concat=n={len(ids)}:v=1:a=0[{label}c];"

    g = f"[0:v]scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[bg];[{mask_i}:v]format=gray,split=2[m1][m2];"
    g += chain(1, "t") + chain(1 + len(top), "b")
    g += "[tc]format=yuv420p[t0];[t0][m1]alphamerge[t];[bc]format=yuv420p[b0];[b0][m2]alphamerge[b];"
    g += f"[bg][t]overlay={C.BOX_X + C.PAD}:{C.TOP_Y + C.PAD}:format=auto[v1];[v1][b]overlay={C.BOX_X + C.PAD}:{C.BOT_Y + C.PAD}:format=auto[v2];"
    g += f"[v2][{badge_i}:v]overlay=0:0:format=auto[v3];[v3]format=yuv420p[v]"
    return ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", g, "-map", "[v]", "-frames:v", str(p["nf"]), "-r", str(C.FPS),
            "-c:v", "libx264", "-preset", "fast", "-crf", str(C.CRF_SCENE), "-pix_fmt", "yuv420p", "-g", str(C.FPS),
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", str(out)]


def render_scene(p, chips, force):
    bg_idx = chips.index(p["chip"])
    top_subs, bot_subs = p["tracks"]["top"], p["tracks"]["bottom"]
    top = [render_clip(s)[0] for s in top_subs]
    bot = [render_clip(s)[0] for s in bot_subs]
    key = md5([p["nf"], bg_idx, [clip_name(s) for s in top_subs], [clip_name(s) for s in bot_subs],
               [f.stat().st_size for f in (C.BUILD / f"bg_{bg_idx}.png", C.BUILD / "mask_inner.png", C.BUILD / "badge.png")],
               [(C.BUILD / f"bg_{bg_idx}.png").stat().st_mtime_ns, (C.BUILD / "badge.png").stat().st_mtime_ns]])
    out = SCENES / f"{p['id']}.mp4"
    keyf = SCENES / f"{p['id']}.key"
    if not force and out.exists() and keyf.exists() and keyf.read_text() == key:
        return p["id"], False
    tmp = out.with_suffix(".part.mp4")
    subprocess.run(scene_cmd(p, bg_idx, top, bot, tmp), check=True)
    tmp.replace(out)
    keyf.write_text(key)
    return p["id"], True


def sheet(p):
    """每个子镜头首 / 中 / 尾三帧（上框 / 下框各一行一行排）。"""
    from PIL import Image, ImageDraw, ImageFont
    import io
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 18)
    tw, th = 324, 182
    rows = []
    for track in ("top", "bottom"):
        for k, s in enumerate(p["tracks"][track]):
            rows.append((track, k, s))
    im = Image.new("RGB", (tw * 3 + 20, (th + 24) * len(rows)), (30, 30, 30))
    d = ImageDraw.Draw(im)
    for r, (track, k, s) in enumerate(rows):
        n = s["nf"]
        d.text((6, r * (th + 24) + 2), f"{p['id']} {track}{k} {s['kind']} src {s['src']} t={s['t']:.2f} spd {s['speed']:.2f} nf {n} hold {s['hold']} c={s['c']}", fill=(255, 220, 0), font=font)
        clip = CLIPS / clip_name(s)
        for c, fi in enumerate((0, n // 2, n - 1)):
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(clip), "-vf", f"select=eq(n\\,{fi}),scale={tw}:{th}", "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                                 capture_output=True, check=True).stdout
            im.paste(Image.open(io.BytesIO(raw)).convert("RGB"), (c * (tw + 10), r * (th + 24) + 22))
    (C.BUILD / "sheets").mkdir(exist_ok=True)
    out = C.BUILD / "sheets" / f"{p['id']}.png"
    im.save(out)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    CLIPS.mkdir(parents=True, exist_ok=True)
    SCENES.mkdir(parents=True, exist_ok=True)
    chips = TL["chips"]
    ps = [p for p in TL["passages"] if not args or p["id"] in args]
    # 先并行渲子镜头（去重），再并行合成各段
    subs = {}
    for p in ps:
        for tr in p["tracks"].values():
            for s in tr:
                subs[clip_name(s)] = s
    todo = [s for n, s in subs.items() if not (CLIPS / n).exists()]
    print(f"{len(ps)} 段，{len(subs)} 个子镜头，要渲 {len(todo)} 个")
    with ThreadPoolExecutor(3) as ex:
        for out, _ in ex.map(render_clip, todo):
            print("  clip", out.name, flush=True)
    with ThreadPoolExecutor(2) as ex:
        for pid, did in ex.map(lambda p: render_scene(p, chips, force), ps):
            print("  scene", pid, "（新渲）" if did else "（缓存）", flush=True)
    if "--sheet" in sys.argv:
        for p in ps:
            print(sheet(p))


if __name__ == "__main__":
    main()
