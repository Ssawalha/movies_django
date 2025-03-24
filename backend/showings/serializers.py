import re

from rest_framework import serializers


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
