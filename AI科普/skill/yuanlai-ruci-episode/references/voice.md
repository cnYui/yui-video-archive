# 配音（2026-09-28 起用户自己录；AI 配音只在用户点名要时用）

只在台本定稿（✋）之后开始。用户 2026-09-28：“原LAI如此配音之后需要我来配音，ai配音用来做每日日报”。所以《原LAI如此》默认由**用户自己录旁白**（`episode.json` 的 `"voice_source": "user"`，`new_episode.py` 默认写好）：技能出录音稿，用户录好给文件，脚本导入、切句（能跳过重读的句子）、对齐字幕。Fish Audio 的 AI 配音（下面「AI 配音」几节）现在只用于《AI每日日报》；《原LAI如此》只有用户点名要 AI 配音时才用（`voice_source` 改成 `"tts"`，或 `new_episode.py --voice tts`）。`voice_source` 没写 = AI 配音（第 1–4 期、《AI每日日报》，行为和以前完全一样）。

## 自己录音（默认）

**录音前先把别的做好**（用户 2026-09-28：“其他的内容你都要帮我写好，我配音完成后，你再做后续的事情”）：台本定稿后先出录音稿给用户；等录音时，`build_timeline.py` 在没有录音的情况下按字数估每句时长（已有功能），照它写 scenes.js、抽帧自查、做封面和投稿信息草稿。录音到了、切好句，再重跑 build_timeline → mix_audio → assemble（scenes.js 按段号和短语挂时间，不用改）。
**开场自称和署名**（用户 2026-09-28：“开场还是说我是鲸鱼娘，配音署名写UE”；当晚又定“之后统一换成悠一”）：台本开场照旧是“大家好，我是{讲解员}”（鲸鱼娘那期就是“大家好，我是鲸鱼娘”，用户用本人的声音念）；片尾清单的「配音」一栏和 B 站简介写 **悠一**（以前写 UE），不写 Fish Audio / AI 合成。

流程：台本定稿 → `chunk_voice.py --whole` → `record_script.py`（录音稿）→ 用户录音 → `import_voice.py` → `select_takes.py` → `segment_audio.py` → 试听 / 补录。

1. **整期一批**：`python scripts/chunk_voice.py <期目录> --whole` → `配音/chunks.json`（一批 C01，全部段号）。它最后打印的音色和“下一步：tts_api.py”是给 AI 配音的，自己录音时不用管。还没有 chunks.json 时 `import_voice.py` 会自动跑这一步。
2. **录音稿**：`python scripts/record_script.py <期目录>` → `配音/录音稿.md`（开头是怎么录和「读法」表，再按章节列每一句：段号 + 字幕原文；英文、数字的读法在每章第一次出现时提示一次，例如 Jev → 杰夫、0.72 → 零点七二；TTS 的拆字写法如 “A P I” 不会出现）和 `配音/录音稿.txt`（提词器用：一句一行，章节之间空一行，没有段号）。把录音稿发给用户（SendUserFile），说一下大约几分钟。录音稿里写好的要求：
   - 手机或麦克风都行，wav / m4a / mp3 都可以；找安静的房间。
   - 按顺序读，句与句之间停 1 秒左右。
   - 读错了不用停：停一下，把这一句从头再读一遍（脚本保留最后读完整的那一遍）。
   - 可以整期一个文件，也可以按章节分几个文件；段号不用读；录好把文件路径发过来。
3. **导入**：`python scripts/import_voice.py <期目录> <文件1> [文件2 …]`（按给的顺序拼接，文件之间 1 秒静音）→ `配音/raw/C01_vN.wav`（44.1 kHz 单声道 16 bit；N 接着往后编，不覆盖，AI 版的 `C01_v1.mp3` 也占一个号）+ `C01_vN.json`（每个原文件在拼接后的起点、时长、响度和增益，报告据此换算回原文件里的时间）。
   - 处理很轻：70 Hz 高通（去低频隆隆声、直流）；每个文件用一个线性增益调到 -20 LUFS，分几次录的文件、补录和主录音一样响。mix_audio.py 只按整条人声的峰值缩放、再给成片做 -16 LUFS 响度归一，不会把文件之间拉平，所以这里不是重复处理。增益以不超过 -1 dBFS 为限；只有个别特别响的瞬间（喷麦、碰到话筒）让音量差 3 dB 以上调不上去时，才自动把那几个峰压到 -3 dBFS（`--limit auto`；`on` 总是压，`off` 不压）。有风扇 / 街上的噪音加 `--denoise`（ffmpeg afftdn，12 dB）；`--no-level` 不调音量。
   - 立体声里一个声道没声音就只用有声音的那个；手机录的视频也能直接导入（只取声音）。
   - 会提醒：爆音（削波）、太小声、总时长比台本估计短很多（少了文件？）、episode.json 没有 `"voice_source": "user"`（那样后面两步要加 `--user-voice`）。
4. **选版本、整期打分**：`python scripts/select_takes.py <期目录>`：只看导入的 `.wav`（AI 的 `.mp3` 不看），**用最新导入的一版**（每次导入都是用户有意重录；要用旧版加 `--take C01_v1.wav`）。和**字幕原文**比对（人读的是字幕，不是 TTS 写法）：分数 = 台本的字在识别结果里找到的比例（重读不扣分），另报多出来的字数（重读 / 噪音）。带词级时间的识别结果缓存在 `配音/raw/asr_words.json`，下一步直接用（small 模型在 CPU 上，识别时间约为录音时长的 1/3）。
5. **切句、对齐**：`python scripts/segment_audio.py <期目录>` → 和 AI 配音一样的产物：`配音/segments/<段号>.wav`、`制作/voice/durations.json`、`制作/voice/alignment.json`、`配音/segments/report.txt`（另有 report.json）。做法（`scripts/uservoice.py`）：
   - 整期字幕原文和识别出的字做全局对齐：重读的句子、读了一半停下的半句、咳嗽 / 噪音都会被跳过；同一句完整读了两遍，用后读的那一遍。
   - 每句单独切：切点在这句前后的停顿里，不切进相邻的句子，跳过的重读不会留在任何一句里。识别常把停顿旁边的字的时间标歪（整个挪进停顿里），切点按声音修正。
   - 识别有时把“停下、整句重读”只写成一遍：一句里有 0.6 s 以上的停顿时，把停顿后面单独再识别一次，是从句首开始的完整一遍就只用它。
   - 字幕每行的起止时间直接按字幕原文对齐（比 AI 配音那条按 TTS 文本换算的更准）。
6. **看报告、试听、补录 ✋**：report.txt 列出
   - 每一句的匹配度（和字幕原文、TTS 读法两种写法比，取高的）；**< 0.8 的是「可能读错 / 漏读」**。整句没找到的先放一小段停顿占位（字幕照常显示），一定要补录；
   - 按声音修正过切点的句子（句中重读、识别时间标歪、旁边有噪音）；
   - 句子里多出来的、重复这句话的字（句中停下重读？）；
   - **跳过的声音**（≥ 0.8 s，或识别出 4 个字以上：重读、读错的半句、噪音），带在录音里的时间和在用户原文件里的时间，确认里面没有要用的句子。

   把列出来的句子发给用户听（`配音/segments/<段号>.wav`；想整期听就用 ffmpeg 按顺序拼一个 `配音/配音试听_整期.wav`）。要重录某一句：用户单独录这一句（录错了照样停一下整句重读）→ `python scripts/import_voice.py <期目录> --segment S03-12 <文件>` → `配音/raw/pickups/S03-12_vN.wav`（同样的处理）→ 再跑 `segment_audio.py`：这一句用最新的补录，其余不变。
   - 整期重录：再 `import_voice.py`（新的 C01_vN）→ `select_takes.py` → `segment_audio.py`。
   - 台本改了字：`build_script.py` → `chunk_voice.py --whole --force` → `record_script.py` → 改了的句子补录（或整期重录）→ `segment_audio.py`。只改 TTS 文本（字幕原文没变）时录音不用动。
7. 之后 `build_timeline.py` → `mix_audio.py` → `assemble.py` 照常。

## AI 配音（Fish Audio API）

**《原LAI如此》不再用；用户点名要 AI 配音时才用（AI 配音现在只用于《AI每日日报》）。** 下面「API key」「费用」「步骤」「备用：网页版」「请用户试听」「注意」都属于 AI 配音，保留备查。用 AI 配音的期：`episode.json` 的 `voice_source` 写 `"tts"` 或不写，`select_takes.py` / `segment_audio.py` 就按原来的做法处理。

2026-09-27 起用户要求：**配音用 Fish Audio API 生成对应角色的音色，不再用浏览器插件操作网页版**；整期一次请求生成，免得分批之间音色不一致。**API 余额不足（402）时**（用户 2026-09-28 定）：改用 Claude in Chrome 插件操作 Fish Audio 网页版，用户已开 Plus，整期一次生成，见下面「备用：网页版」。第 1、2 期是网页版分批做的（免费账号），做法记在 lessons.md「网页版配音」。

用哪个音色看 `episode.json` 的 `presenter`（没有 `presenter` 的期按山田凉）。`tts_api.py` 自动取 `voice_id`；老目录没有 `voice_id` 时，从 `voice_app` / `voice_page` 网址里取 32 位 id。

| 讲解员（预设 id） | 音色 | 音色 id（API 的 reference_id） | 音色页（试听示例） |
|---|---|---|---|
| 山田凉（ryo） | 山田凉 | `82a7576ebd634931b2926b64fc8e23ac` | https://fish.audio/zh-CN/m/82a7576ebd634931b2926b64fc8e23ac/ |
| 鲸鱼娘（whale；DeepSeek 拟人，素材包叫大肥鱼） | 苏晓晓 | `e7219cb8cfab46bebba2ee570932b0a6` | https://fish.audio/zh-CN/m/e7219cb8cfab46bebba2ee570932b0a6/ |

新增讲解员：在 `scripts/epcommon.py` 的 `PRESENTERS` 加一项（写上 `voice_id`），这张表同步加一行。

### API key

- key 在 Windows **用户环境变量 `FISH_API_KEY`** 里，由用户自己设（「编辑账户的环境变量」，`rundll32 sysdm.cpl,EditEnvironmentVariables` → 用户变量 → 新建）。`tts_api.py` 先读当前进程的环境变量，没有再读注册表里的用户变量，刚设好不用重启。
- 不打印、不回显、不写进任何文件（包括日志、台本、docs），不在对话里复述；也不要把 key 输入到任何网页里。检查有没有设好只看“有 / 长度 / 是否以 `sk-fish-` 开头”。
- 没有 key 就停下，请用户按上面的方法设置，不要让用户把 key 发在对话里。

### 费用

- 按请求文本的 UTF-8 字节计费：s1 每百万字节 15 美元（Fish Audio 定价页，2026-09-27）。一期 6 分钟约 6000 字节，**一次约 0.09 美元**。`--dry-run` 先打印字节数和估算；每次生成都追加到 `配音/raw/api_usage.jsonl`。
- 余额不足（402）：不替用户充值，改用网页版（下面「备用：网页版」，用用户 Plus 账号的额度）；不换别的 TTS。
- 模型只用 s1（用户 2026-09-28 再次强调：更便宜）；`tts_api.py` 的 `--model` 只接受 s1，网页版也要在模型下拉里选 S1。

### 步骤

1. **整期一批**：`python scripts/chunk_voice.py <期目录> --whole` → `配音/chunks.json` 只有一批 C01（scene `ALL`，全部段号，文本 = 各段 `tts_text` 按顺序拼接）。
2. **生成**：`python scripts/tts_api.py <期目录> --dry-run` 看字节和费用 → 去掉 `--dry-run` 正式生成 → `配音/raw/C01_v1.mp3`。
   - 模型 s1（到目前为止每期都用它），温度 0.9、top_p 0.9、语速 1.0，和网页版默认一致。
   - 默认每批 1 个版本（用户说过“你就用第一个就行”）；只给还没有“和当前文字一致的版本”的批次生成。台本改过后再跑，文字对不上的旧版本会挪到 `配音/raw/_旧稿_<时间>/`（不删）。
   - 401（key 不对）、403 立即停下告诉用户；402（余额不足）脚本也会停，然后改走下面「备用：网页版」；429、5xx、超时自动重试两次。
3. **打分选版本**：`python scripts/select_takes.py <期目录>`：faster-whisper（small、int8、CPU）转写，和台本比对打分（difflib）→ `配音/selection.json`。整期一批时分数一般在 0.9 以上；低于 0.9 就看转写：常见原因是专有名词被识别成别的字（不一定是念错）、数字写法不同（百分之十五点六 → 15.6%）。真念错、漏句、重复句：`python scripts/tts_api.py <期目录> --only C01` 再生成一个版本（C01_v2），重跑 `select_takes.py` 按分数挑；同一句总念错就改 `script_data.py` 里这一段的 TTS 文本（字幕原文不用动），重跑 `build_script.py`、`chunk_voice.py --whole --force`、`tts_api.py`。
4. **切句、对齐**：`python scripts/segment_audio.py <期目录>` → `配音/segments/<段号>.wav`、`制作/voice/durations.json`、`制作/voice/alignment.json`（字幕每行的起止时间）、`配音/segments/report.txt`。切点在两句之间最安静的 10 ms 处。

### 备用：网页版（API 余额不足时）

用户 2026-09-28：“api key没钱的话，就还是使用浏览器插件来生成，我已经重置了plus，可以使用更多的额度和长度，你可以一次生成完整的音频”。

1. 插件新开标签页打开本期讲解员的 `presenter.voice_app`（生成器，已带音色 id），确认右上是用户已登录的账号、模型下拉选 **S1**。
2. 把 `配音/chunks.json` 里 C01 的整期文本（`--whole` 的拼接结果）一次贴进编辑框；Plus 单次长度够就整期一次生成（超出页面上限再按场景分成尽量少的几批，并告诉用户分批会有音色差）。编辑框里按 Ctrl+Enter 生成（出现播放器后按钮会移位，按坐标点会落空）。
3. 用插件 `read_network_requests`（过滤 `api.fish.audio/task/`）拿任务编号，音频在 `https://platform.r2.fish.audio/tasks/<日期>/<编号>.mp3`；用 `scripts/fetch_check.py --urls 配音/urls.txt` 下载到 `配音/raw/C01_v1.mp3`（名字和 API 版一致，后面 select_takes / segment_audio 照常）。不用点浏览器的下载按钮（Chrome 会拦连续下载）。
4. 不改账号设置、不点升级 / 充值 / 购买；页面弹出付费或额度不足就停下告诉用户。在 `配音/raw/` 里记一行 `web_usage.txt`（日期、字数、任务编号），代替 api_usage.jsonl。

### 请用户试听 ✋

- 把选中的整期音频（`配音/raw/C01_vN.mp3`，可复制成 `配音/配音试听_整期.mp3`）发给用户（SendUserFile），说明分数，把识别结果和台本对不上的地方、英文专有名词的段落列出来重点听。
- 用户说哪句不满意：先试 `--only C01` 重生成一个整期版本；只有一两句的问题也可以改那几段的 TTS 文本后整期重生成（一次约 0.09 美元，比分批拼接音色更统一）。之后 `select_takes.py` → `segment_audio.py` → 时间轴、混音、合成照常重跑。

### 注意

- 音色页上的示例音频可能是别的模型生成的，以 s1 实际生成的为准，请用户试听时说明这一点。
- 需要多个角色对话的片子（例如番外）：一个请求只能用一个音色，要按说话人分批（每个角色一批或按轮次分批），`chunk_voice.py` 目前只支持整期一个讲解员；做番外时再扩展。
- 配音是 AI 合成，投稿时提醒用户勾选创作声明；简介里也写“配音为 AI 合成”（用户自己录音的期不写这句；创作声明怎么勾按实际情况问用户）。
