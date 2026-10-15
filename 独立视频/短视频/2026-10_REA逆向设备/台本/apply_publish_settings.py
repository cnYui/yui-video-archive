"""固化用户指定的封面、标题和平台默认值，避免旧多平台流程覆盖本轮决定。"""
import json
from pathlib import Path

ROOT = Path('D:/大疆')
EP = Path(__file__).resolve().parents[1]
policy = '默认发布平台（2026-10-14 用户定）：短视频、长视频在用户未指定平台时仅发 B 站；不打开、不上传其他平台。用户明确要求其他平台时才启用对应流程。平台默认值不代替发布授权；用户已说“发布”时，完成读回核对后直接发布，不重复确认。'
skills = [
    ROOT/'短视频/skill/short-video/SKILL.md',
    ROOT/'Way to AGI/skill/way-to-agi-episode/SKILL.md',
    ROOT/'AI震惊瘫坐时代计算机研究生必须掌握的技能/skill/cs-grad-ai-episode/SKILL.md',
    ROOT/'Claude Code相关/skill/claude-code-episode/SKILL.md',
    ROOT/'OpenAI相关/skill/openai-episode/SKILL.md',
    ROOT/'AI科普/skill/yuanlai-ruci-episode/SKILL.md',
]
for path in skills:
    text = path.read_text(encoding='utf-8')
    end = text.index('\n---', 4) + 4 if text.startswith('---') else 0
    text = text[:end] + '\n\n**' + policy + '**\n' + text[end:]
    if 'short-video' in str(path):
        text = text.replace('三个平台全发（B 站 / 抖音 / 小红书）', '仅发 B 站（其他平台仅在用户明确指定时启用）')
        text = text.replace('步骤 7：开三个平台', '步骤 7：打开本轮指定的平台（默认仅 B 站）')
        text = text.replace('授权后三个平台**一次填完整', '授权后仅对本轮指定的平台**一次填完整')
        text = text.replace('**同意后发三个平台（④）**', '**同意后发布（④，默认仅 B 站）**')
        text = text.replace('→ 开三个页、', '→ 打开指定平台投稿页（默认仅 B 站）、')
        text = text.replace('现在发布的是 B 站 / 抖音 / 小红书三个平台', '当前默认仅 B 站；抖音 / 小红书须用户另行指定')
    if 'way-to-agi-episode' in str(path):
        text = text.replace('B 站 + YouTube 两个平台都发', '默认仅 B 站；YouTube 仅在用户明确要求时发布')
        text = text.replace('**每期两个平台都发**（用户 2026-09-29）', '**默认仅 B 站，用户明确指定才发 YouTube**（2026-10-14 更新）')
        text = text.replace('### 9. 投稿 ✋（两个平台）', '### 9. 投稿 ✋（默认仅 B 站）')
        text = text.replace('- YouTube：', '- YouTube（仅用户明确指定时）：')
        text = text.replace('「立即投稿」「发布」永远由用户自己点', '用户明确授权“发布”后可由代理点击「立即投稿」「发布」；未授权时停在提交前')
    path.write_text(text, encoding='utf-8')
    reference = path.parent/'references/publish.md'
    if reference.exists():
        content = reference.read_text(encoding='utf-8')
        reference.write_text('> '+policy+'\n\n'+content, encoding='utf-8')

agents = ROOT/'AGENTS.md'
with agents.open('a', encoding='utf-8') as f:
    f.write('\n- **'+policy+'** 旧合集表中的多平台默认值由本条覆盖；本轮改动见 docs/ai/context/20261014-165000-rea-publish-plan_CN.md。\n')

cover = EP/'制作/04_封面/candidates_framed.json'
data = json.loads(cover.read_text(encoding='utf-8'))
a = next(x for x in data['candidates'] if x['id']=='A')
b = next(x for x in data['candidates'] if x['id']=='B')
chosen = dict(a, id='D', big=b['big'], recommend=True, note='用户指定：B 的文字 + A 的图片')
data['candidates'] = [x for x in data['candidates'] if x['id']!='D'] + [chosen]
cover.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

info_path = EP/'投稿信息.json'
info = json.loads(info_path.read_text(encoding='utf-8'))
title = '一个视频拆解最近爆火的“逆向一切”的 RAE 开源项目 从厂商 App 查到设备协议，自己的控制端能自己写吗？'
assert len(title)<=80
info['bilibili']['title'] = title
info['platforms'] = ['bilibili']
info['approval'] = dict(status='approved',cover='D（B文字+A图片）', title=title, approved_at='2026-10-14',note='用户明确授权 Playwright JS 上传后直接发布，仅 B 站；标题 RAE 按原文保留。')
info_path.write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
print('已更新短视频及5个长视频入口技能与发布参考。标题字数：',len(title))
