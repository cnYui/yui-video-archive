"""同步封面后的手机预览与最终交付元数据，保存抽帧和文件诊断。"""
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

EP = Path(__file__).resolve().parents[1]
VIDEO = EP / "REA逆向设备_成片.mp4"
PREVIEW = EP / "REA逆向设备_手机预览.mp4"
QA = EP / "制作" / "00_整片" / "final_qa"
QA.mkdir(exist_ok=True)


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")


run(["ffmpeg", "-v", "error", "-y", "-i", str(VIDEO), "-vf", "scale=540:1170:flags=lanczos", "-c:v", "libx264", "-crf", "27", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(PREVIEW)])
reports = {}
for p in (VIDEO, PREVIEW):
    metadata = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,codec_type,width,height,r_frame_rate,nb_frames:format=duration,size", "-of", "json", str(p)]).stdout)
    video_stream = next(s for s in metadata["streams"] if s["codec_type"] == "video")
    assert video_stream["r_frame_rate"] == "30/1"
    assert int(video_stream["nb_frames"]) == 1762
    assert any(s["codec_type"] == "audio" for s in metadata["streams"])
    diagnostics = run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "null", "-"]).stderr
    assert not diagnostics.strip(), diagnostics
    reports[p.name] = metadata
assert reports[VIDEO.name]["streams"][0]["width"] == 1080
assert reports[VIDEO.name]["streams"][0]["height"] == 2340

info_path = EP / "投稿信息.json"
info = json.loads(info_path.read_text(encoding="utf-8"))
info["duration_s"] = float(reports[VIDEO.name]["format"]["duration"])
info["video"] = str(VIDEO)
info_path.write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(QA / "导出检查.json").write_text(json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

times = [0, 13.4, 26.4, 34.1, 43.4, 48.1]
sheet = Image.new("RGB", (6 * 280, 660), "#d8d8d8")
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype("D:/大疆/AI科普/素材/字体/NotoSansSC.ttf", 20)
for i, t in enumerate(times):
    frame = QA / f"成片_{t:.1f}s.png"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(VIDEO), "-frames:v", "1", str(frame)])
    sheet.paste(Image.open(frame).convert("RGB").resize((270, 585)), (i * 280 + 5, 50))
    draw.text((i * 280 + 5, 10), f"成片 {t:.1f}s", font=font, fill="#141413")
sheet.save(QA / "成片抽帧总览.png")
print(json.dumps(reports, ensure_ascii=False, indent=2))
print("预览同步、导出诊断、投稿信息和成片抽帧已完成。")
