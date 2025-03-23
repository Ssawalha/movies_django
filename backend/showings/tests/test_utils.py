import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.conf import settings


def get_fixture_path(service: str, filename: str) -> str:
    """Get the path to a test fixture file."""
    return os.path.join(
        settings.BASE_DIR, "showings", "tests", "fixtures", service, filename
    )


def load_fixture(service: str, filename: str) -> bytes:
    """Load a test fixture file."""
    fixture_path = get_fixture_path(service, filename)
    with open(fixture_path, "rb") as f:
        return f.read()


def mock_response(content: bytes, status_code: int = 200) -> MagicMock:
    """Create a mock response object."""
    mock = MagicMock()
    mock.content = content
    mock.status_code = status_code
    return mock


def patch_cinema_service(service_name: str, fixture_name: str):
    """Decorator to patch a cinema service with fixture data."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            fixture_content = load_fixture(service_name, fixture_name)
            mock_response_obj = mock_response(fixture_content)

            with patch(f"requests.post", return_value=mock_response_obj):
                return func(*args, **kwargs)

        return wrapper

    return decorator
