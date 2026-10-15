# -*- coding: utf-8 -*-
"""时间轴（短视频竖屏版，从 Claude Code相关 引擎改的）：画面（场景 = 一段或几段素材 / 一张卡片）+ 画外音（Fish 网页版「赛马娘（曼波欧耶版）」）。
字幕按竖屏的字数上限拆：中文一行 ≤ 17 字、英文一行 ≤ 约 60 字符（字号和横屏一样 52 / 30 px，横屏是 28 字 / 90 字符）；开头不留空白（没有片头），最后一句说完留 TAIL 秒就结束。

  python build_timeline.py          → timeline.json / timeline.js（配音用 ../02_配音/edit/tts_edit.json）
  python build_timeline.py --est    → 配音还没出：按字数估时间（出版式小样用），timeline.json 里 est = true

输入：../../台本/录制稿.json（chapters / lines：id、zh（中文字幕）、en（英文字幕，**每句必须有**）、say（念的字））、../../台本/plan.json（plan：场景按先后顺序排）。
输出的 timeline.json 里 cues = 每句一条（zh / en 整句，s / e 是这句话的起止），subs = 按“项目中英双语字幕标准”拆好的字幕（engine.js 画的就是它；finish.py 导出 SRT 也用它）：
一句话按需拆成几条（bilingual_std.split_pair_aligned，中英文一起找断点；自动拆得不顺的句子在台本那一句里写 "cut": [[中文锚点, 英文锚点], …] 手动指定），
中文一行 ≤ 约 28 字、英文一行 ≤ 约 90 字符，每条显示区间 = 开始前 0.1 s ~ 结束后 0.45 s、互不重叠。
场景：
- plan.json 顶层 layout = single（单框）/ dual（双分镜：clip 场景另写 ranges2 = 下框的素材段，写法同 ranges，永远静音）。
- type = clip：ranges = [{src, in, out[, crop, mute, gain_db, speed]}, …] 几段素材首尾相接（speed = 变速倍数，只给静音段：操作录屏 1.5–4× 把长操作压短，人脸别超过 0.9–1.1×）（硬切，不同素材也行；crop = [x0, y0, x1, y1] 先裁出这一块再放大；{src, in, hold: 秒} = 取素材 in 那一帧定格这么久，in 要离素材结尾 ≥ 0.1 s）；type = card：dur 秒的卡片（演示区放卡片，没有素材画面）。
- lines = [{id, a}, …]：这个场景里的画外音，a = 这句话从场景开头起第几秒开口；前一句没念完就顺延（间隔 GAP_LINE）。
- 话比画面长：场景延长到话说完 + PAD_END（clip 场景把最后一段素材接着往下放，素材放完了就定格最后一帧）；spill = true 则不延长，话可以压到下一个场景里。
- caps = [{a, b, zh}]：素材上的小字注释（场景内的秒数）；name / tag / credit：左上角的作品名和模型，右上角的来源。
- 配音按 tts.blocks = [b0, b1, at, 1.0] 切成块放进成片（mix_audio.py 读），字幕和画面用同一套时间。
"""
import json
import re
import sys

from common import EP, FPS, HERE, HAS_AUDIO, src_duration

sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
import bilingual_std as B  # noqa: E402  项目统一的中英双语字幕标准（拆条、显示区间、SRT）
B.ZH_MAX, B.EN_MAX, B.EN_SOFT = 17.5, 60, 64   # 竖屏 1080 宽：中文 52 px 一行 ≤ 17 字（≈ 900 px）、英文 30 px 一行 ≤ 约 60 字符（check_subs.py 再按真实字宽量一遍）

LEAD, TAIL = 0.0, 0.8          # 开头不留空白：第一帧就是钩子那句话的画面；收尾金句说完留 0.8 s 就结束
GAP_LINE, PAD_END = 0.18, 0.4
EST_SEC_PER_HAN, EST_GAP = 0.225, 0.12   # 估时间：每个汉字的秒数（短视频第 1 条实测曼波 S2 Pro 约 0.22 s / 汉字，已含英文词和标点停顿；30 秒封顶 ≈ 125 汉字）、句间停顿


def est_dur(say):
    """本条改的估时（模板是 0.225 s / 汉字，对“温柔男生”偏长约 20%）：用长视频《人人都是 UI 设计师》142 句真实配音回归出来的
    dur ≈ 0.140·汉字 + 0.333·英文词 + 0.284·句内标点 + 0.405（秒，均方误差 0.35 s / 句；合计 455.5 s 与实测 455.5 s 吻合），
    等价于约 6.2 字符 / 秒（含标点、英文、数字）。配音出来以 tts_edit.json 为准。"""
    han = sum(1 for ch in say if "一" <= ch <= "鿿")
    lat = len(re.findall(r"[A-Za-z]+", say))
    inner = len(re.findall(r"[，、：；？！,]", say[:-1]))
    return 0.140 * han + 0.333 * lat + 0.284 * inner + 0.405


def main():
    est = "--est" in sys.argv
    sc = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))
    planj = json.loads((EP / "台本" / "plan.json").read_text(encoding="utf-8"))
    plan, layout = planj["plan"], planj.get("layout", "single")
    assert layout in ("single", "dual"), f"plan.json 的 layout 只能是 single / dual，现在是 {layout}"
    lines = {l["id"]: l for l in sc["lines"]}
    order = [l["id"] for l in sc["lines"]]
    nar = {}                                   # 每句：(有声音的起, 止, 切点起, 切点止)
    if est:
        t = 0.0
        for i in order:
            d = est_dur(lines[i]["say"])
            nar[i] = (t, t + d, t, t + d + EST_GAP)
            t += d + EST_GAP
        tts_total = t
    else:
        td = json.loads((HERE.parent / "02_配音" / "edit" / "tts_edit.json").read_text(encoding="utf-8"))
        for x in td["lines"]:
            nar[x["id"]] = (x["s"], x["e"], x["n0"], x["n1"])
        tts_total = td["total"]
        missing = [i for i in order if i not in nar]
        assert not missing, f"配音里缺这些句子：{missing}"
    used = [ln["id"] for it in plan for ln in it.get("lines", [])]
    assert used == order, f"plan 里的句子顺序和录制稿不一致：plan {used} / 录制稿 {order}"

    sdur = {}
    capwarn = []                              # 注释（caps）结束时刻超过场景长度：叠加层不会在场景结束处截掉，会压到下一个场景上
    cues, segs, blocks, clips = [], [], [], {}
    t, prev_end = LEAD, -1.0
    for item in plan:
        t0 = t + item.get("lead", 0.0)
        if item["type"] == "clip":
            for r in item["ranges"]:
                if r.get("hold"):              # 定格点离素材结尾太近 ffmpeg 取不到那一帧（第 3 期 38.86 s / 素材 38.867 s 就卡在这）
                    sd = sdur.setdefault(r["src"], src_duration(r["src"]))
                    assert r["in"] <= sd - 0.1, f"{item['id']}：定格点 {r['in']} s 离素材 {r['src']} 的结尾（{sd:.2f} s）不到 0.1 s，取不到这一帧——往前挪一点"
            for r in item["ranges"] + item.get("ranges2", []):          # 变速只给静音的段（原声变速会变调；ranges2 永远静音）
                sp = r.get("speed", 1.0)
                assert 0.25 <= sp <= 8, f"{item['id']}：speed {sp} 超出 0.25–8"
                assert sp == 1.0 or r in item.get("ranges2", []) or r.get("mute") or not HAS_AUDIO[r["src"]], f"{item['id']}：有原声的段不能变速（加 mute: true）"
            d0 = sum(r.get("hold") or (r["out"] - r["in"]) / r.get("speed", 1.0) for r in item["ranges"])
        else:
            d0 = item["dur"]
        placed = []
        for ln in item.get("lines", []):
            sv, ev, n0, n1 = nar[ln["id"]]
            v0, vdur = sv - n0, ev - sv
            start = max(t0 + ln["a"], prev_end + GAP_LINE)
            end = start + vdur
            placed.append((ln["id"], start, end, n0, n1, start - v0))
            prev_end = end
        d = d0
        if placed and not item.get("spill"):
            d = max(d0, placed[-1][2] - t0 + PAD_END)
        for c in item.get("caps", []):
            if c["b"] > d + 0.05:
                capwarn.append(f"{item['id']}：注释“{c['zh']}”到 {c['b']} s，场景只有 {d:.1f} s")
        for lid, start, end, n0, n1, at in placed:
            cues.append({"id": lid, "zh": lines[lid]["zh"], "s": round(start, 3), "e": round(end, 3), "kind": "vo", "seg": item["id"]})
            blocks.append([round(n0, 4), round(n1, 4), round(at, 4), 1.0])
        seg = {"id": item["id"], "title": item.get("name") or item.get("kind") or item["id"], "chapter": item.get("chapter", -1),
               "kind": item["type"], "s": round(t0, 3), "e": round(t0 + d, 3)}
        segs.append(seg)
        if item["type"] == "clip":
            rs, cur = [], t0
            for r in item["ranges"]:
                dur = r.get("hold") or (r["out"] - r["in"]) / r.get("speed", 1.0)
                rs.append({"src": r["src"], "in": r["in"], "out": r["out"] if not r.get("hold") else r["in"], "s": round(cur, 3), "e": round(cur + dur, 3),
                           "mute": bool(r.get("mute")), "gain_db": r.get("gain_db", 0), "crop": r.get("crop"), "hold": bool(r.get("hold")), "speed": r.get("speed", 1.0)})
                cur += dur
            hold = 0.0
            if d > d0 + 1e-6 and rs[-1]["hold"]:   # 话比画面长，而最后一段本来就是定格：定格延长
                rs[-1]["e"] = round(rs[-1]["e"] + (d - d0), 3)
            elif d > d0 + 1e-6:                # 话比画面长：最后一段素材接着往下放，放完了定格
                r = rs[-1]
                if r["src"] not in sdur:
                    sdur[r["src"]] = src_duration(r["src"])
                room = max(0.0, sdur[r["src"]] - 0.05 - r["out"])          # 原片里还剩多少秒（原片时间；变速段按 speed 换算成成片时间）
                grow = min((d - d0) * r["speed"], room)
                r["out"] = round(r["out"] + grow, 3)
                r["e"] = round(r["e"] + grow / r["speed"], 3)
                hold = round(d - d0 - grow / r["speed"], 3)
            # 双分镜的下框（ranges2）：从场景开头起首尾相接，永远静音（画外音讲解，原声不用）；比场景短就接着往下放、放完定格，比场景长就截掉
            rs2, cur = [], t0
            for r in item.get("ranges2", []):
                dur = r.get("hold") or (r["out"] - r["in"]) / r.get("speed", 1.0)
                rs2.append({"src": r["src"], "in": r["in"], "out": r["out"] if not r.get("hold") else r["in"], "s": round(cur, 3), "e": round(cur + dur, 3),
                            "mute": True, "gain_db": 0, "crop": r.get("crop"), "hold": bool(r.get("hold")), "speed": r.get("speed", 1.0)})
                cur += dur
            if rs2 and rs2[-1]["e"] < t0 + d - 1e-6 and not rs2[-1]["hold"]:
                r = rs2[-1]
                sdur.setdefault(r["src"], src_duration(r["src"]))
                grow = min((t0 + d - r["e"]) * r["speed"], max(0.0, sdur[r["src"]] - 0.05 - r["out"]))
                r["out"], r["e"] = round(r["out"] + grow, 3), round(r["e"] + grow / r["speed"], 3)
            clips[item["id"]] = {"kind": item.get("kind", "clip"), "ranges": rs, "ranges2": rs2, "s": round(t0, 3), "e": round(t0 + d, 3), "hold": hold,
                                 "name": item.get("name", ""), "tag": item.get("tag", ""), "credit": item.get("credit", ""),
                                 "overlay": item.get("overlay", "clip"), "ui": item.get("ui", {}),
                                 "caps": [{"s": round(t0 + c["a"], 3), "e": round(t0 + c["b"], 3), "zh": c["zh"], "sub": c.get("sub", "")} for c in item.get("caps", [])],
                                 "silent": all(not HAS_AUDIO[r["src"]] or r["mute"] or r["hold"] for r in rs)}
        else:
            clips[item["id"]] = {"kind": item.get("kind", "card"), "ranges": [], "ranges2": [], "s": round(t0, 3), "e": round(t0 + d, 3), "hold": 0.0,
                                 "name": item.get("name", ""), "tag": "", "credit": "", "overlay": item.get("overlay", item.get("kind", "card")),
                                 "ui": item.get("ui", {}), "caps": [], "silent": True}
        t += (t0 - t) + d + item.get("gap", 0.0)
    total = round(t + TAIL, 3)
    segs[-1]["e"] = total
    for a, b in zip(segs, segs[1:]):
        a["e"] = b["s"]
    frames = int(round(total * FPS))
    cues = sorted(cues, key=lambda q: q["s"])
    subs, over, soft = [], [], []
    for q in cues:
        ln = lines[q["id"]]
        en = ln.get("en", "")
        assert en, f"{q['id']} 没有英文：台本每句都要写 en（项目的中英双语字幕标准），见技能 references/subtitles.md"
        who = ln.get("who", "")                  # 说话人标签（同传 / 原话那句写 "who": "Vanessa"）：字幕前面加一个橙色小标签，拆条时把它的宽度算进去（Tavus-Griffin 那条加的）
        chunks = B.split_pair_aligned(q["zh"], en, (0.62 * 0.55 * len(who) + 0.95) if who else 0.0, cuts=[tuple(c) for c in ln["cut"]] if ln.get("cut") else None)
        for k, ((z, e, w), (a, b)) in enumerate(zip(chunks, B.chunk_times(q["s"], q["e"], chunks))):
            if w > B.ZH_MAX or len(e) > B.EN_SOFT:
                over.append(f"{q['id']}.{k + 1}")
            elif len(e) > B.EN_MAX:
                soft.append(f"{q['id']}.{k + 1}")
            subs.append({"id": q["id"], "k": k, "zh": z, "en": e, "who": who, "kind": "vo", "s": round(a, 3), "e": round(b, 3)})
    for x, (a, b) in zip(subs, B.display_windows([(x["s"], x["e"]) for x in subs])):
        x["a"], x["b"] = round(a, 3), round(b, 3)
    tl = {"fps": FPS, "frames": frames, "total": total, "title": sc["title"], "est": est,
          "chapters": sc.get("chapters", []), "hook": sc["hook"], "kicker": sc.get("kicker", ""), "layout": layout, "segs": segs, "cues": cues, "subs": subs, "clips": clips,
          "tts": {"blocks": blocks, "total": round(tts_total, 3)}}
    bgj = HERE / "bg.json"                     # 背景印花：new_short.py 从技能的 assets/backgrounds/ 随机挑一张复制成 bg.png（用户 2026-10-04：每一期随机挑一张）
    if bgj.exists() and json.loads(bgj.read_text(encoding="utf-8")).get("file") and (HERE / "bg.png").exists():
        tl["bg"] = "bg.png"
    for k in ("sub", "titleCard", "factsCard", "outroCard"):        # 页面要用的文案（左栏副标题、开场标题、官方现状卡片、收尾卡片）
        if k in sc:
            tl[k] = sc[k]
    (HERE / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "timeline.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    foot = sum(r["e"] - r["s"] for c in clips.values() for r in c["ranges"])
    voiced = sum(q["e"] - q["s"] for q in cues)
    print(f"整片 {total:.1f} s（{frames} 帧）{'【按字数估的时间】' if est else ''}：{len(segs)} 个场景、{len(cues)} 句画外音（共 {voiced:.1f} s 有声）、素材画面 {foot:.1f} s；"
          f"字幕 {len(subs)} 条（超长没拆开：{' '.join(over) or '无'}；英文略超 {B.EN_MAX} 字符：{' '.join(soft) or '无'}）")
    for s in segs:
        c = clips[s["id"]]
        print(f"  {s['id']:4s} {s['kind']:4s} {s['s']:7.2f}–{s['e']:7.2f}  {s['title']}" + (f"  （定格 {c['hold']} s）" if c["hold"] else ""))
    if capwarn:
        print("【注意】" + "；".join(capwarn) + "：要么缩短注释，要么把场景拉长")
    for q in tl["cues"]:
        print(f"    {q['id']} {q['s']:7.2f}–{q['e']:7.2f} [{q['seg']}] {q['zh']}")


if __name__ == "__main__":
    main()
