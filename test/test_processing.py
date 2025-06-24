"""Tests for LLM-powered processing utilities in app/processing.py."""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, mock_open, call, AsyncMock
from pathlib import Path
import time

from crawl4ai import BrowserConfig, CrawlResult, LLMContentFilter
from rich.progress import Task

from app.processing import (
    read_urls_from_file,
    url_to_filename,
    run_llm_filter,
    absolutify_links,
    process_urls_batch, # Main orchestration function
    RateColumn, # UI component
)
from app.utils.exceptions import FileIOError, LLMError, ProcessingError
from app.utils.logging import CleanConsole # For console output checks


# Mark all tests in this file as asyncio if they involve async functions
pytestmark = pytest.mark.asyncio

# Fixture for CleanConsole mock
@pytest.fixture
def mock_clean_console():
    with patch("app.processing.clean_console", spec=CleanConsole) as mock_console:
        # When progress_bar is called, its __enter__ should return a tuple
        # (mock_progress_instance, mock_task_id)
        mock_progress_instance = MagicMock()
        mock_task_id = MagicMock()
        mock_console.progress_bar.return_value.__enter__.return_value = (mock_progress_instance, mock_task_id)
        yield mock_console

# Fixture for logger mock
@pytest.fixture
def mock_logger():
    with patch("app.processing.logger") as mock_log:
        yield mock_log

# Tests for read_urls_from_file
def test_read_urls_from_file_success(mock_logger):
    """Test successfully reading URLs from a file."""
    file_content = "http://example.com/page1\nhttps://sub.example.com/path?query=true\n  http://another.com/  \ninvalid_line\n"
    expected_urls = [
        "http://example.com/page1",
        "https://sub.example.com/path?query=true",
        "http://another.com/",
    ]
    m = mock_open(read_data=file_content)
    with patch("builtins.open", m):
        urls = read_urls_from_file("dummy_path.txt")
    assert urls == expected_urls
    m.assert_called_once_with("dummy_path.txt", encoding="utf-8")
    mock_logger.info.assert_any_call("Reading URLs from: dummy_path.txt")
    mock_logger.warning.assert_called_once_with("Skipping invalid line: 'invalid_line'")
    mock_logger.info.assert_any_call(f"Found {len(expected_urls)} valid URLs in file")


def test_read_urls_from_file_not_found(mock_logger):
    """Test FileIOError when file is not found."""
    m = mock_open()
    m.side_effect = FileNotFoundError("File not here")
    with patch("builtins.open", m):
        with pytest.raises(FileIOError) as exc_info:
            read_urls_from_file("nonexistent.txt")
    assert "Input file not found: nonexistent.txt" in str(exc_info.value)
    mock_logger.error.assert_called_with("Input file not found: nonexistent.txt")

def test_read_urls_from_file_other_exception(mock_logger):
    """Test FileIOError for other read exceptions."""
    m = mock_open()
    m.side_effect = OSError("Cannot read file")
    with patch("builtins.open", m):
        with pytest.raises(FileIOError) as exc_info:
            read_urls_from_file("unreadable.txt")
    assert "Failed to read file: unreadable.txt" in str(exc_info.value)
    mock_logger.error.assert_called_with("Failed to read file: unreadable.txt")

# Tests for url_to_filename
@pytest.mark.parametrize(
    "url, index, extension, max_len, expected_filename",
    [
        ("http://example.com/path/to/doc", 1, ".md", 100, "page_001_path_to_doc.md"),
        ("https://example.com/", 2, ".txt", 100, "page_002_example.com.txt"),
        ("http://example.com/very/long/path/that/is/definitely/longer/than/allowed", 3, ".md", 20, "page_003_very_long_path_tha.md"),
        ("http://example.com/path?query=value&other=val", 4, ".md", 100, "page_004_path.md"),
        ("http://example.com/path with spaces/doc.html", 5, ".md", 100, "page_005_path_with_spaces_doc.html.md"),
        ("http://example.com/unsafe:*<>?\"|chars", 6, ".md", 100, "page_006_unsafe_chars.md"),
        ("malformed_url", 7, ".md", 100, "page_007.md"), # Fallback for unparseable URL
        ("http://example.com/ending_in_dot.", 8, ".md", 100, "page_008_ending_in_dot.md"),
        ("http://example.com/a", 9, ".md", 100, "page_009_a.md"),
        ("http://example.com/a/b.c_d-e", 10, ".md", 100, "page_010_a_b.c_d-e.md"),
    ]
)
def test_url_to_filename(url, index, extension, max_len, expected_filename, mock_logger):
    """Test url_to_filename with various inputs."""
    filename = url_to_filename(url, index, extension, max_len)
    assert filename == expected_filename
    if url == "malformed_url":
        mock_logger.error.assert_called_once_with(
            f"Failed to generate safe filename for URL index {index}. Using fallback."
        )


# Tests for run_llm_filter (mocking LLMContentFilter and ThreadPoolExecutor)
@patch("app.processing.ThreadPoolExecutor")
async def test_run_llm_filter_success(mock_executor_class, mock_logger):
    """Test successful LLM filtering."""
    mock_llm_filter_instance = MagicMock(spec=LLMContentFilter)
    mock_llm_filter_instance.filter_content.return_value = ["Chunk 1", "Chunk 2"]

    with patch("asyncio.get_event_loop") as mock_get_loop:
        mock_loop = mock_get_loop.return_value
        mock_loop.run_in_executor.return_value = ["Chunk 1", "Chunk 2"]

        html_content = "<div>Some HTML</div>"
        url = "http://example.com/llm_page"
        result = await run_llm_filter(mock_llm_filter_instance, html_content, url)

    assert result == "Chunk 1\n\n---\n\nChunk 2"
    mock_loop.run_in_executor.assert_called_once()
    assert mock_loop.run_in_executor.call_args[0][1] == mock_llm_filter_instance.filter_content
    assert mock_loop.run_in_executor.call_args[0][2] == html_content


async def test_run_llm_filter_empty_content(mock_logger):
    """Test run_llm_filter with empty HTML content."""
    mock_llm_filter_instance = MagicMock(spec=LLMContentFilter)
    result = await run_llm_filter(mock_llm_filter_instance, "", "http://example.com/empty")
    assert result is None
    mock_llm_filter_instance.filter_content.assert_not_called()

@patch("asyncio.get_event_loop")
async def test_run_llm_filter_llm_failure(mock_get_loop, mock_logger):
    """Test run_llm_filter when the LLM filter itself raises an exception."""
    mock_llm_filter_instance = MagicMock(spec=LLMContentFilter)
    
    mock_loop = mock_get_loop.return_value
    test_exception = ValueError("LLM processing failed internally")
    mock_loop.run_in_executor.side_effect = test_exception

    html_content = "<div>HTML that causes failure</div>"
    url = "http://example.com/llm_fail"

    with pytest.raises(LLMError) as exc_info:
        await run_llm_filter(mock_llm_filter_instance, html_content, url)

    assert "LLM filter failed: LLM processing failed internally" in str(exc_info.value)
    assert exc_info.value.url == url
    assert exc_info.value.__cause__ == test_exception

# Tests for absolutify_links
@pytest.mark.parametrize(
    "markdown_text, base_url, expected_text",
    [
        ("No links here.", "http://example.com", "No links here."),
        ("[Relative](./page.md)", "http://example.com/docs/", "[Relative](http://example.com/docs/page.md)"),
        ("Text with [absolute](https://othersite.com/abs) link.", "http://example.com", "Text with [absolute](https://othersite.com/abs) link."),
        ("[Fragment](#section)", "http://example.com/page", "[Fragment](#section)"),
        ("Link with [query params](path?q=1)", "http://base.com/", "Link with [query params](http://base.com/path?q=1)"),
        ("Multiple: [one](./1) and [two](../2)", "http://a.com/sub/folder/", "Multiple: [one](http://a.com/sub/folder/1) and [two](http://a.com/sub/2)"),
        ('<a href="rel/path.html">Relative HTML</a>', "http://base.com/", '<a href="http://base.com/rel/path.html">Relative HTML</a>'),
        ('<a href="https://absolute.com">Absolute HTML</a>', "http://base.com/", '<a href="https://absolute.com">Absolute HTML</a>'),
        ('<a href="#frag">Fragment HTML</a>', "http://base.com/", '<a href="#frag">Fragment HTML</a>'),
        ('Mixed: [MD](./md) and <a href="./html">HTML</a>', "http://x.com/d/", 'Mixed: [MD](http://x.com/d/md) and <a href="http://x.com/d/html">HTML</a>'),
        ('No base URL: [link](./foo)', "", 'No base URL: [link](./foo)'),
        ('Invalid relative link resolution: [link](http://)', "http://example.com", 'Invalid relative link resolution: [link](http://)'),
    ]
)
def test_absolutify_links(markdown_text, base_url, expected_text, mock_logger):
    """Test absolutify_links for various Markdown and HTML link patterns."""
    result = absolutify_links(markdown_text, base_url)
    assert result == expected_text
    if not base_url and "[link](./foo)" in markdown_text :
        mock_logger.warning.assert_called_with(
            "Base URL not provided to absolutify_links, skipping post-processing."
        )

# Tests for RateColumn
def test_rate_column_render_not_started():
    column = RateColumn()
    mock_task = MagicMock(spec=Task, completed=0, start_time=None)
    assert column.render(mock_task).plain == "-.-- s/item"

def test_rate_column_render_in_progress_no_completion():
    column = RateColumn()
    mock_task = MagicMock(spec=Task, completed=0, start_time=time.monotonic() - 10, finished_time=None)
    assert column.render(mock_task).plain == "-.-- s/item"

def test_rate_column_render_completed():
    column = RateColumn()
    current_time = time.monotonic()
    mock_task = MagicMock(spec=Task, completed=10, start_time=current_time - 20, finished_time=current_time)
    
    rendered_text = column.render(mock_task).plain
    assert "s/item" in rendered_text
    val_part = rendered_text.split(" ")[0]
    try:
        rate_val = float(val_part)
        assert 1.9 < rate_val < 2.1 # Approx 2.00 s/item
    except ValueError:
        pytest.fail(f"Could not parse rate value from: {rendered_text}")

# Tests for process_urls_batch
@patch("app.processing.AsyncWebCrawler")
@patch("app.processing.run_llm_filter", new_callable=AsyncMock)
@patch("app.processing.absolutify_links")
@patch("app.processing.url_to_filename")
@patch("builtins.open", new_callable=mock_open)
async def test_process_urls_batch_success_flow(
    mock_file_open,
    mock_url_to_filename,
    mock_absolutify_links,
    mock_run_llm_filter,
    mock_async_web_crawler_class,
    mock_clean_console, 
    mock_logger, 
    tmp_path: Path
):
    mock_crawler_instance = mock_async_web_crawler_class.return_value.__aenter__.return_value
    urls_to_scrape = ["http://example.com/page1", "http://example.com/page2"]
    mock_crawl_results = [
        MagicMock(spec=CrawlResult, success=True, cleaned_html="HTML1", html="HTML1", error_message=None),
        MagicMock(spec=CrawlResult, success=True, cleaned_html="HTML2", html="HTML2", error_message=None),
    ]
    mock_crawler_instance.arun_many.return_value = mock_crawl_results
    mock_run_llm_filter.side_effect = ["MD1", "MD2"]
    mock_absolutify_links.side_effect = lambda md, url: f"Abs_{md}_{url}"
    mock_url_to_filename.side_effect = ["file1.md", "file2.md"]

    mock_args = MagicMock(start_at=0, verbose=False, session_id=None, session=False, wait="n", timeout=1, model="m")
    output_dir = tmp_path
    mock_llm_content_filter = MagicMock(spec=LLMContentFilter)
    mock_browser_config = MagicMock(spec=BrowserConfig)

    summary = await process_urls_batch(
        urls_to_scrape, mock_args, output_dir, mock_llm_content_filter, mock_browser_config
    )

    assert summary["successful_urls"] == urls_to_scrape
    assert not summary["failed_urls"]
    mock_clean_console.print_summary.assert_called_once()
    # Check success_count passed to print_summary
    assert mock_clean_console.print_summary.call_args[0][0] == 2 
    
    mock_file_open.assert_any_call(output_dir / "file1.md", "w", encoding="utf-8")
    mock_file_open.return_value.__enter__.return_value.write.assert_any_call("Abs_MD1_http://example.com/page1")


@patch("app.processing.AsyncWebCrawler")
@patch("app.processing.run_llm_filter", new_callable=AsyncMock)
async def test_process_urls_batch_llm_filter_fails(
    mock_run_llm_filter,
    mock_async_web_crawler_class,
    mock_clean_console,
    mock_logger,
    tmp_path: Path
):
    mock_crawler_instance = mock_async_web_crawler_class.return_value.__aenter__.return_value
    urls_to_scrape = ["http://example.com/fpage1"]
    mock_crawl_results = [MagicMock(spec=CrawlResult, success=True, cleaned_html="HTML_F", html="HTML_F")]
    mock_crawler_instance.arun_many.return_value = mock_crawl_results
    llm_failure_exception = LLMError("LLM ERR", url=urls_to_scrape[0])
    mock_run_llm_filter.side_effect = llm_failure_exception

    mock_args = MagicMock(start_at=0, verbose=True, session_id=None, session=False, wait="l", timeout=10, model="mfail")
    summary = await process_urls_batch(
        urls_to_scrape, mock_args, tmp_path, MagicMock(), MagicMock()
    )

    assert not summary["successful_urls"]
    assert summary["failed_urls"][0] == (urls_to_scrape[0], str(llm_failure_exception))
    
    # Check if print_url_status was called with error details
    # This requires the mock_clean_console to have its progress_bar context manager set up
    mock_progress_instance, mock_task_id = mock_clean_console.progress_bar.return_value.__enter__.return_value
    
    # Check for the specific error log call
    error_call_found = False
    for call_obj in mock_clean_console.print_url_status.call_args_list:
        if call_obj.args[0] == urls_to_scrape[0] and call_obj.args[1] == "error":
            assert str(llm_failure_exception) in call_obj.args[3] # details
            assert call_obj.kwargs.get('progress_console') is mock_progress_instance.console
            error_call_found = True
            break
    assert error_call_found, "print_url_status for LLMError not found or not progress_console aware."


@patch("app.processing.AsyncWebCrawler")
async def test_process_urls_batch_html_fetch_fails(
    mock_async_web_crawler_class,
    mock_clean_console,
    mock_logger,
    tmp_path: Path
):
    mock_crawler_instance = mock_async_web_crawler_class.return_value.__aenter__.return_value
    urls = ["http://ok.com/p1", "http://fail.com/p2"]
    results = [
        MagicMock(spec=CrawlResult, success=True, cleaned_html="H_OK", html="H_OK", url=urls[0]),
        MagicMock(spec=CrawlResult, success=False, error_message="Timeout", url=urls[1], cleaned_html=None, html=None),
    ]
    mock_crawler_instance.arun_many.return_value = results

    with patch("app.processing.run_llm_filter", AsyncMock(return_value="MD_OK")), \
         patch("builtins.open", new_callable=mock_open): # Mock open for the successful one
        mock_args = MagicMock(start_at=0, verbose=True, session_id=None, session=False, wait="l", timeout=10, model="mfetch")
        summary = await process_urls_batch(
            urls, mock_args, tmp_path, MagicMock(), MagicMock()
        )

    assert summary["successful_urls"] == [urls[0]]
    assert summary["failed_urls"][0] == (urls[1], "Timeout")
    
    mock_progress_instance, mock_task_id = mock_clean_console.progress_bar.return_value.__enter__.return_value
    error_call_found = False
    for call_obj in mock_clean_console.print_url_status.call_args_list:
        if call_obj.args[0] == urls[1] and call_obj.args[1] == "error":
            assert "Timeout" in call_obj.args[3]
            assert call_obj.kwargs.get('progress_console') is mock_progress_instance.console
            error_call_found = True
            break
    assert error_call_found, "print_url_status for HTML fetch error not found."


@patch("app.processing.AsyncWebCrawler")
async def test_process_urls_batch_keyboard_interrupt(
    mock_async_web_crawler_class,
    mock_clean_console,
    mock_logger,
    tmp_path
):
    mock_crawler_instance = mock_async_web_crawler_class.return_value.__aenter__.return_value
    urls = ["http://site.com/page1", "http://site.com/page2"]
    results = [
        MagicMock(spec=CrawlResult, success=True, cleaned_html="H1", html="H1"),
        MagicMock(spec=CrawlResult, success=True, cleaned_html="H2", html="H2"),
    ]
    mock_crawler_instance.arun_many.return_value = results

    with patch("app.processing.run_llm_filter", AsyncMock(side_effect=KeyboardInterrupt)):
        mock_args = MagicMock(start_at=0, verbose=False, session_id=None, session=False, wait="l", timeout=10, model="mkey")
        summary = await process_urls_batch(
            urls, mock_args, tmp_path, MagicMock(), MagicMock()
        )

    assert not summary["successful_urls"]
    assert not summary["failed_urls"] # KeyboardInterrupt does not add to failed_urls
    mock_clean_console.print_warning.assert_any_call(
        "KeyboardInterrupt caught during URL processing. Signaling shutdown..."
    )
    mock_clean_console.print_summary.assert_called_once()
