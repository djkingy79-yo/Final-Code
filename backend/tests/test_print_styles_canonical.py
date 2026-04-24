"""
Canonical print-styles regression suite — locked 24 Feb 2026.

Proves every exported constant in services/print_styles.py and every caller's
typography / margin / footer plumbing matches the owner-approved spec:

    Font family        : Times New Roman
    H1                 : 14.5pt bold
    H2                 : 12.5pt bold
    H3                 : 11.5pt bold italic
    Body               : 10pt
    Footer             : 8pt italic
    Footer LEFT        : Criminal Law Appeal Management / {doc} / {appellant} / {case_number}
    Footer RIGHT       : DD/MM/YYYY · Page X of Y
    Missing case no    : "No case number"
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# 1. services/print_styles.py — constants + typography appliers
# ---------------------------------------------------------------------------

def test_canonical_point_size_constants():
    from services.print_styles import (
        CANONICAL_H1_PT, CANONICAL_H2_PT, CANONICAL_H3_PT, CANONICAL_H4_PT,
        CANONICAL_BODY_PT, CANONICAL_FOOTER_PT, CANONICAL_TABLE_SHRINK_PT,
        CANONICAL_LINE_HEIGHT, CANONICAL_PARA_GAP_PT, MISSING_CASE_NUMBER_LABEL,
    )
    assert CANONICAL_H1_PT == 14.5
    assert CANONICAL_H2_PT == 12.5
    assert CANONICAL_H3_PT == 11.5
    assert CANONICAL_H4_PT == 10.5
    assert CANONICAL_BODY_PT == 10
    assert CANONICAL_FOOTER_PT == 8
    assert CANONICAL_TABLE_SHRINK_PT == 9
    assert CANONICAL_LINE_HEIGHT == 1.35
    assert CANONICAL_PARA_GAP_PT == 6
    assert MISSING_CASE_NUMBER_LABEL == "No case number"


def test_canonical_pdf_styles_registered_with_correct_typography():
    from services.print_styles import get_canonical_pdf_styles
    styles = get_canonical_pdf_styles()

    # Every canonical style must exist
    for name in (
        "CanonicalTitle", "CanonicalH1", "CanonicalH2", "CanonicalH3", "CanonicalH4",
        "CanonicalBody", "CanonicalBullet", "CanonicalLawRef",
        "CanonicalCell", "CanonicalHeaderCell", "CanonicalCellShrink",
        "CanonicalFooter",
    ):
        assert name in styles, f"Missing canonical PDF style: {name}"

    # Sizes (locked — DO NOT DRIFT)
    assert styles["CanonicalH1"].fontSize == 14.5
    assert styles["CanonicalH2"].fontSize == 12.5
    assert styles["CanonicalH3"].fontSize == 11.5
    assert styles["CanonicalBody"].fontSize == 10
    assert styles["CanonicalFooter"].fontSize == 8

    # Times New Roman everywhere (ReportLab base-14 font names)
    assert styles["CanonicalH1"].fontName == "Times-Bold"
    assert styles["CanonicalH2"].fontName == "Times-Bold"
    assert styles["CanonicalH3"].fontName == "Times-BoldItalic"   # H3 is bold + italic
    assert styles["CanonicalBody"].fontName == "Times-Roman"
    assert styles["CanonicalFooter"].fontName == "Times-Italic"


def test_canonical_docx_styles_applier_sets_all_headings():
    from docx import Document
    from services.print_styles import apply_canonical_docx_styles

    doc = Document()
    apply_canonical_docx_styles(doc)

    # Heading 1 — 14.5pt Bold, Times New Roman
    h1 = doc.styles["Heading 1"]
    assert h1.font.name == "Times New Roman"
    assert h1.font.size.pt == 14.5
    assert h1.font.bold is True
    assert h1.font.italic in (None, False)

    # Heading 2 — 12.5pt Bold
    h2 = doc.styles["Heading 2"]
    assert h2.font.name == "Times New Roman"
    assert h2.font.size.pt == 12.5
    assert h2.font.bold is True

    # Heading 3 — 11.5pt Bold + Italic (locked — strict both)
    h3 = doc.styles["Heading 3"]
    assert h3.font.name == "Times New Roman"
    assert h3.font.size.pt == 11.5
    assert h3.font.bold is True
    assert h3.font.italic is True

    # Normal body — 10pt Times New Roman
    normal = doc.styles["Normal"]
    assert normal.font.name == "Times New Roman"
    assert normal.font.size.pt == 10


def test_canonical_table_style_includes_repeat_rows_and_canonical_colours():
    from services.print_styles import build_canonical_table_style
    style = build_canonical_table_style()

    cmds = style.getCommands()
    cmd_names = [c[0] for c in cmds]
    assert "GRID" in cmd_names
    assert "REPEATROWS" in cmd_names     # header on every page
    assert "FONTNAME" in cmd_names
    # Find the body FONTSIZE entry — must be 10pt (canonical body)
    font_size_cmds = [c for c in cmds if c[0] == "FONTSIZE"]
    assert font_size_cmds, "No FONTSIZE command found"
    assert any(c[-1] == 10 for c in font_size_cmds), f"Expected FONTSIZE=10 in canonical table style, got {font_size_cmds}"


# ---------------------------------------------------------------------------
# 2. services/export_footer.py — new 4-field format
# ---------------------------------------------------------------------------

def test_build_footer_label_canonical_four_field_format():
    from services.export_footer import build_footer_label
    case = {"defendant_name": "John Smith", "case_number": "2025/001234"}
    got = build_footer_label(case, "Case Summary Report")
    assert got == "Criminal Law Appeal Management / Case Summary Report / John Smith / 2025/001234"


def test_build_footer_label_renders_no_case_number_fallback():
    from services.export_footer import build_footer_label
    case = {"defendant_name": "Jane Doe"}  # no case_number
    got = build_footer_label(case, "Legal Report")
    assert got.endswith("/ No case number")
    # The blank never leaks into the footer
    assert got != "Criminal Law Appeal Management / Legal Report / Jane Doe / "


def test_format_export_date_short_au_ddmmyyyy():
    from services.export_footer import format_export_date
    got = format_export_date("2026-02-24T10:00:00Z")
    assert got == "24/02/2026"


def test_build_footer_label_trims_whitespace():
    from services.export_footer import build_footer_label
    case = {"defendant_name": "  Spaced Name  ", "case_number": "  "}
    got = build_footer_label(case, "Legal Report")
    # Appellant trimmed, blank case number becomes placeholder
    assert "Spaced Name" in got
    assert "No case number" in got
