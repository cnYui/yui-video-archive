# -*- coding: utf-8 -*-
r"""悠一出镜口播：5 段 DJI 原片 → 剪好的“口播母带”（声音 + 脸）+ 每一行字幕在母带上的时间。

  python build_talk.py resolve     把 台本\talk_lines.py 里每一行的锚点对到逐词转写上，打印匹配到的原话和起止（先看一遍对不对）
  python build_talk.py plan        算要剪掉的停顿 / 口误，出 timing.json（每行在母带上的起止）、cuts.json、edit_report.md（不动视频）
  python build_talk.py media       按 cuts.json 出 talk.wav（48 kHz 立体声，样点精确）和 talk_face.mp4（脸，正方形裁切，30 fps，每段一次解码）

剪法（用户 2026-10-06：“再微调一下视频的节奏和字幕”）：只剪“停顿”和明确的口误，不改词序、不加速：
  - 在原声里按能量找静音段（< SIL_DB），静音段 > KEEP_MAX 的缩到 TARGET（句间稍长一点）；切点落在静音中间，所以不会切到字；
  - 口误 / 重说（CUTS）：切点吸附到附近能量最低处；
  - 所有切点对齐 30 fps 帧：视频按帧、声音按 1600 样点 / 帧同切，所以音画永远同步。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
sys.path.insert(0, str(EP / "台本"))
import talk_lines as TLN  # noqa: E402

FPS = 30
SPF = 1600                      # 48 kHz / 30 fps：每帧的样点数
SIL_DB = -48.0                  # 低于它算静音（他的麦克风有降噪，静音段在 −65 dB 以下，说话 −35 … −14 dB）
MIN_SIL = 0.28                  # 至少这么长的静音才当“停顿”
KEEP_MAX = 0.58                 # 停顿不超过它就原样留着（自然的气口）
MIN_CUT = 0.20                  # 能剪掉的不到这么长就不剪（为 0.1 s 打一个接点不值得）
TARGET_MID = 0.32               # 句内长停顿缩到这么长
TARGET_SENT = 0.40              # 句与句之间的长停顿缩到这么长
TARGET_BIG = 0.46               # 超过 1.4 s 的停顿（想事情）缩到这么长
PRE, POST = 0.12, 0.34          # 每段原片开头 / 结尾保留的静音
ASR = Path(TLN.ASR_DIR)


def norm(s):
    return re.sub(r"[\s，。？！：；、“”（）\-—·…,.?!:;'\"()⟨⟩]", "", s).lower()


def load_chars(key):
    rows = json.loads((ASR / TLN.ASR_NAME[key] / "asr.json").read_text(encoding="utf-8"))
    chars = []
    for r in rows:
        for w in r["words"]:
            cs = [c for c in w["w"] if norm(c)]
            for i, c in enumerate(cs):
                d = (w["e"] - w["s"]) / len(cs)
                chars.append((c.lower(), w["s"] + d * i, w["s"] + d * (i + 1)))
    return chars


def load_env(key):
    x, sr = sf.read(ASR / TLN.ASR_NAME[key] / "voice16k.wav")
    n = int(len(x) / (sr * 0.01))
    r = x[: n * int(sr * 0.01)].reshape(n, int(sr * 0.01))
    return 20 * np.log10(np.sqrt((r ** 2).mean(axis=1)) + 1e-9)       # 10 ms 一格的 dB


def resolve():
    chars = {k: load_chars(k) for k in TLN.CLIPS}
    text = {k: "".join(c[0] for c in chars[k]) for k in chars}
    env = {k: load_env(k) for k in TLN.CLIPS}
    raw, pos = [], {k: 0 for k in chars}
    for lid, clip, a, b, zh, en in TLN.LINES:
        T = text[clip]
        i = T.find(norm(a), pos[clip])
        assert i >= 0, f"{lid}: 找不到起点锚点「{a}」（从第 {pos[clip]} 个字起）"
        j = T.find(norm(b), i)
        assert j >= 0, f"{lid}: 找不到终点锚点「{b}」"
        j_end = j + len(norm(b))
        raw.append({"id": lid, "clip": clip, "w0": chars[clip][i][1], "w1": chars[clip][j_end - 1][2], "asr": T[i:j_end], "zh": zh, "en": en})
        pos[clip] = j_end
    # 用能量把起止修到真正的声音边界：转写的词边界常早 / 晚一点；但不越过相邻两行的词边界（连着说的两句话不会互相吃）
    out = []
    for n, l in enumerate(raw):
        e = env[l["clip"]]
        prev = raw[n - 1] if n and raw[n - 1]["clip"] == l["clip"] else None
        nxt = raw[n + 1] if n + 1 < len(raw) and raw[n + 1]["clip"] == l["clip"] else None
        lo = prev["w1"] if prev else 0.0
        hi = nxt["w0"] - 0.01 if nxt else len(e) / 100
        k0 = int(l["w0"] * 100)
        while k0 > 0 and e[k0 - 1] > SIL_DB and l["w0"] - k0 / 100 < 0.12 and k0 / 100 > lo + 0.01:
            k0 -= 1
        k1 = int(l["w1"] * 100)
        while k1 < len(e) - 1 and e[k1] > SIL_DB and k1 / 100 - l["w1"] < 0.4 and k1 / 100 < hi:
            k1 += 1
        out.append({"id": l["id"], "clip": l["clip"], "t0": round(k0 / 100, 2), "t1": round(k1 / 100, 2), "asr": l["asr"], "zh": l["zh"], "en": l["en"]})
    for p0, p1 in zip(out, out[1:]):                      # 相邻两行（同一段）的边界重叠时取中点
        if p0["clip"] == p1["clip"] and p0["t1"] > p1["t0"]:
            m = round((p0["t1"] + p1["t0"]) / 2, 2)
            p0["t1"] = p1["t0"] = m
    return out, env


def silence_runs(e, lo, hi):
    """[lo, hi]（秒）里的静音段 [(起, 止)]，秒。"""
    runs, start = [], None
    a, b = int(lo * 100), int(hi * 100)
    for k in range(a, b):
        if e[k] < SIL_DB:
            if start is None:
                start = k
        elif start is not None:
            if (k - start) / 100 >= MIN_SIL:
                runs.append((start / 100, k / 100))
            start = None
    if start is not None and (b - start) / 100 >= MIN_SIL:
        runs.append((start / 100, b / 100))
    return runs


def valley(e, t, half=0.08):
    """t 附近 ±half 秒里能量最低的 10 ms 格的时间。"""
    a, b = max(0, int((t - half) * 100)), min(len(e) - 1, int((t + half) * 100))
    k = a + int(np.argmin(e[a:b + 1]))
    return k / 100


def plan():
    lines, env = resolve()
    cuts, kept, dur = {}, {}, {}
    for key in TLN.CLIPS:
        e = env[key]
        mine = [l for l in lines if l["clip"] == key]
        K0 = max(0.0, mine[0]["t0"] - PRE)
        K1 = min(len(e) / 100, mine[-1]["t1"] + POST)
        cs = []
        # 1) 口误 / 重说：整段剪掉（切点吸附到静音谷）
        for ck, a, b in TLN.CUTS:
            if ck == key:
                cs.append((valley(e, a), valley(e, b), "口误"))
        # 2) 长停顿缩短
        for s0, s1 in silence_runs(e, K0, K1):
            d = s1 - s0
            if d <= KEEP_MAX:
                continue
            if any(min(b, s1) - max(a, s0) > 0.5 * d for a, b, _ in cs):
                continue
            sent = any(l["t1"] <= s1 + 0.2 and l["t1"] >= s0 - 0.2 for l in mine)       # 这段静音贴着一句话的结尾：句间停顿
            tgt = TARGET_BIG if d > 1.4 else (TARGET_SENT if sent else TARGET_MID)
            if d - tgt < MIN_CUT:
                continue
            cs.append((s0 + tgt / 2, s1 - tgt / 2, "停顿"))
        cs.sort()
        # 切点对齐帧（切掉的区间向内取整，保证切掉的是整数帧）
        fr = []
        for a, b, why in cs:
            fa, fb = int(np.ceil(a * FPS)), int(np.floor(b * FPS))
            if fb > fa:
                fr.append((fa, fb, why))
        fr.sort()
        f0, f1 = int(round(K0 * FPS)), int(round(K1 * FPS))
        ranges, cur = [], f0
        for fa, fb, why in fr:
            if fa > cur:
                ranges.append((cur, fa))
            cur = max(cur, fb)
        if f1 > cur:
            ranges.append((cur, f1))
        kept[key] = ranges
        cuts[key] = [(fa / FPS, fb / FPS, why) for fa, fb, why in fr]
        dur[key] = sum(b - a for a, b in ranges) / FPS
    # 母带时间轴：A → E 依次接起来
    base, tmap = 0, {}
    for key in TLN.CLIPS:
        tmap[key] = []
        for a, b in kept[key]:
            tmap[key].append((a, b, base))
            base += b - a
    total_f = base

    def to_new(key, t, side):
        f = t * FPS
        for a, b, n0 in tmap[key]:
            if a - 0.5 <= f <= b + 0.5:
                return (n0 + min(max(f, a), b) - a) / FPS
        # 落在被剪掉的区间里：取最近的保留点
        best = min(tmap[key], key=lambda r: min(abs(f - r[0]), abs(f - r[1])))
        a, b, n0 = best
        return (n0 + (a if abs(f - a) < abs(f - b) else b) - a) / FPS

    timing = {}
    for l in lines:
        s = to_new(l["clip"], l["t0"], "s")
        e = to_new(l["clip"], l["t1"], "e")
        timing[l["id"]] = [round(s, 3), round(e, 3)]
    raw = sum(len(env[k]) / 100 for k in TLN.CLIPS)
    (HERE / "cuts.json").write_text(json.dumps({"kept": kept, "map": tmap, "cuts": cuts, "total_frames": total_f}, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "lines_resolved.json").write_text(json.dumps(lines, ensure_ascii=False, indent=1), encoding="utf-8")
    # 报告
    rep = [f"# 口播剪辑报告", "", f"- 原片 5 段共 {raw:.1f} s（{raw / 60:.1f} 分钟），剪完母带 {total_f / FPS:.1f} s（{total_f / FPS / 60:.2f} 分钟），去掉 {raw - total_f / FPS:.1f} s。",
           f"- 只剪停顿和口误；不改词序、不加速。静音阈值 {SIL_DB} dB；> {KEEP_MAX} s 的停顿缩短（句内 {TARGET_MID} s、句间 {TARGET_SENT} s、> 1.4 s 的缩到 {TARGET_BIG} s）。", ""]
    names = {k: Path(v).name for k, v in TLN.CLIPS.items()}
    for key in TLN.CLIPS:
        c = cuts[key]
        rep.append(f"## {key}：{names[key]}（保留 {dur[key]:.1f} s，剪掉 {len(c)} 处共 {sum(b - a for a, b, _ in c):.1f} s）")
        for a, b, why in c:
            rep.append(f"- {a:7.2f}–{b:7.2f} s（{b - a:.2f} s）{why}")
        rep.append("")
    (HERE / "edit_report.md").write_text("\n".join(rep), encoding="utf-8")
    print(f"原片 {raw:.1f} s → 母带 {total_f / FPS:.1f} s，{len(lines)} 行；各段保留：" + "，".join(f"{k} {dur[k]:.1f}s" for k in dur))
    return lines


def media():
    cj = json.loads((HERE / "cuts.json").read_text(encoding="utf-8"))
    kept = cj["kept"]
    c = TLN.CROP
    # 声音：整段解码成 48 kHz 立体声，按帧切
    parts = []
    for key, path in TLN.CLIPS.items():
        wav = HERE / f"_a_{key}.wav"
        if not wav.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_f32le", str(wav)], check=True)
        x, sr = sf.read(wav, dtype="float32")
        assert sr == 48000
        fade = 96                                                  # 2 ms 淡入淡出，切点在静音里，只是保险
        for a, b in kept[key]:
            seg = x[a * SPF: b * SPF].copy()
            if len(seg) > 2 * fade:
                seg[:fade] *= np.linspace(0, 1, fade)[:, None]
                seg[-fade:] *= np.linspace(1, 0, fade)[:, None]
            parts.append(seg)
    audio = np.concatenate(parts)
    sf.write(HERE / "talk.wav", audio, 48000, subtype="FLOAT")
    print(f"talk.wav {len(audio) / 48000:.2f} s（{len(audio) // SPF} 帧）")
    # 脸：每段原片一次解码，select 出保留的帧
    for key, path in TLN.CLIPS.items():
        out = HERE / f"_face_{key}.mp4"
        sel = "+".join(f"between(n,{a},{b - 1})" for a, b in kept[key])
        crop = f"crop=w='ih*{c['side']}':h='ih*{c['side']}':x='iw*{c['cx']}-ih*{c['side']}/2':y='ih*{c['cy']}-ih*{c['side']}/2'"
        fs = HERE / f"_filter_{key}.txt"
        fs.write_text(f"[0:v]{crop},scale=720:720:flags=lanczos,fps={FPS},select='{sel}',setpts=N/({FPS}*TB),format=yuv420p[v]", encoding="utf-8")
        subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-threads", "4", "-i", path, "-filter_complex_script", str(fs), "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "14",
                          "-preset", "fast", "-g", "30", "-r", str(FPS), str(out)])
    print("5 路脸的编码已启动（后台），完成后用 python build_talk.py concat 拼成 talk_face.mp4")


def concat():
    lst = HERE / "_face_list.txt"
    lst.write_text("".join(f"file '_face_{k}.mp4'\n" for k in TLN.CLIPS), encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(HERE / "talk_face.mp4")], check=True)
    n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(HERE / "talk_face.mp4")],
                           capture_output=True, text=True).stdout.strip())
    cj = json.loads((HERE / "cuts.json").read_text(encoding="utf-8"))
    print(f"talk_face.mp4：{n} 帧（母带应有 {cj['total_frames']} 帧）")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "resolve"
    if cmd == "resolve":
        lines, _ = resolve()
        for l in lines:
            print(f'{l["id"]} {l["clip"]} {l["t0"]:7.2f}–{l["t1"]:7.2f}  {l["asr"]}')
    elif cmd == "plan":
        plan()
    elif cmd == "media":
        media()
    elif cmd == "concat":
        concat()
