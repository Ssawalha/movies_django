import logging

from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from showings.models import Batch, Location, Movie, Showing
from showings.services import (
    GrandService,
    PrimeService,
    TajService,
    TitleMatchService,
)

logger = logging.getLogger(__name__)


@method_decorator(require_http_methods(["GET"]), name="dispatch")
class GetActiveShowingsView(View):
    """View to get all active showings."""

    def get(self, request):
        try:
            active_showings = Showing.objects.filter(is_showing=True).select_related(
                "movie", "location"
            )

            showings_data = [
                {
                    "movie_title": showing.movie.title,
                    "location": showing.location.name,
                    "date": showing.date,
                    "time": showing.time,
                    "url": showing.url,
                }
                for showing in active_showings
            ]

            return JsonResponse(
                {
                    "status": "success",
                    "count": len(showings_data),
                    "showings": showings_data,
                }
            )

        except Exception as e:
            logger.error(f"Error getting active showings: {str(e)}")
            return JsonResponse(
                {"status": "error", "message": "Failed to fetch active showings"},
                status=500,
            )


@method_decorator(require_http_methods(["POST"]), name="dispatch")
class ParseDataView(View):
    """View to parse movies and showings from all sources."""

    def post(self, request):
        try:
            batch = Batch.objects.create(
                batch_id=f"parse_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
                status=Batch.Status.PROCESSING,
            )

            # Parse movies
            grand_titles = GrandService.get_titles()
            prime_titles = PrimeService.get_titles()
            taj_titles = TajService.get_titles()

            matched_titles = TitleMatchService.match_titles(
                grand_titles, prime_titles, taj_titles
            )
            movies_created = 0

            for title_data in matched_titles:
                movie, created = Movie.objects.get_or_create(
                    normalized_title=title_data["normalized_title"],
                    defaults={
                        "title": title_data["title"],
                        "grand_id": title_data.get("grand_id"),
                        "prime_id": title_data.get("prime_id"),
                        "taj_id": title_data.get("taj_id"),
                        "grand_title": title_data.get("grand_title"),
                        "prime_title": title_data.get("prime_title"),
                        "taj_title": title_data.get("taj_title"),
                    },
                )
                if created:
                    movies_created += 1
                batch.movies.add(movie)

            # Parse showings
            grand_showings = GrandService.get_showings()
            prime_showings = PrimeService.get_showings()
            taj_showings = TajService.get_showings()

            all_showings = grand_showings + prime_showings + taj_showings
            showings_created = 0

            for showing_data in all_showings:
                try:
                    movie = Movie.objects.get(
                        normalized_title=showing_data["normalized_title"]
                    )
                    location, _ = Location.objects.get_or_create(
                        name=showing_data["location"], defaults={"city": "Amman"}
                    )

                    showing, created = Showing.objects.get_or_create(
                        movie=movie,
                        location=location,
                        date=showing_data["date"],
                        time=showing_data["time"],
                        defaults={"url": showing_data.get("url"), "is_showing": True},
                    )

                    if not created:
                        showing.is_showing = True
                        showing.save()
                    else:
                        showings_created += 1

                    batch.showings.add(showing)

                except Movie.DoesNotExist:
                    logger.warning(
                        f"Movie not found: {showing_data['normalized_title']}"
                    )
                    continue
                except Exception as e:
                    logger.error(f"Error saving showing: {str(e)}")
                    continue

            batch.status = Batch.Status.COMPLETED
            batch.save()

            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Successfully parsed {movies_created} new movies and {showings_created} new showings",
                    "batch_id": batch.batch_id,
                    "total_movies": len(matched_titles),
                    "total_showings": len(all_showings),
                }
            )
        except Exception as e:
            logger.error(f"Error parsing data: {str(e)}")
            if "batch" in locals():
                batch.status = Batch.Status.FAILED
                batch.save()
            return JsonResponse(
                {"status": "error", "message": "Failed to parse data"}, status=500
            )
