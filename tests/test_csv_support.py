import csv
import tempfile
import unittest
from pathlib import Path

from app.fast_discovery import save_links_to_file
from app.processing import read_urls_from_file


class TestCSVSupport(unittest.TestCase):
    """Unit tests for CSV format support in save_links_to_file and read_urls_from_file."""

    def setUp(self):
        self.urls = [
            "https://docs.python.org/page1",
            "https://docs.python.org/page2",
            "https://docs.python.org/page3",
        ]

    def urls_to_link_objects(self, urls):
        return [
            {"url": url, "text": "", "title": "", "base_domain": ""} for url in urls
        ]

    def test_save_links_to_file_csv_format(self):
        """Test saving URLs to a CSV file without headers and verify order preservation."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            # Save URLs to temporary CSV file
            save_links_to_file(self.urls, temp_filename, fmt="csv")

            # Read and verify written CSV content
            with open(temp_filename, newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                read_urls = [row[0] for row in reader]

            self.assertEqual(read_urls, self.urls)

        finally:
            Path(temp_filename).unlink()

    def test_save_links_default_filename_csv(self):
        """Test CSV format with explicit filename."""
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_filename = Path(temp_dir_name) / "urls.csv"

            # Save URLs with explicit CSV filename
            save_links_to_file(self.urls, output_file=str(temp_filename), fmt="csv")

            # Verify that the file is created IN THE TEMP DIRECTORY
            self.assertTrue(temp_filename.exists())

            # Verify content is correct
            with open(temp_filename, newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                saved_urls = [row[0] for row in reader]
                self.assertEqual(saved_urls, self.urls)

    def test_read_urls_from_file_txt_and_csv(self):
        """Test read_urls_from_file reading both .txt and .csv correctly."""
        # Test with .txt file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_txt_file:
            temp_txt_filename = temp_txt_file.name
            temp_txt_file.write("\n".join(self.urls) + "\n")

        # Test with .csv file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as temp_csv_file:
            temp_csv_filename = temp_csv_file.name
            csv_writer = csv.writer(temp_csv_file)
            for url in self.urls:
                csv_writer.writerow([url])

        try:
            txt_urls = read_urls_from_file(temp_txt_filename)
            csv_urls = read_urls_from_file(temp_csv_filename)

            self.assertEqual(txt_urls, self.urls)
            self.assertEqual(csv_urls, self.urls)

        finally:
            Path(temp_txt_filename).unlink()
            Path(temp_csv_filename).unlink()

    def test_round_trip_csv(self):
        """Test round-trip save CSV and read back, then check list equality."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            # Discover links and save to CSV
            save_links_to_file(self.urls, temp_filename, fmt="csv")

            # Read back from CSV
            read_back_urls = read_urls_from_file(temp_filename)

            # Verify if the read back list is equal to original
            self.assertEqual(read_back_urls, self.urls)

        finally:
            Path(temp_filename).unlink()


if __name__ == "__main__":
    unittest.main()
