# -*- coding: utf-8 -*-
"""剪开场出镜口播（DJI 0163，2026-10-01 13:53，89 s）：去口癖、说错改口、重复的半句、长停顿。

  python build_edit.py

输出：edit/cam_edit.json（保留片段 源 → 输出、字幕条 C01–C28 的输出时间、src_frames = 成片每一帧对应代理的第几帧）、
      edit/cam_narration.wav（48 kHz 立体声）。画面按帧号取（代理是 30 fps 恒定帧率），口型不会越往后越慢。

剪点（逐词识别 + 20 ms 电平，拿不准的拼一小段让 Whisper 听过）：
- 8.30–8.49 “然后”（“我”从 8.49 起，8.56 起就吞了“我”）
- 60.44–61.40 第一遍“Google Play”（原话“就去走 Google Play、Google Play 商店里面”）
- 38.86–40.56 “也没有办法导出来”（紧接着改口“虽然可以导出来”；38.86 是连读中间，40 ms 淡出）
- 66.92–68.06 第二遍“安卓手机用户的话”（“我”粘在它后面，从 68.06 起正好留下“我建议”）
- 78.06–79.40 “然后之后”
- 开头 0.84 前、结尾 87.18 后的空白。
停顿：片段内超过 0.25 s 的静音（< -50 dB，相隔不到 0.1 s 的合并）压短：句末留 0.26 s，逗号处 0.15–0.2 s，
字中间的犹豫（国…内、跑…路、美…区、安…卓、商…店、推…荐、用…任何）只留 0.06 s。
没剪的：两处“就是”（19.04“中转站的话，就是你的数据”、32.30“走代充的话，就是会有”）都和前面的“的话”连读，
试过 18.97 / 19.00 起剪，“话”会被切掉一半（识别成“中转家”），保留原话；“这期 UP 主”照原话。
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SID = "0163"
FPS, SR = 30, 48000

# 保留的源区间（秒）。fade_out：这一段结尾是连读中间，用长一点的淡出
SPANS = [
    (0.84, 8.28), (8.49, 17.92), (18.32, 30.08),
    (31.56, 38.86, "fade_out"), (40.56, 45.46), (46.60, 60.44), (61.40, 66.92), (68.06, 78.06), (79.40, 87.18),
]
# 静音压到多长（按静音的开始时刻找）；没写的：≥ 0.5 s 留 0.26，否则留 0.15
SIL_KEEP = {2.08: 0.26, 5.44: 0.06, 10.62: 0.30, 13.26: 0.12, 16.14: 0.20, 23.34: 0.28, 25.94: 0.06, 26.70: 0.10,
            35.70: 0.06, 44.12: 0.10, 49.68: 0.06, 51.88: 0.12, 55.26: 0.22, 58.56: 0.06, 61.98: 0.06, 63.04: 0.15,
            64.22: 0.10, 68.40: 0.06, 70.82: 0.24, 73.90: 0.06, 81.96: 0.15}
GAP_AFTER_FADE = 0.20      # 淡出那一刀后面补的停顿（逗号）

CUES = [
    ("C01", "嗨，大家好，我是悠一。", 0.94, 2.08),
    ("C02", "后台有很多朋友在询问我，", 2.66, 4.62),
    ("C03", "怎么去国内去充值 Codex、Claude Code，", 4.64, 8.12),
    ("C04", "我就想做一期这样的介绍视频。", 8.49, 10.62),
    ("C05", "首先我不推荐大家去用任何的中转站或者代充，", 11.28, 16.14),
    ("C06", "因为存在安全问题。", 16.66, 17.68),
    ("C07", "中转站的话，就是你的数据不会往官方那边发，", 18.40, 21.85),
    ("C08", "会从中转站那边转一遍。", 21.90, 23.34),
    ("C09", "中转站那边，它其实会有一些厂商，", 23.84, 28.00),
    ("C10", "会去贩卖你的这种聊天记录。", 28.02, 29.94),
    ("C11", "走代充的话，就是会有一个凭证安全泄露的问题，", 31.64, 34.70),
    ("C12", "如果别人跑路了，你也没有办法续费，", 34.80, 37.45),
    ("C13", "你这里的信息内容，", 37.50, 38.86),
    ("C14", "虽然可以导出来，但是会很麻烦。", 40.62, 42.05),
    ("C15", "对于小白来讲，还是不要轻易地去走代充。", 42.06, 45.34),
    ("C16", "我只推荐两种方法：", 46.68, 47.74),
    ("C17", "一个是苹果用户，就用美区的 Apple ID 去购买", 47.76, 51.88),
    ("C18", "美区的美金的 Apple Card，", 52.88, 55.26),
    ("C19", "然后去走苹果的官方支付。", 55.98, 58.45),
    ("C20", "安卓手机用户的话，就去走 Google Play 商店里面，", 58.48, 63.04),
    ("C21", "去绑定国内的 Visa 卡等等，可以去购买。", 63.60, 66.80),
    ("C22", "我建议大家参考这期 UP 主的视频。", 68.06, 70.82),
    ("C23", "它的方法仅做推荐，", 71.38, 72.90),
    ("C24", "不代表我推荐它店铺内的任何商品，", 72.92, 76.10),
    ("C25", "只是觉得这种方法是可以的。", 76.12, 77.94),
    ("C26", "接下来我会演示，如何通过苹果的方式，", 79.44, 81.96),
    ("C27", "来进行购买 Codex 或者 Claude Code 的会员，", 82.66, 85.32),
    ("C28", "因为我本身也是这样做的。", 85.34, 87.06),
]


def q(t):
    return round(round(t * FPS) / FPS, 4)     # 剪点对齐到 30 fps 的帧，音画一起剪


def silences(db, t0, t1, thr=-50, minlen=0.25, merge=0.1):
    out, s = [], None
    i0, i1 = int(round(t0 / 0.02)), int(round(t1 / 0.02))
    for i in range(i0, i1 + 1):
        quiet = i < i1 and db[i] < thr
        if quiet and s is None:
            s = i
        elif not quiet and s is not None:
            out.append([s * 0.02, i * 0.02])
            s = None
    merged = []
    for a, b in out:
        if merged and a - merged[-1][1] < merge:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return [(a, b) for a, b in merged if b - a >= minlen]


def main():
    w = wave.open(str(HERE / "audio16" / f"{SID}.wav"))
    a16 = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    hop = int(16000 * 0.02)
    n = len(a16) // hop
    db = 20 * np.log10(np.sqrt((a16[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    pieces = []     # (src0, src1, gap_after, fade_out)
    for sp in SPANS:
        s0, s1 = sp[0], sp[1]
        fade = len(sp) > 2
        cur = s0
        for a, b in silences(db, s0, s1):
            if a <= s0 + 0.02 or b >= s1 - 0.02:
                continue
            keep = next((v for k, v in SIL_KEEP.items() if abs(k - a) < 0.12), 0.26 if b - a >= 0.5 else 0.15)
            if b - a <= keep + 0.04:
                continue
            pieces.append([cur, a + keep / 2, 0.0, False])
            cur = b - keep / 2
        pieces.append([cur, s1, GAP_AFTER_FADE if fade else 0.0, fade])
    # 对齐到帧
    for p in pieces:
        p[0], p[1] = q(p[0]), q(p[1])
    out, t = [], 0.0
    for s0, s1, gap, fade in pieces:
        out.append({"src0": s0, "src1": s1, "out0": round(t, 4), "out1": round(t + s1 - s0, 4), "fade": fade, "gap": gap})
        t += s1 - s0 + gap
    total = round(t, 4)

    def src2out(x):
        for p in out:
            if x < p["src0"]:
                return p["out0"]
            if x <= p["src1"]:
                return p["out0"] + x - p["src0"]
        return out[-1]["out1"]
    cues = [{"id": i, "zh": zh, "s": round(src2out(a), 3), "e": round(src2out(b), 3)} for i, zh, a, b in CUES]
    # 口播
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(HERE / "audio" / f"{SID}.wav"), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    A = np.frombuffer(raw, np.float32).reshape(-1, 2)
    segs = []
    for p in out:
        seg = A[int(round(p["src0"] * SR)): int(round(p["src1"] * SR))].copy()
        f_in, f_out = int(0.006 * SR), int((0.04 if p["fade"] else 0.006) * SR)
        seg[:f_in] *= np.linspace(0, 1, f_in)[:, None]
        seg[-f_out:] *= np.linspace(1, 0, f_out)[:, None]
        segs += [seg, np.zeros((int(round(p["gap"] * SR)), 2), np.float32)]
    y = np.concatenate(segs)
    (HERE / "edit").mkdir(exist_ok=True)
    with wave.open(str(HERE / "edit" / "cam_narration.wav"), "wb") as o:
        o.setnchannels(2)
        o.setsampwidth(2)
        o.setframerate(SR)
        o.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    # 出镜画面：成片每一帧对应原片（代理，30 fps）第几帧；补的停顿用前一帧顶上（页面逐帧取图，不另外拼视频）
    nf = int(round(total * FPS))
    src_frames = []
    for k in range(nf):
        x = k / FPS
        p = next((p for p in out if p["out0"] <= x < p["out1"] + p["gap"]), out[-1])
        src_frames.append(min(int(round(p["src1"] * FPS)) - 1, int(round(p["src0"] * FPS)) + int(round((x - p["out0"]) * FPS))))
    d = {"source": SID, "fps": FPS, "total": total, "frames": nf, "pieces": out, "cues": cues, "src_frames": src_frames}
    (HERE / "edit" / "cam_edit.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    kept = sum(p["src1"] - p["src0"] for p in out)
    print(f"出镜口播 {total:.2f} s（原片 89.06 s，保留 {kept:.2f} s，{len(out)} 个片段）；{nf} 帧；{len(cues)} 条字幕")


if __name__ == "__main__":
    main()
