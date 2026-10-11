# -*- coding: utf-8 -*-
"""录屏帧打码（用户 2026-10-01 选“全部打码”）：注册页的邮箱和邮箱验证码、Gmail 标签页标题里的名字、新建项目对话框的 AppID、
WorkBuddy 侧栏左下角的账号邮箱。

做法：本机没有 OCR 模型（EasyOCR 的模型要上网下载），要藏的字是固定的几样，所以用模板匹配：
  - 模板从原片截（ITEMS 里写原片编号、时间、裁切框），每个模板带一个“要打码的框”（原片坐标）；
  - OpenScreen 录屏会自动缩放，同一样东西在不同帧里大小、位置都在变：每帧按一串缩放比例找（模板小的直接全分辨率找）；
  - 只按分数判断会出错（第一版：AppID 的模板对到了上一行“项目名称”，注册页的模板在空白处也能到 0.55），所以每样东西加一道校验：
      WorkBuddy 邮箱左边是绿色头像；注册页的输入框是白底；AppID 是深底亮字；Gmail 标签页左边是彩色的 M；
    再限定时间段（注册页的邮箱只在第一步页面，AppID 只在新建项目对话框开着时）；
  - 时间上补洞：前后都找到、中间漏了几帧且位置接近的，按前后插值；找到的框前后各多盖 2 帧；
  - 打码 = 马赛克 + 模糊，框四周放大一点。
只处理 media/scr/ 里成片会用到的录屏帧（prep_frames.py 抽的，1474×829）。原图先备份到 media/_scr_orig/，打码总是从备份重新做，可以反复调。

  python privacy_blur.py scan [项…]      → privacy/hits.json（每张图每项的最高分、框、校验值）
  python privacy_blur.py apply            → 打码写回 media/scr/，privacy/applied.json
  python privacy_blur.py review           → privacy/_review_*.jpg（打码后的样张，按项裁框附近；R0945 全片抽样；WorkBuddy 没找到邮箱的帧抽样）
  python privacy_blur.py restore          → 从备份恢复原图
"""
import json
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
CUT = HERE.parent / "02_出镜"
sys.path.insert(0, str(CUT))
REC = HERE.parents[1] / "素材" / "录屏"
OUT = HERE / "privacy"
ORIG = HERE / "media" / "_scr_orig"
FW = 1474 / 1920                      # 原片 → 抽出来的帧

SRC = {"R0945": "Recording_2026_10_1_09_45_15.mp4", "R1013": "Recording_2026_10_1_10_13_50.mp4",
       "R1046": "Recording_2026_10_1_10_46_01.mp4"}
WB_TAKES = {"R1013", "R1029", "R1036", "R1041", "R1046"}
# 每项：要找的模板（可以有几个，取分数最高的）；thr 分数门限；check 校验方式和门限；takes / trange 在哪些录屏、哪段时间找；
# 模板的 crop / blur 都是原片 1920×1080 坐标；scales = 目标帧里的大小 / 截模板那一帧里的大小
ITEMS = [
    # pad：画面四周补一圈侧栏的深灰再找——放大时邮箱常被画面边缘切掉一半（R1013 85 s），整块模板对不上
    dict(name="wb_email", takes=WB_TAKES, thr=0.55, check=("green", 0.12), gap=15, variants=[
        dict(src="R1046", t=0.05, crop=(203, 884, 403, 922), blur=(203, 884, 403, 922), scales=(0.85, 2.6), pad=(70, 30)),
    ]),
    # 注册页：画面四周补白（页面是白底，邮箱栏会被画面上沿切掉一半，R0945 12.5 s）；缩放过渡里位置变化大，插值不要求前后位置接近（loose）
    dict(name="reg_email", takes={"R0945"}, trange=(0, 20.6), thr=0.60, check=("white", 0.0), gap=10, loose=True, variants=[
        dict(src="R0945", t=10, crop=(128, 455, 975, 526), blur=(246, 462, 779, 518), scales=(0.45, 1.15), pad=(70, 250)),
    ]),
    dict(name="reg_code", takes={"R0945"}, trange=(0, 20.6), thr=0.60, check=("white", 0.0), gap=10, loose=True, variants=[
        dict(src="R0945", t=10, crop=(128, 650, 785, 736), blur=(246, 656, 779, 712), scales=(0.45, 1.15), pad=(70, 250)),
    ]),
    # 第三个模板只有“账号激活 - jianxiang”几个字：放大时 M 图标会被切到画面外（R0945 24 s）
    dict(name="gmail_tab", takes={"R0945"}, thr=0.60, check=("logo", 0.06), gap=6, loose=True, variants=[
        dict(src="R0945", t=16.3, crop=(444, 134, 626, 157), blur=(566, 134, 628, 157), scales=(0.85, 2.6), pad=(50, 34)),
        dict(src="R0945", t=6, crop=(646, 140, 1012, 178), blur=(868, 142, 972, 178), scales=(0.35, 1.2), pad=(50, 34)),
        dict(src="R0945", t=16.3, crop=(525, 137, 625, 156), blur=(566, 134, 628, 157), scales=(0.85, 2.6), check=("darktext", 0.0), thr=0.70, pad=(50, 34)),
    ]),
    # 门限 0.70：AppID 栏还空着的时候（5.5 s）模板会对到下面的模板缩略图上，分数 0.65；真的 AppID 是 0.79–0.99
    dict(name="appid", takes={"R1013"}, trange=(0, 75), thr=0.70, check=("darktext", 0.0), gap=6, variants=[
        dict(src="R1013", t=34, crop=(478, 527, 700, 560), blur=(474, 522, 772, 565), scales=(0.4, 1.45)),
    ]),
]


# 人工看过、确认是误判的片段（2026-10-01 按 privacy_runs.py 的分段逐个看）：(项, 输出帧起, 止, 框中心 x, y)。
# 都是把别的绿色东西当成了头像：任务栏的 WorkBuddy 图标、绿色按钮、“不使用云服务”的绿点、右键菜单“用 WorkBuddy AI 打开”、调试面板的徽标
DENY = [
    ("wb_email", 6586, 6595, 209, 763), ("wb_email", 6892, 6902, 1038, 825), ("wb_email", 7763, 7773, 487, 823),
    ("wb_email", 7798, 7815, 501, 823), ("wb_email", 8184, 8201, 507, 823), ("wb_email", 8615, 8625, 473, 823),
    ("wb_email", 11068, 11078, 123, 5), ("wb_email", 11583, 11593, 543, 397), ("wb_email", 11603, 11613, 525, 293),
    ("wb_email", 11611, 11621, 846, 824), ("wb_email", 12091, 12115, 795, 587), ("wb_email", 12115, 12126, 711, 427),
    ("wb_email", 14244, 14248, 365, 650), ("wb_email", 16274, 16284, 640, 3), ("wb_email", 16734, 16745, 857, 403),
    ("wb_email", 16734, 16745, 895, 70), ("wb_email", 17244, 17254, 923, 415), ("wb_email", 20174, 20183, 785, 657),
]


def denied(name, n, box):
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    return any(nm == name and f0 <= n <= f1 and abs(cx - x) < 45 and abs(cy - y) < 45 for nm, f0, f1, x, y in DENY)


def grab(src, t):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(REC / SRC[src]), "-frames:v", "1",
                        "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.uint8).reshape(1080, 1920)


def load_items():
    out = []
    for it in ITEMS:
        vs = []
        for v in it["variants"]:
            g = grab(v["src"], v["t"])
            x0, y0, x1, y1 = v["crop"]
            vs.append(dict(v, img=g[y0:y1, x0:x1].copy()))
        out.append(dict(it, variants=vs))
    return out


def frame_list():
    """成片里每个录屏帧：(输出帧号, 图片相对路径, 录屏编号, 录屏秒数)。"""
    from prep_frames import plan
    _, scr, _ = plan()
    s = (HERE / "frames.js").read_text(encoding="utf-8")
    man = json.loads(s[s.index("{"): s.rindex("}") + 1])["scr"]
    out = []
    for n, (x, p) in enumerate(zip(scr, man)):
        if x is None or p is None:
            continue
        out.append((n, p, x[0], x[1]))
    return out


IT = None


def init():
    global IT
    cv2.setNumThreads(1)
    IT = load_items()


def match_variant(gray, v):
    """一个模板在一张帧里的最佳位置：返回 (分数, 模板框 x0,y0,x1,y1, 缩放)。小模板全分辨率找，大模板先半分辨率粗找。"""
    T = v["img"]
    th, tw = T.shape
    lo, hi = v["scales"]
    P = 0
    if v.get("pad"):
        P, val = v["pad"]
        gray = cv2.copyMakeBorder(gray, P, P, P, P, cv2.BORDER_CONSTANT, value=val)
    best = (-1.0, None, None)
    g2 = None
    for r in np.exp(np.linspace(np.log(lo * FW), np.log(hi * FW), 24)):
        w, h = int(round(tw * r)), int(round(th * r))
        if w < 10 or h < 6 or w >= gray.shape[1] or h >= gray.shape[0]:
            continue
        if h >= 30:
            if g2 is None:
                g2 = cv2.resize(gray, (gray.shape[1] // 2, gray.shape[0] // 2), interpolation=cv2.INTER_AREA)
            t2 = cv2.resize(T, (max(1, w // 2), max(1, h // 2)), interpolation=cv2.INTER_AREA)
            res = cv2.matchTemplate(g2, t2, cv2.TM_CCOEFF_NORMED)
            _, mv, _, ml = cv2.minMaxLoc(res)
            loc = (ml[0] * 2, ml[1] * 2)
        else:
            res = cv2.matchTemplate(gray, cv2.resize(T, (w, h), interpolation=cv2.INTER_AREA), cv2.TM_CCOEFF_NORMED)
            _, mv, _, ml = cv2.minMaxLoc(res)
            loc = ml
        if mv > best[0]:
            best = (float(mv), r, loc)
    if best[1] is None:
        return -1.0, None, None
    # 全分辨率细找（缩放 ±5%，位置 ±16 px）
    mv0, r0, (x, y) = best
    bestf = best
    for r in r0 * np.linspace(0.95, 1.05, 7):
        w, h = int(round(tw * r)), int(round(th * r))
        x0, y0 = max(0, x - 16), max(0, y - 16)
        x1, y1 = min(gray.shape[1], x + w + 16), min(gray.shape[0], y + h + 16)
        roi = gray[y0:y1, x0:x1]
        if roi.shape[0] < h or roi.shape[1] < w or w < 4 or h < 4:
            continue
        res = cv2.matchTemplate(roi, cv2.resize(T, (w, h), interpolation=cv2.INTER_AREA), cv2.TM_CCOEFF_NORMED)
        _, mv, _, ml = cv2.minMaxLoc(res)
        if mv > bestf[0]:
            bestf = (float(mv), r, (x0 + ml[0], y0 + ml[1]))
    mv, r, (x, y) = bestf
    x, y = x - P, y - P
    return mv, (x, y, x + tw * r, y + th * r), r


def to_blur_box(v, tbox, r):
    cx0, cy0 = v["crop"][:2]
    bx0, by0, bx1, by1 = v["blur"]
    x, y = tbox[0], tbox[1]
    return [round(x + (bx0 - cx0) * r, 1), round(y + (by0 - cy0) * r, 1), round(x + (bx1 - cx0) * r, 1), round(y + (by1 - cy0) * r, 1)]


def sub(img, box, fx0=0.0, fx1=1.0, fy0=0.0, fy1=1.0):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    a0, a1 = int(max(0, x0 + fx0 * w)), int(min(img.shape[1], x0 + fx1 * w))
    b0, b1 = int(max(0, y0 + fy0 * h)), int(min(img.shape[0], y0 + fy1 * h))
    if a1 - a0 < 2 or b1 - b0 < 2:
        return None
    return img[b0:b1, a0:a1]


def check_value(kind, img, tbox, bbox):
    """校验值：越大越像真的。green = 头像区绿色像素占比；logo = M 图标区彩色像素占比；
    white = 输入框白底（均值够亮、有一点深色字）；darktext = 深底亮字。"""
    if kind == "green":
        a = sub(img, tbox, 0.01, 0.17, 0.1, 0.9)
        if a is None:
            return 0.0
        b, g, r = [a[:, :, k].astype(int) for k in range(3)]
        return float(((g > 110) & (g - r > 35)).mean())
    if kind == "logo":
        a = sub(img, tbox, 0.0, 0.12, 0.1, 0.9)
        if a is None:
            return 0.0
        a = a.astype(int)
        return float(((a.max(2) - a.min(2)) > 70).mean())
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    a = sub(g, bbox)
    if a is None:
        return 0.0
    m = float(a.mean())
    if kind == "white":
        dark = float((a < 140).mean())
        return 1.0 if (m > 185 and 0.005 < dark < 0.5) else 0.0
    if kind == "darktext":                         # 运动模糊时字会变淡（R0945 24 s），按 >100 算
        bright = float((a > 100).mean())
        return 1.0 if (m < 120 and 0.03 < bright < 0.6) else 0.0
    return 0.0


def scan_one(job):
    path, take, t, names = job
    src = ORIG / Path(path).name if (ORIG / Path(path).name).exists() else HERE / "media" / path
    img = cv2.imread(str(src))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    res = {}
    for it in IT:
        if it["name"] not in names:
            continue
        cands = []
        for v in it["variants"]:
            sc, tbox, r = match_variant(gray, v)
            if tbox is None:
                continue
            kind, cthr = v.get("check", it["check"])
            bbox = to_blur_box(v, tbox, r)
            cv = check_value(kind, img, tbox, bbox)
            passed = sc >= v.get("thr", it["thr"]) and cv > cthr
            cands.append((passed, sc, bbox, cv if cv > cthr else 0.0))
        if not cands:
            continue
        cands.sort(key=lambda c: (c[0], c[1]), reverse=True)
        passed, sc, bbox, cv = cands[0]
        res[it["name"]] = [round(sc, 3), bbox, round(cv, 3), bool(passed)]
    return path, res


def wanted(it, take, t):
    if take not in it["takes"]:
        return False
    if "trange" in it and not (it["trange"][0] <= t < it["trange"][1]):
        return False
    return True


def scan(only=None):
    fl = frame_list()
    names = [it["name"] for it in ITEMS if not only or it["name"] in only]
    jobs = {}
    for n, p, take, t in fl:
        want = [it["name"] for it in ITEMS if it["name"] in names and wanted(it, take, t)]
        if want:
            j = jobs.setdefault(p, [p, take, t, set()])
            j[3].update(want)
    items = [(p, take, t, sorted(w)) for p, take, t, w in jobs.values()]
    print(len(fl), "录屏帧，要查的图", len(items), "张，项：", names, flush=True)
    OUT.mkdir(exist_ok=True)
    hp = OUT / "hits.json"
    hits = json.loads(hp.read_text(encoding="utf-8")) if hp.exists() else {}
    for r in hits.values():                       # 重新查的项先清掉旧结果
        for nm in names:
            r.pop(nm, None)
    with Pool(8, initializer=init) as pool:
        for k, (p, res) in enumerate(pool.imap_unordered(scan_one, items, chunksize=6)):
            hits.setdefault(p, {}).update(res)
            if k % 1000 == 0:
                print(f"  {k}/{len(items)}", flush=True)
    hp.write_text(json.dumps(hits), encoding="utf-8")
    stats(hits, names)


def ok(it, r):
    return r is not None and len(r) > 3 and r[3]


def stats(hits=None, names=None):
    hits = hits or json.loads((OUT / "hits.json").read_text(encoding="utf-8"))
    for it in ITEMS:
        if names and it["name"] not in names:
            continue
        rs = [r[it["name"]] for r in hits.values() if it["name"] in r]
        if not rs:
            continue
        sc = np.array([r[0] for r in rs])
        cv = np.array([r[2] for r in rs])
        good = np.array([ok(it, r) for r in rs])
        print(f"{it['name']:10s} 查了 {len(rs):5d} 张：通过 {int(good.sum()):5d}；分数够但校验没过 {int(((sc >= it['thr']) & ~good).sum()):4d}；"
              f"校验过了但分数在 {it['thr'] - 0.1:.2f}–{it['thr']:.2f} {int(((sc >= it['thr'] - 0.1) & (sc < it['thr']) & (cv > it['check'][1])).sum()):4d}")


def boxes_per_frame():
    """按输出帧整理：每项每帧一个框（通过的），时间上补洞、前后各多盖 2 帧。返回 {图片: [(项, 框)…]}。"""
    hits = json.loads((OUT / "hits.json").read_text(encoding="utf-8"))
    fl = frame_list()
    seq = {}
    for it in ITEMS:
        name = it["name"]
        arr = []
        for n, p, take, t in fl:
            r = hits.get(p, {}).get(name)
            arr.append((n, p, take, r[1] if ok(it, r) else None))

        def near(a, b):
            ca, cb = ((a[0] + a[2]) / 2, (a[1] + a[3]) / 2), ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
            wa, wb = a[2] - a[0], b[2] - b[0]
            return abs(ca[0] - cb[0]) < 0.6 * max(wa, wb) and abs(ca[1] - cb[1]) < 2.0 * max(a[3] - a[1], b[3] - b[1]) and 0.6 < wa / max(wb, 1) < 1.6

        idx = [k for k, a in enumerate(arr) if a[3] is not None]
        filled = {k: arr[k][3] for k in idx}
        for a, b in zip(idx, idx[1:]):
            if 1 < b - a <= it["gap"] + 1 and arr[a][2] == arr[b][2] and arr[b][0] - arr[a][0] == b - a and (it.get("loose") or near(arr[a][3], arr[b][3])):
                for k in range(a + 1, b):
                    f = (k - a) / (b - a)
                    filled[k] = [arr[a][3][i] * (1 - f) + arr[b][3][i] * f for i in range(4)]
        extra = {}
        for k, box in filled.items():
            for d in (-2, -1, 1, 2):
                j = k + d
                if 0 <= j < len(arr) and j not in filled and arr[j][2] == arr[k][2] and abs(arr[j][0] - arr[k][0]) == abs(d):
                    extra.setdefault(j, box)
        filled.update(extra)
        for k, box in filled.items():
            if denied(name, arr[k][0], box):
                continue
            seq.setdefault(arr[k][1], []).append((name, [round(v, 1) for v in box]))
    # OCR 找到的隐私文字行（privacy_ocr.py）：直接盖。本帧自己没认出来的，借前后 2 帧内最近一帧的框
    # （不要把前后几帧的框都叠上来：画面在动时会拖成一长条，把相邻的行也盖掉，R1013 38.5 s）
    ocr_path = OUT / "ocr.jsonl"
    if ocr_path.exists():
        import privacy_ocr
        oh = privacy_ocr.load()
        for k, (n, p, take, t) in enumerate(fl):
            src = p if p in oh else None
            if src is None:
                for d in (-1, 1, -2, 2):
                    j = k + d
                    if 0 <= j < len(fl) and fl[j][2] == take and abs(fl[j][0] - n) == abs(d) and fl[j][1] in oh:
                        src = fl[j][1]
                        break
            if src is None:
                continue
            for txt, b in oh[src]:
                box = ["ocr", [b[0] - 6, b[1] - 3, b[2] + 6, b[3] + 3]]
                if box not in [list(x) for x in seq.get(p, [])]:
                    seq.setdefault(p, []).append(tuple(box))
    return seq


def pixelate(img, box):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    pad_x, pad_y = 0.05 * bw + 4, 0.18 * bh + 3
    x0, y0 = int(max(0, x0 - pad_x)), int(max(0, y0 - pad_y))
    x1, y1 = int(min(w, x1 + pad_x)), int(min(h, y1 + pad_y))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return
    roi = img[y0:y1, x0:x1]
    blk = max(4, int((y1 - y0) / 3.0))
    small = cv2.resize(roi, (max(1, (x1 - x0) // blk), max(1, (y1 - y0) // blk)), interpolation=cv2.INTER_AREA)
    mos = cv2.resize(small, (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST)
    img[y0:y1, x0:x1] = cv2.GaussianBlur(mos, (0, 0), max(1.0, blk / 4))


def apply():
    seq = boxes_per_frame()
    ORIG.mkdir(parents=True, exist_ok=True)
    prev = json.loads((OUT / "applied.json").read_text(encoding="utf-8")) if (OUT / "applied.json").exists() else {}
    for p in prev:                                # 上次打过、这次不打的：恢复原图
        if p not in seq and (ORIG / Path(p).name).exists():
            (HERE / "media" / p).write_bytes((ORIG / Path(p).name).read_bytes())
    for p, items in seq.items():
        dst = HERE / "media" / p
        bak = ORIG / Path(p).name
        if not bak.exists():
            bak.write_bytes(dst.read_bytes())
        img = cv2.imread(str(bak))
        for name, box in items:
            pixelate(img, box)
        cv2.imwrite(str(dst), img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    (OUT / "applied.json").write_text(json.dumps(seq), encoding="utf-8")
    cnt = {}
    for items in seq.values():
        for name, _ in items:
            cnt[name] = cnt.get(name, 0) + 1
    print("打码", len(seq), "张图；各项：", cnt)


def restore():
    k = 0
    if (OUT / "applied.json").exists():
        for p in json.loads((OUT / "applied.json").read_text(encoding="utf-8")):
            bak = ORIG / Path(p).name
            if bak.exists():
                (HERE / "media" / p).write_bytes(bak.read_bytes())
                k += 1
    print("恢复", k, "张")


def grid(tiles, path, cols=6, tw=368, th=207):
    rws = max(1, (len(tiles) + cols - 1) // cols)
    canvas = np.full((rws * (th + 4) + 4, cols * (tw + 4) + 4, 3), 200, np.uint8)
    for i, (im, lab) in enumerate(tiles):
        im = cv2.resize(im, (tw, th), interpolation=cv2.INTER_AREA)
        cv2.putText(im, lab, (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 255), 1)
        y, x = 4 + (i // cols) * (th + 4), 4 + (i % cols) * (tw + 4)
        canvas[y:y + th, x:x + tw] = im
    cv2.imwrite(str(path), canvas, [cv2.IMWRITE_JPEG_QUALITY, 86])


def review():
    seq = json.loads((OUT / "applied.json").read_text(encoding="utf-8"))
    fl = frame_list()
    # 1) 每项：打码后，框附近放大（均匀取 36 张）
    for it in ITEMS:
        name = it["name"]
        rows = [(n, p, take, t) for n, p, take, t in fl if any(nm == name for nm, _ in seq.get(p, []))]
        if not rows:
            continue
        pick = [rows[int(i)] for i in np.linspace(0, len(rows) - 1, min(36, len(rows)))]
        tiles = []
        for n, p, take, t in pick:
            im = cv2.imread(str(HERE / "media" / p))
            box = [b for nm, b in seq[p] if nm == name][0]
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            w = max(box[2] - box[0], 90) * 2.2
            h = w * 207 / 368
            a0, b0 = int(max(0, cx - w / 2)), int(max(0, cy - h / 2))
            tiles.append((im[b0:int(b0 + h), a0:int(a0 + w)], f"{take} {t:.1f} #{n}"))
        grid(tiles, OUT / f"_review_{name}.jpg")
    # 2) R0945 全片抽样（每 10 帧一张，整帧）
    r0945 = [x for x in fl if x[2] == "R0945"]
    pick = r0945[::10]
    for k in range(0, len(pick), 36):
        tiles = [(cv2.imread(str(HERE / "media" / p)), f"R0945 {t:.1f} #{n}") for n, p, take, t in pick[k:k + 36]]
        grid(tiles, OUT / f"_review_R0945_{k // 36 + 1}.jpg")
    # 3) WorkBuddy 录屏里没打邮箱码的帧（抽 36 张，整帧）——看有没有漏掉的
    miss = [x for x in fl if x[2] in WB_TAKES and not any(nm == "wb_email" for nm, _ in seq.get(x[1], []))]
    pick = [miss[int(i)] for i in np.linspace(0, len(miss) - 1, min(72, len(miss)))]
    for k in range(0, len(pick), 36):
        tiles = [(cv2.imread(str(HERE / "media" / p)), f"{take} {t:.1f} #{n}") for n, p, take, t in pick[k:k + 36]]
        grid(tiles, OUT / f"_review_wb_miss_{k // 36 + 1}.jpg")
    print("review 样张已出：", sorted(x.name for x in OUT.glob("_review_*.jpg")))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "scan":
        scan(sys.argv[2:] or None)
    elif cmd == "stats":
        stats()
    else:
        {"apply": apply, "restore": restore, "review": review}[cmd]()
