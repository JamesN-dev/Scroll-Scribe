#!/usr/bin/env python3
"""Test if the original functionality still works after my changes."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_original_functionality():
    """Test that existing functionality still works."""

    print("🔍 Testing original ScrollScribe functionality...")

    try:
        # Test 1: Import core modules
        print("\n1️⃣ Testing imports...")
        from app.config import get_browser_config
        from app.utils.logging import get_logger, setup_quiet_environment
        print("✅ Core imports successful")

        # Test 2: Setup environment
        print("\n2️⃣ Testing environment setup...")
        setup_quiet_environment()
        get_logger("test")
        print("✅ Logging setup successful")

        # Test 3: Browser config
        print("\n3️⃣ Testing browser config...")
        browser_config = get_browser_config()
        print(f"✅ Browser config: mode={getattr(browser_config, 'browser_mode', 'default')}")

        # Test 4: Minimal crawl with crawl4ai
        print("\n4️⃣ Testing crawl4ai...")
        from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

        test_config = CrawlerRunConfig(
            cache_mode=CacheMode.DISABLED,
            verbose=False,
            wait_until="load",
            page_timeout=10000
        )

        crawler = AsyncWebCrawler(config=browser_config)
        result = await crawler.arun("https://httpbin.org/html", config=test_config)

        if result.success:
            print(f"✅ crawl4ai working: {len(result.html)} chars")
        else:
            print(f"❌ crawl4ai failed: {result.error_message}")

        # Test 5: Check what I broke
        print("\n5️⃣ Checking for conflicts...")

        # Are the cache flags real crawl4ai flags?
        test_flags = ['disable_cache', 'bypass_cache', 'no_cache_read', 'no_cache_write']
        for flag in test_flags:
            if hasattr(test_config, flag):
                print(f"✅ {flag} is a real crawl4ai flag")
            else:
                print(f"❌ {flag} is NOT a real crawl4ai flag - I made it up!")

        print("\n🎯 Original functionality test complete!")

    except Exception as e:
        print(f"❌ BROKEN: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_original_functionality())
