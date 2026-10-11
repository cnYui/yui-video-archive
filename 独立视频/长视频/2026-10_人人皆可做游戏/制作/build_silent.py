"""《欢迎来到 人人皆可做游戏的 时代》无声版（横屏 1920×1080、60 帧、没有声音）。

做法：每个镜头先渲成一个小 mp4（片段/NN_名字.mp4），最后无损拼起来；同时写出镜头表.md（每段从几分几秒到几分几秒、
对应稿子的哪一段、用的哪份素材），等你的露脸视频和音频到了，按句子对时间再微调。

用法：
  python build_silent.py list              只打印镜头表（不渲）
  python build_silent.py render [S03 ...]  渲指定的段（不写 = 全部），然后拼成 无声版_v1.mp4
  python build_silent.py join              只拼接（片段都渲好了）
  环境变量 THREADS：x264 用几个线程（录屏的时候设 2，别抢游戏的 CPU）
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import vis
from vis import FPS, GAME, H, MAT, W, font

ROOT = Path(__file__).resolve().parent
SEG = ROOT / "片段"
OUT = ROOT / "无声版_v1.mp4"
THREADS = os.environ.get("THREADS", "6")
REC = Path(r"D:\大疆\游戏素材\银魂\录屏素材\2026-10-06_全流程实况")
CLIPS = Path(r"D:\大疆\游戏素材\银魂\录屏素材\2026-10-04_精彩片段")
SRC = {  # 实况录像按段存放的 webm（384×216），时间都是这个文件自己的时间轴
    "A": REC / "A_序章到第三章" / "full.webm", "B": REC / "B_第四到第七章" / "full.webm",
    "C": REC / "C_第八到第十章" / "full.webm", "D": REC / "D_第十一章到终章" / "full.webm",
}
X264 = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS), "-fps_mode", "cfr",
        "-video_track_timescale", "60000", "-threads", THREADS, "-an"]


class Seg:
    """一个镜头。kind = clip（从视频里截一段）/ gen（画面库生成）。"""

    def __init__(self, sec, name, dur, kind, note, src="", **kw):
        self.sec, self.name, self.dur, self.kind, self.note, self.src, self.kw = sec, name, dur, kind, note, src, kw
        self.path = None

    def label(self):
        return "%s_%s" % (self.sec, self.name)


def clip(sec, name, dur, path, start, note, tag="", speed=1.0, crop=None, src=""):
    """path = 要截的视频；src = 写进镜头表的素材说明。"""
    return Seg(sec, name, dur, "clip", note, src=src, path=path, start=start, tag=tag, speed=speed, crop=crop)


def gen(sec, name, dur, fn, note, src=""):
    return Seg(sec, name, dur, "gen", note, src=src, fn=fn)


def tag_png(text, path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vis.tag(im, text)
    im.save(path)


# ---------------------------------------------------------------- 镜头表（时长按稿子口播 5.4 字/秒估，实机段另加 12 秒游戏原声）
def timeline() -> list[Seg]:
    sk = Image.open(GAME / "assets" / "bg" / "title_skyline.png").convert("RGB")
    T: list[Seg] = []
    # S01 冷开场 64 秒：4 秒实机快切 → 出镜 58 秒 → 片名卡 2 秒
    T.append(clip("S01", "快切1_全江户集结", 2.0, CLIPS / "13_第十三章_全江户集结.mp4", 17.0, "「全江户，集结！」", src="精彩片段/13"))
    T.append(clip("S01", "快切2_X字斩", 2.0, CLIPS / "14_第十三章_背靠背和高杉挡刀.mp4", 29.0, "和高杉背靠背，X 字斩", src="精彩片段/14"))
    T.append(gen("S01", "出镜占位", 58.0, lambda: vis.gen_placeholder("S01 冷开场", "9 月 25 号那条视频 → 15 章游戏", 58), "出镜：开场白、起点（9/25 的提示词）、做了什么"))
    T.append(gen("S01", "片名卡", 2.0, lambda: vis.gen_title_card(2.0, sk), "欢迎来到 人人皆可做游戏的时代", src="title_skyline.png"))
    # S03 / S06 / S08 实机段：素材在实况录像里挑好后写进 footage.json
    fs = footage_segments()
    T += [x for x in fs if x.sec == "S03"]
    # S04 人物和场景从哪来 33 秒
    T.append(gen("S04", "角色图集总览", 7.0, lambda: vis.gen_image_push(MAT / "角色图集" / "总览.png", 7.0, 1.0, 1.35, 0.30, 0.30, "角色图集 / 总览.png：42 个角色", pixel=True), "42 个角色", src="角色图集/总览.png"))
    T.append(gen("S04", "银时全部动作", 8.0, lambda: vis.gen_atlas_reel(8.0), "每人 31 个动作、11 种表情（银时 34 种）", src="角色图集/gintoki"))
    T.append(gen("S04", "背景拆图层", 9.0, lambda: vis.gen_layers_stack(9.0), "背景是代码画的，拆成 1600 多张图层", src="assets/bg/street"))
    T.append(gen("S04", "音频清单", 9.0, lambda: vis.gen_list_scroll(9.0), "12 首 8 位配乐、80 多个音效", src="游戏素材/银魂/音频"))
    # S05 剧本从哪来 57 秒
    T.append(gen("S05", "分镜总表", 11.0, lambda: vis.gen_storyboard_table(11.0), "原片 5 分半 80 句台词；15 个场景 = 15 章", src="剧情分镜/分镜总表.md"))
    T.append(gen("S05", "镜头表_分镜图", 9.0, lambda: vis.gen_image_push(MAT / "剧情分镜" / "分镜图" / "s02_shinpachi.png", 9.0, 1.0, 1.6, 0.5, 0.3, "剧情分镜 / 分镜图 / s02_shinpachi.png"), "每个场景一张镜头表", src="剧情分镜/分镜图"))
    T.append(gen("S05", "章节调研", 14.0, lambda: vis.gen_text_scroll(GAME / "docs" / "章节素材调研" / "s13.md", 14.0, 1, 150, "docs/章节素材调研/s13.md", "做每一章之前，逐个镜头研究原片"), "逐个镜头研究原片", src="docs/章节素材调研/s13.md"))
    T.append(gen("S05", "台词代码", 23.0, lambda: vis.gen_code_scroll(GAME / "story" / "chapter1.js", 23.0, 392, 440, "story/chapter1.js", "await S.say(…)  台词是 Claude 按人物性格新写的", highlight=(409, 421)), "台词是 Claude 按人物性格新写的", src="story/chapter1.js"))
    T += [x for x in fs if x.sec == "S06"]
    # S07 代码怎么来的 35 秒
    T.append(gen("S07", "引擎结构", 8.0, lambda: vis.gen_tree(8.0), "一个游戏引擎都没用，浏览器画布 + 原生 JavaScript", src="游戏/ 文件夹"))
    T.append(gen("S07", "剧情代码", 12.0, lambda: vis.gen_code_scroll(GAME / "story" / "chapter2.js", 12.0, 906, 970, "story/chapter2.js", "剧情写成一行行指令：谁说话，往哪走，在哪开打"), "剧情写成一行行指令", src="story/chapter2.js"))
    T.append(gen("S07", "截图墙", 8.0, lambda: vis.gen_screenshot_flash(sorted((GAME / "tools" / "_playtest").glob("*.png")), 8.0, "tools/_playtest：自动通关边玩边截图"), "自动通关：边玩边截图（238 张）", src="tools/_playtest"))
    T.append(gen("S07", "0报错", 7.0, lambda: vis.gen_results_card(7.0), "612 句对话，34 分钟，0 个报错", src="pt_all_final"))
    T += [x for x in fs if x.sec == "S08"]
    # S10 这事比银魂大 47 秒：B-roll（出镜小窗 / 切画面用），中间留出镜占位
    T += s10_segments()
    # S11 收尾 9 秒：出镜 6 秒 → Logo 3 秒
    T.append(gen("S11", "出镜占位", 6.0, lambda: vis.gen_placeholder("S11 收尾", "以前，是人去适应知识的样子……", 6.0), "出镜：金句收尾"))
    T.append(gen("S11", "片尾Logo", 3.0, lambda: vis.gen_end_card(3.0), "游戏 Logo + 人人皆可做游戏的时代", src="assets/ui/logo.png"))
    return T


def footage_segments() -> list[Seg]:
    """实机段：从 footage.json 读（src = A/B/C/D 实况录像的段，或精彩片段里的 mp4 文件名）。哪一段还没有素材，就放占位卡。"""
    p = ROOT / "footage.json"
    items = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    out = []
    for e in items:
        base = SRC[e["src"]] if e["src"] in SRC else CLIPS / e["src"]
        out.append(clip(e["sec"], e["name"], e["dur"], base, e["start"], e["note"], tag=e.get("tag", ""), speed=e.get("speed", 1.0), crop=e.get("crop"),
                        src=str(e["src"])))
    pending = {"S03": ("S03 实机①", 36.0), "S06": ("S06 实机②", 35.0), "S08": ("S08 实机③", 34.0)}
    for sec, (label, dur) in pending.items():
        if not any(x.sec == sec for x in out):
            out.append(gen(sec, "实机待填", dur, (lambda l=label, d=dur: vis.gen_placeholder(l, "footage.json 里还没有这一段", d)), "实机素材待选"))
    return out


def s10_segments() -> list[Seg]:
    """S10 这事比银魂大 47 秒：8 无职转生 + 5 别的动漫 + 14 出镜 + 6 强化学习短视频 + 7 官方课墙 + 7 出镜。"""
    segs = []
    wk = MAT.parent
    atlas = [wk / n / "角色图集" / "总览.png" for n in ("进击的巨人", "火影", "无职转生")]
    shots = sorted((wk / "无职转生" / "游戏" / "tools" / "_playtest").rglob("*.png"))
    segs.append(gen("S10", "无职转生截图", 8.0, lambda: vis.gen_screenshot_flash(shots, 8.0, "无职转生：一句话 → 4 小时 → 8 章（自动测试截图）"), "「我还做了很多动漫视频，《巨人》《火影》《无职转生》……」", src="无职转生/游戏/tools/_playtest"))
    segs.append(gen("S10", "别的动漫图集", 5.0, lambda: vis.gen_wall(atlas, 5.0, 3, 1, "巨人 / 火影 / 无职转生的角色图集：都能拿来复用"), "这些角色的素材都可以拿来复用", src="游戏素材/*/角色图集/总览.png"))
    segs.append(gen("S10", "出镜占位1", 14.0, lambda: vis.gen_placeholder("S10 这事比银魂大（出镜）", "游戏的门槛还剩什么？", 14.0), "出镜：门槛还剩什么，说清楚你想要什么"))
    rl = Path(r"D:\大疆\独立视频\短视频/2026-10_强化学习赌场闯关\强化学习赌场闯关_成片.mp4")
    segs.append(gen("S10", "强化学习短视频", 6.0, lambda: vis.gen_vertical_clip(rl, 8.0, 6.0, "一篇 7000 多词的长文 → 一分钟短视频"), "一篇文章换成视频", src="独立视频/短视频/2026-10_强化学习赌场闯关"))
    eps = sorted((ROOT / "素材").glob("ep*.png"))
    if len(eps) >= 10:
        segs.append(gen("S10", "官方课墙", 7.0, lambda: vis.gen_wall(eps, 7.0, 5, 2, "一门官方课 → 10 集短视频"), "一门课换成 10 集", src="Claude官方教程/短视频"))
    else:
        segs.append(gen("S10", "官方课墙待补", 7.0, lambda: vis.gen_placeholder("官方课墙", "素材/ep*.png 还没抽", 7.0), "待补"))
    segs.append(gen("S10", "出镜占位2", 7.0, lambda: vis.gen_placeholder("S10 这事比银魂大（出镜）", "不仅是游戏：文章、视频、课、漫画、小说", 7.0), "出镜：任何知识都能换一种媒介"))
    return segs


# ---------------------------------------------------------------- 渲染
def ffmpeg(*args, stdin=None):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True, stdin=stdin)


def render(seg: Seg):
    SEG.mkdir(exist_ok=True)
    seg.path = SEG / (seg.label() + ".mp4")
    if seg.kind == "clip":
        vf = ["setpts=PTS/%g" % seg.kw["speed"]] if seg.kw["speed"] != 1.0 else []
        if seg.kw.get("crop"):
            x0, y0, x1, y1 = seg.kw["crop"]                    # 占源画面的比例
            vf.append("crop=iw*%g:ih*%g:iw*%g:ih*%g" % (x1 - x0, y1 - y0, x0, y0))
        vf.append("scale=%d:%d:flags=neighbor" % (W, H))
        pre = ["-ss", "%.3f" % seg.kw["start"], "-t", "%.3f" % (seg.dur * seg.kw["speed"]), "-i", str(seg.kw["path"])]
        if seg.kw["tag"]:
            tp = SEG / (seg.label() + "_tag.png")
            tag_png(seg.kw["tag"], tp)
            ffmpeg(*pre, "-i", str(tp), "-filter_complex", "[0:v]%s[v];[v][1:v]overlay=0:0" % ",".join(vf), *X264, "-t", "%.3f" % seg.dur, str(seg.path))
            tp.unlink()
        else:
            ffmpeg(*pre, "-vf", ",".join(vf), *X264, "-t", "%.3f" % seg.dur, str(seg.path))
        return
    n, frame = seg.kw["fn"]()
    want = int(round(seg.dur * FPS))
    proc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                             "-r", str(FPS), "-i", "-", *X264, str(seg.path)], stdin=subprocess.PIPE)
    last = None
    for i in range(want):
        last = frame(min(i, n - 1)).convert("RGB")
        proc.stdin.write(last.tobytes())
    proc.stdin.close()
    proc.wait()


def write_table(T: list[Seg]):
    t = 0.0
    rows = ["# 无声版镜头表（v1）", "", "- 横屏 1920×1080、60 帧、没有声音；总长 %.0f 秒。" % sum(s.dur for s in T),
            "- “出镜占位”是留给你的露脸视频的位置；其余段落等音频到了按句子对时间再调。", "",
            "| 开始 | 时长 | 段 | 镜头 | 内容 | 素材 |", "|---|---|---|---|---|---|"]
    for s in T:
        rows.append("| %d:%04.1f | %.1f 秒 | %s | %s | %s | %s |" % (t // 60, t % 60, s.dur, s.sec, s.name, s.note, s.src or ""))
        t += s.dur
    (ROOT / "镜头表.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def join(T: list[Seg]):
    lst = SEG / "list.txt"
    lst.write_text("".join("file '%s'\n" % (SEG / (s.label() + ".mp4")).as_posix() for s in T), encoding="utf-8")
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-an", "-movflags", "+faststart", str(OUT))
    print("done:", OUT)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if os.environ.get("LOWPRIO"):                  # 录屏的时候渲：用最低优先级，只吃空闲的 CPU（子进程 ffmpeg 会继承）
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    T = timeline()
    write_table(T)
    if cmd == "list":
        t = 0.0
        for s in T:
            print("%3d:%04.1f  %5.1f s  %-4s %-16s %s" % (t // 60, t % 60, s.dur, s.sec, s.name, s.note))
            t += s.dur
        print("合计 %.0f 秒" % t)
        return
    if cmd == "render":
        only = sys.argv[2:]
        for s in T:
            if only and s.sec not in only:
                continue
            print("渲 %s (%.1f s)" % (s.label(), s.dur), flush=True)
            render(s)
    if cmd == "join" or (cmd == "render" and not sys.argv[2:]):
        join(T)


if __name__ == "__main__":
    main()
