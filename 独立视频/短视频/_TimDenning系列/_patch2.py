# -*- coding: utf-8 -*-
"""一次性补丁 2：A_short 拆成 A_21 / A_28 / A_29 / A_31 单独截图（不把比特币 / 戒酒 / 死亡体验那几条原文带进画面）；A_36 只截到 540 CSS px；
页面底部留白 260 → 130；第 5 期派对图收紧到只留脸。跑完可以删。"""
from pathlib import Path

H = Path(__file__).resolve().parent


def sub(path, old, new, count=1):
    s = path.read_text(encoding="utf-8")
    assert s.count(old) == count, f"{path.name} 里 {old[:50]!r} 出现 {s.count(old)} 次（要 {count} 次）"
    path.write_text(s.replace(old, new), encoding="utf-8")


sd = H / "series_data.py"
sub(sd, '''    "A_short": dict(kind="short"),
''', '''    "A_21": dict(kind="li_range", first="21.", last="22.", head=True),          # “Shorter lessons”标题 + 第 21、22 条（只截这两条，不带后面的第 23 条比特币）
    "A_28": dict(kind="li_range", first="28.", last="28."),
    "A_29": dict(kind="li_range", first="29.", last="29."),
    "A_31": dict(kind="lesson", n=31, h=430),
''')
sub(sd, "A_short = “Shorter lessons”到第 32 条标题（含第 31 条）", "A_21 / A_28 / A_29 = “Shorter lessons”列表里单条截图（避开 23 比特币 / 27 戒酒 / 30 死亡体验）；A_31 = 第 31 条")
# 第 5 期
sub(sd, '''        SC("L29", "第29条", PG("A_short", [
            M("Spend more time with your parents than feels normal", "N12", "陪父母", -0.2, "花在父母身上的时间，要比你觉得正常的更多"),
            M("Soon they'll be gone", "N12", "很快", -0.1, "他们很快就不在了"),
        ]), [''', '''        SC("L29", "第29条", PG("A_29", [
            M("Spend more time with your parents than feels normal", "N12", "陪父母", -0.2, "花在父母身上的时间，要比你觉得正常的更多"),
            M("Soon they'll be gone", "N12", "很快", -0.1, "他们很快就不在了"),
        ], fit=True), [''')
sub(sd, '''        SC("E1", "金句", PG("A_short", [
            M("Soon they'll be gone", "N16", "不会等", -0.4, "他们很快就不在了"),
        ]), [''', '''        SC("E1", "金句", PG("A_29", [
            M("Soon they'll be gone", "N16", "不会等", -0.4, "他们很快就不在了"),
        ], fit=True), [''')
sub(sd, 'PH("party", zoom=0.08, fx=0.50, fy=0.30)', 'PH("party", zoom=0.06, base=1.55, fx=0.46, fy=0.27)')
# 第 6 期：L31 拆成 L28 + L31
sub(sd, '''        SC("L31", "第28、31条", PG("A_short", [
            M("Video games are fine when you're younger", "N09", "游戏", -0.1, "第 28 条：年轻时玩游戏无妨，年纪大了就是吃时间的黑洞"),
            M("Flow states are more important than productivity", "N10", "心流", -0.3, "第 31 条：心流比效率更重要"),
            M("Feeling like 8 hours happened in 1 hour will feel better", "N11", "8 小时", -0.4, "感觉 8 小时像 1 小时，会好得多"),
        ]), [
            L("N09", "第二十八条：游戏年轻时无妨，年纪大了就是吃时间的黑洞。",
              "Lesson 28: games are fine when you're young, but later they're a time suck.",
              "第二十八条：游戏年轻时无妨，年纪大了就是吃时间的黑洞。"),
            L("N10"''', '''        SC("L28", "第28条", PG("A_28", [
            M("Video games are fine when you're younger", "N09", "游戏", -0.1, "第 28 条：年轻时玩游戏无妨，年纪大了就是吃时间的黑洞"),
        ], fit=True), [
            L("N09", "第二十八条：游戏年轻时无妨，年纪大了就是吃时间的黑洞。",
              "Lesson 28: games are fine when you're young, but later they're a time suck.",
              "第二十八条：游戏年轻时无妨，年纪大了就是吃时间的黑洞。"),
        ], tag="第 28 条 · 游戏", credit=CR_ART),
        SC("L31", "第31条", PG("A_31", [
            M("Flow states are more important than productivity", "N10", "心流", -0.3, "第 31 条：心流比效率更重要"),
            M("Feeling like 8 hours happened in 1 hour will feel better", "N11", "8 小时", -0.4, "感觉 8 小时像 1 小时，会好得多"),
        ]), [
            L("N10"''')
sub(sd, '''        SC("C1", "泼冷水", PG("A_short", [
            M("Turn off news and politics to naturally increase your IQ", "N12", "第二十一条", 0.0, "第 21 条：关掉新闻和政治，智商会自然升高"),
        ]), [''', '''        SC("C1", "泼冷水", PG("A_21", [
            M("Turn off news and politics to naturally increase your IQ", "N12", "第二十一条", 0.0, "第 21 条：关掉新闻和政治，智商会自然升高"),
        ], fit=True), [''')

cap = H / "capture_series_pages.py"
sub(cap, '''        art_keys = [k for k in only if D.PAGES[k]["kind"] in ("top", "short", "lesson")]''', '''        art_keys = [k for k in only if D.PAGES[k]["kind"] in ("top", "short", "lesson", "li_range")]''')
sub(cap, '''                elif spec["kind"] == "short":
                    y0, y1 = short_y - 24, lessons[32] - 8
                else:''', '''                elif spec["kind"] == "short":
                    y0, y1 = short_y - 24, lessons[32] - 8
                elif spec["kind"] == "li_range":                              # “Shorter lessons”列表里的单条（或前两条）：按 li 的位置裁
                    a = pg.evaluate("(p) => { const li = [...document.querySelectorAll('li')].find(x => x.textContent.trim().startsWith(p)); const r = li.getBoundingClientRect(); return [r.top + scrollY, r.bottom + scrollY]; }", spec["first"])
                    z = pg.evaluate("(p) => { const li = [...document.querySelectorAll('li')].find(x => x.textContent.trim().startsWith(p)); const r = li.getBoundingClientRect(); return [r.top + scrollY, r.bottom + scrollY]; }", spec["last"])
                    y0 = (short_y - 24) if spec.get("head") else a[0] - 22
                    y1 = z[1] + 22
                else:''')
sub(cap, '''                    n = spec["n"]
                    y0 = lessons[n] - 24
                    y1 = min(nxt[n] - 8, y0 + 2600)''', '''                    n = spec["n"]
                    y0 = lessons[n] - 24
                    y1 = min(nxt[n] - 8, y0 + 2600)
                    if spec.get("h"):
                        y1 = y0 + spec["h"]''')
sub(cap, '''                        y1 = y0 + 760''', '''                        y1 = y0 + 540''')

lib = H / "engine_lib" / "scenes_lib.js"
sub(lib, "PADB = opt.fit ? 0 : 260;", "PADB = opt.fit ? 0 : 130;")
print("patched 2")
