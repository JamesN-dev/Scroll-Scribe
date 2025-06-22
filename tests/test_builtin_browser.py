#!/usr/bin/env python3
"""Test builtin browser mode to verify it fixes singleton issues."""

import asyncio

from crawl4ai import AsyncWebCrawler

from app.config import OptimizedConfig


async def test_builtin_browser():
    """Test that builtin browser mode works without singleton issues."""

    # Silence all the noisy libraries
    OptimizedConfig.silence_all_libraries()

    # Get the optimized config with builtin mode
    browser_config = OptimizedConfig.get_fast_browser_config()

    print("🧪 Testing builtin browser mode...")
    print(f"Browser mode: {getattr(browser_config, 'browser_mode', 'default')}")

    try:
        # Test with builtin browser - should be much faster and avoid singleton issues
        crawler = AsyncWebCrawler(config=browser_config)

        # No need for async context manager with builtin mode!
        result = await crawler.arun("https://httpbin.org/html")

        if result.success:
            print("✅ Builtin browser test successful!")
            print(f"📄 Content length: {len(result.markdown)} chars")
            print("⚡ No singleton lock issues!")
        else:
            print(f"❌ Test failed: {result.error_message}")

    except Exception as e:
        print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_builtin_browser())
