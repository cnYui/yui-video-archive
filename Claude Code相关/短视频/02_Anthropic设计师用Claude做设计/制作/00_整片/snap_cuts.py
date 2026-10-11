# -*- coding: utf-8 -*-
"""给每一段的切点（cut_in / cut_out）找最合适的安静时刻：用逐词识别的字时间划出“不能切进字里”的范围，在范围内按 1/24 s 找 ±30 ms 内最大响度最低的点（离原来的值越近越好）。

  python snap_cuts.py

输出每段入 / 出点的：原值、建议值、建议值处的响度、允许范围（上一个字 / 下一个字之间）。不改 plan.py，由人看着改（有的切点前后紧挨着界面音效，范围里没有安静点，要手工取舍）。
"""
import json
import subprocess
import sys

import numpy as np

import config as C

sys.path.insert(0, str(C.EP / "台本"))
import plan  # noqa: E402

SR = 16000


def load(src):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(C.AUD[src]), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def env(a, hop=0.01):
    h = int(SR * hop)
    n = len(a) // h
    return 20 * np.log10(np.sqrt((a[: n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)


def words(src):
    f = C.EP / "制作" / "02_转写" / ("asr_design_words.json" if src == "design" else "asr_slides_words.json")
    d = json.loads(f.read_text(encoding="utf-8"))
    ws = []
    for s in d["segments"]:
        for w in s["words"]:
            ws.append((w.get("s", w.get("start")), w.get("e", w.get("end")), w.get("w", w.get("word"))))
    return sorted(ws)


def q24(t):
    return round(t * 24) / 24


def best(e, lo, hi, nominal):
    cands = [q24(lo + i / 24) for i in range(int(max(0, (hi - lo)) * 24) + 1)] or [q24((lo + hi) / 2)]
    cands = [t for t in cands if lo - 1e-6 <= t <= hi + 1e-6] or [q24((lo + hi) / 2)]
    sc = []
    for t in cands:
        a, b = max(0, int((t - 0.03) * 100)), max(1, int((t + 0.03) * 100))
        sc.append((float(e[a:b].max()) + 8 * abs(t - nominal), t))
    s, t = min(sc)
    a, b = max(0, int((t - 0.03) * 100)), max(1, int((t + 0.03) * 100))
    return t, float(e[a:b].max())


def main():
    envs = {s: env(load(s)) for s in ("design", "slides")}
    W = {s: words(s) for s in ("design", "slides")}
    for p in plan.PASSAGES:
        src = p["src"]
        ws = W[src]
        e = envs[src]
        cin, cout = q24(p["cut"][0]), q24(p["cut"][1])
        t0 = p["sentences"][0]["t0"]
        row = [p["id"]]
        if p["sentences"][0].get("own"):
            print(p["id"], "（我们自己的句子，原声里没有话；切点只看 BGM / 音效，略）")
            continue
        inside = [w for w in ws if w[0] >= t0 - 0.12 and w[0] < cout - 0.05]
        if not inside:
            print(p["id"], "没找到字")
            continue
        fw, lw = inside[0], inside[-1]
        prev = [w for w in ws if w[1] <= fw[0] - 0.005 and w is not fw]
        nxt = [w for w in ws if w[0] >= lw[1] - 0.005 and w is not lw and w[0] > lw[0]]
        pw, nw = (prev[-1] if prev else None), (nxt[0] if nxt else None)
        lo_in = (pw[1] + 0.05) if pw else cin - 0.4
        hi_in = fw[0] - 0.07
        lo_out = lw[1] + 0.06
        hi_out = (nw[0] - 0.07) if nw else cout + 0.4
        ti, li = best(e, max(lo_in, cin - 0.6), min(hi_in, cin + 0.6), cin)
        to, lo_ = best(e, max(lo_out, cout - 0.6), min(hi_out, cout + 0.6), cout)
        row.append(f"入 {cin:7.3f} → {ti:7.3f}（{li:6.1f} dB；字 {fw[2]!r}@{fw[0]:.2f}，上一个字止 {pw[1] if pw else float('nan'):.2f}）")
        row.append(f"出 {cout:7.3f} → {to:7.3f}（{lo_:6.1f} dB；字 {lw[2]!r} 止 {lw[1]:.2f}，下一个字起 {nw[0] if nw else float('nan'):.2f}）")
        print("  ".join(row))


if __name__ == "__main__":
    main()
