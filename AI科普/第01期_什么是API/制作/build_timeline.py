"""Build 制作/timeline.json — the single source of timing for engine, subtitles, chapter bar and audio mix.

Inputs
  ../build_script_v3.py          scene/segment text + visual notes (imported)
  voice/durations.json           optional {segment_id: seconds} measured from the generated TTS clips
  voice/alignment.json           optional {segment_id: [{"text":..,"start":..,"end":..}]} subtitle line timing
                                 relative to the clip start (from ASR); falls back to char-proportional split

Times in "segments"/"scenes" are MAIN-BODY time (0 = first frame after the intro file).
Times in "chapters" are TOTAL video time (intro + main + outro), so the burned-in bar lines up with the
player's own progress bar.
"""
import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FPS = 30
INTRO = 3.8            # UE intro file length (s)
OUTRO = 4.8            # UE outro file length (s)
SEG_GAP = 0.25         # breathing room after every spoken segment (s)
MAX_LINE = 20          # max display width (CJK units) per subtitle line

spec = importlib.util.spec_from_file_location("script_v3", HERE.parent / "build_script_v3.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)

CHAPTER_TITLES = {
    "S01": "开场", "S02": "三个疑问", "S03": "API 是什么", "S04": "“已接入”接了什么",
    "S05": "API Key 是什么", "S06": "三种调用方式", "S07": "获取 DeepSeek Key", "S08": "总结",
}
BG = {"S01": "bg1", "S02": "bg1", "S03": "bg1", "S04": "bg2", "S05": "bg1", "S06": "bg1", "S07": "bg1", "S08": "bg1"}


def load_json(p, default):
    p = HERE / p
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def width(s):
    """Display width in CJK-character units (ASCII letters/digits are about half as wide)."""
    return sum(0.55 if ord(c) < 128 else 1.0 for c in s)


def _atoms(clause):
    """Break a clause into unbreakable pieces: single CJK chars, whole ASCII words (with trailing space)."""
    return re.findall(r'[A-Za-z0-9_./:\-]+ ?|.', clause)


def split_lines(text):
    """Split a subtitle into display lines: break at punctuation first, never inside an English word,
    keep each line <= MAX_LINE wide, and avoid orphan fragments of just two or three characters."""
    clauses = [p for p in re.split(r'(?<=[，。？！：；、])', text) if p.strip()]
    # 1) any clause wider than the limit is split at an atom boundary near its middle
    pieces = []
    for c in clauses:
        while width(c) > MAX_LINE + 2:
            atoms, acc, cut = _atoms(c), 0.0, 0
            target = min(MAX_LINE, width(c) / 2 + 2)
            for i, a in enumerate(atoms):
                if acc + width(a) > target:
                    break
                acc += width(a)
                cut = i + 1
            cut = max(1, cut)
            pieces.append("".join(atoms[:cut]).rstrip())
            c = "".join(atoms[cut:]).lstrip()
        pieces.append(c)
    # 2) greedily join pieces into lines
    lines, cur = [], ""
    for p in pieces:
        if cur and width(cur) + width(p) > MAX_LINE:
            lines.append(cur)
            cur = p
        else:
            cur += p
    if cur:
        lines.append(cur)
    # 3) merge orphans (< 5 wide) into a neighbour when the result stays readable
    merged = []
    for ln in lines:
        if merged and (width(ln) < 5 or width(merged[-1]) < 5) and width(merged[-1]) + width(ln) <= MAX_LINE + 4:
            merged[-1] += ln
        else:
            merged.append(ln)
    return [ln.rstrip("，、；：").strip() for ln in merged if ln.strip("，、；：").strip()]


def _norm(s):
    return re.sub(r'[\s，。？！：；、“”"\'（）()·—\-]', '', s)


def retime_lines(text, old_lines, seg_start, seg_dur):
    """Time freshly split lines from an older aligned split: interpolate time per normalised character
    inside each old line, then read off the new line boundaries."""
    marks = []                                   # (char_position, time) knots
    pos = 0
    for ol in old_lines:
        n = len(_norm(ol["text"]))
        marks.append((pos, ol["start"]))
        pos += n
        marks.append((pos, ol["end"]))
    total = pos or 1

    def t_at(p):
        for (p0, t0), (p1, t1) in zip(marks, marks[1:]):
            if p0 <= p <= p1:
                return t0 if p1 == p0 else t0 + (t1 - t0) * (p - p0) / (p1 - p0)
        return marks[-1][1]

    new = split_lines(text)
    out, pos = [], 0
    for i, ln in enumerate(new):
        n = len(_norm(ln))
        a = 0.0 if i == 0 else t_at(min(pos, total))
        b = seg_dur if i == len(new) - 1 else t_at(min(pos + n, total))
        out.append(dict(text=ln, start=round(seg_start + a, 3), end=round(seg_start + max(b, a + 0.3), 3)))
        pos += n
    for i in range(1, len(out)):
        out[i]["start"] = out[i - 1]["end"]
    return out


def main():
    durations = load_json("voice/durations.json", {})
    alignment = load_json("voice/alignment.json", {})
    t = 0.0
    n = 0
    segments, gaps, scenes = [], [], []
    for sc in script.SCENES:
        if sc["id"] in ("S00", "S09"):          # intro / outro are separate files
            continue
        start = t
        for row in sc["rows"]:
            if row[0] == "gap":
                _, dur, visual = row
                gaps.append(dict(scene=sc["id"], start=round(t, 3), end=round(t + dur, 3), visual=visual))
                t += dur
                continue
            _, _sid, text, tts, visual = row
            n += 1
            seg_id = f"{sc['id']}-{n:02d}"
            units = script.spoken_units(tts)
            sentences = max(1, len(re.findall(r'[。？！]', tts)))
            est = units / script.CPS + sentences * script.SENT_PAUSE
            dur = float(durations.get(seg_id, est))
            if seg_id in alignment:
                lines = retime_lines(text, alignment[seg_id], t, dur)
            else:
                parts = split_lines(text)
                total = sum(len(p) for p in parts) or 1
                lines, lt = [], t
                for p in parts:
                    ld = dur * len(p) / total
                    lines.append(dict(text=p, start=round(lt, 3), end=round(lt + ld, 3)))
                    lt += ld
            pose = "reach" if "【动作：抬手" in visual else "idle"
            segments.append(dict(id=seg_id, scene=sc["id"], start=round(t, 3), end=round(t + dur, 3),
                                 text=text, tts=tts, visual=visual, pose=pose, lines=lines,
                                 measured=seg_id in durations))
            t += dur + SEG_GAP
        scenes.append(dict(id=sc["id"], title=sc["title"], start=round(start, 3), end=round(t, 3),
                           bg=BG[sc["id"]], notes=sc["char"]))
    main_dur = round(t, 3)
    total = round(INTRO + main_dur + OUTRO, 3)

    chapters = []
    for i, s in enumerate(scenes):
        c_start = 0.0 if i == 0 else INTRO + s["start"]
        c_end = total if i == len(scenes) - 1 else INTRO + s["end"]
        chapters.append(dict(id=s["id"], title=CHAPTER_TITLES[s["id"]], start=round(c_start, 3), end=round(c_end, 3)))

    timeline = dict(fps=FPS, intro=INTRO, outro=OUTRO, main_duration=main_dur, total_duration=total,
                    chapters=chapters, scenes=scenes, segments=segments, gaps=gaps,
                    walk_in=dict(start=0.0, end=1.2))
    (HERE / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding="utf-8")

    def mmss(x):
        return f"{int(x // 60)}:{int(x % 60):02d}"
    chap_txt = "\n".join(f"{mmss(c['start'])} {c['title']}" for c in chapters)
    (HERE / "chapters_bilibili.txt").write_text(chap_txt + "\n", encoding="utf-8")
    measured = sum(1 for s in segments if s["measured"])
    print(f"main={main_dur:.1f}s total={total:.1f}s segments={len(segments)} measured={measured}")
    print(chap_txt)


if __name__ == "__main__":
    main()
