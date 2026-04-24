/**
 * ============================================================================
 * CANONICAL PRINT STYLES — single source of truth for every browser print,
 * PDF-via-print, Word-via-HTML, and iPhone Safari preview surface.
 *
 * Authored 24 Feb 2026 per owner-locked spec. Any file that used to hand-roll
 * its own <style> block (ReportView, BarristerView, CaseDetail tab export,
 * GroundsOfMerit, TimelineEnhanced, NotesSection via exportHtml.js) MUST
 * import `buildCanonicalPrintCss` from this module instead.
 *
 * Typography spec (locked — DO NOT DRIFT):
 *   Font family     : 'Times New Roman', Times, serif
 *   H1              : 14.5pt bold
 *   H2              : 12.5pt bold
 *   H3              : 11.5pt bold + italic
 *   Body            : 10pt
 *   Footer          : 8pt italic
 *   Footer LEFT     : Criminal Law Appeal Management / {doc} / {appellant} / {case_no}
 *   Footer RIGHT    : DD/MM/YYYY · Page X of Y
 *   Missing case no : "No case number"
 *   Portrait margin : 14mm top / 15mm sides / 18mm bottom
 *   Landscape margin: 12mm top / 14mm sides / 15mm bottom
 *   Line-height     : 1.35
 *   Paragraph gap   : 6pt
 *
 * Tables policy:
 *   1. Shrink font cleanly to 9pt if necessary.
 *   2. If still overflowing, switch the table (and only the table) to the
 *      named landscape page via `.legal-landscape-table`.
 *   3. Repeat header row on every page (thead display: table-header-group).
 * ============================================================================
 */

import auSpelling from "./auSpelling";

const _escAttr = (s) => String(s ?? "").replace(/"/g, '\\"').replace(/\n/g, " ");

const _formatDateShortAU = (d = new Date()) => {
  const day = String(d.getDate()).padStart(2, "0");
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const year = d.getFullYear();
  return `${day}/${month}/${year}`;
};

/**
 * Build the canonical footer-left string.
 * "Criminal Law Appeal Management / {doc name} / {appellant name} / {case number}"
 * Missing case number → "No case number".
 */
export function buildCanonicalFooterLeft({ docLabel, appellant, caseNumber }) {
  const doc = (docLabel || "Legal Document").trim();
  const app = (appellant || "Appellant").trim();
  const cn = (caseNumber || "").trim() || "No case number";
  return `Criminal Law Appeal Management / ${doc} / ${app} / ${cn}`;
}

/**
 * Build the canonical footer-right string (date portion only — the
 * ` · Page X of Y` suffix is produced by the CSS counter inside @bottom-right).
 */
export function buildCanonicalFooterRightPrefix({ date } = {}) {
  return _formatDateShortAU(date instanceof Date ? date : new Date());
}

/**
 * Produce the full canonical print CSS for an export HTML document.
 * Caller supplies docLabel, appellant, caseNumber so the @page margin boxes
 * can embed the correct footer text on every page.
 */
export function buildCanonicalPrintCss({ docLabel, appellant, caseNumber, date } = {}) {
  const footerLeft = _escAttr(buildCanonicalFooterLeft({ docLabel, appellant, caseNumber }));
  const datePrefix = _escAttr(buildCanonicalFooterRightPrefix({ date }));
  // CSS content string uses "..." so we escape the middle-dot and the
  // embedded counters. Chrome/Safari/Edge all honour @bottom-* content.
  return `
  /* ========================================================================
     CANONICAL PRINT SPEC (locked 24 Feb 2026 — owner-approved)
     Times New Roman · Body 10pt · H1 14.5pt · H2 12.5pt · H3 11.5pt bold italic
     Footer 8pt italic · DO NOT HAND-ROLL ELSEWHERE
     ======================================================================== */
  * { -webkit-text-size-adjust: 100%; text-size-adjust: 100%; box-sizing: border-box; }
  html, body { background: #fff; margin: 0; padding: 0; }
  body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 10pt;
    color: #0f172a;
    line-height: 1.35;
  }

  /* ---------- PORTRAIT (default) ---------- */
  @page {
    size: A4 portrait;
    margin: 14mm 15mm 18mm 15mm;
    @bottom-left {
      content: "${footerLeft}";
      font-family: 'Times New Roman', Times, serif;
      font-size: 8pt; font-style: italic; color: #334155;
    }
    @bottom-right {
      content: "${datePrefix} \\00B7 Page " counter(page) " of " counter(pages);
      font-family: 'Times New Roman', Times, serif;
      font-size: 8pt; font-style: italic; color: #334155;
    }
  }
  /* ---------- LANDSCAPE (named — used by wide tables) ---------- */
  @page landscape-table {
    size: A4 landscape;
    margin: 12mm 14mm 15mm 14mm;
    @bottom-left {
      content: "${footerLeft}";
      font-family: 'Times New Roman', Times, serif;
      font-size: 8pt; font-style: italic; color: #334155;
    }
    @bottom-right {
      content: "${datePrefix} \\00B7 Page " counter(page) " of " counter(pages);
      font-family: 'Times New Roman', Times, serif;
      font-size: 8pt; font-style: italic; color: #334155;
    }
  }

  /* ---------- HEADINGS (canonical sizes, applied universally) ---------- */
  h1, .legal-h1 {
    font-family: 'Times New Roman', Times, serif;
    font-size: 14.5pt; font-weight: 700; font-style: normal;
    color: #0f172a; margin: 0 0 6pt; line-height: 1.25;
    page-break-after: avoid; break-after: avoid;
  }
  h2, .legal-h2 {
    font-family: 'Times New Roman', Times, serif;
    font-size: 12.5pt; font-weight: 700; font-style: normal;
    color: #0f172a; margin: 8pt 0 3pt; line-height: 1.3;
    page-break-after: avoid; break-after: avoid;
  }
  h3, .legal-h3 {
    font-family: 'Times New Roman', Times, serif;
    font-size: 11.5pt; font-weight: 700; font-style: italic;
    color: #1e3a8a; margin: 6pt 0 3pt; line-height: 1.3;
    page-break-after: avoid; break-after: avoid;
  }
  h4, .legal-h4 {
    font-family: 'Times New Roman', Times, serif;
    font-size: 10.5pt; font-weight: 700;
    color: #1e293b; margin: 5pt 0 2pt; line-height: 1.3;
  }

  /* ---------- BODY ---------- */
  p, .legal-body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 10pt; line-height: 1.35; margin: 0 0 6pt;
    orphans: 3; widows: 3; text-align: justify;
  }

  /* ---------- LISTS: each bullet / numbered item always on its own line ---------- */
  ul, ol {
    margin: 4pt 0 6pt; padding-left: 1.4rem;
    font-family: 'Times New Roman', Times, serif;
  }
  li {
    font-size: 10pt !important; line-height: 1.35;
    margin: 0 0 3pt; display: list-item;
    page-break-inside: avoid; break-inside: avoid;
  }
  li > p { margin: 0; display: inline; }

  /* ---------- TABLES (shrink-then-landscape policy) ---------- */
  table, .legal-table {
    width: 100%; border-collapse: collapse; table-layout: fixed;
    margin: 6pt 0 8pt; font-size: 10pt;
    page-break-inside: auto;
  }
  thead { display: table-header-group; } /* repeat header on every page */
  tfoot { display: table-footer-group; }
  th, td {
    border: 0.5pt solid #94a3b8; padding: 3px 5px;
    font-size: 10pt; line-height: 1.3; vertical-align: top;
    word-wrap: break-word; overflow-wrap: break-word; hyphens: auto;
  }
  th {
    background: #1e3a8a !important; color: #ffffff !important;
    font-weight: 700;
    -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;
  }
  /* Tables explicitly marked wide (>5 cols OR >100 char max cell) shrink cleanly. */
  table.legal-table-shrink, table.legal-table-shrink th, table.legal-table-shrink td {
    font-size: 9pt; padding: 2px 4px;
  }
  /* Last-resort landscape — caller adds .legal-landscape-table to the table
     OR to a wrapping <section> that contains the table. Resumes portrait
     automatically on the next flow block. */
  .legal-landscape-table, table.legal-landscape-table {
    page: landscape-table; break-before: page; break-after: page;
  }

  /* ---------- iPhone / small-screen preview parity (sizes stay, padding tightens) ---------- */
  @media (max-width: 768px) {
    body { font-size: 10pt; line-height: 1.35; padding: 0; }
    h1 { font-size: 14.5pt; }
    h2 { font-size: 12.5pt; }
    h3 { font-size: 11.5pt; }
    h4 { font-size: 10.5pt; }
    p, li { font-size: 10pt; line-height: 1.35; }
    table, th, td { font-size: 10pt; }
    table.legal-table-shrink, table.legal-table-shrink th, table.legal-table-shrink td {
      font-size: 9pt;
    }
  }

  /* ---------- iOS SAFARI SPECIFICS ----------
     Safari's print pipeline drops background colours by default; force exact
     rendering on every coloured element. This is the single rule set that
     fixes the long-standing "iPhone print looks different from desktop" bug. */
  @media print {
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
    body { background: #fff; }
    thead, th { display: table-header-group; }
    tr, td, th, li, p { page-break-inside: avoid; break-inside: avoid; }
    .legal-no-print, .no-print { display: none !important; }
  }
  `;
}

/**
 * Wrap a body HTML fragment in a complete standalone HTML document styled
 * with the canonical print CSS. Replaces the legacy buildExportHtml() body
 * while preserving that function's public signature.
 */
export function buildCanonicalExportHtml({
  title,
  docLabel,
  appellant,
  caseNumber,
  bodyHtml,
}) {
  const safeTitle = (title || docLabel || "Document").replace(/</g, "&lt;");
  const css = buildCanonicalPrintCss({ docLabel: docLabel || title, appellant, caseNumber });
  const body = auSpelling(bodyHtml || "");
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${safeTitle}</title>
<style>${css}</style>
</head>
<body>
${body}
</body>
</html>`;
}

export const CANONICAL_PRINT_SPEC = Object.freeze({
  fontFamily: "'Times New Roman', Times, serif",
  h1Pt: 14.5,
  h2Pt: 12.5,
  h3Pt: 11.5,
  bodyPt: 10,
  footerPt: 8,
  lineHeight: 1.35,
  paragraphGapPt: 6,
  portraitMargin: "14mm 15mm 18mm 15mm",
  landscapeMargin: "12mm 14mm 15mm 14mm",
  missingCaseNumberLabel: "No case number",
});
