# -*- coding: utf-8 -*-
"""timeline.json 的 cues → ASS（烧进画面）+ 三份 SRT。**项目统一的中英双语字幕标准**版
（用户 2026-10-02：“OpenAI 那两条也统一成这个标准”）；旧版（中文 48 / 英文 30 px、半透明黑底、可两行）是 make_ass.py，没删。

  python make_ass_std.py [--ver v3] [--intro 3.8]

  --ver v3（默认）  对齐版拆条（bilingual_std.split_pair_aligned：中英文一起找断点，断在标点 / 语义处）+ 下面 CUTS 里手动指定的断点
                    → bilingual_std_v3.ass、../../整片_v3_{双语,中文,英文}字幕.srt，配 render.py 整片_v3.mp4 bilingual_std_v3.ass
  --ver v2          第一版拆条（split_pair：先拆中文再让英文凑占比，有“政策 | 的航班”“我 | 是不是”这类别扭的断点）
                    → bilingual_std.ass、../../整片_v2_*.srt（已经渲出 整片_v2.mp4，留着复现用）

标准（`Way to AGI/skill/way-to-agi-episode/references/subtitles.md` 「中英双语」+ `pipeline.md` §2，代码在该技能 `scripts/bilingual_std.py`）：
  居中，字幕带 y 922 以下；中文一行 52 px（墨黑白边）、英文一行 30 px（灰），各一行不换行；一条中文 ≤ 约 28 字、英文 ≤ 约 90 字符；
  每条开始前 0.1 s 显示到结束后 0.45 s，不叠。
每条 cue = 一句中文同传（zh）+ 它对应的原话（en）；放不下就拆成多条，拆出来的各条按中文字数占比分这句同传的起止时间。
dot 说的话，中文前面保留橙色“dot：”标签（标准没规定说话人标签，沿用本条的做法，算进 28 字里）。
片头另有一条来源角标（左上角，前 6 秒，沿用旧版）。SRT 的时间已含片头 3.8 s（正片前面还要加悠一片头，只对得上加完片头片尾的成片；--intro 0 就是不含）。
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, "D:/大疆/Way to AGI/skill/way-to-agi-episode/scripts")
import bilingual_std as B  # noqa: E402

CREDIT = "画面：OpenAI 官方 YouTube《The dots demo, take two》｜原声压低，中文同传"
TAG_STYLE = "Style: TAG,NSC600,28,&H00FFFFFF,&H000000FF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,2,0.8,7,48,48,40,1\n"

# 对齐版自动拆得不顺的句子，手动指定断点：每一对 = (中文在这段文字之后断, 英文在这段文字之后断)，按出现的先后找。
# 判断标准：每一条的中文和英文说的是同一件事；不在词组中间断（“large | issues”）。
CUTS = {
    "N002": [("遗憾，", "unfortunate,")],
    "N006": [("直接演示。", "show you it here.")],
    "N023": [("直接过去。", "head straight over."), ("30 到 45 分钟，", "get out of LAX,")],
    "N031": [("有意思。", "looks fun."), ("静音着？", "Am I muted?")],
    "N041": [("进行中、", "in flight,"), ("这些工作。", "that work."), ("没关系；", "that's fine;")],
    "N042": [("手动跑也可以。", "run the feedback manually."), ("确认的是：", "make sure of is")],
    "N047": [("关上了，", "closed the loop;"), ("不太稳定。", "been inconsistent."), ("PR 链接，", "the PR link,")],
    "N048": [("有道理。", "makes sense.")],
    "N050": [("判断是：", "read so far is"), ("在工作。", "actually working."), ("进度不清楚；", "unclear progress;")],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", choices=["v2", "v3"], default="v3")
    ap.add_argument("--intro", type=float, default=3.8)
    a = ap.parse_args()
    aligned = a.ver == "v3"
    ass_name = "bilingual_std_v3.ass" if aligned else "bilingual_std.ass"
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    cues = sorted(T["cues"], key=lambda q: q["s"])
    items = []                                                    # (s, e, 中文, 英文, 说话人, id)
    bad = []
    for q in cues:
        pre = B.zh_units(q["who"] + "：") if q.get("who") else 0.0
        if aligned:
            chunks = B.split_pair_aligned(q["zh"], q["en"], pre, cuts=CUTS.get(q["id"]))
        else:
            chunks = B.split_pair(q["zh"], q["en"], pre)
        times = B.chunk_times(q["s"], q["e"], chunks)
        for k, ((z, e, w), (s, t)) in enumerate(zip(chunks, times)):
            if w + (pre if k == 0 else 0.0) > B.ZH_MAX or len(e) > (B.EN_SOFT if aligned else B.EN_MAX):
                bad.append(f"{q['id']}.{k + 1}")
            items.append((s, t, z, e, q.get("who", "") if k == 0 else "", q["id"]))
    wins = B.display_windows([(i[0], i[1]) for i in items])
    events, rows = [], []
    for (s, t, z, e, who, qid), (wa, wb) in zip(items, wins):
        zt = B.esc_ass(z)
        if who:
            zt = "{\\c" + B.ORANGE + "}" + B.esc_ass(who) + "：{\\c" + B.INK + "}" + zt
        events += B.ass_events(wa, wb, zt, e)
        rows.append((wa + a.intro, wb + a.intro, (who + "：" if who else "") + z, e))
    events.append(f"Dialogue: 1,{B.ts_ass(0.3)},{B.ts_ass(6.3)},TAG,,0,0,0,,{{\\fad(300,500)}}{CREDIT}")
    (HERE / ass_name).write_text(B.ass_header(extra_styles=TAG_STYLE) + "\n".join(events) + "\n", encoding="utf-8")
    B.write_srts(str(HERE.parents[1] / f"整片_{a.ver}"), rows)
    n90 = sum(1 for i in items if len(i[3]) > B.EN_MAX)
    print(f"{ass_name}：{len(cues)} 句同传 → {len(items)} 条字幕（{a.ver}，{'对齐版 + ' + str(len(CUTS)) + ' 处手动断点' if aligned else '旧拆条'}）+ 1 条来源角标；"
          f"SRT 三份写到 {HERE.parents[1]}（整片_{a.ver}_*.srt，时间含片头 {a.intro} s）；超长（没拆开 / 英文 > {B.EN_SOFT if aligned else B.EN_MAX}）：{' '.join(bad) or '无'}；英文 > 90 字符的有 {n90} 条")


if __name__ == "__main__":
    main()
