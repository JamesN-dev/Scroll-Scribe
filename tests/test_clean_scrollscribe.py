#!/usr/bin/env python3
"""Test the fixed caching and clean output."""

import asyncio

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

from app.config import OptimizedConfig


async def test_clean_scrollscribe():
    """Test that we actually disable caching and get clean output."""

    # Silence all the noisy libraries
    OptimizedConfig.silence_all_libraries()

    # Get the optimized configs
    browser_config = OptimizedConfig.get_fast_browser_config()

    # Force cache to be REALLY disabled
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.DISABLED,
        disable_cache=True,         # Belt and suspenders
        bypass_cache=True,          # Extra sure
        no_cache_read=True,         # Don't read cache
        no_cache_write=True,        # Don't write cache
        verbose=False,              # No crawl4ai noise
        stream=False,
    )

    print("🧪 Testing clean ScrollScribe setup...")
    print(f"Browser mode: {getattr(browser_config, 'browser_mode', 'default')}")
    print(f"Cache mode: {crawler_config.cache_mode}")
    print(f"Verbose: {crawler_config.verbose}")

    try:
        crawler = AsyncWebCrawler(config=browser_config)

        print("\n🚀 Testing without sessions (simpler)...")

        # Test multiple URLs without sessions - just like ScrollScribe should work
        test_urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
        ]

        for i, url in enumerate(test_urls, 1):
            print(f"\n📄 Processing URL {i}/{len(test_urls)}: {url}")

            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                print(f"✅ Success! Content: {len(result.markdown)} chars")
                # Should NOT see cache messages now
            else:
                print(f"❌ Failed: {result.error_message}")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_clean_scrollscribe())
