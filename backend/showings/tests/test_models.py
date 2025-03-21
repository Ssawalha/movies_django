from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from showings.models import Location, Movie, Showing, Batch
from showings.tests.test_base import ShowingsTestCase


class TestLocation(ShowingsTestCase):
    """Test cases for the Location model."""

    def setUp(self):
        super().setUp()
        self.valid_location_data = {
            "city": self.fake.city(),
            "name": self.fake.company(),
            "address": self.fake.address(),
            "website": self.fake.url(),
        }

    def test_create_valid_location(self):
        """Test creating a valid location."""
        location = Location.objects.create(**self.valid_location_data)
        self.assertEqual(str(location), f"{location.name} - {location.address}")
        self.assertTrue(location.created_at)
        self.assertTrue(location.updated_at)

    def test_invalid_website_url(self):
        """Test validation of invalid website URL."""
        invalid_data = self.valid_location_data.copy()
        invalid_data["website"] = "invalid-url"
        location = Location(**invalid_data)
        with self.assertRaises(ValidationError):
            location.full_clean()

    def test_unique_location_constraint(self):
        """Test unique constraint for location."""
        Location.objects.create(**self.valid_location_data)
        with self.assertRaises(Exception):
            Location.objects.create(**self.valid_location_data)


class TestMovie(ShowingsTestCase):
    """Test cases for the Movie model."""

    def setUp(self):
        super().setUp()
        self.valid_movie_data = {
            "title": self.fake.catch_phrase(),
            "grand_id": f"G{self.fake.random_number(digits=6)}",
            "normalized_title": self.fake.catch_phrase().lower(),
        }

    def test_create_valid_movie(self):
        """Test creating a valid movie."""
        movie = Movie.objects.create(**self.valid_movie_data)
        self.assertEqual(str(movie), movie.title)
        self.assertTrue(movie.created_at)
        self.assertTrue(movie.updated_at)

    def test_movie_without_source_id(self):
        """Test validation of movie without source ID."""
        invalid_data = {
            "title": self.fake.catch_phrase(),
            "normalized_title": self.fake.catch_phrase().lower(),
        }
        movie = Movie(**invalid_data)
        with self.assertRaises(ValidationError):
            movie.full_clean()

    def test_movie_with_multiple_sources(self):
        """Test movie with multiple source IDs."""
        movie_data = self.valid_movie_data.copy()
        movie_data.update(
            {
                "prime_id": f"P{self.fake.random_number(digits=6)}",
                "taj_id": f"T{self.fake.random_number(digits=6)}",
            }
        )
        movie = Movie.objects.create(**movie_data)
        self.assertEqual(movie.grand_id, movie_data["grand_id"])
        self.assertEqual(movie.prime_id, movie_data["prime_id"])
        self.assertEqual(movie.taj_id, movie_data["taj_id"])


class TestShowing(ShowingsTestCase):
    """Test cases for the Showing model."""

    def setUp(self):
        super().setUp()
        self.location = Location.objects.create(
            city=self.fake.city(), name=self.fake.company(), address=self.fake.address()
        )
        self.movie = Movie.objects.create(
            title=self.fake.catch_phrase(),
            grand_id=f"G{self.fake.random_number(digits=6)}",
            normalized_title=self.fake.catch_phrase().lower(),
        )
        self.tomorrow = timezone.now().date() + timedelta(days=1)
        self.valid_showing_data = {
            "movie": self.movie,
            "location": self.location,
            "date": self.tomorrow,
            "time": self.fake.time(),
            "url": self.fake.url(),
            "is_showing": self.fake.boolean(),
        }

    def test_create_valid_showing(self):
        """Test creating a valid showing."""
        showing = Showing.objects.create(**self.valid_showing_data)
        self.assertEqual(
            str(showing),
            f"{showing.movie.title} at {showing.location.name} - {showing.date} {showing.time}",
        )
        self.assertTrue(showing.created_at)
        self.assertTrue(showing.updated_at)

    def test_past_date_validation(self):
        """Test validation of past date."""
        yesterday = timezone.now().date() - timedelta(days=1)
        invalid_data = self.valid_showing_data.copy()
        invalid_data["date"] = yesterday
        showing = Showing(**invalid_data)
        with self.assertRaises(ValidationError):
            showing.full_clean()

    def test_unique_showing_constraint(self):
        """Test unique constraint for showing."""
        Showing.objects.create(**self.valid_showing_data)
        with self.assertRaises(Exception):
            Showing.objects.create(**self.valid_showing_data)

    def test_invalid_url(self):
        """Test validation of invalid URL."""
        invalid_data = self.valid_showing_data.copy()
        invalid_data["url"] = "invalid-url"
        showing = Showing(**invalid_data)
        with self.assertRaises(ValidationError):
            showing.full_clean()


class TestBatch(ShowingsTestCase):
    """Test cases for the Batch model."""

    def setUp(self):
        super().setUp()
        self.valid_batch_data = {
            "batch_id": f"BATCH_{self.fake.date_time().strftime('%Y_%m_%d')}",
            "status": self.fake.random_element(
                elements=[status[0] for status in Batch.Status.choices]
            ),
        }

    def test_create_valid_batch(self):
        """Test creating a valid batch."""
        batch = Batch.objects.create(**self.valid_batch_data)
        self.assertEqual(str(batch), f"{batch.batch_id} ({batch.status})")
        self.assertTrue(batch.created_at)
        self.assertTrue(batch.updated_at)

    def test_unique_batch_id_constraint(self):
        """Test unique constraint for batch ID."""
        Batch.objects.create(**self.valid_batch_data)
        with self.assertRaises(Exception):
            Batch.objects.create(**self.valid_batch_data)

    def test_valid_status_choices(self):
        """Test valid status choices."""
        batch = Batch.objects.create(**self.valid_batch_data)
        for status in Batch.Status.choices:
            batch.status = status[0]
            batch.full_clean()
            batch.save()

    def test_invalid_status(self):
        """Test validation of invalid status."""
        invalid_data = self.valid_batch_data.copy()
        invalid_data["status"] = "INVALID_STATUS"
        batch = Batch(**invalid_data)
        with self.assertRaises(ValidationError):
            batch.full_clean()

    def test_batch_relationships(self):
        """Test batch relationships with movies and showings."""
        batch = Batch.objects.create(**self.valid_batch_data)

        movie = Movie.objects.create(
            title=self.fake.catch_phrase(),
            grand_id=f"G{self.fake.random_number(digits=6)}",
            normalized_title=self.fake.catch_phrase().lower(),
        )
        location = Location.objects.create(
            city=self.fake.city(), name=self.fake.company(), address=self.fake.address()
        )
        showing = Showing.objects.create(
            movie=movie,
            location=location,
            date=timezone.now().date() + timedelta(days=1),
            time=self.fake.time(),
            is_showing=self.fake.boolean(),
        )

        batch.movies.add(movie)
        batch.showings.add(showing)

        self.assertEqual(batch.movies.count(), 1)
        self.assertEqual(batch.showings.count(), 1)
        self.assertEqual(batch.movies.first(), movie)
        self.assertEqual(batch.showings.first(), showing)
