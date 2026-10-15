"""生成 engine/assets.js + engine/assets.css：页面要用的素材清单（window.__ASSETS__）和字体样式。

为什么要有它：引擎从 file:// 打开，Chromium 不许 fetch 本地 JSON；页面里一张图加载失败会在控制台报错，
render.py 就会以退出码 2 结束。所以页面自己不探测磁盘：这里先检查素材在不在、把 anims.json 内联进 assets.js，
再用 os.path.relpath 算出「引擎目录 → 素材」的相对路径（期目录在 SERIES 下、测试目录在 _skilltest 下层级都不同，
所以绝不写死 ../../../）。

在 制作/ 下运行（素材、episode.json、背景图有变化就重跑）：
    python engine/sync_assets.py
    python engine/sync_assets.py --series D:/大疆/AI科普 --episode ../episode.json --timeline timeline.json
    python engine/sync_assets.py --allow-missing        # 草稿：缺的动作帧 / 背景只警告（动作退回待机），不报错
    python engine/sync_assets.py --frames 角色/大肥鱼像素素材包/素材 --allow-missing   # 讲解员的帧目录还没画好：临时换一个
    python engine/sync_assets.py --sprites-extra D:/大疆/AI科普/_skilltest/actions_v2/frames_preview   # 叠加待确认的新帧

找素材根（SERIES，下面有 素材/）：--series > 环境变量 YUANLAI_SERIES > 从引擎目录往上找第一个含 素材/字体/fonts.css
  （或 素材/角色/动作帧/anims.json）的目录。
找 episode.json：--episode > 引擎目录/../../episode.json > timeline.json 里的 episode 字段。
找 timeline.json：--timeline > 引擎目录/../timeline.json（用来知道有哪些场景、用了哪些动作）。
讲解员（每期一个）：episode.json 的 "presenter"（对象，或只写 id）> timeline.json 的 episode.presenter > 默认 ryo（山田凉）。
  角色帧目录 = SERIES/素材/<presenter.frames>（anims.json + 帧；山田凉是 角色/动作帧，鲸鱼娘是 角色/大肥鱼像素素材包/素材/动作帧）。
  --frames DIR（相对 素材/，也可以写绝对路径）临时顶替 presenter.frames，不改 episode.json，也不用做 episode.json 副本
  （别把副本放进会话临时目录：Windows 下超过 260 个字符的路径 Python 打不开）。
  这个 anims.json 整份内联进 assets.js：帧清单、动作注册表 actions、patch_rects、anchor、frame_w/h，以及可选的角色几何
  （stage、head_offsets、fx_offset，见 pipeline-contract.md §5），core.js 按它画这个讲解员。
  帧目录不存在、里面没有 anims.json、或者没有待机帧 idle_m0..2：直接报错退出（加 --allow-missing 也一样）——没有帧就
  画不出讲解员，页面只会剩一个占位小人；报错里会写出可以临时用的帧目录（--frames）。
叠加动作帧目录（用户确认前的新帧，例如 _skilltest/actions_v2/frames_preview）：--sprites-extra DIR（可多次）>
  环境变量 YUANLAI_SPRITES_EXTRA（多个用 ; 分隔）> episode.json 的 "sprites_extra"（字符串或列表，相对路径按 SERIES 算）。
  目录里要有自己的 anims.json：同名条目覆盖讲解员帧目录里的，新条目追加；顶层 actions（动作注册表）、patch_rects 也按同样规则合并。
  帧路径改写成相对讲解员帧目录的路径，所以页面只有一个 spriteBase。用户确认、帧追加进帧目录以后，把 sprites_extra 删掉。
  叠加目录必须是同一个讲解员的帧（不会检查是谁画的）。

画布（视频尺寸）：引擎和 render.py 只看 timeline.json 的 episode.canvas（没有 = 1920×1080），这里只打印出来；
  episode.json 的 canvas 和 timeline 里的不一样（改了 episode.json 还没重跑 build_timeline）时提醒。
白板版（2026-09-28，episode.json "style": "board"）：另写 handdata.js = 本期可能手写的每个字的笔画（hand_glyphs.py，
  数据在 SERIES/素材/手写，是指向 AI日报/素材/手写 的目录联接）。收字范围：scenes.js、board.js 的源文件，时间轴和 episode.json
  里的全部文字（台词、画面说明、章节名、疑问……），多收几个字没关系。缺笔画的字列出来（hand.js 会留空）。不是白板版的期
  写 window.__HAND__ = null;（index.html 永远能加载到这个文件）。
背景色和版面开关（2026-09-28）：episode.json 的 "bg_color": "#RRGGBB" = 纯色背景、视频不用背景图（浅色时引擎换浅色主题；
  new_episode.py 默认写 "#FFFFFF"），"layout": "center" = 内容以画面中线居中。引擎先看 timeline.json 的 episode（build_timeline
  整份抄过去），再看这里抄进 assets.js 的副本；两边不一样（改了 episode.json 还没重跑 build_timeline）时提醒，写法不对也提醒。

写出：
  assets.js   window.__ASSETS__ = {anims, spriteBase, presenter{id, name, frames}, bg{文件名: 相对路径}, bgList[],
                                   bgScenes{场景: 文件名}, bgAlpha, bgBlur, episode{...}, fontsDir, spriteDirs[]}
  assets.css  @import 素材/字体/fonts.css + 'KuaiLe Han'（ZCOOL KuaiLe 只取中文和数字，拉丁字母回落 Noto Sans SC）
缺素材（字体、讲解员的角色帧、episode.json 里点名的背景图、时间轴 actions 要用的动作帧）：列出清单（写明是哪个讲解员缺哪个
key）并以退出码 1 结束。
动作 v2（时间轴有 episode）：动作注册表里的过渡帧 / 视线 / 特效缺了只警告（引擎照样播，只是少了那一层）；
自动层开着但缺它要的帧时也只警告（引擎关掉那个通道），不报错。
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent
# presenters by id (== scripts/epcommon.py PRESENTERS: only name + frames; used when episode.json writes just the id or
# leaves out a field). No "presenter" at all = ryo (episode 1).
PRESETS = {
    "ryo": {"id": "ryo", "name": "山田凉", "frames": "角色/动作帧"},
    "whale": {"id": "whale", "name": "鲸鱼娘", "frames": "角色/大肥鱼像素素材包/素材/动作帧"},
}
PRESENTER_DEFAULT = "ryo"
IDLE_ANIMS = ["idle_m0", "idle_m1", "idle_m2"]            # without these nothing can fall back to 待机: never allowed missing
REQUIRED_ANIMS = IDLE_ANIMS + ["reach_m0", "reach_m1", "reach_m2", "walk"]
REQUIRED_FONTS = ["fonts.css", "NotoSansSC.ttf", "JetBrainsMono.ttf", "ZCOOLKuaiLe.ttf"]
BG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_ALPHA, DEFAULT_BLUR = 0.22, 10
# fallback action registry when anims.json has no top-level "actions" (keep in step with core.js ACTION_DEFAULTS)
ACTION_DEFAULTS = {
    "reach": {"type": "body", "frames": "reach", "via": "palm", "look": "look_r"},
    "chest": {"type": "body", "frames": "chest", "via": "chest_mid"},
    "hold": {"type": "body", "frames": "hold", "via": "hold_mid"},
    "point": {"type": "body", "frames": "point", "via": "palm", "look": "look_r"},
    "wave": {"type": "body", "frames": ["wave_a", "wave_b", "wave_a", "wave_c"], "via": "palm"},
    "count1": {"type": "body", "frames": "count1", "via": "palm", "fx": "fx_digit1", "chain": "count"},
    "count2": {"type": "body", "frames": "count2", "via": "palm", "fx": "fx_digit2", "chain": "count"},
    "count3": {"type": "body", "frames": "count3", "via": "palm", "fx": "fx_digit3", "chain": "count"},
    "finger_up": {"type": "body", "frames": "finger_up", "via": "chest_mid", "fx": "fx_emph"},
    "think": {"type": "body", "frames": "think", "via": "chest", "look": "look_ur", "fx": "fx_think"},
    "shrug": {"type": "body", "frames": "shrug", "via": "shrug_mid"},
    "thumb": {"type": "body", "frames": "thumb", "via": "chest_mid", "fx": "fx_glint"},
    "hip": {"type": "body", "frames": "hip", "via": "hip_mid"},
    "ear": {"type": "body", "frames": "ear", "via": "palm", "look": "look_r", "fx": "fx_listen"},
    "palm": {"type": "body", "frames": "palm"},
    "palm_r": {"type": "body", "frames": "palm", "look": "look_r"},
    "palm_l": {"type": "body", "frames": "palm_l"},
    "chest_s": {"type": "body", "frames": "chest_mid"},
    "hold_s": {"type": "body", "frames": "hold_mid"},
    "open": {"type": "body", "frames": "shrug_mid"},
    "look": {"type": "head", "via": "head_tr1", "steps": [["head_tr", None]], "eyes": "look_r"},
    "nod": {"type": "head", "steps": [["head_nod", 70], ["head_nod2", 120], ["head_nod", 70]]},
    "nod2": {"type": "head", "steps": [["head_nod", 60], ["head_nod2", 140], ["head_nod", 60], [None, 100],
                                      ["head_nod", 60], ["head_nod2", 140], ["head_nod", 60]]},
    "shake": {"type": "head", "steps": [["head_tl1", 50], ["head_tl", 110], ["head_tl1", 40], ["head_tr1", 40],
                                       ["head_tr", 110], ["head_tr1", 40], ["head_tl1", 40], ["head_tl", 110],
                                       ["head_tl1", 50]]},
    "turnout": {"type": "legs", "frames": "legs_turnout"},
}
AUTO_NEED = {  # auto-layer channel -> breathing sets / anims it needs (core.js drops a missing gesture shape from the
    # pool and turns a channel off only when nothing of it is left)
    "gesture": ["chest_mid_m*", "hold_mid_m*", "shrug_mid_m*", "palm_m*", "palm_l_m*"],
    "nod": ["head_nod_m*", "head_nod2_m*"],
    "look": ["idle_look_r_m*"],
    "weight": ["legs_turnout"],
}


def rel(p: Path) -> str:
    """path of p relative to the engine dir, with forward slashes (for URLs in the page)"""
    return os.path.relpath(str(p), str(ENGINE)).replace("\\", "/")


def rel_to(p: Path, base: Path) -> str:
    """p relative to base for messages ('素材/角色/动作帧'), or the absolute path when it is elsewhere"""
    try:
        return "素材/" + Path(p).resolve().relative_to(Path(base).resolve()).as_posix()
    except ValueError:
        return Path(p).as_posix()


def find_series(arg):
    if arg:
        return Path(arg).resolve()
    if os.environ.get("YUANLAI_SERIES"):
        return Path(os.environ["YUANLAI_SERIES"]).resolve()
    for d in [ENGINE, *ENGINE.parents]:
        if (d / "素材" / "字体" / "fonts.css").exists() or (d / "素材" / "角色" / "动作帧" / "anims.json").exists():
            return d
    return None


def presenter_of(episode, timeline):
    """{id, name, frames}: episode.json "presenter" (object or id) > timeline.episode.presenter > ryo."""
    raw = episode.get("presenter")
    if raw is None:
        raw = ((timeline or {}).get("episode") or {}).get("presenter")
    if isinstance(raw, str):
        raw = {"id": raw}
    raw = raw if isinstance(raw, dict) else {}
    pid = raw.get("id") or PRESENTER_DEFAULT
    out = dict(PRESETS.get(pid) or {"id": pid, "name": pid, "frames": ""})
    out.update({k: raw[k] for k in ("name", "frames") if raw.get(k)})
    out["id"] = pid
    return out


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def frames_problem(sprites: Path):
    """None when the presenter's frame folder can draw her (anims.json with idle_m0..2); else what is wrong"""
    if not sprites.is_dir():
        return "帧目录不存在"
    if not (sprites / "anims.json").exists():
        return "帧目录里没有 anims.json"
    try:
        table = load_json(sprites / "anims.json").get("anims") or {}
    except Exception as e:  # noqa: BLE001
        return f"anims.json 读不了：{e}"
    lost = [a for a in IDLE_ANIMS if a not in table]
    return f"帧目录里没有待机帧 {'、'.join(lost)}（动作没法退回待机）" if lost else None


def frame_dir_candidates(sprites: Path, assets: Path):
    """usable frame folders of the same character pack (sharing 素材/<a>/<b>/ with `sprites`), nearest first,
    as paths relative to 素材/ -- what --frames can point to while her own frames are not drawn yet"""
    try:
        parts = sprites.resolve().relative_to(assets.resolve()).parts
    except ValueError:
        return []
    pack = assets.joinpath(*parts[:2]) if len(parts) >= 2 else None
    if pack is None or not pack.is_dir():
        return []
    found = []
    for j in sorted(pack.glob("**/anims.json"), key=lambda q: (len(q.parts), str(q))):
        d = j.parent
        rel = d.relative_to(assets).as_posix()
        if any(x.startswith(("_", ".")) for x in d.relative_to(pack).parts) or frames_problem(d):
            continue
        found.append((0 if d in sprites.parents else 1, rel, len(load_json(j).get("anims") or {})))
    return [(rel, n) for _, rel, n in sorted(found)]


def expand(keys):
    """'chest_m*' -> chest_m0..2"""
    out = []
    for k in keys:
        out += [k[:-1] + str(m) for m in range(3)] if k.endswith("_m*") else [k]
    return out


def breath(base):
    return [f"{base}_m{m}" for m in range(3)]


def compact(keys):
    """['chest_m0', 'chest_m1', 'chest_m2', 'walk'] -> ['chest_m0..2', 'walk'] (sorted, for messages)"""
    keys = sorted(set(keys))
    out = []
    for k in keys:
        if k[-3:-1] == "_m" and k[-1] in "012":
            b = k[:-3]
            if all(f"{b}_m{m}" in keys for m in range(3)):
                if k.endswith("_m0"):
                    out.append(f"{b}_m0..2")
                continue
        out.append(k)
    return out


def eye_patch_check(sprites, table, rect):
    """Expression / gaze sets idle_<x>_m0 are pasted over body frames through patch_rects.eyes (动作 v2). Returns the box
    [x0, y0, x1, y1) where they differ from idle_m0 when it sticks out of `rect` (else None). Needs Pillow; skipped
    without it. A presenter whose eyes sit elsewhere (鲸鱼娘: rows 22..31) must give her own patch_rects.eyes."""
    try:
        from PIL import Image, ImageChops
    except Exception:  # noqa: BLE001
        return None
    base = (table.get("idle_m0") or {}).get("frames") or []
    box = None
    for name, a in table.items():
        if not (name.startswith("idle_") and name.endswith("_m0")) or name == "idle_m0":
            continue
        for fa, fb in zip(base, a.get("frames") or []):
            try:
                d = ImageChops.difference(Image.open(sprites / fa).convert("RGBA"),
                                          Image.open(sprites / fb).convert("RGBA")).getbbox(alpha_only=False)
            except Exception:  # noqa: BLE001
                continue
            if d:
                box = list(d) if box is None else [min(box[0], d[0]), min(box[1], d[1]), max(box[2], d[2]), max(box[3], d[3])]
    if box and (box[0] < rect[0] or box[1] < rect[1] or box[2] > rect[2] or box[3] > rect[3]):
        return box
    return None


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
                if r.get("via"):
                    extra += breath(r["via"])
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


def merge_sprites(base_dir, extra_dirs, errors, warns, who="讲解员"):
    """anims.json of the presenter's frame folder plus the overlays -> (merged anims json, {anim: dir its frames live in})."""
    anims, src = None, {}
    ap_json = base_dir / "anims.json"
    if not ap_json.exists():                  # main() stops before this (frames_problem); kept for other callers
        errors.append(f"{who}的角色帧清单不存在：{ap_json}")
        return None, src
    try:
        anims = load_json(ap_json)
    except Exception as e:  # noqa: BLE001
        errors.append(f"{who}的 anims.json 读不了：{e}")
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
            # frame paths relative to the presenter's frame folder, so the page keeps one spriteBase
            a["frames"] = [os.path.relpath(str(d / f), str(base_dir)).replace("\\", "/") for f in a.get("frames") or []]
            anims["anims"][k] = a
            src[k] = d
        for key in ("actions", "patch_rects", "stage", "head_offsets", "fx_offset"):   # registry + character geometry
            v = extra.get(key)
            if isinstance(v, dict):
                anims[key] = dict(anims.get(key) if isinstance(anims.get(key), dict) else {}, **v)
            elif isinstance(v, list) and key == "fx_offset":
                anims[key] = v
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
    ap.add_argument("--frames", metavar="DIR",
                    help="临时顶替讲解员的帧目录 presenter.frames（相对 素材/，例如 角色/大肥鱼像素素材包/素材）；"
                         "不改 episode.json。她的帧还没画完、只出草稿时用，一般和 --allow-missing 一起")
    ap.add_argument("--allow-missing", action="store_true",
                    help="草稿：缺的动作帧 / 背景图只警告（动作退回待机），不报错；帧目录本身不存在或没有待机帧时照样报错")
    args = ap.parse_args()

    errors, warns = [], []
    series = find_series(args.series)
    if series is None or not (series / "素材").is_dir():
        sys.exit("找不到素材根目录（含 素材/ 的 SERIES）：用 --series 指定，或设环境变量 YUANLAI_SERIES")
    assets = series / "素材"
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

    # ---- canvas: the engine and render.py take the frame size from timeline.json (episode.canvas, default 1920x1080);
    #      an episode.json edited after the last build_timeline would render at the old size -> say so
    def _cv(v):
        try:
            return tuple(int(x) for x in v) if isinstance(v, (list, tuple)) and len(v) == 2 else None
        except (TypeError, ValueError):
            return None
    cv_tl = _cv(((timeline or {}).get("episode") or {}).get("canvas")) or (1920, 1080)
    cv_ep = _cv(episode.get("canvas")) or (1920, 1080)
    if timeline is not None and ep_path.exists() and cv_ep != cv_tl:
        warns.append(f"episode.json 的 canvas 是 {cv_ep[0]}×{cv_ep[1]}，timeline.json 里是 {cv_tl[0]}×{cv_tl[1]}（画面按 timeline 出）："
                     "先重跑 build_timeline.py（和 mix_audio.py）")

    # ---- background colour + layout switches (core.js reads timeline.json's episode first, then this assets.js copy)
    tep = (timeline or {}).get("episode") or {}
    for key in ("bg_color", "layout", "style", "board_lead"):
        if ep_path.exists() and key in tep and episode.get(key) != tep.get(key):
            warns.append(f"episode.json 的 {key} 是 {episode.get(key)!r}，timeline.json 里是 {tep.get(key)!r}（画面按 timeline 出）："
                         "先重跑 build_timeline.py")
    eff = dict(episode, **tep)            # what core.js sees: timeline.json's episode over the assets.js copy
    raw = eff.get("bg_color")
    bgc = raw.strip().upper() if isinstance(raw, str) and re.fullmatch(r"\s*#[0-9A-Fa-f]{6}\s*", raw) else None
    if raw not in (None, "") and not bgc:
        warns.append(f"bg_color = {raw!r}：要写成 \"#RRGGBB\"（例如 \"#FFFFFF\"），现在按没写处理（深色底 + 章节背景图）")
    layout = eff.get("layout")
    if layout not in (None, "", "center"):
        warns.append(f"layout = {layout!r}：只认 \"center\"（内容以画面中线居中），现在按没写处理（旧版面，内容区 x 440–1860）")

    # ---- sprites (the episode's presenter) ---------------------------------------------------------
    pres = presenter_of(episode, timeline)
    frames_note = ""
    if args.frames:                         # temporary frame folder for this run only (episode.json unchanged)
        frames_note = f"（--frames 临时指定；episode.json 写的是 {pres.get('frames') or '（没写）'}）"
        pres["frames"] = args.frames.replace("\\", "/")
    if not pres.get("frames"):
        errors.append(f"讲解员 {pres['id']} 没有写 frames（episode.json 的 presenter.frames，相对 素材/）")
        pres["frames"] = PRESETS[PRESENTER_DEFAULT]["frames"]
    fp = Path(str(pres["frames"]))
    sprites = (fp if fp.is_absolute() else assets / fp).resolve()
    who = f"讲解员「{pres['name']}」（{rel_to(sprites, assets)}）"
    prob = frames_problem(sprites)
    if prob:                                # no frames = no presenter: never silently fall back to the placeholder
        cands = frame_dir_candidates(sprites, assets)
        lines = [f"{who}：{prob}{frames_note}",
                 "没有她的帧就画不出讲解员（页面只会剩一个占位小人），所以加 --allow-missing 也不放行。"]
        if cands:
            keep, skip = [], False            # this run's own arguments, with --frames / --allow-missing replaced
            for a in sys.argv[1:]:
                if skip or a == "--allow-missing" or a.startswith("--frames="):
                    skip = False
                    continue
                if a == "--frames":
                    skip = True
                    continue
                keep.append(f'"{a}"' if " " in a else a)
            lines += ["她的帧还没画完、只出草稿：用 --frames 临时换成同一个素材包里已有的帧目录（相对 素材/，不改 episode.json），"
                      "没有的动作退回待机：",
                      "    python " + " ".join([Path(__file__).as_posix(), *keep, "--frames", cands[0][0], "--allow-missing"])]
            lines += [f"  可用：{rel}（{n} 条）" for rel, n in cands[:4]]
        else:
            lines.append(f"{rel_to(sprites, assets)} 所在的素材包里没有可以临时用的帧目录（要有 anims.json 和待机帧 "
                         "idle_m0..2）：先把帧画完，或检查 episode.json 的 presenter.frames / --frames 写的路径")
        print("素材检查没通过：\n  " + "\n  ".join(lines), file=sys.stderr)
        sys.exit(1)
    extra_dirs = sprite_extra_dirs(args, episode, series)
    anims, src_dir = merge_sprites(sprites, extra_dirs, errors, warns, who)
    registry = dict(ACTION_DEFAULTS, **((anims or {}).get("actions") or {}))
    if anims is not None:
        table = anims.get("anims") or {}
        missing = [a for a in REQUIRED_ANIMS if a not in table]
        if missing:
            errors.append(f"{who}缺少必需的动作帧 {'、'.join(compact(missing))}（引擎至少要 idle_m0..2、reach_m0..2、walk）")
        for name, a in table.items():
            frames = a.get("frames") or []
            durs = a.get("durations") or []
            if not frames or len(frames) != len(durs):
                errors.append(f"{who}的动作 {name}：frames / durations 数量不一致")
            lost = [f for f in frames if not (sprites / f).exists()]
            if lost:
                errors.append(f"{who}的动作 {name}：缺帧文件 {lost[:4]}{' …' if len(lost) > 4 else ''}")
        need, opt = action_anims(timeline, registry)
        lost_need = {k: used for k, used in need.items() if k not in table}
        if lost_need:
            groups = {}                                     # same places -> one entry: "chest_m0..2（S01-01）"
            for k, used in lost_need.items():
                groups.setdefault(tuple(sorted(used)[:4]), []).append(k)
            items = sorted(f"{'、'.join(compact(ks))}（{', '.join(u)}）" for u, ks in groups.items())
            errors.append(f"{who}缺时间轴 actions 要用的动作帧：{'；'.join(items)}。"
                          f"先把帧补进 {rel_to(sprites, assets)}/（山田凉用 素材/角色/动作生成器/make_sprites.py），"
                          f"或用 --sprites-extra 叠加待确认的帧；只出草稿可加 --allow-missing（缺帧的动作退回待机）")
        lost_opt = compact(k for k in opt if k not in table)
        if lost_opt:
            warns.append(f"{who}的动作过渡帧 / 视线 / 特效缺帧（引擎照样播，只少这一层）：{'、'.join(lost_opt[:8])}{' …' if len(lost_opt) > 8 else ''}")
        if (timeline or {}).get("episode"):          # v2 pastes expression eyes over body / head frames
            rect = list((anims.get("patch_rects") or {}).get("eyes") or [21, 20, 43, 29])
            box = eye_patch_check(sprites, table, rect)
            if box:
                warns.append(f"{who}的表情 / 视线帧和 idle_m0 的差别在 {box}，超出了眼睛补丁 patch_rects.eyes {rect}"
                             f"{'（没写，用的是山田凉的默认值）' if not (anims.get('patch_rects') or {}).get('eyes') else ''}："
                             "表情叠在身体动作上会缺一截。在她的 anims.json 写 patch_rects.eyes 盖住这块（手势帧的手别伸进这个框）")
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
                if not (on and lost):
                    continue
                if ch == "gesture" and len(lost) < len(expand(AUTO_NEED[ch])):
                    warns.append(f"{who}自动层手势缺帧 {'、'.join(compact(lost))}：引擎只用剩下的几种手势（帧补进帧目录或用 --sprites-extra 后恢复）")
                else:
                    warns.append(f"{who}自动层「{ch}」通道缺帧 {'、'.join(compact(lost))}：引擎会关掉这个通道（帧补进帧目录或用 --sprites-extra 后恢复）")

    # ---- fonts -----------------------------------------------------------------------------------
    for f in REQUIRED_FONTS:
        if not (fonts / f).exists():
            errors.append(f"字体文件不存在：{fonts / f}")

    # ---- backgrounds -----------------------------------------------------------------------------
    gal = sorted(p.name for p in gallery.iterdir() if p.suffix.lower() in BG_EXT) if gallery.is_dir() else []
    if not gal and not bgc:
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
                                        "bg_alpha", "bg_blur", "terms", "auto_gestures", "bg_color", "layout",
                                        "style", "board_lead") if k in episode}
    manifest = {
        "anims": anims,
        "spriteBase": rel(sprites) + "/",
        "presenter": {"id": pres["id"], "name": pres["name"], "frames": rel_to(sprites, assets)},
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

    # ---- handwriting strokes (白板版) -> handdata.js
    board = eff.get("style") == "board"
    hand_info = None
    if board:
        sys.path.insert(0, str(ENGINE))
        import hand_glyphs                                           # noqa: E402  (engine/hand_glyphs.py)
        texts = [json.dumps(timeline or {}, ensure_ascii=False), json.dumps(episode, ensure_ascii=False),
                 "你可能也想问本期总结下期见原LAI如此0123456789？！。，、：；（）“”《》—…·"]
        for f in ("scenes.js", "board.js"):
            if (ENGINE / f).exists():
                texts.append((ENGINE / f).read_text(encoding="utf-8"))
        try:
            hd = hand_glyphs.build_hand_js(texts, ENGINE / "handdata.js", series / "素材" / "手写")
            hand_info = (len(hd["cjk"]), len(hd["punct"]), len(hd["lat"]["g"]), (ENGINE / "handdata.js").stat().st_size)
            miss = [ch for ch in hd["missing"] if not ch.isspace() and ord(ch) > 0x2E7F]
            if miss:
                warns.append(f"手写笔画数据里没有这些字（真要手写时会留空，换个字或写成印刷体）：{''.join(miss[:60])}"
                             + (f" 等 {len(miss)} 个" if len(miss) > 60 else ""))
        except FileNotFoundError as e:
            errors.append(str(e))
            (ENGINE / "handdata.js").write_text("window.__HAND__ = null;\n", encoding="utf-8")
    else:
        (ENGINE / "handdata.js").write_text(
            "// generated by engine/sync_assets.py — not a whiteboard episode (episode.json has no \"style\": \"board\")\n"
            "window.__HAND__ = null;\n", encoding="utf-8")

    n_anims = len((anims or {}).get("anims") or {})
    print(f"series : {series}")
    print(f"episode: {ep_src}  (#{episode.get('number', '?')}, {len(episode.get('questions') or [])} questions)")
    print(f"sprites: 讲解员「{pres['name']}」({pres['id']}) {n_anims} anims <- {rel(sprites)}/"
          + "".join(f" + {rel(d)}/" for d in extra_dirs) + frames_note)
    if board and not bgc:
        bgc = "#FFFFFF"                                              # the board is white unless bg_color says otherwise
    if bgc:
        n = int(bgc[1:], 16)
        lum = sum(w * ((c / 255) / 12.92 if c / 255 <= 0.03928 else (((c / 255) + 0.055) / 1.055) ** 2.4)
                  for w, c in ((0.2126, n >> 16), (0.7152, (n >> 8) & 255), (0.0722, n & 255)))
        print(f"bg     : solid {bgc} (bg_color; no background images in the video"
              + ("; light theme" if lum > 0.4 else "") + ")")
    else:
        print(f"bg     : {len(gal)} in gallery; per scene: " + ", ".join(f"{k}={v}" for k, v in bg_scenes.items()))
        print(f"bg look: alpha {manifest['bgAlpha']}, blur {manifest['bgBlur']} px")
    print("layout : " + ("center (content centred on the canvas midline, stage x 960)" if layout == "center"
                         else "content area x 440–1860 (no layout)"))
    if board:
        lead = eff.get("board_lead", 1.0)
        print(f"style  : board (whiteboard; scenes {lead} s ahead of the voice; subtitles 56 px)"
              + (f"; hand strokes {hand_info[0]} 汉字 + {hand_info[1]} 标点 + {hand_info[2]} 拉丁, "
                 f"{hand_info[3] / 1024:.0f} KB -> handdata.js" if hand_info else ""))
    print(f"fonts  : {fr}/")
    print(f"canvas : {cv_tl[0]}×{cv_tl[1]} (timeline.json" + (")" if cv_tl == (1920, 1080) else
          f"; content stage 1920×1080 at x {(cv_tl[0] - 1920) // 2})"))
    for w in warns:
        print("WARN   : " + w)
    for e in errors:
        print("MISSING: " + e)
    print(f"-> {ENGINE / 'assets.js'}\n-> {ENGINE / 'assets.css'}\n-> {ENGINE / 'handdata.js'}")
    if board and hand_info is None:
        sys.exit(1)                  # whiteboard episode without stroke data: nothing could be written by hand


if __name__ == "__main__":
    main()
