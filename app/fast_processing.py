"""Fast HTML-to-Markdown processing for ScrollScribe.

Implements blazing-fast HTML→Markdown conversion using crawl4ai's built-in
markdown generation with PruningContentFilter. Bypasses LLM processing entirely
for 50-200 docs/minute throughput.

Key features:
- No API costs - completely free to run
- Uses crawl4ai's DefaultMarkdownGenerator with PruningContentFilter
- Smart content filtering removes navigation, footers, and low-value content
- Proper batch processing with session reuse
- Rich progress display with persistent Live display
- Compatible with existing CleanConsole logging system
"""

import asyncio
import time
from pathlib import Path
from typing import cast

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    CrawlResult,
)
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from rich.console import Group
from rich.live import Live
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.rule import Rule
from rich.text import Text

from .processing import RateColumn, absolutify_links, url_to_filename
from .utils.exceptions import ProcessingError
from .utils.logging import CleanConsole, get_logger

# Initialize the clean logging system
logger = get_logger("fast_processing")
clean_console = CleanConsole()


async def process_urls_fast(
    urls_to_scrape: list[str],
    args,
    output_dir: Path,
    browser_config: BrowserConfig,
) -> tuple[int, int]:
    """
    Fast HTML→Markdown processing using crawl4ai's built-in markdown generation.

    Features:
    - 50-200 docs/minute throughput (5-20x faster than LLM mode)
    - No API costs - completely free to run
    - Uses PruningContentFilter to remove navigation, footers, low-value content
    - Batch processing with session reuse for performance
    - Rich progress display with persistent Live display
    - Compatible with CleanConsole logging system

    Args:
        urls_to_scrape: List of URLs to process
        args: Command line arguments from argparse
        output_dir: Output directory for markdown files
        browser_config: Browser configuration for crawl4ai

    Returns:
        tuple[int, int]: (success_count, failed_count)
    """
    start_time = time.time()

    # Session logic: only set session_id if --session or --session-id is provided
    session_id: str = ""
    if getattr(args, "session_id", None):
        session_id = args.session_id
    elif getattr(args, "session", False):
        session_id = "scrollscribe_fast_session"

    # Create fast mode markdown generator with PruningContentFilter
    # Based on crawl4ai docs - removes navigation, footers, low-value content
    prune_filter = PruningContentFilter(
        threshold=0.48,  # Balanced threshold for good content retention
        threshold_type="fixed",  # Use fixed threshold for consistency
        min_word_threshold=10,  # Skip very short content blocks
    )

    markdown_generator = DefaultMarkdownGenerator(
        content_filter=prune_filter,
        options={
            "ignore_links": False,  # Keep links for documentation
            "content_source": "cleaned_html",  # Use cleaned HTML as source
        },
    )

    # Configure for fast processing - bypass cache, optimize for speed
    fast_config = CrawlerRunConfig(
        session_id=session_id if session_id else "",  # Always pass a string
        cache_mode=CacheMode.DISABLED,  # Fresh content, no cache overhead
        wait_until=args.wait,
        page_timeout=args.timeout,
        markdown_generator=markdown_generator,  # Use our fast markdown generator
        extraction_strategy=None,  # No structured extraction needed
        verbose=False,  # Minimize noise for speed
        stream=False,  # Batch mode for this implementation
        # Performance optimizations
        exclude_external_links=True,  # Focus on internal content
        excluded_tags=["script", "style", "nav", "footer", "aside", "header"],
        word_count_threshold=10,  # Lower threshold for faster processing
        # Fast mode specific - minimize processing overhead
        only_text=False,  # Keep structure but optimize
        prettiify=False,  # Skip beautification for speed
        remove_forms=True,  # Remove forms to reduce noise
    )

    # Create the persistent Live display like original scrollscribe.py
    progress_columns = [
        TextColumn("[#9ccfd8]⚡ Fast Mode"),
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

    # Use Rose Pine dark theme header format - indicate fast mode
    header_rule = Rule(
        f"[bold #c4a7e7]ScrollScribe[/] | [bold #31748f]Fast Mode:[/] [bold #e0def4]{clean_domain}[/]",
        style="#6e6a86",
    )
    header_text = Text(
        "🚀 Mode: HTML→Markdown (No LLM)", justify="center", style="#f6c177"
    )
    live_group = Group(header_rule, header_text, progress)

    logger.info(f"Starting fast crawl for {len(urls_to_scrape)} URLs...")
    success_count: int = 0
    failed_count: int = 0
    shutdown_requested: bool = False

    try:
        with Live(
            live_group,
            refresh_per_second=8,  # Higher refresh rate for fast mode
            console=clean_console.console,
            transient=False,
        ) as live:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                crawl_task = progress.add_task(
                    description="", total=len(urls_to_scrape)
                )

                # Batch fetch with session reuse for maximum performance
                logger.info(
                    f"Batch fetching {len(urls_to_scrape)} URLs in fast mode..."
                )
                all_results: list[CrawlResult] = cast(
                    "list[CrawlResult]",
                    await crawler.arun_many(urls_to_scrape, config=fast_config),
                )

                # Process each result using CleanConsole for individual URL status
                for loop_index, (url, result) in enumerate(
                    zip(urls_to_scrape, all_results, strict=True)
                ):
                    if shutdown_requested:
                        clean_console.print_warning(
                            "Shutdown requested, stopping fast processing..."
                        )
                        break

                    original_index: int = args.start_at + loop_index + 1
                    total_to_process: int = len(urls_to_scrape)
                    url_start_time = time.time()

                    logger.info(
                        f"Processing URL {loop_index + 1}/{total_to_process} (Overall: {original_index}): {url}"
                    )

                    try:
                        if result.success and result.markdown:
                            # Fast mode gets markdown directly from crawl4ai
                            raw_markdown = result.markdown.raw_markdown

                            if not raw_markdown or len(raw_markdown.strip()) < 50:
                                failed_count += 1
                                clean_console.print_url_status(
                                    url, "warning", 0, "empty content"
                                )
                                progress.update(crawl_task, advance=1)
                                continue

                            logger.info(
                                f"Markdown generated ({len(raw_markdown)} chars) - applying link fixes..."
                            )

                            # Apply link absolutification
                            absolute_md = absolutify_links(raw_markdown, url)
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

                            except OSError as e:
                                failed_count += 1
                                logger.error(
                                    f"Failed to save markdown for {url} to {filepath}: {e}"
                                )
                                clean_console.print_url_status(
                                    url, "error", 0, "save failed"
                                )
                        else:
                            failed_count += 1
                            error_msg = result.error_message or "No markdown generated"
                            logger.error(f"Fast processing failed: {error_msg}")
                            clean_console.print_url_status(url, "error", 0, error_msg)

                        # Minimal delay for fast mode - just enough to be respectful
                        await asyncio.sleep(0.1)  # 100ms delay

                    except KeyboardInterrupt:
                        live.stop()
                        clean_console.print_warning(
                            "KeyboardInterrupt caught during fast processing. Signaling shutdown..."
                        )
                        shutdown_requested = True

                    except Exception as exc:
                        failed_count += 1
                        logger.error(
                            f"Unexpected error in fast processing {url}: {exc}"
                        )

                        # Use proper exception handling
                        if isinstance(exc, ProcessingError):
                            clean_console.print_url_status(url, "error", 0, str(exc))
                        else:
                            clean_console.print_url_status(
                                url, "error", 0, "unexpected error"
                            )

                        await asyncio.sleep(0.1)  # Brief pause on error

                    if not shutdown_requested:
                        progress.update(crawl_task, advance=1)

    except KeyboardInterrupt:
        clean_console.print_warning(
            "KeyboardInterrupt caught outside main loop. Shutting down fast mode..."
        )

    finally:
        total_time = time.time() - start_time

        # Use CleanConsole for final summary
        clean_console.print_summary(success_count, failed_count, total_time)

        # Calculate and display fast mode performance
        if total_time > 0:
            rate_per_minute = (success_count + failed_count) * 60 / total_time
            clean_console.print_success(
                f"Fast mode completed: {rate_per_minute:.1f} pages/minute"
            )

        # Also log for structured logging
        logger.info(
            f"Fast ScrollScribe finished. Saved: {success_count}. Failed/Skipped: {failed_count}."
        )

    return success_count, failed_count
