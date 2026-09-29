# -*- coding: utf-8 -*-
"""口播字幕条（按成片顺序）→ cues.json。每条：段号、录像编号、原录像里的起止秒、条内要剪掉的口癖、中文、英文。

每期重写下面的 c(...)：先跑 asr.py，再用 `python show_asr.py <编号> -w` 看逐词时间，一句一句核对后手写。
- 中文按实际说的话整理（去掉“就是”“那个”“这个这个”等口癖、说错重来的半句），不照搬台本；
- 英文逐句翻译，简短口语；名字写“悠一”，英文 Yui；
- s / e 是原录像里的秒数，说话前后别切到字（build_edit.py 会自动前后各多留 0.06 / 0.10 s）；
- skip=[(起, 止), ...]：条内要剪掉的口癖或重来的半句；
- cut=True：和上一条强制分开（上一条尾巴上有不要的字时用）；
- hold=(秒, 录像, 起点)：这条念完后停几秒不出人声（例如作品展示让片段原声出来），出镜画面用那段录像里没说话的镜头。
完整的例子见 Way to AGI 第 02 期：`D:\大疆\Way to AGI\02_如何使用Claude来低成本的生成视频\制作\02_出镜\make_cues.py`（131 条）。
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

C = []


def c(pid, clip, s, e, zh, en, skip=(), **kw):
    """kw：cut=True 强制和上一条分开；hold=(秒, 录像, 起点) 这条念完后停几秒（不出人声），出镜画面用那段录像里没说话的镜头。"""
    C.append({"pid": pid, "clip": clip, "s": s, "e": e, "zh": zh, "en": en, "skip": [list(x) for x in skip], **kw})


# ------------------------------------------------------------------ 例子（第 02 期开场，换成本期的）
c("N01", "0161", 0.58, 1.76, "Hello，大家好，我是悠一。", "Hello everyone, I'm Yui.")
c("N01", "0161", 4.42, 9.72, "这期视频来教大家，如何用 Opus 5.5 上手做第一个视频。", "Today I'll show you how to make your first video with Opus 5.5.")
c("N04", "0161", 48.60, 55.78, "官方的说法是：这是视觉和电脑操作最强的一个模型，", "Officially, it's the strongest model for vision and computer use,", skip=[(49.70, 52.36)])
c("N07", "0162", 10.58, 14.82, "从主剧情那么多集里面，去挑一些经典场景。", "picking classic scenes from the whole main storyline.", hold=(1.6, "0162", 31.95))
c("N08", "0162", 46.24, 49.04, "那 Claude 不是扩散模型，这些视频是怎么来的呢？", "So if Claude isn't a diffusion model, where do these videos come from?", cut=True)

if __name__ == "__main__":
    (HERE / "cues.json").write_text(json.dumps(C, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(C), "cues")
