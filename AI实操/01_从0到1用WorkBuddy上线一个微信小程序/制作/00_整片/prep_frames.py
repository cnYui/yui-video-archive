# -*- coding: utf-8 -*-
"""按剪辑表（../02_出镜/edit/edit.json）给成片的每一帧找好录屏帧和出镜帧，抽成 JPEG，写清单 frames.js。

  python prep_frames.py            → media/scr/*.jpg（录屏，演示区大小 1474×829）、media/cam/*.jpg（出镜 1280×720）、frames.js
  python prep_frames.py --plan     → 只算清单不抽帧（看有多少段、多少张）

- 录屏：版式 B 的片段才要；主时间落在 takes.BLACKOUT（误开微信）里的帧，换成边缘的干净帧（定格）；超出录屏范围的取首 / 尾帧。
- 出镜：主时间 → 出镜时间（takes.cam_at）；同一段里短于 1.5 s 的“没有出镜”（段首段尾差一点点）用最近的出镜帧补上；
  长时间没有出镜（R0945、R0948、AI 生成的快进）清单里写 null，页面里出镜框换成“画外音”卡。
- 抽帧按“同一来源、同一倍速的连续帧”一批一批抽（ffmpeg -ss … setpts/倍速 fps=30），4 路并行；定格只抽一张。
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUT = HERE.parent / "02_出镜"
sys.path.insert(0, str(CUT))
from ingest import src_of  # noqa: E402
from takes import BLACKOUT, SCR_DUR, CAM_DUR, cam_at, has_screen  # noqa: E402

FPS = 30
SW, SH = 1474, 829
FILL = 1.5


def blackout_fix(take, t):
    for b0, b1 in BLACKOUT.get(take, []):
        if b0 <= t < b1:
            return b0 - 1 / 60 if (t - b0) < (b1 - t) else b1 + 1 / 60
    return t


def plan():
    d = json.loads((CUT / "edit" / "edit.json").read_text(encoding="utf-8"))
    scr, cam = [], []                                   # 每帧 (来源, 秒, 倍速) 或 None
    for c in d["clips"]:
        take, sp = c["take"], c["speed"]
        for k in range(c["n"]):
            m = c["m0"] + k / FPS * sp
            if c.get("scr_freeze"):                      # 克隆配音配在某段录屏的定格帧上
                ft, fs = c["scr_freeze"]
                scr.append((ft, round(fs, 4), 0.0))
            elif c["layout"] == "B" and has_screen(take):
                t = blackout_fix(take, m)
                t = min(max(t, 0.0), SCR_DUR[take] - 1 / 30)
                frozen = t != m
                scr.append((take, round(t, 4), 0.0 if frozen else sp))
            else:
                scr.append(None)
            cm = c["cam_m0"] + k / FPS * sp
            ca = cam_at(take, cm)
            cam.append((ca[0], round(ca[1], 4), sp) if ca else None)
    # 段内短缺口用最近的出镜帧补
    seg_of = []
    for c in d["clips"]:
        seg_of += [c["seg"]] * c["n"]
    n = len(cam)
    i = 0
    while i < n:
        if cam[i] is None:
            j = i
            while j < n and cam[j] is None and seg_of[j] == seg_of[i]:
                j += 1
            if (j - i) / FPS < FILL:
                left = cam[i - 1] if i > 0 and seg_of[i - 1] == seg_of[i] else None
                right = cam[j] if j < n and seg_of[j] == seg_of[i] else None
                for k in range(i, j):
                    src = left if (left and (k - i < j - k or not right)) else right
                    if src:
                        cam[k] = (src[0], src[1], 0.0)
            i = max(j, i + 1)
        else:
            i += 1
    return d, scr, cam


def runs(frames):
    """连续帧分批：同一来源、同一倍速、时间连贯 → (来源, 起点秒, 倍速, 帧数, 起始帧号)。定格（倍速 0）同一张算一批。"""
    out = []
    for f, x in enumerate(frames):
        if x is None:
            continue
        src, t, sp = x
        if out:
            s0, t0, sp0, n0, f0 = out[-1]
            if s0 == src and sp0 == sp and f0 + n0 == f:
                exp = t0 + n0 / FPS * sp
                if (sp == 0 and abs(t - t0) < 1e-3) or (sp > 0 and abs(t - exp) < 0.6 / FPS * max(sp, 1)):
                    out[-1] = (s0, t0, sp0, n0 + 1, f0)
                    continue
        out.append((src, t, sp, 1, f))
    return out


def extract(kind, src, t0, sp, n, name):
    """抽一批帧到 media/<kind>/<name>_%05d.jpg（定格只抽 1 张：<name>_00000.jpg）。"""
    d = HERE / "media" / kind
    d.mkdir(parents=True, exist_ok=True)
    if kind == "scr":
        path = src_of(src)
        size = f"scale={SW}:{SH}:flags=lanczos"
        t0 = round(t0 * 60) / 60 - 0.002        # 录屏 60 fps：对齐到帧，别晚一帧
    else:
        path = CUT / "proxy" / f"{src}.mp4"
        size = "null"
        t0 = round(t0 * 30) / 30 - 0.002        # 出镜代理 30 fps
    if sp == 0:
        vf, cnt = size, 1
    else:
        vf, cnt = f"setpts=(PTS-STARTPTS)/{sp},fps={FPS},{size}", n
    args = ["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0.0, t0):.4f}", "-i", str(path), "-an", "-vf", vf,
            "-frames:v", str(cnt), "-q:v", "3", "-start_number", "0", str(d / f"{name}_%05d.jpg")]
    subprocess.run(args, check=True)
    got = len(list(d.glob(f"{name}_*.jpg")))
    return got


# ─────────────────────────────── R1036 右下角的黑框（OpenScreen 摄像头画中画，录的时候摄像头没画面）
# 中心固定在原片 (1762, 955)，大小随 OpenScreen 的缩放在约 150×112 到 256×202 之间变；做法同第 1 期 cut_pauses.py：
# 每帧量出黑框大小，连同阴影一起用周围的颜色补上（缩小四倍 inpaint 再放大，边缘羽化）。这里在已经缩到演示区大小的帧上做。
BOX_TAKES = {"R1036"}
SC = SW / 1920
BCX, BCY = int(1762 * SC), int(955 * SC)


def box_size(a):
    dark = a.max(axis=2) <= 16
    if not dark[BCY, BCX]:
        return None

    def scan(dx, dy, lim):
        x, y, n = BCX, BCY, 0
        while n < lim and 0 <= x < SW and 0 <= y < SH and dark[y, x]:
            x += dx
            y += dy
            n += 1
        return n
    hw = min(scan(-1, 0, int(150 * SC)), scan(1, 0, int(150 * SC)))
    hh = min(scan(0, -1, int(115 * SC)), scan(0, 1, int(115 * SC)))
    hw = min(hw, hh * 1.42)
    hh = min(hh, hw / 1.28)
    if hw < 40 * SC:
        return None
    return hw, hh


def remove_box(path):
    import cv2
    import numpy as np
    a = cv2.imread(str(path))
    sz = box_size(a[:, :, ::-1])
    if sz is None:
        return False
    hw, hh = sz
    m = 10 * SC + 0.14 * hw
    x0, x1 = int(BCX - hw - m), int(BCX + hw + m)
    y0, y1 = int(BCY - hh - m), int(min(SH, BCY + hh + 1.6 * m))
    pad = int(60 * SC)
    X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(SW, x1 + pad), min(SH, y1 + pad)
    roi = a[Y0:Y1, X0:X1].copy()
    hole = np.zeros(roi.shape[:2], np.uint8)
    cv2.rectangle(hole, (x0 - X0, y0 - Y0), (min(x1, SW) - X0 - 1, y1 - Y0 - 1), 255, -1)
    s = 4
    small = cv2.resize(roi, (roi.shape[1] // s, roi.shape[0] // s), interpolation=cv2.INTER_AREA)
    hs = cv2.resize(hole, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    hs = cv2.dilate(hs, np.ones((3, 3), np.uint8))
    fill = cv2.inpaint(small, hs, 6, cv2.INPAINT_TELEA)
    fill = cv2.GaussianBlur(fill, (5, 5), 0)
    big = cv2.resize(fill, (roi.shape[1], roi.shape[0]), interpolation=cv2.INTER_CUBIC)
    alpha = cv2.GaussianBlur(hole.astype(np.float32) / 255, (0, 0), 6 * SC)[..., None]
    alpha = np.maximum(alpha, (hole > 0)[..., None] * 1.0)
    a[Y0:Y1, X0:X1] = (roi * (1 - alpha) + big * alpha).astype(np.uint8)
    cv2.imwrite(str(path), a, [cv2.IMWRITE_JPEG_QUALITY, 92])
    return True


def main():
    if sys.argv[1:2] == ["--box-test"]:
        for p in sys.argv[2:]:
            print(p, remove_box(Path(p)))
        return
    d, scr, cam = plan()
    total = len(scr)
    jobs, man_s, man_c = [], [None] * total, [None] * total
    for kind, frames, man in (("scr", scr, man_s), ("cam", cam, man_c)):
        for r, (src, t0, sp, n, f0) in enumerate(runs(frames)):
            # 按内容命名（来源、起点、倍速、帧数）：剪辑改了以后，没变的批次直接复用
            name = f"{src}_{t0:08.3f}_{sp:.3f}_{n}"
            last = HERE / "media" / kind / f"{name}_{0 if sp == 0 else n - 1:05d}.jpg"
            if not last.exists() or (kind == "scr" and src in BOX_TAKES and not (HERE / "media" / kind / f"{name}.boxed").exists()):
                jobs.append((kind, src, t0, sp, n, name))
            for k in range(n):
                man[f0 + k] = f"{kind}/{name}_{0 if sp == 0 else k:05d}.jpg"
    ns = sum(1 for j in jobs if j[0] == "scr")
    print(f"{total} 帧；录屏 {ns} 批、出镜 {len(jobs) - ns} 批；没有录屏的帧 {man_s.count(None)}，没有出镜的帧 {man_c.count(None)}")
    if "--plan" in sys.argv:
        return
    missing = []

    def work(j):
        kind, src, t0, sp, n, name = j
        got = extract(kind, src, t0, sp, n, name)
        need = 1 if sp == 0 else n
        if got < need:
            missing.append((name, need, got))
        return name

    with ThreadPoolExecutor(4) as ex:
        for k, _ in enumerate(ex.map(work, jobs)):
            if k % 50 == 0:
                print(f"  {k}/{len(jobs)}", flush=True)
    # 抽少了的（视频末尾不够帧）：用这一批的最后一张补
    for name, need, got in missing:
        print("  补帧：", name, need, got)
    for man in (man_s, man_c):
        for f, p in enumerate(man):
            if p and not (HERE / "media" / p).exists():
                stem, k = p.rsplit("_", 1)
                k = int(k[:5])
                while k > 0 and not (HERE / "media" / f"{stem}_{k:05d}.jpg").exists():
                    k -= 1
                man[f] = f"{stem}_{k:05d}.jpg"
    fixed = 0
    for kind, src, t0, sp, n, name in jobs:
        if kind == "scr" and src in BOX_TAKES:
            for p in sorted((HERE / "media" / "scr").glob(f"{name}_*.jpg")):
                fixed += remove_box(p)
            (HERE / "media" / "scr" / f"{name}.boxed").write_text("ok", encoding="utf-8")
    print(f"抹黑框 {fixed} 张")
    (HERE / "frames.js").write_text("window.FR = " + json.dumps({"scr": man_s, "cam": man_c}, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("frames.js ok")


if __name__ == "__main__":
    main()
