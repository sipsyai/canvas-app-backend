# TASK-04: Pydantic Request/Response Schemas

**Phase:** 4/8
**Tahmini Süre:** 1 saat
**Bağımlılık:** Phase 3 (ORM Models) ✅
**Durum:** ⏳ Bekliyor

---

## 🎯 Görev Açıklaması

Her ORM modeli için **Pydantic schemas** oluştur. Bu schemas:
- API request/response validation için kullanılacak
- ORM modellerini direkt expose etmemek için
- Type safety sağlamak için
- Auto-generated OpenAPI docs için

**ÖNEMLE:** `pydantic.BaseModel` kullan, ORM modellerini direkt döndürme!

---

## 📋 Ön Gereksinimler

- [x] Phase 3 tamamlandı (ORM models mevcut)
- [x] Pydantic 2.5+ kurulu
- [x] `app/models/` klasörü hazır

---

## 📁 Oluşturulacak Dosyalar

```
app/schemas/
├── __init__.py           # Schema exports
├── field.py              # Field schemas
├── object.py             # Object schemas
├── object_field.py       # ObjectField schemas
├── record.py             # Record schemas
├── relationship.py       # Relationship schemas
├── relationship_record.py  # RelationshipRecord schemas
└── application.py        # Application schemas
```

---

## 🎨 Schema Naming Convention

Her model için 3 tip schema oluştur:

1. **`{Model}Create`** - Create endpoint için (POST)
   - ID yok (otomatik generate edilir)
   - created_at/updated_at yok
   - created_by backend'de set edilir

2. **`{Model}Update`** - Update endpoint için (PATCH)
   - Tüm fieldlar optional
   - Sadece değiştirmek istenen fieldlar gönderilir

3. **`{Model}Response`** - API response için (GET)
   - Tüm fieldlar var
   - ID, timestamps dahil
   - ORM → Pydantic conversion (orm_mode/from_attributes)

---

## 🔧 Implementation

### app/schemas/__init__.py
```python
"""Pydantic Schemas for Request/Response Validation"""
from app.schemas.field import FieldCreate, FieldUpdate, FieldResponse
from app.schemas.object import ObjectCreate, ObjectUpdate, ObjectResponse
from app.schemas.object_field import ObjectFieldCreate, ObjectFieldUpdate, ObjectFieldResponse
from app.schemas.record import RecordCreate, RecordUpdate, RecordResponse
from app.schemas.relationship import RelationshipCreate, RelationshipUpdate, RelationshipResponse
from app.schemas.relationship_record import (
    RelationshipRecordCreate,
    RelationshipRecordUpdate,
    RelationshipRecordResponse,
)
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse

__all__ = [
    "FieldCreate",
    "FieldUpdate",
    "FieldResponse",
    "ObjectCreate",
    "ObjectUpdate",
    "ObjectResponse",
    "ObjectFieldCreate",
    "ObjectFieldUpdate",
    "ObjectFieldResponse",
    "RecordCreate",
    "RecordUpdate",
    "RecordResponse",
    "RelationshipCreate",
    "RelationshipUpdate",
    "RelationshipResponse",
    "RelationshipRecordCreate",
    "RelationshipRecordUpdate",
    "RelationshipRecordResponse",
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationResponse",
]
```

---

### app/schemas/field.py
```python
"""Field Schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class FieldBase(BaseModel):
    """Base schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Unique field name (snake_case)")
    label: str = Field(..., min_length=1, max_length=255, description="Display label")
    type: str = Field(..., description="Field type: text, number, email, date, select, etc.")
    description: Optional[str] = Field(None, description="Field description")
    config: dict = Field(default_factory=dict, description="Field configuration (validation, options, etc.)")

class FieldCreate(FieldBase):
    """Schema for creating a new field"""
    is_custom: bool = Field(default=True, description="Custom field (vs system field)")

class FieldUpdate(BaseModel):
    """Schema for updating a field (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    label: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None

class FieldResponse(FieldBase):
    """Schema for field response"""
    id: str
    is_global: bool
    is_custom: bool
    created_at: datetime
    created_by: Optional[str] = None

    model_config = {"from_attributes": True}  # Pydantic 2.x (was orm_mode in v1)
```

---

### app/schemas/object.py
```python
"""Object Schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ObjectBase(BaseModel):
    """Base schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Object name (snake_case)")
    label: str = Field(..., min_length=1, max_length=255, description="Display label")
    plural_label: str = Field(..., min_length=1, max_length=255, description="Plural label")
    description: Optional[str] = Field(None, description="Object description")
    icon: Optional[str] = Field(None, description="Icon (emoji or class)")

class ObjectCreate(ObjectBase):
    """Schema for creating a new object"""
    pass

class ObjectUpdate(BaseModel):
    """Schema for updating an object (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    label: Optional[str] = Field(None, min_length=1, max_length=255)
    plural_label: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None

class ObjectResponse(ObjectBase):
    """Schema for object response"""
    id: str
    is_custom: bool
    is_global: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    model_config = {"from_attributes": True}
```

---

### app/schemas/object_field.py
```python
"""ObjectField Schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ObjectFieldBase(BaseModel):
    """Base schema with common fields"""
    object_id: str = Field(..., description="Object ID")
    field_id: str = Field(..., description="Field ID")
    display_order: int = Field(default=0, ge=0, description="Display order (0-based)")
    is_required: bool = Field(default=False, description="Is field required?")
    is_visible: bool = Field(default=True, description="Is field visible?")
    is_readonly: bool = Field(default=False, description="Is field read-only?")
    field_overrides: dict = Field(default_factory=dict, description="Field-specific config overrides")

class ObjectFieldCreate(ObjectFieldBase):
    """Schema for adding a field to an object"""
    pass

class ObjectFieldUpdate(BaseModel):
    """Schema for updating object-field mapping (all fields optional)"""
    display_order: Optional[int] = Field(None, ge=0)
    is_required: Optional[bool] = None
    is_visible: Optional[bool] = None
    is_readonly: Optional[bool] = None
    field_overrides: Optional[dict] = None

class ObjectFieldResponse(ObjectFieldBase):
    """Schema for object-field response"""
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

---

### app/schemas/record.py
```python
"""Record Schemas"""
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class RecordBase(BaseModel):
    """Base schema with common fields"""
    object_id: str = Field(..., description="Object ID this record belongs to")
    data: Dict[str, Any] = Field(..., description="Dynamic field data (JSONB)")

class RecordCreate(RecordBase):
    """Schema for creating a new record"""
    pass

class RecordUpdate(BaseModel):
    """Schema for updating a record (all fields optional)"""
    data: Optional[Dict[str, Any]] = Field(None, description="Updated field data")

class RecordResponse(RecordBase):
    """Schema for record response"""
    id: str
    primary_value: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    tenant_id: Optional[str] = None

    model_config = {"from_attributes": True}

class RecordListResponse(BaseModel):
    """Schema for paginated record list"""
    total: int = Field(..., description="Total record count")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Records per page")
    records: list[RecordResponse] = Field(..., description="List of records")
```

---

### app/schemas/relationship.py
```python
"""Relationship Schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class RelationshipBase(BaseModel):
    """Base schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Relationship name")
    from_object_id: str = Field(..., description="Source object ID")
    to_object_id: str = Field(..., description="Target object ID")
    type: str = Field(..., regex="^(1:N|N:N)$", description="Relationship type: 1:N or N:N")
    from_label: Optional[str] = Field(None, description="Label shown on 'from' object")
    to_label: Optional[str] = Field(None, description="Label shown on 'to' object")

class RelationshipCreate(RelationshipBase):
    """Schema for creating a new relationship"""
    pass

class RelationshipUpdate(BaseModel):
    """Schema for updating a relationship (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    from_label: Optional[str] = None
    to_label: Optional[str] = None

class RelationshipResponse(RelationshipBase):
    """Schema for relationship response"""
    id: str
    created_at: datetime
    created_by: Optional[str] = None

    model_config = {"from_attributes": True}
```

---

### app/schemas/relationship_record.py
```python
"""RelationshipRecord Schemas"""
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class RelationshipRecordBase(BaseModel):
    """Base schema with common fields"""
    relationship_id: str = Field(..., description="Relationship ID")
    from_record_id: str = Field(..., description="Source record ID")
    to_record_id: str = Field(..., description="Target record ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional relationship metadata")

class RelationshipRecordCreate(RelationshipRecordBase):
    """Schema for creating a relationship between records"""
    pass

class RelationshipRecordUpdate(BaseModel):
    """Schema for updating relationship metadata"""
    metadata: Optional[Dict[str, Any]] = None

class RelationshipRecordResponse(RelationshipRecordBase):
    """Schema for relationship record response"""
    id: str
    created_at: datetime
    created_by: Optional[str] = None

    model_config = {"from_attributes": True}
```

---

### app/schemas/application.py
```python
"""Application Schemas"""
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ApplicationBase(BaseModel):
    """Base schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Application name")
    description: Optional[str] = Field(None, description="Application description")
    icon: Optional[str] = Field(None, description="Icon (emoji or class)")
    config: Dict[str, Any] = Field(default_factory=dict, description="Application configuration")

class ApplicationCreate(ApplicationBase):
    """Schema for creating a new application"""
    pass

class ApplicationUpdate(BaseModel):
    """Schema for updating an application (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class ApplicationResponse(ApplicationBase):
    """Schema for application response"""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    published_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @property
    def is_published(self) -> bool:
        """Check if application is published"""
        return self.published_at is not None
```

---

## ✅ Başarı Kriterleri

Tamamlandığında şunlar olmalı:

- [ ] `app/schemas/` klasöründe 8 dosya (7 schema + __init__.py)
- [ ] Her model için 3 schema var (Create, Update, Response)
- [ ] Response schemas `model_config = {"from_attributes": True}` içeriyor
- [ ] Field validation var (`Field(...)`, `min_length`, `max_length`, `ge`, `le`)
- [ ] Type hints doğru (Optional[], Dict[], list[])
- [ ] Pydantic v2 syntax kullanılmış (from_attributes, not orm_mode)

**Test:**
```python
# Python shell'de
from app.schemas import FieldCreate, FieldResponse

# Create schema validation
field_data = {
    "name": "email",
    "label": "Email Address",
    "type": "email",
    "config": {"validation": {"regex": ".*@.*"}}
}
field_create = FieldCreate(**field_data)
print(field_create.model_dump())  # Pydantic v2 (was .dict() in v1)

# Response schema from ORM
from app.models import Field
from app.database import AsyncSessionLocal

async with AsyncSessionLocal() as db:
    field_orm = Field(
        id="fld_001",
        name="email",
        label="Email",
        type="email",
        is_global=False,
        is_custom=True
    )
    field_response = FieldResponse.model_validate(field_orm)  # Pydantic v2
    print(field_response.model_dump_json())  # JSON response
```

---

## 🐛 Troubleshooting

**Problem: ValidationError when creating schema from ORM**
- **Çözüm**: `model_config = {"from_attributes": True}` ekle (Pydantic v2)

**Problem: Field default values not working**
- **Çözüm**: `Field(default=...)` veya `Field(default_factory=dict)` kullan

**Problem: Optional fields showing as required**
- **Çözüm**: `Optional[str] = None` şeklinde tanımla (None default değer)

**Problem: Pydantic v1 syntax errors (orm_mode not recognized)**
- **Çözüm**: Pydantic v2 syntax kullan:
  - `orm_mode = True` → `model_config = {"from_attributes": True}`
  - `.dict()` → `.model_dump()`
  - `.json()` → `.model_dump_json()`

---

## 📚 İlgili Dökümanlar

- `CLAUDE.md` - Pydantic best practices
- Pydantic v2 docs: https://docs.pydantic.dev/2.0/
- FastAPI validation: https://fastapi.tiangolo.com/tutorial/body/

---

**Sonraki Task:** `TASK-05-business-services.md` (Business logic layer)
