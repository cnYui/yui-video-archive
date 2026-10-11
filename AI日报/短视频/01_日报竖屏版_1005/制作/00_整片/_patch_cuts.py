p = "build_vertical.py"
s = open(p, encoding="utf-8").read()

s = s.replace('''# 开场清单第 i 条''', '''# 字幕拆条：自动拆在词中间的（“智能 / 体”“提示 / 词”）或太短的（“官方称，”0.3 s）手动处理。
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
    "现在很多智能体会自己改自己的提示词、工具和流程，": [("提示词、", "prompts,")],
}
# 开场清单第 i 条''')

s = s.replace('''    items = sorted((u for s in segs for u in s["subs"]), key=lambda u: u["s"])
    chunks_all, over, soft = [], [], []
    for u in items:
        ch = B.split_pair_aligned(u["zh"], u["en"])''', '''    raw = sorted((dict(u) for s in segs for u in s["subs"]), key=lambda u: u["s"])
    items, i = [], 0
    while i < len(raw):
        u = raw[i]
        if MERGE.get(u["zh"]) and i + 1 < len(raw):          # 和下一条合并
            v = raw[i + 1]
            u = dict(zh=u["zh"] + v["zh"], en=u["en"] + " " + v["en"], s=u["s"], e=v["e"])
            i += 1
        items.append(u)
        i += 1
    for k in list(CUTS):                                       # 合并后是第四件那条要再合一次：S05-26 的两条
        pass
    merged, j = [], 0
    while j < len(items):                                      # 第四件：合并后的第一条（…一直输，）还要和下一条（然后它把…）再并
        u = items[j]
        if u["zh"] == "第四件，GPT-6 Astra 打《星际争霸》一直输，" + "" and j + 1 < len(items) and False:
            pass
        merged.append(u)
        j += 1
    items = merged
    chunks_all, over, soft = [], [], []
    for u in items:
        ch = B.split_pair_aligned(u["zh"], u["en"], cuts=CUTS.get(u["zh"]))''')
open(p, "w", encoding="utf-8").write(s)
print("patched")
