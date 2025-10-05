from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
from tqdm import tqdm
from app.core.config import settings


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
        Transcribe multiple segments concurrently with concurrency control and progress bar

        Args:
            segments: List of segment dictionaries

        Returns:
            List of transcription results with detailed error information
        """
        semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_TASKS)
        
        async def transcribe_with_semaphore(segment: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                try:
                    transcription = await self.transcribe_segment(segment['file_path'], segment)
                    return {
                        'segment_index': segment['index'],
                        'success': transcription is not None,
                        'error': None,
                        'error_type': None,
                        'transcription': transcription,
                        'segment_info': segment  # Include full segment info for error reporting
                    }
                except Exception as e:
                    error_type = type(e).__name__
                    error_message = str(e)
                    return {
                        'segment_index': segment['index'],
                        'success': False,
                        'error': error_message,
                        'error_type': error_type,
                        'transcription': None,
                        'segment_info': segment  # Include full segment info for error reporting
                    }
        
        # Create progress bar
        print(f"\n🎯 开始并发转录 (最大并发数: {settings.MAX_CONCURRENT_TASKS})...")
        progress_bar = tqdm(
            total=len(segments),
            desc="转录进度",
            unit="段",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )
        
        # Process segments with concurrency control
        tasks = []
        for segment in segments:
            task = asyncio.create_task(transcribe_with_semaphore(segment))
            task.add_done_callback(lambda _: progress_bar.update(1))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
        # Close progress bar
        progress_bar.close()
        
        # Print summary statistics
        successful = sum(1 for r in results if r['success'])
        failed = sum(1 for r in results if not r['success'])
        
        print(f"\n📊 转录统计:")
        print(f"   成功: {successful}/{len(segments)} 段")
        print(f"   失败: {failed}/{len(segments)} 段")
        
        return results
