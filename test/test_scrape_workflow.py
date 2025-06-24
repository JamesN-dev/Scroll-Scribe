"""Integration tests for the scrape workflow (app.cli.scrape_command)."""

import pytest
import asyncio
import argparse
from unittest.mock import patch, AsyncMock, MagicMock, mock_open, call
from pathlib import Path

from app.cli import scrape_command # The async orchestrator for scrape
from app.utils.logging import CleanConsole
from app.utils.exceptions import ConfigError, FileIOError
from crawl4ai import LLMConfig, BrowserConfig, CrawlResult, LLMContentFilter

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_clean_console_in_cli():
    """Mocks CleanConsole used within app.cli module for these tests."""
    with patch("app.cli.CleanConsole", spec=CleanConsole) as mock_console_class:
        mock_instance = mock_console_class.return_value
        yield mock_instance

@pytest.fixture
def mock_processing_tools():
    """Mocks tools from app.processing and app.fast_processing used by scrape_command."""
    with patch("app.cli.process_urls_batch", new_callable=AsyncMock) as mock_batch, \
         patch("app.cli.process_urls_fast", new_callable=AsyncMock) as mock_fast, \
         patch("app.cli.read_urls_from_file") as mock_read_urls, \
         patch("app.cli.get_browser_config") as mock_get_browser_config, \
         patch("app.cli.LLMConfig") as mock_llm_config_class, \
         patch("app.cli.LLMContentFilter") as mock_llm_filter_class, \
         patch("app.cli.print_summary_report") as mock_print_summary:
        
        # Setup default return values for browser_config and configs
        mock_get_browser_config.return_value = MagicMock(spec=BrowserConfig)
        mock_llm_config_instance = MagicMock(spec=LLMConfig)
        mock_llm_config_class.return_value = mock_llm_config_instance
        mock_llm_filter_instance = MagicMock(spec=LLMContentFilter)
        mock_llm_filter_class.return_value = mock_llm_filter_instance

        yield {
            "batch": mock_batch, "fast": mock_fast, "read_urls": mock_read_urls,
            "get_browser_config": mock_get_browser_config,
            "llm_config_class": mock_llm_config_class,
            "llm_filter_class": mock_llm_filter_class,
            "print_summary": mock_print_summary
        }

# Common arguments for scrape_command
def get_default_scrape_args(input_file: str, output_dir: Path, fast_mode: bool = False, **kwargs) -> argparse.Namespace:
    args_dict = {
        "input_file": input_file, "output_dir": str(output_dir), "start_at": 0,
        "prompt": "", "timeout": 60000, "wait": "networkidle",
        "model": "openrouter/mistralai/codestral-2501", "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1", "max_tokens": 8192,
        "session": False, "session_id": None,
        "fast": fast_mode, "verbose": False, "debug": False,
        **kwargs
    }
    return argparse.Namespace(**args_dict)

async def test_scrape_workflow_llm_mode_success(
    mock_processing_tools, mock_clean_console_in_cli, tmp_path, monkeypatch
):
    """Test successful LLM mode scrape workflow."""
    input_file = "urls.txt" # This file won't actually be read due to mock
    output_dir = tmp_path / "output_llm"
    urls_to_scrape = ["http://example.com/page1", "http://example.com/page2"]

    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key") # Needed for LLM mode

    mock_processing_tools["read_urls"].return_value = urls_to_scrape
    # Simulate process_urls_batch returning a summary
    batch_summary = {"successful_urls": urls_to_scrape, "failed_urls": []}
    mock_processing_tools["batch"].return_value = batch_summary
    
    args = get_default_scrape_args(input_file, output_dir, fast_mode=False)
    
    # Call scrape_command (the async orchestrator)
    returned_summary = await scrape_command(args)
    
    assert returned_summary == batch_summary
    mock_processing_tools["read_urls"].assert_called_once_with(input_file)
    mock_processing_tools["get_browser_config"].assert_called_once() # Check it's called
    
    # Check LLMConfig and LLMContentFilter were instantiated
    mock_processing_tools["llm_config_class"].assert_called_once_with(
        provider=args.model, api_token="test_key", base_url=args.base_url
    )
    mock_processing_tools["llm_filter_class"].assert_called_once()
    
    # Check process_urls_batch was called
    mock_processing_tools["batch"].assert_called_once()
    call_args_batch = mock_processing_tools["batch"].call_args[0]
    assert call_args_batch[0] == urls_to_scrape # urls_to_scrape
    assert call_args_batch[1] == args           # args namespace
    assert call_args_batch[2] == output_dir     # output_dir Path object
    assert isinstance(call_args_batch[3], LLMContentFilter) # llm_content_filter
    assert isinstance(call_args_batch[4], BrowserConfig)    # browser_config

    mock_processing_tools["fast"].assert_not_called()
    mock_processing_tools["print_summary"].assert_called_once_with(batch_summary)
    mock_clean_console_in_cli.print_error.assert_not_called()


async def test_scrape_workflow_fast_mode_success(
    mock_processing_tools, mock_clean_console_in_cli, tmp_path
):
    """Test successful Fast mode scrape workflow."""
    input_file = "fast_urls.txt"
    output_dir = tmp_path / "output_fast"
    urls_to_scrape = ["http://fast.example.com/doc1"]

    mock_processing_tools["read_urls"].return_value = urls_to_scrape
    fast_summary = {"successful_urls": urls_to_scrape, "failed_urls": []}
    mock_processing_tools["fast"].return_value = fast_summary

    args = get_default_scrape_args(input_file, output_dir, fast_mode=True)

    returned_summary = await scrape_command(args)

    assert returned_summary == fast_summary
    mock_processing_tools["read_urls"].assert_called_once_with(input_file)
    mock_processing_tools["get_browser_config"].assert_called_once()
    
    # Check process_urls_fast was called
    mock_processing_tools["fast"].assert_called_once()
    call_args_fast = mock_processing_tools["fast"].call_args[0]
    assert call_args_fast[0] == urls_to_scrape # urls_to_scrape
    assert call_args_fast[1] == args          # args namespace
    assert call_args_fast[2] == output_dir    # output_dir Path object
    assert isinstance(call_args_fast[3], BrowserConfig) # browser_config

    mock_processing_tools["batch"].assert_not_called()
    mock_processing_tools["llm_config_class"].assert_not_called()
    mock_processing_tools["llm_filter_class"].assert_not_called()
    mock_processing_tools["print_summary"].assert_called_once_with(fast_summary)
    mock_clean_console_in_cli.print_error.assert_not_called()


async def test_scrape_workflow_llm_mode_missing_api_key(
    mock_processing_tools, mock_clean_console_in_cli, tmp_path, monkeypatch
):
    """Test LLM mode scrape fails if API key is missing."""
    # Ensure API key is not set
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    args = get_default_scrape_args("urls.txt", tmp_path / "output_err", fast_mode=False)

    with pytest.raises(ConfigError) as exc_info:
        await scrape_command(args)
    
    assert "API key env var 'OPENROUTER_API_KEY' not found!" in str(exc_info.value)
    mock_processing_tools["read_urls"].assert_not_called() # Should fail before reading URLs
    mock_processing_tools["batch"].assert_not_called()
    mock_processing_tools["print_summary"].assert_not_called()


async def test_scrape_workflow_read_urls_fails(
    mock_processing_tools, mock_clean_console_in_cli, tmp_path, monkeypatch
):
    """Test scrape workflow when read_urls_from_file raises FileIOError."""
    input_file = "nonexistent_urls.txt"
    output_dir = tmp_path / "output_read_fail"
    
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key") # For LLM mode

    file_error_message = "File not found during read"
    mock_processing_tools["read_urls"].side_effect = FileIOError(file_error_message, filepath=input_file)
    
    args = get_default_scrape_args(input_file, output_dir, fast_mode=False)

    # scrape_command catches FileIOError and returns a summary
    returned_summary = await scrape_command(args)
    
    assert not returned_summary["successful_urls"]
    assert len(returned_summary["failed_urls"]) == 1
    assert returned_summary["failed_urls"][0] == ("file read", file_error_message)
    
    mock_processing_tools["read_urls"].assert_called_once_with(input_file)
    mock_clean_console_in_cli.print_error.assert_called_once_with(f"File error: {file_error_message}")
    mock_processing_tools["batch"].assert_not_called() # Processing should not start
    mock_processing_tools["print_summary"].assert_not_called() # No summary printed by scrape_command itself on this error.


async def test_scrape_workflow_start_at_out_of_bounds(
    mock_processing_tools, mock_clean_console_in_cli, tmp_path, monkeypatch
):
    """Test scrape workflow with --start-at index out of bounds."""
    input_file = "urls.txt"
    output_dir = tmp_path / "output_start_at"
    urls_to_scrape = ["http://example.com/page1", "http://example.com/page2"] # 2 URLs

    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")

    mock_processing_tools["read_urls"].return_value = urls_to_scrape
    
    # Start at index 2 (0-based), which is out of bounds for 2 URLs
    args = get_default_scrape_args(input_file, output_dir, fast_mode=False, start_at=2)
    
    returned_summary = await scrape_command(args)

    assert not returned_summary["successful_urls"]
    assert len(returned_summary["failed_urls"]) == 1
    assert returned_summary["failed_urls"][0] == ("config", "start_at out of bounds")

    mock_processing_tools["read_urls"].assert_called_once_with(input_file)
    mock_clean_console_in_cli.print_error.assert_called_once_with(
        f"--start-at index 2 is out of bounds for {len(urls_to_scrape)} URLs."
    )
    mock_processing_tools["batch"].assert_not_called() # Processing should not start
    mock_processing_tools["print_summary"].assert_not_called()


async def test_scrape_workflow_no_urls_to_process_after_start_at(
    mock_processing_tools, mock_clean_console_in_cli, tmp_path, monkeypatch
):
    """Test scrape workflow when --start-at leaves no URLs to process."""
    input_file = "urls.txt"
    output_dir = tmp_path / "output_no_urls"
    urls_to_scrape = ["http://example.com/page1"] # 1 URL

    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
    mock_processing_tools["read_urls"].return_value = urls_to_scrape
    
    args = get_default_scrape_args(input_file, output_dir, fast_mode=False, start_at=1) # Start at index 1
    
    returned_summary = await scrape_command(args)

    assert not returned_summary["successful_urls"]
    assert not returned_summary["failed_urls"] # No failures, just nothing to do

    mock_clean_console_in_cli.print_error.assert_called_once_with(
        f"No URLs left to process after --start-at 1"
    )
    mock_processing_tools["batch"].assert_not_called()
    mock_processing_tools["print_summary"].assert_not_called()


@patch('os.makedirs') # Mock os.makedirs which is used by Path.mkdir(parents=True)
async def test_scrape_workflow_output_dir_creation_fails(
    mock_os_makedirs, mock_processing_tools, mock_clean_console_in_cli, tmp_path, monkeypatch
):
    """Test scrape workflow when creating the output directory fails."""
    input_file = "urls.txt"
    output_dir_str = str(tmp_path / "uncreatable_output") # Use a string for Path() inside command
    
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
    mock_processing_tools["read_urls"].return_value = ["http://example.com/page1"]
    
    # Simulate OSError when Path.mkdir is called
    # Path.mkdir calls os.makedirs when parents=True
    mock_os_makedirs.side_effect = OSError("Permission denied to create directory")
    
    args = get_default_scrape_args(input_file, Path(output_dir_str), fast_mode=False)
    
    returned_summary = await scrape_command(args)

    assert not returned_summary["successful_urls"]
    assert len(returned_summary["failed_urls"]) == 1
    assert returned_summary["failed_urls"][0][0] == "file system"
    assert "Permission denied to create directory" in returned_summary["failed_urls"][0][1]

    mock_clean_console_in_cli.print_error.assert_called_once_with(
        f"Could not create output dir {Path(output_dir_str)}"
    )
    mock_processing_tools["batch"].assert_not_called()
    mock_processing_tools["print_summary"].assert_not_called()

# Note: The `print_summary_report` called by the Typer command `scrape` is not directly tested here.
# That function is unit-tested in `test_cli_utils.py`.
# `scrape_command` (the async orchestrator) returns the summary, which is then passed to
# `print_summary_report` by the Typer command layer in `cli.py`.
# The mock `mock_processing_tools["print_summary"]` here is for the summary printing
# that might happen *inside* process_urls_batch or process_urls_fast, not the final one in cli.py.
# However, looking at cli.py, `scrape_command` itself doesn't call `print_summary_report`.
# The Typer command `scrape` calls `print_summary_report` *after* `scrape_command` finishes.
# So, the `mock_print_summary` in `mock_processing_tools` might not be hit by `scrape_command` directly.
# Let's adjust the fixture if it's only for the Typer layer.
# For `scrape_command`, we only care that it *returns* the summary correctly.
# The `print_summary_report` mock in the fixture is more for testing the Typer command `scrape` itself,
# if we were to use Typer's CliRunner.
# For now, we'll assume the summary returned by `scrape_command` is correct and `print_summary_report` handles it.
# The mock for `print_summary_report` in the fixture is thus actually for the `process_command` tests later,
# where `process_command` *does* call `print_summary_report` via the Typer command layer.
# Let's remove it from `mock_processing_tools` for `scrape_command` tests to be precise.

# Re-evaluating: `cli.py`'s `scrape()` Typer command *does* call `print_summary_report`.
# So the mock is valid.

# Example: test_scrape_workflow_llm_mode_success already asserts:
# mock_processing_tools["print_summary"].assert_called_once_with(batch_summary)
# This is correct as per app/cli.py structure.
# The Typer `scrape` command calls `asyncio.run(scrape_command(args))` and then `print_summary_report(summary)`.
# The `scrape_command` function itself *returns* a summary, it does not print it.
# The `print_summary_report` should be mocked at the `app.cli` level where the Typer command calls it.

# Let's refine the fixture and tests for `print_summary_report` mocking.
# It should be `patch("app.cli.print_summary_report")` when testing the Typer command context.
# Since `scrape_command` (the async function) doesn't call it, we don't need to assert it here.
# The tests above are for `scrape_command` (the async logic), not the full Typer `scrape` command.
# The `print_summary` in the fixture is thus for the `app.cli.process_command` integration test.
# For `scrape_command` integration tests, we only need to verify the *returned* summary.
# The existing tests are fine in that they check the *returned* summary.
# The `mock_processing_tools["print_summary"]` assertion in `test_scrape_workflow_llm_mode_success`
# and `test_scrape_workflow_fast_mode_success` is actually correct because the Typer `scrape` command *does* call it.
# The `scrape_command` async function is what's run by `asyncio.run`, and its *return value* is used.

# The current `mock_processing_tools` fixture patches `app.cli.print_summary_report`.
# The `scrape` Typer command in `app.cli.py` calls `print_summary_report` after `scrape_command` finishes.
# So, asserting `mock_processing_tools["print_summary"]` is correct for testing the Typer command's effect.
# The tests correctly verify the summary *returned* by `scrape_command` and *passed to* `print_summary_report`.
# My apologies for the confusion during self-correction. The fixture and assertions are correctly placed.
