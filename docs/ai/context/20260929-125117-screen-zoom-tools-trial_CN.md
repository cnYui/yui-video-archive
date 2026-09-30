# 录屏自动放大工具实测：OpenScreen vs Recordly（Windows 11）

- 时间：2026-09-29（UTC+9），中午。接 `20260929-115628-cs-grad-skills-series-plan-screen-zoom_CN.md`。
- 起因：新系列《AI震惊瘫坐时代计算机研究生必须掌握的技能》要录很多屏幕演示，用户要“镜头跟着鼠标、点哪放大哪”的开源工具。上一份记录查到两个候选，问“要不要下载来比一比”，用户答：“你来试试两个怎么样”。
- 结论：
  1. **OpenScreen（getopenscreen/openscreen v1.13.0）能走通全流程**：录窗口 → 放大 → 满屏导出；有完整命令行，能接进流水线。但命令行的 `--auto-zoom` 对命令行录出来的项目**静默失效（0 个放大）**，绕法见下。
  2. **Recordly（v1.4.0）录制和自动生成放大都正常，但 MP4、GIF 两种导出在这台机器上都失败**（`VideoEncoder is not defined` / `VideoDecoder is not defined`）。所以它的导出画质、速度、能否满屏都没测到。另外它录“窗口”时会把压在窗口上的东西（这次是任务栏）一起录进去。
  3. 目前倾向 **OpenScreen**。Recordly 要用户在自己电脑上正常启动再试一次导出，才能下结论。

## 环境

- Windows 11 家庭中文版，单个 1920×1080 显示器，Intel 核显（导出走 QSV 硬编）。
- Node 24、Python 3.12、ffmpeg 8.0、7-Zip（scoop）、Playwright 的 Chromium。

## 下载与安全核对

| | Recordly | OpenScreen |
|---|---|---|
| 文件 | `Recordly-windows-x64.exe` 185 MB | `Openscreen.Setup.1.13.0.exe` 231 MB |
| 来源 | `webadderall/Recordly` Releases v1.4.0，上传者 github-actions[bot] | `getopenscreen/openscreen` Releases v1.13.0，上传者是维护者个人账号（手动上传） |
| SHA-256 与 GitHub 登记值 | 一致 | 一致 |
| 数字签名 | **无**（NotSigned） | **无**（NotSigned） |
| Defender 主动扫描（安装包、解包后的整个目录） | 未发现威胁 | 未发现威胁 |

- OpenScreen 来历核实：原作者仓库 `siddharthvaddem/openscreen` 2026-06-17 归档，README 指向 `EtienneLescot/openscreen`，该地址现在重定向到 `getopenscreen/openscreen`；原作者在新仓库贡献者里（504 次提交）。所以不是冒名。
- **没有运行安装程序**：用 7z 解开 NSIS 安装包，再解 `$PLUGINSDIR/app-64.7z`，从临时目录直接运行，启动参数 `--user-data-dir` 指到临时目录。检查过：AppData、系统临时目录、注册表都没有留下东西。
- 两个都是“无签名 + 个人 / 小团队”的开源软件，用户自己装时要知道 Windows 会提示未知发布者。

## 测试方法

- 测试页 `zoomtest.html`（标题 `ZOOMTEST-LAB`）：深色页面，四角四个按钮、一块假终端、一块 13 px 小字表格、页面时钟。窗口 1792×1054。
- 驱动脚本用 `mouse_event` + `SendKeys` 在测试窗口里点击 5 次（左上、终端、右下、左下、右上）、终端里打两段字（`git status`、`claude`），约 27 秒。**三道保险**：点击前确认鼠标下面的顶层窗口就是测试窗口、且它是前台窗口；发现鼠标被人挪开超过 25 px 就中止；坐标限制在窗口客户区。
- 两个工具都用“录制指定窗口”，同一个页面、同一套动作。

## 出过的事（按发生顺序）

1. **第一次用 Edge 当测试窗口**：Edge 用 Windows 里登录的微软账号，把我这个临时配置目录**自动登录并开启了同步**（弹窗“我们现在正在你的所有设备上同步你的浏览数据”），弹窗抢了前台，驱动脚本的保险生效，第一轮录制中断，没有乱点。
   - 处理：只结束了命令行里带我临时配置目录的 9 个 Edge 进程（用户自己的 7 个没动）；之后改用 Playwright 自带的 Chromium（没有账号集成）。
   - **遗留**：临时目录里的 `edge-profile`（约 66 MB）删除被环境的安全钩子拦下（`rm -rf` 落在用户目录下、`Remove-Item` 被拦），我没有绕过。里面可能有同步下来的浏览数据，需要用户自己删。微软账号那边可能多了一条设备记录，以及一条 `file:///…/zoomtest.html` 的历史记录，影响很小，用户有兴趣可以去账号页面看。
   - 以后在这台机器上做浏览器自动化测试，不要用 Edge。
2. 我自己脚本里的转义错误（`\f` 变成换页符）让一次 GIF 导出测试白等了 5 分钟，没有副作用。

## OpenScreen 结果

- **录制**：`Openscreen.exe --user-data-dir=<临时> record --window ZOOMTEST-LAB --duration 26 --project x.openscreen --json`。
  - Windows 图形捕获（WGC）录**窗口内容**：1778×1048、H.264、60 fps、26 秒只有 1.4 MB（码率约 0.4 Mbps，静态页面，码率自适应）。
  - 同一个窗口下缘压在任务栏下面，**录出来是干净的，没有任务栏**。
  - `<视频>.cursor.json`：5 次 click 全部记录，位置准确（例：右下按钮记录 (0.867, 0.893)，目标 (87%, 90%)）；合成的点击（`mouse_event`）也被记录；打字**没有**事件。
- **命令行 `--auto-zoom` 返回 0 个放大**，日志：`Auto-zoom: added 0 region(s) from cursor telemetry`。
  - 原因（读源码 + 离线跑真实规划器验证）：自动放大入口 `buildAutoZoomSuggestionsForClips` 用 `clip.sourceEndSec ?? clip.sourceStartSec` 算片段长度；`record --project` 写出的 v2 项目迁移后，片段没有 `sourceEndSec`，长度成 0，整段被跳过，不报错。渲染、导出对话框、场景描述等其他地方都用 `resolveClipSourceEndSec(clip, asset)` 兜底（缺失时取素材时长），只有自动放大没兜底。
  - 离线验证：同一份点击数据，片段带 `sourceEndSec` 得 3 个放大，缺 `sourceEndSec` 得 0 个。
  - 没验证：图形界面里的“魔法棒”是否受同一问题影响（它走导入路径，很可能已补全时长）。
- **规划器行为**（`src/lib/ai-edition/timeline/zoom-suggestions.ts`）：
  - 只看点击，不看停留，也不看打字；没有点击的录制没有自动放大。
  - 放大档位 1.25× / 1.5× / 1.8×，按点击分布选；单点默认 1.8×。
  - 开头 2.5 秒保持全景，结尾前 1 秒回到全景；相隔 ≤3 秒的点击合并成一个镜头；镜头在首次点击前 0.5 秒已经到位，最后一次点击后再停 1.5 秒，最短保持 1.8 秒。
  - 两个放大之间至少 1.5 秒全景，否则能装进同一画面就合并，装不进就舍弃后一个（“别来回拉伸”）。本次 5 次点击得到 3 个放大，第 4 次（左下角）被舍弃。
- **绕法**（已验证）：用它自己的规划器源码（Node 里加载 TypeScript）从 `.cursor.json` 算出区间，写进 `.openscreen` 的 `editor.zoomRegions`（`focusMode: "auto"`），同时把画面改成满屏：`padding 0`、`borderRadius 0`、`shadowIntensity 0`、`wallpaper "#000000"`、`aspectRatio` 设成素材原始比例（1778×1048 → `889:524`）。代码见文末。
- **导出**：`export x.openscreen -o out.mp4 --quality source`，26 秒的片子 **12.5 秒**（约 125 帧/秒），输出 1778×1048、H.264、60 fps、4.6 MB，放大 + 满屏正确。
  - 默认外观是“壁纸 + 圆角 + 内边距”，`quality source` 导出成 1760×990（16:9 画布），要满屏必须改项目字段。
  - **命令行导出固定 H.264 60 fps，没有帧率、编码器选项**。你的成片是 30 fps，需要 ffmpeg 再转一次，或改用图形界面的导出对话框（有 H.265、24 / 30 fps）。
- **画质**：1.8× 时 13 px 的小字表格读起来清楚；光标是重画的手型，点击圈和按钮变绿都保留。
- 其他：命令行还有 `captions`（本机 Whisper 字幕）、`--audio`（混入配音）、`pack`、`info`、`sources`；官方文档写明命令行和项目格式“可能在版本间有破坏性改动”。

## Recordly 结果

- **界面**：录制条是中文界面，选源 / 麦克风 / 摄像头 / 倒计时 / 录制。倒计时默认 3 秒，可设“无延迟”。选源里能选窗口。
- **录制**：WGC，1778×1046、H.264 Constrained Baseline、60 fps，**固定码率 24.3 Mbps**，31 秒 = 约 91 MB（约 180 MB/分钟）。5 次点击全部记录，位置准确。
- **录窗口会录进遮挡物**：同一个窗口、同一位置，原始视频底部出现了任务栏（开始按钮、应用图标、托盘、时钟），OpenScreen 的没有。推测它是按窗口所在的屏幕区域裁剪。用户如果录窗口，别的窗口 / 通知弹窗压上来也会进画面，录完整屏则没区别。
- **自动放大**：录完直接在编辑器时间轴生成 5 个（每次点击一个，“1.5×”，聚焦模式 “Auto”），不用手点。
  - 规划器 `buildInteractionZoomSuggestions`：点击相隔 ≤2.5 秒合并成一簇，放大区间 = 首次点击前 0.5 秒 → 最后一次点击后 0.5 秒（单次点击约 1 秒），已有区间重叠就跳过。没有“别来回拉伸”的保护，也没有开头 / 结尾保持全景。
  - 只使用真实点击事件（停留一类的启发式判断在这个函数里被忽略）。
  - 编辑器预览播放时能看到镜头拉近到点击位置再回到全景，幅度比 OpenScreen 小。
- **编辑器**：内边距 / 阴影 / 圆角是拖动条（键盘无效，要用指针拖）；画面比例只有 16:9、9:16、1:1、4:3、4:5、16:10、10:16，**没有“原始比例”**（录全屏 1920×1080 时 16:9 恰好等于原始）。
- **导出面板**：MP4 / GIF；分辨率 低 / 中 / 高 / 原始；编码 Fast / Balanced / Quality；帧率 24 / **30（默认）** / 60。导出后弹**原生“另存为”**，默认路径是“下载”文件夹。
- **导出失败**（各复现，不是偶发）：
  - MP4：`Export failed: VideoEncoder is not defined`；GIF：`VideoDecoder is not defined`。
  - 编辑器渲染进程里 `typeof VideoEncoder / VideoDecoder / AudioEncoder` 都是 `undefined`，`VideoFrame` 有；页面是安全上下文。
  - **同一台机器上的对照**：Playwright 的 Chromium 145 有；OpenScreen 的 Electron 41.2.1 有；Recordly 的 Electron 43.1.0 没有。
  - Recordly 的启动开关里没有关掉 WebCodecs 的项（都是 Electron 默认值加 `use-angle=d3d11`）；编辑器窗口用了 `webSecurity: false`，不确定有没有关系。
  - **根因没查清**。也没排除我的启动方式（`--remote-debugging-port`、自定义 `--user-data-dir`）的影响，理论上无关。GitHub issues 里搜不到相关报告（搜索可能本身无效）。
  - 所以 Recordly 导出画质、速度、能否满屏都没测。

## 对比（这次实测到的）

| | OpenScreen v1.13.0 | Recordly v1.4.0 |
|---|---|---|
| 许可 | MIT | AGPL-3.0 |
| 录窗口 | 只录窗口内容，干净 | 录窗口所在区域，遮挡物会进画面 |
| 录制码率 | 自适应（这次 0.4 Mbps） | 固定 24 Mbps（180 MB/分钟） |
| 点击记录 | 准确 | 准确 |
| 自动放大 | 命令行有 bug（0 个），界面未验证；规划器有节奏保护 | 录完自动生成，每次点击一个 1.5× |
| 命令行 | 有，可脚本化 | 没有 |
| 导出 | 命令行 60 fps 固定；12.5 秒 / 26 秒片；满屏可行 | 本机导出失败 |
| 导出帧率 | 界面 24 / 30 / 60（命令行固定 60） | 24 / 30（默认）/ 60 |
| 画面比例 | 支持素材原始比例 | 只有预设，没有原始 |

## 对系列的建议

- 先用 **OpenScreen**。录窗口干净、命令行能接进现有 Python / HTML 渲染流程、许可宽松。要 30 fps 就用 ffmpeg 转。
- 终端段落（Claude Code / Codex 主要靠打字，鼠标不动）两个工具的自动放大都不会触发：在项目里手动写 `zoomRegions`（OpenScreen 支持），或在编辑器里手动加。
- 录制分辨率：本次 1778 px 宽放大 1.8× 仍然清楚；1920×1080 同理。
- 第 2 集录 API key：**OpenScreen 有「模糊」标注**（隐私遮罩，平滑 / 马赛克，矩形 / 椭圆；按 `A` 添加，把区间拉满出现 key 的所有时间段，再逐帧拖动检查）。Recordly 有没有没查。
  - 更正：这里原来写的是“两个工具都没有打码功能”，是只看了 README 得出的，不对；后来读 OpenScreen 官方文档才发现有。
  - 仍建议用临时 key，录完就在控制台删除。
- Recordly 备选：要用户先在自己电脑上**正常启动**，试一次 MP4 导出，成功再考虑。

## 待用户决定

- 手动删除 `edge-profile`（在临时目录里，见上面的“遗留”）。
- 是否在自己电脑上装 Recordly 试导出。
- 是否把这套测试脚本和“规划器算放大区间”整理进仓库 / 做成技能（需要先定新系列放在哪个目录）。
- 临时目录约 2.7 GB（两个安装包 + 解包目录各约 1 GB，两份源码克隆约 300 MB），可整个删掉。

## 附：绕开命令行 `--auto-zoom` 的脚本

在 OpenScreen 源码的 `src` 目录上加载 TypeScript（Node 24 自带类型剥离，只需要解析 `@/` 别名和省略的 `.ts` 扩展名）。

`hooks.mjs`：

```js
import { pathToFileURL } from 'node:url';
import path from 'node:path';
const ROOT = process.env.OS_SRC;   // .../openscreen/src
export async function resolve(specifier, context, nextResolve) {
  let s = specifier;
  if (s.startsWith('@/')) s = pathToFileURL(path.join(ROOT, s.slice(2))).href;
  let lastErr;
  for (const ext of ['', '.ts', '.tsx', '/index.ts']) {
    try { return await nextResolve(s + ext, context); } catch (e) { lastErr = e; }
  }
  throw lastErr;
}
```

`register.mjs`：

```js
import { register } from 'node:module';
register('./hooks.mjs', import.meta.url);
```

`mkproject.mjs`（用法 `OS_SRC=<src> node --no-warnings --import ./register.mjs mkproject.mjs in.openscreen out.openscreen`）：

```js
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

const SRC = process.env.OS_SRC;
const [inPath, outPath] = process.argv.slice(2);
const project = JSON.parse(fs.readFileSync(inPath, 'utf8'));
const video = project.media.screenVideoPath;
const cursor = JSON.parse(fs.readFileSync(video + '.cursor.json', 'utf8')).samples;
const probe = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0',
  '-show_entries', 'stream=width,height:format=duration', '-of', 'json', video]).toString());
const W = probe.streams[0].width, H = probe.streams[0].height;
const totalMs = Math.round(Number(probe.format.duration) * 1000);
const gcd = (a, b) => (b ? gcd(b, a % b) : a);

const mod = await import(pathToFileURL(path.join(SRC, 'lib/ai-edition/timeline/zoom-suggestions.ts')).href);
const zoomRegions = mod.buildAutoZoomSuggestions({
  cursorTelemetry: cursor, totalMs, existingRegions: [],
  wideUntilMs: 2500, wideFromMs: totalMs - 1000, ignoreClicksFromMs: totalMs - 1000,
}).map((s, i) => ({ id: `zoom_auto_${i + 1}`, startMs: Math.round(s.span.start), endMs: Math.round(s.span.end),
  depth: s.depth, focus: { cx: s.focus.cx, cy: s.focus.cy }, focusMode: 'auto', source: 'auto' }));

project.editor = { ...project.editor, zoomRegions,
  padding: 0, borderRadius: 0, shadowIntensity: 0, wallpaper: '#000000', showBlur: false, depthOfField: false,
  aspectRatio: `${W / gcd(W, H)}:${H / gcd(W, H)}` };
fs.writeFileSync(outPath, JSON.stringify(project, null, 2));
```

手动放大区间（终端打字段落）：往 `editor.zoomRegions` 里再加 `{ id, startMs, endMs, depth: 3, focus: { cx, cy }, focusMode: "manual", source: "manual" }`，`depth` 1–6 = 1.25× / 1.5× / 1.8× / 2.2× / 3.5× / 5×。
