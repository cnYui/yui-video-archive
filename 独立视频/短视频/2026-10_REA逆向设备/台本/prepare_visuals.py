"""将已核实的原图与原文摘录接入现有短视频引擎。"""
import json
import shutil
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

EP=Path(__file__).resolve().parents[1]
ENG=EP/'制作/00_整片'
MAT=EP.parents[1]/'素材/2026-10_REA逆向设备'
MED=ENG/'media'
MED.mkdir(exist_ok=True)
FONT=Path(r'D:\大疆\AI科普\素材\字体\NotoSansSC.ttf')
MONO=Path(r'C:\Windows\Fonts\consola.ttf')
W,H=1474,829

def font(size,mono=False):
    return ImageFont.truetype(str(MONO if mono else FONT),size)

def excerpt(key, source, first, last, highlights=()):
    # 摘录保留文件名和原始行号，避免把排版后的画面误当作实际运行结果。
    src=MAT/'证据'/source.replace('/','__')
    lines=src.read_text(encoding='utf-8').splitlines()
    im=Image.new('RGB',(W,H),'#101b2c'); d=ImageDraw.Draw(im)
    d.rounded_rectangle((22,22,W-22,90),12,fill='#20304a')
    d.text((44,36),source,font=font(32,True),fill='#e0e7ef')
    y=120
    for n in range(first,last+1):
        raw=lines[n-1]
        chunks=textwrap.wrap(raw, width=65,replace_whitespace=False,drop_whitespace=False) or ['']
        for k,t in enumerate(chunks):
            if y>H-78: break
            if any(s.lower() in raw.lower() for s in highlights):
                d.rectangle((30,y-1,W-30,y+39),fill='#58432c')
            d.text((44,y),str(n) if k==0 else '',font=font(30,True),fill='#7a8ba4')
            d.text((128,y),t,font=font(31,True),fill='#e8edf5')
            y+=40
    sha=json.loads((MAT/'证据/在线代码来源.json').read_text(encoding='utf-8'))[0]['sha']
    d.text((44,H-47),'morluto/rea · '+sha[:8]+' · 原文摘录',font=font(25),fill='#a5b3c8')
    p=MED/(key+'.png');im.save(p)
    return p

def fitted(key, path, crop=None):
    im=Image.open(path).convert('RGB')
    if crop:
        x0,y0,x1,y1=crop; im=im.crop((int(im.width*x0),int(im.height*y0),int(im.width*x1),int(im.height*y1)))
    im=ImageOps.contain(im,(W,H),Image.Resampling.LANCZOS)
    cv=Image.new('RGB',(W,H),'#faf9f5');cv.paste(im,((W-im.width)//2,(H-im.height)//2));p=MED/(key+'.png');cv.save(p);return p

def main():
    prefix='X_0xlangeai_2109544824135467312_'
    rp='X_ResearchWang_2109812002076143824_'
    fitted('tutorial',MAT/(prefix+'01.jpg'))
    fitted('roles',MAT/(prefix+'09.jpg'))
    fitted('code_example',MAT/(prefix+'05.jpg'))
    fitted('workflow',MAT/(rp+'02.jpg'))
    fitted('hopper',MAT/'REA_官方Hopper截图.png')
    fitted('ac',MAT/'MideaBar_官方演示封面.jpg',(0,0,1,.77))
    excerpt('adb','docs/adb-device-analysis.md',33,46,('pull-adb-package','inspect-android-package'))
    excerpt('captures','docs/web-network-captures.md',1,9,('HAR','inspect-web-network-capture'))
    excerpt('firmware','docs/firmware-analysis.md',1,15,('Binwalk','Unblob','Ghidra'))
    excerpt('license','LICENSE',1,9,('MIT','Permission'))
    # GitHub API 元数据是实测快照，单独保留明确的来源标签。
    meta=json.loads((MAT/'证据/github_metadata.json').read_text(encoding='utf-8'))
    stars=meta['stargazers_count'];p=MED/'repo.png';im=Image.new('RGB',(W,H),'#ffffff');d=ImageDraw.Draw(im)
    d.text((65,58),'GitHub API · 2026-10-14',font=font(30),fill='#6e7781')
    d.text((65,140),'morluto / rea',font=font(75),fill='#24292f')
    d.text((65,295),meta['description'][:63],font=font(33,True),fill='#57606a')
    d.rounded_rectangle((65,405,690,600),25,fill='#fff5d3',outline='#d0b95e',width=3)
    d.text((105,425),f'{stars:,} stars',font=font(70),fill='#24292f')
    d.text((105,530),'API 返回值快照',font=font(30),fill='#57606a')
    d.text((65,670),'github.com/morluto/rea · MIT',font=font(42,True),fill='#0969da');im.save(p)
    script=json.loads((EP/'台本/录制稿.json').read_text(encoding='utf-8'))
    plan=[]
    scenes=[('L01','ac','独立示例：MideaBar'),('L02','tutorial','@0xlangeai · X'),('L03','repo','GitHub API 实测'),('L04','hopper','REA 官方截图'),('L05','adb','REA 官方文档'),('L06','firmware','REA 官方文档'),('L07','roles','@0xlangeai · X'),('L08','ac','独立示例：MideaBar'),('L09','code_example','@0xlangeai · X')]
    for i,(lid,img,credit) in enumerate(scenes,1):
        plan.append({'id':f'S{i:02d}','type':'card','dur':1,'name':img,'kind':'source','overlay':'source','ui':{'image':img},'lines':[{'id':lid,'a':0}],'credit':credit})
    (EP/'台本/plan.json').write_text(json.dumps({'layout':'single','plan':plan},ensure_ascii=False,indent=2),encoding='utf-8')
    (ENG/'frames.js').write_text('window.FR = {scr:[],scr2:[]};\n',encoding='utf-8')
    common=(ENG/'common.py').read_text(encoding='utf-8').replace('XV = MAT / "<YYYY-MM_主题>"','XV = MAT / "2026-10_REA逆向设备"')
    (ENG/'common.py').write_text(common,encoding='utf-8')
    # 字体沿用模板指定的相对路径。
    fonts=ENG/'fonts';fonts.mkdir(exist_ok=True)
    for filename in ('NotoSansSC.ttf','Inter.ttf','JetBrainsMono.ttf'):
        candidates=[Path(r'D:\大疆\Claude Code相关\短视频\02_Anthropic设计师用Claude做设计\制作\00_整片\fonts')/filename,Path(r'D:\大疆\AI科普\素材\字体')/filename]
        src=next((p for p in candidates if p.exists()),None)
        if src:shutil.copy(src,fonts/filename)
    mix=(ENG/'mix_audio.py').read_text(encoding='utf-8').replace('-16.0, -21.0, -16.0, 1.0, -9.0','-16.0, -21.0, -10.0, 1.0, -9.0').replace('BGM_SWELL_DB = 5.0','BGM_SWELL_DB = 0.0')
    (ENG/'mix_audio.py').write_text(mix,encoding='utf-8')
    sources=['# 素材来源','', '原图只作介绍和评论引用，版权归原作者。所有 X 图片已下载，没有克隆 REA。','']
    for p in (MAT/'证据').glob('*图片来源.json'):
        for x in json.loads(p.read_text(encoding='utf-8')):sources.append(f"- `{x['file']}`：{x['post']}；图片 {x['url']}；作者 @{x['author']}。")
    sources += ['', '- REA Hopper 原截图：https://github.com/morluto/rea/blob/main/docs/assets/rea-hopper-analysis.png', '- MideaBar 原演示封面：https://github.com/Binaryify/MideaBar/blob/main/website/assets/poster.jpg；这只是独立控制端示例，未声称用 REA 完成。', '- 原文摘录截图：保留 REA 文件名、原始行号和 Git 提交；原文在 `证据/`。']
    (MAT/'来源.md').write_text('\n'.join(sources),encoding='utf-8')
    cov={'candidates':[{'id':'A','recommend':True,'note':'设备控制端角度，推荐','video':str(MAT/'MideaBar_官方演示封面.jpg'),'t':0,'crop':[0,0,1,.78],'big':['设备协议','自己掌握'],'accent_line':1,'sticker':'REA · 协议分析'}, {'id':'B','note':'逆向工具角度','video':str(MAT/'REA_官方Hopper截图.png'),'t':0,'crop':[0,0,1,1],'big':['逆向一切','看见证据'],'accent_line':1,'sticker':'REA · MIT 开源'}, {'id':'C','note':'REA 与 Agent 分工','video':str(MAT/(prefix+'09.jpg')),'t':0,'crop':[0,0,1,1],'big':['看懂程序','再写功能'],'accent_line':1,'sticker':'REA × Codex'}]}
    (EP/'制作/04_封面/candidates_framed.json').write_text(json.dumps(cov,ensure_ascii=False,indent=2),encoding='utf-8')
    print('画面、来源、封面配置完成')

if __name__=='__main__':main()
