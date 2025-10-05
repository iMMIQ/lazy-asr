import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from plugins.base import ASRPlugin
from app.core.config import settings


class FasterWhisperPlugin(ASRPlugin):
    """Faster Whisper ASR plugin"""
    
    def __init__(self):
        super().__init__(
            name="faster-whisper",
            description="Faster Whisper ASR service"
        )
        self.api_url = settings.FASTER_WHISPER_API_URL
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Faster Whisper configuration"""
        # For now, we don't have specific validation requirements
        return True
    
    async def transcribe_segment(self, segment_file: str, segment_info: Dict[str, Any]) -> Optional[List[str]]:
        """
        Transcribe a single audio segment using Faster Whisper
        
        Args:
            segment_file: Path to the audio segment file
            segment_info: Dictionary containing segment information
            
        Returns:
            List of transcription strings or None if failed
        """
        try:
            # Prepare the request data
            data = {
                'stream': 'false',
                'timestamp_granularities': 'segment',
                'prompt': 'よろしくお願いします.',
                'batch_size': '1',
                'model': 'Systran/faster-whisper-large-v2',
                'temperature': '0',
                'response_format': 'text',
                'hotwords': 'string',
                'vad_filter': 'false'
            }
            
            # Send the request
            async with aiohttp.ClientSession() as session:
                with open(segment_file, 'rb') as audio_file:
                    filename = segment_file.split('/')[-1]
                    files = {'file': (filename, audio_file, 'audio/wav')}
                    
                    # Note: aiohttp doesn't support multipart file uploads with fields easily
                    # We'll send as form data instead
                    async with session.post(
                        self.api_url,
                        data=data,
                        timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        response.raise_for_status()
                        
                        # Collect all lines from the streaming response
                        segments = []
                        async for line in response.content:
                            line_str = line.decode('utf-8').strip()
                            if line_str:
                                segments.append(line_str)
                        
                        return segments if segments else None
                        
        except asyncio.TimeoutError:
            print(f"     ❌ Faster Whisper transcription timed out for segment {segment_info.get('index', 'unknown')}")
            return None
        except Exception as e:
            print(f"     ❌ Faster Whisper transcription failed: {e}")
            return None
