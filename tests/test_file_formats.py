"""Unit tests for file format support in Scroll-Scribe.

Tests TXT, CSV, and JSON format support in:
- app.fast_discovery.save_links_to_file
- app.processing.read_urls_from_file

Ensures that all output formats are correctly written and that the data can be
read back consistently, verifying the integrity of the data pipeline.
"""

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

from app.fast_discovery import save_links_to_file
from app.processing import read_urls_from_file


class TestFileFormatSupport(unittest.TestCase):
    """Test suite for file format support (TXT, CSV, JSON)."""

    def setUp(self):
        """Set up test data and mock objects."""
        self.urls = [
            "https://docs.python.org/page1",
            "https://docs.python.org/page2",
            "https://docs.python.org/page3",
        ]
        self.mock_metadata = [
            {
                "url": self.urls[0],
                "path": "/page1",
                "depth": 1,
                "keywords": ["page1"],
                "filename_part": "page1",
                "md_filename": "001_page1.md",
                "discovered_at": "2025-01-01T00:00:00",
            },
            {
                "url": self.urls[1],
                "path": "/page2",
                "depth": 1,
                "keywords": ["page2"],
                "filename_part": "page2",
                "md_filename": "002_page2.md",
                "discovered_at": "2025-01-01T00:00:00",
            },
            {
                "url": self.urls[2],
                "path": "/page3",
                "depth": 1,
                "keywords": ["page3", "key"],
                "filename_part": "page3",
                "md_filename": "003_page3.md",
                "discovered_at": "2025-01-01T00:00:00",
            },
        ]

    def test_save_and_read_txt_format(self):
        """Test saving and reading URLs in TXT format."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_filename = temp_file.name
            # In TXT format, only URLs are written, one per line
            temp_file.write("\n".join(self.urls))

        try:
            read_back_urls = read_urls_from_file(temp_filename)
            self.assertEqual(read_back_urls, self.urls)
        finally:
            Path(temp_filename).unlink()

    @patch("app.fast_discovery.analyze_url_metadata")
    def test_save_and_read_csv_format(self, mock_analyze_metadata):
        """Test saving and reading URLs in multi-column CSV format."""
        mock_analyze_metadata.side_effect = self.mock_metadata

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            # Save the data with metadata
            save_links_to_file(self.urls, temp_filename, fmt="csv")

            # Read it back and verify
            read_back_urls = read_urls_from_file(temp_filename)
            self.assertEqual(read_back_urls, self.urls)

            # Also verify the content for correctness
            with open(temp_filename, "r", encoding="utf-8") as f:
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
            self.assertEqual(len(rows), len(self.urls))
            self.assertEqual(rows[0][0], self.urls[0])
            self.assertEqual(rows[2][3], "page3|key")  # Check keyword joining

        finally:
            Path(temp_filename).unlink()

    @patch("app.fast_discovery.analyze_url_metadata")
    def test_save_and_read_json_format(self, mock_analyze_metadata):
        """Test saving and reading URLs in JSON format."""
        mock_analyze_metadata.side_effect = self.mock_metadata

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            save_links_to_file(self.urls, temp_filename, fmt="json")

            read_back_urls = read_urls_from_file(temp_filename)
            self.assertEqual(read_back_urls, self.urls)

            # Verify the JSON structure
            with open(temp_filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertIsInstance(data, list)
            self.assertEqual(len(data), len(self.urls))
            self.assertEqual(data[0]["url"], self.urls[0])
            self.assertEqual(data[1]["path"], "/page2")

        finally:
            Path(temp_filename).unlink()

    def test_read_urls_from_file_empty(self):
        """Test read_urls_from_file with an empty file returns an empty list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            self.assertEqual(read_urls_from_file(f.name), [])


if __name__ == "__main__":
    unittest.main()