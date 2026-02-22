"""
Celery cleanup endpoints: manual cleanup trigger and stats.
"""

from fastapi import APIRouter, Depends
from core.auth import require_permission
from core.celery_error_handler import handle_celery_errors
from routers.jobs.celery_api import TaskResponse
import logging
import redis

from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/celery", tags=["celery"])


@router.post("/cleanup", response_model=TaskResponse)
@handle_celery_errors("trigger cleanup task")
async def trigger_cleanup(
    current_user: dict = Depends(require_permission("settings.celery", "write")),
):
    """
    Manually trigger the Celery cleanup task.

    This removes old task results and logs based on the configured cleanup_age_hours.
    """
    from tasks.periodic_tasks import cleanup_celery_data_task

    task = cleanup_celery_data_task.delay()

    return TaskResponse(
        task_id=task.id, status="queued", message=f"Cleanup task triggered: {task.id}"
    )


@router.get("/cleanup/stats")
@handle_celery_errors("get cleanup stats")
async def get_cleanup_stats(
    current_user: dict = Depends(require_permission("settings.celery", "read")),
):
    """
    Get statistics about data that would be cleaned up.
    """
    from settings_manager import settings_manager
    from datetime import datetime, timezone, timedelta

    celery_settings = settings_manager.get_celery_settings()
    cleanup_age_hours = celery_settings.get("cleanup_age_hours", 24)
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=cleanup_age_hours)

    r = redis.from_url(settings.redis_url)

    result_keys = list(r.scan_iter("celery-task-meta-*"))

    return {
        "success": True,
        "stats": {
            "cleanup_age_hours": cleanup_age_hours,
            "cutoff_time": cutoff_time.isoformat(),
            "total_result_keys": len(result_keys),
            "message": f"Cleanup will remove task results older than {cleanup_age_hours} hours",
        },
    }
