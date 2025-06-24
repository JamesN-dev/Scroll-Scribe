"""Tests for ScrollScribe retry utilities in app/utils/retry.py."""

import pytest
from unittest.mock import MagicMock, call
from tenacity import RetryError

from app.utils.exceptions import (
    ScrollScribeError,
    LLMError,
    NetworkError,
    RateLimitError,
    ConfigError, # For testing non-retryable ScrollScribeError
)
from app.utils.retry import (
    is_scrollscribe_retryable,
    scrollscribe_wait_strategy,
    retry_scrollscribe_operation,
    retry_llm,
    retry_network,
    map_external_exception,
)

# External exceptions for mapping tests
from litellm.exceptions import (
    APIConnectionError as LiteAPIConnectionError,
    ContextWindowExceededError as LiteContextError,
    RateLimitError as LiteRateLimitError,
)
import asyncio # For async functions used with retry decorators

# Test is_scrollscribe_retryable
@pytest.mark.parametrize(
    "exception_instance, expected",
    [
        (RateLimitError("msg", url="url"), True),
        (NetworkError("msg", url="url", retry_count=1, max_retries=3), True),
        (NetworkError("msg", url="url", retry_count=3, max_retries=3), False), # Cannot retry
        (LLMError("msg", url="url"), True), # Generic LLMError is retryable
        (LLMError("Context length too long", url="url"), False), # Context length error not retryable
        (LiteRateLimitError(message="lite llm rate limit", response=MagicMock()), True),
        (LiteAPIConnectionError(message="lite api connection error"), True),
        (ConfigError("Missing key"), False), # Non-retryable ScrollScribeError
        (ValueError("Some other error"), False), # Non-ScrollScribe, non-LiteLLM error
    ],
)
def test_is_scrollscribe_retryable(exception_instance, expected):
    """Test the is_scrollscribe_retryable function with various exceptions."""
    assert is_scrollscribe_retryable(exception_instance) == expected

# Test scrollscribe_wait_strategy
def create_mock_retry_state(exception_instance, attempt_number=1):
    """Helper to create a mock RetryCallState object."""
    mock_state = MagicMock()
    mock_outcome = MagicMock()
    mock_outcome.exception.return_value = exception_instance
    mock_state.outcome = mock_outcome
    mock_state.attempt_number = attempt_number
    return mock_state

@pytest.mark.parametrize(
    "exception_instance, attempt_number, expected_delay_approx",
    [
        (RateLimitError("msg", url="url", retry_after=15), 1, 15.0),
        (NetworkError("msg", url="url", retry_count=0), 1, 1.0), # 2^0
        (NetworkError("msg", url="url", retry_count=2), 3, 8.0), # 2^2 (retry_count for delay calc)
        (LLMError("msg", url="url"), 1, 1.0), # Default for LLMError without specific delay info
        (LiteRateLimitError(message="lite rate limit", retry_after=5, response=MagicMock()), 1, 5.0),
        (LiteAPIConnectionError(message="lite api error"), 2, 4.0), # 2^attempt_number (2^2)
        (ValueError("generic"), 1, 1.0), # Default for unknown
    ],
)
def test_scrollscribe_wait_strategy(exception_instance, attempt_number, expected_delay_approx):
    """Test scrollscribe_wait_strategy for calculating retry delays."""
    retry_state = create_mock_retry_state(exception_instance, attempt_number)
    # For NetworkError, the delay is based on its internal retry_count, not attempt_number
    if isinstance(exception_instance, NetworkError):
        delay = exception_instance.get_retry_delay()
        assert scrollscribe_wait_strategy(retry_state) == delay
    else:
        assert abs(scrollscribe_wait_strategy(retry_state) - expected_delay_approx) < 0.1


# Test retry_scrollscribe_operation decorator factory
def test_retry_scrollscribe_operation_success_first_try(mocker):
    """Test that a function succeeds on the first try without retries."""
    mock_func = mocker.MagicMock(return_value="success")

    @retry_scrollscribe_operation(max_attempts=3)
    async def func_to_retry():
        return await mock_func()

    result = asyncio.run(func_to_retry())
    assert result == "success"
    mock_func.assert_called_once()

def test_retry_scrollscribe_operation_retries_and_succeeds(mocker):
    """Test that the decorator retries on specified exceptions and then succeeds."""
    mock_func = mocker.MagicMock()
    # Simulate failure twice, then success
    mock_func.side_effect = [
        NetworkError("Attempt 1 fail", url="url1"),
        RateLimitError("Attempt 2 fail", url="url2", retry_after=0.01), # Small delay for test speed
        "success"
    ]

    @retry_scrollscribe_operation(max_attempts=3)
    async def func_to_retry():
        return await mock_func() # await if mock_func itself is async or returns awaitable

    result = asyncio.run(func_to_retry())
    assert result == "success"
    assert mock_func.call_count == 3

def test_retry_scrollscribe_operation_fails_after_max_attempts(mocker):
    """Test that the decorator gives up after max_attempts and reraises the last exception."""
    mock_func = mocker.MagicMock(
        side_effect=NetworkError("Persistent failure", url="url_fail")
    )

    @retry_scrollscribe_operation(max_attempts=2)
    async def func_to_retry():
        return await mock_func()

    with pytest.raises(NetworkError) as exc_info:
        asyncio.run(func_to_retry())

    assert "Persistent failure" in str(exc_info.value)
    assert mock_func.call_count == 2

def test_retry_scrollscribe_operation_non_retryable_exception(mocker):
    """Test that non-retryable exceptions are not retried."""
    mock_func = mocker.MagicMock(side_effect=ConfigError("Config failure"))

    @retry_scrollscribe_operation(max_attempts=3)
    async def func_to_retry():
        return await mock_func()

    with pytest.raises(ConfigError):
        asyncio.run(func_to_retry())
    mock_func.assert_called_once() # Should not retry


# Test convenience decorators @retry_llm and @retry_network
def test_retry_llm_decorator(mocker):
    """Test the @retry_llm decorator specifically."""
    mock_llm_call = mocker.MagicMock()
    mock_llm_call.side_effect = [
        LiteRateLimitError(message="LLM rate limited", response=MagicMock(), retry_after=0.01),
        LLMError("Temporary LLM glitch", url="llm_url"),
        "llm_success"
    ]

    @retry_llm # Default max_attempts=5
    async def call_llm_api():
        return await mock_llm_call()

    result = asyncio.run(call_llm_api())
    assert result == "llm_success"
    assert mock_llm_call.call_count == 3

def test_retry_network_decorator(mocker):
    """Test the @retry_network decorator specifically."""
    mock_network_request = mocker.MagicMock()
    mock_network_request.side_effect = [
        NetworkError("Connection failed", url="net_url1", retry_count=0, max_retries=4),
        LiteAPIConnectionError(message="API connection issue"),
        "network_success"
    ]

    @retry_network # Default max_attempts=4
    async def make_network_request():
        return await mock_network_request()

    result = asyncio.run(make_network_request())
    assert result == "network_success"
    assert mock_network_request.call_count == 3

# Test map_external_exception
@pytest.mark.parametrize(
    "external_exception, target_scrollscribe_type, extra_kwargs, expected_attrs",
    [
        (
            LiteRateLimitError(message="lite rate limit", llm_provider="openai", retry_after=10, response=MagicMock()),
            RateLimitError,
            {"url": "http://test.com"},
            {"api_provider": "openai", "retry_after": 10, "url": "http://test.com"}
        ),
        (
            LiteContextError(message="context too long", model="gpt-4", llm_provider="azure", response=MagicMock()),
            LLMError, # Mapped to generic LLMError, not RateLimitError
            {},
            {"model_name": "gpt-4", "api_provider": "azure"}
        ),
        (
            LiteAPIConnectionError(message="connection refused", request=MagicMock()), # request has .url
            NetworkError,
            {"url": "http://fallback.url"}, # This should be used if request.url is not found
            {"url": "http://fallback.url"} # Assuming LiteAPIConnectionError doesn't have a direct 'url' attribute
        ),
        (
            FileNotFoundError("No such file"),
            ScrollScribeError, # Example: map to base if specific mapping not defined
            {"filepath": "/tmp/file", "operation": "read"},
            {"filepath": "/tmp/file", "operation": "read"}
        ),
    ]
)
def test_map_external_exception(external_exception, target_scrollscribe_type, extra_kwargs, expected_attrs):
    """Test mapping of various external exceptions to ScrollScribeError subtypes."""
    # Simulate a URL attribute if the external exception might have it (like LiteAPIConnectionError)
    if hasattr(external_exception, 'request') and 'url' not in extra_kwargs:
         external_exception.request.url = "http://request-url.com"
         expected_attrs["url"] = "http://request-url.com"


    mapped_exc = map_external_exception(external_exception, target_scrollscribe_type, **extra_kwargs)

    assert isinstance(mapped_exc, target_scrollscribe_type)
    assert mapped_exc.cause == external_exception
    assert str(external_exception) in mapped_exc.message # Original message should be part of the new one

    for attr, expected_value in expected_attrs.items():
        assert hasattr(mapped_exc, attr), f"Mapped exception missing attribute {attr}"
        assert getattr(mapped_exc, attr) == expected_value, f"Attribute {attr} mismatch"

def test_map_external_exception_invalid_type():
    """Test that map_external_exception raises TypeError for invalid target type."""
    class NotAScrollScribeError(Exception): pass

    with pytest.raises(TypeError) as exc_info:
        map_external_exception(ValueError("test"), NotAScrollScribeError) # type: ignore
    assert "NotAScrollScribeError must subclass ScrollScribeError" in str(exc_info.value)


# Example of a synchronous function retry (though most in ScrollScribe are async)
def test_retry_sync_function(mocker):
    mock_sync_func = mocker.MagicMock()
    mock_sync_func.side_effect = [
        NetworkError("Sync fail 1", url="sync_url"),
        "sync_success"
    ]

    @retry_scrollscribe_operation(max_attempts=2)
    def sync_function_to_retry():
        return mock_sync_func()

    result = sync_function_to_retry()
    assert result == "sync_success"
    assert mock_sync_func.call_count == 2
