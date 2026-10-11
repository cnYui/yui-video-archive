r"""片头片尾的路径和时长 —— 所有技能、所有视频共用这一套（2026-10-03 起：用户“所有生成的视频都需要使用片头和片尾”）。

    import sys; sys.path.insert(0, r"D:\大疆\AI科普\片头片尾"); from pack_info import intro_seconds, outro_seconds, ADD_TO_VIDEO
    python D:\大疆\AI科普\片头片尾\pack_info.py        # 打印路径和时长

时长直接从页面的 window.DURATION 读（epcommon.pack_durations 也是这么读的），模板换了不用改脚本：
SRT、B 站 / YouTube 章节时间 = 正片时间 + intro_seconds()。
"""
import re
from pathlib import Path

PACK = Path(__file__).resolve().parent                        # D:\大疆\AI科普\片头片尾
INTRO_HTML = PACK / "intro" / "index.html"
OUTRO_HTML = PACK / "outro" / "index.html"
INTRO_DATA = PACK / "intro" / "data.json"                     # {name, role, endColor}
OUTRO_DATA = PACK / "outro" / "data.json"                     # 默认片尾数据（每期的清单另写，见 README）
ADD_TO_VIDEO = PACK.parent / "skill" / "yuanlai-ruci-episode" / "scripts" / "add_to_video.py"
INTRO_FALLBACK, OUTRO_FALLBACK = 4.8, 9.0


def _duration(html, fallback):
    try:
        m = re.search(r"window\.DURATION\s*=\s*([0-9.]+)", Path(html).read_text(encoding="utf-8", errors="replace"))
        return float(m.group(1)) if m else fallback
    except OSError:
        return fallback


def intro_seconds():
    """片头时长（秒）"""
    return _duration(INTRO_HTML, INTRO_FALLBACK)


def outro_seconds():
    """片尾时长（秒）"""
    return _duration(OUTRO_HTML, OUTRO_FALLBACK)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"片头 {INTRO_HTML}  {intro_seconds()} s\n片尾 {OUTRO_HTML}  {outro_seconds()} s\n加到任意视频：python \"{ADD_TO_VIDEO}\" <正片.mp4> --outro-data <片尾.json>")
