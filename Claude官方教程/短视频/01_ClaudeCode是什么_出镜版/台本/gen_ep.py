# -*- coding: utf-8 -*-
r"""台本 + 选段 → 录制稿.json / plan.json / 制作\02_配音\edit\tts_edit.json（占位）/ 出镜稿 md。

  python gen_ep.py                 用估时（悠一还没录）：中文每字 0.185 s、英文词 0.4 s、句间 0.22 s、场景之间 0.30 s
  python gen_ep.py --timing 台本\timing.json   用真时间：{"N01": [起, 止], …}（秒，从他口播视频起点算；own_voice.py asr 之后整理出来）

场景的长度 = 它最后一句说完的时刻 − 上一个场景最后一句说完的时刻（NATURAL_TIMING：场景切在句子结束处，下一句的 a = 他实际的停顿）。
素材选段按场景长度重新分配（权重 w；够不够、放慢、定格都在这里算），所以改了台本 / 换了真时间，重跑一遍就行。
"""
import json
import re
import sys
from math import inf
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parent
sys.path.insert(0, str(HERE))
import script_data as D  # noqa: E402

TAIL = 0.8
LABEL = {"rec": "悠一的录屏", "c1": "官方课第1课", "c2": "官方课第2课", "c3": "官方课第3课", "c4": "官方课第4课", "c6": "官方课第6课", "p4": "官方课·权限模式", "c8": "官方课第8课", "perm": "悠一的录屏（五种权限）"}


def est_line(zh):
    han = sum(1 for ch in zh if "一" <= ch <= "鿿")
    words = re.findall(r"[A-Za-z][A-Za-z0-9.+\-]*", zh)
    nums = re.findall(r"\d+", zh)
    return han * 0.185 + len(words) * 0.40 + len(nums) * 0.45 + 0.1


def timings(timing_file):
    ids = [l["id"] for l in D.LINES]
    if timing_file:
        t = json.loads(Path(timing_file).read_text(encoding="utf-8"))
        return {i: tuple(t[i]) for i in ids}, True
    out, t = {}, 0.35
    scene_first = {sc["lines"][0] for sc in D.SCENES}
    zh = {l["id"]: l["zh"] for l in D.LINES}
    for i in ids:
        if i in scene_first and i != ids[0]:
            t += 0.08                      # 场景之间比句间再多一点点
        d = est_line(zh[i])
        out[i] = (round(t, 3), round(t + d, 3))
        t += d + 0.22
    return out, False


def alloc(spans, T):
    n = len(spans)
    caps = [inf if s.get("hold") else (s["b"] - s["a"]) / s.get("speed", 1.0) for s in spans]
    w = [s.get("w", 1.0 if s.get("hold") else caps[i]) for i, s in enumerate(spans)]
    L = [0.0] * n
    rem, free = T, list(range(n))
    while free:
        tw = sum(w[i] for i in free)
        over = [i for i in free if rem * w[i] / tw > caps[i] + 1e-9]
        if not over:
            for i in free:
                L[i] = rem * w[i] / tw
            rem = 0.0
            break
        for i in over:
            L[i] = caps[i]
            rem -= caps[i]
            free.remove(i)
    return L, rem


def fit_spans(spans, T):
    """素材不够长：把没写 speed 的非定格段放慢（最慢 0.75×）。"""
    cap = sum(inf if s.get("hold") else (s["b"] - s["a"]) / s.get("speed", 1.0) for s in spans)
    if cap >= T - 0.05:
        return spans
    slow = [s for s in spans if not s.get("hold") and "speed" not in s]
    S_ = sum(s["b"] - s["a"] for s in slow)
    if not slow or S_ <= 0:
        return spans
    f = min(1.33, (S_ + (T - cap)) / S_)
    return [dict(s, speed=round(1 / f, 3)) if s in slow else s for s in spans]


def to_ranges(spans, T, info):
    spans = fit_spans(spans, T)
    L, rem = alloc(spans, T)
    out = []
    for s, l in zip(spans, L):
        if l <= 0.04:
            continue
        r = {"src": s["src"]}
        if s.get("hold"):
            r.update({"in": round(s["a"], 3), "hold": round(l, 3)})
        else:
            sp = s.get("speed", 1.0)
            r.update({"in": round(s["a"], 3), "out": round(s["a"] + l * sp, 3), "mute": True})
            if sp != 1.0:
                r["speed"] = sp
        for k in ("crop", "bg"):
            if s.get(k):
                r[k] = s[k]
        out.append(r)
    if rem > 0.04 and out:
        last = spans[-1]
        t_last = last["a"] if last.get("hold") else last["b"] - 0.05
        r = {"src": last["src"], "in": round(t_last, 3), "hold": round(rem, 3)}
        for k in ("crop", "bg"):
            if last.get(k):
                r[k] = last[k]
        out.append(r)
        info["pad"] = round(rem, 2)
    info["slow"] = any(r.get("speed", 1.0) != 1.0 for r in out)
    return out


def main():
    timing_file = sys.argv[sys.argv.index("--timing") + 1] if "--timing" in sys.argv else None
    tm, real = timings(timing_file)
    ids = [l["id"] for l in D.LINES]
    assert [i for sc in D.SCENES for i in sc["lines"]] == ids, "场景里的句子顺序和台本不一致"
    plan, report, prev_end = [], [], 0.0
    for sc in D.SCENES:
        s_end = tm[sc["lines"][-1]][1]
        T = round(s_end - prev_end, 3)
        item = {"id": sc["id"], "name": sc["name"], "mode": sc["mode"]}
        info = {}
        if sc["kind"] == "card":
            item.update({"type": "card", "kind": "card", "overlay": "card", "dur": 0.5})
        else:
            item.update({"type": "clip", "kind": "demo", "overlay": "clip", "credit": sc.get("credit", ""), "ranges": to_ranges(sc["top"], T, info)})
            if sc["mode"] == "two":
                item["ranges2"] = to_ranges(sc["bottom"], T, info)
        item["lines"] = [{"id": i, "a": round(tm[i][0] - prev_end, 3)} for i in sc["lines"]]
        plan.append(item)
        report.append((sc["id"], sc["name"], sc["mode"], T, info))
        prev_end = s_end
    total = prev_end + TAIL
    (EP / "台本" / "plan.json").write_text(json.dumps({"layout": "faceb", "faceph": False, "plan": plan}, ensure_ascii=False, indent=1), encoding="utf-8")
    rec = {"slug": D.TITLE["slug"], "title": D.TITLE["title"], "kicker": D.TITLE["kicker"], "hook": D.TITLE["hook"],
           "lines": [{k: l[k] for k in ("id", "zh", "say", "en")} for l in D.LINES]}
    (EP / "台本" / "录制稿.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    ed = EP / "制作" / "02_配音" / "edit"
    ed.mkdir(parents=True, exist_ok=True)
    edit = {"total": round(prev_end + 0.2, 3), "estimated": not real, "lines": [
        {"id": l["id"], "zh": l["zh"], "take": "user_voice" if real else "estimate", "src": [tm[l["id"]][0], tm[l["id"]][1]], "n0": round(tm[l["id"]][0] - 0.1, 3), "n1": round(tm[l["id"]][1] + 0.1, 3),
         "s": tm[l["id"]][0], "e": tm[l["id"]][1], "gain_db": 0.0} for l in D.LINES]}
    (ed / "tts_edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=2), encoding="utf-8")
    # 报告 + 给悠一看的稿子
    print(f"{'真时间' if real else '估时'}：整片约 {total:.1f} s（{total / 60:.2f} 分钟），{len(ids)} 句，{sum(len(l['zh']) for l in D.LINES)} 个字符，{len(D.SCENES)} 个场景")
    for sid, name, mode, T, info in report:
        extra = []
        if info.get("pad"):
            extra.append(f"素材不够，定格补 {info['pad']} s")
        if info.get("slow"):
            extra.append("有放慢")
        print(f"  {sid} {mode:4s} {T:5.1f} s  {name}" + (f"  ← {'；'.join(extra)}" if extra else ""))
    write_md(tm, real, total, report)


MODE_CN = {"one": "单窗", "two": "双窗（上下叠）", "big": "大窗（两窗合并那么大）"}


def span_text(sp):
    if sp.get("hold"):
        return f"{LABEL[sp['src']]} {sp['a']:.0f}s 定格"
    return f"{LABEL[sp['src']]} {sp['a']:.0f}–{sp['b']:.0f}s"


def write_md(tm, real, total, report):
    by = {l["id"]: l for l in D.LINES}
    out = [f"# 《Claude官方教程》第 1 期｜Claude Code 是什么、怎么工作（出镜版 · 实际口播稿 / 字幕版）", "",
           f"- 这是按你实际说的话整理的字幕稿：共 {len(D.LINES)} 行（T01–T{len(D.LINES):02d}）、{sum(len(l['zh']) for l in D.LINES)} 个字符；成片时长约 **{total / 60:.1f} 分钟**（{'剪完停顿后的真时间' if real else '估时'}）。",
           "- 字幕只改了转写器听错的专名 / 同音字，没有润色；英文字幕是忠实直译。",
           "- 每个场景标了画面（窗口模式 + 用哪段素材）和时长。", ""]
    for sc, (sid, name, mode, T, info) in zip(D.SCENES, report):
        out.append(f"## {sid}　{name}（{MODE_CN[mode]}，约 {T:.0f} 秒）")
        out.append("")
        for i in sc["lines"]:
            out.append(f"- **{i}**　{by[i]['zh']}")
        if sc["kind"] == "card":
            show = "自己画的说明图"
        else:
            parts = ["、".join(span_text(s) for s in sc["top"])]
            if mode == "two":
                parts.append("、".join(span_text(s) for s in sc["bottom"]))
            show = ("上窗：" if mode == "two" else "") + parts[0] + ("；下窗：" + parts[1] if len(parts) > 1 else "")
        out += ["", f"> 画面：{show}", ""]
    (EP / "台本" / "实际口播稿_字幕版.md").write_text(chr(10).join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
