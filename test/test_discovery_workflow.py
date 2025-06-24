"""Integration tests for the discovery workflow (app.cli.discover_command)."""

import pytest
import asyncio
import argparse
from unittest.mock import patch, AsyncMock, MagicMock, call

# Function to be tested (indirectly via discover_command)
from app.cli import discover_command # The async orchestrator for discovery
from app.utils.logging import CleanConsole # To mock console output

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_clean_console_in_cli():
    """Mocks CleanConsole used within app.cli module for these tests."""
    with patch("app.cli.CleanConsole", spec=CleanConsole) as mock_console_class:
        mock_instance = mock_console_class.return_value
        yield mock_instance

@patch("app.cli.extract_links_fast", new_callable=AsyncMock)
@patch("app.cli.save_links_to_file") # This is in app.discovery but imported into app.cli
async def test_discover_workflow_success(
    mock_save_links,
    mock_extract_links,
    mock_clean_console_in_cli, # Use the cli-specific mock
    tmp_path
):
    """Test the discover command workflow successfully finds and saves links."""
    start_url = "https://docs.example.com"
    output_filename = "discovered_links.txt"
    output_filepath_obj = tmp_path / output_filename # Not actually written by mock

    discovered_urls = {"https://docs.example.com/page1", "https://docs.example.com/page2"}
    mock_extract_links.return_value = discovered_urls

    args = argparse.Namespace(
        start_url=start_url,
        output_file=str(output_filepath_obj), # Pass string path
        verbose=False
    )

    # discover_command is the async function called by the Typer command
    result_code = await discover_command(args)

    assert result_code == 0 # Success
    mock_extract_links.assert_called_once_with(start_url, False) # url, verbose
    mock_save_links.assert_called_once_with(discovered_urls, str(output_filepath_obj), False) # urls, filename, verbose

    # Check console output
    mock_clean_console_in_cli.print_phase.assert_called_once_with(
        "DISCOVERY", f"Finding internal links from {start_url}"
    )
    mock_clean_console_in_cli.print_info.assert_called_once_with(
        f"Output file: {str(output_filepath_obj)}"
    )
    mock_clean_console_in_cli.print_success.assert_called_once_with(
        f"Discovery finished. Found {len(discovered_urls)} URLs."
    )
    mock_clean_console_in_cli.print_error.assert_not_called()
    mock_clean_console_in_cli.print_warning.assert_not_called()


@patch("app.cli.extract_links_fast", new_callable=AsyncMock)
@patch("app.cli.save_links_to_file")
async def test_discover_workflow_no_links_found(
    mock_save_links,
    mock_extract_links,
    mock_clean_console_in_cli,
    tmp_path
):
    """Test the discover command workflow when no links are found."""
    start_url = "https://empty.example.com"
    output_filename = "no_links.txt"
    output_filepath_str = str(tmp_path / output_filename)

    mock_extract_links.return_value = set() # No links found

    args = argparse.Namespace(
        start_url=start_url,
        output_file=output_filepath_str,
        verbose=True # Test verbose output
    )

    result_code = await discover_command(args)

    assert result_code == 1 # Should indicate non-zero for "no URLs"
    mock_extract_links.assert_called_once_with(start_url, True) # verbose=True
    mock_save_links.assert_not_called() # save_links_to_file should not be called if no URLs

    mock_clean_console_in_cli.print_phase.assert_called_once()
    mock_clean_console_in_cli.print_info.assert_called_once()
    mock_clean_console_in_cli.print_warning.assert_called_once_with(
        "No valid URLs extracted."
    )
    mock_clean_console_in_cli.print_success.assert_not_called()
    mock_clean_console_in_cli.print_error.assert_not_called()


@patch("app.cli.extract_links_fast", new_callable=AsyncMock)
@patch("app.cli.save_links_to_file")
async def test_discover_workflow_extraction_fails(
    mock_save_links,
    mock_extract_links,
    mock_clean_console_in_cli,
    tmp_path
):
    """Test the discover command workflow when extract_links_fast raises an exception."""
    start_url = "https://broken.example.com"
    output_filename = "broken_links.txt"
    output_filepath_str = str(tmp_path / output_filename)

    # Simulate extract_links_fast raising an error (e.g., NetworkError)
    simulated_error_message = "Simulated network failure during discovery"
    mock_extract_links.side_effect = Exception(simulated_error_message)

    args = argparse.Namespace(
        start_url=start_url,
        output_file=output_filepath_str,
        verbose=False
    )

    result_code = await discover_command(args)

    assert result_code == 1 # Failure
    mock_extract_links.assert_called_once_with(start_url, False)
    mock_save_links.assert_not_called() # Should not attempt to save

    mock_clean_console_in_cli.print_phase.assert_called_once()
    mock_clean_console_in_cli.print_info.assert_called_once()
    mock_clean_console_in_cli.print_error.assert_called_once_with(
        f"Discovery failed: {simulated_error_message}"
    )
    mock_clean_console_in_cli.print_success.assert_not_called()
    mock_clean_console_in_cli.print_warning.assert_not_called()

# Note: The actual file writing by `save_links_to_file` is not tested here as it's mocked.
# That function's own unit tests (if it had them, it's from legacy discovery.py)
# would cover the file I/O. Here, we confirm it's *called* correctly.
# If `save_links_to_file` itself could raise an error (e.g., FileIOError),
# that path could also be tested in `discover_command`.
# The current `discover_command` in `cli.py` has a try-except Exception around
# the block containing `extract_links_fast` and `save_links_to_file`.
# So, if `save_links_to_file` fails, it would also be caught and logged.

@patch("app.cli.extract_links_fast", new_callable=AsyncMock)
@patch("app.cli.save_links_to_file") # Mock to check its calls
async def test_discover_workflow_save_links_fails(
    mock_save_links_to_file, # Renamed to avoid conflict with outer scope
    mock_extract_links_fast_func, # Renamed
    mock_clean_console_in_cli,
    tmp_path
):
    """Test discover_command when save_links_to_file raises an exception."""
    start_url = "https://test.com"
    output_file = str(tmp_path / "output.txt")
    discovered_urls = {"https://test.com/link1"}

    mock_extract_links_fast_func.return_value = discovered_urls
    # Simulate save_links_to_file raising an OSError (which might become FileIOError)
    save_error_message = "Cannot write to disk"
    mock_save_links_to_file.side_effect = OSError(save_error_message)

    args = argparse.Namespace(start_url=start_url, output_file=output_file, verbose=False)
    
    result_code = await discover_command(args)

    assert result_code == 1 # Should be an error exit code
    mock_extract_links_fast_func.assert_called_once_with(start_url, False)
    mock_save_links_to_file.assert_called_once_with(discovered_urls, output_file, False)
    
    mock_clean_console_in_cli.print_error.assert_called_once_with(
        f"Discovery failed: {save_error_message}"
    )
    mock_clean_console_in_cli.print_success.assert_not_called()
