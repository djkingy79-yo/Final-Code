import { marked } from "marked";
import auSpelling from "./auSpelling";

/**
 * Normalise markdown so ATX headings and bullet/numbered lists are ALWAYS
 * preceded by a blank line. Many LLM outputs use single newlines or two-space
 * hard breaks, which cause headings to be swallowed into the preceding
 * paragraph and bullets to render as literal "-" text.
 */
export const normaliseMarkdown = (raw = "") => {
  if (!raw) return "";
  let text = String(raw).replace(/\r\n/g, "\n");
  // Collapse trailing "two-space hard breaks" into single newlines; we add
  // proper paragraph breaks below.
  text = text.replace(/[ \t]{2,}\n/g, "\n");
  // Ensure a blank line BEFORE ATX heading ( ## , ### , #### )
  text = text.replace(/([^\n])\n(#{1,6})\s/g, "$1\n\n$2 ");
  // Ensure a blank line BEFORE bullet / numbered lists when the preceding
  // line is regular prose (not already blank and not another list item).
  text = text.replace(/([^\n\-\*\d])\n([\-\*]\s+)/g, "$1\n\n$2");
  text = text.replace(/([^\n\-\*\d])\n(\d+\.\s+)/g, "$1\n\n$2");
  // Ensure a blank line BEFORE GFM tables (line starting with | or ending |).
  // A pipe-table without a preceding blank line is treated as a paragraph by
  // most markdown parsers and rendered as literal "| header |" text.
  text = text.replace(/([^\n|])\n(\|)/g, "$1\n\n$2");
  // Collapse 3+ newlines to exactly 2
  text = text.replace(/\n{3,}/g, "\n\n");
  // Tighten consecutive bullet list items (we may have added spurious blank
  // lines between them during the heading/list normalisation pass).
  text = text.replace(/([\-\*][^\n]+)\n\n(?=[\-\*]\s)/g, "$1\n");
  text = text.replace(/(\d+\.[^\n]+)\n\n(?=\d+\.\s)/g, "$1\n");
  return text.trim();
};

// Configure marked once — GitHub-flavoured, no HTML passthrough for safety.
marked.setOptions({
  gfm: true,
  breaks: false,
  headerIds: false,
  mangle: false,
});

/**
 * Render markdown to an HTML string suitable for embedding inside an
 * export/print HTML template. Applies Australian spelling normalisation
 * AFTER parsing so token boundaries are preserved.
 */
export const renderMarkdownToHtml = (raw = "") => {
  if (!raw) return "";
  const normalised = normaliseMarkdown(raw);
  const html = marked.parse(normalised, { async: false });
  return auSpelling(html);
};
