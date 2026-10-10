# -*- coding: utf-8 -*-
"""时间线：台本（录制稿.json）+ 配音时长（02_配音/edit/voice_lines.json）+ 镜头表（shots.json）→ build/timeline.json。

  python build_timeline.py

每句话占一段 [T, T+D)：画面在 T 切（句首先切 LEAD 再开口，第一句晚 LEAD_FIRST 开口），配音在 onset = T + lead 开口、念 dur 秒，
句间空 GAP + LEAD = 0.12 s；最后一句念完再停 HOLD_END（技能规定金句说完 0.8 s 结束，不加片头片尾）。
段与段的边界取整到 30 fps 的帧；一句里的子镜头按 shots.json 的 end（cueN / narr / 秒数）切，没写 end 的相邻子镜头平分剩余时间。
字幕：每条 = (中文, 英文)，开口时间 = onset + cue_at（voice_lines.json 里按配音的能量低点量过）。
检查：人脸子镜头速度应在 0.9–1.1×、操作画面 0.85–4×；总长要在 20–30 s；打印每个子镜头的速度。
"""
import json
import sys

import config as C

BUILD = C.HERE / "build"


def fr(t):
    return round(t * C.FPS)


def main():
    sc = json.loads((C.EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))
    vl = json.loads((C.EP / "制作" / "02_配音" / "edit" / "voice_lines.json").read_text(encoding="utf-8"))
    shots = json.loads((C.HERE / "shots.json").read_text(encoding="utf-8"))
    lines = sc["lines"]
    assert len(lines) == len(vl["lines"]), "台本句数和配音句数对不上"
    warn = []
    # 1 每句的起止
    T, rows = 0.0, []
    for i, (l, v) in enumerate(zip(lines, vl["lines"])):
        assert l["id"] == v["id"], (l["id"], v["id"])
        lead = C.LEAD_FIRST if i == 0 else C.LEAD
        tail = C.HOLD_END if i == len(lines) - 1 else C.GAP
        D = lead + v["dur"] + tail
        rows.append({"id": l["id"], "T": T, "D": D, "onset": T + lead, "dur": v["dur"], "cue_at": v["cue_at"], "cues": l["cues"], "say": l["say"]})
        T += D
    total = T
    bounds = [fr(r["T"]) for r in rows] + [fr(total)]
    for i, r in enumerate(rows):
        r["f0"], r["f1"] = bounds[i], bounds[i + 1]
        r["nf"] = r["f1"] - r["f0"]
    # 2 子镜头
    for r in rows:
        spec = shots[r["id"]]
        r["tracks"] = {}
        for track in ("top", "bottom"):
            subs = spec[track]
            ends = []
            for s in subs:
                e = s.get("end")
                if e is None:
                    ends.append(None)
                elif e == "narr":
                    ends.append(r["onset"] - r["T"] + r["dur"])
                elif isinstance(e, str) and e.startswith("cue"):
                    ends.append(r["onset"] - r["T"] + r["cue_at"][int(e[3:]) - 1])
                else:
                    ends.append(float(e))
            ends[-1] = r["D"]                                   # 最后一个子镜头到句末
            # 没写 end 的相邻子镜头平分剩余时间
            t0, k = 0.0, 0
            bt = []
            while k < len(subs):
                if ends[k] is not None:
                    bt.append((t0, ends[k]))
                    t0 = ends[k]
                    k += 1
                else:
                    j = k
                    while ends[j] is None:
                        j += 1
                    seg_end = ends[j]
                    n = j - k + 1
                    step = (seg_end - t0) / n
                    for q in range(n):
                        bt.append((t0 + step * q, t0 + step * (q + 1)))
                    t0 = seg_end
                    k = j + 1
            fb = [0] + [round(b * C.FPS) for _, b in bt]
            fb[-1] = r["nf"]
            out = []
            for k, (s, a, b) in enumerate(zip(subs, fb, fb[1:])):
                nfr = b - a
                src_len = s["src"][1] - s["src"][0]
                dur = nfr / C.FPS
                hold = bool(s.get("hold"))
                speed = 1.0 if (hold and src_len < dur) else src_len / dur
                lim = (0.9, 1.1) if track == "top" else (0.85, 4.0)       # 操作画面慢到 0.85× 看不出来，人脸不能（嘴型）
                flag = ""
                if not hold and not (lim[0] <= speed <= lim[1]):
                    flag = "  ⚠ 速度超出 %.2f–%.1f×" % lim
                    warn.append(f"{r['id']} {track}{k}: 速度 {speed:.2f}×")
                out.append({"src": s["src"], "crop": s["crop"], "nframes": nfr, "speed": round(speed, 4), "hold": hold, "note": s.get("note", "")})
                print(f"{r['id']} {track:6s}{k}  src {s['src'][0]:6.2f}–{s['src'][1]:6.2f}  → {dur:4.2f} s（{nfr:3d} 帧）  速度 {speed:4.2f}×{'  定格' if hold else ''}{flag}")
            r["tracks"][track] = out
    # 3 字幕、配音
    subs = []
    for r in rows:
        starts = [r["onset"]] + [r["onset"] + t for t in r["cue_at"]]
        ends = starts[1:] + [r["onset"] + r["dur"]]
        for c, a, b in zip(r["cues"], starts, ends):
            subs.append({"id": r["id"], "a": round(a, 3), "b": round(b, 3), "zh": c["zh"], "en": c["en"]})
    out = {"fps": C.FPS, "total": round(total, 3), "frames": bounds[-1], "lines": rows, "subs": subs}
    BUILD.mkdir(exist_ok=True)
    (BUILD / "timeline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"总长 {total:.2f} s（{bounds[-1]} 帧 @ {C.FPS} fps）；字幕 {len(subs)} 条；配音 {sum(r['dur'] for r in rows):.2f} s")
    if not (20 <= total <= 30):
        warn.append(f"总长 {total:.2f} s 不在 20–30 s")
    print("警告：" + ("；".join(warn) if warn else "无"))
    return 1 if warn else 0


if __name__ == "__main__":
    sys.exit(main())
