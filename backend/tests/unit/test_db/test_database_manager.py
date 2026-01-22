"""
Database abstraction layer tests - TDD Fourth Cycle
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestDatabaseManager:
    """Test database manager for connection pooling and abstraction"""

    def test_database_manager_exists(self):
        """DatabaseManager class should exist"""
        from app.db.session import DatabaseManager
        assert DatabaseManager is not None

    def test_database_manager_has_init_method(self):
        """DatabaseManager should have init method"""
        from app.db.session import db_manager

        assert hasattr(db_manager, "init")
        assert callable(db_manager.init)

    def test_database_manager_has_get_session_method(self):
        """DatabaseManager should have get_session method"""
        from app.db.session import db_manager

        assert hasattr(db_manager, "get_session")

    def test_database_manager_has_close_method(self):
        """DatabaseManager should have close method"""
        from app.db.session import db_manager

        assert hasattr(db_manager, "close")
        assert callable(db_manager.close)

    @pytest.mark.asyncio
    async def test_database_manager_creates_engine(self):
        """DatabaseManager should create an engine"""
        from app.db.session import DatabaseManager

        manager = DatabaseManager()
        manager.init("sqlite+aiosqlite:///:memory:")

        assert manager.engine is not None
        await manager.close()

    @pytest.mark.asyncio
    async def test_database_manager_creates_session_factory(self):
        """DatabaseManager should create a session factory"""
        from app.db.session import DatabaseManager

        manager = DatabaseManager()
        manager.init("sqlite+aiosqlite:///:memory:")

        assert manager.session_factory is not None
        await manager.close()


class TestDatabaseURLParsing:
    """Test database URL parsing for different databases"""

    def test_supports_sqlite_url(self):
        """Should support SQLite URLs"""
        from app.db.session import DatabaseManager

        manager = DatabaseManager()
        # Should not raise
        manager.init("sqlite+aiosqlite:///data/test.db")

        assert manager.engine is not None
        # Check URL dialect
        assert "sqlite" in str(manager.engine.url)

    @pytest.mark.skipif(
        __import__("importlib").util.find_spec("asyncpg") is None,
        reason="asyncpg not installed"
    )
    def test_supports_postgresql_url(self):
        """Should support PostgreSQL URLs"""
        from app.db.session import DatabaseManager

        manager = DatabaseManager()
        # Should not raise
        manager.init("postgresql+asyncpg://user:pass@localhost/db")

        assert manager.engine is not None
        # Check URL dialect
        assert "postgresql" in str(manager.engine.url)
