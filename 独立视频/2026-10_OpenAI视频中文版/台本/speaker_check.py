# -*- coding: utf-8 -*-
"""用声学特征给每个小句分“她 / dot”两类（MFCC + 音高 + 左右声道），再和我按内容判断的锚点对照。

  python speaker_check.py

只用来辅助判断字幕里谁在说话，不进成片。
"""
import json
from pathlib import Path

import librosa
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
AUDIO = HERE.parent / "素材" / "fHEIw5CcN5U_audio_en.webm"
SR = 16000

# 我按内容判断的锚点（1 = dot，0 = 她）。只放有把握的。
DOT = "U020 U022 U025 U026 U027 U028 U031 U056 U057 U058 U066 U100 U101 U106 U111 U112 U113 U133".split()
HER = "U001 U002 U003 U004 U005 U006 U007 U014 U015 U018 U019 U021 U024 U029 U030 U032 U033 U053 U055 U062 U063 U065 U068 U070 U071 U073 U075 U094 U095 U097 U098 U099 U109 U110 U130 U131 U132 U148 U149".split()


def main():
    y, _ = librosa.load(str(AUDIO), sr=SR, mono=False)
    if y.ndim == 1:
        y = np.stack([y, y])
    mono = y.mean(0)
    units = json.loads((HERE / "units.json").read_text(encoding="utf-8"))
    rows, keep = [], []
    for u in units:
        a, b = int(u["s"] * SR), int(u["e"] * SR)
        seg = mono[a:b]
        if len(seg) < 0.6 * SR:
            continue
        mf = librosa.feature.mfcc(y=seg, sr=SR, n_mfcc=20)[1:14]
        f0 = librosa.yin(seg, fmin=70, fmax=420, sr=SR, frame_length=1024)
        f0 = f0[(f0 > 75) & (f0 < 410)]
        cen = librosa.feature.spectral_centroid(y=seg, sr=SR)[0]
        L, R = y[0, a:b], y[1, a:b]
        lr = 10 * np.log10((np.mean(L ** 2) + 1e-12) / (np.mean(R ** 2) + 1e-12))
        corr = float(np.corrcoef(L, R)[0, 1]) if np.std(L) > 0 and np.std(R) > 0 else 1.0
        rows.append(np.concatenate([mf.mean(1), mf.std(1), [np.median(f0) if len(f0) else 0, np.std(f0) if len(f0) else 0, cen.mean(), lr, corr]]))
        keep.append(u["id"])
    X = StandardScaler().fit_transform(np.array(rows))
    km = KMeans(n_clusters=2, n_init=30, random_state=0).fit(X)
    lab = dict(zip(keep, km.labels_))
    # 聚类编号没有含义：按和锚点的一致程度决定哪一类是 dot
    agree = sum((lab[i] == 1) for i in DOT if i in lab) + sum((lab[i] == 0) for i in HER if i in lab)
    flip = agree < (len([i for i in DOT if i in lab]) + len([i for i in HER if i in lab])) / 2
    if flip:
        lab = {k: 1 - v for k, v in lab.items()}
    nd = sum(lab[i] == 1 for i in DOT if i in lab)
    nh = sum(lab[i] == 0 for i in HER if i in lab)
    print(f"锚点一致：dot {nd}/{len([i for i in DOT if i in lab])}，她 {nh}/{len([i for i in HER if i in lab])}")
    for name, ids, want in (("dot 锚点里被分错的", DOT, 1), ("她的锚点里被分错的", HER, 0)):
        bad = [i for i in ids if i in lab and lab[i] != want]
        print(name + "：", " ".join(bad) or "无")
    feats = {k: r for k, r in zip(keep, rows)}
    print("\n逐句聚类结果（D = dot，H = 她；锚点用 * 标出）：")
    line = []
    for u in units:
        i = u["id"]
        c = ("D" if lab.get(i) == 1 else "H") if i in lab else "?"
        star = "*" if (i in DOT or i in HER) else " "
        line.append(f"{i[1:]}{c}{star}")
    for k in range(0, len(line), 12):
        print("  " + "  ".join(line[k:k + 12]))
    (HERE / "speaker_clusters.json").write_text(json.dumps({i: ("dot" if lab.get(i) == 1 else "her") for i in lab}, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
