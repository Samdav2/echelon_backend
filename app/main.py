"""
Ticket Booking System - Main Application Entry Point

This module initializes and configures the FastAPI application with all
necessary middleware, routes, and dependencies.

Run with:
    python -m app.main
    or
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import logging
from pathlib import Path
from datetime import datetime
from app.core.init_db import DatabaseInitializer

# Import routes
from app.api import auth, events, profile, user
from app.core.config import settings
from app.core.db_connector import DatabaseConnector
from app.models import CreatorProfile, TableCategory, UserCredential, EventCreation, UserEvent, UserProfile, UserInterest
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """

    # Initialize FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Professional Ticket Booking System API",
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    logger.info("=" * 80)
    logger.info(f"🚀 Initializing {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 80)

    # Setup CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("✅ CORS middleware configured")

    # Create uploads directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info(f"✅ Upload directory ready: {settings.UPLOAD_DIR}")

    # Mount static files for uploads
    if os.path.exists(settings.UPLOAD_DIR):
        app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
        logger.info("✅ Static files mounted at /uploads")

    # Include API routers
    logger.info("📝 Loading API routes...")
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(events.router, prefix="/event", tags=["Events"])
    app.include_router(profile.router, prefix="/profile", tags=["Profiles"])
    app.include_router(user.router, prefix="/user", tags=["Users"])
    logger.info("✅ All API routes loaded successfully")

    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Handle application startup"""
        logger.info("🔄 Running startup tasks...")
        try:
            # First initialize and optionally format/create the database tables
            db_init_success = DatabaseInitializer.initialize_database()
            if not db_init_success:
                logger.warning("⚠️ Database initialization returned false/errors, but continuing startup.")

            # Initialize database connection
            db = DatabaseConnector()
            db_info = db.get_db_info()
            logger.info("✅ Database connection initialized")
            logger.info(f"📊 Database Type: {db_info.get('database_type', 'unknown')}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {str(e)}")
            raise

        logger.info("✨ Application startup complete!")
        logger.info(f"📡 Server running at http://localhost:{settings.PORT}")
        logger.info(f"📚 API Documentation: http://localhost:{settings.PORT}/docs")
        logger.info("=" * 80)

    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Handle application shutdown"""
        logger.info("🛑 Running shutdown tasks...")
        logger.info("✅ Application shutdown complete")

    # Root endpoint
    @app.get("/", tags=["System"])
    async def root():
        """Root endpoint with API information"""
        return {
            "message": "Welcome to Ticket Booking System API",
            "version": settings.APP_VERSION,
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json"
            },
            "endpoints": {
                "auth": "/auth",
                "events": "/event",
                "profiles": "/profile",
                "users": "/user"
            }
        }

    # Health check endpoint
    @app.get("/health", tags=["System"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION
        }

    # API info endpoint
    @app.get("/api/info", tags=["System"])
    async def api_info():
        """Get API information"""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": "Professional Ticket Booking System",
            "database": {
                "host": settings.MYSQL_HOST,
                "port": settings.MYSQL_PORT,
                "database": settings.MYSQL_DATABASE
            },
            "features": [
                "User authentication",
                "Event management",
                "Ticket sales",
                "Creator profiles",
                "User interests",
                "Email notifications",
                "QR code generation",
                "Multi-tier pricing"
            ]
        }

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle uncaught exceptions"""
        logger.error(f"❌ Uncaught exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "detail": str(exc) if settings.DEBUG else "An error occurred"
            }
        )

    # 404 handler
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception):
        """Handle 404 errors"""
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Not found",
                "path": request.url.path
            }
        )

    logger.info("✅ Application configuration complete!")
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on http://0.0.0.0:{settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
