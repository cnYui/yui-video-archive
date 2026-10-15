# -*- coding: utf-8 -*-
"""6 期的封面候选（交付包：3 候选 × 3 比例 = 9 张 + 候选总览）：用技能的 make_cover_framed.py（框版：白字 + 橙字黑描边、边框 6、黄贴纸、本期的背景印花）。

  python series_covers.py            6 期全做：生成底图 → 写 制作/04_封面/candidates_framed.json → 跑 make_cover_framed.py
  python series_covers.py 3          只做第 3 期

候选写法：src = ("photo", 照片路径, [x0, y0, x1, y1] 占整图的比例) 或 ("page", 页面 key, y0, y1（页面图像素）, [要画橙色高亮的英文句子…])；big = 两行大字（每行 ≤ 6 字，第 2 行橙色）；sticker ≤ 12 字。
封面协定（用户）：大字简短、不放最下面那行小字；平台标题写详细、和封面不写同一句；主角放大、版面简洁。人像取安静的帧（作者照：闭嘴、正对镜头）。
配图提醒：Substack 封面 Midjourney 派对图（亮片裙的年轻女性）不做封面（平台审核风险），只在成片里小范围出现。
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import series_data as D  # noqa: E402
from gen_episode import ep_dir  # noqa: E402

SK = Path(r"D:\大疆\短视频\skill\short-video")
FACE = D.MAT / "图片" / "Substack作者照_1101x1030.jpg"
BANNER = D.MAT / "图片" / "X横幅_1500x500.jpg"
PAGES = D.MAT / "页面"
FACE_CROP = [0.12, 0.0, 0.88, 0.80]                  # 作者照：头 + 肩（竖一点的框，脸占满）

COVERS = {
    1: [
        dict(id="A", note="作者照 + “35岁分水岭”（推荐：人像最稳）", recommend=True, src=("photo", FACE, FACE_CROP), big=["35岁", "分水岭"], sticker="简介自称10亿阅读"),
        dict(id="B", note="第 1 条标题截图 + “别等35岁才后悔”", src=("page", "A_1", 40, 1000, ["When you turn 35 you'll see the difference"]), big=["别等35岁", "才后悔"], sticker="Substack 原文"),
        dict(id="C", note="文章标题 + 点赞数截图 + “10亿阅读作家的忠告”", src=("page", "A_top", 40, 760, ["I'm 38. If You're in Your 20's or 30's, Read This."]), big=["10亿阅读", "作家忠告"], sticker="36 条忠告"),
    ],
    2: [
        dict(id="A", note="作者照 + “你拿的是一把小刀”", recommend=True, src=("photo", FACE, FACE_CROP), big=["你拿的是", "一把小刀"], sticker="简介自称10亿阅读"),
        dict(id="B", note="第 3 条标题截图 + “人好不够，要有本事”", src=("page", "A_3", 40, 1000, ["Chasing obsession is the fastest way to become a high performer"]), big=["人好不够", "要有本事"], sticker="第 3 条 · 执念"),
        dict(id="C", note="第 12 条“疯子”标题截图 + “每天评论14小时”", src=("page", "A_12", 40, 1000, ["Maniacs are incredible"]), big=["每天评论", "14小时"], sticker="第 12 条"),
    ],
    3: [
        dict(id="A", note="作者照 + “别爬公司梯子”", recommend=True, src=("photo", FACE, FACE_CROP), big=["别爬", "公司梯子"], sticker="简介自称10亿阅读"),
        dict(id="B", note="第 9 条标题截图 + “爬上去没一个开心”", src=("page", "A_9", 40, 1000, ["No one who climbs the corporate ladder is happy"]), big=["爬上去", "没一个开心"], sticker="第 9 条 · 梯子"),
        dict(id="C", note="第 34 条标题截图 + “公司是托儿所”", src=("page", "A_34", 40, 1000, ["Most workplaces are adult daycare centers"]), big=["公司是", "成年人托儿所"], sticker="第 34 条"),
    ],
    4: [
        dict(id="A", note="作者照 + “别装清高”", recommend=True, src=("photo", FACE, FACE_CROP), big=["别装", "清高"], sticker="简介自称10亿阅读"),
        dict(id="B", note="第 16 条正文截图 + “说不为钱多半自欺”", src=("page", "A_16", 40, 1000, ["People who think they don't pursue their goal for money are delusional"]), big=["不为钱", "多半自欺"], sticker="第 16 条 · 钱"),
        dict(id="C", note="“1000 变 12 万”那句原文截图 + 泼冷水钩子", src=("page", "A_17", 700, 1500, ["Last year I took $1000 and turned it into $120K"]), big=["千元变", "12万？"], sticker="文里没写方法"),
    ],
    5: [
        dict(id="A", note="作者照 + “朋友会换，父母不等”", recommend=True, src=("photo", FACE, FACE_CROP), big=["朋友会换", "父母不等"], sticker="简介自称10亿阅读"),
        dict(id="B", note="第 7 条“40 岁还想过 20 岁日子”截图", src=("page", "A_7", 600, 1360, ["40 year olds still trying to live like 20 year olds"]), big=["40岁还在", "夜店？"], sticker="第 7 条 · 朋友"),
        dict(id="C", note="第 29 条“多陪父母”原文截图", src=("page", "A_29", 0, 2000, ["Spend more time with your parents than feels normal"]), big=["多陪父母", "时间不多"], sticker="第 29 条"),
    ],
    6: [
        dict(id="A", note="作者照 + “别说我很忙”", recommend=True, src=("photo", FACE, FACE_CROP), big=["别说", "“我很忙”"], sticker="简介自称10亿阅读"),
        dict(id="B", note="第 13 条标题截图 + “忙是低地位”", src=("page", "A_13", 40, 1000, ["Avoid being busy"]), big=["忙", "是低地位"], sticker="第 13 条 · 忙"),
        dict(id="C", note="Tim 的 X 横幅（日落冲浪）+ “空出来的时间值钱”", src=("photo", BANNER, [0.0, 0.0, 1.0, 1.0]), big=["空出来的", "时间值钱"], sticker="X 横幅"),
    ],
}


CN = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六"}


def cover_text(n):
    """用户 2026-10-05 夜：封面大字统一成系列字样“2800万浏览 推特万字长文解读(一)”（第 1 期他给的原话），具体内容放平台标题里；其余 5 期套同一个格式只换序号。三行：第三行（序号）橙色。"""
    return ["2800万浏览", "推特万字长文", f"解读({CN[n]})"]


def page_src(key, y0, y1, needles, out):
    meta = json.loads((PAGES / "pages.json").read_text(encoding="utf-8"))[key]
    im = Image.open(PAGES / f"{key}.png").convert("RGB")
    dr = ImageDraw.Draw(im, "RGBA")
    for nd in needles:
        for x, y, w, h in meta["marks"][nd]:
            dr.rectangle([x - 8, y - 6, x + w + 8, y + h + 6], fill=(255, 106, 43, 96), outline=(255, 79, 26, 255), width=5)
    im.crop((0, y0, im.width, min(im.height, y1))).save(out)


def main():
    nums = [int(a) for a in sys.argv[1:]] or sorted(COVERS)
    for n in nums:
        ep = next(e for e in D.EPISODES if e["num"] == n)
        d = ep_dir(ep) / "制作" / "04_封面"
        (d / "_src").mkdir(parents=True, exist_ok=True)
        cands = []
        for c in COVERS[n]:
            kind = c["src"][0]
            if kind == "photo":
                video, crop = str(c["src"][1]), c["src"][2]
            else:
                _, key, y0, y1, needles = c["src"]
                video = str(d / "_src" / f"页面_{c['id']}.png")
                page_src(key, y0, y1, needles, video)
                crop = [0, 0, 1, 1]
            cands.append({"id": c["id"], "note": c["note"], **({"recommend": True} if c.get("recommend") else {}), "video": video, "t": 0, "crop": crop, "big": cover_text(n), "accent_line": 2, "sticker": c["sticker"]})
        (d / "candidates_framed.json").write_text(json.dumps({"candidates": cands}, ensure_ascii=False, indent=1), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SK / "scripts" / "make_cover_framed.py"), str(ep_dir(ep))], capture_output=True, text=True, encoding="utf-8")
        print(f"第 {n} 期：" + (r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[-300:]))


if __name__ == "__main__":
    main()
