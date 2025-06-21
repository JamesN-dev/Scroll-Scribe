"""Main CLI interface for ScrollScribe.

This module provides the main command-line interface that ties together
the discovery and processing modules to implement the core scrollscribe functionality.
"""

import asyncio
import sys
from pathlib import Path

from ..cli.args import parse_args
from ..discovery.links import extract_links
from ..processing.markdown import MarkdownProcessor
from ..utils.exceptions import ScrollScribeError
from ..utils.logging import get_logger, log_error, log_info, setup_logging


async def scrape_command(args) -> int:
    """Execute the scrape command: discover URLs and process them to markdown.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Setup logging
        setup_logging(verbose=args.verbose)
        get_logger()

        # Handle different input sources
        if hasattr(args, 'url') and args.url:
            log_info(f"Starting ScrollScribe scrape from: {args.url}")

            # Step 1: Discover URLs
            log_info("Phase 1: Discovering links...")
            try:
                discovered_urls = extract_links(args.url, verbose=args.verbose)
                log_info(f"Discovered {len(discovered_urls)} unique URLs")
            except Exception as e:
                log_error(f"Failed to discover URLs from {args.url}: {e}")
                return 1

            if not discovered_urls:
                log_error("No URLs discovered. Cannot proceed.")
                return 1

            # Convert to list and apply start_at if needed
            urls_list = sorted(list(discovered_urls))

        elif hasattr(args, 'input_file') and args.input_file:
            log_info(f"Reading URLs from file: {args.input_file}")

            # Read URLs from file
            try:
                with open(args.input_file, encoding='utf-8') as f:
                    urls_list = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                log_info(f"Read {len(urls_list)} URLs from file")
            except Exception as e:
                log_error(f"Failed to read URLs from file {args.input_file}: {e}")
                return 1
        else:
            log_error("Either --url or --input-file must be specified")
            return 1

        log_info(f"Output directory: {args.output_dir}")

        # Apply start_at if needed
        if args.start_at > 0:
            if args.start_at >= len(urls_list):
                log_error(f"--start-at {args.start_at} exceeds URL count {len(urls_list)}")
                return 1
            urls_list = urls_list[args.start_at:]
            log_info(f"Starting from URL index {args.start_at}, processing {len(urls_list)} URLs")

        # Step 2: Process URLs to markdown
        log_info("Phase 2: Processing URLs to markdown...")
        try:
            processor = MarkdownProcessor(
                model=args.model,
                api_key_env=args.api_key_env,
                base_url=args.base_url,
                max_tokens=args.max_tokens,
                timeout=args.timeout,
                wait_until=args.wait,
                custom_prompt=args.prompt,
                verbose=args.verbose
            )

            success_count, failed_count = await processor.process_urls(
                urls_list,
                output_dir=Path(args.output_dir),
                start_at=0  # We already sliced the list above
            )

            log_info(f"Processing complete. Success: {success_count}, Failed: {failed_count}")
            return 0 if success_count > 0 else 1

        except Exception as e:
            log_error(f"Failed to process URLs to markdown: {e}")
            return 1

    except ScrollScribeError as e:
        log_error(f"ScrollScribe error: {e}")
        return 1
    except KeyboardInterrupt:
        log_info("Interrupted by user")
        return 1
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return 1


async def main() -> int:
    """Main entry point for ScrollScribe CLI."""
    try:
        args = parse_args()

        # Route to appropriate command handler
        if args.command == "scrape":
            return await scrape_command(args)
        elif args.command == "serve":
            log_error("Serve command not yet implemented")
            return 1
        elif args.command == "list":
            log_error("List command not yet implemented")
            return 1
        elif args.command == "delete":
            log_error("Delete command not yet implemented")
            return 1
        else:
            log_error(f"Unknown command: {args.command}")
            return 1

    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
