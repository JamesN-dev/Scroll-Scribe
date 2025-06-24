"""Centralized logging system for ScrollScribe.

Provides:
- Clean terminal output with site-by-site status
- LiteLLM/crawl4ai log suppression
- Rich console integration
- Structured error reporting
"""

import logging
from contextlib import contextmanager

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn

from ..constants import URL_DISPLAY_MAX_LENGTH, URL_DISPLAY_MAX_LENGTH_DETAILED
from .url_helpers import clean_url_for_display, clean_url_for_detailed_display


class CleanConsole:
    """Clean console output manager for ScrollScribe."""

    def __init__(self):
        self.console = Console(force_terminal=True, color_system="truecolor")

    def print_url_status(
        self,
        url: str,
        status: str,
        time_taken: float,
        details: str = "",
        progress_console=None,
    ):
        """Print clean status for each URL processed.

        Args:
            url: URL being processed
            status: Status (success, error, warning)
            time_taken: Time taken for processing
            details: Additional details to display
            progress_console: If provided, uses progress.console.log() to avoid breaking progress bars

        Examples:
        ✅ docs.python.org/3/library/asyncio.html (1.2s)
        ✅ docs.python.org/3/tutorial/introduction.html (0.8s)
        ❌ docs.python.org/3/library/broken-module.html (timeout)
        ⚠️  docs.python.org/3/reference/expressions.html (warning: no content)
        """
        # Extract clean domain/path from URL
        try:
            clean_url = clean_url_for_display(url)
        except Exception:
            clean_url = url[:URL_DISPLAY_MAX_LENGTH]

        if status == "success":
            icon = "✅"
            style = "green"
            status_text = f"({time_taken:.1f}s)"
        elif status == "error":
            icon = "❌"
            style = "red"
            status_text = f"({details or 'error'})"
        elif status == "warning":
            icon = "⚠️ "
            style = "yellow"
            status_text = f"({details or 'warning'})"
        else:
            icon = "🔄"
            style = "blue"
            status_text = details or ""

        if details and status == "success":
            status_text += f" - {details}"

        message = f"{icon} {clean_url} {status_text}"

        # Use progress console if in progress context, otherwise use regular console
        if progress_console:
            progress_console.log(f"[{style}]{message}[/]")
        else:
            self.console.print(message, style=style)

    def print_header(self, base_url: str, model: str, total_urls: int):
        """Print clean header for processing session with Rose Pine dark theme."""
        # Extract clean domain from base_url
        clean_domain = (
            base_url.replace("https://", "").replace("http://", "").split("/")[0]
        )

        self.console.print(
            f"[bold #c4a7e7]ScrollScribe[/] | [bold #31748f]Scraping:[/] [bold #e0def4]{clean_domain}[/] | "
            f"🧠 [#9ccfd8]{model}[/] | 📄 [#e0def4]{total_urls}[/] URLs"
        )

    def print_summary(self, success: int, failed: int, total_time: float):
        """Print final summary."""
        total = success + failed
        rate = total / total_time if total_time > 0 else 0

        self.console.print()
        self.console.rule("[bold green]Summary[/]", style="green")
        self.console.print(f"✅ Success: [green]{success}[/]")
        self.console.print(f"❌ Failed: [red]{failed}[/]")
        self.console.print(
            f"⏱️  Rate: [bold #f6c177]{rate:.1f} pages/min[/bold #f6c177]"
        )
        self.console.print(
            f"🕒 Total time: [bold #c4a7e7]{total_time:.1f}s[/bold #c4a7e7]"
        )

    def print_error(self, message: str, details: str = ""):
        """Print error message with Rose Pine love (muted red) theme."""
        if details:
            self.console.print(
                f"[bold #eb6f92]💥 ERROR:[/] [#eb6f92]{message}[/] - [#908caa]{details}[/]"
            )
        else:
            self.console.print(f"[bold #eb6f92]💥 ERROR:[/] [#eb6f92]{message}[/]")

    def print_warning(self, message: str):
        """Print warning message with Rose Pine gold theme."""
        self.console.print(f"[bold #f6c177]⚡ WARNING:[/] [#f6c177]{message}[/]")

    def print_success(self, message: str):
        """Print success message with Rose Pine pine theme."""
        self.console.print(f"✅ [bold #31748f]SUCCESS:[/] [#31748f]{message}[/]")

    def print_processing(self, message: str):
        """Print processing message with Rose Pine foam theme."""
        self.console.print(f"🔄 [bold #9ccfd8]PROCESSING:[/] [#9ccfd8]{message}[/]")

    def print_file_operation(self, operation: str, filename: str, details: str = ""):
        """Print file operation with appropriate icon.

        Examples:
        📁 Created directory: output/
        💾 Saved file: urls.txt (150 URLs)
        📖 Reading file: input.txt
        """
        icons = {
            "created": "📁",
            "saved": "💾",
            "reading": "📖",
            "writing": "✍️",
            "deleted": "🗑️",
            "moved": "📦",
        }
        icon = icons.get(operation.lower(), "📄")
        detail_text = f" ({details})" if details else ""
        self.console.print(
            f"{icon} [bold #f6c177]{operation.title()}:[/] [#e0def4]{filename}[/]{detail_text}"
        )

    def print_step(self, step_num: int, total_steps: int, description: str):
        """Print step in a process.

        Example:
        🔹 Step 1/3: Discovering URLs...
        """
        self.console.print(
            f"🔹 [bold #c4a7e7]Step {step_num}/{total_steps}:[/] [#e0def4]{description}[/]"
        )

    def print_banner(self, title: str, subtitle: str = ""):
        """Print a banner for major operations."""
        self.console.print()
        self.console.rule(f"[bold #c4a7e7]{title}[/]", style="#6e6a86")
        if subtitle:
            self.console.print(f"[#908caa]{subtitle}[/]", justify="center")
        self.console.print()

    def print_info(self, message: str):
        """Print info message with colorful highlighting for important elements."""
        # Color-code different types of content in the message
        import re

        # Highlight URLs (Rose Pine foam - muted teal)
        message = re.sub(
            r"(https?://[^\s]+)", r"[bold #9ccfd8]\1[/bold #9ccfd8]", message
        )

        # Highlight numbers (Rose Pine gold - muted yellow)
        message = re.sub(r"\b(\d+)\b", r"[bold #f6c177]\1[/bold #f6c177]", message)

        # Highlight file paths and extensions (Rose Pine text - soft white)
        message = re.sub(
            r"(/[^\s]+\.(txt|json|md|html))",
            r"[bold #e0def4]\1[/bold #e0def4]",
            message,
        )

        # Highlight environment variable names (Rose Pine pine - muted green)
        message = re.sub(
            r"\b([A-Z_]{3,})\b", r"[bold #31748f]\1[/bold #31748f]", message
        )

        # Highlight quoted strings (Rose Pine text - soft white)
        message = re.sub(r'"([^"]+)"', r'"[bold #e0def4]\1[/bold #e0def4]"', message)

        # Highlight key action words (Rose Pine rose - muted pink)
        action_words = [
            "Starting",
            "Found",
            "Discovery",
            "Reading",
            "Processing",
            "Finished",
            "Saved",
        ]
        for word in action_words:
            message = re.sub(
                f"\\b({word})\\b",
                f"[bold #ebbcba]{word}[/bold #ebbcba]",
                message,
            )

        self.console.print(f"[bold #c4a7e7]ℹ️  INFO:[/] {message}")

    @contextmanager
    def progress_bar(self, total: int, description: str = "Processing"):
        """Context manager for clean progress bar with current URL display."""
        with Progress(
            TextColumn(f"[#9ccfd8]{description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("{task.completed}/{task.total}"),
            TextColumn("•"),
            TimeRemainingColumn(),
            TextColumn("•"),
            TextColumn("[#e0def4]{task.fields[current_url]}[/]", table_column=None),
            console=self.console,
            transient=False,
        ) as progress:
            task = progress.add_task(
                description, total=total, current_url="Starting..."
            )
            yield progress, task

    def print_phase(self, phase: str, description: str = ""):
        """Print phase indicator without separator lines."""
        phase_text = f"[bold #c4a7e7]{phase}[/]"
        if description:
            phase_text += f" [#908caa]• {description}[/]"
        self.console.print(phase_text)

    def print_fetch_status(
        self, url: str, status: str, time_taken: float = 0, progress_console=None
    ):
        """Print simplified fetch status for verbose mode.

        Args:
            url: URL being processed
            status: Status of the operation
            time_taken: Time taken for the operation
            progress_console: If provided, uses progress.console.log() to avoid breaking progress bars
        """
        clean_url = clean_url_for_detailed_display(url)

        if status == "fetched":
            icon = "📥"
            style = "#9ccfd8"
        elif status == "processed":
            icon = "✅"
            style = "#31748f"
        elif status == "error":
            icon = "❌"
            style = "#eb6f92"
        else:
            icon = "🔄"
            style = "#908caa"

        time_str = f"({time_taken:.1f}s)" if time_taken > 0 else ""
        message = f"{icon} [bold {style}]{status.upper()}[/] {clean_url} {time_str}"

        # Use progress console if in progress context, otherwise use regular console
        if progress_console:
            progress_console.log(message)
        else:
            self.console.print(message)


class ScrollScribeLogger:
    """Enhanced logger for ScrollScribe with clean console integration."""

    def __init__(self, name: str = "scrollscribe", console: CleanConsole | None = None):
        self.logger = logging.getLogger(name)
        self.console = console or CleanConsole()
        self._setup_logger()

    def _setup_logger(self):
        """Setup logger with Rich handler."""
        if not self.logger.handlers:
            # Rich handler for structured logs (only for our logger)
            rich_handler = RichHandler(
                console=self.console.console,
                show_time=False,
                show_path=False,
                markup=True,
            )
            rich_handler.setLevel(logging.INFO)

            formatter = logging.Formatter("%(message)s")
            rich_handler.setFormatter(formatter)

            self.logger.addHandler(rich_handler)
            self.logger.setLevel(logging.INFO)

    def url_processing_start(self, url: str, index: int, total: int):
        """Log start of URL processing."""
        clean_url = clean_url_for_display(url)
        self.logger.info(f"[blue]Processing[/] {index}/{total}: [link]{clean_url}[/]")

    def url_success(
        self, url: str, time_taken: float, filename: str = "", chars: int = 0
    ):
        """Log successful URL processing."""
        details = ""
        if chars:
            details = f"{chars:,} chars"
        if filename:
            details += f" → {filename}" if details else f"→ {filename}"

        self.console.print_url_status(url, "success", time_taken, details)

    def url_error(self, url: str, error: str):
        """Log URL processing error."""
        self.console.print_url_status(url, "error", 0, error)

    def url_warning(self, url: str, warning: str):
        """Log URL processing warning."""
        self.console.print_url_status(url, "warning", 0, warning)

    def info(self, message: str):
        """Log info message."""
        self.console.print_info(message)

    def warning(self, message: str):
        """Log warning message."""
        self.console.print_warning(message)

    def error(self, message: str, details: str = ""):
        """Log error message."""
        self.console.print_error(message, details)

    def debug(self, message: str):
        """Log debug message (only if verbose)."""
        self.logger.debug(message)


def set_logging_verbosity(debug: bool = False, verbose: bool = False):
    """Set logging verbosity for all noisy libraries and LiteLLM."""
    import os
    import warnings

    os.environ["LITELLM_LOG"] = "DEBUG" if debug else "ERROR"

    # Set different levels based on mode
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.WARNING  # Show warnings but not info/debug
    else:
        level = logging.ERROR

    noisy_loggers = [
        "litellm",
        "litellm.cost_calculator",
        "litellm.utils",
        "crawl4ai",
        "crawl4ai.async_webcrawler",
        "crawl4ai.utils",
        "playwright",
        "playwright._impl",
        "httpx",
        "urllib3",
        "asyncio",
        "aiohttp",
    ]
    for logger_name in noisy_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        # Completely disable in non-debug mode for these
        if not debug and logger_name in ["litellm", "crawl4ai", "playwright"]:
            logger.disabled = True

    # Suppress crawl4ai's progress output specifically
    if not debug:
        crawl4ai_logger = logging.getLogger("crawl4ai.async_webcrawler")
        crawl4ai_logger.disabled = True

    # Optionally suppress Python warnings in non-debug mode
    if not debug:
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning)


def get_logger(name: str = "scrollscribe", debug: bool = False) -> ScrollScribeLogger:
    """Get a clean ScrollScribe logger instance."""
    set_logging_verbosity(debug)
    return ScrollScribeLogger(name)


# Global logger instance for convenience
logger = get_logger()
