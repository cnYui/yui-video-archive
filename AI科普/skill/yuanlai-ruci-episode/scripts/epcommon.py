"""Shared helpers for the 《原LAI如此》 episode scripts (not a command itself).

Everything that two scripts must agree on lives here, so they cannot drift apart:
series / episode paths, reading episode.json and 台本/script_data.py, segment ids,
the frame size (canvas_of: episode.json "canvas", default 1920x1080; new episodes 2340x1080),
the speech-length estimate, the presenters (讲解员预设 PRESENTERS / presenter_of: name, frame folder, Fish Audio voice)
and the action vocabulary of references/pipeline-contract.md §4
(动作 v2: ACTIONS / ALIASES / parse_actions, the usage tier ACTION_LIMITS, frame checks sprite_keys / frame_status).
"""
import copy
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True           # keep __pycache__ out of the skill and episode folders

SERIES_DEFAULT = Path(r"D:/大疆/AI科普")
SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent

CPS = 5.3            # TTS speed estimate, spoken units / s: fitted to episode 1's Fish Audio takes
                     # (324 s measured; the pre-voice guess 4.3 came out ~20 % too long)
SENT_PAUSE = 0.25    # extra seconds per sentence end
SEG_GAP = 0.25       # breathing room after every spoken segment in the timeline (s)
INTRO_DEFAULT = 3.8  # UE intro length (s) when 片头片尾/intro/index.html cannot be read
OUTRO_DEFAULT = 4.8  # UE outro length (s)
# Frame size (pipeline-contract.md §2 "canvas"). User, 2026-09-27: every video from episode 2 on is 19.5:9 = 2340x1080
# (phone full screen); covers stay 16:9 1920x1080 + 4:3 1440x1080 (make_cover.py, not affected by the canvas).
CANVAS_DEFAULT = (1920, 1080)   # episode.json without "canvas": episode 1, older folders, 《AI每日日报》's calls
CANVAS_NEW = (2340, 1080)       # what new_episode.py writes into a new episode
# Background colour and layout (pipeline-contract.md §2 "bg_color" / "layout"). User, 2026-09-28: 「白底做成引擎开关，以后默认白底」,
# and content centred on the canvas midline like the subtitles. An episode.json without them renders as before (episodes 1-4).
BG_COLOR_NEW = "#FFFFFF"        # what new_episode.py writes: solid white, no background images in the video
LAYOUT_NEW = "center"           # what new_episode.py writes: content centred on the canvas midline (stage x 960)
# User, 2026-09-28: 「原LAI如此配音之后需要我来配音，ai配音用来做每日日报，然后原LAI如此也用手写白板，字提前一秒出现，字幕也同步放大」
STYLE_NEW = "board"             # whiteboard: content written by hand while it is said, 1 s ahead of the voice, 56 px subtitles
VOICE_NEW = "user"              # the user records the narration (record_script / import_voice); AI TTS only for 《AI每日日报》
STAGE = (1920, 1080)            # the content stage scenes.js draws on, centred in the canvas
FORBIDDEN_GAGS = ["吃草", "借钱", "怪人", "弹贝斯", "睡觉", "饿肚子", "肚子饿"]   # character gags unrelated to the topic

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass


# ---------------------------------------------------------------- CLI + paths
def add_common(ap, episode=True):
    """Add the <episode_dir> positional and --series option every script takes."""
    if episode:
        ap.add_argument("episode_dir", help="本期目录，例如 D:/大疆/AI科普/第02期_Token是什么")
    ap.add_argument("--series", default=str(SERIES_DEFAULT),
                    help=f"系列根目录（素材、片头片尾、_旧稿 所在处），默认 {SERIES_DEFAULT}")
    return ap


class Paths:
    """All conventional locations of one episode (pipeline-contract.md §1)."""

    def __init__(self, episode_dir, series=SERIES_DEFAULT):
        self.ep = Path(episode_dir).resolve()
        self.series = Path(series).resolve()
        if not self.ep.is_dir():
            sys.exit(f"找不到本期目录：{self.ep}")
        self.episode_json = self.ep / "episode.json"
        self.script_dir = self.ep / "台本"
        self.script_data = self.script_dir / "script_data.py"
        self.script_md = self.script_dir / "台本.md"
        self.voice_plan = self.script_dir / "配音分段.json"
        self.voice = self.ep / "配音"
        self.chunks = self.voice / "chunks.json"
        self.raw = self.voice / "raw"
        self.selection = self.voice / "selection.json"
        self.segments = self.voice / "segments"
        self.prod = self.ep / "制作"
        self.engine = self.prod / "engine"
        self.timeline = self.prod / "timeline.json"
        self.prod_voice = self.prod / "voice"
        self.durations = self.prod_voice / "durations.json"
        self.alignment = self.prod_voice / "alignment.json"
        self.build = self.prod / "build"
        # series-wide
        self.assets = self.series / "素材"
        self.bg_library = self.assets / "背景图库"
        self.audio = self.assets / "音频"
        self.pack = self.series / "片头片尾"
        self.old = self.series / "_旧稿"

    def dir_name(self, episode=None):
        episode = episode if episode is not None else load_episode(self, required=False)
        return (episode or {}).get("dir_name") or self.ep.name


def load_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data, indent=1):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")


def load_episode(p, required=True):
    ep = load_json(p.episode_json)
    if ep is None and required:
        sys.exit(f"缺少 {p.episode_json}（先用 new_episode.py 建立本期目录）")
    if ep is not None:
        ep.setdefault("bg_alpha", 0.22)
        ep.setdefault("bg_blur", 10)
        ep.setdefault("target_minutes", [5, 7])
        for k in ("questions", "outro_items"):
            ep.setdefault(k, [])
        for k in ("chapters", "backgrounds"):
            ep.setdefault(k, {})
    return ep


def load_script(p):
    """Execute 台本/script_data.py (no bytecode written) and return its namespace."""
    if not p.script_data.exists():
        sys.exit(f"缺少 {p.script_data}")
    src = p.script_data.read_text(encoding="utf-8")
    ns = {"__file__": str(p.script_data), "__name__": "script_data"}
    exec(compile(src, str(p.script_data), "exec"), ns)  # noqa: S102  (our own script data)
    if not isinstance(ns.get("SCENES"), list):
        sys.exit(f"{p.script_data} 里没有 SCENES 列表")
    return ns


def archive(path, p, note=""):
    """Move a file/folder that is about to be replaced into SERIES/_旧稿/ (never delete)."""
    path = Path(path)
    if not path.exists():
        return None
    stamp = time.strftime("%Y%m%d-%H%M%S")
    try:
        rel = path.resolve().relative_to(p.ep)
        rel_s = "_".join(rel.parts)
    except ValueError:
        rel_s = path.name
    try:                                     # _skilltest/第01期_x -> "_skilltest_第01期_x" (never mistaken for a real episode)
        tag = "_".join(p.ep.relative_to(p.series).parts)
    except ValueError:
        tag = p.ep.name
    dst = p.old / f"{tag}_{stamp}{('_' + note) if note else ''}" / rel_s
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path), str(dst))
    return dst


def rel_from_engine(p, target):
    """Relative URL from 制作/engine/ to target (forward slashes), as the page needs it."""
    return os.path.relpath(Path(target).resolve(), p.engine.resolve()).replace("\\", "/")


# ---------------------------------------------------------------- presenters (讲解员预设)
# episode.json "presenter" = one of these presets, written in full (PRESENTER_KEYS) by new_episode.py --presenter <id>.
# No "presenter" field (episode 1, older folders) = PRESENTER_DEFAULT. Fields:
#   name        what she calls herself: the opening line is 「大家好，我是{name}」 (build_script checks it)
#   frames      her frame folder (anims.json + <key>/NN.png), relative to SERIES/素材/; the engine (sync_assets.py),
#               build_script (frame check) and make_cover (default sprite reach_m2/00.png) read it from episode.json
#   voice_id    Fish Audio voice model id = the API's reference_id (tts_api.py generates with it, references/voice.md)
#   voice_page / voice_app / voice_name   the voice's web page / web generator (to listen to samples) and its name
#   aliases     other names of the character: 「我是<alias>」 is flagged when she is not this episode's presenter
#               or when the alias is not her self-name
#   gags        character gags unrelated to the topic (checked on top of FORBIDDEN_GAGS)
#   cover       overrides for assets/cover-template (scale, ryoX, q, rx ...), below 封面/cover.json
# Adding one: an entry here + the same id / name / frames in engine-template/sync_assets.py PRESETS.
PRESENTER_KEYS = ("id", "name", "frames", "voice_id", "voice_page", "voice_app", "voice_name")
PRESENTER_DEFAULT = "ryo"
PRESENTERS = {
    "ryo": dict(
        id="ryo", name="山田凉", frames="角色/动作帧",
        voice_id="82a7576ebd634931b2926b64fc8e23ac",
        voice_page="https://fish.audio/zh-CN/m/82a7576ebd634931b2926b64fc8e23ac/",
        voice_app="https://fish.audio/app/text-to-speech/?modelId=82a7576ebd634931b2926b64fc8e23ac",
        voice_name="山田凉",
        desc="《孤独摇滚！》山田凉的像素同人形象",
        aliases=[], gags=[],
        cover={},                                   # the template defaults are her #01 cover
    ),
    "whale": dict(
        id="whale", name="鲸鱼娘", frames="角色/大肥鱼像素素材包/素材/动作帧",
        voice_id="e7219cb8cfab46bebba2ee570932b0a6",
        voice_page="https://fish.audio/zh-CN/m/e7219cb8cfab46bebba2ee570932b0a6/",
        voice_app="https://fish.audio/app/text-to-speech/?modelId=e7219cb8cfab46bebba2ee570932b0a6",
        voice_name="苏晓晓",
        desc="DeepSeek 拟人鲸鱼娘的像素同人形象（素材包叫大肥鱼）",
        aliases=["大肥鱼"], gags=["白饭", "不许叫胖"],
        # wider than 山田凉 (lace headdress + ahoge up to row 0, head fins x4..58, tail to x63 at rows 36..44):
        # smaller, and the receipt a little to the right, so the tail stays off the title and the 4:3 crop
        # (x 240..1680) keeps her outline; q in sprite px so it stays above her headdress
        cover=dict(scale=9, ryoX=232, rx=790, rw=850, q=dict(sx=40, sy=-15)),
    ),
}


def presenter_of(ep):
    """The episode's presenter as a full dict: episode.json "presenter" (an object, or only an id) on top of its preset;
    no field = PRESENTER_DEFAULT. Unknown ids are kept as written (they need their own "frames")."""
    raw = (ep or {}).get("presenter")
    if isinstance(raw, str):
        raw = {"id": raw}
    raw = dict(raw) if isinstance(raw, dict) else {}
    pid = raw.get("id") or PRESENTER_DEFAULT
    base = PRESENTERS.get(pid) or dict(id=pid, name=raw.get("name") or pid, frames=raw.get("frames") or "",
                                       voice_id="", voice_page="", voice_app="", voice_name="", desc="", aliases=[], gags=[],
                                       cover={})
    out = copy.deepcopy(base)
    for k, v in raw.items():
        if k == "cover" and isinstance(v, dict):
            out["cover"] = dict(out.get("cover") or {}, **v)
        elif v not in (None, ""):
            out[k] = v
    out["id"] = pid
    return out


def voice_id_of(pr):
    """Fish Audio model id (API reference_id) of a presenter dict: voice_id, else the 32-hex id in voice_app / voice_page
    (episode folders written before voice_id existed); '' when there is none."""
    if pr.get("voice_id"):
        return str(pr["voice_id"]).strip()
    for k in ("voice_app", "voice_page"):
        m = re.search(r"(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])", str(pr.get(k) or ""))
        if m:
            return m.group(0)
    return ""


def presenter_entry(pid):
    """What new_episode.py writes into episode.json "presenter" (PRESENTER_KEYS of the preset)."""
    return {k: PRESENTERS[pid][k] for k in PRESENTER_KEYS}


def presenter_frames(series, ep):
    """Absolute frame folder of the episode's presenter (SERIES/素材/<presenter.frames>)."""
    f = Path(str(presenter_of(ep).get("frames") or PRESENTERS[PRESENTER_DEFAULT]["frames"]))
    return f if f.is_absolute() else Path(series) / "素材" / f


def other_names(pr):
    """Names that must not follow 「我是」 in this episode: every other preset's name and aliases, and her own aliases."""
    own = pr.get("name")
    names = set(pr.get("aliases") or [])
    for q in PRESENTERS.values():
        names.add(q["name"])
        names.update(q.get("aliases") or [])
    names.discard(own)
    return sorted(n for n in names if n)


def parse_canvas(v):
    """[W, H] | (W, H) | "WxH" -> (W, H) ints, or None when it cannot be read."""
    if isinstance(v, str):
        v = v.lower().replace("×", "x").split("x")
    if not isinstance(v, (list, tuple)) or len(v) != 2:
        return None
    try:
        w, h = (float(x) for x in v)
    except (TypeError, ValueError):
        return None
    return (int(w), int(h)) if w == int(w) and h == int(h) else None


def canvas_problem(c):
    """None when (w, h) can be rendered (height 1080, even width >= 1920 -- x264 yuv420p needs even sizes), else why not"""
    w, h = c
    if h != 1080:
        return f"高度必须是 1080（现在是 {h}）"
    if w < STAGE[0]:
        return f"宽度至少 {STAGE[0]}（内容舞台 1920×1080 要放得下；现在是 {w}）"
    if w % 2:
        return f"宽度必须是偶数（H.264 yuv420p；现在是 {w}）"
    return None


def canvas_of(ep, strict=True):
    """(W, H) of the episode's video frame: episode.json "canvas" ([2340, 1080]); no field = CANVAS_DEFAULT (1920x1080).
    A value that cannot be rendered stops the script (strict) or falls back to the default with a warning."""
    raw = (ep or {}).get("canvas")
    if raw is None:
        return CANVAS_DEFAULT
    c = parse_canvas(raw)
    why = "写法不对（要写成 [宽, 高]，例如 [2340, 1080]）" if c is None else canvas_problem(c)
    if why:
        msg = f"episode.json 的 canvas = {raw!r}：{why}"
        if strict:
            sys.exit(msg)
        print(f"[提醒] {msg}；按 {CANVAS_DEFAULT[0]}×{CANVAS_DEFAULT[1]} 处理")
        return CANVAS_DEFAULT
    return c


def pack_durations(p):
    """(intro, outro) lengths read from 片头片尾/intro|outro/index.html (window.DURATION = x)."""
    out = []
    for name, default in (("intro", INTRO_DEFAULT), ("outro", OUTRO_DEFAULT)):
        f = p.pack / name / "index.html"
        v = default
        if f.exists():
            m = re.search(r"window\.DURATION\s*=\s*([0-9.]+)", f.read_text(encoding="utf-8", errors="replace"))
            if m:
                v = float(m.group(1))
        out.append(v)
    return tuple(out)


# ---------------------------------------------------------------- script rows
def is_bookend(sc):
    """Intro / outro scenes (片头/片尾) are separate video files and never part of the main timeline."""
    return sc.get("kind") in ("intro", "outro") or sc.get("title") in ("片头", "片尾") or sc.get("id") in ("S00",)


def normalise_row(row, where):
    """Return ('say', text, tts, visual) or ('gap', seconds, visual).

    Accepts the contract forms ("say", text, tts, visual) / ("gap", sec, visual), plus the older
    episode-1 form ("say", id, text, tts, visual) (the id is ignored: ids are generated)."""
    if not row:
        sys.exit(f"{where}: 空行")
    kind = row[0]
    if kind == "gap":
        if len(row) not in (2, 3):
            sys.exit(f"{where}: gap 行应为 (\"gap\", 秒, 画面说明)：{row!r}")
        return ("gap", float(row[1]), row[2] if len(row) > 2 else "")
    if kind == "say":
        if len(row) == 5:
            row = (row[0],) + tuple(row[2:])
        if len(row) == 3:
            row = tuple(row) + ("",)
        if len(row) != 4:
            sys.exit(f"{where}: say 行应为 (\"say\", 字幕原文, TTS 文本, 画面说明)：{row!r}")
        _, text, tts, visual = row
        text = str(text).strip()
        tts = str(tts or text).strip()
        if not text:
            sys.exit(f"{where}: 字幕原文为空")
        return ("say", text, tts, visual or "")
    sys.exit(f"{where}: 行类型必须是 \"say\" 或 \"gap\"：{row!r}")


def walk_script(scenes):
    """Main-body scenes with normalised rows and generated segment ids (S03-12 = scene-global index)."""
    out, n, seen = [], 0, set()
    for sc in scenes:
        if is_bookend(sc):
            continue
        sid = sc.get("id")
        if not sid or sid in seen:
            sys.exit(f"场景 id 缺失或重复：{sid!r}")
        seen.add(sid)
        rows = []
        for i, row in enumerate(sc.get("rows", [])):
            r = normalise_row(row, f"{sid} 第 {i + 1} 行")
            if r[0] == "say":
                n += 1
                rows.append(dict(kind="say", id=f"{sid}-{n:02d}", text=r[1], tts=r[2], visual=r[3]))
            else:
                rows.append(dict(kind="gap", dur=r[1], visual=r[2]))
        out.append(dict(id=sid, title=sc.get("title", sid), char=sc.get("char", ""), bg_note=sc.get("bg", ""),
                        rows=rows))
    return out


def spoken_units(text):
    """Estimate spoken length: CJK char = 1, spelled letters = 1 each, English word ~ 1 per 3 letters."""
    n = len(re.findall(r'[一-鿿]', text))
    for tok in re.findall(r'[A-Za-z]+', text):
        if tok.isupper() and len(tok) <= 4:
            n += len(tok)
        else:
            n += max(1, round(len(tok) / 3))
    n += len(re.findall(r'\d', text))
    return n


def est_seconds(tts):
    sentences = max(1, len(re.findall(r'[。？！]', tts)))
    return spoken_units(tts) / CPS + sentences * SENT_PAUSE


def fmt(t):
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:04.1f}"


def mmss(x):
    return f"{int(x // 60)}:{int(x % 60):02d}"


# ---------------------------------------------------------------- action vocabulary (contract §4 · 动作 v2)
# One entry per script word (【动作：词】). Fields:
#   type / name  timeline action; the engine (core.js) looks body / head names up in the action registry
#                (anims.json "actions": transition frames, gaze, fx), so one name can mean several frame sets
#   dur | whole  seconds from the anchor, or the whole row (max = cap in seconds for a whole-row body pose)
#   at           default anchor when the note has no @: "start" (段首) | "end" (@末尾)
#   clip         cut at the end of its row (body / expr / head); stickers and anims always play in full
#   lip          True = keeps lip-sync while it plays; False = sticker pose / anim (no lip-sync)
#   big          大动作: counts towards ACTION_LIMITS["big_total"] and the >= 15 s spacing
#   sticker      贴纸姿势 (疑问 / 收到 / 好耶): ACTION_LIMITS["sticker_total"], per chapter, never two rows in a row
#   count        1 / 2 / 3 for 数一 / 数二 / 数三 (a group starts at 数一 and goes in order)
#   whole_ok     @整段 allowed (whole row) besides the default anchor
#   frames       frame keys the word needs ("x_m*" = x_m0/_m1/_m2); build_script checks 动作帧/ and sprites_extra
#   v            1 = the 9 words of episode 1; 2 = the 14 new actions of 动作 v2 (+ the control word 不动)
#   use          when to use it (shown in 台本.md)
ACTIONS = {
    # ---- v1: 9 words
    "抬手": dict(type="body", name="reach", dur=1.2, at="start", clip=True, lip=True, frames=["reach_m*"], v=1,
               use="指向右侧内容、列要点、“请看这张图”"),
    "吃惊": dict(type="expr", name="surprised", dur=1.2, at="start", clip=True, lip=True, frames=["idle_surprised_m*"], v=1,
               use="说出反常识的事实"),
    "认真": dict(type="expr", name="determined", whole=True, dur=2.0, clip=True, lip=True, frames=["idle_determined_m*"],
               v=1, use="警告、注意事项（整段；写 @末尾 / @短语 时只占 2 s）"),
    "开心": dict(type="expr", name="happy", whole=True, dur=2.0, clip=True, lip=True, frames=["idle_happy_m*"], v=1,
               use="讲完一题、操作成功（整段；超过 4 s 的段一直眯眼说话会显得呆，写 开心@末尾 只占最后 2 s）"),
    "疑问": dict(type="pose", name="huh", dur=1.5, at="start", lip=False, big=True, sticker=True, frames=["pose_huh"], v=1,
               use="停顿里抛出疑问（贴纸，不对口型）"),
    "收到": dict(type="pose", name="roger", dur=1.5, at="start", lip=False, big=True, sticker=True, frames=["pose_roger"], v=1,
               use="“记住了”“明白”（贴纸）"),
    "好耶": dict(type="pose", name="yay", dur=1.5, at="start", lip=False, big=True, sticker=True, frames=["pose_yay"], v=1,
               use="讲完一题、总结（贴纸，带拉炮；常写 好耶@末尾；全片 1–2 次，至少 1 次）"),
    "小跳": dict(type="anim", name="hop", dur=1.48, at="start", lip=False, big=True, gap_only=True, frames=["hop"], v=1,
               use="章节结尾或总结的停顿里（只放 gap，全片 ≤1）"),
    "走动": dict(type="anim", name="walk", dur=1.2, at="start", lip=False, frames=["walk"], v=1,
               use="只用于开场从左侧走入（第一场第 0 秒的 gap）"),
    # ---- v2: 14 new words (数一 / 数二 / 数三 are one gesture)
    "指这里": dict(type="body", name="point", dur=1.4, at="start", clip=True, lip=True, frames=["point_m*"], v=2,
                use="斜指右上的内容：“看这一行”“这个字段就是 model”"),
    "看右边": dict(type="head", name="look", dur=1.2, at="start", clip=True, lip=True, whole_ok=True,
                frames=["head_tr_m*", "head_tr1_m*", "idle_look_r_m*"], v=2,
                use="“我们看右边这张表”（转头成 3/4 侧脸、眼睛看右；@整段 = 整段看着内容，这一段就不放自动手势）"),
    "数一": dict(type="body", name="count1", dur=1.6, at="start", clip=True, lip=True, big=True, count=1,
               frames=["count1_m*", "fx_digit1"], v=2,
               use="台词真的在列举“第一……”（写 @第一 对准；举手竖食指 + 手腕旁数字小标签）"),
    "数二": dict(type="body", name="count2", dur=1.6, at="start", clip=True, lip=True, big=True, count=2,
               frames=["count2_m*", "fx_digit2"], v=2,
               use="接在数一后面：“第二……”（比 V；和数一相隔不到 0.8 s 时手不放下，直接换手指）"),
    "数三": dict(type="body", name="count3", dur=1.6, at="start", clip=True, lip=True, big=True, count=3,
               frames=["count3_m*", "fx_digit3"], v=2, use="接在数二后面：“第三……”（三根手指）"),
    "重点": dict(type="body", name="finger_up", dur=1.5, at="start", clip=True, lip=True, big=True,
               frames=["finger_up_m*", "fx_emph"], v=2,
               use="“关键是……”“记住这一点”（手肘贴身、食指竖在脸侧 + 三道短线；“一定要”写 重点+认真）"),
    "思考": dict(type="body", name="think", dur=2.0, at="start", clip=True, lip=True, big=True,
               frames=["think_m*", "idle_look_ur_m*", "fx_think"], v=2,
               use="边说边抛问题：“为什么会这样？”（托腮 + 抬眼看右上 + 小的空心思考泡）"),
    "摊手": dict(type="body", name="shrug", dur=1.5, at="end", clip=True, lip=True, big=True, frames=["shrug_m*"], v=2,
               use="“就这么简单”“看情况”"),
    "竖拇指": dict(type="body", name="thumb", dur=1.4, at="end", clip=True, lip=True, frames=["thumb_m*"], v=2,
                use="“这样就可以了”“推荐这么做”（拳头在肩前、拇指朝上 + 一颗静止闪光）"),
    "手放胸前": dict(type="body", name="chest", dur=1.5, at="start", clip=True, lip=True, frames=["chest_m*"], v=2,
                 use="说到“我”“我们”“自己”（手放在胸口）"),
    "合手": dict(type="body", name="hold", whole=True, max=6.0, clip=True, lip=True, frames=["hold_m*"], v=2,
               use="平静说明、承上启下“接下来我们看……”（整段，最长 6 s）"),
    "点头": dict(type="head", name="nod2", dur=0.65, at="end", clip=True, lip=True, frames=["head_nod_m*", "head_nod2_m*"],
               v=2, use="“对”“没错”“就是这样”（点两下，头低 1 → 2 px；手放下时才播）"),
    "摇头": dict(type="head", name="shake", dur=0.6, at="start", clip=True, lip=True,
               frames=["head_tl_m*", "head_tl1_m*", "head_tr_m*", "head_tr1_m*"], v=2,
               use="“不是”“别这么做”（脸左右转 2 px，常写 摇头+认真）"),
    "挥手": dict(type="body", name="wave", dur=1.6, at="start", clip=True, lip=True, big=True,
               frames=["wave_a_m*", "wave_b_m*", "wave_c_m*"], v=2,
               use="开场问好、结尾道谢（第一场 / 最后一场，走入结束 0.25 s 以后）"),
    "叉腰": dict(type="body", name="hip", dur=1.6, at="start", clip=True, lip=True, frames=["hip_m*"], v=2,
               use="下结论、确定的语气：“答案就是它”（双手叉腰；也可 @末尾；同一章里不和「收到」一起用）"),
    "侧耳": dict(type="body", name="ear", dur=1.6, at="start", clip=True, lip=True, frames=["ear_m*", "fx_listen"], v=2,
               use="“常有人说……”“你可能会问……”“听说……”（手放在耳边的头发外沿 + 看右 + 声波）"),
    # ---- control word (not an action)
    "不动": dict(type="auto", name="off", whole=True, clip=True, control=True, frames=[], v=2,
               use="这一段不放任何自动动作（严肃、需要安静的段，如安全警告的主句）"),
}
ALIASES = {"走入": "走动", "走出": "走动", "走路": "走动", "举手": "抬手", "伸手": "抬手",
           "介绍": "抬手", "请看": "抬手", "指着": "指这里", "指向": "指这里", "看这里": "指这里",
           "看右侧": "看右边", "看内容": "看右边", "第一": "数一", "第二": "数二", "第三": "数三",
           "注意": "重点", "想一想": "思考", "托腮": "思考", "拇指": "竖拇指", "胸前": "手放胸前",
           "双手合握": "合手", "嗯嗯": "点头", "不对": "摇头", "招手": "挥手", "就是这样": "叉腰",
           "听说": "侧耳", "有人说": "侧耳"}
ALIASES.update({v["name"]: k for k, v in ACTIONS.items()})       # reach / hop / walk / count1 ... also accepted
IGNORED = {"说话", "待机", "idle", "talk"}                           # default behaviour, nothing to schedule
ACTION_RE = re.compile(r"【动作[:：]\s*([^】]*)】")
BIG_WORDS = [w for w, a in ACTIONS.items() if a.get("big")]
STICKER_WORDS = [w for w, a in ACTIONS.items() if a.get("sticker")]
# usage tier of 动作 v2 (SPEC F.5 + F.7). build_script checks it on the estimated times, build_timeline re-checks the
# big-action spacing on the real times. Change the tier here only (and in AGENTS.md「角色动作尺度」).
ACTION_LIMITS = {
    "total": (20, 30),            # suggested number of explicit actions per episode (stickers / hop / walk-in included)
    "total_warn": 35,             # more than this: warning
    "per_row": 1,                 # explicit actions per row (a body action + an expression = 1)
    "big_total": 12,              # 大动作 (BIG_WORDS) per episode
    "big_spacing": 15.0,          # seconds between the starts of two big actions
    "sticker_total": 4,           # 疑问 + 收到 + 好耶
    "sticker_per_chapter": 1,
    "count_groups": 2,            # 数一(→数二→数三) groups
    "same_body_run": 2,           # the same body action in at most 2 consecutive rows
    "not_same_chapter": [("叉腰", "收到")],   # read alike (a hand on the hip): never both in one chapter
    "long_whole": {"开心": 4.0},  # a whole-row expression longer than this (s): suggest 开心@末尾
    "per_word": {"好耶": 2, "小跳": 1, "走动": 1, "挥手": 2, "重点": 4, "思考": 3, "摊手": 3, "竖拇指": 2,
                 "点头": 6, "摇头": 6, "叉腰": 3, "侧耳": 3},
    "min_word": {"好耶": 1},      # the user asked to keep the party popper: at least once
}


def parse_actions(visual):
    """【动作：抬手】【动作：开心@末尾】【动作：抬手@平台靠它】【动作：摇头+认真】【动作：看右边@整段】 -> list of dicts.

    Returns (actions, warnings); each action = dict(word, anchor, anchored) + the vocabulary entry.
    anchor: "start" (段首) / "end" (@末尾) / "whole" (@整段) / a phrase (@短语: starts where that phrase is spoken);
    without @ the word's default (`at`). anchored=True when the note wrote an explicit @."""
    acts, warns = [], []
    for body in ACTION_RE.findall(visual or ""):
        for item in re.split(r"[、，,+＋/／;；]", body):
            item = item.strip()
            if not item:
                continue
            anc = None
            if "@" in item or "＠" in item:
                item, anc = re.split(r"[@＠]", item, maxsplit=1)
                anc = anc.strip()
            word = re.sub(r"[（(].*?[）)]", "", item).strip()
            key = None
            for k in sorted(list(ACTIONS) + list(ALIASES), key=len, reverse=True):
                if word.lower().startswith(k.lower()):
                    key = ALIASES.get(k, k)
                    break
            if key is None:
                if not any(word.lower().startswith(w) for w in IGNORED):
                    warns.append(f"未知动作「{word}」（词表：{'、'.join(ACTIONS)}）")
                continue
            voc = ACTIONS[key]
            if anc is None or anc in ("", "默认"):
                anchor = "whole" if voc.get("whole") else voc.get("at", "start")
            elif anc in ("末尾", "结尾", "段尾", "end"):
                anchor = "end"
            elif anc in ("开头", "段首", "start"):
                anchor = "start"
            elif anc in ("整段", "全段", "whole"):
                anchor = "whole"
                if not (voc.get("whole") or voc.get("whole_ok") or voc["type"] == "expr"):
                    warns.append(f"「{key}@整段」不支持（只有表情、看右边、合手、不动可以整段），改用默认位置")
                    anchor = voc.get("at", "start")
            else:
                anchor = anc
            acts.append(dict(voc, word=key, anchor=anchor, anchored=anc is not None))
    return acts, warns


def action_units(acts):
    """How many explicit actions a row's notes count as (ACTION_LIMITS): a body / head / sticker / anim each counts,
    expressions count only when nothing else is there (抬手+认真 = 1), 不动 never counts."""
    main = [a for a in acts if a["type"] not in ("expr", "auto")]
    ex = [a for a in acts if a["type"] == "expr"]
    return len(main) + (max(0, len(ex) - 1) if main else len(ex))


def sprite_dirs(series, ep=None):
    """The presenter's frame folder (presenter.frames; 山田凉 = 素材/角色/动作帧) and the preview overlays of this episode
    (episode.json "sprites_extra", relative to SERIES)."""
    base = presenter_frames(series, ep)
    extra = (ep or {}).get("sprites_extra") or []
    extra = [extra] if isinstance(extra, str) else list(extra)
    out = []
    for x in extra:
        q = Path(str(x))
        out.append(q if q.is_absolute() else Path(series) / q)
    return base, out


def sprite_keys(series, ep=None):
    """(keys in the presenter's anims.json, keys only available in the sprites_extra overlays)"""
    base, extra = sprite_dirs(series, ep)
    final = set(((load_json(base / "anims.json", {}) or {}).get("anims") or {}).keys())
    prev = set()
    for d in extra:
        prev |= set(((load_json(d / "anims.json", {}) or {}).get("anims") or {}).keys())
    return final, prev - final


def frame_status(word, final, preview):
    """'ok' (frames in the presenter's folder), 'preview' (only in a sprites_extra overlay: 用户确认前只能出样片) or 'missing'"""
    need = []
    for k in ACTIONS[word].get("frames") or []:
        need += [k[:-1] + str(m) for m in range(3)] if k.endswith("_m*") else [k]
    if all(k in final for k in need):
        return "ok"
    if all(k in final or k in preview for k in need):
        return "preview"
    return "missing"


BG_EXT = {".jpg", ".jpeg", ".png", ".webp"}


def fill_backgrounds(p, ep, scene_ids, warns=None):
    """Every scene gets a background file name: episode.json's choice, else the 背景图库 in name order,
    by scene position (library[i % n]) — the same rule as the engine's sync_assets.py / core.js."""
    warns = warns if warns is not None else []
    lib = sorted(f.name for f in p.bg_library.iterdir() if f.suffix.lower() in BG_EXT) if p.bg_library.is_dir() else []
    chosen, auto = {}, set()
    for i, sid in enumerate(scene_ids):
        f = ep.get("backgrounds", {}).get(sid)
        if f and not (p.bg_library / Path(str(f)).name).exists():
            warns.append(f"背景 {sid}: {f} 不在 {p.bg_library}，改用图库轮换")
            f = None
        f = Path(str(f)).name if f else None
        if not f and lib:
            f = lib[i % len(lib)]
            auto.add(sid)
        chosen[sid] = f
    if not lib and any(v is None for v in chosen.values()):
        warns.append(f"背景图库 {p.bg_library} 是空的，没指定背景的章节将只有深藏青底色")
    return chosen, auto


def md_cell(s):
    """Text safe inside a Markdown table cell."""
    return str(s).replace("|", "\\|").replace("\n", " ")


def tick_times(tl):
    """Main-time moments of the TOC tick sound: timeline toc done times plus gaps whose note says 打勾
    (duplicates within 0.3 s merged). Used by mix_audio.py."""
    ts = [it["done"] for it in ((tl.get("toc") or {}).get("items") or []) if it.get("done") is not None]
    ts += [g["start"] for g in tl.get("gaps", []) if "打勾" in (g.get("visual") or "")]
    out = []
    for t in sorted(ts):
        if not out or t - out[-1] > 0.3:
            out.append(t)
    return out


def mix_signature(tl):
    """Everything mix_audio.py's output depends on that comes from the timeline."""
    return (tl.get("fps"), tl.get("intro"), tl.get("main_duration"), tl.get("total_duration"),
            [(s["id"], s["start"], s["end"]) for s in tl.get("segments", [])],
            [s["start"] for s in tl.get("scenes", [])], tick_times(tl))


def gag_hits(text, extra=None):
    """FORBIDDEN_GAGS (+ the presenter's own gags, PRESENTERS[...]["gags"]) found in text."""
    return [g for g in list(FORBIDDEN_GAGS) + [x for x in (extra or []) if x not in FORBIDDEN_GAGS] if g in (text or "")]
