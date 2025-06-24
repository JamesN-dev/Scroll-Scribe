"""Tests for ScrollScribe custom exceptions in app/utils/exceptions.py."""

import pytest
from app.utils.exceptions import (
    ScrollScribeError,
    DiscoveryError,
    InvalidUrlError,
    NetworkError,
    ProcessingError,
    LLMError,
    RateLimitError,
    FileIOError,
    ConfigError,
    is_retryable_error,
    get_retry_delay,
)
from datetime import datetime
from pathlib import Path

# ScrollScribeError Tests
def test_scroll_scribe_error_basic():
    """Test basic ScrollScribeError instantiation and string representation."""
    error = ScrollScribeError("Test message")
    assert error.message == "Test message"
    assert error.url is None
    assert error.context == {}
    assert error.cause is None
    assert isinstance(error.timestamp, datetime)
    assert str(error) == "Test message"

def test_scroll_scribe_error_with_all_args():
    """Test ScrollScribeError with all arguments."""
    cause_exception = ValueError("Original cause")
    error = ScrollScribeError(
        "Detailed message",
        url="http://example.com",
        context={"key": "value"},
        cause=cause_exception,
    )
    assert error.message == "Detailed message"
    assert error.url == "http://example.com"
    assert error.context == {"key": "value"}
    assert error.cause == cause_exception
    assert "Detailed message" in str(error)
    assert "URL: http://example.com" in str(error)
    assert "Context: key=value" in str(error)
    assert error.traceback_str is not None

def test_scroll_scribe_error_to_dict():
    """Test the to_dict method of ScrollScribeError."""
    error = ScrollScribeError("Dict test", url="http://dict.com")
    error_dict = error.to_dict()
    assert error_dict["error_type"] == "ScrollScribeError"
    assert error_dict["message"] == "Dict test"
    assert error_dict["url"] == "http://dict.com"
    assert isinstance(error_dict["timestamp"], str)
    assert error_dict["cause"] is None

# DiscoveryError Tests
def test_discovery_error():
    """Test DiscoveryError instantiation."""
    error = DiscoveryError("Discovery failed", url="http://discover.me")
    assert isinstance(error, ScrollScribeError)
    assert "Discovery failed" in str(error)
    assert "URL: http://discover.me" in str(error)

# InvalidUrlError Tests
def test_invalid_url_error():
    """Test InvalidUrlError instantiation and string representation."""
    error = InvalidUrlError(
        "Malformed URL", url="htp://badurl", parse_error="Scheme error"
    )
    assert isinstance(error, DiscoveryError)
    assert "Malformed URL" in str(error)
    assert "URL: htp://badurl" in str(error)
    assert "Parse Error: Scheme error" in str(error)

# NetworkError Tests
def test_network_error_basic():
    """Test basic NetworkError instantiation."""
    error = NetworkError("Connection timeout", url="http://network.error")
    assert isinstance(error, DiscoveryError)
    assert "Connection timeout" in str(error)
    assert "URL: http://network.error" in str(error)
    assert "Retry: 0/3" in str(error)
    assert error.status_code is None

def test_network_error_with_status_and_retry():
    """Test NetworkError with status code and retry info."""
    error = NetworkError(
        "Service unavailable",
        url="http://service.down",
        status_code=503,
        retry_count=2,
        max_retries=5,
    )
    assert "Status: 503" in str(error)
    assert "Retry: 2/5" in str(error)

def test_network_error_can_retry():
    """Test NetworkError's can_retry method."""
    error_can_retry = NetworkError("msg", url="url", retry_count=1, max_retries=3)
    error_cannot_retry = NetworkError("msg", url="url", retry_count=3, max_retries=3)
    assert error_can_retry.can_retry() is True
    assert error_cannot_retry.can_retry() is False

def test_network_error_get_retry_delay():
    """Test NetworkError's get_retry_delay method (exponential backoff)."""
    error0 = NetworkError("msg", url="url", retry_count=0) # 2^0 = 1
    error1 = NetworkError("msg", url="url", retry_count=1) # 2^1 = 2
    error2 = NetworkError("msg", url="url", retry_count=2) # 2^2 = 4
    error6 = NetworkError("msg", url="url", retry_count=6) # 2^6 = 64, capped at 60
    assert error0.get_retry_delay() == 1
    assert error1.get_retry_delay() == 2
    assert error2.get_retry_delay() == 4
    assert error6.get_retry_delay() == 60

# ProcessingError Tests
def test_processing_error():
    """Test ProcessingError instantiation."""
    error = ProcessingError("Content mismatch", url="http://process.this", stage="validation")
    assert isinstance(error, ScrollScribeError)
    assert "Content mismatch" in str(error)
    assert "URL: http://process.this" in str(error)
    assert "Stage: validation" in str(error)

# LLMError Tests
def test_llm_error():
    """Test LLMError instantiation."""
    error = LLMError(
        "LLM generation failed",
        url="http://llm.fail",
        model_name="gpt-test",
        api_provider="test_provider",
    )
    assert isinstance(error, ProcessingError)
    assert "LLM generation failed" in str(error)
    assert "Stage: llm_filtering" in str(error)
    assert "Model: gpt-test" in str(error)
    assert "Provider: test_provider" in str(error)

# RateLimitError Tests
def test_rate_limit_error():
    """Test RateLimitError instantiation and get_wait_time."""
    error_no_retry_after = RateLimitError(
        "API rate limit hit", url="http://ratelimit.api", api_provider="openrouter"
    )
    error_with_retry_after = RateLimitError(
        "API rate limit hit", url="http://ratelimit.api", retry_after=45
    )
    error_generic_provider = RateLimitError("API rate limit hit", url="http://ratelimit.api")

    assert isinstance(error_no_retry_after, LLMError)
    assert "Wait: 60s" not in str(error_no_retry_after) # Default not shown in str unless retry_after is set
    assert "Wait: 45s" in str(error_with_retry_after)

    assert error_no_retry_after.get_wait_time() == 60  # OpenRouter default
    assert error_with_retry_after.get_wait_time() == 45
    assert error_generic_provider.get_wait_time() == 30 # Generic default

# FileIOError Tests
def test_file_io_error():
    """Test FileIOError instantiation and helper methods."""
    error = FileIOError(
        "Permission denied", filepath="/root/test.txt", operation="write"
    )
    assert isinstance(error, ScrollScribeError)
    assert "Permission denied" in str(error)
    assert "File: /root/test.txt" in str(error)
    assert "Operation: write" in str(error)
    assert error.is_permission_error() is True
    assert error.is_not_found_error() is False

def test_file_io_error_not_found():
    """Test FileIOError for 'not found' cases."""
    error = FileIOError(
        "No such file or directory", filepath="/tmp/nonexistent.txt", operation="read"
    )
    assert error.is_permission_error() is False
    assert error.is_not_found_error() is True

def test_file_io_error_get_file_info(tmp_path: Path):
    """Test FileIOError's get_file_info method."""
    existing_file = tmp_path / "exists.txt"
    existing_file.write_text("content")
    non_existing_file = tmp_path / "not_exists.txt"

    error_exists = FileIOError("msg", filepath=str(existing_file))
    info_exists = error_exists.get_file_info()
    assert info_exists["filepath"] == str(existing_file)
    assert info_exists["exists"] is True
    assert info_exists["is_file"] is True

    error_not_exists = FileIOError("msg", filepath=str(non_existing_file))
    info_not_exists = error_not_exists.get_file_info()
    assert info_not_exists["filepath"] == str(non_existing_file)
    assert info_not_exists["exists"] is False
    assert info_not_exists["is_file"] is None

# ConfigError Tests
def test_config_error():
    """Test ConfigError instantiation and helper methods."""
    error = ConfigError(
        "Missing API key",
        config_key="OPENROUTER_API_KEY",
        suggested_fix="Set the env var.",
    )
    assert isinstance(error, ScrollScribeError)
    assert "Missing API key" in str(error)
    assert "Key: OPENROUTER_API_KEY" in str(error)
    assert error.is_missing_api_key() is True
    help_msg = error.get_help_message()
    assert "Missing API key" in help_msg
    assert "Set the env var." in help_msg

def test_config_error_missing_api_key_default_fix():
    """Test ConfigError default fix message for missing API key."""
    error = ConfigError("API key for SOME_SERVICE_API_KEY not found", config_key="SOME_SERVICE_API_KEY")
    assert error.is_missing_api_key() is True
    help_msg = error.get_help_message()
    assert "export SOME_SERVICE_API_KEY=your_api_key" in help_msg

# Utility function tests: is_retryable_error and get_retry_delay
@pytest.mark.parametrize(
    "exception_instance, expected_retryable, expected_delay",
    [
        (RateLimitError("msg", url="url", retry_after=10), True, 10.0),
        (NetworkError("msg", url="url", retry_count=0, max_retries=3), True, 1.0),
        (NetworkError("msg", url="url", retry_count=3, max_retries=3), False, 2.0**3), # delay still calculated
        (LLMError("msg", url="url"), True, 1.0), # Default delay for non-specific LLMError
        (LLMError("Context length error", url="url"), False, 1.0), # Context length not retryable
        (ProcessingError("msg", url="url"), False, 1.0), # Generic processing error not retryable by default
        (ScrollScribeError("msg"), False, 1.0), # Base error not retryable
        (ValueError("generic python error"), False, 1.0), # Non-ScrollScribe error
    ],
)
def test_is_retryable_and_get_delay(exception_instance, expected_retryable, expected_delay):
    """Test is_retryable_error and get_retry_delay utility functions."""
    assert is_retryable_error(exception_instance) == expected_retryable
    # For LLMError that is not RateLimitError, it might be retryable but delay comes from generic handling
    if isinstance(exception_instance, LLMError) and not isinstance(exception_instance, RateLimitError) and "Context" not in exception_instance.message:
         assert get_retry_delay(exception_instance) == 1.0 # Default from retry logic if not specific
    elif isinstance(exception_instance, ScrollScribeError):
         assert get_retry_delay(exception_instance) == expected_delay
    else: # For non-ScrollScribeError, get_retry_delay returns default
        assert get_retry_delay(exception_instance) == 1.0

# Test case for LiteLLM exceptions (if they were directly used, which they aren't for these utils)
# from litellm.exceptions import RateLimitError as LiteRateLimitError
# def test_is_retryable_litellm():
#     lite_rate_limit = LiteRateLimitError(message="LiteLLM rate limit", llm_provider="openai", model="gpt-3.5-turbo", response=None)
#     assert is_retryable_error(lite_rate_limit) is True # This would be true if retry.py handled it directly
#     assert get_retry_delay(lite_rate_limit) == 60.0 # Assuming default retry_after from LiteRateLimitError or mapped
