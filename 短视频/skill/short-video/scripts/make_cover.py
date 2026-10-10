# -*- coding: utf-8 -*-
r"""短视频封面：真实画面 + 短钩子大字（+ 箭头指主角），出三个比例。

  python make_cover.py <本条目录>            读 <本条>\制作\04_封面\cover.json，出 cover_3x4.png（1080×1440）、cover_16x9.png（1920×1080）、cover_4x3.png（1440×1080）
  python make_candidates.py <本条目录>       一次出 3 个候选 × 三个比例 + 总览图（交付包用；候选写在 candidates.json，每个候选 = 一份 cover.json 的字段）

cover.json：
  "frame": {"video": 视频路径（相对 cover.json，或绝对）, "t": 秒, "crop": [x0, y0, x1, y1]（占整帧的比例，可省）}  或  "image": 图片路径
  "big": ["第一行", "第二行"]   短钩子，3–6 字一行（封面协定：大字简短、不放小字；平台标题写详细，和封面不写同一句）
  "style": "shot"（默认）| "split" | "full"
     shot  = 真实画面铺满 + 大字（白字墨描边 + 硬投影，accent_line 那行用强调色）+ 块状箭头指主角（"target": [x, y] 占画面的比例；不写就不画箭头）。
             用户 2026-10-03 的 Tavus 那期：三个“设计过”的封面全否，“截图 + 箭头指主角 + 这是AI！”一次通过——有主角的视频第一个候选就做这个。
     split = 白底，画面占一边，两行大字占另一边（3:4 上图下字；横版左字右图）。
     full  = **满框版（用户 2026-10-04 对 Tavus 那条定的样式：“把文字缩小一点，放在画框中，画框可以充满整个屏幕”“用C封面来发”）**：奶油点阵底，
             白框墨边硬投影的方框铺满整张封面（四周只留 30 px 放投影），框里是画面（按比例自动裁：3:4 脸居中偏下，横版脸在左 / 右三分之一），
             大字（衬线粗体，强调色 + 墨色描边 + 硬投影）缩小放进画框里、盖在画面上方的空处，块状箭头从旁边指脸；左上“官方演示 | 来源”小标签、右上“画面：…”小条（"tags"，可省）。
             "target": [x, y]  脸 / 主角中心，占画面的比例；不写就用 OpenCV 检脸，检不到按画面中心（要指别处就写）
             "face_w": 脸宽占画面宽的比例（可省，检脸时自动，默认 0.16；决定箭头离脸多远）
             "avoid": [[x0, y0, x1, y1], …]  占画面的比例：裁窗要躲开的区域（例如视频通话的小窗、水印）；先平移躲，躲不开就放大一点再躲；也可以按比例写 {"3x4": […], "4x3": […]}（没列的比例不躲）
             "keep_clear": [[x0, y0, x1, y1], …]  占画面的比例：留在画面里、但大字不能盖住的区域（横版里没躲掉的小窗）；avoid 里的区域字也自动躲开
             "zoom": 1.0（或 {"3x4": 1.1, "16x9": 1.3}）  再放大一点；"text_side": "left" | "right"  横版字放哪边（可省，默认放在脸的另一边）
             "theme": {"ink": "#140206", "accent": "#FF6183", "cream": "#F7F4EF"}  墨 / 强调 / 底色（可省，默认墨黑 + 橙 + 米白；第三方产品用对方官网的颜色）
             "tags": {"left": "官方演示", "right": "Griffin 发布视频", "source": "画面：@tavus · X（2026-10-01）"}  左上两段小标签 + 右上来源条（可省）
             大字默认用 Noto Serif SC 900（Google Fonts，要联网；加载不到会报错）。
             "text_style": "sticker"  贴纸字（用户 2026-10-04 贴参考图：“白字 + 橙色，文字大一些”）：Noto Sans SC 900 粗黑体，除 accent_line 那行是强调色外全白，深色粗描边 + 向右下的硬投影；
                                      "font_scale": 1.25 再放大（默认 1.0；字放不下会自动缩回去）；"text_w": 0.62 横版字块最宽占画面区宽度的比例（默认 0.46）。
  "accent_line": 1（哪一行用强调色，可省；shot / split），"accent": "#FF4F1A"（强调色，可省；第三方产品可以用对方官网的主色；full 里等于 theme.accent）
字放不下会自动缩，缩到 < 90 px（full 里 < 80 px）就报错（字太多了）。

参考实现（Tavus 那条手调的版本）：独立视频\短视频\01_Tavus-Griffin\制作\04_封面\make_cover_vertical.py（C 3:4、E 16:9、F 4:3、G 4:3 无小窗）。
"""
import json
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

FONTS = "file:///D:/大疆/AI科普/素材/字体/fonts.css"
GF = "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@900&display=block"
SIZES = {"3x4": (1080, 1440), "16x9": (1920, 1080), "4x3": (1440, 1080)}

PAGE = """<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{fonts}">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{w}px; height:{h}px; overflow:hidden; background:#FAF9F5; font-family:'Noto Sans SC'; }}
#img {{ position:absolute; {imgpos} background:url('{img}') {bgpos}/cover no-repeat; }}
#txt {{ position:absolute; {txtpos} display:flex; flex-direction:column; justify-content:{just}; }}
.l {{ font:900 {fs}px/1.16 'Noto Sans SC'; white-space:nowrap; }}
.shot .l {{ color:#fff; -webkit-text-stroke:{stroke}px #141413; paint-order:stroke fill; text-shadow:{sh}px {sh}px 0 #141413; }}
.shot .l.a {{ color:{accent}; }}
.split #txt {{ padding-left:40px; border-left:14px solid {accent}; }}
.split .l {{ color:#141413; }}
.split .l.a span {{ color:{accent}; background:linear-gradient(transparent 60%, #FFD84D 60%, #FFD84D 92%, transparent 92%); padding:0 8px; }}
svg {{ position:absolute; left:0; top:0; overflow:visible; }}
</style></head><body class="{style}"><div id="img"></div><div id="txt">{lines}</div><svg id="arr" width="{w}" height="{h}"></svg></body></html>"""

ARROW_JS = """([iw, ih, fx, fy, accent]) => {
  // 背景图 cover + background-position fx% fy%：算出主角在画布上的位置
  const box = document.getElementById('img').getBoundingClientRect();
  const s = Math.max(box.width / iw, box.height / ih), dw = iw * s, dh = ih * s;
  const tx = box.left + (box.width - dw) * fx + fx * dw, ty = box.top + (box.height - dh) * fy + fy * dh;
  // 箭头从字块离主角最近的那个角出发，尖端停在主角前 30 px
  const t = document.getElementById('txt').getBoundingClientRect();
  const sx = tx > t.right ? t.right + 20 : (tx < t.left ? t.left - 20 : (t.left + t.right) / 2);
  const sy = ty > t.bottom ? t.bottom + 10 : (ty < t.top ? t.top - 10 : (t.top + t.bottom) / 2);
  const dx = tx - sx, dy = ty - sy, L = Math.hypot(dx, dy) - 30;
  if (L < 120) return 'too-close';
  const ux = dx / Math.hypot(dx, dy), uy = dy / Math.hypot(dx, dy), nx = -uy, ny = ux;
  const sw = 34, hw = 92, hl = 96, ex = sx + ux * L, ey = sy + uy * L, bx = ex - ux * hl, by = ey - uy * hl;
  const P = [[sx + nx * sw / 2, sy + ny * sw / 2], [bx + nx * sw / 2, by + ny * sw / 2], [bx + nx * hw / 2, by + ny * hw / 2], [ex, ey],
             [bx - nx * hw / 2, by - ny * hw / 2], [bx - nx * sw / 2, by - ny * sw / 2], [sx - nx * sw / 2, sy - ny * sw / 2]];
  const pts = P.map(p => p.map(v => v.toFixed(1)).join(',')).join(' ');
  document.getElementById('arr').innerHTML =
    `<polygon points="${pts}" transform="translate(8,8)" fill="#141413"/>` +
    `<polygon points="${pts}" fill="${accent}" stroke="#141413" stroke-width="7" stroke-linejoin="round"/>`;
  return 'ok';
}"""


def layout(style, kind, w, h, fx, fy):
    bgpos = f"{fx * 100:.1f}% {fy * 100:.1f}%"
    if style == "shot":
        # 字放在离主角最远的角：主角在上半边 → 字在下面，反之在上面；横版再放到主角的另一侧，字块宽 ≤ 画面一半，别压到主角（尤其头顶）
        v = "bottom:80px;" if fy < 0.5 else "top:80px;"
        if kind == "3x4":
            hpos = "left:70px; right:70px;"
        else:
            hpos = f"left:70px; width:{int(w * 0.5)}px;" if fx >= 0.5 else f"right:70px; width:{int(w * 0.5)}px; align-items:flex-end;"
        return dict(imgpos="left:0; top:0; width:100%; height:100%;", bgpos=bgpos, txtpos=f"{hpos} {v} height:auto;", just="flex-start",
                    fs=190 if kind == "16x9" else 170, stroke=16, sh=10)
    if kind == "3x4":
        return dict(imgpos="left:0; top:0; width:100%; height:62%;", bgpos=bgpos, txtpos=f"left:70px; right:50px; top:{int(h * 0.62) + 40}px; bottom:50px;",
                    just="center", fs=150, stroke=0, sh=0)
    return dict(imgpos="right:0; top:0; width:58%; height:100%;", bgpos=bgpos, txtpos=f"left:70px; width:{int(w * 0.42) - 100}px; top:90px; bottom:90px;",
                just="center", fs=150 if kind == "16x9" else 130, stroke=0, sh=0)


# ------------------------------------------------------------------ full：满框版（Tavus 那条用户定的样式）
MARGIN, PAD, BORDER, SHADOW = 30, 14, 3, 12                     # 方框离画布边 / 白边 / 墨边 / 硬投影
FULL_FS = {"3x4": 170, "16x9": 150, "4x3": 130}                 # 一行字的起始字号（太宽会自动缩）
FULL_TOP = {"3x4": 150, "16x9": 130, "4x3": 130}                # 大字墨迹框的上沿（画布 y）
FULL_ARROW = {"3x4": (0.9, 0.26, -35.0), "16x9": (1.0, 0.17, -12.0), "4x3": (0.95, 0.19, -12.0)}   # 箭头缩放、长度（占画布宽）、方向角（负 = 箭尾在右下）
FULL_FACE_Y = {"3x4": 0.60, "16x9": 0.56, "4x3": 0.56}          # 脸中心在裁窗里的纵向位置（上面留给大字）


def _rgba(hexc, a):
    h = hexc.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


def detect_face(img):
    """OpenCV Haar 检最大的正脸：返回 (cx, cy, w) 占画面的比例；没装 OpenCV 或检不到返回 None。"""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return None
    g = cv2.cvtColor(np.array(img.convert("RGB"))[:, :, ::-1], cv2.COLOR_BGR2GRAY)
    s = min(1.0, 1280 / max(g.shape))
    if s < 1:
        g = cv2.resize(g, None, fx=s, fy=s)
    cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    found = cas.detectMultiScale(g, 1.1, 6, minSize=(40, 40))
    if len(found) == 0:
        return None
    x, y, w, h = max(found, key=lambda r: r[2] * r[3])
    gh, gw = g.shape
    return (x + w / 2) / gw, (y + h / 2) / gh, w / gw


def pick_window(kind, Fw, Fh, fpx, fpy, aspect, side, zoom, avoid):
    """在整帧（Fw×Fh）里裁一个比例 = aspect 的窗口：脸中心放在窗口的 (fx_frac, FULL_FACE_Y) 处；窗口碰到 avoid 里的矩形就先平移、再放大躲开。
    返回 ((x0, y0, x1, y1), 实际放大倍数)；躲不开时放大倍数取负数（调用方报警）。"""
    if Fw / Fh >= aspect:
        ww, wh = Fh * aspect, float(Fh)
    else:
        ww, wh = float(Fw), Fw / aspect
    fx_frac = 0.5 if kind == "3x4" else (0.36 if side == "right" else 0.64)
    fy_frac = FULL_FACE_Y[kind]
    z = max(1.0, zoom)
    while True:
        w, h = ww / z, wh / z
        x0 = min(max(fpx - fx_frac * w, 0), Fw - w)
        y0 = min(max(fpy - fy_frac * h, 0), Fh - h)
        hit = [r for r in avoid if x0 < r[2] and x0 + w > r[0] and y0 < r[3] and y0 + h > r[1]]
        if not hit:
            return (x0, y0, x0 + w, y0 + h), z
        for r in hit:                                              # 先试着平移到 avoid 的右边 / 左边，脸还要留在窗口 12%–88% 之间
            for nx in (r[2], r[0] - w):
                if 0 <= nx <= Fw - w and 0.12 <= (fpx - nx) / w <= 0.88 and not any(nx < q[2] and nx + w > q[0] and y0 < q[3] and y0 + h > q[1] for q in avoid):
                    return (nx, y0, nx + w, y0 + h), z
        z *= 1.06
        if z > 2.4:
            return (x0, y0, x0 + w, y0 + h), -z


def arrow_polygon(cx, cy, s, a, shadow, ink, accent):
    """块状箭头（直角）。tip = 脸中心沿箭头方向退 gap；方向角 ang：从箭尾指向箭头的方向，0 = 朝左，负 = 箭尾在右下（箭头朝左上）。返回 svg 片段（含硬投影）。"""
    ang = math.radians(a["ang"])
    ux, uy = -math.cos(ang), math.sin(ang)
    tipx, tipy = cx - ux * a["gap"] * s, cy - uy * a["gap"] * s
    L, t, w, hl = (a[k] * s for k in ("length", "shaft", "head_w", "head_l"))
    local = [(0, 0), (-hl, w / 2), (-hl, t / 2), (-L, t / 2), (-L, -t / 2), (-hl, -t / 2), (-hl, -w / 2)]
    nx, ny = -uy, ux

    def pts(dx, dy):
        return " ".join(f"{tipx + x * ux + y * nx + dx:.1f},{tipy + x * uy + y * ny + dy:.1f}" for x, y in local)
    sw = 9
    return (f'<polygon points="{pts(shadow, shadow)}" fill="{ink}" stroke="{ink}" stroke-width="{sw}" stroke-linejoin="round"/>'
            f'<polygon points="{pts(0, 0)}" fill="{accent}" stroke="{ink}" stroke-width="{sw}" stroke-linejoin="round"/>'), (tipx, tipy), (ux, uy)


class InkMeter:
    """量衬线大字的墨迹框（含描边）：返回 (相对 left 的偏移, 相对 top 的偏移, 宽, 高)。"""

    def __init__(self, browser):
        self.pg = browser.new_page(viewport={"width": 2400, "height": 800})

    def measure(self, text, fs, ink, sticker=False):
        from io import BytesIO
        stroke = round(fs * (0.075 if sticker else 0.062))
        fam = "Noto Sans SC" if sticker else "Noto Serif SC"
        self.pg.set_content(f'<meta charset="utf-8"><link rel="stylesheet" href="{GF}"><link rel="stylesheet" href="{FONTS}"><body style="margin:0;background:transparent">'
                            f'<div style="position:absolute;left:300px;top:200px;font-size:{fs}px;line-height:1.05;white-space:nowrap;font-family:&quot;{fam}&quot;,serif;'
                            f'font-weight:900;letter-spacing:-.01em;color:#f00;-webkit-text-stroke:{stroke * 2}px {ink};paint-order:stroke fill">{text}</div></body>')
        self.pg.evaluate("async ([t, fam]) => { await document.fonts.load('900 100px \"' + fam + '\"', t); await document.fonts.ready; }", [text, fam])
        self.pg.wait_for_timeout(150)
        x0, y0, x1, y1 = Image.open(BytesIO(self.pg.screenshot(omit_background=True))).getchannel("A").getbbox()
        return x0 - 300, y0 - 200, x1 - x0, y1 - y0

    def close(self):
        self.pg.close()


def render_full(b, cfg, src, kind, out, meter):
    th = {"ink": "#141413", "accent": cfg.get("accent", "#FF4F1A"), "cream": "#FAF9F5", **cfg.get("theme", {})}
    ink, acc, cream = th["ink"], th["accent"], th["cream"]
    W, H = SIZES[kind]
    cw, chh = W - 2 * MARGIN - SHADOW, H - 2 * MARGIN - SHADOW          # 方框外尺寸
    ox = oy = MARGIN + PAD + BORDER                                    # 画面区左上
    iw, ih = cw - 2 * (PAD + BORDER), chh - 2 * (PAD + BORDER)         # 画面区尺寸
    im = Image.open(src).convert("RGB")
    Fw, Fh = im.size
    t, fw = cfg.get("target"), cfg.get("face_w")
    if t is None:
        d = detect_face(im)
        if d:
            t, fw = [d[0], d[1]], fw or d[2]
        else:
            t = [0.5, 0.5]
            print(f"  {kind}：没检到脸，按画面中心放箭头（要指别处就写 target）")
    fw = fw or 0.16
    fpx, fpy = t[0] * Fw, t[1] * Fh
    side = cfg.get("text_side") or ("right" if t[0] < 0.55 else "left")
    zoom = cfg.get("zoom", 1.0)
    zoom = zoom.get(kind, 1.0) if isinstance(zoom, dict) else zoom
    av = cfg.get("avoid", [])
    av = av.get(kind, av.get("all", [])) if isinstance(av, dict) else av         # avoid 也可以按比例写：{"3x4": [...], "4x3": [...]}
    avoid = [[r[0] * Fw, r[1] * Fh, r[2] * Fw, r[3] * Fh] for r in av]
    (x0, y0, x1, y1), z = pick_window(kind, Fw, Fh, fpx, fpy, iw / ih, side, zoom, avoid)
    if z < 0:
        print(f"  {kind}：窗口躲不开 avoid 区域（放大到 {-z:.2f}× 还是碰到），封面上会露出一截——调 target / avoid / zoom")
    if kind != "3x4" and not cfg.get("text_side"):                          # 横版：字放在脸实际所在位置的另一边（躲 avoid 时脸可能被挤到窗口另一侧）
        side = "right" if (fpx - x0) / (x1 - x0) < 0.5 else "left"
    win = im.crop(tuple(round(v) for v in (x0, y0, x1, y1))).resize((iw, ih), Image.LANCZOS)
    win_path = out.with_name(f"_full_{out.stem}_win.png")
    win.save(win_path)
    k = iw / (x1 - x0)                                                  # 一个原片像素 = k 个封面像素
    fcx, fcy = ox + (fpx - x0) * k, oy + (fpy - y0) * k                # 脸中心在封面上的位置
    face_px = fw * Fw * k                                               # 脸宽（封面像素）

    # 大字：放进画框里、盖在画面上方（3:4 居中；横版放在脸的另一边）
    lines = cfg["big"] if isinstance(cfg["big"], list) else [cfg["big"]]
    sticker = cfg.get("text_style") == "sticker"                        # 贴纸字：粗黑体，白字 + 强调色那行，深色粗描边 + 硬投影（用户贴的参考图 2026-10-04）
    fs = int(FULL_FS[kind] * (0.88 if len(lines) > 1 else 1.0) * cfg.get("font_scale", 1.0))
    maxw = (iw - (60 if sticker else 100)) if kind == "3x4" else iw * (cfg.get("text_w", 0.46))
    while True:
        boxes = [meter.measure(ln, fs, ink, sticker) for ln in lines]
        if max(bb[2] for bb in boxes) <= maxw:
            break
        fs -= 6
        if fs < 80:
            sys.exit(f"{kind}：大字缩到 80 px 还放不下，字太多了（封面每行 3–6 字）")
    if kind == "3x4":
        cx = W / 2
    else:
        # 横版：字块放左 / 右哪边，看和“脸 + 肩”、被 avoid 盖住的区域（小窗）重叠最少；cfg.text_side 指定就用指定的
        tw, thh = max(bb[2] for bb in boxes), fs * len(lines)
        rects = [(fcx - 0.65 * face_px, fcy - 0.8 * face_px, fcx + 0.65 * face_px, fcy + 0.9 * face_px)]
        clear = [[r[0] * Fw, r[1] * Fh, r[2] * Fw, r[3] * Fh] for r in cfg.get("keep_clear", [])]      # keep_clear：画面里要保留、但字不能盖住的区域（例：横版里保留的通话小窗）
        rects += [(ox + (r[0] - x0) * k, oy + (r[1] - y0) * k, ox + (r[2] - x0) * k, oy + (r[3] - y0) * k) for r in avoid + clear
                  if r[0] < x1 and r[2] > x0 and r[1] < y1 and r[3] > y0]
        cx_of = {"right": ox + iw * 0.72, "left": ox + iw * 0.28}

        def overlap(sd):
            tr = (cx_of[sd] - tw / 2, FULL_TOP[kind], cx_of[sd] + tw / 2, FULL_TOP[kind] + thh)
            return sum(max(0, min(tr[2], q[2]) - max(tr[0], q[0])) * max(0, min(tr[3], q[3]) - max(tr[1], q[1])) for q in rects)
        if not cfg.get("text_side"):
            side = min(("right", "left"), key=lambda sd: (overlap(sd), 0 if sd == side else 1))
        cx = cx_of[side]
    stroke, off = round(fs * (0.075 if sticker else 0.062)), round(fs * (0.06 if sticker else 0.05))
    acc_line = cfg.get("accent_line", 1)
    fam = "'Noto Sans SC',sans-serif" if sticker else "'Noto Serif SC',serif"
    txt, y = "", FULL_TOP[kind]
    for li, (ln, (ix, iy, bw, bh)) in enumerate(zip(lines, boxes)):
        base = (f"left:{cx - bw / 2 - ix:.1f}px;top:{y - iy:.1f}px;font-size:{fs}px;line-height:1.05;white-space:nowrap;"
                f"font-family:{fam};font-weight:900;letter-spacing:-.01em")
        fill = ("#fff" if li != acc_line else acc) if sticker else acc
        txt += (f'<div class="abs" style="{base};color:{ink};-webkit-text-stroke:{stroke * 2}px {ink};transform:translate({off}px,{off}px)">{ln}</div>'
                f'<div class="abs" style="{base};color:{fill};-webkit-text-stroke:{stroke * 2}px {ink};paint-order:stroke fill">{ln}</div>')
        y += fs
    text_bottom = y
    head_top = fcy - 0.78 * face_px                                     # 头顶大致位置（脸高 ≈ 1.25 × 脸宽的一半多一点）
    if text_bottom + 10 > head_top and (kind == "3x4" or abs(cx - fcx) < maxw / 2 + face_px / 2):
        print(f"  {kind}：大字下沿 y≈{text_bottom:.0f} 可能压到头顶（y≈{head_top:.0f}）——调 zoom / target，或把字缩短")

    # 箭头：从字那一边指向脸，尖端停在脸边上；尾巴别出画面区
    s_arrow, len_frac, ang = FULL_ARROW[kind]
    if side == "left":
        ang = -180 - ang                                                 # 镜像：箭尾在左下
    a = dict(gap=0.95 * face_px / 2 / s_arrow, length=len_frac * W / s_arrow, shaft=52, head_w=134, head_l=108, ang=ang)
    _, tip, (ux, uy) = arrow_polygon(fcx, fcy, s_arrow, a, SHADOW, ink, acc)
    room = []
    if abs(ux) > 1e-3:
        room.append(((tip[0] - ox - 20) / ux) if ux > 0 else ((ox + iw - 20 - tip[0]) / -ux))
    if abs(uy) > 1e-3:
        room.append(((tip[1] - oy - 20) / uy) if uy > 0 else ((oy + ih - 20 - tip[1]) / -uy))
    if room:
        a["length"] = max(0.4 * a["length"], min(a["length"], min(room) / s_arrow))
    arrow, _, _ = arrow_polygon(fcx, fcy, s_arrow, a, SHADOW, ink, acc)

    # 标签（可省）
    tags, tg = "", cfg.get("tags") or {}
    st = {"3x4": 0.8, "16x9": 1.0, "4x3": 0.9}[kind]
    if tg.get("left"):
        tags += (f'<div style="position:absolute;left:{22 * st:.0f}px;top:{20 * st:.0f}px;display:flex;align-items:stretch;border:{3 * st:.1f}px solid {ink};box-shadow:{5 * st:.0f}px {5 * st:.0f}px 0 {ink};z-index:5">'
                 f'<div style="background:{acc};color:{ink};font:800 {27 * st:.0f}px \'Noto Sans SC\';padding:{7 * st:.0f}px {18 * st:.0f}px;white-space:nowrap">{tg["left"]}</div>'
                 + (f'<div style="background:{cream};color:{ink};font:700 {24 * st:.0f}px \'Space Grotesk\',\'Noto Sans SC\';padding:{7 * st:.0f}px {18 * st:.0f}px;white-space:nowrap;display:flex;align-items:center;letter-spacing:.03em">{tg["right"]}</div>' if tg.get("right") else "")
                 + '</div>')
    if tg.get("source"):
        tags += (f'<div style="position:absolute;right:{22 * st:.0f}px;top:{20 * st:.0f}px;background:{ink};color:{cream};font:700 {25 * st:.0f}px \'Noto Sans SC\';padding:{8 * st:.0f}px {20 * st:.0f}px;'
                 f'white-space:nowrap;z-index:5;border:{3 * st:.1f}px solid {ink};box-shadow:{5 * st:.0f}px {5 * st:.0f}px 0 {acc}">{tg["source"]}</div>')
    css = (f"@import url('{FONTS}');* {{margin:0;padding:0;box-sizing:border-box}}body{{background:{cream};font-family:'Noto Sans SC',sans-serif}}"
           f".cv{{position:relative;overflow:hidden;background:{cream}}}.abs{{position:absolute}}"
           f".dots{{background-image:radial-gradient(circle,{_rgba(ink, .07)} 2.2px,transparent 2.8px);background-size:36px 36px}}")
    html = (f'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="{GF}"><link rel="stylesheet" href="{FONTS}"><style>{css}</style>'
            f'<body><div class="cv" style="width:{W}px;height:{H}px"><div class="abs dots" style="left:0;top:0;width:{W}px;height:{H}px"></div>'
            f'<div class="abs" style="left:{MARGIN}px;top:{MARGIN}px;width:{cw}px;height:{chh}px;background:{ink};transform:translate({SHADOW}px,{SHADOW}px)"></div>'
            f'<div class="abs" style="left:{MARGIN}px;top:{MARGIN}px;width:{cw}px;height:{chh}px;background:#fff;border:{BORDER}px solid {ink};padding:{PAD}px">'
            f'<div style="position:relative;width:100%;height:100%;overflow:hidden;background:{ink}"><img src="{win_path.as_uri()}" style="position:absolute;left:0;top:0;width:100%;height:100%;display:block">{tags}</div></div>'
            f'<svg class="abs" style="left:0;top:0" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{arrow}</svg>{txt}</div></body>')
    html_path = out.with_name(f"_full_{out.stem}.html")
    html_path.write_text(html, encoding="utf-8")
    pg = b.new_page(viewport={"width": W, "height": H})
    pg.goto(html_path.as_uri())
    pg.wait_for_timeout(500)
    need = "Noto Sans SC" if sticker else "Noto Serif SC"
    pg.evaluate("async (f) => { await document.fonts.load('900 100px \"' + f + '\"', '封面'); await document.fonts.ready; }", need)
    ok = pg.evaluate("[...document.fonts].filter(f => f.status==='loaded').map(f => f.family.replace(/[\"']/g,''))")
    if need not in ok:
        sys.exit(f"字体没加载到：full 样式的大字要 {need} 900（Serif 要联网取 Google Fonts，Sans 用本地 fonts.css）")
    pg.wait_for_timeout(200)
    pg.screenshot(path=str(out))
    pg.close()
    win_path.unlink(missing_ok=True)
    return f"full，大字 {fs} px，窗口 {x1 - x0:.0f}×{y1 - y0:.0f}（放大 {abs(z):.2f}×），脸 ({fcx:.0f}, {fcy:.0f})"


# ------------------------------------------------------------------ 公共
def source_image(cdir, cfg, name):
    """cfg 里的 image（图片）或 frame（视频 + 秒 + 可选 crop 比例）→ 源图路径（视频帧存成 cdir/name）。"""
    if "image" in cfg:
        return (cdir / cfg["image"]).resolve()
    src, f = cdir / name, cfg["frame"]
    vf = "scale=iw:ih"
    if f.get("crop"):
        x0, y0, x1, y1 = f["crop"]
        vf = f"crop=iw*{x1 - x0:.5f}:ih*{y1 - y0:.5f}:iw*{x0:.5f}:ih*{y0:.5f}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(f["t"]), "-i", str((cdir / f["video"]).resolve()), "-frames:v", "1", "-vf", vf, str(src)], check=True)
    return src


def build(cdir, cfg, out_name=lambda kind: f"cover_{kind}.png", src_name="_cover_src.png", browser=None):
    """出一个封面的三个比例（cfg = 一份 cover.json 的内容）。返回 {比例: 输出路径}。browser 可传入已有的 Playwright 浏览器（出多个候选时复用）。"""
    style = cfg.get("style", "shot")
    accent = cfg.get("accent") or cfg.get("theme", {}).get("accent", "#FF4F1A")          # 强调色：accent，或 theme.accent（full 的写法），都没写就用橙色
    src = source_image(cdir, cfg, src_name)
    iw, ih = Image.open(src).size
    fx, fy = cfg.get("target", [0.5, 0.5])
    acc = cfg.get("accent_line", 1)
    big = cfg["big"] if isinstance(cfg["big"], list) else [cfg["big"]]
    lines = "".join(f'<div class="l{" a" if i == acc else ""}"><span>{t}</span></div>' for i, t in enumerate(big))
    outs = {}
    own = browser is None
    if own:
        pw = sync_playwright().start()
        browser = pw.chromium.launch()
    try:
        meter = InkMeter(browser) if style == "full" else None
        for kind, (w, h) in SIZES.items():
            out = cdir / out_name(kind)
            if style == "full":
                info = render_full(browser, cfg, src, kind, out, meter)
                print(f"{out.name}: {w}×{h}，{info}")
                outs[kind] = out
                continue
            L = layout(style, kind, w, h, fx, fy)
            pg = browser.new_page(viewport={"width": w, "height": h})
            fs = L["fs"]
            while True:
                (cdir / "_cover.html").write_text(PAGE.format(fonts=FONTS, w=w, h=h, img=src.as_uri(), lines=lines, style=style, accent=accent, **{**L, "fs": fs}),
                                                  encoding="utf-8")
                pg.goto((cdir / "_cover.html").as_uri())
                pg.evaluate("document.fonts.ready.then(() => true)")
                over = pg.evaluate("""() => { const t = document.getElementById('txt').getBoundingClientRect();
                    const wide = [...document.querySelectorAll('.l span')].some(s => s.getBoundingClientRect().right > t.right + 1);
                    const tall = [...document.querySelectorAll('.l')].some(l => l.getBoundingClientRect().bottom > t.bottom + 1);
                    return wide || tall; }""")
                if not over:
                    break
                fs -= 6
                if fs < 90:
                    sys.exit(f"{kind}：大字缩到 90 px 还放不下，字太多了（封面每行 3–6 字）")
            arrow = pg.evaluate(ARROW_JS, [iw, ih, fx, fy, accent]) if style == "shot" and "target" in cfg else "无"
            pg.screenshot(path=str(out))
            pg.close()
            print(f"{out.name}: {w}×{h}，{style}，大字 {fs} px，箭头 {arrow}")
            outs[kind] = out
        if meter:
            meter.close()
    finally:
        if own:
            browser.close()
            pw.stop()
    return outs


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    ep = Path(sys.argv[1])
    cdir = ep / "制作" / "04_封面"
    cfg = json.loads((cdir / "cover.json").read_text(encoding="utf-8"))
    build(cdir, cfg)


if __name__ == "__main__":
    main()
