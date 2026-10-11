# -*- coding: utf-8 -*-
r"""把场景的画面需求自动拆成上框 / 下框的选段。series_data 里一个场景可以这样写（三选一，写了 top / bottom 就用它们）：

  dict(id="S2", lines=[...], at=14.0)                       # 锚点：素材 a 的 14 s 起（按本场景需要的时长，从这里往后顺着取，取到下一个锚点为止）
  dict(id="S2", lines=[...], at=("b", 14.0))                # 指定素材
  dict(id="S2", lines=[...], win=[("a", 14.0, 36.0)])       # 明确的窗口（可以写几段）
  dict(id="S2", lines=[...], top=[...], bottom=[...])       # 全部手写（选段字段见 gen_episode.py）

规则：
  - 窗口里按分镜 json 切出的镜头段，离边界留 safe 边距（避开转场帧），不足 0.6 s 的丢掉；
  - 整屏标题卡不用：type == card 的、以及 TEXT_CARDS 里登记的（颜色上判成 other 的文字卡，如 “Terminal” “Context” “Commands”）；cards=True 才收；
  - 人脸镜头进上框，其余（终端 / 页面 / 图示）进下框；某个框不够长，就从另一个框匀整段过来，或把最长的一段切成前后两半（互不重叠）；
  - at 模式下窗口长度 = 2 × 本场景时长 + 余量（只数能用的镜头），所以按课程原来的顺序一路往后用，不会重叠。
"""
import json
from pathlib import Path

_SEG = {}

# 分镜分类器判成 other 的纯文字标题卡（时间区间，秒）。按 视频文件名的前缀 登记。
TEXT_CARDS = {
    "CC101-01": [(32.5, 35.0), (55.5, 57.5), (103.5, 106.25)],
    "CC101-02": [(10.25, 14.0), (61.25, 63.75), (85.0, 87.13), (110.25, 112.5)],
    "CC101-03": [(9.75, 13.0), (61.0, 63.5), (90.25, 92.25), (109.75, 112.0), (144.0, 147.5)],
    "CC101-04": [(38.5, 41.0)],
    "CC101-05": [(19.0, 22.25), (143.0, 145.75)],
    "CC101-06": [(36.5, 39.75), (56.25, 58.25), (125.75, 128.25)],
    "CC101-08": [(11.25, 14.25), (53.25, 55.5), (93.0, 95.5), (120.25, 121.75)],
    "CC101-09": [(28.61, 32.25), (118.75, 121.54)],
    "CC101-10": [(30.28, 33.45), (63.25, 66.28), (100.47, 103.6), (144.48, 147.81)],
    "CC101-11": [(33.2, 36.2), (72.8, 74.8), (105.2, 106.8), (123.2, 125.2)],
    "CCA-04": [(21.8, 24.0), (117.0, 119.5)],
    "CCA-05": [(14.2, 16.2), (85.7, 88.2), (141.8, 144.2)],
}


def segs_of(video_dir, fname):
    stem = Path(fname).stem
    if stem not in _SEG:
        p = Path(video_dir).parent / "分镜" / f"{stem}.json"
        _SEG[stem] = json.loads(p.read_text(encoding="utf-8"))["segments"]
    return _SEG[stem]


# 这两条是旁白 + 动画的课，没有真人出镜；分类器把橙底终端判成了 face，当成非人脸用（可以放慢、可以拆给两个框）
NO_FACE = ("CCA-04", "CCA-05")


def _video_dur(video_dir, fname):
    segs = segs_of(video_dir, fname)
    return segs[-1]["e"]


def is_text_card(fname, s):
    stem = Path(fname).stem
    for k, lst in TEXT_CARDS.items():
        if stem.startswith(k):
            for a, b in lst:
                ov = min(s["e"], b) - max(s["s"], a)
                if ov > 0.5 * (s["e"] - s["s"]):
                    return True
    return False


def usable_pieces(d, video_dir, src, w0, w1, cards=False, endcard=False):
    """窗口 [w0, w1] 里能用的镜头段（已按 safe 边距收窄）。d["skip"] = [(src, a, b)] 是整期都不用的区间（比如画面里有过时的东西）。"""
    out = []
    fname = d["src"][src]
    skips = [(a, b) for (s2, a, b) in d.get("skip", []) if s2 == src]
    dur = _video_dur(video_dir, fname)
    nofa = any(Path(fname).stem.startswith(k) for k in NO_FACE)
    for s in segs_of(video_dir, fname):
        if is_text_card(fname, s) or (not cards and s["type"] == "card"):
            continue
        if not endcard and s["type"] in ("card", "other") and (s["e"] <= 5.0 or s["s"] >= dur - 7.0):      # 片头标题卡、片尾 claude.com/courses 卡
            continue
        if any(min(s["e"], b) - max(s["s"], a) > 0.3 * (s["e"] - s["s"]) for a, b in skips):
            continue
        a, b = max(s["safe_in"], w0), min(s["safe_out"], w1)
        if b - a < 0.6:
            continue
        out.append(dict(src=src, a=round(a, 2), b=round(b, 2), face=(s["type"] == "face" and not nofa), i=s["i"]))
    return out


def _cap(spans):
    return sum(s["b"] - s["a"] for s in spans)


def _len(p):
    return p["b"] - p["a"]


def balance(top, bot, need):
    """让两个框都尽量够 need 秒：从富余的一边整段或切尾巴匀过去（只动富余的部分，不让捐出方不够）。"""
    for _ in range(10):
        ct, cb = _cap(top), _cap(bot)
        if ct >= need - 0.05 and cb >= need - 0.05:
            break
        if ct < need - 0.05 and cb >= need - 0.05:
            recv, donor, deficit, room = top, bot, need - ct, cb - need
        elif cb < need - 0.05 and ct >= need - 0.05:
            recv, donor, deficit, room = bot, top, need - cb, ct - need
        else:                                           # 两边都不够：匀成一样长
            mean = (ct + cb) / 2
            if ct > cb:
                recv, donor, deficit, room = bot, top, mean - cb, ct - mean
            else:
                recv, donor, deficit, room = top, bot, mean - ct, cb - mean
        if room < 0.6 or not donor:
            break
        want = min(deficit, room)
        # 先找一整段刚好能给的（长度 ≤ want + 0.5 且最接近 want）
        whole = [p for p in donor if _len(p) <= want + 0.5 and _len(p) >= min(want, 0.6)]
        if whole:
            p = max(whole, key=_len)
            donor.remove(p)
            recv.append(p)
        else:                                           # 否则把最长的一段切个尾巴
            p = max(donor, key=_len)
            amount = min(want, _len(p) - 0.6)
            if amount < 0.6:
                break
            cut = round(p["b"] - amount, 2)
            recv.append(dict(src=p["src"], a=round(cut + 0.1, 2), b=p["b"], face=p["face"], i=p["i"]))
            p["b"] = cut
        recv.sort(key=lambda x: (x["src"], x["a"]))
        donor.sort(key=lambda x: (x["src"], x["a"]))


def spans_from_window(d, video_dir, wins, T, cards=False):
    """窗口 → (top, bottom)。"""
    pool = []
    for w in wins:
        pool += usable_pieces(d, video_dir, w[0], w[1], w[2], cards)
    top = [p for p in pool if p["face"]]
    bot = [p for p in pool if not p["face"]]
    balance(top, bot, T + 0.2)
    clean = lambda lst: [{k: v for k, v in p.items() if k != "i"} for p in lst]      # 保留 face 标记：配音不够长时只放慢非人脸段
    return clean(top), clean(bot)


def _at(sc):
    a = sc.get("at")
    if a is None:
        return None
    return a if isinstance(a, tuple) else ("a", a)


def auto_window(d, video_dir, sc, T, next_at, slack=1.04):
    """从锚点起往后取够 2T·slack 的可用镜头，最远到 next_at（下一个锚点）。返回 [(src, w0, w1)]。"""
    src, t0 = _at(sc)
    end = next_at if (next_at is not None and next_at > t0) else 1e9
    need = 2 * T * slack + 0.4
    acc, w1 = 0.0, t0
    for p in usable_pieces(d, video_dir, src, t0, end, sc.get("cards", False), sc.get("endcard", False)):
        ln = p["b"] - p["a"]
        if acc + ln >= need:
            w1 = p["a"] + max(need - acc, 0.7) + 0.12            # 最后一段只取需要的那部分，别把整段吃掉
            acc = need
            break
        acc += ln
        w1 = p["b"] + 0.12
    return [(src, t0, min(w1, end))]


def _leftover(d, video_dir, src, used, cards):
    """整条素材里还没被任何场景用掉的可用镜头（已把用过的区间挖掉）。"""
    out = []
    for p in usable_pieces(d, video_dir, src, 0, 1e9, cards):
        segs = [(p["a"], p["b"])]
        for ua, ub in used.get(src, []):
            nxt = []
            for a, b in segs:
                if ub <= a or ua >= b:
                    nxt.append((a, b))
                    continue
                if ua - a >= 0.6:
                    nxt.append((a, ua - 0.1))
                if b - ub >= 0.6:
                    nxt.append((ub + 0.1, b))
            segs = nxt
        for a, b in segs:
            if b - a >= 0.6:
                out.append(dict(p, a=round(a, 2), b=round(b, 2)))
    return out


def resolve_all(d, video_dir, Ts):
    """整期：{场景 id: (top, bottom)}。Ts = {场景 id: 本场景要的秒数}。
    先按 at / win 取各场景自己的窗口；哪个框不够长，再从整条素材里没被用过的镜头里就近借（人脸优先给上框、其余优先给下框）。"""
    scenes = d["scenes"]
    out, pools, anchor, used = {}, {}, {}, {}

    def mark(lst):
        for p in lst:
            used.setdefault(p["src"], []).append((p["a"], p.get("b", p["a"])))      # 手写选段里的定格（hold）没有 b

    for k, sc in enumerate(scenes):
        sid, T = sc["id"], Ts[sc["id"]]
        if "top" in sc and "bottom" in sc:
            out[sid] = (sc["top"], sc["bottom"])
            mark(sc["top"] + sc["bottom"])
            continue
        if "win" in sc:
            wins = list(sc["win"]) + list(sc.get("more", []))
            anchor[sid] = (sc["win"][0][0], sc["win"][0][1])
        elif "at" in sc:
            src, t0 = _at(sc)
            nxt = None
            for later in scenes[k + 1:]:
                a2 = _at(later)
                if a2 and a2[0] == src:
                    nxt = a2[1]
                    break
            if sc.get("until") is not None:
                nxt = sc["until"] if nxt is None or nxt <= t0 else min(nxt, sc["until"])
            wins = auto_window(d, video_dir, sc, T, nxt) + list(sc.get("more", []))
            anchor[sid] = (src, t0)
        else:
            raise ValueError(f"场景 {sid} 没有 at / win / top+bottom")
        pool = []
        for w in wins:
            pool += usable_pieces(d, video_dir, w[0], w[1], w[2], sc.get("cards", False), sc.get("endcard", False))
        pools[sid] = pool
        mark(pool)

    # 第二遍：不够的框就近借
    for sc in scenes:
        sid = sc["id"]
        if sid not in pools:
            continue
        T, need = Ts[sid], Ts[sid] + 0.2
        pool = pools[sid]
        src0, t0 = anchor[sid]
        for _ in range(14):
            top = [dict(p) for p in pool if p["face"]]
            bot = [dict(p) for p in pool if not p["face"]]
            balance(top, bot, need)
            ct, cb = _cap(top), _cap(bot)
            if ct >= need - 0.3 and cb >= need - 0.3:
                break
            want_face = ct < cb
            cand = []
            for s in sorted({p["src"] for p in pool} | {src0}):
                cand += _leftover(d, video_dir, s, used, sc.get("cards", False))
            if not cand:
                break
            cand.sort(key=lambda p: (p["face"] != want_face, abs((p["a"] + p["b"]) / 2 - t0) if p["src"] == src0 else 1e6))
            got = cand[0]
            if got["b"] - got["a"] > 4.0 + (need - min(ct, cb)):       # 别一口借太长
                got = dict(got, b=round(got["a"] + 4.0 + (need - min(ct, cb)), 2))
            pool.append(got)
            mark([got])
        top = [dict(p) for p in pool if p["face"]]
        bot = [dict(p) for p in pool if not p["face"]]
        balance(top, bot, need)
        clean = lambda lst: [{k: v for k, v in p.items() if k != "i"} for p in lst]
        out[sid] = (clean(top), clean(bot))
    return out
