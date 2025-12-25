"""
Database models for persistent scan and monitoring functionality
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class ScanTask(Base):
    """Scan task table"""

    __tablename__ = "scan_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(36), unique=True, nullable=False, index=True)
    path = Column(String(1024), nullable=False)
    status = Column(String(50), nullable=False, index=True)  # pending, running, paused, completed, failed, cancelled
    recursive = Column(Boolean, default=True)
    asr_method = Column(String(100), nullable=False)
    output_formats = Column(JSON)  # List of output formats
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    failed_files = Column(Integer, default=0)
    progress = Column(Integer, default=0)  # 0-100
    current_file = Column(String(1024))
    message = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with media files
    media_files = relationship("MediaFile", back_populates="scan_task", cascade="all, delete-orphan")

    @staticmethod
    def generate_scan_id():
        return str(uuid.uuid4())


class MediaFile(Base):
    """Media file table"""

    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_task_id = Column(Integer, ForeignKey("scan_tasks.id"), nullable=False, index=True)
    file_path = Column(String(1024), nullable=False)
    file_name = Column(String(512), nullable=False)
    file_size = Column(Integer)  # File size in bytes
    file_type = Column(String(50))  # audio or video
    status = Column(
        String(50), nullable=False, index=True, default="pending"
    )  # pending, processing, completed, failed, skipped
    has_subtitle = Column(Boolean, default=False)
    output_files = Column(JSON)  # Dict of format -> file_path
    error_message = Column(Text)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with scan task
    scan_task = relationship("ScanTask", back_populates="media_files")


class MonitorConfig(Base):
    """Monitor configuration table"""

    __tablename__ = "monitor_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    path = Column(String(1024), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    recursive = Column(Boolean, default=True)
    asr_method = Column(String(100), default="local-whisper")
    output_formats = Column(JSON)  # List of output formats
    auto_process = Column(Boolean, default=True)
    scan_interval = Column(Integer, default=3600)  # Scan interval in seconds (default: 1 hour)
    last_scan_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "is_active": self.is_active,
            "recursive": self.recursive,
            "asr_method": self.asr_method,
            "output_formats": self.output_formats,
            "auto_process": self.auto_process,
            "scan_interval": self.scan_interval,
            "last_scan_time": self.last_scan_time.isoformat() if self.last_scan_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
