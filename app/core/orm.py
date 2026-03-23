"""SQLAlchemy ORM session management.

Provides a shared engine and session factory for using the
SQLAlchemy models (e.g., `UserCredential`) at runtime.
"""

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.init_db import DatabaseInitializer

# Build engine using the same logic as database initialization
_db_type = DatabaseInitializer.get_database_type()
_connection_string = DatabaseInitializer.get_connection_string()

if _db_type == "sqlite":
    engine = create_engine(
        _connection_string,
        echo=False,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        _connection_string,
        echo=False,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_session() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
