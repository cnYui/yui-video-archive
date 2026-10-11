"""《AI每日日报》同步到 note.com 的日文文章（用户 2026-10-10 定：routine 发日报时，用视频的素材同步写一篇纯日文文章发到 note）。

    python make_note.py <期目录> check     # 检查 note/article.json（必填项、纯日文、链接、图片、标签）
    python make_note.py <期目录> html      # article.json -> note/article.html（粘进 note 编辑器）+ article.md（人读预览）
    python make_note.py <期目录> cover     # 日文见出し画像：note/見出し画像_1280x670.png（沿用日报封面的白底 + 鲸鱼娘版式，字换成日文）
    python make_note.py <期目录> frames    # 配图：用做视频的 HTML 引擎（制作/vertical）出日文版画面，每条新闻一张 → note/frames/frame_0N.png（note_frames.py）
    python make_note.py <期目录> images    # 配图验收：见出し画像 + 每条新闻一张都在、尺寸对（缺了就不要发 note）
    python make_note.py <期目录> all       # check + html + cover + frames + images

article.json 由 routine 在 gate 通过后、按台本 + 一次资料写成（日文，です・ます体，Yui / 悠一 的口吻；事实只来自台本和 refs，
台本里的限定语——“据报道”“官方称”“Anthropic 自己的测试”——要一并带过去）。格式见 note/article.json（2026-10-10 那期是样板）：
    title, lead[], toc_head, items[{toc, h, when, intro[], sub1?, bullets[], sub2?, bullets2[], paras[], caution?, sources[{name,url}], image?, image_caption?}],
    outro_head, video{text,url}, notes[], tags[], cover{line1, line2, others_head, others[], others_more}
image = note/frames/frame_0N.png（frames 命令出：视频版式的日文画面——标题 + 来源截图橙框 + 鲸鱼娘 + 数字卡）。每条新闻要写 frame：
    {t1, t2, tag, pts[]（条数同视频里的要点卡）, big{n, small, d}, snap?（英文页面的截图文件名，制作/assets/snaps/ 下）, org?, source?（没有截图时框里显示）}
来源是中文页面（IT之家等）的条目不放截图（纯日文文章），框里放机构名 + 标题 + 来源。
"""
import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SERIES = SKILL.parent.parent
TEMPLATE = SKILL / "assets" / "cover-template" / "cover.white.html"
JP_FONT = "'Noto Sans JP', 'Yu Gothic', 'Meiryo', sans-serif"
KANA = re.compile(r"[぀-ヿ]")
JP_FONT_FILE = Path(r"C:/Windows/Fonts/NotoSansJP-VF.ttf")      # 日文字体的字集：汉字不在里面 = 简体中文字（“这”“时”“发”“现”…）
_JP_CMAP = None
ALLOWED_PROPER = ["IT之家", "上善无形"]            # 专有名词里的中文字符（媒体名 / 作者名）照原样保留


def in_jp_font(ch):
    global _JP_CMAP
    if _JP_CMAP is None:
        try:
            from fontTools.ttLib import TTFont
            _JP_CMAP = TTFont(str(JP_FONT_FILE)).getBestCmap()
        except Exception as e:                      # 没有字体 / fontTools：跳过这项检查
            print("[提示] 读不到日文字体，跳过简体字检查：", e)
            _JP_CMAP = {}
    return not _JP_CMAP or ord(ch) in _JP_CMAP


def load(ep):
    p = ep / "note" / "article.json"
    if not p.is_file():
        sys.exit(f"没有 {p}：先照样板（2026-10-10 那期的 note/article.json）写日文文章")
    return json.loads(p.read_text(encoding="utf-8"))


def all_texts(a):
    yield a["title"]
    yield from a.get("lead", [])
    yield a.get("toc_head", "")
    for it in a["items"]:
        for k in ("toc", "h", "when", "sub1", "sub2", "caution", "image_caption"):
            if it.get(k):
                yield it[k]
        for k in ("intro", "bullets", "bullets2", "paras"):
            yield from it.get(k, [])
        for s in it.get("sources", []):
            yield s["name"]
    yield a.get("outro_head", "")
    yield (a.get("video") or {}).get("text", "")
    yield from a.get("notes", [])
    yield from a.get("tags", [])
    cv = a.get("cover") or {}
    for k in ("line1", "line2", "others_head", "others_more"):
        yield cv.get(k, "")
    yield from cv.get("others", [])


def check(ep, a, quiet=False):
    errs, warns = [], []
    for k in ("title", "lead", "items", "notes", "tags", "cover"):   # video 可选：B 站没发成的那天不写
        if not a.get(k):
            errs.append(f"缺 {k}")
    if errs:
        return errs, warns
    if not 3 <= len(a["items"]) <= 8:
        warns.append(f"{len(a['items'])} 条新闻（日报一般 6–8 条）")
    if len(a["title"]) > 140:
        errs.append(f"标题 {len(a['title'])} 字，note 上限 150")
    if len(a["tags"]) > 10:
        errs.append("标签最多 10 个")
    note_dir = ep / "note"
    for i, it in enumerate(a["items"], 1):
        for k in ("toc", "h", "intro", "sources"):
            if not it.get(k):
                errs.append(f"第 {i} 条缺 {k}")
        for s in it.get("sources", []):
            if not re.match(r"https?://", s.get("url", "")):
                errs.append(f"第 {i} 条来源缺网址：{s}")
        if not it.get("image"):                       # 用户 2026-10-10：note 文章必须配图，每条新闻一张
            errs.append(f"第 {i} 条没有 image（note 文章必须配图：image = frames/frame_0{i}.png）")
        elif not it.get("frame"):
            errs.append(f"第 {i} 条有 image 但没有 frame（画面文字、数字卡）")
        elif not (note_dir / it["image"]).is_file():
            warns.append(f"第 {i} 条图片还没生成：{note_dir / it['image']}（先跑 frames）")
        if not it.get("caution"):
            warns.append(f"第 {i} 条没写“注意したい点”（台本里的限定语要带过来）")
    # 纯日文：不能有只在简体中文里用的字（专有名词除外）；必须有假名
    for t in all_texts(a):
        t2 = t
        for pn in ALLOWED_PROPER:
            t2 = t2.replace(pn, "")
        bad = sorted({c for c in t2 if "一" <= c <= "鿿" and not in_jp_font(c)})
        if bad:
            errs.append(f"有简体中文字符 {''.join(bad)}：{t[:40]}…")
    body = "".join(all_texts(a))
    if len(KANA.findall(body)) < 200:
        errs.append("假名太少，不像日文")
    chars = len(body)
    if not quiet:
        print(f"字数约 {chars}，{len(a['items'])} 条，图片 {sum(1 for it in a['items'] if it.get('image'))} 张，标签 {len(a['tags'])} 个")
    return errs, warns


def verify_images(ep, a):
    """用户 2026-10-10：note 文章必须配图。见出し画像 1 张 + 每条新闻 1 张（frames）都在、尺寸对，才允许往 note 发。"""
    errs = []
    note_dir = ep / "note"
    head = note_dir / "見出し画像_1280x670.png"
    if not head.is_file():
        errs.append(f"缺见出し画像：{head}（make_note.py cover）")
    else:
        sz = Image.open(head).size
        if sz != (1280, 670):
            errs.append(f"见出し画像尺寸 {sz}，要 1280x670")
    for i, it in enumerate(a["items"], 1):
        p = note_dir / (it.get("image") or f"frames/frame_{i:02d}.png")
        if not p.is_file():
            errs.append(f"缺第 {i} 条配图：{p}（make_note.py frames）")
            continue
        w, h = Image.open(p).size
        if w != 960 or h < 800:
            errs.append(f"第 {i} 条配图尺寸 {(w, h)} 不对（要宽 960、高 ≥ 800）")
    return errs


def esc(s):
    return html.escape(s, quote=False)


def link(s):
    return f'<a href="{html.escape(s["url"], quote=True)}">{esc(s["name"])}</a>'


def build_html(a):
    h = []
    h.append("<p>[[HEADER]]</p>")
    for t in a["lead"]:
        h.append(f"<p>{esc(t)}</p>")
    h.append(f"<h2>{esc(a['toc_head'])}</h2>")
    h.append("<ul>" + "".join(f"<li>{esc(it['toc'])}</li>" for it in a["items"]) + "</ul>")
    for it in a["items"]:
        h.append(f"<h2>{esc(it['h'])}</h2>")
        if it.get("image"):
            h.append(f"<p>[[IMG:{it['image']}|{esc(it.get('image_caption', ''))}]]</p>")
        intro = list(it["intro"])
        if it.get("when"):
            intro[0] = f"【{it['when']}】{intro[0]}"
        h += [f"<p>{esc(t)}</p>" for t in intro]
        if it.get("sub1"):
            h.append(f"<h3>{esc(it['sub1'])}</h3>")
        if it.get("bullets"):
            h.append("<ul>" + "".join(f"<li>{esc(t)}</li>" for t in it["bullets"]) + "</ul>")
        if it.get("sub2"):
            h.append(f"<h3>{esc(it['sub2'])}</h3>")
        if it.get("bullets2"):
            h.append("<ul>" + "".join(f"<li>{esc(t)}</li>" for t in it["bullets2"]) + "</ul>")
        h += [f"<p>{esc(t)}</p>" for t in it.get("paras", [])]
        if it.get("caution"):
            h.append(f"<p><strong>注意したい点：</strong>{esc(it['caution'])}</p>")
        for j, s in enumerate(it["sources"]):
            h.append(f"<p>{'出典：' if j == 0 else '出典（関連）：'}{link(s)}</p>")
    h.append(f"<h2>{esc(a['outro_head'])}</h2>")
    v = a.get("video")
    if v:
        h.append(f"<p>{esc(v['text'])}</p>")
        h.append(f"<p>動画：{link({'name': 'Bilibiliで見る', 'url': v['url']})}</p>")
    for t in a["notes"]:
        h.append(f"<p>{esc(t)}</p>")
    return "\n".join(h)


def build_md(a):
    m = [f"# {a['title']}", ""]
    m += a["lead"] + ["", f"## {a['toc_head']}"] + [f"- {it['toc']}" for it in a["items"]]
    for it in a["items"]:
        m += ["", f"## {it['h']}"]
        if it.get("image"):
            m.append(f"（画像：{it['image']}　{it.get('image_caption', '')}）")
        intro = list(it["intro"])
        if it.get("when"):
            intro[0] = f"【{it['when']}】{intro[0]}"
        m += intro
        for k_h, k_b in (("sub1", "bullets"), ("sub2", "bullets2")):
            if it.get(k_h):
                m += ["", f"### {it[k_h]}"]
            m += [f"- {t}" for t in it.get(k_b, [])]
        m += it.get("paras", [])
        if it.get("caution"):
            m.append(f"**注意したい点：**{it['caution']}")
        m += [f"出典：{s['name']} {s['url']}" for s in it["sources"]]
    m += ["", f"## {a['outro_head']}"] + ([a["video"]["text"], a["video"]["url"]] if a.get("video") else []) + a["notes"]
    m += ["", "タグ：" + " ".join("#" + t for t in a["tags"])]
    return "\n".join(m)


def make_cover(ep, a):
    sys.path.insert(0, str(HERE))
    import make_cover_white as mc
    sc = json.loads((ep / "台本.json").read_text(encoding="utf-8"))
    cv = a["cover"]
    out = ep / "note"
    out.mkdir(exist_ok=True)
    import datetime
    pz = mc.pose_for((sc.get("cover") or {}).get("mood", "吃惊"), datetime.date.fromisoformat(sc.get("date") or ep.name))
    theme = mc.THEMES[mc.DEFAULT_THEME]
    acc = theme["accent"].lstrip("#")
    sprite, anims = mc.compose_sprite(pz["pose"], pz.get("eyes"), pz.get("fx", []), None,
                                      tuple(int(acc[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    work = out / "_cover"
    work.mkdir(exist_ok=True)
    sprite.save(work / "sprite.png")
    fw, fh = anims["frame_w"], anims["frame_h"]
    data = {"line1": cv.get("line1", ""), "line2": cv["line2"], "l1px": 168, "l2px": 236, "maxw": 1320,
            "safe": [300, 1620], "textCx": 900, "scale": 9, "frame": [fw, fh], "footRow": anims["anchor"]["foot_y"],
            "fishX": mc.place_x("right", 9, fw), "foot": 1062, "tag": "", "theme": theme,
            "others": cv.get("others", []), "othersHead": cv.get("others_head", ""), "othersMore": cv.get("others_more", ""),
            "listX": 300, "listW": 740, "listBottom": 1000}
    (work / "_cover_data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("{{FONTS_CSS}}", Path(__import__("os").path.relpath(SERIES / "素材" / "字体" / "fonts.css", work)).as_posix())
    page = page.replace("{{SPRITE}}", "sprite.png").replace("'Noto Sans SC'", JP_FONT).replace('lang="zh-CN"', 'lang="ja"')
    (work / "cover.html").write_text(page, encoding="utf-8")
    tmp = work / "_render"
    tmp.mkdir(exist_ok=True)
    cmd = [sys.executable, str(SERIES / "片头片尾" / "render.py"), str(work / "cover.html"), "--data", str(work / "_cover_data.json"),
           "--stills", "0", "--stills-dir", str(tmp)]
    for attempt in (1, 2):
        if subprocess.run(cmd).returncode == 0:
            break
        if attempt == 2:
            sys.exit("封面渲染两次都失败")
    src = Image.open(tmp / "still_0.00.png").convert("RGB")
    assert src.size == (1920, 1080), src.size
    # note 的见出し画像是 1280x670（1.91:1）：两边补白到 2063x1080 再缩，鲸鱼娘和大字都不裁
    w = round(1080 * 1280 / 670)
    canvas = Image.new("RGB", (w, 1080), (255, 255, 255))
    canvas.paste(src, ((w - 1920) // 2, 0))
    final = canvas.resize((1280, 670), Image.LANCZOS)
    p = out / "見出し画像_1280x670.png"
    final.save(p, optimize=True)
    src.save(out / "見出し画像_1920x1080_原寸.png", optimize=True)
    print(p, final.size, f"{p.stat().st_size / 1024:.0f} KB", "｜", pz["pose"], "｜版式布局", "（看一眼图确认字没被缩得太小）")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dir")
    ap.add_argument("cmd", choices=["check", "html", "cover", "frames", "images", "all"])
    args = ap.parse_args()
    ep = Path(args.episode_dir).resolve()
    a = load(ep)
    if args.cmd in ("check", "html", "all"):
        errs, warns = check(ep, a)
        for w in warns:
            print("[提示]", w)
        for e in errs:
            print("[错误]", e)
        if errs:
            sys.exit(1)
        print("note 文章检查通过")
    if args.cmd in ("html", "all"):
        (ep / "note" / "article.html").write_text(build_html(a), encoding="utf-8")
        (ep / "note" / "article.md").write_text(build_md(a), encoding="utf-8")
        print("已写 note/article.html、note/article.md")
    if args.cmd in ("cover", "all"):
        make_cover(ep, a)
    if args.cmd in ("frames", "all"):
        sys.path.insert(0, str(HERE))
        from note_frames import make_frames
        make_frames(ep, a)
    if args.cmd in ("images", "all"):
        ierrs = verify_images(ep, a)
        for e in ierrs:
            print("[错误]", e)
        if ierrs:
            sys.exit("note 文章必须配图：配图没齐，不要往 note 发（推送写原因）")
        print(f"配图齐全：见出し画像 1 张 + 每条新闻 {len(a['items'])} 张")


if __name__ == "__main__":
    main()
