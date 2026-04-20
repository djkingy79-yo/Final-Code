# ===========================================================================
# Report CRUD & Generation API Routes
# Extracted from server.py — report endpoints and background tasks
# ===========================================================================

import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List

from fastapi import APIRouter, HTTPException, Request
from starlette.responses import StreamingResponse

from config import db, logger
from auth_utils import get_current_user
from models import ReportRequest, FEATURE_PRICES, feature_type_variants
from services.report_generator import analyze_case_with_ai
from services.barrister_generator import (
    _get_latest_standard_reports,
    _build_barrister_source_signature,
    _run_barrister_report_generation,
    _coerce_utc_datetime,
    BARRISTER_GENERATION_TIMEOUT_MINUTES,
)
from services.pipeline_orchestrator import (
    _pipeline_artifacts_missing_or_stale,
    _refresh_pipeline_for_reporting,
    _auto_verification_limit_for_report_type,
    _select_issues_for_auto_verification,
    _auto_verify_selected_issues,
    _sync_pipeline_projection_to_grounds,
)
from config import is_admin_user
from routers.report_exports import export_report_pdf, export_report_docx
from services.case_validation import validate_case_metadata, log_metadata_warnings

router = APIRouter(prefix="/api")


async def _run_report_generation(report_id: str, case_id: str, user_id: str, report_type: str, aggressive_mode: bool):
    """Background task that generates the AI report and updates the DB record — HARDENED with metadata."""
    pipeline_refresh_result = {"refreshed": False, "extracted_count": 0, "classified_count": 0, "synced_count": 0, "auto_verify_limit": 0, "auto_verify_result": {"attempted": 0, "verified": 0, "failed": 0}}
    try:
        # Pre-draft pipeline refresh: ensure staged artifacts are current
        case = await db.cases.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0})
        if case:
            documents = await db.documents.find(
                {"case_id": case_id, "user_id": user_id}, {"_id": 0, "file_data": 0}
            ).to_list(500)
            try:
                needs_refresh = await _pipeline_artifacts_missing_or_stale(case, documents)
                if needs_refresh:
                    refreshed = await _refresh_pipeline_for_reporting(case, documents, report_type)
                    pipeline_refresh_result = {"refreshed": True, **refreshed}
                    logger.info(f"Pipeline refreshed for report {report_id}: {pipeline_refresh_result}")
                else:
                    # Even if artifacts exist, paid report tiers may justify additional auto-verification
                    auto_verify_limit = _auto_verification_limit_for_report_type(report_type)
                    if auto_verify_limit > 0:
                        selected_issues = await _select_issues_for_auto_verification(case, auto_verify_limit)
                        auto_verify_result = await _auto_verify_selected_issues(case, selected_issues)
                        synced_count = await _sync_pipeline_projection_to_grounds(case)
                        pipeline_refresh_result = {
                            "refreshed": False,
                            "extracted_count": 0,
                            "classified_count": 0,
                            "synced_count": synced_count,
                            "auto_verify_limit": auto_verify_limit,
                            "auto_verify_result": auto_verify_result,
                        }
            except Exception as pe:
                logger.warning(f"Pipeline refresh before report {report_id} failed (non-fatal): {pe}")

        report_titles = {
            "quick_summary": "Quick Case Summary",
            "full_detailed": "Full Detailed Legal Analysis",
            "extensive_log": "Extensive Case Log & Analysis"
        }
        analysis_result = await analyze_case_with_ai(case_id, user_id, report_type, aggressive_mode, report_id=report_id)
        new_analysis = analysis_result.get("analysis", "")
        
        # DO_NOT_UNDO — Content protection: never overwrite a longer report with a shorter one.
        # If the new content is less than 50% the length of the backup, something went wrong
        # (e.g. 502 errors truncated the generation). Keep the backup instead.
        backup_doc = await db.reports.find_one(
            {"report_id": report_id},
            {"_id": 0, "content.backup_analysis": 1}
        )
        backup_analysis = (backup_doc or {}).get("content", {}).get("backup_analysis", "")
        if backup_analysis and len(backup_analysis) > 10000 and len(new_analysis) < len(backup_analysis) * 0.5:
            logger.warning(
                f"Report {report_id}: new content ({len(new_analysis)} chars) is less than 50% of backup "
                f"({len(backup_analysis)} chars). Keeping backup to prevent content loss."
            )
            await db.reports.update_one(
                {"report_id": report_id},
                {"$set": {
                    "status": "completed",
                    "error": None,
                    "content.analysis": backup_analysis,
                    "content.partial": False,
                },
                "$unset": {"content.backup_analysis": 1, "generation_progress": 1}}
            )
            logger.info(f"Report {report_id}: restored backup instead of thin regeneration")
            return

        title = report_titles.get(report_type, "Report")
        if aggressive_mode:
            title = f"{title} (Aggressive)"

        # ── Citation post-processing: strip hallucinated citations ──
        from services.case_validation import strip_hallucinated_citations, validate_similar_cases, validate_law_sections
        clean_analysis = strip_hallucinated_citations(analysis_result.get("analysis", ""))
        clean_grounds = []
        for g in analysis_result.get("grounds_of_merit", []):
            g["similar_cases"] = validate_similar_cases(g.get("similar_cases", []))
            g["law_sections"] = validate_law_sections(g.get("law_sections", []))
            clean_grounds.append(g)

        await db.reports.update_one(
            {"report_id": report_id},
            {"$set": {
                "status": "completed",
                "title": title,
                "content": {
                    "analysis": clean_analysis,
                    "case_title": (analysis_result.get("case_data") or {}).get("title", ""),
                    "defendant": (analysis_result.get("case_data") or {}).get("defendant_name", ""),
                    "document_count": analysis_result.get("document_count", 0),
                    "event_count": analysis_result.get("event_count", 0),
                    "aggressive_mode": aggressive_mode,
                    "draft_source": "pipeline" if (analysis_result.get("pipeline_metadata") or {}).get("status") in ("fresh", "refreshed") else "legacy",
                },
                "grounds_of_merit": clean_grounds,
                "metadata": {
                    **(analysis_result.get("metadata") or {}),
                    "pipeline_refresh_before_draft": pipeline_refresh_result,
                    "pipeline_issue_count": len(((analysis_result.get("pipeline_metadata") or {}).get("staleness") or {}).get("extract_missing_for_documents", [])) if analysis_result.get("pipeline_metadata") else 0,
                    "pipeline_verification_count": 0,
                    **(analysis_result.get("pipeline_metadata") or {}),
                },
                "source_mode": "ai_generated",
                "verification_status": "draft",
            },
            "$unset": {"generation_progress": 1}}
        )
        logger.info(f"Report {report_id} generated successfully")
        # Clear backup after successful generation
        await db.reports.update_one(
            {"report_id": report_id},
            {"$unset": {"content.backup_analysis": 1}}
        )
    except Exception as exc:
        logger.error(f"Report {report_id} generation failed: {exc}")
        friendly_error = "Report generation was interrupted by a temporary AI service error. Retry resumes from the last completed section."
        # DO_NOT_UNDO — Restore backup on failure. If backup_analysis exists,
        # restore it so the user doesn't lose their previous report.
        backup_doc = await db.reports.find_one(
            {"report_id": report_id},
            {"_id": 0, "content.backup_analysis": 1}
        )
        backup = (backup_doc or {}).get("content", {}).get("backup_analysis", "")
        if backup and len(backup) > 5000:
            await db.reports.update_one(
                {"report_id": report_id},
                {"$set": {
                    "status": "completed",
                    "error": None,
                    "content.analysis": backup,
                },
                "$unset": {"content.backup_analysis": 1, "generation_progress": 1}}
            )
            logger.info(f"Report {report_id} generation failed but restored from backup ({len(backup)} chars)")
        else:
            await db.reports.update_one(
                {"report_id": report_id},
                {"$set": {"status": "failed", "error": friendly_error, "technical_error": str(exc)},
                 "$unset": {"generation_progress": 1}}
            )


@router.post("/cases/{case_id}/reports/generate", response_model=dict)
async def generate_report(case_id: str, report_request: ReportRequest, request: Request):
    """Generate an AI-powered report for a case (background task)"""
    user = await get_current_user(request)
    report_type = report_request.report_type
    
    if report_type not in ["quick_summary", "full_detailed", "extensive_log"]:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    # DO_NOT_UNDO — Block duplicate generation. If a report of this type is
    # already generating, return its status instead of creating a duplicate.
    existing_generating = await db.reports.find_one(
        {
            "case_id": case_id,
            "user_id": user.user_id,
            "report_type": report_type,
            "status": "generating",
            "content.aggressive_mode": {"$ne": True},
        },
        {"_id": 0, "report_id": 1},
    )
    if existing_generating:
        return {"report_id": existing_generating["report_id"], "status": "generating", "report_type": report_type}
    
    # Check payment for premium reports (admin bypasses all payments)
    is_admin = is_admin_user(user.email)
    
    if report_type == "full_detailed" and not is_admin:
        payment = await db.payments.find_one({
            "case_id": case_id,
            "user_id": user.user_id,
            "feature_type": {"$in": feature_type_variants("full_report")},
            "status": "completed"
        })
        if not payment:
            raise HTTPException(
                status_code=402, 
                detail={
                    "message": "Payment required for Full Detailed Report",
                    "feature_type": "full_report",
                    "price": FEATURE_PRICES["full_report"]["price"],
                    "currency": "AUD"
                }
            )
    
    if report_type == "extensive_log" and not is_admin:
        payment = await db.payments.find_one({
            "case_id": case_id,
            "user_id": user.user_id,
            "feature_type": {"$in": feature_type_variants("extensive_report")},
            "status": "completed"
        })
        if not payment:
            raise HTTPException(
                status_code=402, 
                detail={
                    "message": "Payment required for Extensive Log Report",
                    "feature_type": "extensive_report",
                    "price": FEATURE_PRICES["extensive_report"]["price"],
                    "currency": "AUD"
                }
            )
    
    existing_failed = await db.reports.find(
        {
            "case_id": case_id,
            "user_id": user.user_id,
            "report_type": report_type,
            "status": "failed",
            "content.aggressive_mode": {"$ne": True},
        },
        {"_id": 0},
    ).sort("generated_at", -1).to_list(1)

    if existing_failed:
        resumed_report = existing_failed[0]
        await db.reports.update_one(
            {"report_id": resumed_report["report_id"]},
            {"$set": {"status": "generating", "error": None, "generated_at": datetime.now(timezone.utc).isoformat()}},
        )
        asyncio.create_task(
            _run_report_generation(resumed_report["report_id"], case_id, user.user_id, report_type, False)
        )
        resumed_report["status"] = "generating"
        resumed_report["error"] = None
        return resumed_report

    # If a completed report of this type already exists, reuse its ID (regenerate in-place)
    existing_completed = await db.reports.find_one(
        {
            "case_id": case_id,
            "user_id": user.user_id,
            "report_type": report_type,
            "status": "completed",
            "content.aggressive_mode": {"$ne": True},
        },
        {"_id": 0, "report_id": 1},
    )
    if existing_completed:
        report_id = existing_completed["report_id"]
        # DO_NOT_UNDO — NEVER wipe content.analysis during regeneration.
        # Keep the old report visible to the user while the new one generates.
        # Only clear partial_analysis and passes_completed (used by the generation engine).
        # The old analysis stays visible until the new generation completes and overwrites it.
        existing_doc = await db.reports.find_one({"report_id": report_id}, {"_id": 0, "content.analysis": 1})
        old_analysis = existing_doc.get("content", {}).get("analysis", "") if existing_doc else ""
        await db.reports.update_one(
            {"report_id": report_id},
            {"$set": {
                "status": "generating",
                "error": None,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "content.partial_analysis": "",
                "content.passes_completed": 0,
                "content.aggressive_mode": False,
                "content.backup_analysis": old_analysis,
            }}
        )
        asyncio.create_task(
            _run_report_generation(report_id, case_id, user.user_id, report_type, False)
        )
        return {"report_id": report_id, "status": "generating", "report_type": report_type}

    # Create a placeholder report with "generating" status and return immediately
    report_id = f"rpt_{uuid.uuid4().hex[:12]}"

    # ── Soft metadata validation (warns but does not block) ──
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    metadata_validation = validate_case_metadata(case) if case else {"complete": False, "warnings": ["Case not found"]}
    log_metadata_warnings(case_id, metadata_validation, f"report:{report_type}")

    report_titles = {
        "quick_summary": "Quick Case Summary",
        "full_detailed": "Full Detailed Legal Analysis",
        "extensive_log": "Extensive Case Log & Analysis"
    }
    aggressive_mode = False
    title = report_titles.get(report_type, "Report")
    placeholder = {
        "report_id": report_id,
        "case_id": case_id,
        "user_id": user.user_id,
        "report_type": report_type,
        "title": title,
        "content": {"analysis": "", "aggressive_mode": aggressive_mode},
        "grounds_of_merit": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "generating",
        "source_mode": "ai_generated",
        "verification_status": "draft",
    }
    insert_doc = {k: v for k, v in placeholder.items()}
    await db.reports.insert_one(insert_doc)

    # Fire-and-forget background task
    asyncio.create_task(
        _run_report_generation(report_id, case_id, user.user_id, report_type, aggressive_mode)
    )

    placeholder["metadata_warnings"] = metadata_validation.get("warnings", [])
    return placeholder


@router.get("/cases/{case_id}/reports/{report_id}/status")
async def get_report_status(case_id: str, report_id: str, request: Request):
    """Poll endpoint for report generation status + pass-level progress."""
    user = await get_current_user(request)
    report = await db.reports.find_one(
        {"report_id": report_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "report_id": 1, "status": 1, "error": 1, "generation_progress": 1, "content.passes_completed": 1}
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    payload = {"report_id": report_id, "status": report.get("status", "completed")}
    if report.get("error"):
        payload["error"] = report["error"]
    progress = report.get("generation_progress") or {}
    if progress and payload["status"] == "generating":
        payload["progress"] = {
            "current_pass": progress.get("current_pass"),
            "total_passes": progress.get("total_passes"),
            "pass_label": progress.get("pass_label"),
            "pass_title": progress.get("pass_title"),
        }
    return payload

@router.get("/cases/{case_id}/reports", response_model=List[dict])
async def get_reports(case_id: str, request: Request):
    """Get all reports for a case"""
    user = await get_current_user(request)
    
    # Auto-fail any report stuck in "generating" for more than 60 minutes
    thirty_min_ago = (datetime.now(timezone.utc) - timedelta(minutes=60)).isoformat()
    await db.reports.update_many(
        {"case_id": case_id, "user_id": user.user_id, "status": "generating", "generated_at": {"$lt": thirty_min_ago}},
        {"$set": {"status": "failed", "error": "Generation timed out"}}
    )
    
    reports = await db.reports.find(
        {
            "case_id": case_id,
            "user_id": user.user_id,
            "content.aggressive_mode": {"$ne": True},
        },
        {"_id": 0}
    ).sort("generated_at", -1).to_list(100)
    
    return reports


@router.get("/cases/{case_id}/reports/barrister-view", response_model=dict)
async def get_or_generate_barrister_view(case_id: str, request: Request, regenerate: bool = False):
    """Return the current barrister brief or start a fresh synthesis when explicitly requested."""
    user = await get_current_user(request)

    # ── Soft metadata validation for Barrister View ──
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if case:
        metadata_val = validate_case_metadata(case)
        log_metadata_warnings(case_id, metadata_val, "barrister_view")

    source_reports = await _get_latest_standard_reports(case_id, user.user_id)
    source_signature = _build_barrister_source_signature(source_reports)

    existing_reports = await db.reports.find(
        {
            "case_id": case_id,
            "user_id": user.user_id,
            "report_type": "barrister_view",
        },
        {"_id": 0},
    ).sort("generated_at", -1).to_list(10)

    # Find current report — prefer one matching current source signature
    current_report = None
    for r in existing_reports:
        if (r.get("content") or {}).get("source_signature") == source_signature:
            current_report = r
            break
    if not current_report and existing_reports:
        current_report = existing_reports[0]

    if current_report and not regenerate:
        current_status = current_report.get("status")
        report_id_cur = current_report.get("report_id")
        if current_status == "completed":
            current_analysis = ((current_report.get("content") or {}).get("analysis") or "").strip()
            if len(current_analysis) < 4000:
                # DO_NOT_UNDO — Backup before auto-regen of thin barrister report
                await db.reports.update_one(
                    {"report_id": report_id_cur},
                    {"$set": {
                        "status": "generating",
                        "error": None,
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "content.backup_analysis": current_analysis,
                    }},
                )
                current_report["status"] = "generating"
                current_report["error"] = None
                asyncio.create_task(_run_barrister_report_generation(report_id_cur, case_id, user.user_id))
                return current_report
            return current_report
        if current_status == "failed":
            # Don't auto-retry — return as-is so user can decide to regenerate
            return current_report
        if current_status == "generating":
            generated_at = _coerce_utc_datetime(current_report.get("generated_at"))
            stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=BARRISTER_GENERATION_TIMEOUT_MINUTES)
            if generated_at and generated_at >= stale_cutoff:
                return current_report

            timeout_message = "Barrister brief generation timed out. Please generate again."
            await db.reports.update_one(
                {"report_id": report_id_cur},
                {"$set": {"status": "failed", "error": timeout_message, "technical_error": timeout_message}},
            )
            current_report["status"] = "failed"
            current_report["error"] = timeout_message
            return current_report

    # If no existing report and not regenerate — return 404 so frontend knows to show "Generate" button
    if not regenerate:
        raise HTTPException(status_code=404, detail="Barrister brief has not been generated yet. Select 'Generate' to create one.")

    # Regenerate requested — create or reuse
    if current_report and current_report.get("status") in ("completed", "failed"):
        report_id_cur = current_report["report_id"]
        await db.reports.update_one(
            {"report_id": report_id_cur},
            {"$set": {"status": "generating", "error": None, "generated_at": datetime.now(timezone.utc).isoformat()}},
        )
        current_report["status"] = "generating"
        current_report["error"] = None
        asyncio.create_task(_run_barrister_report_generation(report_id_cur, case_id, user.user_id))
        return current_report

    report_id = f"rpt_{uuid.uuid4().hex[:12]}"
    placeholder = {
        "report_id": report_id,
        "case_id": case_id,
        "user_id": user.user_id,
        "report_type": "barrister_view",
        "title": "Appellate Research Brief",
        "content": {
            "analysis": "",
            "document_count": len(source_reports),
            "event_count": 0,
            "source_signature": source_signature,
            "source_reports": [
                {
                    "report_id": report.get("report_id"),
                    "report_type": report.get("report_type"),
                    "title": report.get("title"),
                    "generated_at": report.get("generated_at"),
                }
                for report in source_reports
            ],
            "aggressive_mode": False,
        },
        "grounds_of_merit": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "generating",
    }
    await db.reports.insert_one({k: v for k, v in placeholder.items()})

    asyncio.create_task(_run_barrister_report_generation(report_id, case_id, user.user_id))
    return placeholder


async def _get_latest_completed_barrister_report(case_id: str, user_id: str):
    return await db.reports.find_one(
        {
            "case_id": case_id,
            "user_id": user_id,
            "report_type": "barrister_view",
            "status": "completed",
        },
        {"_id": 0},
        sort=[("generated_at", -1)],
    )


@router.get("/cases/{case_id}/reports/barrister-view/export-pdf")
async def export_latest_barrister_view_pdf(case_id: str, request: Request):
    user = await get_current_user(request)
    # Resolve case owner for admin cross-user access
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0, "user_id": 1})
    owner_user_id = (case or {}).get("user_id", user.user_id)
    report = await _get_latest_completed_barrister_report(case_id, owner_user_id)
    if not report:
        raise HTTPException(status_code=404, detail="Completed barrister report not found")
    return await export_report_pdf(case_id, report["report_id"], request)


@router.get("/cases/{case_id}/reports/barrister-view/export-docx")
async def export_latest_barrister_view_docx(case_id: str, request: Request):
    user = await get_current_user(request)
    # Resolve case owner for admin cross-user access
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0, "user_id": 1})
    owner_user_id = (case or {}).get("user_id", user.user_id)
    report = await _get_latest_completed_barrister_report(case_id, owner_user_id)
    if not report:
        raise HTTPException(status_code=404, detail="Completed barrister report not found")
    return await export_report_docx(case_id, report["report_id"], request)


# DO NOT UNDO — Quick Research Brief: 2-page PDF with Counsel Synthesis + Priority Order + top 3 grounds
@router.get("/cases/{case_id}/reports/barrister-quick-brief")
async def export_barrister_quick_brief(case_id: str, request: Request):
    """Generate a concise 2-page Quick Research Brief PDF.
    Contains Counsel Synthesis, Priority Order, and top 3 grounds only.
    Designed for a barrister to review in under 5 minutes before a conference."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from io import BytesIO

    user = await get_current_user(request)

    # Get case
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        if is_admin_user(user.email):
            case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

    # Get barrister report — use case owner's user_id for admin cross-user access
    report_owner_id = case.get("user_id", user.user_id)
    report = await _get_latest_completed_barrister_report(case_id, report_owner_id)
    if not report:
        raise HTTPException(status_code=404, detail="Completed barrister report not found. Generate the Appellate Research Brief first.")

    # Get grounds sorted by priority
    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id}, {"_id": 0}
    ).sort([("priority_order", 1), ("strength", 1)]).to_list(100)

    # Extract Counsel Synthesis from report content
    analysis = report.get("content", {}).get("analysis", "")
    counsel_synthesis = ""
    # Find the Counsel Synthesis section in the markdown
    import re as re_mod
    synth_match = re_mod.search(r"##\s*Counsel Synthesis(.*?)(?=\n##\s[^#]|\Z)", analysis, re_mod.DOTALL)
    if synth_match:
        counsel_synthesis = synth_match.group(1).strip()

    # Build PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=18*mm, bottomMargin=22*mm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='QBTitle', fontSize=18, spaceAfter=6, alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.HexColor('#0f172a')))
    styles.add(ParagraphStyle(name='QBSubtitle', fontSize=10, spaceAfter=10, alignment=TA_CENTER, textColor=colors.HexColor('#475569')))
    styles.add(ParagraphStyle(name='QBSection', fontSize=13, spaceBefore=10, spaceAfter=4, fontName='Helvetica-Bold', textColor=colors.HexColor('#1e3a8a')))
    styles.add(ParagraphStyle(name='QBSubSection', fontSize=11, spaceBefore=6, spaceAfter=3, fontName='Helvetica-Bold', textColor=colors.HexColor('#1e293b')))
    styles.add(ParagraphStyle(name='QBBody', fontSize=10, spaceAfter=4, alignment=TA_JUSTIFY, leading=13))
    styles.add(ParagraphStyle(name='QBPriority', fontSize=10, spaceAfter=3, leftIndent=8, leading=13))
    styles.add(ParagraphStyle(name='QBDisclaimer', fontSize=8, fontName='Helvetica-Oblique', textColor=colors.HexColor('#94a3b8'), alignment=TA_CENTER, leading=10))
    styles.add(ParagraphStyle(name='QBGroundTitle', fontSize=11, spaceBefore=6, spaceAfter=3, fontName='Helvetica-Bold', textColor=colors.HexColor('#1e3a8a')))

    def safe_text(text):
        return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    story = []

    # Header
    defendant = case.get("defendant_name", "Unknown")
    state = (case.get("state") or "UNSPECIFIED").upper()
    sentence = case.get("sentence", "")

    story.append(Paragraph("APPELLATE RESEARCH BRIEF — QUICK BRIEF", styles['QBTitle']))
    story.append(Paragraph(f"Appellant: {safe_text(defendant)} | Jurisdiction: {state}", styles['QBSubtitle']))
    if sentence:
        story.append(Paragraph(f"Sentence: {safe_text(sentence)}", styles['QBSubtitle']))
    story.append(Spacer(1, 3*mm))

    # Thin blue line separator
    line_table = Table([[""]],
        colWidths=[doc.width],
        rowHeights=[1]
    )
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2563eb')),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 4*mm))

    # Counsel Synthesis
    story.append(Paragraph("COUNSEL SYNTHESIS", styles['QBSection']))
    if counsel_synthesis:
        # Enforce 2-page contract: truncate synthesis to ~1200 chars max
        MAX_SYNTHESIS_CHARS = 1200
        truncated_synthesis = counsel_synthesis
        if len(counsel_synthesis) > MAX_SYNTHESIS_CHARS:
            truncated_synthesis = counsel_synthesis[:MAX_SYNTHESIS_CHARS].rsplit(".", 1)[0] + ". [See full Appellate Research Brief for complete synthesis.]"

        # Parse the synthesis into sub-sections
        sections = re_mod.split(r"###\s+", truncated_synthesis)
        for section in sections:
            section = section.strip()
            if not section:
                continue
            lines = section.split("\n", 1)
            heading = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ""

            if heading:
                story.append(Paragraph(safe_text(heading), styles['QBSubSection']))
            if body:
                # Handle numbered lists and paragraphs
                for para in body.split("\n"):
                    para = para.strip()
                    if not para:
                        continue
                    # Numbered items
                    if re_mod.match(r"^\d+\.", para):
                        story.append(Paragraph(safe_text(para), styles['QBPriority']))
                    else:
                        # Convert markdown bold
                        clean = safe_text(para)
                        clean = re_mod.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", clean)
                        story.append(Paragraph(clean, styles['QBBody']))
    else:
        story.append(Paragraph("Counsel Synthesis not available. Generate a new Appellate Research Brief report with the latest prompt to include this section.", styles['QBBody']))

    story.append(Spacer(1, 4*mm))
    story.append(line_table)
    story.append(Spacer(1, 4*mm))

    # Top 3 Grounds
    top_grounds = grounds[:3]
    story.append(Paragraph("TOP 3 GROUNDS OF APPEAL", styles['QBSection']))
    
    VIABILITY_LABELS = {
        "strong": "Arguable \u2014 Strong",
        "moderate": "Arguable \u2014 Moderate",
        "weak": "Requires Development",
    }

    for idx, ground in enumerate(top_grounds, 1):
        title = ground.get("title", "Untitled Ground")
        strength = ground.get("strength", "moderate")
        # Prefer the verified legitimacy_scores.viability_label over raw classifier strength
        viability = (ground.get("legitimacy_scores") or {}).get("viability_label")
        badge_text = viability or f"Unverified strength: {VIABILITY_LABELS.get(strength, strength)}"
        ground_type = ground.get("ground_type", "")
        appellate_pathway = ground.get("appellate_pathway", "")
        description = ground.get("description", "")

        story.append(Paragraph(f"Ground {idx}: {safe_text(title)}", styles['QBGroundTitle']))
        
        # Viability badge — colour keyed to verified label, not raw strength
        viability_colour = {
            "Arguable \u2014 Strong": "#059669",
            "Arguable \u2014 Moderate": "#2563eb",
            "Requires Development": "#dc2626",
        }.get(viability or "", "#64748b")
        story.append(Paragraph(f'<font color="{viability_colour}"><b>{safe_text(badge_text)}</b></font> | Type: {safe_text(ground_type.replace("_", " ").title())}', styles['QBBody']))
        
        if appellate_pathway:
            story.append(Paragraph(f"<b>Appellate Pathway:</b> {safe_text(appellate_pathway)}", styles['QBBody']))

        # Show description (truncated to enforce 2-page contract)
        desc_clean = description.replace("\n\n", " ").replace("\n", " ")
        if len(desc_clean) > 250:
            desc_clean = desc_clean[:250] + "..."
        story.append(Paragraph(safe_text(desc_clean), styles['QBBody']))

        # Contingent warning — prefer legitimacy_scores flag over ground_type alone
        is_contingent = (ground.get("legitimacy_scores") or {}).get("is_contingent", False) or ground_type == "ineffective_counsel"
        if is_contingent:
            story.append(Paragraph('<font color="#d97706"><b>CONTINGENT</b> \u2014 Requires evidentiary support before advancement</font>', styles['QBBody']))

        story.append(Spacer(1, 2*mm))

    if len(grounds) > 3:
        story.append(Paragraph(f"<i>{len(grounds) - 3} additional ground(s) detailed in the full Appellate Research Brief.</i>", styles['QBBody']))

    # Footer disclaimer
    story.append(Spacer(1, 6*mm))
    story.append(line_table)
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "This document is an AI-generated educational analysis tool only. "
        "It does not constitute legal advice. Independent legal counsel must be obtained "
        "before taking any action. Created and designed by Deb King.",
        styles['QBDisclaimer']
    ))
    story.append(Paragraph(
        f"Generated: {datetime.now(timezone.utc).strftime('%d %B %Y at %H:%M UTC')}",
        styles['QBDisclaimer']
    ))

    from services.export_footer import NumberedCanvas, build_footer_label
    qb_footer_label = build_footer_label(case, "Quick Research Brief")
    numbered_canvas = NumberedCanvas(qb_footer_label)
    doc.build(story, canvasmaker=numbered_canvas)
    buffer.seek(0)

    filename = f"Quick_Brief_{defendant.replace(' ', '_')}_{case_id}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/reports/embedded-legacy", response_model=dict)
async def get_embedded_legacy_reports(request: Request, limit: int = 3):
    """Return strongest historical reports for embedding/reference in UI."""
    user = await get_current_user(request)

    all_reports = await db.reports.find(
        {"user_id": user.user_id},
        {
            "_id": 0,
            "report_id": 1,
            "case_id": 1,
            "report_type": 1,
            "title": 1,
            "generated_at": 1,
            "content.analysis": 1,
        },
    ).sort("generated_at", -1).to_list(400)

    def analysis_len(item: dict) -> int:
        return len((item.get("content") or {}).get("analysis", ""))

    valid_types = ["quick_summary", "full_detailed", "extensive_log"]
    by_length = [r for r in all_reports if r.get("report_type") in valid_types and analysis_len(r) > 1200]
    by_length.sort(key=analysis_len, reverse=True)

    selected = []
    seen_types = set()

    for report in by_length:
        rtype = report.get("report_type")
        if rtype in seen_types:
            continue
        seen_types.add(rtype)
        selected.append(report)
        if len(selected) >= limit:
            break

    if len(selected) < limit:
        selected_ids = {r.get("report_id") for r in selected}
        for report in by_length:
            if report.get("report_id") in selected_ids:
                continue
            selected.append(report)
            if len(selected) >= limit:
                break

    embedded = []
    for report in selected[:limit]:
        analysis = (report.get("content") or {}).get("analysis", "")
        embedded.append(
            {
                "report_id": report.get("report_id"),
                "case_id": report.get("case_id"),
                "report_type": report.get("report_type"),
                "title": report.get("title"),
                "generated_at": report.get("generated_at"),
                "analysis": analysis,
                "analysis_length": len(analysis),
            }
        )

    return {"reports": embedded}

@router.get("/cases/{case_id}/reports/{report_id}", response_model=dict)
async def get_report(case_id: str, report_id: str, request: Request):
    """Get a specific report"""
    user = await get_current_user(request)
    
    report = await db.reports.find_one(
        {"report_id": report_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report

@router.delete("/cases/{case_id}/reports/{report_id}")
async def delete_report(case_id: str, report_id: str, request: Request):
    """Delete a report"""
    user = await get_current_user(request)
    
    result = await db.reports.delete_one({
        "report_id": report_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {"message": "Report deleted"}
