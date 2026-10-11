# -*- coding: utf-8 -*-
"""comp.py —— 横版长视频的合成引擎（numpy 逐帧合成，2340×1080、60 帧）。

一条时间线 = 一堆 Item（画板 Panel / 精灵 Sprite / 自定义 Custom），每个 Item 有成片里的起止秒、z 序、入场出场动画；
render_frame(t) 从背景起按 z 序把 t 时刻在场的 Item 画上去。素材（Source）按“要什么尺寸给什么尺寸”取帧：
  VideoSrc  ffmpeg 管道解码（实机 / 原片 / 出镜轨），按显示尺寸直接缩好，一帧一帧顺序读
  ImageSrc  静图（铺满 / 包含 / 缓慢推近）
  GenSrc    PIL 画的活素材（gens.py：动作墙、视差街景、终端卡……）
画板的框（粗边 + 硬阴影）预先算成“稀疏像素表”，每帧只改边上那几万个像素，画板内容是整块内存拷贝，所以不慢。
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import ui
from ui import H, W, FPS

# ---------------------------------------------------------------- 动画曲线
def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def lerp(a, b, u):
    return a + (b - a) * u


# ---------------------------------------------------------------- 画板的框（稀疏像素表）
_KITS: dict = {}


class Kit:
    """某个尺寸 + 样式的画板框：阴影、粗边（稀疏）、四个圆角的内容遮罩。坐标相对内容矩形左上角。"""

    def __init__(self, w, h, r=22, bw=6, sh=(10, 10), sc=ui.ORANGE, ink=ui.INK):
        self.w, self.h, self.r, self.bw = w, h, r, bw
        shadow, ring, m = ui.frame_layers(w, h, r, bw, sh, sc, ink)
        self.m = m
        cs = r + 3
        self.cs = cs
        inner = np.zeros(shadow.size[::-1], bool)               # 一定会被内容盖住的“十字”区
        inner[m:m + h, m + cs:m + w - cs] = True
        inner[m + cs:m + h - cs, m:m + w] = True
        self.shadow = self._sparse(shadow, inner, m)
        self.ring = self._sparse(ring, np.zeros_like(inner), m)
        mask = np.asarray(ui.rr_mask(w, h, r), np.float32) / 255.0
        self.mask = {"tl": mask[:cs, :cs, None], "tr": mask[:cs, w - cs:, None], "bl": mask[h - cs:, :cs, None], "br": mask[h - cs:, w - cs:, None]}
        # 内容的左右上下各多出 m 的包围盒（画板连框带阴影）
        self.bbox = (-m, -m, w + m, h + m)

    @staticmethod
    def _sparse(img: Image.Image, skip, m):
        a = np.asarray(img)
        ys, xs = np.nonzero((a[..., 3] > 0) & ~skip)
        return (ys - m, xs - m, a[ys, xs, :3].astype(np.float32), (a[ys, xs, 3].astype(np.float32) / 255.0)[:, None])


def get_kit(w, h, style):
    key = (w, h, style.get("r", 22), style.get("bw", 6), tuple(style.get("sh", (10, 10))), style.get("sc", ui.ORANGE), style.get("ink", ui.INK))
    k = _KITS.get(key)
    if k is None:
        k = _KITS[key] = Kit(w, h, style.get("r", 22), style.get("bw", 6), tuple(style.get("sh", (10, 10))), style.get("sc", ui.ORANGE), style.get("ink", ui.INK))
    return k


def _blend_sparse(fr, sp, x, y):
    ys, xs, rgb, a = sp
    yy, xx = ys + y, xs + x
    ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
    if not ok.all():
        yy, xx, rgb, a = yy[ok], xx[ok], rgb[ok], a[ok]
    cur = fr[yy, xx].astype(np.float32)
    fr[yy, xx] = (cur + (rgb - cur) * a).astype(np.uint8)


def draw_panel(fr, content: np.ndarray, x: int, y: int, kit: Kit):
    """阴影 → 内容（圆角处还原背景）→ 粗边。content 是 (h, w, 3) uint8，已经是 kit 的尺寸。要整块在画布里。"""
    w, h, cs = kit.w, kit.h, kit.cs
    _blend_sparse(fr, kit.shadow, x, y)
    corners = {"tl": (y, x), "tr": (y, x + w - cs), "bl": (y + h - cs, x), "br": (y + h - cs, x + w - cs)}
    saved = {k: fr[v[0]:v[0] + cs, v[1]:v[1] + cs].copy() for k, v in corners.items()}
    fr[y:y + h, x:x + w] = content
    for k, (cy, cx) in corners.items():
        blk = fr[cy:cy + cs, cx:cx + cs].astype(np.float32)
        fr[cy:cy + cs, cx:cx + cs] = (saved[k] + (blk - saved[k]) * kit.mask[k]).astype(np.uint8)
    _blend_sparse(fr, kit.ring, x, y)


# ---------------------------------------------------------------- 精灵（RGBA）
class Sprite:
    def __init__(self, img: Image.Image):
        img = img.convert("RGBA")
        bb = img.getchannel("A").getbbox()
        self.ox, self.oy = (bb[0], bb[1]) if bb else (0, 0)
        if bb:
            img = img.crop(bb)
        a = np.asarray(img)
        self.rgb = a[..., :3].astype(np.float32)
        self.a = (a[..., 3:4].astype(np.float32)) / 255.0
        self.h, self.w = a.shape[:2]


def blit(fr, spr: Sprite, x: int, y: int, opacity: float = 1.0):
    x += spr.ox
    y += spr.oy
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + spr.w, W), min(y + spr.h, H)
    if x0 >= x1 or y0 >= y1 or opacity <= 0:
        return
    rgb = spr.rgb[y0 - y:y1 - y, x0 - x:x1 - x]
    a = spr.a[y0 - y:y1 - y, x0 - x:x1 - x] * opacity
    reg = fr[y0:y1, x0:x1].astype(np.float32)
    fr[y0:y1, x0:x1] = (reg + (rgb - reg) * a).astype(np.uint8)


# ---------------------------------------------------------------- 素材
def _fit_arr(im: np.ndarray, w: int, h: int, interp=cv2.INTER_AREA) -> np.ndarray:
    if im.shape[1] == w and im.shape[0] == h:
        return im
    return cv2.resize(im, (w, h), interpolation=interp)


class Source:
    def get(self, t: float, w: int, h: int) -> np.ndarray:        # t = 这块素材自己的秒数（从 0 起）
        raise NotImplementedError

    def close(self):
        pass


class ImageSrc(Source):
    """静图。fit = cover（铺满裁切）/ contain（完整放进去，底色 bg）；kb = (z0, z1, 持续秒) 缓慢推近。"""

    def __init__(self, img, fit="cover", cx=0.5, cy=0.5, pixel=False, bg=(255, 255, 255), kb=None):
        if isinstance(img, (str, Path)):
            img = Image.open(img)
        self.img = img.convert("RGB")
        self.arr = np.asarray(self.img)
        self.fit, self.cx, self.cy, self.pixel, self.bg, self.kb = fit, cx, cy, pixel, bg, kb
        self._cache: dict = {}

    def _view(self, w, h, z):
        sh, sw = self.arr.shape[:2]
        if self.fit == "cover":
            s = max(w / sw, h / sh) * z
            cw, ch = w / s, h / s
            x0 = clamp(self.cx * sw - cw / 2, 0, sw - cw)
            y0 = clamp(self.cy * sh - ch / 2, 0, sh - ch)
            return self.arr, (x0, y0, x0 + cw, y0 + ch)
        return self.arr, (0, 0, sw, sh)

    def get(self, t, w, h):
        z = 1.0
        if self.kb:
            z = lerp(self.kb[0], self.kb[1], smooth(t / self.kb[2]))
        key = (w, h, round(z, 3))
        if key in self._cache:
            return self._cache[key]
        arr, (x0, y0, x1, y1) = self._view(w, h, z)
        interp = cv2.INTER_NEAREST if self.pixel else (cv2.INTER_AREA if (x1 - x0) > w else cv2.INTER_LANCZOS4)
        if self.fit == "cover":
            M = np.float32([[w / (x1 - x0), 0, -x0 * w / (x1 - x0)], [0, h / (y1 - y0), -y0 * h / (y1 - y0)]])
            out = cv2.warpAffine(arr, M, (w, h), flags=interp, borderMode=cv2.BORDER_REPLICATE) if self.kb else \
                _fit_arr(np.ascontiguousarray(arr[int(round(y0)):int(round(y1)), int(round(x0)):int(round(x1))]), w, h, interp)
        else:
            out = np.empty((h, w, 3), np.uint8)
            out[:] = self.bg
            sh, sw = arr.shape[:2]
            s = min(w / sw, h / sh)
            nw, nh = max(1, round(sw * s)), max(1, round(sh * s))
            r = cv2.resize(arr, (nw, nh), interpolation=interp)
            out[(h - nh) // 2:(h - nh) // 2 + nh, (w - nw) // 2:(w - nw) // 2 + nw] = r
        if len(self._cache) > 40:
            self._cache.clear()
        self._cache[key] = out
        return out


class GenSrc(Source):
    """PIL 画的活素材：fn(t) → PIL RGB（尺寸 = native）；get 时缩放到要的尺寸。"""

    def __init__(self, fn, native=None, pixel=False):
        self.fn, self.native, self.pixel = fn, native, pixel
        self._last = (None, None)

    def get(self, t, w, h):
        k = round(t * FPS)
        if self._last[0] != k:
            self._last = (k, np.asarray(self.fn(k / FPS).convert("RGB")))
        return _fit_arr(self._last[1], w, h, cv2.INTER_NEAREST if self.pixel else cv2.INTER_AREA)


class VideoSrc(Source):
    """视频：从 start 秒起，按 speed 播，ffmpeg 管道按 (dw, dh) 解码成 60 帧恒定帧率；get 的尺寸不同就再缩一次。
    crop = (x0, y0, x1, y1) 占源画面的比例；flags = neighbor（像素画整数倍放大）/ lanczos / area。"""

    def __init__(self, path, start=0.0, speed=1.0, dec=(1152, 648), flags="neighbor", crop=None, hold_last=True, pre_vf=""):
        self.path, self.start, self.speed, self.dec, self.flags, self.crop, self.pre_vf = str(path), start, speed, dec, flags, crop, pre_vf
        self.proc = None
        self.cur = -1
        self.k0 = 0
        self.last = None

    def _open(self, t):
        self.close()
        ss = self.start + t * self.speed
        dw, dh = self.dec
        vf = []
        if self.pre_vf:
            vf.append(self.pre_vf)
        if self.crop:
            x0, y0, x1, y1 = self.crop
            vf.append("crop=iw*%g:ih*%g:iw*%g:ih*%g" % (x1 - x0, y1 - y0, x0, y0))
        if self.speed != 1.0:
            vf.append("setpts=PTS/%g" % self.speed)
        vf.append("fps=%d" % FPS)
        vf.append("scale=%d:%d:flags=%s" % (dw, dh, self.flags))
        cmd = ["ffmpeg", "-v", "error", "-nostdin", "-ss", "%.4f" % ss, "-i", self.path, "-an", "-vf", ",".join(vf), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=dw * dh * 3 * 4)
        self.k0 = int(round(t * FPS))
        self.cur = self.k0 - 1

    def get(self, t, w, h):
        k = int(round(t * FPS))
        dw, dh = self.dec
        if self.proc is None or k < self.cur or k - self.cur > 90:
            self._open(t)
        nb = dw * dh * 3
        while self.cur < k:
            buf = self.proc.stdout.read(nb) if self.proc else b""
            if len(buf) < nb:                       # 片子播完了：停在最后一帧
                self.cur = k
                break
            self.last = np.frombuffer(buf, np.uint8).reshape(dh, dw, 3)
            self.cur += 1
        if self.last is None:
            return np.zeros((h, w, 3), np.uint8)
        return _fit_arr(self.last, w, h, cv2.INTER_AREA)

    def close(self):
        if self.proc is not None:
            try:
                self.proc.stdout.close()
                self.proc.kill()
                self.proc.wait(timeout=5)
            except Exception:
                pass
            self.proc = None


class FaceSrc(VideoSrc):
    """出镜轨（和成片同一条时间轴的 face_tl.mp4）：按要的宽高比在 16:9 的画面里裁一块（人脸居中偏上），再缩到要的尺寸。
    t 是成片的秒数（不是素材自己的秒数）。"""

    def __init__(self, path, dec=(1152, 648), cx=0.5, cy=0.46):
        super().__init__(path, 0.0, 1.0, dec, "area")
        self.cx, self.cy = cx, cy

    def get(self, t, w, h):
        full = super().get(t, *self.dec)
        dw, dh = self.dec
        aspect = w / h
        cw = min(dw, int(round(dh * aspect)))
        ch = min(dh, int(round(cw / aspect)))
        x0 = int(clamp(self.cx * dw - cw / 2, 0, dw - cw))
        y0 = int(clamp(self.cy * dh - ch / 2, 0, dh - ch))
        view = full[y0:y0 + ch, x0:x0 + cw]
        return _fit_arr(np.ascontiguousarray(view), w, h, cv2.INTER_AREA)


# ---------------------------------------------------------------- Item
def _rect_at(rect, t):
    """rect = (x, y, w, h) 或 [(t, (x, y, w, h)), ...] 关键帧（smooth 插值）。"""
    if isinstance(rect, tuple):
        return rect
    if t <= rect[0][0]:
        return rect[0][1]
    for (ta, ra), (tb, rb) in zip(rect, rect[1:]):
        if t <= tb:
            u = smooth((t - ta) / (tb - ta)) if tb > ta else 1.0
            return tuple(int(round(lerp(a, b, u))) for a, b in zip(ra, rb))
    return rect[-1][1]


class Item:
    z = 0

    def __init__(self, t0, t1, z=0, enter=None, exit=None):
        self.t0, self.t1, self.z = t0, t1, z
        self.enter = enter          # ("fade", dur) 或 ("slide", dx, dy, dur)
        self.exit = exit

    def active(self, t):
        return self.t0 <= t < self.t1

    def anim(self, t):
        """→ (alpha, dx, dy)"""
        a, dx, dy = 1.0, 0, 0
        if self.enter:
            d = self.enter[-1]
            u = ease_out((t - self.t0) / d) if d > 0 else 1.0
            a = min(a, u)
            if self.enter[0] == "slide":
                dx, dy = int(round(self.enter[1] * (1 - u))), int(round(self.enter[2] * (1 - u)))
        if self.exit:
            d = self.exit[-1]
            u = ease_out((self.t1 - t) / d) if d > 0 else 1.0
            a = min(a, u)
            if self.exit[0] == "slide":
                dx, dy = dx + int(round(self.exit[1] * (1 - u))), dy + int(round(self.exit[2] * (1 - u)))
        return a, dx, dy

    def bbox(self, t):
        raise NotImplementedError

    def paint(self, fr, t, dx, dy):
        raise NotImplementedError

    def draw(self, fr, t):
        a, dx, dy = self.anim(t)
        if a <= 0.003:
            return
        if a >= 0.997:
            self.paint(fr, t, dx, dy)
            return
        x0, y0, x1, y1 = self.bbox(t)
        x0, y0, x1, y1 = max(x0 + dx, 0), max(y0 + dy, 0), min(x1 + dx, W), min(y1 + dy, H)
        if x0 >= x1 or y0 >= y1:
            return
        saved = fr[y0:y1, x0:x1].astype(np.float32)
        self.paint(fr, t, dx, dy)
        cur = fr[y0:y1, x0:x1].astype(np.float32)
        fr[y0:y1, x0:x1] = (saved + (cur - saved) * a).astype(np.uint8)

    def close(self):
        pass


class Panel(Item):
    """画板：内容 + 框版边框。rect 可以是关键帧；style 见 Kit；dim = 0–1 压暗；ring = [(ta, tb)] 橙色光环。"""

    def __init__(self, t0, t1, rect, src: Source, style=None, z=0, enter=("slide", 0, 40, 0.35), exit=("fade", 0.25), src_t0=None, dim=None, ring=None):
        super().__init__(t0, t1, z, enter, exit)
        self.rect, self.src, self.style = rect, src, style or {}
        self.src_t0 = t0 if src_t0 is None else src_t0     # 素材第 0 秒对应成片的哪一秒
        self.dim = dim
        self.ring = ring or []

    def bbox(self, t):
        x, y, w, h = _rect_at(self.rect, t)
        m = 22
        return (x - m, y - m, x + w + m, y + m + h)

    def paint(self, fr, t, dx, dy):
        x, y, w, h = _rect_at(self.rect, t)
        content = self.src.get(t - self.src_t0, w, h)
        if self.dim:
            dv = self.dim(t) if callable(self.dim) else self.dim
            if dv > 0:
                content = (content.astype(np.float32) * (1 - dv)).astype(np.uint8)
        kit = get_kit(w, h, self.style)
        draw_panel(fr, content, x + dx, y + dy, kit)
        for ta, tb in self.ring:
            if ta <= t < tb:
                u = min(ease_out((t - ta) / 0.2), ease_out((tb - t) / 0.2))
                g, m = ui.glow_ring((x, y, w, h), bw=7, r=self.style.get("r", 22))
                blit(fr, _sprite_cache(("glow", w, h, self.style.get("r", 22)), lambda: g), x + dx - m, y + dy - m, u)

    def close(self):
        self.src.close()


class SpriteItem(Item):
    """RGBA 精灵（PIL 图）。xy 是 (x, y)，或关键帧 [(t, (x, y)), ...]（smooth 插值）。子类可以覆盖 _sprite(t) 做动态精灵。"""

    def __init__(self, t0, t1, xy, img, z=10, enter=("fade", 0.2), exit=("fade", 0.2), opacity=1.0):
        super().__init__(t0, t1, z, enter, exit)
        self.xy, self.img, self.opacity = xy, img, opacity
        self._spr = None

    def _sprite(self, t):
        if self._spr is None:
            self._spr = Sprite(self.img)
        return self._spr

    def _xy(self, t):
        ks = self.xy
        if not isinstance(ks, list):
            return ks
        if t <= ks[0][0]:
            return ks[0][1]
        for (ta, pa), (tb, pb) in zip(ks, ks[1:]):
            if t <= tb:
                u = smooth((t - ta) / (tb - ta)) if tb > ta else 1.0
                return (int(round(lerp(pa[0], pb[0], u))), int(round(lerp(pa[1], pb[1], u))))
        return ks[-1][1]

    def bbox(self, t):
        s = self._sprite(t)
        x, y = self._xy(t)
        return (x + s.ox, y + s.oy, x + s.ox + s.w, y + s.oy + s.h)

    def paint(self, fr, t, dx, dy):
        s = self._sprite(t)
        x, y = self._xy(t)
        blit(fr, s, x + dx, y + dy, self.opacity)


class Custom(Item):
    """想怎么画怎么画：fn(fr, t) 直接改帧。bbox 给大一点也行（只在淡入淡出时用）。"""

    def __init__(self, t0, t1, fn, z=5, bbox=(0, 0, W, H), enter=None, exit=None):
        super().__init__(t0, t1, z, enter, exit)
        self.fn, self._bb = fn, bbox

    def bbox(self, t):
        return self._bb

    def paint(self, fr, t, dx, dy):
        self.fn(fr, t)


_SPR: dict = {}


def _sprite_cache(key, make):
    s = _SPR.get(key)
    if s is None:
        if len(_SPR) > 600:
            _SPR.clear()
        s = _SPR[key] = Sprite(make())
    return s


# ---------------------------------------------------------------- 时间线
class Timeline:
    def __init__(self, bg_path=None):
        self.items: list[Item] = []
        bg = ui.new_canvas(bg_path).convert("RGB")
        self.bg = np.asarray(bg).copy()
        self.dur = 0.0

    def add(self, item: Item):
        self.items.append(item)
        self.dur = max(self.dur, item.t1)
        return item

    def frame(self, t: float) -> np.ndarray:
        fr = self.bg.copy()
        act = [it for it in self.items if it.t0 - 1e-9 <= t < it.t1]
        act.sort(key=lambda it: it.z)
        for it in act:
            it.draw(fr, t)
        return fr

    def close(self):
        for it in self.items:
            it.close()
