# -*- coding: utf-8 -*-
"""实验一报告自检：页数、A4、空白页、目录页码、禁用内容、图表数量。"""
import os
import re
import sys
from docx import Document
import pypdf

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX = os.path.join(BASE, "report", "坦克大战实验一报告.docx")
PDF = os.path.join(BASE, "report", "cs24104-2024210622-姚帅-坦克大战联机复刻-实验一软件项目计划.pdf")

BANNED = ["评价标准", "附录", "AI 评价", "76 分", "76分", "待填写", "待确定", "TBD", "TODO", "报告导读", "评分表"]


def norm(s):
    return re.sub(r"\s+", "", s or "")


def main():
    doc = Document(DOCX)
    paras = [(p.style.name, p.text.strip()) for p in doc.paragraphs if p.text.strip()]
    text = "\n".join(p[1] for p in paras)
    headings = [(s, t) for s, t in paras if s in ("Heading 1", "Heading 2")]
    print("DOCX paragraphs:", len(paras), "headings:", len(headings), "tables:", len(doc.tables),
          "inline_shapes:", len(doc.inline_shapes))
    print("sections:", [(round(s.page_width.cm, 1), round(s.page_height.cm, 1), s.orientation) for s in doc.sections])

    bad = [b for b in BANNED if b in text]
    print("banned found:", bad if bad else "none")
    print("TOC placeholder:", "目录将在 Word 中自动更新" in text)

    r = pypdf.PdfReader(PDF)
    print("PDF pages:", len(r.pages))
    sizes = set()
    blanks = []
    for i, pg in enumerate(r.pages):
        b = pg.mediabox
        sizes.add((round(float(b.width), 1), round(float(b.height), 1)))
        t = (pg.extract_text() or "").strip()
        if len(t) < 80:
            blanks.append((i + 1, len(t), t[:40]))
    print("page sizes:", sizes)
    print("short/blank pages:", blanks if blanks else "none")

    # 目录页码 vs 正文实际页码（按标题文本定位）
    toc_text = r.pages[1].extract_text() or ""
    toc_pages = {}
    for line in toc_text.splitlines():
        m = re.match(r"(.+?)\.{3,}\s*(\d+)\s*$", line.strip())
        if m:
            toc_pages[norm(m.group(1))] = int(m.group(2))
    mismatches = []
    for style, h in headings:
        key = norm(h)
        if key not in toc_pages:
            continue
        actual = None
        for idx in range(2, len(r.pages)):
            if key in norm(r.pages[idx].extract_text() or ""):
                actual = idx + 1
                break
        if actual is not None and actual != toc_pages[key]:
            mismatches.append((h, toc_pages[key], actual))
    print("TOC entries parsed:", len(toc_pages), "mismatches:", mismatches if mismatches else "none")

    figs = sorted(set(re.findall(r"图 (\d+-\d+)", text)))
    tabs = sorted(set(re.findall(r"表 (\d+-\d+)", text)))
    print("figures:", figs)
    print("tables:", tabs)


if __name__ == "__main__":
    main()
