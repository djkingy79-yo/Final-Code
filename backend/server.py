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

from fastapi import FastAPI, APIRouter, Request, Response, HTTPException
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

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


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


@app.get("/api/health/env")
async def env_health_check(request: Request):
    """Environment variable validation — admin-only diagnostic endpoint.
    Returns status of all required/optional env vars without exposing values."""
    from config import validate_env_status, is_admin_user
    from auth_utils import get_current_user

    try:
        user = await get_current_user(request)
        if not is_admin_user(user.email):
            raise HTTPException(status_code=403, detail="Admin access required")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication required")

    return {
        "env_status": validate_env_status(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


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


# ── API root ──
api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "Criminal Appeal AI API", "status": "operational"}


app.include_router(api_router)

# ── Register all routers ──
register_all_routers(app)


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
