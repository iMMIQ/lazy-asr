from typing import List, Dict, Any, Optional
from plugins.base import ASRPlugin
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class QwenASRPlugin(ASRPlugin):
    """Qwen ASR plugin"""

    def __init__(self):
        super().__init__(name="qwen-asr", description="Qwen ASR service")
        self.api_key = settings.QWEN_ASR_API_KEY
        self.model = settings.QWEN_ASR_MODEL
        self.api_url = settings.QWEN_ASR_API_URL

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Qwen ASR configuration"""
        # Check if API key is provided (either from settings or dynamic config)
        return bool(self.api_key)

    def _get_language_prompt(self, language: str) -> str:
        """
        Get language-specific system prompt for Qwen ASR
        
        Args:
            language: Language code
            
        Returns:
            Language-specific prompt text
        """
        language_prompts = {
            "auto": "よろしくお願いします.",  # Default Japanese prompt for auto detect
            "ja": "よろしくお願いします.",  # Japanese
            "zh": "请转录这段音频。",  # Chinese
            "en": "Please transcribe this audio.",  # English
        }
        
        return language_prompts.get(language, language_prompts["auto"])

    def _get_asr_language(self, language: str) -> str:
        """
        Get language code for Qwen ASR options
        
        Args:
            language: Language code
            
        Returns:
            ASR language code
        """
        language_mapping = {
            "auto": "ja",  # Default to Japanese for auto detect
            "ja": "ja",    # Japanese
            "zh": "zh",    # Chinese
            "en": "en",    # English
        }
        
        return language_mapping.get(language, language_mapping["auto"])

    async def transcribe_segment(self, segment_file: str, segment_info: Dict[str, Any], language: str = "auto") -> Optional[List[str]]:
        """
        Transcribe a single audio segment using Qwen ASR

        Args:
            segment_file: Path to the audio segment file
            segment_info: Dictionary containing segment information
            language: Language code for transcription

        Returns:
            List of transcription strings or None if failed
        """
        try:
            # Import DashScope only when needed
            from dashscope import MultiModalConversation

            # Get language-specific system prompt
            system_prompt = self._get_language_prompt(language)
            
            # Prepare the messages
            messages = [
                {
                    "role": "system",
                    "content": [
                        {"text": system_prompt},
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"audio": segment_file},
                    ],
                },
            ]

            # Get language code for ASR options
            asr_language = self._get_asr_language(language)
            
            # Call the Qwen ASR API
            response = MultiModalConversation.call(
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                result_format="message",
                asr_options={"language": asr_language, "enable_lid": True, "enable_itn": False},
            )

            # Check response status
            if response.status_code != 200:
                logger.error(f"  Qwen ASR request failed: {response.code} - {response.message}")
                return None

            # Extract transcription text
            segments = []
            if hasattr(response, 'output') and response.output:
                if 'choices' in response.output and response.output['choices']:
                    choice = response.output['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        for content_item in choice['message']['content']:
                            if 'text' in content_item:
                                text = content_item['text'].strip()
                                if text:
                                    segments.append(text)

            return segments if segments else None

        except ImportError:
            error_msg = "DashScope SDK not installed. Please install with: pip install dashscope"
            logger.error(f"  {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Qwen ASR transcription failed: {str(e)}"
            logger.error(f"  {error_msg}")
            raise Exception(error_msg)
