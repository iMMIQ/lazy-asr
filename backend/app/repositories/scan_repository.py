"""
Repository for scan tasks and media files database operations
"""

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.models.database import ScanTask, MediaFile
from app.core.logger import get_logger

logger = get_logger(__name__)


class ScanRepository:
    """Repository for scan tasks"""

    @staticmethod
    async def create_scan_task(
        session: AsyncSession,
        scan_id: str,
        path: str,
        recursive: bool,
        asr_method: str,
        output_formats: List[str],
    ) -> ScanTask:
        """Create a new scan task"""
        scan_task = ScanTask(
            scan_id=scan_id,
            path=path,
            status="pending",
            recursive=recursive,
            asr_method=asr_method,
            output_formats=output_formats,
            start_time=datetime.utcnow(),
        )
        session.add(scan_task)
        await session.flush()
        await session.refresh(scan_task)
        return scan_task

    @staticmethod
    async def get_scan_task_by_id(session: AsyncSession, scan_id: str) -> Optional[ScanTask]:
        """Get scan task by scan_id"""
        result = await session.execute(select(ScanTask).where(ScanTask.scan_id == scan_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_scan_task_by_db_id(session: AsyncSession, task_id: int) -> Optional[ScanTask]:
        """Get scan task by database id"""
        result = await session.execute(select(ScanTask).where(ScanTask.id == task_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_scan_tasks(
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> List[ScanTask]:
        """Get all scan tasks with optional filtering"""
        query = select(ScanTask).order_by(ScanTask.created_at.desc())

        if status:
            query = query.where(ScanTask.status == status)

        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_scan_task(session: AsyncSession, scan_id: str, **kwargs) -> Optional[ScanTask]:
        """Update scan task"""
        scan_task = await ScanRepository.get_scan_task_by_id(session, scan_id)
        if not scan_task:
            return None

        for key, value in kwargs.items():
            if hasattr(scan_task, key):
                setattr(scan_task, key, value)

        scan_task.updated_at = datetime.utcnow()
        await session.flush()
        await session.refresh(scan_task)
        return scan_task

    @staticmethod
    async def update_scan_task_status(
        session: AsyncSession,
        scan_id: str,
        status: str,
        message: Optional[str] = None,
    ) -> Optional[ScanTask]:
        """Update scan task status"""
        update_data = {"status": status}
        if message:
            update_data["message"] = message

        if status in ["completed", "failed", "cancelled"]:
            update_data["end_time"] = datetime.utcnow()

        return await ScanRepository.update_scan_task(session, scan_id, **update_data)

    @staticmethod
    async def delete_scan_task(session: AsyncSession, scan_id: str) -> bool:
        """Delete scan task and all associated media files"""
        scan_task = await ScanRepository.get_scan_task_by_id(session, scan_id)
        if not scan_task:
            return False

        await session.delete(scan_task)
        await session.flush()
        return True

    @staticmethod
    async def count_scan_tasks(session: AsyncSession) -> int:
        """Count total scan tasks"""
        result = await session.execute(select(func.count(ScanTask.id)))
        return result.scalar() or 0


class MediaFileRepository:
    """Repository for media files"""

    @staticmethod
    async def create_media_file(
        session: AsyncSession,
        scan_task_id: int,
        file_path: str,
        file_name: str,
        file_size: int,
        file_type: str,
        has_subtitle: bool = False,
    ) -> MediaFile:
        """Create a new media file record"""
        media_file = MediaFile(
            scan_task_id=scan_task_id,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            file_type=file_type,
            has_subtitle=has_subtitle,
            status="pending",
        )
        session.add(media_file)
        await session.flush()
        await session.refresh(media_file)
        return media_file

    @staticmethod
    async def get_media_files_by_scan_id(
        session: AsyncSession,
        scan_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[MediaFile]:
        """Get all media files for a scan task"""
        # First get the scan task's database id
        scan_task = await ScanRepository.get_scan_task_by_id(session, scan_id)
        if not scan_task:
            return []

        query = (
            select(MediaFile)
            .where(MediaFile.scan_task_id == scan_task.id)
            .order_by(MediaFile.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_media_file(session: AsyncSession, file_id: int, **kwargs) -> Optional[MediaFile]:
        """Update media file"""
        result = await session.execute(select(MediaFile).where(MediaFile.id == file_id))
        media_file = result.scalar_one_or_none()

        if not media_file:
            return None

        for key, value in kwargs.items():
            if hasattr(media_file, key):
                setattr(media_file, key, value)

        media_file.updated_at = datetime.utcnow()
        await session.flush()
        await session.refresh(media_file)
        return media_file

    @staticmethod
    async def update_media_file_status(
        session: AsyncSession,
        file_id: int,
        status: str,
        output_files: Optional[dict] = None,
        error_message: Optional[str] = None,
    ) -> Optional[MediaFile]:
        """Update media file status"""
        update_data = {"status": status}

        if status == "completed":
            update_data["processed_at"] = datetime.utcnow()

        if output_files:
            update_data["output_files"] = output_files

        if error_message:
            update_data["error_message"] = error_message

        return await MediaFileRepository.update_media_file(session, file_id, **update_data)

    @staticmethod
    async def get_pending_media_files(
        session: AsyncSession,
        scan_id: str,
        limit: int = 10,
    ) -> List[MediaFile]:
        """Get pending media files for processing"""
        scan_task = await ScanRepository.get_scan_task_by_id(session, scan_id)
        if not scan_task:
            return []

        query = (
            select(MediaFile)
            .where(
                MediaFile.scan_task_id == scan_task.id,
                MediaFile.status == "pending",
                MediaFile.has_subtitle == False,
            )
            .order_by(MediaFile.created_at.asc())
            .limit(limit)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def count_media_files(session: AsyncSession, scan_id: str) -> int:
        """Count media files for a scan task"""
        scan_task = await ScanRepository.get_scan_task_by_id(session, scan_id)
        if not scan_task:
            return 0

        result = await session.execute(select(func.count(MediaFile.id)).where(MediaFile.scan_task_id == scan_task.id))
        return result.scalar() or 0

    @staticmethod
    async def count_media_files_by_status(
        session: AsyncSession,
        scan_id: str,
        status: str,
    ) -> int:
        """Count media files by status"""
        scan_task = await ScanRepository.get_scan_task_by_id(session, scan_id)
        if not scan_task:
            return 0

        result = await session.execute(
            select(func.count(MediaFile.id)).where(
                MediaFile.scan_task_id == scan_task.id,
                MediaFile.status == status,
            )
        )
        return result.scalar() or 0
