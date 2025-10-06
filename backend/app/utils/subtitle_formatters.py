import os
from typing import List, Dict, Any


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


def format_timestamp_vtt(seconds: float) -> str:
    """
    Format seconds to VTT timestamp format (HH:MM:SS.mmm)

    Args:
        seconds: Seconds

    Returns:
        VTT timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def format_timestamp_lrc(seconds: float) -> str:
    """
    Format seconds to LRC timestamp format [MM:SS.mm]

    Args:
        seconds: Seconds

    Returns:
        LRC timestamp string
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds - int(seconds)) * 100)

    return f"[{minutes:02d}:{secs:02d}.{centiseconds:02d}]"


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


def generate_vtt_content(subtitles: List[Dict]) -> str:
    """
    Generate VTT file content

    Args:
        subtitles: List of subtitles

    Returns:
        VTT file content string
    """
    vtt_content = "WEBVTT\n\n"

    for i, subtitle in enumerate(subtitles, 1):
        # Convert timestamp format
        start_seconds = time_string_to_seconds(subtitle['start'])
        end_seconds = time_string_to_seconds(subtitle['end'])

        start_vtt = format_timestamp_vtt(start_seconds)
        end_vtt = format_timestamp_vtt(end_seconds)

        vtt_content += f"{i}\n"
        vtt_content += f"{start_vtt} --> {end_vtt}\n"
        vtt_content += f"{subtitle['text']}\n\n"

    return vtt_content


def generate_lrc_content(subtitles: List[Dict]) -> str:
    """
    Generate LRC file content

    Args:
        subtitles: List of subtitles

    Returns:
        LRC file content string
    """
    lrc_content = ""

    for subtitle in subtitles:
        # Convert timestamp format
        start_seconds = time_string_to_seconds(subtitle['start'])
        lrc_timestamp = format_timestamp_lrc(start_seconds)

        lrc_content += f"{lrc_timestamp}{subtitle['text']}\n"

    return lrc_content


def generate_txt_content(subtitles: List[Dict]) -> str:
    """
    Generate TXT file content

    Args:
        subtitles: List of subtitles

    Returns:
        TXT file content string
    """
    txt_content = ""

    for subtitle in subtitles:
        txt_content += f"{subtitle['text']}\n"

    return txt_content


def generate_subtitle_files(
    subtitles: List[Dict], base_output_path: str, output_formats: List[str] = None
) -> Dict[str, str]:
    """
    Generate multiple format subtitle files

    Args:
        subtitles: List of subtitles
        base_output_path: Base output path (without extension)
        output_formats: Output format list, defaults to ['srt']

    Returns:
        Dictionary containing format to file path mapping
    """
    if output_formats is None:
        output_formats = ['srt']

    # Validate supported formats
    supported_formats = ['srt', 'vtt', 'lrc', 'txt']
    invalid_formats = [fmt for fmt in output_formats if fmt not in supported_formats]
    if invalid_formats:
        raise ValueError(f"Unsupported output formats: {invalid_formats}")

    output_files = {}

    # Sort subtitles by time
    subtitles.sort(key=lambda x: time_string_to_seconds(x['start'].replace(',', '.')))

    for fmt in output_formats:
        if fmt == 'srt':
            content = generate_srt_content(subtitles)
        elif fmt == 'vtt':
            content = generate_vtt_content(subtitles)
        elif fmt == 'lrc':
            content = generate_lrc_content(subtitles)
        elif fmt == 'txt':
            content = generate_txt_content(subtitles)
        else:
            continue

        output_path = f"{base_output_path}.{fmt}"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        output_files[fmt] = output_path

    return output_files


# Backward compatible function
def generate_srt_content_legacy(subtitles: List[Dict]) -> str:
    """Backward compatible SRT generation function"""
    return generate_srt_content(subtitles)
