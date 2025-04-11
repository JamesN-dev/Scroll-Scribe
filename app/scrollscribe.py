# scroll_scribe.py v2.1
# Reads URLs from file, scrapes HTML, uses LLMContentFilter on HTML, saves filtered MD.

import asyncio
import os
import sys
import argparse
import re
from urllib.parse import urlparse
from pathlib import Path
from typing import List, Optional
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    CrawlResult,
    MarkdownGenerationResult,  # Still potentially in result object
    LLMConfig,
)
from crawl4ai.content_filter_strategy import LLMContentFilter
from dotenv import load_dotenv
from rich.console import Console
from concurrent.futures import ThreadPoolExecutor  # Needed for sync filter call
from tqdm import tqdm  # Progress bar

# Load .env
load_dotenv()


# --- TqdmRichFile for Rich + tqdm integration ---
class TqdmRichFile:
    def write(self, data):
        from tqdm import tqdm

        tqdm.write(data, end="")

    def flush(self):
        pass


# --- Rich Console ---
console = Console()


# --- Argument Parser Setup ---
def setup_argparse():
    """Sets up and parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape URLs from file to cleaned Markdown files using LLMContentFilter.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input_file", help="Path to the text file containing URLs.")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="output_llm_filtered_markdown",
        help="Directory to save filtered Markdown files.",
    )
    parser.add_argument(
        "-t", "--timeout", type=int, default=60000, help="Page load timeout in ms."
    )
    parser.add_argument(
        "--wait",
        default="networkidle",
        choices=["load", "domcontentloaded", "networkidle"],
        help="Playwright wait_until state.",
    )
    parser.add_argument(
        "--model",
        default="openrouter/openrouter/optimus-alpha",
        help="LLM model identifier for filtering.",
    )
    parser.add_argument(
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
        "--max-tokens",
        type=int,
        default=4096,
        help="Max output tokens for the LLM filtering.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging."
    )
    return parser.parse_args()


# --- File Reading Function ---
def read_urls_from_file(filepath: str) -> List[str]:
    """Reads URLs from a text file, one per line, skipping empty/invalid lines."""
    urls = []
    console.print(f"[cyan][INFO] Reading URLs from:[/cyan] {filepath}")
    try:
        with open(filepath, mode="r", encoding="utf-8") as file_object:
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
    # (Keep the url_to_filename function from previous version)
    try:
        parsed = urlparse(url)
        path_part = parsed.path.strip("/") or parsed.netloc
        safe_path = re.sub(r'[\\/:*?"<>|]', "_", path_part)
        safe_path = re.sub(r"\s+", "_", safe_path)
        safe_path = safe_path[:max_len].rstrip("._")
        if not safe_path:
            safe_path = f"url_{index}"
        return f"page_{index:03d}_{safe_path}{extension}"
    except Exception:
        return f"page_{index:03d}{extension}"


# --- Helper to run potentially sync filter method in executor ---
async def run_llm_filter(
    filter_instance: LLMContentFilter, html_content: str
) -> Optional[str]:
    """Runs the filter's potentially synchronous method in a thread pool."""
    if not html_content:
        return None
    try:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            # Assuming filter_content might be synchronous
            # If it's already async, just await it directly:
            # filtered_chunks = await filter_instance.filter_content(html_content)
            filtered_chunks = await loop.run_in_executor(
                pool, filter_instance.filter_content, html_content
            )
        # LLMContentFilter likely returns a list of strings (chunks)
        if isinstance(filtered_chunks, list):
            return "\n\n---\n\n".join(filtered_chunks)  # Join chunks
        elif isinstance(filtered_chunks, str):
            return filtered_chunks  # If it returns a single string
        else:
            console.print(
                f"[yellow][WARN] LLM Filter returned unexpected type: {type(filtered_chunks)}[/yellow]"
            )
            return None
    except Exception as e:
        console.print(
            f"[bold red][ERROR] Error running LLMContentFilter: {e}[/bold red]"
        )
        return None


# --- Main Async Function ---
async def main(args):
    """Reads URLs, crawls HTML, uses LLMContentFilter, saves filtered markdown."""
    global cli_args
    cli_args = args

    api_key = os.getenv(args.api_key_env)
    if not api_key:
        console.print(
            f"[bold red][ERROR] API key env var '{args.api_key_env}' not found![/bold red]"
        )
        sys.exit(1)
    console.print(f"[cyan][INFO] Found API key in env var: {args.api_key_env}[/cyan]")

    urls_to_scrape = read_urls_from_file(args.input_file)
    if not urls_to_scrape:
        return

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

    # LLM Config for the filter
    llm_config = LLMConfig(
        provider=args.model,
        api_token=api_key,
        base_url=args.base_url if args.base_url else None,
    )

    # LLM Content Filter instruction - update to whatever prompt you wish. Code is optimized for Markdown extraction.
    llm_filter_instruction = """You are an expert content extractor... Output ONLY the cleaned Markdown content."""

    # Create the LLMContentFilter instance
    llm_content_filter = LLMContentFilter(
        llm_config=llm_config,
        instruction=llm_filter_instruction,
        chunk_token_threshold=8000,
        verbose=args.verbose,
    )

    # Configure the run JUST TO GET HTML reliably
    html_fetch_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Cache the HTML fetch
        wait_until=args.wait,
        page_timeout=args.timeout,  # Use timeout from args
        markdown_generator=None,  # NO markdown generation here
        # content_filter=None,  # NO filter here
        extraction_strategy=None,  # NO extraction strat here
        verbose=args.verbose,
    )
    # --- End Configurations ---

    console.print(
        f"[cyan][INFO] Starting crawl for {len(urls_to_scrape)} URLs (sequentially)...[/cyan]"
    )
    success_count = 0
    failed_count = 0
    # processed_urls = set()
    # tasks = []
    # urls_being_processed = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        tqdm_console = Console(file=TqdmRichFile(), markup=True, force_terminal=True)
        pbar = tqdm(
            urls_to_scrape,
            desc="Processing URLs",
            unit="url",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
        )
        for index, url in enumerate(urls_to_scrape):
            tqdm_console.print(
                f"\n[cyan][INFO] Processing URL {index + 1}/{len(urls_to_scrape)}:[/cyan] {url}"
            )
            filepath = None

            try:
                # --- Pass 1: Fetch HTML ---
                tqdm_console.print("  [INFO] Fetching HTML...")
                result_list = await crawler.arun(
                    url=url, config=html_fetch_config
                )  # Use HTML fetch config

                html_to_filter = None
                if result_list:
                    result = result_list[0]
                    if args.verbose:
                        tqdm_console.print(
                            f"[magenta][DEBUG] Fetched URL: {getattr(result, 'url', 'N/A')} | Success: {getattr(result, 'success', 'N/A')} | HTML length: {len(getattr(result, 'html', '') or '')} | Error: {getattr(result, 'error_message', '')}[/magenta]"
                        )
                    if result.success:
                        html_to_filter = (
                            result.cleaned_html if result.cleaned_html else result.html
                        )
                        if not html_to_filter:
                            tqdm_console.print(
                                "  [yellow][WARN] HTML fetch succeeded but content is empty.[/yellow]"
                            )
                    else:
                        tqdm_console.print(
                            f"  [bold red][ERROR] HTML fetch failed: {result.error_message or 'Unknown error'}[/bold red]"
                        )
                        failed_count += 1
                        # Add delay even after failure before next URL
                        await asyncio.sleep(3.0)  # 3 second delay
                        continue  # Skip to next URL
                else:
                    tqdm_console.print(
                        "  [yellow][WARN] No result returned from HTML fetch. Skipping.[/yellow]"
                    )
                    failed_count += 1
                    # Add delay even after failure before next URL
                    await asyncio.sleep(3.0)  # 3 second delay
                    continue  # Skip to next URL

                # --- Pass 2: Filter with LLM (if HTML was fetched) ---
                if html_to_filter:
                    tqdm_console.print(
                        f"  [INFO] HTML fetched ({len(html_to_filter)} chars). Sending to LLM filter..."
                    )
                    filtered_md = await run_llm_filter(
                        filter_instance=llm_content_filter,
                        html_content=html_to_filter,
                    )
                    if args.verbose and filtered_md:
                        tqdm_console.print(
                            f"[magenta][DEBUG] Filtered markdown length: {len(filtered_md)} chars[/magenta]"
                        )

                    if filtered_md:
                        filename = url_to_filename(url, index + 1)
                        filepath = output_dir / filename
                        try:
                            with open(filepath, "w", encoding="utf-8") as f:
                                f.write(filtered_md)
                            tqdm_console.print(
                                f"[green][SUCCESS] Saved filtered markdown to:[/green] {filepath} ({len(filtered_md)} chars)"
                            )
                            success_count += 1
                        except IOError as e:
                            tqdm_console.print(
                                f"[bold red][ERROR] Failed to save markdown for {url} to {filepath}: {e}[/bold red]"
                            )
                            failed_count += 1
                    else:
                        console.print(
                            f"[yellow][WARN] LLM filter returned no content for {url}. Skipping save.[/yellow]"
                        )
                        failed_count += 1
                else:
                    # Already warned about empty HTML content above
                    failed_count += 1

            except Exception as e:
                console.print(
                    f"[bold red][CRITICAL] Unexpected error processing {url}: {e}[/bold red]"
                )
                failed_count += 1

            # --- IMPORTANT: Delay Between URLs ---
            # Add a pause to avoid overwhelming the server / getting rate-limited
            # Adjust the sleep time as needed (3-5 seconds is often a safe start)
            delay_seconds = 3.0
            tqdm.write(f"  [INFO] Waiting {delay_seconds} seconds before next URL...")
            await asyncio.sleep(delay_seconds)
            # --- End Delay ---
            pbar.update(1)
        pbar.close()

    # --- End Crawling Loop ---

    console.print(
        f"\n[bold green]ScrollScribe finished. Saved: {success_count}. Failed/Skipped: {failed_count}.[/bold green]"
    )

    # --- Final Duration Log ---
    console.print(
        f"\n[bold green]ScrollScribe finished. Saved: {success_count}. Failed/Skipped: {failed_count}.[/bold green]"
    )


# --- Script Entry Point ---
if __name__ == "__main__":
    cli_args = setup_argparse()
    api_key_env_var = cli_args.api_key_env
    if not os.getenv(api_key_env_var):
        console.print(
            f"[bold red][ERROR] API key env var '{api_key_env_var}' not found! Set in .env.[/bold red]"
        )
        sys.exit(1)
    asyncio.run(main(cli_args))
