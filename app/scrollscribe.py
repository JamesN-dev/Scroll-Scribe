# scrollscribe.py v0.1.4 (using rich.progress, improved logging, filename index debug)
# Reads URLs from file, scrapes HTML, uses LLMContentFilter on HTML, saves filtered MD.

import argparse
import asyncio
import os
import re
import sys
import logging  # Import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMConfig,
)
from crawl4ai.content_filter_strategy import LLMContentFilter
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler  # Import RichHandler
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich_argparse import RichHelpFormatter

# --- Rich Console ---
console = Console(force_terminal=True, color_system="truecolor")


# ==========================================================
# Turn on safe local debug logging
# Warning: Logs API keys! Use only in local/dev
# === LLM Debug Override (Optional) ===
def inject_debug_hooks(args):
    """Injects LiteLLM debug logging and completion tracing."""
    if args.debug:
        # --- Configure Root Logger with RichHandler ---
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        rich_handler = RichHandler(
            console=console,
            level=logging.DEBUG,
            show_time=True,
            show_level=True,
            show_path=False,
            markup=True,
        )
        if not any(isinstance(h, RichHandler) for h in root_logger.handlers):
            root_logger.addHandler(rich_handler)
            console.print("[yellow][DEBUG] RichHandler added to root logger.[/yellow]")
        else:
            console.print("[yellow][DEBUG] RichHandler already configured.[/yellow]")
        # --- End Logger Configuration ---

        console.print(
            "[yellow][DEBUG] Logging configured for DEBUG level via RichHandler.[/yellow]"
        )
        try:
            import litellm

            litellm._turn_on_debug()
            console.print(
                "[yellow][DEBUG] LiteLLM debug logging enabled (should use RichHandler).[/yellow]"
            )

            from litellm import completion as real_completion

            def debug_and_trace_completion(*args_, **kwargs_):
                console.print(
                    f"[magenta][LLM TRACE] Calling model: {kwargs_.get('model', '<unspecified>')}[/magenta]"
                )
                response = real_completion(*args_, **kwargs_)
                model_used = getattr(
                    response, "model", kwargs_.get("model", "<unspecified>")
                )
                console.print(
                    f"[bold blue]🧠 Actual model used:[/bold blue] {model_used}"
                )
                return response

            litellm.completion = debug_and_trace_completion
            console.print(
                "[yellow][DEBUG] LiteLLM completion wrapper injected.[/yellow]"
            )

        except ImportError:
            console.print(
                "[bold red][ERROR] litellm not found. Cannot enable LLM debug tracing.[/bold red]"
            )
        except Exception as e:
            console.print(
                f"[bold red][ERROR] Failed to set up LLM debug hooks: {e}[/bold red]"
            )


# ==========================================================

# Load .env
load_dotenv()


# --- Argument Parser Setup ---
def setup_argparse():
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
        "-v", "--verbose", action="store_true", help="Enable verbose logging."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable LLM call tracing (shows model, input/output, etc.). Not for production.",
    )
    return parser.parse_args()


# --- File Reading Function ---
def read_urls_from_file(filepath: str) -> list[str]:
    """Reads URLs from a text file, one per line, skipping empty/invalid lines."""
    urls = []
    console.print(f"[cyan][INFO] Reading URLs from:[/cyan] {filepath}")
    try:
        with open(filepath, encoding="utf-8") as file_object:
            for line in file_object:
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue
                match = re.search(r"https?://\S+", cleaned_line)
                if match:
                    url = match.group(0).rstrip(".,;:!?")
                    urls.append(url)
                else:
                    console.print(
                        f"[yellow][WARN] Skipping invalid line:[/yellow] '{cleaned_line}'"
                    )
    except FileNotFoundError:
        console.print(f"[bold red][ERROR] Input file not found:[/bold red] {filepath}")
        sys.exit(1)
    except Exception as e:
        console.print(
            f"[bold red][ERROR] Failed to read file {filepath}: {e}[/bold red]"
        )
        sys.exit(1)
    console.print(f"[cyan][INFO] Found {len(urls)} valid URLs in file.[/cyan]")
    return urls


# --- Function to create a safe filename ---
def url_to_filename(
    url: str, index: int, extension: str = ".md", max_len: int = 100
) -> str:
    """Creates a relatively safe filename from a URL and index."""
    try:
        parsed = urlparse(url)
        path_part = parsed.path.strip("/") if parsed.path.strip("/") else parsed.netloc
        safe_path = re.sub(r'[\\/:*?"<>|]+', "_", path_part)
        safe_path = re.sub(r"\s+", "_", safe_path)
        safe_path = safe_path[:max_len].rstrip("._")
        if not safe_path:
            safe_path = f"url_{index}"
        return f"page_{index:03d}_{safe_path}{extension}"
    except Exception as e:
        console.print(
            f"[yellow][WARN] Failed to generate safe filename for URL index {index}: {e}. Using fallback.[/yellow]"
        )
        return f"page_{index:03d}{extension}"


# --- Helper to run potentially sync filter method in executor ---
async def run_llm_filter(
    filter_instance: LLMContentFilter, html_content: str
) -> str | None:
    """Runs the filter's potentially synchronous method in a thread pool."""
    if not html_content:
        return None
    try:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            filtered_chunks = await loop.run_in_executor(
                pool, filter_instance.filter_content, html_content
            )
        if isinstance(filtered_chunks, list):
            return "\n\n---\n\n".join(filtered_chunks)
        elif isinstance(filtered_chunks, str):
            return filtered_chunks
        else:
            console.print(
                f"[yellow][WARN] LLM Filter returned unexpected type: {type(filtered_chunks)}[/yellow]"
            )
            return None
    except Exception as e:
        logging.exception(f"Error running LLMContentFilter: {e}")
        return None


# --- Main Async Function ---
async def main(args):
    """Reads URLs, crawls HTML, uses LLMContentFilter, saves filtered markdown."""
    if args.debug:
        inject_debug_hooks(args)  # Configure logging if debug is set

    global cli_args
    cli_args = args

    api_key = os.getenv(args.api_key_env)
    if not api_key:
        console.print(
            f"[bold red][ERROR] API key env var '{args.api_key_env}' not found![/bold red]"
        )
        sys.exit(1)
    console.print(f"[cyan][INFO] Found API key in env var: {args.api_key_env}[/cyan]")

    all_urls = read_urls_from_file(args.input_file)
    if args.start_at < 0:
        console.print(
            "[yellow][WARN] --start-at cannot be negative. Starting from 0.[/yellow]"
        )
        args.start_at = 0
    elif args.start_at >= len(all_urls):
        console.print(
            f"[bold red][ERROR] --start-at index {args.start_at} is out of bounds for {len(all_urls)} URLs.[/bold red]"
        )
        return

    urls_to_scrape = all_urls[args.start_at :]
    total_urls_in_file = len(all_urls)

    if not urls_to_scrape:
        console.print(
            f"[bold red][ERROR] No URLs left to process after --start-at {args.start_at}[/bold red]"
        )
        return

    if args.verbose:
        console.print(
            f"[cyan][INFO] Starting at index {args.start_at} ({urls_to_scrape[0]})[/cyan]"
        )

    output_dir = Path(args.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"[cyan][INFO] Output directory:[/cyan] {output_dir}")
    except OSError as e:
        console.print(
            f"[bold red][ERROR] Could not create output dir {output_dir}: {e}[/bold red]"
        )
        return

    # --- crawl4ai Configurations ---
    browser_config = BrowserConfig(headless=True, verbose=args.verbose)
    llm_config = LLMConfig(
        provider=args.model,
        api_token=api_key,
        base_url=args.base_url if args.base_url else None,
    )
    console.print(f"[cyan][INFO] Using LLM model for filtering: {args.model}[/cyan]")

    # Default prompt updated based on user input
    default_llm_filter_instruction = """You are an expert Markdown converter for technical documentation websites.
    Your goal is to extract ONLY the main documentation content (text, headings, code blocks, lists, tables) from the provided HTML and format it as clean, well-structured Markdown.

    **Site-Specific Hints (Use these to help identify the main content area):**
    <site_hints>
    - For Django docs: The main content is likely within a ` class="container sidebar-right"`, specifically look for content inside the `<main>` tag or elements related to 'docs-content'. Be aware this container might also hold irrelevant sidebar info to exclude.
    Focus on the main documentation only. Ensure the final output contains only valid Markdown syntax. Do not include any raw HTML tags like <div>, <span>, etc. unless it is marked in a code block for demonstration
    </site_hints>

    - Preserve full absolute URLs for all links.
    - Normalize heading styles to consistent title-case.
    - Ensure code blocks, lists, and tables are accurately preserved.
    - Spot-check punctuation and quoting in JSON/YAML snippets to avoid stray characters.
    - Exclude obvious site navigation and ads, but feel free to surface any useful page-specific notes that look relevant.

    Output ONLY the cleaned Markdown content. Do not add any extra explanations or commentary. Ensure the final output contains only valid Markdown syntax. Do not include any raw HTML tags like <div>, <span>, etc. unless it is marked in a code block for demonstration
    """
    llm_filter_instruction = (
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
        markdown_generator=None,
        extraction_strategy=None,
        verbose=args.verbose,
    )
    # --- End Configurations ---

    console.print(
        f"[cyan][INFO] Starting crawl for {len(urls_to_scrape)} URLs (sequentially)...[/cyan]"
    )
    success_count = 0
    failed_count = 0

    async with AsyncWebCrawler(config=browser_config) as crawler:
        if args.debug:
            console.rule("[bold magenta]🧪 LLM Debug Mode Active[/bold magenta]")

        progress_columns = [
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("[cyan]{task.completed:>4d}[/]/[cyan]{task.total:>4d}[/]"),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            TextColumn("•"),
            SpinnerColumn(),
        ]

        with Progress(*progress_columns, console=console, transient=False) as progress:
            crawl_task = progress.add_task(
                "[cyan]Processing URLs", total=len(urls_to_scrape)
            )

            for loop_index, url in enumerate(urls_to_scrape):
                original_index = args.start_at + loop_index + 1
                total_to_process = len(urls_to_scrape)

                console.print(
                    f"\n[cyan][INFO] Processing URL {loop_index + 1}/{total_to_process} (Overall: {original_index}/{total_urls_in_file}):[/cyan] {url}"
                )
                filepath = None
                html_to_filter = None

                try:
                    console.print("  [INFO] Fetching HTML...")
                    result_list = await crawler.arun(url=url, config=html_fetch_config)

                    if result_list:
                        result = result_list[0]
                        if args.verbose or args.debug:
                            logging.debug(
                                f"Fetched URL: {getattr(result, 'url', 'N/A')} | Success: {getattr(result, 'success', 'N/A')} | HTML length: {len(getattr(result, 'html', '') or '')} | Error: {getattr(result, 'error_message', '')}"
                            )

                        if result.success:
                            html_to_filter = (
                                result.cleaned_html
                                if result.cleaned_html
                                else result.html
                            )
                            if not html_to_filter:
                                console.print(
                                    "  [yellow][WARN] HTML fetch succeeded but content is empty.[/yellow]"
                                )
                        else:
                            console.print(
                                f"  [bold red][ERROR] HTML fetch failed: {result.error_message or 'Unknown error'}[/bold red]"
                            )
                            failed_count += 1
                            await asyncio.sleep(1.0)
                            progress.update(crawl_task, advance=1)
                            continue
                    else:
                        console.print(
                            "  [yellow][WARN] No result returned from HTML fetch. Skipping.[/yellow]"
                        )
                        failed_count += 1
                        await asyncio.sleep(1.0)
                        progress.update(crawl_task, advance=1)
                        continue

                    if html_to_filter:
                        console.print(
                            f"  [INFO] HTML fetched ({len(html_to_filter)} chars). Sending to LLM filter ({args.model})..."
                        )
                        filtered_md = await run_llm_filter(
                            filter_instance=llm_content_filter,
                            html_content=html_to_filter,
                        )
                        if args.verbose and filtered_md:
                            logging.debug(
                                f"Filtered markdown length: {len(filtered_md)} chars"
                            )

                        if filtered_md:
                            # --- ADDED DEBUG PRINT ---
                            if args.debug or args.verbose:  # Print if debug or verbose
                                console.print(
                                    f"[magenta][DEBUG] Calculated original_index: {original_index} (start_at={args.start_at}, loop_index={loop_index})[/magenta]"
                                )
                            # --- END DEBUG PRINT ---
                            filename = url_to_filename(url, original_index)
                            filepath = output_dir / filename
                            try:
                                with open(filepath, "w", encoding="utf-8") as f:
                                    f.write(filtered_md)
                                console.print(
                                    f"[green][SUCCESS] Saved filtered markdown to:[/green] {filepath} ({len(filtered_md)} chars)"
                                )
                                success_count += 1
                            except OSError as e:
                                logging.exception(
                                    f"Failed to save markdown for {url} to {filepath}: {e}"
                                )
                                failed_count += 1
                        else:
                            console.print(
                                f"[yellow][WARN] LLM filter returned no content for {url}. Skipping save."
                            )
                            failed_count += 1
                    else:
                        failed_count += 1

                except Exception as e:
                    logging.exception(f"Unexpected error processing {url}: {e}")
                    failed_count += 1

                delay_seconds = 3.0
                console.print(
                    f"  [INFO] Waiting {delay_seconds} seconds before next URL..."
                )
                await asyncio.sleep(delay_seconds)
                progress.update(crawl_task, advance=1)

    console.print(
        f"\n[bold green]ScrollScribe finished. Saved: {success_count}. Failed/Skipped: {failed_count}.[/bold green]"
    )


# --- Script Entry Point ---
if __name__ == "__main__":
    cli_args = setup_argparse()
    api_key_env_var = cli_args.api_key_env
    if not os.getenv(api_key_env_var):
        console.print(
            f"[bold red][ERROR] API key env var '{api_key_env_var}' not found! Set in .env or environment.[/bold red]"
        )
        sys.exit(1)
    asyncio.run(main(cli_args))
