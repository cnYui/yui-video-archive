"""用同一时间映射剪声音与画面，避免累计口型偏移。"""
import json
import subprocess
import sys
from pathlib import Path
from PIL import ImageFont

HERE = Path(__file__).resolve().parent
EP = HERE.parent
SRC = Path(r"H:\DCIM\DJI_001\DJI_20261014115040_0203_D.MP4")
sys.path.insert(0,r"D:\大疆\AI科普\片头片尾")
from pack_info import intro_seconds

def run(cmd):
    subprocess.run([str(x) for x in cmd],check=True)

def stamp(s, ass=False):
    units=100 if ass else 1000
    n=round(s*units)
    h,n=divmod(n,3600*units)
    m,n=divmod(n,60*units)
    sec,n=divmod(n,units)
    return f"{h}:{m:02}:{sec:02}.{n:02}" if ass else f"{h:02}:{m:02}:{sec:02},{n:03}"

def prepare():
    cues=[]
    for line in (HERE/"cues.tsv").read_text(encoding="utf-8").splitlines():
        s,e,zh,en=line.split("\t")
        cues.append(dict(s=float(s),e=float(e),zh=zh,en=en))
    # 按原声边界保留短停顿，较长停顿只在句间压缩。
    groups=[]
    for c in cues:
        s=max(0,c["s"]-.10)
        e=min(147.883,c["e"]+.16)
        if groups and s-groups[-1]["e"]<=.24:
            groups[-1]["e"]=e
        else:
            groups.append(dict(s=s,e=e))
    offset=0
    for i,g in enumerate(groups):
        g["out"]=offset
        part=HERE/"parts"/f"{i:02}.mp4"
        duration=g["e"]-g["s"]
        if part.exists() and part.stat().st_size:
            duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries",
                "format=duration","-of","csv=p=0",str(part)]))
        g["duration"]=duration
        offset+=duration
    def mapped(t):
        for g in groups:
            if g["s"]-.001<=t<=g["e"]+.001:
                return g["out"]+t-g["s"]
        raise ValueError(t)
    for i,c in enumerate(cues):
        c["start"]=max(0,mapped(c["s"])-.10)
        c["end"]=min(offset,mapped(c["e"])+.45)
        if i+1<len(cues):
            c["end"]=min(c["end"],mapped(cues[i+1]["s"])-.10)
    fonts=HERE/"fonts"
    fonts.mkdir(exist_ok=True)
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    base=r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf"
    for weight in (600,800):
        output=fonts/f"NotoSansSC-{weight}.ttf"
        f=instantiateVariableFont(TTFont(base),{"wght":weight})
        for record in f["name"].names:
            if record.nameID in (1,4,6,16):
                record.string=f"NSC{weight}".encode(record.getEncoding())
            elif record.nameID in (2,17):
                record.string="Regular".encode(record.getEncoding())
        f.save(output)
    for lang in ("zh","en","bilingual"):
        blocks=[]
        for i,c in enumerate(cues,1):
            txt=c["zh"]+"\n"+c["en"] if lang=="bilingual" else c[lang]
            blocks.append(f"{i}\n{stamp(c['start']+intro_seconds())} --> {stamp(c['end']+intro_seconds())}\n{txt}\n")
        label={"zh":"中文","en":"英文","bilingual":"双语"}[lang]
        (EP/f"大字理论_{label}字幕.srt").write_text("\n".join(blocks),encoding="utf-8-sig")
    sys.path.insert(0,r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
    from bilingual_std import ass_header,ass_events
    header=ass_header().replace("PlayResX: 1920","PlayResX: 2340")
    events=[]
    for c in cues:
        events.extend(ass_events(c["start"],c["end"],c["zh"],c["en"],cx=1170))
    (HERE/"subtitles.ass").write_text(header+"\n".join(events),encoding="utf-8-sig")
    for c in cues:
        assert len(c["zh"])<=28,c
        assert len(c["en"])<=90,c
    edit=dict(groups=groups,cues=cues,duration=offset,source=str(SRC),intro=intro_seconds())
    (HERE/"edit.json").write_text(json.dumps(edit,ensure_ascii=False,indent=2),encoding="utf-8")
    print("剪辑",len(groups),"段，正片",offset,"秒，字幕",len(cues),"条",flush=True)
    return edit

def render(edit):
    # 先建立一份高质量本地工作视频，后续只解码本地文件。
    work=HERE/"source1080.mp4"
    if not work.exists():
        run(["ffmpeg","-y","-v","warning","-threads","4","-i",SRC,"-map","0:v:0","-map","0:a:0",
            "-filter_threads","1","-vf","fps=30,scale=1920:1080:flags=lanczos,format=yuv420p",
            "-c:v","libx264","-threads","4","-preset","fast","-crf","17","-c:a","aac","-b:a","256k",work])
    # 分段顺序渲染，避免大规模 split 把完整视频同时压进内存。
    parts=HERE/"parts"
    parts.mkdir(exist_ok=True)
    for i,g in enumerate(edit["groups"]):
        p=parts/f"{i:02}.mp4"
        if p.exists():
            continue
        run(["ffmpeg","-y","-v","warning","-threads","4","-ss",f"{g['s']:.3f}","-i",work,
            "-t",f"{g['e']-g['s']:.3f}","-filter_threads","1","-vf","setpts=N/30/TB",
            "-af","asetpts=PTS-STARTPTS","-c:v","libx264","-threads","4","-preset","fast","-crf","17",
            "-c:a","aac","-b:a","256k","-ar","48000",p])
        print(f"剪辑段 {i+1}/{len(edit['groups'])}",flush=True)
    (HERE/"concat.txt").write_text("\n".join(f"file 'parts/{i:02}.mp4'" for i in range(len(edit['groups']))),encoding="utf-8")
    run(["ffmpeg","-y","-v","warning","-f","concat","-safe","0","-i",HERE/"concat.txt",
        "-c","copy",HERE/"edited.mp4"])
    run(["ffmpeg","-y","-v","warning","-i",HERE/"edited.mp4","-vn","-ac","1","-ar","16000",HERE/"qa_audio.wav"])
    finish()

def finish():
    run(["ffmpeg","-y","-v","warning","-threads","4","-i",HERE/"edited.mp4","-filter_threads","1",
        "-vf","pad=2340:1080:210:0:color=0xFAF9F5,ass=subtitles.ass:fontsdir=fonts",
        "-af","highpass=f=70,loudnorm=I=-16:TP=-1:LRA=11",
        "-c:v","libx264","-threads","4","-preset","fast","-crf","17","-profile:v","high","-level:v","4.2",
        "-pix_fmt","yuv420p","-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709",
        "-c:a","aac","-b:a","256k","-ar","48000","-movflags","+faststart",EP/"大字理论_正片.mp4"])

if __name__=="__main__":
    edit=prepare()
    if "--render" in sys.argv:
        render(edit)
    elif "--finish" in sys.argv:
        finish()
