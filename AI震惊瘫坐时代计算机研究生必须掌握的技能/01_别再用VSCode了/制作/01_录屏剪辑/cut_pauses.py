# -*- coding: utf-8 -*-
"""两段录屏去掉停顿（用户：“给你发的两个视频素材也是需要你剪辑的，有一些气口和停顿，需要你剪掉”），再抹掉 Claude Code 录屏右下角的黑框。

录屏没有人声（整段 −46 dB 左右的底噪），所以“停顿”按画面判断：每 0.1 秒比一次前后两帧（960×540 灰度，差 > 24 算变了）：
  - 静止（几乎没有像素变化）连续 0.5 秒以上：只留头尾各 0.15 秒；
  - 只有鼠标在动（变化集中在一个小框里）连续 1 秒以上：2.5 倍速；
  - 手动补的停顿：MANUAL_CUT（整段去掉）、MANUAL_FAST（加速）。
右下角的黑框是 OpenScreen 的摄像头画中画（录的时候摄像头没画面），中心固定在 (1761, 954)，大小随缩放在 148×108 到 264×196 之间变。
每帧量出黑框大小，连同阴影一起用周围的颜色补上（缩小四倍做 inpaint 再放大，边缘羽化）。

用法：python cut_pauses.py [cc|trae …]      → out/<名字>_去停顿.mp4、out/<名字>_edl.json
      python cut_pauses.py --test cc 20 42 150 → out/test_*.png（抹黑框的效果）
EDL：segments = [[原片起, 原片止, 倍速, 新片起, 新片止], …]；新片 30 fps、无声、1920×1080。
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
OUT = HERE / "out"
FPS = 30
W, H = 1920, 1080
SRC = {
    "cc": {"file": EP / "素材/录屏_ClaudeCode桌面版.mp4", "name": "录屏_ClaudeCode桌面版", "box": True},
    "trae": {"file": EP / "素材/录屏_TraeCode.mp4", "name": "录屏_TraeCode", "box": False},
}
STATIC_MIN, STATIC_KEEP = 0.5, 0.15      # 静止多久算停顿、头尾各留多少
CURSOR_MIN, CURSOR_SPEED = 1.0, 2.5      # 只有鼠标在动多久算停顿、加速多少
# 看联系表手动挑的停顿（原片秒数）
MANUAL_CUT = {"cc": [], "trae": []}
MANUAL_FAST = {"cc": [], "trae": []}


# ---------------------------------------------------------------- 分析：每 0.1 秒一个标记  S 静止 / c 只有鼠标 / A 有内容变化
def analyze(key):
    aw, ah, afps = 960, 540, 10
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(SRC[key]["file"]), "-vf", f"fps={afps},scale={aw}:{ah}",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    mask = np.ones((ah, aw), bool)
    if SRC[key]["box"]:
        mask[400:, 780:] = False          # 黑框缩放时会变，不算
    prev, cls = None, []
    while True:
        b = p.stdout.read(aw * ah)
        if len(b) < aw * ah:
            break
        f = np.frombuffer(b, np.uint8).astype(np.int16).reshape(ah, aw)
        if prev is None:
            cls.append("A")
        else:
            d = (np.abs(f - prev) > 24) & mask
            n = int(d.sum())
            if n <= 3:
                cls.append("S")
            else:
                ys, xs = np.where(d)
                cls.append("c" if xs.max() - xs.min() < 70 and ys.max() - ys.min() < 70 else "A")
        prev = f
    p.wait()
    return "".join(cls), 1.0 / afps


def runs(s, ch):
    i = 0
    while i < len(s):
        if s[i] == ch:
            j = i
            while j < len(s) and s[j] == ch:
                j += 1
            yield i, j
            i = j
        else:
            i += 1


def plan(key, dur):
    """返回 [[原片起, 原片止, 倍速], …]（去掉的部分不在里面）。"""
    cls, dt = analyze(key)
    speed = np.ones(len(cls))                      # 每 0.1 秒的倍速；0 = 去掉
    for i, j in runs(cls, "S"):
        if (j - i) * dt >= STATIC_MIN:
            k = int(round(STATIC_KEEP / dt))
            speed[i + k: j - k] = 0
    for i, j in runs(cls, "c"):
        if (j - i) * dt >= CURSOR_MIN:
            speed[i:j] = np.where(speed[i:j] > 0, CURSOR_SPEED, 0)
    for a, b in MANUAL_FAST[key]:
        i, j = int(a / dt), int(b / dt)
        speed[i:j] = np.where(speed[i:j] > 0, np.maximum(speed[i:j], 3.0), 0)
    for a, b in MANUAL_CUT[key]:
        speed[int(a / dt): int(b / dt)] = 0
    segs = []
    for i, v in enumerate(speed):
        t0, t1 = i * dt, min(dur, (i + 1) * dt)
        if v == 0 or t0 >= dur:
            continue
        if segs and segs[-1][2] == v and abs(segs[-1][1] - t0) < 1e-6:
            segs[-1][1] = t1
        else:
            segs.append([t0, t1, float(v)])
    return segs, cls


# ---------------------------------------------------------------- 抹掉右下角的黑框
CX, CY = 1761, 954


def box_size(a):
    dark = a.max(axis=2) <= 12
    if not dark[CY, CX]:
        return None

    def scan(dx, dy, lim):
        x, y, n = CX, CY, 0
        while n < lim and 0 <= x < W and 0 <= y < H and dark[y, x]:
            x += dx
            y += dy
            n += 1
        return n
    hw = min(scan(-1, 0, 150), scan(1, 0, 150))
    hh = min(scan(0, -1, 115), scan(0, 1, 115))
    hw = min(hw, hh * 1.42)
    hh = min(hh, hw / 1.28)
    if hw < 40:
        return None
    return hw, hh


def remove_box(a):
    sz = box_size(a)
    if sz is None:
        return a
    hw, hh = sz
    m = 10 + 0.14 * hw
    x0, x1 = int(CX - hw - m), int(CX + hw + m)
    y0, y1 = int(CY - hh - m), int(min(H, CY + hh + 1.6 * m))
    # 在一块更大的区域里做，缩小四倍 inpaint，再放大贴回去（边缘羽化）
    pad = 60
    X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
    roi = a[Y0:Y1, X0:X1].copy()
    hole = np.zeros(roi.shape[:2], np.uint8)
    cv2.rectangle(hole, (x0 - X0, y0 - Y0), (min(x1, W) - X0 - 1, y1 - Y0 - 1), 255, -1)
    s = 4
    small = cv2.resize(roi, (roi.shape[1] // s, roi.shape[0] // s), interpolation=cv2.INTER_AREA)
    hs = cv2.resize(hole, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    hs = cv2.dilate(hs, np.ones((3, 3), np.uint8))
    fill = cv2.inpaint(small, hs, 6, cv2.INPAINT_TELEA)
    fill = cv2.GaussianBlur(fill, (5, 5), 0)
    big = cv2.resize(fill, (roi.shape[1], roi.shape[0]), interpolation=cv2.INTER_CUBIC)
    alpha = cv2.GaussianBlur(hole.astype(np.float32) / 255, (0, 0), 6)[..., None]
    alpha = np.maximum(alpha, (hole > 0)[..., None] * 1.0)
    out = a.copy()
    out[Y0:Y1, X0:X1] = (roi * (1 - alpha) + big * alpha).astype(np.uint8)
    return out


# ---------------------------------------------------------------- 出片
def render(key):
    info = SRC[key]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(info["file"])],
                               capture_output=True, text=True).stdout.strip())
    segs, cls = plan(key, dur)
    # 新片每一帧对应的原片时刻
    times, edl, t_new = [], [], 0.0
    for a, b, v in segs:
        n0 = len(times)
        t = a
        while t < b - 1e-9:
            times.append(t)
            t += v / FPS
        n1 = len(times)
        edl.append([round(a, 3), round(b, 3), v, round(n0 / FPS, 4), round(n1 / FPS, 4)])
    OUT.mkdir(exist_ok=True)
    out = OUT / f"{info['name']}_去停顿.mp4"
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(info["file"]), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    src_fps = 60.0
    k, fi, frame = 0, -1, None
    for t in times:
        want = int(round(t * src_fps))
        while fi < want:
            b = dec.stdout.read(W * H * 3)
            if len(b) < W * H * 3:
                break
            fi += 1
            frame = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        img = remove_box(frame) if info["box"] else frame
        enc.stdin.write(np.ascontiguousarray(img).tobytes())
        k += 1
    enc.stdin.close()
    enc.wait()
    dec.stdout.close()
    dec.wait()
    new_dur = len(times) / FPS
    cut = sum(b - a for a, b, v in segs)
    info_json = {"source": str(info["file"]), "fps": FPS, "srcDuration": round(dur, 3), "newDuration": round(new_dur, 3),
                 "keptSourceSeconds": round(cut, 3), "segments": edl,
                 "rules": {"staticMin": STATIC_MIN, "staticKeep": STATIC_KEEP, "cursorMin": CURSOR_MIN, "cursorSpeed": CURSOR_SPEED,
                           "manualCut": MANUAL_CUT[key], "manualFast": MANUAL_FAST[key]},
                 "motion10fps": cls}
    (OUT / f"{info['name']}_edl.json").write_text(json.dumps(info_json, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{key}: {dur:.1f}s → {new_dur:.1f}s ({len(edl)} 段), {k} 帧 → {out.name}")


def test(key, ts):
    OUT.mkdir(exist_ok=True)
    for t in ts:
        b = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(SRC[key]["file"]), "-frames:v", "1",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        a = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        r = remove_box(a)
        both = np.concatenate([a[640:, 1280:], r[640:, 1280:]], axis=1)
        cv2.imwrite(str(OUT / f"test_{key}_{t}.png"), cv2.cvtColor(both, cv2.COLOR_RGB2BGR))
        print(t, box_size(a))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*", default=["cc", "trae"])
    ap.add_argument("--test", nargs="+")
    args = ap.parse_args()
    if args.test:
        test(args.test[0], [float(x) for x in args.test[1:]])
        return
    for k in args.keys:
        render(k)


if __name__ == "__main__":
    main()
