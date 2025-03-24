import unittest
from unittest.mock import Mock, patch

from rest_framework import serializers
from showings.clients import ClientError, HTTPClientError, NetworkError
from showings.errors import Error, ParserError, ServiceError
from showings.service_base import ServiceWrapper, handle_errors, handle_service_errors


class MockClient:
    def get_titles_page(self) -> bytes:
        return b"mock titles"

    def get_title_showing_dates(self, title_id: str) -> bytes:
        return b"mock dates"

    def get_title_showing_times_on_date(self, title_id: str, date: str) -> bytes:
        return b"mock times"

    def get_title_showings_page(self, title: dict) -> bytes:
        return b"mock showings"


class MockParser:
    def parse_titles_from_titles_page(self, content: bytes) -> list:
        return ["mock title"]

    def parse_showing_dates(self, content: bytes) -> list:
        return ["2024-01-01"]

    def parse_showing_times(self, content: bytes) -> list:
        return ["10:00"]

    def parse_showings_from_title_page(self, content: bytes) -> list:
        return [{"time": "10:00", "date": "2024-01-01"}]


class TestServiceWrapper(unittest.TestCase):
    def setUp(self):
        self.client = MockClient()
        self.parser = MockParser()
        self.service = ServiceWrapper(self.client, self.parser)

    def test_init(self):
        """Test ServiceWrapper initialization."""
        self.assertEqual(self.service.client, self.client)
        self.assertEqual(self.service.parser, self.parser)


class TestHandleErrors(unittest.TestCase):
    def setUp(self):
        self.mock_logger = Mock()
        self.patcher = patch("showings.service_base.logger", self.mock_logger)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_handle_errors_success(self):
        """Test handle_errors decorator with successful function."""

        @handle_errors("TestService", ServiceError)
        def test_func():
            return "success"

        result = test_func()
        self.assertEqual(result, "success")
        self.mock_logger.error.assert_not_called()

    def test_handle_errors_with_error(self):
        """Test handle_errors decorator with error."""

        @handle_errors("TestService", ServiceError)
        def test_func():
            raise ValueError("test error")

        with self.assertRaises(ServiceError) as context:
            test_func()

        self.assertEqual(
            str(context.exception), "[TestService] service_error: test error"
        )
        self.assertEqual(context.exception.source, "TestService")
        self.mock_logger.error.assert_called_once()

    def test_handle_errors_with_service_error(self):
        """Test handle_errors decorator with ServiceError."""
        error = ServiceError("test error", source="OtherService")

        @handle_errors("TestService", ServiceError)
        def test_func():
            raise error

        with self.assertRaises(ServiceError) as context:
            test_func()

        self.assertEqual(context.exception, error)
        self.mock_logger.error.assert_called_once()


class TestHandleServiceErrors(unittest.TestCase):
    def setUp(self):
        self.mock_logger = Mock()
        self.patcher = patch("showings.service_base.logger", self.mock_logger)
        self.patcher.start()
        self.service = ServiceWrapper(MockClient(), MockParser())

    def tearDown(self):
        self.patcher.stop()

    def test_handle_service_errors_success(self):
        """Test handle_service_errors decorator with successful function."""

        @handle_service_errors("test_operation", "TestService")
        def test_func(self):
            return "success"

        result = test_func(self.service)
        self.assertEqual(result, "success")
        self.mock_logger.error.assert_not_called()

    def test_handle_service_errors_with_http_error(self):
        """Test handle_service_errors decorator with HTTPClientError."""
        error = HTTPClientError("test error", status_code=404)

        @handle_service_errors("test_operation", "TestService")
        def test_func(self):
            raise error

        with self.assertRaises(ServiceError) as context:
            test_func(self.service)

        self.assertIn("HTTP error", str(context.exception))
        self.assertEqual(context.exception.source, "TestService")
        self.assertIn("HTTP 404", str(context.exception))
        self.mock_logger.error.assert_called_once()

    def test_handle_service_errors_with_network_error(self):
        """Test handle_service_errors decorator with NetworkError."""
        error = NetworkError("test error")

        @handle_service_errors("test_operation", "TestService")
        def test_func(self):
            raise error

        with self.assertRaises(ServiceError) as context:
            test_func(self.service)

        self.assertIn("Network error", str(context.exception))
        self.assertEqual(context.exception.source, "TestService")
        self.mock_logger.error.assert_called_once()

    def test_handle_service_errors_with_client_error(self):
        """Test handle_service_errors decorator with ClientError."""
        error = ClientError("test error")

        @handle_service_errors("test_operation", "TestService")
        def test_func(self):
            raise error

        with self.assertRaises(ServiceError) as context:
            test_func(self.service)

        self.assertIn("Client error", str(context.exception))
        self.assertEqual(context.exception.source, "TestService")
        self.mock_logger.error.assert_called_once_with(
            "Client error during test_operation",
            extra={
                "client": "MockClient",
                "error": str(error),
            },
            exc_info=True,
        )

    def test_handle_service_errors_with_parser_error(self):
        """Test handle_service_errors decorator with ParserError."""
        error = ParserError("test error")

        @handle_service_errors("test_operation", "TestService")
        def test_func(self):
            raise error

        with self.assertRaises(ServiceError) as context:
            test_func(self.service)

        self.assertIn("Parser error", str(context.exception))
        self.assertEqual(context.exception.source, "TestService")
        self.mock_logger.error.assert_called_once()

    def test_handle_service_errors_with_validation_error(self):
        """Test handle_service_errors decorator with ValidationError."""
        error = serializers.ValidationError("test error")

        @handle_service_errors("test_operation", "TestService")
        def test_func(self):
            raise error

        with self.assertRaises(ServiceError) as context:
            test_func(self.service)

        self.assertIn("Validation error", str(context.exception))
        self.assertEqual(context.exception.source, "TestService")
        self.mock_logger.warning.assert_called_once()

    def test_handle_service_errors_with_unexpected_error(self):
        """Test handle_service_errors decorator with unexpected error."""
        error = Exception("test error")

        @handle_service_errors("test_operation", "TestService")
        def test_func(self):
            raise error

        with self.assertRaises(ServiceError) as context:
            test_func(self.service)

        self.assertIn("Unexpected error", str(context.exception))
        self.assertEqual(context.exception.source, "TestService")
        self.mock_logger.error.assert_called_once()

    def test_handle_service_errors_with_service_error(self):
        """Test handle_service_errors decorator with ServiceError."""
        error = ServiceError("test error", source="OtherService")

        @handle_service_errors("test_operation", "TestService")
        def test_func(self):
            raise error

        with self.assertRaises(ServiceError) as context:
            test_func(self.service)

        self.assertEqual(context.exception, error)
        # Should not log since we're just re-raising the ServiceError
        self.mock_logger.error.assert_not_called()
