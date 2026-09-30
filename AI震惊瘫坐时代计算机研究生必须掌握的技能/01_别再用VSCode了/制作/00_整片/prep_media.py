# -*- coding: utf-8 -*-
"""整片的素材准备：录屏抽帧、拷图、各家 App 图标、手写笔画数据、静音音轨。先跑 ../01_录屏剪辑/cut_pauses.py 和 build_timeline.py。

  python prep_media.py          全部
  python prep_media.py hand     只重做 handdata.js（改了 scenes_*.js 里要手写的字以后跑这个）
  python prep_media.py icons    只重做图标

输出：media/（帧序列、图片、图标）、icons.js（有哪些真图标）、audio/mix.wav（v1 没有配音，整段静音）。
图标只用这台电脑上装着的 App 自带的图（Claude、Codex 包里的 OpenAI 标、Trae、TRAE SOLO、WorkBuddy、Chrome）；
其他家（VS Code、Copilot、Cursor、Windsurf、Kiro、Gemini、Antigravity、Devin、OpenClaw、豆包…）先用页面里画的字母占位，等用户同意再下载官方图标。
"""
import glob
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
MEDIA = HERE / "media"
AUDIO = HERE / "audio"
TL = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
FPS = TL["fps"]
REC_W, REC_H = 1474, 829          # 演示区画框的内框（16:9）


def run(args):
    subprocess.run(args, check=True, capture_output=True)


def latest(pattern):
    fs = sorted(glob.glob(pattern))
    return Path(fs[-1]) if fs else None


def appx(name):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", f"(Get-AppxPackage {name}).InstallLocation"], capture_output=True, text=True)
    p = r.stdout.strip().splitlines()
    return Path(p[0]) if p else None


def rounded(im, size=256, radius=0.22, bg=None):
    im = im.convert("RGBA").resize((size, size), Image.LANCZOS)
    if bg:
        base = Image.new("RGBA", (size, size), bg)
        base.alpha_composite(im)
        im = base
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size - 1, size - 1), int(size * radius), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(im, (0, 0), m)
    return out


def knot(ico, size=256, pad=0.2, bg="#000000"):
    """OpenAI 的结（白色、透明底）放在纯色圆角方块上。"""
    k = Image.open(ico)
    k = k.ico.getimage(max(k.ico.sizes())).convert("RGBA")
    inner = int(size * (1 - 2 * pad))
    base = Image.new("RGBA", (size, size), bg)
    base.alpha_composite(k.resize((inner, inner), Image.LANCZOS), (int(size * pad), int(size * pad)))
    return rounded(base, size)


# 官网下载的官方图标（2026-09-30 用户：“你下载图片就行，用来介绍的”“都下载”），在 素材/图标/，原样使用
DOWNLOADED = {
    "vscode": "vscode_code-stable.png", "copilot": "copilot_copilot-96.svg", "cursor": "cursor_icon-1024x1024.png",
    "windsurf": "windsurf_windsurf-black-symbol.svg", "devin": "devin_favicon.svg", "openclaw": "openclaw_favicon.svg",
    "so": "stackoverflow_apple-touch-icon@2.png", "mcp": "mcp_favicon.svg", "gemini": "gemini-cli_icon.png",
    "antigravity": "antigravity_icon__full-color.png", "kiro": "kiro_icon.svg", "doubao": "doubao_192x192.png",
    "csdn": "csdn_favicon64.ico", "playwright": "playwright_playwright-logo.svg", "meta": "meta_favicon.svg",
}


def icons():
    """各家 App 图标，一律原样显示（不裁圆角、不加底色）：本机装着的 App 自带的图 + 官网下载的官方图标。"""
    d = MEDIA / "icons"
    d.mkdir(parents=True, exist_ok=True)
    have = {}

    def put(key, src):
        src = Path(src)
        if src.suffix.lower() == ".svg":
            shutil.copy2(src, d / f"{key}.svg")
            have[key] = f"{key}.svg"
            return
        im = Image.open(src)
        if src.suffix.lower() == ".ico":
            im = im.ico.getimage(max(im.ico.sizes()))          # 只换格式（取最大的那一张）
        im = im.convert("RGBA")
        if max(im.size) > 512:
            im.thumbnail((512, 512), Image.LANCZOS)             # 等比缩小，不改图
        im.save(d / f"{key}.png")
        have[key] = f"{key}.png"

    claude = latest(r"C:\Users\yui\AppData\Local\Packages\OpenAI.Codex_*\LocalCache\Local\AnthropicClaude\app-*\resources\ion-dist\images\claude_app_icon.png")
    if claude:
        put("claude", claude)
    codex = appx("OpenAI.Codex")
    if codex and (codex / "app/resources/icon-chatgpt.ico").exists():
        for k in ("openai", "codex", "chatgpt"):                 # Codex 包里带的 OpenAI 图标（深色的结，白底上看得见）
            put(k, codex / "app/resources/icon-chatgpt.ico")
    for key, pat in [("trae", r"C:\Users\yui\AppData\Local\Programs\Trae\resources\app\resources\win32\code_150x150.png"),
                     ("traework", r"C:\Users\yui\AppData\Local\Programs\TRAE SOLO\resources\app\resources\win32\code_150x150.png")]:
        if Path(pat).exists():                                   # 图标四周是透明的空白：只裁掉空白
            im = Image.open(pat).convert("RGBA")
            im.crop(im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()).save(d / f"{key}.png")
            have[key] = f"{key}.png"
    wb = Path(r"C:\Users\yui\AppData\Local\Programs\WorkBuddyAI\Assets\Square150x150Logo.scale-400.png")
    if wb.exists():
        put("workbuddy", wb)
    chrome = latest(r"C:\Program Files\Google\Chrome\Application\*\VisualElements\Logo.png")
    if chrome:
        put("chrome", chrome)
    for key, name in DOWNLOADED.items():
        f = EP / "素材/图标" / name
        if f.exists():
            put(key, f)
    (HERE / "icons.js").write_text("window.ICON_FILES = " + json.dumps({k: f"media/icons/{v}" for k, v in have.items()}) + ";\n"
                                   "window.ICON_ORIG = " + json.dumps(sorted(have)) + ";\n", encoding="utf-8")
    print("icons:", ", ".join(sorted(have)))


def rec_frames():
    """录屏：按剪辑表把用到的范围抽成帧，文件名是去停顿版里的帧号（页面按帧号取）。"""
    done = {}
    for typ, r in TL["recs"].items():
        src = TL["sources"][r["src"]]
        video = (HERE / src["video"]).resolve() if not Path(src["video"]).is_absolute() else Path(src["video"])
        d = MEDIA / "rec" / r["src"]
        d.mkdir(parents=True, exist_ok=True)
        for c in r["cuts"]:
            i0, i1 = int(round(c["n0"] * FPS)), int(round(c["n1"] * FPS))
            key = (r["src"], i0, i1)
            if key in done:
                continue
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{i0 / FPS:.4f}", "-i", str(video), "-frames:v", str(i1 - i0 + 1),
                 "-vf", f"scale={REC_W}:{REC_H}:flags=lanczos", "-q:v", "3", "-start_number", str(i0), str(d / "f_%05d.jpg")])
            done[key] = True
        n = len(list(d.glob("f_*.jpg")))
        print(f"rec {typ:<12} {r['src']:<5} {len(r['cuts'])} 段，目录里共 {n} 帧")


ENGINE = HERE.parents[3] / "AI科普/skill/yuanlai-ruci-episode/assets/engine-template"   # 原LAI如此的白板引擎（hand_glyphs.py）
HAND_DATA = Path(r"D:\大疆\AI科普\素材\手写")                                          # 笔画数据（只读）


def cam():
    """出镜帧：从 edit/facecam.mp4 按帧号抽帧到 media/cam/f_NNNNN.jpg，帧号和正片时间线对齐。"""
    src = EP / "制作/02_出镜/edit/facecam.mp4"
    d = MEDIA / "cam"
    d.mkdir(parents=True, exist_ok=True)
    n = int(round(TL["total"] * FPS))
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src),
         "-frames:v", str(n), "-q:v", "3", "-start_number", "0",
         str(d / "f_%05d.jpg")])
    got = len(list(d.glob("f_*.jpg")))
    print(f"cam: {got} 帧 → media/cam/")


def hand_data():
    """白板版手写字的笔画：把页面脚本里出现的字都收进 handdata.js（用原LAI如此的 hand_glyphs.py，数据只读）。"""
    import sys
    sys.path.insert(0, str(ENGINE))
    import hand_glyphs
    texts = [f.read_text(encoding="utf-8") for f in sorted(HERE.glob("scenes_*.js"))] + [(HERE / "lib.js").read_text(encoding="utf-8")]
    d = hand_glyphs.build_hand_js(texts, HERE / "handdata.js", hand_dir=HAND_DATA)
    size = (HERE / "handdata.js").stat().st_size
    print(f"handdata.js: {len(d['cjk'])} 汉字, {len(d['punct'])} 标点, {len(d['lat']['g'])} 拉丁字符, {size / 1024:.0f} KB"
          + (f"；没有笔画的字：{''.join(d['missing'])}" if d["missing"] else ""))


def main():
    import sys
    if sys.argv[1:] == ["hand"]:
        hand_data()
        return
    if sys.argv[1:] == ["icons"]:
        icons()
        return
    if sys.argv[1:] == ["cam"]:
        cam()
        return
    MEDIA.mkdir(exist_ok=True)
    AUDIO.mkdir(exist_ok=True)
    icons()
    shutil.copy2(EP / "素材/Trae使用记录.png", MEDIA / "trae_heatmap.png")
    rec_frames()
    hand_data()
    total = TL["total"]
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo", str(AUDIO / "mix.wav")])
    print(f"audio/mix.wav 静音 {total:.1f}s")


if __name__ == "__main__":
    main()
