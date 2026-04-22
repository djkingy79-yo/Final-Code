/**
 * Shared export HTML builder for all case sections.
 * Generates a complete HTML document with consistent styling:
 * - Page numbers (CSS counter)
 * - Branding footer (scales + Appeal Case Manager + Founded by Debra King)
 * - NOT LEGAL ADVICE disclaimer
 * - Appellant name + date in footer
 * - Responsive CSS for mobile preview
 */

const SCALES_SVG = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>`;

const formatDate = () =>
  new Date().toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" });

export function buildExportHtml({ title, sectionTitle, defendantName, bodyHtml, accentColor = "#1e40af", docLabel }) {
  const previewDate = new Date().toLocaleDateString("en-AU", { day: "2-digit", month: "2-digit", year: "numeric" });
  // Footer document label: prefer explicit docLabel (e.g. "Extensive Case Log & Analysis"),
  // else sectionTitle, else title. Appended with " — {Appellant}" for identification on every page.
  const label = (docLabel || sectionTitle || title || "Document").replace(/"/g, '\\"');
  const appellant = (defendantName || "Appellant").replace(/"/g, '\\"');
  // Footer spec locked by owner 21/4/2026:
  //   LEFT  = {Appellant}  ·  {Document Type}  ·  {Date in en-AU long form}
  //   RIGHT = Page X of Y
  const footerLeft = `${appellant}  \\00B7  ${label}  \\00B7  ${formatDate().replace(/"/g,'\\"')}`;

  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<style>
  /* ==========================================================================
     PRINT-READY EXPORT STYLES — CSS Paged Media
     - @page rules suppress the browser's auto URL/date headers (Chrome, Edge,
       Safari Print-to-PDF all honour @bottom-* blocks and stop injecting their
       own when we define content there).
     - Landscape tables: every <table> is wrapped (via CSS named page) in a
       landscape page break, portrait resumes after.
     - Footer shows: "{DocumentType} — {Appellant}"  (left) and
                     "Page X of Y"                   (right), 7pt Times-Italic.
     ========================================================================== */

  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { background: #fff; }
  /* CANONICAL PRINT SPEC (locked 2026-02 by owner — DO NOT DRIFT)
     Font:  Times New Roman
     Body:  11pt, line-height 1.5
     H1:    14pt bold
     H2:    12pt bold
     H3:    12pt bold italic
     Paragraph gap: 10pt
     Margins: 18mm top, 20mm sides, 22mm bottom
     Footer: {Appellant} · {Doc Type} · {Date} (left) | Page X of Y (right), 9pt italic
     Every export surface (Notes, Legal, Progress, Bundle, Grounds, Timeline,
     Tab exports, Barrister) must use these values. */
  body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 11pt;
    color: #1e293b;
    line-height: 1.5;
  }

  /* ---------- PORTRAIT (default) ---------- */
  @page {
    size: A4 portrait;
    margin: 18mm 20mm 22mm 20mm;
    @bottom-left {
      content: "${footerLeft}";
      font-family: 'Times New Roman', Times, serif;
      font-size: 9pt;
      font-style: italic;
      color: #334155;
    }
    @bottom-right {
      content: "Page " counter(page) " of " counter(pages);
      font-family: 'Times New Roman', Times, serif;
      font-size: 9pt;
      font-style: italic;
      color: #334155;
    }
  }
  /* ---------- LANDSCAPE (tables only) ---------- */
  @page landscape-table {
    size: A4 landscape;
    margin: 14mm 18mm 20mm 18mm;
    @bottom-left {
      content: "${footerLeft}";
      font-family: 'Times New Roman', Times, serif;
      font-size: 9pt;
      font-style: italic;
      color: #334155;
    }
    @bottom-right {
      content: "Page " counter(page) " of " counter(pages);
      font-family: 'Times New Roman', Times, serif;
      font-size: 9pt;
      font-style: italic;
      color: #334155;
    }
  }
  /* Landscape page for tables — but NO forced break-before/after because
     that pushes the table to a fresh page and leaves huge whitespace
     before it on the preceding portrait page (bug report 2026-02).
     Let the browser break naturally based on table height. */
  .export-body table,
  .section-body table {
    page: landscape-table;
    break-inside: auto;
    page-break-inside: auto;
    width: 100%;
    border-collapse: collapse;
    margin: 8pt 0;
    font-size: 10pt;
    table-layout: fixed;
  }
  .export-body th,
  .section-body th {
    background: #1d4ed8 !important;
    color: #fff !important;
    font-weight: 700 !important;
    padding: 5px 7px;
    text-align: left;
    border: 1px solid #cbd5e1;
    font-size: 9pt;
    word-break: keep-all;
    overflow-wrap: break-word;
    hyphens: none;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  .export-body td,
  .section-body td {
    padding: 5px 7px;
    border: 1px solid #e2e8f0;
    font-size: 9pt;
    line-height: 1.35;
    word-break: keep-all;
    overflow-wrap: break-word;
    hyphens: none;
    vertical-align: top;
  }
  .export-body tr:nth-child(even) td,
  .section-body tr:nth-child(even) td { background: #f8fafc; }

  /* Pipe-delimited <pre> tables (from unparsed markdown): white, readable,
     wrapping. This keeps them legible until the generator is upgraded to
     emit real HTML tables. */
  .export-body pre,
  .section-body pre,
  .export-container pre {
    background: #f8fafc !important;
    color: #1e293b !important;
    font-family: 'Courier New', monospace;
    font-size: 8pt;
    padding: 8px 10px;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    white-space: pre-wrap;
    word-wrap: break-word;
    overflow-wrap: anywhere;
    break-inside: avoid;
    page-break-inside: avoid;
    margin: 6px 0;
  }

  .export-container { max-width: 900px; margin: 0 auto; }

  /* Cover header: WHITE heading on coloured background (was black before) */
  .export-header {
    background: ${accentColor};
    color: #fff !important;
    padding: 20px 24px;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
    page-break-inside: avoid;
    break-inside: avoid;
  }
  .export-header h1,
  .export-header h2,
  .export-header p,
  .export-header * {
    color: #fff !important;
  }
  .export-header h1 {
    font-family: 'Times New Roman', Times, serif;
    font-size: 14pt;
    font-weight: 700;
    margin-bottom: 4px;
  }
  .export-header p { font-size: 11pt; opacity: 0.92; }

  .export-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 10px 24px;
    background: #f1f5f9;
    border-bottom: 1px solid #e2e8f0;
    font-size: 10pt;
  }
  .export-meta-item { display: flex; flex-direction: column; }
  .export-meta-label { font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; font-size: 8pt; }
  .export-meta-value { font-weight: 600; color: #0f172a; }

  .export-body { padding: 16px 24px; }
  .export-body h2 {
    font-family: 'Times New Roman', Times, serif;
    font-size: 12pt;
    font-weight: 700;
    color: #0f172a;
    margin: 14px 0 6px;
    padding-bottom: 3px;
    border-bottom: 1.5px solid ${accentColor};
    /* H2 keeps page-break-after:avoid so section titles don't orphan
       alone at page bottom with no body text below. */
    page-break-after: avoid;
    break-after: avoid;
  }
  /* H3 / H4 intentionally do NOT force break-after. Previously this was
     causing whole subsections (heading + 20 paragraphs) to push to the next
     page, leaving half-blank pages. Browser default orphans:3 widows:3
     gives correct pagination. */
  .export-body h3 { font-family: 'Times New Roman', Times, serif; font-size: 12pt; font-weight: 700; font-style: italic; color: #1e293b; margin: 12px 0 4px; }
  .export-body h4 { font-family: 'Times New Roman', Times, serif; font-size: 11pt; font-weight: 700; color: #1e293b; margin: 10px 0 3px; }

  /* PARAGRAPH SPACING — locked by owner 2026-02:
     - Line-height INSIDE a paragraph: 1.5 (comfortable legal reading)
     - Gap BETWEEN paragraphs: 10pt (clear whitespace, no gaps) */
  .export-body p,
  .section-body p { margin: 0 0 10pt 0; font-size: 11pt; line-height: 1.5; orphans: 3; widows: 3; }
  .export-body ul, .export-body ol,
  .section-body ul, .section-body ol { margin: 4px 0 10pt; padding-left: 1.6rem; }
  .export-body li,
  .section-body li { margin-bottom: 3pt; font-size: 11pt; line-height: 1.5; }

  .export-body .note-card { background: #ffffff; border: 2px solid #1e3a5f; border-radius: 6px; padding: 10px 12px; margin-bottom: 10pt; break-inside: avoid; }
  .export-body .note-title { font-weight: 700; font-size: 12pt; color: #0f172a; margin-bottom: 2px; }
  .export-body .note-date { font-size: 10pt; color: #64748b; margin-bottom: 4px; font-style: italic; }
  .export-body .note-content { font-size: 11pt; color: #1e293b; white-space: pre-wrap; font-weight: 600; line-height: 1.5; }
  .export-body .section-block { margin-bottom: 14pt; padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px; page-break-inside: avoid; break-inside: avoid; }
  .export-body .section-block h3 { margin-top: 0; }

  .toc-container { background: #ffffff; padding: 10px 24px; break-after: page; page-break-after: always; }
  .toc-heading { font-size: 10pt; text-transform: uppercase; letter-spacing: 0.05em; color: #334155; font-weight: 700; margin: 0 0 6px; }
  .toc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2px 16px; }
  .toc-item { font-size: 8pt; color: #334155; padding: 1px 0; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  .sections { padding: 16px 24px; }
  .section { margin-bottom: 18pt; break-inside: auto; }
  .section-header { display: flex; align-items: center; gap: 8px; border-left: 3px solid ${accentColor}; padding-left: 10px; margin-bottom: 6px; break-after: avoid; page-break-after: avoid; }
  .section-number { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border-radius: 50%; background: #e2e8f0; color: #0f172a; font-size: 10pt; font-weight: 700; flex-shrink: 0; margin-right: 2px; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  /* belt-and-braces separator between number and title — works even if the
     flex gap collapses (older Safari / print engines) or the circle doesn't
     render, preventing "1Case Summary" concat seen on some mobile previews. */
  .section-number::after { content: ""; }
  .section-title { font-family: 'Times New Roman', Times, serif; font-size: 12pt; font-weight: 700; color: #0f172a; text-transform: uppercase; }
  .section-title::before { content: none; }
  .section-body { background: #fff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px; font-size: 11pt; line-height: 1.5; }
  .section-body h3 { font-size: 12pt; font-weight: 700; font-style: italic; color: #1e293b; margin: 12px 0 4px; padding-top: 6px; border-top: 1px solid #e2e8f0; }
  .section-body h3:first-child { margin-top: 0; padding-top: 0; border-top: none; }
  .section-body h4 { font-size: 11pt; font-weight: 700; color: #1e293b; margin: 10px 0 3px; }
  .section-body strong { color: #0f172a; font-weight: 700; }

  .flex { display: flex; }
  .items-center { align-items: center; }
  .gap-2 { gap: 8px; }
  .gap-3 { gap: 12px; }
  .gap-4 { gap: 16px; }
  .mb-1 { margin-bottom: 4px; }
  .mb-2 { margin-bottom: 8px; }
  .mb-3 { margin-bottom: 12px; }
  .mb-4 { margin-bottom: 16px; }
  .mt-1 { margin-top: 4px; }
  .mt-2 { margin-top: 8px; }
  .mt-3 { margin-top: 12px; }
  .p-2 { padding: 8px; }
  .p-4 { padding: 16px; }
  .p-6 { padding: 24px; }
  .border { border: 1px solid #e2e8f0; }
  .border-slate-200 { border-color: #e2e8f0; }
  .rounded { border-radius: 4px; }
  .rounded-lg { border-radius: 6px; }
  .font-medium { font-weight: 500; }
  .font-semibold { font-weight: 600; }
  .font-bold { font-weight: 700; }
  .text-xs { font-size: 9pt; }
  .text-sm { font-size: 10pt; }
  .text-slate-400 { color: #94a3b8; }
  .text-slate-500 { color: #64748b; }
  .text-slate-600 { color: #475569; }
  .text-slate-700 { color: #334155; }
  .text-slate-900 { color: #0f172a; }
  .text-white { color: #ffffff; }
  .uppercase { text-transform: uppercase; }
  .whitespace-pre-wrap { white-space: pre-wrap; }
  .flex-wrap { flex-wrap: wrap; }
  .space-y-1 > * + * { margin-top: 4px; }
  .space-y-2 > * + * { margin-top: 8px; }
  .underline { text-decoration: underline; }
  .break-words { overflow-wrap: break-word; }
  .bg-slate-50 { background-color: #f8fafc; }
  .inline-flex { display: inline-flex; }

  .disclaimer { margin: 16px 24px; padding: 10px 14px; background: #dc2626; border: 2px solid #b91c1c; border-radius: 6px; page-break-inside: avoid; break-inside: avoid; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; display: flex; gap: 10px; align-items: flex-start; }
  .disclaimer .disc-hazard { font-size: 22px; color: #facc15; flex-shrink: 0; }
  .disclaimer strong { display: block; font-size: 10pt; color: #fff; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 3px; }
  .disclaimer p { font-size: 8pt; color: #ffffff; line-height: 1.4; margin: 0; font-weight: 700; }

  .branding { text-align: center; margin: 16px 24px; padding: 10px 0; page-break-inside: avoid; break-inside: avoid; }
  .branding .by-line { font-size: 10pt; font-weight: 700; color: #334155; margin: 0 0 6px; }
  .branding-inner { display: inline-flex; align-items: center; gap: 8px; }
  .branding-icon { width: 30px; height: 30px; background: #dc2626; border-radius: 5px; display: flex; align-items: center; justify-content: center; }
  .branding-text { text-align: left; }
  .branding-text .name { margin: 0; font-weight: 700; font-size: 10pt; color: #0f172a; }
  .branding-text .sub { margin: 0; font-size: 8pt; color: #64748b; }

  .page-break { page-break-before: always; break-before: page; }

  @media print {
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
    body { background: #fff; padding: 0; }
    .export-container { max-width: none; }
    .disclaimer, .branding, .export-header, .export-meta, .section-block, .note-card { break-inside: avoid; page-break-inside: avoid; }
    .disclaimer + .branding { break-before: avoid; page-break-before: avoid; }
  }
  @media (max-width: 768px) {
    /* Mobile / iPad: preserve canonical sizes for WYSIWYG parity with the
       printed PDF. Only the container padding shrinks so text isn't jammed
       against the screen edge. Fonts stay at the locked print spec. */
    body { font-size: 11pt; line-height: 1.5; }
    .export-container { padding: 6px; max-width: 100%; }
    .export-header { padding: 10px 12px; }
    .export-header h1 { font-size: 14pt; }
    .export-header p { font-size: 11pt; }
    .export-meta { padding: 6px 12px; gap: 6px; font-size: 10pt; }
    .export-body, .sections { padding: 8px 12px; }
    .export-body h2 { font-size: 12pt; margin: 10px 0 4px; }
    .export-body h3, .section-body h3 { font-size: 12pt; margin: 8px 0 3px; }
    .export-body p, .section-body p { font-size: 11pt; margin: 0 0 10pt 0; line-height: 1.5; }
    .export-body li, .section-body li { font-size: 11pt; line-height: 1.5; }
    .export-body table, .section-body table { font-size: 9.5pt; }
    .export-body th, .export-body td, .section-body th, .section-body td { padding: 3px 5px; }
    .disclaimer { margin: 8px 12px; padding: 8px 10px; }
    .disclaimer strong { font-size: 10pt; }
    .disclaimer p { font-size: 9pt; line-height: 1.45; }
    .disclaimer .disc-hazard { font-size: 18px; }
    .branding { margin: 8px 12px; padding: 6px 0; }
    .branding .by-line { font-size: 10pt; }
    .branding-text .name { font-size: 10pt; }
    .branding-text .sub { font-size: 9pt; }
    .section-title { font-size: 12pt; }
    .section-body { padding: 8px 10px; font-size: 11pt; }
  }
</style>
</head>
<body>
<div class="export-container">
  ${bodyHtml}
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
        <p class="sub" style="font-size:9px;opacity:0.75;margin-top:4px;">Legal Framework v2026.02 &middot; 79 Australian Acts manually verified &middot; criminallawappealmanagement.com.au</p>
      </div>
    </div>
  </div>
</div>
</body>
</html>`;
}

export function openExportPreview(html, mode = "print") {
  localStorage.setItem("document-preview-payload", JSON.stringify({
    html,
    title: "Export Preview",
  }));
  window.open(`/document-preview?mode=${mode}`, "_blank");
}
