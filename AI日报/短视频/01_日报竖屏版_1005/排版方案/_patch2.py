p = "make_daily_layouts.py"
s = open(p, encoding="utf-8").read()
s = s.replace('"用户 2026-10-04：三张印花都进随机池，每期视频随机挑一张；这里把 9 种组合都摆出来，看哪个排版配哪张更顺眼"', '"三张印花都在随机池里，每期视频随机挑一张；9 种组合都摆出来，看哪个更顺眼"')
open(p, "w", encoding="utf-8").write(s)
