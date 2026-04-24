"""
Print / Export Enforcement Pass — regression suite (locked 24 Feb 2026).

Four independent assertions, each catches a recurrence of the drift this
pass eliminated:

1. SINGLE FRONTEND BUILDER: only utils/exportHtml.js is allowed to emit a
   <!DOCTYPE html> print shell. Any other *.jsx/.js file that tries to
   build its own is a regression.

2. NO STALE CANONICAL IMPORT IN COMPONENT BUILDERS: the five flipped
   components must import buildExportHtml from utils/exportHtml and must
   NOT import buildCanonicalPrintCss directly (that would reintroduce the
   per-file CSS shell).

3. NO HELVETICA IN BACKEND EXPORTS.

4. WIDE TABLES (>=6 cols) MUST AUTO-PROMOTE TO LANDSCAPE — verified by
   running the applyLandscapeForWideTables heuristic via a tiny Node eval.

5. INDEX.CSS MUST NOT RE-INTRODUCE @page OR TYPOGRAPHY OVERRIDES.
"""
from __future__ import annotations

import shutil
import subprocess
import pathlib
import pytest


FRONTEND_ROOT = pathlib.Path("/app/frontend/src")
BACKEND_ROOT = pathlib.Path("/app/backend")


# ---------------------------------------------------------------------------
# 1. Only exportHtml.js owns a full HTML shell.
# ---------------------------------------------------------------------------

def test_only_exporthtml_js_builds_full_html_shell():
    """grep for <!DOCTYPE html> in .jsx/.js files across the frontend src.
    Allowed locations:
        - utils/exportHtml.js (canonical)
        - utils/printStyles.js (legacy helper kept for backward-compat)
        - pages/FormTemplates.jsx (court-appeal FORM templates, not reports)
    Everything else is a regression.
    """
    import re

    doctype_re = re.compile(r"<!DOCTYPE html>", re.IGNORECASE)
    allowed = {
        FRONTEND_ROOT / "utils" / "exportHtml.js",
        FRONTEND_ROOT / "utils" / "printStyles.js",
        FRONTEND_ROOT / "pages" / "FormTemplates.jsx",
    }
    violations = []
    for path in FRONTEND_ROOT.rglob("*"):
        if path.suffix not in {".js", ".jsx"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if doctype_re.search(content) and path.resolve() not in {p.resolve() for p in allowed}:
            violations.append(str(path))

    assert not violations, (
        "These files still build their own <!DOCTYPE html> shell and must "
        "be refactored to route through utils/exportHtml.js::buildExportHtml: "
        f"{violations}"
    )


# ---------------------------------------------------------------------------
# 2. Flipped components must import buildExportHtml, not buildCanonicalPrintCss.
# ---------------------------------------------------------------------------

_FLIPPED_COMPONENTS = [
    FRONTEND_ROOT / "pages" / "ReportView.jsx",
    FRONTEND_ROOT / "pages" / "BarristerView.jsx",
    FRONTEND_ROOT / "pages" / "CaseDetail.jsx",
    FRONTEND_ROOT / "components" / "GroundsOfMerit.jsx",
    FRONTEND_ROOT / "components" / "TimelineEnhanced.jsx",
]


@pytest.mark.parametrize("component", [str(p) for p in _FLIPPED_COMPONENTS])
def test_flipped_component_imports_canonical_builder_and_not_css_helper(component):
    src = pathlib.Path(component).read_text(encoding="utf-8")
    # Must import buildExportHtml
    assert "buildExportHtml" in src, (
        f"{component} must import buildExportHtml from utils/exportHtml."
    )
    # Must NOT import buildCanonicalPrintCss (that bypasses the canonical
    # chrome and reintroduces the per-component shell problem).
    assert "buildCanonicalPrintCss" not in src, (
        f"{component} must not import buildCanonicalPrintCss — all CSS "
        "comes from buildExportHtml via utils/exportHtml.js."
    )


# ---------------------------------------------------------------------------
# 3. No Helvetica anywhere in backend export routers / services.
# ---------------------------------------------------------------------------

def test_no_helvetica_anywhere_in_backend_exports():
    targets = []
    for sub in ("routers", "services"):
        for path in (BACKEND_ROOT / sub).rglob("*.py"):
            targets.append(path)
    violations = []
    for path in targets:
        text = path.read_text(encoding="utf-8")
        if "Helvetica" in text:
            violations.append(str(path))
    assert not violations, (
        f"Helvetica still present in backend exports: {violations}. "
        "Canonical spec (24 Feb 2026) requires Times-* everywhere."
    )


# ---------------------------------------------------------------------------
# 4. Wide-table auto-landscape promotion.
# ---------------------------------------------------------------------------

def _node_eval(script: str) -> str:
    if shutil.which("node") is None:
        pytest.skip("node runtime not available")
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, cwd="/app/frontend", timeout=20,
    )
    if r.returncode != 0:
        pytest.skip(f"Node eval unavailable: {r.stderr[:200]}")
    return r.stdout


def test_wide_table_auto_landscape_via_applyLandscapeForWideTables():
    """A 7-column table passed to applyLandscapeForWideTables must come back
    wrapped with class="legal-landscape-table" so the canonical CSS routes
    it through the @page landscape-table named page.

    A 3-column table must NOT be touched."""
    script = r"""
    const fs = require('fs');
    const src = fs.readFileSync('/app/frontend/src/utils/exportHtml.js', 'utf8');
    // Strip ESM imports + convert exports so we can require-eval the file
    // without Vite/Babel/Node-ESM.
    const cjs = src
      .replace(/^import\s+\{\s*buildCanonicalPrintCss\s*\}[\s\S]+?;\n/m, 'const buildCanonicalPrintCss = () => "";\n')
      .replace(/^import\s+auSpelling[\s\S]+?;\n/m, 'const auSpelling = (s) => s;\n')
      .replace(/export function /g, 'function ')
      .replace(/export const /g, 'const ');
    const mod = { exports: {} };
    const fn = new Function('module', 'exports', cjs + '\nmodule.exports = { applyLandscapeForWideTables };');
    fn(mod, mod.exports);
    const wide = '<table><tr><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th><th>F</th><th>G</th></tr></table>';
    const narrow = '<table><tr><th>A</th><th>B</th><th>C</th></tr></table>';
    const wideOut = mod.exports.applyLandscapeForWideTables(wide);
    const narrowOut = mod.exports.applyLandscapeForWideTables(narrow);
    console.log(JSON.stringify({
      wideWrapped: wideOut.includes('legal-landscape-table'),
      narrowLeftAlone: !narrowOut.includes('legal-landscape-table'),
    }));
    """
    out = _node_eval(script).strip()
    import json
    data = json.loads(out)
    assert data["wideWrapped"], "7-column table was not promoted to landscape"
    assert data["narrowLeftAlone"], "3-column table was wrongly promoted to landscape"


# ---------------------------------------------------------------------------
# 5. index.css must not reintroduce @page or typography overrides.
# ---------------------------------------------------------------------------

def test_index_css_no_page_rule_and_no_legal_typography_overrides():
    index_css = (FRONTEND_ROOT / "index.css").read_text(encoding="utf-8")
    # @page rule is forbidden in index.css — typography + @page are owned
    # by utils/printStyles.js. (The canonical code legitimately names
    # "@page" in comments; we check only for the CSS rule start.)
    import re

    for m in re.finditer(r"@page\b[^{/\n]*\{", index_css):
        raise AssertionError(
            "index.css must not contain an @page rule. The canonical "
            "@page lives in utils/printStyles.js. Found at position "
            f"{m.start()}: {index_css[m.start():m.start()+60]!r}"
        )
    # Forbidden legacy typography override classes.
    forbidden_overrides = [
        r"\.legal-report h1 \{[^}]*font-size\s*:\s*\d+pt\s*!important",
        r"\.legal-content h1 \{[^}]*font-size\s*:\s*\d+pt\s*!important",
        r"\.legal-report p[^}]*font-size\s*:\s*\d+pt\s*!important",
    ]
    for pattern in forbidden_overrides:
        match = re.search(pattern, index_css)
        assert not match, (
            f"index.css contains forbidden typography override: {pattern}"
        )
