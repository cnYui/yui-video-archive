# -*- coding: utf-8 -*-
r"""逐期把整片渲出来（一次只渲一个，内存不够就降路数），出 成片 / 手机预览 / 三份 SRT。

  python render_series.py 1            只渲第 1 期
  python render_series.py 2 3 4 …      按顺序渲这几期
  python render_series.py all          1–10 期
  选项：--stills-only   只做 build_timeline / check_subs / prep_frames / 分段静帧，不渲整片
        --skip-stills   不出分段静帧（直接混音 + 渲整片）
        --continue      某一期出错后继续下一期（默认停下来）

每期 制作\00_整片\ 里依次：build_timeline.py → check_subs.py → prep_frames.py → render_all.py --stills-segs → mix_audio.py → render_all.py → finish.py。
日志：每期 制作\_render.log；总进度 工具\_render_series.log。
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import psutil

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from series_data import EPISODES, EP_ROOT  # noqa: E402

LOG = HERE / "_render_series.log"


def say(msg):
    line = time.strftime("%H:%M:%S ") + msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def workers_for_memory():
    free = psutil.virtual_memory().available / 2**30
    return (4 if free > 6 else 3 if free > 3.5 else 2), free


def wait_idle(max_min=30):
    """别的会话在渲染（headless Chrome 一堆）时先等。"""
    t0 = time.time()
    while time.time() - t0 < max_min * 60:
        n = sum(1 for p in psutil.process_iter(["name"]) if (p.info["name"] or "").lower().startswith("chrome-headless"))
        if n <= 1:
            return True
        say(f"  别处有 {n} 个 headless Chrome 在跑，等 30 s")
        time.sleep(30)
    return False


def run(ep_dir, args, log, env=None, must=None):
    t0 = time.time()
    p = subprocess.run([sys.executable] + args, cwd=str(ep_dir / "制作" / "00_整片"), capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    out = (p.stdout or "") + (p.stderr or "")
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"\n===== {' '.join(args)}  (exit {p.returncode}, {time.time() - t0:.0f}s)\n{out}\n")
    ok = p.returncode == 0 and (must is None or must in out)
    return ok, out, time.time() - t0


def episode(n, opts):
    d = EPISODES[n]
    ep = EP_ROOT / d["folder"]
    log = ep / "制作" / "_render.log"
    say(f"第 {n} 期 {d['folder']}：开始")
    steps = [("build_timeline", ["build_timeline.py"], None),
             ("check_subs", ["check_subs.py"], "没问题"),
             ("prep_frames", ["prep_frames.py"], None)]
    if "--skip-stills" not in opts:
        steps.append(("stills", ["render_all.py", "--stills-segs"], None))
    if "--stills-only" not in opts:
        steps += [("mix_audio", ["mix_audio.py"], None), ("render_all", ["render_all.py"], None), ("finish", ["finish.py"], None)]
    for name, args, must in steps:
        env = dict(os.environ)
        if name in ("stills", "render_all"):
            if not wait_idle():
                say("  等了 30 分钟别处还在渲染，放弃这一步")
                return False
            w, free = workers_for_memory()
            env["RENDER_WORKERS"] = str(w)
            say(f"  {name}：空闲内存 {free:.1f} GB → {w} 路")
        ok, out, sec = run(ep, args, log, env, must)
        say(f"  {name}：{'OK' if ok else '出错'}（{sec:.0f}s）" + ("" if ok else "\n" + out[-1500:]))
        if not ok:
            return False
    slug = d["slug"]
    mp4 = ep / f"{slug}_成片.mp4"
    if mp4.exists():
        pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "default=nw=1", str(mp4)], capture_output=True, text=True)
        say(f"第 {n} 期完成：{mp4}  {pr.stdout.strip().replace(chr(10), ' ')}")
    else:
        say(f"第 {n} 期步骤跑完（--stills-only 时没有成片）")
    return True


def main():
    opts = [a for a in sys.argv[1:] if a.startswith("--")]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    eps = sorted(EPISODES) if args and args[0] == "all" else [int(a) for a in args]
    for n in eps:
        ok = episode(n, opts)
        if not ok and "--continue" not in opts:
            say(f"第 {n} 期出错，停下（看 制作\\_render.log）")
            sys.exit(1)
    say("全部完成")


if __name__ == "__main__":
    main()
