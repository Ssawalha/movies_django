from django.core.exceptions import ValidationError
from django.db import migrations


def validate_location_data(name, city, address):
    """Validate location data before creation."""
    if not name or not city or not address:
        raise ValidationError("Location name, city, and address are required")


def add_hardcoded_locations(apps, schema_editor):
    Location = apps.get_model("showings", "Location")

    locations_data = [
        {"name": "Grand Cinema", "city": "Amman", "address": "City Mall"},
        {"name": "Taj Cinema", "city": "Amman", "address": "Taj Mall"},
        {
            "name": "Prime Cinema",
            "city": "Amman",
            "address": "Baraka Mall",
        },
    ]

    for location_data in locations_data:
        try:
            # Validate data
            validate_location_data(
                location_data["name"], location_data["city"], location_data["address"]
            )

            # Check if location already exists
            if not Location.objects.filter(name=location_data["name"]).exists():
                Location.objects.create(**location_data)
            else:
                print(f"Location {location_data['name']} already exists, skipping...")

        except ValidationError as e:
            print(f"Validation error for location {location_data['name']}: {str(e)}")
        except Exception as e:
            print(f"Error creating location {location_data['name']}: {str(e)}")


def remove_hardcoded_locations(apps, schema_editor):
    Location = apps.get_model("showings", "Location")
    try:
        # Only remove locations that were created by this migration
        Location.objects.filter(
            name__in=["Grand Cinema", "Taj Cinema", "Prime Cinema"]
        ).delete()
    except Exception as e:
        print(f"Error removing locations: {str(e)}")


class Migration(migrations.Migration):
    dependencies = [
        ("showings", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_hardcoded_locations, remove_hardcoded_locations),
    ]
