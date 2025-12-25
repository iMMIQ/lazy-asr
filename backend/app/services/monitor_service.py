"""
Monitor service for long-term background monitoring of paths
"""

import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from app.core.config import settings
from app.core.logger import get_logger
from app.core.database import get_db_context
from app.models.database import MonitorConfig
from app.repositories.scan_repository import ScanRepository, MediaFileRepository
from app.services.persistent_scan_service import persistent_scan_service
from app.models.schemas import ScanRequest

logger = get_logger(__name__)


class MonitorService:
    """Service for monitoring paths and auto-processing media files"""

    def __init__(self):
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def start(self):
        """Start the monitor service"""
        async with self._lock:
            if self.running:
                logger.warning("Monitor service is already running")
                return

            self.running = True
            self.monitor_task = asyncio.create_task(self._monitor_loop())
            logger.info("Monitor service started")

    async def stop(self):
        """Stop the monitor service"""
        async with self._lock:
            if not self.running:
                return

            self.running = False
            if self.monitor_task:
                self.monitor_task.cancel()
                try:
                    await self.monitor_task
                except asyncio.CancelledError:
                    pass

            logger.info("Monitor service stopped")

    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                await self._check_and_process_monitors()
                # Wait for 60 seconds before next check
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                logger.info("Monitor loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(60)

    async def _check_and_process_monitors(self):
        """Check all active monitors and process if needed"""
        async with get_db_context() as session:
            # Get all active monitors
            result = await session.execute(
                select(MonitorConfig).where(MonitorConfig.is_active == True).order_by(MonitorConfig.created_at.asc())
            )
            monitors = result.scalars().all()

            for monitor in monitors:
                try:
                    # Check if it's time to scan
                    should_scan = await self._should_scan(monitor)

                    if should_scan:
                        logger.info(f"Starting monitor scan for: {monitor.name} ({monitor.path})")
                        await self._run_monitor_scan(monitor)
                except Exception as e:
                    logger.error(f"Error processing monitor {monitor.name}: {e}")

    async def _should_scan(self, monitor: MonitorConfig) -> bool:
        """Check if monitor should run a scan"""
        if not monitor.last_scan_time:
            # Never scanned before, should scan
            return True

        # Calculate time since last scan
        time_since_last_scan = (datetime.utcnow() - monitor.last_scan_time).total_seconds()

        # Check if enough time has passed
        return time_since_last_scan >= monitor.scan_interval

    async def _run_monitor_scan(self, monitor: MonitorConfig):
        """Run a scan for a monitor"""
        try:
            # Find new media files
            new_files = await self._find_new_media_files(monitor)

            if not new_files:
                logger.info(f"No new files found for monitor: {monitor.name}")
                # Update last scan time even if no new files
                await self._update_last_scan_time(monitor.id)
                return

            logger.info(f"Found {len(new_files)} new files for monitor: {monitor.name}")

            # If auto_process is enabled, process the files
            if monitor.auto_process:
                # Create a scan request for processing
                scan_request = ScanRequest(
                    path=monitor.path,
                    recursive=monitor.recursive,
                    asr_method=monitor.asr_method,
                    output_formats=monitor.output_formats or ["srt"],
                )

                # Start scan
                scan_id = await persistent_scan_service.scan_path(scan_request)
                logger.info(f"Started scan {scan_id} for monitor: {monitor.name}")
            else:
                logger.info(f"Auto-process disabled for monitor: {monitor.name}. Files detected but not processed.")

            # Update last scan time
            await self._update_last_scan_time(monitor.id)

        except Exception as e:
            logger.error(f"Error running monitor scan for {monitor.name}: {e}")

    async def _find_new_media_files(self, monitor: MonitorConfig) -> List[str]:
        """Find new media files that don't have subtitles"""
        new_files = []
        extensions = set(ext.lower() for ext in settings.SCAN_FILE_EXTENSIONS)

        try:
            if monitor.recursive:
                for root, dirs, files in os.walk(monitor.path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_ext = os.path.splitext(file)[1].lower()

                        if file_ext in extensions:
                            # Check if subtitle exists
                            if not self._has_subtitle(file_path, monitor.output_formats or ["srt"]):
                                new_files.append(file_path)
            else:
                for item in os.listdir(monitor.path):
                    item_path = os.path.join(monitor.path, item)
                    if os.path.isfile(item_path):
                        file_ext = os.path.splitext(item)[1].lower()

                        if file_ext in extensions:
                            # Check if subtitle exists
                            if not self._has_subtitle(item_path, monitor.output_formats or ["srt"]):
                                new_files.append(item_path)

        except Exception as e:
            logger.error(f"Error finding new media files for monitor {monitor.name}: {e}")

        return new_files

    def _has_subtitle(self, media_path: str, output_formats: List[str]) -> bool:
        """Check if subtitle files already exist for the given media file"""
        if not output_formats:
            return False

        media_dir = os.path.dirname(media_path)
        base_name = os.path.splitext(os.path.basename(media_path))[0]

        for fmt in output_formats:
            subtitle_path = os.path.join(media_dir, f"{base_name}.{fmt}")
            if os.path.exists(subtitle_path):
                return True

        return False

    async def _update_last_scan_time(self, monitor_id: int):
        """Update the last scan time for a monitor"""
        async with get_db_context() as session:
            result = await session.execute(select(MonitorConfig).where(MonitorConfig.id == monitor_id))
            monitor = result.scalar_one_or_none()

            if monitor:
                monitor.last_scan_time = datetime.utcnow()
                monitor.updated_at = datetime.utcnow()

    # Monitor configuration management methods

    async def create_monitor_config(
        self,
        name: str,
        path: str,
        recursive: bool = True,
        asr_method: str = "local-whisper",
        output_formats: Optional[List[str]] = None,
        auto_process: bool = True,
        scan_interval: int = 3600,
    ) -> MonitorConfig:
        """Create a new monitor configuration"""
        # Validate path
        if not os.path.exists(path):
            raise ValueError(f"Path does not exist: {path}")

        if not os.path.isdir(path):
            raise ValueError(f"Path is not a directory: {path}")

        async with get_db_context() as session:
            monitor = MonitorConfig(
                name=name,
                path=path,
                is_active=True,
                recursive=recursive,
                asr_method=asr_method,
                output_formats=output_formats or ["srt"],
                auto_process=auto_process,
                scan_interval=scan_interval,
            )
            session.add(monitor)
            await session.flush()
            await session.refresh(monitor)

            logger.info(f"Created monitor config: {name} for path: {path}")
            return monitor

    async def get_monitor_config(self, monitor_id: int) -> Optional[MonitorConfig]:
        """Get monitor configuration by ID"""
        async with get_db_context() as session:
            result = await session.execute(select(MonitorConfig).where(MonitorConfig.id == monitor_id))
            return result.scalar_one_or_none()

    async def get_all_monitor_configs(self, active_only: bool = False) -> List[MonitorConfig]:
        """Get all monitor configurations"""
        async with get_db_context() as session:
            query = select(MonitorConfig).order_by(MonitorConfig.created_at.desc())

            if active_only:
                query = query.where(MonitorConfig.is_active == True)

            result = await session.execute(query)
            return result.scalars().all()

    async def update_monitor_config(self, monitor_id: int, **kwargs) -> Optional[MonitorConfig]:
        """Update monitor configuration"""
        async with get_db_context() as session:
            result = await session.execute(select(MonitorConfig).where(MonitorConfig.id == monitor_id))
            monitor = result.scalar_one_or_none()

            if not monitor:
                return None

            for key, value in kwargs.items():
                if hasattr(monitor, key):
                    setattr(monitor, key, value)

            monitor.updated_at = datetime.utcnow()
            await session.flush()
            await session.refresh(monitor)

            logger.info(f"Updated monitor config: {monitor.name}")
            return monitor

    async def delete_monitor_config(self, monitor_id: int) -> bool:
        """Delete monitor configuration"""
        async with get_db_context() as session:
            result = await session.execute(select(MonitorConfig).where(MonitorConfig.id == monitor_id))
            monitor = result.scalar_one_or_none()

            if not monitor:
                return False

            await session.delete(monitor)
            await session.flush()

            logger.info(f"Deleted monitor config: {monitor.name}")
            return True

    async def toggle_monitor_status(self, monitor_id: int, is_active: bool) -> Optional[MonitorConfig]:
        """Toggle monitor active status"""
        return await self.update_monitor_config(monitor_id, is_active=is_active)

    async def get_monitor_status(self) -> Dict[str, Any]:
        """Get overall monitor service status"""
        monitors = await self.get_all_monitor_configs()
        active_monitors = [m for m in monitors if m.is_active]

        return {
            "service_running": self.running,
            "total_monitors": len(monitors),
            "active_monitors": len(active_monitors),
            "monitors": [m.to_dict() for m in monitors],
        }


# Global monitor service instance
monitor_service = MonitorService()
