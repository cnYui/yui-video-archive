# -*- coding: utf-8 -*-
"""配音出来后：用 whisper 词级时间找出 N05 / N06 / N09 里关键词的开口时刻，写三个排期，再重渲三个烤好的片段。

  python make_schedules.py            读 ../00_整片/timeline.json（真实时间）、../02_配音/edit/tts_edit.json、台本/录制稿.json
                                     → carousel_schedule.json / widget_schedule.json / conn_schedule.json，再依次跑 make_cards_clip.py / make_widget_clip.py / make_conn_clip.py

时间都是“场景开头起的秒数”（clip 场景的片段从场景开头放）。关键词 → 时刻：在这句配音里按词级识别结果找（识别错了就退回按字数比例估）。
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
PROD = EP / "制作"
TL = json.loads((PROD / "00_整片" / "timeline.json").read_text(encoding="utf-8"))
TTS = json.loads((PROD / "02_配音" / "edit" / "tts_edit.json").read_text(encoding="utf-8"))
SC = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))
SAY = {l["id"]: l["say"] for l in SC["lines"]}
ZH = {l["id"]: l["zh"] for l in SC["lines"]}
CUE = {q["id"]: q for q in TL["cues"]}
SEG = {s["id"]: s for s in TL["segs"]}
LINE = {x["id"]: x for x in TTS["lines"]}
_model = None


def words_of(lid):
    """这句配音的词级识别：[(文字, 相对“有声起点”的秒数)]"""
    global _model
    from faster_whisper import WhisperModel
    if _model is None:
        _model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=6)
    L = LINE[lid]
    tmp = HERE / "_w.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(L["n0"]), "-t", str(L["n1"] - L["n0"]), "-i", str(PROD / "02_配音" / "edit" / "tts_narration.wav"),
                    "-ac", "1", "-ar", "16000", str(tmp)], check=True)
    segs, _ = _model.transcribe(str(tmp), language="zh", beam_size=5, temperature=0, condition_on_previous_text=False,
                                initial_prompt="Meta、Muse、Home Link、ESP32-C5、Home Assistant、HDMI、WiFi。", word_timestamps=True)
    off = L["s"] - L["n0"]
    return [(w.word, w.start - off) for s in segs for w in s.words]


def when(lid, phrase, words, zh_phrase=None):
    """phrase 在这句里的开口时刻（相对有声起点）：先在识别词里找，找不到按字数比例估。"""
    txt = ZH[lid]
    k = txt.find(zh_phrase or phrase)
    dur = LINE[lid]["e"] - LINE[lid]["s"]
    est = dur * (k / max(len(txt), 1)) if k >= 0 else 0.0
    cat, pos = "", []
    for w, t in words:
        pos.append((len(cat), t))
        cat += w.replace(" ", "")
    j = cat.lower().find(phrase.lower().replace(" ", ""))
    if j >= 0:
        best = max((p for p in pos if p[0] <= j), key=lambda p: p[0], default=None)
        if best and abs(best[1] - est) < 2.2:
            return best[1]
    return est


def rel(lid, t_in_line):
    """场景内的秒数 = 这句字幕起点 − 场景起点 + 句内秒数"""
    q = CUE[lid]
    return q["s"] - SEG[q["seg"]]["s"] + t_in_line


def write_sched(extra=None):
    """sched.js：Home Link 片段三段的起点 + 每句配音的词级时间（scenes.js 的 P() 优先用它；识别不到再按字数比例估）。"""
    f = PROD / "00_整片" / "sched.js"
    cur = json.loads(f.read_text(encoding="utf-8")[len("window.SCHED = "):].strip().rstrip(";")) if f.exists() else {}
    cur.update(extra or {})
    cur["words"] = {lid: [[w, round(t, 2)] for w, t in words_of(lid)] for lid in LINE}
    f.write_text("window.SCHED = " + json.dumps(cur, ensure_ascii=False) + ";" + chr(10), encoding="utf-8")


def main():
    # ── 轮播（N05）：四个项目依次点名 → 橙框；说到“彩色墨水屏”时滚到后面
    w5 = words_of("N05")
    t_pi, t_rd, t_tv, t_ey = (rel("N05", when("N05", p, w5)) for p in ("树莓派", "圆形", "电视", "彩色"))
    scene = SEG[CUE["N05"]["seg"]]
    dur5 = round(CUE["N05"]["e"] - scene["s"] + 0.5, 2)               # 按配音长度排（别按现有场景长度：场景本身又由素材片段撑长，会越排越长）
    hl = [[round(t_pi - 0.1, 2), round(t_rd - 0.2, 2), 0], [round(t_rd - 0.1, 2), round(t_tv - 0.2, 2), 1],
          [round(t_tv - 0.1, 2), round(t_ey - 0.25, 2), 2], [round(t_ey - 0.05, 2), round(dur5 - 0.2, 2), 3]]
    scroll = [[0, 0], [round(t_ey - 1.15, 2), 0], [round(t_ey - 0.2, 2), 1040], [dur5, 1040]]
    (HERE / "carousel_schedule.json").write_text(json.dumps({"dur": dur5, "scroll": scroll, "hl": hl}, ensure_ascii=False), encoding="utf-8")
    print("轮播", dur5, hl, scroll)

    # ── Home Link 组件（N06）：Device 讲“Home Link”，内部讲“ESP32-C5”，连线讲“连家里 Wi-Fi … 开灯”
    w6 = words_of("N06")
    t_c5 = rel("N06", when("N06", "ESP32", w6, "ESP32"))
    t_wf = rel("N06", when("N06", "连家里", w6, "连家里"))
    scene = SEG[CUE["N06"]["seg"]]
    dur6 = CUE["N06"]["e"] - scene["s"] + 0.45
    XF = 0.35
    d_dev = max(2.4, t_c5 - 0.35 + XF)                    # 第 2 段在 t_c5 − 0.35 起（交叉淡化 XF 前一点开始）
    d_in = max(2.6, (t_wf - 0.35) - (t_c5 - 0.35) + XF)
    d_con = max(3.0, dur6 - (t_wf - 0.35) + 0.4)
    (HERE / "widget_schedule.json").write_text(json.dumps({"segs": [round(d_dev, 2), round(d_in, 2), round(d_con, 2)]}), encoding="utf-8")
    s_in = d_dev - XF                                      # Home Link 片段里“内部”“连线”两段的起点（片段内秒数，make_widget_clip.py 的排法）
    s_con = s_in + d_in - XF
    write_sched({"w1_inside": round(s_in, 2), "w1_conn": round(s_con, 2)})
    print("Home Link 三段", round(d_dev, 2), round(d_in, 2), round(d_con, 2), "（ESP32 在", round(t_c5, 2), "s，连家里在", round(t_wf, 2), "s，场景", round(dur6, 2), "s）")

    # ── 收尾（N09）：说到“大脑”时亮橙框
    w9 = words_of("N09")
    t_br = rel("N09", when("N09", "大脑", w9))
    scene = SEG[CUE["N09"]["seg"]]
    dur9 = round(CUE["N09"]["e"] - scene["s"] + 0.4 + 0.8 + 0.15, 2)     # 配音结束 + PAD_END 0.4 + 片尾 TAIL 0.8 + 一点余量
    (HERE / "conn_schedule.json").write_text(json.dumps({"dur": dur9, "hl_t": round(max(0.2, t_br - 0.1), 2)}), encoding="utf-8")
    print("收尾", dur9, "框在", round(t_br - 0.1, 2))

    for s in ("make_cards_clip.py", "make_widget_clip.py", "make_conn_clip.py"):
        subprocess.run([sys.executable, str(HERE / s)], check=True, cwd=str(HERE))


if __name__ == "__main__":
    if "--words-only" in sys.argv:                  # 只更新 sched.js 里的词级时间（不重渲三个片段）
        write_sched()
        print("sched.js 的词级时间已更新")
    else:
        main()
