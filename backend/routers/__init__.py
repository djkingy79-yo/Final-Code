"""
DO NOT UNDO — Criminal Appeal AI - Routers Package. All features in this file are approved and must be preserved.
"""
from routers.auth import router as auth_router
from routers.cases import router as cases_router
from routers.documents import router as documents_router
from routers.timeline import router as timeline_router
from routers.notes import router as notes_router
from routers.deadlines import router as deadlines_router
from routers.resources import router as resources_router
from routers.statistics import router as statistics_router

__all__ = [
    'auth_router',
    'cases_router', 
    'documents_router',
    'timeline_router',
    'notes_router',
    'deadlines_router',
    'resources_router',
    'statistics_router'
]
