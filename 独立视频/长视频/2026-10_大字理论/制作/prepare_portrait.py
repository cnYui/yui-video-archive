"""使用原片的真人形象，避免合成或改变用户面容。"""
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageEnhance
import onnxruntime as ort

ASSETS = Path(r"D:\大疆\独立视频\素材\2026-10_大字理论")
im = Image.open(ASSETS / "face_45.png").convert("RGB").crop((210, 0, 1690, 1080))
im = ImageEnhance.Color(im).enhance(1.12)
im = ImageEnhance.Contrast(im).enhance(1.04)
# 直接运行已有模型，避免当前 rembg 的 numba 与 numpy 版本冲突。
opts = ort.SessionOptions()
opts.intra_op_num_threads = 4
opts.inter_op_num_threads = 1
session = ort.InferenceSession(str(Path.home() / ".u2net/birefnet-general.onnx"),
    sess_options=opts, providers=["CPUExecutionProvider"])
arr = np.array(im.resize((1024, 1024), Image.Resampling.LANCZOS)).astype("float32")
arr /= max(float(arr.max()), 1e-6)
arr = (arr - np.array([0.485, 0.456, 0.406], dtype="float32")) / np.array([0.229, 0.224, 0.225], dtype="float32")
result = session.run(None, {session.get_inputs()[0].name: arr.transpose(2, 0, 1)[None]})[0][0, 0]
mask = 1 / (1 + np.exp(-np.clip(result, -50, 50)))
mask = (mask-mask.min()) / max(float(mask.max()-mask.min()), 1e-6)
cut = im.convert("RGBA")
cut.putalpha(Image.fromarray((mask*255).astype("uint8")).resize(im.size, Image.Resampling.LANCZOS))
alpha = np.array(cut.getchannel("A"))
n, labels, stats, _ = cv2.connectedComponentsWithStats((alpha > 32).astype("uint8"), 8)
if n > 2:
    keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    alpha = np.where(labels == keep, alpha, 0).astype("uint8")
    cut.putalpha(Image.fromarray(alpha))
cut = cut.crop(cut.getbbox())
cut.save(ASSETS / "portrait.png")
print("人像抠图完成", cut.size, flush=True)
