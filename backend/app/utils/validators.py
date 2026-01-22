"""
Input validation utilities for API endpoints
"""
import re
from typing import List, Optional, Union

from app.core.config import settings
from app.core.exceptions import ValidationError


# Valid output formats for subtitles
VALID_OUTPUT_FORMATS = {"srt", "vtt", "lrc", "txt"}

# Common language codes (ISO 639-1)
VALID_LANGUAGE_CODES = {
    "auto",  # Auto-detect
    "zh",  # Chinese
    "en",  # English
    "yue",  # Cantonese
    "ja",  # Japanese
    "ko",  # Korean
    "es",  # Spanish
    "fr",  # French
    "de",  # German
    "it",  # Italian
    "pt",  # Portuguese
    "ru",  # Russian
    "ar",  # Arabic
    "hi",  # Hindi
    "th",  # Thai
    "vi",  # Vietnamese
}


def validate_asr_method(method: str) -> str:
    """
    Validate ASR method name

    Args:
        method: ASR method name to validate

    Returns:
        The validated method name

    Raises:
        ValidationError: If method is not valid
    """
    if not method or not method.strip():
        raise ValidationError("ASR method cannot be empty", field="asr_method")

    method = method.strip().lower()

    if method not in settings.AVAILABLE_ASR_METHODS:
        raise ValidationError(
            f"Invalid ASR method: {method}. Available: {', '.join(settings.AVAILABLE_ASR_METHODS)}",
            field="asr_method"
        )

    return method


def validate_output_formats(formats: Union[str, List[str]]) -> List[str]:
    """
    Validate output format list

    Args:
        formats: Comma-separated string or list of formats

    Returns:
        List of validated format names

    Raises:
        ValidationError: If any format is invalid
    """
    if not formats:
        # Default to srt
        return ["srt"]

    # Parse formats
    if isinstance(formats, str):
        formats = [f.strip() for f in formats.split(",") if f.strip()]
    elif isinstance(formats, list):
        formats = [f.strip() for f in formats if f.strip()]
    else:
        raise ValidationError("Output formats must be a string or list", field="output_formats")

    if not formats:
        return ["srt"]

    # Validate each format
    for fmt in formats:
        fmt_lower = fmt.lower()
        if fmt_lower not in VALID_OUTPUT_FORMATS:
            raise ValidationError(
                f"Invalid output format: {fmt}. Valid: {', '.join(sorted(VALID_OUTPUT_FORMATS))}",
                field="output_formats"
            )

    return [f.lower() for f in formats]


def validate_file_path(file_path: Optional[str]) -> str:
    """
    Validate that a file path is not empty

    Args:
        file_path: File path to validate

    Returns:
        The validated file path

    Raises:
        ValidationError: If file path is invalid
    """
    if not file_path or not isinstance(file_path, str) or not file_path.strip():
        raise ValidationError("File path cannot be empty", field="file_path")

    return file_path.strip()


def validate_language_code(language: str) -> str:
    """
    Validate language code

    Args:
        language: Language code to validate

    Returns:
        The validated language code

    Raises:
        ValidationError: If language code is invalid
    """
    if not language or not language.strip():
        raise ValidationError("Language code cannot be empty", field="language")

    language = language.strip().lower()

    if language not in VALID_LANGUAGE_CODES:
        raise ValidationError(
            f"Invalid language code: {language}. Valid codes: {', '.join(sorted(VALID_LANGUAGE_CODES))}",
            field="language"
        )

    return language


def sanitize_string(input_str: str, max_length: int = 1000) -> str:
    """
    Sanitize a string input by removing potentially dangerous characters

    Args:
        input_str: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        ValidationError: If string is too long
    """
    if not isinstance(input_str, str):
        raise ValidationError("Input must be a string")

    if len(input_str) > max_length:
        raise ValidationError(f"String exceeds maximum length of {max_length}")

    # Remove null bytes
    result = input_str.replace("\x00", "")

    # Remove path traversal patterns
    result = result.replace("../", "").replace("..\\", "")

    return result.strip()


def validate_scan_max_files(max_files: int) -> int:
    """
    Validate max_files parameter for scan operations

    Args:
        max_files: Maximum number of files to scan

    Returns:
        The validated max_files value

    Raises:
        ValidationError: If max_files is invalid
    """
    if not isinstance(max_files, int):
        raise ValidationError("max_files must be an integer", field="max_files")

    if max_files <= 0:
        raise ValidationError("max_files must be greater than 0", field="max_files")

    if max_files > 10000:
        raise ValidationError("max_files cannot exceed 10000", field="max_files")

    return max_files


def validate_json_option(option_value: Optional[str], option_name: str = "option") -> dict:
    """
    Validate and parse a JSON option string

    Args:
        option_value: JSON string to parse
        option_name: Name of the option for error messages

    Returns:
        Parsed dictionary

    Raises:
        ValidationError: If JSON is invalid
    """
    if not option_value or not option_value.strip():
        return {}

    import json

    try:
        return json.loads(option_value)
    except json.JSONDecodeError as e:
        raise ValidationError(
            f"Invalid JSON for {option_name}: {str(e)}",
            field=option_name
        )


def validate_scan_path(path: str) -> str:
    """
    Validate a scan path

    Args:
        path: Path to validate

    Returns:
        The validated path

    Raises:
        ValidationError: If path is invalid
    """
    if not path or not path.strip():
        raise ValidationError("Scan path cannot be empty", field="path")

    path = path.strip()

    # Basic check for obviously dangerous paths
    if "../" in path or "..\\" in path:
        raise ValidationError("Path cannot contain parent directory references", field="path")

    return path
