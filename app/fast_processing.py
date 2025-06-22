"""Fast HTML-to-Markdown processing for ScrollScribe.

Implements the backend for the `--fast` flag in the CLI, enabling high-speed HTML→Markdown conversion
using crawl4ai's built-in markdown generation with PruningContentFilter. Bypasses LLM processing entirely
for 50-200 docs/minute throughput.

Key features:
- No API costs - completely free to run
- Uses crawl4ai's DefaultMarkdownGenerator with PruningContentFilter
- Smart content filtering removes navigation, footers, and low-value content
- Proper batch processing with session reuse
- Rich progress display with persistent Live display
- Compatible with existing CleanConsole logging system

Note:
    This module imports shared processing utilities (such as link absolutification and filename
    sanitization) from `processing.py`.
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

logger = get_logger("fast_processing")
clean_console = CleanConsole()


async def process_urls_fast(
    urls_to_scrape: list[str],
    args,
    output_dir: Path,
    browser_config: BrowserConfig,
) -> tuple[int, int]:
    """Convert a batch of documentation URLs to Markdown using fast, non-LLM processing.

    This function uses crawl4ai's PruningContentFilter and DefaultMarkdownGenerator
    to efficiently convert HTML to Markdown, saving results to the specified output directory.

    Args:
        urls_to_scrape: List of URLs to process.
        args: Command line arguments from argparse.
        output_dir: Output directory for markdown files.
        browser_config: Browser configuration for crawl4ai.

    Returns:
        tuple[int, int]: Number of successful and failed conversions.
    """
    start_time = time.time()

    session_id: str = ""
    if getattr(args, "session_id", None):
        session_id = args.session_id
    elif getattr(args, "session", False):
        session_id = "scrollscribe_fast_session"

    prune_filter = PruningContentFilter(
        threshold=0.48,
        threshold_type="fixed",
        min_word_threshold=10,
    )

    markdown_generator = DefaultMarkdownGenerator(
        content_filter=prune_filter,
        options={
            "ignore_links": False,
            "content_source": "cleaned_html",
        },
    )

    fast_config = CrawlerRunConfig(
        session_id=session_id if session_id else "",
        cache_mode=CacheMode.DISABLED,
        wait_until=args.wait,
        page_timeout=args.timeout,
        markdown_generator=markdown_generator,
        verbose=False,
        stream=False,
        exclude_external_links=True,
        excluded_tags=["script", "style", "nav", "footer", "aside", "header"],
        word_count_threshold=10,
        only_text=False,
        prettiify=False,
        remove_forms=True,
    )

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

    base_url = urls_to_scrape[0] if urls_to_scrape else "unknown"
    clean_domain = base_url.replace("https://", "").replace("http://", "").split("/")[0]

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
            refresh_per_second=8,
            console=clean_console.console,
            transient=False,
        ) as live:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                crawl_task = progress.add_task(
                    description="", total=len(urls_to_scrape)
                )

                logger.info(
                    f"Batch fetching {len(urls_to_scrape)} URLs in fast mode..."
                )
                all_results: list[CrawlResult] = cast(
                    "list[CrawlResult]",
                    await crawler.arun_many(urls_to_scrape, config=fast_config),
                )

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

                            absolute_md = absolutify_links(raw_markdown, url)
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

                        await asyncio.sleep(0.1)

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

                        if isinstance(exc, ProcessingError):
                            clean_console.print_url_status(url, "error", 0, str(exc))
                        else:
                            clean_console.print_url_status(
                                url, "error", 0, "unexpected error"
                            )

                        await asyncio.sleep(0.1)

                    if not shutdown_requested:
                        progress.update(crawl_task, advance=1)

    except KeyboardInterrupt:
        clean_console.print_warning(
            "KeyboardInterrupt caught outside main loop. Shutting down fast mode..."
        )

    finally:
        total_time = time.time() - start_time

        clean_console.print_summary(success_count, failed_count, total_time)

        if total_time > 0:
            rate_per_minute = (success_count + failed_count) * 60 / total_time
            clean_console.print_success(
                f"Fast mode completed: {rate_per_minute:.1f} pages/minute"
            )

        logger.info(
            f"Fast ScrollScribe finished. Saved: {success_count}. Failed/Skipped: {failed_count}."
        )

    return success_count, failed_count
