import unittest
from datetime import datetime
from unittest.mock import patch

from showings.util import (
    get_current_month,
    get_current_year,
    get_first_non_empty,
)


class TestUtil(unittest.TestCase):

    @patch("showings.util.datetime")
    def test_get_current_year(self, mock_datetime):
        fixed_date = datetime(2023, 1, 1)
        mock_datetime.now.return_value = fixed_date
        self.assertEqual(get_current_year(), "2023")

    @patch("showings.util.datetime")
    def test_get_current_month(self, mock_datetime):
        fixed_date = datetime(2023, 1, 1)
        mock_datetime.now.return_value = fixed_date
        self.assertEqual(get_current_month(), "01")

    def test_get_first_non_empty(self):
        title_a = {
            "title": "The Matrix 3",
            "prime_id": "1yts",
            "grand_id": "",
            "taj_id": "",
            "title_prime": "The Matrix 3",
            "title_grand": "",
            "title_taj": "",
            "normalized_title": "the matrix 3",
        }
        title_b = {
            "title": "  The Matrix   ",
            "prime_id": "",
            "grand_id": "1abc",
            "taj_id": "",
            "title_grand": "  The Matrix   ",
            "title_prime": "",
            "title_taj": "",
            "normalized_title": "the matrix",
        }
        expected = "1yts"
        self.assertEqual(
            expected,
            get_first_non_empty(title_a.get("prime_id"), title_b.get("prime_id")),
        )
        self.assertEqual(
            expected,
            get_first_non_empty(title_b.get("prime_id"), title_a.get("prime_id")),
        )
