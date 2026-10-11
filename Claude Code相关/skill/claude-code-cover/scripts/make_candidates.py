# -*- coding: utf-8 -*-
"""Claude Code相关封面：按一份候选清单一次出 2–3 个候选（每个 16:9 + 4:3），逐张验收，拼一张总览图；用户选定后一条命令复制成“选定”。

  python make_candidates.py <封面候选.json> --out "<…>\\制作\\04_封面"                 # 出候选 + 验收 + 候选总览.png
  python make_candidates.py <封面候选.json> --out … --only B                          # 只重出 B（改了字 / 动作后）
  python make_candidates.py --out … --select A [--force]                              # 用户选了 A：封面_A_* 复制成 封面_选定_*（不重新渲染）

封面候选.json（每期放在 制作\\04_封面\\ 里留档）：
  {"title": "视频标题（可选，用来查封面字有没有和标题重复）",
   "candidates": [
     {"name": "A", "line1": "别漏看重点", "line2": "Claude 新插件", "scheme": "night",  "pose": "float2"},
     {"name": "B", "line1": "You should know", "line2": "官方新插件", "scheme": "orange", "pose": "float3"},
     {"name": "C", "line1": "它替你盯着", "line2": "Claude 的输出", "scheme": "ivory",  "pose": "stand", "seed": 2}]}
每个候选的可选键（对应 make_cover.py 的参数）：scheme pose flip eyes seed no_fit bg cell_16x9 cell_4x3 min_cell_16x9 min_cell_4x3 mpos_16x9 mpos_4x3 bg_scale bg_anchor bg_shift。
候选之间要有差别：三个背景方案（night / orange / ivory 或 yellow）× 不同动作 × 不同钩子字；字和动作的选法见 SKILL.md。

出图后要做的事：打开 候选总览.png 看三个候选的整体，再打开用户要选的那组 16:9 / 4:3 原图细看（字有没有被挤、星点有没有读成标点、道具有没有出画、宇航员有没有被裁）——验收脚本代替不了眼睛。
封面只用 make_cover.py（官方像素宇航员）出，不要另写脚本画“自己的” Claude：check_cover.py 第 5 条会拿官方像素表重新渲染来逐像素对，非官方形象过不了。
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_cover as CC  # noqa: E402

VALUE_KEYS = {"scheme": "--scheme", "pose": "--pose", "eyes": "--eyes", "seed": "--seed", "bg": "--bg", "cell_16x9": "--cell-16x9", "cell_4x3": "--cell-4x3",
              "min_cell_16x9": "--min-cell-16x9", "min_cell_4x3": "--min-cell-4x3", "mpos_16x9": "--mpos-16x9", "mpos_4x3": "--mpos-4x3",
              "bg_scale": "--bg-scale", "bg_anchor": "--bg-anchor", "bg_shift": "--bg-shift"}
FLAG_KEYS = {"flip": "--flip", "no_fit": "--no-fit"}
RATIOS = ("16x9", "4x3")
FONT_CANDIDATES = [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf"]


def width_units(s):
    """封面字宽的粗略估计：汉字 1、其他字符 0.55（“You should know”约 8 个汉字宽）。一行超过 12 个汉字宽，字号会被压得很小。"""
    return sum(1.0 if ord(ch) > 0x2E80 else 0.55 for ch in s.strip())


def norm(s):
    return re.sub(r"[\s，。,.:：;；!！?？、—\-·/|“”\"'（）()\[\]【】]+", "", s).lower()


def cover_cmd(c, out):
    cmd = [sys.executable, str(HERE / "make_cover.py"), "--line1", c["line1"], "--line2", c.get("line2", ""), "--out", str(out), "--name", c["name"]]
    for k, flag in VALUE_KEYS.items():
        if k in c and c[k] is not None:
            v = c[k]
            cmd += [flag, ",".join(str(x) for x in v) if isinstance(v, (list, tuple)) else str(v)]
    for k, flag in FLAG_KEYS.items():
        if c.get(k):
            cmd.append(flag)
    return cmd


def lint_spec(spec):
    cands = spec.get("candidates", [])
    names = [c.get("name") for c in cands]
    if not cands or any(not n for n in names) or len(set(names)) != len(names):
        sys.exit("candidates 里每个候选要有不重复的 name（A / B / C）")
    title = norm(spec.get("title", ""))
    for c in cands:
        if not c.get("line1"):
            sys.exit(f"候选 {c['name']} 缺 line1")
        if "TODO" in c["line1"] + c.get("line2", ""):
            sys.exit(f"候选 {c['name']} 的封面字还是 TODO：先把钩子字填好")
        for k in ("line1", "line2"):
            w = width_units(c.get(k, ""))
            if w > 12:
                print(f"⚠ 候选 {c['name']} 的 {k}「{c[k]}」约 {w:.0f} 个汉字宽（> 12）：字号会被压小，封面字要短、要大")
        text = norm(c["line1"] + c.get("line2", ""))
        if title and text and (text in title or title in text):
            print(f"⚠ 候选 {c['name']} 的封面字和标题重复：封面写短钩子、标题写完整一句，两边别是同一句")
    schemes = {c.get("scheme", "night") for c in cands}
    poses = {c.get("pose", "float") for c in cands}
    if len(cands) > 1 and (len(schemes) == 1 or len(poses) == 1):
        print("⚠ 候选的背景方案或动作全都一样：给用户选的三个要有差别（不同背景方案 × 不同动作 × 不同钩子字）")


def font(size):
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def contact_sheet(out, rows, dst):
    """每个候选一行：16:9 缩略图 + 4:3 缩略图 + 一行说明。"""
    th_h, w169, w43, pad, label_h = 360, 640, 480, 16, 56
    W = pad + w169 + pad + w43 + pad
    H = pad + len(rows) * (th_h + label_h + pad)
    sheet = Image.new("RGB", (W, H), (58, 58, 60))
    d = ImageDraw.Draw(sheet)
    for i, r in enumerate(rows):
        y = pad + i * (th_h + label_h + pad)
        x = pad
        for ratio, tw in (("16x9", w169), ("4x3", w43)):
            p = out / f"封面_{r['name']}_{ratio}.png"
            if p.exists():
                sheet.paste(Image.open(p).convert("RGB").resize((tw, th_h), Image.LANCZOS), (x, y))
            x += tw + pad
        txt = f"{r['name']}  {r['scheme']} · {r['pose']}  「{r['line1']} / {r['line2']}」  字号 {r.get('fs16', '?')} / {r.get('fs43', '?')}  宇航员 {r.get('cell16', '?')} / {r.get('cell43', '?')} px  " + ("验收通过" if r["pass"] else "验收不通过")
        d.text((pad, y + th_h + 10), txt, fill=(255, 255, 255) if r["pass"] else (255, 120, 120), font=font(22))
    sheet.save(dst)
    return dst


def run_one(c, out):
    cmd = cover_cmd(c, out)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    sys.stdout.write("".join(ln + "\n" for ln in r.stdout.splitlines() if ln.startswith("->") or ln.lstrip().startswith("⚠")))
    if r.returncode != 0:
        print(f"候选 {c['name']} 出图失败：\n{r.stdout}\n{r.stderr}")
        return None
    row = {"name": c["name"], "scheme": c.get("scheme", "night"), "pose": c.get("pose", "float"), "line1": c["line1"], "line2": c.get("line2", ""), "pass": True}
    for ratio in RATIOS:
        png = out / f"封面_{c['name']}_{ratio}.png"
        if not CC.check_one(png, quiet=True):
            row["pass"] = False
        meta = json.loads(png.with_suffix(".meta.json").read_text(encoding="utf-8"))
        row["fs16" if ratio == "16x9" else "fs43"] = meta["font_size"]
        row["cell16" if ratio == "16x9" else "cell43"] = meta["mascot"]["cell"]
    return row


def select(out, name, force):
    done = True
    for ratio in RATIOS:
        src, dst = out / f"封面_{name}_{ratio}.png", out / f"封面_选定_{ratio}.png"
        if not src.exists():
            sys.exit(f"没有 {src.name}：先出候选")
        if dst.exists() and not force:
            print(f"已有 {dst.name}，没覆盖（要换就加 --force）")
            done = False
            continue
        shutil.copy2(src, dst)
        print("选定 ->", dst)
    if done:
        print("上传 B 站时：封面弹窗里“双比例同步改动”保持不勾，16:9 和 4:3 各传各的（见 SKILL.md）。")
    return done


def main():
    ap = argparse.ArgumentParser(description="按候选清单出封面候选 + 验收 + 总览图；--select 选定")
    ap.add_argument("spec", nargs="?", help="封面候选.json")
    ap.add_argument("--out", required=True, help="封面输出目录（制作\\04_封面）")
    ap.add_argument("--only", help="只出这几个候选（逗号分隔，如 B 或 A,C）")
    ap.add_argument("--select", metavar="NAME", help="把 封面_<NAME>_16x9 / 4x3 复制成 封面_选定_*（不重新渲染）")
    ap.add_argument("--force", action="store_true", help="--select 时覆盖已有的选定图")
    a = ap.parse_args()
    out = Path(a.out)
    if a.select:
        sys.exit(0 if select(out, a.select, a.force) else 2)
    if not a.spec:
        sys.exit("要给候选清单 JSON（或用 --select 选定）")
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    lint_spec(spec)
    out.mkdir(parents=True, exist_ok=True)
    only = set(a.only.split(",")) if a.only else None
    rows = []
    for c in spec["candidates"]:
        if only and c["name"] not in only:
            continue
        print(f"== 候选 {c['name']}：{c.get('scheme', 'night')} · {c.get('pose', 'float')}「{c['line1']} / {c.get('line2', '')}」")
        row = run_one(c, out)
        if row:
            rows.append(row)
    if only:
        # 只重出了部分：总览图要包含全部候选，没重出的从各自的 meta 读
        have = {r["name"] for r in rows}
        for c in spec["candidates"]:
            if c["name"] in have or not (out / f"封面_{c['name']}_16x9.meta.json").exists():
                continue
            m16 = json.loads((out / f"封面_{c['name']}_16x9.meta.json").read_text(encoding="utf-8"))
            m43 = json.loads((out / f"封面_{c['name']}_4x3.meta.json").read_text(encoding="utf-8"))
            ok = CC.check_one(out / f"封面_{c['name']}_16x9.png", quiet=True) & CC.check_one(out / f"封面_{c['name']}_4x3.png", quiet=True)
            rows.append({"name": c["name"], "scheme": m16["scheme"], "pose": m16["mascot"]["pose"], "line1": m16["line1"], "line2": m16["line2"], "pass": ok,
                         "fs16": m16["font_size"], "fs43": m43["font_size"], "cell16": m16["mascot"]["cell"], "cell43": m43["mascot"]["cell"]})
        rows.sort(key=lambda r: [c["name"] for c in spec["candidates"]].index(r["name"]))
    if not rows:
        sys.exit("一个候选都没出成")
    sheet = contact_sheet(out, rows, out / "候选总览.png")
    print(f"\n总览图 -> {sheet}")
    bad = [r["name"] for r in rows if not r["pass"]]
    print("验收：" + ("全部通过" if not bad else f"{'、'.join(bad)} 有不通过的项（上面有逐条）——换动作 / --flip / 缩短封面字 / 换 seed 再出"))
    print("下一步：打开 候选总览.png 和各候选的原图看一眼，发给用户选；用户选定后：python make_candidates.py --out", f'"{out}"', "--select <名字>")


if __name__ == "__main__":
    main()
