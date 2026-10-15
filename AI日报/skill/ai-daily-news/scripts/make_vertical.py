# -*- coding: utf-8 -*-
"""《AI每日日报》竖屏版（用户 2026-10-05：“之后日报的 routine 都是竖屏，并且都要发四个平台”；2026-10-06 起视频号不发）。

画布 1080×2340、30 fps，版式 = 短视频技能的版式 B 单框 + 边框 6（用户 2026-10-05 选的“标准竖版”）：
  标题（kicker + 新闻名 + 钩子）→ 来源截图框（橙框圈出原文标题）→ 中英双语字幕 → 鲸鱼娘 + 要点卡 / 数字卡 → 进度条；背景三张印花每期随机挑一张；
  第 0 帧 = 老封面（16:9 原图居中放进边框）；BGM = 系列 BGM，比配音低 14.5 dB；不加悠一片头片尾。
配音、口型、字幕时间都用日报流水线已经做好的（`daily.py voice` 之后的 制作/timeline.json + 制作/build/voice_main.wav），不重配。
第一版是 2026-10-05 手工做的（`AI日报/短视频/01_日报竖屏版_1005/制作/00_整片/`，记录 docs/ai/context/20261005-090500-daily-vertical-short-build_CN.md），这个脚本把它通用化。

    python make_vertical.py <期目录> all [--workers N]      data → check → mix → render → finish（daily.py render 调这个）
    python make_vertical.py <期目录> data                   只写 制作/vertical/ 下的 tl_v.json / tl_v.js、拷素材（截图、鲸鱼娘、背景、封面）
    python make_vertical.py <期目录> check                  页面里量字幕 / 标题 / 要点的真实宽度、报字号被缩小的地方、页面错误（退出码 1 = 有超宽 / 报错）
    python make_vertical.py <期目录> stills [秒 …]          静帧 + 联系表（不给秒数 = 每个场景 3 张）→ 制作/vertical/stills/
    python make_vertical.py <期目录> mix                    配音 + BGM → 制作/vertical/audio/mix.wav
    python make_vertical.py <期目录> render [--workers N]   整片 → 制作/vertical/整片_v1.mp4（RENDER_WORKERS 或按空闲内存挑路数）
    python make_vertical.py <期目录> finish [--upload]      → <期目录>/<dir_name>_成片.mp4、三份 SRT、_章节.txt、封面_3x4、QA（--upload 另出两个上传版：_上传版.mp4 H.265 / _上传版_h264.mp4）

台本.json 里和竖屏有关的可选字段（没有就自动退回）：
  news[i].vhook   竖屏标题第二行（橙色钩子，≤ 15 字宽；没有就用 points[0]）
  news[i].vbigs   数字卡：[{"line": 第几句(0 起), "n": "3.46B", "small": "活跃参数", "d": "一句说明"}, …]（每条 0–2 个；n ≤ 8 字宽）
  vertical.cuts   字幕断点：{"合并后的那条中文": [["中文锚点", "英文锚点"], …]}，自动拆得不顺的才写（check 会打印每条字幕）
"""
import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import wave
from datetime import date as Date
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
SK = Path(__file__).resolve().parent.parent                       # …\skill\ai-daily-news
SERIES = SK.parent.parent                                          # D:\大疆\AI日报
ENGINE_TPL = SK / "assets" / "vertical-engine"
WAY = Path(r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
SPRITES = Path(r"D:\大疆\AI科普\素材\角色\大肥鱼像素素材包\素材\sprites")
BGM = Path(r"D:\大疆\AI科普\素材\音频\bgm.wav")
BG_DIR = Path(r"D:\大疆\短视频\skill\short-video\assets\backgrounds")
BG_POOL = ["pattern_color.png", "pattern_ink.png", "pattern_orange.png"]
FONT = Path(r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf")
TAIL = 0.8                                                          # 短视频：金句说完 0.8 s 结束
SUB_MAX_PX = 950                                                    # 拆条时 PIL 量的字幕最宽（浏览器里的硬上限是 940：左右各留 ≥ 70 px；PIL 和浏览器差 ±1.5%，check 用浏览器量，超了自动收紧重拆）
SR = 48000
NARR_LUFS, TARGET_LUFS = -16.0, -16.0
BGM_REL_DB, BGM_SWELL_DB = -14.5, 5.0                               # 用户 2026-10-04：BGM 单路比人声低约 14–15 dB；没人说话的空档抬 +5 dB

sys.path.insert(0, str(WAY))
import bilingual_std as B  # noqa: E402

# 数据里常见、jieba 默认词典可能拆开的词（“智能 | 体”“提示 | 词”这类断在词中间的字幕，2026-10-05 手工版踩过）；台本的标题 / 要点 / 串讲短语里的 3–8 字中文词组也一并保护
LEXICON = ["智能体", "提示词", "大模型", "小模型", "开源", "闭源", "激活参数", "总参数", "预训练", "后训练", "微调", "蒸馏", "多模态", "基准测试", "漏洞赏金", "加密服务器",
           "联邦学习", "免费版", "付费版", "预发布版", "测试版", "试用版", "插件", "开发者", "上下文", "算力", "芯片", "显卡", "服务器", "云服务", "订阅", "额度",
           "鲸鱼娘", "星际争霸", "神族", "虫族", "人族", "拉取请求", "代码仓库", "审核", "合规", "隐私", "视频生成", "图像生成", "语音合成", "语音识别", "机器人"]


# ================================================================ 公用
def jload(p, default=None):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


class Ep:
    def __init__(self, ep_dir):
        self.ep = Path(ep_dir).resolve()
        if self.ep.parent != SERIES.resolve():
            sys.exit(f"期目录必须直接放在 {SERIES} 下：{self.ep}")
        self.work = self.ep / "制作" / "vertical"
        self.tl_json, self.tl_js = self.work / "tl_v.json", self.work / "tl_v.js"
        self.audio = self.work / "audio" / "mix.wav"
        self.video = self.work / "整片_v1.mp4"
        self.episode = jload(self.ep / "episode.json", {}) or {}
        self.name = self.episode.get("dir_name") or f"AI每日日报_{self.ep.name[5:7]}{self.ep.name[8:10]}"
        self.voice = self.ep / "制作" / "build" / "voice_main.wav"
        self.cover = self.ep / "封面" / "封面_16x9_1920x1080.png"

    @property
    def final(self):
        return self.ep / f"{self.name}_成片.mp4"

    @property
    def upload(self):
        return self.ep / f"{self.name}_上传版.mp4"                      # B 站用：H.265，≤ 9 MB

    @property
    def upload264(self):
        return self.ep / f"{self.name}_上传版_h264.mp4"                 # 抖音 / 小红书用：H.264，≤ 9 MB

    @property
    def cover34(self):
        return self.ep / "封面" / "封面_3x4_1080x1440.png"             # 成片第 0 帧 y450–1890 的裁切（竖屏平台的 3:4 封面）


def pid_alive(pid):
    try:
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)         # PROCESS_QUERY_LIMITED_INFORMATION（不要用 os.kill(pid, 0)：Windows 上它会把进程杀掉）
        if not h:
            return False
        code = ctypes.c_ulong()
        ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(h)
        return code.value == 259                                              # STILL_ACTIVE
    except Exception:  # noqa: BLE001
        return False


def acquire_lock(e):
    """同一期同一时间只跑一个 make_vertical（2026-10-05 试跑时两个同时跑，抢同一个 parts/ 目录）。"""
    import atexit
    e.work.mkdir(parents=True, exist_ok=True)
    lock = e.work / ".lock"
    if lock.exists():
        try:
            pid = int(lock.read_text().strip())
        except ValueError:
            pid = 0
        if pid and pid != os.getpid() and pid_alive(pid):
            sys.exit(f"另一个 make_vertical（pid {pid}）正在跑这一期：等它跑完，或确认它卡死后删 {lock}")
    lock.write_text(str(os.getpid()))
    atexit.register(lambda: lock.unlink(missing_ok=True))


def run(cmd, **kw):
    cmd = [str(c) for c in cmd]
    print("$ " + " ".join(cmd)[:200], flush=True)
    return subprocess.run(cmd, check=True, **kw)


_FONTS = {}


def _font(size, weight):
    from PIL import ImageFont
    k = (size, weight)
    if k not in _FONTS:
        f = ImageFont.truetype(str(FONT), size)
        f.set_variation_by_axes([weight])
        _FONTS[k] = f
    return _FONTS[k]


def px_zh(s):
    return _font(52, 800).getlength(s)


def px_en(s):
    return _font(30, 600).getlength(s)


# ---------------------------------------------------------------- 竖屏拆条用的“补丁”（只在这个进程里改 bilingual_std 的两个函数，不动那个共用文件）
# 1) 字宽：zh_units 原来是估的（英文字母 0.52–0.58 字宽），竖屏 940 px 一行很紧，改成用字体文件量的真实像素 / 52；
# 2) 候选断点：原来只靠 jieba 分词 + 几条规则，竖屏要多拆一刀时会断在“打 | 《星际争霸》”“下载 | 下来”“AI | 里”“10 月 | 4 日”这类地方
#    （2026-10-05 手工版靠 9 条 cuts 修）。这里加：受保护的片段（英文词 / 型号、数字 + 单位、日期、书名号、引号）里面不断；
#    按词性给断点加罚分：介词 / 副词 / 助词 / 连词 / 代词后面不断、动词后面接宾语或补语不断、方位词和助词前面不断、名词 + 名词（复合词）尽量不断。
_CHAR_PX = {}


def zh_units_px(s):
    tot = 0.0
    for ch in s:
        w = _CHAR_PX.get(ch)
        if w is None:
            w = _CHAR_PX[ch] = _font(52, 800).getlength(ch)
        tot += w
    return tot / 52.0


_PROT = [re.compile(x) for x in (
    r"[A-Za-z0-9][A-Za-z0-9.\-+_/']*[A-Za-z0-9%]",                       # GPT-6、3.46B、v0.2.1-alpha.1
    r"\d+(?:\.\d+)?\s*月\s*\d+\s*[日号]?",                              # 10 月 4 日
    r"\d+\s*年\s*\d+\s*月(?:\s*\d+\s*[日号])?",
    r"\d+(?:\.\d+)?\s*(?:[%％万亿千百]|美元|元|倍|分钟|小时|秒|天|周|年|月|日|号|个|条|次|轮|台|位|人|款|种|页|行|层|代|级|名|家|步|项|张|段)",
    r"《[^》]{1,20}》", r"“[^”]{1,20}”",
)]
_BAD_END = {"p", "c", "d", "u", "uj", "ul", "uz", "ug", "ud", "uv", "us", "y", "e", "o", "r", "rr", "rz", "pba", "pbei"}
_BAD_START = {"f", "u", "uj", "ul", "uz", "ug", "ud", "uv", "us", "y"}
_orig_cand2 = B._zh_candidates2
_ascii_ok = lambda ch: ch.isascii() and (ch.isalnum() or ch in "&%$")


def zh_candidates_pos(zh):
    import jieba.posseg as pseg
    base = _orig_cand2(zh)
    rng = [(m.start(), m.end()) for r in _PROT for m in r.finditer(zh)]
    seq, pos = [], 0
    for w, f in pseg.cut(zh):
        seq.append((pos, pos + len(w), w, f))
        pos += len(w)
    out = []
    have = {c for c, _ in base}
    real = [t for t in seq if t[2].strip()]
    for a_, b_ in zip(real, real[1:]):                           # 原函数不让断的“英文词 | 英文词 / 数字”：Stardust 是 Bruce Mackenzie Nielsen | 2020 年——整句太宽时只有这里能断，留着但罚分很重
        cut = b_[0]
        if cut in have or any(x < cut < y for x, y in rng) or not (_ascii_ok(a_[2][-1]) and _ascii_ok(b_[2][0])):
            continue
        both_caps = a_[2][:1].isupper() and b_[2][:1].isupper()
        base.append((cut, 450.0 if both_caps else 260.0))
    base.sort()
    for cut, pen in base:
        if any(a < cut < b for a, b in rng):
            continue
        if pen <= 20:                                           # 标点后面：照旧
            out.append((cut, pen))
            continue
        prev = next((t for t in reversed(seq) if t[1] <= cut and t[2].strip()), None)
        nxt = next((t for t in seq if t[0] >= cut and t[2].strip()), None)
        if prev and nxt:
            ft, fn = prev[3], nxt[3]
            if nxt[2][0] in "《“（(":                            # 书名号 / 引号 / 括号开头的算名词：“打 | 《星际争霸》”不能断
                fn = "n"
            add = 0
            if ft in _BAD_END:
                add += 300
            if ft.startswith("v") and not (fn in ("c", "p") or fn.startswith("x")):
                add += 150
            if fn in _BAD_START:
                add += 400
            if ft.startswith("n") and fn.startswith("n"):
                add += 50
            if fn == "p" and ft != "p":                         # 介词前面是好断点：“……，替自己上场”
                pen = min(pen, 25.0)
            pen += add
        out.append((cut, pen))
    return out


B.zh_units = zh_units_px
B._zh_candidates2 = zh_candidates_pos
ZH_MAX_PX = SUB_MAX_PX / 52.0                                   # ≈ 18.3 字宽（check 不过会收紧）


def fmt_ts(sec):
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def free_mem_gb():
    """空闲物理内存（GB）；读不到就当 8。"""
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tot", ctypes.c_ulonglong), ("avail", ctypes.c_ulonglong),
                        ("a", ctypes.c_ulonglong), ("b", ctypes.c_ulonglong), ("c", ctypes.c_ulonglong), ("d", ctypes.c_ulonglong), ("e", ctypes.c_ulonglong)]
        m = MS()
        m.l = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.avail / 2 ** 30
    except Exception:  # noqa: BLE001
        return 8.0


def pick_workers(arg):
    """用户 2026-09-28：渲染统一 4 路；2026-10-04：空闲内存 < 6 GB 或别的会话在渲染就降到 3 / 2。"""
    if arg:
        return arg
    if os.environ.get("RENDER_WORKERS"):
        return int(os.environ["RENDER_WORKERS"])
    g = free_mem_gb()
    return 4 if g >= 10 else 3 if g >= 6 else 2


# ================================================================ data
def protect_terms(sc):
    import jieba
    words = set(LEXICON)
    texts = []
    for n in sc["news"]:
        texts += [n.get("headline", ""), n.get("bar_label", ""), n.get("rundown_key", "")] + list(n.get("points") or [])
    for t in texts:
        words.update(re.findall(r"[\u4e00-\u9fff]{3,8}", t))
    for w in words:
        jieba.add_word(w, 50000)


def norm(s):
    return re.sub(r"[\s，。、；：！？,.;:!?“”‘’\"'（）()《》「」]", "", s)


def merge_tiny(raw):
    """日报横屏版的字幕里有“官方称，”“第三件，”这种只有几个字的条：同一句里和后面一条合并再拆；句尾孤零零的几个字并进前一条。"""
    out, i = [], 0
    while i < len(raw):
        u = dict(raw[i])
        while B.zh_units(u["zh"]) < 6 and i + 1 < len(raw) and raw[i + 1]["seg"] == u["seg"]:
            v = raw[i + 1]
            u = dict(zh=u["zh"] + v["zh"], en=(u["en"] + " " + v["en"]).strip(), s=u["s"], e=v["e"], seg=u["seg"])
            i += 1
        out.append(u)
        i += 1
    res = []
    for u in out:
        if res and res[-1]["seg"] == u["seg"] and B.zh_units(u["zh"]) < 4:
            p = res[-1]
            res[-1] = dict(zh=p["zh"] + u["zh"], en=(p["en"] + " " + u["en"]).strip(), s=p["s"], e=u["e"], seg=p["seg"])
        else:
            res.append(u)
    return res


def split_unit(zh, en, cuts=None, lim=None):
    """竖屏拆条：真实字宽 ≤ 930 px（中文 52 px、英文 30 px 各一行），英文起步 ≤ 60 字符；拆完量真实像素，超了就收紧再拆。返回 (chunks, 状态)。
    lim = 只给这一条用的更紧的像素上限（check 量出这条超宽时才给，见 main 的 all；2026-10-06 以前是整片一起收紧，没超宽的条也全变了，中英错条一大片）。"""
    global SUB_MAX_PX, ZH_MAX_PX
    if lim:
        keep = SUB_MAX_PX, ZH_MAX_PX
        SUB_MAX_PX, ZH_MAX_PX = lim, lim / 52.0
        try:
            return split_unit(zh, en, cuts)
        finally:
            SUB_MAX_PX, ZH_MAX_PX = keep
    last = None
    for k, (enmax, zmax) in enumerate(((60, ZH_MAX_PX), (56, 16.8), (52, 15.5), (48, 14.0))):
        B.EN_MAX, B.EN_SOFT, B.ZH_MAX = enmax, enmax + 4, zmax
        ch = B.split_pair_aligned(zh, en, cuts=cuts)
        last = ch
        if all(px_zh(z) <= SUB_MAX_PX and px_en(e) <= SUB_MAX_PX for z, e, _ in ch):
            B.EN_MAX, B.EN_SOFT, B.ZH_MAX = 60, 64, ZH_MAX_PX
            return ch, ("ok" if k == 0 else f"收紧 {k}")
        if cuts:
            break
    B.EN_MAX, B.EN_SOFT, B.ZH_MAX = 60, 64, ZH_MAX_PX
    return last, "超宽"


def make_subs(T, vcuts, total, tight=None):
    """tight = {合并后的那条中文: 像素上限}：check 量出超宽的条单独收紧（制作/vertical/tight.json 记着，重跑沿用）。"""
    segs = T["segments"]
    raw = sorted((dict(u, seg=s["id"]) for s in segs for u in s.get("subs") or []), key=lambda u: u["s"])
    if not raw:
        sys.exit("timeline.json 里没有 subs：先跑 daily.py render 前面的 bilingual_subs.py（中英双语字幕）")
    units = merge_tiny(raw)
    chunks, flags = [], []
    for u in units:
        ch, state = split_unit(u["zh"], u["en"], [tuple(c) for c in vcuts.get(u["zh"], [])] or None, (tight or {}).get(u["zh"]))
        if state != "ok":
            flags.append((u["s"], state, u["zh"]))
        for k, ((z, e, w), (a, b)) in enumerate(zip(ch, B.chunk_times(u["s"], u["e"], ch))):
            chunks.append({"zh": z, "en": e, "s": round(a, 3), "e": round(b, 3), "seg": u["seg"], "u": u["zh"], "uen": u["en"]})
    for x, (a, b) in zip(chunks, B.display_windows([(x["s"], x["e"]) for x in chunks])):
        x["a"], x["b"] = round(a, 3), round(min(b, total), 3)
    return chunks, flags


def find_rundown(seg, news):
    """开场串讲（S01 最后一句）里每条新闻对应的 [起, 止]：用 rundown_key 在这句的短语（lines）里找最短的连续几个短语；找不到的平均分。"""
    lines = seg.get("lines") or []
    n = len(news)
    out = [None] * n
    nl = [norm(x["text"]) for x in lines]
    for i, item in enumerate(news):
        key = norm(item.get("rundown_key") or "")
        if not key:
            continue
        best = None
        for a in range(len(lines)):
            acc = ""
            for b in range(a, len(lines)):
                acc += nl[b]
                if key in acc:
                    if best is None or (b - a) < (best[1] - best[0]):
                        best = (a, b)
                    break
        if best:
            out[i] = [lines[best[0]]["start"], lines[best[1]]["end"]]
    if any(o is None for o in out):                     # 有找不到的：整句平均分（宁可粗一点，不要某张卡永远不亮）
        s0, e0 = seg["start"], seg["end"]
        for i in range(n):
            if out[i] is None:
                out[i] = [s0 + (e0 - s0) * i / n, s0 + (e0 - s0) * (i + 1) / n]
    return out


def hook_for(i, n):
    t2 = (n.get("vhook") or "").strip()
    if not t2:
        pts = n.get("points") or []
        t2 = pts[0] if pts else (n.get("rundown_key") or "")
        if t2.replace(" ", "") == (n.get("headline") or "").replace(" ", "") and len(pts) > 1:
            t2 = pts[1]
    return t2


def build_data(e, bg_arg=None, sub_max=None, tight=None):
    global SUB_MAX_PX, ZH_MAX_PX
    if sub_max:
        SUB_MAX_PX, ZH_MAX_PX = sub_max, sub_max / 52.0
    if tight is None:
        tight = jload(e.work / "tight.json", {}) or {}
    sc = jload(e.ep / "台本.json")
    T = jload(e.ep / "制作" / "timeline.json")
    if not sc or not T:
        sys.exit(f"缺 台本.json 或 制作/timeline.json：{e.ep}")
    news = sc["news"]
    N = len(news)
    d = Date.fromisoformat(sc["date"])
    mmdd = f"{d.month:02d}.{d.day:02d}"
    segs = T["segments"]
    by = {}
    for s in segs:
        by.setdefault(s["scene"], []).append(s)
    segid = {s["id"]: s for s in segs}
    last_end = max(u["e"] for s in segs for u in s.get("subs") or [])
    total = round(last_end + TAIL, 3)
    fps = T["fps"]
    frames = int(round(total * fps))
    snaps = jload(e.ep / "制作" / "assets" / "snaps" / "snaps.json", {}) or {}
    protect_terms(sc)
    vcuts = (sc.get("vertical") or {}).get("cuts") or {}

    from PIL import Image
    scenes, notes = [], []
    rundown = find_rundown(by["S01"][-1], news)
    cv = sc.get("cover") or {}
    line1 = (cv.get("line1") or "").strip()
    open_t2 = line1 + "？" if line1 and B.zh_units(line1 + "？") <= 14.5 and not line1.endswith(("？", "?", "。")) else (cv.get("line2") or line1 or "鲸鱼娘带你看看 AI 圈")
    for s in T["scenes"]:
        sid = s["id"]
        dd = dict(id=sid, s=s["start"], e=min(s["end"], total))
        k = int(sid[1:]) - 1                               # 第几条新闻（1..N）；S01 → 0、回顾 → N+1
        if sid == "S01":
            dd.update(kind="open", kicker=f"AI每日日报 · <b>{mmdd}</b>", t1=f"今天说 {N} 件事", t2=open_t2, tag=f"今日 {N} 条",
                      card=dict(n=str(N), small="件事", d=f"约 {max(1, round(total / 60))} 分钟 · 每条都附来源"), agendaTimes=rundown)
        elif k == N + 1:
            dd.update(kind="review", kicker=f"AI每日日报 · <b>{mmdd}</b>", t1="今日回顾", t2=f"{N} 件事，来源都在简介里", tag="今日回顾",
                      card=dict(n=f"✓ {N}", small="条看完", d="来源都在简介里 · 明天见"))
        else:
            n = news[k - 1]
            ss = by[sid]
            if len(ss) != len(n["lines"]):
                notes.append(f"{sid}：配音段 {len(ss)} 个、台本句子 {len(n['lines'])} 句，按顺序对齐到较少的那个")
            m = min(len(ss), len(n["lines"]))
            ptTimes = [dict(pt=ln["point"], s=seg["start"], e=seg["end"]) for seg, ln in zip(ss[:m], n["lines"][:m]) if ln.get("point") is not None]
            bigs = []
            for b in n.get("vbigs") or []:
                if isinstance(b.get("line"), int) and 0 <= b["line"] < m and b.get("n") and b.get("d"):
                    seg = ss[b["line"]]
                    bigs.append(dict(n=str(b["n"]), small=b.get("small", ""), d=b["d"], s=seg["start"], e=seg["end"]))
                else:
                    notes.append(f"{sid}：vbigs {b} 的 line 不对或缺 n / d，已忽略")
            snap_file = e.ep / "制作" / "assets" / "snaps" / f"news_{k:02d}.png"
            snap = wh = hl = None
            if snap_file.exists() and (snaps.get(str(k)) or {}).get("ok", True):
                snap = f"assets/snaps/news_{k:02d}.png"
                with Image.open(snap_file) as im:
                    wh = list(im.size)
                hl = (snaps.get(str(k)) or {}).get("h1box")
            tag = "来源 · " + (n.get("source_short") or (n.get("source") or "").split("·")[0].strip() or "原文")
            dd.update(kind="news", idx=k, kicker=f"AI每日日报 · <b>{mmdd}</b> · 第 <b>{k}</b> / {N} 条", t1=n["headline"], t2=hook_for(k, n), tag=tag,
                      snap=snap, wh=wh, hl=hl, org=n.get("org") or n.get("source_short") or "", headline=n["headline"], source=n.get("source") or "",
                      pts=n["points"], ptTimes=ptTimes, bigs=bigs)
        scenes.append(dd)
    scenes[-1]["e"] = total

    chunks, flags = make_subs(T, vcuts, total, tight)

    expr = []
    for s in segs:
        for a in s.get("actions", []):
            if a.get("type") == "expr":
                expr.append(dict(name=a["name"], s=a["start"], e=a["end"]))

    agenda = []
    for i, n in enumerate(news, 1):
        has = (e.ep / "制作" / "assets" / "snaps" / f"news_{i:02d}.png").exists() and (snaps.get(str(i)) or {}).get("ok", True)
        agenda.append(dict(n=i, head=n["headline"], org=n.get("org") or n.get("source_short") or "", snap=f"assets/snaps/news_{i:02d}.png" if has else None))

    # 背景印花：每期随机挑一张（用户 2026-10-04）；同一期重跑沿用，用日期做种子
    e.work.mkdir(parents=True, exist_ok=True)
    bgj = jload(e.work / "bg.json", {}) or {}
    bg = bg_arg or bgj.get("file") or random.Random(sc["date"]).choice(BG_POOL)
    (e.work / "bg.json").write_text(json.dumps({"file": bg, "pool": BG_POOL, "note": "短视频技能：每期随机挑一张"}, ensure_ascii=False, indent=1), encoding="utf-8")

    tl = dict(fps=fps, total=total, frames=frames, bg="assets/bg.png", cover="assets/cover.png", n=N, scenes=scenes, subs=chunks, expr=expr,
              mouth=T["mouth"][: frames + 2], agenda=agenda)
    e.tl_json.write_text(json.dumps(tl, ensure_ascii=False), encoding="utf-8")
    e.tl_js.write_text("window.TL = " + json.dumps(tl, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

    # 引擎 + 素材
    for f in ("index.html", "engine.js"):
        shutil.copy2(ENGINE_TPL / f, e.work / f)
    a = e.work / "assets"
    (a / "snaps").mkdir(parents=True, exist_ok=True)
    for f in (e.ep / "制作" / "assets" / "snaps").glob("news_*.png"):
        shutil.copy2(f, a / "snaps" / f.name)
    if not (a / "sprites").exists():
        shutil.copytree(SPRITES, a / "sprites")
    shutil.copy2(BG_DIR / bg, a / "bg.png")
    if not e.cover.exists():
        sys.exit(f"缺封面 {e.cover}：先 make_cover_white.py <期目录> --from-script")
    shutil.copy2(e.cover, a / "cover.png")

    print(f"竖屏数据：{N} 条新闻、{len(scenes)} 个场景、整片 {total:.2f} s（{frames} 帧）、背景 {bg}；日报字幕 → 竖屏 {len(chunks)} 条")
    if flags:
        print("  ! 这些字幕自动拆得不理想（超宽 / 收紧过），check 后看一眼，要改的写进 台本.json 的 vertical.cuts：")
        for s0, st, zh in flags:
            print(f"    {s0:7.2f}s [{st}] {zh}")
    miss = [s["idx"] for s in scenes if s.get("kind") == "news" and not s.get("snap")]
    if miss:
        print(f"  ! 第 {miss} 条没有来源截图，框里放机构名 + 标题")
    nohl = [s["idx"] for s in scenes if s.get("kind") == "news" and s.get("snap") and not s.get("hl")]
    if nohl:
        print(f"  · 第 {nohl} 条没有圈框（snaps.json 里没有 h1box：snap_sources.py 2026-10-05 起才记；--force 重截就有）")
    for n_ in notes:
        print("  ! " + n_)
    return tl


# ================================================================ 页面（check / stills / render）
def open_page(p, e):
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 2340})
    errors = []
    page.on("pageerror", lambda x: errors.append("pageerror: " + str(x)))
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    page.goto((e.work / "index.html").as_uri())
    page.evaluate("window.READY")
    return browser, page, errors


def page_errors(page, errors):
    return errors + page.evaluate("window.__ERR")


def cmd_check(e, want_bad=False):
    """want_bad：另返回超宽字幕所在的那条（合并后的中文）和量到的最宽像素，all 用它只收紧这几条。"""
    from playwright.sync_api import sync_playwright
    T = jload(e.tl_json)
    with sync_playwright() as p:
        browser, page, errors = open_page(p, e)
        js = """(subs) => {
          const m = (txt, font) => { const s = document.createElement('span'); s.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;font:' + font + ';-webkit-text-stroke:0'; s.textContent = txt; document.body.appendChild(s); const w = s.getBoundingClientRect().width; s.remove(); return w; };
          return subs.map(x => [m(x.zh, "800 52px 'Noto Sans SC'"), m(x.en, "600 30px 'Noto Sans SC'")]);
        }"""
        widths = page.evaluate(js, T["subs"])
        warn = page.evaluate("window.__WARN")
        errs = page_errors(page, errors)
        browser.close()
    bad = [(x["s"], zw, ew, x["zh"], x["en"]) for x, (zw, ew) in zip(T["subs"], widths) if zw > 940 or ew > 940]
    mz, me = max(w[0] for w in widths), max(w[1] for w in widths)
    print(f"字幕 {len(widths)} 条：中文最宽 {mz:.0f} px、英文最宽 {me:.0f} px（上限 940）；超宽 {len(bad)} 条")
    for s, zw, ew, zh, en in bad:
        print(f"  {s:7.2f}s 中文 {zw:.0f} / 英文 {ew:.0f}：{zh} / {en}")
    hard = [w for w in warn if "下限还是超宽" in w]
    print("缩小字号的地方:", warn or "无")
    print("页面错误:", errs or "无")
    ok = not bad and not errs and not hard
    print("CHECK OK" if ok else "CHECK FAIL（字幕超宽 / 页面报错 / 标题缩到下限还超宽：改台本里的 vhook / headline、或 vertical.cuts 后重跑 data）")
    if want_bad:
        units = {}
        for x, (zw, ew) in zip(T["subs"], widths):
            if (zw > 940 or ew > 940) and x.get("u"):
                units[x["u"]] = max(units.get(x["u"], 0), zw, ew)
        return (0 if ok else 1), units, bool(errs or hard)
    return 0 if ok else 1


# ---------------------------------------------------------------- 字幕对齐检查（2026-10-06 加）
# 那天 AI 复核连挂 3 次，几乎都是竖屏重拆后的中英错条（中文这条有“Claude / 95% / 视频”，英文这条没有、跑到了下一条）
# 和断在词中间（“英 | 伟达”“研究 | 人员”）。这里在渲染前自动查，查到就停，改 台本.json 的 vertical.cuts（或英文语序）再跑。
LINT_GLOSS = {          # 中文词 → 英文里一定会出现的写法（只收不容易误报的；大小写不敏感）
    "欧盟": ["EU"], "视频": ["video"], "水印": ["watermark"], "英伟达": ["Nvidia"], "上下文": ["context"],
    "研究人员": ["researcher"], "生图": ["image generation"], "谷歌": ["Google"], "微软": ["Microsoft"],
    "阿里": ["Alibaba"], "字节": ["ByteDance"], "腾讯": ["Tencent"], "百度": ["Baidu"], "华为": ["Huawei"], "智谱": ["Zhipu"],
    "亚马逊": ["Amazon"], "苹果": ["Apple"], "豆包": ["Doubao"], "千问": ["Qwen"], "月之暗面": ["Moonshot"], "维基百科": ["Wikipedia"],
    "维基媒体": ["Wikimedia"], "鲸鱼娘": ["Whale Girl"], "宕机": ["outage"], "开源": ["open"], "价格": ["pric"],
}
_MONTH_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
_LAT = re.compile(r"[A-Za-z][A-Za-z0-9.\-+]*[A-Za-z0-9]|[A-Za-z]")
_NUM = re.compile(r"\d+(?:\.\d+)?")


def _zh_keys(z):
    """中文这一条里该在同一条英文里出现的东西：(显示名, [英文里的候选写法])。"""
    out = []
    for t in dict.fromkeys(_NUM.findall(z)):
        out.append((t, [t]))
    for m in re.finditer(r"(\d{1,2})\s*月", z):
        k = int(m.group(1))
        if 1 <= k <= 12:
            out.append((m.group(0), [_MONTH_EN[k - 1], m.group(1)]))
    for t in dict.fromkeys(_LAT.findall(z)):
        if len(t) >= 2 and not t.isdigit():
            out.append((t, [t]))
    for k, v in LINT_GLOSS.items():
        if k in z:
            out.append((k, v))
    return out


def _has(text, forms):
    tl = text.lower()
    return any(f.lower() in tl for f in forms)


def lint_subs(chunks):
    """返回 (errors, warns)，每项是一句话（带时间和那条的拆法）。只比同一条（合并后的那条）里相邻的几段，不管整句怎么翻。"""
    import jieba
    for w in LINT_GLOSS:
        jieba.add_word(w, 50000)
    errors, warns = [], []
    groups, cur = [], []
    for c in chunks:
        if cur and c.get("u") != cur[-1].get("u"):
            groups.append(cur)
            cur = []
        cur.append(c)
    if cur:
        groups.append(cur)
    for g in groups:
        show = " ‖ ".join(f"{c['zh']} / {c['en']}" for c in g)
        t0 = g[0]["s"]
        if len(g) > 1:
            for i, c in enumerate(g):
                others_en = [x["en"] for j, x in enumerate(g) if j != i]
                others_zh = [x["zh"] for j, x in enumerate(g) if j != i]
                for name, forms in _zh_keys(c["zh"]):
                    if not _has(c["en"], forms) and any(_has(o, forms) for o in others_en):
                        errors.append(f"{t0:7.2f}s 中英错条：中文第 {i + 1} 段有“{name}”，英文在别的段：{show}")
                for t in dict.fromkeys(_LAT.findall(c["en"]) + _NUM.findall(c["en"])):
                    if (t[:1].isupper() or any(ch.isdigit() for ch in t)) and len(t) >= 2 and t.lower() not in c["zh"].lower() \
                            and any(t.lower() in o.lower() for o in others_zh):
                        errors.append(f"{t0:7.2f}s 中英错条：英文第 {i + 1} 段有“{t}”，中文在别的段：{show}")
            # 断在词中间：按整条中文分词（只用词典，不用 HMM 猜新词，不然“有英”“体对”这种也算词），段与段的分界落在一个 ≥2 字的中文词里面
            whole = "".join(c["zh"] for c in g)
            bounds, pos = [], 0
            for c in g[:-1]:
                pos += len(c["zh"])
                bounds.append(pos)
            spans, p = [], 0
            for w in jieba.lcut(whole, HMM=False):
                spans.append((p, p + len(w), w))
                p += len(w)
            for b in bounds:
                for a_, z_, w in spans:
                    if a_ < b < z_ and len(w) >= 2 and re.fullmatch(r"[一-鿿]+", w):
                        errors.append(f"{t0:7.2f}s 断在词中间：“{w[: b - a_]} | {w[b - a_:]}”：{show}")
        for c in g:
            dur = c["e"] - c["s"]
            if dur < 1.0 and len(c["en"]) > 24:
                warns.append(f"{c['s']:7.2f}s 这段只停 {dur:.2f} s，英文 {len(c['en'])} 字符读不完：{c['zh']} / {c['en']}")
    return list(dict.fromkeys(errors)), warns


def cmd_lint(e):
    T = jload(e.tl_json)
    if not T or not T.get("subs"):
        sys.exit("没有 制作/vertical/tl_v.json：先跑 data")
    if not all("u" in x for x in T["subs"]):
        sys.exit("tl_v.json 是 2026-10-06 以前的格式（没有分组字段 u）：先重跑 data")
    sc = jload(e.ep / "台本.json")
    if sc:
        protect_terms(sc)
    errors, warns = lint_subs(T["subs"])
    print(f"字幕对齐检查：{len(T['subs'])} 段，错 {len(errors)} 处、提示 {len(warns)} 处")
    for x in errors:
        print("  ✗ " + x)
    for x in warns:
        print("  · " + x)
    if errors:
        print("LINT FAIL：改 台本.json 的 vertical.cuts（键 = 上面 ‖ 连起来的整条中文，锚点 = 在这段文字之后断）或把那句英文换成和中文同样的语序，再跑；不用重配音")
    return 1 if errors else 0


def cmd_stills(e, times):
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageDraw, ImageFont
    T = jload(e.tl_json)
    if not times:
        times = []
        for s in T["scenes"]:
            for f in (0.06, 0.5, 0.94):
                t = round(s["s"] + (s["e"] - s["s"]) * f, 2)
                times.append((t, f"{s['id']} {s['kind']} @{t:.1f}s"))
        tag = "_segs"
    else:
        times = [(t, f"{t:.2f}s") for t in times]
        tag = "_t"
    d = e.work / "stills"
    d.mkdir(exist_ok=True)
    files = []
    with sync_playwright() as p:
        browser, page, errors = open_page(p, e)
        for t, label in times:
            page.evaluate(f"renderAt({t})")
            f = d / f"t{t:07.2f}.png"
            page.screenshot(path=str(f))
            files.append((f, label))
        errs = page_errors(page, errors)
        warn = page.evaluate("window.__WARN")
        browser.close()
    print("errors:", errs or "none", "| 缩小字号的地方:", warn or "无")
    font = ImageFont.truetype(str(FONT), 24)
    W, H, cols = 300, 650, 6
    sheets = []
    for n in range(0, len(files), 12):
        chunk = files[n:n + 12]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (W + 10) + 10, rows * (H + 44) + 10), "#C9CDD3")
        dr = ImageDraw.Draw(sheet)
        for j, (f, label) in enumerate(chunk):
            x, y = 10 + (j % cols) * (W + 10), 10 + (j // cols) * (H + 44)
            dr.text((x, y), label, fill="#111", font=font)
            sheet.paste(Image.open(f).convert("RGB").resize((W, H), Image.LANCZOS), (x, y + 34))
        out = d / f"_sheet{tag}_{n // 12 + 1}.png"
        sheet.save(out)
        sheets.append(out)
        print("sheet ->", out)
    return sheets


# ================================================================ mix（配音 + BGM）
def _load(path, af=None):
    args = ["ffmpeg", "-v", "error", "-i", str(path), "-vn"]
    if af:
        args += ["-af", af]
    args += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(args, check=True, capture_output=True).stdout, dtype=np.float32).reshape(-1, 2).copy()


def _lufs(a):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                       input=a.astype(np.float32).tobytes(), capture_output=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr.decode("utf-8", "replace"))[-1])


def _normalized(path, target=NARR_LUFS):
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", f"highpass=f=70,loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(p1[p1.rindex("{"): p1.rindex("}") + 1])
    af = (f"highpass=f=70,loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    return _load(path, af), m["input_i"]


def _activity(voice, n):
    """有人说话的地方 = 1：10 ms 一格的包络，前 0.12 s、后 0.4 s 保持，再平滑 0.15 s。"""
    hop = SR // 100
    k = n // hop
    mono = voice[: k * hop].mean(1)
    rms = 20 * np.log10(np.sqrt((mono.reshape(k, hop) ** 2).mean(1)) + 1e-9)
    act = (rms > -50).astype(np.float32)
    pad = np.pad(act, (12, 40))
    dil = np.array([pad[i: i + 53].max() for i in range(k)], np.float32)
    sm = np.convolve(dil, np.ones(15) / 15, mode="same")
    return np.interp(np.arange(n) / hop, np.arange(k), sm).astype(np.float32)


def cmd_mix(e):
    T = jload(e.tl_json)
    if not e.voice.exists():
        sys.exit(f"缺配音 {e.voice}：先 daily.py voice + render 里的 mix_audio.py")
    n = T["frames"] * SR // T["fps"]
    voice = np.zeros((n, 2), np.float32)
    v, vin = _normalized(e.voice)
    voice[: min(n, len(v))] = v[:n]
    act = _activity(voice, n)
    b = _load(BGM)
    if len(b) < n:                                         # BGM 492 s，日报 5–6 分钟用不到；万一不够就循环
        b = np.tile(b, (n // len(b) + 1, 1))
    b = b[:n]
    b_lufs = _lufs(b)
    bed_db = (NARR_LUFS + BGM_REL_DB) - b_lufs
    swell = 1 + (10 ** (BGM_SWELL_DB / 20) - 1) * (1 - act)
    bgm = b * (10 ** (bed_db / 20)) * swell[:, None]
    bgm[:SR] *= np.linspace(0, 1, SR)[:, None]
    bgm[-2 * SR:] *= np.linspace(1, 0, 2 * SR)[:, None]
    if os.environ.get("DAILY_SILENT") == "1":              # 2026-10-13 用户：Fish 额度用完，先发“无配音 + BGM”版；配音轨只用来定字幕时间和 BGM 起伏，不混进成片
        mix = bgm.copy()
    else:
        mix = voice + bgm
    g = 10 ** ((TARGET_LUFS - _lufs(mix)) / 20)
    mix *= g
    lim = 10 ** (-1.0 / 20)
    over = np.abs(mix) > lim
    n_over = int(over.sum())
    mix[over] = np.sign(mix[over]) * (lim + (np.abs(mix[over]) - lim) * 0.2)
    mix = np.clip(mix, -lim, lim)
    e.audio.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(e.audio), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    vl, bl = _lufs(voice * g), _lufs(bgm * g)
    print(f"mix.wav {n / SR:.2f}s；配音原始 {vin} LUFS → {NARR_LUFS}；BGM 床 {bed_db:+.1f} dB；成片里配音 {vl:.1f} LUFS、BGM {bl:.1f} LUFS（差 {vl - bl:.1f} dB）；"
          f"整片 {_lufs(mix):.1f} LUFS，峰值 {20 * np.log10(float(np.abs(mix).max())):.1f} dBFS（软限幅 {n_over} 个采样点）")


# ================================================================ render
def worker(e, k, a, b):
    from playwright.sync_api import sync_playwright
    parts = e.work / "parts"
    parts.mkdir(exist_ok=True)
    out = parts / f"part_{k}.mp4"
    with sync_playwright() as p:
        browser, page, errors = open_page(p, e)
        fps = page.evaluate("window.META.FPS")
        enc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
             "-filter_threads", "1", "-vf", "format=yuv420p", "-c:v", "libx264", "-threads", "3", "-crf", "16", "-preset", "medium",
             "-r", str(fps), str(out)], stdin=subprocess.PIPE)
        t0 = time.time()
        for i in range(a, b):
            page.evaluate(f"renderAt({i / fps})")
            enc.stdin.write(page.screenshot(type="jpeg", quality=95))
            if (i - a) % 600 == 0:
                print(f"[w{k}] {i - a}/{b - a} ({time.time() - t0:.0f}s)", flush=True)
        enc.stdin.close()
        enc.wait()
        errs = page_errors(page, errors)
        browser.close()
    (parts / f"part_{k}.json").write_text(json.dumps({"a": a, "b": b, "errors": errs}, ensure_ascii=False), encoding="utf-8")
    print(f"[w{k}] done {b - a} frames in {time.time() - t0:.0f}s, errors: {len(errs)}", flush=True)


def cmd_render(e, workers_arg=None):
    T = jload(e.tl_json)
    fps, n = T["fps"], T["frames"]
    W = pick_workers(workers_arg)
    cuts = [round(n * i / W) for i in range(W + 1)]
    print(f"渲染 {n} 帧，{W} 路（空闲内存 {free_mem_gb():.1f} GB）")
    t0 = time.time()
    parts = e.work / "parts"
    parts.mkdir(exist_ok=True)
    for f in parts.glob("part_*"):
        try:
            f.unlink()
        except PermissionError:
            sys.exit(f"{f.name} 被别的进程占着（还有渲染在跑？）：等它结束再 render")
    procs = []
    for k in range(W):
        procs.append(subprocess.Popen([sys.executable, __file__, str(e.ep), "worker", str(k), str(cuts[k]), str(cuts[k + 1])]))
        time.sleep(0.7)
    for pr in procs:
        pr.wait()
    errs = []
    for k in range(W):
        pj = parts / f"part_{k}.json"
        if not pj.exists():
            sys.exit(f"第 {k} 路没有渲完（{pj} 不存在）：看上面的输出，重跑 render")
        errs += jload(pj)["errors"]
    if errs:
        print("PAGE ERRORS:", *errs[:20], sep="\n  ")
        sys.exit(2)
    lst = parts / "list.txt"
    lst.write_text("".join(f"file 'part_{k}.mp4'\n" for k in range(W)), encoding="utf-8")
    if not e.audio.exists():
        sys.exit(f"缺 {e.audio}：先 mix")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", e.audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", e.video])
    print(f"ok -> {e.video}（{n} 帧，{time.time() - t0:.0f} s）")


# ================================================================ finish
def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,nb_read_packets", "-count_packets",
                                   "-show_entries", "format=duration", "-of", "json", str(path)]).decode()
    j = json.loads(out)
    return int(j["streams"][0]["width"]), int(j["streams"][0]["height"]), int(j["streams"][0]["nb_read_packets"]), float(j["format"]["duration"])


def sync_check(e, T):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(e.video), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.float32)
    fps = T["fps"]
    hop = SR // fps
    k = min(T["frames"], len(a) // hop)
    rms = np.sqrt((a[: k * hop].reshape(k, hop) ** 2).mean(1))
    mouth = np.array(T["mouth"][:k], dtype=float)
    best = []
    for lag in range(-8, 9):
        x, y = (mouth[lag:], rms[: k - lag]) if lag >= 0 else (mouth[: k + lag], rms[-lag:])
        best.append((float(np.corrcoef(x, y)[0, 1]), lag))
    c, l = max(best)
    return l, c, dict((lag, cc) for cc, lag in best)[0]


def cmd_finish(e, upload=False):
    T = jload(e.tl_json)
    if not e.video.exists():
        sys.exit(f"缺 {e.video}：先 render")
    shutil.copy2(e.video, e.final)
    rows = [(x["a"], x["b"], x["zh"], x["en"]) for x in T["subs"]]
    B.write_srts(str(e.ep / e.name), rows)                          # 时间从 0 起，没有片头偏移
    # B 站分段章节：每个场景一段（开场 + N 条 + 回顾，≤ 10 段）；时间 = 场景起点（竖屏没有片头）
    chap = e.episode.get("chapters") or {}
    lines = [f"{fmt_ts(s['s'])} {chap.get(s['id']) or s['t1']}" for s in T["scenes"]]
    (e.ep / f"{e.name}_章节.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    w, h, frames, dur = probe(e.final)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(e.final), "-vn", "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    last = lambda pat: (re.findall(pat, err) or ["—"])[-1]
    lufs, lra, tp = last(r"I:\s+(-?[\d.]+|-inf) LUFS"), last(r"LRA:\s+([\d.]+) LU"), last(r"Peak:\s+(-?[\d.]+|-inf) dBFS")
    lag, corr, corr0 = sync_check(e, T)
    ok = (w, h) == (1080, 2340) and frames == T["frames"] and abs(dur - T["total"]) < 0.15 and (lag == 0 or os.environ.get("DAILY_SILENT") == "1")   # 无配音版没有口型可对
    qa = dict(width=w, height=h, frames=frames, want_frames=T["frames"], duration=round(dur, 3), total=T["total"], lufs=lufs, lra=lra, true_peak=tp,
              mouth_best_lag=lag, mouth_corr=round(corr, 3), mouth_corr0=round(corr0, 3), subs=len(T["subs"]), ok=bool(ok))
    (e.work / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"成片 {e.final.name}：{w}×{h}，{dur:.2f} s（{frames} 帧，要 {T['frames']}），{e.final.stat().st_size / 1e6:.1f} MB，{lufs} LUFS，LRA {lra}，真峰值 {tp} dBFS；"
          f"口型×配音最佳偏移 {lag:+d} 帧（相关 {corr:.3f}）；字幕 {len(T['subs'])} 条；章节 {len(lines)} 段 → {'OK' if ok else 'QA 不通过'}")
    print(f"SRT：{e.ep / e.name}_双语字幕.srt / _中文字幕.srt / _英文字幕.srt；章节：{e.ep / (e.name + '_章节.txt')}")
    # 3:4 封面 = 成片第 0 帧（原封面居中放进边框）y450–1890 的裁切：抖音 / 小红书的竖封面用它
    from PIL import Image
    f0 = e.work / "frame0.png"
    run(["ffmpeg", "-v", "error", "-y", "-i", e.final, "-frames:v", "1", f0])
    e.cover34.parent.mkdir(exist_ok=True)
    Image.open(f0).convert("RGB").crop((0, 450, 1080, 1890)).save(e.cover34)
    print(f"3:4 封面 → {e.cover34}")
    if upload:
        sys.path.insert(0, str(SK / "scripts"))
        from daily import encode_upload
        vf = "scale=720:1560:flags=lanczos"                       # 1080×2340 在 ≈150 kbps 下会糊成块，缩到 720×1560 再编码
        logdir = e.ep / "制作" / "build"
        logdir.mkdir(parents=True, exist_ok=True)
        size, kbps = encode_upload(e.final, e.upload, logdir, "hevc", vf=vf)
        print(f"上传版 {e.upload.name}：{size / 1e6:.2f} MB（H.265，视频 {kbps} kbps，720×1560）→ B 站")
        size, kbps = encode_upload(e.final, e.upload264, logdir, "h264", vf=vf)
        print(f"上传版 {e.upload264.name}：{size / 1e6:.2f} MB（H.264，视频 {kbps} kbps，720×1560）→ 抖音 / 小红书")
    if not ok:
        sys.exit(3)


# ================================================================ main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dir")
    ap.add_argument("cmd", choices=["all", "data", "check", "lint", "stills", "mix", "render", "finish", "worker"])
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--workers", type=int)
    ap.add_argument("--bg", help="指定背景印花（pattern_color.png / pattern_ink.png / pattern_orange.png），默认每期随机")
    ap.add_argument("--upload", action="store_true", help="finish 时另出两个上传版（B 站 H.265 / 其余三个平台 H.264，各 ≤ 9 MB，720×1560）")
    ap.add_argument("--no-lint", action="store_true", help="all：字幕对齐检查有错也接着渲染（只在确认是误报时用，运行记录里写原因）")
    a = ap.parse_args()
    e = Ep(a.episode_dir)
    if a.cmd == "worker":
        worker(e, *[int(x) for x in a.rest])
        return
    if a.cmd in ("all", "render"):
        acquire_lock(e)
    if a.cmd == "data":
        build_data(e, a.bg)
    elif a.cmd == "check":
        sys.exit(cmd_check(e))
    elif a.cmd == "lint":
        sys.exit(cmd_lint(e))
    elif a.cmd == "stills":
        cmd_stills(e, [float(x) for x in a.rest])
    elif a.cmd == "mix":
        cmd_mix(e)
    elif a.cmd == "render":
        cmd_render(e, a.workers)
    elif a.cmd == "finish":
        cmd_finish(e, a.upload)
    elif a.cmd == "all":
        # 浏览器里量出超宽：只把超宽的那几条单独收紧 15 px 重拆（2026-10-06 以前是整片一起收紧，没超宽的条也全变了），最多 3 轮
        tf = e.work / "tight.json"
        tight = jload(tf, {}) or {}
        for attempt in range(3):
            build_data(e, a.bg, tight=tight)
            code, bad_units, fatal = cmd_check(e, want_bad=True)
            if code == 0:
                break
            if fatal or not bad_units:
                sys.exit("check 没通过（页面报错 / 标题缩到下限还超宽）：改台本的 vhook / headline 后重跑；不渲染")
            for u in bad_units:
                tight[u] = (tight.get(u) or SUB_MAX_PX) - 15
            tf.write_text(json.dumps(tight, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"check 没通过：只收紧这 {len(bad_units)} 条（{' / '.join(f'{u[:12]}… → {tight[u]} px' for u in bad_units)}）重来（第 {attempt + 2} 轮）")
        else:
            sys.exit("check 三轮都没通过（见上面）：给超宽的条写 vertical.cuts（多切一刀）或改台本的 vhook / headline 后重跑；不渲染")
        if cmd_lint(e) and not a.no_lint:
            sys.exit("字幕对齐检查没通过（见上面 ✗）：先改 vertical.cuts / 英文语序再跑 daily.py render（不用重配音）；确认是误报才加 --no-lint")
        cmd_stills(e, [])
        cmd_mix(e)
        cmd_render(e, a.workers)
        cmd_finish(e, a.upload)


if __name__ == "__main__":
    main()
