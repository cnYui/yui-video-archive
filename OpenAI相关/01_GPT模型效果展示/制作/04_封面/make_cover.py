# -*- coding: utf-8 -*-
"""《GPT-6.1 Sol / GPT-6 Astra 模型效果展示》封面：三个候选（A 地球 / B Sol 的游戏 / C 毛绒 dots），每个出 16:9（1920×1080）和 4:3（1440×1080，B 站两个比例都要换）。

  python make_cover.py [A B C]          → 封面_<候选>_16x9.png / 封面_<候选>_4x3.png、_封面预览.png（联系表）
  python make_cover.py --select A       → 封面_选定_16x9.png / 封面_选定_4x3.png = 这个候选（用户选定后跑）

规矩（记忆 openai-blue-cover、cover-text-not-repeat-title，版式照 DevDay 解读那套 `独立视频/2026-10_OpenAI-DevDay-2026解读/制作/04_封面/make_covers.py` 的 minimal 版）：
- 黑底 #050505、白字、第二行 **OpenAI 蓝 #0285FF**（ChatGPT 强调蓝）、左边一条蓝竖线；不放 OpenAI 标志；
- 封面只写短钩子两行（白 + 蓝），标题在 B 站填完整一句、不抄同一句；
- 主体放右边、从左边淡入黑底（4:3 标题在上、主体在下）；16:9 的字和主体收在 16:10 安全区内（B 站首页卡片会裁，左右各约 96 px：字左边距 104，主体右端 ≤ x 1824）；
- 主体都是网友作品视频里的原帧（只裁掉浏览器壳 / 第三方水印，不画任何角色），底部一行小字写来源。
"""
import base64
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
XV = EP / "素材" / "X平台视频"
SRC = HERE / "_src"

L1, L2 = "GPT-6.1 Sol", "网友实测"
# crop = (x, y, w, h)：从原帧里裁出主体（去掉浏览器壳 / 水印）；h16 = 16:9 里主体显示高度；cx16 = 主体中心 x；h43 = 4:3 里主体显示高度
COVERS = {
    "A": dict(src=XV / "SamGCoder_2105822535212581210.mp4", t=9.5, crop=(768, 256, 1101, 1101), h16=1010, cx16=1400, h43=760, what="Clearwater 的地球"),
    "B": dict(src=XV / "higgsfield_ai_2105012668348383325.mp4", t=46.5, crop=(330, 100, 1120, 970), h16=1130, cx16=1330, h43=800, what="Sol 做的 3D 游戏"),
    "C": dict(src=XV / "abstrakt314_2105756028935504032.mp4", t=0.3, crop=(154, 139, 790, 800), h16=940, cx16=1350, h43=800, what="高斯泼溅的 dots"),
}

CSS = """
<link rel="stylesheet" href="file:///D:/大疆/AI科普/素材/字体/fonts.css">
<style>
* { box-sizing:border-box; margin:0; padding:0; }
html, body { width:__W__px; height:1080px; overflow:hidden; background:#050505; font-family:'Noto Sans SC', sans-serif; color:#fff; }
#img { position:absolute; width:__IW__px; height:__IH__px; left:__IL__px; top:__IT__px; -webkit-mask-image:__MASK__; mask-image:__MASK__; -webkit-mask-composite:source-in; mask-composite:intersect; }
#shade { position:absolute; inset:0; background:linear-gradient(0deg, rgba(5,5,5,.78) 0%, rgba(5,5,5,0) __SHADE__%); }
#bar { position:absolute; left:0; top:0; width:14px; height:1080px; background:#0285FF; }
.title { position:absolute; left:__PX__px; top:0; white-space:nowrap; font:900 __FMAX__px/1.16 'Noto Sans SC'; letter-spacing:.01em; text-shadow:0 0 30px rgba(0,0,0,.9), 0 0 10px rgba(0,0,0,.7), 0 8px 34px rgba(0,0,0,.55); }
.title .l2 { color:#0285FF; text-shadow:0 0 30px rgba(0,0,0,.9), 0 0 10px rgba(0,0,0,.7), 0 0 56px rgba(2,133,255,.28); }
.src { position:absolute; left:__PX__px; bottom:__SB__px; font:600 __SF__px 'Noto Sans SC'; color:#9AA0A6; letter-spacing:.06em; }
</style>
"""
JS = """
<script>
(async () => {
  await document.fonts.ready;
  const t = document.getElementById('title');
  t.style.fontSize = __FMAX__ + 'px';
  const w0 = t.getBoundingClientRect().width;
  const f = Math.min(__FMAX__, Math.floor(__FMAX__ * __WMAX__ / w0));
  t.style.fontSize = f + 'px';
  const r = t.getBoundingClientRect();
  t.style.top = __TOPEXPR__ + 'px';
  window.__fit = { font: f, width: Math.round(r.width), h: Math.round(r.height), right: Math.round(r.right) };
  window.__ready = true;
})();
</script>
"""


def grab(key, c):
    SRC.mkdir(exist_ok=True)
    p = SRC / f"{key}_crop.png"
    x, y, w, h = c["crop"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{c['t']:.2f}", "-i", str(c["src"]), "-frames:v", "1", "-vf", f"crop={w}:{h}:{x}:{y}", str(p)], check=True)
    return p


def data_uri(path):
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode()


def page(w, c, img_path):
    iw0, ih0 = Image.open(img_path).size
    wide = (w == 1920)
    if wide:
        ih = c["h16"]
        iw = round(ih * iw0 / ih0)
        il = round(c["cx16"] - iw / 2)
        it = round(540 - ih / 2)
        mask = "linear-gradient(90deg, transparent 0px, rgba(0,0,0,.35) 120px, #000 330px), linear-gradient(180deg, transparent 0px, #000 90px, #000 calc(100% - 90px), transparent 100%)"
        v = dict(PX=104, FMAX=140, SB=64, SF=30, SHADE=26)
        wmax = il + 330 - 60 - v["PX"]                    # 标题右端留在主体淡入完成前
        wmax = min(wmax, 1000 - v["PX"])
        topexpr = "Math.round(520 - r.height / 2)"
    else:
        ih = c["h43"]
        iw = round(ih * iw0 / ih0)
        il = round(720 - iw / 2)
        it = 1080 - ih + 40
        mask = "linear-gradient(180deg, transparent 0px, rgba(0,0,0,.35) 90px, #000 230px), linear-gradient(90deg, transparent 0px, #000 16%, #000 84%, transparent 100%)"
        v = dict(PX=84, FMAX=190, SB=44, SF=26, SHADE=18)
        wmax = 1440 - 2 * v["PX"]
        topexpr = "96"
    s = CSS.replace("__W__", str(w)).replace("__IW__", str(iw)).replace("__IH__", str(ih)).replace("__IL__", str(il)).replace("__IT__", str(it)).replace("__MASK__", mask)
    for k, val in v.items():
        s = s.replace(f"__{k}__", str(val))
    js = JS.replace("__FMAX__", str(v["FMAX"])).replace("__WMAX__", str(wmax)).replace("__TOPEXPR__", topexpr)
    body = f"""
<img id="img" src="{data_uri(img_path)}">
<div id="shade"></div>
<div id="bar"></div>
<div class="title" id="title"><div class="l1">{L1}</div><div class="l2">{L2}</div></div>
<div class="src">画面：X 平台网友作品</div>"""
    return "<!doctype html><html><head><meta charset='utf-8'></head><body>" + s + body + js + "</body></html>"


def main():
    if "--select" in sys.argv:
        k = sys.argv[sys.argv.index("--select") + 1]
        for name in ("16x9", "4x3"):
            shutil.copy(HERE / f"封面_{k}_{name}.png", HERE / f"封面_选定_{name}.png")
        print("选定", k)
        return
    keys = [a for a in sys.argv[1:] if a in COVERS] or list(COVERS)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for k in keys:
            c = COVERS[k]
            img = grab(k, c)
            for w, name in ((1920, "16x9"), (1440, "4x3")):
                pg = b.new_page(viewport={"width": w, "height": 1080})
                pg.set_content(page(w, c, img))
                pg.wait_for_function("window.__ready === true", timeout=20000)
                pg.wait_for_timeout(400)
                fit = pg.evaluate("window.__fit")
                out = HERE / f"封面_{k}_{name}.png"
                pg.screenshot(path=str(out))
                print(f"-> {out.name}  标题字号 {fit['font']} px，宽 {fit['width']} px，右端 x {fit['right']}")
                pg.close()
        b.close()
    font = ImageFont.truetype(r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf", 26)
    H = 300
    rows = []
    for k in COVERS:
        pa, pb = HERE / f"封面_{k}_16x9.png", HERE / f"封面_{k}_4x3.png"
        if pa.exists() and pb.exists():
            rows.append((k, Image.open(pa).convert("RGB"), Image.open(pb).convert("RGB")))
    wmax = max(round(a.width * H / a.height) + round(b4.width * H / b4.height) + 40 for _, a, b4 in rows)
    sheet = Image.new("RGB", (wmax + 20, len(rows) * (H + 40) + 10), "#2A2A2A")
    d = ImageDraw.Draw(sheet)
    for i, (k, a, b4) in enumerate(rows):
        y = 10 + i * (H + 40)
        d.text((14, y), f"{k}  {COVERS[k]['what']}", fill="#FFD84D", font=font)
        a2 = a.resize((round(a.width * H / a.height), H), Image.LANCZOS)
        b2 = b4.resize((round(b4.width * H / b4.height), H), Image.LANCZOS)
        sheet.paste(a2, (10, y + 34))
        sheet.paste(b2, (30 + a2.width, y + 34))
    sheet.save(HERE / "_封面预览.png")
    print("预览 ->", HERE / "_封面预览.png")


if __name__ == "__main__":
    main()
