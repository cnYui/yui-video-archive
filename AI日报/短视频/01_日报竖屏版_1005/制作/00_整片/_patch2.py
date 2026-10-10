p = "build_vertical.py"
s = open(p, encoding="utf-8").read()
a = s.index("    for k in list(CUTS):")
b = s.index("    chunks_all, over, soft = [], [], []")
s = s[:a] + s[b:]
s = s.replace("日报字幕 {len(items)} 条", "日报字幕 {len(raw)} 条")
open(p, "w", encoding="utf-8").write(s)
