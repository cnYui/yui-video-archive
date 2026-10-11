# -*- coding: utf-8 -*-
"""日报（10/5 这期）改竖屏短视频的三种排版样图：用这期的真素材（来源截图、真字幕、真要点、鲸鱼娘像素图、从成片抠的手写字）摆在 1080×2340 上。

    python make_daily_layouts.py render      # 抠手写字 + 出 3 种排版 × 4 个场景 × 背景 的 PNG → _render/
    python make_daily_layouts.py sheets      # 拼总览图 / 各排版详情图 / 背景对照图

排版（用户 2026-10-05：“给我三种视频的排版，我来定一下”；格式按短视频技能：1080×2340、版式 B 的安全区、边框 6、背景印花三选一、双语字幕 52/30 px）：
  L1 素材主导 · 标准竖版：技能版式 B 单框——标题 / 来源截图进边框 6 / 字幕 / 下面一张要点卡或数字卡，鲸鱼娘站在卡片旁
  L2 白板主导 · 竖版白板：保留日报的手写白板（手写标题 + 手写要点 + 贴胶带的来源截图），整块白板套边框 6，鲸鱼娘站在白板角上
  L3 角色主导 · 鲸鱼娘说话：鲸鱼娘放大，要点以对话气泡一条条冒出来，来源截图缩成上面一个框
场景：open 开场“今天说这几件事” / kol 新闻条（有大数字）/ cos 新闻条（纯文字要点）/ rev 今日回顾
"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
CROPS = HERE / "_crops"
RENDER = HERE / "_render"
SNAPS = Path(r"D:\大疆\AI日报\2026-10-05\制作\assets\snaps")
BGDIR = Path(r"D:\大疆\短视频\skill\short-video\assets\backgrounds")
SPR = Path(r"D:\大疆\AI科普\素材\角色\大肥鱼像素素材包\素材\sprites\expressions")
FONTS = Path(r"D:\大疆\AI科普\素材\字体\fonts.css")
BGS = {"color": "pattern_color.png", "ink": "pattern_ink.png", "orange": "pattern_orange.png"}

# ---------------------------------------------------------------- 从成片抠手写字（帧在 _crops/frame_*.png，2340×1080）
CROP_BOXES = {
    "kol_title": ("frame_94", (650, 40, 1720, 252)), "kol_bul": ("frame_94", (470, 262, 1090, 690)),
    "cos_title": ("frame_243", (640, 44, 1710, 246)), "cos_bul": ("frame_243", (470, 262, 1090, 690)),
    "open_title": ("frame_27.9", (880, 108, 1470, 232)), "open_l": ("frame_27.9", (255, 268, 1050, 690)), "open_r": ("frame_27.9", (1170, 268, 1990, 690)),
    "rev_title": ("frame_340", (960, 78, 1390, 215)), "rev_l": ("frame_340", (300, 275, 1020, 690)), "rev_r": ("frame_340", (1180, 275, 1900, 690)),
}


def make_crops():
    for name, (fr, box) in CROP_BOXES.items():
        Image.open(CROPS / f"{fr}.png").convert("RGB").crop(box).save(CROPS / f"{name}.png")


# ---------------------------------------------------------------- 场景数据（全部来自 10/5 的台本）
POINTS = {
    "kol": ["总参数 78B", "每次只激活 3.46B", "Apache 2.0 开源", "德语占五分之一以上"],
    "cos": ["PR 要勾选没用 AI", "代码注释描述都算", "理由是审核太累", "不反对 AI 工具本身"],
}
SCENES = {
    "open": dict(kicker="AI每日日报 · <b>10.05</b>", t1="今天说 8 件事", t2="GPT-6 打星际输了？", tag="今日 8 条",
                 zh="还有谷歌治 AI 刷题的新方法。", en="and Google's new fix for AI that memorizes its tests.", prog=0, expr="expr_01_happy.png", name="开场 · 今天说这几件事"),
    "kol": dict(kicker="AI每日日报 · <b>10.05</b> · 第 <b>2</b> / 8 条", t1="德国开源模型 Kolibri", t2="78B 参数，每词只动 3.46B", tag="来源 · Aleph Alpha",
                zh="每层 384 个专家，", en="384 experts per layer,", prog=2, expr="expr_06_talk_m1.png", snap="news_02.png", snap_wh=(1310, 840),
                hl=(24, 572, 905, 104), cur=1, name="新闻条 · 有大数字（Kolibri）"),
    "cos": dict(kicker="AI每日日报 · <b>10.05</b> · 第 <b>6</b> / 8 条", t1="COSMIC 拒收 AI 代码", t2="提交代码先发誓：没用 AI", tag="来源 · Linuxiac",
                zh="代码、注释、PR 描述都算在内。", en="That covers code, comments and PR descriptions.", prog=7, expr="expr_06_talk_m1.png", snap="news_06.png", snap_wh=(1247, 840),
                hl=(30, 288, 1062, 112), cur=1, name="新闻条 · 纯文字要点（COSMIC）"),
    "rev": dict(kicker="AI每日日报 · <b>10.05</b>", t1="今日回顾", t2="8 件事，来源都在简介里", tag="今日回顾",
                zh="好好休息，我们明天见。", en="Get some rest, and see you tomorrow.", prog=9, expr="expr_01_happy.png", name="今日回顾"),
}
ORDER = ["open", "kol", "cos", "rev"]
BAR_N = 10     # 开场 + 8 条 + 回顾


def uri(p):
    return Path(p).as_uri()


BASE_CSS = """
* { box-sizing:border-box; margin:0; padding:0; }
html, body { width:1080px; height:2340px; overflow:hidden; font-family:'Noto Sans SC', sans-serif; color:#141413; background:#FAF9F5 url('%(bg)s') 0 0 / 1080px 2340px no-repeat; }
.abs { position:absolute; }
#head { position:absolute; left:40px; right:40px; top:280px; height:290px; text-align:center; }
#kicker { font:700 30px 'Noto Sans SC'; letter-spacing:.18em; color:#6B7280; white-space:nowrap; }
#kicker b { color:#FF4F1A; font-weight:800; }
#t1 { margin-top:22px; font:900 76px/1.22 'Noto Sans SC'; color:#141413; white-space:nowrap; }
#t2 { margin-top:10px; font:800 60px/1.25 'Noto Sans SC'; color:#FF4F1A; white-space:nowrap; }
#t2 span { background:linear-gradient(transparent 62%%, #FFD84D 62%%, #FFD84D 94%%, transparent 94%%); padding:0 6px; }
/* 边框 6：7 px 黑描边 + 橙色硬阴影 14 px + 右上角黄贴纸 */
.frame { position:absolute; background:#141413; border:7px solid #141413; border-radius:14px; box-shadow:14px 14px 0 #FF4F1A; }
.frame::after { content:attr(data-tag); position:absolute; right:-8px; top:-40px; background:#FFD84D; color:#141413; border:5px solid #141413; border-radius:10px; padding:0 16px; font:900 26px/38px 'Noto Sans SC'; transform:rotate(3deg); white-space:nowrap; z-index:6; }
.frame[data-tag='']::after, .frame:not([data-tag])::after { display:none; }
.frame .inner { position:relative; width:100%%; height:100%%; border-radius:4px; overflow:hidden; background:#fff; }
.snap { position:absolute; left:0; top:0; width:100%%; display:block; }
.hl { position:absolute; border:6px solid #FF4F1A; border-radius:10px; box-shadow:0 0 0 7px rgba(255,79,26,.2); z-index:4; }
/* 字幕（项目标准：中文 52 + 英文 30，居中，描边和背景同色） */
#subs { position:absolute; left:0; width:1080px; height:112px; z-index:30; }
#subZh { position:absolute; left:0; right:0; top:0; text-align:center; font:800 52px/66px 'Noto Sans SC'; color:#141413; -webkit-text-stroke:10px #FAF9F5; paint-order:stroke fill; white-space:nowrap; }
#subEn { position:absolute; left:0; right:0; top:70px; text-align:center; font:600 30px/40px 'Noto Sans SC'; color:#4B5563; -webkit-text-stroke:6px #FAF9F5; paint-order:stroke fill; white-space:nowrap; }
/* 数字卡 / 要点卡 */
.bigcard { position:absolute; text-align:center; background:#fff; border:1px solid #E5E7EB; border-top:8px solid #FF4F1A; border-radius:22px; box-shadow:0 16px 40px rgba(0,0,0,.12); padding:14px 30px 18px; }
.bigcard .n { font:900 92px/1.05 'Space Grotesk','Noto Sans SC'; color:#FF4F1A; white-space:nowrap; }
.bigcard .n small { font:800 42px 'Noto Sans SC'; color:#141413; margin-left:8px; }
.bigcard .d { margin-top:4px; font:700 34px/1.4 'Noto Sans SC'; color:#374151; white-space:nowrap; }
.pts { position:absolute; background:#fff; border:1px solid #E5E7EB; border-top:8px solid #FF4F1A; border-radius:22px; box-shadow:0 16px 40px rgba(0,0,0,.12); padding:14px 16px; display:grid; grid-template-columns:1fr 1fr; gap:10px 10px; }
.pts .pt { display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:14px; font:800 31px/1.2 'Noto Sans SC'; color:#374151; white-space:nowrap; }
.pts .pt i { flex:none; width:38px; height:38px; border-radius:50%%; background:#E5E7EB; color:#6B7280; font:900 24px/38px 'Noto Sans SC'; text-align:center; font-style:normal; }
.pts .pt.cur { background:#FFE98A; color:#141413; }
.pts .pt.cur i { background:#FF4F1A; color:#fff; }
.pts .pt.done i { background:#141413; color:#fff; }
/* 鲸鱼娘 */
.whale { position:absolute; image-rendering:pixelated; z-index:12; }
.wshadow { position:absolute; border-radius:50%%; background:radial-gradient(closest-side, rgba(0,0,0,.22), rgba(0,0,0,0)); z-index:11; }
/* 进度：开场 + 8 条 + 回顾 共 10 段，已播 = 黑、当前 = 橙、未播 = 灰 */
.prog { position:absolute; left:60px; width:960px; display:flex; gap:8px; z-index:20; }
.prog i { flex:1; height:14px; border-radius:7px; background:rgba(20,20,19,.16); }
.prog i.done { background:#141413; }
.prog i.cur { background:#FF4F1A; box-shadow:0 0 0 3px #FAF9F5; }
/* 清单（开场 / 回顾：8 条各一张来源截图缩略图 + 短标题，4 行 × 2 列） */
.agenda { position:absolute; inset:0; display:grid; grid-template-columns:1fr 1fr; grid-template-rows:repeat(4,1fr); gap:8px; padding:8px; background:#EEF0F3; }
.agenda .row { display:flex; background:#fff; border-radius:8px; overflow:hidden; border:1px solid #DCDFE4; }
.agenda .th { position:relative; flex:none; width:42%%; overflow:hidden; background:#fff; border-right:1px solid #DCDFE4; }
.agenda .th img { position:absolute; left:0; top:0; width:100%%; }
.agenda .th s { position:absolute; right:6px; bottom:2px; text-decoration:none; font:900 46px/1 'Noto Sans SC'; color:#16A34A; text-shadow:0 0 0 #fff, 0 3px 0 #fff, 3px 0 0 #fff, -3px 0 0 #fff, 0 -3px 0 #fff, 3px 3px 0 #fff, -3px -3px 0 #fff, 3px -3px 0 #fff, -3px 3px 0 #fff; }
.agenda .tx { flex:1; display:flex; align-items:center; gap:10px; padding:0 10px 0 10px; min-width:0; }
.agenda .tx b { flex:none; width:42px; height:42px; border-radius:50%%; background:#FF4F1A; color:#fff; font:900 26px/42px 'Noto Sans SC'; text-align:center; }
.agenda .tx span { font:800 27px/1.22 'Noto Sans SC'; color:#141413; }
.agenda.sm .tx { gap:8px; padding:0 8px; }
.agenda.sm .tx b { width:36px; height:36px; font-size:22px; line-height:36px; }
.agenda.sm .tx span { font-size:23px; }
"""


def head_html(s):
    return f'<div id="head"><div id="kicker">{s["kicker"]}</div><div id="t1">{s["t1"]}</div><div id="t2"><span>{s["t2"]}</span></div></div>'


def subs_html(s, top):
    return f'<div id="subs" style="top:{top}px"><div id="subZh">{s["zh"]}</div><div id="subEn">{s["en"]}</div></div>'


def prog_html(s, top):
    cells = "".join('<i class="%s"></i>' % ("done" if i < s["prog"] else "cur" if i == s["prog"] else "") for i in range(BAR_N))
    return f'<div class="prog" style="top:{top}px">{cells}</div>'


def whale_html(expr, size, left, top, shadow=True):
    w = f'<img class="whale" src="{uri(SPR / expr)}" style="width:{size}px;left:{left}px;top:{top}px">'
    if shadow:
        w = f'<div class="wshadow" style="left:{left + size * 0.12:.0f}px;top:{top + size * 0.9:.0f}px;width:{size * 0.76:.0f}px;height:{size * 0.1:.0f}px"></div>' + w
    return w


HEADS = ["Gemini 免费版降级", "德国开源模型 Kolibri", "DeepSeek Harness 新测试版", "GPT-6 打星际搬顶尖代码", "谷歌暂停开源漏洞赏金", "COSMIC 拒收 AI 代码",
         "Gboard 训练搬进加密服务器", "治 AI 智能体刷题"]


def grid_html(done=False, small=False):
    rows = []
    for i, h in enumerate(HEADS, 1):
        rows.append(f'<div class="row"><div class="th"><img src="{uri(SNAPS / f"news_0{i}.png")}">{"<s>✓</s>" if done else ""}</div>'
                    f'<div class="tx"><b>{i}</b><span>{h}</span></div></div>')
    return f'<div class="agenda{" sm" if small else ""}">{"".join(rows)}</div>'


def snap_html(s, inner_w):
    w, h = s["snap_wh"]
    x, y, bw, bh = s["hl"]
    return (f'<img class="snap" src="{uri(SNAPS / s["snap"])}">'
            f'<div class="hl" style="left:{x / w * 100:.2f}%;top:{y / w * inner_w:.0f}px;width:{bw / w * 100:.2f}%;height:{bh / w * inner_w:.0f}px"></div>')


def page(body, bg, extra_css=""):
    css = BASE_CSS % {"bg": uri(BGDIR / BGS[bg])}
    return (f'<!doctype html><html lang="zh"><head><meta charset="utf-8"><link rel="stylesheet" href="{uri(FONTS)}"><style>{css}{extra_css}</style></head>'
            f'<body>{body}</body></html>')


# ---------------------------------------------------------------- L1 素材主导 · 标准竖版（技能版式 B 单框）
def l1(sc, bg):
    s = SCENES[sc]
    inner_w = 986
    if sc in ("open", "rev"):
        inner = grid_html(done=(sc == "rev"))
    else:
        inner = snap_html(s, inner_w)
    frame = f'<div class="frame" style="left:40px;top:770px;width:1000px;height:569px" data-tag="{s["tag"]}"><div class="inner">{inner}</div></div>'
    if sc == "open":
        card = '<div class="bigcard" style="left:250px;top:1660px;width:740px"><div class="n">8<small>件事</small></div><div class="d">约 6 分钟 · 每条都附来源</div></div>'
    elif sc == "rev":
        card = '<div class="bigcard" style="left:250px;top:1660px;width:740px"><div class="n">✓ 8<small>条看完</small></div><div class="d">来源都在简介里 · 明天见</div></div>'
    elif sc == "kol":
        card = '<div class="bigcard" style="left:250px;top:1660px;width:740px"><div class="n">3.46B<small>活跃参数</small></div><div class="d">总参数 78B · Apache 2.0 开源</div></div>'
    else:
        chips = "".join(f'<div class="pt {"cur" if i == s["cur"] else "done" if i < s["cur"] else ""}"><i>{i + 1}</i>{p}</div>' for i, p in enumerate(POINTS[sc]))
        card = f'<div class="pts" style="left:250px;top:1660px;width:740px">{chips}</div>'
    body = head_html(s) + frame + subs_html(s, 1498) + card + whale_html(s["expr"], 192, 40, 1650) + prog_html(s, 1912)
    return page(body, bg)


# ---------------------------------------------------------------- L2 白板主导 · 竖版白板
def crop_img(name, left, top, width):
    return f'<img src="{uri(CROPS / (name + ".png"))}" style="position:absolute;left:{left}px;top:{top}px;width:{width}px">'


def l2(sc, bg):
    s = SCENES[sc]
    css = """
    #board { position:absolute; left:40px; top:290px; width:1000px; height:1290px; background:#FDFFFD; border:7px solid #141413; border-radius:14px; box-shadow:14px 14px 0 #FF4F1A; }
    #board::after { content:attr(data-tag); position:absolute; right:-8px; top:-40px; background:#FFD84D; color:#141413; border:5px solid #141413; border-radius:10px; padding:0 16px; font:900 26px/38px 'Noto Sans SC'; transform:rotate(3deg); white-space:nowrap; z-index:6; }
    #board .in { position:absolute; inset:0; overflow:hidden; border-radius:7px; }
    .photo { position:absolute; background:#fff; border:1px solid #E4E4E4; box-shadow:0 14px 30px rgba(0,0,0,.16), 0 2px 6px rgba(0,0,0,.08); transform:rotate(1.3deg); overflow:hidden; }
    .photo img { position:absolute; left:0; top:0; width:100%; }
    .tape { position:absolute; width:130px; height:40px; background:rgba(245,215,120,.62); box-shadow:0 1px 2px rgba(0,0,0,.08); z-index:3; }
    """
    tag = "AI每日日报 · 10.05"
    if sc in ("open", "rev"):
        # 标题 + 左右两列竖着叠（横屏里是左右两列）
        t = "open" if sc == "open" else "rev"
        tw = {"open": 560, "rev": 430}[t]
        # 横屏里是左右两列，竖屏改成上下叠：左列在上、右列在下；两列都留出左下角（鲸鱼娘站的地方）
        if t == "open":
            cols = crop_img("open_l", 120, 215, 760) + crop_img("open_r", 120, 650, 780)
        else:
            cols = crop_img("rev_l", 140, 235, 720) + crop_img("rev_r", 140, 670, 720)
        inner = crop_img(f"{t}_title", (986 - tw) // 2, 46, tw) + cols
        if sc == "rev":
            inner += '<div style="position:absolute;left:0;right:0;top:1130px;text-align:center;font:500 38px \'Noto Sans SC\';color:#8A93AD;letter-spacing:.06em;padding-left:120px">来源都在简介里</div>'
    else:
        t = sc
        inner = crop_img(f"{t}_title", 33, 36, 920) + crop_img(f"{t}_bul", 60, 250, 794)
        w, h = s["snap_wh"]
        pw = 600
        ph = round(pw * 0.62)
        inner += (f'<div class="photo" style="left:372px;top:828px;width:{pw}px;height:{ph}px"><img src="{uri(SNAPS / s["snap"])}"></div>'
                  f'<div class="tape" style="left:420px;top:812px;transform:rotate(-6deg)"></div><div class="tape" style="left:812px;top:822px;transform:rotate(5deg)"></div>')
    board = f'<div id="board" data-tag="{tag}"><div class="in">{inner}</div></div>'
    body = board + whale_html(s["expr"], 256, 8, 1410) + subs_html(s, 1700) + prog_html(s, 1884)
    return page(body, bg, css)


# ---------------------------------------------------------------- L3 角色主导 · 鲸鱼娘说话
def l3(sc, bg):
    s = SCENES[sc]
    css = """
    .bubble { position:absolute; left:446px; top:1240px; width:486px; min-height:236px; background:#fff; border:7px solid #141413; border-radius:30px; box-shadow:10px 10px 0 #FF4F1A; padding:20px 26px 24px; z-index:15; }
    .bubble::before { content:''; position:absolute; left:-44px; top:96px; border:22px solid transparent; border-right:38px solid #141413; border-left:0; }
    .bubble::after { content:''; position:absolute; left:-27px; top:101px; border:17px solid transparent; border-right:30px solid #fff; border-left:0; }
    .bubble .lab { font:700 24px 'Noto Sans SC'; letter-spacing:.14em; color:#6B7280; }
    .bubble .txt { margin-top:6px; font:900 54px/1.25 'Noto Sans SC'; color:#141413; }
    .bubble .txt em { font-style:normal; color:#FF4F1A; }
    .bubble .dots { margin-top:14px; display:flex; gap:10px; }
    .bubble .dots i { width:34px; height:10px; border-radius:5px; background:rgba(20,20,19,.16); }
    .bubble .dots i.on { background:#FF4F1A; }
    """
    inner_w = 846
    if sc in ("open", "rev"):
        inner = grid_html(done=(sc == "rev"), small=True)
    else:
        inner = snap_html(s, inner_w)
    frame = f'<div class="frame" style="left:110px;top:680px;width:860px;height:490px" data-tag="{s["tag"]}"><div class="inner">{inner}</div></div>'
    if sc == "open":
        lab, txt, dots = "先说第一件", "Gemini 免费版<br><em>降级</em>", ""
    elif sc == "rev":
        lab, txt, dots = "来源都在简介里", "今天就这些，<br><em>明天见</em>～", ""
    else:
        cur = s["cur"]
        pt = POINTS[sc][cur]
        txt = {"kol": "每次只激活<br><em>3.46B</em>", "cos": "代码注释<br>描述<em>都算</em>"}[sc]
        lab = f"要点 {cur + 1} / 4"
        dots = '<div class="dots">' + "".join(f'<i class="{"on" if i <= cur else ""}"></i>' for i in range(4)) + "</div>"
    bubble = f'<div class="bubble"><div class="lab">{lab}</div><div class="txt">{txt}</div>{dots}</div>'
    body = head_html(s) + frame + whale_html(s["expr"], 384, 24, 1218) + bubble + subs_html(s, 1692) + prog_html(s, 1876)
    return page(body, bg, css)


COVER16 = Path(r"D:\大疆\AI日报\2026-10-05\封面\封面_16x9_1920x1080.png")


def l0(sc, bg):
    """第 0 帧：封面保持原样（用户 2026-10-05：“封面不要动还是保持之前的封面”），16:9 原图居中，只套上边框和背景。"""
    body = (f'<div class="frame" style="left:40px;top:889px;width:1000px;height:576px"><div class="inner"><img class="snap" src="{uri(COVER16)}"></div></div>')
    return page(body, bg)


LAYOUTS = {"L1": l1, "L2": l2, "L3": l3, "L0": l0}


# ================================================================ 拼图
from PIL import ImageDraw, ImageFont

FONT = r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf"
ACC, INK, GRAY, PAPER = (255, 79, 26), (20, 20, 19), (107, 114, 128), (241, 242, 246)


def F(size, w=500):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([w])
    except Exception:  # noqa: BLE001
        pass
    return f


def phone(png, width, zones=False):
    im = Image.open(png).convert("RGB")
    h = round(im.height * width / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    if zones:
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        k = width / 1080
        shade = (96, 104, 120, 62)
        d.rectangle((0, 0, width, round(250 * k)), fill=shade)
        d.rectangle((0, round(1950 * k), width, h), fill=shade)
        d.rectangle((round(940 * k), round(1170 * k), width, round(1950 * k)), fill=shade)
        f = F(max(11, round(26 * k)), 500)
        d.text((round(30 * k), round(100 * k)), "平台顶栏（状态栏 / 标签）", font=f, fill=(70, 78, 92, 200))
        d.text((round(30 * k), round(2010 * k)), "平台账号名 / 文案 / 音乐条", font=f, fill=(70, 78, 92, 200))
        d.text((round(946 * k), round(1500 * k)), "按\n钮", font=f, fill=(70, 78, 92, 200))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    r = round(width * 0.085)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    out = Image.new("RGBA", (width + 16, im.height + 16), (0, 0, 0, 0))
    ImageDraw.Draw(out).rounded_rectangle((0, 0, width + 15, im.height + 15), r + 8, fill=(26, 26, 31, 255))
    out.paste(im, (8, 8), mask)
    return out


NOSTART = "，。、；：！？）」』”’,.;:!?)"


def wrap(text, font, maxw):
    lines, cur = [], ""
    for ch in text:
        if cur and font.getlength(cur + ch) > maxw and ch not in NOSTART:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def text_lines(d, x, y, lines, font, fill, gap=8):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += font.size + gap
    return y


DET = {
    "L1": ("排版① 素材主导 · 标准竖版", "ink", "墨色印花",
           ["完全照短视频技能：标题 280–570 不动 → 来源截图框 770–1339（边框 6，贴纸 = 来源）→ 字幕 1498 → 底下一张卡 1660–1865 → 进度条。",
            "卡片跟着配音换：有数字就上数字卡（3.46B），没数字就上 2×2 要点卡（当前这条高亮黄底）；来源截图上用橙框圈出原文那句话。"],
           [("open", "开场：今天说 8 件事", "清单 = 8 张来源截图缩略图 + 短标题"),
            ("kol", "新闻条：有大数字", "数字卡随配音出现，原文数字被橙框圈住"),
            ("cos", "新闻条：纯文字要点", "要点卡 4 条，说到哪条哪条变黄"),
            ("rev", "今日回顾", "同一个清单，缩略图上盖绿勾")]),
    "L2": ("排版② 白板主导 · 竖版白板", "color", "原色印花",
           ["整块白板（边框 6、贴纸 = 日报 10.05）压在印花背景上，里面是日报原来的手写：标题 + 黄色波浪线、来源行、蓝色短横要点、黄圈标重点。",
            "手写字就是长视频里同一套笔画数据，竖屏版照样逐笔写出来；来源截图像照片一样贴在白板右下，鲸鱼娘站在白板左下角。"],
           [("open", "开场：今天说这几件事", "手写清单，左列 1–4、右列 5–8 上下叠"),
            ("kol", "新闻条：有大数字", "四条手写要点，数字用黄圈"),
            ("cos", "新闻条：纯文字要点", "同一块白板，截图贴在右下"),
            ("rev", "今日回顾", "打勾清单（和长视频回顾一样）")]),
    "L3": ("排版③ 角色主导 · 鲸鱼娘说话", "orange", "橙色印花",
           ["鲸鱼娘放大到 6 倍像素（384 px），表情和嘴型照日报的配音走；要点做成对话气泡，一次只冒一条，气泡里的 4 个小点显示第几条。",
            "来源截图缩成上面一个 860×490 的框（边框 6），同样用橙框圈出原文那句话；字幕在下。"],
           [("open", "开场：先说第一件", "气泡念出第一件事，框里是 8 条清单"),
            ("kol", "新闻条：有大数字", "气泡 = 当前要点（要点 2 / 4）"),
            ("cos", "新闻条：纯文字要点", "换一条要点，气泡里换字"),
            ("rev", "今日回顾：明天见", "开心表情，清单缩略图盖勾")]),
}


def make_sheets():
    R = RENDER
    # ---------------- 总览
    W, PW = 1840, 400
    cards = [
        (R / "L1_kol_ink.png", "① 素材主导 · 标准竖版",
         "照短视频技能的版式 B：标题在上，来源截图进边框 6 当主角，字幕在下，下面一张数字卡 / 要点卡，鲸鱼娘站在卡片旁。",
         "优点：和你其它短视频最像；来源截图最大最清楚。", "取舍：日报手写白板的味道没了，鲸鱼娘最小。", "背景示例：墨色印花"),
        (R / "L2_kol_color.png", "② 白板主导 · 竖版白板",
         "保留日报的手写白板：手写标题、手写要点、黄圈标重点、胶带贴来源截图；整块白板套边框 6，鲸鱼娘站在白板左下角。",
         "优点：和长视频一脉相承，辨识度最高。", "取舍：字最多，来源截图最小；手写要逐笔动画。", "背景示例：原色印花"),
        (R / "L3_kol_orange.png", "③ 角色主导 · 鲸鱼娘说话",
         "鲸鱼娘放大到 384 px，要点做成对话气泡，一次只冒一条；来源截图缩成上面一个框。",
         "优点：最像“有人在讲”，画面最干净。", "取舍：来源截图缩小；气泡要点要做进出动画。", "背景示例：橙色印花"),
        (R / "L0_cover_ink.png", "第 0 帧 · 封面不动",
         "封面保持日报原来的样子（16:9 原图），只居中放进竖屏，套同款边框和背景；三种排版都一样。",
         "视频号只能选视频里的帧，所以第 0 帧就是这张。", "封面文件一个像素都不改。", "—"),
    ]
    gap = (W - 80 - 4 * (PW + 16)) // 3
    sheet = Image.new("RGB", (W, 1500), PAPER)
    d = ImageDraw.Draw(sheet)
    d.text((40, 34), "日报 → 竖屏短视频：三种排版（10/5 这期）", font=F(52, 400), fill=INK)
    d.text((40, 108), "同一条新闻（Kolibri）、同一句字幕、同一套规格：1080×2340 · 版式 B 安全区 · 边框 6 · 中英双语字幕 52 / 30 px", font=F(25, 400), fill=GRAY)
    d.text((40, 144), "背景印花三选一随机 · BGM 垫底 · 不加片头片尾　　浅灰块 = 平台遮挡区（顶栏 / 账号名文案 / 右侧按钮），重要的字都避开了", font=F(25, 400), fill=GRAY)
    x = 40
    top = 200
    fd, fb, fa = F(24, 400), F(34, 800), F(24, 700)
    maxy = 0
    for png, title, desc, pro, con, bgnote in cards:
        ph = phone(png, PW, zones=True)
        sheet.paste(ph, (x, top), ph)
        y = top + ph.height + 22
        d.text((x, y), title, font=fb, fill=INK)
        y += 54
        y = text_lines(d, x, y, wrap(desc, fd, PW + 8), fd, (55, 65, 81), 6) + 6
        y = text_lines(d, x, y, wrap(pro, fa, PW + 8), fa, ACC, 6)
        y = text_lines(d, x, y, wrap(con, fd, PW + 8), fd, GRAY, 6)
        maxy = max(maxy, y)
        x += PW + 16 + gap
    sheet = sheet.crop((0, 0, W, maxy + 30))
    sheet.save(HERE / "排版总览.png")
    print("  ✓ 排版总览.png", sheet.size)

    # ---------------- 各排版详情（4 个场景）
    for lay, (title, bg, bgname, desc, scenes) in DET.items():
        PW2, G = 400, 40
        Wd = 50 * 2 + 4 * (PW2 + 16) + 3 * G
        sh = Image.new("RGB", (Wd, 1580), PAPER)
        dd = ImageDraw.Draw(sh)
        dd.text((50, 34), title, font=F(48, 400), fill=INK)
        y = 104
        for ln in desc:
            dd.text((50, y), ln, font=F(24, 400), fill=(55, 65, 81))
            y += 36
        dd.text((50, y + 4), f"背景：{bgname}（每期视频随机挑一张；三种都能配这个排版，见《背景对照》）　·　浅灰块 = 平台遮挡区", font=F(23, 500), fill=ACC)
        top = y + 56
        x = 50
        for sc, nm, note in scenes:
            ph = phone(R / f"{lay}_{sc}_{bg}.png", PW2, zones=True)
            sh.paste(ph, (x, top), ph)
            dd.text((x, top + ph.height + 18), nm, font=F(29, 800), fill=INK)
            dd.text((x, top + ph.height + 58), note, font=F(23, 400), fill=GRAY)
            x += PW2 + 16 + G
        sh = sh.crop((0, 0, Wd, top + ph.height + 110))
        name = {"L1": "排版①_素材主导", "L2": "排版②_白板", "L3": "排版③_角色"}[lay] + ".png"
        sh.save(HERE / name)
        print("  ✓", name, sh.size)

    # ---------------- 背景对照 3×3
    PW3, G3 = 280, 30
    labs = [("color", "原色印花"), ("ink", "墨色印花"), ("orange", "橙色印花")]
    rows = [("L1", "① 素材主导"), ("L2", "② 白板主导"), ("L3", "③ 角色主导")]
    Wb = 60 + 200 + 3 * (PW3 + 16) + 2 * G3 + 40
    sample = phone(R / "L1_kol_ink.png", PW3)
    Hb = 190 + 3 * (sample.height + 30) + 20
    sh = Image.new("RGB", (Wb, Hb), PAPER)
    dd = ImageDraw.Draw(sh)
    dd.text((60, 30), "背景对照：三种排版 × 三张背景印花", font=F(46, 400), fill=INK)
    dd.text((60, 100), "三张印花都在随机池里，每期视频随机挑一张；9 种组合都摆出来，看哪个更顺眼", font=F(23, 400), fill=GRAY)
    for ci, (bg, bn) in enumerate(labs):
        dd.text((60 + 200 + ci * (PW3 + 16 + G3), 148), bn, font=F(28, 800), fill=INK)
    for ri, (lay, ln) in enumerate(rows):
        y = 190 + ri * (sample.height + 30)
        dd.text((60, y + sample.height // 2 - 20), ln, font=F(30, 800), fill=INK)
        for ci, (bg, bn) in enumerate(labs):
            ph = phone(R / f"{lay}_kol_{bg}.png", PW3)
            sh.paste(ph, (60 + 200 + ci * (PW3 + 16 + G3), y), ph)
    sh.save(HERE / "背景对照.png")
    print("  ✓ 背景对照.png", sh.size)


def render_all(jobs):
    from playwright.sync_api import sync_playwright
    RENDER.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 2340})
        for lay, sc, bg in jobs:
            out = RENDER / f"{lay}_{sc}_{bg}.png"
            html = LAYOUTS[lay](sc, bg)
            hp = RENDER / f"{lay}_{sc}_{bg}.html"
            hp.write_text(html, encoding="utf-8")
            pg.goto(hp.as_uri())
            pg.wait_for_timeout(350)
            pg.screenshot(path=str(out))
            print("  ✓", out.name)
        b.close()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "render"
    if cmd == "render":
        make_crops()
        bgmap = {"L1": "ink", "L2": "color", "L3": "orange"}
        jobs = [(lay, sc, bgmap[lay]) for lay in ("L1", "L2", "L3") for sc in ORDER]
        # 背景对照：每种排版 × 三种背景（只出 kol 场景）
        jobs += [(lay, "kol", bg) for lay in ("L1", "L2", "L3") for bg in BGS if bg != bgmap[lay]]
        jobs += [("L0", "cover", "ink")]
        render_all(jobs)
    elif cmd == "sheets":
        make_sheets()
