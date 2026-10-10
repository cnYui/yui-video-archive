# -*- coding: utf-8 -*-
"""按时间轴给每一帧准备好画面素材：素材片段按 30 fps 抽成演示区大小（SW×SH = 1474×829，common.py 里定），宽高比对不上的放大铺满做模糊底、原片居中叠上。
输出 media/（scr/ 上框逐帧、scr2/ 双分镜下框逐帧、card/ 卡片用图、qr.png）和 frames.js。

  python prep_frames.py

素材在成片里按原速放，所以第 n 帧 = 这段素材里 in + (n − range.s×30)/30 秒；话比画面长而延长的段落，延长部分接着原片往下放，素材放完了就定格最后一帧。
range 里写 "crop": [x0, y0, x1, y1]（占整帧的比例）就先裁出这一块再放大（发布会幻灯片的价格表这类）；裁出来是 16:9 就直接铺满。
缩略图和卡片图的取帧时刻写在 ../../台本/plan.json 的 "thumbs" / "card_imgs" 里。
增量：media/scr/_manifest.json 记每段（场景 + 序号）上次抽帧用的 src / in / out / crop 和张数，参数没变就复用已抽的帧，只重抽变了的（改台本、改配音后时间轴会变，全抽一遍要 8 分钟）。
"""
import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

from common import EP, FPS, HERE, SH, SRC, SW

MEDIA = HERE / "media"


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + [str(a) for a in args], check=True)


def vf_for(w, h, crop=None, speed=1.0):
    """演示区 SW×SH：比例一致直接缩放；不一致放大铺满做模糊底，原片按比例缩进去居中。crop 先裁一块再算比例。"""
    pre = ""
    if crop:
        x0, y0, x1, y1 = crop
        pre = f"crop=iw*{x1 - x0:.5f}:ih*{y1 - y0:.5f}:iw*{x0:.5f}:ih*{y0:.5f},"
        w, h = w * (x1 - x0), h * (y1 - y0)
    sp = f"setpts=PTS/{speed:.4f}," if abs(speed - 1.0) > 1e-6 else ""          # 变速：先改时间戳再按 30 fps 取帧
    if abs(w / h - SW / SH) < 0.01:
        return f"{sp}fps={FPS},{pre}scale={SW}:{SH}:flags=lanczos"
    return (f"{sp}fps={FPS},{pre}split[a][b];[a]scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH},boxblur=36:6,eq=brightness=-0.10:saturation=0.9[bg];"
            f"[b]scale={SW}:{SH}:force_original_aspect_ratio=decrease:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")


def size_of(key):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(SRC[key])],
                       check=True, capture_output=True, text=True).stdout.strip().split(",")
    return int(o[0]), int(o[1])


def extract(T, stream, sizes):
    """一路画面：stream = "ranges"（上框 / 单框）→ media/scr/，"ranges2"（双分镜的下框）→ media/scr2/。返回每帧的图片名列表（没有画面的帧是 None）。"""
    sub = "scr" if stream == "ranges" else "scr2"
    d = MEDIA / sub
    d.mkdir(parents=True, exist_ok=True)
    mf_path = d / "_manifest.json"
    old_mf = json.loads(mf_path.read_text(encoding="utf-8")) if mf_path.exists() else {}
    sig_of = lambda r: [r["src"], round(r["in"], 3), round(r["out"], 3), r.get("crop"), bool(r.get("hold")), r.get("speed", 1.0)]

    jobs, keep = [], {}
    for cid, c in T["clips"].items():
        for i, r in enumerate(c.get(stream, [])):
            ok = old_mf.get(f"{cid}_{i}")
            if ok and ok["sig"] == sig_of(r) and len(list(d.glob(f"{cid}_{i}_*.jpg"))) == ok["n"]:
                keep[(cid, i)] = ok["n"]
            else:
                jobs.append((cid, i, r))
    wanted = {f"{cid}_{i}_" for cid, i in keep}
    for f in d.glob("*.jpg"):                              # 不再用的帧（场景改了、段数变了）清掉
        if not any(f.name.startswith(w) for w in wanted):
            f.unlink()

    def work(job):
        cid, i, r = job
        extra = 0.12
        if r.get("hold"):                                   # 定格：只取 in 那一刻的一帧，后面的帧编号都指向它
            ff(["-ss", f"{r['in']:.3f}", "-i", SRC[r["src"]], "-frames:v", "1", "-an", "-vf", vf_for(*sizes[r["src"]], crop=r.get("crop")),
                "-q:v", "3", "-start_number", "0", d / f"{cid}_{i}_%05d.jpg"])
        else:
            ff(["-ss", f"{r['in']:.3f}", "-i", SRC[r["src"]], "-t", f"{(r['out'] - r['in']) / r.get('speed', 1.0) + extra:.3f}", "-an", "-filter_threads", "1",   # -t 是输出时长：变速段按变速后的算
                "-vf", vf_for(*sizes[r["src"]], crop=r.get("crop"), speed=r.get("speed", 1.0)), "-q:v", "3", "-start_number", "0", d / f"{cid}_{i}_%05d.jpg"])
        return (cid, i), len(list(d.glob(f"{cid}_{i}_*.jpg")))

    with ThreadPoolExecutor(2) as ex:
        counts = dict(ex.map(work, jobs))
    counts.update(keep)
    sigs = {f"{cid}_{i}": sig_of(r) for cid, c in T["clips"].items() for i, r in enumerate(c.get(stream, []))}
    mf_path.write_text(json.dumps({k: {"sig": sigs[k], "n": counts[(k.rsplit("_", 1)[0], int(k.rsplit("_", 1)[1]))]} for k in sigs}, ensure_ascii=False), encoding="utf-8")

    scr = [None] * T["frames"]
    seg_e = {s["id"]: s["e"] for s in T["segs"]}
    for cid, c in T["clips"].items():
        rs = c.get(stream, [])
        if not rs:
            continue
        end_n = min(T["frames"], int(round(seg_e[cid] * FPS)))
        for i, r in enumerate(rs):
            a = int(round(r["s"] * FPS))
            b = int(round(r["e"] * FPS)) if i + 1 < len(rs) else end_n      # 最后一段铺到场景结束（定格）
            for n in range(a, min(b, end_n, T["frames"])):
                j = min(counts[(cid, i)] - 1, n - a)
                scr[n] = f"{sub}/{cid}_{i}_{j:05d}.jpg"
        # 场景第一段前面如果因为取整空了一帧，用第一段的第一帧补
        a0 = int(round(rs[0]["s"] * FPS))
        if a0 > 0 and scr[a0 - 1] is None and a0 - 1 >= int(round(c["s"] * FPS)):
            scr[a0 - 1] = f"{sub}/{cid}_0_00000.jpg"
    print(f"{sub}：重抽 {len(jobs)} 段，复用 {len(keep)} 段；" + "，".join(f"{k[0]}#{k[1]} {v} 张" for k, v in counts.items()))
    return scr


def main():
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    plan = json.loads((EP / "台本" / "plan.json").read_text(encoding="utf-8"))
    sizes = {k: size_of(k) for k in SRC}
    scr = extract(T, "ranges", sizes)
    scr2 = extract(T, "ranges2", sizes) if T.get("layout") == "dual" else []
    (HERE / "frames.js").write_text("window.FR = " + json.dumps({"scr": scr, "scr2": scr2}, separators=(",", ":")) + ";\n", encoding="utf-8")

    # 左栏缩略图（352×198，页面里显示 176×99）、卡片用图
    (MEDIA / "thumb").mkdir(exist_ok=True)
    (MEDIA / "card").mkdir(exist_ok=True)
    for name, spec in (plan.get("thumbs") or {}).items():
        ff(["-ss", f"{spec['t']:.3f}", "-i", SRC[spec["src"]], "-frames:v", "1", "-vf", "scale=352:198:force_original_aspect_ratio=increase,crop=352:198", "-q:v", "2", MEDIA / "thumb" / f"{name}.jpg"])
    for name, spec in (plan.get("card_imgs") or {}).items():
        ff(["-ss", f"{spec['t']:.3f}", "-i", SRC[spec["src"]], "-frames:v", "1", "-vf", f"scale={spec.get('w', 1100)}:-2:flags=lanczos", "-q:v", "2", MEDIA / "card" / f"{name}.jpg"])
    if plan.get("qr"):                                       # 片尾卡片的二维码：plan.json 里写 "qr": "素材/xxx_qr.png"（相对本期目录；用 OpenCV QRCodeEncoder 生成并解码核对）
        shutil.copy(EP / plan["qr"], MEDIA / "qr.png")
    print(f"frames.js 共 {T['frames']} 帧：上框 {sum(1 for x in scr if x)} 帧有素材画面" + (f"，下框 {sum(1 for x in scr2 if x)} 帧" if scr2 else ""))


if __name__ == "__main__":
    main()
