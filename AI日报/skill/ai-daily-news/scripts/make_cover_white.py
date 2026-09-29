"""White two-line cover for 《AI每日日报》 (style of B 站「通俗解释」: white, grey lead line + coloured hook line, character below).

    python make_cover_white.py <期目录> --from-script        # 日报流程用：台本.json 的 cover 块 + D 版 + 鲸鱼娘蓝
    python make_cover_white.py <期目录> --line1 "Claude 拒绝回答" --line2 "也要收钱了？" [--pose think_m0] [--eyes idle_look_r_m0]
                               [--fx fx_think] [--qmark] [--place center|left|right] [--scale 9] [--out <目录>] [--tag 文字]

--from-script reads 台本.json "cover": {"item": 1, "line1": "铺垫", "line2": "钩子？", "mood": "吃惊|开心|疑问|认真"}
(item = 大字讲第几条新闻, 1 起): layout D (character bottom-right, the other headlines as a small list on the left),
theme blue (用户 2026-09-28 选定), pose from POSES[mood] rotated by date. No cover block -> item 1's headline as one line.

*文字* inside a line flips its colour (orange inside line 1, grey inside line 2).
The character is 鲸鱼娘's 64x64 frame `pose` (a key of 素材/角色/动作帧/动作帧/anims.json, frame 0, or "key#N"), with the
eyes rectangle taken from `eyes` (e.g. idle_surprised_m0 / idle_happy_m0 / idle_look_r_m0: the pack keeps hands out of that
rectangle, so any expression fits any pose), `fx` overlay frames (fx_emph "!", fx_think, fx_glint, fx_listen …) and an
optional orange pixel "?" (--qmark) drawn on the same grid. She is scaled by an integer, never mirrored.
Writes to --out (default <期目录>/封面/): 封面_16x9_1920x1080.png, 封面_4x3_1440x1080.png (centre crop x 240..1680),
封面_预览.png (feed-size board, from 《原LAI如此》 make_cover), cover.html, _cover_data.json, sprite.png.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
SKILL = Path(__file__).resolve().parent.parent
SERIES = SKILL.parent.parent
TEMPLATE = SKILL / "assets" / "cover-template" / "cover.white.html"
YUANLAI_SCRIPTS = Path(r"D:/大疆/AI科普/skill/yuanlai-ruci-episode/scripts")
FRAMES = SERIES / "素材" / "角色" / "动作帧" / "动作帧"          # 大肥鱼像素素材包/素材/动作帧（全套动作）
ORANGE = (245, 162, 29, 255)
# 配色（用户 2026-09-28：给橙色、鲸鱼娘蓝和另一种）。lead = 第 1 行和清单标题，accent = 第 2 行、清单圆点、像素问号
THEMES = {
    "orange": {"bg": "#FFFFFF", "lead": "#8C8C8C", "accent": "#F5A21D", "list": "#5A5A5A", "more": "#9A9A9A"},
    # 鲸鱼娘调色板的亮蓝 B #4A88DA（尾巴、蝴蝶结、围裙上的小鲸鱼）；铺垫行用偏蓝的灰
    "blue": {"bg": "#FFFFFF", "lead": "#8A93AD", "accent": "#4A88DA", "list": "#4D5670", "more": "#9AA2B8"},
    # 深海夜色：视频底色的藏青 + 金色钩子（她裙子上的金色提亮），角色背后一圈浅蓝柔光，免得深色描边糊进底色
    "night": {"bg": "#1B2340", "lead": "#AEBBDD", "accent": "#FFC94D", "list": "#DCE3F5", "more": "#7F8CB3",
              "glow": "rgba(151,195,240,.22)"},
}
QMARK = ["..####..", ".##..##.", "......##", ".....##.", "....##..", "...##...", "...##...", "........", "...##...", "...##..."]
# 情绪 → 姿势组（台本 cover.mood）。角色站右下角（D 版），指向右边的 reach / point 会指到画面外，不用；
# 同一情绪按日期轮换，连着几天同一种情绪也不会一模一样（用户 2026-09-28：姿势多一些变化）
POSES = {
    "吃惊": [dict(pose="finger_up_m2", eyes="idle_surprised_m0", fx=["fx_emph"]),
             dict(pose="shrug_m1", eyes="idle_surprised_m0"),
             dict(pose="pose_huh")],
    "开心": [dict(pose="thumb_m0", eyes="idle_happy_m0", fx=["fx_glint"]),
             dict(pose="hip_m0", eyes="idle_happy_m0"),
             dict(pose="wave_a_m0", eyes="idle_happy_m0"),
             dict(pose="pose_yay")],
    "疑问": [dict(pose="think_m0", eyes="idle_look_ur_m0", qmark=True),
             dict(pose="ear_m0", eyes="idle_look_r_m0", fx=["fx_listen"]),
             dict(pose="pose_huh")],
    "认真": [dict(pose="finger_up_m0", eyes="idle_determined_m0", fx=["fx_emph"]),
             dict(pose="hold_m0", eyes="idle_determined_m0"),
             dict(pose="chest_m0", eyes="idle_determined_m0")],
}
DEFAULT_THEME = "blue"          # 用户 2026-09-28 选定：D 版（角色右下、左边小字清单）+ 鲸鱼娘蓝


def pose_for(mood, date):
    """a pose dict of the mood's group, rotated by the day of the year"""
    group = POSES.get(mood) or POSES["吃惊"]
    return group[date.timetuple().tm_yday % len(group)]


def rel(target, start):
    return Path(os.path.relpath(target, start)).as_posix()


def load_anims():
    return json.loads((FRAMES / "anims.json").read_text(encoding="utf-8"))


def frame_path(anims, key):
    """'think_m0' / 'think_m0#3' / a path under FRAMES -> file"""
    p = FRAMES / key
    if p.is_file():
        return p
    m = re.match(r"^(.+?)(?:#(\d+))?$", key)
    k, i = m.group(1), int(m.group(2) or 0)
    fr = (anims["anims"].get(k) or {}).get("frames") or []
    if not fr:
        sys.exit(f"动作帧里没有 {key}（看 {FRAMES / 'anims.json'} 的 anims）")
    return FRAMES / fr[min(i, len(fr) - 1)]


def compose_sprite(pose, eyes=None, fx=(), qmark=None, qcolor=ORANGE):
    """64x64 RGBA: pose frame, eyes rectangle of another frame, fx overlays, pixel '?' (qcolor) at qmark=(sx, sy)."""
    anims = load_anims()
    im = Image.open(frame_path(anims, pose)).convert("RGBA")
    if eyes:
        x0, y0, x1, y1 = anims["patch_rects"]["eyes"]
        im.paste(Image.open(frame_path(anims, eyes)).convert("RGBA").crop((x0, y0, x1, y1)), (x0, y0))
    for f in fx or ():
        im.alpha_composite(Image.open(frame_path(anims, f)).convert("RGBA"))
    if qmark:
        sx, sy = qmark
        for j, row in enumerate(QMARK):
            for i, ch in enumerate(row):
                if ch == "#" and 0 <= sx + i < im.width and 0 <= sy + j < im.height:
                    im.putpixel((sx + i, sy + j), qcolor)
    return im, anims


def place_x(place, scale, frame_w=64):
    if place == "center":
        return 960 - frame_w * scale // 2
    if place == "left":
        return 270                                  # 4:3 裁切从 x 240 起
    return 1680 - frame_w * scale - 30              # right: 尾巴尖也留在 4:3 里


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dir")
    ap.add_argument("--from-script", action="store_true", help="文案、姿势、版式都从 台本.json 的 cover 块来（日报流程用）")
    ap.add_argument("--line1", default="", help="灰色铺垫行（可空）")
    ap.add_argument("--line2", default="", help="彩色钩子行")
    ap.add_argument("--pose", default="think_m0")
    ap.add_argument("--eyes", default="", help="换眼睛：idle_happy_m0 / idle_surprised_m0 / idle_determined_m0 / idle_look_r_m0 …")
    ap.add_argument("--fx", default="", help="叠加特效帧，逗号分隔：fx_emph,fx_glint …")
    ap.add_argument("--qmark", action="store_true", help="头右上角画一个橙色像素问号")
    ap.add_argument("--qmark-at", default="54,2", help="问号左上角在 64 格里的位置 sx,sy")
    ap.add_argument("--place", default="center", choices=["center", "left", "right"])
    ap.add_argument("--scale", type=int, default=9)
    ap.add_argument("--foot", type=int, default=1062, help="鞋底所在的屏幕 y")
    ap.add_argument("--text-cx", type=int, help="文字中线 x（默认按站位：居中 960，角色在右 900，在左 1020）")
    ap.add_argument("--maxw", type=int, help="文字最大宽度（默认居中 1400，其他 1320）")
    ap.add_argument("--l1px", type=int, default=168)
    ap.add_argument("--l2px", type=int, default=236)
    ap.add_argument("--theme", default=DEFAULT_THEME, choices=sorted(THEMES), help="配色：orange 橙 / blue 鲸鱼娘蓝（默认） / night 深海夜色")
    ap.add_argument("--tag", default="", help="左下角小字（默认没有）")
    ap.add_argument("--others", default="none", choices=["none", "auto"],
                    help="auto：角色对面用小字列出其余新闻标题（episode.json 里除 --featured 那条以外的）")
    ap.add_argument("--featured", type=int, default=0, help="大字讲的是第几条新闻（从 0 起），清单里不再列它")
    ap.add_argument("--others-max", type=int, default=5)
    ap.add_argument("--others-head", default="今天还有 {n} 条", help="清单标题，{n} = 其余条数；空字符串不显示")
    ap.add_argument("--out", help="输出目录（默认 <期目录>/封面）")
    args = ap.parse_args()
    ep = Path(args.episode_dir).resolve()
    ep_json = json.loads((ep / "episode.json").read_text(encoding="utf-8"))
    out = Path(args.out).resolve() if args.out else ep / "封面"
    out.mkdir(parents=True, exist_ok=True)
    for p in (TEMPLATE, FRAMES / "anims.json"):
        if not p.is_file():
            sys.exit(f"缺少 {p}")
    if args.from_script:
        sc = json.loads((ep / "台本.json").read_text(encoding="utf-8"))
        cv = sc.get("cover") or {}
        news = sc.get("news") or []
        item = int(cv.get("item") or 1)
        if not 1 <= item <= len(news):
            sys.exit(f"台本 cover.item = {item}，只有 {len(news)} 条新闻")
        if not cv.get("line2"):
            print("[提醒] 台本里没有 cover 块：封面大字先用第 1 条的标题（写台本时补 cover.line1 / line2 / mood）")
        args.line1 = cv.get("line1", "") if cv.get("line2") else ""
        args.line2 = cv.get("line2") or news[item - 1]["headline"]
        pz = pose_for(cv.get("mood", "吃惊"), datetime.date.fromisoformat(sc.get("date") or ep.name))
        args.pose, args.eyes, args.fx = pz["pose"], pz.get("eyes", ""), ",".join(pz.get("fx", []))
        args.qmark = bool(pz.get("qmark"))
        args.place, args.others, args.featured = "right", "auto", item - 1
        print(f"封面：第 {item} 条｜{args.line1}／{args.line2}｜{cv.get('mood', '吃惊')} → {args.pose} {args.eyes} {args.fx}"
              f"{' ?' if args.qmark else ''}｜{args.theme}")
    if not args.line2:
        sys.exit("要 --line2（或 --from-script）")

    theme = THEMES[args.theme]
    acc = theme["accent"].lstrip("#")
    sprite, anims = compose_sprite(args.pose, args.eyes or None, [f for f in args.fx.split(",") if f],
                                   tuple(int(v) for v in args.qmark_at.split(",")) if args.qmark else None,
                                   tuple(int(acc[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    sprite_png = out / "sprite.png"
    sprite.save(sprite_png)
    fw, fh = anims["frame_w"], anims["frame_h"]
    data = {"line1": args.line1, "line2": args.line2, "l1px": args.l1px, "l2px": args.l2px,
            "maxw": args.maxw or (1400 if args.place == "center" else 1320),
            "textCx": args.text_cx or {"center": 960, "right": 900, "left": 1020}[args.place],
            "scale": args.scale, "frame": [fw, fh], "footRow": anims["anchor"]["foot_y"],
            "fishX": place_x(args.place, args.scale, fw), "foot": args.foot, "tag": args.tag, "theme": theme,
            "_theme": args.theme, "_pose": args.pose, "_eyes": args.eyes, "_fx": args.fx, "_qmark": args.qmark, "_place": args.place}
    if args.others == "auto":
        if args.place == "center":
            sys.exit("--others auto 需要角色站在一侧：--place left 或 right")
        heads = [n["headline"] for n in ep_json.get("news", [])]
        rest = [h for i, h in enumerate(heads) if i != args.featured]
        shown = rest[: args.others_max]
        data.update({"others": shown, "othersHead": args.others_head.format(n=len(rest)),
                     "othersMore": f"……共 {len(heads)} 条" if len(rest) > len(shown) else "",
                     # 清单放在角色对面：角色在右 → 清单 x 270..1040；角色在左 → 清单 x 880..1650（都在 4:3 裁切内）
                     "listX": 270 if args.place == "right" else 880, "listW": 770, "listBottom": 1000})
    html = out / "cover.html"
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("{{FONTS_CSS}}", rel(SERIES / "素材" / "字体" / "fonts.css", out)).replace("{{SPRITE}}", "sprite.png")
    html.write_text(page, encoding="utf-8")
    data_path = out / "_cover_data.json"
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    tmp = out / "_render"
    tmp.mkdir(exist_ok=True)
    cmd = [sys.executable, str(SERIES / "片头片尾" / "render.py"), str(html), "--data", str(data_path),
           "--stills", "0", "--stills-dir", str(tmp)]
    for attempt in (1, 2):                   # 无头浏览器偶尔起不来（2026-09-28 出过一次），重跑一次就好
        if subprocess.run(cmd).returncode == 0:
            break
        if attempt == 2:
            sys.exit("封面渲染两次都失败，看上面的报错")
        print("封面渲染失败，重试一次", flush=True)
    src = Image.open(tmp / "still_0.00.png").convert("RGB")
    assert src.size == (1920, 1080), src.size
    p169, p43, pprev = out / "封面_16x9_1920x1080.png", out / "封面_4x3_1440x1080.png", out / "封面_预览.png"
    src.save(p169, optimize=True)
    crop = src.crop((240, 0, 1680, 1080))
    crop.save(p43, optimize=True)
    sys.path.insert(0, str(YUANLAI_SCRIPTS))
    import make_cover as yl                                   # 《原LAI如此》 helpers: feed thumbnails + preview board
    yl.preview_board(SERIES, src, crop, pprev, yl.video_length_label(ep, ep_json))
    shutil.move(str(tmp / "still_0.00.png"), str(tmp / "last_still.png"))
    for p in (p169, p43, pprev):
        print(p.name, Image.open(p).size, f"{p.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
