"""
Database models for persistent scan functionality
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


