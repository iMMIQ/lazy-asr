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
    DEFAULT_ASR_METHOD: str = "whisper-api"
    AVAILABLE_ASR_METHODS: list = ["whisper-api"]

    # ASR API settings (Lazycat ASR service)
    WHISPER_API_URL: str = "https://asr-ai.${LAZYCAT_BOX_DOMAIN}/v1/audio/transcriptions"
    WHISPER_API_KEY: Optional[str] = None
    WHISPER_API_MODEL: str = "fun-asr-nano"

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

    class Config:
        env_file = ".env"


settings = Settings()
