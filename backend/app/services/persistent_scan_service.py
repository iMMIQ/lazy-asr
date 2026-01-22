"""
Persistent scan service with database support for long-term operation
"""

import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from app.core.config import settings
from app.core.logger import get_logger
from app.core.database import get_db_context
from app.models.schemas import ScanRequest, ScanStatus, ASRResponse
from app.repositories.scan_repository import ScanRepository, MediaFileRepository
from app.services.asr_service import ASRService
from app.models.database import ScanTask, MediaFile, MonitorConfig
from app.utils.file_type import get_file_type, is_media_file

logger = get_logger(__name__)


class PersistentScanService:
    """Service for persistent path scanning with database support"""

    def __init__(self):
        self.asr_service = ASRService()
        self.active_scans: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def scan_path(self, scan_request: ScanRequest) -> str:
        """
        Start scanning a path for media files and process them (persistent)

        Args:
            scan_request: Scan request containing path and parameters

        Returns:
            scan_id: Unique ID for tracking this scan
        """
        # Validate path
        if not os.path.exists(scan_request.path):
            raise ValueError(f"Path does not exist: {scan_request.path}")

        if not os.path.isdir(scan_request.path):
            raise ValueError(f"Path is not a directory: {scan_request.path}")

        # Auto-create monitor config if not exists
        await self._ensure_monitor_exists(scan_request)

        # Create scan task in database
        async with get_db_context() as session:
            scan_id = ScanTask.generate_scan_id()
            scan_task = await ScanRepository.create_scan_task(
                session=session,
                scan_id=scan_id,
                path=scan_request.path,
                recursive=scan_request.recursive,
                asr_method=scan_request.asr_method,
                output_formats=scan_request.output_formats,
            )
            logger.info(f"Created scan task {scan_id} for path: {scan_request.path}")

        # Start scan in background
        task = asyncio.create_task(self._perform_scan(scan_id, scan_request))

        async with self._lock:
            self.active_scans[scan_id] = task

        return scan_id

    async def _ensure_monitor_exists(self, scan_request: ScanRequest):
        """
        Ensure a monitor configuration exists for the scan path.
        Create one if it doesn't exist, using the scan request parameters.
        """
        try:
            async with get_db_context() as session:
                # Check if monitor already exists for this path
                result = await session.execute(select(MonitorConfig).where(MonitorConfig.path == scan_request.path))
                existing_monitor = result.scalar_one_or_none()

                if existing_monitor:
                    logger.info(f"Monitor already exists for path: {scan_request.path}")
                    return

                # Create new monitor with scan request parameters
                # Generate a name based on the path
                path_name = os.path.basename(os.path.normpath(scan_request.path))
                monitor_name = f"{path_name} Monitor"

                monitor = MonitorConfig(
                    name=monitor_name,
                    path=scan_request.path,
                    is_active=True,
                    recursive=scan_request.recursive,
                    asr_method=scan_request.asr_method,
                    output_formats=scan_request.output_formats or ["srt"],
                    auto_process=True,  # Auto-process new files by default
                    scan_interval=3600,  # Default 1 hour interval
                )
                session.add(monitor)
                await session.flush()

                logger.info(f"Auto-created monitor config: {monitor_name} for path: {scan_request.path}")
        except Exception as e:
            logger.warning(f"Failed to auto-create monitor config for {scan_request.path}: {e}")
            # Don't fail the scan if monitor creation fails

    def _has_existing_subtitles(self, media_path: str, output_formats: List[str]) -> bool:
        """
        Check if subtitle files already exist for the given media file

        Args:
            media_path: Path to the media file
            output_formats: List of output formats to check

        Returns:
            True if any subtitle file exists, False otherwise
        """
        if not output_formats:
            return False

        media_dir = os.path.dirname(media_path)
        base_name = os.path.splitext(os.path.basename(media_path))[0]

        for fmt in output_formats:
            subtitle_path = os.path.join(media_dir, f"{base_name}.{fmt}")
            if os.path.exists(subtitle_path):
                return True

        return False

    def _determine_file_type(self, file_path: str) -> str:
        """
        Determine if file is audio or video using filetype library
        
        Args:
            file_path: Path to the file
            
        Returns:
            'audio', 'video', or 'unknown'
        """
        file_type, _ = get_file_type(file_path)
        return file_type if file_type else 'unknown'

    async def _perform_scan(self, scan_id: str, scan_request: ScanRequest):
        """Perform the actual scan and processing"""
        try:
            # Update status to scanning
            async with get_db_context() as session:
                await ScanRepository.update_scan_task_status(
                    session=session,
                    scan_id=scan_id,
                    status="scanning",
                    message="Scanning for media files...",
                )

            # Find media files
            media_files = self._find_media_files(
                scan_request.path, scan_request.recursive, scan_request.max_files or settings.SCAN_MAX_FILES
            )

            if not media_files:
                async with get_db_context() as session:
                    await ScanRepository.update_scan_task_status(
                        session=session,
                        scan_id=scan_id,
                        status="completed",
                        message="No media files found in the specified path",
                    )
                return

            # Create media file records in database
            async with get_db_context() as session:
                scan_task = await ScanRepository.get_scan_task_by_id(session, scan_id)
                if scan_task:
                    for file_path in media_files:
                        try:
                            file_size = os.path.getsize(file_path)
                            file_name = os.path.basename(file_path)
                            file_type = self._determine_file_type(file_path)
                            has_subtitle = self._has_existing_subtitles(file_path, scan_request.output_formats)

                            await MediaFileRepository.create_media_file(
                                session=session,
                                scan_task_id=scan_task.id,
                                file_path=file_path,
                                file_name=file_name,
                                file_size=file_size,
                                file_type=file_type,
                                has_subtitle=has_subtitle,
                            )
                        except Exception as e:
                            logger.error(f"Error creating media file record for {file_path}: {e}")

            # Update scan task with total files count
            async with get_db_context() as session:
                total_count = await MediaFileRepository.count_media_files(session, scan_id)
                skipped_count = await MediaFileRepository.count_media_files_by_status(session, scan_id, "skipped")
                pending_count = total_count - skipped_count

                await ScanRepository.update_scan_task(
                    session=session,
                    scan_id=scan_id,
                    status="processing",
                    total_files=total_count,
                    message=f"Found {total_count} media files, {skipped_count} already have subtitles, processing {pending_count} files...",
                )

            # Process each file
            processed_count = 0
            failed_count = 0

            async with get_db_context() as session:
                scan_task = await ScanRepository.get_scan_task_by_id(session, scan_id)
                if scan_task:
                    media_files = session.execute(
                        select(MediaFile)
                        .where(
                            MediaFile.scan_task_id == scan_task.id,
                            MediaFile.status == "pending",
                            MediaFile.has_subtitle == False,
                        )
                        .order_by(MediaFile.created_at.asc())
                    )
                    media_files = media_files.scalars().all()

                    total_to_process = len(media_files)

                    for i, media_file in enumerate(media_files):
                        try:
                            # Update current file
                            progress = int((i / total_to_process) * 100) if total_to_process > 0 else 0

                            await ScanRepository.update_scan_task(
                                session=session,
                                scan_id=scan_id,
                                current_file=media_file.file_name,
                                progress=progress,
                            )

                            logger.info(f"Processing file {i+1}/{total_to_process}: {media_file.file_path}")

                            # Mark as processing
                            await MediaFileRepository.update_media_file_status(
                                session=session,
                                file_id=media_file.id,
                                status="processing",
                            )

                            # Process the file using existing ASR service
                            result = await self.asr_service.process_media(
                                media_path=media_file.file_path,
                                asr_method=scan_request.asr_method,
                                output_formats=scan_request.output_formats,
                                output_mode="source",
                            )

                            if result.success:
                                processed_count += 1
                                logger.info(f"Successfully processed: {media_file.file_path}")

                                # Update media file as completed
                                await MediaFileRepository.update_media_file_status(
                                    session=session,
                                    file_id=media_file.id,
                                    status="completed",
                                    output_files=result.output_files,
                                )
                            else:
                                failed_count += 1
                                logger.error(f"Failed to process: {media_file.file_path} - {result.message}")

                                # Update media file as failed
                                await MediaFileRepository.update_media_file_status(
                                    session=session,
                                    file_id=media_file.id,
                                    status="failed",
                                    error_message=result.message,
                                )

                        except Exception as e:
                            failed_count += 1
                            logger.error(f"Error processing file {media_file.file_path}: {e}")

                            # Update media file as failed
                            await MediaFileRepository.update_media_file_status(
                                session=session,
                                file_id=media_file.id,
                                status="failed",
                                error_message=str(e),
                            )

            # Update final status
            async with get_db_context() as session:
                total_files = await MediaFileRepository.count_media_files(session, scan_id)
                skipped_files = await MediaFileRepository.count_media_files_by_status(session, scan_id, "skipped")

                await ScanRepository.update_scan_task_status(
                    session=session,
                    scan_id=scan_id,
                    status="completed",
                    message=f"Scan completed. Total: {total_files}, Skipped (existing subtitles): {skipped_files}, Processed: {processed_count}, Failed: {failed_count}",
                )

                await ScanRepository.update_scan_task(
                    session=session,
                    scan_id=scan_id,
                    processed_files=processed_count,
                    failed_files=failed_count,
                    progress=100,
                )

            logger.info(
                f"Scan {scan_id} completed: Total: {total_files}, Skipped: {skipped_files}, Processed: {processed_count}, Failed: {failed_count}"
            )

        except Exception as e:
            logger.error(f"Error during scan {scan_id}: {e}")
            try:
                async with get_db_context() as session:
                    await ScanRepository.update_scan_task_status(
                        session=session,
                        scan_id=scan_id,
                        status="failed",
                        message=f"Scan failed: {str(e)}",
                    )
            except Exception as db_error:
                logger.error(f"Error updating scan status to failed: {db_error}")
        finally:
            # Remove from active scans
            async with self._lock:
                if scan_id in self.active_scans:
                    del self.active_scans[scan_id]

    def _find_media_files(self, path: str, recursive: bool = True, max_files: int = 100) -> List[str]:
        """
        Find media files in the specified path using filetype library

        Args:
            path: Directory path to scan
            recursive: Whether to scan recursively
            max_files: Maximum number of files to return

        Returns:
            List of media file paths
        """
        media_files = []

        try:
            if recursive:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if len(media_files) >= max_files:
                            return media_files

                        file_path = os.path.join(root, file)
                        # Use filetype library to detect if it's a media file
                        if is_media_file(file_path):
                            media_files.append(file_path)
            else:
                for item in os.listdir(path):
                    if len(media_files) >= max_files:
                        return media_files

                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path):
                        # Use filetype library to detect if it's a media file
                        if is_media_file(item_path):
                            media_files.append(item_path)

        except Exception as e:
            logger.error(f"Error scanning path {path}: {e}")

        return media_files

    async def get_scan_status(self, scan_id: str) -> Optional[ScanStatus]:
        """Get the status of a scan"""
        async with get_db_context() as session:
            scan_task = await ScanRepository.get_scan_task_by_id(session, scan_id)
            if not scan_task:
                return None

            return ScanStatus(
                scan_id=scan_task.scan_id,
                status=scan_task.status,
                total_files=scan_task.total_files,
                processed_files=scan_task.processed_files,
                failed_files=scan_task.failed_files,
                current_file=scan_task.current_file,
                progress=scan_task.progress,
                message=scan_task.message,
                start_time=scan_task.start_time,
                end_time=scan_task.end_time,
            )

    async def get_all_scans(self, limit: int = 50, offset: int = 0, status: Optional[str] = None) -> List[ScanStatus]:
        """Get status of all scans"""
        async with get_db_context() as session:
            scan_tasks = await ScanRepository.get_all_scan_tasks(
                session=session,
                limit=limit,
                offset=offset,
                status=status,
            )

            return [
                ScanStatus(
                    scan_id=task.scan_id,
                    status=task.status,
                    total_files=task.total_files,
                    processed_files=task.processed_files,
                    failed_files=task.failed_files,
                    current_file=task.current_file,
                    progress=task.progress,
                    message=task.message,
                    start_time=task.start_time,
                    end_time=task.end_time,
                )
                for task in scan_tasks
            ]

    async def cancel_scan(self, scan_id: str) -> bool:
        """Cancel a scan"""
        async with self._lock:
            if scan_id in self.active_scans:
                task = self.active_scans[scan_id]
                task.cancel()
                del self.active_scans[scan_id]

                # Update database status
                async with get_db_context() as session:
                    await ScanRepository.update_scan_task_status(
                        session=session,
                        scan_id=scan_id,
                        status="cancelled",
                        message="Scan cancelled by user",
                    )

                return True
            else:
                # Check if scan exists in database but not active
                async with get_db_context() as session:
                    scan_task = await ScanRepository.get_scan_task_by_id(session, scan_id)
                    if scan_task and scan_task.status in ["pending", "scanning", "processing"]:
                        await ScanRepository.update_scan_task_status(
                            session=session,
                            scan_id=scan_id,
                            status="cancelled",
                            message="Scan cancelled by user",
                        )
                        return True

        return False

    async def delete_scan(self, scan_id: str) -> bool:
        """Delete a scan and all associated data"""
        async with self._lock:
            # Cancel if active
            if scan_id in self.active_scans:
                task = self.active_scans[scan_id]
                task.cancel()
                del self.active_scans[scan_id]

        # Delete from database
        async with get_db_context() as session:
            return await ScanRepository.delete_scan_task(session=session, scan_id=scan_id)

    async def get_media_files(self, scan_id: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get media files for a scan"""
        async with get_db_context() as session:
            media_files = await MediaFileRepository.get_media_files_by_scan_id(
                session=session,
                scan_id=scan_id,
                limit=limit,
                offset=offset,
            )

            return [
                {
                    "id": mf.id,
                    "file_path": mf.file_path,
                    "file_name": mf.file_name,
                    "file_size": mf.file_size,
                    "file_type": mf.file_type,
                    "status": mf.status,
                    "has_subtitle": mf.has_subtitle,
                    "output_files": mf.output_files,
                    "error_message": mf.error_message,
                    "processed_at": mf.processed_at.isoformat() if mf.processed_at else None,
                    "created_at": mf.created_at.isoformat() if mf.created_at else None,
                }
                for mf in media_files
            ]


# Global persistent scan service instance
persistent_scan_service = PersistentScanService()
