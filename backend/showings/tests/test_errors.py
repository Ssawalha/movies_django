from django.test import TestCase
from showings.errors import (
    ClientError,
    ElementNotFoundError,
    Error,
    ErrorCode,
    HTTPClientError,
    InvalidFormatError,
    NetworkError,
    ParserError,
    SerializerError,
    ServiceError,
)


class TestErrorCode(TestCase):
    """Test the ErrorCode class and its constants."""

    def test_error_codes(self):
        """Test that all error codes are defined and have correct values."""
        self.assertEqual(ErrorCode.SERVICE_ERROR, "service_error")
        self.assertEqual(ErrorCode.CLIENT_ERROR, "client_error")
        self.assertEqual(ErrorCode.PARSER_ERROR, "parser_error")
        self.assertEqual(ErrorCode.VALIDATION_ERROR, "validation_error")
        self.assertEqual(ErrorCode.HTTP_ERROR, "http_error")
        self.assertEqual(ErrorCode.NETWORK_ERROR, "network_error")
        self.assertEqual(ErrorCode.ELEMENT_NOT_FOUND, "element_not_found")
        self.assertEqual(ErrorCode.INVALID_FORMAT, "invalid_format")


class TestBaseError(TestCase):
    """Test the base Error class functionality."""

    def test_error_initialization(self):
        """Test error initialization with all fields."""
        original_error = Exception("original error")
        error = Error(
            message="test message",
            code=ErrorCode.SERVICE_ERROR,
            details={"key": "value"},
            source="TestSource",
            cause=original_error,
        )
        self.assertEqual(error.message, "test message")
        self.assertEqual(error.code, ErrorCode.SERVICE_ERROR)
        self.assertEqual(error.details, {"key": "value"})
        self.assertEqual(error.source, "TestSource")
        self.assertEqual(error.cause, original_error)
        self.assertEqual(str(error), "[TestSource] service_error: test message")

    def test_error_without_optional_fields(self):
        """Test error initialization with only required fields."""
        error = Error(message="test message")
        self.assertEqual(error.code, ErrorCode.SERVICE_ERROR)
        self.assertEqual(error.details, {})
        self.assertEqual(error.source, None)
        self.assertEqual(error.cause, None)
        self.assertEqual(str(error), "service_error: test message")

    def test_error_with_details(self):
        """Test error with details dictionary."""
        error = Error(
            message="test message",
            details={"field": "value", "count": 42},
        )
        self.assertEqual(error.details["field"], "value")
        self.assertEqual(error.details["count"], 42)


class TestServiceError(TestCase):
    """Test the ServiceError class."""

    def test_service_error_initialization(self):
        """Test service error initialization with all fields."""
        original_error = Exception("original error")
        error = ServiceError(
            message="test message",
            source="TestService",
            cause=original_error,
        )
        self.assertEqual(error.message, "test message")
        self.assertEqual(error.code, ErrorCode.SERVICE_ERROR)
        self.assertEqual(error.source, "TestService")
        self.assertEqual(error.cause, original_error)
        self.assertEqual(str(error), "[TestService] service_error: test message")

    def test_service_error_without_source_or_cause(self):
        """Test service error without optional fields."""
        error = ServiceError(message="test message")
        self.assertEqual(error.source, None)
        self.assertEqual(error.cause, None)
        self.assertEqual(str(error), "service_error: test message")


class TestClientErrors(TestCase):
    """Test client-related error classes."""

    def test_client_error_initialization(self):
        """Test base client error initialization."""
        original_error = Exception("original error")
        error = ClientError(
            message="test message",
            source="TestClient",
            cause=original_error,
        )
        self.assertEqual(error.message, "test message")
        self.assertEqual(error.code, ErrorCode.CLIENT_ERROR)
        self.assertEqual(error.source, "TestClient")
        self.assertEqual(error.cause, original_error)
        self.assertEqual(str(error), "[TestClient] client_error: test message")

    def test_http_client_error_initialization(self):
        """Test HTTP client error initialization."""
        original_error = Exception("original error")
        error = HTTPClientError(
            message="Not Found",
            status_code=404,
            source="TestClient",
            cause=original_error,
        )
        self.assertEqual(error.message, "HTTP 404 - Not Found")
        self.assertEqual(error.code, ErrorCode.HTTP_ERROR)
        self.assertEqual(error.source, "TestClient")
        self.assertEqual(error.details["status_code"], 404)
        self.assertEqual(error.cause, original_error)
        self.assertEqual(str(error), "[TestClient] http_error: HTTP 404 - Not Found")

    def test_network_error_initialization(self):
        """Test network error initialization."""
        original_error = Exception("original error")
        error = NetworkError(
            message="Connection refused",
            source="TestClient",
            cause=original_error,
        )
        self.assertEqual(error.message, "Network error - Connection refused")
        self.assertEqual(error.code, ErrorCode.NETWORK_ERROR)
        self.assertEqual(error.source, "TestClient")
        self.assertEqual(error.cause, original_error)
        self.assertEqual(
            str(error), "[TestClient] network_error: Network error - Connection refused"
        )


class TestParserErrors(TestCase):
    """Test parser-related error classes."""

    def test_parser_error_initialization(self):
        """Test base parser error initialization."""
        original_error = Exception("original error")
        error = ParserError(
            message="test message",
            source="TestParser",
            cause=original_error,
        )
        self.assertEqual(error.message, "test message")
        self.assertEqual(error.code, ErrorCode.PARSER_ERROR)
        self.assertEqual(error.source, "TestParser")
        self.assertEqual(error.cause, original_error)
        self.assertEqual(str(error), "[TestParser] parser_error: test message")

    def test_element_not_found_error_initialization(self):
        """Test element not found error initialization."""
        original_error = Exception("original error")
        error = ElementNotFoundError(
            message="Element not found",
            source="TestParser",
            cause=original_error,
        )
        self.assertEqual(error.message, "Element not found")
        self.assertEqual(error.code, ErrorCode.ELEMENT_NOT_FOUND)
        self.assertEqual(error.source, "TestParser")
        self.assertEqual(error.cause, original_error)
        self.assertEqual(
            str(error), "[TestParser] element_not_found: Element not found"
        )

    def test_invalid_format_error_initialization(self):
        """Test invalid format error initialization."""
        original_error = Exception("original error")
        error = InvalidFormatError(
            message="Invalid format",
            source="TestParser",
            cause=original_error,
        )
        self.assertEqual(error.message, "Invalid format")
        self.assertEqual(error.code, ErrorCode.INVALID_FORMAT)
        self.assertEqual(error.source, "TestParser")
        self.assertEqual(error.cause, original_error)
        self.assertEqual(str(error), "[TestParser] invalid_format: Invalid format")


class TestSerializerError(TestCase):
    """Test serializer error class."""

    def test_serializer_error_initialization(self):
        """Test serializer error initialization."""
        original_error = Exception("original error")
        error = SerializerError(
            message="test message",
            source="TestSerializer",
            cause=original_error,
        )
        self.assertEqual(error.message, "test message")
        self.assertEqual(error.code, ErrorCode.VALIDATION_ERROR)
        self.assertEqual(error.source, "TestSerializer")
        self.assertEqual(error.cause, original_error)
        self.assertEqual(str(error), "[TestSerializer] validation_error: test message")

    def test_serializer_error_with_details(self):
        """Test serializer error with details."""
        error = SerializerError(
            message="test message",
            details={"field": "value"},
            source="TestSerializer",
        )
        self.assertEqual(error.details["field"], "value")
