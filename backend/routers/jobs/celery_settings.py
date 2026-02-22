"""
Celery settings management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import require_permission
from core.celery_error_handler import handle_celery_errors
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/celery", tags=["celery"])


class CeleryQueue(BaseModel):
    """
    Celery queue configuration.

    Fields:
        name: Queue name (e.g., "default", "backup", "network", "heavy")
        description: Human-readable description of queue purpose
        built_in: True for hardcoded queues (cannot be deleted), False for custom queues
    """

    name: str
    description: str = ""
    built_in: bool = False


class CelerySettingsRequest(BaseModel):
    max_workers: Optional[int] = None
    cleanup_enabled: Optional[bool] = None
    cleanup_interval_hours: Optional[int] = None
    cleanup_age_hours: Optional[int] = None
    result_expires_hours: Optional[int] = None
    queues: Optional[List[CeleryQueue]] = None


@router.get("/settings")
@handle_celery_errors("get celery settings")
async def get_celery_settings(
    current_user: dict = Depends(require_permission("settings.celery", "read")),
):
    """
    Get current Celery settings from database.

    Queue System:
    - Built-in queues (built_in=true): Hardcoded in celery_app.py, have automatic task routing
    - Custom queues (built_in=false): Must be configured via CELERY_WORKER_QUEUE env var
    """
    from settings_manager import settings_manager

    celery_settings = settings_manager.get_celery_settings()

    return {"success": True, "settings": celery_settings}


@router.put("/settings")
@handle_celery_errors("update celery settings")
async def update_celery_settings(
    request: CelerySettingsRequest,
    current_user: dict = Depends(require_permission("settings.celery", "write")),
):
    """
    Update Celery settings.

    Built-in queues (default, backup, network, heavy) cannot be removed.
    Workers must be restarted to recognize queue changes.
    Note: max_workers changes require restarting the Celery worker to take effect.
    """
    from settings_manager import settings_manager

    current = settings_manager.get_celery_settings()
    updates = request.model_dump(exclude_unset=True)

    if "queues" in updates:
        built_in_queue_names = {"default", "backup", "network", "heavy"}
        updated_queue_names = {q["name"] for q in updates["queues"]}

        missing_built_ins = built_in_queue_names - updated_queue_names
        if missing_built_ins:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot remove built-in queues: {', '.join(missing_built_ins)}. "
                f"Built-in queues (default, backup, network, heavy) are required.",
            )

        for queue in updates["queues"]:
            if queue["name"] in built_in_queue_names:
                queue["built_in"] = True
            elif "built_in" not in queue:
                queue["built_in"] = False

    merged = {**current, **updates}

    success = settings_manager.update_celery_settings(merged)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update Celery settings",
        )

    updated = settings_manager.get_celery_settings()

    return {
        "success": True,
        "settings": updated,
        "message": "Celery settings updated. Worker restart required for max_workers changes.",
    }
