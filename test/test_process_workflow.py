"""Integration tests for the process workflow (app.cli.process_command)."""

import pytest
import asyncio
import argparse
from unittest.mock import patch, AsyncMock, MagicMock, call
from pathlib import Path
import tempfile # For checking temp file usage
import os # For os.unlink and os.getenv

# Function to be tested
from app.cli import process_command # The async orchestrator for process
from app.utils.logging import CleanConsole
from app.utils.exceptions import ConfigError

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_clean_console_in_cli():
    """Mocks CleanConsole used within app.cli module for these tests."""
    with patch("app.cli.CleanConsole", spec=CleanConsole) as mock_console_class:
        mock_instance = mock_console_class.return_value
        yield mock_instance

@pytest.fixture
def mock_command_orchestrators():
    """Mocks the underlying discover_command and scrape_command orchestrators."""
    with patch("app.cli.discover_command", new_callable=AsyncMock) as mock_discover, \
         patch("app.cli.scrape_command", new_callable=AsyncMock) as mock_scrape, \
         patch("app.cli.print_summary_report") as mock_print_summary: # process Typer command calls this
        yield {"discover": mock_discover, "scrape": mock_scrape, "print_summary": mock_print_summary}

# Common arguments for process_command
def get_default_process_args(start_url: str, output_dir: Path, fast_mode: bool = False, **kwargs) -> argparse.Namespace:
    args_dict = {
        "start_url": start_url, "output_dir": str(output_dir), "start_at": 0, # start_at for scrape phase
        "prompt": "", "timeout": 60000, "wait": "networkidle",
        "model": "openrouter/mistralai/codestral-2501", "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1", "max_tokens": 8192,
        "session": False, "session_id": None,
        "fast": fast_mode, "verbose": False, "debug": False,
        **kwargs
    }
    return argparse.Namespace(**args_dict)

@patch("tempfile.NamedTemporaryFile")
@patch("os.unlink")
async def test_process_workflow_llm_mode_success(
    mock_os_unlink,
    mock_tempfile,
    mock_command_orchestrators,
    mock_clean_console_in_cli, # Fixture
    tmp_path,
    monkeypatch
):
    """Test successful LLM mode process workflow."""
    start_url = "https://docs.llm.example.com"
    output_dir = tmp_path / "process_llm_output"
    
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key_llm")

    # Mock tempfile
    mock_temp_file_obj = MagicMock()
    mock_temp_file_obj.name = str(tmp_path / "temp_urls.txt") # Give it a predictable name
    mock_tempfile.return_value.__enter__.return_value = mock_temp_file_obj
    
    # Mock discover_command outcome
    # discover_command returns 0 for success, 1 for failure/no URLs
    mock_command_orchestrators["discover"].return_value = 0 
    
    # Mock scrape_command outcome
    scrape_summary = {"successful_urls": ["url1", "url2"], "failed_urls": []}
    mock_command_orchestrators["scrape"].return_value = scrape_summary

    args = get_default_process_args(start_url, output_dir, fast_mode=False, verbose=True)

    # Call process_command (the async orchestrator)
    # The Typer command `process` calls `asyncio.run(process_command(args))`
    # then `print_summary_report(summary_from_process_command)`
    # So, `process_command` itself should return the summary that `scrape_command` would.
    returned_summary_from_process = await process_command(args)
    
    assert returned_summary_from_process == scrape_summary

    # Verify discover_command call
    mock_command_orchestrators["discover"].assert_called_once()
    discover_args_ns = mock_command_orchestrators["discover"].call_args[0][0]
    assert isinstance(discover_args_ns, argparse.Namespace)
    assert discover_args_ns.start_url == start_url
    assert discover_args_ns.output_file == mock_temp_file_obj.name
    assert discover_args_ns.verbose == args.verbose # Ensure verbosity is passed down

    # Verify API key found log (since verbose=True and not fast mode)
    mock_clean_console_in_cli.print_info.assert_any_call(
        f"🔑 Found API key in env var: [bold lime]{args.api_key_env}[/bold lime]"
    )

    # Verify scrape_command call
    mock_command_orchestrators["scrape"].assert_called_once()
    scrape_args_ns = mock_command_orchestrators["scrape"].call_args[0][0]
    assert isinstance(scrape_args_ns, argparse.Namespace)
    assert scrape_args_ns.input_file == mock_temp_file_obj.name # Important check
    assert scrape_args_ns.output_dir == str(output_dir) # Passed correctly
    assert scrape_args_ns.fast == False
    # Other args like model, api_key_env, etc., should also match the original `args`

    # Verify tempfile usage and cleanup
    mock_tempfile.assert_called_once_with(mode="w", suffix=".txt", delete=False)
    mock_os_unlink.assert_called_once_with(mock_temp_file_obj.name)
    
    # Check console output from process_command itself
    mock_clean_console_in_cli.print_phase.assert_any_call(
        "UNIFIED PROCESSING", "Discovery + Scraping pipeline"
    )
    # The Typer `process` command calls print_summary_report, so we check the mock for that layer.
    # This mock is from `mock_command_orchestrators`.
    mock_command_orchestrators["print_summary"].assert_called_once_with(scrape_summary)


@patch("tempfile.NamedTemporaryFile")
@patch("os.unlink")
async def test_process_workflow_fast_mode_success(
    mock_os_unlink,
    mock_tempfile,
    mock_command_orchestrators,
    mock_clean_console_in_cli,
    tmp_path
):
    """Test successful Fast mode process workflow."""
    start_url = "https://docs.fast.example.com"
    output_dir = tmp_path / "process_fast_output"

    mock_temp_file_obj = MagicMock()
    mock_temp_file_obj.name = str(tmp_path / "temp_fast_urls.txt")
    mock_tempfile.return_value.__enter__.return_value = mock_temp_file_obj
    
    mock_command_orchestrators["discover"].return_value = 0 
    scrape_summary_fast = {"successful_urls": ["fast_url1"], "failed_urls": []}
    mock_command_orchestrators["scrape"].return_value = scrape_summary_fast

    args = get_default_process_args(start_url, output_dir, fast_mode=True, verbose=True)

    returned_summary = await process_command(args)
    assert returned_summary == scrape_summary_fast

    mock_command_orchestrators["discover"].assert_called_once()
    # Ensure fast mode is passed to scrape_command
    mock_command_orchestrators["scrape"].assert_called_once()
    scrape_args_ns = mock_command_orchestrators["scrape"].call_args[0][0]
    assert scrape_args_ns.fast is True

    # Verify "Fast mode enabled" log (since verbose=True and fast mode)
    mock_clean_console_in_cli.print_info.assert_any_call(
        "⚡ Fast mode enabled - no API key needed"
    )
    
    mock_os_unlink.assert_called_once_with(mock_temp_file_obj.name)
    mock_command_orchestrators["print_summary"].assert_called_once_with(scrape_summary_fast)


@patch("tempfile.NamedTemporaryFile")
@patch("os.unlink")
async def test_process_workflow_discovery_fails(
    mock_os_unlink,
    mock_tempfile,
    mock_command_orchestrators,
    mock_clean_console_in_cli,
    tmp_path,
    monkeypatch
):
    """Test process workflow when the discovery phase fails."""
    start_url = "https://docs.discover_fail.example.com"
    output_dir = tmp_path / "process_discover_fail"
    
    monkeypatch.setenv("OPENROUTER_API_KEY", "key_for_fail_test") # Set key to avoid ConfigError

    mock_temp_file_obj = MagicMock()
    mock_temp_file_obj.name = str(tmp_path / "temp_discover_fail.txt")
    mock_tempfile.return_value.__enter__.return_value = mock_temp_file_obj
    
    # Simulate discover_command failing (returns non-zero)
    mock_command_orchestrators["discover"].return_value = 1 
    
    args = get_default_process_args(start_url, output_dir, fast_mode=False)
    returned_summary = await process_command(args)

    # Expect a summary indicating discovery failure
    assert not returned_summary["successful_urls"]
    assert len(returned_summary["failed_urls"]) == 1
    assert returned_summary["failed_urls"][0] == ("discovery", "Failed to find any URLs")

    mock_command_orchestrators["discover"].assert_called_once()
    mock_command_orchestrators["scrape"].assert_not_called() # Scrape should not run
    
    mock_clean_console_in_cli.print_error.assert_called_once_with("Discovery phase failed")
    
    # Temp file should still be created and unlinked
    mock_tempfile.assert_called_once()
    mock_os_unlink.assert_called_once_with(mock_temp_file_obj.name)
    
    # print_summary_report in the Typer command layer would still be called with this error summary
    mock_command_orchestrators["print_summary"].assert_called_once_with(returned_summary)


async def test_process_workflow_llm_mode_missing_api_key(
    mock_command_orchestrators, # discover and scrape will be mocked
    mock_clean_console_in_cli,
    tmp_path,
    monkeypatch
):
    """Test LLM mode process workflow fails if API key is missing (checked before scrape)."""
    start_url = "https://docs.noapikey.example.com"
    output_dir = tmp_path / "process_noapikey"

    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False) # Ensure key is NOT set

    # Mock tempfile usage within process_command
    # We need to mock it here because it's used before the API key check for LLM mode.
    with patch("tempfile.NamedTemporaryFile") as mock_tempfile_direct, \
         patch("os.unlink") as mock_os_unlink_direct:
        
        mock_temp_file_obj_direct = MagicMock()
        mock_temp_file_obj_direct.name = str(tmp_path / "temp_noapikey.txt")
        mock_tempfile_direct.return_value.__enter__.return_value = mock_temp_file_obj_direct

        # Assume discovery part succeeds
        mock_command_orchestrators["discover"].return_value = 0

        args = get_default_process_args(start_url, output_dir, fast_mode=False)
        
        # process_command should catch ConfigError from the API key check
        with pytest.raises(ConfigError) as exc_info:
            await process_command(args)
        
        assert "API key env var 'OPENROUTER_API_KEY' not found!" in str(exc_info.value)

    mock_command_orchestrators["discover"].assert_called_once() # Discovery runs
    mock_command_orchestrators["scrape"].assert_not_called()  # Scrape should not run
    
    # Temp file created by process_command should be unlinked even if ConfigError occurs
    mock_os_unlink_direct.assert_called_once_with(mock_temp_file_obj_direct.name)
    
    # print_summary_report should not be called by the Typer layer if process_command raises unhandled ConfigError
    # However, the current process_command re-raises it.
    mock_command_orchestrators["print_summary"].assert_not_called()


@patch("tempfile.NamedTemporaryFile")
@patch("os.unlink")
async def test_process_workflow_tempfile_unlink_error_does_not_propagate(
    mock_os_unlink,
    mock_tempfile,
    mock_command_orchestrators,
    tmp_path,
    monkeypatch
):
    """Test that an error during os.unlink of the temp file is caught and does not stop processing."""
    start_url = "https://docs.unlinkfail.example.com"
    output_dir = tmp_path / "process_unlinkfail"
    monkeypatch.setenv("OPENROUTER_API_KEY", "key_unlink")

    mock_temp_file_obj = MagicMock()
    mock_temp_file_obj.name = str(tmp_path / "temp_unlink.txt")
    mock_tempfile.return_value.__enter__.return_value = mock_temp_file_obj
    
    mock_command_orchestrators["discover"].return_value = 0
    scrape_summary = {"successful_urls": ["url_ul1"], "failed_urls": []}
    mock_command_orchestrators["scrape"].return_value = scrape_summary

    # Simulate os.unlink raising an error
    mock_os_unlink.side_effect = OSError("Cannot unlink temp file")
    
    args = get_default_process_args(start_url, output_dir, fast_mode=False)
    
    # The error in os.unlink should be caught by the try/finally in process_command
    # and should not prevent the summary from being returned or print_summary_report from being called.
    returned_summary = await process_command(args)
    
    assert returned_summary == scrape_summary # Main operation should succeed
    mock_os_unlink.assert_called_once_with(mock_temp_file_obj.name)
    # The error from unlink is caught, so no exception should propagate from process_command
    
    # print_summary_report in Typer layer should still be called
    mock_command_orchestrators["print_summary"].assert_called_once_with(scrape_summary)

# Note: The Typer `process` command calls `print_summary_report`.
# `process_command` (the async function) returns the summary from its `scrape_command` call.
# The `mock_command_orchestrators["print_summary"]` correctly mocks the one called by the Typer layer.
# So, assertions on it are valid for testing the overall effect of the `process` command.
