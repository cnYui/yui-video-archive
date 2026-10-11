# -*- coding: utf-8 -*-
"""剪录屏口播：素材/录屏/PC1139_买礼品卡.mp4（OpenScreen 录的电脑麦克风，用户边录边讲）。
去掉气口、口癖、说错重说和长停顿，输出：
  edit/pc_edit.json      保留的片段（源时间 → 输出时间）、字幕条（R01…，输出时间从 0 起）
  edit/pc_narration.wav  剪好的口播（48 kHz 立体声，每个剪点 8 ms 淡入淡出）

  python pc_cut.py

剪掉的（2026-10-01，按 ASR 逐词时间 + 20 ms 电平定剪点；这段录音带噪声门，词间是数字静音，剪点都落在静音里）：
  0.00–5.08   开头半句“（买）美区，也就是美金的 Apple Card”（录屏开始时话说了一半）
  39.58–41.28 “然后去……”（起了个头又停了）
  45.40–79.20 在 Gmail 收件箱里找邮件（没说话，收件箱是私人内容）
  80.49–80.86 “昨天”：打开的那封礼品卡邮件是 2023/5/8 的，说“昨天”和画面对不上
  85.48–86.92 “所以他就会”（下一句又说了一遍“他就会”）
  其余：超过 0.3 s 的停顿压到 0.1–0.3 s；28.80 的一声鼠标点击。
听不准：R09“其他博主视频”（识别也可能是“部署视频”，按上下文取“博主”）；R18 的“这个”三次识别只有一次有，字幕不写。
复核：剪完的 pc_narration.wav 再识别一遍，“昨天”“然后去”“所以他就会”都不在了，剪点没有吞字。
"""
import json
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "素材" / "录屏" / "PC1139_买礼品卡.mp4"
SR = 48000

# 保留的源时间区间（含句后停顿）。live = 画面用录屏原片；False = 这段画面换成打码静帧（邮件里有礼品卡号、邮箱地址）
KEEP = [
    (5.08, 10.24, True), (10.66, 13.20, True), (13.64, 19.98, True), (20.50, 26.22, True),
    (26.64, 28.36, True), (28.88, 31.34, True), (31.66, 32.50, True), (33.66, 36.98, True),
    (37.20, 39.58, True), (41.28, 42.84, True), (43.66, 45.40, True),
    (79.20, 80.49, False), (80.86, 82.86, False), (83.28, 85.48, False), (86.92, 88.70, False),
    (89.10, 91.40, False), (91.80, 93.10, False),
]

# 字幕条：(编号, 文字, 源时间起, 源时间止)。文字按实际说的写（只去掉剪掉的部分）
CUES = [
    ("R01", "那我们想要买美国的苹果卡，", 5.12, 7.06),
    ("R02", "其实我们可以上网搜一下，", 7.18, 8.50),
    ("R03", "有很多地方都可以买，", 8.60, 9.68),
    ("R04", "比如说 Apple 的美国官方网站也可以买，", 9.72, 13.06),
    ("R05", "实体店也可以买，", 13.68, 14.56),
    ("R06", "但是我们现在在国内没有办法去购买，", 14.60, 16.46),
    ("R07", "而且我们也没有信用卡去在官方网站上买。", 16.52, 19.86),
    ("R08", "所以我不作为推荐。", 20.52, 22.12),
    ("R09", "但是我自己是在B站上看的其他博主视频，", 22.16, 25.14),
    ("R10", "我是在这里买的，", 25.16, 26.08),
    ("R11", "去点击这里蓝色的苹果卡，", 26.68, 29.28),
    ("R12", "因为这里我们可以用支付宝来支付，", 29.28, 31.20),
    ("R13", "按照每天对应的汇率去进行支付，", 31.70, 35.38),
    ("R14", "所以我还是在这里去购买。", 35.38, 36.84),
    ("R15", "比如说我们最低可以买两刀，", 37.22, 39.50),
    ("R16", "登录之后去进行付款，", 41.30, 42.72),
    ("R17", "它会发到我们的邮箱里。", 43.68, 45.14),
    ("R18", "比如说就可以看到，是我买的礼品卡，", 79.24, 82.70),
    ("R19", "我买了三刀，", 83.32, 84.12),
    ("R20", "这个我已经兑换过了。", 84.12, 85.44),
    ("R21", "他就会把码发给我们，", 87.18, 88.56),
    ("R22", "然后我们去苹果的手机的这里，进行兑换就可以。", 89.14, 92.84),
]


def src_to_out(t, pieces):
    """源时间 → 输出时间（落在剪掉的地方就取下一段的开头）。"""
    for p in pieces:
        if t < p["src0"]:
            return p["out0"]
        if t <= p["src1"]:
            return p["out0"] + (t - p["src0"])
    return pieces[-1]["out1"]


def main():
    pieces, out = [], 0.0
    for a, b, live in KEEP:
        pieces.append({"src0": a, "src1": b, "out0": round(out, 4), "out1": round(out + b - a, 4), "live": live})
        out += b - a
    cues = [{"id": i, "zh": zh, "s": round(src_to_out(a, pieces), 3), "e": round(src_to_out(b, pieces), 3)} for i, zh, a, b in CUES]
    # 口播：原片 48 kHz，逐段拼接，剪点 8 ms 淡入淡出
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC), "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, 2)
    fade = int(0.008 * SR)
    parts = []
    for p in pieces:
        seg = a[int(round(p["src0"] * SR)): int(round(p["src1"] * SR))].copy()
        ramp = np.linspace(0, 1, fade)[:, None]
        seg[:fade] *= ramp
        seg[-fade:] *= ramp[::-1]
        parts.append(seg)
    y = np.concatenate(parts)
    (HERE / "edit").mkdir(exist_ok=True)
    import wave
    with wave.open(str(HERE / "edit" / "pc_narration.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    d = {"source": "PC1139", "total": round(out, 3), "pieces": pieces, "cues": cues}
    (HERE / "edit" / "pc_edit.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    live = sum(p["src1"] - p["src0"] for p in pieces if p["live"])
    print(f"口播 {out:.2f} s（录屏原片 {live:.2f} s + 打码静帧 {out - live:.2f} s），{len(cues)} 条字幕，原片 93.1 s 说话部分")


if __name__ == "__main__":
    main()
