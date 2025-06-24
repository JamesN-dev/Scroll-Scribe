"""ScrollScribe V2 Command Line Interface.

Provides a unified CLI for AI-powered documentation scraping and conversion.
Supports both LLM-based high-quality filtering and fast HTML-to-Markdown conversion.

Commands:
    discover: Extract internal documentation URLs from a starting website
    scrape: Convert a list of URLs to filtered Markdown files using LLM or fast mode
    process: Unified pipeline that combines discovery and scraping in one command

Example Usage:
    # Discover and process documentation in one command
    scrollscribe process https://docs.example.com/ -o output/

    # Fast mode for high-volume processing (no LLM, no API costs)
    scrollscribe process https://docs.example.com/ -o output/ --fast

    # Two-step process with custom LLM filtering
    scrollscribe discover https://docs.example.com/ -o urls.txt
    scrollscribe scrape urls.txt -o output/ --model gpt-4

Environment Variables:
    DEFAULT_API_KEY_ENV: API key for LLM processing (required for non-fast modes)
    LITELLM_LOG: Set to ERROR to reduce library logging noise
"""

import argparse
import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import Annotated

import typer
from crawl4ai import LLMConfig
from crawl4ai.content_filter_strategy import LLMContentFilter
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Assume these are your project's modules.
# If the structure is different, you may need to adjust the import paths.
from .config import get_browser_config
from .constants import (
    DEFAULT_API_KEY_ENV,
    DEFAULT_BASE_URL,
    DEFAULT_LLM_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT_MS,
)
from .fast_discovery import extract_links_fast, save_links_to_file
from .fast_processing import process_urls_fast
from .processing import process_urls_batch, read_urls_from_file
from .utils.exceptions import ConfigError, FileIOError
from .utils.logging import CleanConsole, set_logging_verbosity

# Load environment variables from .env file
load_dotenv()

# --- Globals & App Initialization ---
console = CleanConsole()
rich_console = Console()

app = typer.Typer(
    name="scribe",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=True,
    help="""
:books: [bold #b8bb26]ScrollScribe V2[/bold #b8bb26] — AI-powered documentation scraper.

[#458588]Transform any documentation website into clean, filtered Markdown files.[/]

[bold dim]──────────────────────────────────────────────────────────────────[/bold dim]

[bold #fabd2f]Quick Start:[/bold #fabd2f]

  [#8ec07c]➤ Process an entire documentation site:[/]
    [dim]$ scribe process https://docs.python.org/3/ -o python-docs/[/dim]

  [#8ec07c]➤ Use fast mode for large sites (no LLM costs):[/]
    [dim]$ scribe process https://docs.django.com/ -o django-docs/ --fast[/dim]

[bold dim]──────────────────────────────────────────────────────────────────[/bold dim]

[bold #83a598]Run a command with --help for more details.[/]
(e.g., [dim]scribe scrape --help[/dim])
    """,
    epilog="Made with :heart: by the ScrollScribe team.",
)


# --- Helper Functions ---
def print_summary_report(summary: dict):
    """Prints a beautiful, dynamic summary report table after a job completes."""
    if not summary:
        return

    success_count = len(summary.get("successful_urls", []))
    failed_items = summary.get("failed_urls", [])
    failed_count = len(failed_items)
    total_processed = success_count + failed_count

    if total_processed == 0:
        return

    summary_table = Table(
        title="[bold #b8bb26]Scrape Job Summary[/bold #b8bb26]",
        show_header=True,
        header_style="bold #83a598",
        border_style="#458588",
    )
    summary_table.add_column("Status", style="dim", width=20)
    summary_table.add_column("Count", justify="right")

    summary_table.add_row(
        ":white_check_mark: [green]Successful[/green]", str(success_count)
    )
    summary_table.add_row(":x: [red]Failed[/red]", str(failed_count))
    summary_table.add_row(
        ":hourglass_done: [cyan]Total Processed[/cyan]", str(total_processed)
    )

    rich_console.print("\n")
    rich_console.print(summary_table)

    if failed_items:
        failed_text = "\n".join(
            f"• [dim]{url}[/dim]\n  [red]Reason:[/red] {error}"
            for url, error in failed_items
        )
        failed_panel = Panel(
            failed_text,
            title="[bold #fe8019]Failed URLs[/bold #fe8019]",
            border_style="#fe8019",
            title_align="left",
        )
        rich_console.print(failed_panel)


# --- Typer Commands ---


@app.callback(invoke_without_command=True)
def global_options(
    ctx: typer.Context,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable debug logging for deep troubleshooting.",
            rich_help_panel="General Options",
        ),
    ] = False,
):
    """
    :books: [bold #b8bb26]ScrollScribe V2[/bold #b8bb26] — AI-powered documentation scraper.
    """
    if debug:
        set_logging_verbosity(verbose=True)

    # Pass debug state to subcommands via the context object
    ctx.obj = {"debug": debug}

    # If no command is specified, show the main help text.
    if ctx.invoked_subcommand is None:
        rich_console.print(ctx.get_help())


@app.command()
def discover(
    start_url: Annotated[
        str, typer.Argument(help="The starting URL to crawl for documentation links.")
    ],
    output_file: Annotated[
        str | None,
        typer.Option(
            "-o",
            "--output-file",
            help="Output file to save discovered URLs. Defaults to 'urls.txt'.",
        ),
    ] = "urls.txt",
    verbose: Annotated[
        bool,
        typer.Option(
            "-v", "--verbose", help="Enable verbose logging for the discovery process."
        ),
    ] = False,
):
    """
    :mag: [bold #fabd2f]Discover Mode[/bold #fabd2f]

    [#458588]Chart the territory. Scans a starting URL to map out all internal links, creating a clean list for targeted scraping.[/]

    [bold dim]──────────────────────────────────────────────────────────────────[/bold dim]

    [bold #b8bb26]Common Use Cases:[/bold #b8bb26]
      • Preview the scope of a full process run.
      • Build a custom URL list for focused scraping.
      • Isolate specific sections of a large documentation site.

    [bold #b8bb26]Examples:[/bold #b8bb26]
      [#8ec07c]➤ Discover and save to a custom file:[/]
        [dim]$ scribe discover https://docs.django.com/ -o django-urls.txt[/dim]

      [#8ec07c]➤ Run with verbose output for debugging:[/]
        [dim]$ scribe discover https://fastapi.tiangolo.com/ -v[/dim]

    [bold #83a598]Pro Tip:[/bold #83a598] Use the generated file as input for the '[cyan]scrape[/cyan]' command.
    """
    # This logic matches your original file exactly.
    if output_file is None:
        output_file = "urls.txt"

    args = argparse.Namespace(
        start_url=start_url, output_file=output_file, verbose=verbose
    )
    result = asyncio.run(discover_command(args))
    raise typer.Exit(result)


@app.command()
def scrape(
    ctx: typer.Context,
    # Arguments and Options using modern Typer syntax for rich help text
    input: Annotated[
        str, typer.Argument(help="URL to scrape OR text file containing URLs")
    ],
    output_dir: Annotated[
        str,
        typer.Option(
            ...,
            "-o",
            "--output-dir",
            help="Output directory for markdown files",
            rich_help_panel="Core Options",
        ),
    ],
    start_at: Annotated[
        int,
        typer.Option(
            help="Start processing from URL index (0-based)",
            rich_help_panel="Processing Options",
        ),
    ] = 0,
    fast: Annotated[
        bool,
        typer.Option(
            "--fast/--no-fast",
            help="Enable fast HTML→Markdown mode (no LLM filtering).",
            rich_help_panel="Processing Options",
        ),
    ] = False,
    prompt: Annotated[
        str,
        typer.Option(
            help="Custom LLM filtering prompt (uses default if empty).",
            rich_help_panel="LLM Configuration",
        ),
    ] = "",
    model: Annotated[
        str,
        typer.Option(
            "--model",
            help="LLM model to use for filtering.",
            rich_help_panel="LLM Configuration",
        ),
    ] = DEFAULT_LLM_MODEL,
    api_key_env: Annotated[
        str,
        typer.Option(
            "--api-key-env",
            help="Environment variable containing the API key.",
            rich_help_panel="LLM Configuration",
        ),
    ] = DEFAULT_API_KEY_ENV,
    base_url: Annotated[
        str,
        typer.Option(
            "--base-url",
            help="API Base URL for LLM.",
            rich_help_panel="LLM Configuration",
        ),
    ] = DEFAULT_BASE_URL,
    max_tokens: Annotated[
        int,
        typer.Option(
            "-max",
            "--max-tokens",
            help="Max output tokens for the LLM filtering.",
            rich_help_panel="LLM Configuration",
        ),
    ] = DEFAULT_MAX_TOKENS,
    timeout: Annotated[
        int,
        typer.Option(
            help="Page load timeout in milliseconds.", rich_help_panel="Browser Control"
        ),
    ] = DEFAULT_TIMEOUT_MS,
    wait: Annotated[
        str,
        typer.Option(
            help="When to consider page loading complete.",
            rich_help_panel="Browser Control",
        ),
    ] = "networkidle",
    session: Annotated[
        bool,
        typer.Option(
            "--session/--no-session",
            help="Enable browser session reuse.",
            rich_help_panel="Browser Control",
        ),
    ] = False,
    session_id: Annotated[
        str | None,
        typer.Option(
            "--session-id",
            help="Custom session_id for browser reuse (overrides --session).",
            rich_help_panel="Browser Control",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "-v",
            "--verbose",
            help="Enable verbose logging (Script INFO level).",
            rich_help_panel="General Options",
        ),
    ] = False,
):
    """
    :page_facing_up: [bold #fabd2f]Scrape Mode[/bold #fabd2f]

    [#458588]The workhorse. Converts a single URL or a file of URLs into clean, structured Markdown.[/]

    [bold dim]──────────────────────────────────────────────────────────────────[/bold dim]

    [bold #b8bb26]Mode Comparison:[/bold #b8bb26]
    [#83a598]
      Feature         | LLM-Powered (Default)      | Fast Mode (--fast)
    ────────────────┼────────────────────────────┼──────────────────────────
      Speed           | ~9 sec/URL                 | [green]~150 docs/min[/green]
      Quality         | [green]Superior, Intelligent[/green]      | Good, Raw Conversion
      Cost            | API Token Usage            | [green]Free[/green]
      Requires        | API Key                    | None
    [/]
    [bold dim]──────────────────────────────────────────────────────────────────[/bold dim]

    [bold #b8bb26]Examples:[/bold #b8bb26]
      [#8ec07c]➤ Scrape a single page with LLM filtering:[/]
        [dim]$ scribe scrape https://docs.python.org/3/library/os.html -o output/[/dim]

      [#8ec07c]➤ Scrape a list of URLs using fast mode:[/]
        [dim]$ scribe scrape urls.txt -o output/ --fast[/dim]

      [#8ec07c]➤ Resume a large job from a specific line:[/]
        [dim]$ scribe scrape urls.txt -o output/ --start-at 150[/dim]

    [bold #fe8019]Heads Up:[/bold #fe8019] LLM mode requires the [cyan]DEFAULT_API_KEY_ENV[/] environment variable to be set.
    """
    # This logic matches your original file exactly.
    debug = ctx.obj.get("debug", False)

    # Encapsulate the logic to avoid repetition and handle summary report
    def run_scrape(input_file_path):
        args = argparse.Namespace(
            input_file=input_file_path,
            output_dir=output_dir,
            start_at=start_at,
            prompt=prompt,
            timeout=timeout,
            wait=wait,
            model=model,
            api_key_env=api_key_env,
            base_url=base_url,
            max_tokens=max_tokens,
            session=session,
            session_id=session_id,
            fast=fast,
            verbose=verbose,
            debug=debug,
        )
        summary = asyncio.run(scrape_command(args))
        print_summary_report(summary)

        failed_count = len(summary.get("failed_urls", []))
        if failed_count > 0:
            raise typer.Exit(code=1)
        raise typer.Exit(code=0)

    if input.startswith(("http://", "https://")):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as tmp_file:
            tmp_file.write(input + "\n")
            temp_file_path = tmp_file.name
        try:
            run_scrape(temp_file_path)
        finally:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
    else:
        run_scrape(input)


@app.command()
def process(
    ctx: typer.Context,
    # Arguments and Options using modern Typer syntax
    start_url: Annotated[
        str, typer.Argument(help="Starting URL to discover and process")
    ],
    output_dir: Annotated[
        str,
        typer.Option(
            ...,
            "-o",
            "--output-dir",
            help="Output directory for markdown files",
            rich_help_panel="Core Options",
        ),
    ],
    start_at: Annotated[
        int,
        typer.Option(
            help="Start processing from URL index (0-based)",
            rich_help_panel="Processing Options",
        ),
    ] = 0,
    fast: Annotated[
        bool,
        typer.Option(
            "--fast/--no-fast",
            help="Enable fast HTML→Markdown mode (no LLM filtering).",
            rich_help_panel="Processing Options",
        ),
    ] = False,
    prompt: Annotated[
        str,
        typer.Option(
            help="Custom LLM filtering prompt (uses default if empty).",
            rich_help_panel="LLM Configuration",
        ),
    ] = "",
    model: Annotated[
        str,
        typer.Option(
            "--model",
            help="LLM model to use for filtering.",
            rich_help_panel="LLM Configuration",
        ),
    ] = DEFAULT_LLM_MODEL,
    api_key_env: Annotated[
        str,
        typer.Option(
            "--api-key-env",
            help="Environment variable containing the API key.",
            rich_help_panel="LLM Configuration",
        ),
    ] = DEFAULT_API_KEY_ENV,
    base_url: Annotated[
        str,
        typer.Option(
            "--base-url",
            help="API Base URL for LLM.",
            rich_help_panel="LLM Configuration",
        ),
    ] = DEFAULT_BASE_URL,
    max_tokens: Annotated[
        int,
        typer.Option(
            "-max",
            "--max-tokens",
            help="Max output tokens for the LLM filtering.",
            rich_help_panel="LLM Configuration",
        ),
    ] = DEFAULT_MAX_TOKENS,
    timeout: Annotated[
        int,
        typer.Option(
            help="Page load timeout in milliseconds.", rich_help_panel="Browser Control"
        ),
    ] = DEFAULT_TIMEOUT_MS,
    wait: Annotated[
        str,
        typer.Option(
            help="When to consider page loading complete.",
            rich_help_panel="Browser Control",
        ),
    ] = "networkidle",
    session: Annotated[
        bool,
        typer.Option(
            "--session/--no-session",
            help="Enable browser session reuse.",
            rich_help_panel="Browser Control",
        ),
    ] = False,
    session_id: Annotated[
        str | None,
        typer.Option(
            "--session-id",
            help="Custom session_id for browser reuse (overrides --session).",
            rich_help_panel="Browser Control",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "-v",
            "--verbose",
            help="Enable verbose logging (Script INFO level).",
            rich_help_panel="General Options",
        ),
    ] = False,
):
    """
    :rocket: [bold #fabd2f]Process Mode (All-in-One)[/bold #fabd2f]

    [#458588]The "easy button". Combines discovery and scraping into a seamless, end-to-end pipeline.[/]

    [bold dim]──────────────────────────────────────────────────────────────────[/bold dim]

    [bold #b8bb26]Workflow:[/bold #b8bb26]
      1. Scans your [cyan]start_url[/] to find all internal links.
      2. Feeds the discovered links directly into the scraper.
      3. Saves the resulting Markdown files to your [cyan]output_dir[/].

    [bold #b8bb26]Examples:[/bold #b8bb26]
      [#8ec07c]➤ Process an entire site with a custom LLM:[/]
        [dim]$ scribe process https://fastapi.tiangolo.com/ -o api-docs/ --model gpt-4[/dim]

      [#8ec07c]➤ Quickly archive a whole site in Markdown:[/]
        [dim]$ scribe process https://docs.djangoproject.com/ -o django-docs/ --fast[/dim]

    [bold #83a598]Pro Tip:[/bold #83a598] This is the recommended command for most use cases.
    """
    # This logic matches your original file exactly.
    debug = ctx.obj.get("debug", False)
    args = argparse.Namespace(
        start_url=start_url,
        output_dir=output_dir,
        start_at=start_at,
        prompt=prompt,
        timeout=timeout,
        wait=wait,
        model=model,
        api_key_env=api_key_env,
        base_url=base_url,
        max_tokens=max_tokens,
        session=session,
        session_id=session_id,
        fast=fast,
        verbose=verbose,
        debug=debug,
    )
    summary = asyncio.run(process_command(args))
    print_summary_report(summary)

    # Determine exit code based on failures
    failed_count = len(summary.get("failed_urls", []))
    if failed_count > 0:
        raise typer.Exit(code=1)
    raise typer.Exit(code=0)


# --- Core Logic Functions ---


async def discover_command(args: argparse.Namespace) -> int:
    """Execute the URL discovery command."""
    # This function is identical to your original.
    console = CleanConsole()
    set_logging_verbosity(verbose=args.verbose)
    console.print_phase("DISCOVERY", f"Finding internal links from {args.start_url}")
    console.print_info(f"Output file: {args.output_file}")
    try:
        found_urls: set[str] = await extract_links_fast(args.start_url, args.verbose)
        if found_urls:
            save_links_to_file(found_urls, args.output_file, args.verbose)
            console.print_success(f"Discovery finished. Found {len(found_urls)} URLs.")
            return 0
        else:
            console.print_warning("No valid URLs extracted.")
            return 1
    except Exception as e:
        console.print_error(f"Discovery failed: {e}")
        return 1


async def scrape_command(args: argparse.Namespace) -> dict:
    """Execute the URL scraping and conversion command."""
    # This function is identical to your original.
    console = CleanConsole()
    is_debug = getattr(args, "debug", False)
    set_logging_verbosity(verbose=args.verbose or is_debug)

    if not args.fast:
        api_key: str | None = os.getenv(args.api_key_env)
        if not api_key:
            raise ConfigError(
                f"API key env var '{args.api_key_env}' not found!",
                config_key=args.api_key_env,
                suggested_fix=f"Set {args.api_key_env}=your_api_key in your .env or environment.",
            )

    try:
        urls_to_scrape = read_urls_from_file(args.input_file)
    except FileIOError as e:
        console.print_error(f"File error: {str(e)}")
        return {"successful_urls": [], "failed_urls": [("file read", str(e))]}

    if args.start_at < 0:
        args.start_at = 0
    elif args.start_at >= len(urls_to_scrape):
        console.print_error(
            f"--start-at index {args.start_at} is out of bounds for {len(urls_to_scrape)} URLs."
        )
        return {
            "successful_urls": [],
            "failed_urls": [("config", "start_at out of bounds")],
        }

    urls_to_process = urls_to_scrape[args.start_at :]
    if not urls_to_process:
        console.print_error(f"No URLs left to process after --start-at {args.start_at}")
        return {"successful_urls": [], "failed_urls": []}

    output_dir = Path(args.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        console.print_error(f"Could not create output dir {output_dir}")
        return {"successful_urls": [], "failed_urls": [("file system", str(e))]}

    browser_config = get_browser_config(headless=True, verbose=is_debug)

    if args.fast:
        summary = await process_urls_fast(
            urls_to_scrape=urls_to_process,
            args=args,
            output_dir=output_dir,
            browser_config=browser_config,
        )
    else:
        llm_config = LLMConfig(
            provider=args.model,
            api_token=os.getenv(args.api_key_env),
            base_url=args.base_url if args.base_url else None,
        )
        default_llm_filter_instruction = """You are an expert Markdown converter for technical documentation websites. Your goal is to extract ONLY the main documentation content (text, headings, code blocks, lists, tables) from the provided HTML and format it as clean, well-structured Markdown. Focus on the main documentation only. Ensure the final output contains only valid Markdown syntax. Do not include any raw HTML tags like <div>, <span>, etc. unless it is marked in a code block for demonstration. Convert any relative links to absolute URLs."""
        llm_filter_instruction = args.prompt.strip() or default_llm_filter_instruction
        llm_content_filter = LLMContentFilter(
            llm_config=llm_config,
            instruction=llm_filter_instruction,
            chunk_token_threshold=args.max_tokens,
            verbose=False,
        )
        summary = await process_urls_batch(
            urls_to_scrape=urls_to_process,
            args=args,
            output_dir=output_dir,
            llm_content_filter=llm_content_filter,
            browser_config=browser_config,
        )
    return summary


async def process_command(args: argparse.Namespace) -> dict:
    """Execute the unified processing pipeline (discovery + scraping)."""
    set_logging_verbosity(verbose=args.verbose)
    console.print_phase("UNIFIED PROCESSING", "Discovery + Scraping pipeline")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp_file:
        temp_file_path = tmp_file.name

    try:
        discover_args = argparse.Namespace(
            start_url=args.start_url,
            output_file=temp_file_path,
            verbose=args.verbose,
        )
        discover_result = await discover_command(discover_args)
        if discover_result != 0:
            console.print_error("Discovery phase failed")
            return {
                "successful_urls": [],
                "failed_urls": [("discovery", "Failed to find any URLs")],
            }

        if not args.fast:
            api_key: str | None = os.getenv(args.api_key_env)
            if not api_key:
                raise ConfigError(f"API key env var '{args.api_key_env}' not found!")
            console.print_info(
                f"🔑 Found API key in env var: [bold lime]{args.api_key_env}[/bold lime]"
            )
        else:
            console.print_info("⚡ Fast mode enabled - no API key needed")

        scrape_args = argparse.Namespace(**vars(args))
        scrape_args.input_file = temp_file_path

        summary = await scrape_command(scrape_args)
        return summary
    finally:
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass


def main():
    """Main entry point for the ScrollScribe CLI application."""
    try:
        app()
    except typer.Exit:
        pass
    except Exception as e:
        console.print_error(f"An unexpected application error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
