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
from rich.panel import Panel

from .config import get_browser_config
from .discovery import extract_links, save_links_to_file
from .processing import process_urls_batch, read_urls_from_file
from .utils.exceptions import ConfigError, FileIOError
from .utils.logging import CleanConsole, set_logging_verbosity

# Load environment variables from .env file
load_dotenv()

# Silence noisy libraries ASAP
silence_noisy_libraries()

console = CleanConsole()


def setup_base_parser() -> argparse.ArgumentParser:
    """Create the base argument parser with beautiful Rich formatting."""
    parser = argparse.ArgumentParser(
        prog="scrollscribe",
        description="🚀 ScrollScribe V2 - AI-powered documentation scraper\n\nTransform any documentation website into clean, filtered Markdown files using advanced LLM processing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\nExamples:\n\n  # Discover URLs from documentation site\n  scrollscribe discover https://docs.python.org/3/ -o python_urls.txt\n",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging for troubleshooting and verbose output.",
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
        default="openrouter/google/mistralai/codestral-2501",
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
        "--session",
        action="store_true",
        help="Enable browser session reuse (sets session_id to 'scrollscribe_session')",
    )
    scrape_parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="Custom session_id for browser session reuse (overrides --session)",
    )
    scrape_parser.add_argument(
        "--fast",
        action="store_true",
        help="Enable fast HTML→Markdown mode (50-200 docs/min, no LLM filtering)",
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
        default="openrouter/mistralai/codestral-2501",
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
        "--session",
        action="store_true",
        help="Enable browser session reuse (sets session_id to 'scrollscribe_session')",
    )
    process_parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="Custom session_id for browser session reuse (overrides --session)",
    )
    process_parser.add_argument(
        "--fast",
        action="store_true",
        help="Enable fast HTML→Markdown mode (50-200 docs/min, no LLM filtering)",
    )
    process_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging (Script INFO level)",
    )


async def discover_command(args) -> int:
    """Execute the discover command with CleanConsole."""
    from .utils.logging import CleanConsole

    console = CleanConsole()
    console.print_info(f"Starting Link Discovery from: {args.start_url}")
    console.print_info(f"Output file: {args.output_file}")

    try:
        found_urls: set[str] = extract_links(args.start_url, args.verbose)

        if found_urls:
            save_links_to_file(found_urls, args.output_file, args.verbose)
            console.print_info(f"Discovery finished. Found {len(found_urls)} URLs.")
            return 0
        else:
            console.print_warning("No valid URLs extracted.")
            return 1
    except Exception as e:
        console.print_error(f"Discovery failed: {e}")
        return 1


async def scrape_command(args) -> int:
    """Execute the scrape command with proper logging integration."""

    # Use YOUR logging system instead of setting up own RichHandler
    from .utils.exceptions import ConfigError, FileIOError
    from .utils.logging import CleanConsole

    console = CleanConsole()

    # Fast mode doesn't need API key
    if not args.fast:
        # Check API key for LLM mode
        api_key: str | None = os.getenv(args.api_key_env)
        if not api_key:
            raise ConfigError(
                f"API key env var '{args.api_key_env}' not found!",
                config_key=args.api_key_env,
                suggested_fix=f"Set {args.api_key_env}=your_api_key in your .env file or environment.",
            )
    # Internal logging removed to avoid duplicate with user-facing message in process_command

    try:
        # Read URLs using proper exception handling
        all_urls: list[str] = read_urls_from_file(args.input_file)
    except FileIOError as e:
        console.print_error(f"File error: {str(e)}")
        return 1
    except Exception as e:
        console.print_error(f"Unexpected error reading URLs: {e}")
        return 1

    # Validate start-at
    if args.start_at < 0:
        console.print_warning("--start-at cannot be negative. Starting from 0.")
        args.start_at = 0
    elif args.start_at >= len(all_urls):
        console.print_error(
            f"--start-at index {args.start_at} is out of bounds for {len(all_urls)} URLs."
        )
        return 1

    urls_to_scrape: list[str] = all_urls[args.start_at :]

    if not urls_to_scrape:
        console.print_error(f"No URLs left to process after --start-at {args.start_at}")
        return 1

    # Create output directory
    output_dir: Path = Path(args.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        console.print_error(f"Could not create output dir {output_dir}")
        return 1

    set_logging_verbosity(getattr(args, "debug", False))

    browser_config = get_browser_config(
        headless=True, verbose=getattr(args, "debug", False)
    )

    # Check if fast mode is enabled
    if args.fast:
        console.print_info("🚀 Fast mode enabled - using crawl4ai only (no LLM)")
        from .fast_processing import process_urls_fast

        try:
            success_count, failed_count = await process_urls_fast(
                urls_to_scrape=urls_to_scrape,
                args=args,
                output_dir=output_dir,
                browser_config=browser_config,
            )

            # Return success if we processed at least some URLs
            return 0 if success_count > 0 else 1

        except KeyboardInterrupt:
            console.print_warning("KeyboardInterrupt caught in fast mode. Exiting.")
            return 1
        except Exception as e:
            console.print_error(f"Fast mode error: {e}")
            return 1

    # Regular LLM mode (existing code)
    api_key = os.getenv(args.api_key_env)  # We already checked this exists above

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
        verbose=False,  # Always disable to reduce noise
    )

    # Process URLs with the fixed processing function
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
        console.print_warning("KeyboardInterrupt caught. Exiting.")
        return 1
    except Exception as e:
        console.print_error(f"Unhandled error: {e}")
        return 1


async def process_command(args) -> int:
    """Execute the unified process command (discover + scrape)."""
    console.print_info("Starting unified process (discover + scrape)...")

    try:
        # Step 1: Discovery
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as tmp_file:
            temp_file_path = tmp_file.name

        try:
            # Create args for discover command
            discover_args = argparse.Namespace(
                start_url=args.start_url,
                output_file=temp_file_path,
                verbose=args.verbose,
            )

            discover_result = await discover_command(discover_args)
            if discover_result != 0:
                console.print_error("Discovery phase failed")
                return discover_result

            # Step 2: Scrape
            # Check API key before scraping (only needed for LLM mode)
            if not args.fast:
                api_key: str | None = os.getenv(args.api_key_env)
                if not api_key:
                    raise ConfigError(
                        f"API key env var '{args.api_key_env}' not found!",
                        config_key=args.api_key_env,
                        suggested_fix=f"Set {args.api_key_env}=your_api_key in your .env file or environment.",
                    )
                console.print_info(
                    f"🔑 Found API key in env var: [bold lime]{args.api_key_env}[/bold lime]"
                )
            else:
                console.print_info("⚡ Fast mode enabled - no API key needed")
            # Only log once, not here and in scrape_command

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
                fast=args.fast,  # Pass through the fast flag
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

    except ConfigError as e:
        console.print_error(e.get_help_message())
        return 1


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
        # Only call get_help_message if it exists and is callable
        if hasattr(ce, "get_help_message") and callable(
            getattr(ce, "get_help_message", None)
        ):
            help_message = ce.get_help_message()  # pyright: ignore[reportAttributeAccessIssue]
        else:
            help_message = str(ce)
        console.console.print(
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
