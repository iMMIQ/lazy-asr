import os
from typing import List, Dict, Any


def format_timestamp_srt(seconds: float) -> str:
    """
    将秒数格式化为SRT时间戳格式 (HH:MM:SS,mmm)

    Args:
        seconds: 秒数

    Returns:
        SRT时间戳字符串
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """
    将秒数格式化为VTT时间戳格式 (HH:MM:SS.mmm)

    Args:
        seconds: 秒数

    Returns:
        VTT时间戳字符串
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def format_timestamp_lrc(seconds: float) -> str:
    """
    将秒数格式化为LRC时间戳格式 [MM:SS.mm]

    Args:
        seconds: 秒数

    Returns:
        LRC时间戳字符串
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds - int(seconds)) * 100)

    return f"[{minutes:02d}:{secs:02d}.{centiseconds:02d}]"


def time_string_to_seconds(time_str: str) -> float:
    """
    将时间字符串转换为秒数

    Args:
        time_str: 时间字符串 (HH:MM:SS,mmm 或 HH:MM:SS.mmm)

    Returns:
        秒数
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
    生成SRT文件内容

    Args:
        subtitles: 字幕列表

    Returns:
        SRT文件内容字符串
    """
    srt_content = ""

    for i, subtitle in enumerate(subtitles, 1):
        srt_content += f"{i}\n"
        srt_content += f"{subtitle['start']} --> {subtitle['end']}\n"
        srt_content += f"{subtitle['text']}\n\n"

    return srt_content


def generate_vtt_content(subtitles: List[Dict]) -> str:
    """
    生成VTT文件内容

    Args:
        subtitles: 字幕列表

    Returns:
        VTT文件内容字符串
    """
    vtt_content = "WEBVTT\n\n"

    for i, subtitle in enumerate(subtitles, 1):
        # 转换时间戳格式
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
    生成LRC文件内容

    Args:
        subtitles: 字幕列表

    Returns:
        LRC文件内容字符串
    """
    lrc_content = ""

    for subtitle in subtitles:
        # 转换时间戳格式
        start_seconds = time_string_to_seconds(subtitle['start'])
        lrc_timestamp = format_timestamp_lrc(start_seconds)

        lrc_content += f"{lrc_timestamp}{subtitle['text']}\n"

    return lrc_content


def generate_txt_content(subtitles: List[Dict]) -> str:
    """
    生成TXT文件内容

    Args:
        subtitles: 字幕列表

    Returns:
        TXT文件内容字符串
    """
    txt_content = ""

    for subtitle in subtitles:
        txt_content += f"{subtitle['text']}\n"

    return txt_content


def generate_subtitle_files(
    subtitles: List[Dict], base_output_path: str, output_formats: List[str] = None
) -> Dict[str, str]:
    """
    生成多种格式的字幕文件

    Args:
        subtitles: 字幕列表
        base_output_path: 基础输出路径（不含扩展名）
        output_formats: 输出格式列表，默认为 ['srt']

    Returns:
        字典，包含格式到文件路径的映射
    """
    if output_formats is None:
        output_formats = ['srt']

    # 验证支持的格式
    supported_formats = ['srt', 'vtt', 'lrc', 'txt']
    invalid_formats = [fmt for fmt in output_formats if fmt not in supported_formats]
    if invalid_formats:
        raise ValueError(f"不支持的输出格式: {invalid_formats}")

    output_files = {}

    # 按时间排序字幕
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


# 向后兼容的函数
def generate_srt_content_legacy(subtitles: List[Dict]) -> str:
    """向后兼容的SRT生成函数"""
    return generate_srt_content(subtitles)
