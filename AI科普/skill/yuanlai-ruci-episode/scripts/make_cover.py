"""Render the episode cover (whiteboard or receipt template) and export the Bilibili sizes.

usage: python make_cover.py <episode_dir> [--series D:/大疆/AI科普] [--html-only]

Two templates in assets/cover-template, picked by the episode's style (cover.json "style" overrides it):
  style "board" (the whiteboard episodes: new episodes by default, and #03 since 2026-09-28) -> cover.board.html:
      white page, the title handwritten with this episode's own hand.js + stroke data (the same hand as the video),
      a yellow marker wave under t1, orange question marks, the presenter bottom left pointing at the title
      (user 2026-09-28: 「封面你也要重新生成一下相同的风格」)
  anything else (printed cards, episodes 1, 2, 4) -> cover.template.html: the receipt on a background photo

First run writes <ep>/封面/cover.json (a skeleton to fill in) and <ep>/封面/cover.html
(copied from assets/cover-template with the relative paths filled in), then stops if the
title is still empty. Once cover.json has the text, each run renders one 1920x1080 still and writes:
  封面_16x9_1920x1080.png   16:9 cover
  封面_4x3_1440x1080.png    centre crop (x 240..1680) for the 4:3 slot
  封面_预览.png              both covers + feed-size thumbnails (320x180, 480x270, 4:3 320x240)
Review 封面_预览.png at feed size before showing it to the user.

Whiteboard cover.json keys (everything except sprite is passed to the page as window.__DATA__):
  t1, t2            two big handwritten lines (t1 = the keyword people search for; a trailing ？ of t2 is orange)
  sub               a smaller third line (the second question of the title; trailing ？ orange); when missing, the
                    text of a receipt-style subHTML is used
  hl                the part of sub underlined with the yellow marker (optional)
  sprite            as below (default reach_m2/00.png: pointing at the title)
  any key of the template (bx, bxr, btop, bbot, t1px, t2px, subpx, gap1, gap2, pen, ul, hlW, brand, scale, whoX, foot,
  shadow, q, arrow ...) can be overridden; object keys merge one level deep. The presenter preset's cover block
  (receipt geometry) is not used here.
The handwriting uses <ep>/制作/engine/hand.js and hand_glyphs.py (falls back to assets/engine-template with a note);
_handdata.js next to cover.html holds the strokes of just the cover text.

Receipt cover: the character is this episode's presenter (episode.json "presenter"; none = 山田凉): her frame folder
(presenter.frames) gives the sprite, and her preset's cover block (epcommon.PRESENTERS[id]["cover"], e.g. a smaller
scale and another x for the wider 鲸鱼娘) is applied under cover.json.

Receipt cover.json keys (everything except bg_file/sprite is passed to the page as window.__DATA__):
  t1, t2, subHTML   the three text lines (see the comment block at the top of the template script)
  bg_file           file name in 素材/背景图库 (default: the first background in episode.json)
  plain             a solid page colour instead of the photo, e.g. "#FFFFFF" (bg_file is then ignored; no vignette /
                    warm light, softer shadows). 第 4 期用户要白底、不用背景图时加的
  sprite            frame of the presenter (default reach_m2/00.png: pointing at the title): a path under her frame
                    folder, or an anims.json key ("reach_m2", "reach_m2#3" = frame 3). Missing -> her idle_m0 frame 0
                    with a warning (e.g. before her action frames exist).
  bg                {scale, fx, fy, opacity, blur} background framing; any other template key
                    (rx, rw, t1px, t2px, subpx, scale, ryoX, foot, q {x, y | sx, sy}, shadow, floor ...) can be
                    overridden the same way; object keys merge one level deep.
Order: template defaults (the #01 cover) < presenter preset cover < episode.json presenter.cover < 封面/cover.json.
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
sys.dont_write_bytecode = True
SKILL = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL / "assets" / "cover-template" / "cover.template.html"
BOARD_TEMPLATE = SKILL / "assets" / "cover-template" / "cover.board.html"
ENGINE_T = SKILL / "assets" / "engine-template"
DEFAULT_SERIES = Path(r"D:/大疆/AI科普")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402


def resolve_sprite(frames_dir, sprite, who):
    """(file, note): the cover sprite of the presenter. sprite = a path under her frame folder, or an anims.json key
    (optionally '#index'). Falls back to her idle_m0 frame 0 (note says so); (None, reason) when nothing is there."""
    p = frames_dir / sprite
    if p.is_file():
        return p, None
    table = (C.load_json(frames_dir / "anims.json", {}) or {}).get("anims") or {}
    m = re.match(r"^(.+?)(?:/(\d+)\.png|#(\d+))?$", sprite)
    key, idx = (m.group(1), int(m.group(2) or m.group(3) or 0)) if m else (sprite, 0)
    for k, i, note in ((key, idx, None), ("idle_m0", 0, f"{who}还没有 {sprite}，封面先用 idle_m0 第 0 帧（她的动作帧画完后重跑）")):
        fr = (table.get(k) or {}).get("frames") or []
        if fr and (frames_dir / fr[min(i, len(fr) - 1)]).is_file():
            return frames_dir / fr[min(i, len(fr) - 1)], note
    return None, f"{who}的帧目录里没有 {sprite}，也没有 idle_m0：{frames_dir}"


def merge_cover(*layers):
    """dict layers, later wins; dict values merge one level deep (like the template)"""
    out = {}
    for layer in layers:
        for k, v in (layer or {}).items():
            out[k] = dict(out[k], **v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def rel(target, start):
    return Path(os.path.relpath(target, start)).as_posix()


def font(series, px, wght=500):
    f = ImageFont.truetype(str(series / "素材" / "字体" / "NotoSansSC.ttf"), px)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def feed_thumb(series, src, w, h, duration_label):
    """Downscale like the feed does, then overlay the stats gradient and the duration pill."""
    im = src.resize((w, h), Image.LANCZOS).convert("RGBA")
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    gh = round(h * 0.22)
    for i in range(gh):
        d.line([(0, h - gh + i), (w, h - gh + i)], fill=(0, 0, 0, int(170 * (i / gh) ** 1.3)))
    im = Image.alpha_composite(im, ov)
    d = ImageDraw.Draw(im)
    fs = max(10, round(h * 0.068))
    f = font(series, fs)
    pad = round(w * 0.025)
    d.text((pad, h - pad - fs - 1), "\u25B6 1.2万    \u25A4 356", font=f, fill=(255, 255, 255, 235))
    tw = d.textlength(duration_label, font=f)
    bw, bh = tw + fs * 0.9, fs * 1.45
    x1, y1 = w - pad, h - pad + 2
    box = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([x1 - bw, y1 - bh, x1, y1], radius=round(fs * 0.3), fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, box)
    ImageDraw.Draw(im).text((x1 - bw + fs * 0.45, y1 - bh + fs * 0.12), duration_label, font=f, fill=(255, 255, 255, 240))
    return im.convert("RGB")


def video_length_label(ep, ep_json):
    mp4 = ep / f"{ep_json.get('dir_name', ep.name)}_成片.mp4"
    if mp4.exists():
        try:
            sec = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                                 "-of", "default=nw=1:nk=1", str(mp4)]).decode().strip())
            return f"{int(sec // 60):02d}:{int(sec % 60):02d}"
        except Exception:
            pass
    return "06:00"


def preview_board(series, src, crop, out_path, label_text):
    BG, FG, DIM = (30, 30, 32), (235, 233, 227), (150, 147, 140)
    M, G = 40, 36
    big_w, big_h, s43_w = 1152, 648, 864
    t320 = feed_thumb(series, src, 320, 180, label_text)
    t480 = feed_thumb(series, src, 480, 270, label_text)
    c320 = feed_thumb(series, crop, 320, 240, label_text)
    W = max(M + big_w + G + s43_w + M, M + 320 + G + 640 + G + 480 + G + 320 + M)
    H = M + 44 + big_h + G + 44 + 360 + M
    board = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(board)
    fh, fs = font(series, 28, 700), font(series, 22, 500)

    def label(x, y, title, note=""):
        d.text((x, y), title, font=fh, fill=FG)
        d.text((x + d.textlength(title, font=fh) + 16, y + 5), note, font=fs, fill=DIM)

    label(M, M, "16:9 封面", "1920×1080")
    board.paste(src.resize((big_w, big_h), Image.LANCZOS), (M, M + 44))
    x43 = M + big_w + G
    label(x43, M, "4:3 封面", "1440×1080 · 居中裁切")
    board.paste(crop.resize((s43_w, big_h), Image.LANCZOS), (x43, M + 44))
    y1 = M + 44 + big_h + G
    x = M
    for title, note, im in (("信息流 320×180", "实际像素", t320),
                            ("320×180 ×2", "最近邻放大", t320.resize((640, 360), Image.NEAREST)),
                            ("信息流 480×270", "", t480),
                            ("4:3 · 320×240", "", c320)):
        label(x, y1, title, note)
        board.paste(im, (x, y1 + 44))
        x += im.width + G
    board.save(out_path, optimize=True)


def presenter_sprite(series, ep_json, cfg):
    """(presenter, label, sprite file, geom) for this episode's presenter; exits when her frame is missing"""
    pr = C.presenter_of(ep_json)
    who = f"讲解员「{pr['name']}」"
    frames_dir = C.presenter_frames(series, ep_json)
    sprite_path, note = resolve_sprite(frames_dir, cfg.get("sprite") or "reach_m2/00.png", who)
    if sprite_path is None:
        sys.exit(f"cover.json: sprite not found - {note}")
    if note:
        print("[提醒]", note)
    an = C.load_json(frames_dir / "anims.json", {}) or {}
    geom = {}                                   # her frame size and sole row (anims.json frame_w / frame_h / anchor.foot_y)
    if an.get("frame_w") and an.get("frame_h"):
        geom["frame"] = [an["frame_w"], an["frame_h"]]
    if (an.get("anchor") or {}).get("foot_y") is not None:
        geom["footRow"] = an["anchor"]["foot_y"]
    return pr, who, sprite_path, geom


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s or "").replace("&nbsp;", " ").strip()


def board_cover(args, ep, series, ep_json, out, cfg):
    """the whiteboard cover (cover.board.html): writes cover.html, _handdata.js, _cover_data.json -> data path or None"""
    if not cfg.get("sub") and cfg.get("subHTML"):         # a receipt cover.json being redone as a whiteboard cover
        cfg["sub"] = strip_tags(cfg["subHTML"])
    pr, who, sprite_path, geom = presenter_sprite(series, ep_json, cfg)
    eng = ep / "制作" / "engine"                           # the hand that wrote this episode's video
    if not ((eng / "hand.js").is_file() and (eng / "hand_glyphs.py").is_file()):
        print("[提醒] 这一期的 制作/engine 里没有 hand.js / hand_glyphs.py（引擎是白板版之前复制的？"
              "new_episode.py --update-engine 更新），封面先用 assets/engine-template 的")
        eng = ENGINE_T
    if cfg.get("t1"):
        hg = load_module(eng / "hand_glyphs.py", "hand_glyphs_cover")
        hd = hg.build_hand_js([cfg.get(k, "") for k in ("t1", "t2", "sub")], out / "_handdata.js", series / "素材" / "手写")
        if hd["missing"]:
            sys.exit(f"cover.json: 这些字没有笔画数据，换个写法：{''.join(hd['missing'])}")
    html = out / "cover.html"
    page = BOARD_TEMPLATE.read_text(encoding="utf-8")
    page = (page.replace("{{FONTS_CSS}}", rel(series / "素材" / "字体" / "fonts.css", out))
                .replace("{{SPRITE}}", rel(sprite_path, out))
                .replace("{{HANDDATA_JS}}", "_handdata.js")
                .replace("{{HAND_JS}}", rel(eng / "hand.js", out)))
    html.write_text(page, encoding="utf-8")
    skip = ("sprite", "subHTML", "bg_file", "bg", "plain", "style")
    data = merge_cover(geom, {k: v for k, v in cfg.items() if k not in skip})
    data["number"] = ep_json["number"]
    print(f"白板版封面：{who}（{pr['id']}）sprite {rel(sprite_path, series / '素材')}；手写 {rel(eng / 'hand.js', series)}")
    data_path = out / "_cover_data.json"
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.html_only or not cfg.get("t1"):
        print("cover.json needs t1 / t2 / sub before rendering" if not cfg.get("t1") else f"wrote {html}")
        return None
    return data_path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dir")
    ap.add_argument("--series", default=str(DEFAULT_SERIES))
    ap.add_argument("--html-only", action="store_true", help="write cover.html / cover.json and stop")
    args = ap.parse_args()
    ep = Path(args.episode_dir).resolve()
    series = Path(args.series).resolve()
    ep_json = json.loads((ep / "episode.json").read_text(encoding="utf-8"))
    out = ep / "封面"
    out.mkdir(exist_ok=True)

    cfg_path = out / "cover.json"
    if not cfg_path.exists():
        if ep_json.get("style") == "board":
            skel = {"t1": "", "t2": "", "sub": "", "hl": "", "sprite": "reach_m2/00.png"}
        else:
            bgs = list((ep_json.get("backgrounds") or {}).values())
            skel = {
                "t1": "", "t2": "", "subHTML": "",
                "bg_file": bgs[0] if bgs else "",
                "sprite": "reach_m2/00.png",
                "bg": {"scale": 1.0, "fx": 0.5, "fy": 0.5, "opacity": 0.36, "blur": 8},
            }
        cfg_path.write_text(json.dumps(skel, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote skeleton {cfg_path}")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    html = out / "cover.html"
    if (cfg.get("style") or ep_json.get("style")) == "board":
        data_path = board_cover(args, ep, series, ep_json, out, cfg)
        if data_path:
            export_cover(series, ep, ep_json, out, html, data_path)
        return

    bg_file = "" if cfg.get("plain") else (cfg.get("bg_file") or "")   # "plain": "#FFFFFF" = solid page, no photo
    bg_path = series / "素材" / "背景图库" / bg_file
    if not bg_file and not cfg.get("plain"):
        sys.exit("cover.json: bg_file is empty - pick one from 素材/背景图库 (or set \"plain\": \"#FFFFFF\")")
    if bg_file and not bg_path.is_file():
        sys.exit(f"cover.json: bg_file not found: {bg_path}")
    pr, who, sprite_path, geom = presenter_sprite(series, ep_json, cfg)

    page = TEMPLATE.read_text(encoding="utf-8")
    page = (page.replace("{{FONTS_CSS}}", rel(series / "素材" / "字体" / "fonts.css", out))
                .replace("{{BG}}", rel(bg_path, out) if bg_file else "")
                .replace("{{SPRITE}}", rel(sprite_path, out)))
    html.write_text(page, encoding="utf-8")
    preset = (C.PRESENTERS.get(pr["id"]) or {}).get("cover") or {}
    ep_cover = (ep_json.get("presenter") or {}).get("cover") if isinstance(ep_json.get("presenter"), dict) else None
    data = merge_cover(geom, preset, ep_cover, {k: v for k, v in cfg.items() if k not in ("bg_file", "sprite", "style")})
    data["number"] = ep_json["number"]
    print(f"{who}（{pr['id']}）sprite {rel(sprite_path, series / '素材')}"
          + (f"；讲解员封面参数 {json.dumps(preset, ensure_ascii=False)}" if preset else ""))
    data_path = out / "_cover_data.json"
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.html_only or not cfg.get("t1"):
        print("cover.json needs t1/t2/subHTML before rendering" if not cfg.get("t1") else f"wrote {html}")
        return
    export_cover(series, ep, ep_json, out, html, data_path)


def export_cover(series, ep, ep_json, out, html, data_path):
    """render the page once (1920x1080) -> 16:9, the 4:3 centre crop and the feed-size preview sheet"""
    tmp = out / "_render"
    tmp.mkdir(exist_ok=True)
    subprocess.run([sys.executable, str(series / "片头片尾" / "render.py"), str(html), "--data", str(data_path),
                    "--stills", "0", "--stills-dir", str(tmp)], check=True)
    src = Image.open(tmp / "still_0.00.png").convert("RGB")
    assert src.size == (1920, 1080), src.size
    p169, p43, pprev = out / "封面_16x9_1920x1080.png", out / "封面_4x3_1440x1080.png", out / "封面_预览.png"
    src.save(p169, optimize=True)
    crop = src.crop((240, 0, 1680, 1080))
    crop.save(p43, optimize=True)
    preview_board(series, src, crop, pprev, video_length_label(ep, ep_json))
    shutil.move(str(tmp / "still_0.00.png"), str(tmp / "last_still.png"))
    for p in (p169, p43, pprev):
        print(p.name, Image.open(p).size, f"{p.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
