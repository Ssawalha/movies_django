from unittest.mock import Mock, patch

import requests
from django.test import TestCase
from movie_showings.settings import GRAND_BASE_URL, PRIME_BASE_URL, TAJ_BASE_URL
from showings.clients import GrandClient, PrimeClient, TajClient


class BaseClientTestCase(TestCase):
    def setUp(self):
        self.mock_response = Mock()
        self.mock_response.content = b"mock content"
        self.mock_response.raise_for_status = Mock()
        self.mock_response.status_code = 200

    def create_error_response(self, status_code, error_message):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            error_message
        )
        return mock_response

    def assert_successful_response(self, result):
        self.assertEqual(result, b"mock content")


class TestGrandClient(BaseClientTestCase):
    def setUp(self):
        super().setUp()
        self.client = GrandClient()

    @patch("requests.post")
    def test_get_titles_page_success(self, mock_post):
        mock_post.return_value = self.mock_response
        result = self.client.get_titles_page()
        mock_post.assert_called_once_with(
            f"{GRAND_BASE_URL}/handlers/getmovies.ashx", data={"cinemaId": "0000000002"}
        )
        self.assert_successful_response(result)

    @patch("requests.post")
    def test_get_titles_page_404(self, mock_post):
        mock_post.return_value = self.create_error_response(404, "404 Client Error")
        with self.assertRaises(GrandClient.GrandClientError):
            self.client.get_titles_page()

    @patch("requests.post")
    def test_get_titles_page_500(self, mock_post):
        mock_post.return_value = self.create_error_response(500, "500 Server Error")
        with self.assertRaises(GrandClient.GrandClientError):
            self.client.get_titles_page()

    @patch("requests.post")
    def test_get_titles_page_error(self, mock_post):
        mock_post.side_effect = Exception("Network error")
        with self.assertRaises(GrandClient.GrandClientError):
            self.client.get_titles_page()

    @patch("requests.post")
    def test_get_title_showing_dates_success(self, mock_post):
        mock_post.return_value = self.mock_response
        grand_title_id = "12345"
        result = self.client.get_title_showing_dates(grand_title_id)
        mock_post.assert_called_once_with(
            f"{GRAND_BASE_URL}/handlers/getsessionDate.ashx",
            data={
                "cinemaId": "0000000002",
                "movieId": grand_title_id,
            },
        )
        self.assert_successful_response(result)

    @patch("requests.post")
    def test_get_title_showing_times_on_date_success(self, mock_post):
        mock_post.return_value = self.mock_response
        grand_title_id = "12345"
        date = "2024-03-21"
        result = self.client.get_title_showing_times_on_date(grand_title_id, date)
        mock_post.assert_called_once_with(
            f"{GRAND_BASE_URL}/handlers/getsessionTime.ashx",
            data={"cinemaId": "0000000002", "movieId": grand_title_id, "date": date},
        )
        self.assert_successful_response(result)


class TestTajClient(BaseClientTestCase):
    def setUp(self):
        super().setUp()
        self.client = TajClient()

    @patch("requests.get")
    def test_get_titles_page_success(self, mock_get):
        mock_get.return_value = self.mock_response
        result = self.client.get_titles_page()
        mock_get.assert_called_once_with(TAJ_BASE_URL)
        self.assert_successful_response(result)

    @patch("requests.get")
    def test_get_titles_page_404(self, mock_get):
        mock_get.return_value = self.create_error_response(404, "404 Client Error")
        with self.assertRaises(TajClient.TajClientError):
            self.client.get_titles_page()

    @patch("requests.get")
    def test_get_titles_page_500(self, mock_get):
        mock_get.return_value = self.create_error_response(500, "500 Server Error")
        with self.assertRaises(TajClient.TajClientError):
            self.client.get_titles_page()

    @patch("requests.get")
    def test_get_titles_page_error(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        with self.assertRaises(TajClient.TajClientError):
            self.client.get_titles_page()

    @patch("requests.get")
    def test_get_title_showings_page_success(self, mock_get):
        mock_get.return_value = self.mock_response
        title = {"taj_id": "12345"}
        result = self.client.get_title_showings_page(title)
        mock_get.assert_called_once_with(f"{TAJ_BASE_URL}/movies/12345")
        self.assert_successful_response(result)


class TestPrimeClient(BaseClientTestCase):
    def setUp(self):
        super().setUp()
        self.client = PrimeClient()

    @patch("requests.get")
    def test_get_titles_page_success(self, mock_get):
        mock_get.return_value = self.mock_response
        result = self.client.get_titles_page()
        mock_get.assert_called_once_with(f"{PRIME_BASE_URL}/Browsing/Movies/NowShowing")
        self.assert_successful_response(result)

    @patch("requests.get")
    def test_get_titles_page_404(self, mock_get):
        mock_get.return_value = self.create_error_response(404, "404 Client Error")
        with self.assertRaises(PrimeClient.PrimeClientError):
            self.client.get_titles_page()

    @patch("requests.get")
    def test_get_titles_page_500(self, mock_get):
        mock_get.return_value = self.create_error_response(500, "500 Server Error")
        with self.assertRaises(PrimeClient.PrimeClientError):
            self.client.get_titles_page()

    @patch("requests.get")
    def test_get_titles_page_error(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        with self.assertRaises(PrimeClient.PrimeClientError):
            self.client.get_titles_page()

    @patch("requests.get")
    def test_get_title_showings_page_success(self, mock_get):
        mock_get.return_value = self.mock_response
        title = {"title_id": "12345"}
        result = self.client.get_title_showings_page(title)
        mock_get.assert_called_once_with(
            f"{PRIME_BASE_URL}/Browsing/Movies/Details/12345"
        )
        self.assert_successful_response(result)
