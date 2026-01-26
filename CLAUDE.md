# Canvas App Backend

FastAPI + PostgreSQL + SQLAlchemy (async) no-code platform API.

## Quick Start

```bash
source venv/bin/activate && ./start.sh
```

## Commands

| Task | Command |
|------|---------|
| Server | `./start.sh` / `./stop.sh` |
| Tests | `pytest` |
| Lint | `ruff check . && ruff format .` |
| Migrate | `alembic upgrade head` |

## Critical Rules

1. **venv first** - Always `source venv/bin/activate`
2. **bcrypt==4.1.3** - Pin version (5.x breaks passlib)
3. **datetime.now(UTC)** - Not `utcnow()`
4. **Service layer** - Logic in `services/`, not routers
5. **Pydantic v2** - Use `model_dump()`, not `.dict()`

## Project Structure

```
app/
├── main.py          # FastAPI entry
├── config.py        # Settings
├── database.py      # SQLAlchemy async
├── models/          # ORM models
├── schemas/         # Pydantic schemas
├── routers/         # API endpoints
├── services/        # Business logic (CRITICAL)
├── middleware/      # JWT auth
└── utils/           # Security helpers
```

## Tech Stack

- FastAPI 0.115+ / Python 3.11+
- PostgreSQL 16 (Supabase)
- SQLAlchemy 2.0 (async) + Alembic
- Custom JWT + bcrypt auth
- pytest + ruff

## Documentation

@docs/GETTING_STARTED.md
@docs/DEVELOPMENT_WORKFLOW.md
@docs/architecture/OVERVIEW.md
@docs/api/SPECIFICATION.md
@docs/database/VISUAL_SCHEMA.md
