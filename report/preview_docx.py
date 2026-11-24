"""Approximate paginated preview of the DOCX, for layout checking only.

Renders the DOCX content model with Caladea/Carlito (metric-compatible with
Cambria/Calibri) so the page count and line breaks track what Word will do.
"""
import os
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether,
                                PageBreak, Flowable, NextPageTemplate)
from PIL import Image

import content as C

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
FIG = os.path.join(HERE, "figures")

for name, fn in {"Serif": "Caladea-Regular.ttf", "Serif-B": "Caladea-Bold.ttf",
                 "Serif-I": "Caladea-Italic.ttf", "Sans": "Carlito-Regular.ttf",
                 "Sans-B": "Carlito-Bold.ttf", "Sans-I": "Carlito-Italic.ttf",
                 "Mono": "IBMPlexMono-Regular.ttf"}.items():
    pdfmetrics.registerFont(TTFont(name, os.path.join(A, fn)))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-B",
                              italic="Serif-I", boldItalic="Serif-B")
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-B",
                              italic="Sans-I", boldItalic="Sans-B")

NAVY = colors.HexColor("#1F3A5F")
SLATE = colors.HexColor("#44546A")
GREY = colors.HexColor("#8A94A6")
RULE = colors.HexColor("#C9D2DE")
LIGHT = colors.HexColor("#EDF1F6")
INK = colors.HexColor("#1A1A1A")

PW, PH = A4
ML, MR = 24 * mm, 22 * mm
MT, MB = 22 * mm, 20 * mm
CW = PW - ML - MR

S = {}
S["body"] = ParagraphStyle("body", fontName="Serif", fontSize=10.5, leading=11.13,
                           alignment=TA_JUSTIFY, spaceAfter=5.5, textColor=INK)
S["h1"] = ParagraphStyle("h1", fontName="Sans-B", fontSize=13.5, leading=16,
                         textColor=NAVY, spaceBefore=13, spaceAfter=5,
                         keepWithNext=1)
S["h2"] = ParagraphStyle("h2", fontName="Sans-B", fontSize=10.5, leading=13,
                         textColor=SLATE, spaceBefore=8, spaceAfter=2.5,
                         keepWithNext=1)
S["bul"] = ParagraphStyle("bul", parent=S["body"], leftIndent=21, bulletIndent=6,
                          spaceAfter=3, leading=11.0)
S["cap"] = ParagraphStyle("cap", fontName="Sans", fontSize=8.2, leading=10.5,
                          textColor=SLATE, alignment=TA_CENTER, spaceBefore=2,
                          spaceAfter=9)
S["tabcap"] = ParagraphStyle("tabcap", fontName="Sans", fontSize=8.2, leading=10.5,
                             textColor=SLATE, alignment=TA_LEFT, spaceBefore=6,
                             spaceAfter=3)
S["code"] = ParagraphStyle("code", fontName="Mono", fontSize=8, leading=8.0)
S["codecap"] = ParagraphStyle("cc", fontName="Sans", fontSize=7.8, leading=10,
                              textColor=SLATE, spaceAfter=2)
S["ref"] = ParagraphStyle("ref", fontName="Serif", fontSize=9.5, leading=11.5,
                          leftIndent=24, firstLineIndent=-24, spaceAfter=4,
                          textColor=INK)


def inline(t):
    out = []
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", t):
        if part.startswith("**") and part.endswith("**"):
            out.append(f'<font name="Sans-B">{part[2:-2]}</font>')
        elif part.startswith("`") and part.endswith("`"):
            out.append(f'<font name="Mono" size="9.5">{part[1:-1]}</font>')
        else:
            out.append(part.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return "".join(out)


class CodeBox(Flowable):
    def __init__(self, lines, width):
        Flowable.__init__(self)
        self.lines = lines
        self.width = width
        self.height = len(lines) * 8.0 * 1.0 + 2 * 3 + 0

    def draw(self):
        c = self.canv
        c.setFillColor(colors.HexColor("#F2F5F9"))
        c.setStrokeColor(colors.white)
        c.rect(0, 0, self.width, self.height, stroke=0, fill=1)
        c.setFillColor(NAVY)
        c.rect(0, 0, 2.2, self.height, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("Mono", 8)
        y = self.height - 3 - 8
        for ln in self.lines:
            c.drawString(5, y, ln)
            y -= 8.0


def story():
    st = []
    # cover
    st.append(NextPageTemplate("plain"))
    st.append(Spacer(1, 30 * mm))
    st.append(Paragraph("SECURE COMMUNICATION \u00b7 APPLICATION SECURITY",
                        ParagraphStyle("cv1", fontName="Sans-B", fontSize=8.5, textColor=SLATE)))
    st.append(Spacer(1, 5 * mm))
    st.append(Paragraph(C.TITLE, ParagraphStyle("cv2", fontName="Sans-B", fontSize=27,
                                                leading=32, textColor=NAVY)))
    st.append(Spacer(1, 6 * mm))
    st.append(Paragraph(C.SUBTITLE, ParagraphStyle("cv3", fontName="Serif", fontSize=12,
                                                   leading=15, textColor=SLATE)))
    st.append(Spacer(1, 30 * mm))
    rows = [[Paragraph(k, ParagraphStyle("k", fontName="Sans-B", fontSize=9, textColor=SLATE)),
             Paragraph(v or " ", ParagraphStyle("v", fontName="Sans", fontSize=9))]
            for k, v in C.DOC_META]
    t = Table(rows, colWidths=[36 * mm, 96 * mm], rowHeights=None)
    t.setStyle(TableStyle([("LINEBELOW", (1, 0), (1, -1), 0.6, colors.HexColor("#B9C4D2")),
                           ("TOPPADDING", (0, 0), (-1, -1), 4),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    st.append(t)
    st.append(PageBreak())

    # front matter
    st.append(Paragraph("Contents", ParagraphStyle("toc", fontName="Sans-B", fontSize=16,
                                                   textColor=NAVY, spaceAfter=10)))
    for num, title, page in C.CONTENTS:
        if num and "." not in num:
            st.append(Spacer(1, 3.5))
        if num == "":
            label = title
        elif "." in num:
            label = title
        else:
            label = f"{num}\u2002\u2002{title}"
        if "." in num:
            style = ParagraphStyle("sub", fontName="Serif", fontSize=9.6, leading=12,
                                   leftIndent=15, spaceBefore=0.5)
        else:
            style = ParagraphStyle("maj", fontName="Sans-B", fontSize=9.6, leading=12,
                                   textColor=NAVY, spaceBefore=0)
        p_ = Paragraph(label, style)
        pg = Paragraph(page, ParagraphStyle("pg", fontName="Sans", fontSize=8.5,
                                            alignment=TA_RIGHT))
        st.append(Table([[p_, pg]], colWidths=[CW - 26, 26],
                        style=TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                                          ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                          ("TOPPADDING", (0, 0), (-1, -1), 0),
                                          ("BOTTOMPADDING", (0, 0), (-1, -1), 0)])))
    st.append(Spacer(1, 10 * mm))
    for label, items in (("Figures", C.FIGURES), ("Tables", C.TABLES)):
        st.append(Paragraph(label, ParagraphStyle("lh", fontName="Sans-B", fontSize=9.5,
                                                  textColor=NAVY, spaceBefore=8, spaceAfter=4)))
        for num, title, page in items:
            st.append(Paragraph(f'{num}  {title} \u2003<span color="#8A94A6">{page}</span>',
                                ParagraphStyle("li", fontName="Serif", fontSize=9, leading=12.5)))
    st.append(Spacer(1, 8 * mm))
    st.append(Paragraph("Abbreviations", ParagraphStyle("lh2", fontName="Sans-B",
                                                        fontSize=9.5, textColor=NAVY,
                                                        spaceBefore=8, spaceAfter=5)))
    rows = []
    half = (len(C.ABBREVIATIONS) + 1) // 2
    for i in range(half):
        l = C.ABBREVIATIONS[i]
        r = C.ABBREVIATIONS[half + i] if half + i < len(C.ABBREVIATIONS) else ("", "")
        rows.append([Paragraph(f'<font name="Sans-B" size="8.5">{l[0]}</font>',
                               ParagraphStyle("ak", fontSize=8.5)),
                     Paragraph(l[1], ParagraphStyle("av", fontSize=8.5)),
                     Paragraph(f'<font name="Sans-B" size="8.5">{r[0]}</font>',
                               ParagraphStyle("ak2", fontSize=8.5)),
                     Paragraph(r[1], ParagraphStyle("av2", fontSize=8.5))])
    st.append(Table(rows, colWidths=[17 * mm, 62 * mm, 17 * mm, 62 * mm],
                    style=TableStyle([("TOPPADDING", (0, 0), (-1, -1), 1.5),
                                      ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
                                      ("LEFTPADDING", (0, 0), (-1, -1), 0)])))
    st.append(NextPageTemplate("body"))
    st.append(PageBreak())

    h1n = h2n = 0
    for b in C.BLOCKS:
        k = b[0]
        if k == "h1":
            if b[1] == "References":
                st.append(Paragraph("References", S["h1"]))
            else:
                h1n += 1
                h2n = 0
                st.append(Paragraph(f"{h1n}\u2002\u2002{b[1]}", S["h1"]))
        elif k == "h2":
            h2n += 1
            st.append(Paragraph(f"{h1n}.{h2n}\u2002 {b[1]}", S["h2"]))
        elif k == "p":
            st.append(Paragraph(inline(b[1]), S["body"]))
        elif k == "bullets":
            for it in b[1]:
                st.append(Paragraph(inline(it), S["bul"], bulletText="\u2022"))
            st.append(Spacer(1, 2))
        elif k == "numbers":
            for i, it in enumerate(b[1]):
                st.append(Paragraph(inline(it), ParagraphStyle(
                    "n", parent=S["bul"], bulletFontName="Sans-B", bulletFontSize=10),
                    bulletText=f"{i+1}."))
            st.append(Spacer(1, 2))
        elif k == "code":
            st.append(KeepTogether([Paragraph(b[1], S["codecap"]),
                                    CodeBox(b[2].split("\n"), CW),
                                    Spacer(1, 6)]))
        elif k == "table":
            scale = CW / (sum(b[4]) * 72.0)
            widths = [w * 72 * scale for w in b[4]]
            body = [[Paragraph(f'<font name="Sans-B" size="8.5">{h}</font>',
                               ParagraphStyle("th", fontSize=8.5)) for h in b[2]]]
            for r in b[3]:
                body.append([Paragraph(inline(str(c_)), ParagraphStyle("td", fontSize=8.8,
                                                                       leading=10.2))
                             for c_ in r])
            t = Table(body, colWidths=widths, hAlign="LEFT")
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT),
                                   ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 3),
                                   ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                                   ("TOPPADDING", (0, 0), (-1, -1), 2.6),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6)]))
            st.append(KeepTogether([Paragraph(b[1], S["tabcap"]), t, Spacer(1, 6)]))
        elif k == "figure":
            path = os.path.join(FIG, b[1])
            iw, ih = Image.open(path).size
            w = min(b[3] * 72, CW)
            from reportlab.platypus import Image as RI
            st.append(KeepTogether([Spacer(1, 4), RI(path, width=w, height=w * ih / iw),
                                    Paragraph(b[2], S["cap"])]))
        elif k == "refs":
            for i, r in enumerate(b[1]):
                st.append(Paragraph(f"[{i+1}]\u2002{r}", S["ref"]))
        elif k == "pagebreak":
            st.append(PageBreak())
    return st


def deco(c, d):
    c.saveState()
    c.setFont("Sans", 8)
    c.setFillColor(GREY)
    c.drawString(ML, PH - 13.5 * mm, "TLS 1.3 Client\u2013Server Channel \u00b7 " + C.REPORT_LABEL)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.line(ML, PH - 15.6 * mm, PW - MR, PH - 15.6 * mm)
    c.drawString(ML, MB - 12 * mm, C.DATE)
    c.drawRightString(PW - MR, MB - 12 * mm, str(c.getPageNumber()))
    c.restoreState()


doc = BaseDocTemplate(os.path.join(HERE, "build", "preview-docx.pdf"), pagesize=A4,
                      leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB)
frame = Frame(ML, MB, CW, PH - MT - MB, leftPadding=0, rightPadding=0,
              topPadding=0, bottomPadding=0, id="f")
doc.addPageTemplates([PageTemplate(id="body", frames=[frame], onPage=deco),
                      PageTemplate(id="plain", frames=[frame])])
doc.build(story())
print("done")
