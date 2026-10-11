# -*- coding: utf-8 -*-
"""v2 时间轴：开场 = 真人出镜（DJI 0163，../02_出镜/edit/cam_edit.json）；演示 = 克隆声音配音（../02_出镜/edit/tts_edit.json）。

  python build_timeline.py      → timeline.json / timeline.js

- 开场按用户实际说的分 5 段（都是版式 A）：开场白 / 中转、代充 / 两种方法 / 推荐 UP 主 / 接下来演示苹果（这里放用户自己的订阅截图）。
- 演示①（R01–R22）：录屏原片按新配音逐句伸缩——每条字幕的开头对开头（旧时间 = ../02_出镜/edit/pc_edit.json 里剪好的录屏口播），
  中间线性插值（pc.map）；邮件那段的打码静帧也挂在字幕条上，跟着走。
- 演示②③（M01–M09）：手机录屏按画外音里说到的词“钉”时间（phone.keys），同一时刻两个钉 = 跳剪。
- 配音块之间多留的停顿（换章节处）：BLOCK_GAP。
- v1 的录制稿（台本/录制稿_v1.json）现在只用来出给用户看的 .md；用户录的出镜和稿子不一样，以实际说的为准。
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUT = HERE.parent / "02_出镜" / "edit"
FPS = 30
LEAD, TAIL = 0.4, 1.6
A_HOLD = 1.6        # 开场最后一句（“因为我本身也是这样做的”）说完，订阅截图多留一会儿再切演示
BLOCK_GAP = {"M01": 0.7, "M04": 0.5, "W01": 0.4}     # 配音里这一句前面多留的停顿（换章节）

TITLE = "国内订阅Codex/Claude教程！（非中转非代充）"   # 用户 2026-10-01 改的（原《26年10月两种方式订阅安全正版Codex/Claude教程！》）
CHAPTERS = ["为什么不用中转、代充", "两种方式：苹果 / 安卓", "演示①：买美区礼品卡", "演示②：兑换到账户", "演示③：App 里订阅", "提醒"]
# 开场分段：(段号, 标题, 章节, 第一条字幕)
A_SEGS = [("SA1", "开场", 0, "C01"), ("SA2", "为什么不用中转、代充", 0, "C05"), ("SA3", "两种方法", 1, "C16"),
          ("SA4", "推荐 UP 主（安卓）", 1, "C22"), ("SA5", "接下来演示苹果", 1, "C26")]


def main():
    cam = json.loads((CUT / "cam_edit.json").read_text(encoding="utf-8"))
    tts = json.loads((CUT / "tts_edit.json").read_text(encoding="utf-8"))
    pc = json.loads((CUT / "pc_edit.json").read_text(encoding="utf-8"))
    cues, segs = [], []
    # ── 开场（出镜）
    t_cam = LEAD
    for q in cam["cues"]:
        cues.append({"id": q["id"], "zh": q["zh"], "s": round(t_cam + q["s"], 3), "e": round(t_cam + q["e"], 3), "seg": None, "todo": False})
    a_end = t_cam + cam["total"] + A_HOLD
    CU = {q["id"]: q for q in cues}
    for k, (sid, title, ch, first) in enumerate(A_SEGS):
        s = 0.0 if k == 0 else CU[first]["s"] - 0.25
        segs.append({"id": sid, "title": title, "layout": "A", "chapter": ch, "kind": "cam", "s": round(s, 3)})
    # ── 演示（克隆配音）：按 BLOCK_GAP 拆成几块放
    t_tts = a_end + 0.5
    blocks, cur_off = [], t_tts
    lines = tts["lines"]
    for i, l in enumerate(lines):
        if l["id"] in BLOCK_GAP:
            cut = (lines[i - 1]["e"] + l["s"]) / 2          # 两句之间的停顿中点切开
            blocks.append(cut)
            cur_off += BLOCK_GAP[l["id"]]
        cues.append({"id": l["id"], "zh": l["zh"], "s": round(cur_off + l["s"], 3), "e": round(cur_off + l["e"], 3), "seg": None, "todo": False})
    # 配音块：[配音里的起 b0, 止 b1, 这一块在成片里的开始时刻 at]。成片时间 = o + 配音时间（o = t_tts + 前面累计的 BLOCK_GAP），
    # 所以 at = o + b0。2026-10-01 第一次投稿的版本这里写成了 at = o（漏了 + b0）：后三块（M01–M03、M04–M09、W01–W03）
    # 都被放到了 71–72 s，和演示①的 R 口播叠在一起（1:14–1:36 最多四个声音同时说），演示②③和提醒反而没声音。
    # 字幕、画面用的是 cues（cur_off + 配音时间），本来就是对的，只有混音（mix_audio.py）和电平条（prep_frames.narration_env）用这个。
    bounds = [0.0] + blocks + [tts["total"]]
    offs, o = [], t_tts
    for k in range(len(bounds) - 1):
        if k:
            o += BLOCK_GAP[[l["id"] for l in lines if l["id"] in BLOCK_GAP][k - 1]]
        offs.append([round(bounds[k], 4), round(bounds[k + 1], 4), round(o + bounds[k], 4)])
    CU = {q["id"]: q for q in cues}
    segs.append({"id": "S6", "title": "演示①：买美区礼品卡", "layout": "B", "chapter": 2, "kind": "pc", "s": round(a_end, 3)})
    segs.append({"id": "S7", "title": "演示②：兑换到账户", "layout": "B", "chapter": 3, "kind": "phone1", "s": round(CU["M01"]["s"] - 0.35, 3)})
    segs.append({"id": "S8", "title": "演示③：App 里订阅", "layout": "B", "chapter": 4, "kind": "phone2", "s": round(CU["M04"]["s"] - 0.3, 3)})
    segs.append({"id": "S9", "title": "提醒", "layout": "B", "chapter": 5, "kind": "note", "s": round(CU["W01"]["s"] - 0.35, 3)})
    total = round(CU[lines[-1]["id"]]["e"] + TAIL, 3)
    for a, b in zip(segs, segs[1:]):
        a["e"] = b["s"]
    segs[-1]["e"] = total
    for q in cues:
        q["seg"] = next(s["id"] for s in segs if s["s"] <= q["s"] < s["e"])
    frames = int(round(total * FPS))

    # ── 演示①的录屏伸缩：新时间（成片秒）→ 旧时间（剪好的录屏口播里的秒）。每条字幕开头对开头
    old = {q["id"]: q for q in pc["cues"]}
    seg6 = next(s for s in segs if s["id"] == "S6")
    pmap = [[seg6["s"], 0.0]]
    for q in pc["cues"]:
        pmap.append([CU[q["id"]]["s"], old[q["id"]]["s"]])
    pmap.append([seg6["e"], pc["total"]])
    still_old = next(p["out0"] for p in pc["pieces"] if not p["live"])
    # 打码静帧开始的成片时刻：旧时间 still_old 落在哪两条字幕之间就按比例换算
    still_new = None
    for (n0, o0), (n1, o1) in zip(pmap, pmap[1:]):
        if o0 <= still_old <= o1:
            still_new = n0 + (n1 - n0) * (still_old - o0) / max(1e-6, o1 - o0)
            break

    def S(i):
        return CU[i]["s"]

    def E(i):
        return CU[i]["e"]

    def P(i, phrase):
        q = CU[i]
        k = q["zh"].index(phrase)
        return q["s"] + (q["e"] - q["s"]) * k / len(q["zh"])
    j = 0.001
    seg7 = next(s for s in segs if s["id"] == "S7")
    seg8 = next(s for s in segs if s["id"] == "S8")
    # 原片时刻：M1139 3.5 s 点头像、约 6.9 s 点「兑换代码」、约 10.3 s 点「手动输入兑换码」、11.5 s 起是输入页；
    # M1140 0.6 s 打开侧栏、2.1 s 进设置、6.0 s 进「請求」（账单）、9–10.9 s 白屏加载、11 s 起是苹果的订阅页。
    phone = {
        "S7": {"src": "M1139", "keys": [[seg7["s"], 0.0], [P("M01", "点右上角"), 3.3], [E("M01"), 4.6], [P("M02", "兑换代码"), 6.8],
                                        [P("M02", "再点"), 8.6], [E("M02"), 10.4], [S("M03"), 11.4], [seg7["e"], 14.7]]},
        "S8": {"src": "M1140", "iap": [seg8["s"], E("M05") + 0.15],
               "keys": [[E("M05") + 0.15, 0.2], [P("M06", "在设置"), 1.8], [P("M06", "账单"), 3.4], [P("M06", "账单") + j, 5.6],
                        [P("M06", "就能看到"), 7.0], [P("M06", "我订的") - 0.05, 8.8], [P("M06", "我订的") - 0.05 + j, 11.0],
                        [E("M06"), 12.2], [seg8["e"], 14.6]]},
    }
    tl = {"fps": FPS, "frames": frames, "total": total, "title": TITLE, "chapters": CHAPTERS, "segs": segs, "cues": cues,
          "cam": {"t0": round(t_cam, 4), "total": cam["total"], "face": [0.56, 0.22]},
          "tts": {"blocks": offs},
          "pc": {"t0": seg6["s"], "map": [[round(a, 4), round(b, 4)] for a, b in pmap], "pieces": pc["pieces"], "still_t0": round(still_new, 4)},
          "phone": phone}
    (HERE / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "timeline.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"整片 {total:.1f} s（{frames} 帧）：{len(segs)} 段、{len(cues)} 条字幕（出镜 {len(cam['cues'])}、录屏口播 22、手机画外音 9、提醒 3）")
    for s in segs:
        print(f"  {s['id']} {s['layout']} {s['s']:7.2f}–{s['e']:7.2f}  {s['title']}")
    sp = [(b[0] - a[0]) / max(1e-6, b[1] - a[1]) for a, b in zip(pmap, pmap[1:])]
    print(f"  录屏伸缩：新/旧 {min(sp):.2f}–{max(sp):.2f}；打码静帧从 {still_new:.2f} s 起；配音块 {offs}")


if __name__ == "__main__":
    main()
