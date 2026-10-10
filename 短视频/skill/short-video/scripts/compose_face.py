# -*- coding: utf-8 -*-
r"""出镜小窗：把用户自己录的口播（镜像）作为圆角小窗叠到渲好的卡片版成片上（用户 2026-10-06 定的统一做法：“这个出镜的人脸框我很满意……之后人脸出镜都这样用小窗展示”）。

  python compose_face.py <本条目录> [--base 整片_v1_cards无小窗.mp4] [--out 整片_v1.mp4] [--seconds N] [--moves "A2:bl,A5:tl"]

读 `<本条>\制作\00_整片\face.json`（模板：assets/face-template/face.json）：
  {"src": "H:/DCIM/.../x.MP4", "start": 0.20, "duration": null,          # 原片从 start 秒起（= 配音 tts_narration.wav 的起点），duration 不写 = 成片总长
   "mirror": true,                                                      # 镜像（hflip），用户 2026-10-06 明说要镜像
   "crop": {"cx": 0.515, "cy": 0.449, "side": 0.787},                   # 原片里裁一块正方形（脸 + 肩膀）：中心 cx / cy、边长 side 都是占原片“高度”的比例（cx 占宽度）
   "size": 360, "sticker": "悠一 出镜"}                                  # 默认大小（居中那档）；贴纸文字

位置（版式相关，坐标按 1080×2340）：
  single（单框，标题 + 一个视频框 + 字幕）：默认 center = 字幕下面居中（x 360, y 1664, 360×360）——Claude 中文界面那条用户满意的样子
  dual（两个演示框叠在一起，字幕在下面，下面没地方）：默认 bl = 缩到 240 放到下框的左下角（x 40, y 1460），盖住下框左下角一小块
  faceb（出镜多窗版式，2026-10-06 起：plan.json 顶层 layout = "faceb"，场景各自写 mode = one / two / big）：one 场景按 single 的位置走（居中在字幕下面），
        two / big 场景按 dual 的位置走（缩到 240 放左下角），场景切换处顺势移动；字幕条跟着场景（单窗 y 1490–1620、双窗 / 大窗 y 1756–1884）。
        原来第 1 期出镜版用的包装脚本 compose_face_mixed.py 已并进这里，用法不变：compose_face.py <本条目录>。
  其它角：tl / tr（上框的左上 / 右上角）、bl；hide = 滑到画面外。
  **按场景换位置**：plan.json 的场景写 "face": "center" | "bl" | "tl" | "tr" | "hide"，不写就按版式默认；
  位置 / 大小在场景交界处用缓入缓出“顺势移动”（大小也跟着缩放，整段 0.35 s；有字幕停顿就放进停顿里）；face.json 写 "move": "cut" = 直接跳过去。--moves 可临时覆盖（测试用）。
  跨过字幕条的移动（单框版“框内角落 ↔ 字幕下面居中”）一定会扫过字幕约 0.15 s——脚本会报“⚠ 字幕检查”；停着的位置不允许盖字幕，盖了也会报。

做法：窗口的三层（橙色硬阴影 / 脸 / 黑描边 + 黄贴纸）都做成 440×440 的透明小画布，ffmpeg 里按帧缩放、移动（scale + overlay 的 eval=frame，表达式里用 t），
原片从 start 起、30 fps、4K HEVC 直接解码，不转码中间文件；音轨沿用 base 里已混好的（`-map 0:a`，不重编码）。
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = Path(r"D:\大疆\Claude Code相关\短视频\02_Anthropic设计师用Claude做设计\制作\00_整片\fonts\NotoSansSC.ttf")
CW, OX, OY, RAD, SH = 440, 30, 40, 30, 14          # 小画布 440×440，窗口左上角在 (30, 40)（给硬阴影、描边、贴纸留边）
BASE_SIZE = 360                                      # 画布里窗口的原始大小；实际大小 = BASE_SIZE × 缩放

POS = {   # 名字 → (x, y, size)，窗口本体（不含阴影 / 描边）的左上角和边长
    "single": {"center": (360, 1664, 360), "bl": (56, 1123, 240), "tl": (56, 746, 240), "tr": (784, 746, 240), "br": (56, 1123, 240)},
    "dual": {"bl": (40, 1460, 240), "tl": (40, 640, 240), "tr": (790, 640, 240), "br": (40, 1460, 240), "center": (40, 1460, 240)},
}
HIDE_Y = 2400
DEFAULT_POS = {"single": "center", "dual": "bl"}
MOVE_HALF = 0.175                                    # 没有够长的字幕停顿时：场景交界前后各 0.175 s 移动（整段 0.35 s）
MOVE_DUR = 0.35                                      # 有字幕停顿时：整段移动 0.35 s，放进停顿里（离场景交界最近的那个）；face.json 写 "move": "cut" = 0.04 s 瞬间跳过去


def layers(out_dir, size, sticker):
    S = 3
    out_dir.mkdir(exist_ok=True)
    big = Image.new("RGBA", (CW * S, CW * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([(OX + SH) * S, (OY + SH) * S, (OX + size + SH) * S, (OY + size + SH) * S], radius=RAD * S, fill=(0xFF, 0x4F, 0x1A, 255))
    big.resize((CW, CW), Image.LANCZOS).save(out_dir / "shadow.png")
    ring = Image.new("RGBA", (CW * S, CW * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(ring)
    d.rounded_rectangle([(OX - 7) * S, (OY - 7) * S, (OX + size + 7) * S, (OY + size + 7) * S], radius=(RAD + 7) * S, outline=(0x14, 0x14, 0x13, 255), width=7 * S)
    ring = ring.resize((CW, CW), Image.LANCZOS)
    if sticker:
        f = ImageFont.truetype(str(FONT), 34)
        f.set_variation_by_axes([800])
        tw = int(f.getlength(sticker)) + 36
        st = Image.new("RGBA", (tw, 58), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([0, 0, tw - 1, 57], radius=10, fill=(0xFF, 0xD8, 0x4D, 255), outline=(0x14, 0x14, 0x13, 255), width=4)
        sd.text((18, 6), sticker, font=f, fill=(0x14, 0x14, 0x13, 255))
        st = st.rotate(-3, expand=True, resample=Image.BICUBIC)
        ring.alpha_composite(st, (OX + size - tw + 22, OY - 12))
    ring.save(out_dir / "ring.png")
    m = Image.new("L", (size * S, size * S), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size * S - 1, size * S - 1], radius=RAD * S, fill=255)
    m.resize((size, size), Image.LANCZOS).save(out_dir / "mask.png")


MODE_LAYOUT = {"one": "single", "two": "dual", "big": "dual"}     # faceb 版式（场景各自选窗口模式）：one → 按 single 的位置表，two / big → 按 dual 的


def layout_of(tl, layout, sid):
    """这个场景的小窗按哪套位置表走：single / dual 版式整条一样；faceb 版式按场景的 mode（one 单窗居中在字幕下面；two 双窗 / big 大窗缩到左下角）。"""
    if layout != "faceb":
        return layout
    return MODE_LAYOUT[tl["clips"][sid].get("mode", "two")]


def keyframes(tl, plan, layout, size0, overrides):
    """每个场景一个目标位置 (x, y, s)，s = 缩放（相对 BASE_SIZE）；返回 [(t_start, x, y, s), …]"""
    per = {sc["id"]: sc.get("face") for sc in plan.get("plan", [])}
    per.update(overrides)
    out = []
    for sg in tl["segs"]:
        lay = layout_of(tl, layout, sg["id"])
        name = per.get(sg["id"]) or DEFAULT_POS[lay]
        if name == "hide":
            x, y, sz = POS[lay].get("center", (360, 1664, size0))[0], HIDE_Y, size0
        else:
            x, y, sz = POS[lay][name]
            if name == "center" and lay == "single":
                sz = size0
        out.append((sg["s"], x, y, sz / BASE_SIZE))
    return out


def move_windows(kfs, tl):
    """每个转场的 (ta, tb)：尽量放进两条字幕之间的停顿里（窗口移动时不扫过字幕）；没有够长的停顿才退回交界前后 ±0.175 s。"""
    subs = sorted((x["a"], x["b"]) for x in tl.get("subs", []))
    gaps = [(0.0, subs[0][0])] if subs else []
    gaps += [(subs[i][1], subs[i + 1][0]) for i in range(len(subs) - 1)]
    if subs:
        gaps.append((subs[-1][1], tl["total"]))
    D, wins = MOVE_DUR, []
    for k in kfs[1:]:
        T, best = k[0], None
        for g0, g1 in gaps:
            if g1 - g0 < D + 0.06 or g1 < T - 1.0 or g0 > T + 1.0:
                continue
            ta = min(max(T - D / 2, g0 + 0.03), g1 - D - 0.03)
            cost = abs(ta + D / 2 - T)
            if best is None or cost < best[0]:
                best = (cost, ta)
        wins.append((best[1], best[1] + D) if best else (T - MOVE_HALF, T + MOVE_HALF))
    return wins


def expr(kfs, idx, wins):
    """第 idx 个分量（1 = x, 2 = y, 3 = s）的表达式：v0 + Σ (v_k − v_{k−1}) × smoothstep(t)"""
    v0 = kfs[0][idx]
    terms = []
    for (a, b), (ta, tb) in zip(zip(kfs, kfs[1:]), wins):
        dv = b[idx] - a[idx]
        if abs(dv) < 1e-9:
            continue
        p = f"min(1,max(0,(t-{ta:.3f})/{tb - ta:.3f}))"
        terms.append(f"({dv:.4f})*{p}*{p}*(3-2*{p})")
    return f"{v0:.4f}" + ("+" + "+".join(terms) if terms else "")


SUB_BAND = {"single": (1490, 1620), "dual": (1756, 1884)}      # 字幕条所在的 y 范围（中文 + 英文两行，上下各留一点）；窗口盖到这里就报警


def smooth(t, ta, tb):
    p = min(1.0, max(0.0, (t - ta) / (tb - ta)))
    return p * p * (3 - 2 * p)


def at(kfs, t, wins):
    x, y, sc = kfs[0][1], kfs[0][2], kfs[0][3]
    for (a, b), (ta, tb) in zip(zip(kfs, kfs[1:]), wins):
        e = smooth(t, ta, tb)
        x += (b[1] - a[1]) * e
        y += (b[2] - a[2]) * e
        sc += (b[3] - a[3]) * e
    return x, y, sc * BASE_SIZE


def check_subtitle_overlap(kfs, wins, layout, total, tl=None):
    """逐 0.05 s 采样窗口（含阴影 / 描边 / 贴纸）和字幕条有没有重叠；停着的位置盖字幕 = 错，移动路上扫过 = 提醒。
    faceb 版式的字幕条跟着场景走（单窗 y 1490–1620、双窗 / 大窗 y 1756–1884），按当时所在场景的 mode 取。"""
    if layout == "faceb":
        band = lambda t: SUB_BAND[layout_of(tl, layout, next(g for g in reversed(tl["segs"]) if g["s"] <= t + 1e-6)["id"])]
        top, bot = SUB_BAND["single"][0], SUB_BAND["dual"][1]            # 只用在下面的提示文字里
    else:
        top, bot = SUB_BAND[layout]
        band = lambda t: (top, bot)
    hit, t = [], 0.0
    while t <= total:
        x, y, sz = at(kfs, t, wins)
        b0, b1 = band(t)
        if y - 14 < b1 and y + sz + 14 > b0:
            hit.append(round(t, 2))
        t += 0.05
    if not hit:
        print(f"字幕检查：窗口全程没有盖到字幕条（{layout} 版字幕 y {top}–{bot}）")
        return
    runs, start, prev = [], hit[0], hit[0]
    for h in hit[1:]:
        if h - prev > 0.06:
            runs.append((start, prev)); start = h
        prev = h
    runs.append((start, prev))
    for a, b in runs:
        kind = "移动途中扫过" if b - a <= 0.6 else "停着盖住了"
        print(f"⚠ 字幕检查：{a:.2f}–{b:.2f} s 窗口{kind}字幕条（{layout} 版字幕 y {top}–{bot}）——{'介意就在 face.json 写 "move": "cut"（直接跳过去），或让位置保持不动' if kind.startswith('移动') else '换位置（plan.json 的 face 字段）'}")


def nb_frames(path):
    """mp4 头里的视频帧数（不解码，秒出）；取不到返回 0。"""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=nb_frames", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()
    return int(r) if r.isdigit() else 0


def main():
    global MOVE_DUR, MOVE_HALF
    ap = argparse.ArgumentParser()
    ap.add_argument("ep")
    ap.add_argument("--base", default="整片_v1_cards无小窗.mp4")
    ap.add_argument("--out", default="整片_v1.mp4")
    ap.add_argument("--seconds", type=float, default=0.0, help="只合成前 N 秒（测试用）")
    ap.add_argument("--moves", default="", help='临时覆盖场景位置，例 "A2:bl,A5:tl"')
    a = ap.parse_args()
    ep = Path(a.ep)
    here = ep / "制作" / "00_整片"
    cfg = json.loads((here / "face.json").read_text(encoding="utf-8"))
    tl = json.loads((here / "timeline.json").read_text(encoding="utf-8"))
    plan = json.loads((ep / "台本" / "plan.json").read_text(encoding="utf-8"))
    layout = tl.get("layout", "single")
    if cfg.get("move") == "cut":                      # 不要滑动、直接跳到新位置（滑动时单框版的窗口会扫过字幕条约 0.15 s）
        MOVE_DUR, MOVE_HALF = 0.04, 0.02
    size0 = int(cfg.get("size", 360))
    overrides = dict(x.split(":") for x in a.moves.split(",") if ":" in x)
    kfs = keyframes(tl, plan, layout, size0, overrides)
    dur = a.seconds or cfg.get("duration") or tl["total"]
    layers(here / "_face", BASE_SIZE, cfg.get("sticker", "出镜"))
    c = cfg.get("crop", {"cx": 0.515, "cy": 0.449, "side": 0.787})
    wins = move_windows(kfs, tl)
    sx = expr(kfs, 1, wins) + f"-{OX}*({expr(kfs, 3, wins)})"
    sy = expr(kfs, 2, wins) + f"-{OY}*({expr(kfs, 3, wins)})"
    sc = expr(kfs, 3, wins)
    scale = f"scale=w='trunc({CW}*({sc})/2)*2':h='trunc({CW}*({sc})/2)*2':eval=frame:flags=bicubic"
    mirror = ",hflip" if cfg.get("mirror", True) else ""
    crop = f"crop=w='in_h*{c['side']}':h='in_h*{c['side']}':x='in_w*{c['cx']}-in_h*{c['side']}/2':y='in_h*{c['cy']}-in_h*{c['side']}/2'"
    fc = (f"[1:v]fps=30,{crop},scale={BASE_SIZE}:{BASE_SIZE}:flags=lanczos{mirror},format=yuv420p[fc];"
          f"[4:v]format=gray[mk];[fc][mk]alphamerge[fa];"
          f"[fa]format=rgba,pad={CW}:{CW}:{OX}:{OY}:color=black@0[fp];"
          f"[2:v]format=rgba,{scale}[sh];[fp]{scale}[fs];[3:v]format=rgba,{scale}[rg];"
          f"[0:v][sh]overlay=x='{sx}':y='{sy}':eval=frame:format=auto[b1];"
          f"[b1][fs]overlay=x='{sx}':y='{sy}':eval=frame:format=auto[b2];"
          f"[b2][rg]overlay=x='{sx}':y='{sy}':eval=frame:format=auto,format=yuv420p[v]")
    L = here / "_face"
    base = here / a.base
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(base), "-ss", f"{cfg.get('start', 0)}", "-t", f"{dur}", "-i", cfg["src"],
           "-loop", "1", "-t", f"{dur}", "-i", str(L / "shadow.png"), "-loop", "1", "-t", f"{dur}", "-i", str(L / "ring.png"),
           "-loop", "1", "-t", f"{dur}", "-i", str(L / "mask.png"),
           "-filter_complex", fc, "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
           "-c:a", "copy", "-movflags", "+faststart", "-shortest", str(here / a.out)]
    print("位置关键帧：", [(round(k[0], 2), k[1], k[2], round(k[3] * BASE_SIZE)) for k in kfs])
    check_subtitle_overlap(kfs, wins, layout, tl["total"], tl)
    print("移动窗口：",[(round(a, 2), round(b, 2)) for a, b in wins])
    want = nb_frames(base) if not a.seconds else 0
    for attempt in (1, 2):
        subprocess.run(cmd, check=True)
        got = nb_frames(here / a.out)
        if not want or got >= want:
            break
        # 2026-10-06《Claude官方教程》第 1 期出镜版：同样的输入第一次合成 17230 帧、重渲后第二次只有 17227 帧（-shortest 在片尾丢了 3 帧，原因没查清）——合成完核对帧数，少了就重跑一次
        print(f"⚠ 合成后 {got} 帧 < base {want} 帧（少 {want - got} 帧 = 片尾 {(want - got) / 30:.2f} s 的静帧）" + ("，重跑一次" if attempt == 1 else "：重跑后还是少，片尾短一点点，不影响观看；要补齐就加 tpad 或换 -t"))
    print("ok ->", here / a.out)


if __name__ == "__main__":
    sys.exit(main())
