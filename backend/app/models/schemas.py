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


class ASRResponse(BaseModel):
    success: bool
    message: str
    srt_file_path: Optional[str] = None
    segments: Optional[List[TranscriptionSegment]] = None
    stats: Optional[Dict[str, Any]] = None


class ProcessingStatus(BaseModel):
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    message: str
    created_at: datetime
    updated_at: datetime
    result: Optional[ASRResponse] = None
