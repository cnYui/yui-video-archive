# AI每日日报宽屏版（2340x1080）：从《原LAI如此》scripts/assemble.py 复制。改动：片头片尾补边到 2340 宽、正片用 render_parallel_wide。原文件不动。
"""Render intro + main + outro at 30 fps, join them, mux the final mix, write the SRT and chapter list.

  python assemble.py <episode_dir> [--workers 4] [--skip-main] [--no-sync] [--series D:/大疆/AI科普]

Needs: 制作/timeline.json with `mouth` and 制作/build/mix.wav (run mix_audio.py first), the engine in
制作/engine/, and episode.json outro_items + outro_closing (the credits must be asked from the user —
empty values stop the script).
Steps
  1. intro / outro rendered from SERIES/片头片尾/intro|outro/index.html at 30 fps; data written to
     制作/build/intro_data.json ({name: 悠一, tagline: episode.intro_tagline}) and outro_data.json
     ({items: outro_items, closing: outro_closing, signature: 悠一}); re-encoded to the common x264 settings
  2. python 制作/engine/sync_assets.py --series SERIES (skip with --no-sync), then render_parallel.py -> 制作/build/main.mp4
     (--skip-main reuses an existing main.mp4)
  3. concat -> build/video.mp4, mux build/mix.wav (AAC 192k) ->
     <episode_dir>/<dir_name>_成片.mp4, <dir_name>_字幕.srt, <dir_name>_章节.txt
Checks (the script stops instead of writing a short / broken video): render_parallel exit code (1 = frames
missing after retries, 2 = page errors), main.mp4 frame count = round(main_duration * 30) (also catches a
stale main.mp4 with --skip-main), joined video and final file within 0.1 s of total_duration.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(r"D:/大疆/AI科普/skill/yuanlai-ruci-episode/scripts")))   # epcommon 只读引用
import epcommon as C  # noqa: E402

FPS = 30
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-g", "60",
       "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
       "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709"]


def run(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd)[:200], flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(tl, path):
    rows, i = [], 1
    for s in tl["segments"]:
        for ln in s["lines"]:
            a, b = tl["intro"] + ln["start"], tl["intro"] + ln["end"]
            rows.append(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{ln['text']}\n")
            i += 1
    path.write_text("\n".join(rows), encoding="utf-8")


def count_frames(path):
    """video frames in a file (0 if missing/unreadable)"""
    if not Path(path).exists():
        return 0
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return int(r.stdout.strip().split(",")[0])
    except ValueError:
        return 0


def reencode(src, dst):
    """Normalise a clip to the common encoding (30 fps, same x264 settings) so parts concat cleanly."""
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-r", FPS, *ENC, "-an", dst])


# AI每日日报：UE 片头片尾按原样 1920x1080 渲染，两边各补 210 px 到 2340x1080。补的部分取每一帧最边上 8 px 拉宽再模糊，
# 所以片头从纸白变成深色时，两边跟着变，不会露出色块。
WIDE, PAD = 2340, 210
WIDEN_VF = (f"[0:v]split=3[m][l][r];[l]crop=8:1080:0:0,scale={PAD}:1080,boxblur=12:2[lp];"
            f"[r]crop=8:1080:1912:0,scale={PAD}:1080,boxblur=12:2[rp];"
            f"[m]pad={WIDE}:1080:{PAD}:0[pd];[pd][lp]overlay=0:0[t];[t][rp]overlay={WIDE - PAD}:0,format=yuv420p")


def reencode_wide(src, dst):
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", WIDEN_VF, "-r", FPS, *ENC, "-an", dst])


def pack_data(p, name, ep):
    base = C.load_json(p.pack / name / "data.json", {}) or {}
    if name == "intro":
        base.update(name=base.get("name", "悠一"), tagline=ep.get("intro_tagline", "") or "")   # 兜底值 2026-09-29 起是悠一
    else:
        base.update(items=ep["outro_items"], closing=ep["outro_closing"], signature=base.get("signature", "悠一"))
    return base


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_common(ap)
    ap.add_argument("--workers", type=int, default=4, help="正片并行渲染进程数（默认 4；2026-09-28 用户定：所有渲染统一 4 路并行）")
    ap.add_argument("--skip-main", action="store_true", help="复用已有的 制作/build/main.mp4，不重新渲染正片")
    ap.add_argument("--no-sync", action="store_true", help="不先运行 制作/engine/sync_assets.py")
    args = ap.parse_args()
    p = C.Paths(args.episode_dir, args.series)
    ep = C.load_episode(p)
    items = [it for it in ep.get("outro_items") or [] if (it.get("label") or it.get("value"))]
    if not items or not (ep.get("outro_closing") or "").strip():
        sys.exit("episode.json 的 outro_items / outro_closing 为空：片尾制作清单和感谢语要先问用户，"
                 "不许用默认值。问完填进 episode.json 再运行。")
    tl = C.load_json(p.timeline)
    if tl is None:
        sys.exit(f"缺少 {p.timeline}：先 build_timeline.py、mix_audio.py")
    if not tl.get("mouth"):
        sys.exit("timeline.json 里没有 mouth：先运行 mix_audio.py")
    if not (p.build / "mix.wav").exists():
        sys.exit(f"缺少 {p.build / 'mix.wav'}：先运行 mix_audio.py")
    if not (p.engine / "index.html").exists():
        sys.exit(f"缺少 {p.engine / 'index.html'}：引擎没有复制（new_episode.py --update-engine）")
    intro_len, outro_len = C.pack_durations(p)
    if abs(intro_len - tl["intro"]) > 0.01 or abs(outro_len - tl["outro"]) > 0.01:
        sys.exit(f"片头片尾时长变了（{intro_len}/{outro_len}，时间轴里是 {tl['intro']}/{tl['outro']}）："
                 "重跑 build_timeline.py 和 mix_audio.py")
    p.build.mkdir(parents=True, exist_ok=True)
    render_py = C.SCRIPTS / "render.py"

    for name in ("intro", "outro"):
        data_path = p.build / f"{name}_data.json"
        C.write_json(data_path, pack_data(p, name, ep), indent=2)
        out = p.build / f"{name}_raw.mp4"
        run([sys.executable, render_py, p.pack / name / "index.html", "--data", data_path, "--fps", FPS, "-o", out])
        reencode_wide(out, p.build / f"{name}.mp4")

    if not args.skip_main:
        sync = p.engine / "sync_assets.py"
        if sync.exists() and not args.no_sync:
            try:
                run([sys.executable, sync, "--series", p.series], cwd=str(p.prod))
            except subprocess.CalledProcessError:
                sys.exit("sync_assets.py 没通过（缺素材，见上面的说明），没有渲染。讲解员的帧还没画完、只出草稿时：先手动运行 "
                         f"python {sync.as_posix()} --series {p.series.as_posix()} --frames <已有的帧目录> --allow-missing，"
                         "再 assemble.py --no-sync")
        r = subprocess.run([str(c) for c in [sys.executable, HERE / "render_parallel_wide.py", p.engine / "index.html",
                                             "--data", p.timeline, "--fps", FPS, "--workers", args.workers,
                                             "-o", p.build / "main.mp4"]])
        if r.returncode == 2:
            sys.exit("正片渲染时页面报错（JS 异常 / console.error / 字体加载失败，见上面的 PAGE ERRORS）："
                     "先修 scenes.js 或素材（用 render.py --stills 复现），再重跑 assemble.py")
        if r.returncode != 0:
            sys.exit(f"正片渲染失败（render_parallel.py 退出码 {r.returncode}）：见上面的 FAILED 行，重跑 assemble.py")
    elif not (p.build / "main.mp4").exists():
        sys.exit("--skip-main 但 制作/build/main.mp4 不存在")
    main_frames = count_frames(p.build / "main.mp4")
    want_frames = round(tl["main_duration"] * FPS)
    if main_frames != want_frames:
        sys.exit(f"制作/build/main.mp4 有 {main_frames} 帧，时间轴要 {want_frames} 帧（main_duration {tl['main_duration']}s）："
                 + ("上次渲染不完整，或时间轴在那之后变了，不能用 --skip-main；" if args.skip_main else "")
                 + "重新运行 assemble.py（不加 --skip-main）")

    lst = p.build / "concat.txt"
    lst.write_text("".join(f"file '{(p.build / n).as_posix()}'\n" for n in ("intro.mp4", "main.mp4", "outro.mp4")),
                   encoding="utf-8")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", p.build / "video.mp4"])
    vf = {n: count_frames(p.build / f"{n}.mp4") for n in ("intro", "main", "outro", "video")}
    if abs(vf["video"] / FPS - tl["total_duration"]) > 0.1:
        sys.exit(f"拼接后的画面 {vf['video']} 帧 = {vf['video'] / FPS:.2f}s，时间轴 total_duration 是 {tl['total_duration']}s"
                 f"（片头 {vf['intro']} / 正片 {vf['main']} / 片尾 {vf['outro']} 帧）：没有生成成片，先查哪一段帧数不对")

    name = p.dir_name(ep)
    final = p.ep / f"{name}_成片.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", p.build / "video.mp4", "-i", p.build / "mix.wav",
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-shortest", "-movflags", "+faststart", final])

    write_srt(tl, p.ep / f"{name}_字幕.srt")
    shutil.copy2(p.prod / "chapters_bilibili.txt", p.ep / f"{name}_章节.txt")
    probe = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                     "format=duration:stream=codec_name,width,height,r_frame_rate",
                                     "-of", "compact", str(final)]).decode()
    print(probe)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", str(final)]).decode().strip() or 0)
    print(f"duration {dur:.3f}s, expected total {tl['total_duration']}s")
    print(f"-> {final}\n-> {p.ep / (name + '_字幕.srt')}\n-> {p.ep / (name + '_章节.txt')}")
    if abs(dur - tl["total_duration"]) > 0.1:
        sys.exit(f"成片时长 {dur:.3f}s 和时间轴 total_duration {tl['total_duration']}s 相差超过 0.1 s：不要交付，"
                 "检查 build/ 里 intro / main / outro 各段的帧数")


if __name__ == "__main__":
    main()
