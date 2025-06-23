# ScrollScribe Architecture & Codebase Documentation

**Version:** 2.0
**Last Updated:** June 2025
**Purpose:** Developer onboarding and codebase understanding

---

## 📋 Quick Overview

ScrollScribe is a modular AI-powered documentation scraper that converts documentation websites into clean, filtered Markdown files. The system uses a **hybrid architecture** combining legacy discovery methods with modern crawl4ai processing.

### **Core Pipeline**

```
URL Input → Discovery → Fetching → Processing → Markdown Output
    ↓         ↓           ↓           ↓            ↓
  CLI    crawl4ai    crawl4ai     LLM/Fast    Clean Files
         (links)    (batch HTML)  (filter)
```

---

## 🏗️ Architecture Overview

### **Data Flow**

1. **Input**: Single URL or URL list
2. **Discovery**: Extract internal documentation links using crawl4ai
3. **Fetching**: Batch download all HTML content using crawl4ai
4. **Processing**: Convert HTML to filtered Markdown (LLM or fast mode)
5. **Output**: Individual .md files with clean content

### **Performance Profile**

- **Discovery**: Fast (~seconds, crawl4ai link extraction)
- **Fetching**: Fast (~seconds, crawl4ai batch HTML download)
- **LLM Processing**: ~9 seconds/URL, high quality filtering
- **Fast Processing**: ~0.1 seconds/URL, good quality filtering

---

## 📁 File Structure & Responsibilities

```
ScrollScribe/
├── app/
│   ├── __main__.py          # Package entry point
│   ├── cli.py               # 🎯 CLI interface & command routing
│   ├── discovery.py         # 🗑️ Legacy discovery (DEPRECATED)
│   ├── fast_discovery.py    # ⚡ Fast crawl4ai-based discovery (ACTIVE)
│   ├── processing.py        # ⚡ LLM processing (NEW METHOD)
│   ├── fast_processing.py   # 🚀 Fast processing (NEW METHOD)
│   ├── config.py            # 🔧 Browser & crawler configuration
│   └── utils/               # 🛠️ Shared utilities
│       ├── exceptions.py    # Custom exception hierarchy
│       ├── logging.py       # Rich console & progress displays
│       └── retry.py         # Intelligent retry decorators
├── archive/                 # Legacy V1 reference files
└── REFACTOR/               # Planning & documentation
```

---

## 🔍 Detailed File Analysis

### **`app/cli.py`** - Command Interface ✅ MODERNIZED

**Role:** Modern Typer-based CLI with beautiful help and command orchestration

**Key Components:**

- **Typer Commands:** `discover()`, `scrape()`, `process()` with rich help documentation
- **Async Bridge:** Commands call existing async functions via `argparse.Namespace` bridge
- **Global Options:** `--debug` flag via `@app.callback()` for global configuration

**Dependencies:**

- `typer[all]`: Modern CLI framework with Rich integration
- `crawl4ai`: LLM configuration classes  
- **Bridge:** `argparse.Namespace` for compatibility with existing async functions

**Performance:** ⚡ Fast (CLI layer, no bottlenecks)

**Features:**

- **Gruvbox-themed help** with rich examples and color coding
- **Shell completion** support for tab completion
- **Beautiful error display** integrated with existing CleanConsole system
- **Emoji indicators** for visual appeal and command identification

**Notes:**

- Supports both `--fast` mode and regular LLM mode
- Maintains full backward compatibility through bridge pattern
- All existing async logic preserved unchanged
- Environment variable validation (API keys)

---

### **`app/fast_discovery.py`** - Fast URL Discovery (ACTIVE)

**Role:** Extract internal documentation links from starting URL using crawl4ai

✅ **ACTIVE: Fast, modern, crawl4ai-powered discovery**

**Key Functions:**

- `extract_links_fast(url, verbose)` - Main fast discovery function
- Uses `save_links_to_file()` from legacy discovery.py for file persistence

**Method Used:** **MODERN APPROACH**

```python
# Uses crawl4ai with AsyncWebCrawler
config = CrawlerRunConfig(
    css_selector="a[href]",
    cache_mode=CacheMode.DISABLED,  # Always fresh
    exclude_external_links=True,    # Internal links only
)
async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(start_url, config=config)
```

**Dependencies:**

- `crawl4ai`: Modern web crawler with browser automation
- `asyncio`: Async execution wrapper

**Performance:** ⚡ Fast

- Browser-based crawling with JavaScript support
- Session reuse and optimization
- No cache for fresh content
- Concurrent-ready architecture

**Why It's Fast:**

- Uses modern browser automation
- Built-in link extraction and filtering
- Optimized for documentation sites
- Deterministic and reliable

**Status:** Default and only discovery method as of V2

---

### **`app/processing.py`** - LLM Processing (MODERN)

**Role:** Convert URLs to high-quality filtered Markdown using LLM

**Key Functions:**

- `process_urls_batch()` - Main batch processing function
- `run_llm_filter()` - LLM content filtering with retry
- `absolutify_links()` - Convert relative links to absolute URLs
- `url_to_filename()` - Generate safe filenames from URLs

**Method Used:** **NEW APPROACH**

```python
# Uses modern crawl4ai with batch processing
async with AsyncWebCrawler(config=browser_config) as crawler:
    all_results = await crawler.arun_many(urls_to_scrape, config=html_fetch_config)
    # Process with LLM filtering
    filtered_md = await run_llm_filter(filter_instance, html_content, url)
```

**Dependencies:**

- `crawl4ai`: Modern web crawler with browser automation
- `litellm`: LLM API integration with retry logic
- `rich`: Live progress displays and console output

**Performance:** ⚡ Fast (for what it does)

- Batch processing with session reuse
- Concurrent URL fetching
- ~9 seconds/URL including LLM processing
- Smart retry logic with exponential backoff

**Features:**

- Browser automation with JavaScript rendering
- Persistent browser sessions for performance
- LLM-powered content filtering for high quality
- Rich progress display with ETA and rate calculation

---

### **`app/fast_processing.py`** - Fast Processing (MODERN)

**Role:** High-speed HTML→Markdown conversion without LLM

**Key Functions:**

- `process_urls_fast()` - Main fast processing function

**Method Used:** **NEW APPROACH (No LLM)**

```python
# Uses crawl4ai with PruningContentFilter (no LLM)
prune_filter = PruningContentFilter(threshold=0.48, threshold_type="fixed")
markdown_generator = DefaultMarkdownGenerator(content_filter=prune_filter)
```

**Dependencies:**

- `crawl4ai`: Same modern crawler as processing.py
- `PruningContentFilter`: Smart content filtering without LLM
- `rich`: Progress displays

**Performance:** 🚀 Very Fast

- 50-200 docs/minute (5-20x faster than LLM mode)
- No API costs (completely free)
- Same batch processing benefits as LLM mode
- Smart content filtering removes navigation/footers

**Use Cases:**

- Large documentation sites (hundreds/thousands of pages)
- Budget-conscious projects (no API costs)
- Quick content extraction where perfect formatting isn't critical

---

### **`app/config.py`** - Configuration Management

**Role:** Centralized configuration for browser and crawler settings

**Key Functions:**

- `get_browser_config()` - Browser setup for crawl4ai
- `silence_noisy_libraries()` - Reduce log noise from dependencies
- `get_processing_config()` - Optimized crawler configuration

**Key Settings:**

```python
# Temporary bug fix for crawl4ai
use_managed_browser=False  # Fixes context.pages bug

# Performance optimizations
cache_mode=CacheMode.DISABLED  # Fresh content
excluded_tags=["script", "style", "nav", "footer", "aside"]
word_count_threshold=10
```

**Performance Impact:**

- Disables problematic browser modes to avoid bugs
- Optimizes cache settings for fresh content
- Filters out low-value HTML elements
- Silences noisy library logging

---

### **`app/utils/`** - Utility Modules

#### **`exceptions.py`** - Exception Handling

**Role:** Comprehensive exception hierarchy for different error types

**Key Classes:**

- `ScrollScribeError` - Base exception with enhanced functionality
- `NetworkError` - Network issues with retry information
- `LLMError` - LLM operation failures with provider details
- `RateLimitError` - API rate limiting with wait time calculation
- `FileIOError` - File operation failures with diagnostics

**Features:**

- Structured error logging with context
- Retry-aware exceptions with backoff calculation
- Provider-specific error handling (OpenRouter, etc.)

#### **`logging.py`** - Console Output System ✅ ENHANCED

**Role:** Beautiful terminal output with Rose Pine color theme and progress bar integration

**Key Classes:**

- `CleanConsole` - Main console output manager with progress-aware logging
- `ScrollScribeLogger` - Enhanced logger with Rich integration

**Features:**

- ✅ **ENHANCED**: URL-by-URL status display with icons (✅❌⚠️)
- ✅ **ENHANCED**: Live progress bars with ETA and rate calculation
- ✅ **ENHANCED**: Progress bar persistence - no more broken displays
- ✅ **NEW**: Progress-aware logging with `progress_console` parameter
- ✅ **ENHANCED**: Rose Pine dark color theme for beautiful output
- ✅ **ENHANCED**: Noise suppression for chatty libraries (litellm, httpx)

**Progress Bar Integration:**

- All logging methods support `progress_console` parameter
- Pattern: `clean_console.print_url_status(url, status, time, details, progress_console=progress.console)`
- Ensures progress bars never break due to logging output
- Comprehensive developer documentation in `LOGGING.md`

#### **`retry.py`** - Intelligent Retry Logic

**Role:** Decorators for robust operation retry with smart backoff

**Key Decorators:**

- `@retry_llm` - 5 attempts for LLM operations
- `@retry_network` - 4 attempts for network operations
- `@retry_scrollscribe_operation` - Configurable retry factory

**Features:**

- Smart retry conditions based on exception types
- Exponential backoff with rate limit handling
- Integration with external library exceptions (litellm)
- Preserves original stack traces for debugging

---

## ⚡ Performance Analysis

### **Performance Status**

1. **Discovery Phase** ⚡

    - **Method**: crawl4ai with AsyncWebCrawler (modern)
    - **Speed**: Fast, seconds for most sites
    - **Status**: ✅ Optimized and active

2. **UI/UX Improvements** ✅ COMPLETED
    - **Status**: Complete overhaul of terminal output and logging
    - **Achievements**:
        - Persistent progress bars with current URL display
        - Clean phase separation (DISCOVERY → FETCHING → PROCESSING)
        - Eliminated header reprinting and long separator lines
        - Improved crawl4ai log suppression (no more `[FETCH]`, `[SCRAPE]`, `[COMPLETE]` spam)
        - Simplified verbose output with descriptive status messages
        - Rose Pine color theme throughout
    - **Impact**: Eliminated user confusion about progress and current operation

### **Performance Wins**

1. **Processing Phase** ⚡

    - **Method**: crawl4ai with batch processing
    - **Speed**: ~9 seconds/URL (LLM) or ~0.1 seconds/URL (fast)
    - **Features**: Session reuse, concurrent fetching, smart retry

2. **Terminal UI Excellence** 🎨

    - **Rich Integration**: Advanced progress bars with live URL updates
    - **Phase Indicators**: Clear `DISCOVERY`, `FETCHING`, `PROCESSING` labels
    - **Log Management**: Smart suppression of noisy library output
    - **Persistent Display**: Progress never interrupted by log messages
    - **Color Theme**: Consistent Rose Pine dark theme throughout

3. **Code Quality** 🛠️

    - Clean exception handling with retry logic
    - Modular architecture with clear separation of concerns
    - Rich console output with progress tracking
    - Implementation-agnostic error messages
    - Modern Python 3.10+ type hints

4. **UI/UX Improvements** ✅
    - Progress bar persistence without display breaks
    - Rose Pine dark theme for beautiful, consistent output
    - Progress-aware logging system with comprehensive documentation
    - Clean separation between user-facing and debug logging

---

## 🚀 Upgrade Path (Phase 2)

### **Priority 1: Discovery Performance** ✅ COMPLETED

- ~~Replace `app/discovery.py` with crawl4ai-based batch discovery~~ ✅ DONE
- ~~Expected improvement: 5-10x speed increase~~ ✅ ACHIEVED
- ~~Maintain same API for backward compatibility~~ ✅ MAINTAINED
- **Status**: `fast_discovery.py` is now the active discovery method

### **Priority 2: UI/UX Improvements** ✅ COMPLETED

- ~~Clear phase separation (Discovery → Processing)~~ ✅ DONE
- ~~Better progress indication and status updates~~ ✅ DONE
- ~~Persistent progress bars without display interruption~~ ✅ DONE
- ~~Remove confusing crawl4ai verbose output~~ ✅ DONE
- ~~Implement clean Rose Pine themed output~~ ✅ DONE
- **Status**: Terminal UI completely overhauled with persistent progress and clean phase indicators

### **Priority 3: Interactive Configuration**

- Interactive configuration wizard using Questionary
- Config file support (JSON/TOML)
- CLI flag override system

### **Priority 4: Feature Completion**

- Fast mode optimization and testing
- Session management improvements
- Error recovery enhancements

---

## 🔧 Development Notes

### **Testing the Current System**

```bash
# Test discovery + LLM processing
uv run python -m app process https://docs.crawl4ai.com/ -o output/ -v

# Test fast mode (when implemented)
uv run python -m app process https://docs.crawl4ai.com/ -o output/ --fast -v
```

### **Known Issues**

1. **crawl4ai context.pages bug** - Fixed via `use_managed_browser=False`
2. ~~**Discovery bottleneck** - Sequential processing needs upgrade~~ ✅ FIXED
3. ~~**Terminal UI confusion** - Mixed output and non-persistent headers~~ ✅ FIXED
4. **Session handling** - Some edge cases in browser session management

### **Dependencies**

- **crawl4ai**: Core web crawling and browser automation
- **litellm**: LLM API integration with multiple providers
- **rich**: Terminal UI and progress displays
- **beautifulsoup4**: HTML parsing (legacy discovery only)
- **requests**: HTTP client (legacy discovery only)

---

## 📚 Further Reading

- `REFACTOR/Phase2.md` - Detailed upgrade plans and priorities
- `LOGGING.md` - **NEW**: Comprehensive logging system guide and best practices
- `REFACTOR/bug.md` - Known issues and upstream bug reports
- `archive/` - Legacy V1 implementation for reference
- `pyproject.toml` - Dependencies and project configuration

---

_This document should be updated whenever significant architectural changes are made._
