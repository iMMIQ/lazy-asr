"""
Unified Database Layer Tests - TDD for Refactoring
These tests define the expected behavior of the unified database layer
"""
import os
import pytest
import tempfile
from pathlib import Path


class TestUnifiedDatabase:
    """Tests for the unified database layer after refactoring"""

    def test_single_database_entry_point(self):
        """Should have a single database manager entry point"""
        from app.db.session import db_manager

        assert db_manager is not None
        # Should be a singleton
        from app.db.session import db_manager as db_manager2
        assert db_manager is db_manager2

    def test_database_manager_has_required_methods(self):
        """DatabaseManager should have all required methods"""
        from app.db.session import DatabaseManager

        manager = DatabaseManager()
        assert hasattr(manager, "init")
        assert hasattr(manager, "get_session")
        assert hasattr(manager, "close")
        assert hasattr(manager, "init_db")

    @pytest.mark.asyncio
    async def test_init_creates_database_file(self):
        """init should create database file and directory"""
        from app.db.session import DatabaseManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            db_url = f"sqlite+aiosqlite:///{db_path}"

            manager = DatabaseManager()
            manager.init(db_url)  # Not async
            await manager.init_db()

            # Check database file was created
            assert os.path.exists(db_path)

            await manager.close()

    @pytest.mark.asyncio
    async def test_get_session_returns_async_session(self):
        """get_session should be an async generator that yields sessions"""
        from app.db.session import DatabaseManager
        from sqlalchemy.ext.asyncio import AsyncSession

        manager = DatabaseManager()
        manager.init("sqlite+aiosqlite:///:memory:")

        # get_session returns an async context manager
        async with manager.get_session() as session:
            assert isinstance(session, AsyncSession)
        await manager.close()

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self):
        """init_db should create all required tables"""
        from app.db.session import DatabaseManager
        from app.models.database import Base, ScanTask, MediaFile

        manager = DatabaseManager()
        manager.init("sqlite+aiosqlite:///:memory:")  # Not async
        await manager.init_db()

        # Check that tables exist by inspecting metadata
        assert ScanTask.__tablename__ in Base.metadata.tables
        assert MediaFile.__tablename__ in Base.metadata.tables

        await manager.close()

    @pytest.mark.asyncio
    async def test_close_disposes_engine(self):
        """close should dispose the engine"""
        from app.db.session import DatabaseManager

        manager = DatabaseManager()
        manager.init("sqlite+aiosqlite:///:memory:")  # Not async

        assert manager.engine is not None
        await manager.close()

        # Engine should be None after close
        assert manager.engine is None


class TestDatabaseModuleFunctions:
    """Tests for module-level convenience functions"""

    @pytest.mark.asyncio
    async def test_get_db_dependency_exists(self):
        """get_db function should exist for FastAPI dependency injection"""
        from app.db.session import get_db

        assert callable(get_db)

    @pytest.mark.asyncio
    async def test_init_database_function_exists(self):
        """init_database function should exist for app startup"""
        from app.db.session import init_database

        assert callable(init_database)

        # Should be able to initialize without errors
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_init.db")
            await init_database(f"sqlite+aiosqlite:///{db_path}")
            assert os.path.exists(db_path)

    @pytest.mark.asyncio
    async def test_close_database_function_exists(self):
        """close_database function should exist for app shutdown"""
        from app.db.session import close_database, init_database

        await init_database("sqlite+aiosqlite:///:memory:")
        await close_database()

        # Should not raise


class TestNoDuplicateDatabaseCode:
    """Tests to ensure no duplicate database code exists after refactoring"""

    def test_no_old_database_module(self):
        """Old core/database.py should not exist or be imported"""
        # After refactoring, old database module should be removed
        # This test verifies the cleanup was done

        old_module_path = Path(__file__).parent.parent.parent / "app" / "core" / "database.py"

        # File should either not exist or only contain deprecation import
        if old_module_path.exists():
            content = old_module_path.read_text()
            # Should only import from new location
            assert "from app.db.session import" in content or "deprecated" in content.lower()

    def test_single_repository_location(self):
        """Repository classes should be in a single location"""
        from app.repositories.scan_repository import ScanRepository

        # repositories/scan_repository.py should be the main location
        assert ScanRepository is not None
        assert hasattr(ScanRepository, "create_scan_task")
        assert hasattr(ScanRepository, "get_scan_task_by_id")


class TestDatabaseConfiguration:
    """Tests for database configuration"""

    def test_uses_settings_database_url(self):
        """Should use DATABASE_URL from settings by default"""
        from app.db.session import db_manager
        from app.core.config import settings

        # Settings should have DATABASE_URL
        assert hasattr(settings, "DATABASE_URL")

    def test_sqlite_pool_settings_ignored(self):
        """SQLite should not use pool settings (they cause errors)"""
        from app.db.session import DatabaseManager

        manager = DatabaseManager()

        # Should init with SQLite without requiring pool settings
        # init() is not async
        manager.init("sqlite+aiosqlite:///:memory:")
        assert manager.engine is not None

        # Clean up
        import asyncio
        async def cleanup():
            await manager.close()
        asyncio.run(cleanup())
