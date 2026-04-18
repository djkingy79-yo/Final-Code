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

export function buildExportHtml({ title, sectionTitle, defendantName, bodyHtml, accentColor = "#1e40af" }) {
  const previewDate = new Date().toLocaleDateString("en-AU", { day: "2-digit", month: "2-digit", year: "numeric" });
  const timeStr = new Date().toLocaleTimeString("en-AU", { hour: "2-digit", minute: "2-digit" });
  const footerLabel = `Criminal Law Appeal Management / ${sectionTitle || title} — ${defendantName || "Appellant"} — ${previewDate}`;

  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Times New Roman', Times, serif; font-size: 11pt; color: #1e293b; background: #fff; padding-bottom: 60px; line-height: 1.5; }
  th { background: #1d4ed8 !important; color: #fff !important; font-weight: 700 !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  @page { size: A4; margin: 18mm 18mm 26mm; }
  @page landscape-table { size: A4 landscape; margin: 14mm 14mm 22mm; }
  .export-container { max-width: 900px; margin: 0 auto; }
  .export-header { background: ${accentColor}; color: #fff; padding: 20px 24px; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; page-break-inside: avoid; }
  .export-header h1 { font-family: 'Times New Roman', Times, serif; font-size: 15pt; font-weight: 700; margin-bottom: 3px; }
  .export-header p { font-size: 10pt; opacity: 0.85; }
  .export-meta { display: flex; flex-wrap: wrap; gap: 12px; padding: 10px 24px; background: #f1f5f9; border-bottom: 1px solid #e2e8f0; font-size: 10pt; }
  .export-meta-item { display: flex; flex-direction: column; }
  .export-meta-label { font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; font-size: 8pt; }
  .export-meta-value { font-weight: 600; color: #0f172a; }
  .export-body { padding: 16px 24px; }
  .export-body h2 { font-family: 'Times New Roman', Times, serif; font-size: 15pt; font-weight: 700; color: #0f172a; margin: 16px 0 8px; padding-bottom: 4px; border-bottom: 2px solid ${accentColor}; }
  .export-body h3 { font-family: 'Times New Roman', Times, serif; font-size: 13pt; font-weight: 700; color: #1e293b; margin: 12px 0 5px; }
  .export-body h4 { font-family: 'Times New Roman', Times, serif; font-size: 11pt; font-weight: 700; color: #1e293b; margin: 10px 0 4px; }
  .export-body p { margin-bottom: 6px; font-size: 11pt; line-height: 1.5; }
  .export-body ul, .export-body ol { margin: 4px 0 8px; padding-left: 2rem; }
  .export-body li { margin-bottom: 2px; font-size: 11pt; line-height: 1.5; }
  .export-body table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 9pt; page-break-before: always; }
  .export-body th { background: #1d4ed8; color: #fff; padding: 4px 6px; text-align: left; font-weight: 700; border: 1px solid #cbd5e1; font-size: 8pt; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; word-wrap: break-word; overflow-wrap: break-word; }
  .export-body td { padding: 4px 6px; border: 1px solid #e2e8f0; word-wrap: break-word; overflow-wrap: break-word; font-size: 9pt; }
  .export-body tr:nth-child(even) td { background: #f8fafc; }
  .export-body .note-card { background: #ffffff; border: 2px solid #1e3a5f; border-radius: 6px; padding: 10px 12px; margin-bottom: 8px; }
  .export-body .note-title { font-weight: 700; font-size: 11pt; color: #0f172a; margin-bottom: 2px; }
  .export-body .note-date { font-size: 9pt; color: #64748b; margin-bottom: 4px; font-style: italic; }
  .export-body .note-content { font-size: 11pt; color: #1e293b; white-space: pre-wrap; font-weight: 600; }
  .export-body .section-block { margin-bottom: 12px; padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px; page-break-inside: avoid; }
  .export-body .section-block h3 { margin-top: 0; }
  .toc-container { background: #ffffff; padding: 10px 24px; }
  .toc-heading { font-size: 10pt; text-transform: uppercase; letter-spacing: 0.05em; color: #334155; font-weight: 700; margin: 0 0 6px; }
  .toc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2px 16px; }
  .toc-item { font-size: 8pt; color: #334155; padding: 1px 0; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .sections { padding: 16px 24px; }
  .section { margin-bottom: 14px; }
  .section-header { display: flex; align-items: center; gap: 8px; border-left: 3px solid ${accentColor}; padding-left: 10px; margin-bottom: 6px; }
  .section-number { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border-radius: 50%; background: #e2e8f0; color: #0f172a; font-size: 10pt; font-weight: 700; flex-shrink: 0; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  .section-title { font-family: 'Times New Roman', Times, serif; font-size: 13pt; font-weight: 700; color: #0f172a; text-transform: uppercase; }
  .section-body { background: #fff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px; font-size: 11pt; line-height: 1.5; }
  .section-body h3 { font-size: 13pt; font-weight: 700; color: #1e293b; margin: 12px 0 5px; padding-top: 8px; border-top: 1px solid #e2e8f0; }
  .section-body h3:first-child { margin-top: 0; padding-top: 0; border-top: none; }
  .section-body h4 { font-size: 11pt; font-weight: 700; color: #1e293b; margin: 10px 0 4px; }
  .section-body p { margin-bottom: 6px; font-size: 11pt; line-height: 1.5; }
  .section-body ul, .section-body ol { padding-left: 2rem; margin: 4px 0 8px; }
  .section-body li { margin-bottom: 2px; font-size: 11pt; line-height: 1.5; }
  .section-body strong { color: #0f172a; font-weight: 700; }
  .section-body table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 9pt; page-break-before: always; }
  .section-body th { background: #1d4ed8; color: #fff; padding: 4px 6px; text-align: left; font-weight: 700; border: 1px solid #cbd5e1; font-size: 8pt; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; word-wrap: break-word; }
  .section-body td { padding: 4px 6px; border: 1px solid #e2e8f0; word-wrap: break-word; overflow-wrap: break-word; font-size: 9pt; }
  .section-body tr:nth-child(even) td { background: #f8fafc; }

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
  .print-footer { display: none; position: fixed; left: 0; right: 0; bottom: 0; background: #fff; border-top: 1px solid #1d4ed8; padding: 3px 18mm 4px; }
  .print-footer-row { display: flex; justify-content: space-between; align-items: center; font-size: 7pt; font-style: italic; color: #475569; font-family: 'Times New Roman', Times, serif; }
  .print-footer-page::after { content: ''; }
  .page-break { page-break-before: always; }
  @media print {
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
    body { background: #fff; padding-bottom: 40px; }
    .export-container { max-width: none; }
    .print-footer { display: block; }
    .print-footer-page::after { content: "Page " counter(page) " of " counter(pages); }
    .disclaimer { print-color-adjust: exact; -webkit-print-color-adjust: exact; page-break-inside: avoid; }
    .branding { page-break-inside: avoid; }
    .disclaimer + .branding { page-break-before: avoid; }
    .export-header { print-color-adjust: exact; -webkit-print-color-adjust: exact; page-break-inside: avoid; }
    .section-number { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .section-body th, .export-body th { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
  @media (max-width: 768px) {
    body { font-size: 9pt; }
    .export-header { padding: 14px 12px; }
    .export-header h1 { font-size: 14pt; }
    .export-meta { padding: 8px 12px; gap: 8px; }
    .export-body, .sections { padding: 10px 12px; }
    .export-body h2 { font-size: 13pt; }
    .export-body h3 { font-size: 11pt; }
    .export-body table, .section-body table { font-size: 8pt; }
    .export-body th, .export-body td, .section-body th, .section-body td { padding: 3px 4px; }
    .disclaimer { margin: 10px 12px; padding: 8px 10px; }
    .branding { margin: 10px 12px; }
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
      </div>
    </div>
  </div>
</div>
<div class="print-footer">
  <div class="print-footer-row">
    <span>${footerLabel}</span>
    <span>${timeStr}</span>
    <span class="print-footer-page"></span>
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
