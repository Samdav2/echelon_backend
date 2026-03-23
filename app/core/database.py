"""
Legacy Database Module (Wrapper for backward compatibility)

This module maintains backward compatibility with existing code that imports from
app.core.database. New code should import from app.core.db_connector instead.

The new multi-database connector supports:
- SQLite (development)
- MySQL (production)
- PostgreSQL (alternative production)
"""

from app.core.db_connector import (
    DatabaseConnector,
    DatabaseType,
    db,
    get_db
)

# Re-export for backward compatibility
__all__ = ['DatabaseConnector', 'DatabaseType', 'db', 'get_db']
