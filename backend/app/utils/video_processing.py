import os
import tempfile
from typing import Tuple, Optional, List
import ffmpeg
from app.core.logger import get_logger

logger = get_logger(__name__)


def detect_media_type(file_path: str) -> str:
    """
    Detect the type of media file (video or audio)

    Args:
        file_path: Path to the media file

    Returns:
        'video', 'audio', or 'unknown'
    """
    try:
        # Use ffprobe to get file information
        probe = ffmpeg.probe(file_path)
        format_info = probe.get('format', {})
        streams = probe.get('streams', [])

        # Check if there are video streams
        has_video = any(stream.get('codec_type') == 'video' for stream in streams)
        has_audio = any(stream.get('codec_type') == 'audio' for stream in streams)

        if has_video:
            return 'video'
        elif has_audio:
            return 'audio'
        else:
            return 'unknown'

    except Exception as e:
        logger.error(f"Failed to detect media type for {file_path}: {e}")
        return 'unknown'


def get_supported_formats() -> dict:
    """
    Get list of supported media formats

    Returns:
        Dictionary with supported video and audio formats
    """
    return {
        'video': ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', 'm4v', '3gp', 'mpg', 'mpeg', 'ts', 'mts', 'm2ts'],
        'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma', 'opus', 'aiff', 'amr', 'ac3', 'dts'],
    }


def extract_audio_from_video(video_path: str, output_path: Optional[str] = None) -> str:
    """
    Extract audio from video file using ffmpeg

    Args:
        video_path: Path to the video file
        output_path: Optional output path for extracted audio

    Returns:
        Path to the extracted audio file
    """
    try:
        if output_path is None:
            # Create temporary file for extracted audio
            temp_dir = tempfile.gettempdir()
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(temp_dir, f"{base_name}_extracted_audio.wav")

        logger.info(f"Extracting audio from video: {video_path}")
        logger.info(f"Output audio file: {output_path}")

        # Use ffmpeg to extract audio
        (
            ffmpeg.input(video_path)
            .output(output_path, acodec='pcm_s16le', ac=1, ar='16000')
            .overwrite_output()
            .run(quiet=True)
        )

        logger.info(f"Successfully extracted audio to: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to extract audio from {video_path}: {e}")
        raise


def convert_audio_format(input_path: str, output_path: str, sample_rate: int = 16000, channels: int = 1) -> str:
    """
    Convert audio file to standard format for ASR processing

    Args:
        input_path: Path to input audio file
        output_path: Path for output audio file
        sample_rate: Target sample rate (default 16000)
        channels: Target number of channels (default 1)

    Returns:
        Path to the converted audio file
    """
    try:
        logger.info(f"Converting audio format: {input_path} -> {output_path}")

        # Use ffmpeg to convert audio format
        (
            ffmpeg.input(input_path)
            .output(output_path, acodec='pcm_s16le', ac=channels, ar=str(sample_rate))
            .overwrite_output()
            .run(quiet=True)
        )

        logger.info(f"Successfully converted audio to: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to convert audio format for {input_path}: {e}")
        raise


def get_media_duration(file_path: str) -> float:
    """
    Get duration of media file in seconds

    Args:
        file_path: Path to the media file

    Returns:
        Duration in seconds
    """
    try:
        probe = ffmpeg.probe(file_path)
        format_info = probe.get('format', {})
        duration = float(format_info.get('duration', 0))
        return duration
    except Exception as e:
        logger.error(f"Failed to get duration for {file_path}: {e}")
        return 0.0


def prepare_media_for_asr(media_path: str, output_dir: str) -> Tuple[str, str]:
    """
    Prepare media file for ASR processing

    Args:
        media_path: Path to the media file
        output_dir: Directory to store processed files

    Returns:
        Tuple of (processed_audio_path, media_type)
    """
    try:
        # Detect media type
        media_type = detect_media_type(media_path)
        logger.info(f"Detected media type: {media_type} for {media_path}")

        # Create output filename
        base_name = os.path.splitext(os.path.basename(media_path))[0]
        processed_audio_path = os.path.join(output_dir, f"{base_name}_processed.wav")

        if media_type == 'video':
            # Extract audio from video
            processed_audio_path = extract_audio_from_video(media_path, processed_audio_path)
        elif media_type == 'audio':
            # Convert audio to standard format
            processed_audio_path = convert_audio_format(media_path, processed_audio_path)
        else:
            raise ValueError(f"Unsupported media type: {media_type}")

        return processed_audio_path, media_type

    except Exception as e:
        logger.error(f"Failed to prepare media for ASR: {e}")
        raise


def validate_media_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate if media file is supported and accessible

    Args:
        file_path: Path to the media file

    Returns:
        Tuple of (is_valid, message)
    """
    try:
        if not os.path.exists(file_path):
            return False, "File does not exist"

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "File is empty"

        # Check if file is too large (500MB limit)
        if file_size > 500 * 1024 * 1024:
            return False, "File too large (max 500MB)"

        # Try to probe the file
        probe = ffmpeg.probe(file_path)
        format_info = probe.get('format', {})

        if not format_info:
            return False, "Unable to read file format"

        # Check if there's at least one audio stream
        streams = probe.get('streams', [])
        has_audio = any(stream.get('codec_type') == 'audio' for stream in streams)

        if not has_audio:
            return False, "No audio stream found in file"

        return True, "File is valid"

    except Exception as e:
        return False, f"File validation failed: {str(e)}"
