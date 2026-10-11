# -*- coding: utf-8 -*-
"""渲染本期封面：合集固定模板 cover.html（不改）+ 本期 cover.json。每个候选出 16:9（1920×1080）和 4:3（1440×1080），
再拼一张预览（每个候选一行：16:9、4:3、信息流大小）。

  python render_covers.py               cover.json 里的候选 → 封面_方案N_<名字>_16x9.png / _4x3.png + 封面_候选_预览.png
  python render_covers.py --select 3    选定第 3 个候选（也可以写名字）→ 封面_选定_16x9.png / _4x3.png + 封面_选定_预览.png，
                                         cover.json 记下 selected

cover.json：顶层写本期的 chip（合集胶囊，固定「计算机专业 · AI 基础功」）、line1、line2、icon、face；
candidates 里每个候选只写和顶层不同的字段（一般是 face，有时是 line1 / line2），没写 candidates 就只出顶层这一个。
候选之间只换人像帧或封面字；版式、颜色、字号由模板定。

每张图渲染后自检，问题打印出来、预览图上标红：
  - 字超出安全区：16:9 收在 x 96–1824（B 站首页卡片把 16:9 裁成 16:10，左右各切约 96 px），4:3 收在 40–1400
  - 字进了底部 12%（时长角标、播放量的位置）
  - 字压到人像：按抠图（白描边版）的 alpha 逐像素查（图标算在第二行里）
  - 字被缩得太小：比模板字号小了 15% 以上（封面字太长，缩短）
  - 人像顶部被裁
"""
import argparse
import json
import math
import re
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
CFG = HERE / "cover.json"
SIZES = ((1920, "16x9"), (1440, "4x3"))
FIELDS = ("chip", "line1", "line2", "icon", "face")
FONT = r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf"


def safe(name):
    return re.sub(r'[\\/:*?"<>|\s]+', "_", str(name)).strip("_") or "未命名"


def load_cfg():
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    base = {k: cfg.get(k, "") for k in FIELDS}
    cands = []
    for i, c in enumerate(cfg.get("candidates") or [{}], 1):
        d = dict(base, **{k: v for k, v in c.items() if k in FIELDS})
        d["no"], d["name"] = i, c.get("name") or d["face"]
        for k in ("chip", "line1", "line2", "face"):
            if not d[k]:
                sys.exit(f"cover.json 候选 {i} 缺 {k}")
        if not (HERE / "face_cut" / f"{d['face']}_outline.png").exists():
            sys.exit(f"候选 {i}：没有 face_cut/{d['face']}_outline.png（先跑 cutout.py）")
        cands.append(d)
    return cfg, cands


def out_png(c, tag):
    return HERE / f"封面_方案{c['no']}_{safe(c['name'])}_{tag}.png"


def check(chk, mask_img):
    """自检：返回问题列表。chk 是页面给的文字框、人像框、字号；mask_img 是抠图（白描边版）的 alpha。"""
    w, h = chk["w"], chk["h"]
    lo, hi = (96, w - 96) if w >= 1900 else (40, w - 40)
    issues = []
    p = chk["person"]
    pw, ph = p["x1"] - p["x0"], p["y1"] - p["y0"]
    if p["y0"] < -1:
        issues.append(f"人像顶部被裁 {-p['y0']:.0f} px")
    mask = np.array(mask_img.resize((max(1, round(pw)), max(1, round(ph))), Image.BILINEAR))
    for t in chk["texts"]:
        if t["x0"] < lo - 0.5 or t["x1"] > hi + 0.5:
            issues.append(f"{t['n']} 超出安全区 x {t['x0']:.0f}–{t['x1']:.0f}（安全区 {lo}–{hi}）")
        if t["y1"] > h * 0.88:
            issues.append(f"{t['n']} 进了底部 12%（y 到 {t['y1']:.0f}）")
        x0, y0 = max(t["x0"], p["x0"]), max(t["y0"], p["y0"])
        x1, y1 = min(t["x1"], p["x1"]), min(t["y1"], p["y1"])
        if x1 > x0 and y1 > y0:
            sub = mask[int(y0 - p["y0"]):math.ceil(y1 - p["y0"]), int(x0 - p["x0"]):math.ceil(x1 - p["x0"])]
            if sub.size and (sub > 40).any():
                ys, xs = np.nonzero(sub > 40)
                issues.append(f"{t['n']} 压到人像（约 x {x0 + xs.min():.0f}–{x0 + xs.max():.0f}，y {y0 + ys.min():.0f}–{y0 + ys.max():.0f}）")
    for s in chk["sizes"]:
        if s["s"] < s["d"] * 0.85:
            issues.append(f"{s['n']} 缩到 {s['s']:.0f} px（模板 {s['d']} px），封面字太长")
    return issues


def render(cands):
    outs, probs = {}, {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        for c in cands:
            mask_img = Image.open(HERE / "face_cut" / f"{c['face']}_outline.png").split()[-1]
            for w, tag in SIZES:
                page = browser.new_page(viewport={"width": w, "height": 1080})
                errs = []
                page.on("pageerror", lambda e: errs.append(str(e)))
                data = {k: c[k] for k in FIELDS}
                data["w"] = w
                page.add_init_script(f"window.__COVER__ = {json.dumps(data, ensure_ascii=False)};")
                page.goto((HERE / "cover.html").as_uri())
                page.wait_for_function("window.__READY__ === true || !!window.__ERR__", timeout=30000)
                err = page.evaluate("window.__ERR__ || ''")
                if err or errs:
                    browser.close()
                    sys.exit(f"页面出错（方案{c['no']} {c['name']} {tag}）：{err or errs}")
                out = out_png(c, tag)
                page.screenshot(path=str(out))
                chk = page.evaluate("window.__CHECK__")
                page.close()
                issues = check(chk, mask_img)
                outs[(c["no"], tag)], probs[(c["no"], tag)] = out, issues
                print(out.name, "OK" if not issues else "")
                for s in issues:
                    print("   !", s)
        browser.close()
    return outs, probs


def wrap(d, s, font, maxw):
    """按像素宽度折行：中文逐字折，英文、数字、px 这类连在一起的不拆。"""
    lines, cur = [], ""
    for tok in re.findall(r"[A-Za-z0-9.:%–-]+|\s+|.", s):
        if cur.strip() and d.textlength(cur + tok, font=font) > maxw:
            lines.append(cur.rstrip())
            cur = tok.lstrip()
        else:
            cur += tok
    return lines + [cur] if cur.strip() else lines


def sheet(cands, outs, probs, path):
    """每个候选一行：16:9、4:3、信息流大小（约 360×203）；自检问题标红（写在信息流缩略图下面，自动折行）。"""
    font = ImageFont.truetype(FONT, 30)
    small = ImageFont.truetype(FONT, 22)
    rowh = 560
    img = Image.new("RGB", (880 + 20 + 660 + 20 + 360 + 60, rowh * len(cands) + 20), "#C9CDD3")
    d = ImageDraw.Draw(img)
    for i, c in enumerate(cands):
        y = 10 + i * rowh
        d.text((20, y), f"方案 {c['no']}  {c['name']}", fill="#111", font=font)
        a = Image.open(outs[(c["no"], "16x9")]).convert("RGB")
        b = Image.open(outs[(c["no"], "4x3")]).convert("RGB")
        img.paste(a.resize((880, 495), Image.LANCZOS), (20, y + 50))
        img.paste(b.resize((660, 495), Image.LANCZOS), (920, y + 50))
        img.paste(a.resize((360, 203), Image.LANCZOS), (1600, y + 50))
        d.text((1600, y + 260), "信息流大小", fill="#333", font=font)
        lines = []
        for tag in ("16x9", "4x3"):
            for s in probs[(c["no"], tag)]:
                lines += wrap(d, f"! {tag.replace('x', ':')} {s}", small, 380)
        for k, s in enumerate(lines[:8]):
            d.text((1600, y + 306 + k * 28), s, fill="#B91C1C", font=small)
    img.save(path)
    print(path.name)


def main():
    ap = argparse.ArgumentParser(description="渲染本期封面（合集固定模板）")
    ap.add_argument("--select", metavar="N|名字", help="选定一个候选，复制成 封面_选定_16x9.png / 封面_选定_4x3.png")
    a = ap.parse_args()
    cfg, cands = load_cfg()
    if a.select:
        pick = [c for c in cands if a.select in (str(c["no"]), c["name"])]
        if not pick:
            sys.exit(f"没有候选 {a.select}（有：{'、'.join(str(c['no']) + ' ' + c['name'] for c in cands)}）")
        c = pick[0]
        outs, probs = render([c])
        for _, tag in SIZES:
            shutil.copyfile(outs[(c["no"], tag)], HERE / f"封面_选定_{tag}.png")
            print(f"封面_选定_{tag}.png ← {outs[(c['no'], tag)].name}")
        sheet([c], outs, probs, HERE / "封面_选定_预览.png")
        cfg["selected"] = c["name"]
        CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if any(probs.values()):
            print("注意：选定的这张有自检问题（见上面），确认能接受再投稿")
        return
    outs, probs = render(cands)
    sheet(cands, outs, probs, HERE / "封面_候选_预览.png")


if __name__ == "__main__":
    main()
