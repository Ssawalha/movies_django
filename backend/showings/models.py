from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Location(TimestampMixin):
    city = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    address = models.CharField(max_length=100)
    website = models.URLField(
        null=True, validators=[URLValidator(schemes=["http", "https"])]
    )

    class Meta:
        ordering = ["city", "name"]
        indexes = [
            models.Index(fields=["city", "name"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["name", "address"], name="unique_location")
        ]

    def __str__(self):
        return f"{self.name} - {self.address}"

    def clean(self):
        super().clean()
        if self.website and not self.website.startswith(("http://", "https://")):
            raise ValidationError(
                {"website": "Website URL must start with http:// or https://"}
            )


class Batch(TimestampMixin):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    batch_id = models.CharField(max_length=100, unique=True, db_index=True)
    showings = models.ManyToManyField("Showing", related_name="batches")
    movies = models.ManyToManyField("Movie", related_name="batches")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.batch_id} ({self.status})"


class Movie(TimestampMixin):
    title = models.CharField(max_length=100, db_index=True)
    grand_id = models.CharField(max_length=100, null=True, db_index=True)
    prime_id = models.CharField(max_length=100, null=True, db_index=True)
    taj_id = models.CharField(max_length=100, null=True, db_index=True)
    grand_title = models.CharField(max_length=100, null=True)
    prime_title = models.CharField(max_length=100, null=True)
    taj_title = models.CharField(max_length=100, null=True)
    normalized_title = models.CharField(max_length=100, null=True, db_index=True)
    # Can add imdb info like trailer whatever later.

    class Meta:
        ordering = ["normalized_title"]
        indexes = [
            models.Index(fields=["normalized_title"]),
            models.Index(fields=["grand_id"]),
            models.Index(fields=["prime_id"]),
            models.Index(fields=["taj_id"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(grand_id__isnull=False)
                | models.Q(prime_id__isnull=False)
                | models.Q(taj_id__isnull=False),
                name="at_least_one_source_id",
            )
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if not any([self.grand_id, self.prime_id, self.taj_id]):
            raise ValidationError("Movie must have at least one source ID")


class Showing(TimestampMixin):
    movie = models.ForeignKey(
        Movie, related_name="showings", on_delete=models.CASCADE, db_index=True
    )
    location = models.ForeignKey(
        Location, related_name="showings", on_delete=models.CASCADE, db_index=True
    )
    url = models.URLField(
        null=True, validators=[URLValidator(schemes=["http", "https"])]
    )
    date = models.DateField(db_index=True)
    time = models.TimeField(db_index=True)
    is_showing = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["date", "time"]
        indexes = [
            models.Index(fields=["date", "time"]),
            models.Index(fields=["is_showing"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "location", "date", "time"], name="unique_showing"
            )
        ]

    def __str__(self):
        return f"{self.movie.title} at {self.location.name} - {self.date} {self.time}"

    def clean(self):
        super().clean()
        if self.date < timezone.now().date():
            raise ValidationError({"date": "Showing date cannot be in the past"})
