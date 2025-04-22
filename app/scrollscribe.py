"""ScrollScribe.py: Scrape Web Content to Filtered Markdown using LLMs.

Reads a list of URLs from an input text file, crawls each URL using crawl4ai
to fetch and clean HTML content, applies a crawl4ai LLM-based content filter
(LLMContentFilter) via a specified provider (e.g., Defualt OpenRouter) to extract the
main textual content and format it as Markdown, and saves the resulting
Markdown to individual files in an output directory.

Features:
- Asynchronous web crawling using crawl4ai and Playwright.
- Content filtering and HTML-to-Markdown conversion via Large Language Models.
- Configurable LLM provider, model, API key, base URL, max tokens, and custom prompt injection.
- Support for starting processing from a specific URL index (`--start-at`),
  with output filenames reflecting the original index.
- Rich console output using 'rich':
    - Live-updating progress bar with rate and ETA.
    - Persistent header showing the LLM model in use.
    - Colored status messages and library logs (via RichHandler).
- Enhanced debug logging (`--debug`) including attempts to capture detailed logs
  from underlying libraries (like litellm).
- Graceful shutdown handling for KeyboardInterrupt (Ctrl+C).
- Command-line interface with configurable options via argparse.

Usage:
    # Direct execution (shows script arguments):
    uv run app/scrollscribe.py <input_file.txt> -o <output_directory> [options]

    # Using the helper script (uses defaults from runscript.sh):
    ./runscript.sh [optional --debug]

Example:
    # Direct execution with specific options:
    uv run app/scrollscribe.py data/doc_links.txt -o output/markdown --model mistralai/codestral -v --start-at 10

    # Using the helper script (check runscript.sh for defaults):
    ./runscript.sh
"""

import argparse
import asyncio
import logging
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlparse

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMConfig,
)
from crawl4ai.content_filter_strategy import LLMContentFilter
from dotenv import load_dotenv
from rich.console import Console, Group
from rich.live import Live
from rich.logging import RichHandler
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
from rich.rule import Rule
from rich.text import Text
from rich_argparse import RichHelpFormatter

console = Console(force_terminal=True, color_system="truecolor")

# --- Global placeholder for CLI args ---
# Used for run_llm_filter exception logging context
cli_args: argparse.Namespace | None = None

# --- Define Styles for Wrapping Log Messages ---
# These style tags will wrap the entire message passed to the logger.
# RichHandler markup=True will render them.
INFO_STYLE = "[bright_green]"
WARN_STYLE = "[bright_yellow]"
ERROR_STYLE = "[bright_red]"
CRITICAL_STYLE = "[bold white on red]"
STYLE_END = "[/]"

# --- Configure Root Logger with RichHandler GLOBALLY ---
log = logging.getLogger()  # Get root logger
rich_handler = RichHandler(
    console=console,
    rich_tracebacks=True,
    markup=True,  # Enable markup rendering in log messages
    show_path=False,
)

logging.basicConfig(
    level=logging.WARNING,  # Default level for root logger
    format="%(message)s",  # Let RichHandler control formatting
    datefmt="[%X]",
    handlers=[rich_handler],
)
# Get litellm logger specifically to control its level independently
litellm_logger = logging.getLogger("litellm")
# Default litellm to ERROR (quieter), adjusted in main() based on -v
litellm_logger.setLevel(logging.ERROR)


# ==========================================================
# Custom Rich Progress Column for Rate (Seconds per Item)
# ==========================================================
class RateColumn(ProgressColumn):
    """Renders the processing rate (seconds per item)."""

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


# ==========================================================
# Debug Hooks Function REMOVED
# ==========================================================


# ==========================================================
# Load .env
load_dotenv()


# --- Argument Parser Setup ---
def setup_argparse() -> argparse.Namespace:
    """Sets up and parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape URLs from file to cleaned Markdown files using LLMContentFilter.\n\nExample:\n  uv run app/scrollscribe.py data/doc_links.txt -o output/my_docs_markdown -t 90000",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument("input_file", help="Path to the text file containing URLs.")
    parser.add_argument(
        "--start-at",
        type=int,
        default=0,
        help="Start processing at this index in the input URL list (0-based).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="output_llm_filtered_markdown",
        help="Directory to save filtered Markdown files.",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        default="",
        help="Inject a custom instructions prompt for the LLM content filtering.",
    )
    parser.add_argument(
        "-t", "--timeout", type=int, default=35000, help="Page load timeout in ms."
    )
    parser.add_argument(
        "-w",
        "--wait",
        default="networkidle",
        choices=["load", "domcontentloaded", "networkidle"],
        help="Playwright wait_until state.",
    )
    parser.add_argument(
        "--model",
        default="openrouter/google/gemini-2.0-flash-exp:free",
        help="LLM model identifier for filtering.",
    )
    parser.add_argument(
        "-api",
        "--api-key-env",
        default="OPENROUTER_API_KEY",
        help="Environment variable name for the LLM API key.",
    )
    parser.add_argument(
        "--base-url",
        default="https://openrouter.ai/api/v1",
        help="API Base URL for LLM.",
    )
    parser.add_argument(
        "-max",
        "--max-tokens",
        type=int,
        default=8192,
        help="Max output tokens for the LLM filtering.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging (Script INFO level).",
    )
    return parser.parse_args()


# --- File Reading Function ---
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
        console.print(f"[bold red][ERROR] Input file not found:[/bold red] {filepath}")
        sys.exit(1)
    except Exception:
        log.exception(
            f"{ERROR_STYLE}Failed to read file [underline]{filepath}[/underline]{STYLE_END}"
        )
        console.print(f"[bold red][ERROR] Failed to read file {filepath}[/bold red]")
        sys.exit(1)
    log.info(f"{INFO_STYLE}Found [bold]{len(urls)}[/] valid URLs in file.{STYLE_END}")
    return urls


# --- Function to create a safe filename ---
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
            safe_path = f"url_{index}"  # Fixed E701
        return f"page_{index:03d}_{safe_path}{extension}"
    except Exception:
        log.exception(
            f"{ERROR_STYLE}Failed to generate safe filename for URL index [bold]{index}[/]. Using fallback.{STYLE_END}"
        )
        return f"page_{index:03d}{extension}"


# --- Helper to run potentially sync filter method in executor ---
async def run_llm_filter(
    filter_instance: LLMContentFilter, html_content: str
) -> str | None:
    """
    Runs the filter's potentially synchronous method in a thread pool
    with retry logic for rate limiting errors.
    """
    if not html_content:
        return None  # Fixed E701

    loop = asyncio.get_event_loop()
    max_retries = 5
    filtered_chunks = None

    for attempt in range(max_retries):
        try:
            with ThreadPoolExecutor() as pool:
                filtered_chunks = await loop.run_in_executor(
                    pool, filter_instance.filter_content, html_content
                )
            break  # Success
        except Exception as e:
            msg = str(e).lower()
            is_rate_limit = (
                "429" in msg or "rate limit" in msg or "rate_limit_exceeded" in msg
            )

            if is_rate_limit and attempt < max_retries - 1:
                wait = 2**attempt

                log.warning(
                    f"{WARN_STYLE}Rate limit detected (attempt [bold]{attempt + 1}/{max_retries}[/]). "
                    f"Retrying in [bold]{wait}s[/]... Error: {e}{STYLE_END}"
                )
                await asyncio.sleep(wait)
                continue
            else:
                if is_rate_limit:
                    log.error(
                        f"{ERROR_STYLE}Exceeded {max_retries} retries due to rate limiting. Skipping LLM filter. Last Error: {e}{STYLE_END}"
                    )
                else:
                    log.exception(
                        f"{ERROR_STYLE}Non-retryable error during LLM filter (attempt {attempt + 1}): {e}{STYLE_END}"
                    )
                return None  # Exit function

    if filtered_chunks is None and attempt == max_retries - 1:
        log.error(
            f"{ERROR_STYLE}LLM filter failed after {max_retries} attempts, returning None.{STYLE_END}"
        )
        return None

    # Process successful result
    if isinstance(filtered_chunks, list):
        return "\n\n---\n\n".join(filtered_chunks)
    elif isinstance(filtered_chunks, str):
        return filtered_chunks
    else:
        log.warning(
            f"{WARN_STYLE}LLM Filter returned unexpected type after success: [bold]{type(filtered_chunks)}[/]{STYLE_END}"
        )
        return None


# --- Absolute Link Post-Processing Function ---
def absolutify_links(markdown_text: str, base_url: str) -> str:
    """
    Converts relative links in Markdown text to absolute URLs.
    Handles both Markdown [text](url) and inline HTML <a href="url"> links.
    Uses the provided base_url (typically the original page URL).
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
    if changes_made and (cli_args and cli_args.verbose):
        log.info(
            f"{INFO_STYLE}Applied absolute URL post-processing for base: [link={base_url}]{base_url}[/link]{STYLE_END}"
        )

    return processed_text


# --- Main Async Function ---
async def main(args: argparse.Namespace) -> None:
    """Reads URLs, crawls HTML, uses LLMContentFilter, saves filtered markdown."""

    global cli_args
    cli_args = args

    # --- Adjust Logging Levels Based on Flags --- Simplified ---
    if args.verbose:
        log.setLevel(logging.INFO)
        litellm_logger.setLevel(logging.ERROR)  # Keep litellm quiet
        log.info(
            f"{INFO_STYLE}Verbose logging enabled (INFO). Library logs limited to ERROR.{STYLE_END}"
        )
    else:
        log.setLevel(logging.WARNING)
        litellm_logger.setLevel(logging.ERROR)  # Keep litellm quiet
    # --- End Logging Level Adjustment ---

    # --- Rest of main setup ---
    api_key: str | None = os.getenv(args.api_key_env)
    if not api_key:
        log.critical(
            f"{CRITICAL_STYLE}API key env var '[bold]{args.api_key_env}[/]' not found!{STYLE_END}"
        )
        # Keep console print for critical exit error
        console.print(
            f"[bold red][ERROR] API key env var '{args.api_key_env}' not found![/bold red]"
        )
        sys.exit(1)
    log.info(
        f"{INFO_STYLE}Found API key in env var: [yellow]{args.api_key_env}[/]{STYLE_END}"
    )

    all_urls: list[str] = read_urls_from_file(args.input_file)
    if args.start_at < 0:
        log.warning(
            f"{WARN_STYLE}--start-at cannot be negative. Starting from 0.{STYLE_END}"
        )
        args.start_at = 0
    elif args.start_at >= len(all_urls):
        log.error(
            f"{ERROR_STYLE}--start-at index {args.start_at} is out of bounds for {len(all_urls)} URLs.{STYLE_END}"
        )
        console.print(
            f"[bold red][ERROR] --start-at index {args.start_at} is out of bounds for {len(all_urls)} URLs.[/bold red]"
        )
        return

    urls_to_scrape: list[str] = all_urls[args.start_at :]
    total_urls_in_file: int = len(all_urls)

    if not urls_to_scrape:
        log.error(
            f"{ERROR_STYLE}No URLs left to process after --start-at {args.start_at}{STYLE_END}"
        )
        console.print(
            f"[bold red][ERROR] No URLs left to process after --start-at {args.start_at}[/bold red]"
        )
        return

    log.info(
        f"{INFO_STYLE}Starting processing from index [bold]{args.start_at}[/].{STYLE_END}"
    )

    output_dir: Path = Path(args.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        log.info(
            f"{INFO_STYLE}Output directory set to: [cyan]{output_dir}[/]{STYLE_END}"
        )
    except OSError:
        log.exception(
            f"{ERROR_STYLE}Could not create output dir [cyan]{output_dir}[/]{STYLE_END}"
        )
        # Keep console print for critical exit error
        console.print(
            f"[bold red][ERROR] Could not create output dir {output_dir}[/bold red]"
        )
        return

    browser_config = BrowserConfig(headless=True, verbose=args.verbose)
    llm_config = LLMConfig(
        provider=args.model,
        api_token=api_key,
        base_url=args.base_url if args.base_url else None,
    )
    log.info(
        f"{INFO_STYLE}Using LLM model for filtering: [bold blue]{args.model}[/]{STYLE_END}"
    )

    default_llm_filter_instruction: str = """You are an expert Markdown converter for technical documentation websites.
    Your goal is to extract ONLY the main documentation content (text, headings, code blocks, lists, tables) from the provided HTML and format it as clean, well-structured Markdown.

    **Site-Specific Hints (Use these to help identify the main content area):**
    <site_hints>
    - For Django docs: The main content is likely within a ` class="container sidebar-right"`, specifically look for content inside the `<main>` tag or elements related to 'docs-content'. Be aware this container might also hold irrelevant sidebar info to exclude.
    Focus on the main documentation only. Ensure the final output contains only valid Markdown syntax. Do not include any raw HTML tags like <div>, <span>, etc. unless it is marked in a code block for demonstration
    </site_hints>

    - Convert any relative links (URLs beginning with "/" or just a filename/path) to absolute URLs by prefixing them with the original page’s base URL (e.g., if base is https://example.com/foo/ and link is bar.html, convert to https://example.com/foo/bar.html; if link is /baz/, convert to https://example.com/baz/). Preserve existing absolute URLs.
    - Normalize heading styles to consistent title-case.
    - Ensure code blocks, lists, and tables are accurately preserved.
    - Spot-check punctuation and quoting in JSON/YAML snippets to avoid stray characters.
    - Exclude obvious site navigation and ads, but feel free to surface any useful page-specific notes that look relevant.

    Output ONLY the cleaned Markdown content. Do not add any extra explanations or commentary. Ensure the final output contains only valid Markdown syntax. Do not include any raw HTML tags like <div>, <span>, etc. unless it is marked in a code block for demonstration
    """
    llm_filter_instruction: str = (
        args.prompt.strip() if args.prompt.strip() else default_llm_filter_instruction
    )
    llm_content_filter = LLMContentFilter(
        llm_config=llm_config,
        instruction=llm_filter_instruction,
        chunk_token_threshold=args.max_tokens,
        verbose=args.verbose,
    )
    html_fetch_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_until=args.wait,
        page_timeout=args.timeout,
        markdown_generator=None,  # type: ignore[arg-type]
        extraction_strategy=None,  # type: ignore[arg-type]
        verbose=args.verbose,
    )

    progress_columns = [
        TextColumn("[cyan]Processing URLs"),  # Static description
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
                crawl_task = progress.add_task("", total=len(urls_to_scrape))

                for loop_index, url in enumerate(urls_to_scrape):
                    if shutdown_requested:
                        # Use console print for shutdown message for immediate visibility
                        console.print(
                            "[yellow][WARN] Shutdown requested, stopping processing...[/yellow]"
                        )
                        break

                    original_index: int = args.start_at + loop_index + 1
                    total_to_process: int = len(urls_to_scrape)

                    log.info(
                        f"{INFO_STYLE}Processing URL [yellow]{loop_index + 1}/{total_to_process}[/] (Overall: [yellow]{original_index}/{total_urls_in_file}[/]): [link={url}]{url}[/link]{STYLE_END}"
                    )

                    try:
                        filepath: Path | None = None
                        html_to_filter: str | None = None

                        log.info(f"{INFO_STYLE}Fetching HTML...{STYLE_END}")
                        result_list = await crawler.arun(
                            url=url, config=html_fetch_config
                        )

                        if result_list:
                            result = result_list[0]  # type: ignore[index]

                            if result.success:
                                html_to_filter = (
                                    result.cleaned_html
                                    if result.cleaned_html
                                    else result.html
                                )
                                if not html_to_filter:
                                    log.warning(
                                        f"{WARN_STYLE}HTML fetch succeeded but content is empty.{STYLE_END}"
                                    )
                            else:
                                log.error(
                                    f"{ERROR_STYLE}HTML fetch failed: {result.error_message or 'Unknown error'}{STYLE_END}"
                                )
                                failed_count += 1

                                await asyncio.sleep(1.0)
                                progress.update(crawl_task, advance=1)
                                continue
                        else:
                            log.warning(
                                f"{WARN_STYLE}No result returned from HTML fetch. Skipping.{STYLE_END}"
                            )
                            failed_count += 1

                            await asyncio.sleep(1.0)
                            progress.update(crawl_task, advance=1)
                            continue

                        if html_to_filter:
                            log.info(
                                f"{INFO_STYLE}HTML fetched ([bold]{len(html_to_filter)}[/] chars). Sending to LLM filter ([blue]{args.model}[/])...{STYLE_END}"
                            )
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
                            log.warning(
                                f"{WARN_STYLE}HTML content was empty for {url}. Skipping LLM filter.{STYLE_END}"
                            )
                            failed_count += 1

                        delay_seconds: float = 3.0

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


# --- Script Entry Point ---
if __name__ == "__main__":
    # Setup args first so logging level is set before main logic runs
    cli_args = setup_argparse()
    try:
        asyncio.run(main(cli_args))
    except KeyboardInterrupt:
        console.print(
            "\n[bold yellow]KeyboardInterrupt caught during script startup/shutdown. Exiting.[/bold yellow]"
        )
        sys.exit(1)  # Exit with a non-zero code indicates abnormal termination
    except Exception:
        # Keep console print for critical top-level errors
        console.print(
            "[bold red][CRITICAL] Unhandled top-level error occurred.[/bold red]"
        )
        # Also log the exception with traceback
        log.exception("Unhandled top-level error")
        sys.exit(1)  # Exit with a non-zero code
