import os
import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logger import get_logger
from app.models.schemas import ScanRequest, ScanStatus, ScanResult, ASRResponse
from .asr_service import ASRService

logger = get_logger(__name__)


class ScanService:
    """Service for scanning paths and processing media files"""

    def __init__(self):
        self.asr_service = ASRService()
        self.active_scans: Dict[str, ScanStatus] = {}
        self.scan_results: Dict[str, ScanResult] = {}

    async def scan_path(self, scan_request: ScanRequest) -> str:
        """
        Start scanning a path for media files and process them

        Args:
            scan_request: Scan request containing path and parameters

        Returns:
            scan_id: Unique ID for tracking this scan
        """
        scan_id = str(uuid.uuid4())

        # Validate path
        if not os.path.exists(scan_request.path):
            raise ValueError(f"Path does not exist: {scan_request.path}")

        if not os.path.isdir(scan_request.path):
            raise ValueError(f"Path is not a directory: {scan_request.path}")

        # Create initial scan status
        scan_status = ScanStatus(
            scan_id=scan_id,
            status="pending",
            total_files=0,
            processed_files=0,
            failed_files=0,
            progress=0,
            message="Starting scan...",
            start_time=datetime.now(),
            results=[],
        )

        self.active_scans[scan_id] = scan_status

        # Start scan in background
        asyncio.create_task(self._perform_scan(scan_id, scan_request))

        return scan_id

    async def _perform_scan(self, scan_id: str, scan_request: ScanRequest):
        """Perform the actual scan and processing"""
        try:
            scan_status = self.active_scans[scan_id]
            scan_status.status = "scanning"
            scan_status.message = "Scanning for media files..."

            # Find media files
            media_files = self._find_media_files(
                scan_request.path, scan_request.recursive, scan_request.max_files or settings.SCAN_MAX_FILES
            )

            if not media_files:
                scan_status.status = "completed"
                scan_status.message = "No media files found in the specified path"
                scan_status.end_time = datetime.now()
                scan_status.progress = 100
                return

            scan_status.total_files = len(media_files)
            scan_status.status = "processing"
            scan_status.message = f"Processing {len(media_files)} media files..."

            # Process each file
            processed_count = 0
            failed_count = 0
            results = []

            for i, file_path in enumerate(media_files):
                try:
                    scan_status.current_file = os.path.basename(file_path)
                    scan_status.progress = int((i / len(media_files)) * 100)

                    logger.info(f"Processing file {i+1}/{len(media_files)}: {file_path}")

                    # Process the file using existing ASR service
                    # For scan mode, use output_mode="source" to output to same directory as source file
                    result = await self.asr_service.process_media(
                        media_path=file_path,
                        asr_method=scan_request.asr_method,
                        output_formats=scan_request.output_formats,
                        output_mode="source",  # Scan mode: output to source directory
                    )

                    results.append(result)

                    if result.success:
                        processed_count += 1
                        logger.info(f"Successfully processed: {file_path}")

                        # Log where subtitle files were saved
                        if hasattr(result, 'output_files') and result.output_files:
                            for fmt, output_path in result.output_files.items():
                                logger.info(f"  Generated {fmt.upper()} file: {output_path}")
                    else:
                        failed_count += 1
                        logger.error(f"Failed to process: {file_path} - {result.message}")

                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error processing file {file_path}: {e}")

                    # Create error result
                    error_result = ASRResponse(success=False, message=f"Error processing file: {str(e)}", task_id=None)
                    results.append(error_result)

            # Update final status
            scan_status.processed_files = processed_count
            scan_status.failed_files = failed_count
            scan_status.progress = 100
            scan_status.status = "completed"
            scan_status.message = f"Scan completed. Processed: {processed_count}, Failed: {failed_count}"
            scan_status.end_time = datetime.now()
            scan_status.results = results

            # Create final result
            duration = (scan_status.end_time - scan_status.start_time).total_seconds()
            success_rate = processed_count / len(media_files) if media_files else 0

            scan_result = ScanResult(
                scan_id=scan_id,
                status="completed",
                total_files=len(media_files),
                processed_files=processed_count,
                failed_files=failed_count,
                success_rate=success_rate,
                start_time=scan_status.start_time,
                end_time=scan_status.end_time,
                duration_seconds=duration,
                results=results,
            )

            self.scan_results[scan_id] = scan_result

            logger.info(f"Scan {scan_id} completed: {processed_count} processed, {failed_count} failed")

        except Exception as e:
            logger.error(f"Error during scan {scan_id}: {e}")
            if scan_id in self.active_scans:
                scan_status = self.active_scans[scan_id]
                scan_status.status = "failed"
                scan_status.message = f"Scan failed: {str(e)}"
                scan_status.end_time = datetime.now()

    def _find_media_files(self, path: str, recursive: bool = True, max_files: int = 100) -> List[str]:
        """
        Find media files in the specified path

        Args:
            path: Directory path to scan
            recursive: Whether to scan recursively
            max_files: Maximum number of files to return

        Returns:
            List of media file paths
        """
        media_files = []
        extensions = set(ext.lower() for ext in settings.SCAN_FILE_EXTENSIONS)

        try:
            if recursive:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if len(media_files) >= max_files:
                            return media_files

                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext in extensions:
                            media_files.append(os.path.join(root, file))
            else:
                for item in os.listdir(path):
                    if len(media_files) >= max_files:
                        return media_files

                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path):
                        file_ext = os.path.splitext(item)[1].lower()
                        if file_ext in extensions:
                            media_files.append(item_path)

        except Exception as e:
            logger.error(f"Error scanning path {path}: {e}")

        return media_files

    def get_scan_status(self, scan_id: str) -> Optional[ScanStatus]:
        """Get the status of a scan"""
        return self.active_scans.get(scan_id)

    def get_scan_result(self, scan_id: str) -> Optional[ScanResult]:
        """Get the result of a completed scan"""
        return self.scan_results.get(scan_id)

    def get_all_scans(self) -> List[ScanStatus]:
        """Get status of all scans"""
        return list(self.active_scans.values())

    def cancel_scan(self, scan_id: str) -> bool:
        """Cancel a scan (placeholder for future implementation)"""
        if scan_id in self.active_scans:
            scan_status = self.active_scans[scan_id]
            if scan_status.status in ["pending", "scanning", "processing"]:
                scan_status.status = "cancelled"
                scan_status.message = "Scan cancelled by user"
                scan_status.end_time = datetime.now()
                return True
        return False


# Global scan service instance
scan_service = ScanService()
