import os
import soundfile as sf
from typing import List, Tuple, Dict, Any
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
from app.core.logger import get_logger

logger = get_logger(__name__)


def silero_vad_segmentation(audio_path: str, vad_params: Dict[str, Any] = None) -> Tuple[List[Dict], Any, int]:
    """
    Perform speech activity detection and audio segmentation using Silero VAD

    Args:
        audio_path: Path to the audio file
        vad_params: VAD parameters dictionary

    Returns:
        Tuple of (speech_timestamps, audio_data, sample_rate)
    """
    if vad_params is None:
        vad_params = {'min_speech_duration_ms': 500, 'min_silence_duration_ms': 500}

    logger.info("Loading Silero VAD model...")
    model = load_silero_vad()

    logger.info("Reading audio file...")
    wav = read_audio(audio_path)

    logger.info("Starting VAD speech detection...")
    speech_timestamps = get_speech_timestamps(
        wav,
        model,
        **vad_params,
        return_seconds=True,
    )

    logger.info(f"Silero VAD detection completed, found {len(speech_timestamps)} speech segments")

    # Use soundfile to read audio for subsequent processing
    audio_data, sample_rate = sf.read(audio_path)

    return speech_timestamps, audio_data, sample_rate


def export_silero_segments(
    segments: List[Dict],
    original_audio: Any,
    sample_rate: int,
    output_dir: str = "silero_segments",
    min_duration: float = 0.5,
    max_duration: float = 60.0,
) -> List[Dict]:
    """
    Export speech segments detected by Silero VAD

    Args:
        segments: List of speech segments
        original_audio: Original audio data
        sample_rate: Sample rate
        output_dir: Output directory
        min_duration: Minimum segment duration
        max_duration: Maximum segment duration

    Returns:
        List of exported speech segment information
    """
    os.makedirs(output_dir, exist_ok=True)

    exported_segments = []

    for i, segment in enumerate(segments):
        start_time = segment['start']
        end_time = segment['end']
        duration = segment['end'] - segment['start']

        # Filter segments that are too short or too long
        if duration < min_duration or duration > max_duration:
            continue

        # Convert to sample points
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)

        # Ensure within audio bounds
        start_sample = max(0, min(start_sample, len(original_audio)))
        end_sample = max(0, min(end_sample, len(original_audio)))

        if end_sample > start_sample:
            # Extract audio segment
            segment_audio = original_audio[start_sample:end_sample]
            output_path = os.path.join(output_dir, f"silero_segment_{i+1:04d}.wav")

            # Use soundfile to save audio
            sf.write(output_path, segment_audio, sample_rate)

            exported_segments.append(
                {
                    'index': i + 1,
                    'file_path': output_path,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': duration,
                }
            )

            logger.info(f"Exported segment {i+1:04d}: {start_time:.2f}s - {end_time:.2f}s (duration: {duration:.2f}s)")

    return exported_segments


def time_string_to_seconds(time_str: str) -> float:
    """
    Convert time string to seconds

    Args:
        time_str: Time string (HH:MM:SS,mmm or HH:MM:SS.mmm)

    Returns:
        Seconds as float
    """
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')

    if len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    else:
        return float(time_str)


def format_timestamp_srt(seconds: float) -> str:
    """
    Format seconds to SRT timestamp format (HH:MM:SS,mmm)

    Args:
        seconds: Seconds

    Returns:
        SRT timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt_content(subtitles: List[Dict]) -> str:
    """
    Generate SRT file content

    Args:
        subtitles: List of subtitles

    Returns:
        SRT file content string
    """
    srt_content = ""

    for i, subtitle in enumerate(subtitles, 1):
        srt_content += f"{i}\n"
        srt_content += f"{subtitle['start']} --> {subtitle['end']}\n"
        srt_content += f"{subtitle['text']}\n\n"

    return srt_content


def parse_transcription_segments(
    transcription_lines: List[str], segment_start_time: float, segment_end_time: float
) -> List[Dict]:
    """
    Parse transcription results using VAD segment timestamps

    Args:
        transcription_lines: List of transcription result lines
        segment_start_time: Segment start time
        segment_end_time: Segment end time

    Returns:
        List of adjusted subtitle segments
    """
    adjusted_segments = []

    # Check if transcription result is empty
    if not transcription_lines:
        return adjusted_segments

    # Merge all text lines
    full_text = ' '.join(transcription_lines).strip()

    if full_text:
        adjusted_segments.append(
            {
                'start': format_timestamp_srt(segment_start_time),
                'end': format_timestamp_srt(segment_end_time),
                'text': full_text,
            }
        )

    return adjusted_segments
