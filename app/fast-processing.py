"""Fast HTML-to-Markdown processing for ScrollScribe.

This module provides high-speed HTML→Markdown conversion using crawl4ai's
built-in markdown generation without LLM filtering. Designed to achieve
50-200 docs/minute processing speeds.

Based on analysis of cyberagiinc/DevDocs approach and modern crawl4ai patterns.
"""

import asyncio
import time
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    CrawlResult,
)
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.rule import Rule
from rich.text import Text
from rich.console import Group
from rich.live import Live

from .processing import RateColumn, absolutify_links, url_to_filename
from .utils.exceptions import FileIOError, ProcessingError
from .utils.logging import CleanConsole, get_logger

# Initialize logging
logger = get_logger("fast_processing")
clean_console = CleanConsole()


def get_fast_markdown_generator() -> DefaultMarkdownGenerator:
    """
    Create optimized markdown generator for fast processing.

    Uses PruningContentFilter (no LLM) with settings inspired by
    cyberagiinc/DevDocs implementation for clean, fast conversion.
    """
    content_filter = PruningContentFilter(
        threshold=0.2,  # Lower threshold = keep more content (like their config)
        threshold_type="dynamic",  # Adaptive filtering
        min_word_threshold=5,  # Lower word threshold for more inclusive content
    )

    return DefaultMarkdownGenerator(
        content_filter=content_filter,
        options={
            "body_width": 80,  # Consistent line wrapping
            "ignore_images": True,  # Skip images for faster processing
            "escape_html": True,  # Clean HTML escaping
            "citations": False,  # Skip citations for speed
        },
    )


def get_fast_crawler_config(args) -> CrawlerRunConfig:
    """
    Create optimized crawler configuration for fast processing.

    Focuses on speed and efficiency while maintaining content quality.
    Based on patterns from cyberagiinc/DevDocs and modern crawl4ai best practices.
    """
    # Session logic: same as your processing.py
    session_id: str = ""
    if getattr(args, "session_id", None):
        session_id = args.session_id
    elif getattr(args, "session", False):
        session_id = "scrollscribe_fast_session"

    return CrawlerRunConfig(
        # Session and caching
        session_id=session_id if session_id else "",
        cache_mode=CacheMode.DISABLED,  # Fresh content each time
        # Page loading settings
        wait_until=args.wait,
        page_timeout=args.timeout,
        # Fast markdown generation (no LLM)
        markdown_generator=get_fast_markdown_generator(),
        # Performance optimizations
        exclude_external_links=True,  # Focus on internal content
        exclude_social_media_links=True,  # Skip social links
        excluded_tags=[
            "script",
            "style",
            "nav",
            "footer",
            "aside",
            "header",
        ],  # Remove noise
        word_count_threshold=5,  # Lower threshold for faster processing
        remove_overlay_elements=True,  # Clean overlays
        # Disable expensive features for speed
        extraction_strategy=None,  # type: ignore[arg-type]
        verbose=False,  # Reduce logging noise
        stream=False,
    )


async def process_urls_fast(
    urls_to_scrape: list[str],
    args,
    output_dir: Path,
    browser_config: BrowserConfig,
) -> tuple[int, int]:
    """
    Fast HTML→Markdown processing without LLM filtering.

    Achieves 50-200 docs/minute by:
    - Using crawl4ai's built-in markdown generation only
    - Skipping LLM API calls entirely
    - Optimized browser config and session reuse
    - Streamlined content filtering with PruningContentFilter

    Args:
        urls_to_scrape: List of URLs to process
        args: CLI arguments from argparse
        output_dir: Directory to save markdown files
        browser_config: Browser configuration

    Returns:
        tuple[int, int]: (success_count, failed_count)
    """
    start_time = time.time()

    # Create fast crawler configuration
    fast_config = get_fast_crawler_config(args)

    # Create the persistent Live display (same style as your processing.py)
    progress_columns = [
        TextColumn("[#9ccfd8]Fast Processing URLs"),
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

    # Extract base URL for header
    base_url = urls_to_scrape[0] if urls_to_scrape else "unknown"
    clean_domain = base_url.replace("https://", "").replace("http://", "").split("/")[0]

    # Header with fast mode indication
    header_rule = Rule(
        f"[bold #c4a7e7]ScrollScribe[/] | [bold #31748f]Fast Mode:[/] [bold #e0def4]{clean_domain}[/]",
        style="#6e6a86",
    )
    header_text = Text(
        "⚡ Mode: Fast HTML→Markdown (No LLM)", justify="center", style="#f6c177"
    )
    live_group = Group(header_rule, header_text, progress)

    logger.info(
        f"Starting FAST crawl for {len(urls_to_scrape)} URLs (no LLM processing)..."
    )
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

                # Batch fetch with session reuse (same as your processing.py)
                logger.info(
                    f"Batch fetching {len(urls_to_scrape)} URLs with session reuse (FAST mode)..."
                )
                all_results: list[CrawlResult] = cast(
                    "list[CrawlResult]",
                    await crawler.arun_many(urls_to_scrape, config=fast_config),
                )

                # Process each result
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
                        f"Fast processing URL {loop_index + 1}/{total_to_process} (Overall: {original_index}): {url}"
                    )

                    try:
                        if result.success and result.markdown:
                            # Get the fit_markdown (filtered by PruningContentFilter)
                            markdown_content = (
                                result.markdown.fit_markdown
                                or result.markdown.raw_markdown
                            )

                            if (
                                not markdown_content
                                or len(markdown_content.strip()) < 50
                            ):
                                failed_count += 1
                                clean_console.print_url_status(
                                    url, "warning", 0, "empty/minimal content"
                                )
                                progress.update(crawl_task, advance=1)
                                continue

                            # Absolutify links (same as your processing.py)
                            absolute_md = absolutify_links(markdown_content, url)

                            # Save to file
                            filename: str = url_to_filename(url, original_index)
                            filepath = output_dir / filename

                            try:
                                with open(filepath, "w", encoding="utf-8") as f:
                                    f.write(absolute_md)

                                url_time = time.time() - url_start_time
                                chars = len(absolute_md)

                                clean_console.print_url_status(
                                    url,
                                    "success",
                                    url_time,
                                    f"{chars:,} chars → {filename} (FAST)",
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
                            logger.error(
                                f"Fast processing failed for {url}: {error_msg}"
                            )
                            clean_console.print_url_status(url, "error", 0, error_msg)

                        # Shorter delay for fast mode
                        delay_seconds: float = 0.5  # Faster than regular processing
                        await asyncio.sleep(delay_seconds)

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

                        if isinstance(exc, (ProcessingError, FileIOError)):
                            clean_console.print_url_status(url, "error", 0, str(exc))
                        else:
                            clean_console.print_url_status(
                                url, "error", 0, "unexpected error"
                            )

                        await asyncio.sleep(0.5)

                    if not shutdown_requested:
                        progress.update(crawl_task, advance=1)

    except KeyboardInterrupt:
        clean_console.print_warning(
            "KeyboardInterrupt caught in fast mode. Shutting down..."
        )

    finally:
        total_time = time.time() - start_time

        # Calculate processing rate for fast mode
        if total_time > 0:
            docs_per_minute = (success_count / total_time) * 60
            clean_console.console.print(
                f"\n[bold #f6c177]⚡ Fast Mode Performance:[/] "
                f"[bold #9ccfd8]{docs_per_minute:.1f} docs/minute[/]"
            )

        clean_console.print_summary(success_count, failed_count, total_time)

        logger.info(
            f"ScrollScribe FAST mode finished. Saved: {success_count}. Failed/Skipped: {failed_count}."
        )

    return success_count, failed_count
