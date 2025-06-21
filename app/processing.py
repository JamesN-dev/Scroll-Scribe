"""Core processing functions for ScrollScribe.

Extracted from scrollscribe.py with critical performance fixes:
1. Fixed duplicate fetching bug (2x speed improvement)
2. Added session reuse (additional speed boost)
3. Applied @retry_llm decorator to replace manual retry logic
"""

import asyncio
import logging
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
from rich.console import Console, Group
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

from .utils.exceptions import FileIOError
from .utils.retry import retry_llm

# Get the same logger and styles as original
log = logging.getLogger()
console = Console(force_terminal=True, color_system="truecolor")

# Same styles as original scrollscribe.py
INFO_STYLE = "[bright_green]"
WARN_STYLE = "[bright_yellow]"
ERROR_STYLE = "[bright_red]"
CRITICAL_STYLE = "[bold white on red]"
STYLE_END = "[/]"


class RateColumn(ProgressColumn):
    """Renders the processing rate (seconds per item) - copied from scrollscribe.py."""

    def render(self, task: Task) -> Text:
        """Calculate and render the rate."""
        if not task.completed or task.start_time is None:
            return Text("-.-- s/item", style="progress.remaining")
        elapsed = task.finished_time if task.finished else time.monotonic()
        if elapsed is None:
            return Text("-.-- s/item", style="progress.remaining")
        assert isinstance(elapsed, float), (
            f"Expected float for elapsed, got {type(elapsed)}"
        )
        assert isinstance(task.start_time, float), (
            f"Expected float for start_time, got {type(task.start_time)}"
        )
        run_time = elapsed - task.start_time
        if run_time <= 0:
            return Text("-.-- s/item", style="progress.remaining")
        items_per_second = task.completed / run_time
        if items_per_second <= 0:
            return Text("-.-- s/item", style="progress.remaining")
        seconds_per_item = 1.0 / items_per_second
        return Text(f"{seconds_per_item:.2f} s/item", style="progress.remaining")


def read_urls_from_file(filepath: str) -> list[str]:
    """Reads URLs from a text file, one per line, skipping empty/invalid lines."""
    urls: list[str] = []
    log.info(f"{INFO_STYLE}Reading URLs from: [cyan]{filepath}[/]{STYLE_END}")
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
                    log.warning(
                        f"{WARN_STYLE}Skipping invalid line: '{cleaned_line}'{STYLE_END}"
                    )
    except FileNotFoundError:
        log.error(
            f"{ERROR_STYLE}Input file not found: [underline]{filepath}[/underline]{STYLE_END}"
        )
        raise FileIOError(
            f"Input file not found: {filepath}", filepath=filepath, operation="read"
        )
    except Exception:
        log.exception(
            f"{ERROR_STYLE}Failed to read file [underline]{filepath}[/underline]{STYLE_END}"
        )
        raise FileIOError(
            f"Failed to read file: {filepath}", filepath=filepath, operation="read"
        )
    log.info(f"{INFO_STYLE}Found [bold]{len(urls)}[/] valid URLs in file.{STYLE_END}")
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
        log.exception(
            f"{ERROR_STYLE}Failed to generate safe filename for URL index [bold]{index}[/]. Using fallback.{STYLE_END}"
        )
        return f"page_{index:03d}{extension}"


@retry_llm
async def run_llm_filter(
    filter_instance: LLMContentFilter, html_content: str
) -> str | None:
    """
    Runs the filter's potentially synchronous method in a thread pool.
    Fixed version with @retry_llm decorator instead of manual retry logic.
    """
    if not html_content:
        return None

    loop = asyncio.get_event_loop()

    # Removed manual retry loop - @retry_llm decorator handles this now!
    with ThreadPoolExecutor() as pool:
        filtered_chunks = await loop.run_in_executor(
            pool, filter_instance.filter_content, html_content
        )

    # Process successful result (same as original)
    if isinstance(filtered_chunks, list):
        return "\n\n---\n\n".join(filtered_chunks)
    elif isinstance(filtered_chunks, str):
        return filtered_chunks
    else:
        log.warning(
            f"{WARN_STYLE}LLM Filter returned unexpected type: [bold]{type(filtered_chunks)}[/]{STYLE_END}"
        )
        return None


def absolutify_links(markdown_text: str, base_url: str) -> str:
    """
    Converts relative links in Markdown text to absolute URLs.
    Handles both Markdown [text](url) and inline HTML <a href="url"> links.
    """
    if not base_url:
        log.warning(
            f"{WARN_STYLE}Base URL not provided to absolutify_links, skipping post-processing.{STYLE_END}"
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
            log.warning(
                f"{WARN_STYLE}Could not absolutify MD link: '{link}' with base '{base_url}'{STYLE_END}"
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
            log.warning(
                f"{WARN_STYLE}Could not absolutify HTML href: '{link}' with base '{base_url}'{STYLE_END}"
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
    FIXED VERSION: Process URLs with session reuse and no duplicate fetching.

    Returns:
        tuple[int, int]: (success_count, failed_count)
    """

    # 🚀 PERFORMANCE FIX 1: Add session reuse
    session_id = "scrollscribe_session"

    # 🚀 PERFORMANCE FIX 2: Configure with session_id
    html_fetch_config = CrawlerRunConfig(
        session_id=session_id,  # Enable session reuse!
        cache_mode=CacheMode.DISABLED,
        wait_until=args.wait,
        page_timeout=args.timeout,
        markdown_generator=None,  # type: ignore[arg-type]
        extraction_strategy=None,  # type: ignore[arg-type]
        verbose=args.verbose,
        stream=False,
    )

    # Same Rich progress setup as original
    progress_columns = [
        TextColumn("[cyan]Processing URLs"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TextColumn("[cyan]{task.completed:>4d}[/]/[cyan]{task.total:>4d}[/]"),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        TextColumn("•"),
        RateColumn(),
        TextColumn("•"),
        SpinnerColumn(),
    ]
    progress = Progress(*progress_columns, console=console, transient=False)
    header_rule = Rule(
        f"[bold blue]ScrollScribe | Model: {args.model}[/]", style="blue"
    )
    header_text = Text(
        f"🧠 Filtering with: {args.model}", justify="center", style="dim"
    )
    live_group = Group(header_rule, header_text, progress)

    log.info(
        f"{INFO_STYLE}Starting crawl for [bold]{len(urls_to_scrape)}[/] URLs...{STYLE_END}"
    )
    success_count: int = 0
    failed_count: int = 0
    shutdown_requested: bool = False

    try:
        with Live(
            live_group, refresh_per_second=4, console=console, transient=False
        ) as live:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                crawl_task: TaskID = progress.add_task(
                    description="", total=len(urls_to_scrape)
                )

                # 🚀 PERFORMANCE FIX 3: Batch fetch with session
                log.info(
                    f"{INFO_STYLE}Batch fetching [bold]{len(urls_to_scrape)}[/] URLs with session reuse...{STYLE_END}"
                )
                all_results: list[CrawlResult] = cast(
                    "list[CrawlResult]",
                    await crawler.arun_many(urls_to_scrape, config=html_fetch_config),
                )

                # 🚀 PERFORMANCE FIX 4: Use batch results directly - NO duplicate fetching!
                for loop_index, (url, result) in enumerate(
                    zip(urls_to_scrape, all_results, strict=True)
                ):
                    if shutdown_requested:
                        console.print(
                            "[yellow][WARN] Shutdown requested, stopping processing...[/yellow]"
                        )
                        break

                    original_index: int = args.start_at + loop_index + 1
                    total_to_process: int = len(urls_to_scrape)

                    log.info(
                        f"{INFO_STYLE}Processing URL [yellow]{loop_index + 1}/{total_to_process}[/] (Overall: [yellow]{original_index}[/]): [link={url}]{url}[/link]{STYLE_END}"
                    )

                    try:
                        # 🚀 PERFORMANCE FIX: Use result from batch - no duplicate fetching!
                        if result.success:
                            html_to_filter = result.cleaned_html or result.html

                            if not html_to_filter:
                                log.warning(
                                    f"{WARN_STYLE}HTML fetch succeeded but content is empty.{STYLE_END}"
                                )
                                failed_count += 1
                                progress.update(crawl_task, advance=1)
                                continue

                            log.info(
                                f"{INFO_STYLE}HTML fetched ([bold]{len(html_to_filter)}[/] chars). Sending to LLM filter ([blue]{args.model}[/])...{STYLE_END}"
                            )

                            # Use the fixed run_llm_filter with @retry_llm decorator
                            filtered_md: str | None = await run_llm_filter(
                                filter_instance=llm_content_filter,
                                html_content=html_to_filter,
                            )

                            if filtered_md:
                                absolute_md = absolutify_links(filtered_md, url)

                                filename: str = url_to_filename(url, original_index)
                                filepath = output_dir / filename
                                try:
                                    with open(filepath, "w", encoding="utf-8") as f:
                                        f.write(absolute_md)

                                    log.info(
                                        f"{INFO_STYLE}Saved: [cyan]{filepath}[/] ([bold]{len(absolute_md)}[/] chars){STYLE_END}"
                                    )
                                    console.print(
                                        f"[green]✓ Saved:[/green] [cyan]{filepath.name}[/]"
                                    )
                                    success_count += 1
                                except OSError:
                                    log.exception(
                                        f"{ERROR_STYLE}Failed to save markdown for {url} to {filepath}{STYLE_END}"
                                    )
                                    console.print(
                                        f"[bold red]✗ ERROR saving {filepath.name}[/bold red]"
                                    )
                                    failed_count += 1
                            else:
                                log.warning(
                                    f"{WARN_STYLE}LLM filter returned no content for {url}. Skipping save.{STYLE_END}"
                                )
                                failed_count += 1
                        else:
                            log.error(
                                f"{ERROR_STYLE}HTML fetch failed: {result.error_message or 'Unknown error'}{STYLE_END}"
                            )
                            failed_count += 1

                        # Same delay as original
                        delay_seconds: float = 1.0
                        log.info(
                            f"{INFO_STYLE}Waiting [yellow]{delay_seconds}[/] seconds...{STYLE_END}"
                        )
                        await asyncio.sleep(delay_seconds)

                    except KeyboardInterrupt:
                        live.stop()
                        console.print(
                            "\n[bold yellow]KeyboardInterrupt caught during URL processing. Signaling shutdown...[/bold yellow]"
                        )
                        shutdown_requested = True

                    except Exception:
                        log.exception(
                            f"{ERROR_STYLE}Unexpected error processing {url}{STYLE_END}"
                        )
                        console.print(f"[bold red]✗ ERROR processing {url}[/bold red]")
                        failed_count += 1
                        await asyncio.sleep(1.0)

                    if not shutdown_requested:
                        progress.update(crawl_task, advance=1)

    except KeyboardInterrupt:
        console.print(
            "\n[bold yellow]KeyboardInterrupt caught outside main loop. Shutting down...[/bold yellow]"
        )

    finally:
        console.print(
            f"\n[bold green]ScrollScribe finished processing. Saved: {success_count}. Failed/Skipped: {failed_count}.[/bold green]"
        )

    return success_count, failed_count
