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

        # Auto-detect: PostgreSQL (PG_PATH or PG_HOST) > MySQL > SQLite
        if settings.PG_PATH or (settings.PG_HOST and settings.PG_USER):
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
            # Use PG_PATH if provided (for cloud platforms), otherwise build from components
            if settings.PG_PATH:
                # Force psycopg3 dialect, removing asyncpg or default mappings
                connection_string = settings.PG_PATH
                if connection_string.startswith("postgres://"):
                    connection_string = connection_string.replace("postgres://", "postgresql+psycopg://", 1)
                elif connection_string.startswith("postgresql://"):
                    connection_string = connection_string.replace("postgresql://", "postgresql+psycopg://", 1)
                elif connection_string.startswith("postgresql+asyncpg://"):
                    connection_string = connection_string.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
                return connection_string
            else:
                return (
                    f"postgresql+psycopg://{settings.PG_USER}:{settings.PG_PASSWORD}"
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

            # Auto-sync missing columns on existing tables
            logger.info("🔄 Checking and patching missing schema columns...")
            DatabaseInitializer._sync_schema_columns(engine, db_type)

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

    @staticmethod
    def _sync_schema_columns(engine, db_type: str):
        """
        Ensure missing columns defined in ORM models are automatically added to existing DB tables.
        """
        try:
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()

            with engine.begin() as conn:
                # 1. user_events table patches
                if "user_events" in existing_tables:
                    cols = {c["name"].lower(): c for c in inspector.get_columns("user_events")}

                    # ticket_code column
                    if "ticket_code" not in cols:
                        logger.info("➕ Patching table user_events: adding ticket_code column")
                        if db_type == "sqlite":
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN ticket_code VARCHAR(50)"))
                        elif db_type == "postgresql":
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN IF NOT EXISTS ticket_code VARCHAR(50)"))
                        else:
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN ticket_code VARCHAR(50)"))

                        # Backfill NULL ticket_code values for legacy rows
                        if db_type == "postgresql":
                            conn.execute(text(
                                "UPDATE user_events SET ticket_code = 'ECL-' || UPPER(SUBSTRING(MD5(id::text || clock_timestamp()::text) FROM 1 FOR 8)) WHERE ticket_code IS NULL"
                            ))
                        elif db_type == "mysql":
                            conn.execute(text(
                                "UPDATE user_events SET ticket_code = CONCAT('ECL-', UPPER(SUBSTRING(MD5(CONCAT(id, NOW())), 1, 8))) WHERE ticket_code IS NULL"
                            ))
                        elif db_type == "sqlite":
                            conn.execute(text(
                                "UPDATE user_events SET ticket_code = 'ECL-' || hex(randomblob(4)) WHERE ticket_code IS NULL"
                            ))

                    # ticket_type column
                    if "ticket_type" not in cols:
                        logger.info("➕ Patching table user_events: adding ticket_type column")
                        if db_type == "sqlite":
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN ticket_type VARCHAR(50)"))
                        elif db_type == "postgresql":
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN IF NOT EXISTS ticket_type VARCHAR(50)"))
                        else:
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN ticket_type VARCHAR(50)"))

                    # isVerified column (check case-insensitively)
                    if "isverified" not in cols:
                        logger.info("➕ Patching table user_events: adding isVerified column")
                        if db_type == "postgresql":
                            conn.execute(text('ALTER TABLE user_events ADD COLUMN IF NOT EXISTS "isVerified" BOOLEAN DEFAULT false NOT NULL'))
                        elif db_type == "mysql":
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN isVerified TINYINT(1) DEFAULT 0 NOT NULL"))
                        else:
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN isVerified INTEGER DEFAULT 0 NOT NULL"))

                    # verified_at column
                    if "verified_at" not in cols:
                        logger.info("➕ Patching table user_events: adding verified_at column")
                        if db_type == "postgresql":
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITHOUT TIME ZONE"))
                        elif db_type == "mysql":
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN verified_at DATETIME"))
                        else:
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN verified_at TIMESTAMP"))

                    # created_at column
                    if "created_at" not in cols:
                        logger.info("➕ Patching table user_events: adding created_at column")
                        if db_type == "postgresql":
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL"))
                        elif db_type == "mysql":
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL"))
                        else:
                            conn.execute(text("ALTER TABLE user_events ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL"))

                # 2. creatorprofile table patches
                if "creatorprofile" in existing_tables:
                    cols = {c["name"].lower(): c for c in inspector.get_columns("creatorprofile")}
                    if "bio" not in cols:
                        if db_type == "postgresql":
                            conn.execute(text("ALTER TABLE creatorprofile ADD COLUMN IF NOT EXISTS bio TEXT"))
                        else:
                            conn.execute(text("ALTER TABLE creatorprofile ADD COLUMN bio TEXT"))
                    if "profile_picture" not in cols:
                        if db_type == "postgresql":
                            conn.execute(text("ALTER TABLE creatorprofile ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500)"))
                        else:
                            conn.execute(text("ALTER TABLE creatorprofile ADD COLUMN profile_picture VARCHAR(500)"))

                # 3. userprofiles table patches
                if "userprofiles" in existing_tables:
                    cols = {c["name"].lower(): c for c in inspector.get_columns("userprofiles")}
                    if "profile_picture" not in cols:
                        if db_type == "postgresql":
                            conn.execute(text("ALTER TABLE userprofiles ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500)"))
                        else:
                            conn.execute(text("ALTER TABLE userprofiles ADD COLUMN profile_picture VARCHAR(500)"))

                # 4. table_categories table patches
                if "table_categories" in existing_tables:
                    cols = {c["name"].lower(): c for c in inspector.get_columns("table_categories")}
                    if "available_tables" not in cols:
                        if db_type == "postgresql":
                            conn.execute(text("ALTER TABLE table_categories ADD COLUMN IF NOT EXISTS available_tables INTEGER DEFAULT 0 NOT NULL"))
                        elif db_type == "mysql":
                            conn.execute(text("ALTER TABLE table_categories ADD COLUMN available_tables INT DEFAULT 0 NOT NULL"))
                        else:
                            conn.execute(text("ALTER TABLE table_categories ADD COLUMN available_tables INTEGER DEFAULT 0 NOT NULL"))

                # 5. user_credential table patches
                if "user_credential" in existing_tables:
                    cols = {c["name"].lower(): c for c in inspector.get_columns("user_credential")}
                    if "is_active" not in cols:
                        if db_type == "postgresql":
                            conn.execute(text("ALTER TABLE user_credential ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true NOT NULL"))
                        elif db_type == "mysql":
                            conn.execute(text("ALTER TABLE user_credential ADD COLUMN is_active TINYINT(1) DEFAULT 1 NOT NULL"))
                        else:
                            conn.execute(text("ALTER TABLE user_credential ADD COLUMN is_active INTEGER DEFAULT 1 NOT NULL"))

                # 6. eventcreation table patches
                if "eventcreation" in existing_tables:
                    cols = {c["name"].lower(): c for c in inspector.get_columns("eventcreation")}
                    if "is_active" not in cols:
                        if db_type == "postgresql":
                            conn.execute(text("ALTER TABLE eventcreation ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true NOT NULL"))
                        elif db_type == "mysql":
                            conn.execute(text("ALTER TABLE eventcreation ADD COLUMN is_active TINYINT(1) DEFAULT 1 NOT NULL"))
                        else:
                            conn.execute(text("ALTER TABLE eventcreation ADD COLUMN is_active INTEGER DEFAULT 1 NOT NULL"))

            logger.info("✅ Schema column synchronization complete.")
        except Exception as e:
            logger.warning(f"⚠️ Column schema sync warning: {str(e)}")





def main():
    """Main entry point"""
    logger.info("🚀 Starting Database Initialization...\n")
    success = DatabaseInitializer.initialize_database()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
