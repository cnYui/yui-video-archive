# -*- coding: utf-8 -*-
"""从 series_data.py 生成 / 刷新某一期：目录骨架（new_short.py）+ 引擎（engine_lib 快照 + scenes_lib.js + 本期叠加层）+ 台本 + 页面图 / 照片。

  python gen_episode.py 1            第 1 期（目录不存在就先 new_short.py 建，已有就只刷新 台本 / scenes.js / 页面图）
  python gen_episode.py all          6 期全做
  python gen_episode.py 1 --no-engine  不覆盖引擎文件（只刷新 台本 + scenes.js + 页面图）

每次都会覆盖：制作/00_整片/{index.html, engine.js, check_subs.py, build_timeline.py, mix_audio.py, scenes.js, common.py, pages.js, photos.js}、台本/{录制稿.json, plan.json, 台本.md}、制作/02_配音/say_lines.txt。
不会动：配音、渲染产物、封面、投稿信息.json。
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import series_data as D  # noqa: E402

LIB = HERE / "engine_lib"
ROOT = Path(r"D:\大疆\独立视频\短视频")
SK = Path(r"D:\大疆\短视频\skill\short-video")
IMG = D.MAT / "图片"
PHOTOS = {"face": IMG / "Substack作者照_1101x1030.jpg", "party": IMG / "Substack封面_Midjourney_1232x835.jpg", "banner": IMG / "X横幅_1500x500.jpg"}
ENGINE_FILES = ("index.html", "engine.js", "check_subs.py", "build_timeline.py", "mix_audio.py")


def q(s):
    return json.dumps(s, ensure_ascii=False)


def ep_dir(ep):
    return ROOT / f"2026-10_{ep['name']}"


def t_expr(line, phrase, off):
    return f"P({q(line)}, {q(phrase)}, {off})" if phrase else f"S({q(line)}) + {off}"


def scene_js(ep, sc):
    ids = [ln["id"] for ln in sc["lines"]]
    out = [f"// {sc['id']} {sc['name']}（{ids[0]}–{ids[-1]}）"]
    sh = sc["shot"]
    if sh["kind"] == "page":
        marks = ",\n".join(f"  [{q(m['needle'])}, {t_expr(m['line'], m['phrase'], m['off'])}, {q(m['zh'])}]" if m["zh"] else f"  [{q(m['needle'])}, {t_expr(m['line'], m['phrase'], m['off'])}]" for m in sh["marks"])
        opt = ", ".join(f"{k}: {json.dumps(v)}" for k, v in sh["opt"].items())
        out.append(f"pageShot({q(ids[0])}, {q(ids[-1])}, {q(sh['key'])}, [\n{marks},\n]" + (f", {{ {opt} }}" if opt else "") + ");")
    else:
        opt = ", ".join(f"{k}: {json.dumps(v)}" for k, v in sh["opt"].items())
        out.append(f"photoShot({q(sc['id'])}, {q(sh['key'])}" + (f", {{ {opt} }}" if opt else "") + ");")
    for b in sc["bigs"]:
        out.append(f"{{ const t = {t_expr(b['line'], b['phrase'], b['off'])}; big(t, t + {b['dur']}, {q(b['num'])}, {q(b['unit'])}, {q(b['desc'])}); }}")
    return "\n".join(out)


def md_table(ep):
    rows = []
    for sc in ep["scenes"]:
        sh = sc["shot"]
        rows.append(f"\n## {sc['id']} {sc['name']}（{sc['lines'][0]['id']}–{sc['lines'][-1]['id']}）\n")
        ui = sc["ui"]
        rows.append(f"- 画面：{'页面录屏 ' + sh['key'] if sh['kind'] == 'page' else '照片 ' + sh['key']}；贴纸“{ui['tag']}”；来源小字“{ui['credit']}”")
        if sh["kind"] == "page":
            for m in sh["marks"]:
                rows.append(f"- 高亮（{m['line']}「{m['phrase'] or '句首'}」）：{m['needle']}" + (f" → 译文条“{m['zh']}”" if m["zh"] else ""))
        for b in sc["bigs"]:
            rows.append(f"- 大数字卡：{b['num']} {b['unit']}（{b['desc']}），{b['line']}「{b['phrase']}」起 {b['dur']} s")
        rows.append("\n| 句 | 字幕 zh | 配音 say | 英文 en |\n|---|---|---|---|")
        for ln in sc["lines"]:
            same = "（同 zh）" if ln["say"] == ln["zh"] else ln["say"]
            rows.append(f"| {ln['id']} | {ln['zh']} | {same} | {ln['en']} |")
    return "\n".join(rows)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_engine = "--no-engine" in sys.argv
    nums = [e["num"] for e in D.EPISODES] if args == ["all"] else [int(a) for a in args]
    for n in nums:
        ep = next(e for e in D.EPISODES if e["num"] == n)
        d = ep_dir(ep)
        if not d.exists():
            r = subprocess.run([sys.executable, str(SK / "scripts" / "new_short.py"), "--collection", "独立视频", "--name", ep["name"], "--layout", "single"], capture_output=True, text=True, encoding="utf-8")
            print(r.stdout.strip().splitlines()[0] if r.stdout else r.stderr)
            if r.returncode:
                sys.exit(r.stderr)
        eng = d / "制作" / "00_整片"
        # 引擎
        if not no_engine:
            for f in ENGINE_FILES:
                shutil.copy(LIB / f, eng / f)
        tpl_common = (SK / "assets" / "engine-template" / "common.py").read_text(encoding="utf-8")
        common = tpl_common.replace('XV = MAT / "<YYYY-MM_主题>"', 'XV = MAT / "2026-10_TimDenning38岁忠告"')
        assert common != tpl_common
        (eng / "common.py").write_text(common, encoding="utf-8")
        # 台本
        lines = [ln for sc in ep["scenes"] for ln in sc["lines"]]
        (d / "台本").mkdir(exist_ok=True)
        luzhi = {"slug": ep["slug"], "title": f"Tim Denning 忠告 {n}：{ep['name'].split('_', 1)[1]}", "kicker": ep["kicker"], "hook": ep["hook"],
                 "lines": [{k: v for k, v in ln.items()} for ln in lines]}
        (d / "台本" / "录制稿.json").write_text(json.dumps(luzhi, ensure_ascii=False, indent=1), encoding="utf-8")
        plan = []
        for i, sc in enumerate(ep["scenes"]):
            ui = {k: v for k, v in sc["ui"].items() if v}
            plan.append({"id": sc["id"], "type": "card", "kind": sc["shot"]["kind"], "overlay": "page", "name": sc["name"], "dur": 2.0, "ui": ui,
                         "lines": [{"id": ln["id"], "a": (0.1 if i == 0 else 0.15) if j == 0 else 0.0} for j, ln in enumerate(sc["lines"])]})
        (d / "台本" / "plan.json").write_text(json.dumps({"layout": "single", "plan": plan}, ensure_ascii=False, indent=1), encoding="utf-8")
        total_s = sum(D.est_dur(ln["say"]) + 0.12 for ln in lines)
        md = (f"# 台本：《Tim Denning 的 36 条忠告》第 {n} 期（{ep['name'].split('_', 1)[1]}）\n\n标题（一直挂在顶上）：{ep['hook'][0]} / {ep['hook'][1]}；kicker：{ep['kicker']}。"
              f"第三人称；声线「温柔男生」；中英双语字幕；1080×2340 单框。\n数据源：`独立视频\\短视频\\_TimDenning系列\\series_data.py`（改这里再 `gen_episode.py {n}`，别手改本文件）。\n"
              f"共 {len(lines)} 句、{len(ep['scenes'])} 个场景，估有声 {total_s:.0f} s。\n" + md_table(ep) + "\n")
        (d / "台本" / "台本.md").write_text(md, encoding="utf-8")
        (d / "制作" / "02_配音" / "say_lines.txt").write_text("\n".join(ln["say"] for ln in lines) + "\n", encoding="utf-8")
        # 页面图 / 照片
        meta = json.loads((D.MAT / "页面" / "pages.json").read_text(encoding="utf-8"))
        keys = sorted({sc["shot"]["key"] for sc in ep["scenes"] if sc["shot"]["kind"] == "page"})
        (eng / "media" / "pages").mkdir(parents=True, exist_ok=True)
        use = {}
        for k in keys:
            shutil.copy(D.MAT / "页面" / f"{k}.png", eng / "media" / "pages" / f"{k}.png")
            use[k] = dict(meta[k])
            if k == "X_t1":
                use[k]["url"] = D.TWEET_SHOW_URL
        (eng / "pages.json").write_text(json.dumps(use, ensure_ascii=False, indent=1), encoding="utf-8")
        (eng / "pages.js").write_text("window.PG = " + json.dumps(use, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
        pkeys = sorted({sc["shot"]["key"] for sc in ep["scenes"] if sc["shot"]["kind"] == "photo"})
        (eng / "media" / "photos").mkdir(parents=True, exist_ok=True)
        from PIL import Image
        ph = {}
        for k in pkeys:
            im = Image.open(PHOTOS[k])
            dst = eng / "media" / "photos" / f"{k}{PHOTOS[k].suffix}"
            shutil.copy(PHOTOS[k], dst)
            ph[k] = {"src": f"photos/{dst.name}", "w": im.width, "h": im.height}
        (eng / "photos.js").write_text("window.PH = " + json.dumps(ph, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
        # scenes.js = 库 + 本期叠加层
        body = "\n\n".join(scene_js(ep, sc) for sc in ep["scenes"])
        (eng / "scenes.js").write_text((LIB / "scenes_lib.js").read_text(encoding="utf-8") + "\n" + body + "\n", encoding="utf-8")
        print(f"第 {n} 期 → {d}：{len(lines)} 句、{len(ep['scenes'])} 个场景、页面图 {len(keys)} 张、照片 {len(pkeys)} 张")


if __name__ == "__main__":
    main()
