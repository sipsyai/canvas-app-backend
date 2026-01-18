# TASK-06: FastAPI API Routers

**Phase:** 6/8
**Tahmini Süre:** 2 saat
**Bağımlılık:** Phase 5 (Business Services) ✅
**Durum:** ⏳ Bekliyor

---

## 🎯 Görev Açıklaması

7 resource için **FastAPI router'lar** oluştur. Her router:
- RESTful API endpoints (GET, POST, PATCH, DELETE)
- Request/Response validation (Pydantic schemas)
- Dependency injection (database session, user authentication)
- Error handling (404, 400, 500)
- OpenAPI docs (auto-generated)

**Pattern:** HTTP Request → Router → Service → Model → Database

---

## 📋 Ön Gereksinimler

- [x] Phase 5 tamamlandı (Services mevcut)
- [x] Phase 4 tamamlandı (Pydantic schemas mevcut)
- [x] FastAPI 0.115+ kurulu

---

## 📁 Oluşturulacak Dosyalar

```
app/routers/
├── __init__.py           # Router exports
├── fields.py             # Field endpoints
├── objects.py            # Object endpoints
├── object_fields.py      # ObjectField endpoints
├── records.py            # Record endpoints
├── relationships.py      # Relationship endpoints
├── relationship_records.py  # RelationshipRecord endpoints
└── applications.py       # Application endpoints
```

---

## 🔧 Implementation

### app/main.py (Update - Include Routers)
```python
"""Canvas App Backend - Main Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import (
    fields,
    objects,
    object_fields,
    records,
    relationships,
    relationship_records,
    applications,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="REST API for Object-Centric No-Code Platform",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(fields.router, prefix="/api/fields", tags=["Fields"])
app.include_router(objects.router, prefix="/api/objects", tags=["Objects"])
app.include_router(object_fields.router, prefix="/api/object-fields", tags=["Object Fields"])
app.include_router(records.router, prefix="/api/records", tags=["Records"])
app.include_router(relationships.router, prefix="/api/relationships", tags=["Relationships"])
app.include_router(relationship_records.router, prefix="/api/relationship-records", tags=["Relationship Records"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }

@app.on_event("startup")
async def startup_event():
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    if settings.ENABLE_DOCS:
        print(f"📚 API Docs: http://localhost:{settings.PORT}/docs")
```

---

### app/routers/__init__.py
```python
"""FastAPI Routers"""
from app.routers import (
    fields,
    objects,
    object_fields,
    records,
    relationships,
    relationship_records,
    applications,
)

__all__ = [
    "fields",
    "objects",
    "object_fields",
    "records",
    "relationships",
    "relationship_records",
    "applications",
]
```

---

### app/routers/fields.py
```python
"""Field API Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import FieldCreate, FieldUpdate, FieldResponse
from app.services import field_service

router = APIRouter()

# TODO: Add authentication dependency (Phase 7)
def get_current_user_id() -> str:
    """Mock authentication - returns hardcoded user ID"""
    return "user_123"  # Replace with JWT auth in Phase 7

@router.post("/", response_model=FieldResponse, status_code=201)
async def create_field(
    field_in: FieldCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create new field (custom field only).

    Example request:
    ```json
    {
        "name": "email",
        "label": "Email Address",
        "type": "email",
        "description": "Contact email",
        "config": {
            "validation": {"required": true, "regex": ".*@.*"}
        }
    }
    ```
    """
    field = await field_service.create_field(db, field_in, user_id)
    return field

@router.get("/", response_model=List[FieldResponse])
async def list_fields(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get all fields (global + user's custom fields).

    Returns both system fields (Created By, Owner, etc.) and user's custom fields.
    """
    global_fields = await field_service.get_global_fields(db)
    user_fields = await field_service.get_user_fields(db, user_id)
    return global_fields + user_fields

@router.get("/{field_id}", response_model=FieldResponse)
async def get_field(
    field_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get single field by ID"""
    field = await field_service.get_by_id(db, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field

@router.patch("/{field_id}", response_model=FieldResponse)
async def update_field(
    field_id: str,
    field_in: FieldUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update existing field (custom fields only)"""
    field = await field_service.update_field(db, field_id, field_in)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field

@router.delete("/{field_id}", status_code=204)
async def delete_field(
    field_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete field (custom fields only)"""
    deleted = await field_service.delete(db, field_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Field not found")
    return None
```

---

### app/routers/objects.py
```python
"""Object API Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ObjectCreate, ObjectUpdate, ObjectResponse
from app.services import object_service

router = APIRouter()

def get_current_user_id() -> str:
    return "user_123"  # Mock - replace with JWT in Phase 7

@router.post("/", response_model=ObjectResponse, status_code=201)
async def create_object(
    object_in: ObjectCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create new object (Contact, Company, etc.).

    Example request:
    ```json
    {
        "name": "contact",
        "label": "Contact",
        "plural_label": "Contacts",
        "description": "Customer contacts",
        "icon": "👤"
    }
    ```
    """
    obj = await object_service.create_object(db, object_in, user_id)
    return obj

@router.get("/", response_model=List[ObjectResponse])
async def list_objects(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get all user's objects"""
    objects = await object_service.get_user_objects(db, user_id)
    return objects

@router.get("/{object_id}", response_model=ObjectResponse)
async def get_object(
    object_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get single object by ID"""
    obj = await object_service.get_by_id(db, object_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj

@router.patch("/{object_id}", response_model=ObjectResponse)
async def update_object(
    object_id: str,
    object_in: ObjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update existing object"""
    obj = await object_service.update_object(db, object_id, object_in)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj

@router.delete("/{object_id}", status_code=204)
async def delete_object(
    object_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete object (CASCADE: deletes fields, records)"""
    deleted = await object_service.delete(db, object_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Object not found")
    return None
```

---

### app/routers/records.py (MOST IMPORTANT!)
```python
"""Record API Endpoints - Dynamic JSONB data"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import RecordCreate, RecordUpdate, RecordResponse, RecordListResponse
from app.services import record_service

router = APIRouter()

def get_current_user_id() -> str:
    return "user_123"  # Mock - replace with JWT in Phase 7

@router.post("/", response_model=RecordResponse, status_code=201)
async def create_record(
    record_in: RecordCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create new record with JSONB data.

    Example request:
    ```json
    {
        "object_id": "obj_contact",
        "data": {
            "fld_name": "Ali Yılmaz",
            "fld_email": "ali@example.com",
            "fld_phone": "+90 555 1234567",
            "fld_company": "Acme Corp"
        }
    }
    ```

    Response includes auto-generated primary_value (first text field).
    """
    record = await record_service.create_record(db, record_in, user_id)
    return record

@router.get("/", response_model=RecordListResponse)
async def list_records(
    object_id: str = Query(..., description="Object ID to filter records"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Records per page"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all records for an object with pagination.

    Example: GET /api/records?object_id=obj_contact&page=1&page_size=50
    """
    skip = (page - 1) * page_size
    records, total = await record_service.get_records_by_object(
        db, object_id, skip=skip, limit=page_size
    )
    return RecordListResponse(
        total=total,
        page=page,
        page_size=page_size,
        records=records,
    )

@router.get("/{record_id}", response_model=RecordResponse)
async def get_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get single record by ID"""
    record = await record_service.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.patch("/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: str,
    record_in: RecordUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Update record's JSONB data (MERGE, not replace).

    Example request:
    ```json
    {
        "data": {
            "fld_email": "newemail@example.com"
        }
    }
    ```

    This will update only fld_email, keeping other fields unchanged.
    """
    record = await record_service.update_record(db, record_id, record_in, user_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.delete("/{record_id}", status_code=204)
async def delete_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete record"""
    deleted = await record_service.delete(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return None

@router.get("/search/", response_model=List[RecordResponse])
async def search_records(
    object_id: str = Query(..., description="Object ID"),
    q: str = Query(..., min_length=1, description="Search term"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search records by primary_value (fast text search).

    Example: GET /api/records/search?object_id=obj_contact&q=Ali
    """
    records = await record_service.search_records(db, object_id, q)
    return records
```

---

### app/routers/relationships.py
```python
"""Relationship API Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import RelationshipCreate, RelationshipUpdate, RelationshipResponse
from app.services import relationship_service

router = APIRouter()

def get_current_user_id() -> str:
    return "user_123"

@router.post("/", response_model=RelationshipResponse, status_code=201)
async def create_relationship(
    relationship_in: RelationshipCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create relationship between objects.

    Example: Contact → Opportunities (1:N)
    ```json
    {
        "name": "contact_opportunities",
        "from_object_id": "obj_contact",
        "to_object_id": "obj_opportunity",
        "type": "1:N",
        "from_label": "Opportunities",
        "to_label": "Contact"
    }
    ```
    """
    rel = await relationship_service.create_relationship(db, relationship_in, user_id)
    return rel

@router.get("/objects/{object_id}", response_model=List[RelationshipResponse])
async def get_object_relationships(
    object_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all relationships for an object"""
    relationships = await relationship_service.get_relationships_for_object(db, object_id)
    return relationships

@router.delete("/{relationship_id}", status_code=204)
async def delete_relationship(
    relationship_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete relationship definition"""
    deleted = await relationship_service.delete(db, relationship_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return None
```

---

### app/routers/relationship_records.py
```python
"""RelationshipRecord API Endpoints - Record linking"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import RelationshipRecordCreate, RelationshipRecordResponse
from app.services import relationship_record_service

router = APIRouter()

def get_current_user_id() -> str:
    return "user_123"

@router.post("/", response_model=RelationshipRecordResponse, status_code=201)
async def create_relationship_record(
    link_in: RelationshipRecordCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Link two records via relationship.

    Example: Link Contact to Opportunity
    ```json
    {
        "relationship_id": "rel_contact_opportunity",
        "from_record_id": "rec_ali",
        "to_record_id": "rec_bigdeal",
        "metadata": {"role": "Decision Maker"}
    }
    ```
    """
    link = await relationship_record_service.create_link(db, link_in, user_id)
    return link

@router.get("/records/{record_id}/related", response_model=List[RelationshipRecordResponse])
async def get_related_records(
    record_id: str,
    relationship_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all records related to a specific record via relationship"""
    links = await relationship_record_service.get_related_records(
        db, record_id, relationship_id
    )
    return links

@router.delete("/{link_id}", status_code=204)
async def delete_relationship_record(
    link_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete relationship between records"""
    deleted = await relationship_record_service.delete(db, link_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Link not found")
    return None
```

---

### app/routers/applications.py
```python
"""Application API Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.services import application_service

router = APIRouter()

def get_current_user_id() -> str:
    return "user_123"

@router.post("/", response_model=ApplicationResponse, status_code=201)
async def create_application(
    app_in: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create new application (CRM, ITSM, etc.).

    Example request:
    ```json
    {
        "name": "CRM",
        "description": "Customer Relationship Management",
        "icon": "🤝",
        "config": {
            "objects": ["obj_contact", "obj_company", "obj_opportunity"],
            "navigation": [...]
        }
    }
    ```
    """
    app = await application_service.create_application(db, app_in, user_id)
    return app

@router.get("/", response_model=List[ApplicationResponse])
async def list_applications(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all applications"""
    apps = await application_service.get_all(db, skip=skip, limit=limit)
    return apps

@router.post("/{app_id}/publish", response_model=ApplicationResponse)
async def publish_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Publish application (sets published_at timestamp)"""
    app = await application_service.publish_application(db, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.delete("/{app_id}", status_code=204)
async def delete_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete application"""
    deleted = await application_service.delete(db, app_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
    return None
```

---

## ✅ Başarı Kriterleri

Tamamlandığında şunlar olmalı:

- [ ] `app/routers/` klasöründe 8 dosya (7 router + __init__)
- [ ] `app/main.py`'de tüm router'lar include edilmiş
- [ ] Her endpoint type hints içeriyor
- [ ] Error handling var (HTTPException 404, 400)
- [ ] Dependency injection kullanılmış (Depends)
- [ ] Status code'lar doğru (201 create, 204 delete)
- [ ] API docs çalışıyor: http://localhost:8000/docs

**Test:**
```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Open browser
open http://localhost:8000/docs

# Test create field endpoint
curl -X POST http://localhost:8000/api/fields \
  -H "Content-Type: application/json" \
  -d '{
    "name": "email",
    "label": "Email",
    "type": "email"
  }'

# Expected: 201 Created with field response
```

---

## 📚 İlgili Dökümanlar

- `BACKEND_PROJECT_SPECIFICATION.md` - Full API specification
- FastAPI docs: https://fastapi.tiangolo.com/

---

**Sonraki Task:** `TASK-07-authentication.md` (JWT authentication)
