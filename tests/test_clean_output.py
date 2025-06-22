#!/usr/bin/env python3
"""Test the cleaned up logging and cache configuration."""

import asyncio
import os

from crawl4ai import AsyncWebCrawler, LLMConfig
from crawl4ai.content_filter_strategy import LLMContentFilter

from app.config import OptimizedConfig


async def test_clean_output():
    """Test that our fixes actually clean up the output."""

    # Early silence
    OptimizedConfig.silence_noisy_libraries()

    print("🧪 Testing clean output with real LLM filtering...")

    # Check if we have API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ No OPENROUTER_API_KEY found, skipping LLM test")
        return

    # Get optimized configs
    browser_config = OptimizedConfig.get_fast_browser_config()
    crawler_config = OptimizedConfig.get_fast_crawler_config()

    print(f"🔧 Browser mode: {getattr(browser_config, 'browser_mode', 'default')}")
    print(f"🔧 Cache mode: {crawler_config.cache_mode}")
    print(f"🔧 Cache disabled: {getattr(crawler_config, 'disable_cache', False)}")
    print(f"🔧 Bypass cache: {getattr(crawler_config, 'bypass_cache', False)}")

    # Setup LLM filter
    llm_config = LLMConfig(
        provider="openrouter/google/gemini-2.0-flash-exp:free",  # Free model
        api_token=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    llm_filter = LLMContentFilter(
        llm_config=llm_config,
        instruction="Extract main content as clean markdown. No extra commentary.",
        chunk_token_threshold=4096,
        verbose=False,  # Disable verbose
    )

    try:
        crawler = AsyncWebCrawler(config=browser_config)

        print("🌐 Testing single URL with LLM filtering...")
        result = await crawler.arun("https://httpbin.org/html", config=crawler_config)

        if result.success:
            print(f"✅ HTML fetched: {len(result.html)} chars")

            # Test LLM filtering
            print("🤖 Testing LLM filtering...")
            filtered_content = await llm_filter.filter_content(result.html)

            if filtered_content:
                print(f"✅ LLM filtering successful: {len(str(filtered_content))} chars")
                print("🎯 Clean output test complete!")
            else:
                print("❌ LLM filtering failed")
        else:
            print(f"❌ Crawl failed: {result.error_message}")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_clean_output())
