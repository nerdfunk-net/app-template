"""
Celery infrastructure monitoring endpoints: workers, queues, schedules, status, config.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from kombu import Queue
from core.auth import require_permission
from core.celery_error_handler import handle_celery_errors
from celery_app import celery_app
import logging
import redis

from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/celery", tags=["celery"])


@router.get("/workers")
@handle_celery_errors("list workers")
async def list_workers(
    current_user: dict = Depends(require_permission("settings.celery", "read")),
):
    """
    List active Celery workers and their status, including queue assignments.
    """
    inspect = celery_app.control.inspect()
    active = inspect.active()
    stats = inspect.stats()
    registered = inspect.registered()
    active_queues = inspect.active_queues()

    return {
        "success": True,
        "workers": {
            "active_tasks": active or {},
            "stats": stats or {},
            "registered_tasks": registered or {},
            "active_queues": active_queues or {},
        },
    }


@router.get("/queues")
@handle_celery_errors("list queues")
async def list_queues(
    current_user: dict = Depends(require_permission("settings.celery", "read")),
):
    """
    List all Celery queues with their metrics and worker assignments.
    """
    inspect = celery_app.control.inspect()
    active_queues = inspect.active_queues()
    active_tasks = inspect.active()

    task_queues = celery_app.conf.task_queues or {}
    task_routes = celery_app.conf.task_routes or {}

    try:
        redis_client = redis.Redis.from_url(settings.redis_url)

        queues = []
        for queue_name in task_queues.keys():
            pending_count = redis_client.llen(queue_name)

            active_count = 0
            workers_consuming = []

            if active_queues:
                for worker_name, worker_queues in active_queues.items():
                    for queue_info in worker_queues:
                        if queue_info.get("name") == queue_name:
                            workers_consuming.append(worker_name)

            if active_tasks:
                for worker_name, tasks in active_tasks.items():
                    if worker_name in workers_consuming:
                        active_count += len(tasks)

            routed_tasks = []
            for task_pattern, route_config in task_routes.items():
                if route_config.get("queue") == queue_name:
                    routed_tasks.append(task_pattern)

            queues.append(
                {
                    "name": queue_name,
                    "pending_tasks": pending_count,
                    "active_tasks": active_count,
                    "workers_consuming": workers_consuming,
                    "worker_count": len(workers_consuming),
                    "routed_tasks": routed_tasks,
                    "exchange": task_queues[queue_name].get("exchange"),
                    "routing_key": task_queues[queue_name].get("routing_key"),
                }
            )

        redis_client.close()

        return {
            "success": True,
            "queues": queues,
            "total_queues": len(queues),
        }

    except Exception as e:
        logger.error("Error fetching queue metrics: %s", e)
        return {
            "success": False,
            "error": str(e),
            "queues": [],
            "total_queues": 0,
        }


@router.delete("/queues/{queue_name}/purge")
@handle_celery_errors("purge queue")
async def purge_queue(
    queue_name: str,
    current_user: dict = Depends(require_permission("settings.celery", "write")),
):
    """
    Purge all pending tasks from a specific queue.
    """
    try:
        task_queues = celery_app.conf.task_queues or {}
        if queue_name not in task_queues.keys():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Queue '{queue_name}' not found",
            )

        with celery_app.connection_or_acquire() as conn:
            queue_config = task_queues[queue_name]
            queue_obj = Queue(
                name=queue_name,
                exchange=queue_config.get("exchange", queue_name),
                routing_key=queue_config.get("routing_key", queue_name),
            )
            purged_count = queue_obj(conn.channel()).purge()

        logger.info(
            "Purged %s task(s) from queue '%s' by user %s", purged_count, queue_name, current_user.get('username')
        )

        return {
            "success": True,
            "queue": queue_name,
            "purged_tasks": purged_count or 0,
            "message": f"Purged {purged_count or 0} pending task(s) from queue '{queue_name}'",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error purging queue %s: %s", queue_name, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to purge queue: {str(e)}",
        )


@router.delete("/queues/purge-all")
@handle_celery_errors("purge all queues")
async def purge_all_queues(
    current_user: dict = Depends(require_permission("settings.celery", "write")),
):
    """
    Purge all pending tasks from all queues.
    """
    try:
        task_queues = celery_app.conf.task_queues or {}

        purged_queues = []
        total_purged = 0

        with celery_app.connection_or_acquire() as conn:
            for queue_name in task_queues.keys():
                try:
                    queue_config = task_queues[queue_name]
                    queue_obj = Queue(
                        name=queue_name,
                        exchange=queue_config.get("exchange", queue_name),
                        routing_key=queue_config.get("routing_key", queue_name),
                    )
                    purged_count = queue_obj(conn.channel()).purge()

                    purged_queues.append(
                        {"queue": queue_name, "purged_tasks": purged_count or 0}
                    )
                    total_purged += purged_count or 0

                    logger.info(
                        "Purged %s task(s) from queue '%s'", purged_count, queue_name
                    )
                except Exception as e:
                    logger.error("Error purging queue %s: %s", queue_name, e)
                    purged_queues.append(
                        {"queue": queue_name, "purged_tasks": 0, "error": str(e)}
                    )

        logger.info(
            "Purged total of %s task(s) from all queues by user %s", total_purged, current_user.get('username')
        )

        return {
            "success": True,
            "total_purged": total_purged,
            "queues": purged_queues,
            "message": f"Purged {total_purged} pending task(s) from {len(purged_queues)} queue(s)",
        }

    except Exception as e:
        logger.error("Error purging all queues: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to purge all queues: {str(e)}",
        )


@router.get("/schedules")
@handle_celery_errors("list schedules")
async def list_schedules(
    current_user: dict = Depends(require_permission("settings.celery", "read")),
):
    """
    List all periodic task schedules configured in Celery Beat.
    """
    beat_schedule = celery_app.conf.beat_schedule or {}

    schedules = []
    for name, config in beat_schedule.items():
        schedules.append(
            {
                "name": name,
                "task": config.get("task"),
                "schedule": str(config.get("schedule")),
                "options": config.get("options", {}),
            }
        )

    return {"success": True, "schedules": schedules}


@router.get("/beat/status")
@handle_celery_errors("get beat status")
async def beat_status(
    current_user: dict = Depends(require_permission("settings.celery", "read")),
):
    """
    Get Celery Beat scheduler status.
    """
    r = redis.from_url(settings.redis_url)

    beat_lock_key = "cockpit-ng:beat::lock"
    lock_exists = r.exists(beat_lock_key)

    beat_schedule_key = "cockpit-ng:beat::schedule"
    schedule_exists = r.exists(beat_schedule_key)

    beat_running = bool(lock_exists or schedule_exists)

    return {
        "success": True,
        "beat_running": beat_running,
        "message": "Beat is running" if beat_running else "Beat not detected",
    }


@router.get("/status")
@handle_celery_errors("get celery status")
async def celery_status(
    current_user: dict = Depends(require_permission("settings.celery", "read")),
):
    """
    Get overall Celery system status.
    """
    inspect = celery_app.control.inspect()
    stats = inspect.stats()
    active = inspect.active()

    worker_count = len(stats) if stats else 0

    task_count = 0
    if active:
        for worker_tasks in active.values():
            task_count += len(worker_tasks)

    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        redis_connected = True
    except Exception:
        redis_connected = False

    try:
        r = redis.from_url(settings.redis_url)
        beat_lock_key = "cockpit-ng:beat::lock"
        beat_running = bool(r.exists(beat_lock_key))
    except Exception:
        beat_running = False

    return {
        "success": True,
        "status": {
            "redis_connected": redis_connected,
            "worker_count": worker_count,
            "active_tasks": task_count,
            "beat_running": beat_running,
        },
    }


@router.get("/config")
@handle_celery_errors("get celery config")
async def get_celery_config(
    current_user: dict = Depends(require_permission("settings.celery", "read")),
):
    """
    Get current Celery configuration (read-only).
    Configuration is set via environment variables and cannot be changed at runtime.
    """
    import os

    redis_host = os.getenv("COCKPIT_REDIS_HOST", "localhost")
    redis_port = os.getenv("COCKPIT_REDIS_PORT", "6379")
    redis_password = os.getenv("COCKPIT_REDIS_PASSWORD", "")
    has_password = bool(redis_password)

    conf = celery_app.conf

    return {
        "success": True,
        "config": {
            "redis": {
                "host": redis_host,
                "port": redis_port,
                "has_password": has_password,
                "database": "0",
            },
            "worker": {
                "max_concurrency": settings.celery_max_workers,
                "prefetch_multiplier": conf.worker_prefetch_multiplier,
                "max_tasks_per_child": conf.worker_max_tasks_per_child,
            },
            "task": {
                "time_limit": conf.task_time_limit,
                "serializer": conf.task_serializer,
                "track_started": conf.task_track_started,
            },
            "result": {
                "expires": conf.result_expires,
                "serializer": conf.result_serializer,
            },
            "beat": {
                "scheduler": conf.beat_scheduler,
                "schedule_count": len(conf.beat_schedule) if conf.beat_schedule else 0,
            },
            "timezone": conf.timezone,
            "enable_utc": conf.enable_utc,
        },
    }
