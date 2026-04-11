# DO NOT UNDO — Shared export footer utilities for all PDF and DOCX exports.
# Implements the standardised footer format:
# "Documented from the Criminal Law /Appeal Management Application - [Doc Type] - For [Case Name] [Date] Page X of Y"
# Font: Times New Roman, Italic, 10pt

from datetime import datetime, timezone


def format_export_date(dt=None):
    """Format date as DD/MM/YYYY."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except Exception:
            return datetime.now(timezone.utc).strftime('%d/%m/%Y')
    return dt.strftime('%d/%m/%Y')


def build_footer_label(case: dict, doc_type: str, generated_at=None) -> str:
    """Build the standardised footer label string."""
    case_title = (case.get("title") or case.get("defendant_name") or "Appellant").strip()
    doc_type = (doc_type or "Legal Report").strip()
    date_str = format_export_date(generated_at)
    return f"Documented from the Criminal Law /Appeal Management Application - {doc_type} - For {case_title} {date_str}"


# ============ ReportLab PDF "Page X of Y" Canvas ============

class NumberedCanvas:
    """Factory that produces a Canvas subclass rendering 'Page X of Y' footers
    after all pages have been built (two-pass approach)."""

    def __init__(self, footer_label):
        self._footer_label = footer_label
        
    def __call__(self, filename, **kwargs):
        from reportlab.pdfgen.canvas import Canvas as _Canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors

        outer = self

        class _Numbered(_Canvas):
            def __init__(self, *args, **kw):
                _Canvas.__init__(self, *args, **kw)
                self._saved_page_states = []

            def showPage(self):
                self._saved_page_states.append(dict(self.__dict__))
                _Canvas.showPage(self)

            def save(self):
                total = len(self._saved_page_states)
                for idx, state in enumerate(self._saved_page_states):
                    self.__dict__.update(state)
                    self._draw_footer(idx + 1, total)
                    _Canvas.showPage(self)
                _Canvas.save(self)

            def _draw_footer(self, page_num, total_pages):
                self.saveState()
                footer_y = 11 * mm
                line_y = 16 * mm
                self.setStrokeColor(colors.HexColor('#cbd5e1'))
                self.setLineWidth(0.6)
                self.line(20 * mm, line_y, A4[0] - 20 * mm, line_y)
                self.setFillColor(colors.HexColor('#475569'))
                self.setFont('Times-Italic', 10)
                label = outer._footer_label
                page_str = f"Page {page_num} of {total_pages}"
                # Truncate label if too long to fit
                max_w = A4[0] - 40 * mm - self.stringWidth(page_str, 'Times-Italic', 10) - 10 * mm
                while self.stringWidth(label, 'Times-Italic', 10) > max_w and len(label) > 30:
                    label = label[:-4] + "..."
                self.drawString(20 * mm, footer_y, label)
                self.drawRightString(A4[0] - 20 * mm, footer_y, page_str)
                self.restoreState()

        return _Numbered(filename, **kwargs)


# ============ python-docx DOCX Footer ============

def apply_docx_footer(doc, footer_label):
    """Apply the standardised footer to all sections of a python-docx Document.
    Footer format: [label] Page X of Y — Times New Roman, Italic, 10pt."""
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from docx.shared import Inches

    def add_field(paragraph, field_code):
        run = paragraph.add_run()
        fld_char_begin = OxmlElement('w:fldChar')
        fld_char_begin.set(qn('w:fldCharType'), 'begin')
        instr_text = OxmlElement('w:instrText')
        instr_text.set(qn('xml:space'), 'preserve')
        instr_text.text = f' {field_code} '
        fld_char_end = OxmlElement('w:fldChar')
        fld_char_end.set(qn('w:fldCharType'), 'end')
        run._r.append(fld_char_begin)
        run._r.append(instr_text)
        run._r.append(fld_char_end)

    def style_run(run):
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.italic = True
        run.font.color.rgb = RGBColor(71, 85, 105)

    for section in doc.sections:
        section.footer_distance = Inches(0.35)
        footer = section.footer
        footer_line = footer.paragraphs[0]
        footer_line.alignment = WD_ALIGN_PARAGRAPH.LEFT

        label_run = footer_line.add_run(f"{footer_label} Page ")
        style_run(label_run)
        add_field(footer_line, 'PAGE')
        of_run = footer_line.add_run(" of ")
        style_run(of_run)
        add_field(footer_line, 'NUMPAGES')


# ============ Report Type Labels ============

REPORT_TYPE_LABELS = {
    "quick_summary": "Case Summary Report (Free)",
    "full_detailed": "Full Detailed Report ($150.00)",
    "extensive_log": "Extensive Log Report ($200.00)",
    "barrister_view": "Barrister View Report",
}

DOC_TYPE_LABELS = {
    "timeline": "Timeline of Events",
    "grounds": "Grounds of Merit Report ($99.00)",
    "notes": "Notes",
    "documents": "Uploaded Case Documents",
    "legal_framework": "Legal Framework",
    "progress": "Progress",
    "case_export": "Case Export Pack",
    "translated": "Translated Report",
}
