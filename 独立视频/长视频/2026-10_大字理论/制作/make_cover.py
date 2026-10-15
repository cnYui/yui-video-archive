"""用真实人像和字号对比解释主题，四个大字在小缩略图中也能读清。"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import cv2

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "封面"
OUT.mkdir(exist_ok=True)
ASSETS = Path(r"D:\大疆\独立视频\素材\2026-10_大字理论")
FONT = r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf"
INK, ORANGE, YELLOW, PAPER = "#141413", "#FF5A24", "#FFD747", "#FAF9F5"

def font(size, weight=900):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_axes([weight])
    return f

def cover(w, h, name):
    im = Image.new("RGBA", (w,h), PAPER)
    d = ImageDraw.Draw(im)
    cx,cy = int(w*.61), 535
    for i in range(34):
        a = i*2*math.pi/34
        delta = .017
        pts = [(cx+int(180*math.cos(a)),cy+int(180*math.sin(a))),
            (cx+int(2400*math.cos(a-delta)),cy+int(2400*math.sin(a-delta))),
            (cx+int(2400*math.cos(a+delta)),cy+int(2400*math.sin(a+delta)))]
        d.polygon(pts, fill="#F3E9D8")
    # 两个手机分别表现拥挤的信息流与大字，手机里不增加解释文案。
    x,y=60,120
    small=Image.new("RGBA",(310,640))
    q=ImageDraw.Draw(small)
    q.rounded_rectangle((10,10,295,620),40,fill=INK)
    q.rounded_rectangle((24,43,281,588),22,fill="#E9EDF0")
    for i in range(11):
        yy=82+i*42
        q.rounded_rectangle((40,yy,69,yy+29),7,fill=["#C6D1DA","#A8CDBB","#E8BCAC"][i%3])
        q.rounded_rectangle((82,yy+1,245,yy+7),3,fill="#8D959E")
        q.rounded_rectangle((82,yy+15,218,yy+21),3,fill="#B8BFC5")
        q.ellipse((251,yy-3,278,yy+24),fill="#F24A44")
    small=small.rotate(10,Image.Resampling.BICUBIC,expand=True)
    im.alpha_composite(small,(x-45,y+90))
    d=ImageDraw.Draw(im)
    ax=302
    d.line((ax,525,ax+110,525),fill=ORANGE,width=26)
    d.polygon([(ax+92,481),(ax+144,525),(ax+92,569)],fill=ORANGE)
    bigx = 405 if w==1920 else 350
    bigw = 650 if w==1920 else 570
    d.rounded_rectangle((bigx+16,79,bigx+bigw+16,1024),64,fill=ORANGE)
    d.rounded_rectangle((bigx,55,bigx+bigw,1000),64,fill=INK)
    d.rounded_rectangle((bigx+19,74,bigx+bigw-19,982),49,fill=PAPER)
    d.rounded_rectangle((bigx+bigw//2-62,88,bigx+bigw//2+62,102),7,fill=INK)
    # 两行字让“字很大”本身成为画面论据。
    fontsize=242 if w==1920 else 216
    for text, yy, color in [("大字",225,YELLOW),("理论",525,"#FFFFFF")]:
        f=font(fontsize)
        tx=bigx+(bigw-d.textlength(text,font=f))/2
        d.text((tx+10,yy+14),text,font=f,fill=INK,stroke_width=13,stroke_fill=INK)
        d.text((tx,yy),text,font=f,fill=color,stroke_width=9,stroke_fill=INK)
    d.rounded_rectangle((bigx+bigw//2-65,934,bigx+bigw//2+65,942),4,fill=INK)
    portrait=Image.open(ASSETS/"portrait.png").convert("RGBA")
    if w==1920:
        portrait=portrait.resize((int(portrait.width*1.02),1102),Image.Resampling.LANCZOS)
        px,py=870,-2
    else:
        portrait=portrait.resize((int(portrait.width*.84),907),Image.Resampling.LANCZOS)
        px,py=510,171
        alpha=portrait.getchannel("A")
        mask=ImageDraw.Draw(alpha)
        mask.rectangle((0,0,bigx+bigw+8-px,portrait.height),fill=0)
        portrait.putalpha(alpha)
    # 限制宽度后独立裁 4:3，让人脸和标题同时处在安全区。
    a=np.array(portrait.getchannel("A"))
    border=cv2.dilate(a,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(23,23)))
    outline=Image.new("RGBA",portrait.size,"white")
    outline.putalpha(Image.fromarray(border))
    shadow=Image.new("RGBA",portrait.size,INK)
    shadow.putalpha(Image.fromarray(cv2.dilate(a,np.ones((31,31),np.uint8))))
    im.alpha_composite(shadow,(px+13,py+15))
    im.alpha_composite(outline,(px,py))
    im.alpha_composite(portrait,(px,py))
    im.convert("RGB").save(OUT/f"封面_{name}.png",optimize=True)
    return im.convert("RGB")

a=cover(1920,1080,"16x9")
b=cover(1440,1080,"4x3")
preview=Image.new("RGB",(1000,620),"#DADADA")
preview.paste(a.resize((640,360),Image.Resampling.LANCZOS),(0,0))
preview.paste(b.resize((360,270),Image.Resampling.LANCZOS),(640,0))
preview.paste(a.resize((384,216),Image.Resampling.LANCZOS),(0,390))
preview.paste(b.resize((288,216),Image.Resampling.LANCZOS),(420,390))
preview.save(OUT/"封面预览.png")
print("两比例封面完成",flush=True)
