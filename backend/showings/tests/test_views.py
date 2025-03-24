from datetime import time
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APITestCase
from showings.models import Location, Movie, Showing
from showings.views import ShowingView


@override_settings(ALLOWED_HOSTS=["testserver"])
class TestShowingView(APITestCase):
    def setUp(self):
        # Create test data with hardcoded locations
        self.grand_location = Location.objects.create(
            name="Grand Cinema City Mall", city="Amman", address="City Mall, Amman"
        )

        self.taj_location = Location.objects.create(
            name="Taj Mall", city="Amman", address="Taj Mall, Amman"
        )

        self.prime_location = Location.objects.create(
            name="Prime Mall", city="Amman", address="Prime Mall, Amman"
        )

        self.movie = Movie.objects.create(
            title="Test Movie",
            normalized_title="test movie",
            grand_id="123",
            grand_title="Test Movie",
            taj_title="Test Movie",
            prime_title="Test Movie",
        )

        # Create showings for each location
        self.grand_showing = Showing.objects.create(
            movie=self.movie,
            location=self.grand_location,
            date="2025-03-24",
            time="14:00:00",
            is_showing=True,
            url="http://grand.com",
        )

        self.taj_showing = Showing.objects.create(
            movie=self.movie,
            location=self.taj_location,
            date="2025-03-24",
            time="15:00:00",
            is_showing=True,
            url="http://taj.com",
        )

        self.prime_showing = Showing.objects.create(
            movie=self.movie,
            location=self.prime_location,
            date="2025-03-24",
            time="16:00:00",
            is_showing=True,
            url="http://prime.com",
        )

    def test_get_active_showings(self):
        """Test getting active showings."""
        response = self.client.get("/showings/active/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["count"], 3)  # Should have 3 showings

        # Verify Grand Cinema showing
        grand_showing = next(
            s
            for s in response.data["showings"]
            if s["location__name"] == "Grand Cinema City Mall"
        )
        self.assertEqual(grand_showing["movie__title"], self.movie.title)
        self.assertEqual(grand_showing["location__name"], self.grand_location.name)
        self.assertEqual(str(grand_showing["date"]), self.grand_showing.date)
        self.assertEqual(str(grand_showing["time"]), self.grand_showing.time)
        self.assertEqual(grand_showing["url"], self.grand_showing.url)

        # Verify Taj Mall showing
        taj_showing = next(
            s for s in response.data["showings"] if s["location__name"] == "Taj Mall"
        )
        self.assertEqual(taj_showing["movie__title"], self.movie.title)
        self.assertEqual(taj_showing["location__name"], self.taj_location.name)
        self.assertEqual(str(taj_showing["date"]), str(self.taj_showing.date))
        self.assertEqual(str(taj_showing["time"]), str(self.taj_showing.time))
        self.assertEqual(taj_showing["url"], self.taj_showing.url)

        # Verify Prime Mall showing
        prime_showing = next(
            s for s in response.data["showings"] if s["location__name"] == "Prime Mall"
        )
        self.assertEqual(prime_showing["movie__title"], self.movie.title)
        self.assertEqual(prime_showing["location__name"], self.prime_location.name)
        self.assertEqual(str(prime_showing["date"]), str(self.prime_showing.date))
        self.assertEqual(str(prime_showing["time"]), str(self.prime_showing.time))
        self.assertEqual(prime_showing["url"], self.prime_showing.url)

    @patch("showings.views.ShowingService")
    def test_post_scrape(self, mock_service):
        """Test scraping movies and showings."""
        # Mock the service instance and its methods
        mock_instance = mock_service.return_value
        mock_instance.refresh_and_save.return_value = (
            [self.movie],
            [self.grand_showing, self.taj_showing, self.prime_showing],
        )

        response = self.client.post("/showings/active/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertIn("Successfully scraped", response.data["message"])
        mock_instance.refresh_and_save.assert_called_once()

    def test_invalid_method(self):
        """Test that invalid HTTP methods are rejected."""
        response = self.client.put("/showings/active/")
        self.assertEqual(response.status_code, 405)
