"""
Criminal Appeal AI - Router Package
All API route handlers extracted from the server.py monolith.
"""

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
from routers.collaboration import router as collaboration_router
from routers.documents import router as documents_router
from routers.timeline import router as timeline_router
from routers.deadlines import router as deadlines_router
from routers.notes import router as notes_router
from routers.grounds import router as grounds_router
from routers.payments import router as payments_router
from routers.resources import router as resources_router
from routers.analysis import router as analysis_router

__all__ = [
    'cases_router', 'auth_router', 'password_reset_router',
    'admin_router', 'utilities_router', 'analytics_router',
    'statistics_router', 'compare_router', 'contradictions_router',
    'export_router', 'collaboration_router', 'documents_router',
    'timeline_router', 'deadlines_router', 'notes_router',
    'grounds_router', 'payments_router', 'resources_router',
    'analysis_router',
]
