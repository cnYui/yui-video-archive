# -*- coding: utf-8 -*-
"""封面（用户 2026-10-02：“做个封面，用超人飞行的那个作为背景”）。

  python make_cover.py → 封面_A/B/C_16x9.png、封面_A/B/C_4x3.png + _封面预览.png；封面_选定_* = SELECTED（默认 A）

背景全部是超人飞行素材（@chetaslua 的 X 视频 c2，1920×1080）里的原帧，没有任何自己画的角色，封面上只有这里加的文字：
  A：Art Deco “METROPOLIS” 海报那一帧（21.3 s）——超人穿过摩天楼，深蓝底，最有电影感
  B：波普四宫格那一帧（26.3 s）——超人从四色头像中间飞过，最抢眼
  C：结尾的 20 种画风总览（38.6 s）——就是那个页面本身，右边 20 张缩略图，左边压暗放字
帧在 ../../素材/封面候选帧/（ffmpeg 从 c2 抽的原帧）。
文字：Claude / Fable 5.5（黄色黑描边，频道惯例）+ 红色小标“官方还没公布”（Fable 5.5 官方没有公布，封面不能暗示已发布）+ 副标 + 右下角素材来源。
"""
import base64
import io
import shutil
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FR = HERE.parents[1] / "素材" / "封面候选帧"
SELECTED = "A"
CHIP = False        # 红标“官方还没公布”：用户 2026-10-02 要求删掉（标题改成“疑似发布”，“其他不变，使用封面A”）；想加回来改成 True 重跑

# 每个版本：帧文件、16:9 / 4:3 的裁剪框（原帧 1920×1080 里的坐标），文字排版
VARIANTS = {
    "A": {"frame": "c2_21.3.png", "crop": {"16x9": (325, 38, 1813, 875), "4x3": (510, 38, 1626, 875)}, "dark": "vignette"},
    "B": {"frame": "c2_26.3.png", "crop": {"16x9": (213, 38, 1701, 875), "4x3": (398, 38, 1514, 875)}, "dark": "vignette"},
    "C": {"frame": "c2_38.6.png", "crop": {"16x9": (0, 0, 1920, 1080), "4x3": (480, 0, 1920, 1080)}, "dark": "left"},
}
SIZE = {"16x9": (1920, 1080), "4x3": (1440, 1080)}


def data_uri(im, q=94):
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


CSS = """
<link rel="stylesheet" href="file:///D:/大疆/AI科普/素材/字体/fonts.css">
<style>
* { box-sizing:border-box; margin:0; padding:0; }
html, body { width:__W__px; height:1080px; overflow:hidden; background:#000; font-family:'Noto Sans SC', sans-serif; }
.bg { position:absolute; inset:0; background:url(__BG__) center/100% 100% no-repeat; }
.shade { position:absolute; inset:0; }
.shade.vignette { background:radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 48%, rgba(0,0,0,.5) 100%), linear-gradient(180deg, rgba(0,0,0,.42) 0%, rgba(0,0,0,0) 30%); }
.shade.left { background:linear-gradient(90deg, rgba(9,12,24,1) 0%, rgba(9,12,24,1) __SOLID__%, rgba(9,12,24,.55) __FADE__%, rgba(9,12,24,0) __END__%); }
.abs { position:absolute; white-space:nowrap; }
.out { -webkit-text-stroke:var(--st) #000; paint-order:stroke fill; text-shadow:0 10px 34px rgba(0,0,0,.6); }
.t1 { color:#fff; font-weight:900; letter-spacing:.03em; }
.t2 { color:#FFD84D; font-weight:900; letter-spacing:-.01em; }
.chip { color:#fff; background:#E11D48; font-weight:900; border-radius:__CR__px; border:__CB__px solid #fff; box-shadow:0 10px 28px rgba(0,0,0,.45); }
.sub { color:#fff; font-weight:800; }
.credit { color:rgba(255,255,255,.92); font-weight:700; text-shadow:0 2px 8px rgba(0,0,0,.8); }
</style>
"""


def layout(variant, w):
    """返回 (html 元素, 参数)：16:9 / 4:3 两套字号和位置。A、B 标题在上、红标在下；C 标题在左边压暗的那一半。"""
    k = 1.0 if w == 1920 else 0.76
    p = lambda v: round(v * k)
    chip_ab = f'<div class="abs chip" style="left:{p(52)}px; top:{p(52)}px; font-size:{p(58)}px; padding:{p(8)}px {p(30)}px; line-height:1.2; transform:rotate(-4deg)">官方还没公布</div>' if CHIP else ""
    chip_c = f'<div class="abs chip" style="left:{p(80)}px; top:{p(590)}px; font-size:{p(60)}px; padding:{p(8)}px {p(32)}px; line-height:1.2">官方还没公布</div>' if CHIP else ""
    if variant in ("A", "B"):
        return f"""
<div class="abs t1 out" style="--st:{p(12)}px; left:0; right:0; text-align:center; top:{p(44)}px; font-size:{p(112)}px; line-height:1.1">Claude</div>
<div class="abs t2 out" style="--st:{p(18)}px; left:0; right:0; text-align:center; top:{p(130)}px; font-size:{p(214)}px; line-height:1.1">Fable 5.5</div>
{chip_ab}
<div class="abs sub out" style="--st:{p(8)}px; left:0; right:0; text-align:center; top:{p(372)}px; font-size:{p(42)}px">网友晒出来的 · 超人飞行 20 种画风</div>
<div class="abs credit" style="right:{p(50)}px; bottom:{p(30)}px; font-size:{p(26)}px">画面：@chetaslua · X</div>"""
    return f"""
<div class="abs t1 out" style="--st:{p(10)}px; left:{p(80)}px; top:{p(250)}px; font-size:{p(112)}px; line-height:1.1">Claude</div>
<div class="abs t2 out" style="--st:{p(16)}px; left:{p(66)}px; top:{p(350)}px; font-size:{p(178)}px; line-height:1.1">Fable 5.5</div>
{chip_c}
<div class="abs sub" style="left:{p(80)}px; top:{p(720)}px; font-size:{p(42)}px; line-height:1.4">网友晒出来的<br>超人飞行 20 种画风</div>
<div class="abs credit" style="left:{p(80)}px; bottom:{p(40)}px; font-size:{p(26)}px">画面：@chetaslua · X</div>"""


def page(variant, ratio):
    w, h = SIZE[ratio]
    v = VARIANTS[variant]
    im = Image.open(FR / v["frame"]).convert("RGB").crop(v["crop"][ratio]).resize((w, h), Image.LANCZOS)
    k = 1.0 if w == 1920 else 0.76
    solid, fade, end = (40, 47, 54) if w == 1920 else (46, 54, 62)      # C：左半边压实到 solid%，再渐变到 end%（把原页面标题完全盖住）
    css = (CSS.replace("__W__", str(w)).replace("__BG__", data_uri(im)).replace("__CR__", str(round(20 * k))).replace("__CB__", str(max(3, round(5 * k))))
           .replace("__SOLID__", str(solid)).replace("__FADE__", str(fade)).replace("__END__", str(end)))
    return css + f'<div class="bg"></div><div class="shade {v["dark"]}"></div>' + layout(variant, w)


def main():
    outs = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for variant in VARIANTS:
            for ratio, (w, h) in SIZE.items():
                pg = b.new_page(viewport={"width": w, "height": h})
                pg.set_content("<!doctype html><html><head><meta charset='utf-8'></head><body>" + page(variant, ratio) + "</body></html>")
                pg.evaluate("document.fonts.ready.then(() => true)")
                pg.wait_for_timeout(900)
                out = HERE / f"封面_{variant}_{ratio}.png"
                pg.screenshot(path=str(out))
                outs.append(out)
                print("->", out.name)
                pg.close()
        b.close()
    for ratio in SIZE:
        shutil.copy2(HERE / f"封面_{SELECTED}_{ratio}.png", HERE / f"封面_选定_{ratio}.png")
    # 预览：每版 16:9 在上、4:3 在下
    sheet = Image.new("RGB", (3 * 640 + 4 * 12, 360 + 480 + 3 * 12), "#C9CDD3")
    for i, variant in enumerate(VARIANTS):
        a = Image.open(HERE / f"封面_{variant}_16x9.png").resize((640, 360), Image.LANCZOS)
        c = Image.open(HERE / f"封面_{variant}_4x3.png").resize((640, 480), Image.LANCZOS)
        sheet.paste(a, (12 + i * 652, 12))
        sheet.paste(c, (12 + i * 652, 12 + 360 + 12))
    sheet.save(HERE / "_封面预览.png")
    print(f"封面_选定_* = {SELECTED}；预览 _封面预览.png")


if __name__ == "__main__":
    main()
