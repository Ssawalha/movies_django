"""
Base test case for the showings app.
"""

import django
from django.test import TestCase
from faker import Faker

# Initialize Django for test discovery
django.setup()


class ShowingsTestCase(TestCase):
    """Base test case that provides common functionality for showings app tests."""

    fake = Faker()

    @classmethod
    def setUpClass(cls):
        """Set up data that should be shared across all tests in the class."""
        super().setUpClass()

    def setUp(self):
        """Set up data for each individual test."""
        super().setUp()
