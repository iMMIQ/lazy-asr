from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio


class ASRPlugin(ABC):
    """Base class for ASR plugins"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def transcribe_segment(self, segment_file: str, segment_info: Dict[str, Any]) -> Optional[List[str]]:
        """
        Transcribe a single audio segment
        
        Args:
            segment_file: Path to the audio segment file
            segment_info: Dictionary containing segment information
            
        Returns:
            List of transcription strings or None if failed
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update plugin configuration dynamically
        
        Args:
            config: Configuration dictionary with new values
        """
        # Default implementation - subclasses can override
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    async def transcribe_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transcribe multiple segments concurrently
        
        Args:
            segments: List of segment dictionaries
            
        Returns:
            List of transcription results
        """
        tasks = []
        for segment in segments:
            task = self.transcribe_segment(segment['file_path'], segment)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        transcriptions = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                transcriptions.append({
                    'segment_index': segments[i]['index'],
                    'success': False,
                    'error': str(result),
                    'transcription': None
                })
            else:
                transcriptions.append({
                    'segment_index': segments[i]['index'],
                    'success': result is not None,
                    'error': None,
                    'transcription': result
                })
        
        return transcriptions
