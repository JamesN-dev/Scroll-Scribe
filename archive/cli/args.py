"""Command line arguments for ScrollScribe.

This module provides centralized argument parsing for the ScrollScribe CLI,
with support for various commands and options.
"""

import argparse

from rich_argparse import RichHelpFormatter


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with all subcommands.

    Returns:
        Configured ArgumentParser instance
    """
    # Main parser
    parser = argparse.ArgumentParser(
        description=(
            "ScrollScribe: Documentation Scraper with LLM Filtering\n\n"
            "A tool to scrape documentation websites and convert them to clean Markdown "
            "using LLM-based content filtering."
        ),
        formatter_class=RichHelpFormatter,
    )

    # Add version
    parser.add_argument(
        "-v", "--version", action="version", version="ScrollScribe 0.1.0"
    )

    # Create subcommands
    subparsers = parser.add_subparsers(
        title="commands", dest="command", help="Command to execute"
    )

    # Scrape command
    scrape_parser = subparsers.add_parser(
        "scrape",
        help="Scrape documentation from URLs",
        description="Scrape documentation from a starting URL or list of URLs and convert to Markdown.",
        formatter_class=RichHelpFormatter,
    )
    add_scrape_arguments(scrape_parser)

    # Serve command (for future MCP server)
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start MCP server for AI-powered documentation queries",
        description="Start an MCP server to serve documentation for AI-powered queries.",
        formatter_class=RichHelpFormatter,
    )
    add_serve_arguments(serve_parser)

    # List command (for future use)
    list_parser = subparsers.add_parser(
        "list",
        help="List available documentation sets",
        description="List available documentation sets that have been scraped.",
        formatter_class=RichHelpFormatter,
    )
    add_list_arguments(list_parser)

    # Delete command (for future use)
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a documentation set",
        description="Delete a documentation set that has been scraped.",
        formatter_class=RichHelpFormatter,
    )
    add_delete_arguments(delete_parser)

    return parser


def add_scrape_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the scrape command.

    Args:
        parser: Argument parser to add arguments to
    """
    # Source arguments (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--url",
        type=str,
        help="Starting URL to discover documentation links (e.g., 'https://docs.example.com/').",
    )
    source_group.add_argument(
        "--input-file",
        type=str,
        help="Path to a text file containing URLs to scrape, one per line.",
    )

    # Output directory
    parser.add_argument(
        "-o",
        "--output-dir",
        default="output/markdown",
        help="Directory to save filtered Markdown files.",
    )

    # Discovery options
    parser.add_argument(
        "--discovery",
        choices=["links", "sitemap", "auto"],
        default="links",
        help="Discovery strategy for finding documentation URLs.",
    )

    # LLM options
    parser.add_argument(
        "--model",
        default="openrouter/google/gemini-2.0-flash-exp:free",
        help="LLM model identifier for filtering.",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        default="",
        help="Inject a custom instructions prompt for the LLM content filtering.",
    )
    parser.add_argument(
        "-max",
        "--max-tokens",
        type=int,
        default=8192,
        help="Max output tokens for the LLM filtering.",
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

    # Crawling options
    parser.add_argument(
        "--start-at",
        type=int,
        default=0,
        help="Start processing at this index in the input URL list (0-based).",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=35000,
        help="Page load timeout in ms.",
    )
    parser.add_argument(
        "-w",
        "--wait",
        default="networkidle",
        choices=["load", "domcontentloaded", "networkidle"],
        help="Playwright wait_until state.",
    )

    # Misc options
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with extra logging.",
    )


def add_serve_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the serve command.

    Args:
        parser: Argument parser to add arguments to
    """
    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Start as an MCP server for Claude integration.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind the server to.",
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default="output/markdown",
        help="Directory containing the markdown documentation files.",
    )


def add_list_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the list command.

    Args:
        parser: Argument parser to add arguments to
    """
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information about each documentation set.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Base directory for documentation sets.",
    )


def add_delete_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the delete command.

    Args:
        parser: Argument parser to add arguments to
    """
    parser.add_argument(
        "name",
        type=str,
        help="Name of the documentation set to delete.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Base directory for documentation sets.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete without confirmation.",
    )


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Command line arguments to parse, defaults to sys.argv

    Returns:
        Parsed arguments
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Check if a command was provided
    if not parsed_args.command:
        parser.print_help()
        parser.exit(1, "Error: No command specified\n")

    return parsed_args
