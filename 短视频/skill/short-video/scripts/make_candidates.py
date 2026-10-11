# -*- coding: utf-8 -*-
r"""交付包的封面：3 个候选 × 3 个比例（竖屏 3:4、16:9、4:3）= 9 张，再拼一张总览给用户选。

用户 2026-10-04：“封面的话，是 3x3，3 种每种都要有竖屏、16:9、4:3 的封面”。

  python make_candidates.py <本条目录>                读 <本条>\制作\04_封面\candidates.json，出 候选A_3x4.png / 候选A_16x9.png / 候选A_4x3.png … 候选C_*（共 9 张）和 候选总览.png
  python make_candidates.py <本条目录> --select B     用户选了 B：把 候选B 的三张复制成 封面_选定_3x4.png / 封面_选定_16x9.png / 封面_选定_4x3.png
  python make_candidates.py <本条目录> A C            只重出指定候选（改了某个候选的参数时用），总览照样重拼

candidates.json：
  "defaults": 三个候选共用的字段（style / frame.video / frame.crop / theme / tags / avoid / keep_clear …，字段含义见 make_cover.py 开头）
  "candidates": [ {"id": "A", "note": "一句话说这个候选是什么", "recommend": true, "frame": {"t": 41.2}, "big": ["这是AI！"], …}, … ]
     每个候选 = defaults 叠上自己的字段（frame / theme / tags 这类小字典按键合并）；style 可以混用：full（满框，用户 2026-10-04 定的默认样式）/ shot / split。
三个候选要真有区别：不同的帧或镜头（安静的帧 / 特写 / 页面或数字画面）、不同的钩子字（不和任何一个平台标题同一句）；full 样式的候选要有推荐的那个（"recommend": true）。
横版里有视频通话小窗 / 水印时：avoid 写小窗（3:4 和 4:3 躲开），16:9 保留就在 keep_clear 里写，字自动放到另一边。
"""
import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_cover as M  # noqa: E402

FONT = r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf"
RATIOS = ("3x4", "16x9", "4x3")


def merged(defaults, cand):
    out = dict(defaults)
    for k, v in cand.items():
        if k in ("id", "note", "recommend"):
            continue
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = {**out[k], **v}
        else:
            out[k] = v
    return out


def overview(cdir, cands):
    big, small = ImageFont.truetype(FONT, 38), ImageFont.truetype(FONT, 26)
    H, gap = 420, 40
    rows = []
    for c in cands:
        ims = [Image.open(cdir / f"候选{c['id']}_{r}.png").convert("RGB") for r in RATIOS]
        rows.append((c, [i.resize((int(i.width * H / i.height), H), Image.LANCZOS) for i in ims]))
    W = max(sum(i.width for i in ims) + gap * (len(ims) + 1) for _, ims in rows)
    sheet = Image.new("RGB", (W, len(rows) * (H + 100) + 30), "#F1F2F5")
    d = ImageDraw.Draw(sheet)
    y = 20
    for c, ims in rows:
        tag = "（推荐）" if c.get("recommend") else ""
        d.text((gap, y), f"候选 {c['id']}{tag} · {c.get('note', '')}", fill="#141413", font=big)
        x = gap
        for r, i in zip(RATIOS, ims):
            sheet.paste(i, (x, y + 60))
            d.text((x + 6, y + 60 + H + 4), {"3x4": "3:4 竖屏", "16x9": "16:9", "4x3": "4:3"}[r], fill="#5E5850", font=small)
            x += i.width + gap
        y += H + 100
    out = cdir / "候选总览.png"
    sheet.save(out)
    return out, sheet.size


def main():
    args = [a for a in sys.argv[1:]]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    ep = Path(args.pop(0))
    cdir = ep / "制作" / "04_封面"
    cfgf = json.loads((cdir / "candidates.json").read_text(encoding="utf-8"))
    cands = cfgf["candidates"]
    if "--select" in args:
        pick = args[args.index("--select") + 1]
        if pick not in {c["id"] for c in cands}:
            sys.exit(f"没有候选 {pick}，可选：{', '.join(c['id'] for c in cands)}")
        for r in RATIOS:
            shutil.copy2(cdir / f"候选{pick}_{r}.png", cdir / f"封面_选定_{r}.png")
        print(f"已把候选 {pick} 复制成 封面_选定_3x4 / 16x9 / 4x3.png")
        return
    want = [a for a in args if a in {c["id"] for c in cands}] or [c["id"] for c in cands]
    if len(cands) != 3:
        print(f"注意：交付包要 3 个候选，现在写了 {len(cands)} 个")
    with sync_playwright() as p:
        b = p.chromium.launch()
        for c in cands:
            if c["id"] not in want:
                continue
            cfg = merged(cfgf.get("defaults", {}), c)
            if "big" not in cfg:
                sys.exit(f"候选 {c['id']} 没写 big（封面大字）")
            for ln in (cfg["big"] if isinstance(cfg["big"], list) else [cfg["big"]]):
                if len(ln) > 6:
                    print(f"注意：候选 {c['id']} 的大字“{ln}”超过 6 个字（封面协定：每行 3–6 字）")
            print(f"— 候选 {c['id']}（{c.get('note', '')}）")
            M.build(cdir, cfg, out_name=lambda kind, cid=c["id"]: f"候选{cid}_{kind}.png", src_name=f"_src_{c['id']}.png", browser=b)
        b.close()
    out, size = overview(cdir, cands)
    print(f"{out.name}: {size[0]}×{size[1]}")


if __name__ == "__main__":
    main()
