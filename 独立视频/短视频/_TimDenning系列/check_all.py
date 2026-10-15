# -*- coding: utf-8 -*-
"""逐期跑：build_timeline（估时 / 真配音时间）→ check_subs → prep_frames → render_all --stills-segs，把结果汇总到 _check_all.log。一次只跑一期（同一时间只跑一个渲染）。

  python check_all.py               6 期全跑（估时轴）
  python check_all.py 2 3           只跑指定的期
  python check_all.py --real        用真实配音的时间轴（02_配音/edit/tts_edit.json 已有时）
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import series_data as D  # noqa: E402
from gen_episode import ep_dir  # noqa: E402

real = "--real" in sys.argv
nums = [int(a) for a in sys.argv[1:] if a.isdigit()] or [e["num"] for e in D.EPISODES]
log = HERE / "_check_all.log"
with open(log, "a", encoding="utf-8") as lg:
    for n in nums:
        ep = next(e for e in D.EPISODES if e["num"] == n)
        eng = ep_dir(ep) / "制作" / "00_整片"
        lg.write(f"\n===== 第 {n} 期 {ep['name']}  {time.strftime('%H:%M:%S')} {'真实配音' if real else '估时'} =====\n")
        lg.flush()
        steps = [[sys.executable, "build_timeline.py"] + ([] if real else ["--est"]), [sys.executable, "check_subs.py"], [sys.executable, "prep_frames.py"], [sys.executable, "render_all.py", "--stills-segs"]]
        for st in steps:
            r = subprocess.run(st, cwd=eng, capture_output=True, text=True, encoding="utf-8", errors="replace")
            out = (r.stdout or "") + (r.stderr or "")
            keep = [l for l in out.splitlines() if not any(x in l for x in ("jieba", "pkg_resources", "Building prefix", "Loading model", "Prefix dict"))]
            lg.write(f"$ {' '.join(st[1:])}  (exit {r.returncode})\n" + "\n".join(keep[-14:] if st[1] != "build_timeline.py" else keep[:14]) + "\n")
            lg.flush()
            if r.returncode:
                lg.write("  ← 失败，这一期后面的步骤跳过\n")
                break
        lg.write(f"----- 第 {n} 期结束 {time.strftime('%H:%M:%S')}\n")
        lg.flush()
print("done ->", log)
