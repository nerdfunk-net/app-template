# Fresh Database Setup

This document describes how the scaffold handles fresh database initialization.

## What Happens on First Startup

When you start the application with an empty PostgreSQL database:

### 1. Database Tables Created (Automatic)

The `init_db()` function in `core/database.py` automatically creates all 21 tables defined in `core/models.py`:

**Core Tables:**
- `users` - User accounts
- `user_profiles` - Extended user information
- `roles` - Role definitions
- `permissions` - Permission definitions
- `role_permissions` - Role-permission mappings
- `user_roles` - User-role assignments
- `user_permissions` - Direct user permissions
- `settings` - General settings
- `settings_metadata` - Configuration metadata
- `credentials` - Encrypted credentials
- `git_repositories` - Git repo connections
- `git_settings` - Git configuration
- `cache_settings` - Cache configuration
- `celery_settings` - Celery configuration
- `job_templates` - Job definitions
- `job_schedules` - Job schedules
- `job_runs` - Job execution history
- `templates` - Template definitions
- `template_versions` - Template version history
- `audit_logs` - Activity tracking
- `celery_jobs` - Celery task tracking

**Method:** Uses `Base.metadata.create_all()` from SQLAlchemy - only missing tables are created.

### 2. Admin User Created (Automatic)

The startup process calls `ensure_admin_has_rbac_role()` which:

1. **Creates default admin user** (if no users exist):
   - Username: `admin`
   - Password: From `INITIAL_PASSWORD` env var (default: `admin`)
   - Email: `admin@localhost`
   - Full admin permissions enabled

2. **Seeds RBAC system** (if roles don't exist):
   - Calls `seed_rbac.main()` to create:
     - 39 permissions for scaffold features
     - 4 default roles: admin, operator, network_engineer, viewer
     - Permission assignments to roles

3. **Assigns admin role** to admin user

## Configuration

### Environment Variables

Set in `backend/.env`:

```bash
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=cockpit
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=password

# Redis (required)
COCKPIT_REDIS_PASSWORD=changeme

# Initial Admin Credentials
INITIAL_USERNAME=admin
INITIAL_PASSWORD=admin
```

## Scaffold Permissions

The RBAC system creates these permission categories:

### Dashboard
- `dashboard.settings:read` - Access to settings pages

### Git Management
- `git.repositories:read/write/delete` - Manage git repositories
- `git.operations:execute` - Execute git operations

### Settings Management
- `settings.git:read/write` - Git settings
- `settings.cache:read/write` - Cache settings
- `settings.celery:read/write` - Celery settings
- `settings.credentials:read/write/delete` - Credential management
- `settings.common:read/write` - Common settings

### User & RBAC Management
- `users:read/write/delete` - User management
- `users.roles:write` - Assign roles
- `users.permissions:write` - Assign permissions
- `rbac.roles:read/write/delete` - Role management
- `rbac.permissions:read` - View permissions

### Jobs System
- `jobs.templates:read/write/delete` - Job template management
- `jobs.schedules:read/write/delete` - Job schedule management
- `jobs.runs:read/execute` - Job execution and history

## Default Roles

### Admin
- **Full access** to all features
- All 39 permissions assigned

### Operator
- Manage jobs
- Read-only access to settings
- Execute git operations
- Cannot manage users or RBAC

### Network Engineer
- Same as operator (customizable for future features)

### Viewer
- Read-only access to most features
- Cannot view credentials or user management
- Cannot execute any operations

## Manual Seeding

If you need to re-seed the RBAC system:

```bash
cd backend

# Seed with existing data preserved
python -c "from tools import seed_rbac; seed_rbac.main()"

# Seed with all RBAC data removed first
python -c "from tools import seed_rbac; seed_rbac.main(remove_existing=True)"
```

## Testing Fresh Setup

```bash
# 1. Drop your database (PostgreSQL)
psql -U postgres -c "DROP DATABASE IF EXISTS cockpit;"
psql -U postgres -c "CREATE DATABASE cockpit;"

# 2. Start backend
cd backend
COCKPIT_REDIS_PASSWORD=changeme python start.py

# 3. Check logs - should see:
#    - "Creating 21 missing table(s): ..."
#    - "Created default admin user"
#    - "Initialized RBAC system with default roles and permissions"
#    - "Assigned admin role to user ID 1"

# 4. Login to frontend
# URL: http://localhost:3000
# Username: admin
# Password: admin (or your INITIAL_PASSWORD)
```

## Migration Files

**IMPORTANT:** All old migration files have been removed from `backend/migrations/versions/`.

The scaffold uses direct table creation from SQLAlchemy models instead of migrations. This ensures:
- Clean schema on fresh installations
- No legacy table creation
- Faster startup
- Simpler maintenance

If you need to add schema migrations later, you can:
1. Create new migration files in `migrations/versions/` (format: `NNN_description.py`)
2. Follow the pattern in `migrations/README.md`
3. The system will automatically detect and run new migrations

## Troubleshooting

### "No module named 'tools.seed_rbac'"

The import path is `tools.seed_rbac`, not just `seed_rbac`. Make sure you're in the backend directory.

### "Database connection failed"

Check PostgreSQL is running and credentials in `.env` are correct.

### "Authentication required" (Redis)

Set `COCKPIT_REDIS_PASSWORD` environment variable or in `.env` file.

### Admin user not created

Check startup logs for errors. The user creation is logged as:
```
Created default admin user (RBAC role will be assigned at startup)
Assigned admin role to user 'admin' (user_id=1)
```

### Permissions missing

Re-run the seed script:
```bash
python -c "from tools import seed_rbac; seed_rbac.main()"
```

## Summary

The scaffold provides a fully automated fresh database setup:
- ✅ 21 tables created automatically
- ✅ Admin user created with configurable password
- ✅ 39 permissions created
- ✅ 4 roles created with proper assignments
- ✅ Admin role assigned to admin user
- ✅ No manual intervention required

Just start the application with an empty database, and everything is initialized automatically!
