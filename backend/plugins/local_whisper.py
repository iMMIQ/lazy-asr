import os
import whisper
from typing import List, Dict, Any, Optional
from plugins.base import ASRPlugin
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class LocalWhisperPlugin(ASRPlugin):
    """Local Whisper ASR plugin using OpenAI Whisper"""

    def __init__(self):
        super().__init__(name="local-whisper", description="Local Whisper ASR with tiny model")
        self.model_name = getattr(settings, 'LOCAL_WHISPER_MODEL', 'tiny')
        self.device = getattr(settings, 'LOCAL_WHISPER_DEVICE', 'auto')
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
                logger.info(f"Loading Whisper model: {self.model_name}")
                # Force CPU usage to avoid PyTorch compatibility issues
                self.model = whisper.load_model(
                    self.model_name,
                    device="cpu",  # Force CPU to avoid compatibility issues
                    download_root=self.model_cache_dir,
                )
                logger.info(f"Whisper model {self.model_name} loaded successfully on CPU")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                # Try alternative approach if initial load fails
                try:
                    logger.info("Trying alternative model loading approach...")
                    import torch

                    # Clear any cached models and try again
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    self.model = whisper.load_model(self.model_name, device="cpu", download_root=self.model_cache_dir)
                    logger.info(f"Whisper model {self.model_name} loaded successfully with alternative approach")
                except Exception as e2:
                    logger.error(f"Alternative loading also failed: {e2}")
                    raise

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Local Whisper configuration"""
        # Check if model name is valid
        valid_models = ['tiny', 'base', 'small', 'medium', 'large']
        model_name = config.get('model', self.model_name)
        if model_name not in valid_models:
            logger.error(f"Invalid Whisper model: {model_name}. Valid models: {valid_models}")
            return False

        # Check if device is valid
        valid_devices = ['auto', 'cpu', 'cuda']
        device = config.get('device', self.device)
        if device not in valid_devices:
            logger.error(f"Invalid device: {device}. Valid devices: {valid_devices}")
            return False

        return True

    def _get_language_code(self, language: str) -> str:
        """
        Get language code for Whisper

        Args:
            language: Language code

        Returns:
            Whisper language code
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

        return language_mapping.get(language, None)

    async def transcribe_segment(
        self, segment_file: str, segment_info: Dict[str, Any], language: str = "auto"
    ) -> Optional[List[str]]:
        """
        Transcribe a single audio segment using local Whisper

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

            # Transcribe audio using Whisper
            result = self.model.transcribe(
                segment_file,
                language=whisper_language,  # None for auto detect
                fp16=False,  # Use fp32 for better compatibility
                verbose=False,  # Disable verbose output
            )

            # Extract text segments
            segments = []
            if result and 'text' in result:
                text = result['text'].strip()
                if text:
                    segments.append(text)

            # If no segments found in text field, check segments field
            if not segments and 'segments' in result:
                for segment in result['segments']:
                    if 'text' in segment and segment['text'].strip():
                        segments.append(segment['text'].strip())

            logger.debug(f"Transcribed segment {segment_info.get('index', 'unknown')}: {len(segments)} segments found")
            return segments if segments else None

        except Exception as e:
            error_msg = f"Local Whisper transcription failed: {str(e)}"
            logger.error(f"  {error_msg}")
            raise Exception(error_msg)
