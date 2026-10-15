"""记录本期实际交付和上传阻塞，不将准备完成写成发布成功。"""
import hashlib
import json
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path('D:/大疆')
EP=Path(__file__).resolve().parents[1]
now=datetime.now(timezone(timedelta(hours=9)))
stamp=now.strftime('%Y%m%d-%H%M%S')
p=EP/'投稿信息.json';d=json.loads(p.read_text(encoding='utf-8'))
video=EP/'CCBaga_成片.mp4'
d['delivery']=dict(created_at=now.isoformat(),resolution=[1080,2340],fps=30,frames=2596,duration=86.533333,size_bytes=video.stat().st_size,sha256=hashlib.sha256(video.read_bytes()).hexdigest(),qa=dict(page_errors=0,subtitle_width='通过',audio_asr='20句，17句达到0.8；3句英文专名转写差异',cover_frame0='2596帧与全部pts保持一致，原音轨md5一致，解码无错误'))
d['bilibili']['published']=None
d['publish_status']='waiting_manual_upload'
d['publish_blocker']='Playwright fileChooser.setFiles 返回 DOM.setFileInputFiles: Not allowed；B站登录态已确认可用。'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
rel=f'docs/ai/context/{stamp}-ccbaga-short-video-delivery_CN.md'
text=f'''# CCBaga 短视频交付及 B站上传阻塞

时间：{now.isoformat()}。

## 授权与实际内容

用户要求不出镜、本地模型配音、做完直接 Playwright 发布；本轮后续明确只发 B站。指定封面「Claude永不封号？！」，指定标题「这个github开源项目防止你的Claude封号！ccbaga」。后来要求细讲防封机制，扩成86.5秒，解释身份归档、独立浏览器、语言时区地区对齐、出口核验，并明确全绿不保证防封。

当前项目 v0.2.43；独立事实核对代理检查了 README、usage、Windows文档、浏览器核验与身份源码。项目没有降低封号率的已验证数据；不运行真实身份清理、系统修改或网络部署。身份 UI 是项目原始组件的虚构身份隔离预览，画面与简介标明。

## 交付

- 本期目录：Claude Code相关/短视频/04_CCBaga环境工具/。
- 成片：CCBaga_成片.mp4，1080×2340、30fps、2596帧、86.53秒，约7.2MB。
- 手机预览、三份 SRT、封面3候选×3比例和选定A、事实核对、台本、投稿信息齐备。
- 配音：本机Qwen3-TTS-12Hz-0.6B-CustomVoice，Vivian，原速，20句同源时间轴；混音-16 LUFS，真峰值约-3.3dBFS。
- 字幕宽度与页面加载通过；4路渲染页面报错0。音轨逐句ASR 17/20达到0.8，开头3句差异主要为Claude、CCBaga、GitHub及A/B的转写；没有假称已用耳朵听过。
- 封面首帧验收：帧数、每帧pts一致，原声md5一致，抽样拷贝段逐像素一致，解码无报错。

## 发布真实状态

B站登录有效，已经打开投稿页，但未投稿，没有BV号。分步Playwright扩展连接会重置，改用同次连接处理页面。上传区域真正可点的是 `.upload-area`，文字层是 no-events，点文字会被父层拦截。正确触发文件选择窗后，标准 browser_file_upload 报：`fileChooser.setFiles: Protocol error (DOM.setFileInputFiles): Not allowed`。没有用注入文件、分块或本地服务绕过。

需要用户在原生选择窗选择成片，或取消后拖入原片；用户回复“拖好了”后直接继续填表、两比例封面、人工智能分区、Claude Code相关合集、AI声明并投稿，不重复请求发布许可。发布只有在成功页面及线上稿件接口核对后才能记录为已发布。

共享仓原有多个未提交修改，本轮没有提交、推送或用原文件备份覆盖他人改动。配音主流程、短视频共享引擎和Playwright令牌均未改。
'''
(ROOT/rel).write_text(text,encoding='utf-8')
agents=ROOT/'AGENTS.md'
with agents.open('a',encoding='utf-8') as f:
    f.write(f'\n- **CCBaga 短视频（2026-10-14）**：`Claude Code相关/短视频/04_CCBaga环境工具/`，86.5秒、不出镜、本地Qwen配音，只发B站；封面和标题按用户指定。成片已完成，Playwright标准文件上传被 `DOM.setFileInputFiles: Not allowed` 拒绝，待用户手动上传后继续投稿；尚无BV号。记录 `{rel}`。\n')
print(str(ROOT/rel))
print('交付已记录；发布状态：待用户上传，尚未发布')
