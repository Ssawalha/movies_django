"""
Test settings for the movie_showings project.
"""

from .settings import *  # noqa

# Use the custom test runner
TEST_RUNNER = "showings.tests.test_runner.ShowingsTestRunner"

# Use an in-memory SQLite database for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable debugging in tests
DEBUG = False

# Use faster password hasher during tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
