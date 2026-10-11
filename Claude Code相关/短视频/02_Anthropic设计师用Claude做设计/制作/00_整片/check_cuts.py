# -*- coding: utf-8 -*-
"""检查每一段的切点（cut_in / cut_out）落在原声的哪里：切点附近 ±40 ms 的最大响度（dB），和 ±0.35 s 内最安静的时刻。

  python check_cuts.py

> −40 dB 说明切在了有声音的地方（可能切掉半个词或带进下一句的开头），表里会标 ⚠ 并给出建议的安静时刻（对齐到 1/24 s）；改 plan.py 的 cut 再跑。
只看原声（说话 + BGM / 界面音效）；Slides 有一层持续的 BGM，底噪本来就在 −35 dB 上下，所以判据是“比这一句话的平均音量低 18 dB 以上”。
"""
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


def q24(t):
    return round(t * 24) / 24


def main():
    envs = {s: env(load(s)) for s in ("design", "slides")}
    bad = 0
    for p in plan.PASSAGES:
        e = envs[p["src"]]
        cin, cout = q24(p["cut"][0]), q24(p["cut"][1])
        seg = e[int(cin * 100): int(cout * 100)]
        ref = float(np.percentile(seg, 80)) if len(seg) else -20.0           # 这一段的“说话音量”
        row = [p["id"], f"说话 {ref:5.1f} dB"]
        for name, t in (("入", cin), ("出", cout)):
            lo, hi = max(0, int((t - 0.04) * 100)), max(1, int((t + 0.04) * 100))
            lvl = float(e[lo:hi].max())
            w0, w1 = max(0, int((t - 0.35) * 100)), max(1, int((t + 0.35) * 100))
            k = int(np.argmin(e[w0:w1])) + w0
            best = q24(k / 100)
            flag = lvl > ref - 18
            bad += flag
            row.append(f"{name} {t:7.3f} s：{lvl:6.1f} dB{' ⚠ 建议 ' + format(best, '.3f') + f'（{e[k]:.1f} dB）' if flag else ''}")
        print("  ".join(row))
    print(f"有声音的切点：{bad} 个")


if __name__ == "__main__":
    main()
