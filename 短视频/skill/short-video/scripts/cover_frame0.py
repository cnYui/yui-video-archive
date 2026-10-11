# -*- coding: utf-8 -*-
r"""把选定的封面放进成片的第 0 帧（各平台的默认封面 / 预览都取第一帧）。

用户 2026-10-04：“小红书和视频号第一帧换成封面，之后生成的视频统一第一帧为封面，这样就覆盖了”（当时主要为视频号做：它的上传封面 input 在 shadow 里，插件够不着，封面只能从视频帧里选）。2026-10-06 视频号移出发布流程，**“之后的视频统一第一帧为封面”这条规则不变**，本脚本照常用。

  python cover_frame0.py <本条目录>                 成片 = <本条>\<slug>_成片.mp4（slug 取 台本\录制稿.json），封面 = 制作\04_封面\封面_选定_3x4.png；原地替换，原片留成 <slug>_成片_无封面帧.mp4
  python cover_frame0.py <本条目录> --video X.mp4 --cover Y.png [--out Z.mp4]      指定文件（--out 不写就原地替换并留备份）
  python cover_frame0.py <本条目录> --check         只看现在成片的第 0 帧像不像选定的封面
  python cover_frame0.py <本条目录> --full          整条重编码（拼接校验不过时的备用做法；会有一代画质损失，crf 14）
  python cover_frame0.py <本条目录> --pts-tol 0.002  每帧 pts 的容差（秒，默认 2 ms）：render_all.py 拼 4 路 part 的成片 pts 有亚毫秒抖动，
                                                   2026-10-05《人人都是UI设计师》竖屏版因此在旧的 1e-6 容差下“拼接”“整条”两种做法都校验不过

横版成片（宽 > 高，例如长视频 2340×1080）自动改用 封面_选定_16x9.png：封面放正中间、左右用它自己模糊铺满（2026-10-05 加，《不再Review》长视频第一次用）。
做法（成片是 1080×2340 的竖屏，封面是 3:4 的 1080×1440）：
  · 第 0 帧 = 封面放在画面正中间（y 450–1890），上下两条用封面自己铺满再重度模糊填满——各平台默认封面取第 0 帧的 3:4 居中裁切，就正好是选定的封面（小红书默认封面就是这样；B 站 / 抖音仍各自上传封面图）。
  · 视频长度、帧数、音画同步都不变：只是把第 0 帧换掉（33 ms，播放时看不出）。
  · 画质：只重编码第一个 GOP（到第二个关键帧，约 8 秒）并且第 0 帧用 crf 6 编码，其余帧**直接拷贝**（逐像素和原片一致），原声直接拷贝；
    重编码用和原片一样的参数（读原片 x264 SEI 里的 crf / keyint，像素格式照原片）。做完逐项校验：帧数 / 每一帧 pts 一致、第 0 帧像封面、拷贝段逐像素一致、原声 md5 一致，解码无报错；校验不过就不替换。
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, check=True, **kw)


def probe(video):
    j = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=codec_name,width,height,r_frame_rate,pix_fmt,color_range,nb_frames,time_base:format=duration", "-of", "json", str(video)]).stdout)
    s = j["streams"][0]
    num, den = (int(x) for x in s["r_frame_rate"].split("/"))
    info = dict(codec=s["codec_name"], w=s["width"], h=s["height"], fps=num / den, fps_expr=s["r_frame_rate"], pix_fmt=s["pix_fmt"], tb_den=int(s.get("time_base", "1/15360").split("/")[1]),
                nb=int(s.get("nb_frames") or 0), duration=float(j["format"]["duration"]))
    rows = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-skip_frame", "nokey", "-show_entries", "frame=pts_time", "-of", "csv=p=0", str(video)]).stdout.decode().split()
    info["keys"] = [float(x.split(",")[0]) for x in rows if x]
    info["has_audio"] = bool(run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_name", "-of", "csv=p=0", str(video)]).stdout.strip())
    return info


def x264_params(video):
    """读原片 x264 SEI 里的 crf / keyint（没有就用 16 / 250）。"""
    head = open(video, "rb").read(2_000_000)
    i = head.find(b"x264 - core")
    sei = head[i:i + 1500].decode("latin1") if i >= 0 else ""
    crf = re.search(r"crf=([\d.]+)", sei)
    kmax = re.search(r"keyint=(\d+)", sei)
    kmin = re.search(r"keyint_min=(\d+)", sei)
    return float(crf.group(1)) if crf else 16.0, int(kmax.group(1)) if kmax else 250, int(kmin.group(1)) if kmin else 25


def compose(cover_png, w, h):
    """第 0 帧：封面（3:4）放正中间，上下用封面铺满再模糊填满。"""
    cov = Image.open(cover_png).convert("RGB")
    if w > h:                                   # 横版成片（长视频 2340×1080）：16:9 的封面放正中间（x 方向居中），左右两条用封面自己铺满再模糊填满（2026-10-05 《不再Review》长视频加）
        cw = round(h * 16 / 9)
        if cov.size != (cw, h):
            cov = cov.resize((cw, h), Image.LANCZOS)
        s = max(w / cov.width, h / cov.height)
        bg = cov.resize((round(cov.width * s), round(cov.height * s)), Image.LANCZOS)
        x0, y0 = (bg.width - w) // 2, (bg.height - h) // 2
        bg = bg.crop((x0, y0, x0 + w, y0 + h)).filter(ImageFilter.GaussianBlur(48))
        left = (w - cw) // 2
        bg.paste(cov, (left, 0))
        return bg, (left, left + cw)
    ch = round(w * 4 / 3)
    if cov.size != (w, ch):
        cov = cov.resize((w, ch), Image.LANCZOS)
    s = max(w / cov.width, h / cov.height)
    bg = cov.resize((round(cov.width * s), round(cov.height * s)), Image.LANCZOS)
    x0, y0 = (bg.width - w) // 2, (bg.height - h) // 2
    bg = bg.crop((x0, y0, x0 + w, y0 + h)).filter(ImageFilter.GaussianBlur(48))
    top = (h - ch) // 2
    bg.paste(cov, (0, top))
    return bg, (top, top + ch)


def frame_rgb(video, n, w, h):
    r = run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"select=eq(n\\,{n})", "-vframes", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]).stdout
    if len(r) != h * w * 3:             # 解码器到不了的帧（长视频原片的最后一帧 ffprobe 数得到、ffmpeg select 取不到，原片也一样）
        return None
    return np.frombuffer(r, np.uint8).reshape(h, w, 3)


def psnr(a, b):
    m = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    return float("inf") if m == 0 else 10 * np.log10(255 ** 2 / m)


def pts_list(video):
    rows = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "frame=pts_time", "-of", "csv=p=0", str(video)]).stdout.decode().split()
    return sorted(float(x.split(",")[0]) for x in rows if x)


def audio_md5(video):
    return hashlib.md5(run(["ffmpeg", "-v", "error", "-i", str(video), "-map", "0:a:0", "-c", "copy", "-f", "adts", "-"]).stdout).hexdigest()


def ref_420(png, pix_fmt, w, h):
    """封面只做一次 4:2:0 二次采样后的样子（视频里的第 0 帧最好也只比它差一点点编码损失）。"""
    r = run(["ffmpeg", "-v", "error", "-i", str(png), "-vf", f"format={pix_fmt},format=rgb24", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]).stdout
    return np.frombuffer(r, np.uint8).reshape(h, w, 3)


def verify(new, src, frame0, info, kidx):
    w, h = info["w"], info["h"]
    notes, ok = [], True
    pn, ps = pts_list(new), pts_list(src)
    # pts 容差 2 ms（--pts-tol 改）：render_all.py 把 4 路渲染的 part 拼起来，原片的 pts 有亚毫秒抖动（1998 帧里最多差 0.98 ms，
    # 例：人人都是UI设计师竖屏版），而重编码出来的是整齐的 1/30 s；2 ms 比一帧（33 ms）小得多，不影响音画同步。以前写死 1e-6，这种成片永远校验不过。
    same = len(pn) == len(ps) and all(abs(a - b) < PTS_TOL for a, b in zip(pn, ps))
    notes.append(f"帧数 {len(pn)} / 原片 {len(ps)}，每一帧 pts {'一致' if same else '不一致'}（容差 {PTS_TOL * 1000:g} ms，最大差 {max((abs(a - b) for a, b in zip(pn, ps)), default=0) * 1000:.2f} ms）")
    ok &= same
    f0 = frame_rgb(new, 0, w, h)
    q0 = psnr(f0, ref_420(frame0, info["pix_fmt"], w, h))
    notes.append(f"第 0 帧 vs 封面（只做 4:2:0 的参考）{q0:.1f} dB")
    ok &= q0 >= 40
    if kidx is not None:
        for n in sorted({kidx, (kidx + len(ps) - 1) // 2, len(ps) - 1}):
            fa, fb = frame_rgb(new, n, w, h), frame_rgb(src, n, w, h)
            if fa is None and fb is None:
                notes.append(f"拷贝段第 {n} 帧两边都取不到（解码器到不了这一帧），跳过")
                continue
            eq = fa is not None and fb is not None and np.array_equal(fa, fb)
            notes.append(f"拷贝段第 {n} 帧和原片{'逐像素一致' if eq else '不一致'}")
            ok &= eq
        q = psnr(frame_rgb(new, 1, w, h), frame_rgb(src, 1, w, h))
        notes.append(f"重编码段第 1 帧 vs 原片 {q:.1f} dB")
        ok &= q >= 38
    if info["has_audio"]:
        am = audio_md5(new) == audio_md5(src)
        notes.append(f"原声流 md5 {'一致' if am else '不一致'}")
        ok &= am
    dec = subprocess.run(["ffmpeg", "-v", "error", "-i", str(new), "-f", "null", "-"], capture_output=True)
    notes.append("解码无报错" if not dec.stderr.strip() else f"解码报错：{dec.stderr.decode(errors='ignore')[:200]}")
    ok &= not dec.stderr.strip()
    return ok, notes


def splice(src, frame0, out, info, tmp):
    crf, kmax, kmin = x264_params(src)
    fps, pf = info["fps_expr"], info["pix_fmt"]
    keys = info["keys"]
    kt = keys[1] if len(keys) > 1 else None
    # 第二个关键帧是第几帧：按 pts 排序后的下标算，不能用 pts × fps（成片的第一帧 pts 不是 0 时——例如 add_to_video 拼出来的长视频第一帧 pts = 0.021 s——会多算一帧，
    # 拼出来多一帧、时间戳错乱：2026-10-05《不再Review》长视频第一次用就踩到）
    if kt is not None:
        ps = pts_list(src)
        kidx = min(range(len(ps)), key=lambda i: abs(ps[i] - kt))
    else:
        kidx = None
    n = kidx if kidx is not None else (info["nb"] or round(info["duration"] * info["fps"]))
    head = tmp / "head.mp4"
    flt = (f"[1:v]trim=end_frame=1,setpts=PTS-STARTPTS,format={pf},setsar=1[c];"
           f"[0:v]trim=start_frame=1:end_frame={n},setpts=PTS-STARTPTS,format={pf},setsar=1[v];[c][v]concat=n=2:v=1:a=0[out]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-loop", "1", "-framerate", fps, "-t", "0.2", "-i", str(frame0), "-filter_complex", flt, "-map", "[out]",
         "-c:v", "libx264", "-preset", "medium", "-crf", f"{crf:g}", "-pix_fmt", pf, "-r", fps, "-video_track_timescale", str(info["tb_den"]),
         "-x264-params", f"keyint={kmax}:min-keyint={kmin}:zones=0,0,crf=6", "-an", str(head)])
    parts = [head]
    if kidx is not None:
        tail = tmp / "tail.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{kt + 0.001:.4f}", "-i", str(src), "-map", "0:v:0", "-c", "copy", "-avoid_negative_ts", "make_zero", str(tail)])
        parts.append(tail)
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    joined = tmp / "joined.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(joined)]
    if info["has_audio"]:
        cmd += ["-i", str(src), "-map", "0:v:0", "-map", "1:a:0"]
    cmd += ["-c", "copy", "-movflags", "+faststart", str(out)]
    run(cmd)
    return kidx


def full_reencode(src, frame0, out, info):
    crf, kmax, kmin = x264_params(src)
    fps, pf = info["fps_expr"], info["pix_fmt"]
    flt = (f"[1:v]trim=end_frame=1,setpts=PTS-STARTPTS,format={pf},setsar=1[c];"
           f"[0:v]trim=start_frame=1,setpts=PTS-STARTPTS,format={pf},setsar=1[v];[c][v]concat=n=2:v=1:a=0[out]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(src), "-loop", "1", "-framerate", fps, "-t", "0.2", "-i", str(frame0), "-filter_complex", flt, "-map", "[out]"]
    if info["has_audio"]:
        cmd += ["-map", "0:a:0", "-c:a", "copy"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", pf, "-r", fps, "-x264-params", f"keyint={kmax}:min-keyint={kmin}:zones=0,0,crf=6",
            "-movflags", "+faststart", str(out)]
    run(cmd)


def frame_at(video, t, w, h):
    r = run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-vframes", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]).stdout
    return np.frombuffer(r, np.uint8).reshape(h, w, 3) if len(r) == h * w * 3 else None


def backup_is_stale(video, backup):
    """备份（_无封面帧）是不是上一版成片的原片？第一个 GOP 之后是“拷贝段”，和原片应逐像素一致：取几个时刻比，不一致（或尺寸不同）= 成片后来被重渲过、备份过期。
    视频短到没有第一个 GOP 之后的帧时判断不了，当没过期（保持原来的行为）。"""
    try:
        vi = probe(video)
        bi = probe(backup)
    except Exception:
        return False
    if (vi["w"], vi["h"]) != (bi["w"], bi["h"]) or abs(vi["duration"] - bi["duration"]) > 0.5:
        return True
    keys = vi["keys"]
    t_min = (keys[1] + 0.5) if len(keys) > 1 else 0.0              # 第二个关键帧之后才是拷贝段
    d = vi["duration"]
    times = sorted({t for t in (d * 0.5, d * 0.9, d - 1.0) if t > t_min and t < d - 0.1})
    for t in times:
        a, b = frame_at(video, t, vi["w"], vi["h"]), frame_at(backup, t, vi["w"], vi["h"])
        if a is None or b is None or not np.array_equal(a, b):
            return True
    return False


PTS_TOL = 0.002       # 秒；main() 里 --pts-tol 可以改


def main():
    global PTS_TOL
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    ep = Path(args[0])
    if "--pts-tol" in args:
        PTS_TOL = float(args[args.index("--pts-tol") + 1])

    def opt(name):
        return Path(args[args.index(name) + 1]) if name in args else None
    cdir = ep / "制作" / "04_封面"
    cover = opt("--cover")             # 不写：竖屏成片用 封面_选定_3x4.png，横版成片用 封面_选定_16x9.png（下面按成片方向定）
    video = opt("--video")
    if video is None:
        slug = json.loads((ep / "台本" / "录制稿.json").read_text(encoding="utf-8"))["slug"]
        video = ep / f"{slug}_成片.mp4"
    out = opt("--out")
    backup = video.with_name(video.stem + "_无封面帧.mp4")
    src = backup if (out is None and backup.is_file()) else video          # 已经做过一次：从备份（原片）重新做，不在已替换的片子上叠
    if src == backup and video.is_file() and "--check" not in args and backup_is_stale(video, backup):
        # 2026-10-06《Claude官方教程》第 1 期出镜版：改了顶上的字重渲、finish 出了新成片，但 _无封面帧 还是上一版——照旧从备份重做会把旧标题的版本又放回去。
        print("⚠ _无封面帧 备份和现在的成片内容不一样（成片后来重渲 / 重新 finish 过）：用现在的成片重建备份，再放封面")
        shutil.copy2(video, backup)
    info = probe(src)
    if cover is None:
        cover = cdir / ("封面_选定_16x9.png" if info["w"] > info["h"] else "封面_选定_3x4.png")
    if not cover.is_file():
        sys.exit(f"没找到选定的封面：{cover}（先 make_candidates.py --select X）")
    src_mb = src.stat().st_size / 1e6
    frame0, band = compose(cover, info["w"], info["h"])
    if "--check" in args:
        f0 = frame_rgb(video, 0, info["w"], info["h"])
        tmp_png = ep / "_frame0_check.png"
        frame0.save(tmp_png)
        q = psnr(f0, ref_420(tmp_png, info["pix_fmt"], info["w"], info["h"]))
        tmp_png.unlink()
        print(f"{video.name} 第 0 帧 vs 选定封面：{q:.1f} dB —— {'是封面帧' if q >= 40 else '不是封面帧'}")
        return
    tmp = ep / "_cover_frame0_tmp"
    tmp.mkdir(exist_ok=True)
    frame0_png = tmp / "frame0.png"
    frame0.save(frame0_png)
    new = tmp / "new.mp4"
    mode, kidx = "拼接（只重编码第一个 GOP，其余拷贝）", None
    def check_full():
        """整条重编码没有拷贝段：校验帧数 / pts、第 0 帧像封面、原声 md5、解码无报错。"""
        full_reencode(src, frame0_png, new, info)
        ok_, notes_ = verify(new, src, frame0_png, info, None)
        return ok_, notes_

    if "--full" in args or info["codec"] != "h264":
        mode = "整条重编码（crf 14）"
        ok, notes = check_full()
    else:
        kidx = splice(src, frame0_png, new, info, tmp)
        ok, notes = verify(new, src, frame0_png, info, kidx)
        if not ok:
            print("拼接校验没过：\n  " + "\n  ".join(notes) + "\n改用整条重编码……")
            mode = "整条重编码（拼接校验没过）"
            ok, notes = check_full()
    print(f"做法：{mode}")
    print("校验：\n  " + "\n  ".join(notes))
    if not ok:
        sys.exit(f"校验没过，没有替换任何文件；中间文件在 {tmp}")
    if out is None:
        if not backup.is_file():
            shutil.copy2(video, backup)
        shutil.move(str(new), str(video))
        target = video
        print(f"已替换：{video}（原片留在 {backup.name}）")
    else:
        shutil.move(str(new), str(out))
        target = out
        print(f"已写到：{out}")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"{target.name}：{info['w']}×{info['h']}，{target.stat().st_size / 1e6:.1f} MB（原片 {src_mb:.1f} MB）")
    if info["w"] > info["h"]:
        print(f"横版成片：第 0 帧 = 16:9 封面在画面正中（x {band[0]}–{band[1]}），左右是它的模糊延伸；各平台照常上传封面图。")
    else:
        print(f"竖屏成片：第 0 帧 = 3:4 封面在画面 y {band[0]}–{band[1]}（居中），小红书默认封面就是它的居中裁切；各平台照常上传封面图。")


if __name__ == "__main__":
    main()
