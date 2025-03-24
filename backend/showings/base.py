import logging
from functools import wraps
from typing import Any, Callable, Protocol, Type

from rest_framework import serializers
from showings.clients import ClientError, HTTPClientError, NetworkError
from showings.errors import (
    Error,
    ParserError,
    ServiceError,
)


class ClientProtocol(Protocol):
    """Protocol for client classes."""

    def get_titles_page(self) -> bytes: ...
    def get_title_showing_dates(self, title_id: str) -> bytes: ...
    def get_title_showing_times_on_date(self, title_id: str, date: str) -> bytes: ...
    def get_title_showings_page(self, title: dict) -> bytes: ...


class ParserProtocol(Protocol):
    """Protocol for parser classes."""

    def parse_titles_from_titles_page(self, content: bytes) -> list: ...
    def parse_showing_dates(self, content: bytes) -> list: ...
    def parse_showing_times(self, content: bytes) -> list: ...
    def parse_showings_from_title_page(self, content: bytes) -> list: ...


logger = logging.getLogger(__name__)


def handle_errors(source: str, error_type: Type[Error]) -> Callable:
    """
    Decorator to handle errors consistently.

    Args:
        source: Name of the source for error attribution
        error_type: Type of error to raise
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Error as e:
                e.log(logger)
                raise
            except Exception as e:
                error = error_type(
                    message=str(e),
                    source=source,
                    cause=e,
                )
                error.log(logger)
                raise error

        return wrapper

    return decorator


class ServiceWrapper:
    """Base class for services that use clients and parsers."""

    def __init__(self, client, parser):
        self.client = client
        self.parser = parser


def handle_service_errors(operation: str, service_name: str) -> Callable:
    """
    Decorator to handle service errors consistently.

    Args:
        operation: Name of the operation being performed
        service_name: Name of the service for error attribution
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self: ServiceWrapper, *args: Any, **kwargs: Any) -> Any:
            try:
                return func(self, *args, **kwargs)
            except ServiceError:
                raise
            except HTTPClientError as e:
                logger.error(
                    f"HTTP error during {operation}",
                    extra={
                        "client": self.client.__class__.__name__,
                        "status_code": e.status_code,
                        "error": str(e),
                    },
                    exc_info=True,
                )
                raise ServiceError(
                    f"HTTP error: {str(e)}",
                    source=service_name,
                ) from e
            except NetworkError as e:
                logger.error(
                    f"Network error during {operation}",
                    extra={
                        "client": self.client.__class__.__name__,
                        "error": str(e),
                    },
                    exc_info=True,
                )
                raise ServiceError(
                    f"Network error: {str(e)}",
                    source=service_name,
                ) from e
            except ClientError as e:
                logger.error(
                    f"Client error during {operation}",
                    extra={
                        "client": self.client.__class__.__name__,
                        "function": e.function,
                        "error": str(e),
                    },
                    exc_info=True,
                )
                raise ServiceError(
                    f"Client error: {str(e)}",
                    source=service_name,
                ) from e
            except ParserError as e:
                logger.error(
                    f"Parser error during {operation}",
                    extra={
                        "parser": self.parser.__class__.__name__,
                        "error": str(e),
                    },
                    exc_info=True,
                )
                raise ServiceError(
                    f"Parser error: {str(e)}",
                    source=service_name,
                ) from e
            except serializers.ValidationError as e:
                logger.warning(
                    f"Validation error during {operation}",
                    extra={
                        "errors": e.detail if hasattr(e, "detail") else str(e),
                    },
                )
                raise ServiceError(
                    f'Validation error: {e.detail if hasattr(e, "detail") else str(e)}',
                    source=service_name,
                ) from e
            except Exception as e:
                logger.error(
                    f"Unexpected error during {operation}",
                    extra={
                        "error_type": type(e).__name__,
                        "client": self.client.__class__.__name__,
                        "parser": self.parser.__class__.__name__,
                    },
                    exc_info=True,
                )
                raise ServiceError(
                    f"Unexpected error: {str(e)}",
                    source=service_name,
                ) from e

        return wrapper

    return decorator
