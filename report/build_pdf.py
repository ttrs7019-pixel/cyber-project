"""Render the technical report to PDF (A4) with ReportLab."""
import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether,
                                NextPageTemplate, PageBreak, Flowable)
from reportlab.platypus.tableofcontents import TableOfContents

import content as C

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
FIGDIR = os.path.join(HERE, "figures")

# ------------------------------------------------------------------ fonts
FONTS = {
    "Serif": "SourceSerif4-Regular.ttf",
    "Serif-Semi": "SourceSerif4-Semibold.ttf",
    "Serif-Bold": "SourceSerif4-Bold.ttf",
    "Serif-It": "SourceSerif4-Italic.ttf",
    "Sans": "IBMPlexSans-Regular.ttf",
    "Sans-Med": "IBMPlexSans-Medium.ttf",
    "Sans-Semi": "IBMPlexSans-SemiBold.ttf",
    "Sans-Bold": "IBMPlexSans-Bold.ttf",
    "Sans-It": "IBMPlexSans-Italic.ttf",
    "Mono": "IBMPlexMono-Regular.ttf",
    "Mono-Med": "IBMPlexMono-Medium.ttf",
}
for name, fn in FONTS.items():
    pdfmetrics.registerFont(TTFont(name, os.path.join(ASSETS, fn)))

pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-Bold",
                              italic="Serif-It", boldItalic="Serif-Bold")
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Semi",
                              italic="Sans-It", boldItalic="Sans-Semi")
pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono-Med",
                              italic="Mono", boldItalic="Mono-Med")

# ------------------------------------------------------------------ palette
NAVY = colors.HexColor("#1F3A5F")
SLATE = colors.HexColor("#44546A")
GREY = colors.HexColor("#8A94A6")
RULE = colors.HexColor("#C9D2DE")
LIGHT = colors.HexColor("#EDF1F6")
INK = colors.HexColor("#1A1A1A")
RUST = colors.HexColor("#9C3B2E")

TOC_MAP = {}
BODY_OFFSET = 0

PW, PH = A4
ML, MR = 24 * mm, 22 * mm
MT, MB = 20.5 * mm, 18.5 * mm
CW = PW - ML - MR          # content width

# ------------------------------------------------------------------ styles
S = StyleSheet1()

S.add(ParagraphStyle("Body", fontName="Serif", fontSize=9.2, leading=12.85,
                     textColor=INK, alignment=TA_JUSTIFY, spaceBefore=0,
                     spaceAfter=4.6, firstLineIndent=0))
S.add(ParagraphStyle("BodyFirst", parent=S["Body"], spaceBefore=1))
S.add(ParagraphStyle("H1", fontName="Sans-Semi", fontSize=12.4, leading=15,
                     textColor=NAVY, spaceBefore=10, spaceAfter=4.5,
                     keepWithNext=1))
S.add(ParagraphStyle("H2", fontName="Sans-Semi", fontSize=10.0, leading=12.8,
                     textColor=SLATE, spaceBefore=7.5, spaceAfter=2.6,
                     keepWithNext=1))
S.add(ParagraphStyle("Bullet", parent=S["Body"], leftIndent=11, bulletIndent=2.5,
                     spaceAfter=3.4, bulletFontName="Sans", bulletFontSize=7.4))
S.add(ParagraphStyle("Num", parent=S["Body"], leftIndent=15, bulletIndent=0,
                     spaceAfter=3.6, bulletFontName="Sans-Semi", bulletFontSize=8.6))
S.add(ParagraphStyle("Cap", fontName="Sans", fontSize=7.9, leading=10.9,
                     textColor=SLATE, alignment=TA_CENTER, spaceBefore=4.5,
                     spaceAfter=7))
S.add(ParagraphStyle("TabCap", parent=S["Cap"], alignment=TA_LEFT,
                     spaceBefore=4, spaceAfter=4.5))
S.add(ParagraphStyle("Code", fontName="Mono", fontSize=7.2, leading=10.0,
                     textColor=INK, alignment=TA_LEFT))
S.add(ParagraphStyle("CodeCap", fontName="Sans", fontSize=7.8, leading=10,
                     textColor=SLATE, alignment=TA_LEFT, spaceBefore=0,
                     spaceAfter=3))
S.add(ParagraphStyle("Ref", fontName="Serif", fontSize=8.9, leading=12.0,
                     textColor=INK, alignment=TA_LEFT, leftIndent=13,
                     firstLineIndent=-13, spaceAfter=5))
S.add(ParagraphStyle("CallTitle", fontName="Sans-Semi", fontSize=8.6,
                     leading=11, textColor=NAVY, spaceAfter=2))
S.add(ParagraphStyle("CallBody", fontName="Serif", fontSize=8.9, leading=12.4,
                     textColor=INK, alignment=TA_JUSTIFY))
# cover + front matter
S.add(ParagraphStyle("CovLabel", fontName="Sans-Semi", fontSize=8.4,
                     leading=10, textColor=SLATE, alignment=TA_LEFT))
S.add(ParagraphStyle("CovTitle", fontName="Sans-Semi", fontSize=27,
                     leading=32, textColor=NAVY, alignment=TA_LEFT,
                     spaceAfter=0))
S.add(ParagraphStyle("CovSub", fontName="Serif-It", fontSize=11.6, leading=15.6,
                     textColor=SLATE, alignment=TA_LEFT))
S.add(ParagraphStyle("CovMetaK", fontName="Sans-Med", fontSize=8.6, leading=11,
                     textColor=SLATE, alignment=TA_LEFT))
S.add(ParagraphStyle("CovMetaV", fontName="Sans", fontSize=8.6, leading=11,
                     textColor=INK, alignment=TA_LEFT))
S.add(ParagraphStyle("TocTitle", fontName="Sans-Semi", fontSize=15, leading=18,
                     textColor=NAVY, spaceAfter=14))
S.add(ParagraphStyle("Small", fontName="Sans", fontSize=8.2, leading=11.4,
                     textColor=SLATE))
S.add(ParagraphStyle("TocEntry", fontName="Serif", fontSize=9.0, leading=14.6))
S.add(ParagraphStyle("TocEntrySub", parent=S["TocEntry"], fontSize=8.6,
                     leftIndent=12))
S.add(ParagraphStyle("AbbrRow", fontName="Serif", fontSize=8.1, leading=10.4,
                     textColor=INK))


# ------------------------------------------------------------------ helpers
def inline(text):
    """Convert **bold** and `mono` markers to ReportLab markup."""
    out = []
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if part.startswith("**") and part.endswith("**"):
            out.append(f'<font name="Sans-Semi">{part[2:-2]}</font>')
        elif part.startswith("`") and part.endswith("`"):
            out.append(f'<font name="Mono" size="8.8">{part[1:-1]}</font>')
        else:
            out.append(part.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return "".join(out)


class Rule(Flowable):
    def __init__(self, width, thickness=0.6, color=RULE, space_before=0,
                 space_after=0):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.color = color
        self.sb = space_before
        self.sa = space_after
        self.height = thickness + space_before + space_after

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        y = self.sa + self.thickness / 2
        self.canv.line(0, y, self.width, y)


class CodeBox(Flowable):
    """A mono code block on a light panel, no wrapping (lines are short)."""

    def __init__(self, text, width, pad=6):
        Flowable.__init__(self)
        self.lines = text.split("\n")
        self.width = width
        self.pad = pad
        self.fs = 7.2
        self.lead = 10.0
        self.height = len(self.lines) * self.lead + 2 * pad

    def draw(self):
        c = self.canv
        c.setFillColor(LIGHT)
        c.setStrokeColor(colors.HexColor("#D8DFE8"))
        c.setLineWidth(0.6)
        c.roundRect(0, 0, self.width, self.height, 2.2, stroke=1, fill=1)
        c.setFillColor(colors.HexColor("#2A3F5F"))
        c.setFont("Mono", self.fs)
        y = self.height - self.pad - self.fs
        for ln in self.lines:
            c.drawString(self.pad + 1, y, ln)
            y -= self.lead


def code_block(caption, text):
    return KeepTogether([
        Paragraph(caption, S["CodeCap"]),
        CodeBox(text, CW),
        Spacer(1, 8),
    ])


def figure(fn, caption, width_in):
    from PIL import Image
    path = os.path.join(FIGDIR, fn)
    iw, ih = Image.open(path).size
    w = min(width_in * 72, CW)
    h = w * ih / iw
    from reportlab.platypus import Image as RLImage
    return KeepTogether([
        Spacer(1, 3),
        RLImage(path, width=w, height=h),
        Paragraph(caption, S["Cap"]),
    ])


def data_table(caption, header, rows, widths_in, font_size=8.0):
    scale = CW / (sum(widths_in) * 72)
    widths = [w * 72 * scale for w in widths_in]
    body = [[Paragraph(f'<font name="Sans-Semi" size="7.9" color="#1F3A5F">{h}</font>',
                       ParagraphStyle("th", fontName="Sans-Semi", leading=10.4))
             for h in header]]
    for r in rows:
        body.append([Paragraph(inline(str(cell)), ParagraphStyle(
            "td", fontName="Serif", fontSize=font_size, leading=10.9,
            textColor=INK)) for cell in r])

    t = Table(body, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
        ("LINEBELOW", (0, 0), (-1, 0), 0.7, NAVY),
        ("LINEBELOW", (0, 1), (-1, -2), 0.35, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.7, RULE),
        ("LINEABOVE", (0, 1), (-1, 1), 0.35, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
    ]))
    return KeepTogether([Paragraph(caption, S["TabCap"]), t, Spacer(1, 9)])


def callout(title, text):
    inner = [Paragraph(title, S["CallTitle"]), Paragraph(inline(text), S["CallBody"])]
    t = Table([[inner]], colWidths=[CW], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F9FC")),
        ("LINEBEFORE", (0, 0), (0, -1), 2.0, NAVY),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#DCE3EC")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return KeepTogether([Spacer(1, 2), t, Spacer(1, 9)])



class Leader(Flowable):
    """One table-of-contents line: label, dot leaders, page number."""

    def __init__(self, label, page, width, indent=0, bold=False, size=9.0,
                 leading=15.2, color=INK):
        Flowable.__init__(self)
        self.label = label
        self.page = str(page)
        self.width = width
        self.indent = indent
        self.bold = bold
        self.size = size
        self.lead = leading
        self.height = leading
        self.color = color

    def draw(self):
        c = self.canv
        fname = "Sans-Semi" if self.bold else "Serif"
        c.setFont(fname, self.size)
        c.setFillColor(self.color)
        x = self.indent
        c.drawString(x, 4.2, self.label)
        lw = c.stringWidth(self.label, fname, self.size)
        c.setFont("Sans", 8.3)
        pw = c.stringWidth(self.page, "Sans", 8.3)
        start = x + lw + 4
        end = self.width - pw - 4
        c.setFillColor(colors.HexColor("#B9C4D2"))
        if end > start:
            c.setFont("Serif", self.size)
            dot = c.stringWidth(".", "Serif", self.size)
            n = int((end - start) / (dot * 2.4))
            c.drawString(start, 4.2, ". " * n)
        c.setFillColor(SLATE)
        c.setFont("Sans", 8.3)
        c.drawRightString(self.width, 4.2, self.page)


# ------------------------------------------------------------------ document
class Report(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if getattr(flowable, "style", None) is not None:
            name = flowable.style.name
            text = getattr(flowable, "_text", "")
            if name in ("H1", "H2") and text:
                plain = re.sub(r"<[^>]+>", "", text).replace("\u2003", " ").strip()
                num, _, title = plain.partition(" ")
                heading = title.strip()
                if name == "H2":
                    key = "h2:" + heading
                else:
                    key = "h1:" + heading
                TOC_MAP[key] = self.page - BODY_OFFSET

    def __init__(self, filename, **kw):
        BaseDocTemplate.__init__(self, filename, pagesize=A4,
                                 leftMargin=ML, rightMargin=MR,
                                 topMargin=MT, bottomMargin=MB,
                                 title=C.TITLE, author="", subject=C.SUBTITLE,
                                 creator="", **kw)
        self.section_counter = [0, 0]
        self.fig_no = 0
        self.tab_no = 0
        self.toc_entries = []

        cover_frame = Frame(ML, MB, CW, PH - MT - MB, id="cover",
                            leftPadding=0, rightPadding=0, topPadding=0,
                            bottomPadding=0)
        body_frame = Frame(ML, MB, CW, PH - MT - MB, id="body",
                           leftPadding=0, rightPadding=0, topPadding=0,
                           bottomPadding=0)
        front_frame = Frame(ML, MB, CW, PH - MT - MB, id="front",
                            leftPadding=0, rightPadding=0, topPadding=0,
                            bottomPadding=0)

        cover = PageTemplate(id="Cover", frames=[cover_frame],
                             onPage=self.draw_cover_bg)
        front = PageTemplate(id="Front", frames=[front_frame],
                             onPage=self.draw_front)
        body = PageTemplate(id="Body", frames=[body_frame],
                            onPage=self.draw_body)
        self.addPageTemplates([cover, front, body])

    # ---------------------------------------------------------- decoration
    def draw_cover_bg(self, canv, doc):
        canv.saveState()
        canv.setFillColor(colors.HexColor("#F4F7FA"))
        canv.rect(0, 0, PW, PH, stroke=0, fill=1)
        canv.setFillColor(NAVY)
        canv.rect(0, PH - 21 * mm, PW, 21 * mm, stroke=0, fill=1)
        canv.setFillColor(colors.HexColor("#2C4E77"))
        canv.rect(0, PH - 23.6 * mm, PW, 2.6 * mm, stroke=0, fill=1)

        canv.setFillColor(colors.HexColor("#FFFFFF"))
        canv.setFont("Sans-Semi", 8.6)
        canv.drawString(ML, PH - 13 * mm, C.REPORT_LABEL)
        canv.setFont("Sans", 8.6)
        canv.drawRightString(PW - MR, PH - 13 * mm, C.DATE)

        # faint vertical hairlines in the right margin band only
        canv.setStrokeColor(colors.HexColor("#DCE4EE"))
        canv.setLineWidth(0.7)
        for i in range(5):
            x = PW - MR + 1.2 * mm + i * 1.7 * mm
            canv.line(x, 40 * mm, x, PH - 40 * mm)
        canv.restoreState()

    def draw_front(self, canv, doc):
        canv.saveState()
        canv.setFont("Sans", 7.8)
        canv.setFillColor(GREY)
        canv.drawString(ML, PH - 13.5 * mm, "TLS 1.3 Client\u2013Server Channel \u00b7 " + C.REPORT_LABEL)
        canv.setFillColor(colors.HexColor("#C9D2DE"))
        canv.setLineWidth(0.5)
        canv.line(ML, PH - 15.6 * mm, PW - MR, PH - 15.6 * mm)
        canv.restoreState()

    def draw_body(self, canv, doc):
        canv.saveState()
        canv.setFont("Sans", 7.8)
        canv.setFillColor(GREY)
        canv.drawString(ML, PH - 13.5 * mm,
                        "TLS 1.3 Client\u2013Server Channel \u00b7 " + C.REPORT_LABEL)
        canv.setFillColor(colors.HexColor("#C9D2DE"))
        canv.setLineWidth(0.5)
        canv.line(ML, PH - 15.6 * mm, PW - MR, PH - 15.6 * mm)
        canv.line(ML, MB - 8 * mm, PW - MR, MB - 8 * mm)
        canv.setFillColor(GREY)
        canv.setFont("Sans", 8)
        canv.drawString(ML, MB - 13.6 * mm, C.DATE)
        canv.drawRightString(PW - MR, MB - 13.6 * mm,
                             str(canv.getPageNumber() - BODY_OFFSET))
        canv.restoreState()

    # ---------------------------------------------------------- story
    def cover(self):
        f = []
        f.append(Spacer(1, 44 * mm))
        f.append(Paragraph("SECURE COMMUNICATION \u00b7 APPLICATION SECURITY",
                           S["CovLabel"]))
        f.append(Spacer(1, 5 * mm))
        f.append(Rule(28 * mm, 1.6, NAVY, space_after=0))
        f.append(Spacer(1, 7 * mm))
        f.append(Paragraph(C.TITLE, S["CovTitle"]))
        f.append(Spacer(1, 6.5 * mm))
        f.append(Paragraph(C.SUBTITLE, S["CovSub"]))
        f.append(Spacer(1, 34 * mm))

        rows = []
        for k, v in C.DOC_META:
            rows.append([Paragraph(k, S["CovMetaK"]),
                         Paragraph(v, S["CovMetaV"])])
        t = Table(rows, colWidths=[36 * mm, 96 * mm], hAlign="LEFT")
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4.6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4.6),
            ("LINEBELOW", (1, 0), (1, -1), 0.5, colors.HexColor("#B9C4D2")),
            ("LINEBELOW", (0, 0), (0, -1), 0, colors.white),
        ]))
        f.append(t)
        f.append(Spacer(1, 26 * mm))
        f.append(Rule(CW, 0.6, RULE))
        f.append(Spacer(1, 4 * mm))
        meta = Table([[Paragraph("Submission: " + C.DATE, S["Small"]),
                       Paragraph(C.REPORT_LABEL.title() + " \u00b7 " + C.VERSION,
                                 ParagraphStyle("smr", parent=S["Small"],
                                                alignment=TA_RIGHT))]],
                     colWidths=[CW / 2, CW / 2], hAlign="LEFT")
        meta.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                                  ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                  ("TOPPADDING", (0, 0), (-1, -1), 0),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        f.append(meta)
        return f

    def front_matter(self):
        f = []
        f.append(Paragraph("Contents", S["TocTitle"]))
        for num, title, page in C.CONTENTS:
            if num == "":
                f.append(Spacer(1, 1.5))
                f.append(Leader(title, page, CW, bold=True, size=9.4))
            elif "." in num:
                f.append(Leader(title, page, CW, indent=15, size=8.8, leading=13.4,
                                color=colors.HexColor("#33415A")))
            else:
                f.append(Spacer(1, 1.2))
                f.append(Leader(f"{num}\u2002\u2002{title}", page, CW, bold=True, size=9.4,
                                leading=15.6))

        f.append(Spacer(1, 7 * mm))
        f.append(Rule(CW, 0.5, RULE))
        f.append(Spacer(1, 4.5 * mm))

        def listing(items):
            rows_ = []
            for num, title, page in items:
                rows_.append([
                    Paragraph(f'<font name="Sans-Med" size="8.2" color="#44546A">{num}</font>'
                              f'\u2002{title}',
                              ParagraphStyle("li", fontName="Serif", fontSize=8.2,
                                             leading=11.6, textColor=INK)),
                    Paragraph(page, ParagraphStyle("lir", fontName="Sans", fontSize=8.2,
                                                   leading=11.6, textColor=GREY,
                                                   alignment=TA_RIGHT)),
                ])
            t_ = Table(rows_, colWidths=[(CW / 2) - 34, 16], hAlign="LEFT")
            t_.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1.4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.4),
            ]))
            return t_

        def head(txt):
            return Paragraph(txt, ParagraphStyle(
                "lh", fontName="Sans-Semi", fontSize=9.0, leading=11.6,
                textColor=NAVY, spaceAfter=4.5))

        left_col = [head("Figures"), listing(C.FIGURES)]
        right_col = [head("Tables"), listing(C.TABLES)]
        t2 = Table([[left_col, right_col]], colWidths=[CW / 2, CW / 2], hAlign="LEFT")
        t2.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                                ("TOPPADDING", (0, 0), (-1, -1), 0),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        f.append(t2)

        f.append(Spacer(1, 7 * mm))
        f.append(Rule(CW, 0.5, RULE))
        f.append(Spacer(1, 4.5 * mm))
        f.append(Paragraph("Abbreviations", ParagraphStyle(
            "lh2", fontName="Sans-Semi", fontSize=9.2, leading=12,
            textColor=NAVY, spaceAfter=6)))
        rows = [[Paragraph(f'<font name="Sans-Semi" size="8.4">{a}</font>', S["AbbrRow"]),
                 Paragraph(b, S["AbbrRow"])] for a, b in C.ABBREVIATIONS]
        half = (len(rows) + 1) // 2
        grid = []
        for i in range(half):
            left = rows[i]
            right = rows[half + i] if half + i < len(rows) else ["", ""]
            grid.append([left[0], left[1], right[0], right[1]])
        t4 = Table(grid, colWidths=[17 * mm, 62 * mm, 17 * mm, 62 * mm], hAlign="LEFT")
        t4.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                                ("TOPPADDING", (0, 0), (-1, -1), 1.8),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8)]))
        f.append(t4)
        return f

    def build_story(self):
        story = []
        story.append(NextPageTemplate("Front"))
        story += self.cover()
        story.append(PageBreak())
        story += self.front_matter()
        story.append(NextPageTemplate("Body"))
        story.append(PageBreak())

        h1 = h2 = 0
        for block in C.BLOCKS:
            kind = block[0]
            if kind == "h1":
                if block[1] == "References":
                    story.append(Paragraph(block[1], S["H1"]))
                else:
                    h1 += 1
                    h2 = 0
                    story.append(Paragraph(f"{h1}\u2002\u2002{block[1]}", S["H1"]))
            elif kind == "h2":
                h2 += 1
                story.append(Paragraph(f"{h1}.{h2}\u2002\u2002{block[1]}", S["H2"]))
            elif kind == "p":
                story.append(Paragraph(inline(block[1]), S["Body"]))
            elif kind == "bullets":
                for i, item in enumerate(block[1]):
                    story.append(Paragraph(inline(item), S["Bullet"],
                                           bulletText="\u2022"))
                story.append(Spacer(1, 3))
            elif kind == "numbers":
                for i, item in enumerate(block[1]):
                    story.append(Paragraph(inline(item), S["Num"],
                                           bulletText=f"{i + 1}."))
                story.append(Spacer(1, 3))
            elif kind == "code":
                story.append(code_block(block[1], block[2]))
            elif kind == "table":
                story.append(data_table(block[1], block[2], block[3], block[4]))
            elif kind == "figure":
                story.append(figure(block[1], block[2], block[3]))
            elif kind == "callout":
                story.append(callout(block[1], block[2]))
            elif kind == "refs":
                for i, r in enumerate(block[1]):
                    story.append(Paragraph(f"[{i + 1}]\u2002{r}", S["Ref"]))
            elif kind == "pagebreak":
                story.append(PageBreak())
        return story


if __name__ == "__main__":
    out = os.path.join(HERE, "build", "TLS-1.3-Technical-Report.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc = Report(out)
    doc.build(doc.build_story())
    print("written", out)
