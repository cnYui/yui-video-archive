# -*- coding: utf-8 -*-
"""日报（2026-10-05 这期）→ 竖屏短视频（版式 ① 标准竖版）的数据：读日报的 timeline.json / 台本.json，写 tl_v.json / tl_v.js。

  python build_vertical.py

- 时间轴 = 日报主体部分（不要片头片尾），t = 0 对应日报开场第一句；配音就是日报的 voice_main.wav（不重配）。
- 场景：S01 开场（清单）/ S02–S09 八条新闻 / S10 回顾；每条新闻 = 标题（两行）+ 来源截图框（边框 6，橙框圈出原文）+ 字幕 + 要点卡（四个要点按配音一条条亮）
  + 数字卡（有硬数字的那几句替换要点卡）+ 鲸鱼娘 + 进度条。
- 字幕：日报横屏版的每条重新按竖屏拆（中文 ≤ 17.5 字、英文 ≤ 60 字符，bilingual_std.split_pair_aligned），再按字拆开的占比分配时间。
- 鲸鱼娘：mouth（逐帧口型 0/1/2）和 expr（开心 / 吃惊 / 认真）照搬日报。
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = Path(r"D:\大疆\AI日报\2026-10-05")
sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
import bilingual_std as B  # noqa: E402

B.ZH_MAX, B.EN_MAX, B.EN_SOFT = 17.5, 60, 64      # 竖屏 1080 宽：中文 52 px 一行 ≤ 17 字，英文 30 px 一行 ≤ 约 60 字符（check_v.py 再按真实字宽量）
TAIL = 0.8                                          # 短视频：金句说完 0.8 s 结束

# ---------------------------------------------------------------- 每条新闻的竖屏版文案（钩子 / 来源贴纸 / 截图上圈哪句 / 数字卡）
# hl = (x, y, w, h) 截图像素坐标（news_0N.png 的原始尺寸）；bigs = 按配音那一句（seg id）出数字卡：n 大数字、small 单位、d 一句说明
NEWS_V = {
    "S02": dict(t1="Gemini 免费版降级", t2="10 月 9 日起只剩 Flash-Lite", tag="来源 · 9to5Google", snap="news_01.png", wh=(1290, 840), hl=(26, 64, 1116, 206),
                bigs=[dict(seg="S02-04", n="10月9日", small="起生效", d="免费版只剩 Flash-Lite"),
                      dict(seg="S02-08", n="19.99", small="美元 / 月", d="想要三个模型，得订 AI Pro")]),
    "S03": dict(t1="德国开源模型 Kolibri", t2="78B 参数，每词只动 3.46B", tag="来源 · Aleph Alpha", snap="news_02.png", wh=(1310, 840), hl=(24, 572, 905, 104),
                bigs=[dict(seg="S03-10", n="3.46B", small="活跃参数", d="总参数 78B · 每个词只动这么多"),
                      dict(seg="S03-12", n="6 / 384", small="个专家", d="每层 384 个专家，每次只挑 6 个")]),
    "S04": dict(t1="DeepSeek Harness 新版", t2="试着兼容 Claude Code 插件", tag="来源 · 36氪", snap="news_03.png", wh=(1161, 840), hl=(28, 348, 800, 62),
                bigs=[dict(seg="S04-19", n="v0.2.1", small="alpha.1", d="10 月 3 日发的预发布版")]),
    "S05": dict(t1="GPT-6 打星际搬顶尖代码", t2="输了就下载人类的程序", tag="来源 · XDA", snap="news_04.png", wh=(1500, 840), hl=(70, 742, 1140, 52),
                bigs=[dict(seg="S05-28", n="1 小时", small="写 C++", d="大模型只能用神族，限时写对战程序")]),
    "S06": dict(t1="谷歌暂停开源漏洞赏金", t2="AI 写的假报告太多了", tag="来源 · IT之家", snap="news_05.png", wh=(1095, 840), hl=(28, 405, 995, 115),
                bigs=[dict(seg="S06-35", n="10月1日", small="起", d="不再接收产品漏洞"),
                      dict(seg="S06-39", n="2027 Q1", small="新进展", d="谷歌说会重新调整这个计划")]),
    "S07": dict(t1="COSMIC 拒收 AI 代码", t2="提交代码先发誓：没用 AI", tag="来源 · Linuxiac", snap="news_06.png", wh=(1247, 840), hl=(30, 288, 1062, 112), bigs=[]),
    "S08": dict(t1="Gboard 训练搬进加密服务器", t2="隐私保证能被外部核验", tag="来源 · Google Research", snap="news_07.png", wh=(1232, 840), hl=(20, 62, 880, 340),
                bigs=[dict(seg="S08-48", n="1–2 个月", small="", d="以前训练一个模型要这么久"),
                      dict(seg="S08-54", n="5000 轮", small="× 6500 台", d="一个英语模型的测试规模")]),
    "S09": dict(t1="治 AI 智能体刷题", t2="熟悉环境 97.1%，陌生 0 分", tag="来源 · The Decoder", snap="news_08.png", wh=(1080, 840), hl=(50, 80, 930, 170),
                bigs=[dict(seg="S09-56", n="97.1%", small="→ 0 分", d="熟悉环境 vs 陌生环境"),
                      dict(seg="S09-62", n="+14.1 分", small="", d="练过的题最多涨；没见过的最多涨 4.7 分")]),
}
HEADS = ["Gemini 免费版降级", "德国开源模型 Kolibri", "DeepSeek Harness 新测试版", "GPT-6 打星际搬顶尖代码", "谷歌暂停开源漏洞赏金", "COSMIC 拒收 AI 代码",
         "Gboard 训练搬进加密服务器", "治 AI 智能体刷题"]
# 字幕拆条：自动拆在词中间的（“智能 / 体”“提示 / 词”）或太短的（“官方称，”0.3 s）手动处理。
# MERGE：这条日报字幕和下一条合并再拆；CUTS：{合并后的中文: [(中文锚点, 英文锚点), …]}，在锚点之后断（bilingual_std._manual_chunks）
MERGE = {"官方称，": True, "Stardust 是 Bruce Mackenzie Nielsen 2020 年写的，": True, "第四件，GPT-6 Astra 打《星际争霸》一直输，": True}
CUTS = {
    "官方称，它能打平 Nemotron 3 Super 这类激活参数更多的模型，": [("Super", "matches models")],
    "第三件，DeepSeek 的智能体工具 Harness，": [("DeepSeek 的", "DeepSeek's")],
    "第四件，GPT-6 Astra 打《星际争霸》一直输，然后它把人类写的顶尖程序下载下来，替自己上场。": [("《星际争霸》", "StarCraft,"), ("顶尖程序", "by a human")],
    "Stardust 是 Bruce Mackenzie Nielsen 2020 年写的，算是顶尖里的顶尖。": [("Nielsen", "Nielsen")],
    "Astra 和 Claude Opus 5.5 是 AI 里成绩最好的两个。": [("Opus 5.5", "Opus 5.5")],
    "受限于手机有没有空、算力够不够。": [("没有空、", "were free")],
    "最后一件，一个 AI 智能体在熟悉的环境里拿了 97.1%，": [("智能体", "scored")],
    "这是 The Decoder 10 月 4 日报道里举的例子，": [("4 日", "The Decoder")],
    "现在很多智能体会自己改自己的提示词、工具和流程，": [("会自己改", "edit")],
}
# 开场清单第 i 条（短标题）对应配音里的哪几个短语（S01-02 的 lines 下标；第 3 条跨两个短语）
OPEN_LINES = [[1], [2], [3, 4], [5], [6], [7], [8], [9]]


def main():
    T = json.loads((EP / "制作" / "timeline.json").read_text(encoding="utf-8"))
    SC = json.loads((EP / "台本.json").read_text(encoding="utf-8"))
    segs = T["segments"]
    by = {}
    for s in segs:
        by.setdefault(s["scene"], []).append(s)
    segid = {s["id"]: s for s in segs}
    last_end = max(u["e"] for s in segs for u in s["subs"])
    total = round(last_end + TAIL, 3)
    frames = int(round(total * T["fps"]))

    scenes = []
    for sc in T["scenes"]:
        sid = sc["id"]
        d = dict(id=sid, s=sc["start"], e=min(sc["end"], total))
        if sid == "S01":
            d.update(kind="open", kicker="AI每日日报 · <b>10.05</b>", t1="今天说 8 件事", t2="GPT-6 打星际输了？", tag="今日 8 条", prog=0)
            ls = by["S01"][1]["lines"]
            d["agendaTimes"] = [[ls[ix[0]]["start"], ls[ix[-1]]["end"]] for ix in OPEN_LINES]
        elif sid == "S10":
            d.update(kind="review", kicker="AI每日日报 · <b>10.05</b>", t1="今日回顾", t2="8 件事，来源都在简介里", tag="今日回顾", prog=9)
        else:
            n = int(sid[1:]) - 1                      # 第几条新闻（1..8）
            cfg = NEWS_V[sid]
            news = SC["news"][n - 1]
            ss = by[sid]
            assert len(ss) == len(news["lines"]), (sid, len(ss), len(news["lines"]))
            # 要点按配音一句句亮：lines[i]["point"] 是这一句说的第几个要点（没有就 None）
            ptTimes = [dict(pt=ln["point"], s=seg["start"], e=seg["end"]) for seg, ln in zip(ss, news["lines"]) if ln.get("point") is not None]
            bigs = []
            for b in cfg["bigs"]:
                seg = segid[b["seg"]]
                bigs.append(dict(b, s=seg["start"], e=seg["end"]))
            d.update(kind="news", idx=n, kicker=f"AI每日日报 · <b>10.05</b> · 第 <b>{n}</b> / 8 条", t1=cfg["t1"], t2=cfg["t2"], tag=cfg["tag"], prog=n,
                     snap="assets/snaps/" + cfg["snap"], wh=cfg["wh"], hl=cfg["hl"], pts=news["points"], ptTimes=ptTimes, bigs=bigs)
        scenes.append(d)
    scenes[-1]["e"] = total

    # ---------------------------------------------------------------- 字幕：按竖屏重拆
    raw = sorted((dict(u) for s in segs for u in s["subs"]), key=lambda u: u["s"])
    items, i = [], 0
    while i < len(raw):
        u = raw[i]
        if MERGE.get(u["zh"]) and i + 1 < len(raw):          # 和下一条合并
            v = raw[i + 1]
            u = dict(zh=u["zh"] + v["zh"], en=u["en"] + " " + v["en"], s=u["s"], e=v["e"])
            i += 1
        items.append(u)
        i += 1
    chunks_all, over, soft = [], [], []
    for u in items:
        ch = B.split_pair_aligned(u["zh"], u["en"], cuts=CUTS.get(u["zh"]))
        for k, ((z, e, w), (a, b)) in enumerate(zip(ch, B.chunk_times(u["s"], u["e"], ch))):
            if w > B.ZH_MAX or len(e) > B.EN_SOFT:
                over.append(f"{u['s']:.1f}.{k + 1}")
            elif len(e) > B.EN_MAX:
                soft.append(f"{u['s']:.1f}.{k + 1}")
            chunks_all.append({"zh": z, "en": e, "s": round(a, 3), "e": round(b, 3)})
    for x, (a, b) in zip(chunks_all, B.display_windows([(x["s"], x["e"]) for x in chunks_all])):
        x["a"], x["b"] = round(a, 3), round(min(b, total), 3)

    # ---------------------------------------------------------------- 鲸鱼娘表情
    expr = []
    for s in segs:
        for a in s.get("actions", []):
            if a.get("type") == "expr":
                expr.append(dict(name=a["name"], s=a["start"], e=a["end"]))

    tl = dict(fps=T["fps"], total=total, frames=frames, bg="assets/bg.png", cover="assets/cover.png", scenes=scenes, subs=chunks_all, expr=expr,
              mouth=T["mouth"][: frames + 2],
              agenda=[dict(n=i + 1, head=h, snap=f"assets/snaps/news_0{i + 1}.png") for i, h in enumerate(HEADS)])
    (HERE / "tl_v.json").write_text(json.dumps(tl, ensure_ascii=False), encoding="utf-8")
    (HERE / "tl_v.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"整片 {total:.2f} s（{frames} 帧）：{len(scenes)} 个场景；日报字幕 {len(raw)} 条 → 竖屏 {len(chunks_all)} 条（超长没拆开：{' '.join(over) or '无'}；英文略超 {B.EN_MAX} 字符：{' '.join(soft) or '无'}）")
    for x in chunks_all:
        print(f"  {x['s']:7.2f}-{x['e']:7.2f} | {x['zh']}  /  {x['en']}")


if __name__ == "__main__":
    main()
