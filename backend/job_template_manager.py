"""
Job Template Manager
Handles business logic for job templates using PostgreSQL and repository pattern.
"""

import logging
from typing import Optional, List, Dict, Any

from repositories.jobs.job_template_repository import JobTemplateRepository

logger = logging.getLogger(__name__)

# Initialize repository
repo = JobTemplateRepository()


def create_job_template(
    name: str,
    job_type: str,
    user_id: int,
    created_by: str,
    description: Optional[str] = None,
    is_global: bool = False,
) -> Dict[str, Any]:
    """Create a new job template"""

    # Check for duplicate name
    if repo.check_name_exists(name, user_id if not is_global else None):
        raise ValueError(f"A job template with name '{name}' already exists")

    template = repo.create(
        name=name,
        job_type=job_type,
        description=description,
        is_global=is_global,
        user_id=user_id if not is_global else None,
        created_by=created_by,
    )

    logger.info("Created job template: %s (ID: %s)", name, template.id)
    return _model_to_dict(template)


def get_job_template(template_id: int) -> Optional[Dict[str, Any]]:
    """Get a job template by ID"""
    template = repo.get_by_id(template_id)
    if template:
        return _model_to_dict(template)
    return None


def get_job_template_by_name(
    name: str, user_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """Get a job template by name"""
    template = repo.get_by_name(name, user_id)
    if template:
        return _model_to_dict(template)
    return None


def list_job_templates(
    user_id: Optional[int] = None, job_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List job templates with optional filters"""
    if user_id is not None:
        templates = repo.get_user_templates(user_id, job_type)
    else:
        templates = repo.get_global_templates(job_type)

    return [_model_to_dict(t) for t in templates]


def get_user_job_templates(
    user_id: int, job_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get all job templates accessible by a user (global + their private templates)"""
    templates = repo.get_user_templates(user_id, job_type)
    return [_model_to_dict(t) for t in templates]


def update_job_template(
    template_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_global: Optional[bool] = None,
    user_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Update a job template"""

    # Check for duplicate name if name is being updated
    if name is not None:
        if repo.check_name_exists(name, user_id, exclude_id=template_id):
            raise ValueError(f"A job template with name '{name}' already exists")

    # Build update kwargs
    update_data = {}

    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if is_global is not None:
        update_data["is_global"] = is_global
        if is_global:
            update_data["user_id"] = None
        elif user_id is not None:
            update_data["user_id"] = user_id

    if not update_data:
        # Nothing to update, return current state
        return get_job_template(template_id)

    template = repo.update(template_id, **update_data)
    if template:
        logger.info("Updated job template: %s (ID: %s)", template.name, template_id)
        return _model_to_dict(template)
    return None


def delete_job_template(template_id: int) -> bool:
    """Delete a job template"""
    template = repo.get_by_id(template_id)
    if template:
        repo.delete(template_id)
        logger.info("Deleted job template: %s (ID: %s)", template.name, template_id)
        return True
    return False


def get_job_types() -> List[Dict[str, str]]:
    """Get available job types with descriptions"""
    return [
        {
            "value": "example",
            "label": "Example",
            "description": "Example job type",
        },
    ]


def _model_to_dict(template) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dictionary"""
    return {
        "id": template.id,
        "name": template.name,
        "job_type": template.job_type,
        "description": template.description,
        "is_global": template.is_global,
        "user_id": template.user_id,
        "created_by": template.created_by,
        "created_at": template.created_at,
        "updated_at": template.updated_at,
    }
