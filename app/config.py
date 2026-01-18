"""
Canvas App Backend - Configuration
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Canvas App API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    
    # Docs
    ENABLE_DOCS: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

settings = Settings()
