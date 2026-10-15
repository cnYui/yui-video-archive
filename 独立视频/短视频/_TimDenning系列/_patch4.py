# -*- coding: utf-8 -*-
"""一次性补丁 4：单句 / 短列表片段（A_13p / A_13q / A_21 / A_28 / A_29）改用 420 宽视口截（文字折成几行、放大约 1.5 倍，做成“引语卡”）。
capture_series_pages.py 支持 PAGES[key]["vw"]；封面候选里 A_29 的裁切范围放宽。跑完可以删。"""
from pathlib import Path

H = Path(__file__).resolve().parent


def sub(path, old, new, count=1):
    s = path.read_text(encoding="utf-8")
    assert s.count(old) == count, f"{path.name} 里 {old[:60]!r} 出现 {s.count(old)} 次（要 {count} 次）"
    path.write_text(s.replace(old, new), encoding="utf-8")


cap = H / "capture_series_pages.py"
sub(cap, '''        def ctx_page(url, wait=3000):
            ctx = b.new_context(viewport={"width": VW, "height": 1000}, device_scale_factor=DSF, locale="en-US")''', '''        def ctx_page(url, wait=3000, vw=VW):
            ctx = b.new_context(viewport={"width": vw, "height": 1000}, device_scale_factor=DSF, locale="en-US")''')
sub(cap, '''        art_keys = [k for k in only if D.PAGES[k]["kind"] in ("top", "short", "lesson", "li_range", "para_lines")]
        if art_keys:
            ctx, pg = ctx_page(D.SUB_URL)''', '''        art_all = [k for k in only if D.PAGES[k]["kind"] in ("top", "short", "lesson", "li_range", "para_lines")]
        groups = {}
        for k in art_all:                                                   # 按视口宽度分组（单句片段用 420 宽，其余 640）
            groups.setdefault(D.PAGES[k].get("vw", VW), []).append(k)
        for vw_, art_keys in groups.items():
            ctx, pg = ctx_page(D.SUB_URL, 3000, vw_)''')
sub(cap, '''                shoot(k, pg, {"x": 0, "y": y0, "width": VW, "height": y1 - y0}, D.SUB_URL)''', '''                shoot(k, pg, {"x": 0, "y": y0, "width": vw_, "height": y1 - y0}, D.SUB_URL)''')

sd = H / "series_data.py"
sub(sd, 'PAGES["A_13p"] = dict(kind="para_lines", starts="The key to life is to not be busy", lines=2)', 'PAGES["A_13p"] = dict(kind="para_lines", starts="The key to life is to not be busy", lines=2, vw=420)')
sub(sd, 'PAGES["A_13q"] = dict(kind="para_lines", starts="Busyness isn\'t cool.", lines=None)', 'PAGES["A_13q"] = dict(kind="para_lines", starts="Busyness isn\'t cool.", lines=None, vw=420)')
sub(sd, '"A_21": dict(kind="li_range", first="21.", last="22.", head=True),', '"A_21": dict(kind="li_range", first="21.", last="22.", head=True, vw=420),')
sub(sd, '"A_28": dict(kind="li_range", first="28.", last="28."),', '"A_28": dict(kind="li_range", first="28.", last="28.", vw=420),')
sub(sd, '"A_29": dict(kind="li_range", first="29.", last="29."),', '"A_29": dict(kind="li_range", first="29.", last="29.", vw=420),')

cv = H / "series_covers.py"
sub(cv, 'src=("page", "A_29", 0, 163, ["Spend more time with your parents than feels normal"])', 'src=("page", "A_29", 0, 2000, ["Spend more time with your parents than feels normal"])')
print("patched 4")
