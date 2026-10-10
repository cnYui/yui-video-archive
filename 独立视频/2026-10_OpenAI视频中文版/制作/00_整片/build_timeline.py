# -*- coding: utf-8 -*-
"""时间轴：把中文配音按原话的时间放进片子里 → timeline.json（给混音、字幕、复核用）。

  python build_timeline.py

同传做法（照白宫那条）：每句中文比原话这一句的开头晚 LAG 秒起；一句接一句，前一句没念完就顺延 GAP 秒再起；
一句念不完到下一句的起点，就把这一句配音小幅加速（≤ MAX_SPEED，不变调）；还不够就让它顺延（后面的句子会晚一点，打印出落后多少）。
输入：../../台本/录制稿_v1.json（lines：id / src / who / en / zh / say）、../02_配音/edit/tts_edit.json（每句：s/e 有声音的起止，n0/n1 切点）。
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
VIDEO = EP / "素材" / "fHEIw5CcN5U_1080p_video-only.mp4"
LAG, GAP, MAX_SPEED = 0.20, 0.10, 1.18
TAIL = 0.8                                   # 最后一句念完后多留的时间


def video_duration():
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(VIDEO)], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def main():
    lines = json.loads((EP / "台本" / "录制稿_v1.json").read_text(encoding="utf-8"))["lines"]
    td = json.loads((HERE.parent / "02_配音" / "edit" / "tts_edit.json").read_text(encoding="utf-8"))
    nar = {x["id"]: (x["s"], x["e"], x["n0"], x["n1"]) for x in td["lines"]}
    missing = [l["id"] for l in lines if l["id"] not in nar]
    assert not missing, f"配音里缺这些句子：{missing}"
    vdur = video_duration()
    cues, blocks, prev_end = [], [], -1.0
    for i, l in enumerate(lines):
        sv, ev, n0, n1 = nar[l["id"]]
        v0, vdur_line = sv - n0, ev - sv
        start = max(l["src"][0] + LAG, prev_end + GAP)
        nxt = (lines[i + 1]["src"][0] + LAG) if i + 1 < len(lines) else vdur
        window = nxt - GAP - start
        speed = 1.0
        if vdur_line > window:
            speed = min(MAX_SPEED, vdur_line / max(window, 0.8))
        d = vdur_line / speed
        end = start + d
        blocks.append([round(n0, 4), round(n1, 4), round(start - v0 / speed, 4), round(speed, 4)])
        cues.append({"id": l["id"], "s": round(start, 3), "e": round(end, 3), "src": l["src"], "who": l["who"], "zh": l["zh"], "en": l["en"], "say": l["say"],
                     "lag": round(start - l["src"][0], 2), "speed": round(speed, 3)})
        prev_end = end
    total = round(max(vdur, prev_end + TAIL), 3)
    tl = {"video": VIDEO.name, "video_dur": round(vdur, 3), "total": total, "extend": round(total - vdur, 3), "cues": cues, "tts": {"blocks": blocks, "total": td["total"]}}
    (HERE / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    lags = [c["lag"] for c in cues]
    fast = [c for c in cues if c["speed"] > 1.0]
    print(f"成片 {total:.2f} s（原片 {vdur:.2f} s，{'延长 %.2f s（定格最后一帧）' % tl['extend'] if tl['extend'] > 0 else '不延长'}）；{len(cues)} 句；"
          f"落后原话：平均 {sum(lags) / len(lags):.2f} s，最大 {max(lags):.2f} s；加速的 {len(fast)} 句")
    for c in sorted(cues, key=lambda c: -c["lag"])[:6]:
        print(f"  落后最多：{c['id']} 原话 {c['src'][0]:.2f} → 中文 {c['s']:.2f}（晚 {c['lag']:.2f} s，加速 {c['speed']}）{c['zh'][:24]}")
    for c in fast[:12]:
        print(f"  加速：{c['id']} ×{c['speed']} {c['zh'][:24]}")


if __name__ == "__main__":
    main()
