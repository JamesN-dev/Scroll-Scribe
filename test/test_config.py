"""Tests for ScrollScribe configuration utilities in app/config.py."""

import pytest
import logging
from unittest.mock import MagicMock, patch, call
import os

from crawl4ai import BrowserConfig, CacheMode, CrawlerRunConfig

from app.config import (
    get_browser_config,
    get_processing_config,
    silence_noisy_libraries,
)

# Tests for get_browser_config
def test_get_browser_config_defaults():
    """Test get_browser_config with default parameters."""
    config = get_browser_config()
    assert isinstance(config, BrowserConfig)
    assert config.headless is True
    assert config.verbose is False # crawl4ai.BrowserConfig default verbose is False
    # assert config.browser_mode == "builtin" # This was commented out in source
    assert config.use_managed_browser is False # Specific temporary fix

def test_get_browser_config_custom():
    """Test get_browser_config with custom parameters."""
    config = get_browser_config(headless=False, verbose=True)
    assert isinstance(config, BrowserConfig)
    assert config.headless is False
    assert config.verbose is True
    assert config.use_managed_browser is False

# Tests for get_processing_config
def test_get_processing_config():
    """Test get_processing_config with mock arguments."""
    mock_args = MagicMock()
    mock_args.wait = "load" # crawl4ai default is 'load', project default 'networkidle'
    mock_args.timeout = 45000

    session_id = "test_session_123"
    config = get_processing_config(session_id=session_id, args=mock_args)

    assert isinstance(config, CrawlerRunConfig)
    assert config.session_id == session_id
    assert config.cache_mode == CacheMode.DISABLED
    assert config.wait_until == "load" # Matches mock_args.wait
    assert config.page_timeout == 45000 # Matches mock_args.timeout
    assert config.verbose is False # crawl4ai.CrawlerRunConfig default verbose is False
    assert config.stream is False # crawl4ai.CrawlerRunConfig default stream is False
    assert config.exclude_external_links is True
    assert config.excluded_tags == ["script", "style", "nav", "footer", "aside"]
    assert config.word_count_threshold == 10

# Tests for silence_noisy_libraries
@patch("logging.getLogger")
@patch.dict(os.environ, {}, clear=True) # Ensure a clean os.environ for this test
def test_silence_noisy_libraries(mock_get_logger):
    """Test silence_noisy_libraries sets correct log levels and env var."""
    # Create a dictionary to hold mock loggers to inspect their setLevel calls
    mock_loggers = {}

    def get_mock_logger(name):
        if name not in mock_loggers:
            mock_loggers[name] = MagicMock(spec=logging.Logger)
        return mock_loggers[name]

    mock_get_logger.side_effect = get_mock_logger

    silence_noisy_libraries()

    # Check LITELLM_LOG environment variable
    assert "LITELLM_LOG" in os.environ
    assert os.environ["LITELLM_LOG"] == "ERROR"

    # Check logging levels for specified libraries
    expected_noisy_loggers = [
        "litellm",
        "litellm.cost_calculator",
        "litellm.utils",
        "httpx",
        "urllib3",
    ]
    for logger_name in expected_noisy_loggers:
        assert logger_name in mock_loggers, f"Logger {logger_name} was not retrieved"
        mock_loggers[logger_name].setLevel.assert_called_once_with(logging.ERROR)
        if "litellm" in logger_name:
            # Check that the 'disabled' attribute was set to True for litellm loggers
            assert mock_loggers[logger_name].disabled is True
        else:
            # Ensure 'disabled' was not set for non-litellm loggers (or was set to False)
            assert not hasattr(mock_loggers[logger_name], 'disabled') or mock_loggers[logger_name].disabled is False

    # Ensure getLogger was called for each expected logger
    for name in expected_noisy_loggers:
        mock_get_logger.assert_any_call(name)
        
    # Verify that other loggers were not affected (not easily testable without knowing all loggers)
    # but we can check if get_logger was called with unexpected names.
    all_called_names = {call_args[0][0] for call_args in mock_get_logger.call_args_list}
    unexpected_calls = all_called_names - set(expected_noisy_loggers)
    assert not unexpected_calls, f"Unexpected loggers configured: {unexpected_calls}"
