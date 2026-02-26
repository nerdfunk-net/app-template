"""
Celery task submission and status endpoints.
"""

from fastapi import APIRouter, Depends
from celery.result import AsyncResult
from core.auth import require_permission
from core.celery_error_handler import handle_celery_errors
from celery_app import celery_app
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/celery", tags=["celery"])


# ── Shared response models (imported by other celery sub-routers) ────────────


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    progress: Optional[dict] = None


# ── Request models ────────────────────────────────────────────────────────────


class TestTaskRequest(BaseModel):
    message: str = "Hello from Celery!"


class ProgressTaskRequest(BaseModel):
    duration: int = 10


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post(
    "/test",
    response_model=TaskResponse,
    dependencies=[Depends(require_permission("jobs", "write"))],
)
@handle_celery_errors("submit test task")
async def submit_test_task(request: TestTaskRequest):
    """Submit a test task to verify Celery is working."""
    from tasks import test_tasks

    task = test_tasks.test_task.delay(message=request.message)

    return TaskResponse(
        task_id=task.id, status="queued", message=f"Test task submitted: {task.id}"
    )


@router.post(
    "/test/progress",
    response_model=TaskResponse,
    dependencies=[Depends(require_permission("jobs", "write"))],
)
@handle_celery_errors("submit progress test task")
async def submit_progress_test_task(request: ProgressTaskRequest):
    """Submit a test task that reports progress."""
    from tasks import test_tasks

    task = test_tasks.test_progress_task.delay(duration=request.duration)

    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Progress test task submitted: {task.id}",
    )


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
@handle_celery_errors("get task status")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(require_permission("jobs.runs", "read")),
):
    """
    Get the status and result of a Celery task.

    Status can be: PENDING, STARTED, PROGRESS, SUCCESS, FAILURE, RETRY, REVOKED
    """
    result = AsyncResult(task_id, app=celery_app)

    response = TaskStatusResponse(task_id=task_id, status=result.state)

    if result.state == "PENDING":
        response.progress = {"status": "Task is queued and waiting to start"}
    elif result.state == "PROGRESS":
        response.progress = result.info
    elif result.state == "SUCCESS":
        response.result = result.result
    elif result.state == "FAILURE":
        response.error = str(result.info)

    return response


@router.delete("/tasks/{task_id}")
@handle_celery_errors("cancel task")
async def cancel_task(
    task_id: str,
    current_user: dict = Depends(require_permission("settings.celery", "write")),
):
    """Cancel a running or queued task."""
    result = AsyncResult(task_id, app=celery_app)
    result.revoke(terminate=True)

    return {"success": True, "message": f"Task {task_id} cancelled"}


@router.post("/tasks/cache-demo", response_model=TaskResponse)
@handle_celery_errors("trigger cache demo task")
async def trigger_cache_demo(
    current_user: dict = Depends(require_permission("settings.cache", "write")),
):
    """
    Trigger a simple cache demo task.
    This is a placeholder showing where your caching logic would go.
    """
    from services.background_jobs import cache_demo_task

    task = cache_demo_task.delay()

    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Cache demo task queued: {task.id}",
    )
