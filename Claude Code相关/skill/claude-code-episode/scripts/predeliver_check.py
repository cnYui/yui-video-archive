# -*- coding: utf-8 -*-
r"""交付前 / 投稿前自查：把“成片、字幕、封面、投稿信息、片尾、.gitignore”这些容易漏的东西一次查完，不合格的列出来。

  python predeliver_check.py <本期目录>          例：python predeliver_check.py "D:\大疆\Claude Code相关\03_YouShouldKnow插件"

查的项（全部用本期目录里的文件，不联网）：
 1. 文件：<slug>_成片.mp4、_手机预览.mp4、三份 SRT、投稿信息.json、封面_选定_16x9 / 4x3.png、制作/00_整片/outro.json
 2. 成片：时长 = 片头 + 正片 + 片尾（时长读 AI科普/片头片尾/pack_info.py，不写死，±0.3 s）、2340×1080、30 fps、响度 −16 ± 1.5 LUFS、真峰值 ≤ −0.5 dBFS
 3. SRT：条数 = timeline.json 的字幕条数；最后一条在片尾开始之前结束；中英文各一行
 4. 投稿信息：标题 ≤ 80、简介 ≤ 2000、标签 ≤ 10、章节从 00:00 开始并递增、不超过成片时长
 5. 封面：两个比例尺寸对；调 claude-code-cover 的 check_cover.py 验收（有 meta.json 时）
 6. 片尾 outro.json：references ≤ 8 条、thanks / items ≤ 8 项、有感谢语
 7. .gitignore：本期的渲染产物（media/ frames.js timeline.* 等）和封面 png 有忽略规则
退出码 0 = 全部通过。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

PACK = Path(r"D:\大疆\AI科普\片头片尾")
COVER_CHECK = Path(r"D:\大疆\Claude Code相关\skill\claude-code-cover\scripts\check_cover.py")
GITIGNORE = Path(r"D:\大疆\.gitignore")

sys.path.insert(0, str(PACK))
from pack_info import intro_seconds, outro_seconds  # noqa: E402

res = []


def ok(name, cond, detail=""):
    res.append(bool(cond))
    print(("通过 " if cond else "不通过 ") + name + ("：" + detail if detail else ""))


def ffprobe(path):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", str(path)],
                                  capture_output=True, text=True, check=True).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    num, den = v["r_frame_rate"].split("/")
    return int(v["width"]), int(v["height"]), float(num) / float(den), float(j["format"]["duration"])


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1])


def srt_cues(path):
    txt = Path(path).read_text(encoding="utf-8").strip()
    blocks = [b for b in re.split(r"\n\s*\n", txt) if b.strip()]
    out = []
    for b in blocks:
        lines = b.strip().split("\n")
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", lines[1])
        t1 = int(m[5]) * 3600 + int(m[6]) * 60 + int(m[7]) + int(m[8]) / 1000
        out.append((t1, lines[2:]))
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ep = Path(sys.argv[1])
    sc = json.loads((ep / "台本" / "录制稿.json").read_text(encoding="utf-8"))
    slug = sc["slug"]
    need = [f"{slug}_成片.mp4", f"{slug}_手机预览.mp4", f"{slug}_双语字幕.srt", f"{slug}_中文字幕.srt", f"{slug}_英文字幕.srt", "投稿信息.json",
            "制作/04_封面/封面_选定_16x9.png", "制作/04_封面/封面_选定_4x3.png", "制作/00_整片/outro.json"]
    miss = [n for n in need if not (ep / n).exists()]
    ok("1 文件齐全", not miss, "缺：" + "、".join(miss) if miss else f"{len(need)} 个都在")
    if miss:
        sys.exit(1)

    tl = json.loads((ep / "制作" / "00_整片" / "timeline.json").read_text(encoding="utf-8"))
    intro, outro = intro_seconds(), outro_seconds()
    w, h, fps, dur = ffprobe(ep / f"{slug}_成片.mp4")
    exp = intro + tl["total"] + outro
    ok("2a 成片时长 = 片头 + 正片 + 片尾", abs(dur - exp) <= 0.3, f"{dur:.2f} s（片头 {intro} + 正片 {tl['total']:.2f} + 片尾 {outro} = {exp:.2f}）")
    ok("2b 成片规格", (w, h) == (2340, 1080) and abs(fps - 30) < 0.01, f"{w}×{h} @ {fps:g} fps")
    lufs, peak = loudness(ep / f"{slug}_成片.mp4")
    ok("2c 响度 / 真峰值", abs(lufs + 16) <= 1.5 and peak <= -0.5, f"{lufs} LUFS（−16 ± 1.5），真峰值 {peak} dBFS（≤ −0.5）")

    cues = srt_cues(ep / f"{slug}_双语字幕.srt")
    ok("3a SRT 条数 = 画面里的字幕条数", len(cues) == len(tl["subs"]), f"SRT {len(cues)} 条，timeline {len(tl['subs'])} 条")
    ok("3b 最后一条在片尾开始之前结束", cues[-1][0] <= dur - outro + 0.1, f"最后一条结束 {cues[-1][0]:.2f} s，片尾 {dur - outro:.2f} s 开始")
    ok("3c 双语 SRT 每条两行（中文 + 英文）", all(len(c[1]) == 2 for c in cues), "")

    info = json.loads((ep / "投稿信息.json").read_text(encoding="utf-8"))
    ok("4a 标题 ≤ 80 字", len(info["title"]) <= 80, f"{len(info['title'])} 字")
    ok("4b 简介 ≤ 2000 字", len(info["desc"]) <= 2000, f"{len(info['desc'])} 字")
    ok("4c 标签 ≤ 10 个", len(info["tags"]) <= 10, f"{len(info['tags'])} 个")
    secs = []
    for t, _ in info["chapters"]:
        mm, ss = t.split(":")
        secs.append(int(mm) * 60 + int(ss))
    ok("4d 章节从 00:00 起、递增、不超过成片时长", secs[0] == 0 and secs == sorted(secs) and secs[-1] <= dur, f"{info['chapters'][0][0]} … {info['chapters'][-1][0]}")

    for r, size in (("16x9", (1920, 1080)), ("4x3", (1440, 1080))):
        from PIL import Image
        im = Image.open(ep / "制作" / "04_封面" / f"封面_选定_{r}.png")
        ok(f"5 封面 {r} 尺寸", im.size == size, f"{im.size[0]}×{im.size[1]}")
    sel = ep / "制作" / "04_封面" / "封面_选定_16x9.png"
    cand = [p for p in (ep / "制作" / "04_封面").glob("封面_*_16x9.meta.json")]
    if cand and COVER_CHECK.exists():
        # 选定图和哪个候选一样，就用那个候选的 meta 验收
        import hashlib
        hs = hashlib.md5(sel.read_bytes()).hexdigest()
        for m in cand:
            png = m.with_suffix("").with_suffix(".png")
            if png.exists() and hashlib.md5(png.read_bytes()).hexdigest() == hs:
                pngs = [png]
                png43 = png.with_name(png.name.replace("_16x9", "_4x3"))
                sel43 = ep / "制作" / "04_封面" / "封面_选定_4x3.png"
                if png43.exists() and sel43.exists() and hashlib.md5(png43.read_bytes()).hexdigest() == hashlib.md5(sel43.read_bytes()).hexdigest():
                    pngs.append(png43)                       # 4:3 也是同一个候选：两张一起验
                r = subprocess.run([sys.executable, str(COVER_CHECK), *map(str, pngs)], capture_output=True, text=True, encoding="utf-8", errors="replace")
                ok("5 封面验收（check_cover.py）", r.returncode == 0, f"{len(pngs)} 张：" + (r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""))
                break
        else:
            ok("5 封面验收", True, "选定图没有对应的候选 meta，跳过（用户自己提供的封面？）")

    ou = json.loads((ep / "制作" / "00_整片" / "outro.json").read_text(encoding="utf-8"))
    thanks = ou.get("thanks") or ou.get("items") or []
    ok("6 片尾 outro.json", len(ou.get("references", [])) <= 8 and len(thanks) <= 8 and ou.get("closing"), f"参考文献 {len(ou.get('references', []))} 条、致谢 {len(thanks)} 项")

    gi = GITIGNORE.read_text(encoding="utf-8") if GITIGNORE.exists() else ""
    key = ep.name
    ok("7 .gitignore 有本期规则", key in gi and "/制作/00_整片/media/" in gi.replace("\\", "/"), "没找到本期的渲染产物 / 封面忽略规则" if key not in gi else "")
    print("全部通过" if all(res) else "有不合格项")
    sys.exit(0 if all(res) else 1)


if __name__ == "__main__":
    main()
