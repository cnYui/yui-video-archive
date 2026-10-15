"""按本地逐句缓存的实际长度生成配音时间轴，避免用字数估同步。"""
import importlib.util
import json
import wave
from pathlib import Path
import numpy as np

EP=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('localtts',r'D:\大疆\AI日报\skill\ai-daily-news\scripts\local_tts.py')
tts=importlib.util.module_from_spec(spec);spec.loader.exec_module(tts)
script=json.loads((EP/'台本/录制稿.json').read_text(encoding='utf-8'))
text=(EP/'台本/配音稿.txt').read_text(encoding='utf-8')
cache=sorted((EP/'配音/local_qwen').glob('s*.npy'))
sents=tts.split_sentences(text)
assert len(cache)==len(sents),(len(cache),len(sents))
sr=24000
rows=[];cur=0.;idx=0
for line in script['lines']:
    parts=tts.split_sentences(line['say'])
    start=cur
    for s,end in parts:
        actual=sents[idx][0].lstrip('\ufeff')
        assert actual==s,(actual,s)
        x=np.load(cache[idx]);voice_end=cur+len(x)/sr
        cur=voice_end+int(tts.GAP.get(end,.3)*sr)/sr;idx+=1
    rows.append({'id':line['id'],'s':round(start,5),'e':round(voice_end,5),'n0':round(start,5),'n1':round(cur,5)})
with wave.open(str(EP/'制作/02_配音/edit/tts_narration.wav'),'rb') as w:total=w.getnframes()/w.getframerate()
assert abs(cur-total)<1e-4,(cur,total)
(EP/'制作/02_配音/edit/tts_edit.json').write_text(json.dumps({'engine':'Qwen3-TTS-12Hz-0.6B-CustomVoice','speaker':'Vivian','speed':1.0,'total':total,'lines':rows},ensure_ascii=False,indent=2),encoding='utf-8')
pub=json.loads((EP/'投稿信息.json').read_text(encoding='utf-8'))
pub.update({'slug':'REA逆向设备','video':str(EP/'REA逆向设备_成片.mp4'),'duration_s':total,'source':{'original_post':['https://x.com/0xlangeai/status/2109544824135467312','https://x.com/ResearchWang/status/2109812002076143824'],'original_author':['蓝哥AI @0xlangeai','@ResearchWang'],'project_or_site':'https://github.com/morluto/rea'}})
pub['titles']=[
 {'id':1,'recommend':True,'angle':'设备协议','bilibili':'REA：从厂商 App 查到设备协议，自己的控制端能自己写吗？','douyin':'REA：自己的设备，自己写控制端','xiaohongshu':'用REA，看懂自己的设备协议'},
 {'id':2,'angle':'热度与机制','bilibili':'21.8 万 Star 的 REA 到底做什么？让 AI 顺着证据逆向程序','douyin':'21.8万Star的REA，怎么逆向程序','xiaohongshu':'21.8万Star的REA到底做什么'},
 {'id':3,'angle':'能力边界','bilibili':'“逆向一切”有多真？在线看 REA 代码，拆解 APK、抓包与固件链路','douyin':'“逆向一切”有多真？看REA的证据链','xiaohongshu':'REA真能逆向一切？先看证据'}]
desc='REA（Reverse Engineer Anything）把程序分析工具接给 Claude Code / Codex。本期直接在线阅读官方代码，拆解 ADB 获取 APK、HAR/mitmproxy 抓包分析、Binwalk/Unblob 固件解包和 Ghidra 分析的证据链。Star 为 2026-10-14 查询快照，约 21.8 万。\n\n源码：https://github.com/morluto/rea\nX 教程与原图：蓝哥AI @0xlangeai（https://x.com/0xlangeai/status/2109544824135467312）；@ResearchWang（https://x.com/ResearchWang/status/2109812002076143824）。\n菜单栏空调画面来自独立开源项目 MideaBar：https://github.com/Binaryify/MideaBar，仅作控制端示例，未声称由 REA 完成。固件链路需 Linux 与已有外部工具；是否能还原某台设备取决于协议、权限等。\n本地 Qwen3-TTS 合成配音，中英双语字幕。图片版权归原作者，本期作介绍与评论引用。'
for key in ('bilibili','douyin','xiaohongshu'):
    pub[key]['title']=pub['titles'][0][key];pub[key]['desc']=desc
pub['bilibili']['tags']=['REA','开源','逆向工程','人工智能','Codex','Claude Code','智能家居','设备协议']
pub['douyin']['topics']=['人工智能','开源项目','REA','逆向工程','智能家居']
pub['xiaohongshu']['topics']=['人工智能','开源项目','REA','逆向工程','Codex','ClaudeCode','智能家居','设备协议']
pub['approval']['note']='制作交付，尚未授权发布；推荐封面 A、标题 1。第 0 帧采用推荐封面，供预览。'
(EP/'投稿信息.json').write_text(json.dumps(pub,ensure_ascii=False,indent=2),encoding='utf-8')
print('本地配音',total,'s；',len(rows),'句，',len(sents),'合成块')
