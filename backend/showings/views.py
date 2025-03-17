from django.http import HttpResponse
import logging

from showings.models import Showing
from showings.services import GrandService, TajService, PrimeService
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
    # return HttpResponse("MOVIES")
    grand_titles = GrandService.get_titles()
    prime_titles = PrimeService.get_titles()
    taj_titles = TajService.get_titles()

    # three arrays of titles.. 
    # grand_titles = [{'title': '6 DAYS', 'grand_id': '0010001899'}]
    # prime_titles = [{'title': '6 Days: What The Years done to us', 'prime_id': 'h-HO00006101'}]
    # taj_titles = [{'title': ' El HANA El ANA FEEH', 'taj_id': '454'}]
    # should return a matched list of titles to theaters
    # {'title': '6 DAYS', 'grand_id': '0010001899', 'prime_id': 'h-HO00006101', 'taj_id': ''}
    # {'title': 'El Hana El Ana Feeh', 'grand_id': '', 'prime_id': '', 'taj_id': '454'}
    titles = match_titles(grand_titles, prime_titles, taj_titles)
    # use list to save new movies to database

    return HttpResponse(titles)

def parse_showings(request):
    # grand_showings = GrandService.get_showings() # WORKING
    # print("GRAND")
    # pprint(grand_showings)

    # taj_showings = TajService.get_showings()
    # print("\nTAJ")
    # pprint(taj_showings)

    # prime_showings = PrimeService.get_showings()
    # print("\nPRIME")
    # pprint(prime_showings)

    # showings = {
    #     # 'grand': grand_showings,
    #     # 'taj': taj_showings,
    #     'prime': prime_showings,
    # }
    grand_titles = GrandService.get_titles()
    prime_titles = PrimeService.get_titles()
    taj_titles = TajService.get_titles()
    print(grand_titles)
    print(prime_titles)
    print(taj_titles)
    return HttpResponse('SUCCESS')


def test(request):
    titles = GrandService.get_titles()
    text = ", ".join(titles)
    return HttpResponse(text)


def get_grand_showings(request):
    showings = GrandService.get_showings()
    return HttpResponse(showings)

