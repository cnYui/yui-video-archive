# -*- coding: utf-8 -*-
"""时间轴：画面（场景 = 一段或几段素材 / 一张官网页面截图 / 一张卡片）+ 画外音（Fish 网页版「赛马娘（曼波欧耶版）」）+ 对白字幕（原片里人说的话的译文）。素材为主，话少。
从 OpenAI相关 的引擎模板改：①ranges 默认套 common.SRC_CROP（裁掉原片底部自带的英文烧录字幕）；②场景可以带 dlg（对白字幕，按原片时间码写，自动换算成成片时间）；
③新增 type = shot（官网页面截图镜头：相机推拉 + 高亮框）；④shot 的相机关键帧 / 高亮框的时间可以锚在某句配音的某个词上（["N12", "48%", 偏移秒]），改配音不用改时间。

  python build_timeline.py          → timeline.json / timeline.js（配音用 ../02_配音/edit/tts_edit.json）
  python build_timeline.py --est    → 配音还没出：按字数估时间（出版式小样用），timeline.json 里 est = true

输入：../../台本/录制稿.json（chapters / lines：id、zh、en（**每句必须有**）、say）、../../台本/plan.json（plan：场景按先后顺序排）。
场景（plan 里每项）：
- type = clip：ranges = [{src, in, out[, crop, mute, gain_db]}, …] 几段素材首尾相接（crop 缺省 = common.SRC_CROP[src]，写 null = 不裁）；
    dlg = [{id, src, a, b, who, cls, zh, en}]：原片里人说的话，a/b 是**原片时间码**（秒），自动换成成片时间，进字幕带（kind = dlg）；
- type = shot：img = 官网截图名（素材/官网截图/<img>.png）、dur、cam = [{t, x, y, z}]（相机关键帧：场景内秒数，x/y = 画面中心在图里的比例位置，z = 放大倍数，1 = 整张放进演示区）、
    hl = [{a, b, key | box, label, pad, in}]（高亮框：key = boxes.json 里的文字，box = [x0, y0, x1, y1] 比例；a/b 可以写 ["句号", "词", 偏移秒]）；
- type = card：dur 秒的卡片（overlay = title / outro）。
- lines = [{id, a}, …]：这个场景里的画外音，a = 这句话从场景开头起第几秒开口；前一句没念完就顺延（间隔 GAP_LINE）。话比画面长：场景延长到话说完 + PAD_END（clip 场景把最后一段素材接着往下放，放完定格）；spill = true 则不延长。
- caps = [{a, b, zh, sub}]：素材上的小字注释（场景内的秒数）；name / tag / credit：左上角的名称和来源标签，右上角的来源。
配音按 tts.blocks = [b0, b1, at, 1.0] 切成块放进成片（mix_audio.py 读），字幕和画面用同一套时间。
"""
import json
import sys

from PIL import Image

from common import EP, FPS, HERE, HAS_AUDIO, SRC_CROP, src_duration

sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
import bilingual_std as B  # noqa: E402  项目统一的中英双语字幕标准（拆条、显示区间、SRT）

LEAD, TAIL = 0.0, 1.4          # 开头不留空白：片头（悠一）后面第一帧就是素材画面
GAP_LINE, PAD_END = 0.18, 0.4
EST_CPS, EST_GAP = 6.4, 0.30           # 估时间：字/秒、句间停顿（曼波声线实测约 6.3 字/秒）
TAG_UNITS = 5.2                        # 对白字幕前面的说话人小标签占的宽度（按中文字宽算）
SHOTS = EP / "素材" / "官网截图"


def main():
    est = "--est" in sys.argv
    sc = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))
    plan = json.loads((EP / "台本" / "plan.json").read_text(encoding="utf-8"))["plan"]
    boxes = json.loads((SHOTS / "boxes.json").read_text(encoding="utf-8")) if (SHOTS / "boxes.json").exists() else {}
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
    capwarn = []                              # 注释（caps）结束时刻超过场景长度：叠加层不会在场景结束处截掉，会压到下一个场景上
    cues, segs, blocks, clips, dsubs = [], [], [], {}, []
    cue_at = {}                               # 句号 → (起, 止, 中文)，给 ["句号", "词", 偏移] 这种时间锚用
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
            cue_at[ln["id"]] = (start, end, lines[ln["id"]]["zh"])
        d = d0
        if placed and not item.get("spill"):
            d = max(d0, placed[-1][2] - t0 + PAD_END)
        for c in item.get("caps", []):
            if isinstance(c["b"], (int, float)) and c["b"] > d + 0.05:
                capwarn.append(f"{item['id']}：注释“{c['zh']}”到 {c['b']} s，场景只有 {d:.1f} s")
        for lid, start, end, n0, n1, at in placed:
            cues.append({"id": lid, "zh": lines[lid]["zh"], "s": round(start, 3), "e": round(end, 3), "kind": "vo", "seg": item["id"]})
            blocks.append([round(n0, 4), round(n1, 4), round(at, 4), 1.0])
        seg = {"id": item["id"], "title": item.get("name") or item.get("kind") or item["id"], "chapter": item.get("chapter", -1),
               "kind": item["type"], "s": round(t0, 3), "e": round(t0 + d, 3)}
        segs.append(seg)

        def rel(x):
            """场景内秒数；["句号", "词", 偏移] = 这句配音里说到这个词的时刻（按字数估）相对场景开头。"""
            if isinstance(x, (int, float)):
                return float(x)
            if x == "end":                                   # 撑到场景结束
                return d
            cid, phrase = x[0], x[1]
            off = x[2] if len(x) > 2 else 0.0
            s_, e_, zh_ = cue_at[cid]
            k = zh_.index(phrase)
            return s_ + (e_ - s_) * (k / len(zh_)) + off - t0

        if item["type"] == "clip":
            rs, cur = [], t0
            for r in item["ranges"]:
                crop = r["crop"] if "crop" in r else SRC_CROP.get(r["src"])
                rs.append({"src": r["src"], "in": r["in"], "out": r["out"], "s": round(cur, 3), "e": round(cur + r["out"] - r["in"], 3),
                           "mute": bool(r.get("mute")), "gain_db": r.get("gain_db", 0), "crop": crop})
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
            # 对白字幕：原片时间码 → 成片时间
            for dl in item.get("dlg", []):
                hit = [r for r in rs if r["src"] == dl["src"] and r["in"] - 1e-6 <= dl["a"] and dl["b"] <= r["out"] + 1e-6]
                assert hit, f"{item['id']} 对白 {dl['id']}（{dl['src']} {dl['a']}–{dl['b']}）不在这个场景放的素材片段里：{[(r['src'], r['in'], r['out']) for r in rs]}"
                r = hit[0]
                dsubs.append({"id": dl["id"], "k": 0, "zh": dl["zh"], "en": dl["en"], "who": dl.get("who", ""), "whoCls": dl.get("cls", ""), "kind": "dlg",
                              "s": round(r["s"] + dl["a"] - r["in"], 3), "e": round(r["s"] + dl["b"] - r["in"], 3), "seg": item["id"]})
            clips[item["id"]] = {"kind": item.get("kind", "clip"), "ranges": rs, "s": round(t0, 3), "e": round(t0 + d, 3), "hold": hold,
                                 "name": item.get("name", ""), "tag": item.get("tag", ""), "credit": item.get("credit", ""),
                                 "overlay": item.get("overlay", "clip"), "ui": item.get("ui", {}),
                                 "caps": [{"s": round(t0 + rel(c["a"]), 3), "e": round(t0 + rel(c["b"]), 3), "zh": c["zh"], "sub": c.get("sub", "")} for c in item.get("caps", [])],
                                 "silent": all(not HAS_AUDIO[r["src"]] or r["mute"] for r in rs)}
        elif item["type"] == "shot":
            im = Image.open(SHOTS / f"{item['img']}.png")
            hl = []
            for h in item.get("hl", []):
                box = h.get("box") or boxes[item["img"]][h["key"]]
                assert box, f"{item['id']} 高亮 {h.get('key')}：boxes.json 里没有这段文字的位置"
                hl.append({"a": round(rel(h["a"]), 3), "b": round(rel(h["b"]), 3), "box": [round(v, 5) for v in box], "label": h.get("label", ""), "pad": h.get("pad", 10), "in": bool(h.get("in"))})
            cam = [{"t": round(rel(c["t"]), 3), "x": c.get("x", 0.5), "y": c.get("y", 0.5), "z": c.get("z", 1.0)} for c in item.get("cam", [{"t": 0}])]
            clips[item["id"]] = {"kind": "shot", "ranges": [], "s": round(t0, 3), "e": round(t0 + d, 3), "hold": 0.0,
                                 "name": item.get("name", ""), "tag": item.get("tag", ""), "credit": item.get("credit", ""),
                                 "overlay": "clip", "ui": item.get("ui", {}),
                                 "caps": [{"s": round(t0 + rel(c["a"]), 3), "e": round(t0 + rel(c["b"]), 3), "zh": c["zh"], "sub": c.get("sub", "")} for c in item.get("caps", [])],
                                 "silent": True,
                                 "shot": {"img": item["img"], "w": im.size[0], "h": im.size[1], "fit": item.get("fit", 0.94), "cam": cam, "hl": hl}}
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
    cues = sorted(cues, key=lambda q: q["s"])
    subs, over, soft = [], [], []
    for q in cues:
        ln = lines[q["id"]]
        en = ln.get("en", "")
        assert en, f"{q['id']} 没有英文：台本每句都要写 en（项目的中英双语字幕标准），见技能 references/subtitles.md"
        chunks = B.split_pair_aligned(q["zh"], en, 0.0, cuts=[tuple(c) for c in ln["cut"]] if ln.get("cut") else None)
        for k, ((z, e, w), (a, b)) in enumerate(zip(chunks, B.chunk_times(q["s"], q["e"], chunks))):
            if w > B.ZH_MAX or len(e) > B.EN_SOFT:
                over.append(f"{q['id']}.{k + 1}")
            elif len(e) > B.EN_MAX:
                soft.append(f"{q['id']}.{k + 1}")
            subs.append({"id": q["id"], "k": k, "zh": z, "en": e, "who": "", "whoCls": "", "kind": "vo", "s": round(a, 3), "e": round(b, 3), "seg": q["seg"]})
    for x in dsubs:                                              # 对白字幕：一条一屏，不拆（太长就在 plan 里写短）
        if B.zh_units(x["zh"]) + (TAG_UNITS if x["who"] else 0) > B.ZH_MAX or len(x["en"]) > B.EN_SOFT:
            over.append(f"{x['id']}（对白）")
        subs.append(x)
    subs.sort(key=lambda x: x["s"])
    overlap = [f"{a['id']}.{a['k']} 和 {b['id']}.{b['k']}（{a['kind']}/{b['kind']}）" for a, b in zip(subs, subs[1:]) if b["s"] < a["e"] - 0.05]
    for x, (a, b) in zip(subs, B.display_windows([(x["s"], x["e"]) for x in subs])):
        x["a"], x["b"] = round(a, 3), round(b, 3)
    tl = {"fps": FPS, "frames": frames, "total": total, "title": sc["title"], "est": est,
          "chapters": sc["chapters"], "segs": segs, "cues": cues, "subs": subs, "clips": clips,
          "tts": {"blocks": blocks, "total": round(tts_total, 3)}}
    for k in ("sub", "tocTag", "titleCard", "outroCard"):        # 页面要用的文案（左栏副标题、开场标题、收尾卡片）
        if k in sc:
            tl[k] = sc[k]
    (HERE / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "timeline.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    foot = sum(r["e"] - r["s"] for c in clips.values() for r in c["ranges"])
    shot = sum(c["e"] - c["s"] for c in clips.values() if c["kind"] == "shot")
    voiced = sum(q["e"] - q["s"] for q in cues)
    print(f"整片 {total:.1f} s（{frames} 帧）{'【按字数估的时间】' if est else ''}：{len(segs)} 个场景、{len(cues)} 句画外音（共 {voiced:.1f} s 有声，占 {voiced / total:.0%}）、"
          f"视频素材 {foot:.1f} s、官网页面镜头 {shot:.1f} s、对白字幕 {len(dsubs)} 条；字幕共 {len(subs)} 条（超长没拆开：{' '.join(over) or '无'}；英文略超 90 字符：{' '.join(soft) or '无'}）")
    print(f"字幕互相重叠（画外音和对白不能叠）：{'；'.join(overlap) or '无'}")
    for s in segs:
        c = clips[s["id"]]
        print(f"  {s['id']:4s} {s['kind']:4s} {s['s']:7.2f}–{s['e']:7.2f}  章 {s['chapter'] + 1}  {s['title']}" + (f"  （定格 {c['hold']} s）" if c["hold"] else ""))
    if capwarn:
        print("【注意】" + "；".join(capwarn) + "：要么缩短注释，要么把场景拉长")
    for x in subs:
        print(f"    {x['id']}.{x['k']} {x['s']:7.2f}–{x['e']:7.2f} [{x['seg']}] {x['kind']} {(x['who'] + '：') if x['who'] else ''}{x['zh']}")


if __name__ == "__main__":
    main()
