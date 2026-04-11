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
  const footerLabel = `Documented from the Criminal Law /Appeal Management Application - ${sectionTitle} - For ${defendantName || "Unknown"} ${previewDate}`;

  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Times New Roman', Times, serif; font-size: 12pt; color: #1e293b; background: #fff; padding-bottom: 80px; line-height: 1.8; -webkit-text-size-adjust: 100%; text-size-adjust: 100%; }
  @page { size: A4; margin: 14mm 14mm 22mm; }
  .export-container { max-width: 900px; margin: 0 auto; }
  .export-header { background: ${accentColor}; color: #fff; padding: 28px 32px; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; page-break-inside: avoid; break-inside: avoid; }
  .export-header h1 { font-family: 'Times New Roman', Times, serif; font-size: 22pt; font-weight: 700; margin-bottom: 4px; }
  .export-header p { font-size: 12pt; opacity: 0.85; }
  .export-meta { display: flex; flex-wrap: wrap; gap: 16px; padding: 16px 32px; background: #f1f5f9; border-bottom: 1px solid #e2e8f0; font-size: 12pt; }
  .export-meta-item { display: flex; flex-direction: column; }
  .export-meta-label { font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; font-size: 10pt; }
  .export-meta-value { font-weight: 600; color: #0f172a; }
  .export-body { padding: 24px 32px; }
  .export-body h2 { font-family: 'Times New Roman', Times, serif; font-size: 18pt; font-weight: 700; color: #0f172a; margin: 24px 0 12px; padding-bottom: 8px; border-bottom: 2px solid ${accentColor}; }
  .export-body h3 { font-family: 'Times New Roman', Times, serif; font-size: 14pt; font-weight: 700; color: #1e293b; margin: 18px 0 8px; }
  .export-body p { margin-bottom: 10px; }
  .export-body ul, .export-body ol { margin: 8px 0 12px; padding-left: 2.5rem; }
  .export-body li { margin-bottom: 4px; font-size: 12pt; line-height: 1.75; }
  .export-body table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 11pt; font-family: 'Times New Roman', Times, serif; }
  .export-body th { background: ${accentColor}; color: #fff; padding: 8px 10px; text-align: left; font-weight: 700; border: 1px solid #cbd5e1; font-family: 'Times New Roman', Times, serif; }
  .export-body td { padding: 7px 10px; border: 1px solid #e2e8f0; font-family: 'Times New Roman', Times, serif; }
  .export-body tr:nth-child(even) td { background: #f8fafc; }
  .export-body h4 { font-family: 'Times New Roman', Times, serif; font-size: 12pt; font-weight: 700; color: #1e293b; margin: 14px 0 6px; }
  .export-body .note-card { background: #2563eb; border: 1px solid #1d4ed8; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .export-body .note-title { font-weight: 700; font-size: 14pt; color: #ffffff; margin-bottom: 4px; font-family: 'Times New Roman', Times, serif; }
  .export-body .note-date { font-size: 10pt; color: #bfdbfe; margin-bottom: 8px; font-style: italic; }
  .export-body .note-content { font-size: 12pt; color: #ffffff; white-space: pre-wrap; font-weight: 600; font-family: 'Times New Roman', Times, serif; }
  .export-body .section-block { margin-bottom: 20px; padding: 16px; border: 1px solid #e2e8f0; border-radius: 8px; page-break-inside: avoid; }
  .export-body .section-block h3 { margin-top: 0; }
  .disclaimer { margin: 24px 32px; padding: 16px 20px; background: #dc2626; border: 3px solid #b91c1c; border-radius: 8px; page-break-inside: avoid; break-inside: avoid; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; display: flex; gap: 14px; align-items: flex-start; }
  .disclaimer .disc-hazard { font-size: 28px; color: #facc15; flex-shrink: 0; }
  .disclaimer strong { display: block; font-size: 13px; color: #fff; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
  .disclaimer p { font-size: 11px; color: #ffffff; line-height: 1.6; margin: 0; font-weight: 700; }
  .branding { text-align: center; margin: 24px 32px; padding: 16px 0; page-break-inside: avoid; break-inside: avoid; }
  .branding .by-line { font-size: 12px; font-weight: 700; color: #334155; margin: 0 0 10px; }
  .branding-inner { display: inline-flex; align-items: center; gap: 10px; }
  .branding-icon { width: 36px; height: 36px; background: #dc2626; border-radius: 6px; display: flex; align-items: center; justify-content: center; }
  .branding-text { text-align: left; }
  .branding-text .name { margin: 0; font-weight: 700; font-size: 13px; color: #0f172a; }
  .branding-text .sub { margin: 0; font-size: 11px; color: #64748b; }
  .print-footer { position: fixed; left: 0; right: 0; bottom: 0; background: #fff; border-top: 1px solid #cbd5e1; padding: 8px 24px 10px; }
  .print-footer-row { display: flex; justify-content: space-between; align-items: center; font-size: 10pt; font-style: italic; color: #475569; font-family: 'Times New Roman', Times, serif; }
  .print-footer-page::after { content: ''; }
  .page-break { page-break-before: always; }
  @media print {
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
    body { background: #fff; }
    .export-container { max-width: none; }
    .print-footer { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
    .print-footer-page::after { content: "Page " counter(page); }
    .disclaimer { print-color-adjust: exact; -webkit-print-color-adjust: exact; page-break-inside: avoid; break-inside: avoid; }
    .branding { page-break-inside: avoid; break-inside: avoid; }
    .disclaimer + .branding { page-break-before: avoid; break-before: avoid; }
    .export-header { print-color-adjust: exact; -webkit-print-color-adjust: exact; page-break-inside: avoid; break-inside: avoid; }
    .export-body th { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
  }
  @media (max-width: 768px) {
    body { font-size: 10px; }
    .export-header { padding: 18px 16px; }
    .export-header h1 { font-size: 22px; }
    .export-meta { padding: 12px 16px; gap: 10px; }
    .export-body { padding: 16px; }
    .export-body h2 { font-size: 14px; }
    .export-body h3 { font-size: 12px; }
    .export-body table { font-size: 9px; }
    .export-body th, .export-body td { padding: 5px 6px; }
    .disclaimer { margin: 12px 16px; padding: 12px 14px; }
    .branding { margin: 12px 16px; }
    .print-footer { padding: 6px 12px; }
    .print-footer-row { font-size: 8px; }
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
    <p>This application is an educational research tool only and does NOT constitute legal advice. It must NOT be relied upon as such. The creator of this application is not a lawyer. All analysis, findings, reports, and recommendations generated by this tool must be independently verified by a qualified Australian legal professional before any action is taken. This tool covers Australian law only. No solicitor-client relationship is created by using this service.</p>
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
