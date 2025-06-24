"""Tests for utility functions within app/cli.py."""

import pytest
from unittest.mock import MagicMock, patch, call, AsyncMock
import argparse # For creating Namespace objects if needed for command functions

from rich.console import Console as RichConsole
from rich.table import Table
from rich.panel import Panel

# Function to be tested
from app.cli import print_summary_report

# Async command functions (for basic call verification if we add tests for them)
# from app.cli import discover_command, scrape_command, process_command
# from app.utils.exceptions import ConfigError, FileIOError


@pytest.fixture
def mock_rich_console():
    """Fixture to mock rich.console.Console used by print_summary_report."""
    with patch("app.cli.rich_console", spec=RichConsole) as mock_console:
        yield mock_console

# Tests for print_summary_report
def test_print_summary_report_all_successful(mock_rich_console):
    """Test print_summary_report with all successful URLs."""
    summary = {
        "successful_urls": ["http://example.com/1", "http://example.com/2"],
        "failed_urls": []
    }
    print_summary_report(summary)

    # Check Table creation and content
    table_call = None
    for c in mock_rich_console.print.call_args_list:
        if c.args and isinstance(c.args[0], Table):
            table_call = c.args[0]
            break
    assert table_call is not None, "Rich Table was not printed"
    assert table_call.title == "[bold #b8bb26]Scrape Job Summary[/bold #b8bb26]"
    assert len(table_call.rows) == 3
    # Row data check (fragile if column order changes, but good for now)
    # Assuming columns are "Status", "Count"
    assert table_call.rows[0].cells == [":white_check_mark: [green]Successful[/green]", "2"]
    assert table_call.rows[1].cells == [":x: [red]Failed[/red]", "0"]
    assert table_call.rows[2].cells == [":hourglass_done: [cyan]Total Processed[/cyan]", "2"]

    # Ensure Panel for failed URLs is NOT printed
    panel_printed = any(isinstance(c.args[0], Panel) for c in mock_rich_console.print.call_args_list if c.args)
    assert not panel_printed


def test_print_summary_report_some_failed(mock_rich_console):
    """Test print_summary_report with some failed URLs."""
    summary = {
        "successful_urls": ["http://example.com/success"],
        "failed_urls": [
            ("http://example.com/fail1", "Timeout"),
            ("http://example.com/fail2", "404 Not Found")
        ]
    }
    print_summary_report(summary)

    # Check Table
    table_call = None
    for c in mock_rich_console.print.call_args_list:
        if c.args and isinstance(c.args[0], Table):
            table_call = c.args[0]
            break
    assert table_call is not None
    assert table_call.rows[0].cells[1] == "1" # Successful
    assert table_call.rows[1].cells[1] == "2" # Failed
    assert table_call.rows[2].cells[1] == "3" # Total

    # Check Panel creation and content for failed URLs
    panel_call_arg = None
    for c in mock_rich_console.print.call_args_list:
        if c.args and isinstance(c.args[0], Panel):
            panel_call_arg = c.args[0]
            break
    assert panel_call_arg is not None, "Rich Panel for failed URLs was not printed"
    assert panel_call_arg.title == "[bold #fe8019]Failed URLs[/bold #fe8019]"
    
    # Check if the content of the panel contains the failed URLs and reasons
    # The renderable content of a Panel is often a Rich Text object or string.
    # This might need adjustment based on how Panel stores its content.
    panel_content_str = str(panel_call_arg.renderable) # Or panel_call_arg.renderable.plain if it's Text
    assert "http://example.com/fail1" in panel_content_str
    assert "Reason:[/red] Timeout" in panel_content_str
    assert "http://example.com/fail2" in panel_content_str
    assert "Reason:[/red] 404 Not Found" in panel_content_str


def test_print_summary_report_all_failed(mock_rich_console):
    """Test print_summary_report with all URLs failing."""
    summary = {
        "successful_urls": [],
        "failed_urls": [("http://example.com/fail_all", "Server Error")]
    }
    print_summary_report(summary)

    table_call = None
    for c in mock_rich_console.print.call_args_list:
        if c.args and isinstance(c.args[0], Table):
            table_call = c.args[0]
            break
    assert table_call is not None
    assert table_call.rows[0].cells[1] == "0" # Successful
    assert table_call.rows[1].cells[1] == "1" # Failed
    assert table_call.rows[2].cells[1] == "1" # Total

    panel_call_arg = None
    for c in mock_rich_console.print.call_args_list:
        if c.args and isinstance(c.args[0], Panel):
            panel_call_arg = c.args[0]
            break
    assert panel_call_arg is not None
    assert "http://example.com/fail_all" in str(panel_call_arg.renderable)
    assert "Reason:[/red] Server Error" in str(panel_call_arg.renderable)

def test_print_summary_report_empty_summary(mock_rich_console):
    """Test print_summary_report with an empty summary dictionary."""
    summary = {}
    print_summary_report(summary)
    # No table or panel should be printed
    for c_args, _ in mock_rich_console.print.call_args_list:
        if c_args: # If there are positional arguments
            assert not isinstance(c_args[0], (Table, Panel))


def test_print_summary_report_no_processed_urls(mock_rich_console):
    """Test print_summary_report when no URLs were processed (e.g., empty input file)."""
    summary = {"successful_urls": [], "failed_urls": []}
    print_summary_report(summary)
    # No table or panel should be printed because total_processed is 0
    for c_args, _ in mock_rich_console.print.call_args_list:
         if c_args:
            assert not isinstance(c_args[0], (Table, Panel))


# Basic Orchestration Tests for command functions (Optional - could be expanded)
# These are very light checks, true testing of commands would involve CliRunner for Typer.

@patch("app.cli.discover_command", new_callable=AsyncMock) # Mock the async command logic
async def test_cli_discover_entry_point_calls_discover_command(mock_discover_command_logic, mocker):
    """Test that the Typer 'discover' command entry point calls the underlying async logic."""
    # This test is more conceptual for Typer. To test Typer apps, you'd use CliRunner.
    # For now, we assume the cli.py structure where Typer commands call async functions.
    # We are testing the `discover` function in cli.py that Typer would call.
    from app.cli import discover as discover_typer_command

    mock_args = argparse.Namespace(
        start_url="http://example.com", output_file="urls.txt", verbose=False
    )
    
    # To simulate Typer's call, we'd need to mock how Typer invokes it.
    # Instead, let's assume `discover_command` is the core logic.
    # The `discover` Typer command in cli.py does:
    # result = asyncio.run(discover_command(args))
    # raise typer.Exit(result)
    
    # To test this structure, we mock asyncio.run and the inner discover_command
    with patch("asyncio.run", return_value=0) as mock_asyncio_run, \
         patch("app.cli.discover_command", new_callable=AsyncMock, return_value=0) as mock_core_discover:
        
        with pytest.raises(SystemExit) as e: # typer.Exit is a SystemExit
             # Call the Typer command function directly (as if Typer called it)
             discover_typer_command(start_url="http://example.com", output_file="urls.txt", verbose=False)
        
        assert e.value.code == 0
        mock_asyncio_run.assert_called_once()
        # The actual call to discover_command is inside asyncio.run, so check its args
        # This gets a bit complex because of the Namespace bridging.
        # A simpler approach for unit testing the Typer command's *behavior*
        # would be to directly test `discover_command` if it were not for Typer's direct invocation.

        # Given the current cli.py structure, `discover_command` is the actual worker.
        # We can test that Typer's `discover` command correctly calls `asyncio.run(discover_command(correct_args))`.
        
        # The call to asyncio.run will have discover_command(args_namespace) as its argument.
        # Let's check that the args_namespace passed to discover_command was correct.
        
        # mock_asyncio_run.call_args[0][0] should be the coroutine, which is discover_command(args_ns)
        # This is hard to assert directly on the coroutine object itself.
        # It's easier to assert that `mock_core_discover` (the patched version of discover_command)
        # was called with the correct Namespace.
        
        # Since `discover_command` is what `asyncio.run` executes, we check `mock_core_discover`
        assert mock_core_discover.call_args is not None
        called_args_ns = mock_core_discover.call_args[0][0] # First arg to discover_command
        assert isinstance(called_args_ns, argparse.Namespace)
        assert called_args_ns.start_url == "http://example.com"
        assert called_args_ns.output_file == "urls.txt"
        assert called_args_ns.verbose is False

# Similar conceptual tests could be written for `scrape` and `process` Typer commands,
# focusing on ensuring they construct the argparse.Namespace correctly and call `asyncio.run`
# with the respective `scrape_command` or `process_command`.
# However, these become more like testing the CLI argument parsing bridge than the core logic,
# which is already tested in test_processing.py, test_fast_processing.py, etc.
# True CLI testing uses tools like Typer's CliRunner.
