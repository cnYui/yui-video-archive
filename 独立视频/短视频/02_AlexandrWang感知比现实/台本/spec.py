# -*- coding: utf-8 -*-
r"""《Alexandr Wang：大客户眼里，感知比现实更真实》—— 本条的台本和画面表（gen.py 读它生成 录制稿.json / plan.json）。

素材 w = South Park Commons《Minus One》播客「Alexandr Wang, Scale AI, & the Startup Hunger Games」全程（Aditya Agarwal 主持，2024-12-13 发；Wang 当时是 Scale AI 创始人兼 CEO）。
切点按真实静音（asr/chunks.py：能量 < −46 dB 的 10 ms 格分块；Whisper 的词级时间会偏 0.1–0.4 s，只用来读文字），t = 这句英文的开口（块起点）：
  688.11 / 691.51  “But at a lot of large customers, | perception is more real than reality.”
  672.30 / 676.96  data-driven companies … | the truth makes its way.      680.52 / 683.51  Everybody serves a shared sense of reality … | not true at most large companies … government
  693.83 / 696.42 / 699.58  the reality is just so ugly | very rarely do people actually confront reality | choose to believe the perceptions that they live in
  703.65 + 712.25  enterprise sales … [删掉 “that you have to, you know,”] just as much as your job is to improve the reality, it is to shape the perception
  720.88 / 722.99 / 729.26 / 731.40 / 736.12  Palantir's superpowers … | acting troupe combined with a software company | acting book to all of the new hires
  773.66  I think fundamentally you also need to build a good product.（主持人 Aditya 在 764–773 s 说“dark arts on top of a good product”，Wang 接这句）
镜头（ffmpeg 场景检测 + 缩略图人工分类，asr/shots_raw.json）：655–742 Wang 特写（绿植 + 青墙）；581–641 双人远景；742–776 双人远景；447–581 Wang 特写。
事实核对：同目录 事实核对_来源与原话.md / 事实核对_Wang近期事件.md / 事实核对_Palantir.md。口径：Wang 访谈时是 Scale AI CEO（不写“Meta 首席 AI 官在访谈里说”）；
“感知比现实更真实”必须带“很多大客户”；《Impro》是外界 / 前员工的说法，Wang 没点书名；Slate 的判断挂名 Slate；价格是 Wang 自己报的。
同传句对着英文分句落（每句 a = 英文开口 − 段起点 + 0.4 s），这样中文字幕不会提前一大截结束、重点句和英文重点句同时出现。
"""

SLUG = "Wang感知比现实"
TITLE = "Alexandr Wang：大客户眼里，感知比现实更真实（SPC 播客 2024-12 的旧访谈，2026-10 在 X 上重新流传）"
KICKER = "悠一 · <b>Alexandr Wang</b> 访谈"
HOOK = ["大客户眼里", "感知比现实更真实"]
CREDIT = "SPC 播客 · 2024-12"
NOTE = ("双分镜：上框 = 播客原片（Wang 特写，原声压低留着，同传盖上去；解说段上框也是 Wang 特写但静音），下框 = 双人远景 B-roll（静音）或页面录屏（pageShot {lower:true}）。"
        "同传句带橙色“Wang”标签（who），解说句不带。人称：同传 / 解说都不用“我”；Wang 访谈时是 Scale AI CEO，现在是 Meta 首席 AI 官。配音声线「温柔男生」（2026-10-04 起）。")


def R(a, b, **kw):
    return dict(src="w", **{"in": a, "out": b}, **kw)


SCENES = [
    # S1 钩子：同传按两个英文分句落（第二句落在英文的重点上）
    dict(id="S1", name="钩子：感知比现实更真实",
         up=[R(688.01, 693.61)],
         low=[R(743.0, 749.5)],
         lines=[dict(id="N01", who="Wang", t=688.11,
                     zh="在很多大客户那里", say="在很多大客户那里，",
                     en="At a lot of large customers,"),
                dict(id="N02", who="Wang", t=691.51,
                     zh="感知比现实更真实。",
                     en="perception is more real than reality.")]),

    # S2 背书：2024-12、SPC 播客、当时 Scale AI CEO、现在 Meta 首席 AI 官（下框：SPC 节目页）
    dict(id="S2", name="背书：2024 年 12 月的旧访谈",
         up=[R(500.0, 507.5, mute=True)],
         low=[R(405.0, 412.5)],
         lines=[dict(id="N03", a=0.0,
                     zh="这是 2024 年 12 月的一期播客。",
                     say="这是二零二四年十二月的一期播客。",
                     en="This is a podcast episode from December 2024."),
                dict(id="N04", a=0.0,
                     zh="那时 Wang 是 Scale AI 的 CEO，现在是 Meta 首席 AI 官。",
                     say="那时亚历山大·王是 Scale AI 的 CEO，现在是 Meta 首席 AI 官。",
                     en="Back then Wang was Scale AI's CEO. Now he's Meta's chief AI officer.")]),

    # S3 数据驱动的公司 vs 大公司、政府（两段原话：672.30–678.15 / 680.52–687.78）
    dict(id="S3", name="数据驱动的公司 vs 大公司、政府",
         up=[R(672.20, 678.25), R(680.42, 687.88)],
         low=[R(581.4, 594.9)],
         lines=[dict(id="N05", who="Wang", t=672.30, seg=0,
                     zh="在座各位合作过的公司，多半靠数据说话", say="在座各位合作过的公司，多半靠数据说话，",
                     en="The companies everyone here has worked with are mostly data-driven."),
                dict(id="N06", who="Wang", t=676.96, seg=0,
                     zh="真相自己会浮出来。",
                     en="It feels like the truth makes its way."),
                dict(id="N07", who="Wang", t=680.52, seg=1,
                     zh="大家共享同一个现实。",
                     en="Everybody shares one sense of reality."),
                dict(id="N08", who="Wang", t=683.51, seg=1,
                     zh="但多数大公司不是这样，政府里也不是。",
                     en="But not at most large companies, nor in government, unfortunately.")]),

    # S4 现实太难看（693.83–703.5）
    dict(id="S4", name="现实太难看，人们选择相信感知",
         up=[R(693.73, 703.55)],
         low=[R(594.9, 604.7)],
         lines=[dict(id="N09", who="Wang", t=693.83,
                     zh="现实往往太难看", say="现实往往太难看，",
                     en="Reality is usually so ugly"),
                dict(id="N10", who="Wang", t=696.42,
                     zh="很少有人愿意直面。",
                     en="that people very rarely confront it."),
                dict(id="N11", who="Wang", t=699.58,
                     zh="多数时候，人们宁愿相信自己活在其中的感知。",
                     en="Mostly they choose to believe the perceptions they live in.")]),

    # S5 企业销售：改善现实，也要塑造感知（703.65–709.7 / 712.25–716.09，删掉了 “that you have to, you know,”）
    dict(id="S5", name="做企业销售：改善现实，也要塑造感知",
         up=[R(703.60, 709.80), R(712.15, 716.19)],
         low=[R(604.7, 615.0)],
         lines=[dict(id="N12", who="Wang", t=703.65, seg=0,
                     zh="所以做企业销售、做企业产品", say="所以做企业销售、做企业产品，",
                     en="So if you do enterprise sales or build enterprise products,"),
                dict(id="N13", who="Wang", t=712.25, seg=1,
                     zh="工作既是改善现实，同样也是塑造感知。",
                     en="your job is to improve the reality, just as much as to shape the perception.")]),

    # S6 Palantir：半个表演剧团，半个软件公司，表演书（720.88–742.14）
    dict(id="S6", name="Palantir：半个表演剧团，半个软件公司",
         up=[R(720.78, 742.26)],
         low=[R(615.0, 636.5)],
         lines=[dict(id="N14", who="Wang", t=720.88,
                     zh="Palantir 的绝活之一，", say="帕兰提尔的绝活之一，",
                     en="One of Palantir's superpowers:"),
                dict(id="N15", who="Wang", t=722.99,
                     zh="是比大多数科技公司更会塑造感知。",
                     en="they shape perception better than most tech companies."),
                dict(id="N16", who="Wang", t=729.26,
                     zh="因为它觉得", say="因为它觉得，",
                     en="Because they view themselves"),
                dict(id="N17", who="Wang", t=731.40,
                     zh="自己像半个表演剧团，半个软件公司。",
                     en="as part acting troupe, part software company."),
                dict(id="N18", who="Wang", t=736.12,
                     zh="这还不是比喻：它真的给所有新员工发一本表演书，发了很久。",
                     en="And I'm not even speaking figuratively: they literally gave all new hires an acting book, for a very long time.")]),

    # S7 外界的说法：前员工 Qureshi 和《Impro》（下框：Qureshi 的文章）
    dict(id="S7", name="前员工 Qureshi：入职时寄几本书，有一本是《Impro》",
         up=[R(520.0, 529.0, mute=True)],
         low=[R(420.0, 429.0)],
         lines=[dict(id="N19", a=0.0,
                     zh="Palantir 前员工 Qureshi 写过：入职时公司寄来几本书，有一本是讲即兴戏剧的《Impro》。",
                     say="帕兰提尔前员工库雷希写过：入职时公司寄来几本书，有一本是讲即兴戏剧的《Impro》。",
                     en="Ex-Palantir engineer Nabeel Qureshi wrote that new hires were sent a few books, one of them Impro, on improv theater."),
                dict(id="N20", a=0.0,
                     zh="现在还发不发，他也不确定。",
                     en="Whether they still do, he says he isn't sure.")]),

    # S8 Wang 自己补一句：根本上还得做出好产品（主持人在 764–773 s 说“dark arts on top of a good product”）
    dict(id="S8", name="Wang 自己补一句：根本上要做好产品",
         up=[R(773.56, 776.06, crop=[0.06, 0.18, 0.66, 0.78])],
         low=[R(755.0, 758.0)],
         lines=[dict(id="N21", who="Wang", t=773.66,
                     zh="不过根本上，还是得做出好产品。",
                     en="Fundamentally, you also need to build a good product.")]),

    # S9a 相关事件：Connect 的 30 美元 T 恤（下框：Wang 的 X 帖）
    dict(id="S9", name="相关事件：Meta Connect 的 30 美元 T 恤",
         up=[R(545.0, 551.3, mute=True)],
         low=[R(432.0, 438.3)],
         lines=[dict(id="N22", a=0.0,
                     zh="9 月 23 日，Meta 发布会：Wang 上台穿的 T 恤，他自己说是 30 美元的二手货。",
                     say="九月二十三日，Meta 发布会：亚历山大·王上台穿的体恤衫，他自己说是三十美元的二手货。",
                     en="Sept. 23, Meta Connect: Wang took the stage in a T-shirt he says was a $30 thrift find.")]),

    # S9b Slate 的判断（下框：Slate 文章）
    dict(id="S9b", name="相关事件：Slate 的判断",
         up=[R(553.0, 557.2, mute=True)],
         low=[R(440.0, 444.2)],
         lines=[dict(id="N23", a=0.0,
                     zh="10 月 3 日，Slate 发文：硅谷大佬发现了“显得无害”的好处。",
                     say="十月三日，Slate 发文：硅谷大佬发现了“显得无害”的好处。",
                     en="Oct. 3, Slate: Silicon Valley's most powerful men have discovered the appeal of looking harmless.")]),

    # S10 收尾
    dict(id="S10", name="收尾：感知放大现实，替代不了现实",
         up=[R(561.0, 564.0, mute=True)],
         low=[R(398.5, 401.5)],
         lines=[dict(id="N24", a=0.0,
                     zh="感知能放大现实，替代不了现实。",
                     en="Perception can amplify reality. It can't replace it.")]),
]
