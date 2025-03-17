import logging
from showings.clients import GrandClient, TajClient, PrimeClient
from showings.parsers import GrandParser, TajParser, PrimeParser


logger = logging.getLogger(__name__)
# TODO SERIALIZERS!

class GrandService:
    client = GrandClient
    parser = GrandParser

    @staticmethod
    def get_showings() -> list:
        showings = []
        try:
            titles = GrandService.get_titles()
            for title in titles:
                showing_dates = GrandService.get_showing_dates(title)
                for date in showing_dates:
                    showing_times = GrandService.get_showing_times(title, date)
                    for time in showing_times:
                        showings.append({
                            'title': title.get('title'),
                            'date': date,
                            'time': time,
                            'location': 'Grand Cinema City Mall' # TODO make constant?
                        })
            return showings
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandService.GrandServiceError(f"An error occurred: {e}")

    @staticmethod
    def get_titles() -> list:
        try: 
            titles_page = GrandService.client.get_titles_page()
            titles = GrandService.parser.parse_titles_from_titles_page(titles_page)
            return titles
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandService.GrandServiceError(f"An error occurred: {e}")

    @staticmethod
    def get_showing_dates(title):
        title_id = title.get('grand_id')
        try:
            showing_dates_page = GrandService.client.get_title_showing_dates(title_id)
            showing_dates = GrandService.parser.parse_showing_dates(showing_dates_page)
            return showing_dates
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandService.GrandServiceError(f"An error occurred: {e}")
    
    @staticmethod
    def get_showing_times(title, date):
        title_id = title.get('grand_id')
        try:
            showing_times_page = GrandService.client.get_title_showing_times_on_date(title_id, date)
            showing_times = GrandService.parser.parse_showing_times(showing_times_page)
            return showing_times
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandService.GrandServiceError(f"An error occurred: {e}")        

    class GrandServiceError(Exception):
        pass


class TajService:
    client = TajClient
    parser = TajParser

    @staticmethod
    def get_showings() -> list:
        showings = []
        try:
            titles = TajService.get_titles()
            for t in titles:
                showings += TajService.get_title_showings(t)
            return showings
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise TajService.TajServiceError(f"An error occurred: {e}")  

    @staticmethod
    def get_titles() -> list:
        try:
            titles_page = TajService.client.get_titles_page()
            titles = TajService.parser.parse_titles_from_titles_page(titles_page)
            return titles
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise TajService.TajServiceError(f"An error occurred: {e}")  

    @staticmethod
    def get_title_showings(title) -> list:
        title_showings = []
        try:
            title_page = TajService.client.get_title_showings_page(title)        
            parsed_dates = TajService.parser.parse_showing_dates_from_title_page(title_page)
            parsed_times = TajService.parser.parse_showing_times_from_title_page(title_page, parsed_dates)
            for t in parsed_times:
                t['title'] = title['title']
                t['location'] = 'Taj Mall' # TODO make constant?
                del(t['date_id'])
                title_showings.append(t)
            return title_showings
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise TajService.TajServiceError(f"An error occurred: {e}")  

    class TajServiceError(Exception):
        pass


class PrimeService:
    client = PrimeClient
    parser = PrimeParser

    @staticmethod
    def get_showings() -> list:
        showings = []
        try:
            titles = PrimeService.get_titles()
            for title in titles:
                showings += PrimeService.get_title_showings(title)
            return showings
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise PrimeService.PrimeServiceError(f"An error occurred: {e}")

    @staticmethod
    def get_titles() -> list:
        try:
            titles_page = PrimeService.client.get_titles_page()
            titles = PrimeService.parser.parse_titles_from_titles_page(titles_page)
            return titles
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise PrimeService.PrimeServiceError(f"An error occurred: {e}")  

    @staticmethod
    def get_title_showings(title: dict) -> list:
        try:
            title_showings_page = PrimeService.client.get_title_showings_page(title)
            showings = PrimeService.parser.parse_showings_from_title_page(title_showings_page)
            showings = [{'title': title['prime_id'], 'date': s['date'], 'time': s['time'], 'location': s['location']} for s in showings]
            return showings
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise PrimeService.PrimeServiceError(f"An error occurred: {e}")  

    class PrimeServiceError(Exception):
        pass

