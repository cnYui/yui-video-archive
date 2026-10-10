# -*- coding: utf-8 -*-
"""按时间轴给每一帧准备好画面素材，并给录屏打码。输出 media/ 和 frames.js。

  python prep_frames.py            抽帧 + 打码 + 静帧 + 图片，写 frames.js
  python prep_frames.py --check    只出打码检查图（media/_check_*.png），不写 frames.js

打码（2026-10-01 逐帧看过素材后定的；用户的邮箱、别人能拿去用的码、私人聊天标题都不能上公开视频）：
- PC 录屏：0–45 s 只有 Google 搜索和 Pockyt Shop 页面，没有私人信息，用原片。
  79–93 s 是 Gmail：标签页标题带用户的 Gmail 地址，列表里有两张礼品卡的卡号和一个旧验证码，邮件正文是完整卡号；
  画面一直在缩放、滚动，逐帧跟踪不可靠，所以这一段换成三张打码静帧（列表 78.8 s、邮件 92.0 s、邮件放大 89.0 s），页面里做推近。
- 手机 M1139（兑换）：Apple 账户页的账户名、Game Center 昵称（4.2–7.0 s，跟着“余额”那行定位）。
- 手机 M1140（Claude）：首页问候语里的名字（0–0.7 s）、侧栏“最近的项目”聊天标题（0.55–2.15 s）、
  设置页的账号邮箱（2.0–6.4 s，模板匹配跟踪）。
- 苹果内购截图（04）：账户邮箱。
手机原片发灰（白色只有 193 左右），抽帧时拉一下色阶（白 → 255）。
"""
import json
import subprocess
import sys
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
REC = EP / "素材" / "录屏"
SHOT = EP / "素材" / "截图"
MEDIA = HERE / "media"
FPS = 30
SW, SH = 1636, 920        # 演示区放大后的实际像素（页面里按 1474×829 写、整体 scale 1.1099）
SRC = {"PC1139": REC / "PC1139_买礼品卡.mp4", "M1139": REC / "M1139_兑换代码.mp4", "M1140": REC / "M1140_Claude订阅.mp4"}
LEVELS = "colorlevels=rimax=0.765:gimax=0.765:bimax=0.775"


def tl():
    return json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + [str(a) for a in args], check=True)


def mosaic(img, x0, y0, x1, y1, block=None):
    """打码：先重度高斯模糊再马赛克（字形完全看不出来）。坐标按图片像素，超出边界自动裁掉。"""
    h, w = img.shape[:2]
    x0, y0, x1, y1 = max(0, int(x0)), max(0, int(y0)), min(w, int(x1)), min(h, int(y1))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return
    roi = img[y0:y1, x0:x1]
    k = max(3, int(min(y1 - y0, 60) * 0.6) | 1)
    roi = cv2.GaussianBlur(roi, (k, k), 0)
    b = block or max(8, (y1 - y0) // 3)
    small = cv2.resize(roi, (max(1, (x1 - x0) // b), max(1, (y1 - y0) // b)), interpolation=cv2.INTER_AREA)
    img[y0:y1, x0:x1] = cv2.resize(small, (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST)


# ─────────────────────────────── PC 录屏
def pc_live(T):
    """演示①里用原片的片段：每段按 30 fps 抽成演示区大小。返回 {成片帧号: 文件名}。"""
    d = MEDIA / "scr"
    d.mkdir(parents=True, exist_ok=True)
    pcs = [p for p in T["pc"]["pieces"] if p["live"]]
    jobs = []
    for k, p in enumerate(pcs):
        jobs.append((k, p))

    def work(j):
        k, p = j
        for f in d.glob(f"pc{k:02d}_*.jpg"):
            f.unlink()
        ff(["-ss", f"{p['src0']:.3f}", "-i", SRC["PC1139"], "-t", f"{p['src1'] - p['src0'] + 0.2:.3f}", "-an", "-filter_threads", "1",
            "-vf", f"fps={FPS},scale={SW}:{SH}:flags=lanczos", "-q:v", "3", "-start_number", "0", d / f"pc{k:02d}_%05d.jpg"])
        return k, len(list(d.glob(f"pc{k:02d}_*.jpg")))

    with ThreadPoolExecutor(4) as ex:
        counts = dict(ex.map(work, jobs))
    man = {}
    seg = next(x for x in T["segs"] if x["id"] == "S6")
    for n in range(int(round(seg["s"] * FPS)), int(round(seg["e"] * FPS))):
        t = interp(T["pc"]["map"], n / FPS)            # v2：录屏按新配音逐句伸缩，换算回剪好的录屏口播里的时间
        for k, p in enumerate(pcs):
            if p["out0"] <= t < p["out1"]:
                i = min(counts[k] - 1, int(round((t - p["out0"]) * FPS)))
                man[n] = f"scr/pc{k:02d}_{i:05d}.jpg"
                break
    print(f"录屏原片：{len(pcs)} 段，{sum(counts.values())} 张，用到 {len(man)} 帧")
    return man


# 打码静帧：时刻、要打码的框（原片 1920×1080 像素）
STILLS = {
    "still_list": (78.8, [(676, 133, 846, 158),            # 标签页标题（带 Gmail 地址）
                          (1100, 355, 1664, 481)]),         # 列表摘要的后半截：两张卡的卡号、旧验证码
    "still_mail": (92.0, [(660, 116, 832, 140),            # 标签页标题
                          (1046, 679, 1196, 703)]),         # 礼品卡号
    "still_zoom": (89.0, [(700, 604, 954, 652)]),          # 放大后的礼品卡号
}


def pc_stills():
    for name, (t, boxes) in STILLS.items():
        tmp = MEDIA / f"_{name}.png"
        ff(["-ss", f"{t:.3f}", "-i", SRC["PC1139"], "-frames:v", "1", tmp])
        img = cv2.imread(str(tmp))
        for b in boxes:
            mosaic(img, *b)
        cv2.imwrite(str(MEDIA / f"{name}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 94])
        tmp.unlink()
    print("打码静帧：", ", ".join(STILLS))


# ─────────────────────────────── 手机录屏
def phone_extract(src):
    d = MEDIA / "ph"
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob(f"{src}_*.jpg"):
        f.unlink()
    ff(["-i", SRC[src], "-an", "-vf", f"fps={FPS},{LEVELS}", "-q:v", "2", "-start_number", "0", d / f"{src}_%05d.jpg"])
    return sorted(d.glob(f"{src}_*.jpg"))


def match(gray, tmpl, thr):
    r = cv2.matchTemplate(gray, tmpl, cv2.TM_CCOEFF_NORMED)
    _, mx, _, loc = cv2.minMaxLoc(r)
    return (loc, mx) if mx >= thr else (None, mx)


def blur_m1139(files):
    """Apple 账户页：账户名、Game Center 昵称。用“余额：US$x.xx”那行定位（页面会滚动）。"""
    ref = cv2.imread(str(files[132]))                       # 4.4 s：余额那行在 y≈524（抽出来的帧，不是 -ss 取的那张）
    tmpl = cv2.cvtColor(ref[506:542, 190:402], cv2.COLOR_BGR2GRAY)
    log = []
    for i, f in enumerate(files):
        t = i / FPS
        if not 3.4 <= t <= 7.4:
            continue
        img = cv2.imread(str(f))
        loc, sc = match(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), tmpl, 0.72)
        Y = None if loc is None else loc[1] + 18            # 余额那行的中线；账户名 Y-280…Y-175，Game Center Y-145…Y-55
        if Y is not None and Y - 24 > 192:
            mosaic(img, 28, max(192, Y - 292), 566, Y - 24, block=14)
        # 账户页开着的时候（4.15–6.9 s），账户名会滚到半透明的标题栏底下透出来：
        # 两行还在标题栏下面经过（余额 ≤ 484 或者已经找不到）就连标题一起盖（只留左边的图标和右边的关闭键），否则只盖右半边
        if 4.15 <= t <= 6.9:
            mosaic(img, 85 if (Y is None or Y <= 484) else 232, 90, 500, 192, block=14)
        cv2.imwrite(str(f), img, [cv2.IMWRITE_JPEG_QUALITY, 92])
        log.append((round(t, 2), "无" if loc is None else loc[1] + 18, round(sc, 2)))
    return log


def blur_m1140(files):
    """Claude App：问候语里的名字、侧栏聊天标题、设置页邮箱（邮箱那行用模板跟踪，页面在滑动）。"""
    ref = cv2.imread(str(files[75]))                        # 2.5 s：设置页，邮箱在 y≈262
    tmpl = cv2.cvtColor(ref[238:294, 128:506], cv2.COLOR_BGR2GRAY)
    last = None
    log = []
    for i, f in enumerate(files):
        t = i / FPS
        img = None
        if t <= 0.75 or 0.5 <= t <= 2.2 or 1.95 <= t <= 6.6:
            img = cv2.imread(str(f))
        if img is None:
            continue
        if t <= 0.75:
            mosaic(img, 50, 292, 592, 448, block=16)
        if 0.5 <= t <= 2.2:
            mosaic(img, 0, 706, 488, 1280, block=16)
        if 1.95 <= t <= 6.6:
            loc, sc = match(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), tmpl, 0.6)
            if loc is not None:
                last = (loc, t)
                mosaic(img, loc[0] - 6, loc[1] - 4, loc[0] + 384, loc[1] + 60, block=14)
                log.append((round(t, 2), loc, round(sc, 2)))
            elif last is not None and t - last[1] <= 0.15:
                # 刚跟丢（设置页往左滑走的那几帧，行的高度不变）：按上一次的高度整行盖住；超过 0.15 s 旧页面已经被盖住，不再盖
                mosaic(img, 0, last[0][1] - 30, 592, last[0][1] + 90, block=14)
                log.append((round(t, 2), "沿用", round(sc, 2)))
            else:
                log.append((round(t, 2), "无", round(sc, 2)))
        cv2.imwrite(str(f), img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    return log


def interp(keys, t):
    if t <= keys[0][0]:
        return keys[0][1]
    for (a, x), (b, y) in zip(keys, keys[1:]):
        if a <= t <= b:
            return x + (y - x) * (t - a) / max(1e-6, b - a)
    return keys[-1][1]


def phone_manifest(T, counts):
    man = {}
    segs = {s["id"]: s for s in T["segs"]}
    for sid, ph in T["phone"].items():
        s = segs[sid]
        for n in range(int(s["s"] * FPS), int(round(s["e"] * FPS))):
            t = n / FPS
            if "iap" in ph and ph["iap"][0] - 0.5 <= t < ph["iap"][1]:
                man[n] = "iap"
                continue
            st = interp(ph["keys"], t)
            i = min(counts[ph["src"]] - 1, max(0, int(round(st * FPS))))
            man[n] = f"ph/{ph['src']}_{i:05d}.jpg"
    return man


# ─────────────────────────────── 出镜（开场，DJI 0163 的代理 1280×720 30 fps）
def cam_frames(T):
    """开场每一帧对应代理的第几帧：口播段用 cam_edit.json 的 src_frames；口播前后往原片前后顺延（开头 0.4 s、结尾多留的 2 s 是人在镜头前的自然画面）。"""
    ce = json.loads((HERE.parent / "02_出镜" / "edit" / "cam_edit.json").read_text(encoding="utf-8"))
    sf = ce["src_frames"]
    n_src = int(subprocess.check_output(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets",
                                         "-of", "csv=p=0", str(HERE.parent / "02_出镜" / "proxy" / "0163.mp4")]).decode().strip())
    a_end = next(x for x in T["segs"] if x["id"] == "S6")["s"] + 0.8     # 版式切换那 0.7 s 出镜框还在
    t0 = T["cam"]["t0"]
    want = {}
    for n in range(int(round(a_end * FPS))):
        k = int(round((n / FPS - t0) * FPS))
        i = sf[0] + k if k < 0 else (sf[k] if k < len(sf) else sf[-1] + (k - len(sf) + 1))
        want[n] = min(n_src - 1, max(0, i))
    need = sorted(set(want.values()))
    d = MEDIA / "cam"
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*.jpg"):
        f.unlink()
    # 一次解码，按帧号挑出来（select 输出按顺序编号）
    rng = []                                   # 连续的帧号合成区间，select 表达式短一些
    for i in need:
        if rng and i == rng[-1][1] + 1:
            rng[-1][1] = i
        else:
            rng.append([i, i])
    sel = "+".join(f"between(n,{a},{b})" for a, b in rng)
    ff(["-i", HERE.parent / "02_出镜" / "proxy" / "0163.mp4", "-an", "-vf", f"select='{sel}'", "-fps_mode", "passthrough",
        "-q:v", "3", "-start_number", "0", d / "c_%05d.jpg"])
    got = sorted(d.glob("c_*.jpg"))
    assert len(got) == len(need), (len(got), len(need))
    name = {i: f"cam/c_{k:05d}.jpg" for k, i in enumerate(need)}
    print(f"出镜：{len(want)} 帧，抽了 {len(need)} 张")
    return {n: name[i] for n, i in want.items()}


# ─────────────────────────────── 截图
def images():
    from PIL import Image, ImageFilter
    iap = cv2.imread(str(SHOT / "04_苹果内购_ClaudeMax5x_原图.jpg"))
    mosaic(iap, 205, 1728, 680, 1792, block=16)               # 账户邮箱
    cv2.imwrite(str(MEDIA / "iap.jpg"), iap, [cv2.IMWRITE_JPEG_QUALITY, 93])
    Image.open(SHOT / "03_Claude用量_Max5x.png").convert("RGB").save(MEDIA / "usage.png")
    for src, dst in (("01_UP主视频_AI引导世界.png", "up_video.png"), ("02_UP主账号_AI引导世界.png", "up_account.png")):
        im = Image.open(SHOT / src).convert("RGB")
        im.resize((im.width * 2, im.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2)).save(MEDIA / dst)
    print("截图：iap.jpg（邮箱打码）、usage.png、up_video.png、up_account.png")


def narration_env(T):
    """演示段的人声电平（每帧 0–1），给出镜框里“画外音”卡的电平条用：克隆配音按 TL.tts.blocks 放。"""
    p = HERE.parent / "02_出镜" / "edit" / "tts_narration.wav"
    with wave.open(str(p)) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32).mean(1) / 32768
    env = [0.0] * T["frames"]
    hop = sr // FPS
    for b0, b1, off in T["tts"]["blocks"]:
        for n in range(int(off * FPS), min(T["frames"], int((off + b1 - b0) * FPS) + 1)):
            k = int(round((n / FPS - off + b0) * sr))
            if int(b0 * sr) <= k < min(len(a) - hop, int(b1 * sr)):
                rms = np.sqrt((a[k:k + hop] ** 2).mean())
                env[n] = round(float(np.clip((20 * np.log10(rms + 1e-9) + 50) / 30, 0, 1)), 2)
    return env


def check_sheet(paths, out, cols=6, w=296):
    ims = [cv2.imread(str(p)) for p in paths]
    ims = [cv2.resize(i, (w, int(i.shape[0] * w / i.shape[1]))) for i in ims]
    h = max(i.shape[0] for i in ims)
    rows = (len(ims) + cols - 1) // cols
    sheet = np.full((rows * (h + 6), cols * (w + 6), 3), 200, np.uint8)
    for k, i in enumerate(ims):
        y, x = (k // cols) * (h + 6), (k % cols) * (w + 6)
        sheet[y:y + i.shape[0], x:x + w] = i
    cv2.imwrite(str(MEDIA / out), sheet)


def main():
    T = tl()
    MEDIA.mkdir(exist_ok=True)
    images()
    pc_stills()
    counts, logs = {}, {}
    for src, fn in (("M1139", blur_m1139), ("M1140", blur_m1140)):
        files = phone_extract(src)
        counts[src] = len(files)
        logs[src] = fn(files)
        print(f"{src}：{len(files)} 帧；打码 {sum(1 for x in logs[src] if x[1] != '无')} 帧，没找到定位的 {sum(1 for x in logs[src] if x[1] == '无')} 帧")
    (MEDIA / "_blur_log.json").write_text(json.dumps(logs, ensure_ascii=False, default=str), encoding="utf-8")
    ph = MEDIA / "ph"
    check_sheet([ph / f"M1139_{i:05d}.jpg" for i in range(120, 214, 4)], "_check_M1139.png", cols=12)
    check_sheet([ph / f"M1140_{i:05d}.jpg" for i in list(range(56, 72, 2)) + list(range(166, 190, 2))], "_check_M1140.png", cols=10)
    if "--check" in sys.argv:
        return
    scr = pc_live(T)
    phm = phone_manifest(T, counts)
    cam = cam_frames(T)
    fr = {"scr": [scr.get(n) for n in range(T["frames"])], "ph": [phm.get(n) for n in range(T["frames"])],
          "cam": [cam.get(n) for n in range(T["frames"])], "env": narration_env(T)}
    (HERE / "frames.js").write_text("window.FR = " + json.dumps(fr, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("frames.js ok")


if __name__ == "__main__":
    main()
