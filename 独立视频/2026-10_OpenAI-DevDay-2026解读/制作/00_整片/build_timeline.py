# -*- coding: utf-8 -*-
"""时间轴：画外音（Fish 网页版「赛马娘（曼波欧耶版）」）+ 发布会片段（原声压低垫在下面）按台本的 plan 依次放。

  python build_timeline.py V1            → out/V1/timeline.json / timeline.js（配音用 ../02_配音/edit/tts_edit.json）
  python build_timeline.py V1 --est      → 配音还没出：按字数估时间（出版式小样用），timeline.json 里 est = true

输入：../../台本/V?_*.json（lines：id / kind(vo|dub) / zh（中文字幕） / en（英文字幕，同传句是发布会原话，画外音句是译文，见 ../02_配音/add_en.py） / say（念的字） / ch / who；plan：块的先后顺序）。
输出的 timeline.json 里 cues = 每句一条（zh / en 整句，s / e 是这句话的起止），subs = 按“项目中英双语字幕标准”拆好的字幕（engine.js 画的就是它）。
块有三种：
- card：一段画外音（from → to 几句），演示区放一张卡片（卡片内容在块里的 card，scenes.js 画）；
- vclip：一段画外音，演示区放发布会画面（从 in 起原速放，长度 = 这段画外音 + pad），原声压得更低（gain_db，默认 −4）；
- clip：发布会原话片段（in → out 秒），每句原话配一句中文同传（lines 里的 a = 这句原话在片段里的起点秒）：
  同传比原话晚 LAG 秒起，前一句没念完就排在它后面；念不完的小幅加速（≤ MAX_SPEED），还不够就把片段往后多放一点。
成片时间：vo / vclip 的第 i 句 = at + (配音里的时间 − 这一块在配音里的起点 b0)；混音（mix_audio.py）按 tts.blocks = [b0, b1, at, speed] 切块放。
"""
import json
import sys

from common import FPS, VOICE, load_script, out_dir

sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
import bilingual_std as B  # noqa: E402  项目统一的中英双语字幕标准（拆条、显示区间）

LEAD, TAIL = 0.5, 1.4
GAP_VO, GAP_CLIP = 0.25, 0.35        # 块与块之间的停顿 / 发布会片段播完后多留的
LAG, MAX_SPEED = 0.25, 1.18           # 同传比原话晚起的秒数 / 最多加速的倍数
EST_CPS, EST_GAP = 6.4, 0.30          # 估时间：字/秒、句间停顿（曼波声线第一次试跑实测约 6.3 字/秒）
CREDIT = "OpenAI DevDay 2026"


def main():
    ep = sys.argv[1]
    est = "--est" in sys.argv
    sc = load_script(ep)
    plan = sc["plan"]
    lines = {l["id"]: l for l in sc["lines"]}
    order = [l["id"] for l in sc["lines"]]
    nar = {}                          # 每句在配音里的 (有声音的起, 止, 切点起, 切点止)
    if est:
        t = 0.0
        for i in order:
            d = len(lines[i]["say"]) / EST_CPS
            nar[i] = (t, t + d, t, t + d + EST_GAP)
            t += d + EST_GAP
        tts_total = t
    else:
        td = json.loads((VOICE / "edit" / "tts_edit.json").read_text(encoding="utf-8"))
        for x in td["lines"]:
            nar[x["id"]] = (x["s"], x["e"], x["n0"], x["n1"])
        tts_total = td["total"]
        missing = [i for i in order if i not in nar]
        assert not missing, f"配音里缺这些句子：{missing}"

    cues, segs, blocks, clips = [], [], [], {}
    t = LEAD
    last_gap = GAP_VO
    for k, item in enumerate(plan):
        typ = item["type"]
        sid = item.get("id", f"B{k + 1}")
        if typ in ("card", "vclip"):
            a, b = order.index(item["from"]), order.index(item["to"])
            ids = order[a: b + 1]
            assert all(lines[i]["kind"] == "vo" for i in ids), f"{typ} 块里混进了 dub 句：{ids}"
            b0, b1 = nar[ids[0]][2], nar[ids[-1]][3]
            at = t + item.get("lead", 0.0)
            for i in ids:
                s, e = nar[i][0], nar[i][1]
                cues.append({"id": i, "zh": lines[i]["zh"], "s": round(at + s - b0, 3), "e": round(at + e - b0, 3), "kind": "vo", "seg": None})
            blocks.append([round(b0, 4), round(b1, 4), round(at, 4), 1.0])
            dur = b1 - b0
            if typ == "card":
                segs.append({"id": sid, "title": f"{ids[0]}–{ids[-1]}", "chapter": item["ch"], "kind": "vo", "s": round(t, 3), "card": item.get("card")})
                t += (at - t) + dur + GAP_VO
                last_gap = GAP_VO
            else:
                clip_dur = dur + item.get("pad", 0.35)
                if item.get("min_dur"):
                    clip_dur = max(clip_dur, item["min_dur"])
                clips[sid] = {"src": "kn", "in": item["in"], "out": round(item["in"] + clip_dur, 3), "s": round(at, 3), "e": round(at + clip_dur, 3),
                              "credit": CREDIT, "where": item.get("where", ""), "gain_db": item.get("gain_db", -4), "mode": "vo",
                              "extended": 0, "cap": False, "hold": 0, "tag": "", "ui": item.get("ui", {}), "callouts": item.get("callouts", []), "crop": item.get("crop")}
                segs.append({"id": sid, "title": "画面：" + item.get("what", sid), "chapter": item["ch"], "kind": "clip", "s": round(t, 3)})
                t = at + clip_dur + item.get("gap", GAP_VO)
                last_gap = item.get("gap", GAP_VO)
        else:                         # clip：原话 + 同传
            t0 = t + item.get("lead", 0.0)
            dur0 = item["out"] - item["in"]
            anchors = item["lines"]
            prev_end = t0 - 1.0
            placed = []
            for i, ln in enumerate(anchors):
                lid = ln["id"]
                assert lines[lid]["kind"] == "dub", f"{lid} 不是 dub 句"
                sv, ev, n0, n1 = nar[lid]
                v0, vdur = sv - n0, ev - sv
                anchor_abs = t0 + ln["a"] + LAG
                start = max(anchor_abs, prev_end + 0.08)
                nxt = (t0 + anchors[i + 1]["a"] + LAG) if i + 1 < len(anchors) else (t0 + dur0 + 0.5)
                window = nxt - 0.06 - start
                speed = 1.0
                if vdur > window:
                    speed = min(MAX_SPEED, vdur / max(window, 0.6))
                d = vdur / speed
                end = start + d
                at = start - v0 / speed
                placed.append((lid, start, end, n0, n1, at, speed))
                prev_end = end
            clip_dur = max(dur0, prev_end - t0 + 0.4)
            out_ext = item["in"] + clip_dur
            cap = item.get("cap_out")
            out_used = min(out_ext, cap) if cap else out_ext
            clips[sid] = {"src": "kn", "in": item["in"], "out": round(out_used, 3), "s": round(t0, 3), "e": round(t0 + clip_dur, 3),
                          "credit": CREDIT, "where": item.get("where", ""), "gain_db": item.get("gain_db", 0), "mode": "dub",
                          "extended": round(clip_dur - dur0, 2), "cap": bool(cap), "hold": round(out_ext - out_used, 3),
                          "tag": item.get("tag", ""), "ui": item.get("ui", {}), "callouts": item.get("callouts", [])}
            for lid, start, end, n0, n1, at, speed in placed:
                cues.append({"id": lid, "zh": lines[lid]["zh"], "s": round(start, 3), "e": round(end, 3), "kind": "clip", "who": lines[lid].get("who", ""), "seg": None})
                blocks.append([round(n0, 4), round(n1, 4), round(at, 4), round(speed, 4)])
            segs.append({"id": sid, "title": "原话：" + item.get("what", sid), "chapter": item["ch"], "kind": "clip", "s": round(t0, 3)})
            t = t0 + clip_dur + item.get("gap", GAP_CLIP)
            last_gap = item.get("gap", GAP_CLIP)
    total = round(t - last_gap + TAIL, 3)
    for a, b in zip(segs, segs[1:]):
        a["e"] = b["s"]
    segs[-1]["e"] = total
    for q in cues:
        q["seg"] = next(s["id"] for s in segs if s["s"] <= q["s"] + 1e-6 < s["e"])
    cues.sort(key=lambda q: q["s"])
    # 字幕按项目的中英双语标准（Way to AGI/skill/way-to-agi-episode/references/subtitles.md + scripts/bilingual_std.py）：
    # 一句画外音 / 同传按需拆成几条（split_pair_aligned：中英文一起找断点，断在标点 / 语义处；自动拆得不顺的句子用台本里的 "cut" 手动指定），
    # 中文一行 ≤ 约 28 字、英文一行 ≤ 约 90 字符（同传句中文前面的人名标签也算进 28 字）；
    # 每条的显示区间 [a, b) = 开始前 0.1 s ~ 结束后 0.45 s，互不重叠。engine.js 只查 TL.subs，cues 原样保留（scenes.js / qa_mix.py 在用）。
    subs, over, soft = [], [], []
    for q in cues:
        ln = lines[q["id"]]
        en = ln.get("en", "")
        assert en, f"{q['id']} 没有英文（先跑 ../02_配音/add_en.py）"
        who = q.get("who", "")
        pre = 0.62 * B.zh_units(who) + 1.2 if who else 0.0       # 橙色人名胶囊：字号 .62 倍 + 左右内边距 + 右外边距
        chunks = B.split_pair_aligned(q["zh"], en, pre, cuts=[tuple(c) for c in ln["cut"]] if ln.get("cut") else None)
        for k, ((z, e, w), (s, t)) in enumerate(zip(chunks, B.chunk_times(q["s"], q["e"], chunks))):
            if w + (pre if k == 0 else 0.0) > B.ZH_MAX or len(e) > B.EN_SOFT:
                over.append(f"{q['id']}.{k + 1}")
            elif len(e) > B.EN_MAX:
                soft.append(f"{q['id']}.{k + 1}")
            subs.append({"id": q["id"], "k": k, "zh": z, "en": e, "who": who if k == 0 else "", "kind": q["kind"], "s": round(s, 3), "e": round(t, 3)})
    for x, (a, b) in zip(subs, B.display_windows([(x["s"], x["e"]) for x in subs])):
        x["a"], x["b"] = round(a, 3), round(b, 3)
    frames = int(round(total * FPS))
    tl = {"fps": FPS, "frames": frames, "total": total, "ep": ep, "title": sc["title"], "kicker": sc.get("kicker", ""), "short": sc.get("short", sc["title"]),
          "est": est, "chapters": sc["chapters"], "segs": segs, "cues": cues, "subs": subs, "clips": clips, "tts": {"blocks": blocks, "total": round(tts_total, 3)}}
    od = out_dir(ep)
    (od / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (od / "timeline.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    n_vo = sum(1 for q in cues if q["kind"] == "vo")
    n_dub = sum(1 for q in cues if q["kind"] == "clip")
    print(f"{ep} 整片 {total:.1f} s（{frames} 帧）{'【按字数估的时间】' if est else ''}：{len(segs)} 段、{n_vo} 句画外音、{n_dub} 句同传、"
          f"{len(clips)} 段发布会画面（共 {sum(c['e'] - c['s'] for c in clips.values()):.0f} s）；字幕 {len(subs)} 条（超长没拆开：{' '.join(over) or '无'}；英文略超 90 字符：{' '.join(soft) or '无'}）")
    for s in segs:
        print(f"  {s['id']:4s} {s['kind']:4s} {s['s']:7.2f}–{s['e']:7.2f}  要点{s['chapter'] + 1}  {s['title']}")
    for cid, c in clips.items():
        if c["mode"] == "dub":
            sp = [b[3] for b in blocks if c['s'] - 3 <= b[2] <= c['e'] and b[3] != 1.0]
            print(f"  {cid}: 延长 {c['extended']} s；加速 {sp or '无'}")


if __name__ == "__main__":
    main()
