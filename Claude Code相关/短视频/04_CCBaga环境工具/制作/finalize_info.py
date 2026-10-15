"""交付元信息只读取本期产物，用户指定标题与封面保持原文。"""
import json
from pathlib import Path
EP=Path(__file__).resolve().parents[1]
p=EP/'投稿信息.json';d=json.loads(p.read_text(encoding='utf-8'))
d['duration_s']=json.loads((EP/'制作/00_整片/timeline.json').read_text(encoding='utf-8'))['total']
d['titles'] += [dict(id=2,angle='备选功能介绍，不发布',bilibili='CCBaga：把 Claude 本地身份、浏览器和环境检查放进一个开源工具',douyin='CCBaga：Claude 环境管理工具',xiaohongshu='Claude环境整理工具CCBaga'),dict(id=3,angle='备选边界说明，不发布',bilibili='Claude 永不封号？CCBaga 的绿色核验到底代表什么',douyin='Claude全绿核验能保证不封号吗？',xiaohongshu='CCBaga全绿等于不封号吗？')]
assert d['bilibili']['title']=='这个github开源项目防止你的Claude封号！ccbaga'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
(EP/'README.md').write_text('''# CCBaga 环境工具短视频

用户要求：不出镜、本地模型配音、做完直接 Playwright 发布；本轮明确只发 B站。封面文字「Claude永不封号？！」，标题「这个github开源项目防止你的Claude封号！ccbaga」。

成片：CCBaga_成片.mp4；手机预览：CCBaga_手机预览.mp4；三份字幕：双语、中文、英文 SRT。1080×2340、30fps，约86.5秒，不加片头片尾。

配音：本机 Qwen3-TTS-12Hz-0.6B-CustomVoice，Vivian，原速。20句逐句音频、时间轴同源，混入既有系列 BGM。

内容：本地归档和保留策略、独立浏览器配置、语言时区地区一致性、真实出口与浏览器读数对照。没有核实防封成功率；全绿仅代表已测项目匹配，地区选择不自动改变IP，受限账号应官方申诉。

素材在合集层「素材/2026-10_CCBaga/」。身份界面取项目原始组件的隔离预览，明确标示虚构身份，没有运行真实原生清理或网络变更。项目版本 v0.2.43，来源 https://github.com/liseami/CCBaga。

发布状态以「投稿信息.json」的 published 字段和本轮 context 记录为准，未拿到线上稿件证据前不得称为已发布。
''',encoding='utf-8')
print('已完成交付说明和投稿元信息')
