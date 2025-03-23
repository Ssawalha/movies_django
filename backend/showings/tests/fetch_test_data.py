import json
import os
from datetime import datetime

from django.conf import settings
from showings.services import GrandService, PrimeService, TajService


def save_html_response(service: str, filename: str, content: bytes):
    """Save HTML response to a fixture file."""
    fixtures_dir = os.path.join(
        settings.BASE_DIR, "showings", "tests", "fixtures", service
    )
    os.makedirs(fixtures_dir, exist_ok=True)

    filepath = os.path.join(fixtures_dir, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    print(f"Saved {filename} to {fixtures_dir}")


def fetch_grand_data():
    """Fetch and save Grand Cinema data."""
    # Get titles page
    titles_page = GrandService.client.get_titles_page()
    save_html_response("grand", "titles_page.html", titles_page)

    # Get first movie's showing dates
    titles = GrandService.parser.parse_titles_from_titles_page(titles_page)
    if titles:
        first_movie = titles[0]
        dates_page = GrandService.client.get_title_showing_dates(
            first_movie["grand_id"]
        )
        save_html_response("grand", "title_showing_dates_page.html", dates_page)

        # Get first date's showing times
        dates = GrandService.parser.parse_showing_dates(dates_page)
        if dates:
            times_page = GrandService.client.get_title_showing_times_on_date(
                first_movie["grand_id"], dates[0]
            )
            save_html_response("grand", "title_showing_times_page.html", times_page)


def fetch_taj_data():
    """Fetch and save Taj Cinemas data."""
    # Get titles page
    titles_page = TajService.client.get_titles_page()
    save_html_response("taj", "titles_page.html", titles_page)

    # Get first movie's showing dates
    titles = TajService.parser.parse_titles_from_titles_page(titles_page)
    if titles:
        first_movie = titles[0]
        dates_page = TajService.client.get_title_showings_page(first_movie)
        save_html_response("taj", "title_showings_page.html", dates_page)


def fetch_prime_data():
    """Fetch and save Prime Cinemas data."""
    # Get titles page
    titles_page = PrimeService.client.get_titles_page()
    save_html_response("prime", "titles_page.html", titles_page)

    # Get first movie's showings
    titles = PrimeService.parser.parse_titles_from_titles_page(titles_page)
    if titles:
        first_movie = titles[0]
        showings_page = PrimeService.client.get_title_showings_page(first_movie)
        save_html_response("prime", "title_showings_page.html", showings_page)


def main():
    """Fetch and save test data from all clients."""
    print("Fetching test data...")

    try:
        fetch_grand_data()
        print("✓ Grand Cinema data fetched")
    except Exception as e:
        print(f"✗ Error fetching Grand Cinema data: {e}")

    try:
        fetch_taj_data()
        print("✓ Taj Cinemas data fetched")
    except Exception as e:
        print(f"✗ Error fetching Taj Cinemas data: {e}")

    try:
        fetch_prime_data()
        print("✓ Prime Cinemas data fetched")
    except Exception as e:
        print(f"✗ Error fetching Prime Cinemas data: {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()
