"""Input validation utilities for Scroll-Scribe.

This module provides comprehensive validation functions for all user inputs,
ensuring data integrity and providing clear error messages.
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse

from ..constants import (
    DEFAULT_TIMEOUT_MS,
    EXCLUDED_URL_EXTENSIONS,
    MAX_FILENAME_LENGTH,
    VALID_URL_SCHEMES,
)


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate URL format and basic accessibility requirements.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message will be empty string
    """
    if not url or not isinstance(url, str):
        return False, "URL must be a non-empty string"

    url = url.strip()
    if not url:
        return False, "URL cannot be empty or whitespace only"

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL format: {e}"

    # Check scheme
    if not parsed.scheme:
        return False, "URL must include a scheme (http:// or https://)"

    if parsed.scheme.lower() not in VALID_URL_SCHEMES:
        return False, f"URL scheme must be one of: {', '.join(VALID_URL_SCHEMES)}"

    # Check domain
    if not parsed.netloc:
        return False, "URL must include a domain name"

    # Check for excluded file extensions
    if parsed.path:
        path_lower = parsed.path.lower()
        for ext in EXCLUDED_URL_EXTENSIONS:
            if path_lower.endswith(ext):
                return False, f"File type '{ext}' is not supported for processing"

    return True, ""


def validate_file_path(
    path: str, must_exist: bool = True, must_be_readable: bool = True
) -> tuple[bool, str]:
    """
    Validate file path exists and is accessible.

    Args:
        path: The file path to validate
        must_exist: Whether the file must already exist
        must_be_readable: Whether the file must be readable (only checked if exists)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path or not isinstance(path, str):
        return False, "File path must be a non-empty string"

    path = path.strip()
    if not path:
        return False, "File path cannot be empty or whitespace only"

    try:
        path_obj = Path(path)
    except Exception as e:
        return False, f"Invalid file path format: {e}"

    if must_exist:
        if not path_obj.exists():
            return False, f"File does not exist: {path}"

        if not path_obj.is_file():
            return False, f"Path is not a file: {path}"

        if must_be_readable and not os.access(path, os.R_OK):
            return False, f"File is not readable: {path}"

    return True, ""


def validate_output_directory(
    path: str, create_if_missing: bool = False
) -> tuple[bool, str]:
    """
    Validate output directory can be created/written to.

    Args:
        path: The directory path to validate
        create_if_missing: Whether to attempt creating the directory if it doesn't exist

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path or not isinstance(path, str):
        return False, "Directory path must be a non-empty string"

    path = path.strip()
    if not path:
        return False, "Directory path cannot be empty or whitespace only"

    try:
        path_obj = Path(path)
    except Exception as e:
        return False, f"Invalid directory path format: {e}"

    if path_obj.exists():
        if not path_obj.is_dir():
            return False, f"Path exists but is not a directory: {path}"

        if not os.access(path, os.W_OK):
            return False, f"Directory is not writable: {path}"
    else:
        if create_if_missing:
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create directory: {e}"
        else:
            # Check if parent directory exists and is writable
            parent = path_obj.parent
            if not parent.exists():
                return False, f"Parent directory does not exist: {parent}"

            if not os.access(parent, os.W_OK):
                return False, f"Cannot write to parent directory: {parent}"

    return True, ""


def validate_model_name(model: str) -> tuple[bool, str]:
    """
    Validate LLM model name format.

    Args:
        model: The model name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not model or not isinstance(model, str):
        return False, "Model name must be a non-empty string"

    model = model.strip()
    if not model:
        return False, "Model name cannot be empty or whitespace only"

    # Basic format validation - should contain provider/model pattern
    if "/" not in model:
        return (
            False,
            "Model name should include provider (e.g., 'openrouter/model-name')",
        )

    parts = model.split("/")
    if len(parts) < 2:
        return False, "Model name should be in format 'provider/model-name'"

    provider = parts[0]
    model_name = "/".join(parts[1:])  # Handle nested paths

    if not provider or not model_name:
        return False, "Both provider and model name must be specified"

    # Check for valid characters (alphanumeric, hyphens, underscores, dots)
    valid_pattern = re.compile(r"^[a-zA-Z0-9._-]+$")
    if not valid_pattern.match(provider) or not valid_pattern.match(
        model_name.replace("/", "")
    ):
        return (
            False,
            "Model name contains invalid characters (use only letters, numbers, dots, hyphens, underscores)",
        )

    return True, ""


def validate_timeout(timeout_ms: int = DEFAULT_TIMEOUT_MS) -> tuple[bool, str]:
    """
    Validate timeout value is reasonable.

    Args:
        timeout_ms: Timeout in milliseconds (defaults to DEFAULT_TIMEOUT_MS)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(timeout_ms, int):
        return False, "Timeout must be an integer"  # pyright: ignore[reportUnreachable]
    elif timeout_ms <= 0:
        return False, "Timeout must be positive"
    elif timeout_ms < 1000:
        return (
            False,
            f"Timeout must be at least 1000ms (1 second). Default is {DEFAULT_TIMEOUT_MS}ms (25 seconds)",
        )
    elif timeout_ms > 600000:
        return (
            False,
            f"Timeout cannot exceed 600000ms (10 minutes). Default is {DEFAULT_TIMEOUT_MS}ms (25 seconds)",
        )
    else:
        return True, ""  # pyright: ignore[reportUnreachable]


def validate_batch_size(batch_size: int) -> tuple[bool, str]:
    """
    Validate batch size for processing operations.

    Args:
        batch_size: Number of items to process in a batch

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(batch_size, int):
        return False, "Batch size must be an integer"  # pyright: ignore[reportUnreachable]
    elif batch_size <= 0:
        return False, "Batch size must be positive"
    elif batch_size > 100:
        return False, "Batch size cannot exceed 100 (to prevent resource exhaustion)"
    else:
        return True, ""  # pyright: ignore[reportUnreachable]


def validate_filename(filename: str) -> tuple[bool, str]:
    """
    Validate filename is safe for filesystem use.

    Args:
        filename: The filename to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename or not isinstance(filename, str):
        return False, "Filename must be a non-empty string"
    filename = filename.strip()
    if not filename:
        return False, "Filename cannot be empty or whitespace only"
    elif len(filename) > MAX_FILENAME_LENGTH:
        return False, f"Filename too long (max {MAX_FILENAME_LENGTH} characters)"
    else:
        # Check for invalid characters
        invalid_chars = ["<", ">", ":", '"', "|", "?", "*", "/", "\\"]
        for char in invalid_chars:
            if char in filename:
                return False, f"Filename contains invalid character: '{char}'"
        # Check for reserved names (Windows)
        reserved_names = [
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        ]
        name_without_ext = filename.split(".")[0].upper()
        if name_without_ext in reserved_names:
            return False, f"Filename uses reserved name: {name_without_ext}"
        else:
            return True, ""  # pyright: ignore[reportUnreachable]


def validate_start_line(
    start_line: int, total_lines: int | None = None
) -> tuple[bool, str]:
    """
    Validate start line number for resuming operations.

    Args:
        start_line: Line number to start from (1-based)
        total_lines: Total number of lines (optional, for range checking)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(start_line, int):
        return False, "Start line must be an integer"  # pyright: ignore[reportUnreachable]
    elif start_line < 1:
        return False, "Start line must be 1 or greater"
    elif total_lines is not None and start_line > total_lines:
        return (
            False,
            f"Start line ({start_line}) exceeds total lines ({total_lines})",
        )
    else:
        return True, ""
