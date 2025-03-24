import os
import unittest
from enum import Enum

from showings.errors import (
    ElementNotFoundError,
    InvalidFormatError,
    ParserError,
)
from showings.parsers import GrandParser, PrimeParser, TajParser


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
            "[GrandParser] element_not_found: No valid movie titles found in the page",
        )

    def test_parse_titles_from_titles_page_empty_html(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"")
        self.assertEqual(
            str(cm.exception),
            "[GrandParser] element_not_found: No valid movie titles found in the page",
        )

    def test_parse_titles_from_titles_page_no_titles(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"<html><body></body></html>")
        self.assertEqual(
            str(cm.exception),
            "[GrandParser] element_not_found: No valid movie titles found in the page",
        )

    def test_parse_titles_from_titles_page_missing_label_attrs(self):
        html = b"<html><body><label>Title</label></body></html>"
        with self.assertRaises(ElementNotFoundError) as cm:
            self.parser.parse_titles_from_titles_page(html)
        self.assertEqual(
            str(cm.exception),
            "[GrandParser] element_not_found: No valid movie titles found in the page",
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
            "[GrandParser] element_not_found: No valid dates found in the page",
        )

    def test_parse_showing_dates_malformed_html(self):
        html = b"<html><body><div>No dates here</div></body></html>"
        with self.assertRaises(ElementNotFoundError) as cm:
            self.parser.parse_showing_dates(html)
        self.assertEqual(
            str(cm.exception),
            "[GrandParser] element_not_found: No valid dates found in the page",
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
            "[GrandParser] element_not_found: No valid times found in the page",
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
            "[TajParser] element_not_found: No movies container found in the page",
        )

    def test_parse_titles_from_titles_page_empty_html(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"")
        self.assertEqual(
            str(cm.exception),
            "[TajParser] element_not_found: No movies container found in the page",
        )

    def test_parse_titles_from_titles_page_no_titles(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"<html><body></body></html>")
        self.assertEqual(
            str(cm.exception),
            "[TajParser] element_not_found: No movies container found in the page",
        )

    def test_parse_titles_from_titles_page_missing_link(self):
        html = b"<html><body><div class='prs_upcom_slider_slides_wrapper'><div class='prs_upcom_movie_content_box'></div></div></body></html>"
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(html)
        self.assertEqual(
            str(cm.exception),
            "[TajParser] parser_error: 'NoneType' object has no attribute 'text'",
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
            "[TajParser] element_not_found: No booking dates container found in the page",
        )

    def test_parse_showing_dates_from_title_page_missing_href(self):
        html = b"<html><body><div id='booking-dates'><a>Date</a></div></body></html>"
        with self.assertRaises(InvalidFormatError) as cm:
            self.parser.parse_showing_dates_from_title_page(html)
        self.assertEqual(
            str(cm.exception),
            "[TajParser] invalid_format: Invalid date format: missing date_id",
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
            "[TajParser] element_not_found: No valid showing times found in the page",
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
        with self.assertRaises(InvalidFormatError) as cm:
            self.parser.format_parsed_showing_dates(
                [{"date": "invalid", "date_id": "date1"}]
            )
        self.assertEqual(
            str(cm.exception),
            "[TajParser] invalid_format: Invalid date format: invalid literal for int() with base 10: 'invalid'",
        )

    def test_format_parsed_showing_dates_invalid_day(self):
        with self.assertRaises(InvalidFormatError) as cm:
            self.parser.format_parsed_showing_dates(
                [{"date": "Sun 32", "date_id": "#date-1"}]
            )
        self.assertEqual(
            str(cm.exception),
            "[TajParser] invalid_format: Day must be between 1 and 31",
        )

    def test_format_parsed_showing_dates_invalid_date_format(self):
        with self.assertRaises(InvalidFormatError) as cm:
            self.parser.format_parsed_showing_dates(
                [{"date": "Invalid", "date_id": "#date-1"}]
            )
        self.assertEqual(
            str(cm.exception),
            "[TajParser] invalid_format: Invalid date format: invalid literal for int() with base 10: 'Invalid'",
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
            "[PrimeParser] element_not_found: No movies container found in the page",
        )

    def test_parse_titles_from_titles_page_empty_html(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"")
        self.assertEqual(
            str(cm.exception),
            "[PrimeParser] element_not_found: No movies container found in the page",
        )

    def test_parse_titles_from_titles_page_no_titles(self):
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(b"<html><body></body></html>")
        self.assertEqual(
            str(cm.exception),
            "[PrimeParser] element_not_found: No movies container found in the page",
        )

    def test_parse_titles_from_titles_page_missing_href(self):
        html = b"<html><body><article id='movies-list'><div class='title-wrapper'><h3>Title</h3></div></article></body></html>"
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_titles_from_titles_page(html)
        self.assertEqual(
            str(cm.exception),
            "[PrimeParser] parser_error: 'NoneType' object is not subscriptable",
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
            "[PrimeParser] element_not_found: No film items found in the page",
        )

    def test_parse_showings_from_title_page_invalid_datetime(self):
        html = "<html><body><div class='film-item'><h3 class='film-title'>Theater</h3><time datetime='invalid'></time></div></body></html>"
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_showings_from_title_page(html)
        self.assertEqual(
            str(cm.exception),
            "[PrimeParser] invalid_format: Invalid datetime format: time data 'invalid' does not match format '%Y-%m-%dT%H:%M:%S'",
        )

    def test_parse_showings_from_title_page_missing_datetime(self):
        html = "<html><body><div class='film-item'><h3 class='film-title'>Theater</h3><time></time></div></body></html>"
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_showings_from_title_page(html)
        self.assertEqual(
            str(cm.exception),
            "[PrimeParser] parser_error: 'datetime'",
        )


class ErrorCode(Enum):
    SERVICE_ERROR = "service_error"
    CLIENT_ERROR = "client_error"
    # ...
