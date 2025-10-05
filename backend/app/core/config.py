import os
from typing import Optional
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
    DEFAULT_ASR_METHOD: str = "faster-whisper"
    AVAILABLE_ASR_METHODS: list = ["faster-whisper", "qwen-asr"]

    # Faster Whisper settings
    FASTER_WHISPER_API_URL: str = "https://asr-ai.immiqnas.heiyu.space/v1/audio/transcriptions"
    FASTER_WHISPER_API_KEY: Optional[str] = None
    FASTER_WHISPER_MODEL: str = "Systran/faster-whisper-large-v2"

    # Qwen ASR settings
    QWEN_ASR_API_KEY: Optional[str] = None
    QWEN_ASR_MODEL: str = "qwen3-asr-flash"
    QWEN_ASR_API_URL: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/audio/asr"  # 阿里云ASR API URL (只读)
    QWEN_ASR_AVAILABLE_MODELS: list = ["qwen3-asr-flash"]  # 阿里云可选的模型列表

    # Concurrency settings
    MAX_CONCURRENT_TASKS: int = 16  # Maximum concurrent transcription tasks

    class Config:
        env_file = ".env"


settings = Settings()
