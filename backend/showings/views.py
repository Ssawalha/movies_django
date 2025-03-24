import logging

from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from rest_framework.response import Response
from rest_framework.views import APIView
from showings.services import ShowingService

logger = logging.getLogger(__name__)


@method_decorator(require_http_methods(["GET", "POST"]), name="dispatch")
class ShowingView(APIView):
    """View for showing operations."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ShowingService()

    def _handle_error(self, e: Exception, message: str) -> Response:
        """Handle errors and return appropriate response."""
        logger.error(f"{message}: {str(e)}")
        return Response({"status": "error", "message": message}, status=500)

    def get(self, request):
        """Get all active showings."""
        try:
            showings = self.service.get_active_showings()
            return Response(
                {
                    "status": "success",
                    "count": len(showings),
                    "showings": list(
                        showings.values(
                            "movie__title", "location__name", "date", "time", "url"
                        )
                    ),
                }
            )
        except Exception as e:
            return self._handle_error(e, "Failed to fetch active showings")

    def post(self, request):
        """Scrape and save new movies and showings."""
        try:
            movies, showings = self.service.refresh_and_save()
            return Response(
                {
                    "status": "success",
                    "message": f"Successfully scraped {len(movies)} movies and {len(showings)} showings",
                }
            )
        except Exception as e:
            return self._handle_error(e, "Failed to scrape data")
