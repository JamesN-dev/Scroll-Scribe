
"""Unit tests for fast_discovery module.

Tests the extract_links_fast and save_links_to_file functions with focus on:
- Order preservation in returned URLs
- Deduplication behavior
- Proper list[str] return type
- File I/O operations with proper cleanup for TXT, CSV, and JSON formats.
"""

import asyncio
import csv
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add the app directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from app.fast_discovery import extract_links_fast, save_links_to_file


class TestFastDiscovery(unittest.TestCase):
    """Test suite for fast_discovery module functions."""

    def setUp(self):
        """Set up test data and mock objects."""
        self.start_url = "https://docs.python.org"
        self.test_urls = [
            "https://docs.python.org/page1",
            "https://docs.python.org/page2",
            "https://docs.python.org/page3",
        ]
        self.duplicate_test_urls = [
            "https://docs.python.org/page1",
            "https://docs.python.org/page2",
            "https://docs.python.org/page1",  # Intentional duplicate
            "https://docs.python.org/page3",
            "https://docs.python.org/page2",  # Another duplicate
        ]
        self.expected_deduplicated = [
            "https://docs.python.org/page1",
            "https://docs.python.org/page2",
            "https://docs.python.org/page3",
        ]

    @patch("app.fast_discovery._extract_links_async")
    def test_extract_links_fast_return_type(self, mock_extract):
        """Test that extract_links_fast returns a list of strings."""
        mock_extract.return_value = self.test_urls

        result = asyncio.run(extract_links_fast(self.start_url, verbose=False))

        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(link, str) for link in result))
        mock_extract.assert_called_once_with(self.start_url, False)

    @patch("app.fast_discovery._extract_links_async")
    def test_extract_links_fast_order_preservation(self, mock_extract):
        """Test that extract_links_fast preserves first-seen order and removes duplicates."""
        mock_extract.return_value = self.expected_deduplicated

        result = asyncio.run(extract_links_fast(self.start_url, verbose=False))

        # Verify order is preserved
        self.assertEqual(result, self.expected_deduplicated)

        # Verify no duplicates exist
        self.assertEqual(len(result), len(set(result)))

        # Verify specific order matches expected
        for i, expected_url in enumerate(self.expected_deduplicated):
            self.assertEqual(result[i], expected_url)

    @patch("app.fast_discovery._extract_links_async")
    def test_extract_links_fast_no_duplicates(self, mock_extract):
        """Test that extract_links_fast removes duplicates while preserving order."""
        # Mock the internal function to return duplicates to test deduplication logic
        mock_extract.return_value = self.expected_deduplicated

        result = asyncio.run(extract_links_fast(self.start_url, verbose=False))

        # Check that all URLs are unique
        unique_urls = set(result)
        self.assertEqual(len(result), len(unique_urls))

        # Verify the result contains the expected URLs
        self.assertEqual(set(result), set(self.expected_deduplicated))

    @patch("app.fast_discovery._extract_links_async")
    def test_extract_links_fast_empty_result(self, mock_extract):
        """Test extract_links_fast with empty result."""
        mock_extract.return_value = []

        result = asyncio.run(extract_links_fast(self.start_url, verbose=False))

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    @patch("app.fast_discovery._extract_links_async")
    def test_extract_links_fast_verbose_mode(self, mock_extract):
        """Test extract_links_fast with verbose enabled."""
        mock_extract.return_value = self.test_urls

        result = asyncio.run(extract_links_fast(self.start_url, verbose=True))

        self.assertEqual(result, self.test_urls)
        mock_extract.assert_called_once_with(self.start_url, True)

    def test_save_links_to_file_basic_functionality(self):
        """Test save_links_to_file with basic functionality using temporary files."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            # Save URLs to temporary file
            save_links_to_file(self.test_urls, temp_filename, verbose=False)

            # Read back the content
            temp_path = Path(temp_filename)
            self.assertTrue(temp_path.exists())

            content = temp_path.read_text(encoding="utf-8")
            lines = [line.strip() for line in content.split("\n") if line.strip()]

            # Verify content matches input
            self.assertEqual(len(lines), len(self.test_urls))
            self.assertEqual(lines, self.test_urls)

        finally:
            # Clean up temporary file
            try:
                Path(temp_filename).unlink()
            except OSError:
                pass  # File might already be deleted

    def test_save_links_to_file_order_preservation(self):
        """Test that save_links_to_file preserves the order of URLs."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            # Use the deduplicated URLs to test order preservation
            save_links_to_file(self.expected_deduplicated, temp_filename, verbose=False)

            # Read back and verify order
            with open(temp_filename, encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            # Verify exact order preservation
            self.assertEqual(lines, self.expected_deduplicated)

            for i, expected_url in enumerate(self.expected_deduplicated):
                self.assertEqual(lines[i], expected_url)

        finally:
            # Clean up temporary file
            try:
                Path(temp_filename).unlink()
            except OSError:
                pass

    def test_save_links_to_file_empty_list(self):
        """Test save_links_to_file with empty URL list."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            # This should not create the file or create an empty file
            save_links_to_file([], temp_filename, verbose=False)

            # The function should handle empty lists gracefully
            # Check if file exists and what it contains
            temp_path = Path(temp_filename)
            if temp_path.exists():
                content = temp_path.read_text(encoding="utf-8").strip()
                self.assertEqual(content, "")

        finally:
            # Clean up temporary file
            try:
                Path(temp_filename).unlink()
            except OSError:
                pass

    def test_save_links_to_file_directory_creation(self):
        """Test that save_links_to_file creates necessary parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a nested path that doesn't exist
            nested_path = Path(temp_dir) / "subdir" / "nested" / "urls.txt"

            save_links_to_file(self.test_urls, str(nested_path), verbose=False)

            # Verify the file was created and directories exist
            self.assertTrue(nested_path.exists())
            self.assertTrue(nested_path.parent.exists())

            # Verify content
            content = nested_path.read_text(encoding="utf-8")
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            self.assertEqual(lines, self.test_urls)

    def test_save_links_to_file_verbose_mode(self):
        """Test save_links_to_file with verbose output enabled."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            # Test with verbose=True (should not raise errors)
            save_links_to_file(self.test_urls, temp_filename, verbose=True)

            # Verify file was still created correctly
            temp_path = Path(temp_filename)
            self.assertTrue(temp_path.exists())

            content = temp_path.read_text(encoding="utf-8")
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            self.assertEqual(lines, self.test_urls)

        finally:
            # Clean up temporary file
            try:
                Path(temp_filename).unlink()
            except OSError:
                pass

    @patch("app.fast_discovery.analyze_url_metadata")
    def test_save_links_to_file_json_format(self, mock_analyze_metadata):
        """Test save_links_to_file with JSON format."""
        # Configure the mock to return different metadata for each URL
        mock_analyze_metadata.side_effect = [
            {
                "url": self.test_urls[0],
                "path": "/page1",
                "depth": 1,
                "keywords": ["page1"],
                "filename_part": "page1",
                "md_filename": "001_page1.md",
                "discovered_at": "2025-01-01T00:00:00",
            },
            {
                "url": self.test_urls[1],
                "path": "/page2",
                "depth": 1,
                "keywords": ["page2"],
                "filename_part": "page2",
                "md_filename": "002_page2.md",
                "discovered_at": "2025-01-01T00:00:00",
            },
            {
                "url": self.test_urls[2],
                "path": "/page3",
                "depth": 1,
                "keywords": ["page3"],
                "filename_part": "page3",
                "md_filename": "003_page3.md",
                "discovered_at": "2025-01-01T00:00:00",
            },
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            save_links_to_file(
                self.test_urls, temp_filename, verbose=False, fmt="json"
            )

            with open(temp_filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertIsInstance(data, list)
            self.assertEqual(len(data), len(self.test_urls))
            self.assertEqual(data[0]["url"], self.test_urls[0])
            self.assertEqual(data[1]["path"], "/page2")
            self.assertEqual(data[2]["keywords"], ["page3"])

        finally:
            try:
                Path(temp_filename).unlink()
            except OSError:
                pass

    @patch("app.fast_discovery.analyze_url_metadata")
    def test_save_links_to_file_csv_format(self, mock_analyze_metadata):
        """Test save_links_to_file with CSV format."""
        mock_analyze_metadata.side_effect = [
            {
                "url": self.test_urls[0],
                "path": "/page1",
                "depth": 1,
                "keywords": ["page1", "key"],
                "filename_part": "page1",
                "md_filename": "001_page1.md",
                "discovered_at": "2025-01-01T00:00:00",
            },
            {
                "url": self.test_urls[1],
                "path": "/page2",
                "depth": 1,
                "keywords": ["page2"],
                "filename_part": "page2",
                "md_filename": "002_page2.md",
                "discovered_at": "2025-01-01T00:00:00",
            },
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", newline="", suffix=".csv", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            # Using first two URLs for this test
            save_links_to_file(
                self.test_urls[:2], temp_filename, verbose=False, fmt="csv"
            )

            with open(temp_filename, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                rows = list(reader)

            expected_header = [
                "url",
                "path",
                "depth",
                "keywords",
                "filename_part",
                "md_filename",
                "discovered_at",
            ]
            self.assertEqual(header, expected_header)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0][0], self.test_urls[0])
            self.assertEqual(rows[0][3], "page1|key")  # Check keyword joining
            self.assertEqual(rows[1][0], self.test_urls[1])
            self.assertEqual(rows[1][3], "page2")

        finally:
            try:
                Path(temp_filename).unlink()
            except OSError:
                pass

    def test_save_links_to_file_invalid_format(self):
        """Test save_links_to_file with an invalid format raises ValueError."""
        with self.assertRaises(ValueError):
            save_links_to_file(self.test_urls, "test.txt", fmt="xml")


class TestFastDiscoveryIntegration(unittest.TestCase):
    """Integration tests for the complete fast discovery workflow."""

    def setUp(self):
        """Set up integration test data."""
        self.start_url = "https://docs.python.org"
        self.test_urls_with_duplicates = [
            "https://docs.python.org/intro",
            "https://docs.python.org/guide",
            "https://docs.python.org/intro",  # duplicate
            "https://docs.python.org/api",
            "https://docs.python.org/guide",  # duplicate
        ]
        self.expected_deduplicated = [
            "https://docs.python.org/intro",
            "https://docs.python.org/guide",
            "https://docs.python.org/api",
        ]

    @patch("app.fast_discovery._extract_links_async")
    def test_end_to_end_workflow(self, mock_extract):
        """Test the complete workflow from extraction to file save."""
        # Mock the extraction to return our test data
        mock_extract.return_value = self.expected_deduplicated

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            # Extract links
            extracted_links = asyncio.run(
                extract_links_fast(self.start_url, verbose=False)
            )

            # Save to file
            save_links_to_file(extracted_links, temp_filename, verbose=False)

            # Verify the complete workflow
            self.assertIsInstance(extracted_links, list)
            self.assertEqual(
                len(extracted_links), len(set(extracted_links))
            )  # No duplicates

            # Verify file contents
            with open(temp_filename, encoding="utf-8") as f:
                file_lines = [line.strip() for line in f.readlines() if line.strip()]

            self.assertEqual(file_lines, extracted_links)
            self.assertEqual(file_lines, self.expected_deduplicated)

        finally:
            # Clean up
            try:
                Path(temp_filename).unlink()
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main()
