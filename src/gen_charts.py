# -*- coding: utf-8 -*-
"""生成实验一报告用的甘特图和风险矩阵（Pillow，不依赖 matplotlib）。"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "report", "assets", "charts")
os.makedirs(OUT, exist_ok=True)
FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def text(draw, xy, s, size=22, fill=(0, 0, 0), bold=False, anchor="la"):
    draw.text(xy, s, font=font(size, bold), fill=fill, anchor=anchor)


def gantt():
    W, H = 1900, 1080
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    left, top, right, bottom = 300, 120, 1820, 930
    weeks = 8
    col_w = (right - left) / weeks
    # grid and week labels
    for i in range(weeks + 1):
        x = left + i * col_w
        d.line((x, top, x, bottom), fill=(210, 210, 210), width=1)
    for i in range(weeks):
        text(d, (left + (i + .5) * col_w, top - 40), f"W{10 + i}", 22, anchor="mm")
    text(d, (left - 20, top - 40), "周次", 22, anchor="rm")
    tasks = [
        ("实验一 计划/仓库/EA", 10, 10, "#4C78A8"),
        ("需求分析", 11, 12, "#4C78A8"),
        ("系统设计/接口", 12, 13, "#4C78A8"),
        ("B 渲染/碰撞", 13, 14, "#E45756"),
        ("B 编辑器/AI 生成", 15, 16, "#E45756"),
        ("A 战斗引擎", 13, 16, "#54A24B"),
        ("C 房间/同步", 13, 16, "#54A24B"),
        ("D 道具/升级", 14, 16, "#54A24B"),
        ("E 大厅/战队 H5", 14, 16, "#54A24B"),
        ("联调/测试", 16, 17, "#B279A2"),
        ("答辩/交付", 17, 17, "#B279A2"),
    ]
    row_h = (bottom - top) / len(tasks)
    for i, (name, s, e, color) in enumerate(tasks):
        y = top + i * row_h
        if i % 2 == 0:
            d.rectangle((left, y, right, y + row_h), fill=(248, 250, 252))
        text(d, (left - 18, y + row_h / 2), name, 21, anchor="rm")
        x0 = left + (s - 10) * col_w + 8
        x1 = left + (e - 10 + 1) * col_w - 8
        d.rounded_rectangle((x0, y + 12, x1, y + row_h - 12), radius=8, fill=color)
    # milestones
    ms = [(10, "M1"), (12, "M2"), (13, "M3"), (16, "M4"), (17, "M5")]
    for wk, label in ms:
        x = left + (wk - 10 + .5) * col_w
        y = bottom + 26
        d.polygon([(x, y - 12), (x + 13, y), (x, y + 12), (x - 13, y)], fill="#F2A900")
        text(d, (x, y + 22), label, 18, anchor="ma")
    # buffer
    d.rectangle((left + 6 * col_w, bottom + 70, left + 6.6 * col_w, bottom + 92),
                fill=(230, 230, 230), outline=(120, 120, 120), width=1)
    text(d, (left + 6.3 * col_w, bottom + 81), "2 天缓冲", 16, anchor="mm")
    # legend
    lx, ly = left, 10
    for color, label in [("#4C78A8", "计划/需求/设计"), ("#E45756", "B 地图系统"),
                         ("#54A24B", "A/C/D/E 模块"), ("#B279A2", "测试/答辩")]:
        d.rectangle((lx, ly + 6, lx + 28, ly + 24), fill=color)
        text(d, (lx + 36, ly + 15), label, 18, anchor="lm")
        lx += 300
    im.save(os.path.join(OUT, "fig2-2-gantt.png"), dpi=(200, 200))
    print("gantt ok")


def risk_matrix():
    W, H = 1700, 1100
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    left, top, cell = 190, 110, 150
    # 5x5 cells: x=impact 1..5, y=probability 1..5 (bottom to top)
    for i in range(5):        # impact
        for j in range(5):    # probability
            p = j + 1
            imp = i + 1
            score = p * imp
            if score >= 15:
                color = (244, 199, 195)
            elif score >= 8:
                color = (255, 235, 177)
            else:
                color = (213, 232, 212)
            x0 = left + i * cell
            y0 = top + (4 - j) * cell
            d.rectangle((x0, y0, x0 + cell, y0 + cell), fill=color, outline=(255, 255, 255), width=2)
            text(d, (x0 + cell - 10, y0 + cell - 8), str(score), 20, anchor="rs")
    for i in range(6):
        x = left + i * cell
        d.line((x, top, x, top + 5 * cell), fill=(90, 90, 90), width=2)
        y = top + i * cell
        d.line((left, y, left + 5 * cell, y), fill=(90, 90, 90), width=2)
    for i in range(5):
        text(d, (left + (i + .5) * cell, top + 5 * cell + 32), str(i + 1), 22, anchor="mm")
        text(d, (left - 38, top + (4 - i + .5) * cell), str(i + 1), 22, anchor="rm")
    text(d, (left + 2.5 * cell, top + 5 * cell + 78), "影响（1 低 → 5 高）", 22, anchor="mm")
    text(d, (34, top + 2.5 * cell), "概率", 22, anchor="mm")
    # risks: (id, impact, prob, dx, dy)
    risks = [
        ("R1", 4, 4, 0, 0), ("R2", 3, 3, -35, -28), ("R3", 4, 3, 30, 20),
        ("R4", 3, 4, 28, -24), ("R5", 4, 3, -34, 24), ("R6", 3, 4, -30, 24),
        ("R7", 3, 2, 20, -20),
    ]
    for rid, imp, p, dx, dy in risks:
        x = left + (imp - .5) * cell + dx
        y = top + (4 - p + .5) * cell + dy
        d.ellipse((x - 25, y - 25, x + 25, y + 25), fill=(255, 255, 255), outline=(40, 40, 40), width=3)
        text(d, (x, y), rid, 20, anchor="mm")
    # legend
    lx, ly = left, 1010
    for color, label in [((213, 232, 212), "低 1~7"), ((255, 235, 177), "中 8~14"), ((244, 199, 195), "高 15~25")]:
        d.rectangle((lx, ly, lx + 36, ly + 24), fill=color, outline=(120, 120, 120))
        text(d, (lx + 46, ly + 12), label, 20, anchor="lm")
        lx += 250
    text(d, (left + 800, 1022), "风险值 = 概率 × 影响", 20, anchor="lm")
    im.save(os.path.join(OUT, "fig2-3-risk.png"), dpi=(200, 200))
    print("risk ok")


if __name__ == "__main__":
    gantt()
    risk_matrix()
