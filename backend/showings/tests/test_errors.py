from django.test import TestCase
from showings.errors import (
    ClientError,
    Error,
    HTTPClientError,
    NetworkError,
    ParserError,
    SerializerError,
    ServiceError,
    ValidationError,
)


class TestBaseError(TestCase):
    """Test the base Error class functionality."""

    def test_error_initialization(self):
        original_error = Exception("original error")
        error = Error(
            message="test message",
            code="test_code",
            details={"key": "value"},
            source="TestSource",
            cause=original_error,
        )
        self.assertEqual(error.message, "test message")
        self.assertEqual(error.code, "test_code")
        self.assertEqual(error.details, {"key": "value"})
        self.assertEqual(error.source, "TestSource")
        self.assertEqual(str(error.cause), str(original_error))
        self.assertEqual(str(error), "[TestSource] test_code: test message")

    def test_error_without_optional_fields(self):
        error = Error(message="test message")
        self.assertEqual(error.code, "error")
        self.assertEqual(error.details, {})
        self.assertEqual(error.source, None)
        self.assertEqual(error.cause, None)
        self.assertEqual(str(error), "error: test message")

    def test_error_with_details(self):
        error = Error(
            message="test message",
            details={"field": "value", "count": 42},
        )
        self.assertEqual(error.details["field"], "value")
        self.assertEqual(error.details["count"], 42)


class TestServiceError(TestCase):
    """Test the ServiceError class and its subclasses."""

    def test_service_error_initialization(self):
        original_error = Exception("original error")
        error = ServiceError(
            message="test message",
            source="TestService",
            cause=original_error,
        )
        self.assertEqual(error.message, "test message")
        self.assertEqual(error.source, "TestService")
        self.assertEqual(str(error.cause), str(original_error))
        self.assertEqual(str(error), "[TestService] service_error: test message")

    def test_service_error_source_from_cause(self):
        class TestService:
            pass

        error = ServiceError(
            message="test message",
            cause=TestService(),
        )
        self.assertEqual(error.source, "TestService")

    def test_service_error_without_source_or_cause(self):
        error = ServiceError(message="test message")
        self.assertEqual(error.source, None)
        self.assertEqual(error.cause, None)
        self.assertEqual(str(error), "service_error: test message")


class TestClientErrors(TestCase):
    """Test client-related error classes."""

    def test_client_error_initialization(self):
        original_error = Exception("original error")
        error = ClientError(
            message="test message",
            source="TestClient",
            cause=original_error,
        )
        self.assertEqual(error.message, "test message")
        self.assertEqual(error.source, "TestClient")
        self.assertEqual(error.code, "client_error")
        self.assertEqual(str(error.cause), str(original_error))
        self.assertEqual(str(error), "[TestClient] client_error: test message")

    def test_http_client_error_initialization(self):
        original_error = Exception("original error")
        error = HTTPClientError(
            message="Not Found",
            status_code=404,
            source="TestClient",
            cause=original_error,
        )
        self.assertEqual(error.message, "HTTP 404 - Not Found")
        self.assertEqual(error.source, "TestClient")
        self.assertEqual(error.code, "http_error")
        self.assertEqual(error.details["status_code"], 404)
        self.assertEqual(str(error.cause), str(original_error))
        self.assertEqual(str(error), "[TestClient] http_error: HTTP 404 - Not Found")

    def test_network_error_initialization(self):
        original_error = Exception("original error")
        error = NetworkError(
            message="Connection refused",
            source="TestClient",
            cause=original_error,
        )
        self.assertEqual(error.message, "Network error - Connection refused")
        self.assertEqual(error.source, "TestClient")
        self.assertEqual(error.code, "network_error")
        self.assertEqual(str(error.cause), str(original_error))
        self.assertEqual(
            str(error), "[TestClient] network_error: Network error - Connection refused"
        )


class TestParserAndValidationErrors(TestCase):
    """Test parser and validation error classes."""

    def test_parser_error_initialization(self):
        original_error = Exception("original error")
        error = ParserError(
            message="test message",
            source="TestParser",
            cause=original_error,
        )
        self.assertEqual(error.message, "test message")
        self.assertEqual(error.source, "TestParser")
        self.assertEqual(error.code, "parser_error")
        self.assertEqual(str(error.cause), str(original_error))
        self.assertEqual(str(error), "[TestParser] parser_error: test message")

    def test_validation_error_initialization(self):
        original_error = Exception("original error")
        error = ValidationError(
            message="test message",
            source="TestValidator",
            cause=original_error,
        )
        self.assertEqual(error.message, "test message")
        self.assertEqual(error.source, "TestValidator")
        self.assertEqual(error.code, "validation_error")
        self.assertEqual(str(error.cause), str(original_error))
        self.assertEqual(str(error), "[TestValidator] validation_error: test message")

    def test_validation_error_with_details(self):
        error = ValidationError(
            message="test message",
            details={"field": ["error1", "error2"]},
            source="TestValidator",
        )
        self.assertEqual(error.details["field"], ["error1", "error2"])


class TestSerializerError(TestCase):
    """Test serializer error class."""

    def test_serializer_error_initialization(self):
        original_error = Exception("original error")
        error = SerializerError(
            message="test message",
            source="TestSerializer",
            cause=original_error,
        )
        self.assertEqual(error.message, "test message")
        self.assertEqual(error.source, "TestSerializer")
        self.assertEqual(error.code, "serializer_error")
        self.assertEqual(str(error.cause), str(original_error))
        self.assertEqual(str(error), "[TestSerializer] serializer_error: test message")

    def test_serializer_error_with_details(self):
        error = SerializerError(
            message="test message",
            details={"field": "value"},
            source="TestSerializer",
        )
        self.assertEqual(error.details["field"], "value")
