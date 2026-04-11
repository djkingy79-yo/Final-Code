# DO NOT UNDO — server.py. All endpoints in this file are approved and must be preserved.
# ===========================================================================
# Criminal Appeal AI - Main Server
# ===========================================================================
# Thin app factory: middleware, health checks, router registration, startup/shutdown.
# Business logic lives in routers/ and services/.
# ===========================================================================

import os
import sys

# Ensure backend/ is on sys.path so relative imports (from config import ...)
# resolve correctly regardless of working directory or Procfile invocation.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone

from fastapi import FastAPI, APIRouter, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import db, logger, limiter
from routers import register_all_routers


# ── FastAPI app ──
app = FastAPI(title="Criminal Appeal AI", version="2.0.0")

# ── Rate Limiter ──
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Security Headers Middleware ──
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
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


# ── Health Checks ──
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
    try:
        await db.command("ping")
        user_count = await db.users.count_documents({})
        checks["mongodb"] = {"status": "ok", "users": user_count}
    except Exception as e:
        checks["mongodb"] = {"status": "error", "detail": str(e)}
    checks["llm_key"] = {"status": "ok" if EMERGENT_LLM_KEY else "missing"}
    resend_key = os.environ.get("RESEND_API_KEY", "")
    checks["email"] = {"status": "ok" if resend_key else "not_configured"}
    all_ok = all(c.get("status") == "ok" for c in checks.values())
    return {"healthy": all_ok, "checks": checks, "timestamp": datetime.now(timezone.utc).isoformat()}


# ── API root + Stripe webhook proxy ──
api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "Criminal Appeal AI API", "status": "operational"}


@api_router.post("/webhook/stripe")
async def stripe_webhook_proxy(request: Request):
    """Top-level Stripe webhook endpoint."""
    from routers.stripe_payments import stripe_webhook_handler
    return await stripe_webhook_handler(request)


app.include_router(api_router)

# ── Register all routers ──
register_all_routers(app)

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


# ── Startup / Shutdown ──
@app.on_event("startup")
async def on_startup():
    from services.startup_tasks import (
        create_database_indexes,
        recover_orphaned_reports,
        flag_undersized_reports,
        dedup_grounds_on_startup,
    )
    await create_database_indexes()
    await recover_orphaned_reports()
    await flag_undersized_reports()
    await dedup_grounds_on_startup()


@app.on_event("shutdown")
async def on_shutdown():
    from services.startup_tasks import shutdown_db
    shutdown_db()


# ── Serve frontend static files (Docker single-container deploy) ──
# Must be AFTER all API routers so /api/* routes take priority
import pathlib as _pathlib  # noqa: E402
_static_dir = _pathlib.Path(__file__).parent / "static"
if _static_dir.is_dir():
    from starlette.staticfiles import StaticFiles as _StaticFiles
    app.mount("/", _StaticFiles(directory=str(_static_dir), html=True), name="static")
