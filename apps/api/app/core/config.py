import os
from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "PDF Pride API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database: Supports SQLite (for easy local dev) and PostgreSQL (for production)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./pdfpride.db"
    )

    # Redis broker for Celery and state cache
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Storage settings
    STORAGE_DRIVER: str = os.getenv("STORAGE_DRIVER", "local")  # 'local' or 's3'
    LOCAL_STORAGE_DIR: str = os.getenv(
        "LOCAL_STORAGE_DIR", 
        str(Path(__file__).resolve().parent.parent.parent / "storage_data")
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "pdfpride_insecure_dev_secret_key_change_in_production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3100",
        "http://127.0.0.1:3100",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
