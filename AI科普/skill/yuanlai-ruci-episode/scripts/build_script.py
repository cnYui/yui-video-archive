"""Build 台本/台本.md and 台本/配音分段.json from 台本/script_data.py (the one source of truth).

  python build_script.py <episode_dir> [--series D:/大疆/AI科普]

台本.md       结构表、本期目录、分场台本（时间 = 按语速估算的正片时间，epcommon.CPS）、角色动作用量、制作说明
配音分段.json  [{id, scene, text, tts_text, est_seconds, start}]：配音与字幕的分段（段号 S03-12）
Also checks: the opening line 「大家好，我是{讲解员}」 (episode.json presenter.name; 山田凉 when there is no presenter) and
「我是<别的讲解员 / 别名>」 anywhere (e.g. “我是山田凉” in a 鲸鱼娘 episode), unknown 【动作：xxx】 words, the action usage tier
of 动作 v2 (epcommon.ACTION_LIMITS: total, one per row, big actions and their spacing, stickers, 好耶 at least once, 小跳 only
in a gap, 走动 only for the opening walk-in, 挥手 only in the first / last scene, 数一→数二→数三 in order, the same body
action in 3 rows running, 点头 / 摇头 next to a hand gesture, 叉腰 and 收到 in one chapter, a whole-row 开心 longer than
4 s), whether the words' frames are in the presenter's frame folder (presenter.frames; or only in a preview overlay),
off-topic character gags, “待写” placeholders, episode.json questions / chapters / backgrounds that point at missing scenes
or files, and the estimated length against episode.json target_minutes.
"""
import argparse
import datetime
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402

LIMITS = getattr(C, "ACTION_LIMITS", {})
TYPE_CN = {"body": "身体", "expr": "表情", "pose": "贴纸", "anim": "动画", "head": "头部", "auto": "控制"}


def vocab_use(w):
    return C.ACTIONS[w].get("use", "")


def presenter(ep):
    """epcommon.presenter_of (older epcommon without presenters: 山田凉)"""
    if hasattr(C, "presenter_of"):
        return C.presenter_of(ep)
    return dict(id="ryo", name="山田凉", frames="角色/动作帧", voice_name="山田凉", voice_page="", voice_app="",
                desc="", aliases=[], gags=[])


def _flat(s):
    """text for the opening check: no spaces, ASCII comma / period as full-width"""
    return re.sub(r"\s+", "", str(s or "")).replace(",", "，").replace(".", "。")


def check_presenter_lines(scenes, pr, warns, explicit=True):
    """Opening line 「大家好，我是{name}」 (subtitle and TTS) + 「我是<other name>」 anywhere."""
    name = pr.get("name") or "山田凉"
    want = f"大家好，我是{name}"
    src = "episode.json presenter" if explicit else "episode.json 没写 presenter，默认山田凉"
    first = next((r for sc in scenes for r in sc["rows"] if r["kind"] == "say"), None)
    if first is not None:
        for label, txt in (("字幕", first["text"]), ("TTS", first["tts"])):
            if not _flat(txt).startswith(want):
                warns.append(f"{first['id']}：开场白{label}应以“{want}。”开头（本期讲解员：{name}，{src}），现在是“{str(txt)[:24]}”")
    others = C.other_names(pr) if hasattr(C, "other_names") else []
    for sc in scenes:
        for r in sc["rows"]:
            if r["kind"] != "say":
                continue
            for n in others:
                if f"我是{n}" in _flat(r["text"]) or f"我是{n}" in _flat(r["tts"]):
                    warns.append(f"{r['id']}：台词里有“我是{n}”，本期讲解员是{name}（{src}）")


def build(p):
    ns = C.load_script(p)
    ep = C.load_episode(p)
    pr = presenter(ep)
    scenes = C.walk_script(ns["SCENES"])
    intro, outro = C.pack_durations(p)
    warns = []
    check_presenter_lines(scenes, pr, warns, explicit=bool(ep.get("presenter")))
    t, voice, md_scenes, units_total = 0.0, [], [], 0
    used = Counter()
    where_used = {}
    events = []                     # (t, word, row id, scene id, row kind, row index in the whole script)
    rows_acts = []                  # (row id, scene, kind, acts)
    k_row = 0
    for sc in scenes:
        start, rows_md = t, []
        for r in sc["rows"]:
            acts, w = C.parse_actions(r["visual"])
            warns += [f"{sc['id']}：{x}" for x in w]
            rid = r.get("id") or f"{sc['id']} 停顿 {C.fmt(t)}"
            dur = r["dur"] if r["kind"] == "gap" else round(C.est_seconds(r["tts"]), 1)
            for a in acts:
                lw = (LIMITS.get("long_whole") or {}).get(a["word"])
                if lw and a.get("anchor") == "whole" and r["kind"] == "say" and dur > lw:
                    warns.append(f"{rid}：{a['word']}整段约 {dur:.1f}s，超过 {lw:.0f}s 一直眯眼说话会显得呆："
                                 f"写【动作：{a['word']}@末尾】（只占最后 2 s），或配一个手势")
                used[a["word"]] += 1
                where_used.setdefault(a["word"], []).append(rid)
                at = t + (max(0.0, dur - a.get("dur", 0)) if a.get("anchor") == "end" else 0.0)
                events.append((at, a["word"], rid, sc["id"], r["kind"], k_row))
            rows_acts.append((rid, sc["id"], r["kind"], acts))
            k_row += 1
            for g in C.gag_hits(r["visual"], pr.get("gags")) + C.gag_hits(r.get("text", ""), pr.get("gags")):
                warns.append(f"{sc['id']}：出现和知识无关的角色梗「{g}」")
            if r["kind"] == "gap":
                rows_md.append(f"| {C.fmt(t)}–{C.fmt(t + r['dur'])} | （画面） | {C.md_cell(r['visual'])} |")
                t += r["dur"]
                continue
            if "待写" in r["text"] or "TODO" in r["text"]:
                warns.append(f"{r['id']}：台词还是占位（待写）")
            units_total += C.spoken_units(r["tts"])
            voice.append(dict(id=r["id"], scene=sc["id"], text=r["text"], tts_text=r["tts"],
                              est_seconds=dur, start=round(t, 1)))
            rows_md.append(f"| {C.fmt(t)}–{C.fmt(t + dur)} | **{r['id']}** {C.md_cell(r['text'])} | {C.md_cell(r['visual'])} |")
            t += dur + C.SEG_GAP
        md_scenes.append((sc, start, t, rows_md))

    ids = {sc["id"] for sc in scenes}
    for i, q in enumerate(ep.get("questions", []), 1):
        for s in q.get("scenes", []):
            if s not in ids:
                warns.append(f"episode.json questions[{i}] 指向不存在的场景 {s}")
    if ep.get("questions") and ep.get("question_scene") not in ids:
        warns.append(f"episode.json question_scene={ep.get('question_scene')!r} 不是台本里的场景")
    for k in list(ep.get("chapters", {})) + list(ep.get("backgrounds", {})):
        if k not in ids:
            warns.append(f"episode.json 里的 {k} 不是台本里的场景")
    bg_files, bg_auto = C.fill_backgrounds(p, ep, [sc["id"] for sc in scenes], warns)
    for sc in scenes:
        if sc["id"] not in ep.get("chapters", {}):
            warns.append(f"episode.json chapters 没写 {sc['id']}（进度条先用场景名「{sc['title']}」）")
    total = intro + t + outro
    lo, hi = ep.get("target_minutes", [5, 7])
    if not lo * 60 <= total <= hi * 60:
        warns.append(f"预计总长 {C.fmt(total)} 不在目标 {lo}–{hi} 分钟内")
    usage = check_usage(p, ep, scenes, rows_acts, events, t, warns)
    return dict(ns=ns, ep=ep, pr=pr, scenes=scenes, bg_files=bg_files, bg_auto=bg_auto, voice=voice, md_scenes=md_scenes, main=t,
                total=total, intro=intro, outro=outro, units=units_total, used=used, where_used=where_used, warns=warns, usage=usage)


def check_usage(p, ep, scenes, rows_acts, events, main, warns):
    """动作用量（SPEC F.5 / F.7，上限在 epcommon.ACTION_LIMITS）。Returns a summary dict for 台本.md."""
    if not LIMITS:                       # older epcommon without the v2 tier: nothing to check
        return {}
    A = C.ACTIONS
    total = sum(C.action_units(acts) for _, _, _, acts in rows_acts)
    big = sorted((t, w, rid) for t, w, rid, *_ in events if A[w].get("big"))
    stickers = [(t, w, rid, sid, k) for t, w, rid, sid, _, k in events if A[w].get("sticker")]
    first, last = (scenes[0]["id"], scenes[-1]["id"]) if scenes else (None, None)
    lo, hi = LIMITS["total"]
    mins = max(main / 60, 1e-6)
    if total > LIMITS["total_warn"]:
        warns.append(f"台本动作 {total} 个，超过 {LIMITS['total_warn']}（建议 {lo}–{hi} 个，约 12–18 s 一个）：删掉一些，别让动作喧宾夺主")
    elif total < lo:
        warns.append(f"台本动作只有 {total} 个（建议 {lo}–{hi} 个，约 12–18 s 一个）：用户要的是“不只是站着读稿”，"
                     f"在列举、指向内容、下结论、抛问题的地方再加一些（自动层只管小动作）")
    # one per row
    for rid, sid, kind, acts in rows_acts:
        n = C.action_units(acts)
        if n > LIMITS["per_row"]:
            warns.append(f"{rid}：一段写了 {n} 个动作（{'、'.join(a['word'] for a in acts)}），一段最多 {LIMITS['per_row']} 个"
                         "（身体动作+表情算 1 个）")
        heads = [a for a in acts if a["type"] == "head"]
        bodies = [a for a in acts if a["type"] in ("body", "pose", "anim")]
        if heads and bodies:
            warns.append(f"{rid}：{heads[0]['word']} 和 {bodies[0]['word']} 同一段：头部动作只在手放下时才播，会被手势盖掉")
        if kind == "say":
            for a in acts:
                if A[a["word"]].get("gap_only"):
                    warns.append(f"{rid}：{a['word']} 只放在 gap（停顿）里，不放在台词段")
    # per-word limits and minimums
    cnt = Counter(w for _, w, *_ in events)
    for w, mx in LIMITS.get("per_word", {}).items():
        if cnt.get(w, 0) > mx:
            warns.append(f"{w} 用了 {cnt[w]} 次，全片上限 {mx} 次")
    for w, mn in LIMITS.get("min_word", {}).items():
        if cnt.get(w, 0) < mn:
            warns.append(f"{w} 一次都没用：用户点名保留了「好耶」的拉炮，讲完一题或总结时至少放 {mn} 次（常写 好耶@末尾）"
                         if w == "好耶" else f"{w} 至少用 {mn} 次")
    # big actions
    if len(big) > LIMITS["big_total"]:
        warns.append(f"大动作（{'、'.join(BIG_LIST())}）一共 {len(big)} 个，全片上限 {LIMITS['big_total']}")
    for (t0, w0, r0), (t1, w1, r1) in zip(big, big[1:]):
        if t1 - t0 < LIMITS["big_spacing"] and not (A[w0].get("count") and A[w1].get("count")):
            warns.append(f"大动作太近：{r0} {w0}（约 {C.fmt(t0)}）和 {r1} {w1}（约 {C.fmt(t1)}）相隔 {t1 - t0:.1f}s，"
                         f"建议 ≥ {LIMITS['big_spacing']:.0f}s（按估算时长，配音后 build_timeline 会再查）")
    # stickers
    if len(stickers) > LIMITS["sticker_total"]:
        warns.append(f"贴纸姿势（疑问 / 收到 / 好耶）一共 {len(stickers)} 个，全片上限 {LIMITS['sticker_total']}")
    per_ch = Counter(sid for _, _, _, sid, _ in stickers)
    for sid, n in per_ch.items():
        if n > LIMITS["sticker_per_chapter"]:
            warns.append(f"{sid}：贴纸姿势 {n} 个，每章最多 {LIMITS['sticker_per_chapter']} 个")
    ks = sorted(set(k for *_, k in stickers))
    for a, b in zip(ks, ks[1:]):
        if b - a == 1:
            warns.append(f"相邻两段都是贴纸姿势（{next(r for _, _, r, _, k in stickers if k == a)} → "
                         f"{next(r for _, _, r, _, k in stickers if k == b)}）：中间隔开")
    # pairs that read alike (叉腰 / 收到: a hand on the hip) never in one chapter
    for w0, w1 in LIMITS.get("not_same_chapter", []):
        for sid in sorted({e[3] for e in events if e[1] == w0} & {e[3] for e in events if e[1] == w1}):
            warns.append(f"{sid}：「{w0}」和「{w1}」在同一章里（看起来都是手叉腰），换掉一个")
    # walk: only the opening walk-in
    for t, w, rid, sid, kind, k in events:
        if w == "走动" and not (sid == first and kind == "gap" and t <= 0.01):
            warns.append(f"{rid}：走动只用于开场走入（第一场第 0 秒的 gap），章节转场不走动")
        if w == "挥手" and sid not in (first, last):
            warns.append(f"{rid}：挥手只用于开场问好（第一场）和结尾道谢（最后一场）")
    # counting groups: 数一 -> 数二 -> 数三 in order
    groups, expect = 0, None
    for t, w, rid, *_ in sorted(events):
        c = A[w].get("count")
        if not c:
            continue
        if c == 1:
            groups += 1
            expect = 2
        elif expect == c:
            expect = c + 1
        else:
            warns.append(f"{rid}：{w} 前面没有{'数一' if c == 2 else '数二'}（数一 → 数二 → 数三 按顺序成组用）")
            expect = None
    if groups > LIMITS["count_groups"]:
        warns.append(f"数一/数二/数三 用了 {groups} 组，全片最多 {LIMITS['count_groups']} 组（只在台词真的在列举时用）")
    # the same body action in 3 rows running
    run, prev = 0, None
    for rid, sid, kind, acts in rows_acts:
        names = [a["name"] for a in acts if a["type"] == "body"]
        cur = names[0] if names else None
        run = run + 1 if cur and cur == prev else (1 if cur else 0)
        if cur and run == LIMITS["same_body_run"] + 1:
            warns.append(f"{rid}：{next(a['word'] for a in acts if a['type'] == 'body')} 连续 {run} 段了，换一个或空一段")
        prev = cur
    # frames: in the presenter's frame folder (final), only in the preview overlay, or missing
    status = {}
    if hasattr(C, "sprite_keys"):
        pr = presenter(ep)
        base, _extra = C.sprite_dirs(p.series, ep)
        try:
            where = "素材/" + base.resolve().relative_to((Path(p.series) / "素材").resolve()).as_posix()
        except ValueError:
            where = base.as_posix()
        final, prev_keys = C.sprite_keys(p.series, ep)
        if not (base / "anims.json").exists():
            warns.append(f"讲解员「{pr['name']}」的帧目录 {where}/ 还没有 anims.json（帧还没画完？）：下面用到的动作都算缺帧，"
                         "sync_assets.py 会报缺帧；只出草稿可以加 --allow-missing，或临时把 presenter.frames 指到已有的帧目录")
        for w in sorted(cnt):
            st = C.frame_status(w, final, prev_keys)
            status[w] = st
            if st == "preview":
                warns.append(f"「{w}」的帧还在预览目录（episode.json sprites_extra）里，没追加进 {where}/："
                             f"用户确认新动作帧之前只能出样片")
            elif st == "missing" and final:
                warns.append(f"「{w}」没有{pr['name']}的帧（{where}/ 和 sprites_extra 里都没有）：sync_assets.py 会报缺帧")
    return dict(total=total, big=len(big), stickers=len(stickers), per_min=total / mins, groups=groups, status=status)


def BIG_LIST():
    return getattr(C, "BIG_WORDS", [])


def bg_label(b, sid):
    f = b["bg_files"].get(sid)
    if not f:
        return "（无：背景图库为空）"
    return f"{f}（未指定，按图库顺序轮换）" if sid in b["bg_auto"] else f


def auto_label(ep):
    ag = ep.get("auto_gestures", None)
    if ag is False:
        return "关（episode.json auto_gestures = false）"
    if isinstance(ag, dict):
        return "开，" + "，".join(f"{k}={v}" for k, v in ag.items())
    return "开（默认：说话时小手势约 6/分、句末点头约 3/分、看向内容约 2/分）" if ag is not None else \
        "（episode.json 没写 auto_gestures：新引擎按「开」处理，建议写上 true）"


def render_md(p, b):
    ns, ep, pr = b["ns"], b["ep"], b["pr"]
    speech = sum(v["est_seconds"] for v in b["voice"])
    lo, hi = ep.get("target_minutes", [5, 7])
    gags = "、".join(list(C.FORBIDDEN_GAGS) + [g for g in pr.get("gags") or [] if g not in C.FORBIDDEN_GAGS])
    L = [f"# 《原LAI如此》第 {ep['number']} 期「{ep['title']}」台本\n"]
    L.append(f"- 生成：{datetime.date.today().isoformat()}，由 `scripts/build_script.py` 从 `台本/script_data.py` 生成（改台本请改 script_data.py，不要手改本文件）")
    L.append(f"- 预计总长：**{C.fmt(b['total'])}**（片头 {b['intro']} s + 正片 {C.fmt(b['main'])} + 片尾 {b['outro']} s；目标 {lo}–{hi} 分钟）。配音按每秒 {C.CPS} 字估算，配好后以实测为准")
    L.append(f"- 台词：{len(b['voice'])} 段，约 {b['units']} 字，配音约 {speech:.0f} 秒")
    L.append(f"- **本期讲解员：{pr['name']}**——{pr.get('desc') or '像素形象'}。角色帧 `素材/{pr.get('frames')}`"
             f"（episode.json `presenter`）；开场白“大家好，我是{pr['name']}。今天给大家介绍……”。")
    L.append(f"- **配音音色：Fish Audio「{pr.get('voice_name') or '（未设置）'}」**"
             + (f"（音色 id {C.voice_id_of(pr)}，API 生成，模型 s1）" if C.voice_id_of(pr) else "")
             + (f"：音色页 {pr['voice_page']}" if pr.get("voice_page") else "")
             + "。")
    L.append(f"- 讲解员左下角固定位置、不镜像。台本动作只用下面词表里的词；说话时的小手势、句末点头、看向内容由引擎的自动层加，不用写。不用和知识无关的角色梗（{gags}）。")
    L.append(f"- 背景：素材/背景图库，每章一张，进入新章节时交叉淡化；不透明度 {ep.get('bg_alpha', 0.22)}、模糊 {ep.get('bg_blur', 10)} px。")
    for n in ns.get("NOTES", []) or []:
        L.append(f"- {n}")
    L.append("")

    if ep.get("questions"):
        L.append("## 本期目录（右上角）\n")
        L.append(f"在 {ep.get('question_scene', 'S02')} 最后一句结束时由疑问卡飞入右上角；讲到哪一题高亮哪一题，这一题的最后一个章节结束时打勾。\n")
        L.append("| # | 疑问 | 对应章节 |")
        L.append("|---|---|---|")
        for i, q in enumerate(ep["questions"], 1):
            L.append(f"| {i} | {q.get('text', '')} | {'、'.join(q.get('scenes', []))} |")
        L.append("")

    L.append("## 结构\n")
    L.append("| 场 | 时间（正片） | 内容 | 进度条章节名 | 背景 |")
    L.append("|---|---|---|---|---|")
    for sc, s, e, _ in b["md_scenes"]:
        L.append(f"| {sc['id']} | {C.fmt(s)}–{C.fmt(e)} | {sc['title']} | {ep.get('chapters', {}).get(sc['id'], sc['title'])} | {bg_label(b, sc['id'])} |")
    L.append("")

    L.append("## 分场台本\n")
    L.append("说明：时间是正片时间（不含片头）。粗体编号是配音段，后面的文字就是字幕。画面说明里的【动作：xxx】会变成角色动作，"
             "其余时间说话时动嘴、不说话时待机呼吸，再加上自动层的小动作。\n")
    for sc, s, e, rows in b["md_scenes"]:
        L.append(f"### {sc['id']}｜{sc['title']}｜{C.fmt(s)}–{C.fmt(e)}\n")
        L.append(f"- 背景：{bg_label(b, sc['id'])}")
        L.append(f"- 角色：{sc['char'] or '说话'}\n")
        L.append("| 时间 | 台词（＝字幕） | 画面 |")
        L.append("|---|---|---|")
        L.extend(rows)
        L.append("")

    L.append("## 制作说明\n")
    u = b.get("usage") or {}
    L.append("### 角色动作（词表见 references/pipeline-contract.md §4）\n")
    if u:
        lo_n, hi_n = LIMITS["total"]
        L.append(f"- 本期台本动作 **{u['total']} 个**（建议 {lo_n}–{hi_n} 个，超过 {LIMITS['total_warn']} 警告），约每分钟 {u['per_min']:.1f} 个；"
                 f"大动作 {u['big']} 个（≤{LIMITS['big_total']}，间隔 ≥{LIMITS['big_spacing']:.0f} s）；贴纸姿势 {u['stickers']} 个（≤{LIMITS['sticker_total']}，每章 ≤1）。")
    L.append(f"- 自动层：{auto_label(ep)}。嫌多先把 episode.json 的 `auto_gestures` 调成 `{{\"gesture\": 0.6}}` 或关掉某个通道（`nod` / `look` 设 false）；"
             "某一段要安静就写【动作：不动】。")
    L.append("- 写法：`【动作：抬手】`；`@末尾` 放在这一段结尾；`@短语` 从这句话里那个短语开始（`【动作：数一@第一】`）；"
             "`@整段` 覆盖整段（看右边）；`+` 身体动作加表情（`【动作：摇头+认真】`，算 1 个）。一段最多 1 个动作。\n")
    L.append("| 台本写法 | 别名 | 效果 | 什么时候用 | 上限 | 本期次数 |")
    L.append("|---|---|---|---|---|---|")
    alias_of = {}
    for k, v in C.ALIASES.items():
        if v in C.ACTIONS and not k.isascii():
            alias_of.setdefault(v, []).append(k)
    per_word = LIMITS.get("per_word", {})
    status = u.get("status", {})
    for w, a in C.ACTIONS.items():
        eff = f"{TYPE_CN.get(a['type'], a['type'])} {a['name']}，" + ("整段" + (f"（≤{a['max']:.0f} s）" if a.get("max") else "")
                                                                   if a.get("whole") else f"{a['dur']} s")
        if a.get("at") == "end" and not a.get("whole"):
            eff += "，默认 @末尾"
        if a.get("lip") is False:
            eff += "，不对口型"
        where = "、".join(b["where_used"].get(w, []))
        cap = per_word.get(w)
        cap = f"≤{cap}" if cap else ("贴纸合计 ≤4" if a.get("sticker") else "—")
        if a.get("big"):
            cap += "（大动作）"
        tag = {"preview": "（帧待确认）", "missing": "（缺帧）"}.get(status.get(w), "")
        L.append(f"| 【动作：{w}】 | {'、'.join(alias_of.get(w, [])) or '—'} | {eff} | {vocab_use(w)} | {cap} | "
                 f"{b['used'].get(w, 0)}{tag}{('（' + where + '）') if where else ''} |")
    L.append("")
    L.append(f"- {pr['name']} ×5 最近邻放大，站左下角，全片同一位置同一大小，不镜像翻转；走动只用于开场走入，不让位。")
    L.append(f"- 不用：{gags}等和知识无关的角色梗。\n")

    L.append("### 背景\n")
    for sc, _s, _e, _ in b["md_scenes"]:
        L.append(f"- {sc['id']} {sc['title']}：{bg_label(b, sc['id'])}")
    L.append(f"- 处理：叠在深藏青 #1B2340 上，不透明度 {ep.get('bg_alpha', 0.22)}、模糊 {ep.get('bg_blur', 10)} px、暗角 15%；换章节时 0.8 s 交叉淡化。\n")

    L.append("### 画面风格\n")
    L.append("- 左上只有「原LAI如此 #%02d」；右上「本期目录」；左下角色；底部字幕按整个画面水平居中；最底《孤独摇滚！》四色章节进度条（整片时间，含片头片尾）。" % ep["number"])
    L.append("- 文字卡片：纸白底、墨黑字、橙色强调，和片头片尾同一套“终端小票”配色。每个要点一张卡，编号清楚。")
    L.append("- 代码卡：墨黑底 + JetBrains Mono，右上角标“示意·已简化”；Key 一律打码（sk-••••）。")
    L.append("- App、工具界面都用虚构示意，不用真实 App 截图和 logo。")
    L.append("- 音效只用两种：新章节卡片出现的轻“嗒”声、目录打勾声。BGM 无人声轻音乐，说话时压低。\n")

    L.append("### 配音\n")
    L.append(f"- 音色：Fish Audio「{pr.get('voice_name') or '（未设置）'}」（本期讲解员 {pr['name']}"
             + (f"，音色 id {C.voice_id_of(pr)}" if C.voice_id_of(pr) else "")
             + "），模型 s1。音色页上的示例可能是别的模型生成的，以 s1 实际效果为准。")
    L.append("- 按 `台本/配音分段.json` 的 `tts_text` 生成，字幕用 `text`。用 Fish Audio API 整期一次生成："
             "`scripts/chunk_voice.py --whole` → `scripts/tts_api.py`（key 在用户环境变量 FISH_API_KEY）"
             " → `select_takes.py` 语音识别打分 → `segment_audio.py` 切句。")
    for n in ns.get("PRONUNCIATION", []) or []:
        L.append(f"- {n}")
    L.append("")

    if ns.get("CHECKLIST"):
        L.append("### 出片前核对\n")
        for i, n in enumerate(ns["CHECKLIST"], 1):
            L.append(f"{i}. {n}")
        L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_common(ap)
    args = ap.parse_args()
    p = C.Paths(args.episode_dir, args.series)
    b = build(p)
    p.script_dir.mkdir(exist_ok=True)
    p.script_md.write_text(render_md(p, b), encoding="utf-8")
    C.write_json(p.voice_plan, b["voice"], indent=2)
    speech = sum(v["est_seconds"] for v in b["voice"])
    print(f"讲解员 {b['pr']['name']}（{b['pr']['id']}）  配音 Fish Audio「{b['pr'].get('voice_name') or '？'}」")
    print(f"预计总长 {C.fmt(b['total'])}（正片 {b['main']:.1f}s）  配音段 {len(b['voice'])}  约 {b['units']} 字  配音约 {speech:.0f}s")
    u = b.get("usage") or {}
    extra = f"（合计 {u['total']} 个，约每分钟 {u['per_min']:.1f} 个；大动作 {u['big']}、贴纸 {u['stickers']}）" if u else ""
    print("动作：" + ("、".join(f"{w}×{n}" for w, n in b["used"].items()) or "无") + extra)
    print(f"-> {p.script_md}\n-> {p.voice_plan}")
    for w in b["warns"]:
        print("[提醒]", w)


if __name__ == "__main__":
    main()
