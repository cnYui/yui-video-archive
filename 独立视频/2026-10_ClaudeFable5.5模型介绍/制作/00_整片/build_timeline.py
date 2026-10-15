# -*- coding: utf-8 -*-
"""时间轴：画面（场景 = 一段或几段素材 / 一张卡片）+ 画外音（Fish 网页版「赛马娘（曼波欧耶版）」）。素材为主，话少。

  python build_timeline.py          → timeline.json / timeline.js（配音用 ../02_配音/edit/tts_edit.json）
  python build_timeline.py --est    → 配音还没出：按字数估时间（出版式小样用），timeline.json 里 est = true

输入：../../台本/录制稿.json（chapters / lines：id、zh、say）、../../台本/plan.json（plan：场景按先后顺序排）。
场景：
- type = clip：ranges = [{src, in, out}, …] 几段素材首尾相接（硬切，不同素材也行）；type = card：dur 秒的卡片（演示区放卡片，没有素材画面）。
- lines = [{id, a}, …]：这个场景里的画外音，a = 这句话从场景开头起第几秒开口；前一句没念完就顺延（间隔 GAP_LINE）。
- 话比画面长：场景延长到话说完 + PAD_END（clip 场景把最后一段素材接着往下放，素材放完了就定格最后一帧）；spill = true 则不延长，话可以压到下一个场景里。
- caps = [{a, b, zh}]：素材上的小字注释（场景内的秒数）；name / tag / credit：左上角的作品名和模型，右上角的来源。
- 配音按 tts.blocks = [b0, b1, at, 1.0] 切成块放进成片（mix_audio.py 读），字幕和画面用同一套时间。
"""
import json
import sys

from common import EP, FPS, HERE, HAS_AUDIO, src_duration

LEAD, TAIL = 0.0, 1.4          # 开头不留空白：片头（悠一）后面第一帧就是素材画面
GAP_LINE, PAD_END = 0.18, 0.4
EST_CPS, EST_GAP = 6.4, 0.30           # 估时间：字/秒、句间停顿（曼波声线实测约 6.3 字/秒）


def main():
    est = "--est" in sys.argv
    sc = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))
    plan = json.loads((EP / "台本" / "plan.json").read_text(encoding="utf-8"))["plan"]
    lines = {l["id"]: l for l in sc["lines"]}
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
    cues, segs, blocks, clips = [], [], [], {}
    t, prev_end = LEAD, -1.0
    for item in plan:
        t0 = t + item.get("lead", 0.0)
        if item["type"] == "clip":
            d0 = sum(r["out"] - r["in"] for r in item["ranges"])
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
        for lid, start, end, n0, n1, at in placed:
            cues.append({"id": lid, "zh": lines[lid]["zh"], "s": round(start, 3), "e": round(end, 3), "kind": "vo", "seg": item["id"]})
            blocks.append([round(n0, 4), round(n1, 4), round(at, 4), 1.0])
        seg = {"id": item["id"], "title": item.get("name") or item.get("kind") or item["id"], "chapter": item.get("chapter", -1),
               "kind": item["type"], "s": round(t0, 3), "e": round(t0 + d, 3)}
        segs.append(seg)
        if item["type"] == "clip":
            rs, cur = [], t0
            for r in item["ranges"]:
                rs.append({"src": r["src"], "in": r["in"], "out": r["out"], "s": round(cur, 3), "e": round(cur + r["out"] - r["in"], 3),
                           "mute": bool(r.get("mute")), "gain_db": r.get("gain_db", 0)})
                cur += r["out"] - r["in"]
            hold = 0.0
            if d > d0 + 1e-6:                  # 话比画面长：最后一段素材接着往下放，放完了定格
                r = rs[-1]
                if r["src"] not in sdur:
                    sdur[r["src"]] = src_duration(r["src"])
                room = max(0.0, sdur[r["src"]] - 0.05 - r["out"])
                grow = min(d - d0, room)
                r["out"] = round(r["out"] + grow, 3)
                r["e"] = round(r["e"] + grow, 3)
                hold = round(d - d0 - grow, 3)
            clips[item["id"]] = {"kind": item.get("kind", "clip"), "ranges": rs, "s": round(t0, 3), "e": round(t0 + d, 3), "hold": hold,
                                 "name": item.get("name", ""), "tag": item.get("tag", ""), "credit": item.get("credit", ""),
                                 "overlay": item.get("overlay", "clip"), "ui": item.get("ui", {}),
                                 "caps": [{"s": round(t0 + c["a"], 3), "e": round(t0 + c["b"], 3), "zh": c["zh"], "sub": c.get("sub", "")} for c in item.get("caps", [])],
                                 "silent": all(not HAS_AUDIO[r["src"]] or r["mute"] for r in rs)}
        else:
            clips[item["id"]] = {"kind": item.get("kind", "card"), "ranges": [], "s": round(t0, 3), "e": round(t0 + d, 3), "hold": 0.0,
                                 "name": item.get("name", ""), "tag": "", "credit": "", "overlay": item.get("overlay", item.get("kind", "card")),
                                 "ui": item.get("ui", {}), "caps": [], "silent": True}
        t += (t0 - t) + d + item.get("gap", 0.0)
    total = round(t + TAIL, 3)
    segs[-1]["e"] = total
    for a, b in zip(segs, segs[1:]):
        a["e"] = b["s"]
    frames = int(round(total * FPS))
    tl = {"fps": FPS, "frames": frames, "total": total, "title": sc["title"], "est": est,
          "chapters": sc["chapters"], "segs": segs, "cues": sorted(cues, key=lambda q: q["s"]), "clips": clips,
          "tts": {"blocks": blocks, "total": round(tts_total, 3)}}
    for k in ("sub", "titleCard", "factsCard", "outroCard"):        # 页面要用的文案（左栏副标题、开场标题、官方现状卡片、收尾卡片）
        if k in sc:
            tl[k] = sc[k]
    (HERE / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "timeline.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    foot = sum(r["e"] - r["s"] for c in clips.values() for r in c["ranges"])
    voiced = sum(q["e"] - q["s"] for q in cues)
    print(f"整片 {total:.1f} s（{frames} 帧）{'【按字数估的时间】' if est else ''}：{len(segs)} 个场景、{len(cues)} 句画外音（共 {voiced:.1f} s 有声）、素材画面 {foot:.1f} s")
    for s in segs:
        c = clips[s["id"]]
        print(f"  {s['id']:4s} {s['kind']:4s} {s['s']:7.2f}–{s['e']:7.2f}  章 {s['chapter'] + 1}  {s['title']}" + (f"  （定格 {c['hold']} s）" if c["hold"] else ""))
    for q in tl["cues"]:
        print(f"    {q['id']} {q['s']:7.2f}–{q['e']:7.2f} [{q['seg']}] {q['zh']}")


if __name__ == "__main__":
    main()
