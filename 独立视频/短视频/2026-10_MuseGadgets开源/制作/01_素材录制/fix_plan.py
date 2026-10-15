# -*- coding: utf-8 -*-
"""配音 / 排期出来后，把 plan.json 里素材片段的 range 长度对齐：H1（AYi 动画）= N01 配音长 + 0.9 s；C1 / W1 / W2 = 对应烤好的片段时长。
  python fix_plan.py          （改 台本/plan.json；改之前先备份成 plan.json.bak_<时间>）"""
import json
import shutil
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
BASE = Path(r"D:\大疆\独立视频\素材\2026-10_MuseGadgets开源\官网与仓库")
TTS = json.loads((EP / "制作" / "02_配音" / "edit" / "tts_edit.json").read_text(encoding="utf-8"))
L = {x["id"]: x for x in TTS["lines"]}


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)], capture_output=True, text=True, check=True).stdout.strip())


plan_p = EP / "台本" / "plan.json"
plan = json.loads(plan_p.read_text(encoding="utf-8"))
shutil.copy(plan_p, plan_p.with_name("plan.json.bak_" + time.strftime("%H%M%S")))
want = {"H1": round(min(14.5, max(5.0, L["N01"]["e"] - L["N01"]["s"] + 0.4)), 2),
        "C1": round(dur(BASE / "cards_carousel.mp4") - 0.05, 2),
        "W1": round(dur(BASE / "homelink_widget.mp4") - 0.05, 2),
        "W2": round(dur(BASE / "homelink_conn_hl.mp4") - 0.05, 2)}
for sc in plan["plan"]:
    if sc["id"] in want:
        sc["ranges"][0]["out"] = want[sc["id"]]
        print(sc["id"], "range out =", want[sc["id"]])
plan_p.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
