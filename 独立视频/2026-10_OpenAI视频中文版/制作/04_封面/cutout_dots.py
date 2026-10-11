# -*- coding: utf-8 -*-
"""把 OpenAI 官方 dots 图（og_art_card_16x9.png，3840×2160，纯黑底）里的四只小角色抠出来，存成带透明的 PNG。

  python cutout_dots.py            # 出 素材/dots形象/官方/dots_四只_抠图.png（整个 素材/ 不进 git）+ 三张深浅底预览

只用官方原图，不重画。背景是 (0,0,0) 纯黑，角色 = 非黑：
  1. 形状：非黑（≥3）→ 闭运算 + 填洞（补上黑色贝雷帽毛料的缝）→ 只留最大一块（四只连在一起，被画面底边切平）；
  2. 彩色毛料的边缘按“黑底上的半透明”还原：像素 = α × 毛料色，α = 亮度 ÷ 里面毛料的亮度，颜色换成里面的毛料色
     （不这样做，边缘一圈暗毛会在浅色底上变成黑色毛边）；
  3. 贝雷帽、墨镜这类黑 / 灰色的地方不能按亮度算（本来就暗），直接用形状，边缘向里收 1 px 再柔化。
彩色 / 灰色按“里面毛料的饱和度”平滑过渡，所以贝雷帽和蓝色身体交界处不会断。
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "素材" / "dots形象" / "官方" / "og_art_card_16x9.png"
OUT = ROOT / "素材" / "dots形象" / "官方" / "dots_四只_抠图.png"
CROP = (700, 1400, 3250, 2158)             # 只取下面那排角色（上面的 dots 发光字不要）；最后 2 行是缩放时变暗的边，丢掉
PAD = 24                                   # 形态学运算前在四周补边（边缘复制），否则画面切平的底边会被吃掉几行


def smoothstep(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def nconv(x, w, sigma):
    """归一化卷积：只用权重 w 标出来的像素，把它们的平均值向外延伸。"""
    if x.ndim == 3:
        return np.dstack([nconv(x[..., i], w, sigma) for i in range(x.shape[2])])
    return ndi.gaussian_filter(x * w, sigma) / (ndi.gaussian_filter(w, sigma) + 1e-6)


def build():
    rgb = np.asarray(Image.open(SRC).convert("RGB").crop(CROP)).astype(np.float32)
    m = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    V = m / 255.0
    S = np.where(m > 0, (m - mn) / np.maximum(m, 1), 0.0)

    # 1. 形状
    core = np.pad(m >= 3, PAD, mode="edge")
    core = ndi.binary_closing(core, structure=np.ones((3, 3)), iterations=4)
    core = ndi.binary_fill_holes(core)
    lab, n = ndi.label(core)
    core = lab == (1 + int(np.argmax(ndi.sum(core, lab, range(1, n + 1)))))
    dist = ndi.distance_transform_edt(core)[PAD:-PAD, PAD:-PAD]
    core_p = core
    core = core[PAD:-PAD, PAD:-PAD]

    # 2. 彩色毛料边缘：α = 亮度 ÷ 里面的毛料亮度
    interior = (dist > 8).astype(np.float32)
    V_ref = np.maximum(nconv(V, interior, 9), 0.25)
    S_ref = nconv(S, interior, 9)
    C_ref = nconv(rgb, interior, 4)
    a_col = smoothstep(V / V_ref, 0.10, 0.70)
    near = ndi.binary_dilation(core_p, iterations=7)[PAD:-PAD, PAD:-PAD]   # 形状外面一圈细毛也算
    a_col = np.where(near, a_col, 0.0)

    # 3. 灰 / 黑色的地方：形状，向里收 1 px 再柔化
    inner = ndi.binary_erosion(np.pad(core, PAD, mode="edge"), structure=np.ones((3, 3)), iterations=1)[PAD:-PAD, PAD:-PAD]
    a_neu = np.clip((ndi.gaussian_filter(inner.astype(np.float32), 1.0) - 0.2) / 0.6, 0, 1)

    wcol = smoothstep(S_ref, 0.30, 0.55)
    alpha = np.where(dist > 8, 1.0, wcol * a_col + (1 - wcol) * a_neu)
    color = np.where((dist > 8)[..., None], rgb, wcol[..., None] * C_ref + (1 - wcol[..., None]) * rgb)
    out = np.dstack([np.clip(color, 0, 255), alpha * 255]).round().astype(np.uint8)
    res = Image.fromarray(out, "RGBA")
    box = res.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    return res.crop(box), box


def main():
    res, box = build()
    res.save(OUT)
    print("cutout", res.size, "bbox in crop", box, "->", OUT.name)
    for name, bg in (("light", (205, 220, 235)), ("dark", (14, 16, 22)), ("mid", (110, 120, 135))):
        canvas = Image.new("RGBA", res.size, bg + (255,))
        canvas.alpha_composite(res)
        canvas.convert("RGB").save(OUT.with_name(f"_preview_{name}.png"))


if __name__ == "__main__":
    main()
