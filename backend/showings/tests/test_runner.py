"""
Custom test runner for the showings app.
"""

from django.test.runner import DiscoverRunner


class ShowingsTestRunner(DiscoverRunner):
    """Custom test runner that ensures Django is properly configured for tests."""

    def setup_databases(self, **kwargs):
        """Set up the test databases."""
        return super().setup_databases(**kwargs)

    def setup_test_environment(self, **kwargs):
        """Set up the test environment."""
        return super().setup_test_environment(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        """Tear down the test databases."""
        super().teardown_databases(old_config, **kwargs)

    def teardown_test_environment(self, **kwargs):
        """Tear down the test environment."""
        super().teardown_test_environment(**kwargs)
