# -*- coding: utf-8 -*-
"""时间轴：画面（场景 = 一段或几段访谈素材 / 一张页面）+ 画外音和同传（Fish 网页版「温柔男生」，同一个声音）。素材为主。
claude-code-episode 的 build_timeline.py + OpenAI-DevDay 的“原话 + 同传”（dub）合并版。

  python build_timeline.py          → timeline.json / timeline.js（配音用 ../02_配音/edit/tts_edit.json）
  python build_timeline.py --est    → 配音还没出：按字数估时间（出版式小样用），timeline.json 里 est = true

输入：../../台本/录制稿.json（chapters / lines：id、kind（vo 画外音 | dub 同传）、who（同传是谁说的）、zh（中文字幕）、en（英文字幕，**每句必须有**；同传句是原话）、say（念的字））、
../../台本/plan.json（plan：场景按先后顺序排）。
输出的 timeline.json 里 cues = 每句一条（zh / en 整句，s / e 是这句话的起止），subs = 按“项目中英双语字幕标准”拆好的字幕（engine.js 画的就是它；finish.py 导出 SRT 也用它）：
一句话按需拆成几条（bilingual_std.split_pair_aligned，中英文一起找断点；自动拆得不顺的句子在台本那一句里写 "cut": [[中文锚点, 英文锚点], …] 手动指定），
中文一行 ≤ 约 28 字（同传句前面的人名胶囊也算进去）、英文一行 ≤ 约 90 字符，每条显示区间 = 开始前 0.1 s ~ 结束后 0.45 s、互不重叠。
场景（plan 里按先后顺序排）：
- type = clip：画外音盖在素材画面上。ranges = [{src, in, out[, crop, mute, gain_db]}, …] 几段素材首尾相接（{src, in, hold: 秒} = 取素材 in 那一帧定格这么久，in 要离素材结尾 ≥ 0.1 s）；
  lines = [{id, a}, …]：这个场景里的画外音，a = 这句话从场景开头起第几秒开口；前一句没念完就顺延（间隔 GAP_LINE）；话比画面长：场景延长到话说完 + PAD_END。
- type = card：画外音盖在一张页面 / 卡片上（dur 秒；页面录屏用 overlay: "page"，画面由 scenes.js 的 pageShot 铺满）。
- type = dub：访谈原话 + 中文同传。src / in / out = 原话片段（秒，素材里的时刻）；lines = [{id, a}, …]，a = 这句原话在片段里的起点秒；
  同传比原话晚 LAG 秒起，前一句没念完就排在它后面；念不完的小幅加速（≤ MAX_SPEED），还不够就把片段往后多放一点；cap_out = 片段最多放到素材的这一秒，之后定格。
  素材原声压在 −29 LUFS 垫底（mix_audio.py 的 dub 模式），同传 −16 LUFS。
- caps = [{a, b, zh}]：素材上的小字注释（场景内的秒数）；name / credit / where：场景名、右上角来源、讲话人头衔。
- 配音按 tts.blocks = [b0, b1, at, speed] 切成块放进成片（mix_audio.py 读），字幕和画面用同一套时间。
"""
import json
import sys

from common import EP, FPS, HERE, HAS_AUDIO, src_duration

sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
import bilingual_std as B  # noqa: E402  项目统一的中英双语字幕标准（拆条、显示区间、SRT）

LEAD, TAIL = 0.0, 1.4          # 开头不留空白：片头（悠一）后面第一帧就是素材画面
GAP_LINE, PAD_END = 0.18, 0.4
LAG, MAX_SPEED = 0.30, 1.18     # 同传比原话晚起的秒数 / 最多加速的倍数
EST_CPS, EST_GAP = 6.0, 0.30    # 估时间：字/秒、句间停顿（温柔男生声线第一次试跑后按实测改）


def main():
    est = "--est" in sys.argv
    sc = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))
    plan = json.loads((EP / "台本" / "plan.json").read_text(encoding="utf-8"))["plan"]
    lines = {l["id"]: l for l in sc["lines"]}
    for l in sc["lines"]:
        l.setdefault("kind", "vo")
    order = [l["id"] for l in sc["lines"]]
    nar = {}                                   # 每句：(有声音的起, 止, 切点起, 切点止)
    if est:
        t = 0.0
        for i in order:
            d = len(lines[i]["say"]) / EST_CPS
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
        typ = item["type"]
        ranges_in = item.get("ranges") or []
        if typ == "dub":
            ranges_in = [{"src": item.get("src", "iv"), "in": item["in"], "out": item["out"], "crop": item.get("crop"), "bg": item.get("bg")}]
        if typ in ("clip", "dub"):
            for r in ranges_in:
                if r.get("hold"):              # 定格点离素材结尾太近 ffmpeg 取不到那一帧
                    sd = sdur.setdefault(r["src"], src_duration(r["src"]))
                    assert r["in"] <= sd - 0.1, f"{item['id']}：定格点 {r['in']} s 离素材 {r['src']} 的结尾（{sd:.2f} s）不到 0.1 s，取不到这一帧——往前挪一点"
            d0 = sum(r.get("hold") or (r["out"] - r["in"]) for r in ranges_in)
        else:
            d0 = item["dur"]
        placed = []
        if typ == "dub":
            anchors = item["lines"]
            p_end = t0 - 1.0
            for i, ln in enumerate(anchors):
                lid = ln["id"]
                assert lines[lid]["kind"] == "dub", f"{lid} 不是 dub 句（同传场景 {item['id']} 里只能放 dub 句）"
                sv, ev, n0, n1 = nar[lid]
                v0, vdur = sv - n0, ev - sv
                start = max(t0 + ln["a"] + LAG, p_end + 0.08)
                nxt = (t0 + anchors[i + 1]["a"] + LAG) if i + 1 < len(anchors) else (t0 + d0 + 0.5)
                window = nxt - 0.06 - start
                speed = 1.0
                if vdur > window:
                    speed = min(MAX_SPEED, vdur / max(window, 0.6))
                dd = vdur / speed
                end = start + dd
                placed.append((lid, start, end, n0, n1, start - v0 / speed, speed))
                p_end = end
            d = max(d0, p_end - t0 + 0.4)
        else:
            for ln in item.get("lines", []):
                assert lines[ln["id"]]["kind"] == "vo", f"{ln['id']} 是 dub 句，不能放进画外音场景 {item['id']}"
                sv, ev, n0, n1 = nar[ln["id"]]
                v0, vdur = sv - n0, ev - sv
                start = max(t0 + ln["a"], prev_end + GAP_LINE)
                end = start + vdur
                placed.append((ln["id"], start, end, n0, n1, start - v0, 1.0))
                prev_end = end
            d = d0
            if placed and not item.get("spill"):
                d = max(d0, placed[-1][2] - t0 + PAD_END)
        for c in item.get("caps", []):
            if c["b"] > d + 0.05:
                capwarn.append(f"{item['id']}：注释“{c['zh']}”到 {c['b']} s，场景只有 {d:.1f} s")
        for lid, start, end, n0, n1, at, speed in placed:
            cues.append({"id": lid, "key": lines[lid].get("key", ""), "zh": lines[lid]["zh"], "s": round(start, 3), "e": round(end, 3), "kind": lines[lid]["kind"], "who": lines[lid].get("who", ""), "seg": item["id"]})
            blocks.append([round(n0, 4), round(n1, 4), round(at, 4), round(speed, 4)])
        seg = {"id": item["id"], "title": item.get("name") or item.get("kind") or item["id"], "chapter": item.get("chapter", -1),
               "kind": typ, "s": round(t0, 3), "e": round(t0 + d, 3)}
        segs.append(seg)
        if typ in ("clip", "dub"):
            rs, cur = [], t0
            for r in ranges_in:
                dur = r.get("hold") or (r["out"] - r["in"])
                rs.append({"src": r["src"], "in": r["in"], "out": r["out"] if not r.get("hold") else r["in"], "s": round(cur, 3), "e": round(cur + dur, 3),
                           "mute": bool(r.get("mute") or item.get("mute")), "gain_db": r.get("gain_db", item.get("gain_db", 0)), "crop": r.get("crop"), "bg": r.get("bg"), "hold": bool(r.get("hold")),
                           "mode": "dub" if typ == "dub" else "vo"})
                cur += dur
            hold = 0.0
            if d > d0 + 1e-6 and rs[-1]["hold"]:   # 话比画面长，而最后一段本来就是定格：定格延长
                rs[-1]["e"] = round(rs[-1]["e"] + (d - d0), 3)
            elif d > d0 + 1e-6:                # 话比画面长：最后一段素材接着往下放（cap_out 封顶），放完了定格
                r = rs[-1]
                if r["src"] not in sdur:
                    sdur[r["src"]] = src_duration(r["src"])
                room = max(0.0, sdur[r["src"]] - 0.05 - r["out"])
                if item.get("cap_out"):
                    room = min(room, max(0.0, item["cap_out"] - r["out"]))
                grow = min(d - d0, room)
                r["out"] = round(r["out"] + grow, 3)
                r["e"] = round(r["e"] + grow, 3)
                hold = round(d - d0 - grow, 3)
            clips[item["id"]] = {"kind": item.get("kind", typ), "ranges": rs, "s": round(t0, 3), "e": round(t0 + d, 3), "hold": hold,
                                 "name": item.get("name", ""), "tag": item.get("tag", ""), "credit": item.get("credit", ""), "where": item.get("where", ""),
                                 "mode": "dub" if typ == "dub" else "vo", "extended": round(d - d0, 2),
                                 "overlay": item.get("overlay", "clip"), "ui": item.get("ui", {}), "callouts": item.get("callouts", []),
                                 "caps": [{"s": round(t0 + c["a"], 3), "e": round(t0 + c["b"], 3), "zh": c["zh"], "sub": c.get("sub", "")} for c in item.get("caps", [])],
                                 "silent": all(not HAS_AUDIO[r["src"]] or r["mute"] or r["hold"] for r in rs)}
        else:
            clips[item["id"]] = {"kind": item.get("kind", "card"), "ranges": [], "s": round(t0, 3), "e": round(t0 + d, 3), "hold": 0.0,
                                 "name": item.get("name", ""), "tag": "", "credit": "", "where": "", "mode": "vo", "extended": 0,
                                 "overlay": item.get("overlay", item.get("kind", "card")), "ui": item.get("ui", {}), "callouts": item.get("callouts", []), "caps": [], "silent": True}
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
        who = q.get("who", "")
        pre = 0.62 * B.zh_units(who) + 1.2 if who else 0.0       # 橙色人名胶囊：字号 .62 倍 + 左右内边距 + 右外边距
        chunks = B.split_pair_aligned(q["zh"], en, pre, cuts=[tuple(c) for c in ln["cut"]] if ln.get("cut") else None)
        for k, ((z, e, w), (a, b)) in enumerate(zip(chunks, B.chunk_times(q["s"], q["e"], chunks))):
            if w + (pre if k == 0 else 0.0) > B.ZH_MAX or len(e) > B.EN_SOFT:
                over.append(f"{q['id']}.{k + 1}")
            elif len(e) > B.EN_MAX:
                soft.append(f"{q['id']}.{k + 1}")
            subs.append({"id": q["id"], "k": k, "zh": z, "en": e, "who": who if k == 0 else "", "kind": q["kind"], "s": round(a, 3), "e": round(b, 3)})
    for x, (a, b) in zip(subs, B.display_windows([(x["s"], x["e"]) for x in subs])):
        x["a"], x["b"] = round(a, 3), round(b, 3)
    tl = {"fps": FPS, "frames": frames, "total": total, "title": sc["title"], "est": est,
          "chapters": sc["chapters"], "segs": segs, "cues": cues, "subs": subs, "clips": clips,
          "tts": {"blocks": blocks, "total": round(tts_total, 3)}}
    for k in ("sub", "kicker"):        # 页面要用的文案（左栏副标题等）
        if k in sc:
            tl[k] = sc[k]
    (HERE / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "timeline.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    foot = sum(r["e"] - r["s"] for c in clips.values() for r in c["ranges"])
    n_vo = sum(1 for q in cues if q["kind"] == "vo")
    n_dub = sum(1 for q in cues if q["kind"] == "dub")
    voiced = sum(q["e"] - q["s"] for q in cues)
    print(f"整片 {total:.1f} s（{frames} 帧）{'【按字数估的时间】' if est else ''}：{len(segs)} 个场景、{n_vo} 句画外音 + {n_dub} 句同传（共 {voiced:.1f} s 有声）、素材画面 {foot:.1f} s；"
          f"字幕 {len(subs)} 条（超长没拆开：{' '.join(over) or '无'}；英文略超 90 字符：{' '.join(soft) or '无'}）")
    for s in segs:
        c = clips[s["id"]]
        extra = ""
        if c["hold"]:
            extra += f"  （定格 {c['hold']} s）"
        if c["mode"] == "dub":
            sp = [b[3] for b in blocks if c["s"] - 3 <= b[2] <= c["e"] and b[3] != 1.0]
            extra += f"  （同传：延长 {c['extended']} s；加速 {sp or '无'}）"
        print(f"  {s['id']:4s} {s['kind']:4s} {s['s']:7.2f}–{s['e']:7.2f}  章 {s['chapter'] + 1}  {s['title']}" + extra)
    if capwarn:
        print("【注意】" + "；".join(capwarn) + "：要么缩短注释，要么把场景拉长")
    for q in tl["cues"]:
        print(f"    {q['id']} {q['s']:7.2f}–{q['e']:7.2f} [{q['seg']}] {(q['who'] + '：') if q['who'] else ''}{q['zh']}")


if __name__ == "__main__":
    main()
