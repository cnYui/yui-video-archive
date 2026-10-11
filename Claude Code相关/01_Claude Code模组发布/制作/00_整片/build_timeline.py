# -*- coding: utf-8 -*-
"""时间轴 v1：全程画外音（Fish 网页版「赛马娘（曼波欧耶版）」S2 Pro）；演示区放卡片，或放 @ClaudeDevs 发的官方演示视频（画外音盖在上面）。

  python build_timeline.py          → timeline.json / timeline.js（配音用 ../02_配音/edit/tts_edit.json）
  python build_timeline.py --est    → 配音还没出：按字数估时间（出版式小样用），timeline.json 里 est = true

输入：../../台本/录制稿_v1.json（lines：id / ch / zh / say）、../../台本/plan_v1.json（plan：vo 块，可带 bg 视频）。
- vo 块：from → to 一段连续的句子；成片时间 = at + (配音里的时间 − 这一块在配音里的起点 b0)。
  混音（mix_audio.py）按 tts.blocks = [b0, b1, at, speed] 把配音切成块放进去，字幕和画面也用同一套时间。
- bg：这一块演示区放官方演示视频。parts 按顺序拼接，rate = 素材总长 / 画外音块时长（限制在 [min_rate, max_rate]，默认 0.75–1.5）；
  素材播完还没到块尾 → 定格最后一帧（hold_from）；素材比块长（rate 已到上限）→ 在块结束处截断。
  captions：来源视频底部英文说明条的中文翻译，换算成成片时间（caps）。
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
FPS = 30
LEAD, TAIL = 0.5, 1.4
GAP_VO = 0.25                          # 块与块之间的停顿（plan 里某块写 "gap": 0 就不加，镜头在句子中间换时用）
EST_CPS, EST_GAP = 6.4, 0.30           # 估时间：字/秒、句间停顿（曼波声线实测约 6.3 字/秒）
RATE_MIN, RATE_MAX = 0.75, 1.5

TITLE = "现在你可以修改Claude Code成自己喜欢的样子"


def main():
    est = "--est" in sys.argv
    sc = json.loads((EP / "台本" / "录制稿_v1.json").read_text(encoding="utf-8"))
    pl = json.loads((EP / "台本" / "plan_v1.json").read_text(encoding="utf-8"))
    plan, caps_map, credit = pl["plan"], pl.get("captions", {}), pl.get("credit", "")
    lines = {l["id"]: l for l in sc["lines"]}
    order = [l["id"] for l in sc["lines"]]
    nar = {}                            # 每句在配音里的 (有声音的起, 止, 切点起, 切点止)
    if est:
        t = 0.0
        for i in order:
            d = len(lines[i]["say"].replace(" ", "")) / EST_CPS
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

    used = []
    cues, segs, blocks, clips = [], [], [], {}
    t = LEAD
    for k, item in enumerate(plan):
        a, b = order.index(item["from"]), order.index(item["to"])
        ids = order[a: b + 1]
        used += ids
        b0, b1 = nar[ids[0]][2], nar[ids[-1]][3]
        D = b1 - b0
        at = t
        for i in ids:
            s, e = nar[i][0], nar[i][1]
            cues.append({"id": i, "zh": lines[i]["zh"], "s": round(at + s - b0, 3), "e": round(at + e - b0, 3), "kind": "vo", "seg": None})
        blocks.append([round(b0, 4), round(b1, 4), round(at, 4), 1.0])
        seg = {"id": f"V{k + 1}", "title": f"{ids[0]}–{ids[-1]}", "chapter": lines[ids[0]]["ch"], "kind": "vo", "bg": None, "s": round(t, 3)}
        bg = item.get("bg")
        if bg:
            lead = bg.get("lead", 0.0)
            S = sum(p[2] - p[1] for p in bg["parts"])
            avail = D - lead
            rmin, rmax = bg.get("min_rate", RATE_MIN), bg.get("max_rate", RATE_MAX)
            rate = max(rmin, min(rmax, S / avail))
            play = S / rate
            c0 = at + lead
            parts, tt = [], c0
            for src, a_, b_ in bg["parts"]:
                d = (b_ - a_) / rate
                parts.append({"src": src, "in": a_, "out": b_, "t0": round(tt, 4), "t1": round(tt + d, 4)})
                tt += d
            cut = play > avail + 1e-6
            if cut:                                          # 素材比画外音长：在块尾截断
                over = play - avail
                last = parts[-1]
                last["t1"] = round(last["t1"] - over, 4)
                last["out"] = round(last["in"] + (last["t1"] - last["t0"]) * rate, 4)
            hold_from = None if cut or play >= avail - 0.02 else round(c0 + play, 4)
            caps = []
            for p in parts:
                for m0, m1, name, zh in ([] if bg.get("no_caps") else caps_map.get(p["src"], [])):
                    lo, hi = max(m0, p["in"]), min(m1, p["out"])
                    if hi - lo < 0.15:
                        continue
                    caps.append({"t0": round(p["t0"] + (lo - p["in"]) / rate, 3), "t1": round(p["t0"] + (hi - p["in"]) / rate, 3), "name": name, "zh": zh})
            clips[bg["id"]] = {"seg": seg["id"], "s": round(c0, 3), "e": round(at + D, 3), "rate": round(rate, 4), "parts": parts, "hold_from": hold_from,
                               "cut": bool(cut), "credit": bg.get("credit", credit), "tag": bg.get("tag", ""), "nav": bg.get("nav"), "caps": caps, "bar": bg.get("bar")}
            seg["bg"] = bg["id"]
        segs.append(seg)
        t += D + item.get("gap", GAP_VO)
    never = [i for i in order if i not in used]
    assert not never, f"这些句子没放进 plan：{never}"
    total = round(t - plan[-1].get("gap", GAP_VO) + TAIL, 3)
    for a, b in zip(segs, segs[1:]):
        a["e"] = b["s"]
    segs[-1]["e"] = total
    if segs[-1]["bg"]:                                     # 最后一个镜头带演示视频：铺到片尾（片尾那 1.4 s 不能是空白）
        clips[segs[-1]["bg"]]["e"] = total
    for q in cues:
        q["seg"] = next(s["id"] for s in segs if s["s"] <= q["s"] + 1e-6 < s["e"])
    cues.sort(key=lambda q: q["s"])
    frames = int(round(total * FPS))
    tl = {"fps": FPS, "frames": frames, "total": total, "title": TITLE, "est": est, "credit": credit,
          "chapters": sc["chapters"], "segs": segs, "cues": cues, "clips": clips, "tts": {"blocks": blocks, "total": round(tts_total, 3)}}
    (HERE / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "timeline.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"整片 {total:.1f} s（{frames} 帧）{'【按字数估的时间】' if est else ''}：{len(segs)} 段、{len(cues)} 句画外音、{len(clips)} 个演示视频")
    for s in segs:
        c = clips.get(s["bg"]) if s["bg"] else None
        extra = f"  视频 ×{c['rate']:.2f}{'（截断）' if c['cut'] else ''}{'，定格 ' + format(c['hold_from'], '.1f') if c['hold_from'] else ''}" if c else ""
        print(f"  {s['id']:4s} {s['s']:7.2f}–{s['e']:7.2f}  第{s['chapter'] + 1}章  {s['title']}{extra}")


if __name__ == "__main__":
    main()
