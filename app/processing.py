"""Core processing functions for ScrollScribe.

FIXED VERSION: Proper integration with CleanConsole + persistent Live display.
Uses exceptions.py, retry.py, and logging.py properly.
Combines the best of original scrollscribe.py with new CleanConsole system.
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
from rich.console import Group
from rich.live import Live
from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    Task,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.rule import Rule
from rich.text import Text

from .utils.exceptions import FileIOError, LLMError, ProcessingError
from .utils.logging import CleanConsole, get_logger
from .utils.retry import retry_llm

# Initialize the clean logging system
logger = get_logger("processing")
clean_console = CleanConsole()  # This handles noisy library silencing


class RateColumn(ProgressColumn):
    """Renders the processing rate (seconds per item) - from original scrollscribe.py."""

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
    """Reads URLs from a text file, using proper exception handling."""
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
    url: str, index: int, extension: str = ".md", max_len: int = 100
) -> str:
    """Creates a relatively safe filename from a URL and index."""
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
    """
    Runs the LLM filter with proper retry logic and exception handling.
    Uses @retry_llm decorator from utils/retry.py
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
    """
    Converts relative links in Markdown text to absolute URLs.
    Handles both Markdown [text](url) and inline HTML <a href="url"> links.
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
) -> tuple[int, int]:
    """
    PROPERLY INTEGRATED VERSION: Process URLs with CleanConsole + persistent Live display.

    Combines:
    - Your CleanConsole system for clean URL-by-URL status
    - Original scrollscribe.py persistent Live display with model info
    - Proper exception handling with utils/exceptions.py
    - Retry logic with utils/retry.py

    Returns:
        tuple[int, int]: (success_count, failed_count)
    """
    start_time = time.time()

    # Session logic: only set session_id if --session or --session-id is provided
    session_id: str = ""
    if getattr(args, "session_id", None):
        session_id = args.session_id
    elif getattr(args, "session", False):
        session_id = "scrollscribe_session"

    # Use exact config from original - preserves all functionality
    html_fetch_config = CrawlerRunConfig(
        session_id=session_id if session_id else "",  # Always pass a string
        cache_mode=CacheMode.DISABLED,
        wait_until=args.wait,
        page_timeout=args.timeout,
        markdown_generator=None,  # type: ignore[arg-type]
        extraction_strategy=None,  # type: ignore[arg-type]
        verbose=args.verbose,  # Respect user's verbose choice
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

    # Extract base URL from first URL for header
    base_url = urls_to_scrape[0] if urls_to_scrape else "unknown"
    clean_domain = base_url.replace("https://", "").replace("http://", "").split("/")[0]

    # Use Rose Pine dark theme header format
    header_rule = Rule(
        f"[bold #c4a7e7]ScrollScribe[/] | [bold #31748f]Scraping:[/] [bold #e0def4]{clean_domain}[/]",
        style="#6e6a86",
    )
    header_text = Text(f"🧠 Model: {args.model}", justify="center", style="#9ccfd8")
    live_group = Group(header_rule, header_text, progress)

    logger.info(f"Starting crawl for {len(urls_to_scrape)} URLs...")
    success_count: int = 0
    failed_count: int = 0
    shutdown_requested: bool = False

    try:
        with Live(
            live_group,
            refresh_per_second=4,
            console=clean_console.console,
            transient=False,
        ) as live:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                crawl_task: TaskID = progress.add_task(
                    description="", total=len(urls_to_scrape)
                )

                # Batch fetch with session reuse (performance fix)
                logger.info(
                    f"Batch fetching {len(urls_to_scrape)} URLs with session reuse..."
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
                    total_to_process: int = len(urls_to_scrape)
                    url_start_time = time.time()

                    logger.info(
                        f"Processing URL {loop_index + 1}/{total_to_process} (Overall: {original_index}): {url}"
                    )

                    try:
                        if result.success:
                            html_to_filter = result.cleaned_html or result.html

                            if not html_to_filter:
                                failed_count += 1
                                # Use CleanConsole for clean URL status
                                clean_console.print_url_status(
                                    url, "warning", 0, "empty content"
                                )
                                progress.update(crawl_task, advance=1)
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

                                    # Use CleanConsole for clean status display
                                    clean_console.print_url_status(
                                        url,
                                        "success",
                                        url_time,
                                        f"{chars:,} chars → {filename}",
                                    )
                                    success_count += 1

                                except OSError:
                                    failed_count += 1
                                    logger.error(
                                        f"Failed to save markdown for {url} to {filepath}"
                                    )
                                    clean_console.print_url_status(
                                        url, "error", 0, "save failed"
                                    )
                            else:
                                failed_count += 1
                                clean_console.print_url_status(
                                    url, "warning", 0, "no LLM content"
                                )
                        else:
                            failed_count += 1
                            error_msg = result.error_message or "Unknown error"
                            logger.error(f"HTML fetch failed: {error_msg}")
                            clean_console.print_url_status(url, "error", 0, error_msg)

                        # Delay between requests
                        delay_seconds: float = 1.0
                        await asyncio.sleep(delay_seconds)

                    except KeyboardInterrupt:
                        live.stop()
                        clean_console.print_warning(
                            "KeyboardInterrupt caught during URL processing. Signaling shutdown..."
                        )
                        shutdown_requested = True

                    except Exception as exc:
                        failed_count += 1
                        logger.error(f"Unexpected error processing {url}: {exc}")

                        # Use proper exception handling
                        if isinstance(exc, LLMError | ProcessingError):
                            clean_console.print_url_status(url, "error", 0, str(exc))
                        else:
                            clean_console.print_url_status(
                                url, "error", 0, "unexpected error"
                            )

                        await asyncio.sleep(1.0)

                    if not shutdown_requested:
                        progress.update(crawl_task, advance=1)

    except KeyboardInterrupt:
        clean_console.print_warning(
            "KeyboardInterrupt caught outside main loop. Shutting down..."
        )

    finally:
        total_time = time.time() - start_time

        # Use CleanConsole for final summary
        clean_console.print_summary(success_count, failed_count, total_time)

        # Also log for structured logging
        logger.info(
            f"ScrollScribe finished processing. Saved: {success_count}. Failed/Skipped: {failed_count}."
        )

    return success_count, failed_count
