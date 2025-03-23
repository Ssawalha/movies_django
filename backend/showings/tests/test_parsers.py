import os
import unittest

from showings.parsers import GrandParser, ParserError, PrimeParser, TajParser


def load_test_data(filename: str) -> bytes:
    """Load test data from file."""
    test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
    filepath = os.path.join(test_data_dir, filename)
    with open(filepath, "rb") as f:
        return f.read()


class TestGrandParser(unittest.TestCase):
    def setUp(self):
        self.parser = GrandParser()
        self.titles_html = load_test_data("grand_titles_page.html")
        self.dates_html = load_test_data("grand_title_showing_dates_page.html")
        self.times_html = load_test_data("grand_title_showing_times_page.html")

    def test_parse_titles_from_titles_page_success(self):
        result = self.parser.parse_titles_from_titles_page(self.titles_html)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        for title in result:
            self.assertIn("title", title)
            self.assertIn("grand_id", title)

    def test_parse_titles_from_titles_page_invalid_html(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"invalid html")
        self.assertEqual(
            str(cm.exception),
            "GrandParser.parse_titles_from_titles_page: No valid movie titles found in the page",
        )

    def test_parse_titles_from_titles_page_empty_html(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"")
        self.assertEqual(
            str(cm.exception),
            "GrandParser.parse_titles_from_titles_page: No valid movie titles found in the page",
        )

    def test_parse_titles_from_titles_page_no_titles(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"<html><body></body></html>")
        self.assertEqual(
            str(cm.exception),
            "GrandParser.parse_titles_from_titles_page: No valid movie titles found in the page",
        )

    def test_parse_showing_dates_success(self):
        result = self.parser.parse_showing_dates(self.dates_html)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        for date in result:
            self.assertIsInstance(date, str)

    def test_parse_showing_dates_error(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_showing_dates(b"invalid html")
        self.assertEqual(
            str(cm.exception),
            "GrandParser.parse_showing_dates: No valid dates found in the page",
        )

    def test_parse_showing_times_success(self):
        result = self.parser.parse_showing_times(self.times_html)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        for time in result:
            self.assertIsInstance(time, str)

    def test_parse_showing_times_error(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_showing_times(b"invalid html")
        self.assertEqual(
            str(cm.exception),
            "GrandParser.parse_showing_times: No valid times found in the page",
        )


class TestTajParser(unittest.TestCase):
    def setUp(self):
        self.parser = TajParser()
        self.titles_html = load_test_data("taj_titles_page.html")
        self.dates_html = load_test_data("taj_title_showings_page.html")

    def test_parse_titles_from_titles_page_success(self):
        result = self.parser.parse_titles_from_titles_page(self.titles_html)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        for title in result:
            self.assertIn("title", title)
            self.assertIn("taj_id", title)

    def test_parse_titles_from_titles_page_invalid_html(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"invalid html")
        self.assertEqual(
            str(cm.exception),
            "TajParser.parse_titles_from_titles_page: No movies container found in the page",
        )

    def test_parse_titles_from_titles_page_empty_html(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"")
        self.assertEqual(
            str(cm.exception),
            "TajParser.parse_titles_from_titles_page: No movies container found in the page",
        )

    def test_parse_titles_from_titles_page_no_titles(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"<html><body></body></html>")
        self.assertEqual(
            str(cm.exception),
            "TajParser.parse_titles_from_titles_page: No movies container found in the page",
        )

    def test_parse_showing_dates_from_title_page_success(self):
        result = self.parser.parse_showing_dates_from_title_page(self.dates_html)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        for date in result:
            self.assertIn("date", date)
            self.assertIn("date_id", date)

    def test_parse_showing_dates_from_title_page_error(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_showing_dates_from_title_page(b"invalid html")
        self.assertEqual(
            str(cm.exception),
            "TajParser.parse_showing_dates_from_title_page: No booking dates container found in the page",
        )

    def test_parse_showing_times_from_title_page_success(self):
        showing_dates = self.parser.parse_showing_dates_from_title_page(self.dates_html)
        result = self.parser.parse_showing_times_from_title_page(
            self.dates_html, showing_dates
        )
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        for showing in result:
            self.assertIn("date_id", showing)
            self.assertIn("date", showing)
            self.assertIn("time", showing)

    def test_parse_showing_times_from_title_page_error(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_showing_times_from_title_page(b"invalid html", [])
        self.assertEqual(
            str(cm.exception),
            "TajParser.parse_showing_times_from_title_page: No valid showing times found in the page",
        )

    def test_format_parsed_showing_dates_success(self):
        parsed_dates = [
            {"date": "Sun  23", "date_id": "#date-319"},
            {"date": "Mon  24", "date_id": "#date-320"},
        ]
        result = self.parser.format_parsed_showing_dates(parsed_dates)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["date_id"], "date-319")
        self.assertEqual(result[1]["date_id"], "date-320")

    def test_format_parsed_showing_dates_error(self):
        with self.assertRaises(ValueError) as cm:
            self.parser.format_parsed_showing_dates(
                [{"date": "invalid", "date_id": "date1"}]
            )
        self.assertEqual(
            str(cm.exception),
            "TajParser.format_parsed_showing_dates: No valid formatted dates found",
        )


class TestPrimeParser(unittest.TestCase):
    def setUp(self):
        self.parser = PrimeParser()
        self.titles_html = load_test_data("prime_titles_page.html")
        self.showings_html = load_test_data("prime_title_showings_page.html")

    def test_parse_titles_from_titles_page_success(self):
        result = self.parser.parse_titles_from_titles_page(self.titles_html)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        for title in result:
            self.assertIn("title", title)
            self.assertIn("prime_id", title)

    def test_parse_titles_from_titles_page_invalid_html(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"invalid html")
        self.assertEqual(
            str(cm.exception),
            "PrimeParser.parse_titles_from_titles_page: No movies list found in the page",
        )

    def test_parse_titles_from_titles_page_empty_html(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"")
        self.assertEqual(
            str(cm.exception),
            "PrimeParser.parse_titles_from_titles_page: No movies list found in the page",
        )

    def test_parse_titles_from_titles_page_no_titles(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"<html><body></body></html>")
        self.assertEqual(
            str(cm.exception),
            "PrimeParser.parse_titles_from_titles_page: No movies list found in the page",
        )

    def test_parse_showings_from_title_page_success(self):
        result = self.parser.parse_showings_from_title_page(self.showings_html)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        for showing in result:
            self.assertIn("location", showing)
            self.assertIn("date", showing)
            self.assertIn("time", showing)

    def test_parse_showings_from_title_page_error(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_showings_from_title_page("invalid html")
        self.assertEqual(
            str(cm.exception),
            "PrimeParser.parse_showings_from_title_page: No film items found in the page",
        )
