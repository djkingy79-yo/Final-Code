/**
 * exportHtml.js — shared export HTML builder for all frontend print/PDF/Word paths.
 *
 * Locked 24 Feb 2026 — refactored to delegate all typography/@page CSS to
 * utils/printStyles.js (single source of truth). This file retains only the
 * project-specific HTML shell (disclaimer, branding, docLabel passthrough)
 * and the existing `openExportPreview` handler so every caller continues to
 * work with no signature change — only the footer format changes per spec.
 *
 * Callers must pass `caseNumber` (new 24 Feb 2026 spec). Omitting it renders
 * "No case number" in the footer — never blank.
 */

import { buildCanonicalPrintCss } from "./printStyles";
import auSpelling from "./auSpelling";

const SCALES_SVG = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>`;

/**
 * Build a complete standalone export HTML document.
 *
 * Preserved signature (kept stable for every existing caller):
 *   buildExportHtml({ title, sectionTitle, defendantName, bodyHtml, accentColor, docLabel, caseNumber })
 *
 * - title          : <title> element + cover heading
 * - sectionTitle   : badge text above the title
 * - defendantName  : shown in header + threaded through to footer as {appellant}
 * - bodyHtml       : the page content
 * - accentColor    : decorative header bar colour (unchanged — legal content only)
 * - docLabel       : document name used in the canonical footer. Falls back to
 *                    sectionTitle or title.
 * - caseNumber     : case number used in the canonical footer. Missing → the
 *                    footer renders "No case number" per 24 Feb 2026 spec.
 */
export function buildExportHtml({
  title,
  sectionTitle,
  defendantName,
  bodyHtml,
  accentColor = "#1e40af",
  docLabel,
  caseNumber,
}) {
  const effectiveDocLabel = docLabel || sectionTitle || title || "Legal Document";
  const appellant = defendantName || "Appellant";
  const canonicalCss = buildCanonicalPrintCss({
    docLabel: effectiveDocLabel,
    appellant,
    caseNumber,
  });

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${(title || effectiveDocLabel).replace(/</g, "&lt;")}</title>
<style>
  /* Canonical typography + @page rules (imported from utils/printStyles.js). */
  ${canonicalCss}

  /* Export-specific chrome (disclaimer + branding) — NOT typography. */
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
</style>
</head>
<body>
<div class="export-container">
  ${auSpelling(bodyHtml || "")}
  <div class="disclaimer">
    <span class="disc-hazard">&#9888;</span>
    <div>
      <strong>NOT LEGAL ADVICE</strong>
      <p>This application is an educational research tool only and does NOT constitute legal advice. It must NOT be relied upon as such. The creator of this application is not a lawyer. All analysis, findings, reports, and recommendations generated by this tool must be independently verified by a qualified Australian legal professional before any action is taken. This tool covers Australian law only. No solicitor-client relationship is created by using this service. No document, report, or output generated by this Application should be filed with, submitted to, or relied upon before any court, tribunal, or regulatory body.</p>
    </div>
  </div>
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
  </div>
</div>
</body>
</html>`;
}

/**
 * Open the document-preview route (iOS-safe wrapper). localStorage payload
 * is identical to existing contract so DocumentPreviewPage.jsx consumes it
 * unchanged.
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
