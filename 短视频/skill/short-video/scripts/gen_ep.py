# -*- coding: utf-8 -*-
r"""台本 + 选段 → 录制稿.json / plan.json / 制作\02_配音\edit\tts_edit.json / 实际口播稿_字幕版.md（faceb 版式：每个场景自己选窗口模式 one / two / big）。

  python gen_ep.py <本条目录>                                          用估时（口播还没录 / 没剪）：中文每字 0.185 s、英文词 0.4 s、句间 0.22 s、场景之间 0.30 s
  python gen_ep.py <本条目录> --timing 制作\01_口播\timing.json         用真时间：{"T01": [起, 止], …}（母带上的秒；build_talk.py plan 的输出）

读 <本条>\台本\script_data.py：TITLE（slug / title / kicker / hook）、LABEL（素材短名 → 中文名，写口播稿用）、LINES（id / zh / say / en）、
SCENES（每个场景：mode、kind、lines、top / bottom 选段、credit）。模板 assets/oncam-multiclip/template/台本/script_data.py，真实例子在 example_ep1/。
场景的长度 = 它最后一句说完的时刻 − 上一个场景最后一句说完的时刻（NATURAL_TIMING：场景切在句子结束处，下一句的 a = 他实际的停顿）。
素材选段按场景长度重新分配（权重 w = 相对时长；够不够、放慢、定格都在这里算；素材比分到的短就放慢，最慢 0.75×，再不够就定格补满），
所以改了台本 / 换了真时间，重跑一遍就行。选段写法：S(src, a, b, w, speed, crop) 放一段；H(src, a, w) 定格 a 那一帧 w 秒。

**定格报告**（2026-10-06 第 1 期出镜版加的）：每个场景分上窗 / 下窗各报定格几秒、最长一段几秒；单段 > 3 s 标 ⚠。
原来只报上窗的“定格补 x s”，下窗定格 10.9 s 要翻 plan.json 才看到，观众只看见另一个窗口在动。有意停住讲一张图 / 一个对话框的可以留，其余补素材（官方课的安全段、别的录屏片段）或把场景改成单窗。
渲前再用 scripts/audit_holds.py 对 build_timeline 之后的 timeline.json 查一遍。
"""
import json
import re
import sys
from math import inf
from pathlib import Path

TAIL = 0.8
HOLD_WARN = 3.0                      # 单段定格超过它标 ⚠


def est_line(zh):
    han = sum(1 for ch in zh if "一" <= ch <= "鿿")
    words = re.findall(r"[A-Za-z][A-Za-z0-9.+\-]*", zh)
    nums = re.findall(r"\d+", zh)
    return han * 0.185 + len(words) * 0.40 + len(nums) * 0.45 + 0.1


def timings(D, timing_file):
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
    holds = [r["hold"] for r in out if r.get("hold")]
    info["hold"], info["hold_max"] = round(sum(holds), 2), round(max(holds, default=0.0), 2)
    return out


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    EP = Path(args[0]).resolve()
    timing_file = args[args.index("--timing") + 1] if "--timing" in args else None
    sys.path.insert(0, str(EP / "台本"))
    import script_data as D  # noqa: E402
    tm, real = timings(D, timing_file)
    ids = [l["id"] for l in D.LINES]
    assert [i for sc in D.SCENES for i in sc["lines"]] == ids, "场景里的句子顺序和台本不一致"
    plan, report, prev_end = [], [], 0.0
    for sc in D.SCENES:
        s_end = tm[sc["lines"][-1]][1]
        T = round(s_end - prev_end, 3)
        item = {"id": sc["id"], "name": sc["name"], "mode": sc["mode"]}
        top, bot = {}, {}
        if sc["kind"] == "card":
            item.update({"type": "card", "kind": "card", "overlay": "card", "dur": 0.5})
        else:
            item.update({"type": "clip", "kind": "demo", "overlay": "clip", "credit": sc.get("credit", ""), "ranges": to_ranges(sc["top"], T, top)})
            if sc["mode"] == "two":
                item["ranges2"] = to_ranges(sc["bottom"], T, bot)
        item["lines"] = [{"id": i, "a": round(tm[i][0] - prev_end, 3)} for i in sc["lines"]]
        plan.append(item)
        report.append((sc["id"], sc["name"], sc["mode"], T, top, bot))
        prev_end = s_end
    total = prev_end + TAIL
    (EP / "台本" / "plan.json").write_text(json.dumps({"layout": "faceb", "plan": plan}, ensure_ascii=False, indent=1), encoding="utf-8")
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
    warn = []
    for sid, name, mode, T, top, bot in report:
        extra = []
        for win, info in (("上窗", top), ("下窗", bot)):
            if not info:
                continue
            tag = win if bot else ""                       # 只有一个窗口的场景不写“上窗”
            if info.get("pad"):
                extra.append(f"{tag}素材不够，定格补 {info['pad']} s")
            if info.get("slow"):
                extra.append(f"{tag}有放慢")
            if info.get("hold_max", 0) > HOLD_WARN:
                extra.append(f"⚠ {tag}定格最长 {info['hold_max']} s（共 {info['hold']} s）")
                warn.append((sid, win if bot else "单窗", info["hold_max"]))
        print(f"  {sid} {mode:4s} {T:5.1f} s  {name}" + (f"  ← {'；'.join(extra)}" if extra else ""))
    if warn:
        print(f"⚠ 单段定格 > {HOLD_WARN:g} s 的 {len(warn)} 处：" + "、".join(f"{s} {w} {m} s" for s, w, m in warn)
              + "（有意停住讲一张图 / 一个对话框的可以留，其余补素材或把场景改成单窗）")
    else:
        print(f"单段定格都 ≤ {HOLD_WARN:g} s")
    write_md(D, EP, tm, real, total, report)
    return 0


MODE_CN = {"one": "单窗", "two": "双窗（上下叠）", "big": "大窗（两窗合并那么大）"}


def span_text(D, sp):
    label = getattr(D, "LABEL", {}).get(sp["src"], sp["src"])
    if sp.get("hold"):
        return f"{label} {sp['a']:.0f}s 定格"
    return f"{label} {sp['a']:.0f}–{sp['b']:.0f}s"


def write_md(D, EP, tm, real, total, report):
    by = {l["id"]: l for l in D.LINES}
    n = len(D.LINES)
    out = [f"# {D.TITLE['title']}（出镜版 · 实际口播稿 / 字幕版）", "",
           f"- 这是按你实际说的话整理的字幕稿：共 {n} 行（T01–T{n:02d}）、{sum(len(l['zh']) for l in D.LINES)} 个字符；成片时长约 **{total / 60:.1f} 分钟**（{'剪完停顿后的真时间' if real else '估时'}）。",
           "- 字幕只改了转写器听错的专名 / 同音字，没有润色；英文字幕是忠实直译。",
           "- 每个场景标了画面（窗口模式 + 用哪段素材）和时长。", ""]
    for sc, (sid, name, mode, T, top, bot) in zip(D.SCENES, report):
        out.append(f"## {sid}　{name}（{MODE_CN[mode]}，约 {T:.0f} 秒）")
        out.append("")
        for i in sc["lines"]:
            out.append(f"- **{i}**　{by[i]['zh']}")
        if sc["kind"] == "card":
            show = "自己画的说明图"
        else:
            parts = ["、".join(span_text(D, s) for s in sc["top"])]
            if mode == "two":
                parts.append("、".join(span_text(D, s) for s in sc["bottom"]))
            show = ("上窗：" if mode == "two" else "") + parts[0] + ("；下窗：" + parts[1] if len(parts) > 1 else "")
        out += ["", f"> 画面：{show}", ""]
    (EP / "台本" / "实际口播稿_字幕版.md").write_text(chr(10).join(out), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
