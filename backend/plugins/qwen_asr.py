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

    async def transcribe_segment(self, segment_file: str, segment_info: Dict[str, Any]) -> Optional[List[str]]:
        """
        Transcribe a single audio segment using Qwen ASR

        Args:
            segment_file: Path to the audio segment file
            segment_info: Dictionary containing segment information

        Returns:
            List of transcription strings or None if failed
        """
        try:
            # Import DashScope only when needed
            from dashscope import MultiModalConversation

            # Prepare the messages
            messages = [
                {
                    "role": "system",
                    "content": [
                        {"text": "よろしくお願いします."},
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"audio": segment_file},
                    ],
                },
            ]

            # Call the Qwen ASR API
            response = MultiModalConversation.call(
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                result_format="message",
                asr_options={"language": "ja", "enable_lid": True, "enable_itn": False},
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
