"""Tests for ScrollScribe logging utilities in app/utils/logging.py."""

import pytest
import logging
from unittest.mock import MagicMock, patch, call

from rich.console import Console as RichConsole
from rich.progress import Progress

from app.utils.logging import (
    CleanConsole,
    ScrollScribeLogger,
    set_logging_verbosity,
    get_logger as get_scrollscribe_logger_instance, # Alias to avoid conflict
)

# Fixture for CleanConsole instance with a mocked RichConsole
@pytest.fixture
def clean_console_mocker():
    """Provides a CleanConsole instance with a mocked internal RichConsole."""
    with patch("app.utils.logging.RichConsole", spec=RichConsole) as mock_rich_console_class:
        mock_rich_console_instance = mock_rich_console_class.return_value
        console = CleanConsole()
        # Replace the real console instance with the mock for assertions
        console.console = mock_rich_console_instance
        return console, mock_rich_console_instance

# CleanConsole Tests
def test_clean_console_print_url_status_success(clean_console_mocker):
    """Test CleanConsole.print_url_status for success status."""
    console, mock_rich_console = clean_console_mocker
    console.print_url_status("http://example.com/page1", "success", 1.23, "Details here")
    mock_rich_console.print.assert_called_once_with(
        "✅ example.com/page1 (1.2s) - Details here", style="green"
    )

def test_clean_console_print_url_status_error(clean_console_mocker):
    """Test CleanConsole.print_url_status for error status."""
    console, mock_rich_console = clean_console_mocker
    console.print_url_status("http://example.com/page2", "error", 0, "Timeout")
    mock_rich_console.print.assert_called_once_with(
        "❌ example.com/page2 (Timeout)", style="red"
    )

def test_clean_console_print_url_status_warning(clean_console_mocker):
    """Test CleanConsole.print_url_status for warning status."""
    console, mock_rich_console = clean_console_mocker
    console.print_url_status("http://example.com/page3", "warning", 0, "Empty content")
    mock_rich_console.print.assert_called_once_with(
        "⚠️  example.com/page3 (Empty content)", style="yellow"
    )

def test_clean_console_print_url_status_long_url(clean_console_mocker):
    """Test CleanConsole.print_url_status with a long URL that should be truncated."""
    console, mock_rich_console = clean_console_mocker
    long_url = "http://this.is.a.very.long.domain.name.that.should.exceed.the.limit/and/some/path"
    console.print_url_status(long_url, "success", 0.5)
    # Expected truncated URL: "this.is.a.very.long.domain.name.that.should.ex..."
    mock_rich_console.print.assert_called_once_with(
        "✅ this.is.a.very.long.domain.name.that.should.ex... (0.5s)", style="green"
    )

def test_clean_console_print_url_status_with_progress_console(clean_console_mocker):
    """Test CleanConsole.print_url_status when a progress_console is provided."""
    console, _ = clean_console_mocker # We don't need the main mock_rich_console here
    mock_progress_console = MagicMock(spec=RichConsole)
    console.print_url_status(
        "http://example.com/progress", "success", 0.8, progress_console=mock_progress_console
    )
    mock_progress_console.log.assert_called_once_with(
        "[green]✅ example.com/progress (0.8s)[/]"
    )

def test_clean_console_print_header(clean_console_mocker):
    """Test CleanConsole.print_header."""
    console, mock_rich_console = clean_console_mocker
    console.print_header("http://docs.example.com/api", "gpt-model-x", 150)
    expected_call = (
        "[bold #c4a7e7]ScrollScribe[/] | [bold #31748f]Scraping:[/] [bold #e0def4]docs.example.com[/] | "
        "🧠 [#9ccfd8]gpt-model-x[/] | 📄 [#e0def4]150[/] URLs"
    )
    mock_rich_console.print.assert_called_once_with(expected_call)

def test_clean_console_print_summary(clean_console_mocker):
    """Test CleanConsole.print_summary."""
    console, mock_rich_console = clean_console_mocker
    console.print_summary(success=90, failed=10, total_time=120.5)
    assert mock_rich_console.print.call_count == 5 # Empty line, rule, success, failed, rate, time
    mock_rich_console.rule.assert_called_once_with("[bold green]Summary[/]", style="green")
    # Check a few specific print calls
    calls = mock_rich_console.print.call_args_list
    assert calls[1] == call("✅ Success: [green]90[/]") # After empty print()
    assert calls[2] == call("❌ Failed: [red]10[/]")
    # Rate calculation: (90+10) / 120.5 = 100 / 120.5 = ~0.83 pages/sec. Rate is pages/min.
    # So, 0.83 * 60 = ~49.8 pages/min
    assert "⏱️  Rate: [bold #f6c177]49.8 pages/min[/bold #f6c177]" in str(calls[3])
    assert "🕒 Total time: [bold #c4a7e7]120.5s[/bold #c4a7e7]" in str(calls[4])


@pytest.mark.parametrize(
    "method_name, message, details, expected_style, expected_prefix",
    [
        ("print_error", "Big Problem", "Details here", "#eb6f92", "💥 ERROR:"),
        ("print_error", "Simple Problem", "", "#eb6f92", "💥 ERROR:"),
        ("print_warning", "Possible Issue", None, "#f6c177", "⚡ WARNING:"),
        ("print_success", "Great Success!", None, "#31748f", "✅ SUCCESS:"),
        ("print_processing", "Working on it", None, "#9ccfd8", "🔄 PROCESSING:"),
    ],
)
def test_clean_console_status_methods(clean_console_mocker, method_name, message, details, expected_style, expected_prefix):
    """Test various status printing methods of CleanConsole."""
    console, mock_rich_console = clean_console_mocker
    method_to_call = getattr(console, method_name)
    if details is not None: # Methods like print_warning don't take details
        method_to_call(message, details) if details else method_to_call(message)
    else:
        method_to_call(message)

    # Construct expected output based on whether details are present
    if details:
        expected_output = f"[bold {expected_style}]{expected_prefix}[/] [{expected_style}]{message}[/] - [#908caa]{details}[/]"
    elif method_name == "print_error" and not details: # Special case for print_error without details
         expected_output = f"[bold {expected_style}]{expected_prefix}[/] [{expected_style}]{message}[/]"
    else:
        expected_output = f"[bold {expected_style}]{expected_prefix}[/] [{expected_style}]{message}[/]"

    mock_rich_console.print.assert_called_once_with(expected_output)


def test_clean_console_print_info_highlighting(clean_console_mocker):
    """Test CleanConsole.print_info with its regex-based highlighting."""
    console, mock_rich_console = clean_console_mocker
    message = 'Starting process for http://example.com on 123 items. API_KEY found. Output to "/path/to/file.txt". "Quoted part".'
    console.print_info(message)

    expected_highlighted_message = (
        "[bold #ebbcba]Starting[/bold #ebbcba] process for [bold #9ccfd8]http://example.com[/bold #9ccfd8] on "
        "[bold #f6c177]123[/bold #f6c177] items. [bold #31748f]API_KEY[/bold #31748f] [bold #ebbcba]Found[/bold #ebbcba]. "
        "Output to \"[bold #e0def4]/path/to/file.txt[/bold #e0def4]\". "
        "\"[bold #e0def4]Quoted part[/bold #e0def4]\"."
    )
    mock_rich_console.print.assert_called_once_with(
        f"[bold #c4a7e7]ℹ️  INFO:[/] {expected_highlighted_message}"
    )

@patch("app.utils.logging.Progress", spec=Progress)
def test_clean_console_progress_bar(mock_progress_class, clean_console_mocker):
    """Test CleanConsole.progress_bar context manager."""
    console, mock_rich_console = clean_console_mocker
    mock_progress_instance = mock_progress_class.return_value
    mock_task_id = mock_progress_instance.add_task.return_value

    with console.progress_bar(total=100, description="Testing Progress") as (progress, task_id):
        assert progress == mock_progress_instance
        assert task_id == mock_task_id
        progress.update(task_id, advance=10, current_url="http://test.url")

    mock_progress_class.assert_called_once() # Check Progress was instantiated
    # Check that add_task was called on the instance
    mock_progress_instance.add_task.assert_called_once_with(
        "Testing Progress", total=100, current_url="Starting..."
    )
    # Check that update was called
    mock_progress_instance.update.assert_called_once_with(mock_task_id, advance=10, current_url="http://test.url")


def test_clean_console_print_phase(clean_console_mocker):
    """Test CleanConsole.print_phase."""
    console, mock_rich_console = clean_console_mocker
    console.print_phase("DISCOVERY", "Finding links")
    expected_output = "[bold #c4a7e7]DISCOVERY[/] [#908caa]• Finding links[/]"
    mock_rich_console.print.assert_called_once_with(expected_output)

def test_clean_console_print_fetch_status(clean_console_mocker):
    """Test CleanConsole.print_fetch_status."""
    console, mock_rich_console = clean_console_mocker
    console.print_fetch_status("http://example.com/fetched_item", "fetched", 0.75)
    expected_output = "📥 [bold #9ccfd8]FETCHED[/] example.com/fetched_item (0.8s)" # Time is rounded
    mock_rich_console.print.assert_called_once_with(expected_output)


# ScrollScribeLogger Tests
@pytest.fixture
def scribe_logger_mocker():
    """Provides a ScrollScribeLogger instance with a mocked CleanConsole and Python logger."""
    with patch("app.utils.logging.CleanConsole") as MockCleanConsole, \
         patch("logging.getLogger") as mock_get_python_logger:

        mock_clean_console_instance = MockCleanConsole.return_value
        mock_python_logger_instance = mock_get_python_logger.return_value

        # Prevent actual handler setup for Python logger during tests
        mock_python_logger_instance.handlers = [MagicMock()]

        logger = ScrollScribeLogger(name="test_scribe_logger", console=mock_clean_console_instance)
        logger.logger = mock_python_logger_instance # Ensure it uses the mocked Python logger

        return logger, mock_clean_console_instance, mock_python_logger_instance

def test_scroll_scribe_logger_setup(scribe_logger_mocker):
    """Test ScrollScribeLogger initialization and setup."""
    logger, mock_clean_console, mock_python_logger = scribe_logger_mocker
    assert logger.console == mock_clean_console
    assert logger.logger == mock_python_logger
    # _setup_logger is called during init. If handlers weren't empty, it would add one.
    # Since we mock handlers to be non-empty, addHandler shouldn't be called again.
    # If we wanted to test _setup_logger directly, we'd need more intricate mocking.
    # For now, this confirms the logger uses the mocked instances.

def test_scroll_scribe_logger_url_success(scribe_logger_mocker):
    """Test ScrollScribeLogger.url_success method."""
    logger, mock_clean_console, _ = scribe_logger_mocker
    logger.url_success("http://example.com", 2.1, "file.md", 1024)
    mock_clean_console.print_url_status.assert_called_once_with(
        "http://example.com", "success", 2.1, "1,024 chars → file.md"
    )

def test_scroll_scribe_logger_info(scribe_logger_mocker):
    """Test ScrollScribeLogger.info method."""
    logger, mock_clean_console, _ = scribe_logger_mocker
    logger.info("This is an info message.")
    mock_clean_console.print_info.assert_called_once_with("This is an info message.")

def test_scroll_scribe_logger_debug(scribe_logger_mocker):
    """Test ScrollScribeLogger.debug method forwards to Python logger."""
    logger, _, mock_python_logger = scribe_logger_mocker
    logger.debug("This is a debug message.")
    mock_python_logger.debug.assert_called_once_with("This is a debug message.")


# set_logging_verbosity and get_logger tests
@patch("logging.getLogger")
@patch("os.environ", {}) # Ensure clean env for this test
def test_set_logging_verbosity_debug(mock_get_logger, caplog):
    """Test set_logging_verbosity with debug=True."""
    mock_logger_instance = MagicMock()
    mock_get_logger.return_value = mock_logger_instance

    set_logging_verbosity(debug=True, verbose=False)

    assert logging.getLogger("litellm").level == logging.DEBUG
    assert logging.getLogger("crawl4ai").level == logging.DEBUG
    assert logging.getLogger("playwright").level == logging.DEBUG
    assert logging.getLogger("httpx").level == logging.DEBUG
    assert "LITELLM_LOG" in logging.os.environ
    assert logging.os.environ["LITELLM_LOG"] == "DEBUG"

    # Check that specific loggers are NOT disabled
    assert logging.getLogger("litellm").disabled is False
    assert logging.getLogger("crawl4ai.async_webcrawler").disabled is False


@patch("logging.getLogger")
@patch("os.environ", {})
def test_set_logging_verbosity_verbose(mock_get_logger, caplog):
    """Test set_logging_verbosity with verbose=True and debug=False."""
    mock_logger_instance = MagicMock()
    mock_get_logger.return_value = mock_logger_instance

    set_logging_verbosity(debug=False, verbose=True)

    assert logging.getLogger("litellm").level == logging.WARNING
    assert logging.getLogger("crawl4ai").level == logging.WARNING # crawl4ai gets WARNING in verbose
    assert logging.getLogger("playwright").disabled is True # playwright gets disabled
    assert logging.getLogger("httpx").level == logging.WARNING
    assert logging.os.environ["LITELLM_LOG"] == "ERROR" # verbose still sets LITELLM_LOG to ERROR

    # Check that specific loggers ARE disabled or set to higher level
    assert logging.getLogger("litellm").disabled is True
    assert logging.getLogger("crawl4ai.async_webcrawler").disabled is True


@patch("logging.getLogger")
@patch("os.environ", {})
def test_set_logging_verbosity_quiet(mock_get_logger, caplog):
    """Test set_logging_verbosity with debug=False and verbose=False (quiet)."""
    mock_logger_instance = MagicMock()
    mock_get_logger.return_value = mock_logger_instance

    set_logging_verbosity(debug=False, verbose=False)

    assert logging.getLogger("litellm").level == logging.ERROR
    assert logging.getLogger("crawl4ai").level == logging.ERROR
    assert logging.getLogger("playwright").disabled is True
    assert logging.getLogger("httpx").level == logging.ERROR
    assert logging.os.environ["LITELLM_LOG"] == "ERROR"

    assert logging.getLogger("litellm").disabled is True
    assert logging.getLogger("crawl4ai.async_webcrawler").disabled is True

@patch("app.utils.logging.ScrollScribeLogger")
@patch("app.utils.logging.set_logging_verbosity")
def test_get_scrollscribe_logger_instance(mock_set_verbosity, mock_scribe_logger_class):
    """Test the get_logger utility function."""
    mock_logger_instance = mock_scribe_logger_class.return_value
    
    logger = get_scrollscribe_logger_instance(name="custom_logger", debug=True)

    mock_set_verbosity.assert_called_once_with(True)
    mock_scribe_logger_class.assert_called_once_with("custom_logger")
    assert logger == mock_logger_instance

# Global logger test (very basic, just checks it's an instance of ScrollScribeLogger)
def test_global_logger_instance():
    """Test that the global `logger` is an instance of ScrollScribeLogger."""
    from app.utils.logging import logger as global_logger # Import the global instance
    assert isinstance(global_logger, ScrollScribeLogger)
