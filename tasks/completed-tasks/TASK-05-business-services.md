# TASK-05: Business Services Layer

**Phase:** 5/8
**Tahmini Süre:** 2 saat
**Bağımlılık:** Phase 4 (Pydantic Schemas) ✅
**Durum:** ⏳ Bekliyor

---

## 🎯 Görev Açıklaması

Her model için **business logic layer** (service) oluştur. Service layer:
- Database CRUD operations
- Business logic (validation, computed fields, etc.)
- Router'ların database'e direkt erişmesini engeller
- Testable ve reusable kod

**Pattern:** Router → Service → Model → Database

---

## 📋 Ön Gereksinimler

- [x] Phase 4 tamamlandı (Pydantic schemas mevcut)
- [x] Phase 3 tamamlandı (ORM models mevcut)
- [x] SQLAlchemy async session configured

---

## 📁 Oluşturulacak Dosyalar

```
app/services/
├── __init__.py           # Service exports
├── base.py               # Base service class (DRY)
├── field_service.py      # Field CRUD
├── object_service.py     # Object CRUD
├── object_field_service.py  # ObjectField CRUD
├── record_service.py     # Record CRUD (most complex!)
├── relationship_service.py  # Relationship CRUD
├── relationship_record_service.py  # RelationshipRecord CRUD
└── application_service.py   # Application CRUD
```

---

## 🔧 Implementation

### app/services/__init__.py
```python
"""Business Services Layer"""
from app.services.field_service import FieldService
from app.services.object_service import ObjectService
from app.services.object_field_service import ObjectFieldService
from app.services.record_service import RecordService
from app.services.relationship_service import RelationshipService
from app.services.relationship_record_service import RelationshipRecordService
from app.services.application_service import ApplicationService

__all__ = [
    "FieldService",
    "ObjectService",
    "ObjectFieldService",
    "RecordService",
    "RelationshipService",
    "RelationshipRecordService",
    "ApplicationService",
]
```

---

### app/services/base.py (DRY Pattern)
```python
"""Base Service Class - Reusable CRUD operations"""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseService(Generic[ModelType]):
    """Base service with common CRUD operations"""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: str) -> Optional[ModelType]:
        """Get single record by ID"""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """Get all records with pagination"""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: dict) -> ModelType:
        """Create new record"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        id: str,
        obj_in: dict,
    ) -> Optional[ModelType]:
        """Update existing record"""
        db_obj = await self.get_by_id(db, id)
        if not db_obj:
            return None

        for field, value in obj_in.items():
            if value is not None:  # Only update non-None values
                setattr(db_obj, field, value)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: str) -> bool:
        """Delete record by ID"""
        db_obj = await self.get_by_id(db, id)
        if not db_obj:
            return False

        await db.delete(db_obj)
        await db.commit()
        return True
```

---

### app/services/field_service.py
```python
"""Field Service - Field CRUD operations"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Field
from app.schemas import FieldCreate, FieldUpdate
from app.services.base import BaseService
import uuid

class FieldService(BaseService[Field]):
    """Service for Field operations"""

    def __init__(self):
        super().__init__(Field)

    async def create_field(
        self,
        db: AsyncSession,
        field_in: FieldCreate,
        user_id: str,
    ) -> Field:
        """Create new field with auto-generated ID"""
        field_data = field_in.model_dump()
        field_data["id"] = f"fld_{uuid.uuid4().hex[:8]}"
        field_data["created_by"] = user_id
        return await self.create(db, field_data)

    async def get_global_fields(self, db: AsyncSession) -> List[Field]:
        """Get all global (system) fields"""
        result = await db.execute(
            select(Field).where(Field.is_global == True)
        )
        return list(result.scalars().all())

    async def get_user_fields(self, db: AsyncSession, user_id: str) -> List[Field]:
        """Get user's custom fields"""
        result = await db.execute(
            select(Field).where(
                Field.created_by == user_id,
                Field.is_custom == True
            )
        )
        return list(result.scalars().all())

    async def update_field(
        self,
        db: AsyncSession,
        field_id: str,
        field_in: FieldUpdate,
    ) -> Optional[Field]:
        """Update existing field"""
        update_data = field_in.model_dump(exclude_unset=True)
        return await self.update(db, field_id, update_data)

# Singleton instance
field_service = FieldService()
```

---

### app/services/object_service.py
```python
"""Object Service - Object CRUD operations"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Object
from app.schemas import ObjectCreate, ObjectUpdate
from app.services.base import BaseService
import uuid

class ObjectService(BaseService[Object]):
    """Service for Object operations"""

    def __init__(self):
        super().__init__(Object)

    async def create_object(
        self,
        db: AsyncSession,
        object_in: ObjectCreate,
        user_id: str,
    ) -> Object:
        """Create new object with auto-generated ID"""
        object_data = object_in.model_dump()
        object_data["id"] = f"obj_{uuid.uuid4().hex[:8]}"
        object_data["created_by"] = user_id
        object_data["is_custom"] = True
        object_data["is_global"] = False
        return await self.create(db, object_data)

    async def get_user_objects(self, db: AsyncSession, user_id: str) -> List[Object]:
        """Get user's custom objects"""
        result = await db.execute(
            select(Object).where(Object.created_by == user_id)
        )
        return list(result.scalars().all())

    async def update_object(
        self,
        db: AsyncSession,
        object_id: str,
        object_in: ObjectUpdate,
    ) -> Optional[Object]:
        """Update existing object"""
        update_data = object_in.model_dump(exclude_unset=True)
        return await self.update(db, object_id, update_data)

# Singleton instance
object_service = ObjectService()
```

---

### app/services/record_service.py (MOST COMPLEX!)
```python
"""Record Service - Record CRUD with JSONB handling"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Record, Object, Field, ObjectField
from app.schemas import RecordCreate, RecordUpdate
from app.services.base import BaseService
import uuid

class RecordService(BaseService[Record]):
    """Service for Record operations (JSONB hybrid model)"""

    def __init__(self):
        super().__init__(Record)

    async def create_record(
        self,
        db: AsyncSession,
        record_in: RecordCreate,
        user_id: str,
    ) -> Record:
        """
        Create new record with JSONB data.

        Example:
        record_in.data = {
            "fld_name": "Ali Yılmaz",
            "fld_email": "ali@example.com"
        }
        """
        # Generate primary_value from first text field
        primary_value = self._extract_primary_value(record_in.data)

        record_data = {
            "id": f"rec_{uuid.uuid4().hex[:8]}",
            "object_id": record_in.object_id,
            "data": record_in.data,
            "primary_value": primary_value,
            "created_by": user_id,
            "updated_by": user_id,
            "tenant_id": user_id,  # Multi-tenancy
        }
        return await self.create(db, record_data)

    async def get_records_by_object(
        self,
        db: AsyncSession,
        object_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Record], int]:
        """
        Get all records for an object with pagination.
        Returns: (records, total_count)
        """
        # Get total count
        count_result = await db.execute(
            select(func.count()).select_from(Record).where(Record.object_id == object_id)
        )
        total = count_result.scalar_one()

        # Get records
        result = await db.execute(
            select(Record)
            .where(Record.object_id == object_id)
            .offset(skip)
            .limit(limit)
            .order_by(Record.created_at.desc())
        )
        records = list(result.scalars().all())

        return records, total

    async def update_record(
        self,
        db: AsyncSession,
        record_id: str,
        record_in: RecordUpdate,
        user_id: str,
    ) -> Optional[Record]:
        """
        Update record's JSONB data.

        IMPORTANT: Merges data, doesn't replace!
        """
        record = await self.get_by_id(db, record_id)
        if not record:
            return None

        # Merge data (don't replace!)
        if record_in.data:
            record.data = {**record.data, **record_in.data}

        # Update primary_value
        record.primary_value = self._extract_primary_value(record.data)
        record.updated_by = user_id

        await db.commit()
        await db.refresh(record)
        return record

    async def search_records(
        self,
        db: AsyncSession,
        object_id: str,
        search_term: str,
    ) -> List[Record]:
        """
        Search records using primary_value (faster than JSONB search).
        For advanced JSONB search, use PostgreSQL full-text search.
        """
        result = await db.execute(
            select(Record)
            .where(
                Record.object_id == object_id,
                Record.primary_value.ilike(f"%{search_term}%")
            )
            .limit(50)
        )
        return list(result.scalars().all())

    def _extract_primary_value(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Extract primary value from JSONB data (first text-like field).
        Used for list views and search.
        """
        for key, value in data.items():
            if isinstance(value, str) and value.strip():
                return value[:255]  # Max 255 chars
        return None

# Singleton instance
record_service = RecordService()
```

---

### app/services/relationship_service.py
```python
"""Relationship Service - Relationship CRUD operations"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Relationship
from app.schemas import RelationshipCreate, RelationshipUpdate
from app.services.base import BaseService
import uuid

class RelationshipService(BaseService[Relationship]):
    """Service for Relationship operations"""

    def __init__(self):
        super().__init__(Relationship)

    async def create_relationship(
        self,
        db: AsyncSession,
        relationship_in: RelationshipCreate,
        user_id: str,
    ) -> Relationship:
        """Create new relationship with validation"""
        # TODO: Validate from_object_id and to_object_id exist

        relationship_data = relationship_in.model_dump()
        relationship_data["id"] = f"rel_{uuid.uuid4().hex[:8]}"
        relationship_data["created_by"] = user_id
        return await self.create(db, relationship_data)

    async def get_relationships_for_object(
        self,
        db: AsyncSession,
        object_id: str,
    ) -> List[Relationship]:
        """Get all relationships where object is source or target"""
        result = await db.execute(
            select(Relationship).where(
                (Relationship.from_object_id == object_id) |
                (Relationship.to_object_id == object_id)
            )
        )
        return list(result.scalars().all())

# Singleton instance
relationship_service = RelationshipService()
```

---

### app/services/relationship_record_service.py
```python
"""RelationshipRecord Service - Junction table CRUD"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import RelationshipRecord
from app.schemas import RelationshipRecordCreate
from app.services.base import BaseService
import uuid

class RelationshipRecordService(BaseService[RelationshipRecord]):
    """Service for RelationshipRecord operations"""

    def __init__(self):
        super().__init__(RelationshipRecord)

    async def create_link(
        self,
        db: AsyncSession,
        link_in: RelationshipRecordCreate,
        user_id: str,
    ) -> RelationshipRecord:
        """Create relationship between two records"""
        link_data = link_in.model_dump()
        link_data["id"] = f"lnk_{uuid.uuid4().hex[:8]}"
        link_data["created_by"] = user_id
        return await self.create(db, link_data)

    async def get_related_records(
        self,
        db: AsyncSession,
        record_id: str,
        relationship_id: str,
    ) -> List[RelationshipRecord]:
        """Get all related records via a specific relationship"""
        result = await db.execute(
            select(RelationshipRecord).where(
                RelationshipRecord.relationship_id == relationship_id,
                (
                    (RelationshipRecord.from_record_id == record_id) |
                    (RelationshipRecord.to_record_id == record_id)
                )
            )
        )
        return list(result.scalars().all())

# Singleton instance
relationship_record_service = RelationshipRecordService()
```

---

### app/services/application_service.py
```python
"""Application Service - Application CRUD operations"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Application
from app.schemas import ApplicationCreate, ApplicationUpdate
from app.services.base import BaseService
import uuid

class ApplicationService(BaseService[Application]):
    """Service for Application operations"""

    def __init__(self):
        super().__init__(Application)

    async def create_application(
        self,
        db: AsyncSession,
        app_in: ApplicationCreate,
        user_id: str,
    ) -> Application:
        """Create new application"""
        app_data = app_in.model_dump()
        app_data["id"] = f"app_{uuid.uuid4().hex[:8]}"
        app_data["created_by"] = user_id
        return await self.create(db, app_data)

    async def publish_application(
        self,
        db: AsyncSession,
        app_id: str,
    ) -> Optional[Application]:
        """Publish application (set published_at)"""
        from datetime import datetime

        app = await self.get_by_id(db, app_id)
        if not app:
            return None

        app.published_at = datetime.utcnow()
        await db.commit()
        await db.refresh(app)
        return app

# Singleton instance
application_service = ApplicationService()
```

---

## ✅ Başarı Kriterleri

Tamamlandığında şunlar olmalı:

- [ ] `app/services/` klasöründe 9 dosya (7 service + base + __init__)
- [ ] Her service `BaseService`'den inherit ediyor (DRY)
- [ ] Tüm metodlar async (`async def`)
- [ ] Type hints var (parameters, return types)
- [ ] UUID generation var (uuid4)
- [ ] user_id parametreleri var (multi-tenancy)
- [ ] Pagination support var (skip, limit)
- [ ] RecordService'de JSONB handling doğru

**Test:**
```python
# Python shell'de async test
import asyncio
from app.database import AsyncSessionLocal
from app.services import field_service
from app.schemas import FieldCreate

async def test():
    async with AsyncSessionLocal() as db:
        # Create field
        field_in = FieldCreate(
            name="email",
            label="Email Address",
            type="email",
            config={"validation": {"required": True}}
        )
        field = await field_service.create_field(db, field_in, user_id="user_123")
        print(f"Created: {field.id}")

        # Get field
        field = await field_service.get_by_id(db, field.id)
        print(f"Retrieved: {field.name}")

asyncio.run(test())
```

---

## 🐛 Troubleshooting

**Problem: AsyncSession not working**
- **Çözüm**: Tüm database calls'da `await` kullan:
  ```python
  result = await db.execute(select(Field))  # ✅
  result = db.execute(select(Field))        # ❌
  ```

**Problem: JSONB merge not working in record update**
- **Çözüm**: `{**dict1, **dict2}` spread operator kullan (Python 3.9+)

**Problem: UUID collision**
- **Çözüm**: UUID4 kullan (random), UUID1 değil (time-based)

---

## 📚 İlgili Dökümanlar

- `CLAUDE.md` - Service layer best practices
- `BACKEND_PROJECT_SPECIFICATION.md` - API endpoint specifications

---

**Sonraki Task:** `TASK-06-api-routers.md` (FastAPI endpoints)
