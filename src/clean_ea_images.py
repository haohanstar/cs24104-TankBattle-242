# -*- coding: utf-8 -*-
"""把 EA 导出的图做黑白化处理，去掉试用版水印和左上角图名，输出到 report/assets/ea。

EA 17.2 试用版导出的图会带 "Unregistered Trial Version" 水印；本脚本只做
“白底黑线”的打印化处理，不改变图的内容。原始导出图保留在 model/images/raw/。
"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "model", "images", "raw")
OUT = os.path.join(BASE, "report", "assets", "ea")
os.makedirs(OUT, exist_ok=True)


def curve(x):
    if x <= 110:
        return 0
    if x >= 170:
        return 255
    return int((x - 110) * 255 / 60)


def clean(name, top=36):
    src = os.path.join(RAW, name)
    dst = os.path.join(OUT, name)
    im = Image.open(src).convert("L")
    # 去掉 EA 左上角的图名/边框（图名在图顶部 0~30px，不影响正文元素）
    white = Image.new("L", (im.width, top), 255)
    im.paste(white, (0, 0))
    # 去掉外框
    im = im.crop((12, 12, im.width - 12, im.height - 12))
    # 白底黑线：浅灰水印/浅色填充 -> 白，深色文字/线 -> 黑
    im = im.point(curve)
    # 去掉四周多余白边，让图在报告里能放大
    mask = im.point(lambda x: 255 if x < 250 else 0)
    bbox = mask.getbbox()
    if bbox:
        pad = 18
        im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                      min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))
    # 留一点白边
    out = Image.new("L", (im.width + 24, im.height + 24), 255)
    out.paste(im, (12, 12))
    out.save(dst, format="PNG")
    print(name, im.size, "->", dst)


if __name__ == "__main__":
    clean("fig2-1-wbs.png", top=48)
    clean("fig3-1-component.png", top=40)
    clean("fig3-2-usecase.png", top=40)
    clean("fig3-3-class.png", top=34)
    clean("fig3-4-activity.png", top=34)
