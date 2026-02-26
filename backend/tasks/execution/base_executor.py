"""
Base executor and job type dispatcher.
Routes job execution to the appropriate executor based on job type.
"""

import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def execute_job_type(
    job_type: str,
    schedule_id: Optional[int],
    credential_id: Optional[int],
    job_parameters: Optional[dict],
    target_devices: Optional[list],
    task_context,
    template: Optional[dict] = None,
    job_run_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Execute the appropriate job based on job type.

    Routes the job execution to the correct executor function.

    Args:
        job_type: Type of job to execute
        schedule_id: ID of schedule if triggered by schedule
        credential_id: ID of credential for authentication
        job_parameters: Additional job parameters
        target_devices: List of target device UUIDs
        task_context: Celery task context (self)
        template: Job template configuration
        job_run_id: Job run ID for result tracking

    Returns:
        dict: Execution results
    """
    job_executors = {
        "example": execute_example,
    }

    executor = job_executors.get(job_type)
    if not executor:
        return {"success": False, "error": f"Unknown job type: {job_type}"}

    return executor(
        schedule_id=schedule_id,
        credential_id=credential_id,
        job_parameters=job_parameters,
        target_devices=target_devices,
        task_context=task_context,
        template=template,
        job_run_id=job_run_id,
    )


def execute_example(
    schedule_id: Optional[int] = None,
    credential_id: Optional[int] = None,
    job_parameters: Optional[dict] = None,
    target_devices: Optional[list] = None,
    task_context=None,
    template: Optional[dict] = None,
    job_run_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Example job executor - demonstrates how to implement a job type.

    This is a template for creating real job executors. Replace this
    with actual business logic as needed.

    Args:
        schedule_id: ID of the triggering schedule
        credential_id: ID of credential (unused in example)
        job_parameters: Additional parameters from the schedule
        target_devices: List of target device identifiers
        task_context: Celery task context for progress updates
        template: Job template configuration
        job_run_id: Job run ID for tracking

    Returns:
        dict: Execution results with success status
    """
    logger.info("Running example job (schedule_id=%s, job_run_id=%s)", schedule_id, job_run_id)

    # Simulate some work
    time.sleep(2)

    return {
        "success": True,
        "message": "Example job completed successfully",
        "schedule_id": schedule_id,
        "job_run_id": job_run_id,
        "job_parameters": job_parameters or {},
        "target_devices": target_devices or [],
    }
