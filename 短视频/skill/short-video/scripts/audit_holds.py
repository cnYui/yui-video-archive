# -*- coding: utf-8 -*-
r"""审定格：每个场景的每个窗口（上框 / 下框）定格了多少秒。

  python audit_holds.py <本条目录> [--max 3.0]

读 <本条>\制作\00_整片\timeline.json（build_timeline.py 的输出）里每个场景 ranges（上框）/ ranges2（下框）里 hold = true 的段，
单段 > --max 秒（默认 3）的列出来，并报每个窗口定格的总比例。有超限的退出码 1。
为什么：素材比台词短时 gen_ep / build_timeline 会把最后一帧定格补满，而 gen_ep.py 的报告只打印“定格补 x s”里上窗的那个数，
下窗定格 10.9 s 要翻 plan.json 才看得到（第 1 期出镜版）。一个窗口死定格十几秒，观众只看到另一个窗口在动。
有意的定格（讲解一张图 / 一个对话框时停住）可以留，但要心里有数；其余的补素材（官方课的安全段、录屏别的片段）或把场景改成单窗。
"""
import json
import sys
from pathlib import Path


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    ep = Path(args[0])
    mx = float(args[args.index("--max") + 1]) if "--max" in args else 3.0
    tl = json.loads((ep / "制作" / "00_整片" / "timeline.json").read_text(encoding="utf-8"))
    tot = {"ranges": 0.0, "ranges2": 0.0}
    dur = {"ranges": 0.0, "ranges2": 0.0}
    over = []
    for sid, c in tl["clips"].items():
        if c.get("kind") == "card":
            continue
        for key in ("ranges", "ranges2"):
            rs = c.get(key) or []
            if not rs:
                continue
            dur[key] += sum(r["e"] - r["s"] for r in rs)
            for r in rs:
                if r.get("hold"):
                    d = r["e"] - r["s"]
                    tot[key] += d
                    if d > mx:
                        over.append((sid, "上框" if key == "ranges" else "下框", r["src"], r["in"], d, r["s"]))
    for sid, win, src, t_in, d, t0 in over:
        print(f"  {sid} {win}：{src} 第 {t_in:.1f} s 定格 {d:.1f} s（成片 {t0:.1f} s 起）")
    for key, name in (("ranges", "上框"), ("ranges2", "下框")):
        if dur[key]:
            print(f"{name}：定格共 {tot[key]:.1f} s / {dur[key]:.1f} s（{tot[key] / dur[key] * 100:.0f}%）")
    print(f"单段定格 > {mx:g} s 的 {len(over)} 处" + ("（有意停住讲一张图 / 一个对话框的可以留，其余补素材）" if over else "：无"))
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
