"""单帧检查：python test_vis.py 名字 时间秒 ...  → 输出到 _check/ 里的 PNG"""
import sys
from pathlib import Path
import vis
from vis import *
OUT = Path(__file__).parent / "_check"; OUT.mkdir(exist_ok=True)
G = {
 "atlas": lambda: gen_image_push(MAT / "角色图集" / "总览.png", 7, 1.0, 1.4, 0.3, 0.3, "游戏素材 / 角色图集 / 总览.png", pixel=True),
 "reel": lambda: gen_atlas_reel(8),
 "layers": lambda: gen_layers_stack(9),
 "audio": lambda: gen_list_scroll(6),
 "table": lambda: gen_storyboard_table(10),
 "s02": lambda: gen_image_push(MAT / "剧情分镜" / "分镜图" / "s02_shinpachi.png", 8, 1.0, 1.5, 0.5, 0.35, "剧情分镜 / 分镜图 / s02_shinpachi.png"),
 "s13md": lambda: gen_text_scroll(GAME / "docs" / "章节素材调研" / "s13.md", 12, 1, 140, "docs/章节素材调研/s13.md", "逐个镜头研究原片"),
 "ch1js": lambda: gen_code_scroll(GAME / "story" / "chapter1.js", 14, 380, 428, "story/chapter1.js", "await S.say(…)", highlight=(392, 394)),
 "ch2js": lambda: gen_code_scroll(GAME / "story" / "chapter2.js", 10, 900, 960, "story/chapter2.js", "S.say / S.walk / S.fight"),
 "tree": lambda: gen_tree(6),
 "result": lambda: gen_results_card(4),
 "ph": lambda: gen_placeholder("S01 冷开场", "9 月 25 号那条视频 → 15 章游戏", 58),
 "end": lambda: gen_end_card(4),
}
name = sys.argv[1]
n, fr = G[name]()
for t in sys.argv[2:]:
    i = min(n - 1, int(float(t) * FPS))
    fr(i).save(OUT / f"{name}_{float(t):05.2f}.png"); print(OUT / f"{name}_{float(t):05.2f}.png")
