"""Create a new 《原LAI如此》 episode folder with the conventional layout (pipeline-contract.md §1).

  python new_episode.py --number 2 --title "Token 是什么" --presenter whale
  python new_episode.py --number 1 --title "什么是API" --dest D:/大疆/AI科普/_skilltest     # test episode
  python new_episode.py --update-engine D:/大疆/AI科普/第02期_Token是什么                  # refresh engine files

--presenter picks this episode's presenter from epcommon.PRESENTERS (default ryo = 山田凉; whale = 鲸鱼娘, DeepSeek 拟人,
素材包叫大肥鱼). Her full entry (id, name, frames, voice_page, voice_app, voice_name) goes into episode.json "presenter":
the opening line, the character frames (sync_assets.py / make_cover.py) and the Fish Audio voice all follow it.
--canvas is the video frame size written into episode.json "canvas": default 2340x1080 (19.5:9, the user's rule since
2026-09-27; scenes.js still draws on the 1920x1080 content stage centred in it). An episode.json without "canvas"
(episode 1) is 1920x1080. Covers are always 16:9 1920x1080 + 4:3 1440x1080 (make_cover.py).
--bg-color is written into episode.json "bg_color": default #FFFFFF (the user, 2026-09-28: 「以后默认白底」) = a solid
background, no chapter images in the video (the cover still uses a photo from 背景图库, cover.json); "none" leaves the
field out = the navy stage with the chapter images (episodes 1, 2). --layout is written into "layout": default center =
content centred on the canvas midline, the line the subtitles are centred on; "old" leaves the field out (content area
x 440-1860, episodes 1-4).
--style is written into "style": default board = the whiteboard (user, 2026-09-28: content written by hand while it
is said, text 1 s ahead of the voice, 56 px subtitles; hand.js / board.js); "cards" leaves the field out (printed
cards, episodes 1-4). --voice is written into "voice_source": default user = the user records the narration
(record_script.py -> the user's recording -> import_voice.py); "tts" = Fish Audio TTS (only when the user asks).

Creates <dest>/第NN期_<题目去空格>/ with
  episode.json              skeleton: presenter; canvas [2340, 1080]; bg_color "#FFFFFF"; layout "center"; style "board";
                            voice_source "user";
                            questions / chapters / backgrounds / outro_items
                            left empty to fill in (bg_alpha 0.22, bg_blur 10, target_minutes [5, 7],
                            auto_gestures true = 动作 v2 自动层开)
  台本/script_data.py        skeleton with commented examples (opening 「大家好，我是{讲解员}」, rows, 【动作：xxx】 notes)
  配音/raw/  配音/segments/
  制作/engine/              copied from SKILL/assets/engine-template/ (scenes.template.js -> scenes.js)
  制作/voice/  制作/build/  封面/
Nothing is overwritten: an existing episode folder is refused. --update-engine re-copies the template's
engine files into an existing episode (scenes.js is never touched; replaced files go to SERIES/_旧稿/).
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402

TEMPLATE = C.SKILL / "assets" / "engine-template"
SKIP_NAMES = {"__pycache__", "_check", ".DS_Store", "Thumbs.db"}
TEXT_EXT = {".html", ".js", ".css", ".py", ".json", ".md", ".txt"}
CONTRACT_REL = "../../../"          # engine -> series, for an episode directly under SERIES


def dir_name_for(number, title):
    t = re.sub(r"\s+", "", title)
    t = re.sub(r'[\\/:*?"<>|]', "", t)
    return f"第{number:02d}期_{t}"


def episode_skeleton(number, title, dir_name, presenter="ryo", canvas=C.CANVAS_NEW, bg_color=C.BG_COLOR_NEW,
                     layout=C.LAYOUT_NEW, style=C.STYLE_NEW, voice=C.VOICE_NEW):
    ep = {
        "number": number,
        "title": title,
        "dir_name": dir_name,
        "presenter": C.presenter_entry(presenter),
        "canvas": list(canvas),
        "bg_color": bg_color,
        "layout": layout,
        "style": style,
        "voice_source": voice,
        "target_minutes": [5, 7],
        "question_scene": "S02",
        "questions": [],
        "chapters": {},
        "backgrounds": {},
        "bg_alpha": 0.22,
        "bg_blur": 10,
        "terms": [],
        "auto_gestures": True,
        "intro_tagline": "",
        "outro_items": [],
        "outro_closing": "",
        "_说明": [
            "presenter：本期讲解员（new_episode.py --presenter ryo|whale 写入，预设在 scripts/epcommon.py PRESENTERS）。"
            "name = 开场自称（“大家好，我是{name}”），frames = 角色帧目录（相对 素材/），voice_page / voice_app / voice_name = "
            "Fish Audio 音色；换讲解员就把整段换成另一个预设。帧还没画完时，出草稿可以临时把 frames 指到已有的帧目录",
            "canvas：视频画面尺寸 [宽, 高]，默认 [2340, 1080]（19.5:9，2026-09-27 起每期都用）；没有这一项 = 1920×1080（第 1 期）。"
            "scenes.js 仍按 1920×1080 的内容舞台写坐标（舞台在画布里水平居中）；徽标、目录、角色、字幕、进度条、背景由引擎铺满画布。"
            "封面不受影响，照旧 16:9 + 4:3。改了要重跑 build_timeline",
            "bg_color：视频背景色，默认 \"#FFFFFF\"（2026-09-28 用户：以后默认白底）= 纯色背景、视频里不用背景图；浅色时引擎自动换"
            "浅色主题（深色章节标题 / 徽标 / 进度条文字，卡片阴影减轻，右上目录保留深色底板，字幕不变）。删掉这一项 = 深藏青底 + "
            "backgrounds 的章节背景图（第 1、2 期）。封面：白板版（style board）也是白底、手写标题，make_cover.py 自动选；卡片版照旧在 封面/cover.json 选背景图。改了要重跑 build_timeline",
            "layout：\"center\" = 内容以画面中线居中（舞台 x 960 = 画布中线，和字幕同一条线；章节标题收起后停在顶部正中）；"
            "右上目录、左下讲解员不动。删掉这一项 = 旧版面（内容区 x 440–1860，中线 1150，第 1–4 期）。改了要重跑 build_timeline",
            "style：\"board\" = 白板手写版（2026-09-28 用户：原LAI如此也用手写白板，字提前一秒出现，字幕也同步放大）：标题、"
            "要点、结论边说边手写，画面比声音早 board_lead 秒（默认 1），字幕 56 px 黑字白边，右上目录白卡片。删掉这一项 = "
            "印刷体卡片版（第 1–4 期）。改了要重跑 build_timeline 和 sync_assets（它生成手写笔画 handdata.js）",
            "voice_source：\"user\" = 用户自己配音（2026-09-28 用户：原LAI如此配音之后需要我来配音）：record_script.py 出录音稿，"
            "用户录好后 import_voice.py 导入，segment_audio.py 切句（能跳过重读的句子）；\"tts\" = Fish Audio 合成（用户点名要时才用，"
            "AI 配音现在只用于《AI每日日报》）",
            "questions：右上角「本期目录」，如 {\"text\": \"Token 是什么\", \"scenes\": [\"S03\"]}，scenes 是讲这一题的章节",
            "chapters：进度条章节名，如 {\"S01\": \"开场\", \"S02\": \"三个疑问\"}（没写的用场景 title）",
            "backgrounds：每章一张 素材/背景图库 里的文件名，如 {\"S01\": \"01_放学路上_树影.jpg\"}；没写的章节按图库顺序轮换。"
            "有 bg_color 时视频不用它，可以空着",
            "terms：字幕里要标橙色的术语（引擎已内置 API、API Key、Token、JSON、HTTP 等），如 [\"Token\", \"上下文窗口\"]",
            "outro_items / outro_closing：片尾制作清单和感谢语，必须问用户，不许用默认值（assemble.py 为空会报错）",
            "auto_gestures：角色自动层（说话时小手势、句末点头、看向内容），true 开 / false 关；嫌多写成 "
            "{\"gesture\": 0.6}（手势密度倍率），或 {\"nod\": false} / {\"look\": false} 关掉某个通道",
            "sprites_extra（可选）：新动作帧还没追加进本期讲解员的帧目录（presenter.frames）时出样片用，例如 "
            "\"_skilltest/actions_v2/frames_preview\"（相对 SERIES，必须是同一个讲解员的帧）；用户确认、帧追加进帧目录以后删掉",
            "这个 _说明 字段可以删掉，脚本不读它",
        ],
    }
    for k, v in (("bg_color", bg_color), ("layout", layout), ("style", style), ("voice_source", voice)):
        if not v:
            del ep[k]                     # --bg-color none / --layout old / --style cards: left out (as episodes 1-4)
    return ep


SCRIPT_SKELETON = '''# -*- coding: utf-8 -*-
"""《原LAI如此》第 {number} 期「{title}」台本数据 —— 本期内容的唯一来源。

本期讲解员：{name}（episode.json presenter）；配音：Fish Audio「{voice_name}」。
开场只一句：“大家好，我是{name}。今天给大家介绍……”（build_script.py 会检查；台词里不要出现别的讲解员的自称）。

改完运行（<本期> = 这个文件上两级的目录）：
  python {scripts}/build_script.py <本期>     -> 台本/台本.md、台本/配音分段.json
  python {scripts}/chunk_voice.py  <本期> --whole  -> 配音/chunks.json（整期一批）
  python {scripts}/tts_api.py      <本期>     -> 配音/raw/C01_v1.mp3（Fish Audio API，本期讲解员的音色）

行的写法（skill/references/pipeline-contract.md 第 3、4 节）：
  ("say", "字幕原文", "TTS 文本", "画面说明")    一段配音 = 一段字幕；段号按全片顺序自动生成（S03-12）
  ("gap", 秒, "画面说明")                        不说话的纯画面停顿
TTS 文本：英文缩写拆开读（"A P I"）、品牌名分词（"Deep Seek"）、网址念出来（"platform 点 deepseek 点 com"）。

画面 {canvas_w}×{canvas_h}（episode.json canvas）：画面说明里的“左边 / 右边 / 中间”都按居中的 1920×1080 内容舞台想，
scenes.js 也按舞台坐标写；左上徽标、右上目录、左下讲解员、字幕、进度条、背景由引擎铺在整个画布上，台本不用管。
{look}
{board}
角色动作写在画面说明里，只用词表里的词（skill/references/pipeline-contract.md §4；怎么选见 visuals.md「角色动作」）。
说话时的小手势、句末点头、看向内容由引擎的自动层加（episode.json auto_gestures），台本不用写。
台本动作（第 2 期档位：全片 20–30 个，约 12–18 s 一个；一段最多 1 个，「身体动作+表情」算 1 个）：
  讲解  抬手（介绍、请看）  指这里  看右边（可 @整段）  手放胸前  合手（整段）  叉腰（≤3）  侧耳（听说、有人说，≤3）
  列举  数一 / 数二 / 数三（写 @第一 @第二 @第三，按顺序成组，≤2 组）  重点（注意，≤4）
  语气  点头（默认 @末尾，≤6）  摇头（≤6，常写 摇头+认真）  思考（≤3）  摊手（默认 @末尾，≤3）  竖拇指（默认 @末尾，≤2）
  表情  吃惊  认真（整段）  开心（整段）
  贴纸  疑问  收到  好耶（拉炮，全片 1–2 次、至少 1 次）：不对口型，合计 ≤4、每章 ≤1、相邻两段不能都是贴纸
  其他  挥手（开场、结尾各 ≤1）  小跳（只放 gap，≤1）  走动（只用于开场走入）  不动（这一段不加自动动作）
  大动作（挥手、数一/二/三、重点、思考、摊手、疑问、收到、好耶、小跳）全片 ≤12，相邻两个间隔 ≥15 s。
  位置：@末尾 放到段尾；@短语 从这句里那个短语开始（【动作：数一@第一】）；@整段；+ 身体动作加表情（【动作：摇头+认真】）。
不用和知识无关的角色梗（吃草、借钱、怪人、弹贝斯、睡觉、饿肚子{gags}）。用多少以 D:/大疆/AGENTS.md「角色动作尺度」为准，
build_script.py 会按 epcommon.ACTION_LIMITS 数一遍并提醒。
"""

NOTES = [
    # 台本.md 开头的说明，每条一行，例如：
    # "v1 → v2：按用户意见删掉比喻，先抛三个疑问再讲。",
]

PRONUNCIATION = [
    # 配音读法提醒（写进 台本.md「配音」一节），例如：
    # "API 写成“A P I”逐个字母读；DeepSeek 写成“Deep Seek”。",
]

CHECKLIST = [
    # 出片前要核对的事实（官方文档、界面名称、价格、日期），例如：
    # "接口地址 https://api.deepseek.com：已按 2026-09-26 的官方文档核对。",
]

SCENES = [
    dict(id="S01", title="开场白", char="从左侧走入，停在左下角，然后说话", rows=[
        ("gap", 1.2, "【动作：走动】背景淡入"),
        ("say", "大家好，我是{name}。今天给大家介绍（待写）。",
                "大家好，我是{name}。今天给大家介绍（待写）。",
                "【动作：手放胸前@我是】画面中央大字「（待写）」"),
        ("gap", 0.4, ""),
    ]),
    dict(id="S02", title="三个疑问", char="说话；列举疑问时数一、二、三", rows=[
        ("say", "你可能会有三个疑问：", "你可能会有三个疑问。",
                "【动作：抬手】右侧出现标题「你可能也想问」"),
        ("say", "第一，（待写）？", "第一，（待写）？", "【动作：数一@第一】疑问卡 ① 弹出（“嗒”）"),
        ("say", "第二，（待写）？", "第二，（待写）？", "【动作：数二@第二】疑问卡 ② 弹出（“嗒”）"),
        ("say", "第三，（待写）？", "第三，（待写）？", "【动作：数三@第三】疑问卡 ③ 弹出（“嗒”）"),
        ("say", "这期视频，就把这三个问题讲清楚。", "这期视频，就把这三个问题讲清楚。",
                "【动作：点头】三张疑问卡飞到右上角，成为本期目录"),
        ("gap", 0.6, "转场：目录 ① 高亮"),
    ]),
    dict(id="S03", title="一、（待写）", char="说话；指向要点卡", rows=[
        ("say", "先说第一个问题：（待写）。", "先说第一个问题，（待写）。", "章节标题「一、（待写）」"),
        ("say", "它主要做三件事：", "它主要做三件事。", "【动作：指这里】要点卡标题「（待写）」"),
        ("say", "（待写）", "（待写）", "【动作：好耶@末尾】要点逐条出现；讲完这一题"),
        ("gap", 0.6, "目录 ① 打勾"),
    ]),
    # ... S04、S05 …… 每一题一个或几个章节（在 episode.json 的 questions 里对应起来）
    dict(id="S08", title="总结", char="说话", rows=[
        ("say", "最后总结一下。", "最后总结一下。", "【动作：合手】总结卡标题「本期总结」"),
        ("say", "第一，（待写）。", "第一，（待写）。", "总结卡 ①"),
        ("say", "我是{name}，我们下期见。", "我是{name}，我们下期见。", "【动作：挥手】"),
        ("gap", 0.5, "淡出到片尾"),
    ]),
]
'''


def copy_engine(p, update=False):
    """Copy the engine template into 制作/engine/. Returns list of (action, path)."""
    done = []
    if not TEMPLATE.is_dir():
        print(f"[警告] 还没有引擎模板 {TEMPLATE}；制作/engine/ 先留空，模板就绪后运行：\n"
              f"        python {Path(__file__).name} --update-engine {p.ep}")
        return done
    rel_series = C.rel_from_engine(p, p.series) + "/"
    p.engine.mkdir(parents=True, exist_ok=True)
    rewritten = []
    if not (TEMPLATE / "scenes.template.js").exists() and not (p.engine / "scenes.js").exists():
        print("[警告] 模板里没有 scenes.template.js：制作/engine/scenes.js 要自己写（可参考 scenes.example.js）")
    for src in sorted(TEMPLATE.rglob("*")):
        if any(part in SKIP_NAMES for part in src.relative_to(TEMPLATE).parts) or src.is_dir():
            continue
        rel = src.relative_to(TEMPLATE)
        if src.name == "scenes.template.js":
            rel = rel.with_name("scenes.js")
            if (p.engine / rel).exists():           # scenes.js is per-episode work: never replaced
                done.append(("keep", rel))
                continue
        dst = p.engine / rel
        if src.suffix.lower() in TEXT_EXT:
            data = src.read_text(encoding="utf-8")
            if rel_series != CONTRACT_REL:          # episode not directly under SERIES (e.g. _skilltest/)
                fixed = data.replace(CONTRACT_REL + "素材/", rel_series + "素材/")
                fixed = fixed.replace(CONTRACT_REL + "片头片尾/", rel_series + "片头片尾/")
                if fixed != data:
                    rewritten.append(rel.as_posix())
                    data = fixed
            if dst.exists() and dst.read_text(encoding="utf-8") == data:
                done.append(("same", rel))
                continue
            if dst.exists() and update:
                C.archive(dst, p, "engine")
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(data, encoding="utf-8")
        else:
            if dst.exists() and dst.read_bytes() == src.read_bytes():
                done.append(("same", rel))
                continue
            if dst.exists() and update:
                C.archive(dst, p, "engine")
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        done.append(("copy", rel))
    if rewritten:
        print(f"注意：本期不在系列根目录下，{rewritten} 里的 {CONTRACT_REL}素材/ 已改写为 {rel_series}素材/")
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--number", type=int, help="期号 N（目录名里写成两位：第02期）")
    ap.add_argument("--title", help="本期题目，如 \"Token 是什么\"（目录名去掉空格）")
    ap.add_argument("--dest", help="父目录（默认就是 --series；测试时用 D:/大疆/AI科普/_skilltest）")
    ap.add_argument("--presenter", choices=sorted(C.PRESENTERS), default=C.PRESENTER_DEFAULT,
                    help="本期讲解员：" + "，".join(f"{k} = {v['name']}（配音 {v['voice_name']}）" for k, v in C.PRESENTERS.items())
                    + f"；默认 {C.PRESENTER_DEFAULT}")
    ap.add_argument("--canvas", default="x".join(map(str, C.CANVAS_NEW)),
                    help=f"视频画面尺寸 WxH，写进 episode.json 的 canvas；默认 {C.CANVAS_NEW[0]}x{C.CANVAS_NEW[1]}（19.5:9）。"
                         "高度 1080，宽度 ≥1920 的偶数")
    ap.add_argument("--bg-color", default=C.BG_COLOR_NEW,
                    help=f"视频背景色，写进 episode.json 的 bg_color；默认 {C.BG_COLOR_NEW}（纯白，视频不用背景图）；"
                         "none = 不写（深藏青底 + 章节背景图，第 1、2 期的样子）")
    ap.add_argument("--layout", default=C.LAYOUT_NEW, choices=["center", "old"],
                    help="版面，写进 episode.json 的 layout：center（默认）= 内容以画面中线居中；old = 不写（内容区 x 440–1860）")
    ap.add_argument("--style", default=C.STYLE_NEW, choices=["board", "cards"],
                    help="画面风格，写进 episode.json 的 style：board（默认）= 白板手写版，画面比声音早 1 秒、字幕 56 px；"
                         "cards = 不写（印刷体卡片版，第 1–4 期）")
    ap.add_argument("--voice", default=C.VOICE_NEW, choices=["user", "tts"],
                    help="配音，写进 episode.json 的 voice_source：user（默认）= 用户自己录；tts = Fish Audio 合成（用户点名要时才用）")
    ap.add_argument("--update-engine", metavar="EPISODE_DIR",
                    help="不新建：把引擎模板重新复制到这个已有的期目录（不动 scenes.js 和 episode.json，被替换的文件移到 _旧稿）")
    C.add_common(ap, episode=False)
    args = ap.parse_args()

    if args.update_engine:
        p = C.Paths(args.update_engine, args.series)
        done = copy_engine(p, update=True)
        for act, rel in done:
            print(f"  {act:5s} 制作/engine/{rel.as_posix()}")
        return

    if args.number is None or not args.title:
        ap.error("新建一期需要 --number 和 --title")
    canvas = C.parse_canvas(args.canvas)
    why = "写成 WxH，例如 2340x1080" if canvas is None else C.canvas_problem(canvas)
    if why:
        ap.error(f"--canvas {args.canvas}：{why}")
    bg_color = None if args.bg_color.strip().lower() in ("none", "") else args.bg_color.strip().upper()
    if bg_color and not re.fullmatch(r"#[0-9A-F]{6}", bg_color):
        ap.error(f"--bg-color {args.bg_color}：写成 #RRGGBB（例如 #FFFFFF），或 none")
    layout = None if args.layout == "old" else args.layout
    style = None if args.style == "cards" else args.style
    voice = args.voice
    series = Path(args.series).resolve()
    dest = Path(args.dest).resolve() if args.dest else series
    dest.mkdir(parents=True, exist_ok=True)
    name = dir_name_for(args.number, args.title)
    ep_dir = dest / name
    if ep_dir.exists():
        sys.exit(f"已存在：{ep_dir}（不会覆盖；换个期号/题目，或手动把旧目录移到 _旧稿）")
    clash = [d.name for d in dest.glob(f"第{args.number:02d}期_*") if d.is_dir()]
    if clash:
        print(f"[警告] {dest} 下已有同期号的目录：{clash}")

    for sub in ("台本", "配音/raw", "配音/segments", "制作/engine", "制作/voice", "制作/build", "封面"):
        (ep_dir / sub).mkdir(parents=True, exist_ok=True)
    p = C.Paths(ep_dir, series)
    ep = episode_skeleton(args.number, args.title, name, args.presenter, canvas, bg_color, layout, style, voice)
    C.write_json(p.episode_json, ep, indent=2)
    pr = C.presenter_of(ep)
    own_gags = [g for g in pr.get("gags") or [] if g not in C.FORBIDDEN_GAGS]
    p.script_data.write_text(SCRIPT_SKELETON.format(number=args.number, title=args.title, scripts=C.SCRIPTS.as_posix(),
                                                    name=pr["name"], voice_name=pr["voice_name"],
                                                    canvas_w=canvas[0], canvas_h=canvas[1],
                                                    look=("背景纯色 " + bg_color + "（episode.json bg_color），不用背景图；" if bg_color
                                                          else "背景是章节背景图（episode.json backgrounds）；")
                                                    + ("内容以画面中线居中（layout center，和字幕同一条线），“中间”就是舞台 x 960。"
                                                       if layout else "内容区 x 440–1860（没有 layout）。"),
                                                    board=("白板版（style board）：画面说明写“手写什么、画什么”（标题、要点、结论边说边写；框、箭头、圈重点），"
                                                           "画面比声音早 1 秒是引擎做的，台本照声音写。" if style else ""),
                                                    gags="".join("、" + g for g in own_gags)), encoding="utf-8")
    done = copy_engine(p)
    print(f"新建：{ep_dir}")
    print(f"  讲解员 {pr['name']}（{pr['id']}），配音 Fish Audio「{pr['voice_name']}」，角色帧 素材/{pr['frames']}")
    print(f"  画面 {canvas[0]}×{canvas[1]}（episode.json canvas；scenes.js 按居中的 1920×1080 内容舞台写坐标；封面照旧 16:9 + 4:3）")
    print("  背景 " + (f"纯色 {bg_color}（episode.json bg_color；视频不用背景图；白板版封面也是白底）" if bg_color
                      else "章节背景图（没写 bg_color）")
          + "；版面 " + ("内容以画面中线居中（layout center）" if layout else "旧版面（没写 layout）")
          + "；风格 " + ("白板手写版（style board，画面早 1 秒、字幕 56 px）" if style else "印刷体卡片版（没写 style）")
          + "；配音 " + ("用户自己录（voice_source user）" if voice == "user" else "Fish Audio 合成（voice_source tts）"))
    print(f"  episode.json、台本/script_data.py 骨架；引擎文件 {sum(1 for a, _ in done if a == 'copy')} 个")
    frames = C.presenter_frames(series, ep)
    if not (frames / "anims.json").exists():
        print(f"[提醒] 讲解员「{pr['name']}」的帧目录还没有 anims.json：{frames}\n"
              "        帧画完之前 sync_assets.py 会报缺帧；出草稿可以临时把 episode.json 的 presenter.frames 指到已有的帧目录，"
              "或 sync_assets.py --allow-missing")
    print("下一步：写 台本/script_data.py，填 episode.json（questions / chapters"
          + ("" if bg_color else " / backgrounds") + "；outro_items 要问用户），然后运行 build_script.py")


if __name__ == "__main__":
    main()
