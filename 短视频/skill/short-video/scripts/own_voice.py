# -*- coding: utf-8 -*-
r"""用户自己录口播（DJI 等出镜视频）做短视频：ASR 转写 + 用原片音轨建“配音”（不走 Fish）。2026-10-06《Claude 中文界面》那条定的流程。

  python own_voice.py asr <原片> [--out <目录>] [--prompt "专名,专名"]
      原片音轨 → 16 kHz 单声道 → faster-whisper large-v3-turbo（带逐词时间）+ medium 两遍，打印分句和起止；写 <目录>/asr.json（turbo）。
      用两遍对照专名 / 同音（“钓鱼执法 / 钓鱼之法”“ChatGPT / 拆GPT”）；末尾的“好好好”之类是 ASR 幻觉（其实是静音 / 杂音），成片截到最后一句 + 0.8 s。
  python own_voice.py build <本条目录> <lines.json> --video <原片> [--start 0.20] [--tail 0.8]
      lines.json = [{"id": "N01", "s": 0.43, "e": 5.09, "zh": "字幕（照他说的，只改 ASR 听错的专名）", "say": "（可省，默认同 zh）", "en": "英文字幕（忠实直译）"}, …]（s / e = 原片时间）
      写：制作/02_配音/edit/tts_narration.wav（原片音轨，48 kHz 立体声，从 start 起）、edit/tts_edit.json（每句 s / e = 原片时间 − start）、
          台本/录制稿.json 的 lines（保留 hook / kicker / slug）、台本/plan.json 每句的 a（= 他实际的停顿，场景 dur 写 0.5）、制作/00_整片/common.py 的 NATURAL_TIMING = True、
          制作/00_整片/face.json（不存在才写：原片路径 + start，脸的裁切 / 大小用默认值，要看过画面再调）。
  之后：build_timeline → check_subs → prep_frames → mix_audio → render_all → 把 整片_v1.mp4 改名成 整片_v1_cards无小窗.mp4 → compose_face.py → qa_mix → finish（references/face-window.md）。

**字幕内容一字不改**（用户 2026-10-06：“不要修改任何内容”）：只改 ASR 听错的专名 / 同音字；观点句（对公司态度的判断、没出处的比较）风险写进交付说明，不改稿、不替他润色。
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def asr(video, out, prompt):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    wav = out / "voice16k.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    from faster_whisper import WhisperModel
    init = "Claude，Anthropic，GPT，ChatGPT，IP，app，" + (prompt or "")
    res = {}
    for name in ("large-v3-turbo", "medium"):
        m = WhisperModel(name, device="cpu", compute_type="int8")
        segs, info = m.transcribe(str(wav), language="zh", word_timestamps=(name != "medium"), vad_filter=True, initial_prompt=init)
        rows = [{"s": round(s.start, 2), "e": round(s.end, 2), "text": s.text.strip(),
                 "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)} for w in (s.words or [])]} for s in segs]
        res[name] = rows
        print(f"── {name}（时长 {info.duration:.1f} s）")
        for r in rows:
            print(f'{r["s"]:7.2f} {r["e"]:7.2f}  {r["text"]}')
    (out / "asr.json").write_text(json.dumps(res["large-v3-turbo"], ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "asr_medium.json").write_text(json.dumps(res["medium"], ensure_ascii=False, indent=1), encoding="utf-8")


def build(ep, lines_file, video, start, tail):
    ep = Path(ep)
    lines = json.loads(Path(lines_file).read_text(encoding="utf-8"))
    end = max(l["e"] for l in lines) + tail
    ed = ep / "制作" / "02_配音" / "edit"
    ed.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start}", "-to", f"{end + 0.2}", "-i", video, "-vn", "-ac", "2", "-ar", "48000", str(ed / "tts_narration.wav")], check=True)
    edit = {"total": round(end - start, 3), "lines": [
        {"id": l["id"], "zh": l["zh"], "take": "user_voice", "src": [round(l["s"] - start, 3), round(l["e"] - start, 3)],
         "n0": round(l["s"] - start - 0.1, 3), "n1": round(l["e"] - start + 0.1, 3), "s": round(l["s"] - start, 3), "e": round(l["e"] - start, 3), "gain_db": 0.0} for l in lines]}
    (ed / "tts_edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=2), encoding="utf-8")
    rec_f = ep / "台本" / "录制稿.json"
    rec = json.loads(rec_f.read_text(encoding="utf-8")) if rec_f.exists() else {}
    rec["lines"] = [{"id": l["id"], "zh": l["zh"], "say": l.get("say") or l["zh"], "en": l["en"]} for l in lines]
    rec_f.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    plan_f = ep / "台本" / "plan.json"
    if plan_f.exists():
        plan = json.loads(plan_f.read_text(encoding="utf-8"))
        nat = {l["id"]: (l["s"] - start, l["e"] - start) for l in lines}
        prev_end = 0.0
        for sc in plan["plan"]:
            sc["dur"] = 0.5
            for ln in sc.get("lines", []):
                ln["a"] = round(nat[ln["id"]][0] - prev_end, 3)
            prev_end = nat[sc["lines"][-1]["id"]][1]
        plan_f.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    cm = ep / "制作" / "00_整片" / "common.py"
    s = cm.read_text(encoding="utf-8")
    if re.search(r"^NATURAL_TIMING\s*=", s, re.M):
        s = re.sub(r"^NATURAL_TIMING\s*=\s*\w+", "NATURAL_TIMING = True", s, flags=re.M)
    else:
        s += "\nNATURAL_TIMING = True                      # 悠一原声版：保持自然停顿（build_timeline.py 读）\n"
    cm.write_text(s, encoding="utf-8")
    ff = ep / "制作" / "00_整片" / "face.json"
    if not ff.exists():
        ff.write_text(json.dumps({"src": video.replace("\\", "/"), "start": start, "duration": round(end - start, 2), "mirror": True,
                                  "crop": {"cx": 0.515, "cy": 0.449, "side": 0.787}, "size": 360, "sticker": "悠一 出镜"}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"总长 {end - start:.2f} s；{len(lines)} 句；narration / tts_edit / 录制稿 / plan(a) / NATURAL_TIMING / face.json 已写。下一步 build_timeline.py。")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("asr")
    a.add_argument("video")
    a.add_argument("--out", default=".")
    a.add_argument("--prompt", default="")
    b = sub.add_parser("build")
    b.add_argument("ep")
    b.add_argument("lines")
    b.add_argument("--video", required=True)
    b.add_argument("--start", type=float, default=0.20)
    b.add_argument("--tail", type=float, default=0.8)
    x = ap.parse_args()
    if x.cmd == "asr":
        asr(x.video, x.out, x.prompt)
    else:
        build(x.ep, x.lines, x.video, x.start, x.tail)
