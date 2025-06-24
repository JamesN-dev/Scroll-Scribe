"""Tests for fast (non-LLM) processing utilities in app/fast_processing.py."""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, mock_open, call, AsyncMock
from pathlib import Path

from crawl4ai import BrowserConfig, CrawlResult, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from app.fast_processing import process_urls_fast
from app.utils.logging import CleanConsole # For console output checks

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

# Fixture for CleanConsole mock
@pytest.fixture
def mock_clean_console():
    with patch("app.fast_processing.clean_console", spec=CleanConsole) as mock_console:
        # Mock the console used by Rich Live/Progress if it's directly from clean_console.console
        mock_rich_console_for_progress = MagicMock()
        mock_console.console = mock_rich_console_for_progress
        yield mock_console

# Fixture for logger mock
@pytest.fixture
def mock_logger():
    with patch("app.fast_processing.logger") as mock_log:
        yield mock_log

# Fixture to mock Rich Live and Progress
@pytest.fixture
def mock_rich_live_progress():
    with patch("app.fast_processing.Live") as mock_live_class, \
         patch("app.fast_processing.Progress") as mock_progress_class:
        
        mock_live_instance = mock_live_class.return_value.__enter__.return_value
        mock_progress_instance = mock_progress_class.return_value
        
        # Simulate the structure returned by CleanConsole's progress_bar if used,
        # or direct Progress usage. For fast_processing, it's direct.
        mock_task_id = mock_progress_instance.add_task.return_value
        
        yield {
            "live_class": mock_live_class,
            "progress_class": mock_progress_class,
            "live_instance": mock_live_instance,
            "progress_instance": mock_progress_instance,
            "task_id": mock_task_id,
        }

@patch("app.fast_processing.AsyncWebCrawler")
@patch("app.fast_processing.absolutify_links") # Mock shared utility
@patch("app.fast_processing.url_to_filename")   # Mock shared utility
@patch("builtins.open", new_callable=mock_open)
async def test_process_urls_fast_success_flow(
    mock_file_open,
    mock_url_to_filename,
    mock_absolutify_links,
    mock_async_web_crawler_class,
    mock_rich_live_progress, # Fixture
    mock_clean_console,      # Fixture
    mock_logger,             # Fixture
    tmp_path: Path
):
    """Test the successful processing flow of process_urls_fast."""
    # Setup Mocks for AsyncWebCrawler
    mock_crawler_instance = mock_async_web_crawler_class.return_value.__aenter__.return_value
    
    urls_to_scrape = ["http://example.com/fast1", "http://example.com/fast2"]
    # Mock CrawlResult with markdown attribute
    mock_crawl_results = [
        MagicMock(spec=CrawlResult, success=True, markdown=MagicMock(raw_markdown="Raw MD for page1"), error_message=None),
        MagicMock(spec=CrawlResult, success=True, markdown=MagicMock(raw_markdown="Raw MD for page2"), error_message=None),
    ]
    mock_crawler_instance.arun_many.return_value = mock_crawl_results

    # Mock shared utilities
    mock_absolutify_links.side_effect = lambda md, url: f"Absolutified_Fast: {md} for {url}"
    mock_url_to_filename.side_effect = ["fast_page1.md", "fast_page2.md"]

    # Prepare arguments for process_urls_fast
    mock_args = MagicMock()
    mock_args.start_at = 0 # Used for original_index calculation in url_to_filename
    mock_args.session_id = None
    mock_args.session = False
    mock_args.wait = "domcontentloaded" # Different from LLM processing default
    mock_args.timeout = 20000

    output_dir = tmp_path
    mock_browser_config = MagicMock(spec=BrowserConfig)

    # Call the function
    summary = await process_urls_fast(
        urls_to_scrape, mock_args, output_dir, mock_browser_config
    )

    # Assertions
    assert summary["successful_urls"] == urls_to_scrape
    assert not summary["failed_urls"]
    
    # Check AsyncWebCrawler instantiation and arun_many call
    mock_async_web_crawler_class.assert_called_once_with(config=mock_browser_config)
    mock_crawler_instance.arun_many.assert_called_once()
    # Verify the config used in arun_many
    arun_many_config: CrawlerRunConfig = mock_crawler_instance.arun_many.call_args[1]['config']
    assert isinstance(arun_many_config.markdown_generator, DefaultMarkdownGenerator)
    assert isinstance(arun_many_config.markdown_generator.content_filter, PruningContentFilter)
    assert arun_many_config.wait_until == "domcontentloaded"

    # Check calls to shared utilities
    assert mock_absolutify_links.call_count == 2
    mock_absolutify_links.assert_any_call("Raw MD for page1", urls_to_scrape[0])

    assert mock_url_to_filename.call_count == 2
    mock_url_to_filename.assert_any_call(urls_to_scrape[0], 1) # Original index

    # Check file writes
    assert mock_file_open.call_count == 2
    handle = mock_file_open.return_value.__enter__.return_value
    handle.write.assert_any_call("Absolutified_Fast: Raw MD for page1 for http://example.com/fast1")
    
    # Check Rich Progress and Live were used
    mock_rich_live_progress["live_class"].assert_called_once()
    mock_rich_live_progress["progress_class"].assert_called_once()
    mock_progress_instance = mock_rich_live_progress["progress_instance"]
    mock_task_id = mock_rich_live_progress["task_id"]
    mock_progress_instance.add_task.assert_called_once()
    assert mock_progress_instance.update.call_count == len(urls_to_scrape)
    mock_progress_instance.update.assert_any_call(mock_task_id, advance=1)

    # Check console summary outputs
    mock_clean_console.print_summary.assert_called_once()
    assert mock_clean_console.print_summary.call_args[0][0] == 2 # success_count
    mock_clean_console.print_success.assert_any_call(pytest.stringMatching(r"Fast mode completed: \d+\.\d+ pages/minute"))


@patch("app.fast_processing.AsyncWebCrawler")
async def test_process_urls_fast_crawl_result_no_markdown(
    mock_async_web_crawler_class,
    mock_rich_live_progress,
    mock_clean_console,
    mock_logger,
    tmp_path: Path
):
    """Test scenario where a crawl result is successful but has no markdown content."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value.__aenter__.return_value
    urls_to_scrape = ["http://example.com/no_md"]
    # Simulate success but markdown.raw_markdown is empty or too short
    mock_crawl_results = [
        MagicMock(spec=CrawlResult, success=True, markdown=MagicMock(raw_markdown="  "), error_message=None),
    ]
    mock_crawler_instance.arun_many.return_value = mock_crawl_results

    mock_args = MagicMock(start_at=0, session_id=None, session=False, wait="load", timeout=1000)
    summary = await process_urls_fast(
        urls_to_scrape, mock_args, tmp_path, MagicMock(spec=BrowserConfig)
    )

    assert not summary["successful_urls"]
    assert len(summary["failed_urls"]) == 1
    assert summary["failed_urls"][0] == (urls_to_scrape[0], "empty content")
    
    # Check that print_url_status was called with warning
    mock_clean_console.print_url_status.assert_called_with(
        urls_to_scrape[0], "warning", 0, "empty content"
    )
    mock_rich_live_progress["progress_instance"].update.assert_called_once()


@patch("app.fast_processing.AsyncWebCrawler")
async def test_process_urls_fast_crawl_failure(
    mock_async_web_crawler_class,
    mock_rich_live_progress,
    mock_clean_console,
    mock_logger,
    tmp_path: Path
):
    """Test scenario where arun_many returns a failed CrawlResult."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value.__aenter__.return_value
    urls_to_scrape = ["http://example.com/crawl_fails"]
    crawl_error_message = "Simulated DNS resolution error"
    mock_crawl_results = [
        MagicMock(spec=CrawlResult, success=False, markdown=None, error_message=crawl_error_message),
    ]
    mock_crawler_instance.arun_many.return_value = mock_crawl_results

    mock_args = MagicMock(start_at=0, session_id=None, session=False, wait="load", timeout=1000)
    summary = await process_urls_fast(
        urls_to_scrape, mock_args, tmp_path, MagicMock(spec=BrowserConfig)
    )

    assert not summary["successful_urls"]
    assert len(summary["failed_urls"]) == 1
    assert summary["failed_urls"][0] == (urls_to_scrape[0], crawl_error_message)
    
    mock_clean_console.print_url_status.assert_called_with(
        urls_to_scrape[0], "error", 0, crawl_error_message
    )
    mock_logger.error.assert_called_with(f"Fast processing failed: {crawl_error_message}")


@patch("app.fast_processing.AsyncWebCrawler")
@patch("builtins.open", new_callable=mock_open)
async def test_process_urls_fast_file_save_error(
    mock_file_open,
    mock_async_web_crawler_class,
    mock_rich_live_progress,
    mock_clean_console,
    mock_logger,
    tmp_path: Path
):
    """Test scenario where saving the markdown file fails."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value.__aenter__.return_value
    urls_to_scrape = ["http://example.com/save_fail"]
    mock_crawl_results = [
        MagicMock(spec=CrawlResult, success=True, markdown=MagicMock(raw_markdown="Valid MD"), error_message=None),
    ]
    mock_crawler_instance.arun_many.return_value = mock_crawl_results

    # Mock shared utilities that are called before file open
    with patch("app.fast_processing.absolutify_links", return_value="Abs_MD"), \
         patch("app.fast_processing.url_to_filename", return_value="file_save_fail.md"):
        
        # Simulate OSError on file open
        mock_file_open.side_effect = OSError("Disk full")

        mock_args = MagicMock(start_at=0, session_id=None, session=False, wait="load", timeout=1000)
        summary = await process_urls_fast(
            urls_to_scrape, mock_args, tmp_path, MagicMock(spec=BrowserConfig)
        )

    assert not summary["successful_urls"]
    assert len(summary["failed_urls"]) == 1
    assert summary["failed_urls"][0][0] == urls_to_scrape[0]
    assert "save failed: Disk full" in summary["failed_urls"][0][1]
    
    mock_clean_console.print_url_status.assert_called_with(
        urls_to_scrape[0], "error", 0, "save failed"
    )
    mock_logger.error.assert_called_with(
        f"Failed to save markdown for {urls_to_scrape[0]} to {tmp_path / 'file_save_fail.md'}: Disk full"
    )


@patch("app.fast_processing.AsyncWebCrawler")
async def test_process_urls_fast_keyboard_interrupt_in_loop(
    mock_async_web_crawler_class,
    mock_rich_live_progress,
    mock_clean_console,
    mock_logger,
    tmp_path: Path
):
    """Test handling of KeyboardInterrupt inside the URL processing loop."""
    mock_crawler_instance = mock_async_web_crawler_class.return_value.__aenter__.return_value
    urls_to_scrape = ["http://example.com/page1", "http://example.com/page2"]
    
    # Simulate results for arun_many
    mock_crawl_results = [
        MagicMock(spec=CrawlResult, success=True, markdown=MagicMock(raw_markdown="MD1")),
        MagicMock(spec=CrawlResult, success=True, markdown=MagicMock(raw_markdown="MD2")), # This one won't be processed
    ]
    mock_crawler_instance.arun_many.return_value = mock_crawl_results

    # Make absolutify_links raise KeyboardInterrupt on the first call
    with patch("app.fast_processing.absolutify_links", side_effect=KeyboardInterrupt) as mock_abs_links_interrupt:
        mock_args = MagicMock(start_at=0, session_id=None, session=False, wait="load", timeout=1000)
        summary = await process_urls_fast(
            urls_to_scrape, mock_args, tmp_path, MagicMock(spec=BrowserConfig)
        )
    
    assert not summary["successful_urls"]
    # KeyboardInterrupt doesn't add to failed_urls in the current implementation
    assert not summary["failed_urls"] 
    
    mock_abs_links_interrupt.assert_called_once() # Should be called for the first URL
    mock_clean_console.print_warning.assert_any_call(
        "KeyboardInterrupt caught during fast processing. Signaling shutdown..."
    )
    mock_clean_console.print_summary.assert_called_once() # Summary should still print


@patch("app.fast_processing.AsyncWebCrawler", new_callable=AsyncMock) # Mock the class itself as async
async def test_process_urls_fast_keyboard_interrupt_in_with_live(
    mock_async_web_crawler_class, # This is now an AsyncMock for the class
    mock_rich_live_progress, # Original fixture
    mock_clean_console,
    mock_logger,
    tmp_path: Path
):
    """Test handling of KeyboardInterrupt within the Live context manager setup."""
    # Make the __enter__ of the Live instance raise KeyboardInterrupt
    mock_rich_live_progress["live_class"].return_value.__enter__.side_effect = KeyboardInterrupt

    urls_to_scrape = ["http://example.com/page1"]
    mock_args = MagicMock(start_at=0, session_id=None, session=False, wait="load", timeout=1000)
    
    summary = await process_urls_fast(
        urls_to_scrape, mock_args, tmp_path, MagicMock(spec=BrowserConfig)
    )

    assert not summary["successful_urls"]
    assert not summary["failed_urls"]
    
    mock_clean_console.print_warning.assert_called_with(
        "KeyboardInterrupt caught outside main loop. Shutting down fast mode..."
    )
    mock_clean_console.print_summary.assert_called_once()
    # AsyncWebCrawler should not have been entered if Live setup failed
    mock_async_web_crawler_class.return_value.__aenter__.assert_not_called()
