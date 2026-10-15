"""本期数据与本地配音接线：保持共享模板不变，明确材料和实测边界。"""
import json
import re
from pathlib import Path

EP = Path(__file__).resolve().parents[1]
ENG = EP / '制作/00_整片'
MAT = EP.parents[1] / '素材/2026-10_CCBaga'
def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

rows = [
('Claude 永不封号？这个问号必须留着。','克劳德永不封号？这个问号必须留着。','Claude, never banned? Keep that question mark.'),
('有人把环境整理工具，做成了 CCBaga。','有人把环境整理工具，做成了西西巴嘎。','CCBaga brings environment tools into one app.'),
('GitHub 开源，核心分成 A、B 两个应用。','吉特哈布开源，核心分成诶、逼两个应用。','Open source on GitHub, with two apps: A and B.'),
('A 管本地身份，B 是独立浏览器。','诶管本地身份，逼是独立浏览器。','A manages local identities. B is a separate browser.'),
('清理之前先归档，聊天和缓存按需保留。','清理之前先归档，聊天和缓存按需保留。','Archive first. Keep chats and caches as needed.'),
('技能和配置，也能选择留下。','技能和配置，也能选择留下。','Skills and settings can stay in the workspace.'),
('这样换环境时，旧缓存不会混在一起。','这样换环境时，旧缓存不会混在一起。','This separates local state when changing workspaces.'),
('但本地归档，不会抹掉平台的服务端记录。','但本地归档，不会抹掉平台的服务端记录。','Local archives do not erase server-side records.'),
('浏览器支持换指纹种子，设置语言和时区。','浏览器支持换指纹种子，设置语言和时区。','Rotate browser seeds, and set language and timezone.'),
('独立配置目录，减少不同会话的本地数据混用。','独立配置目录，减少不同会话的本地数据混用。','A separate profile keeps local session data apart.'),
('语言、时区和地区对齐，让配置更容易检查。','语言、时区和地区对齐，让配置更容易检查。','Aligned regional settings make mismatches easier to inspect.'),
('再把浏览器读数，和真实网络出口对照。','再把浏览器读数，和真实网络出口对照。','Compare browser readings with the real network exit.'),
('浏览器自报的地区，得和出口实测一起看。','浏览器自报的地区，得和出口实测一起看。','Inspect reported regions alongside the measured exit.'),
('实测项目都匹配，验证页才会变绿。','实测项目都匹配，验证页才会变绿。','The page turns green only when measured checks match.'),
('但选地区，不会自动改变公网 IP。','但选地区，不会自动改变公网艾匹。','Selecting a region does not change your public IP.'),
('全绿也不等于免封号，项目自己写得很清楚。','全绿也不等于免封号，项目自己写得很清楚。','Green checks do not guarantee account acceptance.'),
('也没有实测数据，证明这套流程降低了封号率。','也没有实测数据，证明这套流程降低了封号率。','No measured ban-rate reduction is established here.'),
('它支持三大桌面系统，Windows 一个包就有 A 加 B。','它支持三大桌面系统，温斗斯一个包就有诶加逼。','Three desktop platforms. One Windows installer has A+B.'),
('只管理自己的环境，账号受限走官方申诉。','只管理自己的环境，账号受限走官方申诉。','Manage your own environment. Appeal restrictions officially.'),
('把环境看清楚，别把工具当成免封保证。','把环境看清楚，别把工具当成免封保证。','Inspect the environment. No tool guarantees no bans.'),
]
lines=[dict(id=f'N{i:02}',zh=z,say=s,en=e) for i,(z,s,e) in enumerate(rows,1)]
write_json(EP/'台本/录制稿.json',dict(slug='CCBaga',title='CCBaga 环境管理工具',kicker='悠一 · <b>Claude</b> 开源工具',hook=['Claude永不封号？！','CCBaga 开源工具'],lines=lines))
groups=[('repo',['N01','N02']),('arch',['N03','N04']),('identity',['N05','N06','N07','N08']),('browser',['N09','N10','N11','N12','N13','N14']),('limits',['N15','N16','N17']),('install',['N18']),('closing',['N19','N20'])]
write_json(EP/'台本/plan.json',dict(layout='single',plan=[dict(id=k,type='card',kind='page',overlay='page',name=k,dur=0.2,lines=[dict(id=i,a=0.0) for i in ids]) for k,ids in groups]))

cp=ENG/'capture_pages.py'
s=cp.read_text(encoding='utf-8')
start=s.index('SPECS = {'); end=s.index('SHOW_URL =',start)
specs={
'repo':('https://github.com/liseami/CCBaga','@top',2400,0,['CCBaga brings local maintenance']),
'arch':('https://github.com/liseami/CCBaga','Two applications work together',900,80,['CCBaga-A','CCBaga-B']),
'browser':('https://github.com/liseami/CCBaga','Open Browser',1200,75,['The success page appears only','A green result describes']),
'limits':('https://github.com/liseami/CCBaga','Selecting a region changes',900,130,['does not change your public IP']),
'install':('https://github.com/liseami/CCBaga','Platforms:',1150,90,['Windows x86_64 uses one NSIS']),
'closing':('https://github.com/liseami/CCBaga/blob/main/docs/usage.md','@top',2200,0,[]),
}
s=s[:start]+'SPECS = '+repr(specs)+'\n'+s[end:]
cp.write_text(s,encoding='utf-8')
sc=ENG/'scenes.js'
s=sc.read_text(encoding='utf-8')
s=s.split('\n// 画面采用当前项目页面；身份样本明确标示隔离界面预览。')[0]
s+='\n// 画面采用当前项目页面；身份样本明确标示隔离界面预览。\n'
s+="pageShot('N01','N02','repo', [['CCBaga brings local maintenance', S('N02'), '开源环境管理工具']]);\n"
s+="pageShot('N03','N04','arch', [['CCBaga-A',S('N03'),'A：本地操作'],['CCBaga-B',S('N04'),'B：配套浏览器']]);\n"
s+="pageShot('N05','N08','identity',[],{start:0});\n"
s+="note(S('N05'),E('N08')+.35,'隔离界面预览 · 虚构身份','',{y:710});\n"
s+="pageShot('N09','N14','browser',[['The success page appears only',S('N14'),'测量项目匹配，才显示绿色']]);\n"
s+="pageShot('N15','N17','limits',[['does not change your public IP',S('N15'),'选择地区不会改变公网 IP']]);\n"
s+="pageShot('N18','N18','install',[['Windows x86_64 uses one NSIS',S('N18'),'Windows：一个安装器包含 A+B']]);\n"
s+="pageShot('N19','N20','closing',[],{start:350,pad:.85});\n"
s+="linkPill(0.1,TL.total,'github.com/','liseami/<b>CCBaga</b>');\n"
sc.write_text(s,encoding='utf-8')
p=ENG/'mix_audio.py'; s=p.read_text(encoding='utf-8').replace('-21.0, -16.0, 1.0','-21.0, -10.0, 1.0').replace('BGM_SWELL_DB = 5.0','BGM_SWELL_DB = 0.0'); p.write_text(s,encoding='utf-8')
sub=EP/'投稿信息.json'; d=json.loads(sub.read_text(encoding='utf-8'))
title='这个github开源项目防止你的Claude封号！ccbaga'
d.update(slug='CCBaga',video=str(EP/'CCBaga_成片.mp4'),platforms=['bilibili'])
d['titles']=[dict(id=1,angle='用户指定',recommend=True,bilibili=title,douyin='CCBaga：把 Claude 环境一次理清',xiaohongshu='CCBaga能防封吗？')]
d['approval']=dict(status='authorized',cover='A',title=1,note='用户要求做完直接 Playwright 发布，后明确只发 B站；封面与标题按用户原文。')
d['bilibili'].update(title=title,desc='CCBaga 把 Claude 本地身份归档、配套浏览器和环境核验放到一个桌面工作流中。\n\n标题围绕防封话题；项目明确：选择地区不改变公网 IP，绿色结果只说明本次已测项目匹配，不保证匿名、解封或账号获准。仅管理自己的身份，遵守 Anthropic 条款与支持地区，账号受限走官方申诉。\n\n项目与画面来源：https://github.com/liseami/CCBaga\n版本：2026年10月14日核对 v0.2.43；第三方开源项目，与 Anthropic 无隶属或背书关系。身份页面为项目原始组件的隔离预览，使用虚构身份；没有执行真实清理或网络修改。\n\n配音：本机 Qwen3-TTS 开源模型合成；中英双语字幕。背景音乐来自本项目既有系列素材。',tags=['Claude','Claude Code','CCBaga','开源工具','AI工具','人工智能'],collection='Claude Code相关（9223239）',repost_source='')
write_json(sub,d)
write_json(EP/'制作/04_封面/candidates_framed.json',dict(candidates=[dict(id='A',note='用户指定文字，项目身份界面',recommend=True,video=str(MAT/'identity-preview.png'),t=0,crop=[0,0,1,1],big=['Claude','永不封号？！'],accent_line=1,sticker='CCBaga'),dict(id='B',note='用户指定文字，仓库主视觉',video=str(MAT/'CCBaga/docs/readme-hero.png'),t=0,crop=[0,0,1,1],big=['Claude','永不封号？！'],accent_line=1,sticker='CCBaga'),dict(id='C',note='用户指定文字，项目架构图',video=str(MAT/'architecture.png'),t=0,crop=[0,0,1,1],big=['Claude','永不封号？！'],accent_line=1,sticker='CCBaga')] ))
(EP/'台本/配音稿.txt').write_text('\n'.join(x['say'] for x in lines),encoding='utf-8')
print('已写本期台本、场景、用户指定封面和 B站投稿信息')
