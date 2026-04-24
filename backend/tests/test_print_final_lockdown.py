"""
Print / Export FINAL LOCKDOWN regression suite (locked 24 Feb 2026).

Five hard contracts enforced by this file. Each catches a specific class
of drift that would break the canonical spec:

1. ZERO inline non-canonical typography (font-size 11/12/13/14/15/16/18pt)
   inside CaseDetail.jsx's Progress / Bundle builders. Those paths go
   through buildExportHtml(), so any inline `font-size: 12pt` was
   overriding the canonical 10pt body rule.

2. ZERO inline `font-family: 'Times New Roman'` anywhere in component
   bodies — the canonical CSS already applies Times New Roman universally.

3. CANONICAL CSS contains the locked list rules: each bullet/numbered
   item on its own line (`display: list-item` + per-item margin).

4. The `@page landscape-table` rule is present in canonical CSS (wide-
   table policy).

5. The five canonical heading sizes (14.5/12.5/11.5/10.5/10pt) appear
   with the expected weights and italics.
"""
from __future__ import annotations

import re
import pathlib
import pytest


FRONTEND_SRC = pathlib.Path("/app/frontend/src")
PRINT_STYLES_JS = FRONTEND_SRC / "utils" / "printStyles.js"
EXPORT_HTML_JS = FRONTEND_SRC / "utils" / "exportHtml.js"


# ---------------------------------------------------------------------------
# 1. No inline non-canonical font-size in CaseDetail Progress/Bundle paths.
# ---------------------------------------------------------------------------

def test_casedetail_has_no_inline_non_canonical_font_size():
    """CaseDetail.jsx's buildProgressPreviewHtml + buildCompleteBundleHtml
    go through buildExportHtml(). Any inline font-size in pt (other than
    the locked 8pt meta-label / 10pt body / 10.5pt h4 / 11.5pt h3) is a
    regression because it overrides the canonical CSS.

    Allowed pt values inside CaseDetail inline styles:
        - 8pt  (meta labels / footer-adjacent content)
        - 10pt (body)
        - 10.5pt, 11.5pt, 12.5pt, 14.5pt (canonical heading sizes)

    Specifically forbidden (pre-lockdown drift values):
        11pt, 12pt, 13pt, 14pt, 15pt, 16pt, 18pt, 20pt
    """
    src = (FRONTEND_SRC / "pages" / "CaseDetail.jsx").read_text(encoding="utf-8")
    bad = re.findall(r"font-size:\s*(11|12|13|14|15|16|18|20)pt\b", src)
    assert not bad, (
        f"CaseDetail.jsx contains {len(bad)} non-canonical font-size "
        f"overrides ({set(bad)}). These conflict with the canonical "
        "typography applied by buildExportHtml()."
    )


# ---------------------------------------------------------------------------
# 2. No inline font-family: Times New Roman in component bodies.
# ---------------------------------------------------------------------------

# Allowlist: utility sources, FormTemplates (static court forms — outside
# canonical spec per scope), and on-screen <style jsx> blocks in
# ReportView / BarristerView (screen-only, not export). The test asserts
# NO *inline* style="font-family:'Times New Roman'" attributes in component
# bodies — those are the leaks that pre-empt canonical.
def test_no_inline_times_new_roman_font_family_in_component_bodies():
    violations = []
    for path in FRONTEND_SRC.rglob("*.jsx"):
        if any(skip in str(path) for skip in ("utils/", "components/ui/", "FormTemplates.jsx")):
            continue
        text = path.read_text(encoding="utf-8")
        # Only match inline-style attributes, not CSS-in-JS <style jsx>.
        for m in re.finditer(r'style="[^"]*font-family:\s*[\'"]Times[^"]*"', text):
            violations.append((str(path), m.group(0)[:80]))
    assert not violations, (
        f"{len(violations)} inline font-family='Times New Roman' leaks "
        f"found. These override the canonical CSS. First 3:\n" +
        "\n".join(f"  {p}: {s}" for p, s in violations[:3])
    )


# ---------------------------------------------------------------------------
# 3. Canonical list / table / landscape rules in printStyles.js.
# ---------------------------------------------------------------------------

def test_canonical_css_forces_bullets_and_numbered_on_separate_lines():
    """Each bullet / numbered item must render on its own line. The
    canonical CSS achieves this with `display: list-item` + `margin`
    on li, and with paragraph gap on the surrounding ul/ol."""
    css = PRINT_STYLES_JS.read_text(encoding="utf-8")
    # Find the li rule block.
    m = re.search(r"li\s*\{[^}]*\}", css, re.DOTALL)
    assert m, "Canonical li rule missing"
    li_block = m.group(0)
    assert "display: list-item" in li_block, (
        "Canonical li must declare `display: list-item` so each item wraps."
    )
    assert "margin" in li_block, "Canonical li must set margin for separation."

    # And ul/ol must have margin + padding for separation.
    m2 = re.search(r"ul, ol\s*\{[^}]*\}", css, re.DOTALL)
    assert m2, "Canonical ul/ol rule missing"
    ul_block = m2.group(0)
    assert "margin" in ul_block and "padding-left" in ul_block


def test_canonical_css_has_landscape_table_named_page():
    css = PRINT_STYLES_JS.read_text(encoding="utf-8")
    assert "@page landscape-table" in css, (
        "Canonical CSS must declare the @page landscape-table named page "
        "for wide-table escape hatch."
    )
    assert ".legal-landscape-table" in css, (
        "Canonical CSS must declare .legal-landscape-table utility class "
        "that routes wide tables into the landscape named page."
    )


def test_canonical_css_has_all_five_heading_sizes():
    css = PRINT_STYLES_JS.read_text(encoding="utf-8")
    # H1 14.5pt bold
    assert re.search(r"h1,\s*\.legal-h1\s*\{[^}]*font-size:\s*14\.5pt[^}]*font-weight:\s*700", css, re.DOTALL)
    # H2 12.5pt bold
    assert re.search(r"h2,\s*\.legal-h2\s*\{[^}]*font-size:\s*12\.5pt[^}]*font-weight:\s*700", css, re.DOTALL)
    # H3 11.5pt bold italic
    h3_match = re.search(r"h3,\s*\.legal-h3\s*\{([^}]*)\}", css, re.DOTALL)
    assert h3_match, "H3 rule missing"
    h3_block = h3_match.group(1)
    assert "font-size: 11.5pt" in h3_block
    assert "font-weight: 700" in h3_block
    assert "font-style: italic" in h3_block
    # H4 10.5pt bold
    assert re.search(r"h4,\s*\.legal-h4\s*\{[^}]*font-size:\s*10\.5pt", css, re.DOTALL)
    # Body 10pt
    assert re.search(r"p,\s*\.legal-body\s*\{[^}]*font-size:\s*10pt", css, re.DOTALL)


# ---------------------------------------------------------------------------
# 4. Footer format — left and right halves locked.
# ---------------------------------------------------------------------------

def test_canonical_footer_left_and_right_format():
    """Footer left: 'Criminal Law Appeal Management / {doc} / {appellant} / {case_no}'
    Footer right: 'DD/MM/YYYY · Page X of Y'
    Missing case number → 'No case number'."""
    src = PRINT_STYLES_JS.read_text(encoding="utf-8")
    # The builder functions must construct the left half exactly this way.
    assert "Criminal Law Appeal Management" in src
    assert "No case number" in src
    # The @bottom-right content includes 'Page ' + counter(page) + ' of ' + counter(pages)
    assert "counter(page)" in src and "counter(pages)" in src
    # Date is passed in as DD/MM/YYYY format (via buildCanonicalFooterRightPrefix).
    assert "_formatDateShortAU" in src or "formatDateShortAU" in src

    # Right half uses middle-dot separator U+00B7.
    assert "\\00B7" in src or "\u00B7" in src


# ---------------------------------------------------------------------------
# 5. iPhone preview path preserved.
# ---------------------------------------------------------------------------

def test_iphone_document_preview_wrapper_still_exists_and_is_called():
    """DocumentPreviewPage.jsx is the iOS-safe wrapper. Every "print" /
    "PDF preview" action must route through it, not call window.print()
    directly. The only permitted window.print() call in the app is inside
    DocumentPreviewPage itself."""
    preview_page = FRONTEND_SRC / "pages" / "DocumentPreviewPage.jsx"
    assert preview_page.exists(), "DocumentPreviewPage.jsx must exist"

    # Collect every window.print() caller.
    violators = []
    for path in FRONTEND_SRC.rglob("*.jsx"):
        text = path.read_text(encoding="utf-8")
        if "window.print()" in text and path.name != "DocumentPreviewPage.jsx":
            violators.append(str(path))
    assert not violators, (
        f"These files bypass the iOS-safe DocumentPreviewPage by calling "
        f"window.print() directly: {violators}"
    )


# ---------------------------------------------------------------------------
# 6. Backend: zero Helvetica anywhere in export modules.
# ---------------------------------------------------------------------------

def test_backend_has_zero_helvetica_in_exports():
    """Canonical spec is Times New Roman everywhere — no Helvetica."""
    backend_root = pathlib.Path("/app/backend")
    violators = []
    for sub in ("routers", "services"):
        for path in (backend_root / sub).rglob("*.py"):
            if "Helvetica" in path.read_text(encoding="utf-8"):
                violators.append(str(path))
    assert not violators, f"Helvetica still present in: {violators}"
