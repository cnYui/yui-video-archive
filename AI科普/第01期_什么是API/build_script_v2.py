"""Build 台本_v2.md and 配音分段_v2.json from one source of truth (lines + visuals + timing)."""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
CPS = 4.3          # TTS speed estimate: characters per second
SENT_PAUSE = 0.25  # extra seconds per sentence end

# Each scene: id, title, background, character notes, list of rows.
# Row: ("say", id, subtitle_text, tts_text, visual) or ("gap", seconds, visual)
SCENES = [
    dict(id="S00", title="片头", bg="片头自带", char="无", rows=[
        ("gap", 3.7, "UE 片头（现成，3.7 秒）"),
    ]),
    dict(id="S01", title="开场白", bg="BG1 STARRY 吧台（压暗）", char="从画面左侧走入，停在左 1/3 处，然后说话", rows=[
        ("gap", 1.2, "【动作：walk 走入】背景淡入；左上角小字「原LAI如此 #01」"),
        ("say", "01", "大家好，我是山田凉。今天给大家介绍API。",
         "大家好，我是山田凉。今天给大家介绍 A P I。",
         "【动作：说话】画面中央大字「API」"),
        ("gap", 0.4, ""),
    ]),
    dict(id="S02", title="三个疑问", bg="BG1 STARRY 吧台（压暗）", char="说话；只在“你可能会有三个疑问”时抬手一次", rows=[
        ("say", "02", "很多App都写着“已接入DeepSeek”，有些AI工具还要你填“API Key”。",
         "很多 App 都写着，已接入 Deep Seek。有些 A I 工具，还要你填 A P I Key。",
         "右侧手机界面示意：顶部横幅「已接入 DeepSeek」；下方一个设置框「API Key：______」（虚构界面，不用真实 App）"),
        ("say", "03", "你可能会有三个疑问：",
         "你可能会有三个疑问。",
         "【动作：抬手（本场唯一一次）】手机缩小移走，右侧出现标题「你可能也想问」"),
        ("say", "04", "第一，API是什么？",
         "第一，A P I 是什么？",
         "疑问卡 ①「API 是什么？」弹出（“嗒”）"),
        ("say", "05", "第二，App上写的“已接入”，接的是什么？",
         "第二，App 上写的已接入，接的是什么？",
         "疑问卡 ②「“已接入”接的是什么？」弹出（“嗒”）"),
        ("say", "06", "第三，API Key是什么，怎么拿到？",
         "第三，A P I Key 是什么，怎么拿到？",
         "疑问卡 ③「API Key 是什么？怎么拿到？」弹出（“嗒”）"),
        ("say", "07", "这期视频，就把这三个问题讲清楚。",
         "这期视频，就把这三个问题讲清楚。",
         "三张疑问卡排成一列，缩到画面右上角作为本期目录，常驻"),
        ("gap", 0.6, "转场：目录卡 ① 高亮放大"),
    ]),
    dict(id="S03", title="一、API 是什么", bg="BG1 STARRY 吧台（压暗）", char="说话；列要点时抬手", rows=[
        ("say", "08", "先说第一个问题：API是什么。",
         "先说第一个问题，A P I 是什么。",
         "章节标题「一、API 是什么」"),
        ("say", "09", "API是三个英文单词的缩写：Application Programming Interface。",
         "A P I，是三个英文单词的缩写。Application，Programming，Interface。",
         "三个单词依次出现，首字母 A、P、I 高亮"),
        ("say", "10", "中文叫“应用程序编程接口”。",
         "中文叫，应用程序编程接口。",
         "每个单词下方出现中文：应用程序 / 编程 / 接口"),
        ("say", "11", "这里的接口，指的是程序和程序之间的一套调用规则，跟USB那种插口没关系。",
         "这里的接口，指的是程序和程序之间的一套调用规则，跟 U S B 那种插口没关系。",
         "两个程序方块「程序 A」「程序 B」，中间一份「调用规则」；角落一个 USB 插口图标被划掉"),
        ("say", "12", "它主要规定三件事：",
         "它主要规定三件事。",
         "【动作：抬手】要点卡标题「调用规则主要规定：」"),
        ("say", "13", "能调用哪些功能，请求按什么格式发，结果按什么格式返回。",
         "能调用哪些功能。请求按什么格式发。结果按什么格式返回。",
         "要点逐条出现：① 能调用哪些功能 ② 请求的格式 ③ 返回的格式"),
        ("say", "14", "程序A按规则发出请求，程序B处理完，把结果返回来。这一来一回，就是一次API调用。",
         "程序 A 按规则发出请求，程序 B 处理完，把结果返回来。这一来一回，就是一次 A P I 调用。",
         "动画：一张「请求」从 A 飞向 B，一张「结果」从 B 飞回 A；下方标注「一次 API 调用」"),
        ("say", "16", "这些规则会写成一份说明书，叫接口文档。开发者照着它写代码，就能调用别人开放出来的功能。",
         "这些规则会写成一份说明书，叫接口文档。开发者照着它写代码，就能调用别人开放出来的功能。",
         "一份文档示意「接口文档」，旁边标「开发者照着写」"),
        ("gap", 0.6, "目录卡 ① 打勾；目录卡 ② 高亮"),
    ]),
    dict(id="S04", title="二、“已接入”接的是什么", bg="BG2 下北泽街道（压暗）", char="说话；讲流程时站在左下，不遮挡流程图", rows=[
        ("say", "17", "第二个问题：“已接入DeepSeek”，接的是什么。",
         "第二个问题，已接入 Deep Seek，接的是什么。",
         "章节标题「二、“已接入”接的是什么」"),
        ("say", "18", "多数情况下，接的是DeepSeek大模型的API。",
         "多数情况下，接的是 Deep Seek 大模型的 A P I。",
         "大字「接的是：DeepSeek 大模型的 API」"),
        ("say", "19", "你手机上的App负责界面，真正生成回答的大模型，跑在服务器上。",
         "你手机上的 App 负责界面，真正生成回答的大模型，跑在服务器上。",
         "流程图搭建：左「手机 App（界面）」，中间小方块「App 后台（通常有）」，右「服务器上的大模型」"),
        ("say", "20", "你在App里提问，App把问题按接口格式发给服务器。",
         "你在 App 里提问，App 把问题按接口格式，发给服务器。",
         "流程图第 1 段：问题从手机经「App 后台」，沿箭头飞向模型服务器；后台到模型这一段标「API 请求」"),
        ("say", "21", "模型生成回答，再通过API返回，显示在你的屏幕上。",
         "模型生成回答，再通过 A P I 返回，显示在你的屏幕上。",
         "流程图第 2 段：回答沿箭头飞回手机，箭头标「API 返回」"),
        ("say", "22", "这台服务器可能是DeepSeek官方的，也可能是云厂商或App厂商自己部署的。",
         "这台服务器，可能是 Deep Seek 官方的，也可能是云厂商或 App 厂商自己部署的。",
         "服务器下方三个标签：「DeepSeek 官方」「云厂商部署」「App 厂商自己部署」"),
        ("say", "23", "所以“已接入”，就是这个App通过API，调用了DeepSeek的模型。",
         "所以已接入，就是这个 App 通过 A P I，调用了 Deep Seek 的模型。",
         "结论卡「已接入 ＝ App 通过 API 调用 DeepSeek 的模型」"),
        ("say", "24", "不过，各家App接的型号、给的额度可能不一样，所以同样是“已接入”，用起来也会有差别。",
         "不过，各家 App 接的型号，给的额度，可能不一样。所以同样是已接入，用起来也会有差别。",
         "三个虚构 App 图标连着同一个模型，各自标「型号」「额度」，数值用 ×× 表示"),
        ("gap", 0.6, "目录卡 ② 打勾；目录卡 ③ 高亮"),
    ]),
    dict(id="S05", title="三、API Key 是什么", bg="BG1 STARRY 吧台（压暗）", char="说话；列要点时抬手", rows=[
        ("say", "25", "第三个问题：API Key是什么。",
         "第三个问题，A P I Key 是什么。",
         "章节标题「三、API Key 是什么」"),
        ("say", "26", "API Key就是调用API用的密钥，是一长串字符。比如DeepSeek的Key，以sk开头。",
         "A P I Key，就是调用 A P I 用的密钥，是一长串字符。比如 Deep Seek 的 Key，以 s k 开头。",
         "一条 Key 示意「sk-••••••••••••••••」（全程打码，不出现真实 Key）；标注「密钥」"),
        ("say", "27", "调用这类API时，程序每次都要带上这串Key。平台靠它确认三件事：",
         "调用这类 A P I 时，程序每次都要带上这串 Key。平台靠它确认三件事。",
         "请求示意：请求上贴着 Key；【动作：抬手】要点卡标题「平台用 Key 确认：」"),
        ("say", "28", "是谁在调用，有没有权限，费用记在谁的账上。",
         "是谁在调用。有没有权限。费用记在谁的账上。",
         "要点逐条出现：① 身份 ② 权限 ③ 计费"),
        ("say", "29", "大模型的API一般按用量收费，钱就从这个Key对应的账户里扣。",
         "大模型的 A P I，一般按用量收费，钱就从这个 Key 对应的账户里扣。",
         "示意：Key → 账户 → 余额，余额数字往下走（用 ×× 表示）"),
        ("say", "30", "所以API Key要像密码一样保管：不要发给别人，不要截图发到群里，也不要写进公开的代码。",
         "所以 A P I Key 要像密码一样保管。不要发给别人，不要截图发到群里，也不要写进公开的代码。",
         "三条禁止事项逐条出现，每条前一个红色 ✕"),
        ("say", "31", "如果怀疑泄露了，马上在平台上删掉这个Key，再新建一个。",
         "如果怀疑泄露了，马上在平台上删掉这个 Key，再新建一个。",
         "示意：旧 Key 被删除，新 Key 生成"),
        ("gap", 0.6, "目录卡 ③ 高亮保持（后半题：怎么拿到）"),
    ]),
    dict(id="S06", title="实操：获取 DeepSeek API Key", bg="录屏窗口 + BG1 压暗垫底", char="缩小到左下角，只做说话和偶尔抬手，不遮挡录屏", rows=[
        ("say", "32", "下面说怎么拿到DeepSeek的API Key，一共四步。",
         "下面说怎么拿到 Deep Seek 的 A P I Key，一共四步。",
         "章节标题「实操：获取 DeepSeek API Key」（对应目录卡 ③ 的后半题）；右侧步骤条 ①②③④"),
        ("say", "33", "第一步，打开DeepSeek开放平台，网址是platform.deepseek.com，注册并登录。",
         "第一步，打开 Deep Seek 开放平台。网址是 platform 点 deepseek 点 com。注册并登录。",
         "录屏：浏览器地址栏输入 platform.deepseek.com，进入登录页；地址栏放大高亮"),
        ("say", "34", "注意，它和平时聊天用的DeepSeek网页不是同一个入口。",
         "注意，它和平时聊天用的 Deep Seek 网页，不是同一个入口。",
         "对比小卡：左「chat.deepseek.com 聊天」右「platform.deepseek.com 开放平台（本期用这个）」"),
        ("gap", 1.0, "录屏：登录后进入开放平台首页（账号信息打码）"),
        ("say", "35", "第二步，在左侧菜单点“API keys”，再点“创建API key”，起一个名字，点创建。",
         "第二步，在左侧菜单点 A P I keys，再点创建 A P I key。起一个名字，点创建。",
         "录屏：左侧菜单「API keys」高亮 → 点「创建 API key」→ 输入名称「测试用」→ 点创建；鼠标位置加圆圈提示"),
        ("gap", 1.0, "录屏：弹出新 Key 的窗口（Key 全程打码）"),
        ("say", "36", "第三步，复制这串Key，保存到安全的地方。它只在创建时完整显示一次，之后就看不到完整的Key了。",
         "第三步，复制这串 Key，保存到安全的地方。它只在创建时完整显示一次，之后就看不到完整的 Key 了。",
         "录屏：点「复制」；Key 打码；画面上加提示条「只显示一次，先保存」"),
        ("say", "37", "如果弄丢了，删掉重新创建就行。",
         "如果弄丢了，删掉重新创建就行。",
         "录屏：API keys 列表里「删除」按钮高亮"),
        ("say", "38", "第四步，充值。充值前要先按页面提示完成实名认证。账户里没余额，调用就会报错，提示余额不足。",
         "第四步，充值。充值前，要先按页面提示完成实名认证。账户里没余额，调用就会报错，提示余额不足。",
         "录屏：实名认证页（姓名、证件号全部打码）→「充值」页面（金额、支付信息打码）；旁边小卡「余额不足 → 报错 402」"),
        ("say", "39", "自己测试的话，少充一点就够了。价格可以看官网的价格页。",
         "自己测试的话，少充一点就够了。价格可以看官网的价格页。",
         "录屏：切到文档「模型 & 价格」页（只停留，不念数字）"),
        ("gap", 0.8, "步骤条 ①②③④ 全部打勾"),
        ("say", "40", "拿到Key以后，在支持DeepSeek的工具里填上它。有的工具还要填接口地址和模型名，照着屏幕填就行。",
         "拿到 Key 以后，在支持 Deep Seek 的工具里填上它。有的工具，还要填接口地址和模型名，照着屏幕填就行。",
         "设置卡（虚构工具界面）：API Key「sk-••••」／接口地址「https://api.deepseek.com」，下方小字「Anthropic 格式的工具填 https://api.deepseek.com/anthropic」／模型名「deepseek-flash」；角标「截至 2026 年 9 月，以官方文档为准」"),
        ("gap", 1.5, "设置卡停留，方便截图"),
        ("gap", 0.4, "目录卡 ③ 打勾"),
    ]),
    dict(id="S07", title="总结", bg="BG1 STARRY 吧台（压暗）", char="回到左 1/3，说话", rows=[
        ("say", "41", "最后总结一下。",
         "最后总结一下。",
         "总结卡标题「本期总结」"),
        ("say", "42", "第一，API是程序之间的调用规则，全称应用程序编程接口。",
         "第一，A P I 是程序之间的调用规则，全称应用程序编程接口。",
         "总结卡 ①"),
        ("say", "43", "第二，“已接入DeepSeek”，一般就是App通过API调用了DeepSeek的模型。",
         "第二，已接入 Deep Seek，一般就是 App 通过 A P I，调用了 Deep Seek 的模型。",
         "总结卡 ②"),
        ("say", "44", "第三，API Key是调用API的密钥，用来认身份、算费用，一定要保管好。",
         "第三，A P I Key 是调用 A P I 的密钥，用来认身份、算费用，一定要保管好。",
         "总结卡 ③（三条同时可见，可截图）"),
        ("say", "45", "下期讲token：你问AI一句话，到底花了多少钱。",
         "下期讲 token。你问 A I 一句话，到底花了多少钱。",
         "预告条「下期：你问 AI 一句话，花了多少钱？」"),
        ("say", "46", "我是山田凉，我们下期见。",
         "我是山田凉，我们下期见。",
         "【动作：walk 走出画面】或停在 idle；右下角「原LAI如此」"),
        ("gap", 0.5, "淡出到片尾"),
    ]),
    dict(id="S08", title="片尾", bg="片尾自带", char="无", rows=[
        ("gap", 4.8, "本期制作清单（现成片尾，4.8 秒）"),
    ]),
]


def spoken_units(text):
    """Estimate spoken length: CJK char = 1, spelled letters = 1 each, English word ~ 1 per 3 letters."""
    n = len(re.findall(r'[一-鿿]', text))
    for tok in re.findall(r'[A-Za-z]+', text):
        if tok.isupper() and len(tok) <= 3:
            n += len(tok)
        else:
            n += max(1, round(len(tok) / 3))
    n += len(re.findall(r'\d', text))
    return n


def fmt(t):
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:04.1f}"


def build():
    t = 0.0
    voice, md_scenes, outline = [], [], []
    total_units = 0
    for sc in SCENES:
        start = t
        rows_md = []
        for row in sc["rows"]:
            if row[0] == "gap":
                _, dur, visual = row
                rows_md.append(f"| {fmt(t)}–{fmt(t + dur)} | （画面） | {visual} |")
                t += dur
            else:
                _, sid, text, tts, visual = row
                units = spoken_units(tts)
                sentences = max(1, len(re.findall(r'[。？！]', tts)))
                dur = round(units / CPS + sentences * SENT_PAUSE, 1)
                total_units += units
                seg_id = f"{sc['id']}-{sid}"
                voice.append(dict(id=seg_id, scene=sc["id"], text=text, tts_text=tts,
                                  start=round(t, 1), est_seconds=dur))
                rows_md.append(f"| {fmt(t)}–{fmt(t + dur)} | **{seg_id}** {text} | {visual} |")
                t += dur
        outline.append((sc, start, t))
        md_scenes.append((sc, start, t, rows_md))
    return voice, md_scenes, outline, t, total_units


def main():
    voice, md_scenes, outline, total, units = build()
    speech = sum(v["est_seconds"] for v in voice)
    L = []
    L.append("# 《原LAI如此》第 1 期「什么是 API」台本 v2\n")
    L.append("- 日期：2026-09-26")
    L.append(f"- 预计总长：**{fmt(total)}**（配音按每秒 {CPS} 字估算，试读后按实际长度校准）")
    L.append(f"- 台词：{len(voice)} 段，约 {units} 字，配音约 {speech:.0f} 秒")
    L.append("- 讲解员：山田凉（像素形象）。动作只用三种：走入 / 走出、说话口型、讲要点时抬手；没有其他小动作和性格梗。")
    L.append("- 背景：《孤独摇滚！》场景空镜（画面里不出现原作角色），压暗后使用。")
    L.append("- v1 → v2：按用户意见重写。开场一句话；先抛三个疑问再讲；只讲 API、“已接入”、API Key、DeepSeek Key 获取四块；不用比喻；删掉吃草、借钱、怪人、小元等和知识无关的内容。")
    L.append("- 审校：口播编辑（语气、结构）和技术审校（事实）各看一遍，意见已全部改进本版。段号保留原编号，所以中间有空号（S03-15 已删）。\n")

    L.append("## 结构\n")
    L.append("| 场 | 时间 | 内容 | 背景 |")
    L.append("|---|---|---|---|")
    for sc, s, e in outline:
        L.append(f"| {sc['id']} | {fmt(s)}–{fmt(e)} | {sc['title']} | {sc['bg']} |")
    L.append("")

    L.append("## 分场台本\n")
    L.append("说明：粗体编号是配音段，后面的文字就是字幕。动作只标出“走入 / 走出 / 抬手”，其余时间说话时动嘴、不说话时待机呼吸。\n")
    for sc, s, e, rows in md_scenes:
        L.append(f"### {sc['id']}｜{sc['title']}｜{fmt(s)}–{fmt(e)}\n")
        L.append(f"- 背景：{sc['bg']}")
        L.append(f"- 角色：{sc['char']}\n")
        L.append("| 时间 | 台词（＝字幕） | 画面 |")
        L.append("|---|---|---|")
        L.extend(rows)
        L.append("")

    L.append("## 制作说明\n")
    L.append("### 角色动作（只用这几种）\n")
    L.append("| 动作 | 来源 | 用在哪 |")
    L.append("|---|---|---|")
    L.append("| 走入 / 走出 | 素材包 walk（正面走路），整体从画面左侧平移进来 | S01 开头、S07 结尾 |")
    L.append("| 待机 | 素材包 idle（待机呼吸） | 不说话的时候 |")
    L.append("| 说话 | 新生成：在 idle 上逐帧叠 2–3 个嘴型（用素材包 `源代码/ryo` 的现成嘴型部件拼，不新画像素） | 所有台词 |")
    L.append("| 抬手 | 素材包身体姿势 reach（伸手，掌心朝右），配合说话口型 | 全片 5 次左右：抛出疑问前、列要点时，每次约 1 秒 |")
    L.append("")
    L.append("- 角色 ×6 放大（最近邻），站画面左 1/3；S04 讲流程和 S06 录屏时缩到 ×4 放左下角。不镜像翻转。")
    L.append("- 不用：吃草、借钱、被叫怪人、睡觉、贝斯、贴纸表情。\n")

    L.append("### 背景\n")
    L.append("- BG1：STARRY Live House 吧台（空镜）。用在 S01–S03、S05、S07，S06 录屏时垫底。")
    L.append("- BG2：下北泽街道（空镜）。用在 S04。")
    L.append("- 处理：深色底 + 背景不透明度约 45% + 轻微模糊，保证文字卡和角色清楚。\n")

    L.append("### 画面风格\n")
    L.append("- 文字卡片：纸白底、墨黑字、橙色强调，和片头片尾同一套配色。每个要点一张卡，编号清楚。")
    L.append("- 字幕放底部居中，避开左侧角色。术语（API、接口文档、API Key）用橙色。")
    L.append("- S06 录屏：用浏览器实际录制 DeepSeek 开放平台的操作。账号、余额、实名信息、Key 全部打码，画面上不能出现真实 Key。")
    L.append("- App、工具界面都用虚构示意，不用真实 App 截图和 logo。")
    L.append("- 音效只用两种：卡片出现的轻“嗒”声、打勾声。BGM 用无人声的轻音乐，人声时压低。\n")

    L.append("### 配音\n")
    L.append("- 按 `配音分段_v2.json` 的 `tts_text` 生成，字幕用 `text`。")
    L.append("- 英文读法：API 写成“A P I”逐个字母读；DeepSeek 写成“Deep Seek”；网址念“platform 点 deepseek 点 com”。试读时重点听这几处。\n")

    L.append("### 出片前核对\n")
    L.append("1. 开放平台的菜单名（“API keys”“创建 API key”“充值”）、Key 是否只完整显示一次、Key 是否以 sk 开头、充值前是否要实名认证：官方文档里查不到原文，录屏时以实际页面为准，不一致就改台词。")
    L.append("2. 接口地址 `https://api.deepseek.com`（OpenAI 格式）/ `https://api.deepseek.com/anthropic`（Anthropic 格式）、模型名 `deepseek-flash`：已按 2026-09-26 的官方文档核对（api-docs.deepseek.com）。出片前再看一次。")
    L.append("3. 余额不足报错码 402：已按官方文档“错误码”页核对。")

    (HERE / "台本_v2.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (HERE / "配音分段_v2.json").write_text(json.dumps(voice, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"total={fmt(total)} ({total:.1f}s) speech={speech:.1f}s segments={len(voice)} units={units}")


if __name__ == "__main__":
    main()
