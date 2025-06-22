# ScrollScribe Logging System Guide

**Purpose:** Developer guide for consistent logging patterns and progress bar integration  
**Last Updated:** June 2025  
**Audience:** New developers and contributors

---

## 🎯 **Logging Philosophy**

ScrollScribe uses a **dual logging system**:
1. **Beautiful terminal output** via `CleanConsole` for user-facing messages
2. **Structured logging** via Python's `logging` module for debugging

**Key Principle:** Never break the progress bar display with logging.

---

## 🏗️ **Logging Architecture**

### **Core Components**

```
app/utils/logging.py
├── CleanConsole        # User-facing beautiful output
├── ScrollScribeLogger  # Structured logging integration  
└── Logging utilities   # Verbosity control, noise suppression
```

### **Progress Bar Integration**

**CRITICAL:** When inside a progress bar context, always use `progress_console` parameter:

```python
# ✅ CORRECT - Progress-aware logging
clean_console.print_url_status(url, "success", time_taken, details, 
                              progress_console=progress.console)

# ❌ WRONG - Breaks progress bar
clean_console.print_url_status(url, "success", time_taken, details)
```

---

## 📋 **Logging Patterns & Usage**

### **1. URL Status Logging**

Use `CleanConsole.print_url_status()` for per-URL results:

```python
# Success with timing and details
clean_console.print_url_status(
    url="https://example.com/page", 
    status="success", 
    time_taken=1.2, 
    details="5,432 chars → page_001.md",
    progress_console=progress.console  # REQUIRED in progress context
)

# Error with message
clean_console.print_url_status(
    url="https://example.com/broken", 
    status="error", 
    time_taken=0, 
    details="HTTP 404",
    progress_console=progress.console
)

# Warning
clean_console.print_url_status(
    url="https://example.com/empty", 
    status="warning", 
    time_taken=0, 
    details="no content found",
    progress_console=progress.console
)
```

**Output Examples:**
```
✅ example.com/page (1.2s) - 5,432 chars → page_001.md
❌ example.com/broken (HTTP 404)
⚠️  example.com/empty (no content found)
```

### **2. Fetch/Process Status Logging**

Use `CleanConsole.print_fetch_status()` for operation status:

```python
# Processing status
clean_console.print_fetch_status(
    url="https://example.com/page",
    status="processing", 
    progress_console=progress.console  # REQUIRED in progress context
)

# Fetched status with timing
clean_console.print_fetch_status(
    url="https://example.com/page",
    status="fetched",
    time_taken=0.8,
    progress_console=progress.console
)
```

**Output Examples:**
```
🔄 PROCESSING example.com/page
📥 FETCHED example.com/page (0.8s)
```

### **3. Phase Indicators**

Use `CleanConsole.print_phase()` for major phase transitions:

```python
# Phase transitions (safe outside progress context)
clean_console.print_phase("DISCOVERY", "Finding internal links from docs.example.com")
clean_console.print_phase("PROCESSING", f"Converting {len(urls)} URLs to Markdown")
clean_console.print_phase("FETCHING", f"Downloading {len(urls)} pages")
```

**Output Examples:**
```
DISCOVERY • Finding internal links from docs.example.com
PROCESSING • Converting 41 URLs to Markdown
FETCHING • Downloading 41 pages
```

### **4. General Messages**

Use `CleanConsole` methods for general user communication:

```python
# Information (outside progress context)
clean_console.print_info("Starting unified process (discover + scrape)")
clean_console.print_success(f"Discovery finished. Found {len(urls)} URLs.")
clean_console.print_warning("No valid URLs extracted.")
clean_console.print_error("Discovery failed", "Network timeout")
```

### **5. Structured Debug Logging**

Use `logger` for detailed debugging information:

```python
logger = get_logger("processing")

# Debug information (only visible with --debug)
logger.info(f"HTML fetched ({len(html)} chars). Sending to LLM filter ({model})...")
logger.warning(f"Retrying URL after rate limit: {url}")
logger.error(f"Failed to save markdown for {url} to {filepath}")
```

---

## ⚡ **Progress Bar Best Practices**

### **DO:** Use Progress-Aware Logging

```python
# Inside progress bar context
with clean_console.progress_bar(len(urls), "Processing URLs") as (progress, task):
    for url in urls:
        # ✅ CORRECT - Won't break progress bar
        clean_console.print_url_status(url, "success", 1.2, "details", 
                                      progress_console=progress.console)
        
        # ✅ CORRECT - Use logger for debug info
        logger.info(f"Processing {url}")
        
        progress.update(task, advance=1)
```

### **DON'T:** Direct Console Output in Progress Context

```python
# Inside progress bar context
with clean_console.progress_bar(len(urls), "Processing URLs") as (progress, task):
    for url in urls:
        # ❌ WRONG - Breaks progress bar
        clean_console.print_url_status(url, "success", 1.2, "details")
        
        # ❌ WRONG - Direct console output
        print(f"Processing {url}")
        
        # ❌ WRONG - Direct rich console
        console.print("Some message")
```

---

## 🔧 **Adding New Logging**

### **Step 1: Identify Context**

**Question:** Are you logging inside a progress bar context?

- **YES** → Use `progress_console=progress.console` parameter
- **NO** → Use regular `CleanConsole` methods

### **Step 2: Choose Appropriate Method**

| Use Case | Method | Example |
|----------|--------|---------|
| URL processing result | `print_url_status()` | Success/error per URL |
| Operation status | `print_fetch_status()` | Fetching, processing status |
| Phase transitions | `print_phase()` | Discovery → Processing |
| General messages | `print_info/success/warning/error()` | High-level status |
| Debug information | `logger.info/warning/error()` | Technical details |

### **Step 3: Implementation Pattern**

```python
# Template for progress-aware logging
def process_url(url: str, progress_console=None):
    try:
        # Do processing work
        result = some_operation(url)
        
        # Log success with progress awareness
        if progress_console:
            clean_console.print_url_status(url, "success", 1.2, "processed", 
                                          progress_console=progress_console)
        else:
            clean_console.print_url_status(url, "success", 1.2, "processed")
            
    except Exception as e:
        # Log error with progress awareness
        if progress_console:
            clean_console.print_url_status(url, "error", 0, str(e), 
                                          progress_console=progress_console)
        else:
            clean_console.print_url_status(url, "error", 0, str(e))
```

---

## 🎨 **Styling & Colors**

ScrollScribe uses the **Rose Pine dark theme** for consistent, beautiful output:

### **Color Palette**

```python
# Rose Pine colors used in logging
colors = {
    "primary": "#c4a7e7",      # Iris - main headings
    "secondary": "#9ccfd8",    # Foam - info/processing  
    "success": "#31748f",      # Pine - success messages
    "warning": "#f6c177",      # Gold - warnings
    "error": "#eb6f92",        # Love - errors  
    "muted": "#908caa",        # Subtle - secondary text
    "text": "#e0def4",         # Text - main content
}
```

### **Icon Standards**

```python
# Consistent icons across the application
icons = {
    "success": "✅",
    "error": "❌", 
    "warning": "⚠️ ",
    "processing": "🔄",
    "fetching": "📥",
    "info": "ℹ️ ",
    "phase": "🔹"
}
```

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: Progress Bar Resets/Breaks**

**Symptoms:** Progress bar shows "0% • 0/41" repeatedly  
**Cause:** Direct console output inside progress context  
**Solution:** Add `progress_console=progress.console` parameter

### **Issue 2: Missing Verbose Output**

**Symptoms:** No detailed logging in verbose mode  
**Solution:** Ensure `set_logging_verbosity(verbose=True)` is called

### **Issue 3: Noisy Library Logs**

**Symptoms:** Too much output from crawl4ai, litellm, etc.  
**Solution:** Library silencing is automatic, but check `set_logging_verbosity()`

### **Issue 4: Inconsistent Styling**

**Symptoms:** Different colors/icons across similar messages  
**Solution:** Use standardized `CleanConsole` methods instead of manual styling

---

## 📚 **Testing Logging**

### **Test Progress Bar Integration**

```bash
# Test with verbose mode to see all logging
uv run python -m app process https://docs.crawl4ai.com/ -o test_output/ -v

# Look for:
# ✅ Persistent progress bar (incremental: 1/41, 2/41, etc.)
# ✅ Clean logs above progress bar
# ❌ No progress bar resets or broken display
```

### **Test Different Verbosity Levels**

```bash
# Quiet mode - minimal output
uv run python -m app process https://docs.crawl4ai.com/ -o test_output/

# Verbose mode - detailed logs
uv run python -m app process https://docs.crawl4ai.com/ -o test_output/ -v

# Debug mode - everything including library logs  
uv run python -m app process https://docs.crawl4ai.com/ -o test_output/ --debug
```

---

## 📝 **Contributing Guidelines**

### **Before Adding New Logging:**

1. **Read this guide** - Understand the patterns and best practices
2. **Check context** - Are you inside a progress bar? Use `progress_console`
3. **Choose method** - Use appropriate `CleanConsole` method for the use case
4. **Test thoroughly** - Ensure progress bars don't break
5. **Follow styling** - Use Rose Pine colors and standard icons

### **Code Review Checklist:**

- [ ] Progress bar integration tested
- [ ] Consistent styling with Rose Pine theme
- [ ] Appropriate verbosity levels
- [ ] No direct console output in progress contexts
- [ ] Proper exception handling and logging

---

*This guide should be updated when new logging patterns or methods are added.*