from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class ASRRequest(BaseModel):
    asr_method: str = "whisper-api"
    vad_method: str = Field(default="ten", description="VAD method to use (silero, ten)")
    vad_options: Optional[Dict[str, Any]] = None
    asr_options: Optional[Dict[str, Any]] = None
    output_mode: str = "task"  # "task": 输出到任务目录, "source": 输出到源文件目录

    @field_validator('vad_method')
    @classmethod
    def validate_vad_method(cls, v: str) -> str:
        """Validate that vad_method is one of the available VAD methods."""
        from app.core.config import settings
        if v not in settings.AVAILABLE_VAD_METHODS:
            raise ValueError(f"vad_method must be one of {settings.AVAILABLE_VAD_METHODS}, got '{v}'")
        return v


class SegmentInfo(BaseModel):
    index: int
    start_time: float
    end_time: float
    duration: float
    file_path: str


class TranscriptionSegment(BaseModel):
    start: str
    end: str
    text: str


class FailedSegment(BaseModel):
    index: int
    start_time: float
    end_time: float
    duration: float
    file_path: str
    error: str
    error_type: Optional[str] = None


class ASRResponse(BaseModel):
    success: bool
    message: str
    srt_file_path: Optional[str] = None  # Backward compatibility
    output_files: Optional[Dict[str, str]] = None  # New field: format -> file_path mapping
    segments: Optional[List[TranscriptionSegment]] = None
    stats: Optional[Dict[str, Any]] = None
    failed_segments_details: Optional[List[FailedSegment]] = None
    task_id: Optional[str] = None  # Task ID for bundle download


class FileResult(BaseModel):
    """Single file processing result"""

    filename: str
    success: bool
    message: str
    output_files: Optional[Dict[str, str]] = None
    segments: Optional[List[TranscriptionSegment]] = None
    stats: Optional[Dict[str, Any]] = None
    failed_segments_details: Optional[List[FailedSegment]] = None
    task_id: Optional[str] = None


class MultiFileASRResponse(BaseModel):
    """Multiple file processing response"""

    success: bool
    message: str
    batch_id: str  # Batch ID
    total_files: int
    processed_files: int
    failed_files: int
    file_results: List[FileResult]
    overall_stats: Optional[Dict[str, Any]] = None


class ProcessingStatus(BaseModel):
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    message: str
    created_at: datetime
    updated_at: datetime
    result: Optional[ASRResponse] = None


# Path scanning related models
class ScanRequest(BaseModel):
    """Request to scan a path for media files"""

    path: str
    recursive: bool = True
    asr_method: str = "whisper-api"
    output_formats: List[str] = ["srt"]
    max_files: Optional[int] = None


class ScanStatus(BaseModel):
    """Status of a scan operation"""

    scan_id: str
    status: str  # pending, scanning, processing, completed, failed
    total_files: int
    processed_files: int
    failed_files: int
    current_file: Optional[str] = None
    progress: int  # 0-100
    message: str
    start_time: datetime
    end_time: Optional[datetime] = None
    results: List[ASRResponse] = []


class ScanResult(BaseModel):
    """Result of a scan operation"""

    scan_id: str
    status: str
    total_files: int
    processed_files: int
    failed_files: int
    success_rate: float
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    results: List[ASRResponse] = []
