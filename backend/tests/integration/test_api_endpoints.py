"""
Integration tests for API endpoints.

These tests verify the interaction between API layers and the database.
They use test databases and make actual HTTP requests to the test app.
"""
import pytest

from tests.factories import TaskFactory


@pytest.mark.integration
class TestTaskEndpoints:
    """Test task-related API endpoints."""

    async def test_create_task(self, client):
        """Test creating a new task via API."""
        response = await client.post(
            "/api/tasks",
            json={"filename": "test.wav", "language": "zh"}
        )
        assert response.status_code in (201, 200)

        data = response.json()
        assert "id" in data or "task_id" in data
        assert data.get("status") == "pending"

    async def test_get_task_by_id(self, client):
        """Test retrieving a task by its ID."""
        # First create a task
        create_response = await client.post(
            "/api/tasks",
            json={"filename": "test.wav"}
        )
        task_id = create_response.json().get("id") or create_response.json().get("task_id")

        # Then retrieve it
        response = await client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200

        data = response.json()
        assert data.get("id") == task_id or data.get("task_id") == task_id

    async def test_list_tasks(self, client):
        """Test listing all tasks."""
        response = await client.get("/api/tasks")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data.get("items") or data, list)

    async def test_task_not_found(self, client):
        """Test requesting a non-existent task."""
        response = await client.get("/api/tasks/non-existent-id")
        assert response.status_code == 404


@pytest.mark.integration
class TestScanEndpoints:
    """Test scan-related API endpoints."""

    async def test_start_scan_with_file(self, client, sample_audio_file):
        """Test starting a scan with an audio file."""
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("test.wav", f, "audio/wav")}
            response = await client.post("/api/scan", files=files)

        assert response.status_code in (201, 200, 202)

        data = response.json()
        assert "id" in data or "task_id" in data

    async def test_start_scan_invalid_file(self, client):
        """Test starting a scan with an invalid file."""
        files = {"file": ("test.txt", b"not an audio file", "text/plain")}
        response = await client.post("/api/scan", files=files)

        assert response.status_code == 400


@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check endpoints."""

    async def test_health_check(self, client):
        """Test the health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
