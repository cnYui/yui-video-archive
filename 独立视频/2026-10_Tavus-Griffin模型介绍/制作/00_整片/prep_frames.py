# -*- coding: utf-8 -*-
"""按时间轴给每一帧准备好画面素材：素材片段按 30 fps 抽成演示区大小（SW×SH = 1474×829，common.py 里定），宽高比对不上的放大铺满做模糊底、原片居中叠上。
输出 media/（scr/ 逐帧、thumb/ 左栏缩略图、card/ 卡片用图、qr.png）和 frames.js。

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

from common import EP, FPS, HERE, SH, SRC, SRC_CROP, SW

MEDIA = HERE / "media"


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + [str(a) for a in args], check=True)


def vf_for(w, h, crop=None):
    """演示区 SW×SH：比例一致直接缩放；不一致放大铺满做模糊底，原片按比例缩进去居中。crop 先裁一块再算比例。"""
    pre = ""
    if crop:
        x0, y0, x1, y1 = crop
        pre = f"crop=iw*{x1 - x0:.5f}:ih*{y1 - y0:.5f}:iw*{x0:.5f}:ih*{y0:.5f},"
        w, h = w * (x1 - x0), h * (y1 - y0)
    if abs(w / h - SW / SH) < 0.01:
        return f"fps={FPS},{pre}scale={SW}:{SH}:flags=lanczos"
    return (f"fps={FPS},{pre}split[a][b];[a]scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH},boxblur=36:6,eq=brightness=-0.10:saturation=0.9[bg];"
            f"[b]scale={SW}:{SH}:force_original_aspect_ratio=decrease:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")


def size_of(key):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(SRC[key])],
                       check=True, capture_output=True, text=True).stdout.strip().split(",")
    return int(o[0]), int(o[1])


def main():
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    plan = json.loads((EP / "台本" / "plan.json").read_text(encoding="utf-8"))
    d = MEDIA / "scr"
    d.mkdir(parents=True, exist_ok=True)
    sizes = {k: size_of(k) for k in SRC}
    mf_path = d / "_manifest.json"
    old_mf = json.loads(mf_path.read_text(encoding="utf-8")) if mf_path.exists() else {}

    jobs, keep = [], {}
    for cid, c in T["clips"].items():
        for i, r in enumerate(c["ranges"]):
            sig = [r["src"], round(r["in"], 3), round(r["out"], 3), r.get("crop")]
            ok = old_mf.get(f"{cid}_{i}")
            if ok and ok["sig"] == sig and len(list(d.glob(f"{cid}_{i}_*.jpg"))) == ok["n"]:
                keep[(cid, i)] = ok["n"]
            else:
                jobs.append((cid, i, r, sig))
    wanted = {f"{cid}_{i}_" for cid, i in keep}
    for f in d.glob("*.jpg"):                              # 不再用的帧（场景改了、段数变了）清掉
        if not any(f.name.startswith(w) for w in wanted):
            f.unlink()

    def work(job):
        cid, i, r, sig = job
        extra = 0.12
        ff(["-ss", f"{r['in']:.3f}", "-i", SRC[r["src"]], "-t", f"{r['out'] - r['in'] + extra:.3f}", "-an", "-filter_threads", "1",
            "-vf", vf_for(*sizes[r["src"]], crop=r.get("crop")), "-q:v", "3", "-start_number", "0", d / f"{cid}_{i}_%05d.jpg"])
        return (cid, i), len(list(d.glob(f"{cid}_{i}_*.jpg")))

    with ThreadPoolExecutor(2) as ex:
        counts = dict(ex.map(work, jobs))
    counts.update(keep)
    sigs = {f"{cid}_{i}": [r["src"], round(r["in"], 3), round(r["out"], 3), r.get("crop")] for cid, c in T["clips"].items() for i, r in enumerate(c["ranges"])}
    mf_path.write_text(json.dumps({k: {"sig": sigs[k], "n": counts[tuple([k.rsplit("_", 1)[0], int(k.rsplit("_", 1)[1])])]} for k in sigs}, ensure_ascii=False), encoding="utf-8")
    print(f"重抽 {len(jobs)} 段，复用 {len(keep)} 段")

    scr = [None] * T["frames"]
    seg_e = {s["id"]: s["e"] for s in T["segs"]}
    for cid, c in T["clips"].items():
        if not c["ranges"]:
            continue
        end_n = min(T["frames"], int(round(seg_e[cid] * FPS)))
        for i, r in enumerate(c["ranges"]):
            a = int(round(r["s"] * FPS))
            b = int(round(r["e"] * FPS)) if i + 1 < len(c["ranges"]) else end_n      # 最后一段铺到场景结束（定格）
            for n in range(a, min(b, T["frames"])):
                j = min(counts[(cid, i)] - 1, n - a)
                scr[n] = f"scr/{cid}_{i}_{j:05d}.jpg"
        # 场景第一段前面如果因为取整空了一帧，用第一段的第一帧补
        a0 = int(round(c["ranges"][0]["s"] * FPS))
        if a0 > 0 and scr[a0 - 1] is None and a0 - 1 >= int(round(c["s"] * FPS)):
            scr[a0 - 1] = f"scr/{cid}_0_00000.jpg"
    (HERE / "frames.js").write_text("window.FR = " + json.dumps({"scr": scr}, separators=(",", ":")) + ";\n", encoding="utf-8")

    # 官网页面镜头用的截图：复制进 media/shots/（引擎里 img 的 src）
    (MEDIA / "shots").mkdir(exist_ok=True)
    shots = sorted({c["shot"]["img"] for c in T["clips"].values() if c.get("shot")})
    for name in shots:
        src_png = EP / "素材" / "官网截图" / f"{name}.png"
        dst_png = MEDIA / "shots" / f"{name}.png"
        if not dst_png.exists() or dst_png.stat().st_mtime < src_png.stat().st_mtime:
            shutil.copy(src_png, dst_png)
    # 左栏缩略图（352×198，页面里显示 176×99）、卡片用图。spec：{"src": 素材短名, "t": 秒[, "crop": [...]]}（视频取帧，crop 缺省 = SRC_CROP）或 {"img": 官网截图名[, "crop": [x0, y0, x1, y1]]}
    (MEDIA / "thumb").mkdir(exist_ok=True)
    (MEDIA / "card").mkdir(exist_ok=True)

    def crop_vf(spec):
        crop = spec["crop"] if "crop" in spec else (SRC_CROP.get(spec.get("src")) if "src" in spec else None)
        if not crop:
            return ""
        x0, y0, x1, y1 = crop
        return f"crop=iw*{x1 - x0:.5f}:ih*{y1 - y0:.5f}:iw*{x0:.5f}:ih*{y0:.5f},"

    def one_frame(spec, vf_tail, out, q="2"):
        if "img" in spec:
            ff(["-i", EP / "素材" / "官网截图" / f"{spec['img']}.png", "-frames:v", "1", "-vf", crop_vf(spec) + vf_tail, "-q:v", q, out])
        else:
            ff(["-ss", f"{spec['t']:.3f}", "-i", SRC[spec["src"]], "-frames:v", "1", "-vf", crop_vf(spec) + vf_tail, "-q:v", q, out])

    for name, spec in (plan.get("thumbs") or {}).items():
        one_frame(spec, "scale=352:198:force_original_aspect_ratio=increase,crop=352:198", MEDIA / "thumb" / f"{name}.jpg")
    for name, spec in (plan.get("card_imgs") or {}).items():
        one_frame(spec, f"scale={spec.get('w', 1100)}:-2:flags=lanczos", MEDIA / "card" / f"{name}.jpg")
    if plan.get("qr"):                                       # 片尾卡片的二维码：plan.json 里写 "qr": "素材/xxx_qr.png"（相对本期目录；用 OpenCV QRCodeEncoder 生成并解码核对）
        shutil.copy(EP / plan["qr"], MEDIA / "qr.png")
    total = sum(1 for x in scr if x)
    print("素材帧：" + "，".join(f"{k[0]}#{k[1]} {v} 张" for k, v in counts.items()) + f"；frames.js 共 {T['frames']} 帧，其中 {total} 帧是素材画面")


if __name__ == "__main__":
    main()
