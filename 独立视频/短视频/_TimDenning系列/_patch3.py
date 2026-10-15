# -*- coding: utf-8 -*-
"""一次性补丁 3：第 13 条（忙）那一段里有 “heroin” 和 “su!cide” 两句（台本特意跳过的），页面截图不能把它们带进画面——
A_13 只截到 “Busyness is a red flag.”；A_13p = 第 79 段只要前两行（到 “Eliminate calendar events as quickly”）；A_13q = 第 80 段整段（“Busyness isn't cool…”）。
capture_series_pages.py 加 lesson 的 until / 新 kind para_lines；第 6 期把 L13 拆成 L13a + L13b。跑完可以删。"""
from pathlib import Path

H = Path(__file__).resolve().parent


def sub(path, old, new, count=1):
    s = path.read_text(encoding="utf-8")
    assert s.count(old) == count, f"{path.name} 里 {old[:50]!r} 出现 {s.count(old)} 次（要 {count} 次）"
    path.write_text(s.replace(old, new), encoding="utf-8")


sd = H / "series_data.py"
sub(sd, '''for _n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 19, 32, 34, 35, 36):
    PAGES[f"A_{_n}"] = dict(kind="lesson", n=_n)''', '''for _n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 17, 19, 32, 34, 35, 36):
    PAGES[f"A_{_n}"] = dict(kind="lesson", n=_n)
# 第 13 条：同一段里有 heroin / su!cide 两句（台本跳过的），只截不含它们的片段
PAGES["A_13"] = dict(kind="lesson", n=13, until="Busyness is a red flag.")            # 标题 + 第一句
PAGES["A_13p"] = dict(kind="para_lines", starts="The key to life is to not be busy", lines=2)   # “The key to life…” 这段只要前两行（到 Eliminate calendar events as quickly）
PAGES["A_13q"] = dict(kind="para_lines", starts="Busyness isn't cool.", lines=None)''')
sub(sd, '''        SC("L13", "第13条", PG("A_13", [
            M("It means your life is out of control and you have no focus", "N03", "失控", -0.3, "忙意味着你的生活失控，没有焦点"),
            M("Eliminate calendar events as quickly as possible", "N04", "删掉", -0.5, "尽快删掉日历上的安排"),
        ]), [
            L("N03", "忙，意味着不会专注，生活失控。",
              "Busyness means you can't focus and your life is out of control.",
              "忙，意味着不会专注，生活失控。"),
            L("N04", "做法：尽快删掉日历上的安排，把时间空出来过日子。",
              "The fix: delete calendar events as fast as you can, and make room for living.",
              "做法：尽快删掉日历上的安排，把时间空出来过日子。"),
        ], tag="第 13 条 · 忙", credit=CR_ART),''', '''        SC("L13a", "第13条·失控", PG("A_13q", [
            M("It means your life is out of control and you have no focus", "N03", "失控", -0.3, "忙意味着你的生活失控，没有焦点"),
        ], fit=True), [
            L("N03", "忙，意味着不会专注，生活失控。",
              "Busyness means you can't focus and your life is out of control.",
              "忙，意味着不会专注，生活失控。"),
        ], tag="第 13 条 · 忙", credit=CR_ART),
        SC("L13b", "第13条·做法", PG("A_13p", [
            M("Eliminate calendar events as quickly", "N04", "删掉", -0.5, "尽快删掉日历上的安排"),
        ], fit=True), [
            L("N04", "做法：尽快删掉日历上的安排，把时间空出来过日子。",
              "The fix: delete calendar events as fast as you can, and make room for living.",
              "做法：尽快删掉日历上的安排，把时间空出来过日子。"),
        ], tag="第 13 条 · 忙", credit=CR_ART),''')

cap = H / "capture_series_pages.py"
sub(cap, '''art_keys = [k for k in only if D.PAGES[k]["kind"] in ("top", "short", "lesson", "li_range")]''', '''art_keys = [k for k in only if D.PAGES[k]["kind"] in ("top", "short", "lesson", "li_range", "para_lines")]''')
sub(cap, '''                    if spec.get("h"):
                        y1 = y0 + spec["h"]''', '''                    if spec.get("h"):
                        y1 = y0 + spec["h"]
                    if spec.get("until"):                                     # 截到某一段的底下（避开后面带敏感词的段落）
                        y1 = pg.evaluate(PARA_JS, [spec["until"], 0])[1] + 14''')
sub(cap, '''                elif spec["kind"] == "li_range":''', '''                elif spec["kind"] == "para_lines":                             # 某一段的前 N 行（lines = None 整段）
                    top, bot = pg.evaluate(PARA_JS, [spec["starts"], spec["lines"] or 0])
                    y0, y1 = top - 10, bot + 6
                elif spec["kind"] == "li_range":''')
sub(cap, '''H1_JS = ''', '''# 找以某段文字开头的 <p>：返回 [段顶, 第 N 行的底]（N = 0 → 整段的底）
PARA_JS = r"""
([starts, nlines]) => {
  const f = s => s.replace(/[’‘]/g, "'").replace(/\\u00a0/g, ' ').trim().toLowerCase();
  const p = [...document.querySelectorAll('p')].find(x => f(x.textContent).startsWith(f(starts)));
  if (!p) throw new Error('找不到段落：' + starts);
  const r = document.createRange(); r.selectNodeContents(p);
  const rects = [...r.getClientRects()].filter(q => q.width > 2 && q.height > 2).map(q => [q.top + scrollY, q.bottom + scrollY]);
  const tops = [];
  for (const [t, b] of rects) { const k = tops.find(x => Math.abs(x.t - t) < 3); if (k) k.b = Math.max(k.b, b); else tops.push({t, b}); }
  tops.sort((a, b) => a.t - b.t);
  const pr = p.getBoundingClientRect();
  const use = nlines ? tops.slice(0, nlines) : tops;
  return [pr.top + scrollY, Math.max(...use.map(x => x.b))];
}
"""

H1_JS = ''')

cv = H / "series_covers.py"
print("ok")
