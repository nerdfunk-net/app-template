# Cockpit-NG Application Template

> **Modern Full-Stack Application Scaffold for Business Applications**

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)

Cockpit-NG is a production-ready application scaffold/template designed to accelerate the development of modern business applications. It provides a complete foundation with authentication, authorization, job orchestration, Git integration, and a modern UI framework.

---

## ✨ Features

### 🔐 Authentication & Authorization
- **Role-Based Access Control (RBAC)**: Fine-grained permission management
- **JWT Authentication**: Secure token-based authentication
- **OIDC/SSO Support**: Integration with identity providers (Keycloak, Azure AD, Okta)
- **User Management**: Create, manage, and assign roles to users
- **Permission System**: Control access to features based on user roles (format: `resource:action`)

### ⚙️ Job Orchestration System
- **Job Templates**: Define reusable job configurations with parameters
- **Job Scheduler**: Cron-based scheduling for recurring tasks
- **Job Execution**: Celery-based background task execution with Redis
- **Job Monitoring**: Track job progress, view results, and access logs
- **Job History**: Complete audit trail of all job executions

### 📋 Template & Git Management
- **Template System**: Jinja2-based template engine for dynamic content generation
- **Template Versioning**: Track template versions with Git integration
- **Git Integration**: Version control with branch/commit management
- **Configuration Templates**: Store and version application configurations
- **Template History**: Track changes over time with Git history

### 🎨 Modern UI Framework
- **Next.js 15 App Router**: React 19-based frontend with server components
- **Shadcn UI**: Beautiful, accessible component library
- **Tailwind CSS 4**: Utility-first CSS framework
- **TanStack Query**: Powerful data fetching and caching
- **Type-Safe**: Full TypeScript support with strict type checking

### ⚡ Developer Experience
- **Feature-Based Organization**: Code organized by domains, not technical layers
- **Repository Pattern**: Clean separation of data access and business logic
- **API Proxy**: Frontend API calls routed through Next.js proxy
- **Hot Reload**: Fast development with automatic reloading
- **ESLint + Prettier**: Code quality and formatting enforcement

---

## 🏗️ Architecture

Cockpit-NG uses a modern full-stack architecture with the following components:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Environment                        │
├─────────────────┬─────────────────┬─────────────────────────────┤
│                 │                 │                             │
│  ┌───────────┐  │  ┌───────────┐  │  ┌───────────┐             │
│  │  Next.js  │  │  │  FastAPI  │  │  │  Celery   │             │
│  │ Frontend  │◄─┼─►│  Backend  │◄─┼─►│  Worker   │             │
│  │  :3000    │  │  │   :8000   │  │  │           │             │
│  └───────────┘  │  └─────┬─────┘  │  └─────┬─────┘             │
│                 │        │        │        │                    │
│                 │        ▼        │        ▼                    │
│                 │  ┌───────────┐  │  ┌───────────┐             │
│                 │  │PostgreSQL │  │  │   Redis   │             │
│                 │  │  Database │  │  │  Broker   │             │
│                 │  └───────────┘  │  └───────────┘             │
│                 │                 │        ▲                    │
│                 │                 │        │                    │
│                 │                 │  ┌─────┴─────┐             │
│                 │                 │  │  Celery   │             │
│                 │                 │  │   Beat    │             │
│                 │                 │  │(Scheduler)│             │
│                 │                 │  └───────────┘             │
└─────────────────┴─────────────────┴─────────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │    External Services    │
              ├─────────────────────────┤
              │  • Git Repositories     │
              │  • OIDC Providers       │
              │  • Custom Integrations  │
              └─────────────────────────┘
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Next.js 15, React 19, TypeScript | Modern web UI with Tailwind CSS |
| **Backend** | FastAPI, Python 3.11+ | REST API, authentication, business logic |
| **Worker** | Celery | Background task execution |
| **Scheduler** | Celery Beat | Periodic task scheduling |
| **Database** | PostgreSQL | Persistent data storage (40+ tables) |
| **Message Broker** | Redis | Task queue and caching |

### Included Features

| Feature | Status | Description |
|---------|--------|-------------|
| ✅ Authentication | Ready | JWT tokens, login/logout, user profile |
| ✅ RBAC System | Ready | Users, roles, permissions with fine-grained control |
| ✅ OIDC/SSO | Ready | Multi-provider support (Keycloak, Azure AD, Okta) |
| ✅ Job System | Ready | Templates, scheduler, execution, monitoring |
| ✅ Git Integration | Ready | Repository management, branch/commit tracking |
| ✅ Template Engine | Ready | Jinja2 templates with versioning |
| ✅ Settings Management | Ready | Git, Cache, Celery, Credentials configuration |
| ✅ Credentials | Ready | Encrypted credential storage |
| ✅ Cache System | Ready | Redis-based caching for performance |
| ✅ Audit Logging | Ready | Complete activity tracking |

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/your-app.git
cd your-app

# Copy and configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Start the application
cd docker
docker compose up -d
```

### Access the Application

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

### Default Credentials

- **Username**: `admin`
- **Password**: `admin`

> ⚠️ **Important**: Change the default password immediately after first login!

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [INSTALL.md](INSTALL.md) | Detailed installation guide |
| [CLAUDE.md](CLAUDE.md) | Technical architecture and developer guide |
| [OIDC_SETUP.md](OIDC_SETUP.md) | OIDC/SSO configuration |
| [PERMISSIONS.md](PERMISSIONS.md) | RBAC and permission system |
| [docker/README.md](docker/README.md) | Docker deployment options |

---

## 🔧 Configuration

### Environment Variables

Configure your backend in `backend/.env`:

```bash
# Server
BACKEND_SERVER_HOST=127.0.0.1
BACKEND_SERVER_PORT=8000

# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=cockpit
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=password

# Redis
COCKPIT_REDIS_PASSWORD=changeme

# Authentication
SECRET_KEY=your-secret-key-change-in-production
INITIAL_USERNAME=admin
INITIAL_PASSWORD=admin
```

### OIDC/SSO

Configure identity providers in `config/oidc_providers.yaml`. See [OIDC_SETUP.md](OIDC_SETUP.md) for details.

### Celery Queues

The system includes built-in Celery queues defined in `backend/celery_app.py`:
- **default**: General purpose tasks
- **backup**: Backup operations
- **network**: Network operations (can be repurposed)
- **heavy**: Resource-intensive tasks

---

## 🛠️ Development

### Local Development Setup

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL and Redis (via Docker or locally)
# Configure .env with connection details

# Run backend
COCKPIT_REDIS_PASSWORD=changeme python start.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Celery Worker (new terminal)
cd backend
python start_celery.py

# Celery Beat (new terminal)
cd backend
python start_beat.py
```

### Project Structure

```
backend/
├── core/           # Database models, auth, config
├── routers/        # FastAPI route handlers
├── services/       # Business logic layer
├── repositories/   # Data access layer
├── tasks/          # Celery background tasks
├── models/         # Pydantic request/response models
└── migrations/     # Database migrations

frontend/
├── src/
│   ├── app/                    # Next.js pages (App Router)
│   ├── components/
│   │   ├── ui/                 # Shadcn UI primitives
│   │   ├── features/           # Feature-specific components
│   │   └── layout/             # Layout components
│   ├── hooks/                  # React hooks
│   │   └── queries/            # TanStack Query hooks
│   ├── lib/                    # Utilities and stores
│   └── services/               # API service wrappers
```

### Adding New Features

1. **Backend**: Create model → repository → service → router
2. **Frontend**: Create page → components → queries/mutations → integrate
3. **Database**: Add table to `backend/core/models.py`
4. **Permissions**: Define in Settings → Permissions UI

See [CLAUDE.md](CLAUDE.md) for detailed architectural guidelines.

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend linting
cd frontend
npm run lint
```

---

## 🎯 Use Cases

This scaffold is perfect for building:

- **Business Applications**: CRM, ERP, inventory management
- **Management Dashboards**: Monitoring, reporting, analytics
- **Workflow Automation**: Job orchestration, scheduled tasks
- **Multi-Tenant SaaS**: RBAC-ready with OIDC support
- **Admin Panels**: User management, settings, audit logs

---

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/nerdfunk-net/cockpit-ng/issues)
- **Documentation**: See the `doc/` directory for additional documentation
