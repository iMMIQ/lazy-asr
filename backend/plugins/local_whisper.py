import os
from faster_whisper import WhisperModel
from typing import List, Dict, Any, Optional
from plugins.base import ASRPlugin
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class LocalWhisperPlugin(ASRPlugin):
    """Local Whisper ASR plugin using faster-whisper (CPU-only)"""

    def __init__(self):
        super().__init__(
            name="local-whisper",
            display_name="Local Whisper",
            description="Local Whisper ASR with tiny model (CPU-only)"
        )
        self.model_name = getattr(settings, 'LOCAL_WHISPER_MODEL', 'tiny')
        self.model_cache_dir = getattr(settings, 'LOCAL_WHISPER_MODEL_CACHE_DIR', 'models')

        # Initialize model (will be loaded on first use)
        self.model = None
        self._ensure_model_cache_dir()

    def _ensure_model_cache_dir(self):
        """Ensure model cache directory exists"""
        os.makedirs(self.model_cache_dir, exist_ok=True)

    def _load_model(self):
        """Load Whisper model if not already loaded"""
        if self.model is None:
            try:
                logger.info(f"Loading faster-whisper model: {self.model_name}")
                # Use CPU-only inference
                self.model = WhisperModel(
                    self.model_name,
                    device="cpu",
                    compute_type="int8",  # Use int8 for CPU efficiency
                    download_root=self.model_cache_dir,
                )
                logger.info(f"faster-whisper model {self.model_name} loaded successfully on CPU")
            except Exception as e:
                logger.error(f"Failed to load faster-whisper model: {e}")
                raise

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Local Whisper configuration"""
        # Check if model name is valid
        valid_models = ['tiny', 'base', 'small', 'medium', 'large-v1', 'large-v2', 'large-v3']
        model_name = config.get('model', self.model_name)
        if model_name not in valid_models:
            logger.error(f"Invalid Whisper model: {model_name}. Valid models: {valid_models}")
            return False

        return True

    def _get_language_code(self, language: str) -> Optional[str]:
        """
        Get language code for Whisper

        Args:
            language: Language code

        Returns:
            Whisper language code or None for auto-detect
        """
        language_mapping = {
            "auto": None,  # Auto detect
            "ja": "ja",  # Japanese
            "zh": "zh",  # Chinese
            "en": "en",  # English
            "fr": "fr",  # French
            "de": "de",  # German
            "es": "es",  # Spanish
            "ru": "ru",  # Russian
            "ko": "ko",  # Korean
        }

        return language_mapping.get(language)

    async def transcribe_segment(
        self, segment_file: str, segment_info: Dict[str, Any], language: str = "auto"
    ) -> Optional[List[str]]:
        """
        Transcribe a single audio segment using faster-whisper

        Args:
            segment_file: Path to the audio segment file
            segment_info: Dictionary containing segment information
            language: Language code for transcription

        Returns:
            List of transcription strings or None if failed
        """
        try:
            # Load model if not already loaded
            self._load_model()

            # Get language code for Whisper
            whisper_language = self._get_language_code(language)

            # Transcribe audio using faster-whisper
            segments, info = self.model.transcribe(
                segment_file,
                language=whisper_language,  # None for auto detect
                beam_size=5,  # Default beam size for better accuracy
                vad_filter=False,  # VAD is already applied in the pipeline
            )

            # Extract text segments
            result_segments = []
            for segment in segments:
                text = segment.text.strip()
                if text:
                    result_segments.append(text)

            logger.debug(
                f"Transcribed segment {segment_info.get('index', 'unknown')}: "
                f"detected language={info.language}, language_probability={info.language_probability:.2f}, "
                f"{len(result_segments)} segments found"
            )

            return result_segments if result_segments else None

        except Exception as e:
            error_msg = f"Local Whisper (faster-whisper) transcription failed: {str(e)}"
            logger.error(f"  {error_msg}")
            raise Exception(error_msg)
