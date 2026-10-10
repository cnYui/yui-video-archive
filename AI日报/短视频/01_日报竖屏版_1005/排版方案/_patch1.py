p = "make_daily_layouts.py"
s = open(p, encoding="utf-8").read()

# 1) 空贴纸不画
s = s.replace(".frame .inner { position:relative;", ".frame[data-tag='']::after, .frame:not([data-tag])::after { display:none; }\n.frame .inner { position:relative;")

# 2) 自动换行
s = s.replace("def text_lines(d, x, y, lines, font, fill, gap=8):", '''NOSTART = "，。、；：！？）」』”’,.;:!?)"


def wrap(text, font, maxw):
    lines, cur = [], ""
    for ch in text:
        if cur and font.getlength(cur + ch) > maxw and ch not in NOSTART:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def text_lines(d, x, y, lines, font, fill, gap=8):''')

# 3) 总览的说明文字重写
start = s.index("    cards = [\n        (R / \"L1_kol_ink.png\"")
end = s.index("    sheet.save(HERE / \"排版总览.png\")")
new = '''    cards = [
        (R / "L1_kol_ink.png", "① 素材主导 · 标准竖版",
         "照短视频技能的版式 B：标题在上，来源截图进边框 6 当主角，字幕在下，下面一张数字卡 / 要点卡，鲸鱼娘站在卡片旁。",
         "优点：和你其它短视频最像；来源截图最大最清楚。", "取舍：日报手写白板的味道没了，鲸鱼娘最小。", "背景示例：墨色印花"),
        (R / "L2_kol_color.png", "② 白板主导 · 竖版白板",
         "保留日报的手写白板：手写标题、手写要点、黄圈标重点、胶带贴来源截图；整块白板套边框 6，鲸鱼娘站在白板左下角。",
         "优点：和长视频一脉相承，辨识度最高。", "取舍：字最多，来源截图最小；手写要逐笔动画。", "背景示例：原色印花"),
        (R / "L3_kol_orange.png", "③ 角色主导 · 鲸鱼娘说话",
         "鲸鱼娘放大到 384 px，要点做成对话气泡，一次只冒一条；来源截图缩成上面一个框。",
         "优点：最像“有人在讲”，画面最干净。", "取舍：来源截图缩小；气泡要点要做进出动画。", "背景示例：橙色印花"),
        (R / "L0_cover_ink.png", "第 0 帧 · 封面不动",
         "封面保持日报原来的样子（16:9 原图），只居中放进竖屏，套同款边框和背景；三种排版都一样。",
         "视频号只能选视频里的帧，所以第 0 帧就是这张。", "封面文件一个像素都不改。", "—"),
    ]
    gap = (W - 80 - 4 * (PW + 16)) // 3
    sheet = Image.new("RGB", (W, 1500), PAPER)
    d = ImageDraw.Draw(sheet)
    d.text((40, 34), "日报 → 竖屏短视频：三种排版（10/5 这期）", font=F(52, 400), fill=INK)
    d.text((40, 108), "同一条新闻（Kolibri）、同一句字幕、同一套规格：1080×2340 · 版式 B 安全区 · 边框 6 · 中英双语字幕 52 / 30 px", font=F(25, 400), fill=GRAY)
    d.text((40, 144), "背景印花三选一随机 · BGM 垫底 · 不加片头片尾　　浅灰块 = 平台遮挡区（顶栏 / 账号名文案 / 右侧按钮），重要的字都避开了", font=F(25, 400), fill=GRAY)
    x = 40
    top = 200
    fd, fb, fa = F(24, 400), F(34, 800), F(24, 700)
    maxy = 0
    for png, title, desc, pro, con, bgnote in cards:
        ph = phone(png, PW, zones=True)
        sheet.paste(ph, (x, top), ph)
        y = top + ph.height + 22
        d.text((x, y), title, font=fb, fill=INK)
        y += 54
        y = text_lines(d, x, y, wrap(desc, fd, PW + 8), fd, (55, 65, 81), 6) + 6
        y = text_lines(d, x, y, wrap(pro, fa, PW + 8), fa, ACC, 6)
        y = text_lines(d, x, y, wrap(con, fd, PW + 8), fd, GRAY, 6)
        maxy = max(maxy, y)
        x += PW + 16 + gap
    sheet = sheet.crop((0, 0, W, maxy + 30))
'''
s = s[:start] + new + s[end:]
open(p, "w", encoding="utf-8").write(s)
print("patched")
