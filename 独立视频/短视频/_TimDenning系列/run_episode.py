# -*- coding: utf-8 -*-
"""配音之后的流水线，逐期跑，每步日志写到 制作/_run_<阶段>.log，最后打印摘要。

  python run_episode.py voice 1 2 3      每期 制作/02_配音：build_voice.py --qa（逐句识别核对）
  python run_episode.py timeline 1 2     每期 制作/00_整片：build_timeline.py（真实配音时间）→ check_subs → prep_frames → 静帧（--stills-segs）
  python run_episode.py render 1         每期：mix_audio → render_all（4 路，空闲内存不够自动降到 3 / 2 路）→ finish（成片 / 手机预览 / 三份 SRT）
  python run_episode.py qa 1 2           每期：qa_mix（把混音按字幕条切开逐句识别，CPU 占用大、不占渲染槽位）
  python run_episode.py all 1            voice + timeline + render 一口气（单期）

渲染前先 ListAgents 看别的会话在不在渲染（同一时间只跑一个渲染），并发消息约；用完发“渲染完了”。
"""
import ctypes
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import series_data as D  # noqa: E402
from gen_episode import ep_dir  # noqa: E402


def free_gb():
    class MS(ctypes.Structure):
        _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong), ("tv", ctypes.c_ulonglong),
                    ("av", ctypes.c_ulonglong), ("te", ctypes.c_ulonglong), ("ae", ctypes.c_ulonglong), ("ax", ctypes.c_ulonglong)]
    m = MS()
    m.l = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ap / 2 ** 30


def run(cmd, cwd, log, env=None):
    t0 = time.time()
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    out = (r.stdout or "") + (r.stderr or "")
    keep = [l for l in out.splitlines() if not any(x in l for x in ("jieba", "pkg_resources", "Building prefix", "Loading model", "Prefix dict"))]
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"\n$ {' '.join(str(c) for c in cmd[1:])}  (exit {r.returncode}, {time.time() - t0:.0f} s)\n" + "\n".join(keep) + "\n")
    return r.returncode, keep


def stage_voice(ep):
    d = ep_dir(ep) / "制作" / "02_配音"
    log = ep_dir(ep) / "制作" / "_run_voice.log"
    rc, out = run([sys.executable, "build_voice.py", "--qa"], d, log)
    low = [l for l in out if l.endswith("<<<")]
    print(f"第 {ep['num']} 期 voice：exit {rc}；" + (out[0] if out else "") + f"；机器识别低分 {len(low)} 句")
    for l in low:
        print("    ", l)


def stage_timeline(ep):
    e = ep_dir(ep) / "制作" / "00_整片"
    log = ep_dir(ep) / "制作" / "_run_timeline.log"
    for st in ([sys.executable, "build_timeline.py"], [sys.executable, "check_subs.py"], [sys.executable, "prep_frames.py"], [sys.executable, "render_all.py", "--stills-segs"]):
        rc, out = run(st, e, log)
        head = out[0] if out else ""
        print(f"第 {ep['num']} 期 {st[1]}：exit {rc}；{head[:160]}")
        if rc:
            return


def stage_render(ep):
    e = ep_dir(ep) / "制作" / "00_整片"
    log = ep_dir(ep) / "制作" / "_run_render.log"
    g = free_gb()
    workers = 4 if g >= 6 else 3 if g >= 4.5 else 2
    env = dict(os.environ, RENDER_WORKERS=str(workers))
    print(f"第 {ep['num']} 期 render：空闲内存 {g:.1f} GB → {workers} 路")
    for st in ([sys.executable, "mix_audio.py"], [sys.executable, "render_all.py"], [sys.executable, "finish.py"]):
        rc, out = run(st, e, log, env)
        tail = [l for l in out if l.strip()][-3:]
        print(f"  {st[1]}：exit {rc}；" + " | ".join(t[:150] for t in tail))
        if rc:
            return


def stage_qa(ep):
    e = ep_dir(ep) / "制作" / "00_整片"
    log = ep_dir(ep) / "制作" / "_run_qa.log"
    rc, out = run([sys.executable, "qa_mix.py"], e, log)
    low = [l for l in out if "<<<" in l or l.startswith("低于")]
    print(f"第 {ep['num']} 期 qa_mix：exit {rc}；" + (" | ".join(l[:120] for l in low[-8:]) or (out[-1][:150] if out else "")))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    stage, nums = sys.argv[1], [int(a) for a in sys.argv[2:]]
    for n in nums:
        ep = next(e for e in D.EPISODES if e["num"] == n)
        if stage in ("voice", "all"):
            stage_voice(ep)
        if stage in ("timeline", "all"):
            stage_timeline(ep)
        if stage in ("render", "all"):
            stage_render(ep)
        if stage in ("qa", "all"):
            stage_qa(ep)


if __name__ == "__main__":
    main()
