# -*- coding: utf-8 -*-
"""封面 A7：A6 把黑块里的“DevDay”换成“OpenAI”，其他不变。用户原话：“把DevDay修改为Openai，其他不变”。

  python make_cover_a7.py     # 出 封面_A7_*（“。。”）和 封面_A7_省略号_*（“……”）各 16:9 / 4:3

直接复用 make_cover_a6.make（只改黑块文字），版面、字号、照片、角色都和 A6 一样。
用户打的是“Openai”，这里写成官方的“OpenAI”（大写 AI）。
"""
import make_cover_a6 as a6
from make_cover3 import HERE

KICKER = "OpenAI"


def main():
    a6.KICKER = KICKER                       # a6.make 在调用时才读这个全局变量
    for name, tail in (("", "。。"), ("省略号_", "……")):
        for tag, c in a6.CFG.items():
            out = HERE / f"封面_A7_{name}{tag}.png"
            a6.make(tail=tail, **c).save(out)
            print(out.name)


if __name__ == "__main__":
    main()
