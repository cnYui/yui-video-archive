# -*- coding: utf-8 -*-
r"""从 series_data.py 生成 / 刷新某一期的 台本\录制稿.json、台本\plan.json、制作\00_整片\common.py（素材表）和 scenes.js 的本期叠加层。

  python gen_episode.py N            配音还没出：按字数估每句的时长（0.225 s / 汉字 + 句间 0.18 s）
  python gen_episode.py N --tts      配音已导入：用 制作\02_配音\edit\tts_edit.json 里每句的真实时长
  python gen_episode.py all [--tts]

每个场景写两路“选段”（top = 上框、bottom = 下框），每个选段 = 素材里的一段 [a, b]（b 是上限，取自分镜表的 safe_in / safe_out）；
按这个场景的念白长度 T 自动分配每段放多久（和各段可用长度成比例、不超过上限），不够 T 就把最后一帧定格补齐。所以配音一出来重跑 --tts，画面就跟着对上。
选段字段：src（series_data 里 src 的键）、a、b、crop（占整帧的比例，x1−x0 = y1−y0 时仍是 16:9）、speed（只给静音段）、hold（True = 定格 a 这一帧）、bg、w（权重）。
"""
import json
import re
import sys
from math import inf
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from series_data import EPISODES, EP_ROOT, VIDEO_DIR  # noqa: E402
from plan_spans import resolve_all  # noqa: E402

GAP_LINE, PAD_END, EST_HAN, EST_GAP = 0.18, 0.4, 0.225, 0.12   # 和 build_timeline.py 里的一致


def han_count(s):
    return sum(1 for ch in s if "一" <= ch <= "鿿")


EST_WORD = 0.32          # 每个英文词 / 数字串约 0.32 s（配音还没出时的估值，--tts 之后用真实时长）


def est_dur(say):
    """没有配音时估一句的有声时长：汉字 0.225 s + 英文词 0.32 s。"""
    h = han_count(say)
    w = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9.+_/@-]*", say))
    return h * EST_HAN + w * EST_WORD if (h or w) else len(say) / 5.0


def line_durs(ep, d, use_tts):
    """每句的有声时长（秒）。use_tts：全部用真实配音；否则有 tts_edit.json 的句子用真实时长、其余按字数估（实测估值偏长 8%，乘 0.92）。"""
    js = ep / "制作" / "02_配音" / "edit" / "tts_edit.json"
    by = {}
    if js.exists():
        td = json.loads(js.read_text(encoding="utf-8"))
        by = {x["id"]: x["e"] - x["s"] for x in td["lines"]}
    if use_tts:
        return {l["id"]: by[l["id"]] for l in d["lines"]}
    return {l["id"]: (by[l["id"]] if l["id"] in by else est_dur(l["say"]) * 0.92) for l in d["lines"]}


def alloc(spans, T):
    """把总长 T 分给各选段：长度和各段可用长度成比例、不超过上限；全部到顶还不够就定格最后一帧补齐。返回每段放多久（成片秒）。"""
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
    """素材不够长时，把非人脸、没写 speed 的选段放慢（最慢 0.8×，终端 / 页面 / 图示放慢看不出来）；返回新的选段列表。"""
    cap = sum(inf if s.get("hold") else (s["b"] - s["a"]) / s.get("speed", 1.0) for s in spans)
    if cap >= T - 0.05:
        return spans
    slow = [s for s in spans if not s.get("face") and not s.get("hold") and "speed" not in s]
    S = sum(s["b"] - s["a"] for s in slow)
    if not slow or S <= 0:
        return spans
    f = min(1.25, (S + (T - cap)) / S)                # 时间拉长倍数 = 1 / speed
    out = []
    for s in spans:
        if s in slow:
            s = dict(s, speed=round(1 / f, 3))
        out.append(s)
    return out


def to_ranges(spans, T):
    """选段 → plan.json 的 ranges（静音；不够的补一段定格）。"""
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
        if s.get("crop"):
            r["crop"] = s["crop"]
        if s.get("bg"):
            r["bg"] = s["bg"]
        out.append(r)
    if rem > 0.04 and out:                                       # 所有段都到顶了还差 rem 秒：定格最后一段的最后一帧
        last = spans[-1]
        t_last = last["a"] if last.get("hold") else last["b"] - 0.05
        r = {"src": last["src"], "in": round(t_last, 3), "hold": round(rem, 3)}
        if last.get("crop"):
            r["crop"] = last["crop"]
        if last.get("bg"):
            r["bg"] = last["bg"]
        out.append(r)
    return out


def gen(n, use_tts):
    d = EPISODES[n]
    ep = EP_ROOT / d["folder"]
    assert ep.is_dir(), f"{ep} 不存在：先 new_short.py 建这一期"
    durs = line_durs(ep, d, use_tts)
    # 录制稿
    sc = {"slug": d["slug"], "title": d["title"], "kicker": d["kicker"], "hook": d["hook"],
          "lines": [{k: v for k, v in l.items() if v not in (None, "")} for l in d["lines"]]}
    (ep / "台本" / "录制稿.json").write_text(json.dumps(sc, ensure_ascii=False, indent=1), encoding="utf-8")
    # plan
    plan, seen = [], []
    Ts = {s["id"]: sum(durs[i] for i in s["lines"]) + GAP_LINE * (len(s["lines"]) - 1) + PAD_END for s in d["scenes"]}
    boxes = resolve_all(d, VIDEO_DIR, Ts)
    for s in d["scenes"]:
        ids = s["lines"]
        T = Ts[s["id"]]
        top, bottom = boxes[s["id"]]
        item = {"id": s["id"], "type": "clip", "kind": "demo", "overlay": "clip", "name": s.get("name", s["id"]), "credit": s.get("credit", d.get("credit", "")),
                "ranges": to_ranges(top, T), "ranges2": to_ranges(bottom, T),
                "lines": [{"id": i, "a": 0.0} for i in ids]}
        plan.append(item)
        seen += ids
    assert seen == [l["id"] for l in d["lines"]], f"场景里的句子顺序和台本不一致：{seen}"
    (ep / "台本" / "plan.json").write_text(json.dumps({"layout": "dual", "plan": plan}, ensure_ascii=False, indent=1), encoding="utf-8")
    # 素材表
    keys = sorted(d["src"])
    rows = "\n".join(f'    "{k}": XV / "视频" / "{d["src"][k]}",' for k in keys)
    has = "\n".join(f'    "{k}": False,' for k in keys)
    cp = ep / "制作" / "00_整片" / "common.py"
    txt = cp.read_text(encoding="utf-8")
    txt = re.sub(r'XV = MAT / "[^"]*"[^\n]*', 'XV = MAT / "2026-10_ClaudeAcademy"           # Claude Academy 官方视频（合集层 素材\\ 下；README 有来源和挂名）', txt, count=1)
    txt = re.sub(r"SRC = \{.*?\n\}", "SRC = {\n" + rows + "\n}", txt, count=1, flags=re.S)
    txt = re.sub(r"HAS_AUDIO = \{.*?\n\}", "HAS_AUDIO = {\n" + has + "\n}", txt, count=1, flags=re.S)
    cp.write_text(txt, encoding="utf-8")
    # 叠加层
    sp = ep / "制作" / "00_整片" / "scenes.js"
    js = sp.read_text(encoding="utf-8")
    marker = "// ═════════════════════════════ 本条的叠加层（写在这里；时间都按字幕条算）"
    i = js.index(marker)
    head = js[:i] + marker + "\n"
    sp.write_text(head + (d.get("overlays") or "") + "\n", encoding="utf-8")
    tot = sum(sum(durs[i] for i in s["lines"]) + GAP_LINE * (len(s["lines"]) - 1) + PAD_END for s in d["scenes"])
    print(f"第 {n} 期 {d['folder']}：{len(d['lines'])} 句、{len(plan)} 个场景，念白约 {sum(durs.values()):.1f} s，场景合计约 {tot:.1f} s（{'真实配音' if use_tts else '按字数估'}）")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tts = "--tts" in sys.argv
    for a in (sorted(EPISODES) if args and args[0] == "all" else [int(x) for x in args]):
        gen(a, tts)
