import logging
from datetime import date
from functools import wraps
from typing import Any, Callable, Dict, Optional, Protocol, Type, Union

import requests
from movie_showings.settings import GRAND_BASE_URL, PRIME_BASE_URL, TAJ_BASE_URL
from requests.exceptions import HTTPError, RequestException
from rest_framework.exceptions import ValidationError

from .errors import ClientError, HTTPClientError, NetworkError
from .serializers import (
    GrandClientShowingDatesSerializer,
    GrandClientShowingTimesSerializer,
    PrimeClientTitleShowingsSerializer,
    TajClientTitleShowingsSerializer,
)

logger = logging.getLogger(__name__)


def handle_client_errors(client_name: str) -> Callable:
    """
    Decorator to handle common client errors.

    Args:
        client_name: Name of the client for logging purposes (e.g., "GrandClient")
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"{client_name}.{func.__name__} Validation error: {e}")
                raise ClientError(
                    message=f"Validation error: {e.detail}",
                    source=client_name,
                    cause=e,
                )
            except HTTPError as e:
                logger.error(f"{client_name}.{func.__name__} HTTP error: {e}")
                raise HTTPClientError(
                    message=str(e),
                    status_code=e.response.status_code,
                    source=client_name,
                    cause=e,
                )
            except RequestException as e:
                logger.error(f"{client_name}.{func.__name__} Network error: {e}")
                raise NetworkError(
                    message=str(e),
                    source=client_name,
                    cause=e,
                )
            except Exception as e:
                logger.error(f"{client_name}.{func.__name__} Unexpected error: {e}")
                raise ClientError(
                    message=str(e),
                    source=client_name,
                    cause=e,
                )

        return wrapper

    return decorator


class GrandClient:
    @staticmethod
    @handle_client_errors("GrandClient")
    def get_titles_page() -> bytes:
        url = f"{GRAND_BASE_URL}/handlers/getmovies.ashx"
        body = {"cinemaId": "0000000002"}
        response = requests.post(url, data=body)
        response.raise_for_status()
        return response.content

    @staticmethod
    @handle_client_errors("GrandClient")
    def get_title_showing_dates(grand_title_id: str) -> bytes:
        serializer = GrandClientShowingDatesSerializer(
            data={"grand_id": grand_title_id}
        )
        serializer.is_valid(raise_exception=True)

        url = f"{GRAND_BASE_URL}/handlers/getsessionDate.ashx"
        body = {
            "cinemaId": "0000000002",
            "movieId": grand_title_id,
        }
        response = requests.post(url, data=body)
        response.raise_for_status()
        return response.content

    @staticmethod
    @handle_client_errors("GrandClient")
    def get_title_showing_times_on_date(grand_title_id: str, date: str) -> bytes:
        serializer = GrandClientShowingTimesSerializer(
            data={"grand_id": grand_title_id, "date": date}
        )
        serializer.is_valid(raise_exception=True)

        url = f"{GRAND_BASE_URL}/handlers/getsessionTime.ashx"
        body = {"cinemaId": "0000000002", "movieId": grand_title_id, "date": date}
        response = requests.post(url, data=body)
        response.raise_for_status()
        return response.content


class TajClient:
    @staticmethod
    @handle_client_errors("TajClient")
    def get_titles_page() -> bytes:
        url = TAJ_BASE_URL
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    @staticmethod
    @handle_client_errors("TajClient")
    def get_title_showings_page(title: Dict[str, str]) -> bytes:
        serializer = TajClientTitleShowingsSerializer(data=title)
        serializer.is_valid(raise_exception=True)

        title_id = serializer.validated_data["taj_id"]
        url = f"{TAJ_BASE_URL}/movies/{title_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.content


class PrimeClient:
    @staticmethod
    @handle_client_errors("PrimeClient")
    def get_titles_page() -> bytes:
        url = f"{PRIME_BASE_URL}/Browsing/Movies/NowShowing"
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    @staticmethod
    @handle_client_errors("PrimeClient")
    def get_title_showings_page(title: Dict[str, str]) -> bytes:
        serializer = PrimeClientTitleShowingsSerializer(data=title)
        serializer.is_valid(raise_exception=True)

        title_id = serializer.validated_data["prime_id"]
        url = f"{PRIME_BASE_URL}/Browsing/Movies/Details/{title_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.content
