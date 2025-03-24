import unittest
from pprint import pprint
from unittest.mock import patch

from showings.errors import ServiceError
from showings.services import GrandService, PrimeService, ShowingService, TajService


class TestShowingService(unittest.TestCase):
    def setUp(self):
        self.service = ShowingService()
        self.grand_titles = [{"title": "The Matrix", "grand_id": "1abc"}]
        self.taj_titles = [{"title": "Django Unchained", "taj_id": "asdfg"}]
        self.prime_titles = [{"title": "Inception", "prime_id": "gsdf"}]
        self.common_titles = [
            {
                "title": "Interstellar",
                "grand_id": "2def",
                "taj_id": "qwert",
                "prime_id": "zxcvb",
            },
        ]
        self.mixed_titles = [
            {
                "title": "The Matrix",
                "grand_id": "1abc",
                "taj_id": None,
                "prime_id": None,
            },
            {
                "title": "Django Unchained",
                "grand_id": None,
                "taj_id": "asdfg",
                "prime_id": None,
            },
            {
                "title": "Inception",
                "grand_id": None,
                "taj_id": None,
                "prime_id": "gsdf",
            },
        ]
        self.grand_showings = [
            {
                "title": "The Matrix",
                "date": "2024-03-20",
                "time": "14:00",
                "location": "Grand Cinema City Mall",
            }
        ]
        self.taj_showings = [
            {
                "title": "Django Unchained",
                "date": "2024-03-20",
                "time": "17:00",
                "location": "Taj Mall",
            }
        ]
        self.prime_showings = [
            {
                "title": "Inception",
                "date": "2024-03-20",
                "time": "20:00",
                "location": "Prime Mall",
            }
        ]
        self.mixed_showings = [
            *self.grand_showings,
            *self.taj_showings,
            *self.prime_showings,
        ]

    @patch.object(GrandService, "get_titles")
    @patch.object(TajService, "get_titles")
    @patch.object(PrimeService, "get_titles")
    def test__get_and_validate_titles(
        self, mock_prime_titles, mock_taj_titles, mock_grand_titles
    ):
        mock_grand_titles.return_value = self.grand_titles
        mock_taj_titles.return_value = self.taj_titles
        mock_prime_titles.return_value = self.prime_titles
        titles = self.service._get_and_validate_titles()
        self.assertEqual(len(titles), 3)
        expected_titles = [
            {
                "title_grand": "",
                "grand_id": "",
                "normalized_title": "django unchained",
                "title_prime": "",
                "prime_id": "",
                "title_taj": "Django Unchained",
                "taj_id": "asdfg",
                "title": "",
            },
            {
                "title_grand": "",
                "grand_id": "",
                "normalized_title": "inception",
                "title_prime": "Inception",
                "prime_id": "gsdf",
                "title_taj": "",
                "taj_id": "",
                "title": "",
            },
            {
                "title_grand": "The Matrix",
                "grand_id": "1abc",
                "normalized_title": "the matrix",
                "title_prime": "",
                "prime_id": "",
                "title_taj": "",
                "taj_id": "",
                "title": "",
            },
        ]
        self.assertEqual(titles, expected_titles)

    @patch.object(GrandService, "get_showings")
    @patch.object(TajService, "get_showings")
    @patch.object(PrimeService, "get_showings")
    def test__get_all_showings(
        self, mock_prime_showings, mock_taj_showings, mock_grand_showings
    ):
        # Setup mock returns
        mock_grand_showings.return_value = self.grand_showings
        mock_taj_showings.return_value = self.taj_showings
        mock_prime_showings.return_value = self.prime_showings

        # Set the titles in the service
        titles = self.mixed_titles
        showings = self.service._get_all_showings(titles)

        self.assertEqual(len(showings), 3)
        self.assertEqual(showings, self.mixed_showings)

    @patch.object(GrandService, "get_showings")
    @patch.object(TajService, "get_showings")
    @patch.object(PrimeService, "get_showings")
    def test__get_all_showings_no_titles(
        self,
        mock_prime_showings,
        mock_taj_showings,
        mock_grand_showings,
    ):
        # Setup mocks
        mock_grand_showings.return_value = self.grand_showings
        mock_taj_showings.return_value = self.taj_showings
        mock_prime_showings.return_value = self.prime_showings

        # Set titles to None to trigger scraping
        titles = None

        showings = self.service._get_all_showings(titles)
        self.assertEqual(showings, [])

    @patch.object(GrandService, "get_showings")
    @patch.object(TajService, "get_showings")
    @patch.object(PrimeService, "get_showings")
    def test__get_all_showings_empty_list(
        self,
        mock_prime_showings,
        mock_taj_showings,
        mock_grand_showings,
    ):
        # Setup mocks
        mock_grand_showings.return_value = []
        mock_taj_showings.return_value = []
        mock_prime_showings.return_value = []

        titles = []

        showings = self.service._get_all_showings(titles)
        self.assertEqual(showings, [])

    def test_filter_titles_grand_id(self):
        titles = self.mixed_titles
        titles += self.common_titles
        filtered_titles = self.service._filter_titles(titles, "grand_id")
        expected_titles = [
            {
                "title": "The Matrix",
                "grand_id": "1abc",
                "taj_id": None,
                "prime_id": None,
            },
            {
                "title": "Interstellar",
                "grand_id": "2def",
                "taj_id": "qwert",
                "prime_id": "zxcvb",
            },
        ]
        self.assertEqual(filtered_titles, expected_titles)

    def test_filter_titles_taj_id(self):
        titles = self.mixed_titles
        titles += self.common_titles
        filtered_titles = self.service._filter_titles(titles, "taj_id")
        expected_titles = [
            {
                "title": "Django Unchained",
                "grand_id": None,
                "taj_id": "asdfg",
                "prime_id": None,
            },
            {
                "title": "Interstellar",
                "grand_id": "2def",
                "taj_id": "qwert",
                "prime_id": "zxcvb",
            },
        ]
        self.assertEqual(filtered_titles, expected_titles)

    def test_filter_titles_prime_id(self):
        titles = self.mixed_titles
        titles += self.common_titles
        filtered_titles = self.service._filter_titles(titles, "prime_id")
        expected_titles = [
            {
                "title": "Inception",
                "grand_id": None,
                "taj_id": None,
                "prime_id": "gsdf",
            },
            {
                "title": "Interstellar",
                "grand_id": "2def",
                "taj_id": "qwert",
                "prime_id": "zxcvb",
            },
        ]
        self.assertEqual(filtered_titles, expected_titles)

    def test_filter_titles_empty_list(self):
        filtered_titles = self.service._filter_titles([], "grand_id")
        self.assertEqual(filtered_titles, [])

    def test_filter_titles_no_matches(self):
        titles_without_grand = [
            {"title": "Django Unchained", "taj_id": "asdfg", "prime_id": None},
            {"title": "Inception", "taj_id": None, "prime_id": "gsdf"},
        ]
        filtered_titles = self.service._filter_titles(titles_without_grand, "grand_id")
        self.assertEqual(filtered_titles, [])


class TestGrandService(unittest.TestCase):
    def setUp(self):
        self.mock_titles = [
            {"title": "The Matrix", "grand_id": "1abc"},
            {"title": "Inception", "grand_id": "2def"},
        ]
        self.mock_dates = ["2024-03-20", "2024-03-21"]
        self.mock_times = ["14:00", "17:00", "20:00"]
        self.mock_titles_page = "<html>Mock titles page</html>"
        self.mock_dates_page = "<html>Mock dates page</html>"
        self.mock_times_page = "<html>Mock times page</html>"

        self.service = GrandService()

    def test_get_showings(self):
        with patch.object(
            self.service, "get_titles", return_value=self.mock_titles
        ), patch.object(
            self.service, "get_showing_dates", return_value=self.mock_dates
        ), patch.object(
            self.service, "get_showing_times", return_value=self.mock_times
        ):

            showings = self.service.get_showings()

            expected_showings = [
                {
                    "title": "The Matrix",
                    "date": "2024-03-20",
                    "time": "14:00",
                    "location": "Grand Cinema City Mall",
                },
                {
                    "title": "The Matrix",
                    "date": "2024-03-20",
                    "time": "17:00",
                    "location": "Grand Cinema City Mall",
                },
                {
                    "title": "The Matrix",
                    "date": "2024-03-20",
                    "time": "20:00",
                    "location": "Grand Cinema City Mall",
                },
                {
                    "title": "The Matrix",
                    "date": "2024-03-21",
                    "time": "14:00",
                    "location": "Grand Cinema City Mall",
                },
                {
                    "title": "The Matrix",
                    "date": "2024-03-21",
                    "time": "17:00",
                    "location": "Grand Cinema City Mall",
                },
                {
                    "title": "The Matrix",
                    "date": "2024-03-21",
                    "time": "20:00",
                    "location": "Grand Cinema City Mall",
                },
                {
                    "title": "Inception",
                    "date": "2024-03-20",
                    "time": "14:00",
                    "location": "Grand Cinema City Mall",
                },
                {
                    "title": "Inception",
                    "date": "2024-03-20",
                    "time": "17:00",
                    "location": "Grand Cinema City Mall",
                },
                {
                    "title": "Inception",
                    "date": "2024-03-20",
                    "time": "20:00",
                    "location": "Grand Cinema City Mall",
                },
                {
                    "title": "Inception",
                    "date": "2024-03-21",
                    "time": "14:00",
                    "location": "Grand Cinema City Mall",
                },
                {
                    "title": "Inception",
                    "date": "2024-03-21",
                    "time": "17:00",
                    "location": "Grand Cinema City Mall",
                },
                {
                    "title": "Inception",
                    "date": "2024-03-21",
                    "time": "20:00",
                    "location": "Grand Cinema City Mall",
                },
            ]
            self.assertEqual(showings, expected_showings)

    def test_get_showings_error(self):
        with patch.object(
            self.service, "get_titles", side_effect=Exception("Test error")
        ):
            with self.assertRaises(ServiceError):
                self.service.get_showings()

    def test_get_titles(self):
        with patch.object(
            self.service.client, "get_titles_page", return_value=self.mock_titles_page
        ), patch.object(
            self.service.parser,
            "parse_titles_from_titles_page",
            return_value=self.mock_titles,
        ):

            titles = self.service.get_titles()
            self.assertEqual(titles, self.mock_titles)

    def test_get_titles_error(self):
        with patch.object(
            self.service.client, "get_titles_page", side_effect=Exception("Test error")
        ):
            with self.assertRaises(ServiceError):
                self.service.get_titles()

    def test_get_showing_dates(self):
        title = {"title": "The Matrix", "grand_id": "1abc"}
        with patch.object(
            self.service.client,
            "get_title_showing_dates",
            return_value=self.mock_dates_page,
        ), patch.object(
            self.service.parser, "parse_showing_dates", return_value=self.mock_dates
        ):

            dates = self.service.get_showing_dates(title)
            self.assertEqual(dates, self.mock_dates)

    def test_get_showing_dates_error(self):
        title = {"title": "The Matrix", "grand_id": "1abc"}
        with patch.object(
            self.service.client,
            "get_title_showing_dates",
            side_effect=Exception("Test error"),
        ):
            with self.assertRaises(ServiceError):
                self.service.get_showing_dates(title)

    def test_get_showing_times(self):
        title = {"title": "The Matrix", "grand_id": "1abc"}
        date = "2024-03-20"
        with patch.object(
            self.service.client,
            "get_title_showing_times_on_date",
            return_value=self.mock_times_page,
        ), patch.object(
            self.service.parser, "parse_showing_times", return_value=self.mock_times
        ):

            times = self.service.get_showing_times(title, date)
            self.assertEqual(times, self.mock_times)

    def test_get_showing_times_error(self):
        title = {"title": "The Matrix", "grand_id": "1abc"}
        date = "2024-03-20"
        with patch.object(
            self.service.client,
            "get_title_showing_times_on_date",
            side_effect=Exception("Test error"),
        ):
            with self.assertRaises(ServiceError):
                self.service.get_showing_times(title, date)


class TestTajService(unittest.TestCase):
    def setUp(self):
        self.service = TajService()
        self.mock_titles = [
            {"title": "The Matrix", "taj_id": "1abc"},
            {"title": "Inception", "taj_id": "2def"},
        ]
        self.mock_showings = [
            {"date": "2024-03-20", "time": "14:00", "date_id": "123"},
            {"date": "2024-03-20", "time": "17:00", "date_id": "123"},
        ]
        self.mock_titles_page = "<html>Mock titles page</html>"
        self.mock_showings_page = "<html>Mock showings page</html>"

    def test_get_showings(self):
        with patch.object(
            self.service, "get_titles", return_value=self.mock_titles
        ), patch.object(
            self.service, "get_title_showings", return_value=self.mock_showings
        ):

            showings = self.service.get_showings()

            expected_showings = [
                {"date": "2024-03-20", "date_id": "123", "time": "14:00"},
                {"date": "2024-03-20", "date_id": "123", "time": "17:00"},
                {"date": "2024-03-20", "date_id": "123", "time": "14:00"},
                {"date": "2024-03-20", "date_id": "123", "time": "17:00"},
            ]
            self.assertEqual(showings, expected_showings)

    def test_get_showings_error(self):
        with patch.object(
            self.service, "get_titles", side_effect=Exception("Test error")
        ):
            with self.assertRaises(ServiceError):
                self.service.get_showings()

    def test_get_titles(self):
        with patch.object(
            self.service.client, "get_titles_page", return_value=self.mock_titles_page
        ), patch.object(
            self.service.parser,
            "parse_titles_from_titles_page",
            return_value=self.mock_titles,
        ):

            titles = self.service.get_titles()
            self.assertEqual(titles, self.mock_titles)

    def test_get_titles_error(self):
        with patch.object(
            self.service.client, "get_titles_page", side_effect=Exception("Test error")
        ):
            with self.assertRaises(ServiceError):
                self.service.get_titles()

    def test_get_title_showings(self):
        title = {"title": "The Matrix", "taj_id": "1abc"}
        with patch.object(
            self.service.client,
            "get_title_showings_page",
            return_value=self.mock_showings_page,
        ), patch.object(
            self.service.parser,
            "parse_showing_dates_from_title_page",
            return_value=["2024-03-20"],
        ), patch.object(
            self.service.parser,
            "parse_showing_times_from_title_page",
            return_value=self.mock_showings,
        ):

            showings = self.service.get_title_showings(title)
            expected_showings = [
                {
                    "title": "The Matrix",
                    "date": "2024-03-20",
                    "time": "14:00",
                    "location": "Taj Mall",
                },
                {
                    "title": "The Matrix",
                    "date": "2024-03-20",
                    "time": "17:00",
                    "location": "Taj Mall",
                },
            ]
            self.assertEqual(showings, expected_showings)

    def test_get_title_showings_error(self):
        title = {"title": "The Matrix", "taj_id": "1abc"}
        with patch.object(
            self.service.client,
            "get_title_showings_page",
            side_effect=Exception("Test error"),
        ):
            with self.assertRaises(ServiceError):
                self.service.get_title_showings(title)


class TestPrimeService(unittest.TestCase):
    def setUp(self):
        self.service = PrimeService()
        self.mock_titles = [
            {"title": "The Matrix", "prime_id": "1abc"},
            {"title": "Inception", "prime_id": "2def"},
        ]
        self.mock_showings = [
            {"date": "2024-03-20", "time": "14:00", "location": "Prime Mall"},
            {"date": "2024-03-20", "time": "17:00", "location": "Prime Mall"},
        ]
        self.mock_titles_page = "<html>Mock titles page</html>"
        self.mock_showings_page = "<html>Mock showings page</html>"

    def test_get_showings(self):
        with patch.object(
            PrimeService, "get_titles", return_value=self.mock_titles
        ), patch.object(
            PrimeService, "get_title_showings", return_value=self.mock_showings
        ):

            showings = self.service.get_showings()

            expected_showings = [
                {"date": "2024-03-20", "location": "Prime Mall", "time": "14:00"},
                {"date": "2024-03-20", "location": "Prime Mall", "time": "17:00"},
                {"date": "2024-03-20", "location": "Prime Mall", "time": "14:00"},
                {"date": "2024-03-20", "location": "Prime Mall", "time": "17:00"},
            ]
            self.assertEqual(showings, expected_showings)

    def test_get_showings_error(self):
        with patch.object(
            PrimeService, "get_titles", side_effect=Exception("Test error")
        ):
            with self.assertRaises(ServiceError):
                self.service.get_showings()

    def test_get_titles(self):
        with patch.object(
            PrimeService.client, "get_titles_page", return_value=self.mock_titles_page
        ), patch.object(
            PrimeService.parser,
            "parse_titles_from_titles_page",
            return_value=self.mock_titles,
        ):

            titles = self.service.get_titles()
            self.assertEqual(titles, self.mock_titles)

    def test_get_titles_error(self):
        with patch.object(
            PrimeService.client, "get_titles_page", side_effect=Exception("Test error")
        ):
            with self.assertRaises(ServiceError):
                self.service.get_titles()

    def test_get_title_showings(self):
        title = {"title": "The Matrix", "prime_id": "1abc"}
        with patch.object(
            PrimeService.client,
            "get_title_showings_page",
            return_value=self.mock_showings_page,
        ), patch.object(
            PrimeService.parser,
            "parse_showings_from_title_page",
            return_value=self.mock_showings,
        ):

            showings = self.service.get_title_showings(title)
            expected_showings = [
                {
                    "title": "1abc",
                    "date": "2024-03-20",
                    "time": "14:00",
                    "location": "Prime Mall",
                },
                {
                    "title": "1abc",
                    "date": "2024-03-20",
                    "time": "17:00",
                    "location": "Prime Mall",
                },
            ]
            self.assertEqual(showings, expected_showings)

    def test_get_title_showings_error(self):
        title = {"title": "The Matrix", "prime_id": "1abc"}
        with patch.object(
            PrimeService.client,
            "get_title_showings_page",
            side_effect=Exception("Test error"),
        ):
            with self.assertRaises(ServiceError):
                self.service.get_title_showings(title)
