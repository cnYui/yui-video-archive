# -*- coding: utf-8 -*-
r"""新建一条短视频（竖屏 1080×2340）：目录骨架 + 引擎模板 + 台本骨架 + 配音脚本。

  python new_short.py --collection "Claude Code相关" --num 01 --name 短名 --layout dual|single
  python new_short.py --collection 独立视频 --name 短名 --layout single        （不写 --num 就用 YYYY-MM_ 开头，独立视频照这个命名）
  python new_short.py --root <任意目录> --num 01 --name 短名 --layout dual      （测试用）
  python new_short.py --collection Claude官方教程 --num 02 --name 短名_出镜版 --layout faceb      （悠一出镜多段口播 + 官方素材 + 说明卡，见 assets/oncam-multiclip/README.md）

放在哪（用户 2026-10-04：“在当前项目的所有不同分类的文件夹下，都新创建短视频和长视频两个文件夹，划分开来，素材可以公用”）：
  <合集>\短视频\NN_<短名>\        这一条：台本\、制作\00_整片\（引擎）、制作\02_配音\、制作\04_封面\
  <合集>\素材\<YYYY-MM_主题>\     素材放合集层，短、长视频共用（没有就新建）；common.py 的 SRC 指过去
--collection 写合集目录名：AI实操 / AI日报 / AI科普 / AI震惊瘫坐时代计算机研究生必须掌握的技能 / Claude Code相关 / OpenAI相关 / Way to AGI / 独立视频（不属于任何合集的放这）。

- dual   双分镜：一个长视频里挑两个不冲突的镜头（比如人脸 + 电脑操作），上下同时放，画外音把观点讲得更快更密（长视频二次剪辑）。
- single 单框：标题 + 一个素材框 + 大数字卡片（多来源的新闻短条，AI大圆镜 那种）。
- faceb  出镜多窗（2026-10-06 加，《Claude官方教程》第 1 期出镜版）：每个场景自己选窗口模式 one 单窗 / two 双窗上下叠 / big 大窗，悠一的镜像小窗跟着换位置；
         建条目时还会铺好多段口播的骨架（台本\talk_lines.py / script_data.py、制作\00_整片\scenes_ep.js、制作\01_口播\、face.json），NATURAL_TIMING = True，BGM 床 −11 dB。
"""
import argparse
import json
import random
import re
import shutil
import sys
from pathlib import Path

SK = Path(__file__).resolve().parents[1]
PROJECT = Path(r"D:\大疆")


def pick_background(want, eng):
    """背景印花（assets/backgrounds/pattern_*.png，不含 pattern_none）：不指定就随机挑一张，复制成 eng/bg.png，选择记在 eng/bg.json。"""
    lib = sorted(p for p in (SK / "assets" / "backgrounds").glob("pattern_*.png") if p.name != "pattern_none.png")
    if want == "none" or not lib:
        (eng / "bg.json").write_text(json.dumps({"file": None, "how": "none" if want == "none" else "背景库是空的"}, ensure_ascii=False), encoding="utf-8")
        return "无（只有米白底 + 点阵）"
    if want:
        src = SK / "assets" / "backgrounds" / want
        if src not in lib:
            sys.exit(f"背景库里没有 {want}，可选：{', '.join(p.name for p in lib)} / none")
        how = "指定"
    else:
        src, how = random.choice(lib), "随机"
    shutil.copy(src, eng / "bg.png")
    (eng / "bg.json").write_text(json.dumps({"file": src.name, "how": how, "pool": [p.name for p in lib]}, ensure_ascii=False), encoding="utf-8")
    return f"{src.name}（{how}）"


def scaffold_faceb(ep):
    """出镜多窗版（layout faceb）的整套骨架：多段口播 + 官方素材 + 说明卡（assets/oncam-multiclip/，流程见它的 README.md）。返回做了什么（给最后的提示用）。"""
    done = []
    kit = SK / "assets" / "oncam-multiclip" / "template"
    for rel in ("台本/talk_lines.py", "台本/script_data.py", "制作/00_整片/scenes_ep.js"):
        shutil.copy(kit / rel, ep / rel)
    (ep / "制作" / "01_口播").mkdir(exist_ok=True)
    eng = ep / "制作" / "00_整片"
    shutil.copy(SK / "assets" / "face-template" / "face.json", eng / "face.json")
    done.append("台本\\talk_lines.py / script_data.py、制作\\00_整片\\scenes_ep.js + face.json、制作\\01_口播\\ 已铺好")

    def patch(name, pat, repl, what):
        f = eng / name
        s, n = re.subn(pat, repl, f.read_text(encoding="utf-8"), count=1, flags=re.M)
        if n:
            f.write_text(s, encoding="utf-8")
            done.append(what)
        else:
            done.append(f"⚠ {name} 里没找到 {what} 要改的那一行（模板改过？手工改）")

    patch("common.py", r"^NATURAL_TIMING\s*=\s*\w+", "NATURAL_TIMING = True", "common.py NATURAL_TIMING = True（原声：不按句切块、不加句间停顿）")
    patch("index.html", r'<script src="scenes\.js"></script>', '<script src="scenes.js"></script>\n<script src="scenes_ep.js"></script>', "index.html 加载 scenes_ep.js")
    patch("mix_audio.py", r"(NARR_LUFS, FOOT_LUFS, BGM_BED, BGM_DUCK, VOICE_DUCK_DB = -16\.0, -21\.0, )-16\.0(, 1\.0, -9\.0)", r"\g<1>-11.0\g<2>", "mix_audio.py BGM 床 −11 dB（长口播别再抬高）")
    patch("mix_audio.py", r"^BGM_SWELL_DB = 5\.0", "BGM_SWELL_DB = 0.0", "mix_audio.py BGM_SWELL_DB = 0（句间停顿只有 0.2–0.5 s，抬了会一抽一抽）")
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--num", help="期号（NN）；不写就用当月 YYYY-MM 当前缀（独立视频的命名）")
    ap.add_argument("--name", required=True)
    ap.add_argument("--layout", required=True, choices=["dual", "single", "faceb"])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--collection", help="合集目录名，例：Claude Code相关、独立视频")
    g.add_argument("--root", help="直接指定放短视频的目录（测试用）")
    ap.add_argument("--bg", help="背景印花：assets/backgrounds/ 里的文件名；不写就随机挑一张（用户 2026-10-04：每一期随机挑一张）；none = 不用印花")
    a = ap.parse_args()
    if a.bg and a.bg != "none" and not (SK / "assets" / "backgrounds" / a.bg).is_file():   # 先查，别建了一半目录才报错
        lib = sorted(p.name for p in (SK / "assets" / "backgrounds").glob("pattern_*.png") if p.name != "pattern_none.png")
        sys.exit(f"背景库里没有 {a.bg}，可选：{', '.join(lib)} / none")
    if a.collection:
        coll = PROJECT / a.collection
        if not (coll / "短视频").is_dir():
            sys.exit(f"{coll}\\短视频 不存在：合集名写错了？（各合集下都有 短视频\\ 和 长视频\\）")
        root = coll / "短视频"
    else:
        root = Path(a.root)
        root.mkdir(parents=True, exist_ok=True)
    ep = root / f"{a.num or __import__('datetime').date.today().strftime('%Y-%m')}_{a.name}"
    if ep.exists():
        sys.exit(f"{ep} 已经存在，不动")
    for d in ("台本", "制作/00_整片", "制作/02_配音/tts/seg_raw", "制作/02_配音/edit", "制作/04_封面"):
        (ep / d).mkdir(parents=True)
    mat = ep.parents[1] / "素材"
    mat.mkdir(exist_ok=True)
    for f in (SK / "assets" / "engine-template").iterdir():
        if f.is_file() and ".bak" not in f.name:            # 只拷模板文件：子目录、备份（*.bak*）不拷
            shutil.copy(f, ep / "制作" / "00_整片" / f.name)
    for f in (SK / "assets" / "voice-template").iterdir():
        shutil.copy(f, ep / "制作" / "02_配音" / f.name)
    shutil.copy(SK / "assets" / "script-template" / "录制稿.json", ep / "台本" / "录制稿.json")
    shutil.copy(SK / "assets" / "script-template" / f"plan.{a.layout}.json", ep / "台本" / "plan.json")
    shutil.copy(SK / "assets" / "cover-template" / "cover.json", ep / "制作" / "04_封面" / "cover.json")
    shutil.copy(SK / "assets" / "cover-template" / "candidates_framed.json", ep / "制作" / "04_封面" / "candidates_framed.json")      # 交付包：封面 3×3（框版，2026-10-05 起统一样式）
    shutil.copy(SK / "assets" / "publish-template" / "投稿信息.json", ep / "投稿信息.json")                          # 交付包：标题 3×3 + 各平台字段
    bg = pick_background(a.bg, ep / "制作" / "00_整片")
    print(f"已建 {ep}（{a.layout}，背景 {bg}）；素材放 {mat}\\<YYYY-MM_主题>\\（短、长视频共用）")
    if a.layout == "faceb":
        for line in scaffold_faceb(ep):
            print("  ·", line)
        print("下一步（出镜多段流水线，assets/oncam-multiclip/README.md；每一步脚本都在 scripts/，参数是 <本条目录>）：\n"
              "  0) 先问用户：顶上两行字（hook，每一帧都在，第一张静帧就单独给他看）、封面（Claude / Anthropic 内容放官方吉祥物）、小红书原创声明开 / 关；ListAgents + ls -t docs/ai/context；\n"
              "  1) asr_clips.py <素材\\出镜_ASR> <原片…> --prompt \"专名，…\" → 写 台本\\talk_lines.py（CLIPS / ASR_DIR / ASR_NAME / CROP / CUTS / LINES）→ build_talk.py resolve | plan | media | concat <本条>；\n"
              "  2) 写 台本\\script_data.py（TITLE / LABEL / SCENES）→ gen_ep.py <本条> --timing 制作\\01_口播\\timing.json（看定格报告）；common.py 填 SRC / HAS_AUDIO；face.json 的 src 写 talk_face.mp4、crop {cx 0.5, cy 0.5, side 1.0}；\n"
              "  3) build_timeline.py → check_phrases.py → check_subs.py → prep_frames.py → scan_faces.py（官方课 / 访谈素材）→ audit_holds.py → render_all.py --stills-segs（全场景静帧逐张看）；\n"
              "  4) mix_audio.py → render_all.py（同一时间只跑一个渲染、BelowNormal）→ 整片_v1.mp4 改名 整片_v1_cards无小窗.mp4 → compose_face.py <本条> → check_face_sync.py → qa_mix.py → finish.py；\n"
              "  5) 交付包（封面 3×3 + 标题 3×3 + 顶上两行字 + 5 个要他耳朵确认的词）→ 用户同意 → cover_frame0.py（先把新成片拷成 _成片_无封面帧.mp4 备份）→ 发布。\n"
              "公开仓库：.gitignore 里已有 **/短视频/*/ 的通配规则，不用另补。")
        return
    print("下一步（细节在 SKILL.md 和 references/）：\n"
          "  1) 下素材（references/sources.md）→ 填 制作/00_整片/common.py 的 SRC / HAS_AUDIO；scripts/tsheet.py 看素材；\n"
          "  2) 事实核对（references/facts.md）→ 台本 录制稿.json（照 D:/大疆/docs/台本风格_AI大圆镜.md）+ plan.json；\n"
          "  3) build_timeline.py --est → check_subs.py → prep_frames.py → render_all.py --stills-segs（逐张看）；\n"
          "  4) 配音（references/voice.md）→ build_voice.py → 重跑 build_timeline / prep_frames → mix_audio → render_all → qa_mix → finish；\n"
          "  5) 交付包（成片一出就一次发给用户）：封面 3×3 = 填 制作/04_封面/candidates_framed.json → scripts/make_cover_framed.py <本条>（框版：白字 + 橙字黑描边、边框 6、黄贴纸；3 候选 × 3:4 / 16:9 / 4:3 + 候选总览.png）；\n"
          "     标题 3×3 = 写 投稿信息.json 的 titles（3 候选 × B 站 / 抖音 / 小红书）→ scripts/check_titles.py 核对限长；\n"
          "  6) 用户回“封面 X 标题 Y 同意”→ make_cover_framed.py <本条> --select X → cover_frame0.py → 发布（references/publish.md）。\n"
          "  （用户自己录口播 / 要出镜？不走 Fish：own_voice.py asr → build，渲完用 compose_face.py 叠镜像小窗，见 references/face-window.md；双框版小窗自动缩到下框左下角）\n"
          "公开仓库：.gitignore 里已有 **/短视频/*/ 的通配规则（渲染产物、配音原始文件、封面中间文件不收），不用另补。")


if __name__ == "__main__":
    main()
