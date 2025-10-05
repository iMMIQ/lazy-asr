import os
import soundfile as sf
from typing import List, Tuple, Dict, Any
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps


def silero_vad_segmentation(audio_path: str, vad_params: Dict[str, Any] = None) -> Tuple[List[Dict], Any, int]:
    """
    使用Silero VAD进行语音活动检测和音频分段

    Args:
        audio_path: 音频文件路径
        vad_params: VAD参数字典

    Returns:
        Tuple of (speech_timestamps, audio_data, sample_rate)
    """
    if vad_params is None:
        vad_params = {'min_speech_duration_ms': 500, 'min_silence_duration_ms': 500}

    print("🎵 加载Silero VAD模型...")
    model = load_silero_vad()

    print("📁 读取音频文件...")
    wav = read_audio(audio_path)

    print("🔍 开始VAD语音检测...")
    speech_timestamps = get_speech_timestamps(
        wav,
        model,
        **vad_params,
        return_seconds=True,
    )

    print(f"✅ Silero VAD检测完成，找到 {len(speech_timestamps)} 个语音段")

    # 使用soundfile读取音频用于后续处理
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
    导出Silero VAD检测到的语音段

    Args:
        segments: 语音段列表
        original_audio: 原始音频数据
        sample_rate: 采样率
        output_dir: 输出目录
        min_duration: 最小段时长
        max_duration: 最大段时长

    Returns:
        导出的语音段信息列表
    """
    os.makedirs(output_dir, exist_ok=True)

    exported_segments = []

    for i, segment in enumerate(segments):
        start_time = segment['start']
        end_time = segment['end']
        duration = segment['end'] - segment['start']

        # 过滤太短或太长的段
        if duration < min_duration or duration > max_duration:
            continue

        # 转换为样本点
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)

        # 确保不超出音频范围
        start_sample = max(0, min(start_sample, len(original_audio)))
        end_sample = max(0, min(end_sample, len(original_audio)))

        if end_sample > start_sample:
            # 提取音频段
            segment_audio = original_audio[start_sample:end_sample]
            output_path = os.path.join(output_dir, f"silero_segment_{i+1:04d}.wav")

            # 使用soundfile保存音频
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

            print(f"💾 导出段 {i+1:04d}: {start_time:.2f}s - {end_time:.2f}s " f"(时长: {duration:.2f}s)")

    return exported_segments


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


def parse_transcription_segments(
    transcription_lines: List[str], segment_start_time: float, segment_end_time: float
) -> List[Dict]:
    """
    解析转录结果，使用VAD分段的时间戳

    Args:
        transcription_lines: 转录结果行列表
        segment_start_time: 分段开始时间
        segment_end_time: 分段结束时间

    Returns:
        调整后的字幕段列表
    """
    adjusted_segments = []

    # 检查转录结果是否为空
    if not transcription_lines:
        return adjusted_segments

    # 合并所有文本行
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
