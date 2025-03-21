import logging

import requests
from movie_showings.settings import GRAND_BASE_URL, PRIME_BASE_URL, TAJ_BASE_URL

# TODO add typing to all functions
# TODO add error handling to all functions
# TODO SERIALIZERS!

logger = logging.getLogger(__name__)


class GrandClient:

    @staticmethod
    def get_titles_page():  # rename.
        try:
            url = f"{GRAND_BASE_URL}/handlers/getmovies.ashx"
            body = {"cinemaId": "0000000002"}
            response = requests.post(url, data=body)
            response.raise_for_status()
            response.raise_for_status()
            return response.content

        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandClient.GrandClientError(f"An error occurred: {e}")

    @staticmethod
    def get_title_showing_dates(grand_title_id):
        try:
            url = f"{GRAND_BASE_URL}/handlers/getsessionDate.ashx"
            body = {
                "cinemaId": "0000000002",
                "movieId": grand_title_id,
            }
            response = requests.post(url, data=body)
            return response.content

        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandClient.GrandClientError(f"An error occurred: {e}")

    @staticmethod
    def get_title_showing_times_on_date(grand_title_id, date):
        try:
            url = f"{GRAND_BASE_URL}/handlers/getsessionTime.ashx"
            body = {"cinemaId": "0000000002", "movieId": grand_title_id, "date": date}
            response = requests.post(url, data=body)
            return response.content

        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandClient.GrandClientError(f"An error occurred: {e}")

    class GrandClientError(Exception):
        pass


class TajClient:

    @staticmethod
    def get_titles_page():
        try:
            response = requests.get(TAJ_BASE_URL)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise TajClient.TajClientError(f"An error occurred: {e}")

    @staticmethod
    def get_title_showings_page(title: dict):
        title_id = title.get("taj_id")
        try:
            url = f"{TAJ_BASE_URL}/movies/{title_id}"
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise TajClient.TajClientError(f"An error occurred: {e}")

    class TajClientError(Exception):
        pass


class PrimeClient:

    @staticmethod
    def get_titles_page():
        try:
            response = requests.get(f"{PRIME_BASE_URL}/Browsing/Movies/NowShowing")
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise PrimeClient.PrimeClientError(f"An error occurred: {e}")

    @staticmethod
    def get_title_showings_page(title: dict):
        try:
            title_id = title.get("title_id")
            response = requests.get(
                f"{PRIME_BASE_URL}/Browsing/Movies/Details/{title_id}"
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise PrimeClient.PrimeClientError(f"An error occurred: {e}")

    class PrimeClientError(Exception):
        pass
