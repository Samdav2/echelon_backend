"""
Universal Database Connection Manager

Supports multiple database backends:
- SQLite (development/testing)
- MySQL (production)
- PostgreSQL (alternative production)

Automatically selects the appropriate driver based on configuration.
"""

import os
import logging
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any
from enum import Enum

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types"""
    SQLITE = "sqlite"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"


class DatabaseConnector:
    """Universal database connector supporting multiple backends"""

    _instance: Optional['DatabaseConnector'] = None
    _db_type: Optional[DatabaseType] = None
    _pool: Optional[Any] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the appropriate database connector"""
        if self._pool is None:
            self._detect_database_type()
            self._initialize_pool()

    @staticmethod
    def _detect_database_type() -> DatabaseType:
        """Detect which database to use based on configuration"""
        # Priority: Explicit setting > PostgreSQL (PG_PATH or components) > MySQL > SQLite

        db_type = os.getenv("DB_TYPE", "").lower()
        if db_type in ["sqlite", "mysql", "postgresql", "postgres"]:
            if db_type == "postgres":
                db_type = "postgresql"
            DatabaseConnector._db_type = DatabaseType(db_type)
            logger.info(f"Using explicitly configured database: {db_type}")
            return DatabaseConnector._db_type

        # Check PostgreSQL config (PG_PATH takes priority)
        if settings.PG_PATH or (settings.PG_HOST and settings.PG_USER):
            DatabaseConnector._db_type = DatabaseType.POSTGRESQL
            logger.info("Auto-detected PostgreSQL configuration")
            return DatabaseConnector._db_type

        # Check MySQL config
        if settings.MYSQL_HOST and settings.MYSQL_USER:
            DatabaseConnector._db_type = DatabaseType.MYSQL
            logger.info("Auto-detected MySQL configuration")
            return DatabaseConnector._db_type

        # Default to SQLite
        DatabaseConnector._db_type = DatabaseType.SQLITE
        logger.info("Using SQLite (default/development)")
        return DatabaseConnector._db_type

    @staticmethod
    def _initialize_pool():
        """Initialize connection pool for detected database type"""
        db_type = DatabaseConnector._db_type

        try:
            if db_type == DatabaseType.SQLITE:
                DatabaseConnector._initialize_sqlite()
            elif db_type == DatabaseType.MYSQL:
                DatabaseConnector._initialize_mysql()
            elif db_type == DatabaseType.POSTGRESQL:
                DatabaseConnector._initialize_postgresql()
        except Exception as e:
            logger.error(f"Failed to initialize {db_type.value} database: {e}")
            raise

    @staticmethod
    def _initialize_sqlite():
        """Initialize SQLite connection"""
        import sqlite3

        db_path = os.getenv("SQLITE_PATH", "data/ticket_booking.db")

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)

        # Create connection (SQLite doesn't use connection pooling)
        try:
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            logger.info(f"✓ Connected to SQLite database at {db_path}")
            DatabaseConnector._pool = conn
        except sqlite3.Error as e:
            logger.error(f"✗ Failed to connect to SQLite: {e}")
            raise

    @staticmethod
    def _initialize_mysql():
        """Initialize MySQL connection pool"""
        try:
            import mysql.connector
            from mysql.connector import pooling
        except ImportError:
            raise ImportError("mysql-connector-python not installed. Run: pip install mysql-connector-python")

        try:
            pool = pooling.MySQLConnectionPool(
                pool_name="ticket_pool",
                pool_size=5,
                pool_reset_session=True,
                host=settings.MYSQL_HOST,
                database=settings.MYSQL_DATABASE,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                port=settings.MYSQL_PORT,
                autocommit=False
            )
            logger.info(f"✓ Connected to MySQL at {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")
            DatabaseConnector._pool = pool
        except Exception as e:
            logger.error(f"✗ Failed to connect to MySQL: {e}")
            raise

    @staticmethod
    def _initialize_postgresql():
        """Initialize PostgreSQL connection pool using psycopg (v3)"""
        try:
            import psycopg
            from psycopg import pool as pg_pool_module
        except ImportError:
            raise ImportError("psycopg[binary] not installed. Run: pip install 'psycopg[binary]'")

        try:
            # Parse PG_PATH if provided (e.g., postgresql://user:pass@host:5432/database)
            pg_host = settings.PG_HOST
            pg_user = settings.PG_USER
            pg_password = settings.PG_PASSWORD
            pg_database = settings.PG_DATABASE
            pg_port = settings.PG_PORT or 5432

            if settings.PG_PATH:
                # Use PG_PATH directly - psycopg3 handles connection strings natively
                conninfo = settings.PG_PATH
                logger.info(f"Using PG_PATH connection string")
            else:
                # Build connection string from individual components
                conninfo = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
                logger.info(f"Built connection string: postgresql://{pg_user}:***@{pg_host}:{pg_port}/{pg_database}")

            # Create connection pool
            pg_pool = pg_pool_module.ConnectionPool(
                conninfo,
                min_size=1,
                max_size=10,
                timeout=30,
                check=pg_pool_module.check_connection
            )
            logger.info(f"✓ Connected to PostgreSQL")
            DatabaseConnector._pool = pg_pool
        except Exception as e:
            logger.error(f"✗ Failed to connect to PostgreSQL: {e}")
            raise

    def get_connection(self):
        """Get a database connection"""
        if self._db_type == DatabaseType.SQLITE:
            return self._pool
        elif self._db_type == DatabaseType.MYSQL:
            return self._pool.get_connection()
        elif self._db_type == DatabaseType.POSTGRESQL:
            # psycopg3 pool.getconn() method
            return self._pool.getconn()

    def return_connection(self, conn):
        """Return connection to pool (for PostgreSQL)"""
        if self._db_type == DatabaseType.POSTGRESQL:
            # psycopg3 pool.putconn() method
            self._pool.putconn(conn)
        # MySQL and SQLite don't need explicit return

    @contextmanager
    def get_db_context(self):
        """Context manager for database connections"""
        conn = self.get_connection()
        try:
            yield conn
        finally:
            if self._db_type == DatabaseType.SQLITE:
                conn.close()
            elif self._db_type == DatabaseType.MYSQL:
                conn.close()
            elif self._db_type == DatabaseType.POSTGRESQL:
                self.return_connection(conn)

    def execute_query(self, query: str, params: tuple = (), fetch_one: bool = False):
        """
        Execute SELECT query

        Args:
            query: SQL query string
            params: Query parameters tuple
            fetch_one: If True, return first row; if False, return all rows

        Returns:
            Single row dict or list of row dicts
        """
        with self.get_db_context() as conn:
            if self._db_type == DatabaseType.SQLITE:
                cursor = conn.cursor()
                # Convert MySQL-style %s placeholders to SQLite-style ?
                sqlite_query = query.replace('%s', '?')
                cursor.execute(sqlite_query, params)
                rows = cursor.fetchone() if fetch_one else cursor.fetchall()
                cursor.close()
                # Convert sqlite3.Row to dict
                if fetch_one and rows:
                    return dict(rows)
                elif not fetch_one:
                    return [dict(row) for row in rows]
                return rows

            elif self._db_type == DatabaseType.MYSQL:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params)
                result = cursor.fetchone() if fetch_one else cursor.fetchall()
                cursor.close()
                return result

            elif self._db_type == DatabaseType.POSTGRESQL:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if fetch_one:
                    row = cursor.fetchone()
                    cursor.close()
                    if row:
                        # Get column names from cursor description
                        cols = [desc[0] for desc in cursor.description]
                        return dict(zip(cols, row))
                    return None
                else:
                    rows = cursor.fetchall()
                    cols = [desc[0] for desc in cursor.description]
                    cursor.close()
                    return [dict(zip(cols, row)) for row in rows]

    def execute_insert_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute INSERT, UPDATE, or DELETE query

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            Number of rows affected
        """
        with self.get_db_context() as conn:
            try:
                if self._db_type == DatabaseType.SQLITE:
                    cursor = conn.cursor()
                    # Convert MySQL-style %s placeholders to SQLite-style ?
                    sqlite_query = query.replace('%s', '?')
                    cursor.execute(sqlite_query, params)
                    conn.commit()
                    rows_affected = cursor.rowcount
                    cursor.close()
                    return rows_affected

                elif self._db_type == DatabaseType.MYSQL:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    conn.commit()
                    rows_affected = cursor.rowcount
                    cursor.close()
                    return rows_affected

                elif self._db_type == DatabaseType.POSTGRESQL:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    conn.commit()
                    rows_affected = cursor.rowcount
                    cursor.close()
                    return rows_affected

            except Exception as e:
                conn.rollback()
                logger.error(f"Database error during insert/update: {e}")
                raise

    def get_db_type(self) -> DatabaseType:
        """Get the current database type"""
        return self._db_type

    def get_db_info(self) -> Dict[str, Any]:
        """Get information about the current database"""
        db_type = self._db_type

        info = {
            "database_type": db_type.value,
            "connected": self._pool is not None
        }

        if db_type == DatabaseType.SQLITE:
            info["path"] = os.getenv("SQLITE_PATH", "data/ticket_booking.db")
        elif db_type == DatabaseType.MYSQL:
            info["host"] = settings.MYSQL_HOST
            info["port"] = settings.MYSQL_PORT
            info["database"] = settings.MYSQL_DATABASE
        elif db_type == DatabaseType.POSTGRESQL:
            info["host"] = settings.PG_HOST
            info["port"] = settings.PG_PORT or 5432
            info["database"] = settings.PG_DATABASE

        return info


# Singleton instance
db = DatabaseConnector()


async def get_db():
    """FastAPI dependency - returns database connection"""
    conn = db.get_connection()
    try:
        yield conn
    finally:
        db.return_connection(conn) if db.get_db_type() == DatabaseType.POSTGRESQL else None
