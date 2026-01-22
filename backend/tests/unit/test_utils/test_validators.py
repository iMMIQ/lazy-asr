"""
Input validation tests - TDD Third Cycle
"""
import pytest
from app.core.exceptions import ValidationError


class TestInputValidators:
    """Test input validation utilities"""

    def test_validate_asr_method_accepts_valid_method(self):
        """Should accept valid ASR methods"""
        from app.utils.validators import validate_asr_method

        # Should not raise
        result = validate_asr_method("local-whisper")
        assert result == "local-whisper"

    def test_validate_asr_method_rejects_invalid_method(self):
        """Should reject invalid ASR methods"""
        from app.utils.validators import validate_asr_method

        with pytest.raises(ValidationError):
            validate_asr_method("invalid-method")

    def test_validate_output_formats_accepts_valid_formats(self):
        """Should accept valid output formats"""
        from app.utils.validators import validate_output_formats

        # Should not raise
        result = validate_output_formats("srt,vtt,lrc")
        assert result == ["srt", "vtt", "lrc"]

    def test_validate_output_formats_accepts_single_format(self):
        """Should accept single output format"""
        from app.utils.validators import validate_output_formats

        result = validate_output_formats("srt")
        assert result == ["srt"]

    def test_validate_output_formats_rejects_invalid_format(self):
        """Should reject invalid output formats"""
        from app.utils.validators import validate_output_formats

        with pytest.raises(ValidationError):
            validate_output_formats("srt,invalid,lrc")

    def test_validate_file_path_checks_empty_path(self):
        """Should reject empty file paths"""
        from app.utils.validators import validate_file_path

        with pytest.raises(ValidationError):
            validate_file_path("")

    def test_validate_file_path_checks_none(self):
        """Should reject None file paths"""
        from app.utils.validators import validate_file_path

        with pytest.raises(ValidationError):
            validate_file_path(None)

    def test_validate_language_code_accepts_valid_code(self):
        """Should accept valid language codes"""
        from app.utils.validators import validate_language_code

        result = validate_language_code("zh")
        assert result == "zh"

    def test_validate_language_code_accepts_auto(self):
        """Should accept 'auto' for auto-detection"""
        from app.utils.validators import validate_language_code

        result = validate_language_code("auto")
        assert result == "auto"

    def test_validate_language_code_rejects_invalid_code(self):
        """Should reject invalid language codes"""
        from app.utils.validators import validate_language_code

        with pytest.raises(ValidationError):
            validate_language_code("invalid-language-code")

    def test_sanitize_string_removes_dangerous_chars(self):
        """Should remove dangerous characters from strings"""
        from app.utils.validators import sanitize_string

        result = sanitize_string("../../../etc/passwd")
        # Should remove or escape path traversal characters
        assert ".." not in result

    def test_validate_scan_request_positive_max_files(self):
        """Should require positive max_files value"""
        from app.utils.validators import validate_scan_max_files

        with pytest.raises(ValidationError):
            validate_scan_max_files(-1)

        with pytest.raises(ValidationError):
            validate_scan_max_files(0)

        # Should not raise for positive values
        validate_scan_max_files(1)
        validate_scan_max_files(100)
