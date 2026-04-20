# DO NOT UNDO — translate router. Extracted from export.py.
"""
Criminal Appeal AI - Report Translation Router
Handles translation of reports into 41 languages with cached results and PDF export.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
from pydantic import BaseModel
import asyncio
import io
import re
import uuid
import logging

from config import db
from auth_utils import get_current_user, verify_case_ownership
from services.llm_service import call_llm_structured

logger = logging.getLogger(__name__)

# In-memory store for running translation tasks
_translate_tasks: dict = {}

translate_router = APIRouter(prefix="/api", tags=["translation"])

SUPPORTED_LANGUAGES = {
    "en": "English",
    "zh": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "hi": "Hindi",
    "ar": "Arabic",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "ko": "Korean",
    "vi": "Vietnamese",
    "th": "Thai",
    "tl": "Filipino/Tagalog",
    "el": "Greek",
    "tr": "Turkish",
    "ru": "Russian",
    "pl": "Polish",
    "nl": "Dutch",
    "sv": "Swedish",
    "id": "Indonesian",
    "ms": "Malay",
    "fa": "Persian/Farsi",
    "ur": "Urdu",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "ne": "Nepali",
    "si": "Sinhala",
    "my": "Burmese",
    "km": "Khmer",
    "lo": "Lao",
    "am": "Amharic",
    "sw": "Swahili",
    "so": "Somali",
    "ti": "Tigrinya",
    "to": "Tongan",
    "sm": "Samoan",
    "mi": "Maori",
    "pa": "Punjabi",
}


REPORT_TYPE_LABELS = {
    "quick_summary": "Quick Summary Report",
    "full_detailed": "Full Detailed Report",
    "extensive_log": "Extensive Log Report",
    "barrister_view": "Appellate Research Brief",
    "acceptance_pack": "Barrister Acceptance Pack",
    "translated": "Translated Report",
}


class TranslateRequest(BaseModel):
    language: str
    report_id: str


def _format_inline(text: str) -> str:
    clean = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", clean)
    clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
    return clean


def _render_table_to_story(lines, story_ref, doc_ref, body_style=None):
    """Module-level table renderer for PDF exports."""
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    rows = []
    for line in lines:
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if not parts:
            continue
        if all(set(p) <= set("-:") for p in parts):
            continue
        safe_parts = [re.sub(r"\*\*(.*?)\*\*", r"\1", p).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for p in parts]
        rows.append(safe_parts)
    if not rows:
        return
    col_count = max(len(r) for r in rows)
    rows = [r + [""] * (col_count - len(r)) for r in rows]
    try:
        col_width = doc_ref.width / col_count
        cell_style = ParagraphStyle(name="TblCell", fontSize=9, leading=12, fontName="Helvetica", wordWrap="CJK")
        header_cell = ParagraphStyle(name="TblHeader", fontSize=9, leading=12, fontName="Helvetica-Bold", textColor=colors.white)
        para_rows = []
        for ri, row in enumerate(rows):
            st = header_cell if ri == 0 else cell_style
            para_rows.append([Paragraph(c[:260], st) for c in row])
        table = Table(para_rows, colWidths=[col_width] * col_count, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story_ref.append(table)
        story_ref.append(Spacer(1, 4 * mm))
    except Exception as e:
        logger.warning(f"Table render failed: {e}")
        fallback = body_style or cell_style
        for row in rows:
            story_ref.append(Paragraph(" | ".join(row), fallback))


@translate_router.get("/languages")
async def get_supported_languages():
    """Return the list of supported translation languages."""
    return {"languages": [{"code": k, "name": v} for k, v in SUPPORTED_LANGUAGES.items()]}


@translate_router.post("/cases/{case_id}/translate")
async def translate_report(case_id: str, req: TranslateRequest, request: Request):
    """Start translating a report. Returns cached result instantly or starts background task."""
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)

    if req.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {req.language}")

    if req.language == "en":
        raise HTTPException(status_code=400, detail="Report is already in English.")

    # Fetch report
    report = await db.reports.find_one(
        {"report_id": req.report_id, "case_id": case_id, "user_id": user.user_id, "status": "completed"},
        {"_id": 0},
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    analysis = (report.get("content") or {}).get("analysis", "")
    if not analysis:
        raise HTTPException(status_code=400, detail="Report has no content to translate.")

    target_lang = SUPPORTED_LANGUAGES[req.language]

    # Check for cached translation
    cached = await db.report_translations.find_one(
        {"report_id": req.report_id, "language": req.language},
        {"_id": 0},
    )
    if cached:
        return {"translated_content": cached["translated_content"], "language": req.language, "language_name": target_lang, "cached": True}

    # Check if a task is already running for this report+language
    task_key = f"{req.report_id}_{req.language}"
    if task_key in _translate_tasks and _translate_tasks[task_key].get("status") == "running":
        return {"status": "running", "task_id": _translate_tasks[task_key]["task_id"], "language_name": target_lang}

    # Start background translation task
    task_id = str(uuid.uuid4())[:12]
    _translate_tasks[task_key] = {"task_id": task_id, "status": "running", "progress": 0, "total_chunks": 0}

    asyncio.create_task(_run_translation_background(
        task_key=task_key,
        task_id=task_id,
        report_id=req.report_id,
        case_id=case_id,
        user_id=user.user_id,
        language=req.language,
        target_lang=target_lang,
        analysis=analysis,
    ))

    return {"status": "started", "task_id": task_id, "language_name": target_lang}


async def _persist_task(task_key: str, state: dict) -> None:
    """Mirror the in-memory translation task snapshot into Mongo so the
    status endpoint can recover after a backend restart wipes memory."""
    try:
        await db.translation_tasks.replace_one(
            {"task_key": task_key},
            {
                "task_key": task_key,
                "updated_at": datetime.now(timezone.utc),
                **state,
            },
            upsert=True,
        )
    except Exception as e:
        logger.warning(f"translation_tasks persist failed for {task_key}: {e}")


async def _run_translation_background(*, task_key, task_id, report_id, case_id, user_id, language, target_lang, analysis):
    """Background coroutine that translates all chunks and caches the result.

    Chunks are translated with bounded concurrency (semaphore=3) so a 10-chunk
    report completes in ~1/3 the wall time of the previous sequential loop
    without exceeding the user's OpenAI per-minute rate limits.
    """
    try:
        system_prompt = (
            f"You are a professional legal document translator. Translate the following Australian criminal law appeal report "
            f"from English into {target_lang}. Preserve ALL legal terminology, case citations, section references, formatting "
            f"(headings, bullet points, numbered lists, tables), and the overall structure. "
            f"Do NOT add commentary, opinions, or new content. Do NOT invent or fabricate any citations, section numbers, or facts. "
            f"Do NOT default to NSW legislation references — preserve the original jurisdiction references exactly as they appear. "
            f"Preserve all forensic appellate language (e.g. 'it is arguable that' should remain hedged in the target language). "
            f"Translate accurately and completely. Keep markdown formatting intact. Use Australian English spelling for any untranslated terms."
        )

        max_chunk = 12000
        if len(analysis) <= max_chunk:
            chunks = [analysis]
        else:
            paragraphs = analysis.split("\n\n")
            chunks = []
            current = ""
            for para in paragraphs:
                if len(current) + len(para) + 2 > max_chunk:
                    if current:
                        chunks.append(current)
                    current = para
                else:
                    current = current + "\n\n" + para if current else para
            if current:
                chunks.append(current)

        total_chunks = len(chunks)
        _translate_tasks[task_key]["total_chunks"] = total_chunks
        await _persist_task(task_key, {
            "task_id": task_id, "status": "running", "progress": 0,
            "total_chunks": total_chunks, "report_id": report_id,
            "case_id": case_id, "user_id": user_id, "language": language,
            "language_name": target_lang,
        })

        translated_parts: list = [None] * total_chunks
        progress_counter = {"done": 0}
        # Concurrency limit — 3 parallel chunks is a sweet spot: ~3x wall-time
        # reduction without tripping OpenAI per-minute token rate limits.
        sem = asyncio.Semaphore(3)

        async def translate_chunk(index: int, chunk: str):
            async with sem:
                user_prompt = f"Translate the following into {target_lang}:\n\n{chunk}"
                result = await call_llm_structured(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    session_id=f"translate_{report_id}_{language}_{index}",
                    task_type="general",
                    max_tokens=16384,
                    timeout_seconds=180,
                    require_json=False,
                )
                if not result["ok"]:
                    raise RuntimeError(result.get("error", "LLM call failed"))
                translated_parts[index] = result["content"]
                progress_counter["done"] += 1
                _translate_tasks[task_key]["progress"] = progress_counter["done"]
                await _persist_task(task_key, {
                    "task_id": task_id, "status": "running",
                    "progress": progress_counter["done"],
                    "total_chunks": total_chunks, "report_id": report_id,
                    "case_id": case_id, "user_id": user_id, "language": language,
                    "language_name": target_lang,
                })

        try:
            await asyncio.gather(*(translate_chunk(i, c) for i, c in enumerate(chunks)))
        except Exception as chunk_err:
            _translate_tasks[task_key] = {"task_id": task_id, "status": "failed", "error": str(chunk_err)[:200]}
            await _persist_task(task_key, {
                "task_id": task_id, "status": "failed", "error": str(chunk_err)[:200],
                "report_id": report_id, "case_id": case_id, "user_id": user_id,
                "language": language, "language_name": target_lang,
            })
            return

        translated_content = "\n\n".join(p or "" for p in translated_parts)

        # Cache translation
        await db.report_translations.replace_one(
            {"report_id": report_id, "language": language},
            {
                "report_id": report_id,
                "case_id": case_id,
                "user_id": user_id,
                "language": language,
                "language_name": target_lang,
                "translated_content": translated_content,
                "translated_at": datetime.now(timezone.utc).isoformat(),
            },
            upsert=True,
        )

        _translate_tasks[task_key] = {"task_id": task_id, "status": "completed", "language": language, "language_name": target_lang}
        await _persist_task(task_key, {
            "task_id": task_id, "status": "completed",
            "language": language, "language_name": target_lang,
            "report_id": report_id, "case_id": case_id, "user_id": user_id,
            "progress": total_chunks, "total_chunks": total_chunks,
        })
        logger.info(f"Translation completed: {report_id} -> {target_lang} ({total_chunks} chunks)")

    except Exception as e:
        logger.error(f"Background translation failed: {e}")
        _translate_tasks[task_key] = {"task_id": task_id, "status": "failed", "error": str(e)[:200]}
        await _persist_task(task_key, {
            "task_id": task_id, "status": "failed", "error": str(e)[:200],
            "report_id": report_id, "case_id": case_id, "user_id": user_id,
            "language": language, "language_name": target_lang,
        })


@translate_router.get("/cases/{case_id}/translate/status")
async def translate_status(case_id: str, report_id: str, language: str, request: Request):
    """Poll translation progress. Returns cached result when complete."""
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)

    target_lang = SUPPORTED_LANGUAGES.get(language, language)
    task_key = f"{report_id}_{language}"

    # Check if cached result exists (translation completed)
    cached = await db.report_translations.find_one(
        {"report_id": report_id, "language": language},
        {"_id": 0},
    )
    if cached:
        # Clean up task
        _translate_tasks.pop(task_key, None)
        return {"status": "completed", "translated_content": cached["translated_content"], "language": language, "language_name": target_lang}

    # Check in-memory task status
    task = _translate_tasks.get(task_key)
    if not task:
        # In-memory state lost (e.g. backend was restarted mid-translation).
        # Fall back to the persisted snapshot so the UI can keep polling.
        persisted = await db.translation_tasks.find_one({"task_key": task_key}, {"_id": 0})
        if persisted:
            status = persisted.get("status")
            if status == "failed":
                return {"status": "failed", "error": persisted.get("error", "Unknown error")}
            if status == "completed":
                # Cached translation missing but task marked complete — shouldn't happen,
                # but treat as completed-without-cache so the user sees a clean failure.
                return {"status": "failed", "error": "Translation completed but cache is missing. Please retry."}
            # Still running — surface last persisted progress
            return {
                "status": "running",
                "progress": persisted.get("progress", 0),
                "total_chunks": persisted.get("total_chunks", 0),
                "recovered": True,
            }
        return {"status": "not_found"}

    if task["status"] == "failed":
        error = task.get("error", "Unknown error")
        _translate_tasks.pop(task_key, None)
        return {"status": "failed", "error": error}

    return {"status": "running", "progress": task.get("progress", 0), "total_chunks": task.get("total_chunks", 0)}


@translate_router.get("/cases/{case_id}/translate/{report_id}/pdf")
async def export_translated_report_pdf(case_id: str, report_id: str, lang: str, request: Request):
    """Generate a properly formatted PDF of a translated report."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)

    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")

    target_lang_name = SUPPORTED_LANGUAGES[lang]

    # Fetch cached translation
    cached = await db.report_translations.find_one(
        {"report_id": report_id, "case_id": case_id, "language": lang},
        {"_id": 0},
    )
    if not cached:
        raise HTTPException(status_code=404, detail="Translation not found. Please translate the report first.")

    # Fetch case and report metadata
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    report = await db.reports.find_one(
        {"report_id": report_id, "case_id": case_id},
        {"_id": 0, "report_type": 1, "generated_at": 1},
    )

    report_label = REPORT_TYPE_LABELS.get(report.get("report_type") if report else "", "Report")
    sentence = case.get("sentence") or "See report analysis"

    # Register CJK font for Asian languages
    cjk_langs = {"zh", "zh-TW", "ja", "ko", "th", "my", "km", "lo", "si", "bn", "ta", "te", "ne", "hi", "pa", "ur"}
    use_cjk = lang in cjk_langs
    body_font = "Helvetica"
    bold_font = "Helvetica-Bold"

    if use_cjk:
        try:
            import os
            noto_paths = [
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/noto-cjk/NotoSansCJKsc-Regular.otf",
            ]
            for fp in noto_paths:
                if os.path.exists(fp):
                    pdfmetrics.registerFont(TTFont("NotoSansCJK", fp))
                    body_font = "NotoSansCJK"
                    bold_font = "NotoSansCJK"
                    break
        except Exception:
            pass

    # Build PDF
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=22 * mm,
        leftMargin=22 * mm,
        topMargin=22 * mm,
        bottomMargin=28 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TrTitle", fontSize=20, spaceAfter=8, alignment=TA_CENTER, fontName=bold_font, textColor=colors.HexColor("#0f172a")))
    styles.add(ParagraphStyle(name="TrSubtitle", fontSize=11, spaceAfter=5, alignment=TA_CENTER, textColor=colors.HexColor("#475569"), fontName=body_font))
    styles.add(ParagraphStyle(name="TrSection", fontSize=14, spaceBefore=14, spaceAfter=6, fontName=bold_font, textColor=colors.HexColor("#0f172a")))
    styles.add(ParagraphStyle(name="TrSubSection", fontSize=11, spaceBefore=8, spaceAfter=4, fontName=bold_font, textColor=colors.HexColor("#1e293b")))
    styles.add(ParagraphStyle(name="TrBody", fontSize=10.5, spaceAfter=4, alignment=TA_JUSTIFY, leading=15, fontName=body_font))
    styles.add(ParagraphStyle(name="TrBullet", fontSize=10.5, spaceAfter=3, leading=15, fontName=body_font, leftIndent=14, bulletIndent=7))
    styles.add(ParagraphStyle(name="TrDisclaimer", fontSize=10, fontName=bold_font, textColor=colors.HexColor("#dc2626"), alignment=TA_CENTER, leading=14))
    styles.add(ParagraphStyle(name="TrMetaValue", fontSize=11, fontName=bold_font, textColor=colors.HexColor("#0f172a"), spaceAfter=4))
    styles.add(ParagraphStyle(name="TrLangBadge", fontSize=12, fontName=bold_font, textColor=colors.HexColor("#1e40af"), alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle(name="TrNumberedHeader", fontSize=12, spaceBefore=10, spaceAfter=5, fontName=bold_font, textColor=colors.HexColor("#0f172a")))

    story = []

    # COVER PAGE
    story.append(Spacer(1, 22 * mm))
    story.append(Paragraph("APPEAL CASE MANAGER", styles["TrSubtitle"]))
    story.append(Paragraph(report_label, styles["TrTitle"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f"Translated to {target_lang_name}", styles["TrLangBadge"]))
    story.append(Spacer(1, 10 * mm))

    cover_data = [
        ["Case Title", case.get("title", "N/A")],
        ["Defendant", case.get("defendant_name", "N/A")],
        ["Court / State", f"{case.get('court', 'Court')} — {(case.get('state', 'NSW') or 'NSW').upper()}"],
        ["Sentence", sentence],
        ["Language", target_lang_name],
    ]
    cover_rows = []
    for label, val in cover_data:
        cover_rows.append([
            Paragraph(f"<b>{label}</b>", styles["TrMetaValue"]),
            Paragraph(str(val), styles["TrBody"]),
        ])
    cover_table = Table(cover_rows, colWidths=[40 * mm, 115 * mm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(
        "IMPORTANT DISCLAIMER — NOT LEGAL ADVICE — This application is an educational research tool only "
        "and does NOT constitute legal advice. The creator is not a lawyer. All analysis and recommendations "
        "must be independently verified by a qualified Australian legal professional. Australian law only. "
        "No solicitor-client relationship is created.",
        styles["TrDisclaimer"],
    ))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        f"Exported: {datetime.now(timezone.utc).strftime('%d %B %Y at %H:%M UTC')}",
        styles["TrSubtitle"],
    ))
    story.append(PageBreak())

    # TRANSLATED CONTENT
    translated_text = cached["translated_content"]
    lines = (translated_text or "").splitlines()
    buffer = []

    def flush_buf():
        if buffer:
            para = " ".join(buffer).strip()
            if para:
                safe = _format_inline(para)
                try:
                    story.append(Paragraph(safe, styles["TrBody"]))
                    story.append(Spacer(1, 2 * mm))
                except Exception:
                    clean = re.sub(r"<[^>]+>", "", safe)
                    story.append(Paragraph(clean, styles["TrBody"]))
                    story.append(Spacer(1, 2 * mm))
            buffer.clear()

    table_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_buf()
            continue

        # Table detection
        if stripped.startswith("|") and "|" in stripped:
            flush_buf()
            table_lines.append(stripped)
            continue
        if table_lines:
            _render_table_to_story(table_lines, story, doc)
            table_lines = []

        # Headings
        if stripped.startswith("## "):
            flush_buf()
            story.append(Paragraph(_format_inline(stripped[3:].strip()), styles["TrSection"]))
            story.append(Spacer(1, 2 * mm))
            continue
        if re.match(r"^\d+\.\s+[A-Z\u0400-\u04FF\u0600-\u06FF\u4E00-\u9FFF]", stripped) and len(stripped) < 120:
            flush_buf()
            story.append(Paragraph(_format_inline(stripped), styles["TrNumberedHeader"]))
            story.append(Spacer(1, 2 * mm))
            continue
        if stripped.startswith("### ") or stripped.startswith("#### "):
            flush_buf()
            hdr = stripped.lstrip("#").strip()
            story.append(Paragraph(_format_inline(hdr), styles["TrSubSection"]))
            story.append(Spacer(1, 1 * mm))
            continue
        if stripped.startswith("- ") or stripped.startswith("• "):
            flush_buf()
            story.append(Paragraph(_format_inline(f"- {stripped[2:].strip()}"), styles["TrBullet"]))
            story.append(Spacer(1, 1 * mm))
            continue
        if re.match(r"^\d+\.\s", stripped):
            flush_buf()
            story.append(Paragraph(_format_inline(stripped), styles["TrBullet"]))
            story.append(Spacer(1, 1 * mm))
            continue

        buffer.append(stripped)

    flush_buf()
    if table_lines:
        _render_table_to_story(table_lines, story, doc)

    # Final disclaimer
    story.append(Spacer(1, 15 * mm))
    story.append(Paragraph(
        "NOT LEGAL ADVICE — This translated report is an educational research tool only. "
        "All analysis must be verified by a qualified Australian legal professional. "
        "Translation accuracy cannot be guaranteed for legal terminology.",
        styles["TrDisclaimer"],
    ))

    # Footer
    from services.export_footer import build_footer_label, NumberedCanvas
    tr_label = f"{report_label} ({target_lang_name} Translation)"
    footer_label = build_footer_label(case, tr_label)
    numbered_canvas = NumberedCanvas(footer_label)

    try:
        doc.build(story, canvasmaker=numbered_canvas)
    except Exception as e:
        logger.error(f"Translated PDF build failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)[:200]}")

    pdf_buffer.seek(0)
    safe_title = "".join(c for c in case.get("title", "Case")[:25] if c.isalnum() or c in " -_").strip()
    filename = f"{safe_title}_{target_lang_name}_Translation.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Section-only translation — fast path for barristers who just want to
# translate a single section (e.g. "Grounds of Appeal") for a client.
# Synchronous because a single section typically fits in one LLM call
# (<=12k chars), so there's no need for the background task + polling dance.
# ---------------------------------------------------------------------------

class SectionTranslateRequest(BaseModel):
    report_id: str
    language: str
    section_heading: str
    section_text: str


@translate_router.post("/cases/{case_id}/translate-section")
async def translate_section(case_id: str, payload: SectionTranslateRequest, request: Request):
    """Translate a single report section on-demand.

    Cached under `report_section_translations` keyed by
    (report_id, language, section_slug) so repeat requests are instant.
    """
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)

    if payload.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {payload.language}")
    if payload.language == "en":
        return {"status": "completed", "translated_content": payload.section_text, "cached": False}

    target_lang = SUPPORTED_LANGUAGES[payload.language]
    section_slug = re.sub(r"[^a-z0-9]+", "-", payload.section_heading.lower()).strip("-")[:80] or "section"
    # Validate input size — protect against abuse / runaway prompts
    section_text = payload.section_text.strip()
    if not section_text:
        raise HTTPException(status_code=400, detail="section_text cannot be empty")
    if len(section_text) > 30000:
        raise HTTPException(status_code=400, detail="Section too long — use the full report translator instead")

    # Cache hit?
    cache = await db.report_section_translations.find_one(
        {"report_id": payload.report_id, "language": payload.language, "section_slug": section_slug},
        {"_id": 0, "translated_content": 1, "language_name": 1},
    )
    if cache:
        return {
            "status": "completed",
            "language": payload.language,
            "language_name": cache.get("language_name", target_lang),
            "translated_content": cache["translated_content"],
            "cached": True,
        }

    # Verify the report belongs to this case (defense in depth)
    report = await db.reports.find_one({"report_id": payload.report_id, "case_id": case_id}, {"_id": 0, "report_id": 1})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this case")

    system_prompt = (
        f"You are a professional legal document translator. Translate the following section of an Australian criminal law appeal report "
        f"from English into {target_lang}. Preserve ALL legal terminology, case citations, section references, markdown formatting "
        f"(headings, bullet points, numbered lists, tables), and the section's structure. "
        f"Do NOT add commentary, opinions, or new content. Do NOT invent or fabricate any citations, section numbers, or facts. "
        f"Do NOT default to NSW legislation references — preserve the original jurisdiction references exactly as they appear. "
        f"Preserve forensic appellate hedging (e.g. 'it is arguable that') in the target language. "
        f"Use Australian English spelling for any untranslated English terms."
    )
    user_prompt = f"Translate the following section titled \"{payload.section_heading}\" into {target_lang}:\n\n{section_text}"

    result = await call_llm_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        session_id=f"translate_section_{payload.report_id}_{payload.language}_{section_slug}",
        task_type="general",
        max_tokens=16384,
        timeout_seconds=120,
        require_json=False,
    )
    if not result["ok"]:
        raise HTTPException(status_code=502, detail=result.get("error", "Translation failed"))

    translated = result["content"]

    # Cache result (fire-and-forget style — don't fail the response if write errors)
    try:
        await db.report_section_translations.replace_one(
            {"report_id": payload.report_id, "language": payload.language, "section_slug": section_slug},
            {
                "report_id": payload.report_id,
                "case_id": case_id,
                "user_id": user.user_id,
                "language": payload.language,
                "language_name": target_lang,
                "section_slug": section_slug,
                "section_heading": payload.section_heading,
                "translated_content": translated,
                "translated_at": datetime.now(timezone.utc),
            },
            upsert=True,
        )
    except Exception as e:
        logger.warning(f"Section translation cache write failed: {e}")

    return {
        "status": "completed",
        "language": payload.language,
        "language_name": target_lang,
        "translated_content": translated,
        "cached": False,
    }
