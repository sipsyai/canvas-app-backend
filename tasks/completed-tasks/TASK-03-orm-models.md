# TASK-03: SQLAlchemy ORM Models

**Phase:** 3/8
**Tahmini Süre:** 1.5 saat
**Bağımlılık:** Phase 2 (Database Migration) ✅
**Durum:** ⏳ Bekliyor

---

## 🎯 Görev Açıklaması

7 database tablosu için **async SQLAlchemy ORM modelleri** oluştur. Her model:
- Database tablosuna mapping yapmalı
- Type hints içermeli
- Relationships tanımlamalı
- Repr/str metodları olmalı

**ÖNEMLE:** `app/database.py`'deki `Base` sınıfından inherit etmeli.

---

## 📋 Ön Gereksinimler

- [x] Phase 2 tamamlandı (database migration uygulandı)
- [x] `app/database.py` mevcut ve `Base = declarative_base()` tanımlı
- [x] SQLAlchemy 2.0+ kurulu (`sqlalchemy[asyncio]`)

---

## 📁 Oluşturulacak Dosyalar

```
app/models/
├── __init__.py         # Model exports
├── field.py            # Field model
├── object.py           # Object model
├── object_field.py     # ObjectField model
├── record.py           # Record model
├── relationship.py     # Relationship model
├── relationship_record.py  # RelationshipRecord model
└── application.py      # Application model
```

---

## 🔧 Implementation

### app/models/__init__.py
```python
"""SQLAlchemy ORM Models"""
from app.models.field import Field
from app.models.object import Object
from app.models.object_field import ObjectField
from app.models.record import Record
from app.models.relationship import Relationship
from app.models.relationship_record import RelationshipRecord
from app.models.application import Application

__all__ = [
    "Field",
    "Object",
    "ObjectField",
    "Record",
    "Relationship",
    "RelationshipRecord",
    "Application",
]
```

---

### app/models/field.py
```python
"""Field Model - Master Field Library"""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class Field(Base):
    """
    Master field library containing both system (global) and custom fields.

    Examples:
    - System fields: created_by, created_at, owner
    - Custom fields: email, phone, company_name
    """
    __tablename__ = "fields"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Field Definition
    name = Column(String, nullable=False, unique=True)
    label = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'text', 'number', 'email', 'date', 'select', etc.
    description = Column(Text, nullable=True)

    # Configuration (validation, options, default_value, etc.)
    config = Column(JSONB, nullable=False, server_default='{}')

    # System/Custom Distinction
    is_global = Column(Boolean, nullable=False, default=False)  # System fields
    is_custom = Column(Boolean, nullable=False, default=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("auth.users.id"), nullable=True)

    # Relationships
    object_fields = relationship("ObjectField", back_populates="field", cascade="all, delete")

    def __repr__(self) -> str:
        return f"<Field(id={self.id}, name={self.name}, type={self.type})>"

    def to_dict(self) -> dict:
        """Convert to dictionary (useful for debugging)"""
        return {
            "id": self.id,
            "name": self.name,
            "label": self.label,
            "type": self.type,
            "config": self.config,
            "is_global": self.is_global,
            "is_custom": self.is_custom,
        }
```

---

### app/models/object.py
```python
"""Object Model - Object Definitions (Contact, Company, etc.)"""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Object(Base):
    """
    Object definitions (similar to Salesforce sObjects).

    Examples:
    - Contact (custom)
    - Company (custom)
    - Opportunity (custom)
    - User (system)
    """
    __tablename__ = "objects"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Object Definition
    name = Column(String, nullable=False)
    label = Column(String, nullable=False)
    plural_label = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)  # Emoji or icon class

    # System/Custom Distinction
    is_custom = Column(Boolean, nullable=False, default=True)
    is_global = Column(Boolean, nullable=False, default=False)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, ForeignKey("auth.users.id"), nullable=True)

    # Relationships
    object_fields = relationship("ObjectField", back_populates="object", cascade="all, delete-orphan")
    records = relationship("Record", back_populates="object", cascade="all, delete-orphan")
    relationships_from = relationship(
        "Relationship",
        foreign_keys="Relationship.from_object_id",
        back_populates="from_object",
        cascade="all, delete-orphan"
    )
    relationships_to = relationship(
        "Relationship",
        foreign_keys="Relationship.to_object_id",
        back_populates="to_object",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Object(id={self.id}, name={self.name}, label={self.label})>"
```

---

### app/models/object_field.py
```python
"""ObjectField Model - N:N Mapping between Objects and Fields"""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class ObjectField(Base):
    """
    N:N mapping table connecting objects to fields.

    Example:
    - Contact object has Email field
    - Contact object has Phone field
    - Company object has Email field (reused!)
    """
    __tablename__ = "object_fields"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Foreign Keys
    object_id = Column(String, ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String, ForeignKey("fields.id", ondelete="RESTRICT"), nullable=False)

    # Field Configuration
    display_order = Column(Integer, nullable=False, default=0)
    is_required = Column(Boolean, nullable=False, default=False)
    is_visible = Column(Boolean, nullable=False, default=True)
    is_readonly = Column(Boolean, nullable=False, default=False)

    # Field-specific overrides (override field.config for this object)
    field_overrides = Column(JSONB, nullable=False, server_default='{}')

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    object = relationship("Object", back_populates="object_fields")
    field = relationship("Field", back_populates="object_fields")

    def __repr__(self) -> str:
        return f"<ObjectField(object_id={self.object_id}, field_id={self.field_id})>"
```

---

### app/models/record.py
```python
"""Record Model - Dynamic Data Storage (JSONB Hybrid Pattern)"""
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class Record(Base):
    """
    Universal data storage using JSONB Hybrid Model.

    Example data:
    {
        "id": "rec_001",
        "object_id": "obj_contact",
        "data": {
            "fld_name": "Ali Yılmaz",
            "fld_email": "ali@example.com",
            "fld_phone": "+90 555 1234567"
        },
        "primary_value": "Ali Yılmaz"
    }
    """
    __tablename__ = "records"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Foreign Key
    object_id = Column(String, ForeignKey("objects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Dynamic Data (JSONB)
    data = Column(JSONB, nullable=False, server_default='{}')

    # Denormalized Primary Value (for performance - list views, search)
    primary_value = Column(Text, nullable=True, index=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, ForeignKey("auth.users.id"), nullable=True)
    updated_by = Column(String, ForeignKey("auth.users.id"), nullable=True)

    # Multi-tenancy (redundant check)
    tenant_id = Column(String, nullable=True)

    # Relationships
    object = relationship("Object", back_populates="records")
    relationship_records_from = relationship(
        "RelationshipRecord",
        foreign_keys="RelationshipRecord.from_record_id",
        back_populates="from_record",
        cascade="all, delete-orphan"
    )
    relationship_records_to = relationship(
        "RelationshipRecord",
        foreign_keys="RelationshipRecord.to_record_id",
        back_populates="to_record",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Record(id={self.id}, object_id={self.object_id}, primary_value={self.primary_value})>"

    def get_field_value(self, field_id: str) -> any:
        """Get specific field value from JSONB data"""
        return self.data.get(field_id)

    def set_field_value(self, field_id: str, value: any) -> None:
        """Set specific field value in JSONB data"""
        if self.data is None:
            self.data = {}
        self.data[field_id] = value
```

---

### app/models/relationship.py
```python
"""Relationship Model - Relationship Definitions"""
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Relationship(Base):
    """
    Defines relationships between objects.

    Examples:
    - Contact → Opportunities (1:N)
    - Contact ↔ Companies (N:N)
    - Opportunity → Contact (N:1)
    """
    __tablename__ = "relationships"

    # Primary Key
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # From/To Objects
    from_object_id = Column(String, ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    to_object_id = Column(String, ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)

    # Relationship Type
    type = Column(String, nullable=False)  # '1:N' or 'N:N'

    # Display Labels
    from_label = Column(Text, nullable=True)  # e.g., "Opportunities" on Contact page
    to_label = Column(Text, nullable=True)    # e.g., "Contact" on Opportunity page

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("auth.users.id"), nullable=True)

    # Relationships
    from_object = relationship("Object", foreign_keys=[from_object_id], back_populates="relationships_from")
    to_object = relationship("Object", foreign_keys=[to_object_id], back_populates="relationships_to")
    relationship_records = relationship("RelationshipRecord", back_populates="relationship", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Relationship(id={self.id}, from={self.from_object_id}, to={self.to_object_id}, type={self.type})>"
```

---

### app/models/relationship_record.py
```python
"""RelationshipRecord Model - N:N Junction Table"""
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class RelationshipRecord(Base):
    """
    Junction table for N:N relationships.

    Example:
    - Contact "Ali Yılmaz" is related to Opportunity "BigDeal 2024"
    - Metadata: {"role": "Decision Maker", "influence": "High"}
    """
    __tablename__ = "relationship_records"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Foreign Keys
    relationship_id = Column(String, ForeignKey("relationships.id", ondelete="CASCADE"), nullable=False, index=True)
    from_record_id = Column(String, ForeignKey("records.id", ondelete="CASCADE"), nullable=False, index=True)
    to_record_id = Column(String, ForeignKey("records.id", ondelete="CASCADE"), nullable=False, index=True)

    # Optional Metadata (e.g., role, start_date, etc.)
    metadata = Column(JSONB, nullable=False, server_default='{}')

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("auth.users.id"), nullable=True)

    # Relationships
    relationship = relationship("Relationship", back_populates="relationship_records")
    from_record = relationship("Record", foreign_keys=[from_record_id], back_populates="relationship_records_from")
    to_record = relationship("Record", foreign_keys=[to_record_id], back_populates="relationship_records_to")

    def __repr__(self) -> str:
        return f"<RelationshipRecord(from={self.from_record_id}, to={self.to_record_id})>"
```

---

### app/models/application.py
```python
"""Application Model - Application Containers (CRM, ITSM, etc.)"""
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

class Application(Base):
    """
    Application containers grouping multiple objects.

    Examples:
    - CRM (Contact, Company, Opportunity, Task)
    - ITSM (Ticket, Change Request, Configuration Item)
    """
    __tablename__ = "applications"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Application Definition
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)

    # Application Configuration (navigation, layout, permissions)
    config = Column(JSONB, nullable=False, server_default='{}')

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, ForeignKey("auth.users.id"), nullable=True)
    published_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, name={self.name})>"

    @property
    def is_published(self) -> bool:
        """Check if application is published"""
        return self.published_at is not None
```

---

## ✅ Başarı Kriterleri

Tamamlandığında şunlar olmalı:

- [ ] `app/models/` klasöründe 8 dosya (7 model + __init__.py)
- [ ] Her model `Base`'den inherit ediyor
- [ ] Tüm foreign key'ler tanımlı (ForeignKey(...))
- [ ] Relationship'ler doğru (`relationship(...)`, `back_populates`)
- [ ] CASCADE/RESTRICT davranışları doğru
- [ ] Type hints var (Column types, return types)
- [ ] `__repr__` metodları var
- [ ] `app/models/__init__.py`'da tüm modeller export ediliyor

**Test:**
```python
# Python shell'de
from app.models import Field, Object, Record
from app.database import Base

# Tüm modeller import edilebilmeli
print(Field.__tablename__)  # 'fields'
print(Object.__tablename__)  # 'objects'
print(Record.__tablename__)  # 'records'
```

---

## 🐛 Troubleshooting

**Problem: ImportError: cannot import name 'Base'**
- **Çözüm**: `app/database.py`'de `Base = declarative_base()` olduğundan emin ol

**Problem: Circular import between models**
- **Çözüm**: `relationship()` içinde string kullan: `relationship("Object", ...)` (class değil!)

**Problem: Type hint errors with relationships**
- **Çözüm**: `from __future__ import annotations` ekle dosya başına

---

## 📚 İlgili Dökümanlar

- `CLAUDE.md` - SQLAlchemy best practices
- `DATABASE_VISUAL_SCHEMA.md` - Tablo ilişkileri
- SQLAlchemy 2.0 docs: https://docs.sqlalchemy.org/en/20/

---

**Sonraki Task:** `TASK-04-pydantic-schemas.md` (Request/Response schemas)
