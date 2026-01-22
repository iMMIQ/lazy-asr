"""
File type detection utilities

Uses the filetype library to detect media file types based on file content (magic bytes).
No hardcoded extensions - relies entirely on filetype library.
"""

import os
from typing import Optional, Tuple
import filetype


def get_file_type(file_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Detect file type using filetype library based on file content
    
    Args:
        file_path: Path to the file to analyze
        
    Returns:
        Tuple of (type_category, mime_type) where:
        - type_category: 'audio', 'video', or None
        - mime_type: MIME type string or None
    """
    try:
        # Check if file exists and is readable
        if not os.path.exists(file_path):
            return None, None
            
        if not os.path.isfile(file_path):
            return None, None
            
        # Use filetype to detect from file content (magic bytes)
        kind = filetype.guess(file_path)
        
        if kind is None:
            # filetype cannot detect this file type
            return None, None
            
        # Map filetype types to our categories
        if kind.mime.startswith('audio/'):
            return 'audio', kind.mime
        elif kind.mime.startswith('video/'):
            return 'video', kind.mime
            
        return None, None
        
    except Exception as e:
        # On any error, return None
        return None, None


def is_audio_file(file_path: str) -> bool:
    """
    Check if file is an audio file
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if file is audio, False otherwise
    """
    file_type, _ = get_file_type(file_path)
    return file_type == 'audio'


def is_video_file(file_path: str) -> bool:
    """
    Check if file is a video file
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if file is video, False otherwise
    """
    file_type, _ = get_file_type(file_path)
    return file_type == 'video'


def is_media_file(file_path: str) -> bool:
    """
    Check if file is a media file (audio or video)
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if file is media, False otherwise
    """
    file_type, _ = get_file_type(file_path)
    return file_type in ('audio', 'video')
