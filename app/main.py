"""
Canvas App Backend - Main Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.routers import (
    auth,
    fields,
    objects,
    object_fields,
    records,
    relationships,
    relationship_records,
    applications,
)
from app.utils.rate_limit import limiter

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="REST API for Object-Centric No-Code Platform",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
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
