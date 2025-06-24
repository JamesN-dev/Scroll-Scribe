"""Tests for fast_discovery.py using Crawl4AI."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CrawlResult

from app.fast_discovery import extract_links_fast
from app.utils.exceptions import InvalidUrlError, NetworkError
from app.utils.logging import CleanConsole # For console output checks if needed

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_clean_console():
    """Fixture to mock CleanConsole."""
    with patch("app.fast_discovery.CleanConsole", spec=CleanConsole) as mock_console_class:
        yield mock_console_class.return_value

async def mock_crawler_arun_success(start_url, config):
    """Simulates a successful crawl4ai arun call for link extraction."""
    mock_result = MagicMock(spec=CrawlResult)
    mock_result.success = True
    mock_result.error_message = None
    mock_result.links = {
        "internal": [
            {"href": "https://example.com/page1"},
            {"href": "https://example.com/page2#section"},
            {"href": "/relative/path"}, # Should be resolved by crawl4ai if base_url is implicit
            {"href": "https://example.com/"}, # Should be ignored if it's the start_url
        ],
        "external": [
            {"href": "https://othersite.com/resource"},
        ],
    }
    # Simulate crawl4ai behavior: relative links are often returned as absolute by the crawler
    # For this test, we assume crawl4ai has already absolutized them if needed,
    # or we test the filtering of what it returns.
    # The function itself primarily filters and cleans.
    if start_url == "https://example.com":
        mock_result.links["internal"].append({"href": start_url + "/relative/path"})


    # Add a mock for a case where href is not a string, to test robustness
    mock_result.links["internal"].append({"href": None})
    mock_result.links["internal"].append({"href": 123})


    return mock_result

async def mock_crawler_arun_failure_message(start_url, config, error_message="Unknown crawl error"):
    """Simulates a failed crawl4ai arun call with an error message."""
    mock_result = MagicMock(spec=CrawlResult)
    mock_result.success = False
    mock_result.error_message = error_message
    mock_result.links = {}
    return mock_result

@patch("app.fast_discovery.AsyncWebCrawler", spec=AsyncWebCrawler)
async def test_extract_links_fast_success(mock_async_web_crawler_class, mock_clean_console):
    """Test successful link extraction and filtering."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value
    mock_crawler_instance.arun = AsyncMock(side_effect=mock_crawler_arun_success)

    start_url = "https://example.com"
    expected_links = {
        "https://example.com/page1",
        "https://example.com/page2", # Fragment should be removed
        "https://example.com/relative/path",
        # start_url itself and external links should be excluded
        # Non-string hrefs should be ignored
    }

    # To make the assertion for "/relative/path" pass, we need to ensure
    # mock_crawler_arun_success returns it as absolute based on start_url
    # The current mock_crawler_arun_success adds "https://example.com/relative/path"

    links = await extract_links_fast(start_url, verbose=False)

    assert links == expected_links
    mock_crawler_instance.arun.assert_called_once()
    # Check that CrawlerRunConfig was instantiated with correct parameters
    call_args = mock_crawler_instance.arun.call_args
    assert isinstance(call_args[1]['config'], CrawlerRunConfig)
    run_config: CrawlerRunConfig = call_args[1]['config']
    assert run_config.css_selector == "a[href]"
    assert run_config.exclude_external_links is True


@patch("app.fast_discovery.AsyncWebCrawler", spec=AsyncWebCrawler)
async def test_extract_links_fast_no_links_found(mock_async_web_crawler_class, mock_clean_console):
    """Test scenario where no internal links are found."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value
    async def arun_no_links(start_url, config):
        mock_result = MagicMock(spec=CrawlResult)
        mock_result.success = True
        mock_result.links = {"internal": [], "external": []}
        return mock_result
    mock_crawler_instance.arun = AsyncMock(side_effect=arun_no_links)

    links = await extract_links_fast("https://example.com/empty", verbose=False)
    assert links == set()

@patch("app.fast_discovery.AsyncWebCrawler", spec=AsyncWebCrawler)
async def test_extract_links_fast_crawl_failure_generic(mock_async_web_crawler_class, mock_clean_console):
    """Test handling of a generic crawl failure from arun."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value
    mock_crawler_instance.arun = AsyncMock(
        side_effect=lambda start_url, config: mock_crawler_arun_failure_message(
            start_url, config, error_message="Simulated crawl failure"
        )
    )

    with pytest.raises(NetworkError) as exc_info:
        await extract_links_fast("https://example.com/fails", verbose=False)
    assert "Discovery operation failed: Simulated crawl failure" in str(exc_info.value)

@patch("app.fast_discovery.AsyncWebCrawler", spec=AsyncWebCrawler)
async def test_extract_links_fast_crawl_failure_invalid_url_in_message(mock_async_web_crawler_class, mock_clean_console):
    """Test handling of crawl failure when error message indicates an invalid URL."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value
    mock_crawler_instance.arun = AsyncMock(
        side_effect=lambda start_url, config: mock_crawler_arun_failure_message(
            start_url, config, error_message="Invalid URL format provided"
        )
    )
    start_url_test = "htp://bad-schema.com"
    with pytest.raises(InvalidUrlError) as exc_info:
        await extract_links_fast(start_url_test, verbose=False)

    assert f"Invalid URL format: {start_url_test}" in str(exc_info.value)
    assert "Invalid URL format provided" in exc_info.value.parse_error # Check the original error is preserved


@patch("app.fast_discovery.AsyncWebCrawler", spec=AsyncWebCrawler)
async def test_extract_links_fast_arun_raises_network_exception(mock_async_web_crawler_class, mock_clean_console):
    """Test when arun itself raises a network-like exception."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value
    # Simulate an exception that might be raised by httpx or playwright via crawl4ai
    mock_crawler_instance.arun = AsyncMock(side_effect=ConnectionRefusedError("Connection refused by server"))

    with pytest.raises(NetworkError) as exc_info:
        await extract_links_fast("https://example.com/refused", verbose=True)

    assert "Network error during discovery: Connection refused by server" in str(exc_info.value)
    # Check that verbose logging for the error occurred (optional, depends on CleanConsole mock complexity)
    # mock_clean_console.print_error.assert_any_call("Unexpected error during discovery: Connection refused by server")


@patch("app.fast_discovery.AsyncWebCrawler", spec=AsyncWebCrawler)
async def test_extract_links_fast_arun_raises_url_parsing_exception(mock_async_web_crawler_class, mock_clean_console):
    """Test when arun raises an exception that implies a URL parsing issue."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value
    # Simulate an exception that might indicate a malformed URL was processed internally by crawl4ai
    mock_crawler_instance.arun = AsyncMock(side_effect=ValueError("Malformed URL processed internally"))

    start_url_test = "https://example.com/malformed-trigger"
    with pytest.raises(InvalidUrlError) as exc_info:
        await extract_links_fast(start_url_test, verbose=False)

    assert f"URL processing error: {start_url_test}" in str(exc_info.value)
    assert "Malformed URL processed internally" in exc_info.value.parse_error


@patch("app.fast_discovery.AsyncWebCrawler", spec=AsyncWebCrawler)
async def test_extract_links_fast_unexpected_exception_in_arun(mock_async_web_crawler_class, mock_clean_console):
    """Test handling of truly unexpected exceptions from arun, mapping to NetworkError."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value
    mock_crawler_instance.arun = AsyncMock(side_effect=RuntimeError("A very unexpected runtime error"))

    with pytest.raises(NetworkError) as exc_info:
        await extract_links_fast("https://example.com/unexpected", verbose=False)

    assert "Discovery operation failed: A very unexpected runtime error" in str(exc_info.value)


# Test the retry_network decorator implicitly by causing retriable errors
# This is more of an integration test for the decorator with this function.
# For pure decorator unit tests, see test_retry.py.
@patch("app.fast_discovery.AsyncWebCrawler", spec=AsyncWebCrawler)
async def test_extract_links_fast_retries_on_network_issues(mock_async_web_crawler_class, mock_clean_console):
    """Test that extract_links_fast (via @retry_network) retries on network issues."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value

    # Simulate AsyncWebCrawler.arun failing a few times then succeeding
    side_effects = [
        ConnectionRefusedError("Fail 1"), # Mapped to NetworkError by _extract_links_async
        ConnectionRefusedError("Fail 2"), # Mapped to NetworkError
        mock_crawler_arun_success("https://retry.example.com", None) # Success
    ]
    mock_crawler_instance.arun = AsyncMock(side_effect=side_effects)

    # @retry_network has max_attempts=4 by default
    links = await extract_links_fast("https://retry.example.com", verbose=False)

    assert "https://retry.example.com/page1" in links # Check for a known successful link
    assert mock_crawler_instance.arun.call_count == 3 # Called 3 times (2 fails, 1 success)

@patch("app.fast_discovery.AsyncWebCrawler", spec=AsyncWebCrawler)
async def test_extract_links_fast_fails_after_max_retries(mock_async_web_crawler_class, mock_clean_console):
    """Test that extract_links_fast fails if network issues persist beyond retries."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value
    # Always raise a retriable error
    mock_crawler_instance.arun = AsyncMock(side_effect=ConnectionRefusedError("Persistent connection failure"))

    # @retry_network has max_attempts=4 by default
    with pytest.raises(NetworkError) as exc_info:
        await extract_links_fast("https://persistentfail.example.com", verbose=False)

    assert "Network error during discovery: Persistent connection failure" in str(exc_info.value)
    assert mock_crawler_instance.arun.call_count == 4 # Called max_attempts times

def test_extract_links_fast_initial_invalid_url_not_retried(mock_clean_console):
    """
    Test that if the initial URL itself is invalid in a way that _extract_links_async
    catches it before AsyncWebCrawler is even called (or if it's caught by the outer try-except),
    it raises InvalidUrlError without retry.
    The `extract_links_fast` function itself doesn't do pre-validation, it relies on `_extract_links_async`.
    If `_extract_links_async` raises `InvalidUrlError` due to `AsyncWebCrawler` behavior,
    `@retry_network` would not retry `InvalidUrlError` by default.

    This test is a bit conceptual as the current structure has retry at the `extract_links_fast` level.
    If `_extract_links_async` raises `InvalidUrlError`, `retry_network` (which wraps `extract_links_fast`)
    would not retry it because `InvalidUrlError` is not in its `retry_on_exceptions` list.
    """
    # This test is more about ensuring InvalidUrlError isn't retried by @retry_network
    # We can simulate this by having _extract_links_async raise it directly.
    with patch("app.fast_discovery._extract_links_async", AsyncMock(side_effect=InvalidUrlError("Bad URL", url="bad", parse_error="test"))) as mock_internal_extract:
        with pytest.raises(InvalidUrlError):
            await extract_links_fast("bad", verbose=False)
        mock_internal_extract.assert_called_once() # Ensure it was called only once, no retry.
