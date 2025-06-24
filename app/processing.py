"""LLM-powered HTML-to-Markdown processing for ScrollScribe.

Implements the backend for the default (LLM-based) processing pipeline, used when the --fast flag is not specified in the CLI.
Provides high-quality Markdown conversion using advanced LLM filtering, robust retry logic, and persistent progress reporting.

Key features:
- Batch processing of documentation URLs with LLM-based content filtering
- Compatible with existing CleanConsole logging system
- Integrates standardized exception and retry handling
- Converts relative links to absolute URLs and generates safe filenames
- Designed for high-quality, well-structured Markdown output

Note:
    This module shares core processing logic and utility functions (such as link absolutification and filename sanitization)
    with both the default (LLM-based) and fast (non-LLM) processing pipelines.
    The fast processing mode (`process_urls_fast` in `fast_processing.py`) imports and reuses these helpers to avoid duplication.
"""

import asyncio
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import cast
from urllib.parse import urljoin, urlparse

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    CrawlResult,
)
from crawl4ai.content_filter_strategy import LLMContentFilter
from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    Task,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.text import Text

from .constants import DEFAULT_EXTENSION, MAX_FILENAME_LENGTH
from .utils.exceptions import FileIOError, LLMError, ProcessingError
from .utils.logging import CleanConsole, get_logger
from .utils.retry import retry_llm
from .utils.url_helpers import clean_url_for_display

# Initialize the clean logging system
logger = get_logger("processing")
clean_console = CleanConsole()  # This handles noisy library silencing


class RateColumn(ProgressColumn):
    """Progress column for displaying the processing rate (seconds per item).

    This column calculates and renders the average time taken to process each item
    in a Rich progress bar.

    Attributes:
        None

    Methods:
        render(task: Task) -> Text: Calculate and render the rate for the given task.

    Example:
        progress = Progress(RateColumn(), ...)
    """

    def render(self, task: Task) -> Text:
        """Calculate and render the rate."""
        if not task.completed or task.start_time is None:
            return Text("-.-- s/item", style="#6e6a86")
        elapsed = task.finished_time if task.finished else time.monotonic()
        if elapsed is None:
            return Text("-.-- s/item", style="#6e6a86")
        assert isinstance(elapsed, float), (
            f"Expected float for elapsed, got {type(elapsed)}"
        )
        assert isinstance(task.start_time, float), (
            f"Expected float for start_time, got {type(task.start_time)}"
        )
        run_time = elapsed - task.start_time
        if run_time <= 0:
            return Text("-.-- s/item", style="#6e6a86")
        items_per_second = task.completed / run_time
        if items_per_second <= 0:
            return Text("-.-- s/item", style="#6e6a86")
        seconds_per_item = 1.0 / items_per_second
        return Text(f"{seconds_per_item:.2f} s/item", style="#6e6a86")


def read_urls_from_file(filepath: str) -> list[str]:
    """Read a list of URLs from a text file.

    Args:
        filepath (str): Path to the text file containing URLs, one per line.

    Returns:
        list[str]: A list of valid URLs extracted from the file.

    Raises:
        FileIOError: If the file cannot be read.

    Notes:
        - Lines that do not contain a valid URL are skipped with a warning.
        - Only URLs starting with http:// or https:// are considered valid.
    """
    urls: list[str] = []
    logger.info(f"Reading URLs from: {filepath}")

    try:
        with open(filepath, encoding="utf-8") as file_object:
            for line in file_object:
                cleaned_line: str = line.strip()
                if not cleaned_line:
                    continue
                match = re.search(r"https?://\S+", cleaned_line)
                if match:
                    url: str = match.group(0).rstrip(".,;:!?")
                    urls.append(url)
                else:
                    logger.warning(f"Skipping invalid line: '{cleaned_line}'")

    except FileNotFoundError as err:
        logger.error(f"Input file not found: {filepath}")
        raise FileIOError(
            f"Input file not found: {filepath}", filepath=filepath, operation="read"
        ) from err
    except Exception as err:
        logger.error(f"Failed to read file: {filepath}")
        raise FileIOError(
            f"Failed to read file: {filepath}", filepath=filepath, operation="read"
        ) from err

    logger.info(f"Found {len(urls)} valid URLs in file")
    return urls


def url_to_filename(
    url: str,
    index: int,
    extension: str = DEFAULT_EXTENSION,
    max_len: int = MAX_FILENAME_LENGTH,
) -> str:
    """Generate a safe, filesystem-friendly filename from a URL and index.

    This function parses the given URL and constructs a filename that is safe for most filesystems,
    using the URL path or netloc, sanitized and truncated as needed. The filename includes a
    zero-padded index for ordering and the specified file extension.

    Args:
        url (str): The source URL to convert into a filename.
        index (int): The index of the URL in the processing batch (used for ordering).
        extension (str, optional): The file extension to use (default: ".md").
        max_len (int, optional): Maximum length for the filename base (default: 100).

    Returns:
        str: A safe filename string suitable for saving the processed content.

    Notes:
        - If the URL cannot be parsed, a fallback filename using only the index is returned.
        - All unsafe filesystem characters are replaced with underscores.
    """
    try:
        parsed = urlparse(url)
        path_part: str = (
            parsed.path.strip("/") if parsed.path.strip("/") else parsed.netloc
        )
        safe_path: str = re.sub(r'[\\/:*?"<>|]+', "_", path_part)
        safe_path = re.sub(r"\s+", "_", safe_path)
        safe_path = safe_path[:max_len].rstrip("._")
        if not safe_path:
            safe_path = f"url_{index}"
        return f"page_{index:03d}_{safe_path}{extension}"
    except Exception:
        logger.error(
            f"Failed to generate safe filename for URL index {index}. Using fallback."
        )
        return f"page_{index:03d}{extension}"


@retry_llm
async def run_llm_filter(
    filter_instance: LLMContentFilter, html_content: str, url: str
) -> str | None:
    """Apply an LLM-based content filter to HTML content, with automatic retry and exception handling.

    This function uses the provided LLMContentFilter instance to process the given HTML content,
    returning filtered Markdown output. Retries are handled automatically via the @retry_llm decorator.

    Args:
        filter_instance (LLMContentFilter): The LLM content filter to use for processing.
        html_content (str): The HTML content to be filtered.
        url (str): The source URL of the content (used for logging and context).

    Returns:
        str | None: The filtered Markdown content, or None if filtering fails after retries.

    Raises:
        LLMError: If the LLM operation fails after all retry attempts.
    """
    if not html_content:
        return None

    loop = asyncio.get_event_loop()

    try:
        with ThreadPoolExecutor() as pool:
            filtered_chunks = await loop.run_in_executor(
                pool, filter_instance.filter_content, html_content
            )

        # Process successful result
        if isinstance(filtered_chunks, list):
            return "\n\n---\n\n".join(filtered_chunks)
        elif isinstance(filtered_chunks, str):
            return filtered_chunks
        else:
            raise LLMError(
                f"LLM Filter returned unexpected type: {type(filtered_chunks)}", url=url
            )

    except Exception as e:
        # Let @retry_llm handle the retries
        raise LLMError(f"LLM filter failed: {str(e)}", url=url) from e


def absolutify_links(markdown_text: str, base_url: str) -> str:
    """Convert all relative links in Markdown and inline HTML to absolute URLs using the provided base URL.

    This function scans the input Markdown text for:
      - Markdown links of the form [text](url)
      - Inline HTML anchor tags of the form <a href="url">

    Any link that is not already absolute (i.e., does not start with http(s)://, mailto:, #, or data:) is converted to an absolute URL using the given base URL.

    Args:
        markdown_text (str): The Markdown content to process.
        base_url (str): The base URL to resolve relative links against.

    Returns:
        str: The Markdown text with all relative links converted to absolute URLs.

    Notes:
        - If base_url is not provided, the function returns the input unchanged.
        - Logs a warning if a link cannot be resolved to an absolute URL.
        - Does not modify links that are already absolute or use unsupported schemes.
    """
    if not base_url:
        logger.warning(
            "Base URL not provided to absolutify_links, skipping post-processing."
        )
        return markdown_text

    processed_text = markdown_text
    changes_made = False
    md_link_pattern = re.compile(
        r"\[([^\]]+)\]\(((?!https?://|mailto:|#|data:)[^)]+)\)"
    )

    def repl_md(m):
        nonlocal changes_made
        text, link = m.group(1), m.group(2)
        safe_link = link.strip()
        try:
            absolute_link = urljoin(base_url, safe_link)
            if link != absolute_link:
                changes_made = True
            return f"[{text}]({absolute_link})"
        except ValueError:
            logger.warning(
                f"Could not absolutify MD link: '{link}' with base '{base_url}'"
            )
            return m.group(0)

    processed_text = md_link_pattern.sub(repl_md, processed_text)
    html_link_pattern = re.compile(
        r'(<a\s+[^>]*href=["\'])(?!https?://|mailto:|#|data:)([^"\']+)(["\'][^>]*>)',
        re.IGNORECASE,
    )

    def repl_html(m):
        nonlocal changes_made
        before, link, after = m.group(1), m.group(2), m.group(3)
        safe_link = link.strip()
        try:
            absolute_link = urljoin(base_url, safe_link)
            if link != absolute_link:
                changes_made = True
            return f"{before}{absolute_link}{after}"
        except ValueError:
            logger.warning(
                f"Could not absolutify HTML href: '{link}' with base '{base_url}'"
            )
            return m.group(0)

    processed_text = html_link_pattern.sub(repl_html, processed_text)
    return processed_text


async def process_urls_batch(
    urls_to_scrape: list[str],
    args,
    output_dir: Path,
    llm_content_filter: LLMContentFilter,
    browser_config: BrowserConfig,
) -> dict:  # <--- CHANGE THIS LINE
    """Processes a batch of documentation URLs, converting each to filtered Markdown using an LLM content filter.

    This function:
    - Logs progress and status for each URL using CleanConsole.
    - Maintains a persistent progress display with model and URL information.
    - Handles exceptions and retries using the project's standardized utilities.

    Args:
        urls_to_scrape (list[str]): List of documentation URLs to process.
        args: Parsed CLI arguments or configuration options.
        output_dir (Path): Directory where Markdown files will be saved.
        llm_content_filter (LLMContentFilter): Content filter for LLM-based processing.
        browser_config (BrowserConfig): Configuration for the web browser/crawler.

    Returns:
        dict: Summary with lists of successful and failed URLs.
    """
    start_time = time.time()
    # [NOT FUNCTIONAL CURRENTLY - CRAWL4AI BUG]
    # Session logic: only set session_id if --session or --session-id is provided
    session_id: str = ""
    if getattr(args, "session_id", None):
        session_id = args.session_id
    elif getattr(args, "session", False):
        session_id = "scrollscribe_session"

    html_fetch_config = CrawlerRunConfig(
        session_id=session_id if session_id else "",
        cache_mode=CacheMode.DISABLED,
        wait_until=args.wait,
        page_timeout=args.timeout,
        verbose=args.verbose,
        stream=False,
    )

    # Create the persistent Live display like original scrollscribe.py
    progress_columns = [
        TextColumn("[#9ccfd8]Processing URLs"),
        BarColumn(),
        TextColumn("[#6e6a86]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TextColumn("[#908caa]{task.completed:>4d}[/]/[#908caa]{task.total:>4d}[/]"),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TextColumn("ETA"),
        TimeRemainingColumn(),
        TextColumn("•"),
        RateColumn(),
        TextColumn("•"),
        SpinnerColumn(),
    ]
    progress = Progress(
        *progress_columns, console=clean_console.console, transient=False
    )

    # Extract base URL for header and print phase indicator
    base_url = urls_to_scrape[0] if urls_to_scrape else "unknown"
    clean_console.print_phase(
        "PROCESSING", f"Converting {len(urls_to_scrape)} URLs to Markdown"
    )
    clean_console.print_header(base_url, args.model, len(urls_to_scrape))

    logger.info(f"Starting crawl for {len(urls_to_scrape)} URLs...")
    success_count: int = 0
    failed_count: int = 0
    successful_urls = []
    failed_urls = []
    shutdown_requested: bool = False

    try:
        with clean_console.progress_bar(len(urls_to_scrape), "Processing URLs") as (
            progress,
            task,
        ):
            async with AsyncWebCrawler(config=browser_config) as crawler:
                # Batch fetch with session reuse (performance fix)
                if args.verbose:
                    progress.console.log(
                        f"📥 [bold #9ccfd8]FETCHING[/] Downloading {len(urls_to_scrape)} pages"
                    )

                all_results: list[CrawlResult] = cast(
                    "list[CrawlResult]",
                    await crawler.arun_many(urls_to_scrape, config=html_fetch_config),
                )

                # Process each result - using CleanConsole for individual URL status
                for loop_index, (url, result) in enumerate(
                    zip(urls_to_scrape, all_results, strict=True)
                ):
                    if shutdown_requested:
                        clean_console.print_warning(
                            "Shutdown requested, stopping processing..."
                        )
                        break

                    original_index: int = args.start_at + loop_index + 1
                    len(urls_to_scrape)
                    url_start_time = time.time()

                    # Update progress bar with current URL
                    clean_url = clean_url_for_display(url)
                    progress.update(task, current_url=clean_url)

                    if args.verbose:
                        clean_console.print_fetch_status(
                            url, "processing", progress_console=progress.console
                        )

                    try:
                        if result.success:
                            html_to_filter = result.cleaned_html or result.html

                            if not html_to_filter:
                                failed_count += 1
                                failed_urls.append((url, "empty content"))
                                clean_console.print_url_status(
                                    url,
                                    "warning",
                                    0,
                                    "empty content",
                                    progress_console=progress.console,
                                )
                                progress.update(task, advance=1)
                                continue

                            logger.info(
                                f"HTML fetched ({len(html_to_filter)} chars). Sending to LLM filter ({args.model})..."
                            )

                            # Use the properly decorated run_llm_filter
                            filtered_md: str | None = await run_llm_filter(
                                filter_instance=llm_content_filter,
                                html_content=html_to_filter,
                                url=url,
                            )

                            if filtered_md:
                                absolute_md = absolutify_links(filtered_md, url)
                                filename: str = url_to_filename(url, original_index)
                                filepath = output_dir / filename

                                try:
                                    with open(filepath, "w", encoding="utf-8") as f:
                                        f.write(absolute_md)

                                    url_time = time.time() - url_start_time
                                    chars = len(absolute_md)

                                    if args.verbose:
                                        clean_console.print_url_status(
                                            url,
                                            "success",
                                            url_time,
                                            f"{chars:,} chars → {filename}",
                                            progress_console=progress.console,
                                        )
                                    successful_urls.append(url)
                                    success_count += 1

                                except OSError as e:
                                    failed_count += 1
                                    failed_urls.append((url, str(e)))
                                    logger.error(
                                        f"Failed to save markdown for {url} to {filepath}"
                                    )
                                    clean_console.print_url_status(
                                        url,
                                        "error",
                                        0,
                                        "save failed",
                                        progress_console=progress.console,
                                    )
                            else:
                                failed_count += 1
                                failed_urls.append((url, "no LLM content"))
                                clean_console.print_url_status(
                                    url,
                                    "warning",
                                    0,
                                    "no LLM content",
                                    progress_console=progress.console,
                                )
                        else:
                            failed_count += 1
                            failed_urls.append((url, "empty content"))
                            error_msg = result.error_message or "Unknown error"
                            logger.error(f"HTML fetch failed: {error_msg}")
                            clean_console.print_url_status(
                                url,
                                "error",
                                0,
                                error_msg,
                                progress_console=progress.console,
                            )

                        # Delay between requests
                        delay_seconds: float = 1.0
                        await asyncio.sleep(delay_seconds)

                    except KeyboardInterrupt:
                        clean_console.print_warning(
                            "KeyboardInterrupt caught during URL processing. Signaling shutdown..."
                        )
                        shutdown_requested = True

                    except Exception as exc:
                        failed_count += 1
                        failed_urls.append((url, str(exc)))
                        logger.error(f"Unexpected error processing {url}: {exc}")

                        # Use proper exception handling
                        if isinstance(exc, LLMError | ProcessingError):
                            clean_console.print_url_status(
                                url,
                                "error",
                                0,
                                str(exc),
                                progress_console=progress.console,
                            )
                        else:
                            clean_console.print_url_status(
                                url,
                                "error",
                                0,
                                "unexpected error",
                                progress_console=progress.console,
                            )

                        await asyncio.sleep(1.0)

                    if not shutdown_requested:
                        progress.update(task, advance=1)

    except KeyboardInterrupt:
        clean_console.print_warning(
            "KeyboardInterrupt caught outside main loop. Shutting down..."
        )

    finally:
        total_time = time.time() - start_time

        # Final summary
        clean_console.print_summary(success_count, failed_count, total_time)

        logger.info(
            f"ScrollScribe finished processing. Saved: {success_count}. Failed/Skipped: {failed_count}."
        )

    summary = {
        "successful_urls": successful_urls,
        "failed_urls": failed_urls,
    }
    return summary
