# DO NOT UNDO — Router registry. All routers must be registered here.
"""
Centralised router registration for the Criminal Appeal AI application.
All route modules are imported and registered via register_all_routers(app).
"""

from .cases import router as cases_router
from .auth import router as auth_router
from .password_reset import router as password_reset_router
from .admin import router as admin_router
from .utilities import router as utilities_router
from .analytics import router as analytics_router
from .statistics import router as statistics_router
from .compare import router as compare_router
from .contradictions import router as contradictions_router
from .export import router as export_router
from .translate import translate_router
from .collaboration import router as collaboration_router
from .documents import router as documents_router
from .timeline import router as timeline_router
from .deadlines import router as deadlines_router
from .notes import router as notes_router
from .grounds import router as grounds_router
from .payments import router as payments_router
from .resources import router as resources_router
from .analysis import router as analysis_router
from .legislation import router as legislation_router
from .pipeline import router as pipeline_router
from .pipeline_staged import router as pipeline_staged_router
from .caselaw import router as caselaw_router
from .reports import router as reports_router
from .report_exports import router as report_exports_router
from .payment_history import router as payment_history_router
from .barrister_pack import router as barrister_pack_router


_ALL_ROUTERS = [
    cases_router,
    auth_router,
    password_reset_router,
    admin_router,
    utilities_router,
    analytics_router,
    statistics_router,
    compare_router,
    contradictions_router,
    export_router,
    translate_router,
    collaboration_router,
    documents_router,
    timeline_router,
    deadlines_router,
    notes_router,
    grounds_router,
    payments_router,
    resources_router,
    analysis_router,
    pipeline_router,
    pipeline_staged_router,
    caselaw_router,
    reports_router,
    report_exports_router,
    legislation_router,
    payment_history_router,
    barrister_pack_router,
]


def register_all_routers(app):
    """Register all API routers with the FastAPI app instance."""
    for router in _ALL_ROUTERS:
        app.include_router(router)
