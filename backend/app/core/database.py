"""
Database initialization and session management

DEPRECATED: This module is deprecated. Use app.db.session instead.
This file is kept for backward compatibility and will be removed in future versions.
"""
import warnings

# Re-export from new location for backward compatibility
from app.db.session import db_manager, get_db, init_database, close_database, DatabaseManager
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager


# For backward compatibility, recreate get_db_context
@asynccontextmanager
async def get_db_context():
    """Get database session as context manager (backward compatibility wrapper)"""
    async with db_manager.get_session() as session:
        yield session


__all__ = [
    "db_manager",
    "get_db",
    "get_db_context",
    "init_database",
    "close_database",
    "DatabaseManager",
    "AsyncSession",
]
