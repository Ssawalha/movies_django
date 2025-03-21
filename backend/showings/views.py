import logging

from django.http import HttpResponse
from showings.models import Showing
from showings.services import GrandService, PrimeService, TajService
from showings.util import match_titles

# TODO SERIALIZERS!
logger = logging.getLogger(__name__)

from pprint import pprint


def index(request):
    return HttpResponse("AGGREGATED MOVIE SHOWINGS - JORDAN")


def get_active_showings(request):
    active_showings = Showing.objects.filter(is_showing=True)
    if active_showings:
        body = ", ".join([s.movie.title for s in active_showings])
    else:
        body = "No active showings"
    return HttpResponse(f"GET ACTIVE SHOWINGS: {body}")


def get_showing(request):
    return HttpResponse("GET SHOWING")


def get_all_movies(request):
    grand_titles = GrandService.get_titles()
    prime_titles = PrimeService.get_titles()
    taj_titles = TajService.get_titles()

    titles = match_titles(grand_titles, prime_titles, taj_titles)
    # use list to save new movies to database

    return HttpResponse(titles)


def parse_showings(request):

    grand_titles = GrandService.get_titles()
    prime_titles = PrimeService.get_titles()
    taj_titles = TajService.get_titles()
    print(grand_titles)
    print(prime_titles)
    print(taj_titles)
    return HttpResponse("SUCCESS")


def test(request):
    titles = GrandService.get_titles()
    text = ", ".join(titles)
    return HttpResponse(text)


def get_grand_showings(request):
    showings = GrandService.get_showings()
    return HttpResponse(showings)
