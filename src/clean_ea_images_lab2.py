# -*- coding: utf-8 -*-
"""把实验二 EA 导出图做“白底黑线”打印化处理，去掉试用版水印和左上角图名。

原始导出保留在 model/images/lab2/raw/，交付图输出到 docs/model/lab2/。
不改变图的内容，只去水印/去底色，方便嵌进报告和 PDF。
"""
import os
import glob
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "model", "images", "lab2", "raw")
OUT = os.path.join(BASE, "docs", "model", "lab2")
os.makedirs(OUT, exist_ok=True)


def curve(x):
    if x <= 118:
        return 0
    if x >= 176:
        return 255
    return int((x - 118) * 255 / 58)


def clean(src):
    im = Image.open(src).convert("L")
    # 去掉 EA 顶部图名条
    white = Image.new("L", (im.width, 46), 255)
    im.paste(white, (0, 0))
    # 去掉外框
    im = im.crop((10, 10, im.width - 10, im.height - 10))
    # 浅色水印与浅填充 -> 白；深色文字与线 -> 黑
    im = im.point(curve)
    mask = im.point(lambda x: 255 if x < 250 else 0)
    bbox = mask.getbbox()
    if bbox:
        pad = 20
        im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                      min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))
    out = Image.new("L", (im.width + 24, im.height + 24), 255)
    out.paste(im, (12, 12))
    dst = os.path.join(OUT, os.path.basename(src))
    out.save(dst, format="PNG")
    print(os.path.basename(src), out.size, "->", dst)


if __name__ == "__main__":
    for f in sorted(glob.glob(os.path.join(RAW, "*.png"))):
        clean(f)
