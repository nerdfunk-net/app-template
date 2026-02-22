"""
Job scheduling and management routers.

This package contains routers for:
- Job templates (reusable job configurations)
- Job schedules (scheduled job execution)
- Job runs (execution history and status)
- Celery task submission and status (celery_api)
- Celery infrastructure monitoring (celery_status)
- Celery settings management (celery_settings)
- Celery cleanup operations (celery_cleanup)
"""

from .templates import router as templates_router
from .schedules import router as schedules_router
from .runs import router as runs_router
from .celery_api import router as celery_router
from .celery_status import router as celery_status_router
from .celery_settings import router as celery_settings_router
from .celery_cleanup import router as celery_cleanup_router

__all__ = [
    "templates_router",
    "schedules_router",
    "runs_router",
    "celery_router",
    "celery_status_router",
    "celery_settings_router",
    "celery_cleanup_router",
]
