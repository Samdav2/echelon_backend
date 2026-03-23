from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application configuration settings"""

    # Server
    APP_NAME: str = "Ticket Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", "5000"))

    # Database - MySQL
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "ticket_db")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))

    # Database - PostgreSQL (optional)
    # Can use either PG_PATH (full connection string) OR individual components
    PG_PATH: Optional[str] = os.getenv("PG_PATH")  # e.g., "postgresql://user:pass@host:5432/database"
    PG_HOST: Optional[str] = os.getenv("PG_HOST")
    PG_USER: Optional[str] = os.getenv("PG_USER")
    PG_PASSWORD: Optional[str] = os.getenv("PG_PASSWORD")
    PG_DATABASE: Optional[str] = os.getenv("PG_DATABASE")
    PG_PORT: Optional[int] = int(os.getenv("PG_PORT", "5432")) if os.getenv("PG_PORT") else None

    # Database - SQLite (development)
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "data/ticket_booking.db")

    # Database Type Selection
    # Valid values: "sqlite", "mysql", "postgresql"
    # If not set, auto-detects based on available config (PostgreSQL > MySQL > SQLite)
    DB_TYPE: Optional[str] = os.getenv("DB_TYPE", "").lower() or None

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    VERIFICATION_CODE_EXPIRY: int = 5 * 60  # 5 minutes in seconds

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "https://echelontix.com.ng"
        "http://echelontix.com.ng/"
        "https://www.echelontix.com.ng"
    ]

    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 9 * 1024 * 1024  # 9MB

    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@example.com")

    # Mailjet
    MAILJET_API_KEY: str = os.getenv("MAILJET_API_KEY", "")
    MAILJET_API_SECRET: str = os.getenv("MAILJET_API_SECRET", "")

    # Cache
    CACHE_TTL: int = 300  # Cache time-to-live in seconds

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

    class Config:
        case_sensitive = True

settings = Settings()
