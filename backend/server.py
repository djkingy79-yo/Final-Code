# DO NOT UNDO — server.py. All endpoints in this file are approved and must be preserved.
# ===========================================================================
# Criminal Appeal AI - Main Server (Refactored)
# ===========================================================================
# This file contains:
#   - App factory, CORS, security middleware
#   - Health check endpoints
#   - Router inclusion and startup/shutdown
# Service modules: services/report_quality.py, services/pipeline_orchestrator.py,
#   services/report_generator.py, services/barrister_generator.py
# Route modules: routers/reports.py, routers/report_exports.py
# ===========================================================================

import os
import sys

# Ensure backend/ is on sys.path so relative imports (from config import ...)
# resolve correctly regardless of working directory or Procfile invocation.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, APIRouter, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from config import db, logger, client

from routers.cases import router as cases_router
from routers.auth import router as auth_router
from routers.password_reset import router as password_reset_router
from routers.admin import router as admin_router
from routers.utilities import router as utilities_router
from routers.analytics import router as analytics_router
from routers.statistics import router as statistics_router
from routers.compare import router as compare_router
from routers.contradictions import router as contradictions_router
from routers.export import router as export_router
from routers.export import translate_router
from routers.collaboration import router as collaboration_router
from routers.documents import router as documents_router
from routers.timeline import router as timeline_router
from routers.deadlines import router as deadlines_router
from routers.notes import router as notes_router
from routers.grounds import router as grounds_router
from routers.payments import router as payments_router
from routers.resources import router as resources_router
from routers.analysis import router as analysis_router
from routers.pipeline import router as pipeline_router
from routers.pipeline_staged import router as pipeline_staged_router
from routers.caselaw import router as caselaw_router
from routers.reports import router as reports_router
from routers.report_exports import router as report_exports_router

# ── FastAPI app ──
app = FastAPI(title="Criminal Appeal AI", version="2.0.0")
api_router = APIRouter(prefix="/api")


# ── Security Headers Middleware ──
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers and rate-limits auth endpoints."""
    _auth_attempts: dict = {}  # IP -> [(timestamp, ...)]

    async def dispatch(self, request: Request, call_next):
        # Rate limit auth endpoints: 10 requests per minute per IP
        path = request.url.path
        if request.method == "POST" and any(p in path for p in ["/auth/login", "/auth/register", "/auth/forgot-password"]):
            ip = request.client.host if request.client else "unknown"
            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(minutes=1)
            attempts = self._auth_attempts.get(ip, [])
            attempts = [t for t in attempts if t > cutoff]
            if len(attempts) >= 10:
                return Response(
                    content='{"detail":"Too many attempts. Please wait 1 minute."}',
                    status_code=429,
                    media_type="application/json"
                )
            attempts.append(now)
            self._auth_attempts[ip] = attempts

        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)


@app.get("/health")
@app.get("/api/health")
async def health_check():
    try:
        await db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "healthy", "database": db_status, "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/ready")
async def readiness_check():
    """Readiness probe — returns 503 if MongoDB is not connected."""
    try:
        await db.command("ping")
        return {"ready": True, "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception:
        return Response(
            content='{"ready":false,"reason":"database_unavailable"}',
            status_code=503,
            media_type="application/json"
        )


@app.get("/api/health/deep")
async def deep_health_check():
    """Deep health check — verifies MongoDB, LLM key, and email service."""
    from config import EMERGENT_LLM_KEY
    checks = {}
    # MongoDB
    try:
        await db.command("ping")
        user_count = await db.users.count_documents({})
        checks["mongodb"] = {"status": "ok", "users": user_count}
    except Exception as e:
        checks["mongodb"] = {"status": "error", "detail": str(e)}
    # LLM Key
    checks["llm_key"] = {"status": "ok" if EMERGENT_LLM_KEY else "missing"}
    # Resend
    resend_key = os.environ.get("RESEND_API_KEY", "")
    checks["email"] = {"status": "ok" if resend_key else "not_configured"}
    all_ok = all(c.get("status") == "ok" for c in checks.values())
    return {"healthy": all_ok, "checks": checks, "timestamp": datetime.now(timezone.utc).isoformat()}


# ============ HEALTH CHECK ============

@api_router.get("/")
async def root():
    return {"message": "Criminal Appeal AI API", "status": "operational"}



# ── Include api_router (report/export endpoints defined above) ──
app.include_router(api_router)

# ── Include routers ──
app.include_router(cases_router)
app.include_router(auth_router)
app.include_router(password_reset_router)
app.include_router(admin_router)
app.include_router(utilities_router)
app.include_router(analytics_router)
app.include_router(statistics_router)
app.include_router(compare_router)
app.include_router(contradictions_router)
app.include_router(export_router)
app.include_router(translate_router)
app.include_router(collaboration_router)
app.include_router(documents_router)
app.include_router(timeline_router)
app.include_router(deadlines_router)
app.include_router(notes_router)
app.include_router(grounds_router)
app.include_router(payments_router)
app.include_router(resources_router)
app.include_router(analysis_router)
app.include_router(pipeline_router)
app.include_router(pipeline_staged_router)
app.include_router(caselaw_router)
app.include_router(reports_router)
app.include_router(report_exports_router)

# DO_NOT_UNDO — CORS Middleware. Uses CORS_ORIGINS env var for allowed origins.
# Must include ALL domains the frontend is served from (preview, production, custom domain).
_cors_origins_raw = os.environ.get("CORS_ORIGINS", "")
_frontend_url = os.environ.get("FRONTEND_URL", "").replace("/api", "")
_all_origins = set()
if _cors_origins_raw.strip() == "*":
    _all_origins = {"*"}
else:
    for src in [_cors_origins_raw, _frontend_url]:
        for o in src.split(","):
            o = o.strip().strip('"').strip("'")
            if o:
                _all_origins.add(o)
if not _all_origins:
    logger.warning("CORS: No origins configured — set CORS_ORIGINS or FRONTEND_URL in .env")
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True if "*" not in _all_origins else False,
    allow_origins=list(_all_origins),
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.on_event("startup")
async def cleanup_orphaned_reports():
    """Auto-fail or recover reports stuck in 'generating' from server restarts.
    
    DO_NOT_UNDO — Recovery uses minimum character targets to decide whether a partial
    report is complete enough to mark as finished, or needs re-generation.
    """
    # ─── Database Initialisation ────────────────────────────────────────
    # Create indexes for ALL collections used by the app.
    # MongoDB creates collections automatically on first write, but indexes
    # must be ensured at startup to guarantee query performance in deployment.
    
    # Core collections
    await db.users.create_index([("user_id", 1)], unique=True)
    await db.users.create_index([("email", 1)], unique=True)
    await db.cases.create_index([("case_id", 1)], unique=True)
    await db.cases.create_index([("user_id", 1)])
    await db.reports.create_index([("report_id", 1)], unique=True)
    await db.reports.create_index([("case_id", 1), ("user_id", 1)])
    await db.reports.create_index([("case_id", 1), ("report_type", 1)])
    await db.documents.create_index([("document_id", 1)], unique=True)
    await db.documents.create_index([("case_id", 1), ("user_id", 1)])
    
    # Grounds and analysis
    await db.grounds_of_merit.create_index([("ground_id", 1)], unique=True)
    await db.grounds_of_merit.create_index([("case_id", 1), ("user_id", 1)])
    await db.grounds_of_merit.create_index([("case_id", 1), ("priority_order", 1)])
    await db.issue_arguments.create_index([("case_id", 1)])
    
    # Pipeline collections
    await db.document_extracts.create_index([("case_id", 1), ("user_id", 1)])
    await db.document_extracts.create_index([("extract_id", 1)], unique=True)
    await db.document_extracts.create_index([("document_id", 1), ("case_id", 1)])
    await db.case_extracts.create_index([("case_id", 1), ("user_id", 1)])
    await db.case_extracts.create_index([("case_extract_id", 1)], unique=True)
    await db.issue_classifications.create_index([("case_id", 1), ("user_id", 1)])
    await db.issue_classifications.create_index([("issue_id", 1)], unique=True)
    await db.issue_verifications.create_index([("issue_id", 1), ("case_id", 1)])
    await db.issue_verifications.create_index([("verification_id", 1)], unique=True)
    await db.pipeline_tasks.create_index([("case_id", 1), ("user_id", 1), ("task_type", 1)])
    await db.pipeline_tasks.create_index([("task_id", 1)], unique=True)
    
    # Auth and sessions
    await db.user_sessions.create_index([("session_token", 1)], unique=True)
    await db.user_sessions.create_index([("user_id", 1)])
    await db.user_sessions.create_index([("expires_at", 1)], expireAfterSeconds=0)
    await db.password_reset_tokens.create_index([("token", 1)], unique=True)
    await db.password_reset_tokens.create_index([("expires_at", 1)], expireAfterSeconds=0)
    
    # Case features
    await db.notes.create_index([("case_id", 1), ("user_id", 1)])
    await db.timeline_events.create_index([("case_id", 1)])
    await db.deadlines.create_index([("case_id", 1), ("user_id", 1)])
    await db.checklist_items.create_index([("case_id", 1), ("user_id", 1)])
    await db.submissions_drafts.create_index([("case_id", 1), ("user_id", 1)])
    await db.activities.create_index([("case_id", 1)])
    await db.contradiction_scans.create_index([("case_id", 1)])
    
    # Payments
    await db.payments.create_index([("user_id", 1)])
    await db.payments.create_index([("case_id", 1)])
    await db.payments.create_index([("payment_id", 1)], unique=True)
    
    # Sharing
    await db.case_shares.create_index([("case_id", 1)])
    await db.share_links.create_index([("link_id", 1)], unique=True)
    
    # Analytics
    await db.visits.create_index([("timestamp", 1)])
    await db.visit_stats.create_index([("date", 1)])
    await db.contact_messages.create_index([("created_at", 1)])
    
    # Notifications
    await db.notifications.create_index([("user_id", 1), ("read", 1)])
    await db.case_messages.create_index([("case_id", 1)])
    
    # Counters
    await db.counters.create_index([("name", 1)], unique=True)

    # Minimum character targets — reports below these are incomplete
    min_recovery_targets = {
        "quick_summary": 10000,
        "full_detailed": 70000,
        "extensive_log": 120000,
    }

    five_min_ago = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    async for report in db.reports.find({"status": "generating", "generated_at": {"$lt": five_min_ago}}):
        partial = report.get("content", {}).get("analysis", "") or report.get("content", {}).get("partial_analysis", "")
        report_type = report.get("report_type", "quick_summary")
        min_target = min_recovery_targets.get(report_type, 10000)
        
        if partial and len(partial) > 5000:
            if len(partial) >= min_target:
                # Full recovery — report meets minimum target
                await db.reports.update_one(
                    {"report_id": report["report_id"]},
                    {"$set": {"status": "completed", "content.analysis": partial, "content.partial": False}}
                )
                logger.info(f"Recovered complete report {report['report_id']} ({len(partial)} chars)")
            else:
                # Partial recovery — save content but mark as failed so user can regenerate (resume)
                await db.reports.update_one(
                    {"report_id": report["report_id"]},
                    {"$set": {
                        "status": "failed",
                        "error": f"Generation interrupted after {report.get('content', {}).get('passes_completed', '?')}/8 passes ({len(partial)} chars). Click Generate to resume from where it stopped.",
                        "content.analysis": partial,
                        "content.partial": True,
                        "content.partial_analysis": partial,
                    }}
                )
                logger.info(f"Partial report {report['report_id']} below target ({len(partial)} < {min_target}), marked as failed for resume")
        else:
            # DO_NOT_UNDO — Restore from backup if available. When a user regenerates
            # a completed report and the generation fails, restore the old content
            # so they never lose their existing report.
            backup = report.get("content", {}).get("backup_analysis", "")
            if backup and len(backup) > 5000:
                await db.reports.update_one(
                    {"report_id": report["report_id"]},
                    {"$set": {
                        "status": "completed",
                        "error": None,
                        "content.analysis": backup,
                        "content.partial": False,
                    },
                    "$unset": {"content.backup_analysis": 1}}
                )
                logger.info(f"Restored report {report['report_id']} from backup ({len(backup)} chars)")
            else:
                await db.reports.update_one(
                    {"report_id": report["report_id"]},
                    {"$set": {"status": "failed", "error": "Generation interrupted by server restart. Please try again."}}
                )
                logger.info(f"Failed orphaned report {report['report_id']}")

    # ── FLAG EXISTING UNDERSIZED "COMPLETED" REPORTS (non-destructive) ──
    # Add a flag to undersized reports so the UI can show a "Regenerate for full depth" option.
    # DO NOT change status from "completed" — the user must still be able to VIEW their existing reports.
    min_completed_targets = {
        "full_detailed": 70000,
        "extensive_log": 120000,
    }
    flagged_count = 0
    for rtype, min_chars in min_completed_targets.items():
        async for report in db.reports.find({"status": "completed", "report_type": rtype}):
            analysis = (report.get("content", {}).get("analysis") or "")
            if len(analysis) < min_chars:
                await db.reports.update_one(
                    {"report_id": report["report_id"]},
                    {"$set": {"content.below_target": True, "content.actual_chars": len(analysis), "content.target_chars": min_chars}}
                )
                flagged_count += 1
    if flagged_count:
        logger.info(f"Flagged {flagged_count} undersized reports on startup")

    # Also restore any reports that were accidentally set to "failed" by a previous migration
    # DO_NOT_UNDO — Only restore if the report actually meets the minimum target.
    # Reports below the target MUST stay failed so the user can regenerate them.
    for rtype, min_chars in min_completed_targets.items():
        async for report in db.reports.find({"status": "failed", "report_type": rtype}):
            analysis = (report.get("content", {}).get("analysis") or report.get("content", {}).get("partial_analysis") or "")
            if analysis and len(analysis) >= min_chars:
                await db.reports.update_one(
                    {"report_id": report["report_id"]},
                    {"$set": {
                        "status": "completed",
                        "content.analysis": analysis,
                        "content.partial": False,
                        "content.below_target": False,
                        "content.actual_chars": len(analysis),
                        "content.target_chars": min_chars,
                        "error": None,
                    }}
                )
                logger.info(f"Restored report {report['report_id']} to completed ({len(analysis)} chars >= {min_chars} target)")


@app.on_event("startup")
async def startup_dedup_grounds():
    """DO_NOT_UNDO — Auto-cleanup duplicate grounds on every server start.
    
    Runs the fuzzy deduplication cleanup across ALL cases to merge any duplicates
    that slipped through before the dedup logic was fully applied.
    This prevents the recurring 'grounds multiplying' bug from ever persisting.
    """
    from services.ground_dedup import cleanup_duplicate_grounds, cleanup_duplicate_issues

    try:
        # Get all unique (case_id, user_id) pairs that have grounds
        pipeline = [
            {"$group": {"_id": {"case_id": "$case_id", "user_id": "$user_id"}}},
        ]
        case_pairs = await db.grounds_of_merit.aggregate(pipeline).to_list(500)

        total_removed = 0
        for pair in case_pairs:
            cid = pair["_id"]["case_id"]
            uid = pair["_id"]["user_id"]

            # Cleanup grounds
            result = await cleanup_duplicate_grounds(db, cid, uid)
            if result["removed"] > 0:
                total_removed += result["removed"]

            # Also cleanup issue_classifications
            await cleanup_duplicate_issues(db, cid, uid)

        if total_removed > 0:
            logger.info(f"Startup dedup: removed {total_removed} duplicate grounds across {len(case_pairs)} cases")
        else:
            logger.info(f"Startup dedup: no duplicates found across {len(case_pairs)} cases")
    except Exception as e:
        logger.error(f"Startup dedup failed (non-fatal): {e}")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


# ── Serve frontend static files (Docker single-container deploy) ──
# Must be AFTER all API routers so /api/* routes take priority
import pathlib as _pathlib  # noqa: E402
_static_dir = _pathlib.Path(__file__).parent / "static"
if _static_dir.is_dir():
    from starlette.staticfiles import StaticFiles as _StaticFiles
    app.mount("/", _StaticFiles(directory=str(_static_dir), html=True), name="static")
