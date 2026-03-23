"""
Ticket Booking System - FastAPI Application

A complete ticket booking platform with:
- User authentication and profiles
- Event creation and management
- Ticket sales and verification
- Creator profiles
- User interests and recommendations
- Email notifications
- QR code generation

Main Components:
- api: API endpoints (auth, events, profiles, users)
- core: Core utilities (config, database, security)
- models: SQLAlchemy ORM models
- schema: Pydantic validation schemas
- service: Business logic layer
- repo: Data access repositories
- dependencies: Dependency injection

Entry Point:
    from app.main import app
    or
    python -m app.main
    or
    uvicorn main:app --reload
"""

__version__ = "2.0.0"
__author__ = "Development Team"

from app.main import app

__all__ = ["app"]
