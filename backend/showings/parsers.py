import datetime
import logging
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from bs4.builder import ParserRejectedMarkup
from showings.base import handle_errors
from showings.errors import (
    ElementNotFoundError,
    InvalidFormatError,
    ParserError,
)
from showings.util import get_current_month, get_current_year

logger = logging.getLogger(__name__)


def handle_parser_errors(source: str):
    """Decorator to handle parser errors consistently.

    Args:
        source: The name of the parser class/method that raised the error.

    Returns:
        A decorator that wraps parser methods and handles errors.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ElementNotFoundError, InvalidFormatError):
                raise
            except Exception as e:
                logger.error(f"Parser error in {source}", exc_info=True)
                raise ParserError(
                    f"Failed to parse content: {str(e)}", source=source, cause=e
                )

        return wrapper

    return decorator


class GrandParser:
    @staticmethod
    @handle_errors("GrandParser", ParserError)
    def parse_titles_from_titles_page(titles_page: bytes) -> list:
        """Parse movie titles from Grand Cinema's titles page.

        Args:
            titles_page: The HTML content of the titles page.

        Returns:
            A list of dictionaries containing title information.

        Raises:
            ElementNotFoundError: If required elements are not found.
            InvalidFormatError: If the HTML format is invalid.
            ParserError: For other parsing errors.
        """
        soup = BeautifulSoup(titles_page, "lxml")
        labels = soup.find_all("label")
        titles = []
        for label in labels:
            title = label.text
            grand_id = label.attrs.get("for")
            if title and grand_id:
                titles.append({"title": title, "grand_id": grand_id})
        if not titles:
            raise ElementNotFoundError(
                "No valid movie titles found in the page", source="GrandParser"
            )
        return titles

    @staticmethod
    @handle_errors("GrandParser", ParserError)
    def parse_showing_dates(showing_dates_page: bytes) -> list:
        """Parse showing dates from Grand Cinema's dates page.

        Args:
            showing_dates_page: The HTML content of the dates page.

        Returns:
            A list of date strings.

        Raises:
            ElementNotFoundError: If required elements are not found.
            InvalidFormatError: If the HTML format is invalid.
            ParserError: For other parsing errors.
        """
        soup = BeautifulSoup(showing_dates_page, "lxml")
        dates = [i.text for i in soup.find_all("label")]
        if not dates:
            raise ElementNotFoundError(
                "No valid dates found in the page", source="GrandParser"
            )
        return dates

    @staticmethod
    @handle_errors("GrandParser", ParserError)
    def parse_showing_times(showing_times_page: bytes) -> list:
        """Parse showing times from Grand Cinema's times page.

        Args:
            showing_times_page: The HTML content of the times page.

        Returns:
            A list of time strings.

        Raises:
            ElementNotFoundError: If required elements are not found.
            InvalidFormatError: If the HTML format is invalid.
            ParserError: For other parsing errors.
        """
        soup = BeautifulSoup(showing_times_page, "lxml")
        times = [i.text for i in soup.find_all("label")]
        if not times:
            raise ElementNotFoundError(
                "No valid times found in the page", source="GrandParser"
            )
        return times


class TajParser:
    @staticmethod
    @handle_errors("TajParser", ParserError)
    def parse_titles_from_titles_page(titles_page: bytes) -> list:
        """Parse movie titles from Taj Cinema's titles page.

        Args:
            titles_page: The HTML content of the titles page.

        Returns:
            A list of dictionaries containing title information.

        Raises:
            ElementNotFoundError: If required elements are not found.
            InvalidFormatError: If the HTML format is invalid.
            ParserError: For other parsing errors.
        """
        soup = BeautifulSoup(titles_page, "lxml")
        movies_container = soup.find("div", class_="prs_upcom_slider_slides_wrapper")
        if not movies_container:
            raise ElementNotFoundError(
                "No movies container found in the page", source="TajParser"
            )
        movie_containers = movies_container.find_all(
            "div", class_="prs_upcom_movie_content_box"
        )
        titles = []
        for container in movie_containers:
            title = container.find("a").text
            taj_id = container.find("a")["href"].split("/")[-1]
            titles.append({"title": title, "taj_id": taj_id})
        if not titles:
            raise ElementNotFoundError(
                "No valid movie titles found in the page", source="TajParser"
            )
        return titles

    @staticmethod
    @handle_errors("TajParser", ParserError)
    def parse_showing_dates_from_title_page(title_page: bytes) -> list:
        """Parse showing dates from Taj Cinema's title page.

        Args:
            title_page: The HTML content of the title's page.

        Returns:
            A list of dictionaries containing date information.

        Raises:
            ElementNotFoundError: If required elements are not found.
            InvalidFormatError: If the HTML format is invalid.
            ParserError: For other parsing errors.
        """
        soup = BeautifulSoup(title_page, "lxml")
        calendar_container = soup.find("div", id="booking-dates")
        if not calendar_container:
            raise ElementNotFoundError(
                "No booking dates container found in the page", source="TajParser"
            )
        day_components = calendar_container.find_all("a")
        parsed_showing_dates = [
            {"date": i.text, "date_id": i.attrs.get("href")} for i in day_components
        ]
        showing_dates = TajParser.format_parsed_showing_dates(parsed_showing_dates)
        if not showing_dates:
            raise ElementNotFoundError(
                "No valid showing dates found in the page", source="TajParser"
            )
        return showing_dates

    @staticmethod
    @handle_errors("TajParser", ParserError)
    def parse_showing_times_from_title_page(
        title_page: bytes, showing_dates: list
    ) -> list:
        """Parse showing times from Taj Cinema's title page.

        Args:
            title_page: The HTML content of the title's page.
            showing_dates: List of dates to parse times for.

        Returns:
            A list of dictionaries containing time information.

        Raises:
            ElementNotFoundError: If required elements are not found.
            InvalidFormatError: If the HTML format is invalid.
            ParserError: For other parsing errors.
        """
        soup = BeautifulSoup(title_page, "lxml")
        showings = []
        for date in showing_dates:
            date_id = date["date_id"]
            times_container = soup.find("div", id=date_id)
            if not times_container:
                continue
            times = times_container.find_all("a")
            for time in times:
                showings.append(
                    {
                        "date_id": date_id,
                        "date": date["date"],
                        "time": time.text.strip(),
                    }
                )
        if not showings:
            raise ElementNotFoundError(
                "No valid showing times found in the page", source="TajParser"
            )
        return showings

    @staticmethod
    def _validate_and_format_day(day_str: str) -> str:
        """Validate day is between 1-31 and format with leading zero."""
        day_int = int(day_str)
        if day_int < 1 or day_int > 31:
            raise InvalidFormatError("Day must be between 1 and 31", source="TajParser")
        return str(day_int).zfill(2)

    @staticmethod
    def _build_date_string(day: str) -> str:
        """Build full date string in YYYY-MM-DD format."""
        date = f"{get_current_year()}-{get_current_month()}-{day}"
        datetime.datetime.strptime(date, "%Y-%m-%d")
        return date

    @staticmethod
    def format_parsed_showing_dates(
        parsed_dates: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """Format parsed showing dates into a consistent format.

        Args:
            parsed_dates: List of dictionaries containing date information.

        Returns:
            A list of dictionaries with formatted date information.

        Raises:
            InvalidFormatError: If the date format is invalid.
        """
        formatted_dates = []
        for date_info in parsed_dates:
            try:
                date_text = date_info["date"]
                date_id = date_info["date_id"]
                if not date_id:
                    raise InvalidFormatError(
                        "Invalid date format: missing date_id", source="TajParser"
                    )
                day = date_text.split()[-1]
                formatted_day = TajParser._validate_and_format_day(day)
                formatted_date = TajParser._build_date_string(formatted_day)
                formatted_dates.append(
                    {
                        "date": formatted_date,
                        "date_id": date_id.lstrip("#"),
                    }
                )
            except (ValueError, IndexError) as e:
                raise InvalidFormatError(
                    f"Invalid date format: {str(e)}", source="TajParser"
                ) from e
        return formatted_dates


class PrimeParser:
    @staticmethod
    @handle_errors("PrimeParser", ParserError)
    def parse_titles_from_titles_page(titles_page: bytes) -> list:
        """Parse movie titles from Prime Cinema's titles page.

        Args:
            titles_page: The HTML content of the titles page.

        Returns:
            A list of dictionaries containing title information.

        Raises:
            ElementNotFoundError: If required elements are not found.
            InvalidFormatError: If the HTML format is invalid.
            ParserError: For other parsing errors.
        """
        soup = BeautifulSoup(titles_page, "lxml")
        movies_container = soup.find("article", id="movies-list")
        if not movies_container:
            raise ElementNotFoundError(
                "No movies container found in the page", source="PrimeParser"
            )
        title_containers = movies_container.find_all("div", class_="title-wrapper")
        titles = []
        for container in title_containers:
            title = container.find("h3").text
            prime_id = container.find("a")["href"].split("/")[-1]
            titles.append({"title": title, "prime_id": prime_id})
        if not titles:
            raise ElementNotFoundError(
                "No valid movie titles found in the page", source="PrimeParser"
            )
        return titles

    @staticmethod
    @handle_errors("PrimeParser", ParserError)
    def parse_showings_from_title_page(title_page: bytes) -> list:
        """Parse showings from Prime Cinema's title page.

        Args:
            title_page: The HTML content of the title's page.

        Returns:
            A list of dictionaries containing showing information.

        Raises:
            ElementNotFoundError: If required elements are not found.
            InvalidFormatError: If the HTML format is invalid.
            ParserError: For other parsing errors.
        """
        soup = BeautifulSoup(title_page, "lxml")
        film_items = soup.find_all("div", class_="film-item")
        if not film_items:
            raise ElementNotFoundError(
                "No film items found in the page", source="PrimeParser"
            )
        showings = []
        for item in film_items:
            try:
                location = item.find("h3", class_="film-title").text
                datetime_str = item.find("time")["datetime"]
                datetime_obj = datetime.datetime.strptime(
                    datetime_str, "%Y-%m-%dT%H:%M:%S"
                )
                showings.append(
                    {
                        "location": location,
                        "date": datetime_obj.strftime("%Y-%m-%d"),
                        "time": datetime_obj.strftime("%H:%M"),
                    }
                )
            except (ValueError, AttributeError) as e:
                raise InvalidFormatError(
                    f"Invalid datetime format: {str(e)}", source="PrimeParser"
                ) from e
        if not showings:
            raise ElementNotFoundError(
                "No valid showings found in the page", source="PrimeParser"
            )
        return showings
