class ErrorCode:
    ERROR = "error"
    SERVICE_ERROR = "service_error"
    CLIENT_ERROR = "client_error"
    HTTP_ERROR = "http_error"
    NETWORK_ERROR = "network_error"
    PARSER_ERROR = "parser_error"
    VALIDATION_ERROR = "validation_error"
    SERIALIZER_ERROR = "serializer_error"


class Error(Exception):
    """Base exception class for all errors"""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.ERROR,
        details: dict = None,
        source: str = None,
        cause: Exception = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.source = source or self._get_source_from_cause(cause)
        self.cause = cause
        super().__init__(self.message)

    def _get_source_from_cause(self, cause: Exception) -> str:
        """Extract source from the exception's class name."""
        if cause and hasattr(cause, "__class__"):
            class_name = cause.__class__.__name__
            if any(
                class_name.endswith(suffix)
                for suffix in ["Service", "Client", "Parser"]
            ):
                return class_name
        return None

    def __str__(self):
        error_msg = f"{self.code}: {self.message}"
        if self.source:
            error_msg = f"[{self.source}] {error_msg}"
        return error_msg


class ServiceError(Error):
    """Base class for all service-related errors."""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.SERVICE_ERROR,
        details: dict = None,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(message, code, details, source, cause)


class ClientError(ServiceError):
    """Base class for all client-related errors."""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.CLIENT_ERROR,
        details: dict = None,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(message, code, details, source, cause)


class HTTPClientError(ClientError):
    """Raised when an HTTP error occurs."""

    def __init__(
        self,
        message: str,
        status_code: int,
        source: str = None,
        cause: Exception = None,
    ):
        details = {"status_code": status_code}
        super().__init__(
            message=f"HTTP {status_code} - {message}",
            code=ErrorCode.HTTP_ERROR,
            details=details,
            source=source,
            cause=cause,
        )


class NetworkError(ClientError):
    """Raised when a network error occurs."""

    def __init__(
        self,
        message: str,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(
            message=f"Network error - {message}",
            code=ErrorCode.NETWORK_ERROR,
            source=source,
            cause=cause,
        )


class ParserError(ServiceError):
    """Parser error that can contain validation errors"""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.PARSER_ERROR,
        details: dict = None,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(message, code, details, source, cause)


class ValidationError(ServiceError):
    """Validation error that can be used by all other error types"""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.VALIDATION_ERROR,
        details: dict = None,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(message, code, details, source, cause)


class SerializerError(ServiceError):
    """Serializer error for data validation and transformation errors"""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.SERIALIZER_ERROR,
        details: dict = None,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(message, code, details, source, cause)
