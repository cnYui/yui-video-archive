"""生成 engine/assets.js + engine/assets.css：页面要用的素材清单（window.__ASSETS__）和字体样式。

为什么要有它：引擎从 file:// 打开，Chromium 不许 fetch 本地 JSON；页面里一张图加载失败会在控制台报错，
render.py 就会以退出码 2 结束。所以页面自己不探测磁盘：这里先检查素材在不在、把 anims.json 内联进 assets.js，
再用 os.path.relpath 算出「引擎目录 → 素材」的相对路径（期目录在 SERIES 下、测试目录在 _skilltest 下层级都不同，
所以绝不写死 ../../../）。

在 制作/ 下运行（素材、episode.json、背景图有变化就重跑）：
    python engine/sync_assets.py
    python engine/sync_assets.py --series D:/大疆/AI科普 --episode ../episode.json --timeline timeline.json
    python engine/sync_assets.py --allow-missing        # 草稿：缺素材只警告（页面用占位图），不报错
    python engine/sync_assets.py --sprites-extra D:/大疆/AI科普/_skilltest/actions_v2/frames_preview   # 叠加待确认的新帧

找素材根（SERIES，下面有 素材/）：--series > 环境变量 YUANLAI_SERIES > 从引擎目录往上找第一个含 素材/角色/动作帧/anims.json 的目录。
找 episode.json：--episode > 引擎目录/../../episode.json > timeline.json 里的 episode 字段。
找 timeline.json：--timeline > 引擎目录/../timeline.json（用来知道有哪些场景、用了哪些动作）。
叠加动作帧目录（用户确认前的新帧，例如 _skilltest/actions_v2/frames_preview）：--sprites-extra DIR（可多次）>
  环境变量 YUANLAI_SPRITES_EXTRA（多个用 ; 分隔）> episode.json 的 "sprites_extra"（字符串或列表，相对路径按 SERIES 算）。
  目录里要有自己的 anims.json：同名条目覆盖 动作帧/ 的，新条目追加；顶层 actions（动作注册表）、patch_rects 也按同样规则合并。
  帧路径改写成相对 动作帧/ 的路径，所以页面只有一个 spriteBase。用户确认、帧追加进 动作帧/ 以后，把 sprites_extra 删掉。

写出：
  assets.js   window.__ASSETS__ = {anims, spriteBase, bg{文件名: 相对路径}, bgList[], bgScenes{场景: 文件名},
                                   bgAlpha, bgBlur, episode{...}, fontsDir, spriteDirs[]}
  assets.css  @import 素材/字体/fonts.css + 'KuaiLe Han'（ZCOOL KuaiLe 只取中文和数字，拉丁字母回落 Noto Sans SC）
缺素材（字体、角色帧、episode.json 里点名的背景图、时间轴 actions 要用的动作帧）：列出清单并以退出码 1 结束。
动作 v2（时间轴有 episode）：动作注册表里的过渡帧 / 视线 / 特效缺了只警告（引擎照样播，只是少了那一层）；
自动层开着但缺它要的帧时也只警告（引擎关掉那个通道），不报错。
"""
import argparse
import json
import os
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent
REQUIRED_ANIMS = ["idle_m0", "idle_m1", "idle_m2"]   # AI每日日报: 大肥鱼只有待机 / 口型 / 表情，没有 reach、walk（台本里不用抬手、走动）
REQUIRED_FONTS = ["fonts.css", "NotoSansSC.ttf", "JetBrainsMono.ttf", "ZCOOLKuaiLe.ttf"]
BG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_ALPHA, DEFAULT_BLUR = 0.22, 10
# fallback action registry when anims.json has no top-level "actions" (keep in step with core.js ACTION_DEFAULTS)
ACTION_DEFAULTS = {
    "reach": {"type": "body", "frames": "reach", "via": "palm", "look": "look_r"},
    "chest": {"type": "body", "frames": "chest", "via": "chest_mid"},
    "palm": {"type": "body", "frames": "palm"},
    "palm_r": {"type": "body", "frames": "palm", "look": "look_r"},
    "hold": {"type": "body", "frames": "hold", "via": "chest_mid"},
    "point": {"type": "body", "frames": "point", "via": "palm", "look": "look_r"},
    "wave": {"type": "body", "frames": ["wave_a", "wave_b"], "via": "reach"},
    "count1": {"type": "body", "frames": "count1", "via": "reach", "fx": "fx_digit1"},
    "count2": {"type": "body", "frames": "count2", "via": "reach", "fx": "fx_digit2"},
    "count3": {"type": "body", "frames": "count3", "via": "reach", "fx": "fx_digit3"},
    "finger_up": {"type": "body", "frames": "count1", "via": "reach", "fx": "fx_exclaim"},
    "think": {"type": "body", "frames": "think", "via": "chest", "look": "look_ur", "fx": "fx_think"},
    "shrug": {"type": "body", "frames": "shrug"},
    "thumb": {"type": "body", "frames": "thumb", "via": "reach", "fx": "fx_glint"},
    "hip": {"type": "body", "frames": "hip", "via": "hip_mid"},
    "ear": {"type": "body", "frames": "ear", "via": "reach", "look": "look_r", "fx": "fx_listen"},
    "nod": {"type": "head", "steps": [["head_nod", 220]], "eyes": "half"},
    "nod2": {"type": "head", "steps": [["head_nod", 180], [None, 120], ["head_nod", 180]], "eyes": "half"},
    "shake": {"type": "head", "steps": [["head_l", 150], ["head_r", 150], ["head_l", 150]]},
    "turnout": {"type": "legs", "frames": "legs_turnout"},
}
AUTO_NEED = {  # auto-layer channel -> breathing sets / anims it needs (core.js turns the channel off without them)
    "gesture": ["chest_m*", "palm_m*", "hold_m*"],
    "nod": ["head_nod_m*"],
    "look": ["idle_look_r_m*"],
    "weight": ["legs_turnout"],
}


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


def expand(keys):
    """'chest_m*' -> chest_m0..2"""
    out = []
    for k in keys:
        out += [k[:-1] + str(m) for m in range(3)] if k.endswith("_m*") else [k]
    return out


def breath(base):
    return [f"{base}_m{m}" for m in range(3)]


def action_anims(timeline, registry):
    """anim names the timeline's actions need -> ({anim: {where}}, {optional anim: {where}}).

    v1 timeline (no episode): expr -> idle_<name>_m0..2, pose -> pose_<name>, anim -> <name>, body -> <name>_m0..2.
    v2 (episode present): body / head frames come from the action registry; its transition (via), gaze (look) and fx
    frames are optional (the engine plays the action without that layer)."""
    need, opt = {}, {}
    v2 = bool((timeline or {}).get("episode"))
    for item in (timeline or {}).get("segments", []) + (timeline or {}).get("gaps", []):
        where = item.get("id") or f"gap@{item.get('start')}"
        for a in item.get("actions") or []:
            t, n = a.get("type"), a.get("name")
            req, extra = [], []
            if t == "expr":
                req = breath(f"idle_{n}")
            elif t == "pose":
                req = [f"pose_{n}"]
            elif t in ("anim", "fx"):
                req = [n]
            elif t == "body" and not v2:
                req = breath(n)
            elif t == "body":
                r = registry.get(n) or {"frames": n}
                fr = r.get("frames") or n
                for b in (fr if isinstance(fr, list) else [fr]):
                    req += breath(b)
                if r.get("via"):
                    extra += breath(r["via"])
                if r.get("look"):
                    extra += breath(f"idle_{r['look']}")
                if r.get("fx"):
                    extra.append(r["fx"])
            elif t == "head":
                r = registry.get(n) or {"steps": [[n, 0]]}
                for f, _ms in r.get("steps") or []:
                    if f:
                        req += breath(f)
                if r.get("eyes"):
                    extra += breath(f"idle_{r['eyes']}")
            for k in req:
                need.setdefault(k, set()).add(where)
            for k in extra:
                opt.setdefault(k, set()).add(where)
    return need, opt


def sprite_extra_dirs(args, episode, series):
    raw = list(args.sprites_extra or [])
    if not raw and os.environ.get("YUANLAI_SPRITES_EXTRA"):
        raw = [x for x in os.environ["YUANLAI_SPRITES_EXTRA"].split(";") if x.strip()]
    if not raw and episode.get("sprites_extra"):
        v = episode["sprites_extra"]
        raw = [v] if isinstance(v, str) else list(v)
    out = []
    for x in raw:
        p = Path(str(x))
        out.append((p if p.is_absolute() else series / p).resolve())
    return out


def merge_sprites(base_dir, extra_dirs, errors, warns):
    """anims.json of 动作帧/ plus the overlays -> (merged anims json, {anim: dir its frames live in})."""
    anims, src = None, {}
    ap_json = base_dir / "anims.json"
    if not ap_json.exists():
        errors.append(f"角色帧清单不存在：{ap_json}")
        return None, src
    try:
        anims = load_json(ap_json)
    except Exception as e:  # noqa: BLE001
        errors.append(f"anims.json 读不了：{e}")
        return None, src
    anims.setdefault("anims", {})
    for k in anims["anims"]:
        src[k] = base_dir
    for d in extra_dirs:
        j = d / "anims.json"
        if not j.exists():
            warns.append(f"叠加动作帧目录没有 anims.json，跳过：{d}")
            continue
        try:
            extra = load_json(j)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{j} 读不了：{e}")
            continue
        n_new = n_over = 0
        for k, a in (extra.get("anims") or {}).items():
            a = dict(a)
            if k in anims["anims"]:
                n_over += 1
            else:
                n_new += 1
            # frame paths relative to 动作帧/, so the page keeps one spriteBase
            a["frames"] = [os.path.relpath(str(d / f), str(base_dir)).replace("\\", "/") for f in a.get("frames") or []]
            anims["anims"][k] = a
            src[k] = d
        for key in ("actions", "patch_rects"):
            if isinstance(extra.get(key), dict):
                anims[key] = dict(anims.get(key) or {}, **extra[key])
        if extra.get("version") is not None:
            anims["version"] = max(extra["version"], anims.get("version") or 1)
        warns.append(f"叠加动作帧 {d}：新增 {n_new} 条、覆盖 {n_over} 条（用户确认前的样片专用）")
    return anims, src


def main():
    ap = argparse.ArgumentParser(description="write engine/assets.js + assets.css")
    ap.add_argument("--series", help="series root (the folder that contains 素材/)")
    ap.add_argument("--episode", help="episode.json (default: <engine>/../../episode.json)")
    ap.add_argument("--timeline", help="timeline.json (default: <engine>/../timeline.json)")
    ap.add_argument("--sprites-extra", action="append", metavar="DIR",
                    help="叠加的动作帧目录（含 anims.json），例如 _skilltest/actions_v2/frames_preview；可多次")
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
    extra_dirs = sprite_extra_dirs(args, episode, series)
    anims, src_dir = merge_sprites(sprites, extra_dirs, errors, warns)
    registry = dict(ACTION_DEFAULTS, **((anims or {}).get("actions") or {}))
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
        need, opt = action_anims(timeline, registry)
        for k, used in sorted(need.items()):
            if k not in table:
                errors.append(f"时间轴 actions 要用的动作帧 {k} 不在 anims.json 里（用在 {sorted(used)[:4]}）："
                              f"先跑 素材/角色/动作生成器/make_sprites.py，或用 --sprites-extra 叠加待确认的帧")
        lost_opt = sorted(k for k in opt if k not in table)
        if lost_opt:
            warns.append(f"动作的过渡帧 / 视线 / 特效缺帧（引擎照样播，只少这一层）：{lost_opt[:8]}{' …' if len(lost_opt) > 8 else ''}")
        tep = (timeline or {}).get("episode")
        if tep and tep.get("auto_gestures", True) is not False:
            ag = tep.get("auto_gestures")
            chans = {"gesture": True, "nod": True, "look": True, "weight": False}
            if isinstance(ag, dict):
                for k in chans:
                    if k in ag:
                        chans[k] = bool(ag[k]) and ag[k] != 0
            for ch, on in chans.items():
                lost = [k for k in expand(AUTO_NEED[ch]) if k not in table]
                if on and lost:
                    warns.append(f"自动层「{ch}」通道缺帧 {lost[:6]}：引擎会关掉这个通道（帧追加进 动作帧/ 或用 --sprites-extra 后恢复）")

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
                                        "bg_alpha", "bg_blur", "terms", "auto_gestures") if k in episode}
    manifest = {
        "anims": anims,
        "spriteBase": rel(sprites) + "/",
        "spriteDirs": [rel(sprites)] + [rel(d) for d in extra_dirs],
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
    print(f"sprites: {n_anims} anims <- {rel(sprites)}/" + "".join(f" + {rel(d)}/" for d in extra_dirs))
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
