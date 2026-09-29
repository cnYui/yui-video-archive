"""Handwriting glyph data for the whiteboard engine (hand.js): every character the episode writes by hand.

    python hand_glyphs.py <out.js> "文字一" "文字二" ...        # or: build_hand_js(texts, out_path) from Python

Writes `window.__HAND__ = {cjk, punct, lat, missing}` (plain JSON inside a script, loaded before hand.js):
  cjk[字]   = strokes in stroke order; each stroke = flat [x, y, x, y, ...] in the 1024 box, origin = box centre,
              y DOWN (Make Me a Hanzi medians, converted; brush entry hooks trimmed, near-duplicate points dropped)
  punct[字] = the same for hand-made CJK punctuation (、，。：；！？（）etc. — the stroke data has none), plus
              {"adv": cell width in boxes}
  lat       = {"xh": x-height in font units, "g": {ch: {"a": advance, "s": strokes}}} from the single-line font
              EMS Tech (single-stroke "Architects Daughter"); strokes in font units, origin = glyph origin on the
              baseline, y DOWN; plotter retraces and pen travel removed, letters written in a natural order
  missing   = characters found nowhere (hand.js leaves a gap and warns; make_episode reports them)
Layout, jitter, smoothing and timing are done in hand.js (so scenes can place text freely).

Data (read only): D:/大疆/AI日报/素材/手写/hanzi-writer-data (Arphic Public License, ARPHICPL.TXT there) and
hersheytext/svg_fonts/EMSTech.svg (SIL OFL). Geometry helpers come from the 2026-09-28 sample
(_测试_手写动画_20260928/build.py), which was checked stroke by stroke.
"""
import html
import json
import math
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HAND = Path(r"D:/大疆/AI日报/素材/手写")
HANZI_DIR = HAND / "hanzi-writer-data"
FONT_SVG = HAND / "hersheytext" / "svg_fonts" / "EMSTech.svg"
PEN_OVER_XH = 0.152        # pen width / x-height (hand.js: pen 7 % of the CJK box, x-height 46 % of it)


# ---------------------------------------------------------------- geometry (points are (x, y) tuples)
def dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def lerp(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def turn_deg(a, b, c):
    v1, v2 = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
    n1, n2 = math.hypot(*v1), math.hypot(*v2)
    if n1 < 1e-9 or n2 < 1e-9:
        return 0.0
    return math.degrees(math.acos(max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))))


def poly_len(pts):
    return sum(dist(a, b) for a, b in zip(pts, pts[1:]))


def dedupe(pts, eps):
    out = [pts[0]]
    for p in pts[1:-1]:
        if dist(out[-1], p) >= eps:
            out.append(p)
    if len(out) > 1 and dist(out[-1], pts[-1]) < eps:
        out[-1] = pts[-1]
    else:
        out.append(pts[-1])
    return out


def bez(seg, t):
    a, b, c, d = seg
    s = 1 - t
    return (s * s * s * a[0] + 3 * s * s * t * b[0] + 3 * s * t * t * c[0] + t * t * t * d[0],
            s * s * s * a[1] + 3 * s * s * t * b[1] + 3 * s * t * t * c[1] + t * t * t * d[1])


# ---------------------------------------------------------------- Chinese
def trim_entry(pts, budget=75.0, min_turn=20.0):
    """Drop the Kai brush entry hook (a short lead-in turning away from the stroke): a marker just starts."""
    pts = list(pts)
    while len(pts) > 2:
        l0 = dist(pts[0], pts[1])
        if l0 < budget and turn_deg(pts[0], pts[1], pts[2]) > min_turn:
            pts.pop(0)
            budget -= l0
        else:
            break
    return pts


def cjk_glyph(ch):
    f = HANZI_DIR / f"{ch}.json"
    if not f.exists():
        return None
    data = json.loads(f.read_text(encoding="utf-8"))
    out = []
    for med in data["medians"]:
        pts = [(float(x) - 512.0, 388.0 - float(y)) for x, y in med]      # box centre origin, y down
        pts = trim_entry(dedupe(pts, 14.0))
        out.append([round(v) for p in pts for v in p])
    return out


# ---------------------------------------------------------------- punctuation (drawn here: the stroke data has none)
# cell-centre origin, y down, 1024 box units; the line's CJK characters span about y -420..420
def _arc(cx, cy, rx, ry, a0, a1, n=12):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
            for k in range(n + 1)]


PUNCT = {
    "，": (0.5, [[(-40, 250), (-50, 320), (-100, 400)]]),
    "、": (0.5, [[(-90, 240), (-20, 330)]]),
    "。": (0.5, [_arc(-40, 300, 70, 70, -100, 250, 14)]),
    "：": (0.5, [[(0, -170), (6, -140)], [(0, 170), (6, 200)]]),
    "；": (0.5, [[(0, -170), (6, -140)], [(8, 170), (0, 250), (-40, 330)]]),
    "！": (0.5, [[(0, -390), (4, -100), (0, 170)], [(0, 320), (6, 350)]]),
    "？": (0.62, [[(-150, -250), (-110, -360), (0, -400), (120, -350), (150, -240), (80, -140), (10, -60), (0, 70)],
                  [(0, 300), (6, 330)]]),
    "（": (0.5, [[(110, -430), (-10, -250), (-60, 0), (-10, 250), (110, 430)]]),
    "）": (0.5, [[(-110, -430), (10, -250), (60, 0), (10, 250), (-110, 430)]]),
    "“": (0.5, [[(60, -400), (20, -300)], [(170, -400), (130, -300)]]),
    "”": (0.5, [[(-130, -400), (-170, -300)], [(-20, -400), (-60, -300)]]),
    "《": (0.6, [[(100, -380), (-120, 0), (100, 380)], [(230, -380), (10, 0), (230, 380)]]),
    "》": (0.6, [[(-230, -380), (-10, 0), (-230, 380)], [(-100, -380), (120, 0), (-100, 380)]]),
    "—": (1.0, [[(-480, 0), (0, -10), (480, 0)]]),
    "…": (1.0, [[(-310, 60), (-300, 75)], [(0, 60), (10, 75)], [(310, 60), (320, 75)]]),
    "·": (0.4, [[(0, 0), (8, 14)]]),
    "≤": (0.9, [[(260, -300), (-240, -80), (260, 140)], [(-240, 320), (260, 320)]]),
    "≥": (0.9, [[(-260, -300), (240, -80), (-260, 140)], [(-260, 320), (240, 320)]]),
    "～": (0.8, [[(-300, 30), (-160, -70), (0, 0), (160, 70), (300, -30)]]),
    "→": (1.0, [[(-400, 0), (400, 0)], [(240, -150), (400, 0), (240, 150)]]),
    "×": (0.7, [[(-200, -200), (200, 200)], [(200, -200), (-200, 200)]]),
    "✓": (0.9, [[(-300, 20), (-90, 260), (330, -330)]]),
}
FULL2LAT = {"％": "%", "＋": "+", "－": "-", "／": "/", "．": ".", "＝": "=", "＜": "<", "＞": ">", "～": "~"}


# ---------------------------------------------------------------- Latin: single-line SVG font
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


def parse_path(d, curve_steps=8):
    toks = re.findall(r"[MLCZmlcz]|" + NUM, d)
    subs, cur, cmd, i = [], None, None, 0
    pos = start = (0.0, 0.0)

    def num():
        nonlocal i
        i += 1
        return float(toks[i - 1])

    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd in "Zz":
                if cur:
                    cur.append(start)
                pos = start
                continue
        if cmd == "M":
            pos = start = (num(), num())
            cur = [pos]
            subs.append(cur)
            cmd = "L"
        elif cmd == "L":
            pos = (num(), num())
            cur.append(pos)
        elif cmd == "C":
            c1, c2, p = (num(), num()), (num(), num()), (num(), num())
            cur += [bez((pos, c1, c2, p), k / curve_steps) for k in range(1, curve_steps + 1)]
            pos = p
        else:
            raise ValueError(f"unsupported path command {cmd!r}")
    return subs


def split_reversals(pts, deg=150.0):
    pieces, cur = [], [pts[0]]
    for i in range(1, len(pts) - 1):
        cur.append(pts[i])
        if turn_deg(pts[i - 1], pts[i], pts[i + 1]) > deg:
            pieces.append(cur)
            cur = [pts[i]]
    cur.append(pts[-1])
    pieces.append(cur)
    return pieces


def resample(pts, step):
    out, acc, nxt = [(0.0, pts[0])], 0.0, step
    for a, b in zip(pts, pts[1:]):
        seg = dist(a, b)
        while seg > 0 and nxt <= acc + seg:
            out.append((nxt, lerp(a, b, (nxt - acc) / seg)))
            nxt += step
        acc += seg
    out.append((acc, pts[-1]))
    return out


def seg_dist(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    l2 = vx * vx + vy * vy
    u = 0.0 if l2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / l2))
    return math.hypot(p[0] - a[0] - u * vx, p[1] - a[1] - u * vy)


def near(p, polys, tol):
    return any(seg_dist(p, a, b) <= tol for q in polys for a, b in zip(q, q[1:]))


def cut_from(pts, s):
    acc = 0.0
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        seg = dist(a, b)
        if acc + seg >= s:
            return [lerp(a, b, (s - acc) / seg if seg else 0.0)] + pts[i + 1:]
        acc += seg
    return pts[-2:]


def glyph_strokes(d, tol):
    """Plotter glyph -> pen strokes in a natural order (split retraces, drop pen travel over ink, trim lead-ins)."""
    pieces = []
    for sp in parse_path(d):
        sp = dedupe(sp, 2.0)
        if len(sp) >= 2:
            pieces += split_reversals(sp)
    keep = list(pieces)
    for pc in sorted(pieces, key=poly_len):
        others = [q for q in keep if q is not pc]
        if others and all(near(p, others, tol) for _, p in resample(pc, tol / 3)):
            keep.remove(pc)
    out = []
    for pc in keep:
        if out:
            first_new = next((s for s, p in resample(pc, tol / 4) if not near(p, out, tol)), None)
            if first_new is None:
                continue
            if first_new > tol:
                pc = cut_from(pc, first_new - 0.8 * tol)
        out.append(pc)
    return out


_FONT = None


def latin_font():
    global _FONT
    if _FONT is None:
        s = FONT_SVG.read_text(encoding="utf-8")
        default_adv = float(re.search(r'<font[^>]*horiz-adv-x="([^"]+)"', s).group(1))
        glyphs = {}
        for m in re.finditer(r"<glyph\s+([^>]*?)/>", s, re.S):
            a = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
            glyphs[html.unescape(a.get("unicode", ""))] = (float(a.get("horiz-adv-x", default_adv)), a.get("d", ""))
        tops = sorted(max(y for sp in parse_path(glyphs[ch][1]) for _, y in sp) for ch in "acemnorsuvwxz"
                      if glyphs.get(ch, (0, ""))[1])
        _FONT = {"glyphs": glyphs, "xh": tops[len(tops) // 2]}
    return _FONT


def latin_glyph(ch):
    f = latin_font()
    if ch not in f["glyphs"]:
        return None
    adv, d = f["glyphs"][ch]
    tol = 0.5 * PEN_OVER_XH * f["xh"]
    strokes = []
    for pc in (glyph_strokes(d, tol) if d else []):
        pc = dedupe(pc, 0.02 * f["xh"])
        strokes.append([round(v) for x, y in pc for v in (x, -y)])        # y down
    return {"a": round(adv), "s": strokes}


# ---------------------------------------------------------------- build
def collect(texts):
    """-> dict ready for window.__HAND__ with every character of `texts` (spaces ignored)."""
    chars = sorted({ch for t in texts for ch in str(t) if not ch.isspace()})
    cjk, punct, lat, missing = {}, {}, {}, []
    for ch in chars:
        if ch in PUNCT:
            adv, strokes = PUNCT[ch]
            punct[ch] = {"adv": adv, "s": [[round(v) for p in st for v in p] for st in strokes]}
            continue
        g = cjk_glyph(ch) if ord(ch) > 0x2E7F else None
        if g:
            cjk[ch] = g
            continue
        lg = latin_glyph(FULL2LAT.get(ch, ch))
        if lg and lg["s"]:
            lat[ch] = lg
            continue
        missing.append(ch)
    return {"cjk": cjk, "punct": punct, "lat": {"xh": round(latin_font()["xh"]), "g": lat}, "missing": missing}


def build_hand_js(texts, out_path):
    data = collect(texts)
    Path(out_path).write_text(
        "// generated by hand_glyphs.py — handwriting strokes for this episode (Make Me a Hanzi data: Arphic Public\n"
        "// License, see 素材/手写/hanzi-writer-data/ARPHICPL.TXT; Latin: EMS Tech, SIL OFL). Do not edit.\n"
        "window.__HAND__ = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    d = build_hand_js(sys.argv[2:], sys.argv[1])
    print(f"{sys.argv[1]}: {len(d['cjk'])} 汉字, {len(d['punct'])} 标点, {len(d['lat']['g'])} 拉丁字符"
          + (f"；缺：{''.join(d['missing'])}" if d["missing"] else ""))
