# Canvas App Backend

**REST API for Object-Centric No-Code Platform**

A FastAPI-based backend for building Salesforce/ServiceNow/Airtable-style applications.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16 (or Supabase account)
- pip / virtualenv

### Installation

```bash
# 1. Clone repository (or create new directory)
git clone <repo-url>
cd canvas-app-backend

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your database credentials

# 5. Run database migrations
alembic upgrade head

# 6. Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access API

- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/health

## 📚 Documentation

**Start here (in this order):**

1. **[Architecture Analysis](./docs/architecture/ANALYSIS.md)** - Complete architecture analysis and technology decisions
2. **[Database Visual Schema](./docs/database/VISUAL_SCHEMA.md)** - Visual database schema with CRM example
3. **[API Specification](./docs/api/SPECIFICATION.md)** - Full API specification and implementation guide
4. **[CLAUDE.md](./CLAUDE.md)** - Development guidelines for Claude Code
5. **[Development Workflow](./docs/DEVELOPMENT_WORKFLOW.md)** - Common workflows and pitfalls

## 🏗️ Architecture

### Technology Stack

```yaml
Framework: FastAPI 0.115+
Language: Python 3.11+
Database: PostgreSQL 16
ORM: SQLAlchemy 2.0 (async)
Auth: Supabase Auth (JWT)
Migration: Alembic
Testing: pytest + pytest-asyncio
Linting: ruff
Type Checking: mypy
```

### Database Pattern

**JSONB Hybrid Model:**
- Metadata: Normalized tables (fields, objects, relationships)
- Data: JSONB in `records.data`
- Performance: Denormalized `primary_value` + GIN indexes

### Core Tables

1. **fields** - Master field library
2. **objects** - Object definitions (Contact, Company, etc.)
3. **object_fields** - N:N mapping between objects and fields
4. **records** - Dynamic data storage (JSONB)
5. **relationships** - Relationship definitions
6. **relationship_records** - N:N junction table
7. **applications** - Application collections (CRM, ITSM)

## 🔌 API Endpoints

### Fields API

```
GET    /api/fields              # List all fields
POST   /api/fields              # Create new field
GET    /api/fields/{id}         # Get field details
PATCH  /api/fields/{id}         # Update field
DELETE /api/fields/{id}         # Delete field
```

### Objects API

```
GET    /api/objects             # List user's objects
POST   /api/objects             # Create new object
GET    /api/objects/{id}        # Get object with fields
PATCH  /api/objects/{id}        # Update object
DELETE /api/objects/{id}        # Delete object
POST   /api/objects/{id}/fields # Add field to object
DELETE /api/objects/{id}/fields/{field_id}
```

### Records API

```
GET    /api/records             # Query records (filters, sort, pagination)
POST   /api/records             # Create record
GET    /api/records/{id}        # Get record with typed values
PATCH  /api/records/{id}        # Update record
DELETE /api/records/{id}        # Delete record
POST   /api/records/bulk        # Bulk create
DELETE /api/records/bulk        # Bulk delete
```

### Relationships API

```
GET    /api/relationships       # List relationships
POST   /api/relationships       # Create relationship
DELETE /api/relationships/{id}  # Delete relationship
POST   /api/relationships/{id}/link    # Link records (N:N)
DELETE /api/relationships/{id}/link/{link_id}
GET    /api/records/{id}/related/{relationship_id}
```

### Applications API

```
GET    /api/applications        # List applications
POST   /api/applications        # Create application
GET    /api/applications/{id}   # Get application
PATCH  /api/applications/{id}   # Update application
DELETE /api/applications/{id}   # Delete application
```

See [API Specification](./docs/api/SPECIFICATION.md) for complete API documentation.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_fields.py

# Run with verbose output
pytest -v
```

## 🛠️ Development

### Project Structure

```
canvas-app-backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # SQLAlchemy engine setup
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic layer
│   ├── middleware/          # Authentication, logging
│   └── utils/               # Helper functions
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Ruff/mypy configuration
└── .env                     # Environment variables
```

### Common Commands

```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Lint code
ruff check .

# Format code
ruff format .

# Type check
mypy app/

# Create database migration
alembic revision --autogenerate -m "Migration description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/canvasapp
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# App
APP_NAME=Canvas App API
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Security
SECRET_KEY=your-secret-key-here
```

See `.env.example` for complete list.

## 🔒 Authentication

All endpoints require Bearer token authentication (except `/health` and `/auth/*`):

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Authentication is handled via Supabase Auth with JWT tokens.

## 📦 Deployment

### Docker

```bash
# Build image
docker build -t canvas-app-backend .

# Run container
docker run -p 8000:8000 --env-file .env canvas-app-backend
```

### Docker Compose

```bash
docker-compose up -d
```

### Production Platforms

- **Railway:** `railway up`
- **Render:** Connect GitHub repository
- **AWS Fargate:** Use Dockerfile
- **Fly.io:** `fly deploy`

## 🐛 Debugging

### Enable SQL Logging

```python
# app/database.py
engine = create_async_engine(DATABASE_URL, echo=True)
```

### Check Database Connection

```bash
# Via Python
python -c "from app.database import engine; import asyncio; asyncio.run(engine.connect())"

# Via psql
psql $DATABASE_URL
```

### View Logs

```bash
# Development server logs
tail -f logs/app.log

# Or use structured logging
uvicorn app.main:app --log-config logging.json
```

## 🤝 Contributing

1. Read [CLAUDE.md](./CLAUDE.md) for development guidelines
2. Follow existing code patterns
3. Write tests for new features
4. Run linter and type checker before committing
5. Update documentation as needed

## 📝 License

[Your License Here]

## 🔗 Related Projects

- **Frontend:** [canvas-app](../canvas-app) - React + Vite frontend
- **Database:** PostgreSQL 16 with Supabase

## 📞 Support

For questions or issues:
- Read the documentation in `/docs`
- Check [API Specification](./docs/api/SPECIFICATION.md)
- Review [CLAUDE.md](./CLAUDE.md) for common patterns
- See [Development Workflow](./docs/DEVELOPMENT_WORKFLOW.md) for troubleshooting

---

**Status:** 🚀 Ready for Development

**Estimated Development Time:** ~8 hours for MVP (following specification)

**Next Steps:**
1. Setup environment (.env)
2. Create database migration
3. Implement service layer
4. Build API routes
5. Write tests
6. Deploy

See [API Specification](./docs/api/SPECIFICATION.md) Section 12 for detailed development checklist.
