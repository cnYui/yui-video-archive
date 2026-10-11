p = "build_vertical.py"
s = open(p, encoding="utf-8").read()
s = s.replace('wh=(1290, 840), hl=(18, 52, 915, 172),', 'wh=(1290, 840), hl=(26, 64, 1116, 206),')
open(p, "w", encoding="utf-8").write(s)
# 要点卡字号 29 → 30
q = "index.html"
t = open(q, encoding="utf-8").read()
t = t.replace("font:800 29px/1.2 'Noto Sans SC'; color:var(--gray); white-space:nowrap; overflow:hidden; }", "font:800 30px/1.2 'Noto Sans SC'; color:var(--gray); white-space:nowrap; overflow:hidden; }")
open(q, "w", encoding="utf-8").write(t)
