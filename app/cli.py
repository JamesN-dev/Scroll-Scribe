"""ScrollScribe V2 CLI - Unified command-line interface.

Commands:
- discover: Extract URLs from a documentation website
- scrape: Convert URLs to filtered markdown using LLM
- process: Unified pipeline (discover + scrape)
"""

import argparse
import asyncio
import os
import sys
import tempfile
from pathlib import Path

from crawl4ai import LLMConfig
from crawl4ai.content_filter_strategy import LLMContentFilter
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from .config import get_browser_config
from .discovery import extract_links, save_links_to_file
from .processing import process_urls_batch, read_urls_from_file
from .utils.exceptions import ConfigError, FileIOError

# Load environment variables from .env file
load_dotenv()

console = Console(force_terminal=True, color_system="truecolor")


def setup_base_parser() -> argparse.ArgumentParser:
    """Create the base argument parser."""
    parser = argparse.ArgumentParser(
        description="ScrollScribe V2 - AI-powered documentation scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover URLs only
  python -m app discover https://docs.example.com/ -o urls.txt

  # Scrape from URL list
  python -m app scrape urls.txt -o output/

  # Unified pipeline
  python -m app process https://docs.example.com/ -o output/
        """,
    )
    return parser


def setup_discover_parser(subparsers) -> None:
    """Setup the discover subcommand."""
    discover_parser = subparsers.add_parser(
        "discover", help="Extract URLs from a documentation website"
    )
    discover_parser.add_argument(
        "start_url", help="Starting URL to discover documentation links"
    )
    discover_parser.add_argument(
        "-o",
        "--output-file",
        required=True,
        help="Output file to save discovered URLs",
    )
    discover_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )


def setup_scrape_parser(subparsers) -> None:
    """Setup the scrape subcommand."""
    scrape_parser = subparsers.add_parser(
        "scrape", help="Convert URLs to filtered markdown using LLM"
    )
    scrape_parser.add_argument("input_file", help="Text file containing URLs to scrape")
    scrape_parser.add_argument(
        "--start-at",
        type=int,
        default=0,
        help="Start processing from URL index (0-based)",
    )
    scrape_parser.add_argument(
        "-o",
        "--output-dir",
        required=True,
        help="Output directory for markdown files",
    )
    scrape_parser.add_argument(
        "--prompt",
        default="",
        help="Custom LLM filtering prompt (uses default if empty)",
    )
    scrape_parser.add_argument(
        "--timeout",
        type=int,
        default=60000,
        help="Page timeout in milliseconds",
    )
    scrape_parser.add_argument(
        "--wait",
        default="networkidle",
        help="When to consider page loading complete",
    )
    scrape_parser.add_argument(
        "--model",
        default="openrouter/google/gemini-2.0-flash-exp:free",
        help="LLM model to use for filtering",
    )
    scrape_parser.add_argument(
        "--api-key-env",
        default="OPENROUTER_API_KEY",
        help="Environment variable containing the API key",
    )
    scrape_parser.add_argument(
        "--base-url",
        default="https://openrouter.ai/api/v1",
        help="API Base URL for LLM",
    )
    scrape_parser.add_argument(
        "-max",
        "--max-tokens",
        type=int,
        default=8192,
        help="Max output tokens for the LLM filtering",
    )
    scrape_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging (Script INFO level)",
    )


def setup_process_parser(subparsers) -> None:
    """Setup the unified process subcommand."""
    process_parser = subparsers.add_parser(
        "process", help="Unified pipeline (discover + scrape)"
    )
    process_parser.add_argument(
        "start_url", help="Starting URL to discover and process"
    )
    process_parser.add_argument(
        "--start-at",
        type=int,
        default=0,
        help="Start processing from URL index (0-based)",
    )
    process_parser.add_argument(
        "-o",
        "--output-dir",
        required=True,
        help="Output directory for markdown files",
    )
    process_parser.add_argument(
        "--prompt",
        default="",
        help="Custom LLM filtering prompt (uses default if empty)",
    )
    process_parser.add_argument(
        "--timeout",
        type=int,
        default=60000,
        help="Page timeout in milliseconds",
    )
    process_parser.add_argument(
        "--wait",
        default="networkidle",
        help="When to consider page loading complete",
    )
    process_parser.add_argument(
        "--model",
        default="openrouter/google/gemini-2.0-flash-exp:free",
        help="LLM model to use for filtering",
    )
    process_parser.add_argument(
        "--api-key-env",
        default="OPENROUTER_API_KEY",
        help="Environment variable containing the API key",
    )
    process_parser.add_argument(
        "--base-url",
        default="https://openrouter.ai/api/v1",
        help="API Base URL for LLM",
    )
    process_parser.add_argument(
        "-max",
        "--max-tokens",
        type=int,
        default=8192,
        help="Max output tokens for the LLM filtering",
    )
    process_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging (Script INFO level)",
    )


async def discover_command(args) -> int:
    """Execute the discover command."""
    console.print("[cyan][INFO] Starting Link Discovery...[/cyan]")
    console.print(f"[cyan][INFO] Start URL:[/cyan] {args.start_url}")
    console.print(f"[cyan][INFO] Output File:[/cyan] {args.output_file}")

    try:
        found_urls: set[str] = extract_links(args.start_url, args.verbose)

        if found_urls:
            save_links_to_file(found_urls, args.output_file, args.verbose)
            console.print("[cyan][INFO] Discovery finished.[/cyan]")
            return 0
        else:
            console.print("[yellow][WARN] No valid URLs extracted.[/yellow]")
            return 1
    except Exception as e:
        console.print(f"[bold red][ERROR] Discovery failed: {e}[/bold red]")
        return 1


async def scrape_command(args) -> int:
    """Execute the scrape command."""
    # Same setup as original scrollscribe.py
    import logging

    from rich.logging import RichHandler

    # Configure logging (same as original)
    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        markup=True,
        show_path=False,
    )

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[rich_handler],
        force=True,
    )

    # Quiet litellm
    litellm_logger = logging.getLogger("litellm")
    litellm_logger.setLevel(logging.ERROR)

    # Check API key using ConfigError
    api_key: str | None = os.getenv(args.api_key_env)
    if not api_key:
        raise ConfigError(
            f"API key env var '{args.api_key_env}' not found!",
            config_key=args.api_key_env,
            suggested_fix=f"Set the environment variable: export {args.api_key_env}=your_api_key",
        )

    # Read URLs
    try:
        all_urls: list[str] = read_urls_from_file(args.input_file)
    except SystemExit:
        return 1

    # Validate start-at
    if args.start_at < 0:
        console.print(
            "[yellow][WARN] --start-at cannot be negative. Starting from 0.[/yellow]"
        )
        args.start_at = 0
    elif args.start_at >= len(all_urls):
        console.print(
            f"[bold red][ERROR] --start-at index {args.start_at} is out of bounds for {len(all_urls)} URLs.[/bold red]"
        )
        return 1

    urls_to_scrape: list[str] = all_urls[args.start_at :]

    if not urls_to_scrape:
        console.print(
            f"[bold red][ERROR] No URLs left to process after --start-at {args.start_at}[/bold red]"
        )
        return 1

    # Create output directory
    output_dir: Path = Path(args.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        console.print(
            f"[bold red][ERROR] Could not create output dir {output_dir}[/bold red]"
        )
        return 1

    # Setup browser config
    browser_config = get_browser_config(headless=True, verbose=args.verbose)

    # Setup LLM config and filter
    llm_config = LLMConfig(
        provider=args.model,
        api_token=api_key,
        base_url=args.base_url if args.base_url else None,
    )

    # Same default prompt as original
    default_llm_filter_instruction: str = """You are an expert Markdown converter for technical documentation websites.
    Your goal is to extract ONLY the main documentation content (text, headings, code blocks, lists, tables) from the provided HTML and format it as clean, well-structured Markdown.

    **Site-Specific Hints (Use these to help identify the main content area):**
    <site_hints>
    - For Django docs: The main content is likely within a ` class="container sidebar-right"`, specifically look for content inside the `<main>` tag or elements related to 'docs-content'. Be aware this container might also hold irrelevant sidebar info to exclude.
    Focus on the main documentation only. Ensure the final output contains only valid Markdown syntax. Do not include any raw HTML tags like <div>, <span>, etc. unless it is marked in a code block for demonstration
    </site_hints>

    - Convert any relative links (URLs beginning with "/" or just a filename/path) to absolute URLs by prefixing them with the original page's base URL (e.g., if base is https://example.com/foo/ and link is bar.html, convert to https://example.com/foo/bar.html; if link is /baz/, convert to https://example.com/baz/). Preserve existing absolute URLs.
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

    # Process URLs with performance fixes
    try:
        success_count, failed_count = await process_urls_batch(
            urls_to_scrape=urls_to_scrape,
            args=args,
            output_dir=output_dir,
            llm_content_filter=llm_content_filter,
            browser_config=browser_config,
        )

        # Return success if we processed at least some URLs
        return 0 if success_count > 0 else 1

    except KeyboardInterrupt:
        console.print("\n[bold yellow]KeyboardInterrupt caught. Exiting.[/bold yellow]")
        return 1
    except Exception as e:
        console.print(f"[bold red][CRITICAL] Unhandled error: {e}[/bold red]")
        return 1


async def process_command(args) -> int:
    """Execute the unified process command (discover + scrape)."""
    console.print("[cyan][INFO] Starting unified process (discover + scrape)...[/cyan]")

    # Step 1: Discovery
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp_file:
        temp_file_path = tmp_file.name

    try:
        # Create args for discover command
        discover_args = argparse.Namespace(
            start_url=args.start_url, output_file=temp_file_path, verbose=args.verbose
        )

        discover_result = await discover_command(discover_args)
        if discover_result != 0:
            console.print("[bold red][ERROR] Discovery phase failed[/bold red]")
            return discover_result

        # Step 2: Scrape
        # Create args for scrape command
        scrape_args = argparse.Namespace(
            input_file=temp_file_path,
            start_at=args.start_at,
            output_dir=args.output_dir,
            prompt=args.prompt,
            timeout=args.timeout,
            wait=args.wait,
            model=args.model,
            api_key_env=args.api_key_env,
            base_url=args.base_url,
            max_tokens=args.max_tokens,
            verbose=args.verbose,
        )

        scrape_result = await scrape_command(scrape_args)
        return scrape_result

    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass


def main() -> int:
    """Main CLI entry point."""
    parser = setup_base_parser()
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup subcommands
    setup_discover_parser(subparsers)
    setup_scrape_parser(subparsers)
    setup_process_parser(subparsers)

    args = parser.parse_args()

    try:
        if args.command == "discover":
            return asyncio.run(discover_command(args))
        elif args.command == "scrape":
            return asyncio.run(scrape_command(args))
        elif args.command == "process":
            return asyncio.run(process_command(args))
        else:
            parser.print_help()
            return 1
    except (ConfigError, FileIOError) as ce:
        panel_title = (
            "[bold red]CONFIG ERROR[/bold red]"
            if isinstance(ce, ConfigError)
            else "[bold red]FILE ERROR[/bold red]"
        )
        help_message = (
            ce.get_help_message() if hasattr(ce, "get_help_message") else str(ce)
        )
        console.print(
            Panel(
                help_message,
                title=panel_title,
                border_style="red",
                expand=False,
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
