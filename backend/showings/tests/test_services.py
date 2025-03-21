import unittest

import pandas as pd
from showings.services import TitleMatchService


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
