"""
Test data factories for creating test objects.

Use these factories to generate consistent test data
instead of hardcoding values in each test.
"""
from datetime import datetime, timedelta
from typing import Any


class TaskFactory:
    """Factory for creating task-related test data."""

    DEFAULTS = {
        "id": "test-task-123",
        "status": "pending",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
    }

    @classmethod
    def create(cls, **overrides: Any) -> dict[str, Any]:
        """Create a task with default values.

        Args:
            **overrides: Fields to override from defaults

        Returns:
            A task dictionary
        """
        return {**cls.DEFAULTS, **overrides}

    @classmethod
    def create_completed(cls, **overrides: Any) -> dict[str, Any]:
        """Create a completed task."""
        return cls.create(
            status="completed",
            progress=100,
            **overrides
        )

    @classmethod
    def create_failed(cls, error: str = "Test error", **overrides: Any) -> dict[str, Any]:
        """Create a failed task."""
        return cls.create(
            status="failed",
            error=error,
            **overrides
        )

    @classmethod
    def create_batch(cls, count: int, **overrides: Any) -> list[dict[str, Any]]:
        """Create multiple tasks.

        Args:
            count: Number of tasks to create
            **overrides: Fields to override in each task

        Returns:
            List of task dictionaries
        """
        return [
            cls.create(id=f"test-task-{i}", **overrides)
            for i in range(count)
        ]


class ScanResultFactory:
    """Factory for creating scan result test data."""

    DEFAULTS = {
        "task_id": "test-task-123",
        "status": "completed",
        "duration": 12.5,
        "text": "Sample transcribed text",
        "segments": [
            {"start": 0.0, "end": 5.0, "text": "First segment"},
            {"start": 5.0, "end": 12.5, "text": "Second segment"},
        ],
    }

    @classmethod
    def create(cls, **overrides: Any) -> dict[str, Any]:
        """Create a scan result with default values."""
        return {**cls.DEFAULTS, **overrides}

    @classmethod
    def create_with_empty_text(cls, **overrides: Any) -> dict[str, Any]:
        """Create a scan result with no transcribed text."""
        return cls.create(text="", segments=[], **overrides)


class FileInfoFactory:
    """Factory for creating file info test data."""

    DEFAULTS = {
        "filename": "test_audio.wav",
        "size": 1024 * 100,  # 100KB
        "mime_type": "audio/wav",
        "duration": 10.0,
    }

    @classmethod
    def create(cls, **overrides: Any) -> dict[str, Any]:
        """Create file info with default values."""
        return {**cls.DEFAULTS, **overrides}

    @classmethod
    def create_mp3(cls, **overrides: Any) -> dict[str, Any]:
        """Create MP3 file info."""
        return cls.create(
            filename="test_audio.mp3",
            mime_type="audio/mpeg",
            **overrides
        )

    @classmethod
    def create_large(cls, size_mb: int = 10, **overrides: Any) -> dict[str, Any]:
        """Create a large file info."""
        return cls.create(
            size=size_mb * 1024 * 1024,
            **overrides
        )
