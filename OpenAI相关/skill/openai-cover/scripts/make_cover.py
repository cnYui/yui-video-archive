# -*- coding: utf-8 -*-
"""「OpenAI相关」合集封面（OpenAI 品牌色，版式固定）：按规格 cover.json 出候选，每个候选 16:9（1920×1080）+ 4:3（1440×1080）。

  python make_cover.py --spec <…>\\制作\\04_封面\\cover.json [--only A B] [--out DIR]     出候选 PNG + 每张的 .meta.json + _封面预览.png（联系表）
  python make_cover.py --spec … --select B                                              用户选定后：复制成 封面_选定_16x9.png / 封面_选定_4x3.png
  python check_cover.py <…>\\封面_B_16x9.png                                             验收（同目录有同名 .meta.json）

规格 cover.json（例见 ../assets/cover.example.json）：
  line1 / line2     封面钩子两行：第 1 行白、第 2 行 OpenAI 蓝；短（每行 ≤ 约 7 个字或 11 个英文字符）；和 B 站标题不写同一句
  source            不再画（2026-10-03 封面协定：封面不放小字，来源写在简介里）；写了会打印提醒
  candidates        {名字: {src, t, crop, h16, cx16, h43, note}}：src = 视频或图片（相对 cover.json 所在目录或绝对路径），t = 取帧秒数（图片忽略），
                    crop = [x, y, w, h] 在原帧里裁出主体（去掉浏览器壳、第三方水印、会被 B 站裁掉的边），
                    h16 / cx16 = 16:9 里主体显示高度 / 水平中心（中心 1330–1400、高 940–1130 最常用），h43 = 4:3 里主体显示高度（700–800）
版式（固定，数字见 ../references/design.md）：黑底 #050505、白字、第 2 行 OpenAI 蓝 #0285FF、左边一条 14 px 蓝竖线、不放 OpenAI 标志；
16:9 标题在左、主体在右并从左边淡入黑底（上下边缘也淡出，没有方形硬边）；4:3 标题在上、主体在下；字和主体收在 B 站 16:10 安全区内（左右各留约 96 px）。
"""
import argparse
import base64
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

FONTS = r"D:\大疆\AI科普\素材\字体"
BG, BLUE, GRAY = "#050505", "#0285FF", "#9AA0A6"

CSS = """
<link rel="stylesheet" href="file:///D:/大疆/AI科普/素材/字体/fonts.css">
<style>
* { box-sizing:border-box; margin:0; padding:0; }
html, body { width:__W__px; height:1080px; overflow:hidden; background:__BG__; font-family:'Noto Sans SC', sans-serif; color:#fff; }
#img { position:absolute; width:__IW__px; height:__IH__px; left:__IL__px; top:__IT__px; -webkit-mask-image:__MASK__; mask-image:__MASK__; -webkit-mask-composite:source-in; mask-composite:intersect; }
#shade { position:absolute; inset:0; background:linear-gradient(0deg, rgba(5,5,5,.78) 0%, rgba(5,5,5,0) __SHADE__%); }
#bar { position:absolute; left:0; top:0; width:14px; height:1080px; background:__BLUE__; }
.title { position:absolute; left:__PX__px; top:0; white-space:nowrap; font:900 __FMAX__px/1.16 'Noto Sans SC'; letter-spacing:.01em; text-shadow:0 0 30px rgba(0,0,0,.9), 0 0 10px rgba(0,0,0,.7), 0 8px 34px rgba(0,0,0,.55); }
.title .l2 { color:__BLUE__; text-shadow:0 0 30px rgba(0,0,0,.9), 0 0 10px rgba(0,0,0,.7), 0 0 56px rgba(2,133,255,.28); }
.src { position:absolute; left:__PX__px; bottom:__SB__px; font:600 __SF__px 'Noto Sans SC'; color:__GRAY__; letter-spacing:.06em; }
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
  const r2 = t.getBoundingClientRect();
  window.__fit = { font: f, left: Math.round(r2.left), right: Math.round(r2.right), top: Math.round(r2.top), bottom: Math.round(r2.bottom) };
  window.__ready = true;
})();
</script>
"""


def grab(c, name, base, work):
    """候选的主体图：视频取一帧 / 图片原样，再按 crop 裁出来。"""
    src = Path(c["src"])
    if not src.is_absolute():
        src = base / src
    work.mkdir(exist_ok=True)
    out = work / f"{name}_crop.png"
    vf = []
    if c.get("crop"):
        x, y, w, h = c["crop"]
        vf = ["-vf", f"crop={w}:{h}:{x}:{y}"]
    pre = ["-ss", f"{c.get('t', 0):.2f}"] if src.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm") else []
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + pre + ["-i", str(src), "-frames:v", "1"] + vf + [str(out)], check=True)
    return out


def data_uri(path):
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode()


def page(w, spec, c, img_path):
    iw0, ih0 = Image.open(img_path).size
    if w == 1920:
        ih = c["h16"]
        iw = round(ih * iw0 / ih0)
        il = round(c["cx16"] - iw / 2)
        it = round(540 - ih / 2)
        mask = "linear-gradient(90deg, transparent 0px, rgba(0,0,0,.35) 120px, #000 330px), linear-gradient(180deg, transparent 0px, #000 90px, #000 calc(100% - 90px), transparent 100%)"
        v = dict(PX=104, FMAX=190, SB=64, SF=30, SHADE=26)
        wmax = min(il + 330 - 60 - v["PX"], 1000 - v["PX"])           # 标题右端留在主体淡入完成前、且不过 x 1000
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
    s = s.replace("__BG__", BG).replace("__BLUE__", BLUE).replace("__GRAY__", GRAY)
    for k, val in v.items():
        s = s.replace(f"__{k}__", str(val))
    js = JS.replace("__FMAX__", str(v["FMAX"])).replace("__WMAX__", str(wmax)).replace("__TOPEXPR__", topexpr)
    src_line = ""                      # 2026-10-03 封面协定：不放左下角来源小字（来源写在简介里）
    if spec.get("source"):
        print(f"[提醒] cover.json 里的 source「{spec['source']}」不画了：封面不放小字，来源写进简介")
    body = f"""
<img id="img" src="{data_uri(img_path)}">
<div id="shade"></div>
<div id="bar"></div>
<div class="title" id="title"><div class="l1">{spec['line1']}</div><div class="l2">{spec['line2']}</div></div>
{src_line}"""
    return "<!doctype html><html><head><meta charset='utf-8'></head><body>" + s + body + js + "</body></html>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--out")
    ap.add_argument("--select")
    a = ap.parse_args()
    spec_path = Path(a.spec).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    base = spec_path.parent
    out = Path(a.out).resolve() if a.out else base
    if a.select:
        for name in ("16x9", "4x3"):
            shutil.copy(out / f"封面_{a.select}_{name}.png", out / f"封面_选定_{name}.png")
        print("选定", a.select)
        return
    keys = a.only or list(spec["candidates"])
    work = out / "_src"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for k in keys:
            c = spec["candidates"][k]
            img = grab(c, k, base, work)
            for w, name in ((1920, "16x9"), (1440, "4x3")):
                pg = b.new_page(viewport={"width": w, "height": 1080})
                pg.set_content(page(w, spec, c, img))
                pg.wait_for_function("window.__ready === true", timeout=20000)
                pg.wait_for_timeout(400)
                fit = pg.evaluate("window.__fit")
                png = out / f"封面_{k}_{name}.png"
                pg.screenshot(path=str(png))
                (out / f"封面_{k}_{name}.meta.json").write_text(json.dumps({"w": w, "h": 1080, "title": fit, "line1": spec["line1"], "line2": spec["line2"]}, ensure_ascii=False), encoding="utf-8")
                print(f"-> {png.name}  标题字号 {fit['font']} px，字框 x {fit['left']}–{fit['right']}，y {fit['top']}–{fit['bottom']}")
                pg.close()
        b.close()
    font = ImageFont.truetype(FONTS + r"\NotoSansSC.ttf", 26)
    H = 300
    rows = []
    for k in spec["candidates"]:
        pa, pb = out / f"封面_{k}_16x9.png", out / f"封面_{k}_4x3.png"
        if pa.exists() and pb.exists():
            rows.append((k, Image.open(pa).convert("RGB"), Image.open(pb).convert("RGB")))
    wmax = max(round(x.width * H / x.height) + round(y.width * H / y.height) + 40 for _, x, y in rows)
    sheet = Image.new("RGB", (wmax + 20, len(rows) * (H + 40) + 10), "#2A2A2A")
    d = ImageDraw.Draw(sheet)
    for i, (k, x, y) in enumerate(rows):
        yy = 10 + i * (H + 40)
        d.text((14, yy), f"{k}  {spec['candidates'][k].get('note', '')}", fill="#FFD84D", font=font)
        x2 = x.resize((round(x.width * H / x.height), H), Image.LANCZOS)
        y2 = y.resize((round(y.width * H / y.height), H), Image.LANCZOS)
        sheet.paste(x2, (10, yy + 34))
        sheet.paste(y2, (30 + x2.width, yy + 34))
    sheet.save(out / "_封面预览.png")
    print("预览 ->", out / "_封面预览.png")


if __name__ == "__main__":
    main()
