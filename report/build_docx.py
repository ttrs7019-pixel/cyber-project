"""Render the same technical report to DOCX (A4, Word-friendly fonts)."""
import os
from datetime import datetime

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor, Emu

import content as C

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "figures")

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
SLATE = RGBColor(0x44, 0x54, 0x6A)
GREY = RGBColor(0x8A, 0x94, 0xA6)
INK = RGBColor(0x1A, 0x1A, 0x1A)

BODY_FONT = "Cambria"
SANS_FONT = "Calibri"
MONO_FONT = "Consolas"
BODY_SIZE = 10.5

PAGE_W, PAGE_H = Mm(210), Mm(297)
MARGIN_L, MARGIN_R = Mm(24), Mm(22)
MARGIN_T, MARGIN_B = Mm(22), Mm(20)


# ------------------------------------------------------------------ helpers
def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def cell_valign(cell, val="top"):
    tcPr = cell._tc.get_or_add_tcPr()
    va = OxmlElement("w:vAlign")
    va.set(qn("w:val"), val)
    tcPr.append(va)


def cell_borders(cell, **kwargs):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        spec = kwargs.get(edge)
        el = OxmlElement(f"w:{edge}")
        if spec:
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), str(spec[0]))
            el.set(qn("w:color"), spec[1])
        else:
            el.set(qn("w:val"), "nil")
        borders.append(el)
    tcPr.append(borders)


def para_shading(paragraph, hex_color):
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    pPr.append(shd)


def no_space(paragraph, before=0, after=0):
    pf = paragraph.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)


def add_run(paragraph, text, font=BODY_FONT, size=BODY_SIZE, bold=False,
            italic=False, color=INK):
    run = paragraph.add_run(text)
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(attr), font)
    return run


def inline_runs(paragraph, text, size=BODY_SIZE, color=INK):
    """Render **bold** and `mono` inline markers."""
    import re
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            add_run(paragraph, part[2:-2], font=SANS_FONT, size=size, bold=True,
                    color=color)
        elif part.startswith("`") and part.endswith("`"):
            add_run(paragraph, part[1:-1], font=MONO_FONT, size=size - 1.0,
                    color=color)
        else:
            add_run(paragraph, part, size=size, color=color)


def field(paragraph, instr, placeholder="1"):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    run._r.append(fld_begin)
    run2 = paragraph.add_run()
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    run2._r.append(instr_el)
    run3 = paragraph.add_run()
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    run3._r.append(fld_sep)
    run4 = paragraph.add_run(placeholder)
    run4.font.name = SANS_FONT
    run4.font.size = Pt(8.5)
    run4.font.color.rgb = GREY
    run5 = paragraph.add_run()
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run5._r.append(fld_end)


def hrule(paragraph, color="C9D2DE", size=6):
    pPr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), color)
    borders.append(bottom)
    pPr.append(borders)


# ------------------------------------------------------------------ document
doc = Document()

core = doc.core_properties
core.title = C.TITLE
core.subject = C.SUBTITLE
core.author = ""
core.comments = ""
core.category = "Technical report"
core.keywords = "TLS 1.3, Python ssl, handshake, AEAD, certificate, Wireshark"
core.created = datetime(2026, 11, 20, 9, 30)
core.modified = datetime(2026, 11, 20, 9, 30)
core.revision = 3

styles = doc.styles
normal = styles["Normal"]
normal.font.name = BODY_FONT
normal.font.size = Pt(BODY_SIZE)
normal.font.color.rgb = INK
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.06

section = doc.sections[0]
section.page_width = PAGE_W
section.page_height = PAGE_H
section.left_margin = MARGIN_L
section.right_margin = MARGIN_R
section.top_margin = MARGIN_T
section.bottom_margin = MARGIN_B
section.header_distance = Mm(11)
section.footer_distance = Mm(10)
CW = section.page_width - MARGIN_L - MARGIN_R


def header_footer(sec, with_header=True):
    hdr = sec.header
    hdr.is_linked_to_previous = False
    p = hdr.paragraphs[0]
    p.text = ""
    no_space(p, 0, 3)
    if with_header:
        add_run(p, "TLS 1.3 Client\u2013Server Channel \u00b7 " + C.REPORT_LABEL,
                font=SANS_FONT, size=8, color=GREY)
        hrule(p)

    ftr = sec.footer
    ftr.is_linked_to_previous = False
    p = ftr.paragraphs[0]
    p.text = ""
    no_space(p, 4, 0)
    tab_stops = p.paragraph_format.tab_stops
    tab_stops.add_tab_stop(CW, WD_TAB_ALIGNMENT.RIGHT)
    add_run(p, C.DATE, font=SANS_FONT, size=8, color=GREY)
    add_run(p, "\t", font=SANS_FONT, size=8, color=GREY)
    field(p, " PAGE ")


header_footer(section, with_header=False)

# ------------------------------------------------------------------ cover
band = doc.add_table(rows=1, cols=2)
band.autofit = False
band_cells = band.rows[0].cells
band_cells[0].width = int(CW * 0.55)
band_cells[1].width = int(CW * 0.45)
for cell in band_cells:
    set_cell_bg(cell, "1F3A5F")
    cell_borders(cell, top=None, bottom=None, left=None, right=None)
pb = band_cells[0].paragraphs[0]
no_space(pb, 9, 9)
add_run(pb, C.REPORT_LABEL, font=SANS_FONT, size=8.6, bold=True,
        color=RGBColor(0xFF, 0xFF, 0xFF))
pb2 = band_cells[1].paragraphs[0]
no_space(pb2, 9, 9)
pb2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
add_run(pb2, C.DATE, font=SANS_FONT, size=8.6,
        color=RGBColor(0xFF, 0xFF, 0xFF))

p = doc.add_paragraph()
no_space(p, Mm(26), 0)
add_run(p, "SECURE COMMUNICATION \u00b7 APPLICATION SECURITY", font=SANS_FONT,
        size=8.5, bold=True, color=SLATE)

p = doc.add_paragraph()
no_space(p, 6, 0)
hrule(p, color="1F3A5F", size=12)

p = doc.add_paragraph()
no_space(p, 10, 0)
add_run(p, C.TITLE, font=SANS_FONT, size=27, bold=True, color=NAVY)

p = doc.add_paragraph()
no_space(p, 6, 0)
add_run(p, C.SUBTITLE, font=BODY_FONT, size=12, italic=True, color=SLATE)

p = doc.add_paragraph()
no_space(p, Mm(30), 0)

tbl = doc.add_table(rows=len(C.DOC_META), cols=2)
tbl.autofit = False
for row, (k, v) in zip(tbl.rows, C.DOC_META):
    row.cells[0].width = Mm(36)
    row.cells[1].width = Mm(96)
    pk = row.cells[0].paragraphs[0]
    no_space(pk, 4, 4)
    add_run(pk, k, font=SANS_FONT, size=9, bold=True, color=SLATE)
    pv = row.cells[1].paragraphs[0]
    no_space(pv, 4, 4)
    cell_borders(row.cells[1], bottom=(6, "B9C4D2"), top=None, left=None, right=None)
    add_run(pv, v or " ", font=SANS_FONT, size=9, color=INK)

p = doc.add_paragraph()
no_space(p, Mm(26), 0)
hrule(p, color="C9D2DE", size=6)

p = doc.add_paragraph()
no_space(p, 6, 0)
tab_stops = p.paragraph_format.tab_stops
tab_stops.add_tab_stop(CW, WD_TAB_ALIGNMENT.RIGHT)
add_run(p, "Submission: " + C.DATE, font=SANS_FONT, size=8.5, color=SLATE)
add_run(p, "\tTechnical report \u00b7 " + C.VERSION, font=SANS_FONT, size=8.5,
        color=SLATE)

# ------------------------------------------------------------------ contents
doc.add_section(WD_SECTION.NEW_PAGE)
sec2 = doc.sections[1]
sec2.page_width, sec2.page_height = PAGE_W, PAGE_H
sec2.left_margin, sec2.right_margin = MARGIN_L, MARGIN_R
sec2.top_margin, sec2.bottom_margin = MARGIN_T, MARGIN_B
header_footer(sec2, with_header=True)

p = doc.add_paragraph()
no_space(p, 2, 10)
add_run(p, "Contents", font=SANS_FONT, size=16, bold=True, color=NAVY)

# static contents table: deterministic page numbers, dot leaders via tab stops
for num, title, page in C.CONTENTS:
    p = doc.add_paragraph()
    is_major = num == "" or "." not in num
    no_space(p, 3.5 if is_major else 0, 2.0 if is_major else 0.5)
    p.paragraph_format.tab_stops.add_tab_stop(CW, WD_TAB_ALIGNMENT.RIGHT,
                                              WD_TAB_LEADER.DOTS)
    if num and "." in num:
        p.paragraph_format.left_indent = Cm(0.55)
        add_run(p, title, font=BODY_FONT, size=9.6, color=RGBColor(0x33, 0x41, 0x5A))
    else:
        label = f"{num}\u2002\u2002{title}" if num else title
        add_run(p, label, font=SANS_FONT, size=9.6, bold=True, color=NAVY)
    add_run(p, "\t", font=BODY_FONT, size=9)
    add_run(p, page, font=SANS_FONT, size=8.5, color=GREY)

p = doc.add_paragraph()
no_space(p, 14, 0)
hrule(p, color="C9D2DE", size=6)


def static_list(title, items):
    p = doc.add_paragraph()
    no_space(p, 10, 4)
    add_run(p, title, font=SANS_FONT, size=9.5, bold=True, color=NAVY)
    for num, text, page in items:
        p = doc.add_paragraph()
        no_space(p, 0, 2)
        p.paragraph_format.tab_stops.add_tab_stop(CW, WD_TAB_ALIGNMENT.RIGHT)
        add_run(p, f"{num}  ", font=SANS_FONT, size=8.5, color=SLATE)
        add_run(p, text, font=BODY_FONT, size=9, color=INK)
        add_run(p, f"\t{page}", font=SANS_FONT, size=8.5, color=GREY)


static_list("Figures", C.FIGURES)
static_list("Tables", C.TABLES)

p = doc.add_paragraph()
no_space(p, 12, 0)
hrule(p, color="C9D2DE", size=6)

p = doc.add_paragraph()
no_space(p, 10, 5)
add_run(p, "Abbreviations", font=SANS_FONT, size=9.5, bold=True, color=NAVY)

half = (len(C.ABBREVIATIONS) + 1) // 2
ab = doc.add_table(rows=half, cols=4)
ab.autofit = False
for i in range(half):
    left = C.ABBREVIATIONS[i]
    right = C.ABBREVIATIONS[half + i] if half + i < len(C.ABBREVIATIONS) else ("", "")
    for col, (key, val) in ((0, left), (2, right)):
        cell_k = ab.cell(i, col)
        cell_v = ab.cell(i, col + 1)
        cell_k.width = Mm(17)
        cell_v.width = Mm(62)
        cell_valign(cell_k, "top")
        cell_valign(cell_v, "top")
        pk = cell_k.paragraphs[0]
        no_space(pk, 1.5, 1.5)
        add_run(pk, key, font=SANS_FONT, size=8.5, bold=True, color=INK)
        pv = cell_v.paragraphs[0]
        no_space(pv, 1.5, 1.5)
        add_run(pv, val, font=BODY_FONT, size=8.5, color=INK)

# ------------------------------------------------------------------ body
doc.add_section(WD_SECTION.NEW_PAGE)
sec3 = doc.sections[2]
sec3.page_width, sec3.page_height = PAGE_W, PAGE_H
sec3.left_margin, sec3.right_margin = MARGIN_L, MARGIN_R
sec3.top_margin, sec3.bottom_margin = MARGIN_T, MARGIN_B
header_footer(sec3, with_header=True)


def h1(text, numbered=True):
    p = doc.add_paragraph()
    p.style = styles["Heading 1"]
    no_space(p, 13, 5)
    p.paragraph_format.keep_with_next = True
    if numbered:
        parts = text.split(" ", 1)
        add_run(p, parts[0] + "\u2002\u2002", font=SANS_FONT, size=13.5,
                bold=True, color=NAVY)
        add_run(p, parts[1], font=SANS_FONT, size=13.5, bold=True, color=NAVY)
    else:
        add_run(p, text, font=SANS_FONT, size=13.5, bold=True, color=NAVY)


def h2(text):
    p = doc.add_paragraph()
    p.style = styles["Heading 2"]
    no_space(p, 8, 2.5)
    p.paragraph_format.keep_with_next = True
    add_run(p, text, font=SANS_FONT, size=10.5, bold=True, color=SLATE)


def body(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    no_space(p, 0, 5.5)
    p.paragraph_format.line_spacing = 1.06
    inline_runs(p, text)


def bullet_list(items, numbered=False, size=BODY_SIZE):
    for i, item in enumerate(items):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        no_space(p, 0, 3)
        p.paragraph_format.left_indent = Cm(0.75)
        p.paragraph_format.first_line_indent = Cm(-0.5)
        p.paragraph_format.line_spacing = 1.05
        if numbered:
            add_run(p, f"{i + 1}.  ", font=SANS_FONT, size=size, bold=True,
                    color=NAVY)
        else:
            add_run(p, "\u2022  ", font=SANS_FONT, size=size - 0.8, color=SLATE)
        inline_runs(p, item, size=size)


def code_block(caption, text):
    p = doc.add_paragraph()
    no_space(p, 3, 2)
    p.paragraph_format.keep_with_next = True
    add_run(p, caption, font=SANS_FONT, size=7.8, color=SLATE)

    tbl = doc.add_table(rows=1, cols=1)
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = CW
    set_cell_bg(cell, "F2F5F9")
    cell_borders(cell, left=(12, "1F3A5F"), top=None, bottom=None, right=None)
    cell.paragraphs[0].text = ""
    for i, line in enumerate(text.split("\n")):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        no_space(p, 1.2, 1.2)
        p.paragraph_format.line_spacing = 1.0
        add_run(p, line if line else " ", font=MONO_FONT, size=8, color=INK)

    p = doc.add_paragraph()
    no_space(p, 0, 6)


def table_block(caption, header, rows, widths_in, size=8.8):
    p = doc.add_paragraph()
    no_space(p, 6, 3)
    p.paragraph_format.keep_with_next = True
    add_run(p, caption, font=SANS_FONT, size=8.2, color=SLATE)

    scale = CW / Mm(sum(widths_in) * 25.4)
    widths = [int(w * 25.4 * scale) for w in widths_in]

    tbl = doc.add_table(rows=len(rows) + 1, cols=len(header))
    tbl.autofit = False
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT

    for j, htext in enumerate(header):
        cell = tbl.cell(0, j)
        cell.width = widths[j]
        set_cell_bg(cell, "EDF1F6")
        cell_borders(cell, bottom=(12, "1F3A5F"), top=None, left=None, right=None)
        cell_valign(cell, "top")
        p = cell.paragraphs[0]
        no_space(p, 3, 3)
        add_run(p, htext, font=SANS_FONT, size=8.5, bold=True, color=NAVY)

    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.width = widths[j]
            last = (i == len(rows))
            cell_borders(cell, bottom=(8 if last else 4, "C9D2DE" if not last else "C9D2DE"),
                         top=None, left=None, right=None)
            cell_valign(cell, "top")
            p = cell.paragraphs[0]
            no_space(p, 2.6, 2.6)
            p.paragraph_format.line_spacing = 1.0
            inline_runs(p, str(val), size=size)

    p = doc.add_paragraph()
    no_space(p, 0, 6)


def figure_block(fn, caption, width_in):
    from PIL import Image
    path = os.path.join(FIGDIR, fn)
    iw, ih = Image.open(path).size
    width = min(Emu(int(width_in * 914400)), CW)

    p = doc.add_paragraph()
    no_space(p, 4, 2)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=width)

    p = doc.add_paragraph()
    no_space(p, 2, 9)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, caption, font=SANS_FONT, size=8.2, color=SLATE)


h1n = 0
h2n = 0
for block in C.BLOCKS:
    kind = block[0]
    if kind == "h1":
        if block[1] == "References":
            h1(block[1], numbered=False)
        else:
            h1n += 1
            h2n = 0
            h1(f"{h1n} {block[1]}")
    elif kind == "h2":
        h2n += 1
        h2(f"{h1n}.{h2n}\u2002 {block[1]}")
    elif kind == "p":
        body(block[1])
    elif kind == "bullets":
        bullet_list(block[1])
    elif kind == "numbers":
        bullet_list(block[1], numbered=True)
    elif kind == "code":
        code_block(block[1], block[2])
    elif kind == "table":
        table_block(block[1], block[2], block[3], block[4])
    elif kind == "figure":
        figure_block(block[1], block[2], block[3])
    elif kind == "refs":
        for i, r in enumerate(block[1]):
            p = doc.add_paragraph()
            no_space(p, 0, 4)
            p.paragraph_format.left_indent = Cm(0.85)
            p.paragraph_format.first_line_indent = Cm(-0.85)
            add_run(p, f"[{i + 1}]\u2002", font=BODY_FONT, size=9.5, color=SLATE)
            add_run(p, r, font=BODY_FONT, size=9.5, color=INK)
    elif kind == "pagebreak":
        doc.add_page_break()

out = os.path.join(HERE, "build", "TLS-1.3-Technical-Report.docx")
os.makedirs(os.path.dirname(out), exist_ok=True)
doc.save(out)
print("written", out)
