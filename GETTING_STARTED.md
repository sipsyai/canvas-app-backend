# Getting Started - Canvas App Backend

**Quick start guide for Claude Code development**

## 📁 Project Ready!

Your backend project is ready at:
```
/Users/ali/Documents/Projects/canvas-app-backend
```

## 📚 What's Included

### Documentation (Read First!)

1. **[BACKEND_ARCHITECTURE_ANALYSIS.md](./BACKEND_ARCHITECTURE_ANALYSIS.md)** (37 KB)
   - Complete architecture analysis
   - Technology decisions and rationale
   - JSONB vs EAV performance comparison
   - Multi-tenancy strategy
   - Migration path

2. **[DATABASE_VISUAL_SCHEMA.md](./DATABASE_VISUAL_SCHEMA.md)** (73 KB)
   - Complete visual database schema
   - Example CRM application
   - SQL query examples
   - Relationship diagrams
   - Performance considerations

3. **[BACKEND_PROJECT_SPECIFICATION.md](./BACKEND_PROJECT_SPECIFICATION.md)** (37 KB)
   - Full API specification (30+ endpoints)
   - Service layer architecture
   - Testing strategy
   - Development workflow
   - Deployment guide

4. **[CLAUDE.md](./CLAUDE.md)** (14 KB)
   - Claude Code development guidelines
   - Code patterns and standards
   - Common workflows
   - Debugging tips
   - **Read this before coding!**

5. **[README.md](./README.md)** (8 KB)
   - Quick start guide
   - API endpoints overview
   - Development commands

### Configuration Files

- ✅ **requirements.txt** - All dependencies (FastAPI, SQLAlchemy, Supabase, pytest, ruff)
- ✅ **.env.example** - Environment variables template
- ✅ **.gitignore** - Python + project-specific ignores
- ✅ **pyproject.toml** - Ruff + mypy configuration

### Project Structure

```
canvas-app-backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # ⚠️ Empty - Start here!
│   ├── config.py         # ⚠️ Empty - Create next
│   ├── database.py       # ⚠️ Empty - Database setup
│   ├── models/           # ✅ Ready
│   ├── schemas/          # ✅ Ready
│   ├── routers/          # ✅ Ready
│   ├── services/         # ✅ Ready
│   ├── middleware/       # ✅ Ready
│   └── utils/            # ✅ Ready
├── alembic/              # ✅ Ready (run alembic init)
│   └── versions/
├── tests/                # ✅ Ready
│   ├── __init__.py
│   └── conftest.py       # ⚠️ Empty - Add fixtures
└── docs/                 # All analysis docs
```

## 🚀 Quick Start (5 Steps)

### Step 1: Setup Environment (5 min)

```bash
# Navigate to project
cd /Users/ali/Documents/Projects/canvas-app-backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your Supabase credentials
```

### Step 2: Database Setup (10 min)

```bash
# Initialize Alembic
alembic init alembic

# Create initial migration (see BACKEND_PROJECT_SPECIFICATION.md Section 3)
alembic revision -m "Initial schema"
# Copy SQL schema from DATABASE_VISUAL_SCHEMA.md

# Apply migration
alembic upgrade head
```

### Step 3: Create Core Files (15 min)

**Priority order:**

1. **app/config.py** - Environment configuration
   ```python
   from pydantic_settings import BaseSettings

   class Settings(BaseSettings):
       DATABASE_URL: str
       SUPABASE_URL: str
       SUPABASE_ANON_KEY: str
       # ... (see CLAUDE.md for full example)
   ```

2. **app/database.py** - SQLAlchemy setup
   ```python
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   # ... (see BACKEND_PROJECT_SPECIFICATION.md Section 3)
   ```

3. **app/main.py** - FastAPI app
   ```python
   from fastapi import FastAPI

   app = FastAPI(title="Canvas App API", version="1.0.0")

   @app.get("/api/health")
   async def health_check():
       return {"status": "ok"}
   ```

### Step 4: Run Development Server (1 min)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs

### Step 5: Build Features (Following Spec)

Follow **BACKEND_PROJECT_SPECIFICATION.md Section 12** (Claude Code Checklist):

```
Phase 1: Project Setup ✅ (Done!)
Phase 2: Database (1 hour) - Create migration
Phase 3: Models (1 hour) - SQLAlchemy models
Phase 4: Schemas (30 min) - Pydantic schemas
Phase 5: Services (2 hours) - Business logic
Phase 6: Routers (1 hour) - API endpoints
Phase 7: Testing (1 hour) - Unit + integration tests
Phase 8: Documentation (30 min) - OpenAPI docs
```

## 📖 Development Guide

### Read These Before Coding

1. **CLAUDE.md** - Development standards (MUST READ!)
2. **BACKEND_PROJECT_SPECIFICATION.md** - Full API spec
3. **DATABASE_VISUAL_SCHEMA.md** - Database schema

### Key Patterns

**Service Layer Pattern:**
```
Router (routers/) → Service (services/) → Model (models/) → Database
```

**Type Safety:**
```python
# Request/Response: Pydantic schemas (schemas/)
# Database: SQLAlchemy models (models/)
# Business Logic: Services (services/)
```

**Async Everything:**
```python
async def create_field(db: AsyncSession, ...) -> Field:
    result = await db.execute(...)
    await db.commit()
    return field
```

## 🔧 Common Commands

```bash
# Development server
uvicorn app.main:app --reload

# Run tests
pytest

# Lint code
ruff check .

# Format code
ruff format .

# Type check
mypy app/

# Database migration
alembic revision --autogenerate -m "Add table"
alembic upgrade head
```

## 📊 Database Schema Overview

**7 Core Tables:**

1. **fields** - Master field library (global + user fields)
2. **objects** - Object definitions (Contact, Company, etc.)
3. **object_fields** - N:N mapping (which fields in which objects)
4. **records** - Dynamic data (JSONB storage)
5. **relationships** - Relationship definitions (1:N, N:N)
6. **relationship_records** - Junction table for N:N
7. **applications** - App collections (CRM, ITSM)

See **DATABASE_VISUAL_SCHEMA.md** for complete schema with examples.

## 🎯 Development Checklist

Use this to track progress:

### Phase 1: Foundation
- [ ] Read CLAUDE.md
- [ ] Read BACKEND_PROJECT_SPECIFICATION.md
- [ ] Setup .env with Supabase credentials
- [ ] Create app/config.py
- [ ] Create app/database.py
- [ ] Create app/main.py (basic FastAPI app)
- [ ] Run server and verify /docs works

### Phase 2: Database
- [ ] Initialize Alembic
- [ ] Create migration with schema (from DATABASE_VISUAL_SCHEMA.md)
- [ ] Apply migration
- [ ] Verify tables in Supabase dashboard
- [ ] Test RLS policies

### Phase 3: Models
- [ ] Create Field model (app/models/field.py)
- [ ] Create Object model (app/models/object.py)
- [ ] Create ObjectField model (app/models/object_field.py)
- [ ] Create Record model (app/models/record.py)
- [ ] Create Relationship models
- [ ] Create Application model

### Phase 4: Schemas
- [ ] Create Pydantic schemas for all models
- [ ] Add validation rules
- [ ] Create request/response schemas

### Phase 5: Services
- [ ] FieldService - CRUD operations
- [ ] ObjectService - CRUD + field mapping
- [ ] RecordService - JSONB validation
- [ ] RelationshipService - Link/unlink records
- [ ] ApplicationService - App management

### Phase 6: Routers
- [ ] Fields API (/api/fields)
- [ ] Objects API (/api/objects)
- [ ] Records API (/api/records)
- [ ] Relationships API (/api/relationships)
- [ ] Applications API (/api/applications)
- [ ] Add authentication middleware

### Phase 7: Testing
- [ ] Setup test fixtures (conftest.py)
- [ ] Write service tests
- [ ] Write router tests
- [ ] Write integration tests
- [ ] Achieve >90% coverage

### Phase 8: Documentation
- [ ] Generate OpenAPI docs
- [ ] Add docstrings to services
- [ ] Update README with examples
- [ ] Create deployment guide

## 🐛 Troubleshooting

### Issue: Module not found

```bash
# Make sure you're in virtualenv
which python  # Should show venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Database connection failed

```bash
# Check .env
cat .env | grep DATABASE_URL

# Test connection
python -c "from app.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### Issue: Alembic migration failed

```bash
# Check migration file
cat alembic/versions/*.py

# Check database
psql $DATABASE_URL -c "\dt"

# Rollback and retry
alembic downgrade -1
alembic upgrade head
```

## 📞 Need Help?

1. Check **CLAUDE.md** for patterns
2. Read **BACKEND_PROJECT_SPECIFICATION.md** for API details
3. Review **DATABASE_VISUAL_SCHEMA.md** for schema questions
4. Look at **BACKEND_ARCHITECTURE_ANALYSIS.md** for architecture decisions

## 🎉 Success Criteria

Backend is ready when:

- ✅ Server runs on http://localhost:8000
- ✅ /docs shows interactive API documentation
- ✅ Database has 7 tables with RLS policies
- ✅ Can create field via API
- ✅ Can create object with fields via API
- ✅ Can create record with JSONB data via API
- ✅ Authentication works (JWT from Supabase)
- ✅ Tests pass with >90% coverage

## 🚢 Next Steps (After Backend Complete)

1. **Frontend Integration** - Connect React app to API
2. **Real-time Updates** - Add WebSocket support
3. **Bulk Operations** - Optimize CSV import/export
4. **Audit Trail** - Track all changes
5. **Deployment** - Deploy to Railway/Render

---

**Ready to start?** Open this project in Claude Code and follow Phase 2! 🚀

**Estimated Time to MVP:** ~8 hours (following the specification)
