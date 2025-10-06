from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ASRRequest(BaseModel):
    asr_method: str = "faster-whisper"
    vad_options: Optional[Dict[str, Any]] = None
    asr_options: Optional[Dict[str, Any]] = None


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
