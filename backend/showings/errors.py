import logging


class ErrorCode:
    """Error codes for the application."""

    SERVICE_ERROR = "service_error"
    CLIENT_ERROR = "client_error"
    PARSER_ERROR = "parser_error"
    VALIDATION_ERROR = "validation_error"
    HTTP_ERROR = "http_error"
    NETWORK_ERROR = "network_error"
    ELEMENT_NOT_FOUND = "element_not_found"
    INVALID_FORMAT = "invalid_format"


class Error(Exception):
    """Base error class for all application errors."""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.SERVICE_ERROR,
        details: dict = None,
        source: str = None,
        cause: Exception = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.source = source
        self.cause = cause
        super().__init__(self.message)

    def __str__(self):
        source = f"[{self.source}] " if self.source else ""
        return f"{source}{self.code}: {self.message}"

    def log(self, logger: logging.Logger) -> None:
        logger.error(str(self), extra=self.details)


class ServiceError(Error):
    """Base error for service layer errors."""

    def __init__(
        self,
        message: str,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCode.SERVICE_ERROR,
            source=source,
            cause=cause,
        )


class ClientError(Error):
    """Base error for client layer errors."""

    def __init__(
        self,
        message: str,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCode.CLIENT_ERROR,
            source=source,
            cause=cause,
        )


class HTTPClientError(ClientError):
    """Raised when an HTTP request fails."""

    def __init__(
        self,
        message: str,
        status_code: int = None,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(
            message=message,
            source=source,
            cause=cause,
        )
        self.code = ErrorCode.HTTP_ERROR
        if status_code:
            self.details["status_code"] = status_code
            self.message = f"HTTP {status_code} - {message}"


class NetworkError(ClientError):
    """Raised when a network error occurs."""

    def __init__(
        self,
        message: str,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(
            message=message,
            source=source,
            cause=cause,
        )
        self.code = ErrorCode.NETWORK_ERROR
        self.message = f"Network error - {message}"


class SerializerError(ClientError):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str,
        source: str = None,
        cause: Exception = None,
        details: dict = None,
    ):
        super().__init__(
            message=message,
            source=source,
            cause=cause,
        )
        self.code = ErrorCode.VALIDATION_ERROR
        if details:
            self.details.update(details)


class ParserError(Error):
    """Base error for parser layer errors."""

    def __init__(
        self,
        message: str,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCode.PARSER_ERROR,
            source=source,
            cause=cause,
        )


class ElementNotFoundError(ParserError):
    """Raised when an element is not found in the HTML content."""

    def __init__(
        self,
        message: str,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(
            message=message,
            source=source,
            cause=cause,
        )
        self.code = ErrorCode.ELEMENT_NOT_FOUND


class InvalidFormatError(ParserError):
    """Raised when the format of the HTML content is invalid."""

    def __init__(
        self,
        message: str,
        source: str = None,
        cause: Exception = None,
    ):
        super().__init__(
            message=message,
            source=source,
            cause=cause,
        )
        self.code = ErrorCode.INVALID_FORMAT
