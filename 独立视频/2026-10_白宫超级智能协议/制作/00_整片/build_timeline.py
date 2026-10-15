# -*- coding: utf-8 -*-
"""时间轴 v2：画外音（Fish 网页版「赛马娘（曼波欧耶版）」）+ 现场片段（白宫官方 / PBS NewsHour，原声压低垫在下面，上面是同一个声音的中文同声传译）按 plan 交替放。

  python build_timeline.py          → timeline.json / timeline.js（配音用 ../02_配音/edit/tts_edit.json）
  python build_timeline.py --est    → 配音还没出：按字数估时间（出版式小样用），timeline.json 里 est = true

输入：../../台本/录制稿_v2.json（lines：id / kind(vo|dub) / zh / say / ch / who）、../../台本/plan_v2.json（plan：vo 块和 clip 块的顺序）。
- vo 块：from → to 一段连续的句子；成片时间 = at + (配音里的时间 − 这一块在配音里的起点 b0)。
  混音（mix_audio.py）按 tts.blocks = [b0, b1, at, speed] 把配音切成块放进去，字幕和画面也用同一套时间。
- clip 块：src 的 in → out（秒）原样放，原声压低；lines 是这个片段里的中文同传，每句一个块：
  同传比原话这一句的开头晚 LAG 秒起（真人同传也是这样），前一句没念完就排在它后面；
  一句念不完下一句的位置就小幅加速（speed ≤ 1.18，只在配音里这一块），还不够就把片段往后多放一点（out 延长，原片接着往下放）。
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
FPS = 30
LEAD, TAIL = 0.5, 1.4
GAP_VO, GAP_CLIP = 0.25, 0.35        # 块与块之间的停顿 / 现场片段播完后多留的
LAG, MAX_SPEED = 0.25, 1.18           # 同传比原话晚起的秒数 / 最多加速的倍数
EST_CPS, EST_GAP = 6.4, 0.30          # 估时间：字/秒、句间停顿（曼波声线第一次试跑实测约 6.3 字/秒）

TITLE = "一个视频带你看懂：昨天川普和6位CEO到底签署了啥？"


def main():
    est = "--est" in sys.argv
    sc = json.loads((EP / "台本" / "录制稿_v2.json").read_text(encoding="utf-8"))
    plan = json.loads((EP / "台本" / "plan_v2.json").read_text(encoding="utf-8"))["plan"]
    lines = {l["id"]: l for l in sc["lines"]}
    order = [l["id"] for l in sc["lines"]]
    # 每句在配音里的 (有声音的起, 止, 切点起, 切点止)
    nar = {}
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

    cues, segs, blocks, clips = [], [], [], {}
    t = LEAD
    for k, item in enumerate(plan):
        if item["type"] == "vo":
            a, b = order.index(item["from"]), order.index(item["to"])
            ids = order[a: b + 1]
            assert all(lines[i]["kind"] == "vo" for i in ids), f"vo 块里混进了 dub 句：{ids}"
            b0, b1 = nar[ids[0]][2], nar[ids[-1]][3]
            at = t
            for i in ids:
                s, e = nar[i][0], nar[i][1]
                cues.append({"id": i, "zh": lines[i]["zh"], "s": round(at + s - b0, 3), "e": round(at + e - b0, 3), "kind": "vo", "seg": None})
            blocks.append([round(b0, 4), round(b1, 4), round(at, 4), 1.0])
            segs.append({"id": f"V{k + 1}", "title": f"{ids[0]}–{ids[-1]}", "chapter": lines[ids[0]]["ch"], "kind": "vo", "s": round(t, 3)})
            t += b1 - b0 + GAP_VO
        else:
            t0 = t + item.get("lead", 0.0)        # lead：这个片段前面多停一会儿（例：片尾彩蛋和上一句口播拉开）
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
            cap = item.get("cap_out")             # cap_out：原片到这个秒数就是镜头切换，多出来的时间定格最后一帧，不往下放
            out_used = min(out_ext, cap) if cap else out_ext
            clips[item["id"]] = {"src": item["src"], "in": item["in"], "out": round(out_used, 3), "s": round(t0, 3), "e": round(t0 + clip_dur, 3),
                                 "credit": item["credit"], "where": item.get("where", ""), "gain_db": item.get("gain_db", 0),
                                 "extended": round(clip_dur - dur0, 2), "cap": bool(cap), "hold": round(out_ext - out_used, 3),
                                 "tag": item.get("tag", ""), "ui": item.get("ui", {})}
            for lid, start, end, n0, n1, at, speed in placed:
                cues.append({"id": lid, "zh": lines[lid]["zh"], "s": round(start, 3), "e": round(end, 3), "kind": "clip", "who": lines[lid].get("who", ""), "seg": None})
                blocks.append([round(n0, 4), round(n1, 4), round(at, 4), round(speed, 4)])
            segs.append({"id": item["id"], "title": "现场：" + item.get("what", item["id"]), "chapter": item["chapter"], "kind": "clip", "s": round(t0, 3)})
            t += clip_dur + item.get("gap", GAP_CLIP)
    total = round(t - GAP_VO + TAIL, 3) if plan[-1]["type"] == "vo" else round(t + plan[-1].get("tail", TAIL), 3)
    for a, b in zip(segs, segs[1:]):
        a["e"] = b["s"]
    segs[-1]["e"] = total
    for q in cues:
        q["seg"] = next(s["id"] for s in segs if s["s"] <= q["s"] + 1e-6 < s["e"])
    cues.sort(key=lambda q: q["s"])
    frames = int(round(total * FPS))
    tl = {"fps": FPS, "frames": frames, "total": total, "title": TITLE, "est": est,
          "chapters": sc["chapters"], "segs": segs, "cues": cues, "clips": clips, "tts": {"blocks": blocks, "total": round(tts_total, 3)}}
    (HERE / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "timeline.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    n_vo = sum(1 for q in cues if q["kind"] == "vo")
    n_dub = sum(1 for q in cues if q["kind"] == "clip")
    print(f"整片 {total:.1f} s（{frames} 帧）{'【按字数估的时间】' if est else ''}：{len(segs)} 段、{n_vo} 句画外音、{n_dub} 句同传、{len(clips)} 个现场片段（共 {sum(c['e'] - c['s'] for c in clips.values()):.0f} s）")
    for s in segs:
        print(f"  {s['id']:4s} {s['kind']:4s} {s['s']:7.2f}–{s['e']:7.2f}  第{s['chapter'] + 1}章  {s['title']}")
    for cid, c in clips.items():
        sp = [b[3] for b in blocks if c['s'] - 3 <= b[2] <= c['e'] and b[3] != 1.0]
        print(f"  {cid}: 延长 {c['extended']} s；加速 {sp or '无'}")


if __name__ == "__main__":
    main()
