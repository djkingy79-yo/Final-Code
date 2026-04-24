/**
 * exportHtml.js — THE ONLY PLACE IN THE FRONTEND THAT BUILDS PRINT/EXPORT HTML.
 *
 * Locked 24 Feb 2026 Print/Export Enforcement Pass:
 *   - No other component is permitted to emit a full `<html>` export shell.
 *   - Typography and `@page` rules come exclusively from utils/printStyles.js.
 *   - Footer format is locked per REPORT_PRODUCT_SPEC.md and enforced by
 *     buildCanonicalPrintCss().
 *   - Wide tables (>=6 columns) are automatically promoted to the canonical
 *     landscape named page via a post-processor.
 *
 * Callers pass their report-specific body (with any non-typography chrome)
 * as `bodyHtml`; buildExportHtml() handles the rest.
 */

import { buildCanonicalPrintCss } from "./printStyles";
import auSpelling from "./auSpelling";

const SCALES_SVG = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>`;

/**
 * Post-processor: any table with >=6 columns (first <tr>) or marked
 * `data-wide-table` is automatically wrapped with the `.legal-landscape-table`
 * class so the canonical CSS routes it through `@page landscape-table`.
 *
 * Safe HTML-string operation — uses DOMParser in the browser, falls back to
 * a string-only heuristic during SSR / test.
 */
export function applyLandscapeForWideTables(html) {
  if (!html || typeof html !== "string") return html || "";
  if (typeof DOMParser === "undefined") {
    // Non-browser fallback — heuristic: 6+ <td> in the first row.
    return html.replace(
      /<table([^>]*)>\s*(<thead[^>]*>\s*)?<tr[^>]*>([\s\S]*?)<\/tr>/i,
      (match, tableAttrs, theadOpen, firstRow) => {
        const cellCount = (firstRow.match(/<t[dh]\b/gi) || []).length;
        if (cellCount < 6) return match;
        const hasClass = /\bclass=/.test(tableAttrs);
        const injected = hasClass
          ? tableAttrs.replace(/class="([^"]*)"/, 'class="$1 legal-landscape-table"')
          : `${tableAttrs} class="legal-landscape-table"`;
        return `<table${injected}>${theadOpen || ""}<tr>${firstRow}</tr>`;
      },
    );
  }
  try {
    const parser = new DOMParser();
    const wrapper = `<!DOCTYPE html><html><body>${html}</body></html>`;
    const doc = parser.parseFromString(wrapper, "text/html");
    const tables = doc.body.querySelectorAll("table");
    tables.forEach((tbl) => {
      if (tbl.classList.contains("legal-landscape-table")) return;
      const firstRow = tbl.querySelector("tr");
      if (!firstRow) return;
      const cells = firstRow.querySelectorAll("th, td").length;
      if (cells >= 6 || tbl.dataset.wideTable === "true") {
        tbl.classList.add("legal-landscape-table");
      }
    });
    return doc.body.innerHTML;
  } catch {
    return html;
  }
}

/**
 * Build a complete standalone export HTML document.
 *
 * Required:
 *   - bodyHtml       : the document content
 *   - docLabel       : shown in footer + <title>
 *   - defendantName  : appellant surname — flows into footer
 *   - caseNumber     : case number — flows into footer ("No case number" if blank)
 *
 * Optional component-specific chrome (pre-existing callers continue to work):
 *   - title          : overrides docLabel in <title>
 *   - sectionTitle   : kicker text above the title banner
 *   - accentColor    : report header banner colour
 *   - extraStyles    : CSS injected AFTER the canonical spec (component-only,
 *                      NON-TYPOGRAPHY rules — border, background, layout).
 *                      Attempts to set font-family / font-size / @page are
 *                      explicitly disallowed by the lint test in
 *                      backend/tests/test_print_enforcement.py.
 *   - skipChrome     : if true, omits the disclaimer + branding blocks
 *                      (e.g. Timeline print).
 *   - beforeBody     : raw HTML injected BEFORE bodyHtml inside the container
 *                      (e.g. cover-page section for ReportView).
 */
export function buildExportHtml({
  title,
  sectionTitle,
  defendantName,
  bodyHtml,
  accentColor = "#1e40af",
  docLabel,
  caseNumber,
  extraStyles,
  skipChrome = false,
  beforeBody,
}) {
  const effectiveDocLabel = docLabel || sectionTitle || title || "Legal Document";
  const appellant = defendantName || "Appellant";
  const canonicalCss = buildCanonicalPrintCss({
    docLabel: effectiveDocLabel,
    appellant,
    caseNumber,
  });

  // Promote any wide table in the body to the canonical landscape page
  // before anything else touches it.
  const processedBody = applyLandscapeForWideTables(bodyHtml || "");

  const disclaimerBlock = skipChrome
    ? ""
    : `
  <div class="disclaimer">
    <span class="disc-hazard">&#9888;</span>
    <div>
      <strong>NOT LEGAL ADVICE</strong>
      <p>This application is an educational research tool only and does NOT constitute legal advice. It must NOT be relied upon as such. The creator of this application is not a lawyer. All analysis, findings, reports, and recommendations generated by this tool must be independently verified by a qualified Australian legal professional before any action is taken. This tool covers Australian law only. No solicitor-client relationship is created by using this service. No document, report, or output generated by this Application should be filed with, submitted to, or relied upon before any court, tribunal, or regulatory body.</p>
    </div>
  </div>`;

  const brandingBlock = skipChrome
    ? ""
    : `
  <div class="branding">
    <p class="by-line">Created and Designed by Deb King</p>
    <div class="branding-inner">
      <div class="branding-icon">${SCALES_SVG}</div>
      <div class="branding-text">
        <p class="name">Appeal Case Manager</p>
        <p class="sub">Founded by Debra King</p>
        <p class="sub">Criminal Appeal Research Tool &mdash; Australian Law Only</p>
        <p class="sub" style="font-size:8pt;opacity:0.75;margin-top:3px;">Legal Framework v2026.02 &middot; 79 Australian Acts manually verified &middot; criminallawappealmanagement.com.au</p>
      </div>
    </div>
  </div>`;

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${(title || effectiveDocLabel).replace(/</g, "&lt;")}</title>
<style>
  /* 1. CANONICAL typography + @page (single source of truth). */
  ${canonicalCss}

  /* 2. Export-chrome CSS — layout-only, NO typography overrides. */
  .export-container { max-width: 820px; margin: 0 auto; padding: 12px 16px; }
  .export-header { background: ${accentColor}; color: #fff; padding: 12px 18px; border-radius: 8px; margin-bottom: 10pt;
    -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  .export-header h1, .export-header h1 * { color: #fff !important; }
  .export-header h1 { margin: 0 0 4px; }
  .export-header p { margin: 0; color: rgba(255,255,255,0.92); font-size: 10pt; }
  .export-meta { background: #f1f5f9; padding: 6px 10px; border-radius: 6px; margin-bottom: 10pt; font-size: 10pt; color: #334155; }

  .disclaimer { margin: 14pt 0 8pt; padding: 8px 10px; background: #dc2626; border: 1pt solid #b91c1c; border-radius: 4px;
    color: #fff; display: flex; gap: 8px; align-items: flex-start;
    -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;
    page-break-inside: avoid; break-inside: avoid; }
  .disclaimer .disc-hazard { font-size: 20px; color: #facc15; flex-shrink: 0; }
  .disclaimer strong { display: block; font-size: 10pt; color: #fff; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 3px; }
  .disclaimer p { font-size: 8pt; color: #fff; line-height: 1.4; margin: 0; font-weight: 700; }

  .branding { text-align: center; margin: 12pt 0 0; padding: 8pt 0 2pt; page-break-inside: avoid; break-inside: avoid; }
  .branding .by-line { font-size: 10pt; font-weight: 700; color: #334155; margin: 0 0 5pt; }
  .branding-inner { display: inline-flex; align-items: center; gap: 8px; }
  .branding-icon { width: 28px; height: 28px; background: #dc2626; border-radius: 5px; display: flex; align-items: center; justify-content: center;
    -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  .branding-text { text-align: left; }
  .branding-text .name { margin: 0; font-weight: 700; font-size: 10pt; color: #0f172a; }
  .branding-text .sub { margin: 0; font-size: 8pt; color: #64748b; }
  .page-break { page-break-before: always; break-before: page; }

  /* 3. Caller-supplied component-only chrome CSS (optional). Must NOT
     override typography (font-family / font-size / @page) — that is
     enforced by the print enforcement lint test. */
  ${extraStyles || ""}
</style>
</head>
<body>
<div class="export-container">
  ${beforeBody || ""}
  ${auSpelling(processedBody)}
  ${disclaimerBlock}
  ${brandingBlock}
</div>
</body>
</html>`;
}

/**
 * Open the iOS-safe document-preview route. Every browser print flow
 * funnels through this so iPhone Safari gets the canonical output.
 */
export function openExportPreview(html, mode = "print") {
  localStorage.setItem(
    "document-preview-payload",
    JSON.stringify({
      html,
      mode,
      title: "Export Preview",
      createdAt: Date.now(),
    })
  );
  window.open(`/document-preview?mode=${mode}`, "_blank");
}
