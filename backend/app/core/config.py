import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ASR Service"

    # File upload settings
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "output"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB

    # ASR settings
    DEFAULT_ASR_METHOD: str = "local-whisper"
    AVAILABLE_ASR_METHODS: list = ["local-whisper", "whisper-api", "qwen-asr"]

    # Whisper API settings
    WHISPER_API_URL: str = "https://funasr-ai.immiqtop.heiyu.space/v1/audio/transcriptions"
    WHISPER_API_KEY: Optional[str] = None
    WHISPER_API_MODEL: str = "fun-asr-nano"

    # Qwen ASR settings
    QWEN_ASR_API_KEY: Optional[str] = None
    QWEN_ASR_MODEL: str = "qwen3-asr-flash"
    QWEN_ASR_API_URL: str = (
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/audio/asr"  # Alibaba Cloud ASR API URL (read-only)
    )
    QWEN_ASR_AVAILABLE_MODELS: list = ["qwen3-asr-flash"]  # Alibaba Cloud available model list

    # Local Whisper settings (faster-whisper, CPU-only)
    LOCAL_WHISPER_MODEL: str = "tiny"  # tiny, base, small, medium, large-v1, large-v2, large-v3
    LOCAL_WHISPER_MODEL_CACHE_DIR: str = "models"  # Model cache directory

    # VAD settings
    DEFAULT_VAD_METHOD: str = "ten"
    AVAILABLE_VAD_METHODS: List[str] = ["silero", "ten"]

    # Concurrency settings
    MAX_CONCURRENT_TASKS: int = 16  # Maximum concurrent transcription tasks

    # Path scanning settings
    SCAN_PATHS: list = []  # List of paths to scan for media files
    SCAN_FILE_EXTENSIONS: list = []  # Empty list - use filetype library to detect actual media files
    SCAN_RECURSIVE: bool = True  # Whether to scan recursively
    SCAN_MAX_FILES: int = 100  # Maximum number of files to process in one scan

    # Security settings
    # CORS allowed origins - In production, specify exact origins
    # Can be a comma-separated string: "http://localhost:3000,https://example.com"
    # Note: Empty list allows all origins (for development)
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "ws://localhost:3000", "ws://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list = ["Content-Type", "Authorization", "X-Request-ID", "Sec-WebSocket-Key", "Sec-WebSocket-Version", "Sec-WebSocket-Protocol", "Sec-WebSocket-Extensions", "Connection", "Upgrade"]

    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///data/asr_service.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
