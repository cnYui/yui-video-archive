"""将用户最新的上传阈值写入各制作入口，保留历史记录。"""
import json
from pathlib import Path

ROOT=Path('D:/大疆')
rule='**上传方式（2026-10-14 用户定）：文件小于 10 MB 且本轮已授权自动上传时，可用 Playwright JS 上传完整文件；达到或超过 10 MB 就提醒用户手动上传。不为自动上传压缩、分块或改用低清版本。用户手动上传后继续填表，已授权发布则读回核对后点击发布。**'
skills=[ROOT/x for x in ['短视频/skill/short-video','Way to AGI/skill/way-to-agi-episode','AI震惊瘫坐时代计算机研究生必须掌握的技能/skill/cs-grad-ai-episode','Claude Code相关/skill/claude-code-episode','OpenAI相关/skill/openai-episode','AI科普/skill/yuanlai-ruci-episode']]
for skill in skills:
    path=skill/'SKILL.md'
    text=path.read_text(encoding='utf-8')
    marker='平台默认值不代替发布授权；用户已说“发布”时，完成读回核对后直接发布，不重复确认。**'
    assert marker in text
    text=text.replace(marker,marker+'\n\n'+rule,1)
    path.write_text(text,encoding='utf-8')
    ref=skill/'references/publish.md'
    if ref.exists():
        ref.write_text(rule+'\n\n'+ref.read_text(encoding='utf-8'),encoding='utf-8')
with (ROOT/'AGENTS.md').open('a',encoding='utf-8') as f:
    f.write('\n- '+rule+' 本期14.5MB原片由用户手动上传，见 docs/ai/context/20261014-165500-rea-manual-upload-rule_CN.md。\n')
template=ROOT/'短视频/skill/short-video/assets/publish-template/投稿信息.json'
data=json.loads(template.read_text(encoding='utf-8'))
data['platforms']=['bilibili']
data['_说明']='2026-10-14 起默认仅 B 站；其他平台字段只是备用，用户明确指定才启用。'+data['_说明']
data['video']='<成片完整路径>（小于10MB且已授权时可自动传；达到或超过10MB提醒用户手动上传，不压缩）'
template.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('已同步6个制作入口、发布参考、模板与项目规则。')
