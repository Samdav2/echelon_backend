"""
Database Initialization Script

This script creates all database tables using SQLAlchemy ORM models.
It handles database creation and table initialization with proper error handling.

Supports multiple database backends:
- SQLite (development)
- MySQL (production)
- PostgreSQL (alternative production)

Usage:
    python app/core/init_db.py
"""

import os
import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Database initialization and management supporting multiple backends"""

    @staticmethod
    def get_database_type() -> str:
        """Detect which database type to use"""
        db_type = os.getenv("DB_TYPE", "").lower()

        if db_type in ["sqlite", "mysql", "postgresql"]:
            return db_type

        # Auto-detect: PostgreSQL > MySQL > SQLite
        if settings.PG_HOST and settings.PG_USER:
            return "postgresql"
        elif settings.MYSQL_HOST and settings.MYSQL_USER:
            return "mysql"
        else:
            return "sqlite"

    @staticmethod
    def get_connection_string() -> str:
        """Build database connection string for the selected database type"""
        db_type = DatabaseInitializer.get_database_type()

        if db_type == "sqlite":
            db_path = os.getenv("SQLITE_PATH", "data/ticket_booking.db")
            os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
            return f"sqlite:///{db_path}"

        elif db_type == "mysql":
            return (
                f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
                f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
            )

        elif db_type == "postgresql":
            return (
                f"postgresql://{settings.PG_USER}:{settings.PG_PASSWORD}"
                f"@{settings.PG_HOST}:{settings.PG_PORT or 5432}/{settings.PG_DATABASE}"
            )

    @staticmethod
    def initialize_database():
        """Initialize database and create all tables"""
        try:
            db_type = DatabaseInitializer.get_database_type()
            connection_string = DatabaseInitializer.get_connection_string()

            logger.info(f"🔧 Database Type: {db_type.upper()}")

            if db_type == "sqlite":
                logger.info(f"📁 SQLite Database: {os.getenv('SQLITE_PATH', 'data/ticket_booking.db')}")
            elif db_type == "mysql":
                logger.info(f"🔗 MySQL Database: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")
            elif db_type == "postgresql":
                logger.info(f"🔗 PostgreSQL Database: {settings.PG_HOST}:{settings.PG_PORT or 5432}/{settings.PG_DATABASE}")

            logger.info("📦 Creating database engine...")

            # Create engine with appropriate settings for each database type
            if db_type == "sqlite":
                engine = create_engine(
                    connection_string,
                    echo=False,
                    connect_args={"check_same_thread": False}
                )
            elif db_type == "mysql":
                engine = create_engine(
                    connection_string,
                    echo=False,
                    pool_pre_ping=True,
                    pool_size=5,
                    max_overflow=10
                )
            elif db_type == "postgresql":
                engine = create_engine(
                    connection_string,
                    echo=False,
                    pool_pre_ping=True,
                    pool_size=5,
                    max_overflow=10
                )

            # Test connection
            logger.info("✅ Testing database connection...")
            with engine.connect() as connection:
                if db_type == "postgresql":
                    connection.execute(text("SELECT 1"))
                elif db_type == "mysql":
                    connection.execute(text("SELECT 1"))
                logger.info("✅ Successfully connected to database")

            # Create all tables
            logger.info("📋 Creating database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created successfully")

            # Verify tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()

            if tables:
                logger.info(f"📊 Created tables: {', '.join(sorted(tables))}")

                # Display table information
                logger.info("\n📋 Table Schema:")
                for table_name in sorted(tables):
                    columns = inspector.get_columns(table_name)
                    logger.info(f"\n  ├─ Table: {table_name}")
                    for i, col in enumerate(columns):
                        is_last = i == len(columns) - 1
                        prefix = "└─" if is_last else "├─"
                        col_type = str(col['type'])
                        nullable = "NULL" if col['nullable'] else "NOT NULL"
                        logger.info(f"  │  {prefix} {col['name']}: {col_type} {nullable}")
            else:
                logger.warning("⚠️ No tables found after initialization")

            logger.info("\n✨ Database initialization completed successfully!")
            engine.dispose()
            return True

        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False




def main():
    """Main entry point"""
    logger.info("🚀 Starting Database Initialization...\n")
    success = DatabaseInitializer.initialize_database()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
