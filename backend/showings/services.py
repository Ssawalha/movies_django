import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from django.utils import timezone
from showings.clients import GrandClient, PrimeClient, TajClient
from showings.errors import ServiceError
from showings.models import Location, Movie, Showing
from showings.parsers import GrandParser, PrimeParser, TajParser
from showings.serializers import (
    GrandServiceGetShowingDatesSerializer,
    MovieSerializer,
    ShowingServiceShowingSerializer,
    ShowingServiceTitleSerializer,
)
from showings.service_base import ServiceWrapper, handle_service_errors
from showings.title_matching import TitleMatchService

logger = logging.getLogger(__name__)


class ShowingService:
    """Service to coordinate between different cinema services."""

    def __init__(self):
        self.grand_service = GrandService()
        self.taj_service = TajService()
        self.prime_service = PrimeService()
        self.title_matching_service = TitleMatchService()

    @handle_service_errors("refresh_and_save", "ShowingService")
    def refresh_and_save(self) -> tuple[List[Movie], List[Showing]]:
        """Refresh data from sources and save to database."""
        # Get and save titles
        titles = self._get_and_validate_titles()
        movies = self._save_movies(titles)

        # Get and save showings
        all_showings = self._get_all_showings(titles)
        saved_showings = self._save_showings(all_showings, movies)

        return movies, saved_showings

    def _get_and_validate_titles(self) -> List[Dict]:
        """Get titles from all services and validate them."""
        grand_titles = self.grand_service.get_titles()
        taj_titles = self.taj_service.get_titles()
        prime_titles = self.prime_service.get_titles()

        titles = self.title_matching_service.match_titles(
            grand_titles, taj_titles, prime_titles
        )

        # Validate titles
        title_serializer = ShowingServiceTitleSerializer(data=titles, many=True)
        title_serializer.is_valid(raise_exception=True)

        return titles

    def _save_movies(self, titles: List[Dict]) -> List[Movie]:
        """Save or update movies from titles data."""
        movies = []
        for title_data in titles:
            serializer = MovieSerializer(
                data={
                    "title": title_data["title"],
                    "grand_id": title_data.get("grand_id"),
                    "prime_id": title_data.get("prime_id"),
                    "taj_id": title_data.get("taj_id"),
                    "grand_title": title_data.get("title_grand"),
                    "prime_title": title_data.get("title_prime"),
                    "taj_title": title_data.get("title_taj"),
                    "normalized_title": title_data["normalized_title"],
                },
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            movie, _ = Movie.objects.update_or_create(
                normalized_title=title_data["normalized_title"],
                defaults=serializer.validated_data,
            )
            movies.append(movie)
        return movies

    def _get_all_showings(self, titles: List[Dict]) -> List[Dict]:
        """Get showings from all services."""
        all_showings = []

        # Grand Cinema showings
        try:
            grand_showings = self.grand_service.get_showings(
                self._filter_titles(titles, "grand_id")
            )
            all_showings.extend(grand_showings)
        except Exception as e:
            logger.error(f"Failed to get Grand Cinema showings: {e}")

        # Taj Mall showings
        try:
            taj_showings = self.taj_service.get_showings(
                self._filter_titles(titles, "taj_id")
            )
            all_showings.extend(taj_showings)
        except Exception as e:
            logger.error(f"Failed to get Taj Mall showings: {e}")

        # Prime Mall showings
        try:
            prime_showings = self.prime_service.get_showings(
                self._filter_titles(titles, "prime_id")
            )
            all_showings.extend(prime_showings)
        except Exception as e:
            logger.error(f"Failed to get Prime Mall showings: {e}")

        # Validate showings
        showing_serializer = ShowingServiceShowingSerializer(
            data=all_showings, many=True
        )
        showing_serializer.is_valid(raise_exception=True)

        return all_showings

    def _save_showings(
        self, showings: List[Dict], movies: List[Movie]
    ) -> List[Showing]:
        """Save or update showings."""
        current_showings = set()
        showings_to_create = []
        showings_to_update = []

        # Get all movies in one query
        movies_dict = {m.normalized_title: m for m in movies}

        for showing_data in showings:
            try:
                showing = self._process_showing(showing_data, movies_dict)
                if showing:
                    if hasattr(showing, "id"):
                        showings_to_update.append(showing)
                    else:
                        showings_to_create.append(showing)
                    current_showings.add(showing.id if hasattr(showing, "id") else None)
            except Exception as e:
                logger.error(f"Error processing showing: {showing_data}, error: {e}")
                continue

        # Perform bulk operations
        if showings_to_create:
            created_showings = Showing.objects.bulk_create(showings_to_create)
            current_showings.update(s.id for s in created_showings)

        if showings_to_update:
            Showing.objects.bulk_update(
                showings_to_update, fields=["is_showing", "url"]
            )

        # Mark all showings not in the current batch as not showing
        Showing.objects.filter(
            date__gte=timezone.now().date(), is_showing=True
        ).exclude(id__in=current_showings).update(is_showing=False)

        # Return all current showings
        return Showing.objects.filter(id__in=current_showings)

    def _process_showing(
        self, showing_data: Dict, movies_dict: Dict[str, Movie]
    ) -> Optional[Showing]:
        """Process a single showing and return a Showing instance."""
        movie = movies_dict.get(showing_data["title"])
        if not movie:
            logger.warning(f"Movie not found for showing: {showing_data}")
            return None

        location, _ = Location.objects.get_or_create(
            name=showing_data["location"],
            defaults={"city": "Amman", "address": "Default Address"},
        )

        # Parse date and time
        date = datetime.strptime(showing_data["date"], "%Y-%m-%d").date()
        time = datetime.strptime(showing_data["time"], "%H:%M").time()

        # Only process future dates
        if date < timezone.now().date():
            return None

        showing_data = {
            "movie": movie,
            "location": location,
            "date": date,
            "time": time,
            "is_showing": True,
            "url": showing_data.get("url"),
        }

        try:
            showing = Showing.objects.get(
                movie=movie,
                location=location,
                date=date,
                time=time,
            )
            # Update existing showing
            for key, value in showing_data.items():
                setattr(showing, key, value)
            return showing
        except Showing.DoesNotExist:
            # Create new showing
            return Showing(**showing_data)

    @staticmethod
    def _filter_titles(titles: List[Dict], id_name: str) -> List[Dict]:
        """Filter titles that have a specific ID field."""
        return [title for title in titles if title.get(id_name)]

    def get_active_showings(self) -> List[Showing]:
        """Get all active showings."""
        return Showing.objects.filter(
            is_showing=True, date__gte=timezone.now().date()
        ).select_related("movie", "location")

    def get_showings_by_date(self, date: datetime.date) -> List[Showing]:
        """Get all showings for a specific date."""
        return Showing.objects.filter(date=date, is_showing=True).select_related(
            "movie", "location"
        )

    def get_showings_by_movie(self, movie_id: int) -> List[Showing]:
        """Get all showings for a specific movie."""
        return Showing.objects.filter(
            movie_id=movie_id, is_showing=True, date__gte=timezone.now().date()
        ).select_related("movie", "location")

    def get_showings_by_location(self, location_id: int) -> List[Showing]:
        """Get all showings for a specific location."""
        return Showing.objects.filter(
            location_id=location_id, is_showing=True, date__gte=timezone.now().date()
        ).select_related("movie", "location")

    def get_movies(self) -> List[Movie]:
        """Get all movies."""
        return Movie.objects.all()

    def get_locations(self) -> List[Location]:
        """Get all locations."""
        return Location.objects.all()


class GrandService(ServiceWrapper):
    client = GrandClient
    parser = GrandParser

    def __init__(self):
        super().__init__(self.client, self.parser)

    @handle_service_errors("get_showings", "GrandService")
    def get_showings(self, titles: Optional[list] = None) -> list:
        showings = []
        if titles is None:
            titles = self.get_titles()
        for title in titles:
            showing_dates = self.get_showing_dates(title)
            for date in showing_dates:
                showing_times = self.get_showing_times(title, date)
                for time in showing_times:
                    showings.append(
                        {
                            "title": title.get("title"),
                            "date": date,
                            "time": time,
                            "location": "Grand Cinema City Mall",
                        }
                    )
        return showings

    @handle_service_errors("get_titles", "GrandService")
    def get_titles(self) -> list:
        titles_page = self.client.get_titles_page()
        titles = self.parser.parse_titles_from_titles_page(titles_page)
        return titles

    @handle_service_errors("get_showing_dates", "GrandService")
    def get_showing_dates(self, title: Dict[str, Any]) -> list:
        title_id = title.get("grand_id")
        serializer = GrandServiceGetShowingDatesSerializer(data={"grand_id": title_id})
        serializer.is_valid(raise_exception=True)
        showing_dates_page = self.client.get_title_showing_dates(title_id)
        showing_dates = self.parser.parse_showing_dates(showing_dates_page)
        return showing_dates

    @handle_service_errors("get_showing_times", "GrandService")
    def get_showing_times(self, title: Dict[str, Any], date: str) -> list:
        title_id = title.get("grand_id")
        showing_times_page = self.client.get_title_showing_times_on_date(title_id, date)
        showing_times = self.parser.parse_showing_times(showing_times_page)
        return showing_times


class TajService(ServiceWrapper):
    client = TajClient
    parser = TajParser

    def __init__(self):
        super().__init__(self.client, self.parser)

    @handle_service_errors("get_showings", "TajService")
    def get_showings(self, titles: Optional[list] = None) -> list:
        showings = []
        titles = self.get_titles()
        for t in titles:
            showings += self.get_title_showings(t)
        return showings

    @handle_service_errors("get_titles", "TajService")
    def get_titles(self) -> list:
        titles_page = self.client.get_titles_page()
        titles = self.parser.parse_titles_from_titles_page(titles_page)
        return titles

    @handle_service_errors("get_title_showings", "TajService")
    def get_title_showings(self, title: Dict[str, Any]) -> list:
        title_showings = []
        title_page = self.client.get_title_showings_page(title)
        parsed_dates = self.parser.parse_showing_dates_from_title_page(title_page)
        parsed_times = self.parser.parse_showing_times_from_title_page(
            title_page, parsed_dates
        )
        for t in parsed_times:
            t["title"] = title["title"]
            t["location"] = "Taj Mall"
            del t["date_id"]
            title_showings.append(t)
        return title_showings


class PrimeService(ServiceWrapper):
    client = PrimeClient
    parser = PrimeParser

    def __init__(self):
        super().__init__(self.client, self.parser)

    @handle_service_errors("get_showings", "PrimeService")
    def get_showings(self, titles: Optional[list] = None) -> list:
        showings = []
        if titles is None:
            titles = self.get_titles()
        for title in titles:
            showings += self.get_title_showings(title)
        return showings

    @handle_service_errors("get_titles", "PrimeService")
    def get_titles(self) -> list:
        titles_page = self.client.get_titles_page()
        titles = self.parser.parse_titles_from_titles_page(titles_page)
        return titles

    @handle_service_errors("get_title_showings", "PrimeService")
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
