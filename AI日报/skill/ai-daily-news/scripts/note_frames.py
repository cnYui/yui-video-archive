"""note 文章配图：用做视频的 HTML 引擎出日文版画面（make_note.py 的 frames 命令调用）。

拷贝视频的 HTML 引擎（制作/vertical 的 engine.js、assets），index.html 的文字换成日文、字体换成 Noto Sans JP，
去掉字幕和进度条，来源截图框、鲸鱼娘 + 数字卡都往上收；每条新闻在数字卡亮着的那一秒截一张，
裁成 1080×1270（标题 + 来源截图框 + 鲸鱼娘 + 数字卡），缩到宽 960。
没有英文截图的条目（来源是中文页面）：框里放机构名 + 标题 + 来源（引擎自带的 nosnap 版式），不放中文页面截图。
"""
import copy
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

CROP_Y, CROP_H, OUT_W = 250, 1270, 960


def make_frames(ep, a):
    from playwright.sync_api import sync_playwright
    vdir = ep / "制作" / "vertical"
    T = json.loads((vdir / "tl_v.json").read_text(encoding="utf-8"))
    out = ep / "note" / "_frames"
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy(vdir / "engine.js", out / "engine.js")
    shutil.copytree(vdir / "assets", out / "assets", dirs_exist_ok=True)
    news = [sc for sc in T["scenes"] if sc["kind"] == "news"]
    if len(news) != len(a["items"]):
        sys.exit(f"视频里 {len(news)} 条新闻，article.json 里 {len(a['items'])} 条")
    J = copy.deepcopy(T)
    J["subs"] = []
    J["agenda"] = [dict(x, head=it["frame"]["t1"]) for x, it in zip(J["agenda"], a["items"])]
    kicker = a.get("frames_kicker", "AIデイリーニュース")
    dd = f"{int(ep.name[5:7])}.{int(ep.name[8:10])}"
    times = []
    for sc, it in zip([x for x in J["scenes"] if x["kind"] == "news"], a["items"]):
        f = it["frame"]
        if len(f["pts"]) != len(sc["pts"]) or len(sc.get("bigs", [])) != 1:
            sys.exit(f"第 {sc['idx']} 条：要点数（{len(f['pts'])}）和数字卡数要和视频一致（{len(sc['pts'])} / {len(sc.get('bigs', []))}）")
        sc["kicker"] = f"{kicker} · <b>{dd}</b> · 第 <b>{sc['idx']}</b> / {len(news)} 本"
        sc["t1"], sc["t2"], sc["tag"] = f["t1"], f["t2"], f.get("tag", "")
        sc["headline"], sc["org"], sc["source"] = f["t1"], f.get("org", ""), f.get("source", "")
        sc["pts"] = f["pts"]
        b = sc["bigs"][0]
        b.update(f["big"])
        if f.get("snap"):
            shutil.copy(ep / "制作" / "assets" / "snaps" / f["snap"], out / "assets" / "snaps" / f["snap"])
            sc["snap"] = "assets/snaps/" + f["snap"]
        else:
            for k in ("snap", "hl", "wh"):
                sc.pop(k, None)
        times.append(round((b["s"] + b["e"]) / 2, 2))
    (out / "tl_v.js").write_text("window.TL = " + json.dumps(J, ensure_ascii=False) + ";\n", encoding="utf-8")
    page_html = (vdir / "index.html").read_text(encoding="utf-8")
    page_html = page_html.replace("'Noto Sans SC'", "'Noto Sans JP','Noto Sans SC'").replace('<html lang="zh">', '<html lang="ja">')
    page_html = page_html.replace("</style>", "/* 日文版配图：字幕和进度条不要；来源截图框、鲸鱼娘 + 数字卡都往上收 */\n"
                                  ".frame { top:620px; } .cardwrap { top:1300px; } .whale { top:1290px; } #wshadow { top:1462px; } #subs, #prog { display:none; }\n</style>", 1)
    (out / "index.html").write_text(page_html, encoding="utf-8")
    fd = ep / "note" / "frames"
    fd.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 2340})
        errors = []
        page.on("pageerror", lambda x: errors.append("pageerror: " + str(x)))
        page.goto((out / "index.html").as_uri())
        page.evaluate("window.READY")
        for i, t in enumerate(times, 1):
            page.evaluate(f"renderAt({t})")
            raw = fd / f"_raw_{i:02d}.png"
            page.screenshot(path=str(raw), clip={"x": 0, "y": CROP_Y, "width": 1080, "height": CROP_H})
            im = Image.open(raw).convert("RGB")
            im = im.resize((OUT_W, round(im.height * OUT_W / im.width)), Image.LANCZOS)
            im.save(fd / f"frame_{i:02d}.png", optimize=True)
            raw.unlink()
        errors += page.evaluate("window.__ERR")
        warn = page.evaluate("window.__WARN")
        browser.close()
    print("errors:", errors or "none", "| 缩小字号的地方:", warn or "无")
    for i in range(1, len(times) + 1):
        pth = fd / f"frame_{i:02d}.png"
        print(pth.name, Image.open(pth).size, f"{pth.stat().st_size / 1024:.0f} KB")
