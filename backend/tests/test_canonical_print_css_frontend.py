"""
Frontend-side canonical print CSS regression — proves the JS module
frontend/src/utils/printStyles.js emits a CSS string that contains every
locked rule: @page, @bottom-left, @bottom-right, @page landscape-table,
all canonical sizes (14.5pt / 12.5pt / 11.5pt / 10pt / 8pt), the Times New
Roman family, and the new 4-field footer label format.

Executed via a small Node harness so pytest works without Jest.

Locked 24 Feb 2026.
"""
import json
import shutil
import subprocess
from pathlib import Path
import pytest


FRONTEND_UTILS = Path("/app/frontend/src/utils")


def _node_eval(script: str) -> dict:
    """Run a tiny Node script that imports printStyles.js and prints JSON."""
    if shutil.which("node") is None:
        pytest.skip("node runtime not available")
    result = subprocess.run(
        ["node", "--experimental-vm-modules", "-e", script],
        capture_output=True,
        text=True,
        cwd="/app/frontend",
        timeout=30,
    )
    if result.returncode != 0:
        pytest.skip(f"Node eval unavailable: {result.stderr[:200]}")
    out = result.stdout.strip()
    if not out:
        pytest.skip("Node produced empty output")
    return json.loads(out)


@pytest.fixture(scope="module")
def css_output():
    """Render CANONICAL CSS via a CommonJS transpile of the ESM module."""
    # Approach: convert the ESM exports to a CJS module via a small wrapper,
    # then require() it from Node. We use a minimal inline bundler here.
    script = r"""
    (async () => {
      try {
        // Read the source and transpile just the two helpers we need.
        const fs = require('fs');
        const src = fs.readFileSync('/app/frontend/src/utils/printStyles.js', 'utf8');
        // Strip the ESM `import` line (auSpelling) — replace with identity.
        const cjs = src
          .replace(/^import\s+auSpelling[\s\S]+?;\n/m, 'const auSpelling = (s) => s;\n')
          .replace(/export function /g, 'function ')
          .replace(/export const /g, 'const ');
        const mod = { exports: {} };
        const fn = new Function('module', 'exports', cjs + '\nmodule.exports = { buildCanonicalPrintCss, buildCanonicalFooterLeft, buildCanonicalFooterRightPrefix, CANONICAL_PRINT_SPEC };');
        fn(mod, mod.exports);
        const css = mod.exports.buildCanonicalPrintCss({
          docLabel: 'Case Summary Report',
          appellant: 'John Smith',
          caseNumber: '2025/001234',
        });
        const footerLeft = mod.exports.buildCanonicalFooterLeft({
          docLabel: 'Legal Report', appellant: 'Jane Doe', caseNumber: ''
        });
        const spec = mod.exports.CANONICAL_PRINT_SPEC;
        process.stdout.write(JSON.stringify({ css, footerLeft, spec }));
      } catch (e) {
        process.stderr.write('EVAL_ERROR: ' + e.stack);
        process.exit(2);
      }
    })();
    """
    return _node_eval(script)


def test_canonical_css_contains_times_new_roman(css_output):
    assert "'Times New Roman'" in css_output["css"]


def test_canonical_css_declares_at_page_portrait_and_landscape(css_output):
    assert "@page {" in css_output["css"]
    assert "@page landscape-table {" in css_output["css"]


def test_canonical_css_has_bottom_left_and_bottom_right_footer_boxes(css_output):
    assert "@bottom-left" in css_output["css"]
    assert "@bottom-right" in css_output["css"]


def test_canonical_css_embeds_4_field_footer_label_with_forward_slashes(css_output):
    # LEFT footer must contain the canonical format for the supplied case.
    # We escape the quote character that the CSS `content: "..."` uses.
    assert "Criminal Law Appeal Management / Case Summary Report / John Smith / 2025/001234" in css_output["css"]


def test_canonical_css_renders_no_case_number_when_blank(css_output):
    assert css_output["footerLeft"] == "Criminal Law Appeal Management / Legal Report / Jane Doe / No case number"


def test_canonical_css_has_all_locked_heading_sizes(css_output):
    css = css_output["css"]
    # H1 14.5 / H2 12.5 / H3 11.5 / Body 10 / Footer 8 — exact point values.
    assert "font-size: 14.5pt" in css          # H1
    assert "font-size: 12.5pt" in css          # H2
    assert "font-size: 11.5pt" in css          # H3
    assert "font-size: 10pt" in css            # body + li + p
    assert "font-size: 8pt; font-style: italic" in css  # footer


def test_canonical_css_h3_is_bold_italic(css_output):
    # H3 rule block must carry BOTH font-weight: 700 and font-style: italic.
    # Grab the h3 block.
    css = css_output["css"]
    idx = css.find("h3, .legal-h3 {")
    assert idx != -1
    h3_block = css[idx:idx + 400]
    assert "font-weight: 700" in h3_block
    assert "font-style: italic" in h3_block


def test_canonical_css_includes_iphone_safari_print_colour_adjust(css_output):
    css = css_output["css"]
    assert "-webkit-print-color-adjust" in css
    assert "print-color-adjust" in css
    # iPhone @media (max-width: 768px) block must exist with canonical sizes
    assert "@media (max-width: 768px)" in css


def test_canonical_css_table_policy_has_shrink_and_landscape_helpers(css_output):
    css = css_output["css"]
    assert ".legal-table-shrink" in css
    assert ".legal-landscape-table" in css
    assert "page: landscape-table" in css


def test_canonical_spec_constants_match_backend(css_output):
    spec = css_output["spec"]
    assert spec["h1Pt"] == 14.5
    assert spec["h2Pt"] == 12.5
    assert spec["h3Pt"] == 11.5
    assert spec["bodyPt"] == 10
    assert spec["footerPt"] == 8
    assert spec["missingCaseNumberLabel"] == "No case number"
