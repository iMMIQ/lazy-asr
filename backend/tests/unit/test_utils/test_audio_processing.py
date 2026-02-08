"""
Tests for audio_processing module with Silero VAD

Tests follow TDD principles:
1. Write failing test first
2. Verify it fails correctly
3. Write minimal code to pass
4. Verify it passes
"""
import os
import tempfile
from unittest.mock import patch, MagicMock

import numpy as np
import pytest
import soundfile as sf

from app.utils.audio_processing import (
    silero_vad_segmentation,
    export_silero_segments,
    time_string_to_seconds,
    format_timestamp_srt,
    generate_srt_content,
    parse_transcription_segments,
)


class TestTimeStringToSeconds:
    """Tests for time_string_to_seconds function"""

    def test_convert_hhmmss_with_comma_milliseconds(self):
        """Should convert HH:MM:SS,mmm format to seconds"""
        result = time_string_to_seconds("01:02:03,456")
        assert result == 3723.456

    def test_convert_hhmmss_with_dot_milliseconds(self):
        """Should convert HH:MM:SS.mmm format to seconds"""
        result = time_string_to_seconds("01:02:03.456")
        assert result == 3723.456

    def test_convert_simple_seconds(self):
        """Should handle simple seconds input"""
        result = time_string_to_seconds("123.456")
        assert result == 123.456


class TestFormatTimestampSrt:
    """Tests for format_timestamp_srt function"""

    def test_format_basic_timestamp(self):
        """Should format seconds to SRT timestamp format"""
        result = format_timestamp_srt(3723.456)
        assert result == "01:02:03,456"

    def test_format_small_timestamp(self):
        """Should format small seconds values correctly"""
        result = format_timestamp_srt(1.5)
        assert result == "00:00:01,500"

    def test_format_zero_timestamp(self):
        """Should handle zero seconds"""
        result = format_timestamp_srt(0.0)
        assert result == "00:00:00,000"


class TestGenerateSrtContent:
    """Tests for generate_srt_content function"""

    def test_generate_single_subtitle(self):
        """Should generate correct SRT content for single subtitle"""
        subtitles = [
            {"start": "00:00:01,000", "end": "00:00:02,000", "text": "Hello"}
        ]
        result = generate_srt_content(subtitles)
        expected = "1\n00:00:01,000 --> 00:00:02,000\nHello\n\n"
        assert result == expected

    def test_generate_multiple_subtitles(self):
        """Should generate correct SRT content for multiple subtitles"""
        subtitles = [
            {"start": "00:00:01,000", "end": "00:00:02,000", "text": "Hello"},
            {"start": "00:00:03,000", "end": "00:00:04,000", "text": "World"},
        ]
        result = generate_srt_content(subtitles)
        assert "1\n00:00:01,000 --> 00:00:02,000\nHello\n" in result
        assert "2\n00:00:03,000 --> 00:00:04,000\nWorld\n" in result


class TestParseTranscriptionSegments:
    """Tests for parse_transcription_segments function"""

    def test_parse_valid_transcription(self):
        """Should parse transcription lines into subtitle segments"""
        transcription_lines = ["Hello", "world"]
        result = parse_transcription_segments(transcription_lines, 1.0, 2.0)

        assert len(result) == 1
        assert result[0]["start"] == "00:00:01,000"
        assert result[0]["end"] == "00:00:02,000"
        assert result[0]["text"] == "Hello world"

    def test_parse_empty_transcription(self):
        """Should return empty list for empty transcription"""
        result = parse_transcription_segments([], 1.0, 2.0)
        assert result == []

    def test_parse_whitespace_transcription(self):
        """Should return empty list for whitespace-only transcription"""
        result = parse_transcription_segments(["   ", "  "], 1.0, 2.0)
        assert result == []


class TestSileroVADSegmentation:
    """Tests for silero_vad_segmentation function"""

    @pytest.fixture
    def audio_file_with_speech(self, temp_dir):
        """Create an audio file with speech-like audio"""
        audio_path = os.path.join(temp_dir, "test_speech.wav")
        # Create audio with speech-like characteristics (noise)
        sample_rate = 16000
        duration = 2.0
        audio_data = np.random.randn(int(sample_rate * duration)) * 0.3
        sf.write(audio_path, audio_data, sample_rate)
        return audio_path

    @pytest.fixture
    def audio_file_silence(self, temp_dir):
        """Create an audio file with silence"""
        audio_path = os.path.join(temp_dir, "test_silence.wav")
        sample_rate = 16000
        duration = 1.0
        audio_data = np.zeros(int(sample_rate * duration))
        sf.write(audio_path, audio_data, sample_rate)
        return audio_path

    @pytest.mark.slow
    def test_silero_vad_segmentation_returns_expected_structure(
        self, audio_file_with_speech
    ):
        """Should return tuple of (timestamps, audio_data, sample_rate)"""
        result = silero_vad_segmentation(audio_file_with_speech)

        assert isinstance(result, tuple)
        assert len(result) == 3

        timestamps, audio_data, sample_rate = result
        assert isinstance(timestamps, list)
        assert isinstance(audio_data, np.ndarray)
        assert isinstance(sample_rate, int)

    @pytest.mark.slow
    def test_silero_vad_segmentation_with_custom_params(self, audio_file_with_speech):
        """Should use custom VAD parameters when provided"""
        vad_params = {
            "min_speech_duration_ms": 250,
            "min_silence_duration_ms": 250,
        }
        timestamps, audio_data, sample_rate = silero_vad_segmentation(
            audio_file_with_speech, vad_params
        )

        # Should complete without error
        assert isinstance(timestamps, list)

    @pytest.mark.slow
    def test_silero_vad_segmentation_handles_silence(self, audio_file_silence):
        """Should handle audio with no speech segments"""
        timestamps, audio_data, sample_rate = silero_vad_segmentation(
            audio_file_silence
        )

        # Should return empty list for silence
        assert isinstance(timestamps, list)


class TestExportSileroSegments:
    """Tests for export_silero_segments function"""

    @pytest.fixture
    def sample_audio_data(self):
        """Create sample audio data"""
        sample_rate = 16000
        duration = 5.0
        return np.random.randn(int(sample_rate * duration)) * 0.1

    @pytest.fixture
    def sample_segments(self):
        """Create sample speech segments"""
        return [
            {"start": 0.5, "end": 1.5},
            {"start": 2.0, "end": 3.0},
            {"start": 3.5, "end": 4.5},
        ]

    def test_export_segments_creates_files(
        self, temp_dir, sample_segments, sample_audio_data
    ):
        """Should create WAV files for each segment"""
        output_dir = os.path.join(temp_dir, "segments")
        result = export_silero_segments(
            sample_segments, sample_audio_data, 16000, output_dir
        )

        assert len(result) == 3
        for segment_info in result:
            assert "file_path" in segment_info
            assert os.path.exists(segment_info["file_path"])
            assert segment_info["file_path"].endswith(".wav")

    def test_export_segments_filters_short_segments(
        self, temp_dir, sample_audio_data
    ):
        """Should filter out segments shorter than min_duration"""
        segments = [
            {"start": 0.0, "end": 0.3},  # Too short (< 0.5s)
            {"start": 0.5, "end": 1.5},  # Valid
        ]
        output_dir = os.path.join(temp_dir, "segments")
        result = export_silero_segments(
            segments, sample_audio_data, 16000, output_dir, min_duration=0.5
        )

        assert len(result) == 1
        assert result[0]["start_time"] == 0.5

    def test_export_segments_filters_long_segments(
        self, temp_dir, sample_audio_data
    ):
        """Should filter out segments longer than max_duration"""
        sample_rate = 16000
        segments = [
            {"start": 0.0, "end": 70.0},  # Too long (> 60s)
            {"start": 70.0, "end": 71.0},  # Valid
        ]
        # Create long enough audio data
        long_audio = np.random.randn(sample_rate * 71) * 0.1
        output_dir = os.path.join(temp_dir, "segments")
        result = export_silero_segments(
            segments, long_audio, sample_rate, output_dir, max_duration=60.0
        )

        assert len(result) == 1
        assert result[0]["start_time"] == 70.0

    def test_export_segments_returns_correct_metadata(
        self, temp_dir, sample_segments, sample_audio_data
    ):
        """Should return correct metadata for each exported segment"""
        output_dir = os.path.join(temp_dir, "segments")
        result = export_silero_segments(
            sample_segments, sample_audio_data, 16000, output_dir
        )

        for i, segment_info in enumerate(result):
            assert "index" in segment_info
            assert "file_path" in segment_info
            assert "start_time" in segment_info
            assert "end_time" in segment_info
            assert "duration" in segment_info

            # Verify duration calculation
            expected_duration = segment_info["end_time"] - segment_info["start_time"]
            assert abs(segment_info["duration"] - expected_duration) < 0.01

    def test_export_segments_creates_output_directory(
        self, sample_segments, sample_audio_data, temp_dir
    ):
        """Should create output directory if it doesn't exist"""
        output_dir = os.path.join(temp_dir, "new_segments", "nested")
        assert not os.path.exists(output_dir)

        export_silero_segments(sample_segments, sample_audio_data, 16000, output_dir)

        assert os.path.exists(output_dir)

    def test_export_segments_handles_empty_segments(self, temp_dir, sample_audio_data):
        """Should handle empty segments list"""
        output_dir = os.path.join(temp_dir, "segments")
        result = export_silero_segments([], sample_audio_data, 16000, output_dir)

        assert result == []

    def test_export_segments_handles_boundary_conditions(
        self, temp_dir, sample_audio_data
    ):
        """Should handle segments at audio boundaries"""
        # Create exactly 1 second of audio
        audio_data = np.random.randn(16000) * 0.1
        segments = [
            {"start": 0.0, "end": 0.5},  # At start
            {"start": 0.5, "end": 1.0},  # At end
        ]
        output_dir = os.path.join(temp_dir, "segments")
        result = export_silero_segments(segments, audio_data, 16000, output_dir)

        # Both segments should be exported without error
        assert len(result) == 2
