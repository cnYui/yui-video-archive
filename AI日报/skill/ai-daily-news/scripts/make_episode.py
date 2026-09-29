"""台本.json -> one episode directory the 《原LAI如此》 scripts can process.

    python make_episode.py <期目录>            # reads <期目录>/台本.json
    python make_episode.py <期目录> --check    # only validate 台本.json, write nothing

Writes (never deletes; replaced files go to SERIES/_旧稿/):
  episode.json                 the episode block (chapters / questions / news / outro …), copied into timeline.json later
  台本/script_data.py          SCENES rows ("say", 字幕, TTS, 画面说明) / ("gap", 秒, 画面说明) for build_script.py
  制作/engine/                  the show's engine template (scenes.news.js -> scenes.js)
Then run build_script.py / chunk_voice.py / … with --series D:/大疆/AI日报 (daily.py does all of this).

台本.json (written by Claude during the run; see SKILL.md):
  {date: "2026-09-27", opening: [{text, tts?, expr?}], news: [{headline, org, source, source_short?, date, points[],
   rundown_key?, lines: [{text, tts?, point?, expr?}], refs: [{name, url}]}], closing: [{text, tts?, expr?}]}
"""
import argparse
import json
import re
import shutil
import sys
import time
from datetime import date as Date
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SERIES = SKILL.parent.parent                       # D:/大疆/AI日报
ENGINE_TPL = SKILL / "assets" / "engine-template"
ENGINE_FILES = ["index.html", "core.js", "components.js", "style.css", "sync_assets.py", "check_layout.py", "hand.js", "board.css"]
# 画面风格：board = 白板手写版（scenes.board.js + hand.js；用户 2026-09-28 看过样片后定：从 9/29 那期起用，字比声音早 1 秒）；
# news = 原来的深色卡片版（scenes.news.js，留作退路）。台本.json 可以写 "style" 覆盖。
STYLE_DEFAULT = "board"
BACKGROUNDS = ["01_深海气泡.png", "02_星点.png", "03_波纹.png"]
WEEKDAYS = "一二三四五六日"
EXPR = {"开心", "吃惊", "认真"}
# 用户 2026-09-27：每期 6–8 条；B 站「分段章节」只能加在总时长超过 5 分钟的稿件上。
# chars: 「苏晓晓」(S1) 实测约 6.35 字/秒（829 字 → 130.5 s 配音），加上场景间停顿，正片 5–6 分钟 ≈ 1850–2200 字
# point / bar_label：用户 2026-09-27 要求画面字更大、居中、进度条字数压缩（居中后左右两栏各约 650 px：要点 ≤12 字宽才能到 41 px 以上；进度条短标签 ≤8 字宽）
# chars 下限 2000：「苏晓晓」API 每次生成语速有波动（2026-09-28 实测 6.1–7.1 字/秒），1891 字的一版只有 268 秒，总长不到 5 分钟
LIMITS = dict(headline=14, point=12, bar_label=8, points=(2, 4), news=(3, 8), news_target=6, chars=(2000, 2250), outro_value=30,
              cover_line1=10, cover_line2=8)
CHARS_PER_SEC = 6.35
BAR_COLORS = ["#97C3F0", "#F3C98C", "#4A88DA", "#C6E6FB"]
# 不放“配音 Fish Audio · 苏晓晓（AI 合成）”：用户 2026-09-27 要求片尾也去掉，配音说明只写在简介里
OUTRO_FIXED = [
    {"label": "形象", "value": "大肥鱼同人 · 上善无形 / ZipZipPipe"},
    {"label": "视频制作模型", "value": "Opus 5.5"},
]


def clen(s):
    """display length: CJK = 1, ASCII = 0.55 (the same measure as build_timeline's subtitle wrap)"""
    return sum(0.55 if ord(ch) < 128 else 1 for ch in str(s))


def validate(sc):
    errs, warns = [], []
    need = lambda cond, msg: None if cond else errs.append(msg)
    need(re.fullmatch(r"\d{4}-\d{2}-\d{2}", sc.get("date", "")), "date 要写成 YYYY-MM-DD（发布当天，北京时间）")
    need(sc.get("opening"), "opening 至少一句（开场白 + 串讲）")
    news = sc.get("news") or []
    lo, hi = LIMITS["news"]
    need(lo <= len(news) <= hi, f"news 要 {lo}–{hi} 条（现在 {len(news)}）")
    if lo <= len(news) < LIMITS["news_target"]:
        warns.append(f"只有 {len(news)} 条：目标 {LIMITS['news_target']}–{hi} 条（合格的新闻不够时可以少，但正片会不到 5 分钟，加不了 B 站分段章节）")
    run = ((sc.get("opening") or [{}])[-1].get("text") or "")
    if news and len(run) < 6 * len(news):
        warns.append(f"开场最后一句（串讲）只有 {len(run)} 字：要把 {len(news)} 条都念一遍（每条约 6–10 字），今日要闻卡才看得清")
    for part in ("opening", "closing"):          # 用户 2026-09-27：配音和画面里都不出现“本期配音由 AI 合成”（太割裂）；标识靠投稿时的创作声明 + 简介
        for ln in sc.get(part) or []:
            if re.search(r"AI\s*合成|人工智能合成", ln.get("text", "")):
                errs.append(f"{part}「{ln['text'][:20]}」：配音里不要念 AI 合成提示（用户要求），创作声明和简介里已经有了")
    total = 0
    for part in ("opening", "closing"):
        for ln in sc.get(part) or []:
            need(ln.get("text"), f"{part} 有空句")
            total += len(re.sub(r"\s", "", ln.get("text", "")))
    for i, n in enumerate(news, 1):
        tag = f"第 {i} 条"
        need(n.get("headline"), f"{tag} 没有 headline")
        if not n.get("bar_label") or clen(n["bar_label"]) > LIMITS["bar_label"]:
            errs.append(f"{tag} bar_label「{n.get('bar_label') or ''}」要有，而且 ≤{LIMITS['bar_label']} 字宽（底部进度条的短标签，如“OpenAI 停训”）")
        if clen(n.get("headline", "")) > LIMITS["headline"]:
            errs.append(f"{tag} headline「{n.get('headline')}」超过 {LIMITS['headline']} 字宽（目录、标题卡放不下）")
        pts = n.get("points") or []
        a, b = LIMITS["points"]
        need(a <= len(pts) <= b, f"{tag} points 要 {a}–{b} 条")
        for p in pts:
            if clen(p) > LIMITS["point"]:
                errs.append(f"{tag} 要点「{p}」超过 {LIMITS['point']} 字宽")
        lines = n.get("lines") or []
        need(len(lines) >= 2, f"{tag} 至少两句")
        used = {ln.get("point") for ln in lines if ln.get("point") is not None}
        for j in range(len(pts)):
            if j not in used:
                warns.append(f"{tag} 要点 {j + 1} 没有对应的句子（会按顺序挂在第 {j + 2} 句）")
        for ln in lines:
            need(ln.get("text"), f"{tag} 有空句")
            if ln.get("expr") and ln["expr"] not in EXPR:
                errs.append(f"{tag} expr「{ln['expr']}」不在 {sorted(EXPR)} 里")
            total += len(re.sub(r"\s", "", ln.get("text", "")))
        refs = [r for r in n.get("refs") or [] if r.get("url")]
        need(refs, f"{tag} 没有来源网址（refs）")
        need(n.get("source"), f"{tag} 没有 source（卡片上显示的来源）")
    lo, hi = LIMITS["chars"]
    msg = f"全片约 {total} 字，按每秒 {CHARS_PER_SEC} 字约 {total / CHARS_PER_SEC / 60:.1f} 分钟；目标正片 5–6 分钟（约 {lo}–{hi} 字）"
    if total < lo and len(news) >= LIMITS["news_target"]:
        errs.append(msg + "：6 条以上时要写够，总时长超过 5 分钟才能加 B 站分段章节")
    elif not lo <= total <= hi:
        warns.append(msg)
    for pat, why in ((r"不是.{1,12}而是", "不用“不是……而是……”句式"), (r"炸裂|王炸|史诗级|颠覆|震撼", "不用夸张词")):
        for part in ("opening", "closing"):
            for ln in sc.get(part) or []:
                if re.search(pat, ln.get("text", "")):
                    warns.append(f"{part}「{ln['text'][:20]}」：{why}")
        for n in news:
            for ln in n.get("lines") or []:
                if re.search(pat, ln.get("text", "")):
                    warns.append(f"「{ln['text'][:20]}」：{why}")
    # 封面（用户 2026-09-28）：一条新闻两行大字（灰色铺垫 + 蓝色钩子），不写日期；其余新闻由封面脚本自动列成小字
    cv = sc.get("cover")
    if not isinstance(cv, dict):
        errs.append('要写 cover：{"item": 大字讲第几条（1 起）, "line1": "铺垫（≤10 字宽）", "line2": "钩子（≤8 字宽）", '
                    '"mood": "吃惊|开心|疑问|认真"}；封面不写日期（标题里有）')
    else:
        need(isinstance(cv.get("item"), int) and 1 <= cv["item"] <= len(news), f"cover.item 要是 1–{len(news)} 的整数")
        need(cv.get("line2"), "cover.line2（彩色大字那一行）不能空")
        for key, lim, hard in (("line1", LIMITS["cover_line1"], 13), ("line2", LIMITS["cover_line2"], 10)):
            w = clen(cv.get(key) or "")
            if w > hard:
                errs.append(f"cover.{key}「{cv.get(key)}」{w:g} 字宽，太长（信息流里看不清），改到 ≤{lim}")
            elif w > lim:
                warns.append(f"cover.{key}「{cv.get(key)}」{w:g} 字宽，建议 ≤{lim}（会自动缩小字号）")
        need(cv.get("mood", "吃惊") in ("吃惊", "开心", "疑问", "认真"), "cover.mood 只能是 吃惊 / 开心 / 疑问 / 认真")
        if re.search(r"\d+\s*月\s*\d+\s*日|周[一二三四五六日天]", (cv.get("line1") or "") + (cv.get("line2") or "")):
            errs.append("封面文案里不写日期（用户 2026-09-28：和标题重复）")
    if (sc.get("style") or STYLE_DEFAULT) == "board" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", sc.get("date", "")):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from hand_glyphs import collect
        d = Date.fromisoformat(sc["date"])
        missing = collect(hand_texts(f"{d.month}月{d.day}日", [n.get("headline", "") for n in news],
                                     [p for n in news for p in n.get("points") or []]))["missing"]
        if missing:
            errs.append(f"白板手写没有这些字的笔画：{''.join(missing)}（标题、要点换个说法或换成常用字）")
    return errs, warns, total


def row(ln, extra_note=""):
    note = extra_note
    if ln.get("expr"):
        note = (note + " " if note else "") + f"【动作：{ln['expr']}】"
    return ("say", ln["text"].strip(), (ln.get("tts") or ln["text"]).strip(), note)


def outro_sources(news):
    names = []
    for n in news:
        for r in n.get("refs") or []:
            nm = (r.get("name") or "").strip()
            if nm and nm not in names:
                names.append(nm)
    rows, cur = [], ""
    for nm in names:
        cand = f"{cur} · {nm}" if cur else nm
        if clen(cand) <= LIMITS["outro_value"]:
            cur = cand
        else:
            rows.append(cur)
            cur = nm
    if cur:
        rows.append(cur)
    if len(rows) > 2:            # the outro holds 6 rows; keep 2 for sources and say where the rest is
        rows = rows[:2]
        rows[1] = (rows[1] + " 等")[: int(LIMITS["outro_value"])]
    return [{"label": "新闻来源" if i == 0 else "来源（续）", "value": v} for i, v in enumerate(rows)]


def hand_texts(date_label, headlines, points):
    """every string scenes.board.js writes by hand (keep in step with it)"""
    return [date_label, "今天说这几件事", "今日回顾", "一二三四五六七八九十、", "0123456789"] + list(headlines) + list(points)


def write_handdata(path, episode):
    """制作/engine/handdata.js: the handwriting strokes for a board episode; a null stub otherwise (the page always loads it)"""
    if episode is None:
        Path(path).write_text("// 深色卡片版：不用手写\nwindow.__HAND__ = null;\n", encoding="utf-8")
        return
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from hand_glyphs import build_hand_js
    news = episode.get("news") or []
    d = build_hand_js(hand_texts(episode["date_label"], [n["headline"] for n in news], [p for n in news for p in n.get("points") or []]), path)
    if d["missing"]:
        print(f"  ! 手写没有这些字的笔画，会留空：{''.join(d['missing'])}")


def archive(path):
    path = Path(path)
    if not path.exists():
        return
    dst = SERIES / "_旧稿" / f"{path.parent.name}_{time.strftime('%Y%m%d-%H%M%S')}" / path.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path), str(dst))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dir")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    ep_dir = Path(args.episode_dir).resolve()
    if ep_dir.parent != SERIES.resolve():
        sys.exit(f"期目录必须直接放在 {SERIES} 下（引擎按 ../../../素材/ 找素材）：{ep_dir}")
    sc = json.loads((ep_dir / "台本.json").read_text(encoding="utf-8"))
    errs, warns, total = validate(sc)
    for w in warns:
        print("  ! " + w)
    if errs:
        print("\n".join("  ✗ " + e for e in errs))
        sys.exit(f"台本.json 有 {len(errs)} 处要改")
    print(f"台本.json 检查通过：{len(sc['news'])} 条，约 {total} 字（约 {total / CHARS_PER_SEC / 60:.1f} 分钟）")
    if args.check:
        return

    d = Date.fromisoformat(sc["date"])
    label = f"{d.month}月{d.day}日"
    news = sc["news"]
    ids = [f"S{i:02d}" for i in range(1, len(news) + 3)]      # S01 开场, S02.. 新闻, 最后 回顾
    scenes = [dict(id=ids[0], title="开场", rows=[row(ln, "日期大字；串讲时今日要闻卡逐张出现，飞进右上目录" if k == len(sc["opening"]) - 1 else "")
                                              for k, ln in enumerate(sc["opening"])])]
    news_ep = []
    for i, n in enumerate(news):
        rows = [row(ln, "标题卡" if k == 0 else (f"要点 {ln['point'] + 1}" if ln.get("point") is not None else ""))
                for k, ln in enumerate(n["lines"])]
        rows.append(("gap", 0.5, "停顿；目录打勾"))
        scenes.append(dict(id=ids[i + 1], title=n["headline"], rows=rows))
        news_ep.append({k: n.get(k) for k in ("headline", "org", "source", "source_short", "date", "points", "rundown_key") if n.get(k)}
                       | {"line_points": [ln.get("point") for ln in n["lines"]], "refs": n.get("refs") or []})
    closing = [row(ln, "今日回顾卡") for ln in sc.get("closing") or [{"text": "来源都在简介里。"}]]
    closing.append(("gap", 2.0, "今日回顾卡停留（结尾那句太短，不停一下卡片看不清）"))
    scenes.append(dict(id=ids[-1], title="回顾", rows=closing))

    episode = {
        "number": d.month * 100 + d.day,
        "title": f"{label}，鲸鱼娘带你看看AI圈发生了什么？",
        "dir_name": f"AI每日日报_{d:%m%d}",
        "date": sc["date"], "date_label": label, "weekday": "周" + WEEKDAYS[d.weekday()],
        "subtitle": "鲸鱼娘带你看看 AI 圈发生了什么",
        # 不写 ai_notice：用户 2026-09-27 要求配音和画面里都不出现“本期配音由 AI 合成”（AI 标识靠 B 站创作声明 + 简介说明）
        "target_minutes": [5, 6],
        "question_scene": ids[0],
        "questions": [{"text": n["headline"], "scenes": [ids[i + 1]]} for i, n in enumerate(news)],
        "chapters": {ids[0]: "开场", **{ids[i + 1]: n["headline"] for i, n in enumerate(news)}, ids[-1]: "回顾"},
        "bar_labels": {ids[0]: "开场", **{ids[i + 1]: n.get("bar_label") or n["headline"] for i, n in enumerate(news)}, ids[-1]: "回顾"},
        "backgrounds": {sid: BACKGROUNDS[k % len(BACKGROUNDS)] for k, sid in enumerate(ids)},
        "bg_alpha": 0.9, "bg_blur": 0,
        "intro_tagline": "",
        "outro_items": outro_sources(news) + OUTRO_FIXED,
        "outro_closing": "感谢大家看到最后",
        "auto_gestures": False,
        # 《原LAI如此》脚本的讲解员预设（epcommon.PRESENTERS["whale"]：自称鲸鱼娘、别名大肥鱼、音色苏晓晓）；
        # 帧目录用本系列的 素材/角色/动作帧（联接到大肥鱼像素素材包/素材）
        "presenter": {"id": "whale", "frames": "角色/动作帧"},
        "badge_html": f'AI每日日报<span class="n">{d:%m.%d}</span>',
        "toc_kicker_html": "<b>今日要闻</b>TODAY",
        "bar_colors": BAR_COLORS,
        "news": news_ep,
        "style": sc.get("style") or STYLE_DEFAULT,
    }
    ep_json = ep_dir / "episode.json"
    archive(ep_json)
    ep_json.write_text(json.dumps(episode, ensure_ascii=False, indent=2), encoding="utf-8")

    sd = ep_dir / "台本" / "script_data.py"
    sd.parent.mkdir(parents=True, exist_ok=True)
    archive(sd)
    body = ["# 由 make_episode.py 从 台本.json 生成；要改台词请改 台本.json 再重跑", "SCENES = ["]
    for s in scenes:
        body.append(f"    dict(id={s['id']!r}, title={s['title']!r}, rows=[")
        body += [f"        {r!r}," for r in s["rows"]]
        body.append("    ]),")
    body.append("]")
    sd.write_text("\n".join(body) + "\n", encoding="utf-8")

    eng = ep_dir / "制作" / "engine"
    eng.mkdir(parents=True, exist_ok=True)
    for f in ENGINE_FILES:
        shutil.copy2(ENGINE_TPL / f, eng / f)
    board = episode["style"] == "board"
    shutil.copy2(ENGINE_TPL / ("scenes.board.js" if board else "scenes.news.js"), eng / "scenes.js")
    write_handdata(eng / "handdata.js", episode if board else None)
    print(f"-> {ep_json}\n-> {sd}\n-> {eng}（引擎 + scenes.js，{'白板手写版' if board else '深色卡片版'}）")
    print(f"片尾清单：{'；'.join(it['label'].strip() + ' ' + it['value'] for it in episode['outro_items'])}")


if __name__ == "__main__":
    main()
