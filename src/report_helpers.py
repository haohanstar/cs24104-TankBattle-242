# -*- coding: utf-8 -*-
"""python-docx 中文报告排版工具。"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BODY_FONT = "宋体"
HEAD_FONT = "黑体"
HEADER_COLOR = RGBColor(0x44, 0x54, 0x6A)
ACCENT = RGBColor(0x1F, 0x4E, 0x79)
HEADER_FILL = "D9E2F3"
ALT_FILL = "F2F5FA"


def set_run_font(run, name=BODY_FONT, size=12, bold=None, color=None, italic=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def set_doc_defaults(doc):
    st = doc.styles["Normal"]
    st.font.name = BODY_FONT
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    st.paragraph_format.line_spacing = 1.4
    st.paragraph_format.space_after = Pt(4)
    for name, size in (("Heading 1", 18), ("Heading 2", 14), ("Heading 3", 12)):
        try:
            s = doc.styles[name]
            s.font.name = HEAD_FONT
            s.font.size = Pt(size)
            s.font.bold = True
            s.font.color.rgb = ACCENT
            s.element.rPr.rFonts.set(qn("w:eastAsia"), HEAD_FONT)
        except Exception:
            pass


def set_section_layout(section, landscape=False, margins=None):
    if landscape:
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = Cm(29.7)
        section.page_height = Cm(21.0)
        section.top_margin = Cm(1.8)
        section.bottom_margin = Cm(1.8)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)
    else:
        section.orientation = WD_ORIENT.PORTRAIT
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(1.8)
        section.bottom_margin = Cm(1.8)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)
    if margins:
        section.top_margin, section.bottom_margin, section.left_margin, section.right_margin = margins
    section.header_distance = Cm(1.0)
    section.footer_distance = Cm(1.0)


def add_section(doc, landscape=False, start_page=None, link_header=True):
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    set_section_layout(sec, landscape)
    sec.header.is_linked_to_previous = link_header
    sec.footer.is_linked_to_previous = link_header
    sectPr = sec._sectPr
    pgNumType = sectPr.find(qn("w:pgNumType"))
    if start_page is not None:
        if pgNumType is None:
            pgNumType = OxmlElement("w:pgNumType")
            sectPr.append(pgNumType)
        pgNumType.set(qn("w:start"), str(start_page))
    else:
        # 新 section 会继承上一节的 pgNumType；删除它，使页码连续
        if pgNumType is not None:
            sectPr.remove(pgNumType)
    return sec


def add_field(run, instr, placeholder="1"):
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = instr
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t")
    t.text = placeholder
    fld3 = OxmlElement("w:fldChar")
    fld3.set(qn("w:fldCharType"), "end")
    run._r.append(fld1)
    run._r.append(it)
    run._r.append(fld2)
    run._r.append(t)
    run._r.append(fld3)


def add_header_footer(section, header_text):
    hp = section.header.paragraphs[0]
    hp.text = ""
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = hp.add_run(header_text)
    set_run_font(r, BODY_FONT, 8.5, color=HEADER_COLOR)
    # bottom border
    pPr = hp._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "4")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "A6B7D4")
    pbdr.append(bottom)
    pPr.append(pbdr)

    fp = section.footer.paragraphs[0]
    fp.text = ""
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = fp.add_run("第 ")
    set_run_font(r1, BODY_FONT, 8.5, color=HEADER_COLOR)
    r2 = fp.add_run()
    set_run_font(r2, BODY_FONT, 8.5, color=HEADER_COLOR)
    add_field(r2, "PAGE")
    r3 = fp.add_run(" 页  共 ")
    set_run_font(r3, BODY_FONT, 8.5, color=HEADER_COLOR)
    r4 = fp.add_run()
    set_run_font(r4, BODY_FONT, 8.5, color=HEADER_COLOR)
    add_field(r4, "NUMPAGES")
    r5 = fp.add_run(" 页")
    set_run_font(r5, BODY_FONT, 8.5, color=HEADER_COLOR)


def h(doc, text, level=1, page_break=False):
    if page_break:
        doc.add_page_break()
    p = doc.add_heading(level=level)
    r = p.add_run(text)
    size = {1: 18, 2: 15, 3: 12.5}.get(level, 12.5)
    set_run_font(r, HEAD_FONT, size, bold=True, color=ACCENT)
    p.paragraph_format.space_before = Pt(8 if level == 1 else 5)
    p.paragraph_format.space_after = Pt(3 if level == 1 else 2)
    p.paragraph_format.keep_with_next = True
    return p


def body(doc, text, bold=False, indent=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
         size=11.5, space_after=5, color=None):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(space_after)
    if indent:
        pf.first_line_indent = Pt(23)
    r = p.add_run(text)
    set_run_font(r, BODY_FONT, size, bold=bold, color=color)
    return p


def rich(doc, parts, indent=True, size=11.5, space_after=5):
    """parts: list of (text, bold) tuples."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_after = Pt(space_after)
    if indent:
        p.paragraph_format.first_line_indent = Pt(24)
    for text, b in parts:
        r = p.add_run(text)
        set_run_font(r, BODY_FONT, size, bold=b)
    return p


def bullets(doc, items, size=11.5):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(it)
        set_run_font(r, BODY_FONT, size)


def caption(doc, text, kind="图"):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    set_run_font(r, BODY_FONT, 9.5, bold=True)
    return p


def set_cell_shading(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def set_cell_margins(table, top=25, bottom=25, left=50, right=50):
    tblPr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for k, v in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        el = OxmlElement("w:" + k)
        el.set(qn("w:w"), str(v))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tblPr.append(mar)


def set_repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)


def set_row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    cs = OxmlElement("w:cantSplit")
    cs.set(qn("w:val"), "true")
    trPr.append(cs)


def set_col_widths(table, widths_cm):
    for row in table.rows:
        for i, w in enumerate(widths_cm):
            if i < len(row.cells):
                row.cells[i].width = Cm(w)
    for i, w in enumerate(widths_cm):
        if i < len(table.columns):
            table.columns[i].width = Cm(w)


def add_table(doc, headers, rows, widths_cm, font_size=8, header_fill=HEADER_FILL,
              first_col_bold=False, align=WD_ALIGN_PARAGRAPH.LEFT, caption_text=None):
    if caption_text:
        cap = caption(doc, caption_text, "表")
        cap.paragraph_format.keep_with_next = True
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_cell_margins(table)
    hdr = table.rows[0]
    set_repeat_header(hdr)
    set_row_cant_split(hdr)
    for i, htxt in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(str(htxt))
        set_run_font(r, BODY_FONT, font_size, bold=True)
        set_cell_shading(cell, header_fill)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        set_row_cant_split(table.rows[-1])
        for i, val in enumerate(row):
            cell = cells[i]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = align
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(str(val))
            set_run_font(r, BODY_FONT, font_size, bold=(first_col_bold and i == 0))
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if ridx % 2 == 1:
                set_cell_shading(cell, ALT_FILL)
    set_col_widths(table, widths_cm)
    return table


def add_figure(doc, path, caption_text, width_cm=16.0, landscape=False, note=None):
    if landscape:
        add_section(doc, landscape=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    run.add_picture(path, width=Cm(width_cm))
    caption(doc, caption_text, "图")
    if note:
        np = doc.add_paragraph()
        np.alignment = WD_ALIGN_PARAGRAPH.CENTER
        np.paragraph_format.space_after = Pt(4)
        r = np.add_run(note)
        set_run_font(r, BODY_FONT, 9, color=RGBColor(0x59, 0x59, 0x59))
    if landscape:
        add_section(doc, landscape=False)


def add_toc(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run()
    fldChar = OxmlElement("w:fldChar")
    fldChar.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-2" \\h \\z \\u'
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t")
    t.text = "目录将在 Word 中自动更新（打开 PDF 前已更新）。"
    fldChar3 = OxmlElement("w:fldChar")
    fldChar3.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar)
    run._r.append(instr)
    run._r.append(fldChar2)
    run._r.append(t)
    run._r.append(fldChar3)


def page_break(doc):
    doc.add_page_break()


def set_paragraph_border_bottom(p, color="1F4E79", size=12):
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), color)
    pbdr.append(bottom)
    pPr.append(pbdr)
