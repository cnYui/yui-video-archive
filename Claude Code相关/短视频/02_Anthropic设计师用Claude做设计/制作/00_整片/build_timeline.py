# -*- coding: utf-8 -*-
"""时间线：台本 plan.py + 同传真实时长（02_配音/edit/voice_lines.json）→ build/timeline.json。

  python build_timeline.py

每段 = 原片的一个连续片段 [cut_in, cut_out]（对齐到 1/24 s），画面 + 原声同步；同传每句在英文开口后 TTS_LAG 秒开口（前一句没说完就顺延，句间至少空 TTS_GAP）。
段长 P = max(原片片段长 L, 最后一句同传说完 + TTS_TAIL)；同传比原片长时，画面定格最后一帧等同传说完（原声此时无声；不加速配音）。
帧：全片按 30 fps 的整帧累加（段起点 = 前面各段帧数之和 / 30），音频放置时刻和字幕都用同一个时间轴。
子镜头：上 / 下框各一串，`at` = 距段首的秒数，下一个的 at（或 until）就是上一个的结束；O 的原片时间 = cut_in + at（或 src_t），原片不够长就定格。
字幕：每句同传的每一条 = 同传开口时刻（第 2、3… 条用 voice_lines.json 的 cue_at），显示窗口按项目标准（开始前 0.1 s、结束后 0.45 s、不叠）并裁在本段内。
"""
import json
import math
import sys

import config as C

sys.path.insert(0, str(C.EP / "台本"))
sys.path.insert(0, str(C.WAY_SCRIPTS))
import plan  # noqa: E402
from bilingual_std import display_windows  # noqa: E402

TL = C.BUILD / "timeline.json"


def q24(t):
    return round(t * C.SRC_FPS) / C.SRC_FPS


def resolve_panel(subs, p, cin, cout, P):
    """把一串子镜头摆到 [0, P)：返回带帧数 / 原片时间 / 速度的字典列表。"""
    nf = round(P * C.FPS)
    out = []
    assert subs and abs(subs[0].get("at", 0.0)) < 1e-9, f"{p['id']}：第一个子镜头 at 必须是 0"
    for i, s in enumerate(subs):
        a_f = round(s.get("at", 0.0) * C.FPS)
        if "until" in s:
            e_f = round(s["until"] * C.FPS)
        elif i + 1 < len(subs):
            e_f = round(subs[i + 1].get("at", 0.0) * C.FPS)
        else:
            e_f = nf
        e_f = min(e_f, nf)
        n = e_f - a_f
        if n <= 0:
            continue
        r = {"kind": s["kind"], "c": s["c"], "nf": n, "at_f": a_f, "hold": False}
        if s["kind"] == "orig":
            r["src"] = p["src"]
            speed = float(s.get("speed", 1.0))
            t0 = s["src_t"] if "src_t" in s else cin + s.get("at", 0.0)
            r["speed"], r["t"] = speed, round(q24(t0), 4)
            avail = (cout - r["t"]) if "src_t" not in s else 1e9
            need = n / C.FPS * speed
            r["src_len"] = round(min(need, max(avail, 0.0)), 4)
            r["hold"] = need > avail + 1e-6
        elif s["kind"] == "broll":
            r["src"] = s["src"]
            speed = float(s.get("speed", 1.0))
            r["speed"], r["t"] = speed, round(q24(s["a"]), 4)
            avail = s["b"] - s["a"]
            need = n / C.FPS * speed
            r["src_len"] = round(min(need, avail), 4)
            r["hold"] = need > avail + 1e-6
        else:                                                    # freeze
            r["src"], r["t"], r["speed"], r["src_len"] = s["src"], round(s["t"], 4), 1.0, 0.0
        out.append(r)
    return out


def main():
    voice = {l["id"]: l for l in json.loads((C.EP / "制作" / "02_配音" / "edit" / "voice_lines.json").read_text(encoding="utf-8"))["lines"]}
    passages, chips, warn = [], [], []
    f_cursor = 0
    for p in plan.PASSAGES:
        cin, cout = q24(p["cut"][0]), q24(p["cut"][1])
        L = cout - cin
        tts, prev_end = [], -1e9
        for k, s in enumerate(p["sentences"]):
            bid = f"{p['id']}{chr(ord('a') + k)}"
            v = voice[bid]
            onset = s["tts_at"] if s.get("own") else (s["t0"] - cin) + C.TTS_LAG
            onset = max(onset, prev_end + C.TTS_GAP, 0.0)
            tts.append({"id": bid, "onset": round(onset, 3), "dur": v["dur"], "end": round(onset + v["dur"], 3), "cue_at": v["cue_at"], "zh": s["zh"], "en": s["en"]})
            prev_end = onset + v["dur"]
        P = max(L + p.get("extra", 0.0), prev_end + C.TTS_TAIL)          # extra = 段尾多放的秒数（比如 S06 把原片后面一段安静的操作加速放完）
        nf = math.ceil(P * C.FPS - 1e-9)
        P_eff = nf / C.FPS
        T0 = f_cursor / C.FPS
        tracks = {"top": resolve_panel(p["top"], p, cin, cout, P_eff), "bottom": resolve_panel(p["bottom"], p, cin, cout, P_eff)}
        for name, tr in tracks.items():
            assert sum(x["nf"] for x in tr) == nf, f"{p['id']} {name} 子镜头帧数 {sum(x['nf'] for x in tr)} ≠ {nf}"
        # 字幕（相对段首）
        raw = []
        for t in tts:
            starts = [t["onset"]] + [t["onset"] + c for c in t["cue_at"]]
            ends = starts[1:] + [t["end"]]
            for z, e, a, b in zip(t["zh"], t["en"], starts, ends):
                raw.append((a, b, z, e))
        wins = display_windows([(a, b) for a, b, _, _ in raw])
        cues = []
        for (a, b, z, e), (wa, wb) in zip(raw, wins):
            wa, wb = max(0.0, wa), min(P_eff, wb)
            if wb - wa > 0.15:
                cues.append({"a": round(T0 + wa, 3), "b": round(T0 + wb, 3), "zh": z, "en": e, "id": p["id"]})
        audio_to = q24(p["audio_to"]) if "audio_to" in p else cout
        passages.append({"id": p["id"], "chip": list(p["chip"]), "src": p["src"], "f0": f_cursor, "nf": nf, "t0": round(T0, 4), "dur": round(P_eff, 4),
                         "cin": cin, "cout": cout, "L": round(L, 3), "hold": round(P_eff - L, 3),
                         "audio": {"src": p["src"], "cin": cin, "len": round(min(audio_to - cin, P_eff), 4)},
                         "tts": [{"id": t["id"], "start": round(T0 + t["onset"], 3), "dur": t["dur"]} for t in tts], "tracks": tracks, "cues": cues})
        if tuple(p["chip"]) not in [tuple(c) for c in chips]:
            chips.append(list(p["chip"]))
        if P_eff - L > 1.2:
            warn.append(f"{p['id']}：同传比原片段长 {P_eff - L:.2f} s（定格）")
        f_cursor += nf
        print(f"{p['id']}  {p['chip'][0][-6:]} {p['chip'][1] or '--':6s}  原片 {cin:7.3f}–{cout:7.3f}（{L:5.2f} s）  同传 {', '.join(f'{t['onset']:.2f}–{t['end']:.2f}' for t in tts)}  段长 {P_eff:5.2f} s  定格 {max(0.0, P_eff - L):4.2f} s  起点 {T0:6.2f}")
    total = f_cursor / C.FPS
    C.BUILD.mkdir(exist_ok=True)
    TL.write_text(json.dumps({"fps": C.FPS, "frames": f_cursor, "total": round(total, 4), "chips": chips, "passages": passages}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"总长 {total:.2f} s（{f_cursor} 帧 @ {C.FPS} fps）；{len(passages)} 段；字幕 {sum(len(x['cues']) for x in passages)} 条；同传 {sum(t['dur'] for x in passages for t in x['tts']):.1f} s")
    print("提醒：" + ("；".join(warn) if warn else "无"))


if __name__ == "__main__":
    main()
