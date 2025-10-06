import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from plugins.base import ASRPlugin
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class FasterWhisperPlugin(ASRPlugin):
    """Faster Whisper ASR plugin"""

    def __init__(self):
        super().__init__(name="faster-whisper", description="Faster Whisper ASR service")
        self.api_url = settings.FASTER_WHISPER_API_URL
        self.api_key = settings.FASTER_WHISPER_API_KEY
        self.model = settings.FASTER_WHISPER_MODEL

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Faster Whisper configuration"""
        # For now, we don't have specific validation requirements
        return True

    def _get_language_prompt(self, language: str) -> str:
        """
        Get language-specific prompt for Faster Whisper
        
        Args:
            language: Language code
            
        Returns:
            Language-specific prompt text
        """
        language_prompts = {
            "auto": "",  # Default prompt for auto detect
            "ja": "よろしくお願いします.",  # Japanese
            "zh": "请转录这段音频。",  # Chinese
            "en": "Please transcribe this audio.",  # English
        }
        
        return language_prompts.get(language, language_prompts["auto"])

    async def transcribe_segment(self, segment_file: str, segment_info: Dict[str, Any], language: str = "auto") -> Optional[List[str]]:
        """
        Transcribe a single audio segment using Faster Whisper

        Args:
            segment_file: Path to the audio segment file
            segment_info: Dictionary containing segment information
            language: Language code for transcription

        Returns:
            List of transcription strings or None if failed
        """
        try:
            # Create FormData for multipart upload
            form_data = aiohttp.FormData()

            # Read the audio file content and add to form data
            with open(segment_file, 'rb') as audio_file:
                filename = segment_file.split('/')[-1]
                audio_content = audio_file.read()
                form_data.add_field('file', audio_content, filename=filename, content_type='audio/wav')

            # Add language-specific prompt
            prompt_text = self._get_language_prompt(language)
            
            # Add other form fields
            form_data.add_field('stream', 'false')
            form_data.add_field('timestamp_granularities', 'segment')
            form_data.add_field('prompt', prompt_text)
            form_data.add_field('batch_size', '1')
            form_data.add_field('model', self.model)
            form_data.add_field('temperature', '0')
            form_data.add_field('response_format', 'text')
            form_data.add_field('hotwords', 'string')
            form_data.add_field('vad_filter', 'false')

            # Prepare headers
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            # Send the request with FormData
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url, data=form_data, headers=headers, timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    response.raise_for_status()

                    # Parse the response as plain text
                    text = await response.text()
                    text = text.strip()

                    # Return as list with single text segment
                    return [text] if text else None

        except asyncio.TimeoutError:
            error_msg = f"Faster Whisper transcription timed out for segment {segment_info.get('index', 'unknown')}"
            logger.error(f"  {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Faster Whisper transcription failed: {str(e)}"
            logger.error(f"  {error_msg}")
            raise Exception(error_msg)
