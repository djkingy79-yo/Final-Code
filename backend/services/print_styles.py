"""
services/print_styles.py — canonical PDF & DOCX style helpers.

Single source of truth for every backend export route:
  - Times New Roman everywhere
  - H1 14.5pt bold · H2 12.5pt bold · H3 11.5pt bold italic · Body 10pt
  - Footer 8pt italic (rendered via services/export_footer.py::NumberedCanvas)
  - Footer LEFT  : Criminal Law Appeal Management / {doc} / {appellant} / {case_no}
  - Footer RIGHT : DD/MM/YYYY · Page X of Y
  - Missing case number → "No case number"
  - Tables: shrink cleanly to 9pt first; fall back to landscape if still
    overflowing (helpers provided).

Locked 24 Feb 2026 per owner spec. Any backend export route that previously
defined its own ParagraphStyle or set its own heading sizes MUST import from
this module instead.
"""
from __future__ import annotations

# Heading / body point sizes — exported constants so tests can assert them.
CANONICAL_H1_PT = 14.5
CANONICAL_H2_PT = 12.5
CANONICAL_H3_PT = 11.5
CANONICAL_H4_PT = 10.5
CANONICAL_BODY_PT = 10
CANONICAL_FOOTER_PT = 8
CANONICAL_FOOTER_COLOUR = "#334155"
CANONICAL_HEADING_COLOUR = "#0f172a"
CANONICAL_H3_COLOUR = "#1e3a8a"
CANONICAL_TABLE_HEADER_BG = "#1e3a8a"
CANONICAL_TABLE_HEADER_FG = "#ffffff"
CANONICAL_TABLE_BORDER = "#94a3b8"
CANONICAL_TABLE_SHRINK_PT = 9
CANONICAL_LINE_HEIGHT = 1.35
CANONICAL_PARA_GAP_PT = 6
MISSING_CASE_NUMBER_LABEL = "No case number"

# Margins (ReportLab expects mm multiples; use `from reportlab.lib.units import mm`
# at the call site). We expose the numeric millimetre values here.
PORTRAIT_MARGINS_MM = {"top": 14, "right": 15, "bottom": 18, "left": 15}
LANDSCAPE_MARGINS_MM = {"top": 12, "right": 14, "bottom": 15, "left": 14}


# ---------------------------------------------------------------------------
# DOCX (python-docx)
# ---------------------------------------------------------------------------

def apply_canonical_docx_styles(doc) -> None:
    """Apply canonical typography to a python-docx Document.

    Sets Normal + Title + Heading 1/2/3 + List Bullet + List Number styles to
    the locked spec. Callers should still use the semantic style names —
    `doc.add_paragraph(..., style='Heading 1')` etc.
    """
    from docx.shared import Pt, RGBColor

    def _rgb(hex_str: str) -> RGBColor:
        h = hex_str.lstrip("#")
        return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    styles = doc.styles

    # Normal / body — 10pt Times New Roman, 1.35 line height, 6pt gap after.
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(CANONICAL_BODY_PT)
    normal.font.color.rgb = _rgb(CANONICAL_HEADING_COLOUR)
    normal.paragraph_format.space_after = Pt(CANONICAL_PARA_GAP_PT)
    normal.paragraph_format.line_spacing = CANONICAL_LINE_HEIGHT

    # Title (cover page) — matched to H1 size so on-screen preview and export agree.
    title = styles["Title"]
    title.font.name = "Times New Roman"
    title.font.size = Pt(CANONICAL_H1_PT)
    title.font.bold = True
    title.font.italic = False
    title.font.color.rgb = _rgb(CANONICAL_HEADING_COLOUR)
    title.paragraph_format.space_after = Pt(CANONICAL_PARA_GAP_PT)

    # Heading 1 — 14.5pt bold.
    h1 = styles["Heading 1"]
    h1.font.name = "Times New Roman"
    h1.font.size = Pt(CANONICAL_H1_PT)
    h1.font.bold = True
    h1.font.italic = False
    h1.font.color.rgb = _rgb(CANONICAL_HEADING_COLOUR)
    h1.paragraph_format.space_before = Pt(10)
    h1.paragraph_format.space_after = Pt(CANONICAL_PARA_GAP_PT)
    h1.paragraph_format.keep_with_next = True
    # page_break_before intentionally FALSE — callers insert page breaks
    # explicitly where needed; forcing it on every H1 produces cover-bleed.
    h1.paragraph_format.page_break_before = False

    # Heading 2 — 12.5pt bold.
    h2 = styles["Heading 2"]
    h2.font.name = "Times New Roman"
    h2.font.size = Pt(CANONICAL_H2_PT)
    h2.font.bold = True
    h2.font.italic = False
    h2.font.color.rgb = _rgb(CANONICAL_HEADING_COLOUR)
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(3)
    h2.paragraph_format.keep_with_next = True

    # Heading 3 — 11.5pt bold + italic.
    h3 = styles["Heading 3"]
    h3.font.name = "Times New Roman"
    h3.font.size = Pt(CANONICAL_H3_PT)
    h3.font.bold = True
    h3.font.italic = True
    h3.font.color.rgb = _rgb(CANONICAL_H3_COLOUR)
    h3.paragraph_format.space_before = Pt(6)
    h3.paragraph_format.space_after = Pt(3)
    h3.paragraph_format.keep_with_next = True

    # List Bullet / List Number — every list item on its own paragraph.
    for list_style_name in ("List Bullet", "List Number"):
        try:
            ls = styles[list_style_name]
        except KeyError:  # pragma: no cover — default python-docx ships both
            continue
        ls.font.name = "Times New Roman"
        ls.font.size = Pt(CANONICAL_BODY_PT)
        ls.font.color.rgb = _rgb(CANONICAL_HEADING_COLOUR)
        ls.paragraph_format.line_spacing = CANONICAL_LINE_HEIGHT
        ls.paragraph_format.left_indent = Pt(18)
        ls.paragraph_format.space_after = Pt(2)


# ---------------------------------------------------------------------------
# PDF (ReportLab)
# ---------------------------------------------------------------------------

def get_canonical_pdf_styles():
    """Return a ReportLab StyleSheet pre-populated with all canonical styles.

    Styles provided:
      - CanonicalTitle (14.5pt bold, centred — cover page)
      - CanonicalH1    (14.5pt bold)
      - CanonicalH2    (12.5pt bold)
      - CanonicalH3    (11.5pt bold italic)
      - CanonicalH4    (10.5pt bold)
      - CanonicalBody  (10pt justified, 6pt gap, 1.35 leading)
      - CanonicalBullet (10pt, indented)
      - CanonicalLawRef (10pt italic, blue, indented)
      - CanonicalCell  (10pt, wrap)
      - CanonicalHeaderCell (10pt bold white — reversed on dark fill)
      - CanonicalCellShrink (9pt — used when a table needs to shrink cleanly)
      - CanonicalFooter (8pt italic, grey — rarely used, footer is painted by NumberedCanvas)
    """
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

    styles = getSampleStyleSheet()

    _body_leading = CANONICAL_BODY_PT * CANONICAL_LINE_HEIGHT

    def _add(name, **kwargs):
        if name in styles:
            # ReportLab's sample sheet sometimes ships a same-named style.
            for k, v in kwargs.items():
                setattr(styles[name], k, v)
        else:
            styles.add(ParagraphStyle(name=name, **kwargs))

    _add(
        "CanonicalTitle",
        fontName="Times-Bold",
        fontSize=CANONICAL_H1_PT,
        leading=CANONICAL_H1_PT * 1.25,
        alignment=TA_CENTER,
        spaceAfter=CANONICAL_PARA_GAP_PT,
        textColor=colors.HexColor(CANONICAL_HEADING_COLOUR),
    )
    _add(
        "CanonicalH1",
        fontName="Times-Bold",
        fontSize=CANONICAL_H1_PT,
        leading=CANONICAL_H1_PT * 1.25,
        spaceBefore=10,
        spaceAfter=CANONICAL_PARA_GAP_PT,
        textColor=colors.HexColor(CANONICAL_HEADING_COLOUR),
        keepWithNext=True,
    )
    _add(
        "CanonicalH2",
        fontName="Times-Bold",
        fontSize=CANONICAL_H2_PT,
        leading=CANONICAL_H2_PT * 1.3,
        spaceBefore=8,
        spaceAfter=3,
        textColor=colors.HexColor(CANONICAL_HEADING_COLOUR),
        keepWithNext=True,
    )
    _add(
        "CanonicalH3",
        # ReportLab fallback: "Times-BoldItalic" is a PDF base-14 font name.
        fontName="Times-BoldItalic",
        fontSize=CANONICAL_H3_PT,
        leading=CANONICAL_H3_PT * 1.3,
        spaceBefore=6,
        spaceAfter=3,
        textColor=colors.HexColor(CANONICAL_H3_COLOUR),
        keepWithNext=True,
    )
    _add(
        "CanonicalH4",
        fontName="Times-Bold",
        fontSize=CANONICAL_H4_PT,
        leading=CANONICAL_H4_PT * 1.3,
        spaceBefore=4,
        spaceAfter=2,
        textColor=colors.HexColor("#1e293b"),
        keepWithNext=True,
    )
    _add(
        "CanonicalBody",
        fontName="Times-Roman",
        fontSize=CANONICAL_BODY_PT,
        leading=_body_leading,
        alignment=TA_JUSTIFY,
        spaceAfter=CANONICAL_PARA_GAP_PT,
        textColor=colors.HexColor(CANONICAL_HEADING_COLOUR),
    )
    _add(
        "CanonicalBullet",
        fontName="Times-Roman",
        fontSize=CANONICAL_BODY_PT,
        leading=_body_leading,
        leftIndent=18,
        bulletIndent=9,
        spaceAfter=3,
        textColor=colors.HexColor(CANONICAL_HEADING_COLOUR),
    )
    _add(
        "CanonicalLawRef",
        fontName="Times-Italic",
        fontSize=CANONICAL_BODY_PT,
        leading=_body_leading,
        leftIndent=18,
        spaceAfter=2,
        textColor=colors.HexColor("#1e40af"),
    )
    _add(
        "CanonicalCell",
        fontName="Times-Roman",
        fontSize=CANONICAL_BODY_PT,
        leading=CANONICAL_BODY_PT * 1.25,
        wordWrap="CJK",
    )
    _add(
        "CanonicalHeaderCell",
        fontName="Times-Bold",
        fontSize=CANONICAL_BODY_PT,
        leading=CANONICAL_BODY_PT * 1.25,
        textColor=colors.white,
    )
    _add(
        "CanonicalCellShrink",
        fontName="Times-Roman",
        fontSize=CANONICAL_TABLE_SHRINK_PT,
        leading=CANONICAL_TABLE_SHRINK_PT * 1.2,
        wordWrap="CJK",
    )
    _add(
        "CanonicalFooter",
        fontName="Times-Italic",
        fontSize=CANONICAL_FOOTER_PT,
        leading=CANONICAL_FOOTER_PT * 1.25,
        textColor=colors.HexColor(CANONICAL_FOOTER_COLOUR),
    )
    return styles


def build_canonical_table_style(*, shrink: bool = False):
    """Standard TableStyle for every PDF legal-report table."""
    from reportlab.lib import colors
    from reportlab.platypus import TableStyle

    body_pt = CANONICAL_TABLE_SHRINK_PT if shrink else CANONICAL_BODY_PT
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(CANONICAL_TABLE_HEADER_BG)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), body_pt),
        ("LEADING", (0, 0), (-1, -1), body_pt * 1.25),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(CANONICAL_TABLE_BORDER)),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("REPEATROWS", (0, 0), (-1, 0), 1),  # header on every page
    ])


def canonical_page_margins_mm(*, landscape: bool = False) -> dict:
    return LANDSCAPE_MARGINS_MM if landscape else PORTRAIT_MARGINS_MM
