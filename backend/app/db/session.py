"""
Database session management with support for SQLite and PostgreSQL
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


class DatabaseManager:
    """
    Database connection manager supporting multiple database backends

    Supports:
    - SQLite: sqlite+aiosqlite:///path/to/database.db
    - PostgreSQL: postgresql+asyncpg://user:pass@host:port/database
    """

    def __init__(self):
        self.engine = None
        self.session_factory = None

    def init(self, database_url: str = None) -> None:
        """
        Initialize database engine and session factory

        Args:
            database_url: Database connection URL. If None, uses settings.DATABASE_URL
        """
        if database_url is None:
            database_url = settings.DATABASE_URL

        # Determine pool settings based on database type
        is_postgres = "postgresql" in database_url

        # Build engine kwargs - SQLite doesn't support pool settings
        engine_kwargs = {
            "echo": False,  # Set to True for SQL query logging
            "pool_pre_ping": True,  # Verify connections before using
        }

        # Only add pool settings for PostgreSQL
        if is_postgres:
            engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
            engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW

        # Create engine
        self.engine = create_async_engine(database_url, **engine_kwargs)

        # Create session factory
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session with automatic transaction management

        Yields:
            AsyncSession: Database session

        Example:
            async with db_manager.get_session() as session:
                await session.execute(query)
        """
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """Close all database connections"""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None

    async def init_db(self) -> None:
        """Initialize database tables"""
        from app.models.database import Base

        if self.engine:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection function for getting database sessions

    Use in FastAPI endpoints:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with db_manager.get_session() as session:
        yield session


async def init_database(database_url: str = None) -> None:
    """
    Initialize database connection and create tables

    Args:
        database_url: Optional database URL override
    """
    db_manager.init(database_url)
    await db_manager.init_db()


async def close_database() -> None:
    """Close database connections"""
    await db_manager.close()
