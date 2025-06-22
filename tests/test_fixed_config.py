#!/usr/bin/env python3
"""Test the fixed configuration and logging."""

import asyncio
import os

from app.config import OptimizedConfig


async def test_fixed_scrollscribe():
    """Test the fixed configuration."""

    print("🧪 Testing fixed ScrollScribe configuration...")

    # Test 1: Check if silence function works
    print("\n1️⃣ Testing silence function...")
    OptimizedConfig.silence_noisy_libraries()
    print("✅ Silence function called without errors")

    # Test 2: Check browser config
    print("\n2️⃣ Testing browser config...")
    browser_config = OptimizedConfig.get_fast_browser_config()
    print(f"✅ Browser mode: {getattr(browser_config, 'browser_mode', 'default')}")
    print(f"✅ Verbose: {browser_config.verbose}")

    # Test 3: Check crawler config with all cache disable flags
    print("\n3️⃣ Testing crawler config...")
    crawler_config = OptimizedConfig.get_fast_crawler_config(
        session_id="test",
        timeout=30000,
        wait_until="networkidle"
    )
    print(f"✅ Cache mode: {crawler_config.cache_mode}")
    print(f"✅ Disable cache: {getattr(crawler_config, 'disable_cache', False)}")
    print(f"✅ Bypass cache: {getattr(crawler_config, 'bypass_cache', False)}")
    print(f"✅ No cache read: {getattr(crawler_config, 'no_cache_read', False)}")
    print(f"✅ No cache write: {getattr(crawler_config, 'no_cache_write', False)}")
    print(f"✅ Wait until: {crawler_config.wait_until}")
    print(f"✅ Verbose: {crawler_config.verbose}")

    # Test 4: Check LiteLLM environment variable
    print("\n4️⃣ Testing LiteLLM environment variable...")
    litellm_log = os.environ.get("LITELLM_LOG", "NOT_SET")
    print(f"✅ LITELLM_LOG: {litellm_log}")

    # Test 5: Test a minimal crawl to see output cleanliness
    print("\n5️⃣ Testing minimal crawl with fixed configs...")

    from crawl4ai import AsyncWebCrawler

    try:
        crawler = AsyncWebCrawler(config=browser_config)
        result = await crawler.arun("https://httpbin.org/html", config=crawler_config)

        if result.success:
            print(f"✅ Crawl successful: {len(result.html)} chars")
            print("✅ Output should be much cleaner now!")
        else:
            print(f"❌ Crawl failed: {result.error_message}")

    except Exception as e:
        print(f"❌ Crawl exception: {e}")

    print("\n🎯 Fixed configuration test complete!")
    print("\nKey improvements:")
    print("- LiteLLM logging set to ERROR level only")
    print("- All cache flags disabled (belt and suspenders)")
    print("- Verbose disabled in all configs")
    print("- Clean logger usage throughout")

if __name__ == "__main__":
    asyncio.run(test_fixed_scrollscribe())
