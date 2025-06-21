"""Custom exceptions for ScrollScribe application with functional error handling.

This module defines only the exceptions that are actually used in the codebase,
based on real error patterns found in the code analysis.
"""

import traceback
from datetime import datetime
from pathlib import Path
from typing import Any


class ScrollScribeError(Exception):
    """Base exception for all ScrollScribe errors with enhanced functionality."""

    def __init__(
        self,
        message: str,
        url: str | None = None,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.url = url
        self.context = context or {}
        self.cause = cause
        self.timestamp = datetime.now()
        self.traceback_str = traceback.format_exc() if cause else None

    def __str__(self) -> str:
        parts = [self.message]
        if self.url:
            parts.append(f"URL: {self.url}")
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        return " | ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for structured logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "url": self.url,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "cause": str(self.cause) if self.cause else None,
            "traceback": self.traceback_str,
        }


# Discovery-related exceptions (actually used in links.py)
class DiscoveryError(ScrollScribeError):
    """Base exception for URL discovery errors."""

    pass


class InvalidUrlError(DiscoveryError):
    """Raised when a URL is invalid or malformed."""

    def __init__(self, message: str, url: str, parse_error: str | None = None):
        super().__init__(message, url)
        self.parse_error = parse_error

    def __str__(self) -> str:
        base = super().__str__()
        if self.parse_error:
            base += f" | Parse Error: {self.parse_error}"
        return base


class NetworkError(DiscoveryError):
    """Network-related errors with retry information."""

    def __init__(
        self,
        message: str,
        url: str,
        status_code: int | None = None,
        retry_count: int = 0,
        max_retries: int = 3,
    ):
        super().__init__(message, url)
        self.status_code = status_code
        self.retry_count = retry_count
        self.max_retries = max_retries

    def can_retry(self) -> bool:
        """Check if this error can be retried."""
        return self.retry_count < self.max_retries

    def get_retry_delay(self) -> float:
        """Calculate exponential backoff delay."""
        return min(2**self.retry_count, 60)  # Max 60 seconds

    def __str__(self) -> str:
        base = super().__str__()
        if self.status_code:
            base += f" | Status: {self.status_code}"
        base += f" | Retry: {self.retry_count}/{self.max_retries}"
        return base


# Processing-related exceptions (actually used in markdown.py)
class ProcessingError(ScrollScribeError):
    """Base exception for content processing errors."""

    def __init__(
        self,
        message: str,
        url: str | None = None,
        stage: str = "unknown",
    ):
        super().__init__(message, url)
        self.stage = stage

    def __str__(self) -> str:
        base = super().__str__()
        base += f" | Stage: {self.stage}"
        return base


class LLMError(ProcessingError):
    """Raised when LLM operations fail."""

    def __init__(
        self,
        message: str,
        url: str | None = None,
        model_name: str | None = None,
        api_provider: str | None = None,
    ):
        super().__init__(message, url, "llm_filtering")
        self.model_name = model_name
        self.api_provider = api_provider

    def __str__(self) -> str:
        base = super().__str__()
        if self.model_name:
            base += f" | Model: {self.model_name}"
        if self.api_provider:
            base += f" | Provider: {self.api_provider}"
        return base


class RateLimitError(LLMError):
    """Raised when API rate limits are exceeded."""

    def __init__(
        self,
        message: str,
        url: str | None = None,
        retry_after: int | None = None,
        api_provider: str | None = None,
    ):
        super().__init__(message, url, api_provider=api_provider)
        self.retry_after = retry_after

    def get_wait_time(self) -> int:
        """Get recommended wait time in seconds."""
        if self.retry_after:
            return self.retry_after
        # Default based on provider
        if self.api_provider and "openrouter" in self.api_provider.lower():
            return 60  # OpenRouter typically needs 60s
        return 30  # Conservative default

    def __str__(self) -> str:
        base = super().__str__()
        if self.retry_after:
            base += f" | Wait: {self.retry_after}s"
        return base


# File and configuration exceptions (actually used in files.py, markdown.py)
class FileIOError(ScrollScribeError):
    """Raised when file I/O operations fail."""

    def __init__(
        self,
        message: str,
        filepath: str,
        operation: str = "unknown",
    ):
        super().__init__(message)
        self.filepath = filepath
        self.operation = operation  # "read", "write", "create", "delete"

    def is_permission_error(self) -> bool:
        """Check if this is a permission-related error."""
        return "permission" in self.message.lower() or "access" in self.message.lower()

    def is_not_found_error(self) -> bool:
        """Check if file/directory was not found."""
        return (
            "not found" in self.message.lower()
            or "no such file" in self.message.lower()
        )

    def get_file_info(self) -> dict[str, Any]:
        """Get file information for debugging."""
        try:
            path = Path(self.filepath)
            return {
                "filepath": self.filepath,
                "exists": path.exists(),
                "is_file": path.is_file() if path.exists() else None,
                "is_dir": path.is_dir() if path.exists() else None,
                "parent_exists": path.parent.exists(),
                "operation": self.operation,
            }
        except Exception:
            return {"filepath": self.filepath, "operation": self.operation}

    def __str__(self) -> str:
        return f"{self.message} | File: {self.filepath} | Operation: {self.operation}"


class ConfigError(ScrollScribeError):
    """Raised when configuration is invalid or missing (API keys, etc)."""

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        suggested_fix: str | None = None,
    ):
        super().__init__(message)
        self.config_key = config_key
        self.suggested_fix = suggested_fix

    def is_missing_api_key(self) -> bool:
        """Check if this is a missing API key error."""
        return "api" in self.message.lower() and "key" in self.message.lower()

    def get_help_message(self) -> str:
        """Get helpful error message with suggested fix."""
        base = self.message
        if self.suggested_fix:
            base += f"\n💡 Suggested fix: {self.suggested_fix}"
        elif self.is_missing_api_key() and self.config_key:
            base += f"\n💡 Set the environment variable: export {self.config_key}=your_api_key"
        return base

    def __str__(self) -> str:
        base = self.message
        if self.config_key:
            base += f" | Key: {self.config_key}"
        return base


# Utility functions for exception handling
def is_retryable_error(exc: Exception) -> bool:
    """Check if an exception should trigger a retry."""
    if isinstance(exc, NetworkError):
        return exc.can_retry()
    elif isinstance(exc, RateLimitError):
        return True  # Rate limits are always retryable with delay
    elif isinstance(exc, LLMError):
        return "context" not in exc.message.lower()  # Don't retry context length errors

    return False


def get_retry_delay(exc: Exception) -> float:
    """Get appropriate retry delay for an exception."""
    if isinstance(exc, NetworkError):
        return exc.get_retry_delay()
    elif isinstance(exc, RateLimitError):
        return float(exc.get_wait_time())

    return 1.0  # Default 1 second delay
