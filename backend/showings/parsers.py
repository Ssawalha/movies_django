import datetime
import logging
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from bs4.builder import ParserRejectedMarkup
from showings.util import get_current_month, get_current_year

logger = logging.getLogger(__name__)


class ParserError(Exception):
    """Base exception for all parser errors."""

    pass


class BaseParser(ABC):
    """Base class for all parsers with common error handling."""

    @staticmethod
    def handle_parsing_error(e: Exception, context: str, parser_class: type) -> None:
        """Handle parsing errors with consistent logging and error raising."""
        parser_name = parser_class.__name__
        method_name = e.__traceback__.tb_frame.f_code.co_name
        error_msg = f"{parser_name}.{method_name}: {str(e)}"
        logger.critical(error_msg)
        raise ParserError(error_msg)

    @abstractmethod
    def parse_titles_from_titles_page(self, titles_page: bytes) -> list:
        """Parse titles from a titles page."""
        pass


class GrandParser(BaseParser):
    @staticmethod
    def parse_titles_from_titles_page(titles_page: bytes) -> list:
        try:
            soup = BeautifulSoup(titles_page, "lxml")
            labels = soup.find_all("label")
            titles = [{"title": i.text, "grand_id": i.attrs.get("for")} for i in labels]
            if not titles:
                raise ValueError("No valid movie titles found in the page")
            return titles
        except Exception as e:
            GrandParser.handle_parsing_error(e, "titles page", GrandParser)

    @staticmethod
    def parse_showing_dates(showing_dates_page: bytes) -> list:
        try:
            soup = BeautifulSoup(showing_dates_page, "lxml")
            dates = [i.text for i in soup.find_all("label")]
            if not dates:
                raise ValueError("No valid dates found in the page")
            return dates
        except Exception as e:
            GrandParser.handle_parsing_error(e, "showing dates", GrandParser)

    @staticmethod
    def parse_showing_times(showing_times_page: bytes) -> list:
        try:
            soup = BeautifulSoup(showing_times_page, "lxml")
            times = [i.text for i in soup.find_all("label")]
            if not times:
                raise ValueError("No valid times found in the page")
            return times
        except Exception as e:
            GrandParser.handle_parsing_error(e, "showing times", GrandParser)


class TajParser(BaseParser):
    @staticmethod
    def parse_titles_from_titles_page(titles_page: bytes) -> list:
        try:
            soup = BeautifulSoup(titles_page, "lxml")
            movies_container = soup.find(
                "div", class_="prs_upcom_slider_slides_wrapper"
            )
            if not movies_container:
                raise ValueError("No movies container found in the page")
            movie_containers = movies_container.find_all(
                "div", class_="prs_upcom_movie_content_box"
            )
            titles = []
            for container in movie_containers:
                title = container.find("a").text
                taj_id = container.find("a")["href"].split("/")[-1]
                titles.append({"title": title, "taj_id": taj_id})
            if not titles:
                raise ValueError("No valid movie titles found in the page")
            return titles
        except Exception as e:
            TajParser.handle_parsing_error(e, "titles page", TajParser)

    @staticmethod
    def parse_showing_dates_from_title_page(title_page: bytes) -> list:
        try:
            soup = BeautifulSoup(title_page, "lxml")
            calendar_container = soup.find("div", id="booking-dates")
            if not calendar_container:
                raise ValueError("No booking dates container found in the page")
            day_components = calendar_container.find_all("a")
            parsed_showing_dates = [
                {"date": i.text, "date_id": i.attrs.get("href")} for i in day_components
            ]
            showing_dates = TajParser.format_parsed_showing_dates(parsed_showing_dates)
            if not showing_dates:
                raise ValueError("No valid showing dates found in the page")
            return showing_dates
        except Exception as e:
            TajParser.handle_parsing_error(e, "showing dates", TajParser)

    @staticmethod
    def parse_showing_times_from_title_page(
        title_page: bytes, showing_dates: list
    ) -> list:
        try:
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
                raise ValueError("No valid showing times found in the page")
            return showings
        except Exception as e:
            TajParser.handle_parsing_error(e, "showing times", TajParser)

    @staticmethod
    def _validate_and_format_day(day_str: str) -> str:
        """Validate day is between 1-31 and format with leading zero."""
        day_int = int(day_str)
        if day_int < 1 or day_int > 31:
            raise ValueError(
                "TajParser._validate_and_format_day: Day must be between 1 and 31"
            )
        return str(day_int).zfill(2)

    @staticmethod
    def _build_date_string(day: str) -> str:
        """Build full date string in YYYY-MM-DD format."""
        date = f"{get_current_year()}-{get_current_month()}-{day}"
        datetime.datetime.strptime(date, "%Y-%m-%d")
        return date

    @staticmethod
    def format_parsed_showing_dates(parsed_showing_dates: list) -> list:
        formatted_dates = []
        for d in parsed_showing_dates:
            try:
                date_id = d["date_id"][1:]  # Remove leading '#'
                day = d["date"].split(" ")[-1]  # Get day from "Sun 23" format

                day_str = TajParser._validate_and_format_day(day)
                date = TajParser._build_date_string(day_str)

                formatted_dates.append({"date": date, "date_id": date_id})
            except (ValueError, TypeError):
                continue

        if not formatted_dates:
            raise ValueError(
                "TajParser.format_parsed_showing_dates: No valid formatted dates found"
            )
        return formatted_dates


class PrimeParser(BaseParser):
    @staticmethod
    def parse_titles_from_titles_page(titles_page: bytes) -> list:
        try:
            soup = BeautifulSoup(titles_page, "lxml")
            movies = soup.find("article", attrs={"id": "movies-list"})
            if not movies:
                raise ParserError("No movies list found in the page")
            title_containers = movies.find_all("div", class_="title-wrapper")
            titles = []
            for movie in title_containers:
                link = movie.find("a")["href"]
                title = movie.find("h3").text
                title_id = link.split("/")[-1]
                titles.append({"title": title.strip(), "prime_id": title_id})
            if not titles:
                raise ParserError("No valid movie titles found in the page")
            return titles
        except Exception as e:
            PrimeParser.handle_parsing_error(e, "titles page", PrimeParser)

    @staticmethod
    def parse_showings_from_title_page(title_showings_page: str) -> list:
        try:
            soup = BeautifulSoup(title_showings_page, "lxml")
            locations = soup.find_all("div", class_="film-item")
            if not locations:
                raise ParserError("No film items found in the page")
            showings = []
            for l in locations:
                theater = l.find("h3", class_="film-title").text
                sessions = l.find_all("time")
                for s in sessions:
                    session_timestamp = datetime.datetime.strptime(
                        s["datetime"], "%Y-%m-%dT%H:%M:%S"
                    )
                    date = session_timestamp.strftime("%Y-%m-%d")
                    time = session_timestamp.strftime("%H:%M")
                    showings.append(
                        {
                            "location": theater,
                            "date": date,
                            "time": time,
                        }
                    )
            if not showings:
                raise ParserError("No valid showings found in the page")
            return showings
        except Exception as e:
            PrimeParser.handle_parsing_error(e, "showings", PrimeParser)
