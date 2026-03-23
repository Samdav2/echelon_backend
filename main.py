"""
Main Entry Point - Wrapper for app.main

This module serves as the entry point for running the application.
It imports the FastAPI app from app.main for compatibility with
ASGI servers like Uvicorn.

Usage:
    uvicorn main:app --reload
    python main.py
"""

from app.main import app
from app.core.config import settings

# For direct execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
