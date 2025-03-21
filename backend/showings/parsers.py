import datetime
import logging

from bs4 import BeautifulSoup
from showings.util import get_current_month, get_current_year

logger = logging.getLogger(__name__)
# TODO SERIALIZERS!


class GrandParser:

    @staticmethod
    def parse_titles_from_titles_page(titles_page) -> list:
        try:
            soup = BeautifulSoup(titles_page, "lxml")
            labels = soup.find_all("label")
            titles = [{"title": i.text, "grand_id": i.attrs.get("for")} for i in labels]
            return titles
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandParser.GrandParserError(f"An error occurred: {e}")

    @staticmethod
    def parse_showing_dates(showing_dates_page: bytes) -> list:
        try:
            soup = BeautifulSoup(showing_dates_page, "lxml")
            dates = soup.find_all("label")
            dates = [i.text for i in dates]
            return dates
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandParser.GrandParserError(f"An error occurred: {e}")

    @staticmethod
    def parse_showing_times(showing_times_page: bytes) -> list:
        try:
            soup = BeautifulSoup(showing_times_page, "lxml")
            times = soup.find_all("label")
            times = [i.text for i in times]
            return times
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandParser.GrandParserError(f"An error occurred: {e}")

    class GrandParserError(Exception):
        pass


class TajParser:

    @staticmethod
    def parse_titles_from_titles_page(titles_page: bytes) -> list:
        titles = []
        try:
            soup = BeautifulSoup(titles_page, "lxml")
            movies_container = soup.find(
                "div", class_="prs_upcom_slider_slides_wrapper"
            )
            movie_containers = movies_container.find_all(
                "div", class_="prs_upcom_movie_content_box"
            )
            for container in movie_containers:
                title = container.find("a").text
                taj_id = container.find("a")["href"].split("/")[-1]
                titles.append({"title": title, "taj_id": taj_id})
            return titles
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise TajParser.TajParserError(f"An error occurred: {e}")

    @staticmethod
    def parse_showing_dates_from_title_page(title_page: bytes):
        try:
            soup = BeautifulSoup(title_page, "lxml")
            calendar_container = soup.find("div", id="booking-dates")
            day_components = calendar_container.find_all("a")
            parsed_showing_dates = [
                {"date": i.text, "date_id": i.attrs.get("href")} for i in day_components
            ]
            showing_dates = TajParser.format_parsed_showing_dates(parsed_showing_dates)
            return showing_dates
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise TajParser.TajParserError(f"An error occurred: {e}")

    @staticmethod
    def parse_showing_times_from_title_page(title_page: bytes, showing_dates):
        showings = []
        try:
            soup = BeautifulSoup(title_page, "lxml")
            for date in showing_dates:
                date_id = date["date_id"]
                times_container = soup.find("div", id=date_id)
                times = times_container.find_all("a")
                for time in times:
                    showings.append(
                        {
                            "date_id": date_id,
                            "date": date["date"],
                            "time": time.text.strip(),
                        }
                    )
            return showings
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise TajParser.TajParserError(f"An error occurred: {e}")

    @staticmethod
    def format_parsed_showing_dates(parsed_showing_dates: list) -> list:
        formatted_dates = []
        try:
            for d in parsed_showing_dates:
                date_id = d["date_id"][1:]
                raw_date = d["date"]
                day = raw_date.split(" ")[-1]
                date = f"{get_current_year()}-{get_current_month()}-{day}"
                formatted_dates.append({"date": date, "date_id": date_id})
            return formatted_dates
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise TajParser.TajParserError(f"An error occurred: {e}")

    class TajParserError(Exception):
        pass


class PrimeParser:

    @staticmethod
    def parse_titles_from_titles_page(titles_page: bytes) -> list:
        titles = []
        try:
            soup = BeautifulSoup(titles_page, "lxml")
            movies = soup.find("article", attrs={"id": "movies-list"})
            title_containers = movies.find_all("div", class_="title-wrapper")
            for movie in title_containers:
                link = movie.find("a")["href"]
                title = movie.find("h3").text
                title_id = link.split("/")[-1]
                titles.append({"title": title.strip(), "prime_id": title_id})
            return titles
        except Exception as e:
            return f"An error occurred: {e}"

    @staticmethod
    def parse_showings_from_title_page(title_showings_page: str) -> list:
        showings = []
        try:
            soup = BeautifulSoup(title_showings_page, "lxml")
            locations = soup.find_all("div", class_="film-item")
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
            return showings
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise PrimeParser.PrimeParserError(f"An error occurred: {e}")

    class PrimeParserError(Exception):
        pass
