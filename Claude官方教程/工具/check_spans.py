# -*- coding: utf-8 -*-
r"""检查 series_data.py 里每期每个场景的画面选段：
  1. 选段有没有跨过“硬切”镜头（框里画面会突然跳）、或落在转场帧上（超出 safe_in / safe_out）；
  2. 同一段素材有没有被两个选段重复用（同一期里重复出现同一画面）；
  3. 按台本字数估出每个场景要多长，每个框的素材够不够；不够的要定格补多少秒（> 1.0 s 就该换 / 加选段）。

  python check_spans.py          全部
  python check_spans.py 3 5      只查第 3、5 期
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from series_data import EPISODES, VIDEO_DIR  # noqa: E402
from gen_episode import alloc, line_durs, fit_spans, GAP_LINE, PAD_END  # noqa: E402
from series_data import EP_ROOT  # noqa: E402
from plan_spans import resolve_all  # noqa: E402

SEG_DIR = VIDEO_DIR.parent / "分镜"
_cache = {}


def segs_of(fname):
    stem = Path(fname).stem
    if stem not in _cache:
        _cache[stem] = json.loads((SEG_DIR / f"{stem}.json").read_text(encoding="utf-8"))["segments"]
    return _cache[stem]


def check_span(fname, a, b):
    """返回问题列表 [(级别, 说明)]。"""
    issues = []
    segs = segs_of(fname)
    hit = [s for s in segs if s["e"] > a + 1e-6 and s["s"] < b - 1e-6]
    if not hit:
        return [("✗", "不在任何镜头段里")]
    for s in hit[1:]:
        # 进入下一段：why == cut 是硬切；type 是类别变化（溶解 / 动画内变化）
        if s["why"] == "cut":
            issues.append(("△", f"跨过硬切 {s['s']:.2f}（#{s['i']} {s['type']}，画面会跳一下）"))
        elif s["type"] != hit[0]["type"]:
            issues.append(("△", f"跨过类别变化 {s['s']:.2f}（{hit[0]['type']}→{s['type']}，可能是转场 / 动画内变化）"))
    first, last = hit[0], hit[-1]
    if a < first["safe_in"] - 0.02:
        issues.append(("△", f"开头 {a:.2f} 早于 safe_in {first['safe_in']:.2f}（#{first['i']}，可能带转场帧）"))
    if b > last["safe_out"] + 0.02:
        issues.append(("△", f"结尾 {b:.2f} 晚于 safe_out {last['safe_out']:.2f}（#{last['i']}）"))
    return issues


def main():
    want = [int(x) for x in sys.argv[1:] if x.isdigit()] or sorted(EPISODES)
    for n in want:
        d = EPISODES[n]
        print(f"\n══ 第 {n} 期 {d['folder']}")
        used = {}                                   # (src, a, b) → 场景 / 框
        by = {l["id"]: l for l in d["lines"]}
        durs = line_durs(EP_ROOT / d["folder"], d, "--tts" in sys.argv)
        Ts = {sc["id"]: sum(durs[i] for i in sc["lines"]) + GAP_LINE * (len(sc["lines"]) - 1) + PAD_END for sc in d["scenes"]}
        boxes = resolve_all(d, VIDEO_DIR, Ts)
        for sc in d["scenes"]:
            T = Ts[sc["id"]]
            top_b, bot_b = boxes[sc["id"]]
            for box in ("top", "bottom"):
                spans = top_b if box == "top" else bot_b
                spans = fit_spans(spans, T)
                L, rem = alloc(spans, T)
                tag = f"{sc['id']}·{box}"
                msgs = []
                for sp in spans:
                    fname = d["src"][sp["src"]]
                    sb = sp.get("b", sp["a"] + 0.04)                 # 手写选段里的定格（hold）只有 a：当作一帧来查
                    for lvl, m in check_span(fname, sp["a"], sb):
                        msgs.append(f"    {lvl} {sp['src']} {sp['a']:.2f}–{sb:.2f}：{m}")
                    key = (sp["src"], sp["a"], sb)
                    # 重叠检查（定格不占素材，不查）
                    if not sp.get("hold"):
                        for (k2, who) in list(used.items()):
                            if k2[0] == sp["src"] and k2[1] < sb and sp["a"] < k2[2]:
                                msgs.append(f"    ✗ {sp['src']} {sp['a']:.2f}–{sb:.2f} 和 {who} 的 {k2[1]:.2f}–{k2[2]:.2f} 重叠（同一画面用了两次）")
                    used[key] = tag
                flag = "" if rem <= 1.0 else "  ← 素材不够，要定格"
                print(f"  {tag}：需要 {T:.1f} s，素材上限 {sum((s['b'] - s['a']) / s.get('speed', 1.0) for s in spans if not s.get('hold')):.1f} s{' 含放慢' if any('speed' in s for s in spans) else ''}，定格补 {rem:.1f} s{flag}")
                for m in msgs:
                    print(m)


if __name__ == "__main__":
    main()
