from unittest.mock import Mock, patch

import requests
from django.test import TestCase
from movie_showings.settings import GRAND_BASE_URL, PRIME_BASE_URL, TAJ_BASE_URL
from requests import Response
from requests.status_codes import codes
from showings.clients import GrandClient, PrimeClient, TajClient
from showings.errors import ClientError, HTTPClientError, NetworkError


class BaseClientTestCase(TestCase):
    def setUp(self):
        self.mock_response = Mock()
        self.mock_response.content = b"mock content"
        self.mock_response.raise_for_status = Mock()
        self.mock_response.status_code = codes["ok"]

    def create_error_response(self, status_code, error_message):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.content = b"error content"
        mock_response.raise_for_status = Mock(
            side_effect=requests.exceptions.HTTPError(
                error_message, response=mock_response
            )
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
    def test_get_titles_page_http_error(self, mock_post):
        mock_response = self.create_error_response(codes["not_found"], "404 Not Found")
        mock_post.return_value = mock_response
        with self.assertRaises(HTTPClientError) as exc_info:
            self.client.get_titles_page()
        self.assertEqual(
            str(exc_info.exception),
            "[GrandClient] http_error: HTTP 404 - 404 Not Found",
        )

    @patch("requests.post")
    def test_get_titles_page_network_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException(
            "Connection refused"
        )
        with self.assertRaises(NetworkError) as exc_info:
            self.client.get_titles_page()
        self.assertEqual(
            str(exc_info.exception),
            "[GrandClient] network_error: Network error - Connection refused",
        )

    @patch("requests.post")
    def test_get_title_showing_dates_success(self, mock_post):
        mock_post.return_value = self.mock_response
        result = self.client.get_title_showing_dates("grand_id")
        mock_post.assert_called_once_with(
            f"{GRAND_BASE_URL}/handlers/getsessionDate.ashx",
            data={"cinemaId": "0000000002", "movieId": "grand_id"},
        )
        self.assert_successful_response(result)

    @patch("requests.post")
    def test_get_title_showing_times_on_date_success(self, mock_post):
        mock_post.return_value = self.mock_response
        result = self.client.get_title_showing_times_on_date("123", "2024-03-20")
        mock_post.assert_called_once_with(
            f"{GRAND_BASE_URL}/handlers/getsessionTime.ashx",
            data={"cinemaId": "0000000002", "movieId": "123", "date": "2024-03-20"},
        )
        self.assert_successful_response(result)

    @patch("requests.post")
    def test_get_title_showing_dates_validation_error(self, mock_post):
        # Test with invalid data (empty string)
        with self.assertRaises(ClientError) as exc_info:
            self.client.get_title_showing_dates("")
        self.assertEqual(
            str(exc_info.exception),
            "[GrandClient] client_error: Validation error: {'grand_id': [ErrorDetail(string='This field cannot be empty.', code='blank')]}",
        )
        mock_post.assert_not_called()  # Verify no HTTP request was made


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
    def test_get_titles_page_http_error(self, mock_get):
        mock_response = self.create_error_response(404, "404 Not Found")
        mock_get.return_value = mock_response
        with self.assertRaises(HTTPClientError) as exc_info:
            self.client.get_titles_page()
        self.assertEqual(
            str(exc_info.exception),
            "[TajClient] http_error: HTTP 404 - 404 Not Found",
        )

    @patch("requests.get")
    def test_get_title_showings_page_success(self, mock_get):
        mock_get.return_value = self.mock_response
        result = self.client.get_title_showings_page({"taj_id": "456"})
        mock_get.assert_called_once_with(f"{TAJ_BASE_URL}/movies/456")
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
    def test_get_titles_page_http_error(self, mock_get):
        mock_response = self.create_error_response(404, "404 Not Found")
        mock_get.return_value = mock_response
        with self.assertRaises(HTTPClientError) as exc_info:
            self.client.get_titles_page()
        self.assertEqual(
            str(exc_info.exception),
            "[PrimeClient] http_error: HTTP 404 - 404 Not Found",
        )

    @patch("requests.get")
    def test_get_title_showings_page_success(self, mock_get):
        mock_get.return_value = self.mock_response
        result = self.client.get_title_showings_page({"prime_id": "789"})
        mock_get.assert_called_once_with(
            f"{PRIME_BASE_URL}/Browsing/Movies/Details/789"
        )
        self.assert_successful_response(result)
