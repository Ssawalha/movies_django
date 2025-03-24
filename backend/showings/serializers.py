import re

from rest_framework import serializers
from showings.models import Movie


class BaseIdSerializer(serializers.Serializer):
    id_field_name = "id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.id_field_name] = serializers.CharField(
            required=True,
            allow_blank=False,
            allow_null=False,
            error_messages={
                "blank": "This field cannot be empty.",
                "required": "This field is required.",
                "null": "This field cannot be null.",
            },
        )


class GrandClientShowingDatesSerializer(BaseIdSerializer):
    id_field_name = "grand_id"


class GrandClientShowingTimesSerializer(GrandClientShowingDatesSerializer):
    date = serializers.CharField(
        required=True,
        error_messages={
            "invalid": "This field must be in the format YYYY-MM-DD.",
            "required": "This field is required.",
            "blank": "This field cannot be empty.",
            "null": "This field cannot be null.",
        },
    )

    def validate_date(self, value):
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if not date_pattern.match(value):
            raise serializers.ValidationError(
                "This field must be in the format YYYY-MM-DD."
            )
        try:
            serializers.DateField().to_internal_value(value)
        except:
            raise serializers.ValidationError("Invalid date format.")
        return value


class TajClientTitleShowingsSerializer(BaseIdSerializer):
    id_field_name = "taj_id"


class PrimeClientTitleShowingsSerializer(BaseIdSerializer):
    id_field_name = "prime_id"


class GrandServiceGetShowingDatesSerializer(BaseIdSerializer):
    id_field_name = "grand_id"


class GrandServiceGetShowingtimesSerializer(GrandServiceGetShowingDatesSerializer):
    date = serializers.CharField(
        required=True,
        error_messages={
            "invalid": "This field must be in the format YYYY-MM-DD.",
            "required": "This field is required.",
            "blank": "This field cannot be empty.",
            "null": "This field cannot be null.",
        },
    )

    def validate_date(self, value):
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if not date_pattern.match(value):
            raise serializers.ValidationError(
                "This field must be in the format YYYY-MM-DD."
            )
        try:
            serializers.DateField().to_internal_value(value)
        except:
            raise serializers.ValidationError("Invalid date format.")
        return value


class ShowingServiceTitleSerializer(serializers.Serializer):
    """Serializer for titles in ShowingService."""

    title_grand = serializers.CharField(required=False, allow_blank=True)
    grand_id = serializers.CharField(required=False, allow_blank=True)
    title_prime = serializers.CharField(required=False, allow_blank=True)
    prime_id = serializers.CharField(required=False, allow_blank=True)
    title_taj = serializers.CharField(required=False, allow_blank=True)
    taj_id = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        """Validate that at least one ID is present."""
        if not any([data.get("grand_id"), data.get("taj_id"), data.get("prime_id")]):
            raise serializers.ValidationError("At least one cinema ID must be present")
        if not any(
            [data.get("title_grand"), data.get("title_prime"), data.get("title_taj")]
        ):
            raise serializers.ValidationError("At least one title must be present")
        return data


class ShowingServiceShowingSerializer(serializers.Serializer):
    """Serializer for showings in ShowingService."""

    title = serializers.CharField(required=True)
    date = serializers.CharField(required=True)
    time = serializers.CharField(required=True)
    location = serializers.CharField(required=True)

    def validate_date(self, value):
        """Validate date format."""
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if not date_pattern.match(value):
            raise serializers.ValidationError("Date must be in format YYYY-MM-DD")
        return value

    def validate_time(self, value):
        """Validate time format."""
        time_pattern = re.compile(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
        if not time_pattern.match(value):
            raise serializers.ValidationError("Time must be in format HH:MM")
        return value


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie model."""

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "grand_id",
            "prime_id",
            "taj_id",
            "grand_title",
            "prime_title",
            "taj_title",
            "normalized_title",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        """Validate that at least one source ID is present."""
        if not any([data.get("grand_id"), data.get("prime_id"), data.get("taj_id")]):
            raise serializers.ValidationError("At least one cinema ID must be present")
        return data
