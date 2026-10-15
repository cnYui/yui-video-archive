# -*- coding: utf-8 -*-
r"""从 spec.py 生成 录制稿.json 和 plan.json（本条的唯一来源是 spec.py，别手改那两个 json）。

  python gen.py

spec.py 里每个场景：
  up   上框 = 原片镜头（Wang 特写 / 远景），  mute=False 的段带原声（压低留着，曼波同传盖在上面）
  low  下框 = 静音镜头（远景 B-roll）；页面录屏（pageShot {lower:true}）盖在下框上，写在 制作/00_整片/scenes.js
  lines：同传句写 t = 英文开口的原片时刻，a = t − 该段起点 + 0.4（同传比英文晚 0.4 s 开口）；解说句（画面静音）写 a。
"""
import json
from pathlib import Path

import spec

HERE = Path(__file__).resolve().parent
LEAD = 0.4                     # 同传比英文晚开口的秒数（技能 script.md：约 0.4 s）


def rng(r):
    d = {"src": r.get("src", "w"), "in": round(r["in"], 3), "out": round(r["out"], 3)}
    for k in ("mute", "crop", "speed", "gain_db"):
        if r.get(k) not in (None, False):
            d[k] = r[k]
    if r.get("hold"):
        d = {"src": d["src"], "in": round(r["in"], 3), "hold": r["hold"]}
        if r.get("crop"):
            d["crop"] = r["crop"]
    return d


def main():
    lines, plan = [], []
    for sc in spec.SCENES:
        ups = [rng(r) for r in sc["up"]]
        item = {"id": sc["id"], "type": "clip", "kind": "demo", "overlay": "clip", "name": sc["name"], "credit": sc.get("credit", spec.CREDIT),
                "ranges": ups}
        if sc.get("low"):
            item["ranges2"] = [dict(rng(r), mute=True) for r in sc["low"]]
        ls = []
        for ln in sc["lines"]:
            d = {"id": ln["id"], "zh": ln["zh"], "say": ln.get("say", ln["zh"]), "en": ln["en"]}
            if ln.get("who"):
                d["who"] = ln["who"]
            if ln.get("cut"):
                d["cut"] = ln["cut"]
            lines.append(d)
            if "t" in ln:        # 同传：按原片时刻算开口点（只支持这一场景的第一段起点之后的连续素材：多段 up 时 t 要落在第 k 段里，写 seg = k）
                k = ln.get("seg", 0)
                off = sum((r["out"] - r["in"]) / r.get("speed", 1.0) for r in sc["up"][:k])
                a = off + ln["t"] - sc["up"][k]["in"] + LEAD
            else:
                a = ln.get("a", 0.0)
            ls.append({"id": ln["id"], "a": round(max(0.0, a), 2)})
        item["lines"] = ls
        if not sc["up"][-1].get("mute") and sc.get("freeze_tail", True):
            item["freeze_tail"] = True                       # 带原声的场景：话比画面长时把最后一帧定格，不接着放原片
        for k in ("lead", "gap", "spill"):
            if k in sc:
                item[k] = sc[k]
        plan.append(item)
    script = {"slug": spec.SLUG, "title": spec.TITLE, "kicker": spec.KICKER, "hook": spec.HOOK, "lines": lines}
    (HERE / "录制稿.json").write_text(json.dumps(script, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "plan.json").write_text(json.dumps({"_说明": spec.NOTE, "layout": "dual", "plan": plan}, ensure_ascii=False, indent=1), encoding="utf-8")
    han = sum(1 for l in lines for ch in l["say"] if "一" <= ch <= "鿿")
    print(f"{len(plan)} 个场景、{len(lines)} 句、{han} 个汉字 → 录制稿.json / plan.json")


if __name__ == "__main__":
    main()
