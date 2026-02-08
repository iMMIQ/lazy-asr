"""
Unified Scan Service Tests - TDD for Refactoring
Tests for the unified scan service that combines memory and persistent approaches
"""
import os
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from app.services.scan_service import scan_service
from app.models.schemas import ScanRequest, ScanStatus


class TestScanServiceExists:
    """Test that scan service exists and has required methods"""

    def test_scan_service_exists(self):
        """scan_service global instance should exist"""
        from app.services.scan_service import scan_service
        assert scan_service is not None

    def test_scan_service_has_scan_path_method(self):
        """ScanService should have scan_path method"""
        from app.services.scan_service import ScanService
        assert hasattr(ScanService, "scan_path")

    def test_scan_service_has_get_scan_status_method(self):
        """ScanService should have get_scan_status method"""
        from app.services.scan_service import ScanService
        assert hasattr(ScanService, "get_scan_status")

    def test_scan_service_has_cancel_scan_method(self):
        """ScanService should have cancel_scan method"""
        from app.services.scan_service import ScanService
        assert hasattr(ScanService, "cancel_scan")


class TestScanPathValidation:
    """Test scan path validation"""

    @pytest.mark.asyncio
    async def test_scan_path_rejects_nonexistent_path(self):
        """scan_path should reject non-existent paths"""
        scan_request = ScanRequest(
            path="/nonexistent/path/that/does/not/exist",
            recursive=True,
            asr_method="whisper-api",
            output_formats=["srt"]
        )

        with pytest.raises(ValueError, match="does not exist"):
            await scan_service.scan_path(scan_request)

    @pytest.mark.asyncio
    async def test_scan_path_rejects_file_instead_of_directory(self):
        """scan_path should reject a file path when expecting a directory"""
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=False):

            scan_request = ScanRequest(
                path="/path/to/file.txt",
                recursive=True,
                asr_method="whisper-api",
                output_formats=["srt"]
            )

            with pytest.raises(ValueError, match="not a directory"):
                await scan_service.scan_path(scan_request)

    @pytest.mark.asyncio
    async def test_scan_path_returns_scan_id(self):
        """scan_path should return a scan_id for valid requests"""
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=True), \
             patch('app.services.scan_service.ScanService._perform_scan'):

            scan_request = ScanRequest(
                path="/valid/path",
                recursive=True,
                asr_method="whisper-api",
                output_formats=["srt"]
            )

            scan_id = await scan_service.scan_path(scan_request)
            # Should return a UUID string
            assert scan_id is not None
            assert len(scan_id) > 0


class TestScanStatusRetrieval:
    """Test scan status retrieval"""

    def test_get_scan_status_returns_status_object(self):
        """get_scan_status should return ScanStatus object"""
        # Create a scan first
        scan_status = ScanStatus(
            scan_id="test-id",
            status="processing",
            total_files=10,
            processed_files=5,
            failed_files=1,
            current_file="test.mp3",
            progress=50,
            message="Processing...",
            start_time=datetime.now(),
            results=[],
        )
        scan_service.active_scans["test-id"] = scan_status

        status = scan_service.get_scan_status("test-id")

        assert status is not None
        assert status.scan_id == "test-id"
        assert status.status == "processing"
        assert status.total_files == 10

    def test_get_scan_status_returns_none_for_nonexistent_scan(self):
        """get_scan_status should return None for non-existent scan"""
        status = scan_service.get_scan_status("nonexistent-id")
        assert status is None


class TestScanCancellation:
    """Test scan cancellation"""

    def test_cancel_scan_sets_status_to_cancelled(self):
        """cancel_scan should set scan status to cancelled"""
        # Create a scan first
        scan_status = ScanStatus(
            scan_id="test-id",
            status="processing",
            total_files=10,
            processed_files=5,
            failed_files=0,
            current_file="test.mp3",
            progress=50,
            message="Processing...",
            start_time=datetime.now(),
            results=[],
        )
        scan_service.active_scans["test-id"] = scan_status

        result = scan_service.cancel_scan("test-id")
        assert result is True
        assert scan_status.status == "cancelled"


class TestGetAllScans:
    """Test retrieving all scans"""

    def test_get_all_scans_returns_list_of_status(self):
        """get_all_scans should return list of ScanStatus objects"""
        # Create some test scans
        scan_status1 = ScanStatus(
            scan_id="test-id-1",
            status="completed",
            total_files=5,
            processed_files=5,
            failed_files=0,
            current_file=None,
            progress=100,
            message="Completed",
            start_time=datetime.now(),
            results=[],
        )
        scan_service.active_scans["test-id-1"] = scan_status1

        scans = scan_service.get_all_scans()

        assert isinstance(scans, list)
        assert len(scans) >= 1
        assert any(s.scan_id == "test-id-1" for s in scans)


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility with existing API"""

    def test_scan_status_schema_exists(self):
        """ScanStatus schema should exist with required fields"""
        from app.models.schemas import ScanStatus

        # Should be able to create a ScanStatus with valid datetime
        now = datetime.now()
        status = ScanStatus(
            scan_id="test-id",
            status="pending",
            total_files=0,
            processed_files=0,
            failed_files=0,
            progress=0,
            message="Test message",
            start_time=now,
            results=[]
        )

        assert status.scan_id == "test-id"
        assert status.status == "pending"

    def test_scan_request_schema_exists(self):
        """ScanRequest schema should exist"""
        from app.models.schemas import ScanRequest

        request = ScanRequest(
            path="/test/path",
            recursive=True,
            asr_method="whisper-api",
            output_formats=["srt"]
        )

        assert request.path == "/test/path"
