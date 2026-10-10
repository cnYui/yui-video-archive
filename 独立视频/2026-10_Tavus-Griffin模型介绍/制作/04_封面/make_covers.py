# -*- coding: utf-8 -*-
r"""Tavus 视频封面：官网配色（奶油 #F7F4EF / 墨黑 #140206 / 亮粉 #FF6183 / 荧光绿点 #1BD944）+ 衬线大字 + 硬投影方框，三个候选 × 两个比例。

  python make_covers.py [A B C]          出 封面_<候选>_16x9.png（1920×1080）和 _4x3.png（1440×1080）

B 站首页卡片会把 16:9 裁成 16:10（左右各切约 96 px）：字和主体都收在 x 96–1824 之内；4:3 单独排版（字在上、主体在下）。
人脸帧取自 Griffin 发布视频（素材/X平台视频，@tavus 官方）：原片自带的英文烧录字幕在 y 985 以下，用底部奶油色条盖住；
背景图 / 主体图都是 Tavus 官方素材，整个 04_封面/_src 和成品 png 不进 git。
字体：Noto Sans SC（本地，OFL）+ Instrument Serif / Noto Serif SC（Google Fonts，OFL，渲染时在线加载并等加载完）。
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SRC = HERE / "_src"
SHOT = HERE.parents[1] / "素材" / "官网截图"
FONTS = "file:///D:/大疆/AI科普/素材/字体/fonts.css"
GF = "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Noto+Serif+SC:wght@600;900&display=block"

CSS = f"""
@import url('{FONTS}');
:root {{ --cream:#F7F4EF; --ink:#140206; --pink:#FF6183; --pink3:#FFB4C5; --green:#1BD944; --sand:#E4DDD2; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:var(--cream); font-family:'Noto Sans SC',sans-serif; color:var(--ink); }}
.cv {{ position:relative; overflow:hidden; background:var(--cream); }}
.abs {{ position:absolute; }}
.serif {{ font-family:'Instrument Serif','Noto Serif SC',serif; }}
.cjk {{ font-family:'Noto Serif SC','Instrument Serif',serif; font-weight:900; }}
.mono {{ font-family:'JetBrains Mono','Noto Sans SC',monospace; }}
.chip {{ position:absolute; display:inline-flex; align-items:center; gap:14px; background:var(--ink); color:var(--cream); font:700 34px 'JetBrains Mono','Noto Sans SC'; letter-spacing:.08em; padding:10px 24px; white-space:nowrap; }}
.chip i {{ display:block; width:16px; height:16px; background:var(--green); }}
.card {{ position:absolute; background:var(--cream); border:5px solid var(--ink); box-shadow:16px 16px 0 var(--ink); }}
.sticker {{ position:absolute; background:var(--pink); color:var(--ink); border:5px solid var(--ink); box-shadow:10px 10px 0 var(--ink); font:900 76px 'Noto Sans SC'; padding:6px 30px 10px; white-space:nowrap; }}
.bar {{ position:absolute; left:0; right:0; bottom:0; background:var(--cream); border-top:6px solid var(--ink); }}
.photo {{ position:absolute; overflow:hidden; background:#000; }}
.photo img {{ position:absolute; display:block; }}
.dots {{ background-image:radial-gradient(circle, rgba(20,2,6,.07) 2.2px, transparent 2.8px); background-size:36px 36px; }}
"""

# Vanessa 的脸在 gr_48.7_nopip.png（1920×1080）里的位置：中心 (1074, 535)，脸宽约 308（OpenCV 人脸检测）。
FACE = (1074, 535)


def img_tag(path, s, left, top, extra=""):
    """把 1920×1080 的原图放大 s 倍，左上角对到 (left, top)（原图坐标 → 画布坐标 = (x − left) × s）。"""
    return f'<img src="{Path(path).as_uri()}" style="left:{-left * s:.1f}px;top:{-top * s:.1f}px;width:{1920 * s:.1f}px;{extra}">'


def variant_A(w, h):
    """A：整帧人脸 + 大卡片「48% 以为她是真人」+ 粉色贴纸「她是 AI」+ 底部奶油条（盖住原片的烧录字幕）。"""
    src = SRC / "gr_48.7_nopip.png"
    if w == 1920:
        s, left, top = 1.2, 74, 118                      # 脸中心落在画布 (1200, 500)
        photo = f'<div class="photo" style="left:0;top:0;width:{w}px;height:{h}px">{img_tag(src, s, left, top)}</div>'
        card = ('<div class="card" style="left:110px;top:44px;width:800px;height:580px;padding:22px 40px">'
                '<div class="serif abs" style="left:34px;top:-30px;font-size:420px;line-height:1;color:var(--pink);letter-spacing:-6px;white-space:nowrap">48<span style="font-size:250px">%</span></div>'
                '<div class="cjk abs" style="left:40px;top:360px;font-size:104px;line-height:1.1;white-space:nowrap">以为是真人</div>'
                '<div class="abs" style="left:44px;top:500px;font-size:30px;font-weight:700;color:#5E5850;white-space:nowrap">Tavus 官方实验 · 54 人 · 视频通话 1 分钟</div></div>')
        sticker = '<div class="sticker" style="left:1400px;top:215px;transform:rotate(5deg)">她是 AI</div>'
        bar = ('<div class="bar" style="height:150px"><div class="chip" style="left:110px;top:42px"><i></i>TAVUS · GRIFFIN</div>'
               '<div class="abs mono" style="left:700px;top:50px;font-size:34px;font-weight:700;letter-spacing:.06em;white-space:nowrap">研究预览版 · 官方说法</div></div>')
        return photo + card + sticker + bar
    # 4:3：字在上、脸在下。脸中心落在画布 (720, 690)
    s, left, top = 1.25, 474, 20
    photo = f'<div class="photo" style="left:0;top:0;width:{w}px;height:{h}px">{img_tag(src, s, left, top)}</div>'
    card = ('<div class="card" style="left:70px;top:60px;width:1300px;height:420px">'
            '<div class="serif abs" style="left:40px;top:-26px;font-size:360px;line-height:1;color:var(--pink);letter-spacing:-5px;white-space:nowrap">48<span style="font-size:210px">%</span></div>'
            '<div class="cjk abs" style="left:610px;top:92px;font-size:112px;line-height:1.12;white-space:nowrap">以为<br>是真人</div>'
            '<div class="abs" style="left:44px;top:348px;font-size:30px;font-weight:700;color:#5E5850;white-space:nowrap">Tavus 官方实验 · 54 人 · 视频通话 1 分钟</div></div>')
    sticker = '<div class="sticker" style="left:880px;top:560px;transform:rotate(5deg)">她是 AI</div>'
    bar = ('<div class="bar" style="height:130px"><div class="chip" style="left:70px;top:34px"><i></i>TAVUS · GRIFFIN</div>'
           '<div class="abs mono" style="left:660px;top:42px;font-size:30px;font-weight:700;letter-spacing:.06em;white-space:nowrap">研究预览版 · 官方说法</div></div>')
    return photo + card + sticker + bar


def variant_B(w, h):
    """B：官网 Griffin 首屏的暗红色夕阳底图（鹰头狮）+ 衬线大字 Griffin + 粉色「第一个人类交互模型」+ 右侧人脸卡片。"""
    hero = SHOT / "g_hero_art.png"
    face = SRC / "gr_48.7_nopip.png"
    if w == 1920:
        bg = (f'<div class="abs" style="left:0;top:0;width:{w}px;height:{h}px;background:url({hero.as_uri()}) center 30%/cover;filter:brightness(2.6) contrast(1.15) saturate(1.5)"></div>'
              f'<div class="abs" style="left:0;top:0;width:{w}px;height:{h}px;background:linear-gradient(90deg,rgba(20,2,6,.72) 0%,rgba(20,2,6,.35) 55%,rgba(20,2,6,.05) 100%)"></div>')
        text = ('<div class="abs mono" style="left:110px;top:150px;font-size:34px;font-weight:700;letter-spacing:.32em;color:var(--pink);white-space:nowrap">INTRODUCING</div>'
                '<div class="serif abs" style="left:96px;top:170px;font-size:430px;line-height:1.05;color:var(--cream);letter-spacing:-8px;white-space:nowrap">Griffin</div>'
                '<div class="cjk abs" style="left:110px;top:640px;font-size:98px;line-height:1.15;color:var(--ink);background:var(--pink);border:5px solid var(--ink);box-shadow:12px 12px 0 var(--ink);padding:4px 30px 8px;white-space:nowrap">第一个人类交互模型</div>')
        chips = ('<div class="chip" style="left:110px;top:900px"><i></i>TAVUS</div>'
                 '<div class="chip" style="left:360px;top:900px;background:var(--pink);color:var(--ink)">研究预览版 · 官方说法</div>')
        photo = (f'<div class="card" style="left:1180px;top:200px;width:620px;height:520px;padding:14px;background:#fff">'
                 f'<div class="photo" style="left:14px;top:14px;width:582px;height:492px">{img_tag(face, 0.66, 624, 160)}</div></div>')
        tag = '<div class="sticker" style="left:1450px;top:690px;transform:rotate(-4deg);font-size:64px">她是 AI</div>'
        return bg + text + chips + photo + tag
    bg = (f'<div class="abs" style="left:0;top:0;width:{w}px;height:{h}px;background:url({hero.as_uri()}) 30% 30%/cover;filter:brightness(2.6) contrast(1.15) saturate(1.5)"></div>'
          f'<div class="abs" style="left:0;top:0;width:{w}px;height:{h}px;background:linear-gradient(180deg,rgba(20,2,6,.7) 0%,rgba(20,2,6,.25) 55%,rgba(20,2,6,.05) 100%)"></div>')
    text = ('<div class="abs mono" style="left:70px;top:70px;font-size:30px;font-weight:700;letter-spacing:.32em;color:var(--pink);white-space:nowrap">INTRODUCING</div>'
            '<div class="serif abs" style="left:60px;top:84px;font-size:360px;line-height:1.05;color:var(--cream);letter-spacing:-7px;white-space:nowrap">Griffin</div>'
            '<div class="cjk abs" style="left:70px;top:462px;font-size:96px;line-height:1.15;color:var(--ink);background:var(--pink);border:5px solid var(--ink);box-shadow:12px 12px 0 var(--ink);padding:4px 26px 8px;white-space:nowrap">第一个人类交互模型</div>')
    photo = (f'<div class="card" style="left:70px;top:640px;width:600px;height:340px;padding:12px;background:#fff">'
             f'<div class="photo" style="left:12px;top:12px;width:560px;height:312px">{img_tag(face, 0.62, 560, 250)}</div></div>')
    tag = '<div class="sticker" style="left:400px;top:880px;transform:rotate(-4deg);font-size:58px">她是 AI</div>'
    chips = ('<div class="chip" style="left:760px;top:700px"><i></i>TAVUS</div>'
             '<div class="chip" style="left:760px;top:790px;background:var(--pink);color:var(--ink)">研究预览版 · 官方说法</div>')
    return bg + text + photo + tag + chips


def variant_C(w, h):
    """C：奶油色海报——「对面是 AI 还是真人？」三行衬线大字 + 右侧斜放的人脸卡片（官网那种白底方框 + 硬投影）。"""
    face = SRC / "gr_48.7_nopip.png"
    if w == 1920:
        bg = f'<div class="abs dots" style="left:0;top:0;width:{w}px;height:{h}px"></div>'
        text = ('<div class="cjk abs" style="left:104px;top:130px;font-size:150px;line-height:1.1;white-space:nowrap">对面是</div>'
                '<div class="cjk abs" style="left:100px;top:300px;font-size:230px;line-height:1.05;white-space:nowrap;letter-spacing:-4px">AI 还是</div>'
                '<div class="cjk abs" style="left:100px;top:560px;font-size:330px;line-height:1.05;white-space:nowrap;color:var(--pink);letter-spacing:-6px">真人？</div>')
        chips = ('<div class="chip" style="left:110px;top:62px"><i></i>TAVUS · GRIFFIN</div>'
                 '<div class="chip" style="left:110px;top:956px;background:var(--pink);color:var(--ink)">Tavus 新模型 · 官方说法</div>')
        photo = (f'<div class="card" style="left:975px;top:110px;width:800px;height:760px;padding:16px;background:#fff;transform:rotate(2.2deg)">'
                 f'<div class="photo" style="left:16px;top:16px;width:758px;height:716px">{img_tag(face, 0.9, 610, 60)}</div></div>')
        tag = '<div class="sticker" style="left:1250px;top:830px;transform:rotate(-3deg);font-size:68px">其实是 AI</div>'
        return bg + text + chips + photo + tag
    bg = f'<div class="abs dots" style="left:0;top:0;width:{w}px;height:{h}px"></div>'
    text = ('<div class="chip" style="left:70px;top:48px"><i></i>TAVUS · GRIFFIN</div>'
            '<div class="cjk abs" style="left:70px;top:130px;font-size:150px;line-height:1.1;white-space:nowrap">对面是 AI</div>'
            '<div class="cjk abs" style="left:70px;top:290px;font-size:220px;line-height:1.05;white-space:nowrap;color:var(--pink);letter-spacing:-4px">还是真人？</div>')
    photo = (f'<div class="card" style="left:120px;top:560px;width:1000px;height:440px;padding:14px;background:#fff;transform:rotate(-1.6deg)">'
             f'<div class="photo" style="left:14px;top:14px;width:968px;height:408px">{img_tag(face, 0.78, 600, 215)}</div></div>')
    tag = '<div class="sticker" style="left:880px;top:900px;transform:rotate(4deg);font-size:60px">其实是 AI</div>'
    chips = '<div class="chip" style="left:640px;top:990px;background:var(--pink);color:var(--ink);font-size:28px">Tavus 新模型 · 官方说法</div>'
    return bg + text + photo + tag + chips


VARIANTS = {"A": variant_A, "B": variant_B, "C": variant_C}
SIZES = {"16x9": (1920, 1080), "4x3": (1440, 1080)}


def main():
    want = [a for a in sys.argv[1:] if a in VARIANTS] or list(VARIANTS)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for v in want:
            for tag, (w, h) in SIZES.items():
                pg = b.new_page(viewport={"width": w, "height": h})
                body = VARIANTS[v](w, h)
                html = f'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="{GF}"><style>{CSS}</style><body><div class="cv" style="width:{w}px;height:{h}px">{body}</div></body>'
                f = HERE / f"_cover_{v}_{tag}.html"
                f.write_text(html, encoding="utf-8")
                pg.goto(f.as_uri())
                pg.wait_for_timeout(800)
                pg.evaluate("""async () => {
                    await Promise.all([document.fonts.load('900 100px "Noto Serif SC"', '对面是还真人以为她第一个类交互模型，？48%'), document.fonts.load('400 100px "Instrument Serif"', 'Griffin48%'),
                                       document.fonts.load('800 60px "Noto Sans SC"', '她是其实AI官方说法研究预览版TAVUS')]);
                    await document.fonts.ready; }""")
                ok = pg.evaluate("[...document.fonts].filter(f => f.status==='loaded').map(f => f.family.replace(/[\"']/g,''))")
                assert "Noto Serif SC" in ok and "Instrument Serif" in ok, f"字体没加载到：{set(ok)}"
                pg.wait_for_timeout(300)
                out = HERE / f"封面_{v}_{tag}.png"
                pg.screenshot(path=str(out))
                print("->", out.name)
                pg.close()
        b.close()


if __name__ == "__main__":
    main()
