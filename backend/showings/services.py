import logging
from typing import Any, Dict

from showings.base import ServiceWrapper, handle_errors
from showings.clients import GrandClient, PrimeClient, TajClient
from showings.errors import ServiceError
from showings.parsers import GrandParser, PrimeParser, TajParser
from showings.serializers import GrandServiceGetShowingDatesSerializer

logger = logging.getLogger(__name__)


class GrandService:
    client = GrandClient
    parser = GrandParser

    @staticmethod
    @handle_errors("GrandService", ServiceError)
    def get_showings() -> list:
        showings = []
        titles = GrandService.get_titles()
        for title in titles:
            showing_dates = GrandService.get_showing_dates(title)
            for date in showing_dates:
                showing_times = GrandService.get_showing_times(title, date)
                for time in showing_times:
                    showings.append(
                        {
                            "title": title.get("title"),
                            "date": date,
                            "time": time,
                            "location": "Grand Cinema City Mall",  # TODO make constant?
                        }
                    )
        return showings

    @staticmethod
    @handle_errors("GrandService", ServiceError)
    def get_titles() -> list:
        titles_page = GrandService.client.get_titles_page()
        titles = GrandService.parser.parse_titles_from_titles_page(titles_page)
        return titles

    @staticmethod
    @handle_errors("GrandService", ServiceError)
    def get_showing_dates(title: Dict[str, Any]) -> list:
        title_id = title.get("grand_id")
        serializer = GrandServiceGetShowingDatesSerializer(data={"grand_id": title_id})
        if not serializer.is_valid():
            raise ServiceError(
                f"Invalid grand_id: {serializer.errors}",
                source="GrandService",
            )
        showing_dates_page = GrandService.client.get_title_showing_dates(title_id)
        showing_dates = GrandService.parser.parse_showing_dates(showing_dates_page)
        return showing_dates

    @staticmethod
    @handle_errors("GrandService", ServiceError)
    def get_showing_times(title: Dict[str, Any], date: str) -> list:
        title_id = title.get("grand_id")
        showing_times_page = GrandService.client.get_title_showing_times_on_date(
            title_id, date
        )
        showing_times = GrandService.parser.parse_showing_times(showing_times_page)
        return showing_times


class TajService:
    client = TajClient
    parser = TajParser

    @staticmethod
    @handle_errors("TajService", ServiceError)
    def get_showings() -> list:
        showings = []
        titles = TajService.get_titles()
        for t in titles:
            showings += TajService.get_title_showings(t)
        return showings

    @staticmethod
    @handle_errors("TajService", ServiceError)
    def get_titles() -> list:
        titles_page = TajService.client.get_titles_page()
        titles = TajService.parser.parse_titles_from_titles_page(titles_page)
        return titles

    @staticmethod
    @handle_errors("TajService", ServiceError)
    def get_title_showings(title: Dict[str, Any]) -> list:
        title_showings = []
        title_page = TajService.client.get_title_showings_page(title)
        parsed_dates = TajService.parser.parse_showing_dates_from_title_page(title_page)
        parsed_times = TajService.parser.parse_showing_times_from_title_page(
            title_page, parsed_dates
        )
        for t in parsed_times:
            t["title"] = title["title"]
            t["location"] = "Taj Mall"  # TODO make constant?
            del t["date_id"]
            title_showings.append(t)
        return title_showings


class PrimeService(ServiceWrapper):
    client = PrimeClient
    parser = PrimeParser

    def __init__(self):
        super().__init__(self.client, self.parser)

    @handle_errors("PrimeService", ServiceError)
    def get_showings(self) -> list:
        showings = []
        titles = self.get_titles()
        for title in titles:
            showings += self.get_title_showings(title)
        return showings

    @handle_errors("PrimeService", ServiceError)
    def get_titles(self) -> list:
        titles_page = self.client.get_titles_page()
        titles = self.parser.parse_titles_from_titles_page(titles_page)
        return titles

    @handle_errors("PrimeService", ServiceError)
    def get_title_showings(self, title: Dict[str, Any]) -> list:
        title_showings_page = self.client.get_title_showings_page(title)
        showings = self.parser.parse_showings_from_title_page(title_showings_page)
        showings = [
            {
                "title": title["prime_id"],
                "date": s["date"],
                "time": s["time"],
                "location": s["location"],
            }
            for s in showings
        ]
        return showings
