"""生成 engine/assets.js + engine/assets.css：页面要用的素材清单（window.__ASSETS__）和字体样式。

为什么要有它：引擎从 file:// 打开，Chromium 不许 fetch 本地 JSON；页面里一张图加载失败会在控制台报错，
render.py 就会以退出码 2 结束。所以页面自己不探测磁盘：这里先检查素材在不在、把 anims.json 内联进 assets.js，
再用 os.path.relpath 算出「引擎目录 → 素材」的相对路径（期目录在 SERIES 下、测试目录在 _skilltest 下层级都不同，
所以绝不写死 ../../../）。

在 制作/ 下运行（素材、episode.json、背景图有变化就重跑）：
    python engine/sync_assets.py
    python engine/sync_assets.py --series D:/大疆/AI科普 --episode ../episode.json --timeline timeline.json
    python engine/sync_assets.py --allow-missing        # 草稿：缺素材只警告（页面用占位图），不报错

找素材根（SERIES，下面有 素材/）：--series > 环境变量 YUANLAI_SERIES > 从引擎目录往上找第一个含 素材/角色/动作帧/anims.json 的目录。
找 episode.json：--episode > 引擎目录/../../episode.json > timeline.json 里的 episode 字段。
找 timeline.json：--timeline > 引擎目录/../timeline.json（用来知道有哪些场景、用了哪些动作）。

写出：
  assets.js   window.__ASSETS__ = {anims, spriteBase, bg{文件名: 相对路径}, bgList[], bgScenes{场景: 文件名},
                                   bgAlpha, bgBlur, episode{...}, fontsDir}
  assets.css  @import 素材/字体/fonts.css + 'KuaiLe Han'（ZCOOL KuaiLe 只取中文和数字，拉丁字母回落 Noto Sans SC）
缺素材（字体、角色帧、episode.json 里点名的背景图、时间轴 actions 要用的动作帧）：列出清单并以退出码 1 结束。
"""
import argparse
import json
import os
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent
REQUIRED_ANIMS = ["idle_m0", "idle_m1", "idle_m2", "reach_m0", "reach_m1", "reach_m2", "walk"]
REQUIRED_FONTS = ["fonts.css", "NotoSansSC.ttf", "JetBrainsMono.ttf", "ZCOOLKuaiLe.ttf"]
BG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_ALPHA, DEFAULT_BLUR = 0.22, 10


def rel(p: Path) -> str:
    """path of p relative to the engine dir, with forward slashes (for URLs in the page)"""
    return os.path.relpath(str(p), str(ENGINE)).replace("\\", "/")


def find_series(arg):
    if arg:
        return Path(arg).resolve()
    if os.environ.get("YUANLAI_SERIES"):
        return Path(os.environ["YUANLAI_SERIES"]).resolve()
    for d in [ENGINE, *ENGINE.parents]:
        if (d / "素材" / "角色" / "动作帧" / "anims.json").exists():
            return d
    return None


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def action_anims(timeline):
    """anim names the timeline's actions need (expr -> idle_<name>_m0..2, pose -> pose_<name>, anim -> <name>)"""
    need = {}
    for item in (timeline or {}).get("segments", []) + (timeline or {}).get("gaps", []):
        for a in item.get("actions") or []:
            t, n = a.get("type"), a.get("name")
            names = {"body": [f"{n}_m{m}" for m in range(3)], "expr": [f"idle_{n}_m{m}" for m in range(3)],
                     "pose": [f"pose_{n}"], "anim": [n]}.get(t, [])
            for k in names:
                need.setdefault(k, set()).add(item.get("id") or f"gap@{item.get('start')}")
    return need


def main():
    ap = argparse.ArgumentParser(description="write engine/assets.js + assets.css")
    ap.add_argument("--series", help="series root (the folder that contains 素材/)")
    ap.add_argument("--episode", help="episode.json (default: <engine>/../../episode.json)")
    ap.add_argument("--timeline", help="timeline.json (default: <engine>/../timeline.json)")
    ap.add_argument("--allow-missing", action="store_true", help="draft mode: warn instead of failing on missing assets")
    args = ap.parse_args()

    errors, warns = [], []
    series = find_series(args.series)
    if series is None or not (series / "素材").is_dir():
        sys.exit("找不到素材根目录（含 素材/ 的 SERIES）：用 --series 指定，或设环境变量 YUANLAI_SERIES")
    assets = series / "素材"
    sprites = assets / "角色" / "动作帧"
    fonts = assets / "字体"
    gallery = assets / "背景图库"

    # ---- timeline + episode ----------------------------------------------------------------------
    tl_path = Path(args.timeline).resolve() if args.timeline else ENGINE.parent / "timeline.json"
    timeline = load_json(tl_path) if tl_path.exists() else None
    if timeline is None:
        warns.append(f"timeline.json 不存在（{tl_path}）：按 episode.json 的 chapters 分配背景，不检查动作帧")
    ep_path = Path(args.episode).resolve() if args.episode else ENGINE.parent.parent / "episode.json"
    if ep_path.exists():
        episode = load_json(ep_path)
        ep_src = str(ep_path)
    elif timeline and timeline.get("episode"):
        episode = dict(timeline["episode"])
        ep_src = f"{tl_path} 的 episode 字段"
    else:
        episode = {}
        ep_src = "（无）"
        warns.append("没有 episode.json，也没有 timeline.episode：徽标没有期号、没有本期目录、背景按图库顺序轮换")

    # ---- sprites ---------------------------------------------------------------------------------
    anims = None
    ap_json = sprites / "anims.json"
    if not ap_json.exists():
        errors.append(f"角色帧清单不存在：{ap_json}")
    else:
        try:
            anims = load_json(ap_json)
        except Exception as e:  # noqa: BLE001
            errors.append(f"anims.json 读不了：{e}")
    if anims is not None:
        table = anims.get("anims") or {}
        missing = [a for a in REQUIRED_ANIMS if a not in table]
        if missing:
            errors.append(f"anims.json 缺少必需动作 {missing}")
        for name, a in table.items():
            frames = a.get("frames") or []
            durs = a.get("durations") or []
            if not frames or len(frames) != len(durs):
                errors.append(f"动作 {name}：frames / durations 数量不一致")
            lost = [f for f in frames if not (sprites / f).exists()]
            if lost:
                errors.append(f"动作 {name}：缺帧文件 {lost[:4]}{' …' if len(lost) > 4 else ''}")
        for k, used in sorted(action_anims(timeline).items()):
            if k not in table:
                errors.append(f"时间轴 actions 要用的动作帧 {k} 不在 anims.json 里（用在 {sorted(used)[:4]}）："
                              f"先跑 素材/角色/动作生成器/make_sprites.py")

    # ---- fonts -----------------------------------------------------------------------------------
    for f in REQUIRED_FONTS:
        if not (fonts / f).exists():
            errors.append(f"字体文件不存在：{fonts / f}")

    # ---- backgrounds -----------------------------------------------------------------------------
    gal = sorted(p.name for p in gallery.iterdir() if p.suffix.lower() in BG_EXT) if gallery.is_dir() else []
    if not gal:
        warns.append(f"背景图库是空的：{gallery}（页面用深色渐变占位）")
    wanted = {}
    for sid, v in (episode.get("backgrounds") or {}).items():
        name = Path(str(v).replace("\\", "/")).name
        if not (gallery / name).exists():
            errors.append(f"episode.json backgrounds.{sid} = {v}：{gallery} 里没有这张图")
        else:
            wanted[sid] = name
    scene_ids = [s["id"] for s in timeline["scenes"]] if timeline else list((episode.get("chapters") or {}).keys())
    bg_scenes = {}
    for i, sid in enumerate(scene_ids):
        if sid in wanted:
            bg_scenes[sid] = wanted[sid]
        elif gal:
            bg_scenes[sid] = gal[i % len(gal)]   # 没写的章节按背景图库顺序轮换
    bg_map = {name: rel(gallery / name) for name in gal}

    # ---- write -----------------------------------------------------------------------------------
    if errors and not args.allow_missing:
        print("素材检查没通过：\n  " + "\n  ".join(errors), file=sys.stderr)
        if warns:
            print("另外：\n  " + "\n  ".join(warns), file=sys.stderr)
        sys.exit(1)

    ep_small = {k: episode[k] for k in ("number", "title", "question_scene", "questions", "chapters", "backgrounds",
                                        "bg_alpha", "bg_blur", "terms") if k in episode}
    manifest = {
        "anims": anims,
        "spriteBase": rel(sprites) + "/",
        "bg": bg_map,
        "bgList": gal,
        "bgScenes": bg_scenes,
        "bgAlpha": float(episode.get("bg_alpha", DEFAULT_ALPHA)),
        "bgBlur": float(episode.get("bg_blur", DEFAULT_BLUR)),
        "episode": ep_small,
        "fontsDir": rel(fonts) + "/",
    }
    (ENGINE / "assets.js").write_text(
        "// generated by engine/sync_assets.py — do not edit by hand\n"
        f"window.__ASSETS__ = {json.dumps(manifest, ensure_ascii=False)};\n", encoding="utf-8")
    fr = rel(fonts)
    (ENGINE / "assets.css").write_text(
        "/* generated by engine/sync_assets.py — do not edit by hand. Fonts: 素材/字体 (SIL OFL 1.1). */\n"
        f"@import url('{fr}/fonts.css');\n"
        "/* same OFL file as ZCOOL KuaiLe, limited to CJK + digits so Latin letters fall back to Noto Sans SC (its \"K\" reads as \"k\") */\n"
        f"@font-face {{ font-family: 'KuaiLe Han'; src: url('{fr}/ZCOOLKuaiLe.ttf') format('truetype'); font-display: block;\n"
        "  unicode-range: U+0030-003A, U+2013, U+2014, U+201C-201D, U+2E80-9FFF, U+3000-303F, U+FF00-FFEF; }\n",
        encoding="utf-8")

    n_anims = len((anims or {}).get("anims") or {})
    print(f"series : {series}")
    print(f"episode: {ep_src}  (#{episode.get('number', '?')}, {len(episode.get('questions') or [])} questions)")
    print(f"sprites: {n_anims} anims <- {rel(sprites)}/")
    print(f"bg     : {len(gal)} in gallery; per scene: " + ", ".join(f"{k}={v}" for k, v in bg_scenes.items()))
    print(f"bg look: alpha {manifest['bgAlpha']}, blur {manifest['bgBlur']} px")
    print(f"fonts  : {fr}/")
    for w in warns:
        print("WARN   : " + w)
    for e in errors:
        print("MISSING: " + e)
    print(f"-> {ENGINE / 'assets.js'}\n-> {ENGINE / 'assets.css'}")


if __name__ == "__main__":
    main()
