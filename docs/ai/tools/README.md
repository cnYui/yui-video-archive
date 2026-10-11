# docs/ai/tools：多个会话共用的小工具

## chrome_win.ps1：把被最小化 / 被盖住的 Chrome 窗口前置、用完放回去（2026-10-05）
Chrome 窗口里各会话的标签（Chrome 插件的标签组）在窗口被最小化时都是后台标签（`document.visibilityState === 'hidden'`、`document.hasFocus() === false`）：`computer type` 会丢字、Fish 点“生成”没反应、截图超时。

```powershell
# 1) 找我的窗口句柄（标题带当前标签的标题，Chrome_WidgetWin_1 类；Iconic=True 就是最小化了）
#    例：EnumWindows + GetClassName == 'Chrome_WidgetWin_1'（见 chrome_win.ps1 同目录的做法，或直接用下面的参数试）
# 2) 前置：恢复（SW_RESTORE）+ 按一下 Alt 解除前置限制 + SetForegroundWindow
powershell -File D:\大疆\docs\ai\tools\chrome_win.ps1 -Action front -Hwnd <我的窗口句柄>
# 3) 在插件里用 javascript_tool 确认 document.visibilityState === 'visible' 且 document.hasFocus() 再操作
# 4) 用完：最小化 + 把焦点还给 Claude 桌面端窗口（-Back 是它的句柄）
powershell -File D:\大疆\docs\ai\tools\chrome_win.ps1 -Action back -Hwnd <我的窗口句柄> -Back <Claude 窗口句柄>
```
- 用户自己的 Chrome 窗口（标题是他正在看的页面）别碰；我这个标签组的窗口通常是最后一个 `故事工作室 | Fish Audio … - Google Chrome` 之类的。
- 关掉我自己的最后一个标签，标签组和窗口会一起消失，也就不用再最小化。
- 另一种做法（别的会话用过）：UI Automation 选中自己组里的标签 `SelectionItemPattern.Select()`，比按 Ctrl+9 稳。

## chrome_tabs.ps1 / chrome_find_uia.ps1 / win_shot.ps1：共用 Chrome 窗口里找标签、选标签、前置、截窗口（2026-10-05，Muse 并行发布时写的）
用 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File …` 跑（要 Windows PowerShell 5.1，UIA 在里面最稳）。
```powershell
# 列出所有 Chrome 窗口和各窗口里的标签（[*] = 该窗口当前选中的标签；标签名里带“属于‘<群组名>’群组”）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\大疆\docs\ai\tools\chrome_tabs.ps1
# 选中自己组里的某个标签：-Select 群组名里的关键词 -Also 平台名（别用会变的页面标题；两个关键词都要出现在名字里）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\大疆\docs\ai\tools\chrome_tabs.ps1 -Select "开源信息短视频制作" -Also "小红书"
# 把窗口前置（Alt 技巧 + SetForegroundWindow），hwnd 从第一条命令的输出里取；要打字的话和选标签放在同一条命令里，别分开
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\大疆\docs\ai\tools\chrome_tabs.ps1 -Front <hwnd>
# 全树搜索某个名字出现在哪个 Chrome 窗口里（窗口太窄时列标签看不到靠后的标签组，用它确认标签还在）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\大疆\docs\ai\tools\chrome_find_uia.ps1 -Needle "开源信息"
# 截某个窗口所在屏幕区域存成 PNG（窗口要在最上面；-TopOnly 140 只截顶部标签条）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\大疆\docs\ai\tools\win_shot.ps1 -Hwnd <hwnd> -Out <png> [-TopOnly 140]
```
- 几个会话共用一个窗口时，同一时刻只有一个活动标签：别人选自己的标签我的页就变 `hidden`（打字丢字、小红书候选 / “发布”按钮不渲染）。要打字：选标签 + 前置 + 立刻 JS focus → `computer type`；和别的会话约“前台时段”。不打字的步骤用 JS / `find` + `file_upload`。见记忆 `chrome-shared-window-uia-foreground`。
- Claude 桌面端会在工具调用之间抢回前台：`SendKeys` 要在前置的同一条命令里发，否则按键落到 Claude 窗口。

## overlay_check.py：叠加层抽查（2026-10-05）
把成片里每个叠加层（数字框 / 说明条 / 高亮框 / 页面录屏 / 来源角标）出现中间的那一帧抽出来拼联系表，逐张看有没有盖住素材自带的名牌、角标、标题。起止时刻从页面里的 `OV` 取（和渲染同一套时间），画面从成片抽。横版 / 竖屏引擎都行。
```bash
python D:\大疆\docs\ai\tools\overlay_check.py "<引擎目录 制作\00_整片>" [--video 成片.mp4] [--skip-credit] [--only-from 秒]
```
- 默认视频 = `<引擎目录>\整片_v1.mp4`，联系表在 `<引擎目录>\stills_overlay\_sheet_N.png`（横版 3×3 一张、竖屏 6×2 一张，标签写时刻和叠加层编号）。
- 出整片前后各跑一遍：只看每场景 3 张静帧会漏掉叠加层出现的那几秒（《不再Review》长视频第一次渲完就是这样漏了 288 s 的数字框盖住来源角标、访谈左下角“Matt”名牌被说明条盖半）。见记忆 `overlay-check-every-frame-and-avoid-source-labels`。

## chrome_group_recover/：Claude in Chrome 标签组丢了，把自己的页面接回来（2026-10-05）
扩展重连时 Chrome 里的标签组会被解散（几个会话同时丢），`tabs_context_mcp` 报 No tab group exists；页面里上传好的视频 / 填了一半的表都还在，要把散标签接回新组而不是重开。脚本（拖出独立窗口、拖标签进组、前置、选标签）和步骤见该目录的 `README.md`。

## published_cleanup/：已发布作品的本地视频移进回收站（2026-10-05）
用户：「之前已经发布的视频统一清除本地的视频，素材不要删除」。`published_works.json` 登记已发布的作品（只有 `投稿信息.json` 里全平台都发了的才加）、`build_manifest.py` 出清单（只读，跳过 `素材` / 出镜 `proxy` / 共用片头片尾 / 测试目录）、`recycle.ps1` 逐个 `SendToRecycleBin` 并按回收站实体文件核对。第一次清了 35 个作品、1021 个文件、10.34 GiB。**回收站有容量上限（D 盘 24.6 GB），装不下会静默永久清掉；移进回收站不腾空间，要用户清空**。规则、踩的坑、还原办法见该目录 `README.md`，记录 `docs/ai/context/20261005-213800-published-videos-local-cleanup_CN.md`。

## chrome_topmost.ps1 / untopmost_later.ps1：临时把 Chrome 窗口设成“总在最前”（2026-10-06，GPU 长文短视频发布时写的）
Claude 桌面端（最大化）会在工具调用之间抢回前台，把共用 Chrome 窗口完全盖住 → 我的标签 `visibilityState: hidden`、截图 30 s 超时、小红书发布按钮 / 候选列表不渲染。
```powershell
# 置顶并摆到屏幕内（同时起 untopmost_later.ps1：15 分钟后自动取消置顶的保险）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\大疆\docs\ai\tools\chrome_topmost.ps1 -Mode on -Hwnd <Chrome 窗口句柄> -X 300 -Y 10 -Wd 1500 -Ht 1020
# 再选自己的标签并 JS 确认 visible
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\大疆\docs\ai\tools\chrome_tabs.ps1 -Select "<标签名里的关键词>" -Also "<群组名>"
# 用完 / 等用户回复前必须取消（置顶的 Chrome 会盖住聊天窗口，用户回不了话）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\大疆\docs\ai\tools\chrome_topmost.ps1 -Mode off -Hwnd <Chrome 窗口句柄>
```
- 别在脚本里用 `$H` 和 `$h` 同时当变量（PowerShell 不分大小写，高度会变成窗口句柄）。
- `chrome_group_recover/drag_group_out.ps1`：把整组标签（按组名里的关键词找 chip）拖成独立窗口；拖到屏幕左侧才成（拖到本窗口内部没分出新窗口）；拖完扩展会丢组（`No tab group exists`），**别在发布中途用**，要独立窗口就在开页之前做，或者直接用上面的置顶。
