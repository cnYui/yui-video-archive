# -*- coding: utf-8 -*-
"""按字幕条号取静帧：python stills_at.py N05+1.0 N07+2.5 12.3 …（Nxx+秒 = 这条开始说之后几秒；纯数字 = 成片秒数）→ stills/_sheet_t_*.png"""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
cu = {q["id"]: q for q in T["cues"]}
ts = []
for a in sys.argv[1:]:
    if a[0] == "N":
        i, _, off = a.partition("+")
        ts.append(round(cu[i]["s"] + float(off or 0), 2))
    else:
        ts.append(float(a))
print("时刻：", ts)
subprocess.run([sys.executable, str(HERE / "render_all.py"), "--stills"] + [str(t) for t in ts], check=True)
