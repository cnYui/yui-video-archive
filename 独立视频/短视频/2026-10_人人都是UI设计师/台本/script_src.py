# -*- coding: utf-8 -*-
"""台本数据源：《人人都是 UI 设计师》竖屏短视频（长视频同一篇文章的短版；文章：龙海 @longhaiqwe123，2026-10-03；规则出自《Refactoring UI》）。

  python script_src.py        生成 录制稿.json、plan.json、台本.md、../制作/02_配音/say_lines.txt，并检查字幕宽度 / 估时

每句三栏：zh = 字幕（中文一行）、say = 配音念的字（数字写汉字）、en = 英文字幕。say 缺省 = zh。
口径（和长视频一致，数字一律取自 长视频/台本/事实核对.md）：
- 第三人称，不以“我”开头；讲解者叫他“X 用户龙海”；文章里的判断一律挂“书里 / 作者 / 官网”的名。
- 数字取自图片里的标注（图 09 的 20 / 10 像素，图 14 的 5.97 / 9.01 ……，图 17 的 .55）或文章原文，不自己编。
- 对着图写“上面 / 下面”：dual 版式里上框 = 错误做法那一半，下框 = 正确做法那一半（图 14 上框是蓝色“？”：合格，但抢眼，不是错）。
结构（照 AI大圆镜 短条骨架）：钩子 → 背书 → 5 条规则（每条：错在哪 + 怎么改 + 一个数字）→ 泼冷水 → 金句。
选哪 5 条：13 颜色（钩子 + 色阶）、06 按钮分主次、09 间距 20 / 20 → 20 / 10、14 浅底深字、17 图上文字（理由见 README.md）。
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parent

sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
import bilingual_std as B  # noqa: E402

B.ZH_MAX, B.EN_MAX, B.EN_SOFT = 17.5, 60, 64      # 和 build_timeline.py 一致：竖屏中文一行 ≤ 17 字、英文 ≤ 约 60 字符


def L(id_, zh, en, say=None, cut=None):
    """cut = [[中文锚点, 英文锚点], …]：字幕在这些文字之后断条（自动拆得不顺的句子用，bilingual_std 的手动断点）。"""
    d = dict(id=id_, zh=zh, say=say or zh, en=en)
    if cut:
        d["cut"] = cut
    return d


# 标题（整条一直挂在顶上）：用户建议“人人都是 / UI设计师”
HOOK = ["人人都是", "UI设计师"]
KICKER = "悠一 · <b>Refactoring UI</b> 5 条规则"

# 每个场景：id / name / overlay（panel = 对比图面板，page = 页面截图，wall = 书 + 缩略图墙）/ ui（tag = 上框贴纸，tag2 = 下框贴纸，kicker = 这个场景的小标题）/ lines / screen（画面说明，给人读）
SCENES = [
    dict(id="H0", name="钩子", overlay="panel", a0=0.1,
         ui=dict(tag="x|只用 5 个色码", tag2="ok|按色阶取色", credit="图：《Refactoring UI》· 龙海的文章"),
         screen="上框 = 图 13 下层 ✕：5 个色码硬套出来的界面（黄底、红条、深蓝侧栏）；下框 = 同一界面 ✓：按色阶取色（白底灰字、浅黄提示条）。两个框里的界面取同样大的窗口（R 的界面比 L 低 63 px，窗口都从 y=756 起）。\n贴纸：上“✕ 只用 5 个色码”、下“✓ 按色阶取色”；来源小字“图：《Refactoring UI》· 龙海的文章”（上框左上角外）。\n高亮（只画框不写字，贴纸已经写了）：“五个颜色”→ 上框红框（黄色主区域）；“什么像样”→ 下框绿框（白色主区域）。第 0 帧就有画面（场景从 −0.5 s 起），可以直接当封面帧。",
         lines=[
             L("N01", "书里说，只靠五个颜色，什么像样的界面都做不出来。",
               "The book says five colors alone can't build any decent interface."),
         ]),
    dict(id="B1", name="背书", overlay="page", a0=0.1,
         ui=dict(tag="龙海 · X 长文", tag2="refactoringui.com"),
         screen="上框 = 龙海的推文截图（X 嵌入页，整张缩进框里，框顶浏览器条显示 x.com/longhaiqwe123/status/…）；下框 = refactoringui.com 首屏（整张缩进框里）。\n贴纸：上“龙海 · X 长文”、下“refactoringui.com”。\n高亮：“10 月 3 号”→ 推文时间“2026年10月3日”（荧光笔）；“龙海”→ 作者名；“Refactoring”→ 推文里的《Refactoring UI》（橙框）+ 下框的书封面（橙框）；“二十条”→“20 条设计军规”（荧光笔）。",
         lines=[
             L("N02", "10 月 3 号，X 用户龙海发了一篇长文。",
               "On October 3, X user Long Hai posted a long article.",
               "十月三号，X 用户龙海发了一篇长文。"),
             L("N03", "二十条设计规则，精选自《Refactoring UI》这本书。",
               "Twenty design rules, picked from the book Refactoring UI.",
               "二十条设计规则，精选自《Refactoring UI》这本书。"),
             L("N04", "先看五条，每条都带一个数字。",
               "Here are five of them, each with a number."),
         ]),
    dict(id="S06", name="按钮分主次", overlay="panel", a0=0.1, rule=6,
         ui=dict(tag="x|三个实心", tag2="ok|只有一个主操作", kicker="悠一 · <b>规则 06</b> 按钮分主次", credit="图：《Refactoring UI》· 龙海的文章"),
         screen="上框 = 图 06 ✕：红 Delete Listing / 蓝 Edit / 绿 Publish 三个实心按钮；下框 = ✓：Publish 实心、Edit 浅底、Delete 退成文字链接。取景收紧到卡片（850×478，16:9）。\n贴纸：上“✕ 三个实心”、下“✓ 只有一个主操作”；小标题“规则 06 按钮分主次”。\n焦点：N05 上框亮、下框蒙米白；N06、N07 下框亮。高亮：“红蓝绿”→ 上框三个红框依次出现 + 标签“三个都是实心”；“主操作”→ 下框 Publish 绿框 + 标签“主操作”；“删除”→ 下框 Delete 绿框 + 标签“文字链接”。",
         lines=[
             L("N05", "上面三个按钮全是实心，红蓝绿谁都想当主角。",
               "On top, three solid buttons: red, blue and green all want to be the lead.",
               cut=[["全是实心，", "solid buttons:"]]),
             L("N06", "书里说，多数页面只有一个主操作。",
               "The book says most pages have just one primary action."),
             L("N07", "下面只有发布是实心，删除退成了文字链接。",
               "Below, only Publish stays solid, and Delete shrinks to a text link."),
         ]),
    dict(id="S09", name="间距有亲疏", overlay="panel", a0=0.1, rule=9,
         ui=dict(tag="x|上 20 下 20", tag2="ok|上 20 下 10", kicker="悠一 · <b>规则 09</b> 间距有亲疏", credit="图：《Refactoring UI》· 龙海的文章"),
         screen="上框 = 图 09 ✕：“Street address”标签上下各 20px（红色标注线）；下框 = ✓：上 20px、下 10px。取景收紧到表单左半边（640×360，16:9），标注的字放大。\n贴纸：上“✕ 上 20 下 20”、下“✓ 上 20 下 10”。焦点：N08 上框、N09 下框。\n高亮：“标签”→ 上框红框 + 标签“上 20 · 下 20 px”；“改成”→ 下框绿框 + 标签“上 20 · 下 10 px”。",
         lines=[
             L("N08", "标签上下各空 20 像素，归上还是归下，说不清。",
               "A label with 20 pixels above and 20 below could belong to either field.",
               "标签上下各空二十像素，归上还是归下，说不清。"),
             L("N09", "改成上 20、下 10，标签立刻贴住自己的输入框。",
               "Make it 20 above and 10 below, and the label snaps to its own input.",
               "改成上二十、下十，标签立刻贴住自己的输入框。"),
         ]),
    dict(id="S13", name="颜色比想象的多", overlay="panel", a0=0.1, rule=13,
         ui=dict(tag="x|调色板 5 色", tag2="ok|完整色阶", kicker="悠一 · <b>规则 13</b> 颜色比想象的多", credit="图：《Refactoring UI》· 龙海的文章"),
         screen="上框 = 图 13 上层 ✕：在线调色板给的 5 个色块（#173F5F #20639B #3CAEA3 #F6D55C #ED553B）；下框 = ✓：Primary / Neutral / Accents 三类完整色阶。上框取和下框一样高的整块（色条在中间），两边一样大。\n贴纸：上“✕ 调色板 5 色”、下“✓ 完整色阶”。焦点：N10 上框、N11 下框。\n高亮：N10 → 上框红框 + 标签“只有 5 个色码”；“主色”→ 下框第一行绿框 + “主色 5–10 档”；“灰色”→ 第二行 + “灰色 8–10 档”；“强调色”→ 第三块（三行）+ “强调色各 5–10 档”（标签写在框里左侧留白处）。",
         lines=[
             L("N10", "在线调色板，就给你上面这五个色块。",
               "An online palette tool hands you just these five swatches."),
             L("N11", "书里的做法：主色 5 到 10 档，灰色 8 到 10 档，强调色各 5 到 10 档。",
               "The book's way: 5 to 10 shades of the main color, 8 to 10 greys, and 5 to 10 for each accent.",
               "书里的做法：主色五到十档，灰色八到十档，强调色各五到十档。",
               cut=[["主色 5 到 10 档，", "of the main color,"], ["灰色 8 到 10 档，", "8 to 10 greys,"]]),
         ]),
    dict(id="S14", name="浅底深字", overlay="panel", a0=0.1, rule=14,
         ui=dict(tag="?|合格，但抢眼", tag2="ok|浅底深字", kicker="悠一 · <b>规则 14</b> 浅底深字", credit="图：《Refactoring UI》· 龙海的文章"),
         screen="上框 = 图 14 左（角标是蓝色“？”：深底白字标签，对比度 5.97 / 5.07 / 5.34，合格但抢眼，不是错）；下框 = ✓：浅底深字，9.01 / 9.78 / 12.32。取景裁到数字后面留一点边。\n贴纸：上“？ 合格，但抢眼”（蓝）、下“✓ 浅底深字”。焦点：N12 上框、N13 下框。\n高亮（上框用蓝色框，不是红）：N12 开头 → 标签栏框 +“深底白字”；“对比度”→ 数字栏框 +“对比度 5.07–5.97”；下框同理 +“浅底深字”“对比度 9.01–12.32”（绿）。",
         lines=[
             L("N12", "上面深底白字，对比度过了无障碍标准的 4.5，但抢眼。",
               "On top, white on dark clears WCAG's 4.5 contrast bar, but it shouts.",
               "上面深底白字，对比度过了无障碍标准的四点五，但抢眼。",
               cut=[["上面深底白字，", "on dark"], ["对比度过了无障碍标准的 4.5，", "contrast bar,"]]),
             L("N13", "下面浅底深字，对比度 9.01 到 12.32，反而更柔和。",
               "Below, dark text on pale badges scores 9.01 to 12.32, and looks softer.",
               "下面浅底深字，对比度九点零一到十二点三二，反而更柔和。",
               cut=[["下面浅底深字，", "on pale badges"]]),
         ]),
    dict(id="S17", name="图上文字", overlay="panel", a0=0.1, rule=17,
         ui=dict(tag="x|白字压照片", tag2="ok|垫蒙版 0.55", kicker="悠一 · <b>规则 17</b> 图上文字", credit="图：《Refactoring UI》· 龙海的文章"),
         screen="上框 = 图 17 ✕：白字直接压在照片上，亮处看不清；下框 = ✓：垫一层半透明黑色蒙版，图下标注 background-color: hsla(0, 0%, 0%, .55)。\n贴纸：上“✕ 白字压照片”、下“✓ 垫蒙版 0.55”。焦点：N14 上框、N15 下框。\n高亮：“白字”→ 上框文字红框 + 标签“字被照片吃掉”；“垫”→ 下框整张照片绿框 + “半透明黑蒙版”；“不透明度”→ 下框 CSS 那一行绿框 + “0.55”。",
         lines=[
             L("N14", "上面白字压在照片上，亮的地方就隐形了。",
               "On top, white text over a photo vanishes wherever the picture is bright."),
             L("N15", "先动背景：垫一层黑色蒙版，不透明度 0.55。",
               "Fix the background first: a black overlay at 0.55 opacity.",
               "先动背景：垫一层黑色蒙版，不透明度零点五五。"),
         ]),
    dict(id="C1", name="泼冷水", overlay="wall", a0=0.1,
         ui=dict(tag="官网 · 全书 50 章", tag2="文章覆盖 20 条"),
         screen="上框 = 官网“The Book”一节（高亮 50 incredibly visual chapters）；下框 = 20 条规则的 ✓ 面板铺成 5×4 缩略图墙（带编号），本期讲的 06 / 09 / 13 / 14 / 17 亮橙框，底部说明条“亮的是这期讲的 5 条”。\n贴纸：上“官网 · 全书 50 章”、下“文章覆盖 20 条”。高亮：“五十章”→ 荧光笔；“一半”→ 说明条出现；N16 开头 0.6 s 后五张缩略图亮起。",
         lines=[
             L("N16", "不过二十条，连书里五十章的一半都不到。",
               "But twenty rules are less than half of the book's fifty chapters."),
             L("N17", "文中的判断，是龙海摘自书里的说法。",
               "The article's claims are Long Hai's picks from the book."),
             L("N18", "龙海也提醒：别死记数字。",
               "Long Hai also warns: don't memorize the numbers."),
         ]),
    dict(id="E1", name="金句", overlay="panel", a0=0.1,
         ui=dict(tag="x|只用 5 个色码", tag2="ok|按色阶取色", credit="图：《Refactoring UI》· 龙海的文章"),
         screen="和钩子同一对画面（图 13 下层 ✕ / ✓）：首尾呼应；“审美”→ 下框绿框。最后一个场景的叠加层盖到片尾（句末留 0.8 s）。",
         lines=[
             L("N19", "代码交给 AI，审美交给清单。",
               "Leave the code to AI. Leave the taste to a checklist."),
         ]),
]


def stats(say):
    han = sum(1 for ch in say if "\u4e00" <= ch <= "\u9fff")
    lat = len(re.findall(r"[A-Za-z]+", say))
    inner = len(re.findall(r"[，、：；？！,]", say[:-1]))
    return han, lat, inner


def est_dur(say):
    """温柔男生实测回归（长视频 142 句：dur ≈ 0.140·汉字 + 0.333·英文词 + 0.284·句内标点 + 0.405，均方误差 0.35 s / 句）。"""
    han, lat, inner = stats(say)
    return 0.140 * han + 0.333 * lat + 0.284 * inner + 0.405


def all_lines():
    return [l for s in SCENES for l in s["lines"]]


def build():
    lines = all_lines()
    ids = [l["id"] for l in lines]
    assert len(ids) == len(set(ids)), "句子 id 重复"
    problems, tot_han, tot_chars, tot_dur = [], 0, 0, 0.0
    rows = []
    for l in lines:
        w, e = B.zh_units(l["zh"]), len(l["en"])
        chunks = B.split_pair_aligned(l["zh"], l["en"], 0.0, cuts=[tuple(c) for c in l["cut"]] if l.get("cut") else None)
        bad = [f"{l['id']}.{k + 1}" for k, (z, en, cw) in enumerate(chunks) if cw > B.ZH_MAX or len(en) > B.EN_SOFT]
        if e > 120:
            problems.append(f"{l['id']} 英文 {e} 字符 > 120")
        if bad:
            problems.append(f"{l['id']} 拆出来超长：{' '.join(bad)}")
        han, lat, inner = stats(l["say"])
        d = est_dur(l["say"])
        tot_han += han
        tot_chars += len(l["say"])
        tot_dur += d
        rows.append((l["id"], han, len(l["say"]), d, w, e, len(chunks)))
    sc = dict(slug="人人都是UI设计师_竖屏短版", title="人人都是 UI 设计师：5 条设计规则（长视频《人人都是 UI 设计师》的竖屏短版，内部标题，不是平台标题）",
              kicker=KICKER, hook=HOOK, chapters=[],
              lines=[{k: v for k, v in l.items()} for l in lines])
    (HERE / "录制稿.json").write_text(json.dumps(sc, ensure_ascii=False, indent=1), encoding="utf-8")

    plan = []
    for s in SCENES:
        it = dict(id=s["id"], type="card", kind=s["overlay"], overlay=s["overlay"], name=s["name"], dur=1.0, ui=dict(s["ui"]),
                  lines=[dict(id=l["id"], a=(s["a0"] if i == 0 else 0)) for i, l in enumerate(s["lines"])])
        if s.get("rule"):
            it["rule"] = s["rule"]
        plan.append(it)
    (HERE / "plan.json").write_text(json.dumps(dict(layout="dual", plan=plan), ensure_ascii=False, indent=1), encoding="utf-8")

    (EP / "制作" / "02_配音" / "say_lines.txt").write_text("\n".join(l["say"] for l in lines) + "\n", encoding="utf-8")

    # 估时：制作/00_整片/timeline.json（build_timeline.py --est 或配音后生成）里的场景起止
    seg_t = {}
    tl = EP / "制作" / "00_整片" / "timeline.json"
    if tl.exists():
        T = json.loads(tl.read_text(encoding="utf-8"))
        seg_t = {g["id"]: (g["s"], g["e"]) for g in T["segs"]}
        est = T.get("est")
        total = T.get("total")
    else:
        est, total = True, None
    md = ["# 台本：《人人都是 UI 设计师》竖屏短视频（5 条规则）", "",
          f"标题（一直挂在顶上）：{HOOK[0]} / {HOOK[1]}；kicker：{re.sub('<[^>]+>', '', KICKER)}。第三人称；声线「温柔男生」；中英双语字幕；1080×2340，dual 双框（上框 = 错的 / 下框 = 对的）。", "",
          "选题：13 颜色（钩子 + 色阶）、06 按钮分主次、09 间距 20/20 → 20/10、14 浅底深字、17 图上文字——每条都有一个能直接抄的数字（5 个色码 vs 主色 5–10 档 / 灰 8–10 档；一个主操作；20 → 10 px；对比度 5.07–5.97 → 9.01–12.32；蒙版 0.55），画面反差也最大。数字和说法都取自 长视频/台本/事实核对.md 和图里的标注。", "",
          f"## 总览（时间{'是按字数估的，配音出来后以 制作/00_整片/timeline.json 为准' if est else '取自 timeline.json'}；共 {len(lines)} 句、{tot_chars} 个字符{'，整片约 %.1f s' % total if total else ''}）", "",
          "| 场景 | 内容 | 起止 s | 句子 |", "|---|---|---|---|"]
    for s_ in SCENES:
        t = seg_t.get(s_["id"])
        md.append(f"| {s_['id']} | {s_['name']} | {('%.1f–%.1f' % t) if t else '—'} | {s_['lines'][0]['id']}–{s_['lines'][-1]['id']} |")
    md.append("")
    for s_ in SCENES:
        t = seg_t.get(s_["id"])
        md += [f"## {s_['id']} {s_['name']}" + (f"（{'估 ' if est else ''}{t[0]:.1f}–{t[1]:.1f} s）" if t else ""), "", "画面：", ""]
        md += [f"- {x}" for x in s_["screen"].split("\n")]
        md += ["", "| 句 | 字幕 zh | 配音 say | 英文 en |", "|---|---|---|---|"]
        for l in s_["lines"]:
            md.append(f"| {l['id']} | {l['zh']} | {l['say'] if l['say'] != l['zh'] else '（同 zh）'} | {l['en']} |")
        md.append("")
    (HERE / "台本.md").write_text("\n".join(md), encoding="utf-8")

    for r in rows:
        print(f"  {r[0]}  汉字 {r[1]:2d}  字符 {r[2]:2d}  估 {r[3]:.1f} s  中文宽 {r[4]:.1f}  英文 {r[5]:3d}  拆 {r[6]} 条")
    print(f"{len(lines)} 句，念的字 {tot_chars} 个（其中汉字 {tot_han}），有声估时 {tot_dur:.1f} s（回归模型）；"
          f"按 6.2 字符/秒 = {tot_chars / 6.2:.1f} s；场景 {len(plan)} 个")
    print("【问题】\n  " + "\n  ".join(problems) if problems else "字幕宽度全部在限内（中文 ≤ 17.5 / 条，英文 ≤ 64 / 条，整句英文 ≤ 120）")


if __name__ == "__main__":
    build()
