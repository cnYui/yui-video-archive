# -*- coding: utf-8 -*-
"""《OpenAI DevDay 2026 解读》6 条短片的封面。

用户 2026-10-02：“做一个封面，用openai的品牌色” → 看过第一版（绿色）后：“就用v1，但是请使用openai的蓝色”。
所以版式照第一版（黑底、左边两行大标题第二行强调色、左上角药丸标签、两个标签、右边是发布会画面），强调色从绿换成 OpenAI 蓝。

  python make_covers.py [V1 V2 …]     → V?_封面_16x9_1920x1080.png / V?_封面_4x3_1440x1080.png（B 站两个比例都要换）、_sheet.png（预览联系表）、_thumbs.png（320 px 缩略图，看小尺寸还认不认得出）

**OpenAI 蓝 = #0285FF**：OpenAI 官网样式里有这个值（ChatGPT 的强调蓝），发布会幻灯片上的蓝（“AI research interns”“Now with GPT-6 Astra computer use”“everywhere”）
抽样是 #0684EA / #0078D8 / #0090EA，就是它被舞台屏幕和视频压缩压暗后的样子。底色黑 #050505，字白色，次要信息灰 #9AA0A6。
没有用 OpenAI 的标志（官方规范：Blossom 不能加色、不能放在复杂画面上、不能把标志当主品牌）；“OPENAI DEVDAY 2026”只是文字标签，下面一行写明“OpenAI 官方发布会 · 中文解读”。

第一版（绿色）的问题和这版的改法：标题压在画面自带的大字上（V1 的 dots、V2 的 ChatGPT Space、V6 的 1.2B…），V4 的白色界面被压暗发灰。
现在每张封面给一个“主体框”（box，占整帧的比例）：16:9 把主体放到右边（主体左边缘 SL 以右），画面从左边淡入黑底；标题字号按“主体左边缘 − 左边距”自动缩到放得下；
4:3 标题在上、主体在下。V6 的标题缩短了（“12 亿人每周在用 / 你的产品怎么上”，画面上自带 “1.2B people use ChatGPT every week”）。
"""
import base64
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
VIDEO = EP / "素材" / "keynote_video_silent.mp4"
FR = HERE / "_frames"
BLUE = "#0285FF"

# B 站首页卡片会把 16:9 裁成 16:10（左右各约 96 px）：标题左边距 104 px，主体里的关键字右端收在 x ≤ 1824（用户的规矩，见记忆 cover-text-not-repeat-title），所以 SL 都在 945–1100。
# t = 原片秒数（抽整帧）；box = 画面里的主体框（x0, y0, x1, y1，占整帧的比例）；z = 16:9 的放大倍数（≥ 1）；SL = 16:9 主体左边缘放到的 x
COVERS = {
    # V1：用户 2026-10-02 “封面的文字只保留：全天在线的AI助理”（标题改成了“OpenAI发布Dots，电影里的AI助理，OpenAI做出来了”，原来封面上的钩子挪进了标题）
    # → minimal：没有“OPENAI DEVDAY 2026 / 解读 01”标签、没有两个小标签、没有底部小字，只剩这一句，分两行（白 + 蓝），字号放大（F16 / F43）。
    # 旧版（带全部文字）在 _旧稿/V1_封面_*_带全部文字版.png。画面自带的 “dots” 是发布会屏幕上的字，不算封面文字。
    "V1": dict(t=159.0, no="01", l1="全天在线的", l2="AI 助理", chips=[], minimal=True, F16=190, F43=150,
               box=(0.30, 0.25, 0.70, 0.80), z=1.0, SL=1090),
    "V2": dict(t=502.6, no="02", l1="工程师的 Dots", l2="每天修几十个 bug", chips=[("ChatGPT Space", True), ("Dots 协作", False)],
               box=(0.34, 0.14, 0.79, 0.74), z=1.0, SL=1052),
    "V3": dict(t=1275.0, no="03", l1="火箭已经起飞", l2="对手还没画完", chips=[("Ultra Fast", True), ("GPT-6.1 Sol", False)],
               box=(0.31, 0.27, 0.61, 0.67), z=1.25, SL=1100, FL=140, CX43=900),     # FL：淡入只有 140 px，画面左边的提示词和“↑”按钮留在黑里
    # V4：用户 2026-10-02 “封面的文字只保留：让模型只做选择，快到几乎即时”（标题改成“OpenAI预览Decisions API，对标Jev模型”；Jev 模型是用户自己《原LAI如此》第 3 期讲过的）
    # → 和 V1 一样的 minimal 版式（只有这一句，分两行，白 + 蓝，行尾的逗号照本组封面的习惯不写）。旧版在 _旧稿/V4_封面_*_带全部文字版.png。
    "V4": dict(t=1341.6, no="04", l1="让模型只做选择", l2="快到几乎即时", chips=[], minimal=True, F16=190, F43=150,
               box=(0.08, 0.18, 0.60, 0.75), z=1.0, SL=1080),
    # V5：用户 2026-10-02 “封面中的文字只保留：合上笔记本 / 任务照样跑”（标题改成“OpenAI把Codex搬上云端，手机开任务电脑接着干，Agents API开放公测”）
    # → minimal 版式（去掉标签和两个小标签，只剩这两行，白 + 蓝）。旧版在 _旧稿/V5_封面_*_带全部文字版.png。
    "V5": dict(t=1695.3, no="05", l1="合上笔记本", l2="任务照样跑", chips=[], minimal=True, F16=190, F43=150,
               box=(0.36, 0.18, 0.84, 0.60), z=1.15, SL=1090),
    "V6": dict(t=2652.8, no="06", l1="12 亿人每周在用", l2="你的产品怎么上", chips=[("开发者怎么赚钱", True), ("Marketplace", False)],
               box=(0.28, 0.12, 0.74, 0.79), z=1.0, SL=945),
}


def grab(key, t):
    FR.mkdir(exist_ok=True)
    p = FR / f"{key}_cover.jpg"
    if not p.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(VIDEO), "-frames:v", "1", "-q:v", "2", str(p)], check=True)
    return p


def data_uri(path):
    return "data:image/jpeg;base64," + base64.b64encode(Path(path).read_bytes()).decode()


def place(c, wide):
    """主体框 → 图片的位置和大小（像素）+ 淡入遮罩的位置。返回 dict。"""
    x0, y0, x1, y1 = c["box"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    sw, sh = x1 - x0, y1 - y0
    if wide:
        z = c["z"]
        iw, ih = round(1920 * z), round(1080 * z)
        il = round(c["SL"] - x0 * iw)                     # 主体左边缘落在 SL
        it = round(560 - cy * ih)                         # 主体中心略低于画面中线
        it = max(1080 - ih, min(0, it))
        il = max(1920 - iw, il)                           # 右边要盖满；左边可以留黑（会被淡入遮住）
        fe = c["SL"] - 20                                 # 遮罩：淡入在主体左边缘前 20 px 结束；前 72% 几乎不透明度（标题压在上面不吵），最后一段才拉起来
        fs = max(fe - c.get("FL", 420), il + 24)
        fe = max(fe, fs + 120)
        mid = fs - il + round(0.72 * (fe - fs))
        return dict(iw=iw, ih=ih, il=il, it=it, mask=f"linear-gradient(90deg, transparent {fs - il}px, rgba(0,0,0,.08) {mid}px, #000 {fe - il}px)")
    z = max(0.75, min(1300 / (sw * 1920), 460 / (sh * 1080), 1.6))
    iw, ih = round(1920 * z), round(1080 * z)
    il = round(c.get("CX43", 720) - cx * iw)
    il = max(1440 - iw, min(0, il))
    it = round(800 - cy * ih)
    it = max(1080 - ih, min(470, it))
    fs = max(500, it + 24)
    return dict(iw=iw, ih=ih, il=il, it=it, mask=f"linear-gradient(180deg, transparent {fs - it}px, #000 {fs - it + 90}px)")


CSS = """
<link rel="stylesheet" href="file:///D:/大疆/AI科普/素材/字体/fonts.css">
<style>
* { box-sizing:border-box; margin:0; padding:0; }
html, body { width:__W__px; height:1080px; overflow:hidden; background:#050505; font-family:'Noto Sans SC', sans-serif; color:#fff; }
#img { position:absolute; width:__IW__px; height:__IH__px; left:__IL__px; top:__IT__px; filter:brightness(.95) saturate(1.05); -webkit-mask-image:__MASK__; mask-image:__MASK__; }
#shade { position:absolute; inset:0; background:linear-gradient(0deg, rgba(5,5,5,.8) 0%, rgba(5,5,5,0) __SHADE__%); }
#bar { position:absolute; left:0; top:0; width:14px; height:1080px; background:#0285FF; }
.tag { position:absolute; display:flex; align-items:center; gap:18px; left:__PX__px; top:__TAGY__px; }
.pill { font:700 __TAGF__px 'Space Grotesk','Noto Sans SC'; letter-spacing:.14em; padding:__TPY__px __TPX__px; border-radius:999px; white-space:nowrap; }
.pill.g { background:#0285FF; color:#fff; }
.pill.o { border:4px solid #fff; color:#fff; font-weight:800; letter-spacing:.06em; font-family:'Noto Sans SC'; padding:__TPY2__px __TPX__px; background:rgba(5,5,5,.55); }
.title { position:absolute; left:__PX__px; top:0; white-space:nowrap; font:900 __FMAX__px/1.16 'Noto Sans SC'; letter-spacing:.01em; text-shadow:0 0 30px rgba(0,0,0,.9), 0 0 10px rgba(0,0,0,.7), 0 8px 34px rgba(0,0,0,.55); }
.title .l2 { color:#0285FF; text-shadow:0 0 30px rgba(0,0,0,.9), 0 0 10px rgba(0,0,0,.7), 0 0 56px rgba(2,133,255,.28); }
.chips { position:absolute; left:__PX__px; top:0; display:flex; gap:22px; }
.chip { font:800 __CF__px 'Noto Sans SC'; padding:__CPY__px __CPX__px; border-radius:18px; border:4px solid #fff; white-space:nowrap; background:rgba(5,5,5,.55); }
.chip.g { background:#0285FF; border-color:#0285FF; color:#fff; }
.src { position:absolute; left:__PX__px; bottom:__SB__px; font:600 __SF__px 'Noto Sans SC'; color:#9AA0A6; letter-spacing:.06em; }
</style>
"""

JS = """
<script>
(async () => {
  await document.fonts.ready;
  const t = document.getElementById('title'), chips = document.getElementById('chips');
  const FMAX = __FMAX__, WMAX = __WMAX__;
  t.style.fontSize = FMAX + 'px';
  const w0 = t.getBoundingClientRect().width;
  const f = Math.min(FMAX, Math.floor(FMAX * WMAX / w0));
  t.style.fontSize = f + 'px';
  const r = t.getBoundingClientRect();
  const cr = chips ? chips.getBoundingClientRect() : { height: 0 };
  const top = __TOPEXPR__;
  t.style.top = top + 'px';
  if (chips) chips.style.top = (top + r.height + __GAP__) + 'px';
  window.__fit = { font: f, width: Math.round(r.width), top: Math.round(top), h: Math.round(r.height) };
  window.__ready = true;
})();
</script>
"""


def page(w, c, img):
    wide = (w == 1920)
    pl = place(c, wide)
    if wide:
        v = dict(PX=104, TAGY=92, TAGF=32, TPY=10, TPX=26, TPY2=6, FMAX=150, CF=44, CPY=12, CPX=30, SB=64, SF=30, SHADE=26)
        wmax = c["SL"] - 90 - v["PX"]                     # 标题右端留在主体左边缘前 90 px 以内
        topexpr = "Math.round(520 - (r.height + 70 + cr.height) / 2)"
        gap = 70
    else:
        v = dict(PX=84, TAGY=64, TAGF=28, TPY=9, TPX=22, TPY2=5, FMAX=124, CF=38, CPY=10, CPX=26, SB=44, SF=26, SHADE=22)
        wmax = 1440 - 2 * v["PX"]
        topexpr = "150"
        gap = 26
    mini = bool(c.get("minimal"))
    if mini:                                              # 只有标题：放大字号，竖直居中
        v["FMAX"] = c["F16"] if wide else c["F43"]
        topexpr = "Math.round(520 - r.height / 2)" if wide else "190"
        gap = 0
    s = CSS.replace("__W__", str(w)).replace("__IW__", str(pl["iw"])).replace("__IH__", str(pl["ih"])).replace("__IL__", str(pl["il"])).replace("__IT__", str(pl["it"])).replace("__MASK__", pl["mask"])
    for k, val in v.items():
        s = s.replace(f"__{k}__", str(val))
    js = JS.replace("__FMAX__", str(v["FMAX"])).replace("__WMAX__", str(wmax)).replace("__TOPEXPR__", topexpr).replace("__GAP__", str(gap))
    chips = "".join(f'<div class="chip{" g" if g else ""}">{t}</div>' for t, g in c["chips"])
    if mini:
        body = f"""
<img id="img" src="{img}">
<div id="shade"></div>
<div id="bar"></div>
<div class="title" id="title"><div class="l1">{c['l1']}</div><div class="l2">{c['l2']}</div></div>"""
    else:
        body = f"""
<img id="img" src="{img}">
<div id="shade"></div>
<div id="bar"></div>
<div class="tag"><div class="pill g">OPENAI DEVDAY 2026</div><div class="pill o">解读 {c['no']}</div></div>
<div class="title" id="title"><div class="l1">{c['l1']}</div><div class="l2">{c['l2']}</div></div>
<div class="chips" id="chips">{chips}</div>
<div class="src">OpenAI 官方发布会 · 中文解读</div>"""
    return "<!doctype html><html><head><meta charset='utf-8'></head><body>" + s + body + js + "</body></html>"


def main():
    keys = sys.argv[1:] or list(COVERS)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for k in keys:
            c = COVERS[k]
            img = data_uri(grab(k, c["t"]))
            for w, name in ((1920, "16x9_1920x1080"), (1440, "4x3_1440x1080")):
                pg = b.new_page(viewport={"width": w, "height": 1080})
                pg.set_content(page(w, c, img))
                pg.wait_for_function("window.__ready === true", timeout=20000)
                pg.wait_for_timeout(400)
                fit = pg.evaluate("window.__fit")
                out = HERE / f"{k}_封面_{name}.png"
                pg.screenshot(path=str(out))
                print(f"-> {out.name}  标题字号 {fit['font']} px，宽 {fit['width']} px，高 {fit['h']} px，顶 {fit['top']}")
                pg.close()
        b.close()
    # 预览联系表：每条一行（16:9 + 4:3）；缩略图：6 张 16:9 缩到 320 宽
    font = ImageFont.truetype(r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf", 26)
    H = 300
    rows = []
    for k in COVERS:
        a = Image.open(HERE / f"{k}_封面_16x9_1920x1080.png").convert("RGB")
        b4 = Image.open(HERE / f"{k}_封面_4x3_1440x1080.png").convert("RGB")
        rows.append((k, a, b4))
    wmax = max(round(a.width * H / a.height) + round(b4.width * H / b4.height) + 40 for _, a, b4 in rows)
    sheet = Image.new("RGB", (wmax + 20, len(rows) * (H + 40) + 10), "#2A2A2A")
    d = ImageDraw.Draw(sheet)
    for i, (k, a, b4) in enumerate(rows):
        y = 10 + i * (H + 40)
        d.text((14, y), k, fill="#FFD84D", font=font)
        a2 = a.resize((round(a.width * H / a.height), H), Image.LANCZOS)
        b2 = b4.resize((round(b4.width * H / b4.height), H), Image.LANCZOS)
        sheet.paste(a2, (10, y + 34))
        sheet.paste(b2, (30 + a2.width, y + 34))
    sheet.save(HERE / "_sheet.png")
    tw, th = 320, 180
    cols = 3
    trows = (len(rows) + cols - 1) // cols
    thumbs = Image.new("RGB", (cols * (tw + 10) + 10, trows * (th + 10) + 10), "#2A2A2A")
    for i, (k, a, _) in enumerate(rows):
        thumbs.paste(a.resize((tw, th), Image.LANCZOS), (10 + (i % cols) * (tw + 10), 10 + (i // cols) * (th + 10)))
    thumbs.save(HERE / "_thumbs.png")
    print("sheet / thumbs ->", HERE)


if __name__ == "__main__":
    main()
