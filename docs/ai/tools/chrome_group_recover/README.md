# chrome_group_recover：Claude in Chrome 的标签组丢了，怎么把自己的页面接回来（2026-10-05）

**症状**：`tabs_context_mcp` 报 `No tab group exists for this session`；`computer` / `javascript_tool` 报 `Tab N is not in Claude's tab group`；偶尔先报 `Claude in Chrome is not connected`（等几秒重试，常是暂时的）。
**原因**：Chrome 扩展重连（几个会话同时用扩展时很频繁，一天里我丢了四次，别的会话也同时丢）；丢的时候 Chrome 里的标签组被直接解散，标签变成没有组的散标签，页面里已经上传的视频 / 填了一半的表都还在——**所以不能重开页面，要把这些标签接回来**。

用 Windows PowerShell 5.1 跑：`powershell -NoProfile -ExecutionPolicy Bypass -File <脚本> [参数]`。脚本都靠 UI Automation 读标签位置、鼠标拖拽（鼠标只有一个：几个会话同时拖会互相打架，先在 `SendMessage` 里约好）。

## 做法（按顺序）

1. **看标签现在在哪**：`docs\ai\tools\chrome_tabs.ps1`（别的会话写的，列所有窗口 / 标签，带“属于‘群组名’群组”）；我的散标签没有“属于”。
2. **先给自己一个独立窗口**（强烈建议：别的会话的新组也会落在“最近用的窗口”里，共用窗口里同一时刻只有一个活动标签，别人选标签我的页就 `hidden`）：
   - `make_window.ps1 -Win <旧窗口句柄>`：把我的抖音散标签（脚本里按名字写死，要改就改 `MyTab $Win '…'`）拖出去成新窗口，放右半屏；
   - `join_window.ps1 -From <旧窗口> -To <新窗口> -Key <标签名关键字>`：把其余散标签逐个拖进新窗口（对每个标签跑一次）。
3. `raise_mine.ps1 -Window <新窗口句柄>` 前置新窗口，再 **`tabs_context_mcp` 带 `createIfEmpty: true`**：新组会建在前台那个窗口里（里面一个空白页）。
4. `join_group.ps1 -Window <新窗口句柄> -NameLike <标签名关键字>`：把每个散标签拖进那个新组（终点是组里的标签；起点 / 终点最上面的窗口不是我的就不拖）。
5. 再 `tabs_context_mcp`：标签 ID 不变（582105921… 这些），页面状态原样。
6. 要打字 / 截图时：`select_tab.ps1 -Key <标签名关键字> -Window <我的窗口句柄>` 选中该标签（别用共用窗口的），JS 确认 `document.visibilityState === 'visible'`。

## 踩过的坑

- **别的会话的流程会把我的窗口最小化**（`chrome_win.ps1 -Action back` 之类）：窗口最小化后里面的标签 `hidden`，`screenshot` 30 秒超时（“renderer may be frozen”）——先 `raise_mine.ps1`（ShowWindow 9 + Alt + SetForegroundWindow）。
- **PowerShell 变量不分大小写**：`recover_group.ps1` 里 `$mine` 和参数 `$Mine` 撞名，目的地算成 (0,0)，整组被拖成了新窗口（结果也能用：`recover_group2.ps1` 就是接着把那个窗口里的组拖回主窗口，已修）。
- 拖拽前一定用 `Top-WindowAt` 检查起点 / 终点最上面的窗口；Claude 桌面端窗口常盖在 Chrome 上面，必须先前置 Chrome。
- 拖标签进别的窗口时，终点用“组里第一个标签靠右 70 %”的位置；同一窗口拖进组也一样。偶尔一次拖成了“撕出新窗口”（B 站标签那次）——再列一遍标签，接着拖。
- 用 `createIfEmpty` 前要先前置自己的窗口，否则新组会落在别的会话的窗口里（这次第一次就落进了共用窗口，得再把组拖出来）。
- `browser_batch`（插件里的批量工具）是 deferred 工具，要先 `ToolSearch select:mcp__claude-in-chrome__browser_batch` 才能用；截图坐标是“截图 frame”坐标（比 CSS 像素小，`vw 1719` 的页面 frame 是 1568 宽），点击要按 frame 坐标，不是 `getBoundingClientRect` 的值。
