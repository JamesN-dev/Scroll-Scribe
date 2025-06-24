"""Tests for the processing module."""

from app.processing import url_to_filename


def test_url_to_filename():
    """Test URL to filename conversion."""
    # Test basic URL
    url = "https://docs.python.org/3/library/asyncio.html"
    assert url_to_filename(url, 1) == "page_001_3_library_asyncio.html.md"

    # Test URL with query params
    url = "https://docs.python.org/3/library/asyncio.html?highlight=async"
    assert url_to_filename(url, 2) == "page_002_3_library_asyncio.html.md"

    # Test URL with special characters
    url = "https://docs.python.org/3/library/os.path.html#os.path.join"
    assert url_to_filename(url, 3) == "page_003_3_library_os.path.html.md"
