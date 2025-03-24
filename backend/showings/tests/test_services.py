import unittest

from showings.errors import ServiceError
from showings.services import GrandService, PrimeService, TajService


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

    def test_get_showings(self):
        with unittest.mock.patch.object(
            GrandService, "get_titles", return_value=self.mock_titles
        ), unittest.mock.patch.object(
            GrandService, "get_showing_dates", return_value=self.mock_dates
        ), unittest.mock.patch.object(
            GrandService, "get_showing_times", return_value=self.mock_times
        ):

            showings = GrandService.get_showings()

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
        with unittest.mock.patch.object(
            GrandService, "get_titles", side_effect=Exception("Test error")
        ):
            with self.assertRaises(ServiceError):
                GrandService.get_showings()

    def test_get_titles(self):
        with unittest.mock.patch.object(
            GrandService.client, "get_titles_page", return_value=self.mock_titles_page
        ), unittest.mock.patch.object(
            GrandService.parser,
            "parse_titles_from_titles_page",
            return_value=self.mock_titles,
        ):

            titles = GrandService.get_titles()
            self.assertEqual(titles, self.mock_titles)

    def test_get_titles_error(self):
        with unittest.mock.patch.object(
            GrandService.client, "get_titles_page", side_effect=Exception("Test error")
        ):
            with self.assertRaises(ServiceError):
                GrandService.get_titles()

    def test_get_showing_dates(self):
        title = {"title": "The Matrix", "grand_id": "1abc"}
        with unittest.mock.patch.object(
            GrandService.client,
            "get_title_showing_dates",
            return_value=self.mock_dates_page,
        ), unittest.mock.patch.object(
            GrandService.parser, "parse_showing_dates", return_value=self.mock_dates
        ):

            dates = GrandService.get_showing_dates(title)
            self.assertEqual(dates, self.mock_dates)

    def test_get_showing_dates_error(self):
        title = {"title": "The Matrix", "grand_id": "1abc"}
        with unittest.mock.patch.object(
            GrandService.client,
            "get_title_showing_dates",
            side_effect=Exception("Test error"),
        ):
            with self.assertRaises(ServiceError):
                GrandService.get_showing_dates(title)

    def test_get_showing_times(self):
        title = {"title": "The Matrix", "grand_id": "1abc"}
        date = "2024-03-20"
        with unittest.mock.patch.object(
            GrandService.client,
            "get_title_showing_times_on_date",
            return_value=self.mock_times_page,
        ), unittest.mock.patch.object(
            GrandService.parser, "parse_showing_times", return_value=self.mock_times
        ):

            times = GrandService.get_showing_times(title, date)
            self.assertEqual(times, self.mock_times)

    def test_get_showing_times_error(self):
        title = {"title": "The Matrix", "grand_id": "1abc"}
        date = "2024-03-20"
        with unittest.mock.patch.object(
            GrandService.client,
            "get_title_showing_times_on_date",
            side_effect=Exception("Test error"),
        ):
            with self.assertRaises(ServiceError):
                GrandService.get_showing_times(title, date)


class TestTajService(unittest.TestCase):
    def setUp(self):
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
        with unittest.mock.patch.object(
            TajService, "get_titles", return_value=self.mock_titles
        ), unittest.mock.patch.object(
            TajService, "get_title_showings", return_value=self.mock_showings
        ):

            showings = TajService.get_showings()

            expected_showings = [
                {"date": "2024-03-20", "date_id": "123", "time": "14:00"},
                {"date": "2024-03-20", "date_id": "123", "time": "17:00"},
                {"date": "2024-03-20", "date_id": "123", "time": "14:00"},
                {"date": "2024-03-20", "date_id": "123", "time": "17:00"},
            ]
            self.assertEqual(showings, expected_showings)

    def test_get_showings_error(self):
        with unittest.mock.patch.object(
            TajService, "get_titles", side_effect=Exception("Test error")
        ):
            with self.assertRaises(ServiceError):
                TajService.get_showings()

    def test_get_titles(self):
        with unittest.mock.patch.object(
            TajService.client, "get_titles_page", return_value=self.mock_titles_page
        ), unittest.mock.patch.object(
            TajService.parser,
            "parse_titles_from_titles_page",
            return_value=self.mock_titles,
        ):

            titles = TajService.get_titles()
            self.assertEqual(titles, self.mock_titles)

    def test_get_titles_error(self):
        with unittest.mock.patch.object(
            TajService.client, "get_titles_page", side_effect=Exception("Test error")
        ):
            with self.assertRaises(ServiceError):
                TajService.get_titles()

    def test_get_title_showings(self):
        title = {"title": "The Matrix", "taj_id": "1abc"}
        with unittest.mock.patch.object(
            TajService.client,
            "get_title_showings_page",
            return_value=self.mock_showings_page,
        ), unittest.mock.patch.object(
            TajService.parser,
            "parse_showing_dates_from_title_page",
            return_value=["2024-03-20"],
        ), unittest.mock.patch.object(
            TajService.parser,
            "parse_showing_times_from_title_page",
            return_value=self.mock_showings,
        ):

            showings = TajService.get_title_showings(title)
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
        with unittest.mock.patch.object(
            TajService.client,
            "get_title_showings_page",
            side_effect=Exception("Test error"),
        ):
            with self.assertRaises(ServiceError):
                TajService.get_title_showings(title)


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
        with unittest.mock.patch.object(
            PrimeService, "get_titles", return_value=self.mock_titles
        ), unittest.mock.patch.object(
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
        with unittest.mock.patch.object(
            PrimeService, "get_titles", side_effect=Exception("Test error")
        ):
            with self.assertRaises(ServiceError):
                self.service.get_showings()

    def test_get_titles(self):
        with unittest.mock.patch.object(
            PrimeService.client, "get_titles_page", return_value=self.mock_titles_page
        ), unittest.mock.patch.object(
            PrimeService.parser,
            "parse_titles_from_titles_page",
            return_value=self.mock_titles,
        ):

            titles = self.service.get_titles()
            self.assertEqual(titles, self.mock_titles)

    def test_get_titles_error(self):
        with unittest.mock.patch.object(
            PrimeService.client, "get_titles_page", side_effect=Exception("Test error")
        ):
            with self.assertRaises(ServiceError):
                self.service.get_titles()

    def test_get_title_showings(self):
        title = {"title": "The Matrix", "prime_id": "1abc"}
        with unittest.mock.patch.object(
            PrimeService.client,
            "get_title_showings_page",
            return_value=self.mock_showings_page,
        ), unittest.mock.patch.object(
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
        with unittest.mock.patch.object(
            PrimeService.client,
            "get_title_showings_page",
            side_effect=Exception("Test error"),
        ):
            with self.assertRaises(ServiceError):
                self.service.get_title_showings(title)
