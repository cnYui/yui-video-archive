"""Cover for one episode of 《AI每日日报》, filled in from episode.json (no manual cover.json).

    python make_cover.py <期目录>

Writes <期目录>/封面/: 封面_16x9_1920x1080.png, 封面_4x3_1440x1080.png (centre crop x 240..1680),
封面_预览.png (both + feed-size thumbnails, drawn by the 《原LAI如此》 make_cover helpers), cover.html, _cover_data.json.
Layout: big date, gold hook line, the first 3 headlines as cards (+ "…等 N 件事"), 大肥鱼 (happy frame) on the right.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
SKILL = Path(__file__).resolve().parent.parent
SERIES = SKILL.parent.parent
TEMPLATE = SKILL / "assets" / "cover-template" / "cover.daily.html"
YUANLAI_SCRIPTS = Path(r"D:/大疆/AI科普/skill/yuanlai-ruci-episode/scripts")
BG = "01_深海气泡.png"
SPRITE = "sprites/idle_happy_m0/00.png"         # under 素材/角色/动作帧 (= 大肥鱼像素素材包/素材)


def rel(target, start):
    return Path(os.path.relpath(target, start)).as_posix()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dir")
    args = ap.parse_args()
    ep = Path(args.episode_dir).resolve()
    ep_json = json.loads((ep / "episode.json").read_text(encoding="utf-8"))
    out = ep / "封面"
    out.mkdir(exist_ok=True)
    bg = SERIES / "素材" / "背景图库" / BG
    sprite = SERIES / "素材" / "角色" / "动作帧" / SPRITE
    for p in (bg, sprite, TEMPLATE):
        if not p.is_file():
            sys.exit(f"缺少 {p}")
    heads = [n["headline"] for n in ep_json.get("news", [])]
    data = {"date_label": ep_json["date_label"], "weekday": ep_json.get("weekday", ""), "hook": "鲸鱼娘带你看看 AI 圈",
            "headlines": heads[:3], "more": f"…等 {len(heads)} 件事" if len(heads) > 3 else ""}
    html = out / "cover.html"
    page = TEMPLATE.read_text(encoding="utf-8")
    page = (page.replace("{{FONTS_CSS}}", rel(SERIES / "素材" / "字体" / "fonts.css", out))
                .replace("{{BG}}", rel(bg, out)).replace("{{SPRITE}}", rel(sprite, out)))
    html.write_text(page, encoding="utf-8")
    data_path = out / "_cover_data.json"
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    tmp = out / "_render"
    tmp.mkdir(exist_ok=True)
    subprocess.run([sys.executable, str(SERIES / "片头片尾" / "render.py"), str(html), "--data", str(data_path),
                    "--stills", "0", "--stills-dir", str(tmp)], check=True)
    src = Image.open(tmp / "still_0.00.png").convert("RGB")
    assert src.size == (1920, 1080), src.size
    p169, p43, pprev = out / "封面_16x9_1920x1080.png", out / "封面_4x3_1440x1080.png", out / "封面_预览.png"
    src.save(p169, optimize=True)
    crop = src.crop((240, 0, 1680, 1080))
    crop.save(p43, optimize=True)
    sys.path.insert(0, str(YUANLAI_SCRIPTS))
    import make_cover as yl                                   # 《原LAI如此》 helpers: feed thumbnails + preview board
    yl.preview_board(SERIES, src, crop, pprev, yl.video_length_label(ep, ep_json).replace("06:00", "03:30"))
    shutil.move(str(tmp / "still_0.00.png"), str(tmp / "last_still.png"))
    for p in (p169, p43, pprev):
        print(p.name, Image.open(p).size, f"{p.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
