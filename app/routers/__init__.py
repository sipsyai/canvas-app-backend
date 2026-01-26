"""FastAPI Routers"""
from app.routers import (
    applications,
    auth,
    dashboard,
    fields,
    object_fields,
    objects,
    records,
    relationship_records,
    relationships,
)

__all__ = [
    "applications",
    "auth",
    "dashboard",
    "fields",
    "objects",
    "object_fields",
    "records",
    "relationships",
    "relationship_records",
]
