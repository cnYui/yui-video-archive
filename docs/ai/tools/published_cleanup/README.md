# published_cleanup：已发布作品的本地视频，移进回收站

用户 2026-10-05：「之前已经发布的视频统一清除本地的视频，素材不要删除」。做法：只清**已发布作品**的视频，移进回收站（不永久删，清空由用户自己来），`素材` 一律不碰。第一次的结果和清单见 `docs/ai/context/20261005-213800-published-videos-local-cleanup_CN.md`。

## 用法

```powershell
# 1) 往 published_works.json 的 works 里加新发布的作品（先看它的 投稿信息.json，规则见下）
# 2) 出清单（只读；登记的作品里有 approval.status = pending 的会直接报错退出）
python D:\大疆\docs\ai\tools\published_cleanup\build_manifest.py --out D:\大疆\docs\ai\tools\published_cleanup\manifest.csv
# 3) dry-run：每个文件核对存在 / 字节数 / 修改时间，不动手
powershell -File D:\大疆\docs\ai\tools\published_cleanup\recycle.ps1 -Manifest D:\大疆\docs\ai\tools\published_cleanup\manifest.csv
# 4) 先拿 1 个小文件试点，再全量（-Execute 才真的移）
powershell -File ...\recycle.ps1 -Manifest ...\manifest.csv -Execute -OnlyPathLike "某个小文件名"
powershell -File ...\recycle.ps1 -Manifest ...\manifest.csv -Execute
```
`manifest.csv` 和 `*.recycle_log.tsv` 不进 git（`.gitignore` 白名单没有 csv / tsv），是本机的流水。

## 什么算“已发布”（要全对才加进登记表）
- 以各条的 `投稿信息.json` 为准：`approval.status` 是 `pending` 的不算；视频号 2026-10-06 起不发：判断“全平台发完”只看 B 站 / 抖音 / 小红书（以前写着“视频号待发”的作品现在也算已发布，但要不要补清理先问用户，没有擅自清）；只有 B 站 BV 号但其他平台明确没发的也不算，除非本来就只发那个平台（日报竖屏版不发 B 站、Way to AGI 短视频不发 B 站）。
- 没有 `投稿信息.json` 的老作品，看 `AGENTS.md` / `README.md` 的发布表和 `docs/ai/context/` 里的投稿记录，有 BV 号 / “已投稿”才算。拿不准就不加，问用户。
- **B 站公开接口核对不了**：连续查几个 BV 就返回 412（风控），这是反爬拦截，别绕。“审核中”的几条（Fable5.5、白宫、Claude Code 03、订阅教程）记录里没写过审结果，清理时在报告里单独标出，让用户清空回收站之前自己在 B 站看一眼。
- 同一个作品目录里没发布的版本要避开：用 `include` / `exclude`（DevDay 六条只发了 V1 / V4 / V5；第 3 期的白板版没换上线）。

## 一律不碰（`protected_components`）
`素材`、`参考分析`、`真人素材`、`游戏素材`、`_skilltest`、`片头片尾`（共用模板的渲染）、`proxy`、`_check`、`engine`。
- `制作\02_出镜\proxy\*.mp4` 是 SD 卡原片（`H:\DCIM\DJI_001`，只读、平时没插着）的 720p 代理，可能是出镜原片在本机唯一的副本，按素材留。从它剪出来的 `02_出镜\edit\facecam.mp4`、`_segs\*.mp4` 是能再生成的，清了。
- 非视频文件（音频、图片、台本、脚本、json、字幕、封面）一个都不动；清空后的空目录也留着。

## 踩过的坑
- **回收站有容量上限**：注册表 `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\BitBucket\Volume\{卷 GUID}` 的 `MaxCapacity`（MB），D 盘是 25172 MB（约 24.6 GB），`NukeOnDelete=0` 才是真的进回收站。**装不下时 Windows 静默永久清掉超出的部分（连同里面原有的东西）**。动手前核对：清单总量 + 回收站原有 < 上限；超了就分几次、让用户先清空一次回收站。2026-10-03 星轨那次 U 盘卡的回收站只有 7.2 GB，就是因此改成先拷到 C 盘再删。
- **`SHQueryRecycleBin` 的计数滞后**：刚移完显示 +0 条（试点时的假警报，文件其实已在回收站里）。`recycle.ps1` 改成数回收站文件夹里 `$R*` 的实体文件个数 + 字节数，每个作品一批、对不上就停。
- 移进回收站**不释放磁盘空间**，要用户清空回收站才腾出来（D 盘 2026-10-05 只剩 10.7 GB）。
- 移之前每个文件核对字节数 + 修改时间：多个会话同时在工作（别人刚重渲的文件和清单不一致就跳过）。
- dcg 钩子会拦递归删除（见记忆 `dcg-hook-blocks-rm-rf-in-home`）；这个脚本是逐个文件 `SendToRecycleBin`，没被拦过。被拦就别绕，把命令交给用户。
- 还原：打开回收站，选中要的文件“还原”，会回到原路径。

## 登记表之外还能清的（没动，等用户说话）
测试 / 试跑 / 旧稿目录（`AI科普\_skilltest` 2.0 GB、`AI日报\_测试_*` / `_试跑_*` / `_旧稿` 等，共约 3.3 GiB，不是已发布作品）；确认已发布后才能清的作品（AI实操第 1 期等，见记录）。
