import unittest

import pandas as pd
from showings.services import GrandService, PrimeService, TajService, TitleMatchService


class TestTitleMatchService(unittest.TestCase):
    def setUp(self):
        self.raw_title_grand = {"title": "   The Matrix ", "grand_id": "1abc"}
        self.raw_title_prime = {"title": "The Matrix 3", "prime_id": "1yts"}
        self.raw_title_taj = {"title": "THE MATRIX", "taj_id": "2"}

        self.title_grand = {
            "title": "  The Matrix   ",
            "prime_id": "",
            "grand_id": "1abc",
            "taj_id": "",
            "title_grand": "  The Matrix   ",
            "title_prime": "",
            "title_taj": "",
            "normalized_title": "the matrix",
        }
        self.title_prime = {
            "title": "The Matrix 3",
            "prime_id": "1yts",
            "grand_id": "",
            "taj_id": "",
            "title_prime": "The Matrix 3",
            "title_grand": "",
            "title_taj": "",
            "normalized_title": "the matrix 3",
        }
        self.title_taj = {
            "title": "THE MATRIX",
            "prime_id": "",
            "grand_id": "",
            "taj_id": "2",
            "title_prime": "",
            "title_grand": "",
            "title_taj": "THE MATRIX",
            "normalized_title": "the matrix",
        }

        self.merged_title = {
            "title": self.title_prime["title"],
            "prime_id": self.title_prime["prime_id"],
            "grand_id": self.title_grand["grand_id"],
            "taj_id": "",
            "normalized_title": self.title_prime["normalized_title"],
            "title_prime": self.title_prime["title_prime"],
            "title_grand": self.title_grand["title_grand"],
            "title_taj": "",
        }

        self.merged_empty = {
            "title_grand": "",
            "grand_id": "",
            "normalized_title": "",
            "title_prime": "",
            "prime_id": "",
            "title_taj": "",
            "taj_id": "",
            "title": "",
        }

        self.grand_titles = [
            {"title": "   The Matrix ", "grand_id": "1abc"},
            {"title": "Inception   ", "grand_id": "2"},
            {"title": " El Dashash", "grand_id": "3"},
            {"title": "Inception IMAX", "grand_id": "4"},
        ]
        self.prime_titles = [
            {"title": "THE MATRIX", "prime_id": "1yts"},
            {"title": "ALIEN 5", "prime_id": "ahd2"},
            {"title": "AL DESHASH", "prime_id": "bj3h"},
            {"title": "300", "prime_id": "lo5f"},
        ]
        self.taj_titles = [
            {"title": "elDashash ", "taj_id": "1vfda"},
            {"title": "The Matrix Reloaded", "taj_id": "yajg2"},
            {"title": "Alien 5  ", "taj_id": "ad3sa"},
            {"title": "1919", "taj_id": "3hj2"},
        ]

    def test_normalize_title(self):
        self.assertEqual(
            TitleMatchService.normalize_title(self.raw_title_grand["title"]),
            "the matrix",
        )

    def test_handle_raw_titles(self):
        titles = [self.raw_title_grand]
        expected = pd.DataFrame(
            [
                {
                    "title": "   The Matrix ",
                    "grand_id": "1abc",
                    "normalized_title": "the matrix",
                }
            ]
        )
        self.assertEqual(
            pd.DataFrame.equals(TitleMatchService.handle_raw_titles(titles), expected),
            True,
        )

    def test_format_merged_titles(self):
        titles_df = pd.DataFrame([{}])
        expected = [self.merged_empty]
        self.assertEqual(TitleMatchService.format_merged_titles(titles_df), expected)

        titles_df = pd.DataFrame(
            [
                {
                    "title_grand": "   The Matrix ",
                    "grand_id": "1abc",
                    "normalized_title": "the matrix",
                    "title_prime": "THE MATRIX",
                    "prime_id": "1yts",
                }
            ]
        )
        expected = [
            {
                "title_grand": "   The Matrix ",
                "grand_id": "1abc",
                "normalized_title": "the matrix",
                "title_prime": "THE MATRIX",
                "prime_id": "1yts",
                "title_taj": "",
                "taj_id": "",
                "title": "",
            }
        ]
        self.assertEqual(TitleMatchService.format_merged_titles(titles_df), expected)

    def test_get_suffix__empty(self):
        titles_df = pd.DataFrame([{}])
        self.assertRaises(ValueError, TitleMatchService.get_suffix, titles_df)

    def test_get_suffix__merged(self):
        titles_df = pd.DataFrame([self.merged_title])
        self.assertEqual(TitleMatchService.get_suffix(titles_df), "merged")

    def test_get_suffix__grand(self):
        title_a = self.raw_title_grand
        title_a["normalized_title"] = "the matrix"
        titles_df = pd.DataFrame([title_a])
        self.assertEqual(TitleMatchService.get_suffix(titles_df), "grand")

    def test_get_suffix__taj(self):
        title_a = self.raw_title_taj
        title_a["normalized_title"] = "the matrix"
        titles_df = pd.DataFrame([title_a])
        self.assertEqual(TitleMatchService.get_suffix(titles_df), "taj")

    def test_get_suffix__prime(self):
        title_a = self.raw_title_prime
        title_a["normalized_title"] = "the matrix 3"
        titles_df = pd.DataFrame([self.raw_title_prime])
        self.assertEqual(TitleMatchService.get_suffix(titles_df), "prime")

    def test_is_merged_df(self):
        titles_df = pd.DataFrame([self.merged_title])
        self.assertEqual(TitleMatchService.is_merged_df(titles_df), True)

        titles_df = pd.DataFrame([self.raw_title_grand])
        self.assertEqual(TitleMatchService.is_merged_df(titles_df), False)

    def test_should_merge_fuzzy_match_titles(self):
        title_a = {
            "prime_id": "1yts",
            "grand_id": "zc",
            "taj_id": "",
        }
        title_b = {
            "prime_id": "",
            "grand_id": "1abc",
            "taj_id": "1vfda",
        }
        self.assertEqual(
            TitleMatchService.should_merge_fuzzy_match_titles(title_a, title_b), False
        )

        title_a = {
            "prime_id": "1yts",
            "grand_id": "",
            "taj_id": "zzz",
        }
        title_b = {
            "prime_id": "",
            "grand_id": "1abc",
            "taj_id": "",
        }
        self.assertEqual(
            TitleMatchService.should_merge_fuzzy_match_titles(title_a, title_b), True
        )

    # merge_fuzzy_match_titles tests
    def test_merge_fuzzy_match_titles(self):
        title_a = self.title_prime
        title_b = self.title_grand
        expected = {
            "title_grand": "  The Matrix   ",
            "grand_id": "1abc",
            "normalized_title": "the matrix 3",
            "title_prime": "The Matrix 3",
            "prime_id": "1yts",
            "title_taj": "",
            "taj_id": "",
            "title": "The Matrix 3",
        }
        self.assertEqual(
            TitleMatchService.merge_fuzzy_match_titles(title_a, title_b), expected
        )

    def test_merge_fuzzy_match_titles__prioritize_prime(self):
        title_a = self.title_grand
        title_b = self.title_prime
        expected = {
            "title_grand": "  The Matrix   ",
            "grand_id": "1abc",
            "normalized_title": "the matrix 3",
            "title_prime": "The Matrix 3",
            "prime_id": "1yts",
            "title_taj": "",
            "taj_id": "",
            "title": "The Matrix 3",
        }
        self.assertEqual(
            TitleMatchService.merge_fuzzy_match_titles(title_a, title_b), expected
        )

    def test_merge_fuzzy_match_titles__prioritize_merged(self):
        title_a = self.merged_title
        title_b = self.title_taj
        expected = {
            "title_grand": "  The Matrix   ",
            "grand_id": "1abc",
            "normalized_title": "the matrix 3",
            "title_prime": "The Matrix 3",
            "prime_id": "1yts",
            "title_taj": "THE MATRIX",
            "taj_id": "2",
            "title": "The Matrix 3",
        }
        self.assertEqual(
            TitleMatchService.merge_fuzzy_match_titles(title_a, title_b), expected
        )

        title_b = self.merged_title
        title_a = self.title_taj
        expected = {
            "title_grand": "  The Matrix   ",
            "grand_id": "1abc",
            "normalized_title": "the matrix 3",
            "title_prime": "The Matrix 3",
            "prime_id": "1yts",
            "title_taj": "THE MATRIX",
            "taj_id": "2",
            "title": "The Matrix 3",
        }
        self.assertEqual(
            TitleMatchService.merge_fuzzy_match_titles(title_a, title_b), expected
        )

    # handle_perfect_match_titles tests
    def test_handle_perfect_match_titles__no_titles_found(self):
        with self.assertRaises(ValueError):
            TitleMatchService.handle_perfect_match_titles([], [], [])

    def test_handle_perfect_match_titles__merges_empty_titles(self):
        expected = [
            {
                "title": "",
                "grand_id": "1abc",
                "prime_id": "",
                "taj_id": "",
                "normalized_title": "the matrix",
                "title_grand": "   The Matrix ",
                "title_prime": "",
                "title_taj": "",
            }
        ]

        grand_titles = [{"title": "   The Matrix ", "grand_id": "1abc"}]
        prime_titles = []
        taj_titles = []

        merged_titles = TitleMatchService.handle_perfect_match_titles(
            grand_titles, prime_titles, taj_titles
        )
        self.assertEqual(merged_titles, expected)

    def test_handle_perfect_match_titles__merges_matching_titles(self):
        expected = [
            {
                "title": "",
                "grand_id": "1abc",
                "prime_id": "1yts",
                "taj_id": "",
                "normalized_title": "the matrix",
                "title_grand": "   The Matrix ",
                "title_prime": "THE MATRIX",
                "title_taj": "",
            }
        ]

        grand_titles = [{"title": "   The Matrix ", "grand_id": "1abc"}]
        prime_titles = [{"title": "THE MATRIX", "prime_id": "1yts"}]
        taj_titles = []

        merged_titles = TitleMatchService.handle_perfect_match_titles(
            grand_titles, prime_titles, taj_titles
        )
        self.assertEqual(merged_titles, expected)

    def test_handle_perfect_match_titles__merges_titles_when_no_matches_found(self):
        expected = [
            {
                "title": "",
                "grand_id": "",
                "prime_id": "ahd2",
                "taj_id": "",
                "normalized_title": "alien 5",
                "title_grand": "",
                "title_prime": "ALIEN 5",
                "title_taj": "",
            },
            {
                "title": "",
                "grand_id": "1abc",
                "prime_id": "",
                "taj_id": "",
                "normalized_title": "the matrix",
                "title_grand": "   The Matrix ",
                "title_prime": "",
                "title_taj": "",
            },
        ]

        grand_titles = [{"title": "   The Matrix ", "grand_id": "1abc"}]
        prime_titles = [
            {"title": "ALIEN 5", "prime_id": "ahd2"},
        ]

        merged_titles = TitleMatchService.handle_perfect_match_titles(
            grand_titles, prime_titles
        )
        self.assertEqual(merged_titles, expected)

    def test_handle_perfect_match_titles__merges_three_dataframes(self):
        expected = [
            {
                "title": "",
                "grand_id": "1abc",
                "prime_id": "1yts",
                "taj_id": "",
                "normalized_title": "the matrix",
                "title_grand": "   The Matrix ",
                "title_prime": "THE MATRIX",
                "title_taj": "",
            },
            {
                "title": "",
                "grand_id": "",
                "prime_id": "",
                "taj_id": "yajg2",
                "normalized_title": "the matrix reloaded",
                "title_grand": "",
                "title_prime": "",
                "title_taj": "The Matrix Reloaded",
            },
        ]

        grand_titles = [{"title": "   The Matrix ", "grand_id": "1abc"}]
        prime_titles = [{"title": "THE MATRIX", "prime_id": "1yts"}]
        taj_titles = [{"title": "The Matrix Reloaded", "taj_id": "yajg2"}]

        merged_titles = TitleMatchService.handle_perfect_match_titles(
            grand_titles, prime_titles, taj_titles
        )
        self.assertEqual(merged_titles, expected)

    # handle_fuzzy_match_titles tests
    def test_handle_fuzzy_match_titles__no_match_found(self):
        processed_titles = [
            {
                "title": "the matrix",
                "grand_id": "1abc",
                "prime_id": "1yts",
                "taj_id": "",
                "normalized_title": "the matrix",
                "title_grand": "   The Matrix ",
                "title_prime": "THE MATRIX",
                "title_taj": "",
            },
            {
                "title": "the matrix reloaded",
                "grand_id": "",
                "prime_id": "",
                "taj_id": "yajg2",
                "normalized_title": "the matrix reloaded",
                "title_grand": "",
                "title_prime": "",
                "title_taj": "The Matrix Reloaded",
            },
        ]
        self.assertEqual(
            processed_titles,
            TitleMatchService.handle_fuzzy_match_titles(processed_titles),
        )

    def test_handle_fuzzy_match_titles__should_merge_returned_false(self):
        processed_titles = [
            {
                "title": "the matrix",
                "grand_id": "1abc",
                "prime_id": "1yts",
                "taj_id": "",
                "normalized_title": "the matrix",
                "title_grand": "   The Matrix ",
                "title_prime": "THE MATRIX",
                "title_taj": "",
            },
            {
                "title": "the matrix 3",
                "grand_id": "yajg2",
                "prime_id": "",
                "taj_id": "",
                "normalized_title": "the matrix 3",
                "title_grand": "The Matrix 3",
                "title_prime": "",
                "title_taj": "",
            },
        ]
        self.assertEqual(
            processed_titles,
            TitleMatchService.handle_fuzzy_match_titles(processed_titles),
        )

    def test_handle_fuzzy_match_titles__should_merge_returned_true(self):
        processed_titles = [
            {
                "title": "the matrix",
                "grand_id": "1abc",
                "prime_id": "1yts",
                "taj_id": "",
                "normalized_title": "the matrix",
                "title_grand": "   The Matrix ",
                "title_prime": "THE MATRIX",
                "title_taj": "",
            },
            {
                "title": "the matrix 3",
                "grand_id": "",
                "prime_id": "",
                "taj_id": "yajg2",
                "normalized_title": "the matrix 3",
                "title_grand": "",
                "title_prime": "",
                "title_taj": "The Matrix 3",
            },
        ]

        expected = [
            {
                "title": "the matrix",
                "grand_id": "1abc",
                "prime_id": "1yts",
                "taj_id": "yajg2",
                "normalized_title": "the matrix",
                "title_grand": "   The Matrix ",
                "title_prime": "THE MATRIX",
                "title_taj": "The Matrix 3",
            }
        ]

        self.assertEqual(
            TitleMatchService.handle_fuzzy_match_titles(processed_titles), expected
        )

    # match_titles tests
    def test_match_titles__no_titles_found(self):
        with self.assertRaises(ValueError):
            TitleMatchService.match_titles([], [], [])

    def test_match_titles(self):
        grand_titles = self.grand_titles
        prime_titles = self.prime_titles
        taj_titles = self.taj_titles

        expected = [
            {
                "grand_id": "3",
                "normalized_title": "eldashash",
                "prime_id": "bj3h",
                "taj_id": "1vfda",
                "title": "",
                "title_grand": " El Dashash",
                "title_prime": "AL DESHASH",
                "title_taj": "elDashash ",
            },
            {
                "grand_id": "2",
                "normalized_title": "inception",
                "prime_id": "",
                "taj_id": "",
                "title": "",
                "title_grand": "Inception   ",
                "title_prime": "",
                "title_taj": "",
            },
            {
                "grand_id": "4",
                "normalized_title": "inception imax",
                "prime_id": "",
                "taj_id": "",
                "title": "",
                "title_grand": "Inception IMAX",
                "title_prime": "",
                "title_taj": "",
            },
            {
                "grand_id": "",
                "normalized_title": "1919",
                "prime_id": "",
                "taj_id": "3hj2",
                "title": "",
                "title_grand": "",
                "title_prime": "",
                "title_taj": "1919",
            },
            {
                "grand_id": "",
                "normalized_title": "300",
                "prime_id": "lo5f",
                "taj_id": "",
                "title": "",
                "title_grand": "",
                "title_prime": "300",
                "title_taj": "",
            },
            {
                "grand_id": "",
                "normalized_title": "alien 5",
                "prime_id": "ahd2",
                "taj_id": "ad3sa",
                "title": "",
                "title_grand": "",
                "title_prime": "ALIEN 5",
                "title_taj": "Alien 5  ",
            },
            {
                "grand_id": "1abc",
                "normalized_title": "the matrix",
                "prime_id": "1yts",
                "taj_id": "",
                "title": "",
                "title_grand": "   The Matrix ",
                "title_prime": "THE MATRIX",
                "title_taj": "",
            },
            {
                "grand_id": "",
                "normalized_title": "the matrix reloaded",
                "prime_id": "",
                "taj_id": "yajg2",
                "title": "",
                "title_grand": "",
                "title_prime": "",
                "title_taj": "The Matrix Reloaded",
            },
        ]

        self.assertEqual(
            TitleMatchService.match_titles(grand_titles, prime_titles, taj_titles),
            expected,
        )


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
            with self.assertRaises(GrandService.GrandServiceError):
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
            with self.assertRaises(GrandService.GrandServiceError):
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
            with self.assertRaises(GrandService.GrandServiceError):
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
            with self.assertRaises(GrandService.GrandServiceError):
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
            with self.assertRaises(TajService.TajServiceError):
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
            with self.assertRaises(TajService.TajServiceError):
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
            with self.assertRaises(TajService.TajServiceError):
                TajService.get_title_showings(title)


class TestPrimeService(unittest.TestCase):
    def setUp(self):
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

            showings = PrimeService.get_showings()

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
            with self.assertRaises(PrimeService.PrimeServiceError):
                PrimeService.get_showings()

    def test_get_titles(self):
        with unittest.mock.patch.object(
            PrimeService.client, "get_titles_page", return_value=self.mock_titles_page
        ), unittest.mock.patch.object(
            PrimeService.parser,
            "parse_titles_from_titles_page",
            return_value=self.mock_titles,
        ):

            titles = PrimeService.get_titles()
            self.assertEqual(titles, self.mock_titles)

    def test_get_titles_error(self):
        with unittest.mock.patch.object(
            PrimeService.client, "get_titles_page", side_effect=Exception("Test error")
        ):
            with self.assertRaises(PrimeService.PrimeServiceError):
                PrimeService.get_titles()

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

            showings = PrimeService.get_title_showings(title)
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
            with self.assertRaises(PrimeService.PrimeServiceError):
                PrimeService.get_title_showings(title)
