"""Application constants and configuration values.

This module centralizes all magic numbers and configurable values used throughout
the Scroll-Scribe application, making them easy to maintain and tune.
"""

# Display & UI Constants
URL_DISPLAY_MAX_LENGTH = 50
"""Maximum length for URL display in standard contexts"""

URL_DISPLAY_MAX_LENGTH_DETAILED = 60
"""Maximum length for URL display in detailed/verbose contexts"""

# Processing Constants
CONTENT_SIMILARITY_THRESHOLD = 0.48
"""Threshold for content similarity detection in fast processing"""

MIN_WORD_THRESHOLD = 10
"""Minimum word count threshold for content processing"""

# Network & Timeout Constants
DEFAULT_TIMEOUT_MS = 25000  # 25 seconds - better UX than 60s
"""Default timeout for network operations in milliseconds"""

DISCOVERY_TIMEOUT_MS = 20000  # 20 seconds
"""Timeout specifically for URL discovery operations"""

PROCESSING_TIMEOUT_MS = 30000  # 30 seconds
"""Timeout for content processing operations"""

# LLM Configuration Constants
DEFAULT_LLM_MODEL = "openrouter/mistralai/codestral-2501"
"""Default LLM model for content filtering"""

FALLBACK_LLM_MODEL = "openrouter/openai/gpt-3.5-turbo"
"""Fallback LLM model if default is unavailable"""

DEFAULT_MAX_TOKENS = 8192
"""Default maximum tokens for LLM responses"""

DEFAULT_API_KEY_ENV = "OPENROUTER_API_KEY"
"""Default environment variable name for API key"""

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
"""Default API base URL for LLM services"""

# File Processing Constants
MAX_FILENAME_LENGTH = 100
"""Maximum length for generated filenames"""

DEFAULT_EXTENSION = ".md"
"""Default file extension for processed content"""

# Rate Limiting & Performance
DEFAULT_BATCH_SIZE = 10
"""Default batch size for processing multiple URLs"""

MAX_CONCURRENT_REQUESTS = 5
"""Maximum number of concurrent network requests"""

# Retry Configuration
MAX_RETRY_ATTEMPTS = 3
"""Maximum number of retry attempts for failed operations"""

RETRY_DELAY_BASE = 1.0
"""Base delay in seconds for exponential backoff retries"""

MAX_RETRY_DELAY_NETWORK = 5.0
"""Maximum delay for network retry operations (seconds)"""

MAX_RETRY_DELAY_LLM = 10.0
"""Maximum delay for LLM retry operations (seconds)"""

# Content Processing
MIN_CONTENT_LENGTH = 100
"""Minimum content length to consider for processing"""

MAX_CONTENT_LENGTH = 1000000  # 1MB
"""Maximum content length to process (safety limit)"""

# URL Processing
VALID_URL_SCHEMES = ["http", "https"]
"""Valid URL schemes for processing"""

EXCLUDED_URL_EXTENSIONS = [
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
    ".tar",
    ".gz",
    ".rar",
    ".7z",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".webp",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".exe",
    ".dmg",
    ".pkg",
    ".deb",
    ".rpm",
]
"""File extensions to exclude from URL processing"""
