"""Integration tests for error handling in various ScrollScribe workflows."""

import pytest
import asyncio
import argparse
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path

# Import command orchestrators from app.cli
from app.cli import discover_command, scrape_command, process_command
from app.utils.logging import CleanConsole
from app.utils.exceptions import ConfigError, FileIOError, LLMError, NetworkError

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_clean_console_in_cli():
    """Mocks CleanConsole used within app.cli module."""
    with patch("app.cli.CleanConsole", spec=CleanConsole) as mock_console_class:
        mock_instance = mock_console_class.return_value
        yield mock_instance

# --- Tests for `discover_command` Error Handling ---

@patch("app.cli.extract_links_fast", new_callable=AsyncMock)
async def test_discover_error_extract_links_network_error(
    mock_extract_links, mock_clean_console_in_cli, tmp_path
):
    """Test discover_command when extract_links_fast raises a NetworkError."""
    start_url = "https://network-error.example.com"
    output_file = str(tmp_path / "net_error_links.txt")
    
    network_err_msg = "Simulated DNS failure"
    mock_extract_links.side_effect = NetworkError(network_err_msg, url=start_url)
    
    args = argparse.Namespace(start_url=start_url, output_file=output_file, verbose=False)
    result_code = await discover_command(args)
    
    assert result_code == 1 # Failure
    mock_extract_links.assert_called_once_with(start_url, False)
    mock_clean_console_in_cli.print_error.assert_called_once_with(
        f"Discovery failed: {NetworkError(network_err_msg, url=start_url)}" # Exception includes URL
    )

# --- Tests for `scrape_command` Error Handling ---

async def common_scrape_args(input_file_str: str, output_dir_path: Path, **kwargs):
    base = {
        "input_file": input_file_str, "output_dir": str(output_dir_path), "start_at": 0,
        "prompt": "", "timeout": 1000, "wait": "load", # Faster defaults for tests
        "model": "test-model", "api_key_env": "TEST_API_KEY",
        "base_url": "test-base-url", "max_tokens": 100,
        "session": False, "session_id": None,
        "fast": False, "verbose": False, "debug": False,
    }
    base.update(kwargs)
    return argparse.Namespace(**base)

@patch("app.cli.read_urls_from_file")
@patch("app.cli.process_urls_batch", new_callable=AsyncMock)
async def test_scrape_error_llm_mode_partial_batch_failure(
    mock_process_urls_batch, mock_read_urls, mock_clean_console_in_cli, tmp_path, monkeypatch
):
    """Test scrape_command in LLM mode where some URLs in a batch fail processing."""
    input_file = "partial_fail_urls.txt"
    output_dir = tmp_path / "output_partial_llm"
    urls = ["http://good.com/page1", "http://bad.com/page2", "http://good.com/page3"]
    
    monkeypatch.setenv("TEST_API_KEY", "fake_key")
    mock_read_urls.return_value = urls
    
    # Simulate process_urls_batch returning a mixed summary
    partial_summary = {
        "successful_urls": [urls[0], urls[2]],
        "failed_urls": [(urls[1], "LLM Timed Out")]
    }
    mock_process_urls_batch.return_value = partial_summary
    
    args = await common_scrape_args(input_file, output_dir, fast_mode=False)
    
    # scrape_command itself returns the summary. The Typer command layer would handle exit codes.
    returned_summary = await scrape_command(args) 
    
    assert returned_summary == partial_summary
    mock_process_urls_batch.assert_called_once()
    # print_summary_report is called by the Typer layer, not by scrape_command directly.
    # We are testing scrape_command's returned value here.
    # If we were testing the Typer `scrape` command, we'd mock print_summary_report.

@patch("app.cli.read_urls_from_file")
@patch("app.cli.process_urls_fast", new_callable=AsyncMock)
async def test_scrape_error_fast_mode_all_batch_failure(
    mock_process_urls_fast, mock_read_urls, mock_clean_console_in_cli, tmp_path
):
    """Test scrape_command in Fast mode where all URLs in a batch fail processing."""
    input_file = "all_fail_fast.txt"
    output_dir = tmp_path / "output_all_fail_fast"
    urls = ["http://fastfail.com/1", "http://fastfail.com/2"]
    
    mock_read_urls.return_value = urls
    
    all_fail_summary = {
        "successful_urls": [],
        "failed_urls": [(urls[0], "Fast Conversion Error"), (urls[1], "Content Too Short")]
    }
    mock_process_urls_fast.return_value = all_fail_summary
    
    args = await common_scrape_args(input_file, output_dir, fast_mode=True)
    returned_summary = await scrape_command(args)
    
    assert returned_summary == all_fail_summary
    mock_process_urls_fast.assert_called_once()


# --- Tests for `process_command` Error Handling ---

async def common_process_args(start_url_str: str, output_dir_path: Path, **kwargs):
    base = {
        "start_url": start_url_str, "output_dir": str(output_dir_path), "start_at": 0,
        "prompt": "", "timeout": 1000, "wait": "load",
        "model": "test-model-process", "api_key_env": "PROCESS_TEST_API_KEY",
        "base_url": "test-process-base-url", "max_tokens": 100,
        "session": False, "session_id": None,
        "fast": False, "verbose": False, "debug": False,
    }
    base.update(kwargs)
    return argparse.Namespace(**base)

@patch("tempfile.NamedTemporaryFile")
@patch("os.unlink")
@patch("app.cli.discover_command", new_callable=AsyncMock)
@patch("app.cli.scrape_command", new_callable=AsyncMock) # Mock the whole scrape_command
async def test_process_error_scrape_phase_fails_after_successful_discovery(
    mock_scrape_command, mock_discover_command, mock_os_unlink, mock_tempfile,
    mock_clean_console_in_cli, tmp_path, monkeypatch
):
    """Test process_command when discovery succeeds but the subsequent scrape phase fails."""
    start_url = "https://process.scrapefail.com"
    output_dir = tmp_path / "proc_scrape_fail"
    
    monkeypatch.setenv("PROCESS_TEST_API_KEY", "key_for_scrape_fail")

    # Mock tempfile
    mock_temp_file_obj = MagicMock()
    temp_file_name = str(tmp_path / "temp_proc_scrape_fail.txt")
    mock_temp_file_obj.name = temp_file_name
    mock_tempfile.return_value.__enter__.return_value = mock_temp_file_obj
    
    # Discovery succeeds
    mock_discover_command.return_value = 0 
    
    # Scrape phase returns an error summary
    scrape_failure_summary = {
        "successful_urls": [],
        "failed_urls": [("http://discovered.url/page1", "Scraping failed badly")]
    }
    mock_scrape_command.return_value = scrape_failure_summary
    
    args = await common_process_args(start_url, output_dir, fast_mode=False)
    
    # process_command should return the summary from scrape_command
    returned_summary = await process_command(args)
    
    assert returned_summary == scrape_failure_summary
    mock_discover_command.assert_called_once()
    
    # Check that scrape_command was called with the temp file from discovery
    mock_scrape_command.assert_called_once()
    scrape_args_ns = mock_scrape_command.call_args[0][0]
    assert scrape_args_ns.input_file == temp_file_name
    
    mock_os_unlink.assert_called_once_with(temp_file_name) # Temp file should still be cleaned up
    
    # The Typer layer of `process` command calls print_summary_report with this returned summary.
    # We don't mock print_summary_report here as we are testing process_command's return.


@patch("tempfile.NamedTemporaryFile")
@patch("os.unlink")
@patch("app.cli.discover_command", new_callable=AsyncMock)
@patch("app.cli.scrape_command", new_callable=AsyncMock)
async def test_process_error_llm_mode_api_key_missing_after_discovery(
    mock_scrape_command, mock_discover_command, mock_os_unlink, mock_tempfile,
    mock_clean_console_in_cli, tmp_path, monkeypatch
):
    """
    Test process_command in LLM mode: discovery succeeds, but API key is missing
    when it's time for the scrape phase.
    """
    start_url = "https://process.noapikey.com"
    output_dir = tmp_path / "proc_noapikey"
    
    # Ensure API key is NOT set for the scrape phase check in process_command
    monkeypatch.delenv("PROCESS_TEST_API_KEY", raising=False)

    mock_temp_file_obj = MagicMock()
    temp_file_name = str(tmp_path / "temp_proc_noapikey.txt")
    mock_temp_file_obj.name = temp_file_name
    mock_tempfile.return_value.__enter__.return_value = mock_temp_file_obj
    
    mock_discover_command.return_value = 0 # Discovery succeeds
    
    args = await common_process_args(start_url, output_dir, fast_mode=False, api_key_env="PROCESS_TEST_API_KEY")
    
    # process_command should raise ConfigError before calling scrape_command
    with pytest.raises(ConfigError) as exc_info:
        await process_command(args)
        
    assert "API key env var 'PROCESS_TEST_API_KEY' not found!" in str(exc_info.value)
    
    mock_discover_command.assert_called_once()
    mock_scrape_command.assert_not_called() # Scrape phase should not be reached
    mock_os_unlink.assert_called_once_with(temp_file_name) # Temp file cleanup should still occur

# General note: Many specific error types from underlying modules (like LLMError, NetworkError from processing)
# are expected to be caught within `process_urls_batch`/`process_urls_fast`.
# Those functions then return these errors in their summaries.
# The `scrape_command` and `process_command` orchestrators primarily deal with:
# 1. Configuration errors (API keys, bad args).
# 2. File I/O for the URL list.
# 3. Failures from the sub-commands they call (e.g., if discovery returns non-zero).
# 4. Propagating summaries that include errors from deeper down.
# These tests focus on errors at the orchestrator/CLI command level.```python
import pytest
import asyncio
import argparse
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path

# Import command orchestrators from app.cli
from app.cli import discover_command, scrape_command, process_command
from app.utils.logging import CleanConsole
from app.utils.exceptions import ConfigError, FileIOError, LLMError, NetworkError

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_clean_console_in_cli():
    """Mocks CleanConsole used within app.cli module."""
    with patch("app.cli.CleanConsole", spec=CleanConsole) as mock_console_class:
        mock_instance = mock_console_class.return_value
        yield mock_instance

# --- Tests for `discover_command` Error Handling ---

@patch("app.cli.extract_links_fast", new_callable=AsyncMock)
async def test_discover_error_extract_links_network_error(
    mock_extract_links, mock_clean_console_in_cli, tmp_path
):
    """Test discover_command when extract_links_fast raises a NetworkError."""
    start_url = "https://network-error.example.com"
    output_file = str(tmp_path / "net_error_links.txt")
    
    network_err_msg = "Simulated DNS failure"
    # Pass the url to the NetworkError constructor as the original code would
    simulated_exception = NetworkError(network_err_msg, url=start_url)
    mock_extract_links.side_effect = simulated_exception
    
    args = argparse.Namespace(start_url=start_url, output_file=output_file, verbose=False)
    result_code = await discover_command(args)
    
    assert result_code == 1 # Failure
    mock_extract_links.assert_called_once_with(start_url, False)
    # The discover_command catches Exception e and logs f"Discovery failed: {e}"
    # So the string representation of the simulated_exception is what we expect.
    mock_clean_console_in_cli.print_error.assert_called_once_with(
        f"Discovery failed: {simulated_exception}"
    )

# --- Tests for `scrape_command` Error Handling ---

def common_scrape_args_namespace(input_file_str: str, output_dir_path: Path, **kwargs) -> argparse.Namespace:
    base = {
        "input_file": input_file_str, "output_dir": str(output_dir_path), "start_at": 0,
        "prompt": "", "timeout": 1000, "wait": "load", # Faster defaults for tests
        "model": "test-model", "api_key_env": "TEST_API_KEY",
        "base_url": "test-base-url", "max_tokens": 100,
        "session": False, "session_id": None,
        "fast": False, "verbose": False, "debug": False,
    }
    base.update(kwargs)
    return argparse.Namespace(**base)

@patch("app.cli.read_urls_from_file")
@patch("app.cli.process_urls_batch", new_callable=AsyncMock)
@patch("app.cli.print_summary_report") # Mock at app.cli level
async def test_scrape_error_llm_mode_partial_batch_failure(
    mock_print_summary_cli, mock_process_urls_batch, mock_read_urls, 
    mock_clean_console_in_cli, tmp_path, monkeypatch
):
    """Test scrape_command in LLM mode where some URLs in a batch fail processing."""
    input_file = "partial_fail_urls.txt"
    output_dir = tmp_path / "output_partial_llm"
    urls = ["http://good.com/page1", "http://bad.com/page2", "http://good.com/page3"]
    
    monkeypatch.setenv("TEST_API_KEY", "fake_key")
    mock_read_urls.return_value = urls
    
    partial_summary = {
        "successful_urls": [urls[0], urls[2]],
        "failed_urls": [(urls[1], "LLM Timed Out")]
    }
    mock_process_urls_batch.return_value = partial_summary
    
    args = common_scrape_args_namespace(input_file, output_dir, fast_mode=False)
    
    # scrape_command is the async orchestrator. The Typer command `scrape` calls it.
    # We are testing the behavior of the Typer command `scrape` by checking print_summary_report.
    # The Typer command `scrape` would call `asyncio.run(scrape_command(args))`
    # and then `print_summary_report(summary)`.
    # To simulate this, we can call scrape_command and then check print_summary_report mock.
    
    # Simulate Typer's execution flow
    summary_from_async = await scrape_command(args)
    # Manually call the mocked print_summary_report as the Typer layer would
    # This is a bit of a workaround for not using CliRunner.
    # In cli.py: `summary = asyncio.run(scrape_command(args)); print_summary_report(summary)`
    # So, we check that `mock_print_summary_cli` was called with `summary_from_async`.
    # This requires print_summary_report to be mocked where it's called (app.cli)

    # This test structure is a bit off. `scrape_command` (async) doesn't call print_summary_report.
    # The Typer `scrape` command does.
    # For this unit/integration test of `scrape_command` (async), we check its *return*.
    
    assert summary_from_async == partial_summary
    mock_process_urls_batch.assert_called_once()
    # `print_summary_report` is NOT called by `scrape_command` directly.
    # It's called by the Typer `scrape` function.
    # So, for testing `scrape_command` (async), we don't assert `mock_print_summary_cli`.
    # That mock would be for a higher-level test using Typer's CliRunner.

@patch("app.cli.read_urls_from_file")
@patch("app.cli.process_urls_fast", new_callable=AsyncMock)
async def test_scrape_error_fast_mode_all_batch_failure(
    mock_process_urls_fast, mock_read_urls, mock_clean_console_in_cli, tmp_path
):
    """Test scrape_command in Fast mode where all URLs in a batch fail processing."""
    input_file = "all_fail_fast.txt"
    output_dir = tmp_path / "output_all_fail_fast"
    urls = ["http://fastfail.com/1", "http://fastfail.com/2"]
    
    mock_read_urls.return_value = urls
    
    all_fail_summary = {
        "successful_urls": [],
        "failed_urls": [(urls[0], "Fast Conversion Error"), (urls[1], "Content Too Short")]
    }
    mock_process_urls_fast.return_value = all_fail_summary
    
    args = common_scrape_args_namespace(input_file, output_dir, fast_mode=True)
    returned_summary = await scrape_command(args) # Test the async orchestrator
    
    assert returned_summary == all_fail_summary
    mock_process_urls_fast.assert_called_once()

# --- Tests for `process_command` Error Handling ---

def common_process_args_namespace(start_url_str: str, output_dir_path: Path, **kwargs) -> argparse.Namespace:
    base = {
        "start_url": start_url_str, "output_dir": str(output_dir_path), "start_at": 0,
        "prompt": "", "timeout": 1000, "wait": "load",
        "model": "test-model-process", "api_key_env": "PROCESS_TEST_API_KEY",
        "base_url": "test-process-base-url", "max_tokens": 100,
        "session": False, "session_id": None,
        "fast": False, "verbose": False, "debug": False,
    }
    base.update(kwargs)
    return argparse.Namespace(**base)

@patch("tempfile.NamedTemporaryFile")
@patch("os.unlink")
@patch("app.cli.discover_command", new_callable=AsyncMock)
@patch("app.cli.scrape_command", new_callable=AsyncMock) 
async def test_process_error_scrape_phase_fails_after_successful_discovery(
    mock_scrape_command, mock_discover_command, mock_os_unlink, mock_tempfile,
    mock_clean_console_in_cli, tmp_path, monkeypatch
):
    """Test process_command when discovery succeeds but the subsequent scrape phase fails."""
    start_url = "https://process.scrapefail.com"
    output_dir = tmp_path / "proc_scrape_fail"
    
    monkeypatch.setenv("PROCESS_TEST_API_KEY", "key_for_scrape_fail")

    mock_temp_file_obj = MagicMock()
    temp_file_name = str(tmp_path / "temp_proc_scrape_fail.txt")
    mock_temp_file_obj.name = temp_file_name
    mock_tempfile.return_value.__enter__.return_value = mock_temp_file_obj
    
    mock_discover_command.return_value = 0 
    
    scrape_failure_summary = {
        "successful_urls": [],
        "failed_urls": [("http://discovered.url/page1", "Scraping failed badly")]
    }
    mock_scrape_command.return_value = scrape_failure_summary
    
    args = common_process_args_namespace(start_url, output_dir, fast_mode=False)
    
    # process_command (async) returns the summary from scrape_command
    returned_summary = await process_command(args)
    
    assert returned_summary == scrape_failure_summary
    mock_discover_command.assert_called_once()
    
    mock_scrape_command.assert_called_once()
    scrape_args_ns = mock_scrape_command.call_args[0][0]
    assert scrape_args_ns.input_file == temp_file_name
    
    mock_os_unlink.assert_called_once_with(temp_file_name)
    # The Typer `process` command calls print_summary_report.
    # We are testing the async `process_command` here, so we don't mock/check print_summary_report.

@patch("tempfile.NamedTemporaryFile")
@patch("os.unlink")
@patch("app.cli.discover_command", new_callable=AsyncMock)
@patch("app.cli.scrape_command", new_callable=AsyncMock)
async def test_process_error_llm_mode_api_key_missing_after_discovery(
    mock_scrape_command, mock_discover_command, mock_os_unlink, mock_tempfile,
    mock_clean_console_in_cli, tmp_path, monkeypatch
):
    start_url = "https://process.noapikey.com"
    output_dir = tmp_path / "proc_noapikey"
    
    monkeypatch.delenv("PROCESS_TEST_API_KEY", raising=False)

    mock_temp_file_obj = MagicMock()
    temp_file_name = str(tmp_path / "temp_proc_noapikey.txt")
    mock_temp_file_obj.name = temp_file_name
    mock_tempfile.return_value.__enter__.return_value = mock_temp_file_obj
    
    mock_discover_command.return_value = 0 
    
    args = common_process_args_namespace(start_url, output_dir, fast_mode=False, api_key_env="PROCESS_TEST_API_KEY")
    
    with pytest.raises(ConfigError) as exc_info:
        await process_command(args) # Test the async orchestrator
        
    assert "API key env var 'PROCESS_TEST_API_KEY' not found!" in str(exc_info.value)
    
    mock_discover_command.assert_called_once()
    mock_scrape_command.assert_not_called() 
    mock_os_unlink.assert_called_once_with(temp_file_name)

```

This file (`tests/integration/test_error_handling.py`) provides a few examples. More specific error conditions from deeper modules (like `LLMError` from `processing.py`) are expected to be handled within those modules and result in failed items in the summary, which `scrape_command` or `process_command` then return. These tests focus on errors that occur at the CLI command orchestration level or that cause entire phases to fail.

I have now added the initial batch of unit tests and integration tests as per the plan.
