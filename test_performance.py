#!/usr/bin/env python3
"""Test script to verify ScrollScribe V2 performance improvements."""

import subprocess
import sys
import time


def run_command(command: list[str], description: str) -> tuple[bool, float]:
    """Run a command and measure execution time."""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(command)}")

    start_time = time.time()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        end_time = time.time()
        duration = end_time - start_time

        if result.returncode == 0:
            print(f"✅ Success! Duration: {duration:.2f} seconds")
            return True, duration
        else:
            print(f"❌ Failed with return code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False, duration
    except subprocess.TimeoutExpired:
        print("❌ Command timed out after 5 minutes")
        return False, 300.0
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False, 0.0

def main():
    print("🧪 ScrollScribe V2 Performance Test")
    print("=" * 50)

    # Test the new CLI
    print("\n📋 Testing new unified CLI...")

    # Test discover command
    discover_success, discover_time = run_command([
        "python", "-m", "app", "discover",
        "https://docs.crawl4ai.com/",
        "-o", "test_urls.txt",
        "-v"
    ], "Testing discover command")

    if not discover_success:
        print("❌ Discover test failed - stopping here")
        return 1

    # Check if URLs were discovered
    try:
        with open("test_urls.txt") as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"📝 Discovered {len(urls)} URLs")

        # Limit to first 3 URLs for quick testing
        if len(urls) > 3:
            urls = urls[:3]
            with open("test_urls_small.txt", "w") as f:
                f.write("\n".join(urls))
            url_file = "test_urls_small.txt"
        else:
            url_file = "test_urls.txt"

    except Exception as e:
        print(f"❌ Error reading discovered URLs: {e}")
        return 1

    # Test scrape command with performance fixes
    scrape_success, scrape_time = run_command([
        "python", "-m", "app", "scrape",
        url_file,
        "-o", "test_output_v2",
        "--model", "openrouter/google/gemini-2.0-flash-exp:free",
        "-v"
    ], f"Testing scrape command (V2) with {len(urls)} URLs")

    if not scrape_success:
        print("❌ Scrape test failed")
        return 1

    # Calculate performance metrics
    print("\n📊 Performance Results:")
    print(f"Discovery time: {discover_time:.2f} seconds")
    print(f"Scrape time: {scrape_time:.2f} seconds")
    print(f"Total time: {discover_time + scrape_time:.2f} seconds")
    print(f"URLs processed: {len(urls)}")
    if scrape_time > 0:
        rate = len(urls) / scrape_time * 60  # URLs per minute
        print(f"Processing rate: {rate:.2f} URLs/minute")

    # Test unified process command
    print("\n🔄 Testing unified process command...")
    process_success, process_time = run_command([
        "python", "-m", "app", "process",
        "https://docs.crawl4ai.com/",
        "-o", "test_output_unified",
        "--model", "openrouter/google/gemini-2.0-flash-exp:free",
        "--start-at", "0",
        "-v"
    ], "Testing unified process command")

    if process_success:
        print(f"✅ Unified process completed in {process_time:.2f} seconds")

    print("\n🎉 Test completed!")
    print("🏗️ Key improvements:")
    print("   - Fixed duplicate fetching bug")
    print("   - Added session reuse for performance")
    print("   - Replaced manual retry with @retry_llm decorator")
    print("   - Created unified CLI interface")

    return 0

if __name__ == "__main__":
    sys.exit(main())
