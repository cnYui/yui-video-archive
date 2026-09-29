"""Build 台本_v3.md and 配音分段_v3.json from one source of truth (lines + visuals + timing)."""
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
    dict(id="S06", title="四、主流的三种调用方式", bg="BG1 STARRY 吧台（压暗）", char="缩到 ×4 放左下角，只做说话，列要点时抬手；画面主体给代码卡", rows=[
        ("say", "", "再看一下，调用大模型的API具体长什么样。",
         "再看一下，调用大模型的 A P I，具体长什么样。",
         "章节标题「四、主流的三种调用方式」"),
        ("say", "", "不管哪家，都是向一个网址发一个HTTP请求，请求和结果都用JSON格式写。",
         "不管哪家，都是向一个网址，发一个 H T T P 请求。请求和结果，都用 JSON 格式写。",
         "示意：一个网址 → 一张 JSON 请求卡发出去 → 一张 JSON 结果卡回来；标注「HTTP 请求」「JSON」"),
        ("say", "", "现在主流的格式有三种。",
         "现在主流的格式有三种。",
         "【动作：抬手】三张标签依次出现：① Chat Completions ② Responses ③ Claude Messages"),
        ("gap", 0.4, "标签 ① 放大"),
        # --- Chat Completions ---
        ("say", "", "第一种，OpenAI的Chat Completions，地址结尾是/chat/completions。",
         "第一种，Open A I 的 Chat Completions，地址结尾是 chat completions。",
         "代码卡①（简化示意）：POST /v1/chat/completions，地址部分橙色高亮"),
        ("say", "", "请求里主要写两样：model是用哪个模型，messages是对话记录。",
         "请求里主要写两样。model，是用哪个模型。messages，是对话记录。",
         "代码卡①请求体逐行高亮：\"model\": \"gpt-5.5\" / \"messages\": [ … ]"),
        ("say", "", "每条消息都标明角色：system是设定，user是用户，assistant是模型的回复。",
         "每条消息都标明角色。system 是设定，user 是用户，assistant 是模型的回复。",
         "messages 里三条消息，role 分别标 system / user / assistant"),
        ("say", "", "回答放在返回结果的choices里。",
         "回答，放在返回结果的 choices 里。",
         "代码卡①返回体：choices[0].message.content 高亮；usage 一行灰色"),
        ("say", "", "这是用得最广的格式，DeepSeek和很多国产模型都兼容它。",
         "这是用得最广的格式。Deep Seek，和很多国产模型，都兼容它。",
         "代码卡①下方小字「兼容：DeepSeek 等」"),
        ("gap", 0.4, "标签 ② 放大"),
        # --- Responses ---
        ("say", "", "第二种，OpenAI的Responses，地址结尾是/responses。",
         "第二种，Open A I 的 Responses，地址结尾是 responses。",
         "代码卡②（简化示意）：POST /v1/responses"),
        ("say", "", "这是OpenAI在2025年推出的新接口，官方推荐新项目用它。",
         "这是 Open A I 在2025年推出的新接口，官方推荐新项目用它。",
         "角标「官方：新项目推荐 Responses；Chat Completions 继续支持」"),
        ("say", "", "它用input代替messages，设定写在单独的instructions字段里。",
         "它用 input 代替 messages，设定写在单独的 instructions 字段里。",
         "代码卡②请求体：\"instructions\": \"…\" / \"input\": \"…\"；旁边对照卡①的 messages，用箭头表示替换"),
        ("say", "", "返回的output是一组条目，除了文字，还可以有工具调用的结果。",
         "返回的 output，是一组条目。除了文字，还可以有工具调用的结果。",
         "代码卡②返回体：output 数组里两个条目，一个 type 为文字消息，一个为工具调用"),
        ("say", "", "它还能用previous_response_id接上一轮对话，不用每次把聊天记录全部重发。",
         "它还能用 previous response id，接上一轮对话，不用每次把聊天记录全部重发。",
         "示意：第二次请求只带「previous_response_id」和新问题，前面的聊天记录由服务器接上"),
        ("gap", 0.4, "标签 ③ 放大"),
        # --- Claude Messages ---
        ("say", "", "第三种，Anthropic的Messages，也就是Claude的接口，地址是/v1/messages。",
         "第三种，Anthropic 的 Messages，也就是 Claude 的接口，地址是 v1 messages。",
         "代码卡③（简化示意）：POST https://api.anthropic.com/v1/messages"),
        ("say", "", "它和OpenAI的格式有三点不同。",
         "它和 Open A I 的格式，有三点不同。",
         "【动作：抬手】对比小标题「和 OpenAI 格式的不同」"),
        ("say", "", "第一，认证。Key放在x-api-key请求头里，还要带上anthropic-version版本号；OpenAI格式放在Authorization里。",
         "第一，认证。Key 放在 x api key 请求头里，还要带上 anthropic version 版本号。Open A I 的格式，放在 Authorization 里。",
         "请求头对比：左「Authorization: Bearer sk-••••」右「x-api-key: sk-ant-••••」+「anthropic-version: 2023-06-01」"),
        ("say", "", "第二，请求。max_tokens必须填，设定用单独的system字段，不放进messages。",
         "第二，请求。max tokens 必须填。设定用单独的 system 字段，不放进 messages。",
         "代码卡③请求体：\"model\": \"claude-opus-5\" / \"max_tokens\": 1024（标「必填」）/ \"system\": \"…\" / \"messages\": [ … ]"),
        ("say", "", "第三，返回。回答放在content数组里，分成一个个内容块，每块标明类型，比如text是文字，tool_use是工具调用。",
         "第三，返回。回答放在 content 数组里，分成一个个内容块。每块标明类型，比如 text 是文字，tool use 是工具调用。",
         "代码卡③返回体：content 数组里两个块，type 分别为 text 和 tool_use；下方一行 usage（input_tokens / output_tokens）"),
        ("gap", 0.5, "三张代码卡缩小并排"),
        # --- Streaming ---
        ("say", "", "另外，想让回答一段一段地出来，三种接口都可以把stream设成true。",
         "另外，想让回答一段一段地出来，三种接口，都可以把 stream 设成 true。",
         "三张卡上同时出现一行 \"stream\": true"),
        ("say", "", "服务器会用SSE，也就是服务器推送事件，把结果一段段推过来。",
         "服务器会用 S S E，也就是服务器推送事件，把结果一段段推过来。",
         "示意：服务器向手机连续推送一小段一小段的数据，标注「SSE 服务器推送事件」"),
        ("say", "", "Claude的推送按事件来：message_start是开始，content_block_delta是一段段文字，message_stop是结束。",
         "Claude 的推送，按事件来。message start 是开始，content block delta 是一段段文字，message stop 是结束。",
         "事件流示意，从上到下依次出现：message_start → content_block_start → content_block_delta ×N → content_block_stop → message_delta → message_stop；念到的三个橙色高亮"),
        ("gap", 0.4, ""),
        ("say", "", "所以在工具里填接口地址时，要先看它用的是哪种格式。",
         "所以在工具里填接口地址时，要先看它用的是哪种格式。",
         "对比总表（可截图）：格式｜地址结尾｜Key 放在｜输入字段｜回答在哪 —— Chat Completions｜/chat/completions｜Authorization｜messages｜choices ／ Responses｜/responses｜Authorization｜input｜output ／ Claude Messages｜/v1/messages｜x-api-key｜messages + system｜content"),
        ("gap", 1.5, "对比总表停留，方便截图"),
    ]),
    dict(id="S07", title="实操：获取 DeepSeek API Key", bg="录屏窗口 + BG1 压暗垫底", char="缩小到左下角，只做说话和偶尔抬手，不遮挡录屏", rows=[
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
        ("say", "40", "拿到Key以后，在支持DeepSeek的工具里填上它。有的工具还要填接口地址和模型名。",
         "拿到 Key 以后，在支持 Deep Seek 的工具里填上它。有的工具，还要填接口地址和模型名。",
         "设置卡（虚构工具界面）：API Key「sk-••••」／接口地址／模型名「deepseek-flash」；角标「截至 2026 年 9 月，以官方文档为准」"),
        ("say", "40", "DeepSeek两种格式都支持：OpenAI格式和Anthropic格式的地址不一样，照着屏幕填就行。",
         "Deep Seek 两种格式都支持。Open A I 格式和 Anthropic 格式的地址不一样，照着屏幕填就行。",
         "设置卡接口地址一栏分两行：「OpenAI 格式：https://api.deepseek.com」「Anthropic 格式：https://api.deepseek.com/anthropic」"),
        ("gap", 1.5, "设置卡停留，方便截图"),
        ("gap", 0.4, "目录卡 ③ 打勾"),
    ]),
    dict(id="S08", title="总结", bg="BG1 STARRY 吧台（压暗）", char="回到左 1/3，说话", rows=[
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
         "总结卡 ③"),
        ("say", "45", "第四，主流的调用格式有三种：Chat Completions、Responses，和Claude的Messages。",
         "第四，主流的调用格式有三种。Chat Completions，Responses，和 Claude 的 Messages。",
         "总结卡 ④（四条同时可见，可截图）"),
        ("say", "46", "我是山田凉，我们下期见。",
         "我是山田凉，我们下期见。",
         "【动作：walk 走出画面】或停在 idle；右下角「原LAI如此」"),
        ("gap", 0.5, "淡出到片尾"),
    ]),
    dict(id="S09", title="片尾", bg="片尾自带", char="无", rows=[
        ("gap", 4.8, "本期制作清单（现成片尾，4.8 秒）"),
    ]),
]


def spoken_units(text):
    """Estimate spoken length: CJK char = 1, spelled letters = 1 each, English word ~ 1 per 3 letters."""
    n = len(re.findall(r'[一-鿿]', text))
    for tok in re.findall(r'[A-Za-z]+', text):
        if tok.isupper() and len(tok) <= 4:
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
    n = 0
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
                n += 1
                seg_id = f"{sc['id']}-{n:02d}"
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
    L.append("# 《原LAI如此》第 1 期「什么是 API」台本 v3\n")
    L.append("- 日期：2026-09-26")
    L.append(f"- 预计总长：**{fmt(total)}**（配音按每秒 {CPS} 字估算，试读后按实际长度校准）")
    L.append(f"- 台词：{len(voice)} 段，约 {units} 字，配音约 {speech:.0f} 秒")
    L.append("- 讲解员：山田凉（像素形象）。动作只用三种：走入 / 走出、说话口型、讲要点时抬手；没有其他小动作和性格梗。")
    L.append("- 背景：《孤独摇滚！》场景空镜（画面里不出现原作角色），压暗后使用。")
    L.append("- v1 → v2：按用户意见重写。开场一句话；先抛三个疑问再讲；只讲 API、“已接入”、API Key、DeepSeek Key 获取四块；不用比喻；删掉吃草、借钱、怪人、小元等和知识无关的内容。")
    L.append("- 审校：口播编辑（语气、结构）和技术审校（事实）各看一遍 v2，意见已全部改进。")
    L.append("- v2 → v3：删掉下期预告；新增第四节“主流的三种调用方式”（/chat/completions、/responses、Claude 的 /v1/messages 和流式推送）；实操结尾补上 DeepSeek 两种格式的地址；总结加第四条。段号按顺序重新编号。\n")

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
    L.append("- 角色 ×6 放大（最近邻），站画面左 1/3；S04 讲流程、S06 代码卡和 S07 录屏时缩到 ×4 放左下角。不镜像翻转。")
    L.append("- 不用：吃草、借钱、被叫怪人、睡觉、贝斯、贴纸表情。\n")

    L.append("### 背景\n")
    L.append("- BG1：STARRY Live House 吧台（空镜）。用在 S01–S03、S05、S06、S08，S07 录屏时垫底。")
    L.append("- BG2：下北泽街道（空镜）。用在 S04。")
    L.append("- 处理：深色底 + 背景不透明度约 45% + 轻微模糊，保证文字卡和角色清楚。\n")

    L.append("### 画面风格\n")
    L.append("- 文字卡片：纸白底、墨黑字、橙色强调，和片头片尾同一套配色。每个要点一张卡，编号清楚。")
    L.append("- 字幕放底部居中，避开左侧角色。术语（API、接口文档、API Key）用橙色。")
    L.append("- S06 录屏：用浏览器实际录制 DeepSeek 开放平台的操作。账号、余额、实名信息、Key 全部打码，画面上不能出现真实 Key。")
    L.append("- App、工具界面都用虚构示意，不用真实 App 截图和 logo。")
    L.append("- 音效只用两种：卡片出现的轻“嗒”声、打勾声。BGM 用无人声的轻音乐，人声时压低。\n")

    L.append("### 配音\n")
    L.append("- 按 `配音分段_v3.json` 的 `tts_text` 生成，字幕用 `text`。")
    L.append("- 英文读法：API 写成“A P I”逐个字母读；DeepSeek 写成“Deep Seek”；网址念“platform 点 deepseek 点 com”。试读时重点听这几处。\n")

    L.append("### 出片前核对\n")
    L.append("1. 开放平台的菜单名（“API keys”“创建 API key”“充值”）、Key 是否只完整显示一次、Key 是否以 sk 开头、充值前是否要实名认证：官方文档里查不到原文，录屏时以实际页面为准，不一致就改台词。")
    L.append("2. 接口地址 `https://api.deepseek.com`（OpenAI 格式）/ `https://api.deepseek.com/anthropic`（Anthropic 格式）、模型名 `deepseek-flash`：已按 2026-09-26 的官方文档核对（api-docs.deepseek.com）。出片前再看一次。")
    L.append("3. 余额不足报错码 402：已按官方文档“错误码”页核对。")
    L.append("4. OpenAI：`/v1/chat/completions` 继续支持、新项目推荐 `/v1/responses`；Responses 用 `input` 和 `instructions`，返回 `output` 条目，可用 `previous_response_id` 接续对话；示例模型名 `gpt-5.5`。依据 2026-09-26 的 OpenAI 迁移指南（developers.openai.com）。")
    L.append("5. Claude：`POST https://api.anthropic.com/v1/messages`，请求头 `x-api-key` + `anthropic-version: 2023-06-01`；`max_tokens` 必填、`system` 是单独字段；返回 `content` 内容块（text / tool_use）和 `usage`（input_tokens / output_tokens）；流式事件 message_start → content_block_start → content_block_delta → content_block_stop → message_delta → message_stop；示例模型名 `claude-opus-5`。依据 Anthropic 官方 API 参考。")
    L.append("6. DeepSeek 支持 Responses 和 Anthropic 格式：依据官方“模型 & 价格”页的功能表。")
    L.append("7. 代码卡上的请求和返回都是简化示意，右上角标“示意·已简化”，Key 一律打码。")

    (HERE / "台本_v3.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (HERE / "配音分段_v3.json").write_text(json.dumps(voice, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"total={fmt(total)} ({total:.1f}s) speech={speech:.1f}s segments={len(voice)} units={units}")


if __name__ == "__main__":
    main()
