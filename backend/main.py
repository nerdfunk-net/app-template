"""
Main FastAPI application for Cockpit network device management dashboard.

This is the refactored main application file that uses modular routers
for better code organization and maintainability.
"""

from __future__ import annotations
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from core.limiter import limiter
import asyncio

# Import routers
# Auth routers
from routers.auth import auth_router, oidc_router, profile_router

# Settings routers
from routers.settings import (
    git_router,
    common_router as settings_router,
    cache_router,
    credentials_router,
    templates_router,
    rbac_router,
)

# Job routers
from routers.jobs import (
    templates_router as job_templates_router,
    schedules_router as job_schedules_router,
    runs_router as job_runs_router,
    celery_router,
    celery_status_router,
    celery_settings_router,
    celery_cleanup_router,
)

# Health router
from health import router as health_router

# Import auth dependency

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup then shutdown."""
    # ── Startup ──────────────────────────────────────────────────────────────
    logger.info("=== Application startup - initializing services ===")

    # Initialize database tables first
    try:
        from core.database import init_db

        init_db()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database tables: %s", e)
        raise

    # Ensure built-in Celery queues exist
    try:
        from settings_manager import settings_manager

        settings_manager.ensure_builtin_queues()
        logger.info("Built-in Celery queues verified")
    except Exception as e:
        logger.error("Failed to ensure built-in queues: %s", e)

    # Export SSH keys to filesystem
    try:
        import credentials_manager

        exported_keys = credentials_manager.export_ssh_keys_to_filesystem()
        if exported_keys:
            logger.info("Exported %s SSH keys to ./data/ssh_keys/", len(exported_keys))
        else:
            logger.debug("No SSH keys to export")
    except Exception as e:
        logger.error("Failed to export SSH keys: %s", e)

    # Ensure admin user has RBAC role assigned
    try:
        import user_db_manager

        user_db_manager.ensure_admin_has_rbac_role()
        logger.info("Admin RBAC role assignment completed")
    except Exception as e:
        logger.error("Failed to ensure admin RBAC role: %s", e)

    # Initialize next_run for job schedules that don't have one
    try:
        import jobs_manager

        result = jobs_manager.initialize_schedule_next_runs()
        if result["initialized_count"] > 0:
            logger.info(
                "Initialized next_run for %s job schedules", result['initialized_count']
            )
    except Exception as e:
        logger.error("Failed to initialize job schedule next_runs: %s", e)

    # Initialize cache prefetch
    try:
        logger.debug("Startup cache: hook invoked")
        from settings_manager import settings_manager
        from services.settings.git.shared_utils import get_git_repo_by_id
        from services.settings.cache import cache_service

        cache_cfg = settings_manager.get_cache_settings()
        logger.debug("Startup cache: settings loaded: %s", cache_cfg)
        if cache_cfg.get("enabled", True):

            async def prefetch_commits_once():
                try:
                    logger.debug("Startup cache: prefetch_commits_once() starting")
                    selected_id = settings_manager.get_selected_git_repository()
                    if not selected_id:
                        logger.warning(
                            "Startup cache: No repository selected; skipping commits prefetch"
                        )
                        return

                    repo = get_git_repo_by_id(selected_id)
                    try:
                        branch_name = repo.active_branch.name
                    except Exception:
                        logger.warning(
                            "Startup cache: No active branch detected; skipping commits prefetch"
                        )
                        return

                    try:
                        if not repo.head.is_valid():
                            logger.debug(
                                "Startup cache: Repository has no commits yet; nothing to prefetch"
                            )
                            return
                    except Exception:
                        logger.debug(
                            "Startup cache: Unable to validate HEAD; skipping prefetch"
                        )
                        return

                    limit = int(cache_cfg.get("max_commits", 500))
                    commits = []
                    for commit in repo.iter_commits(branch_name, max_count=limit):
                        commits.append(
                            {
                                "hash": commit.hexsha,
                                "short_hash": commit.hexsha[:8],
                                "message": commit.message.strip(),
                                "author": {
                                    "name": commit.author.name,
                                    "email": commit.author.email,
                                },
                                "date": commit.committed_datetime.isoformat(),
                                "files_changed": len(commit.stats.files),
                            }
                        )

                    ttl = int(cache_cfg.get("ttl_seconds", 600))
                    repo_scope = (
                        f"repo:{selected_id}" if selected_id else "repo:default"
                    )
                    cache_key = f"{repo_scope}:commits:{branch_name}"
                    cache_service.set(cache_key, commits, ttl)
                    logger.debug(
                        "Startup cache: Prefetched %s commits for branch '%s' (ttl=%ss)", len(commits), branch_name, ttl
                    )
                except Exception as e:
                    logger.warning("Startup cache: commits prefetch failed: %s", e)

            if cache_cfg.get("prefetch_on_startup", True):
                prefetch_items = cache_cfg.get("prefetch_items") or {"git": True}
                prefetch_map = {"git": prefetch_commits_once}
                for key, enabled in prefetch_items.items():
                    if enabled and key in prefetch_map:
                        logger.debug(
                            "Startup cache: prefetch enabled for '%s' — scheduling task", key
                        )
                        asyncio.create_task(prefetch_map[key]())
                    elif not enabled:
                        logger.debug("Startup cache: prefetch disabled for '%s'", key)
                    else:
                        logger.debug("Startup cache: no prefetch handler for '%s'", key)
    except Exception as e:
        logger.warning("Startup cache: Failed to initialize cache prefetch: %s", e)

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Application shutdown completed")


# Initialize FastAPI app
app = FastAPI(
    title="Cockpit API",
    description="Network Device Management Dashboard API",
    version="2.0.0",
    docs_url=None,  # Disable default docs to use custom ones
    redoc_url=None,  # Disable default redoc to use custom one
    redirect_slashes=True,
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


@app.middleware("http")
async def security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


# Mount swagger-ui static files for air-gapped environments
# This serves Swagger UI assets locally instead of from CDN
# Mounted under /api/ prefix so it works through the Next.js proxy
try:
    static_dir = os.path.join(os.path.dirname(__file__), "static", "swagger-ui")
    if os.path.exists(static_dir):
        app.mount(
            "/api/static/swagger-ui",
            StaticFiles(directory=static_dir),
            name="swagger-ui",
        )
        logger.info("Swagger UI static files mounted from: %s", static_dir)
    else:
        logger.warning("Swagger UI static directory not found: %s", static_dir)
except Exception as e:
    logger.error("Failed to mount Swagger UI static files: %s", e)

# Include routers
# Authentication & Profile
app.include_router(auth_router)
app.include_router(oidc_router)
app.include_router(profile_router)

# Jobs (Templates, Schedules, Runs, Celery)
app.include_router(job_templates_router)
app.include_router(job_schedules_router)
app.include_router(job_runs_router)
app.include_router(celery_router)
app.include_router(celery_status_router)
app.include_router(celery_settings_router)
app.include_router(celery_cleanup_router)

# Settings (Git, Templates, Cache, Celery, Credentials, RBAC, Common)
app.include_router(git_router)
app.include_router(templates_router)
app.include_router(cache_router)
app.include_router(credentials_router)
app.include_router(rbac_router)
app.include_router(settings_router)

# Health Check
app.include_router(health_router)


# Health check and basic endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI endpoint using local static files."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        swagger_js_url="/api/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/api/static/swagger-ui/swagger-ui.css",
        swagger_favicon_url="/api/static/swagger-ui/favicon-32x32.png",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Custom ReDoc endpoint using local static files."""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=app.title + " - ReDoc",
        redoc_js_url="/api/static/swagger-ui/redoc.standalone.js",
    )


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Cockpit API v2.0 - Network Device Management Dashboard",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    from config import settings

    uvicorn.run(app, host="127.0.0.1", port=settings.port)
