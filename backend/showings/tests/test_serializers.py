import unittest

from rest_framework.exceptions import ErrorDetail
from showings.serializers import (
    GrandClientShowingDatesSerializer,
    GrandClientShowingTimesSerializer,
    PrimeClientTitleShowingsSerializer,
    TajClientTitleShowingsSerializer,
)


class TestGrandClientShowingDatesSerializer(unittest.TestCase):
    def test_valid_data(self):
        serializer = GrandClientShowingDatesSerializer(data={"grand_id": "123"})
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        # Test with missing required field
        serializer = GrandClientShowingDatesSerializer(data={"invalid_field": "123"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

        # Test with empty string
        serializer = GrandClientShowingDatesSerializer(data={"grand_id": ""})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field cannot be empty.", code="blank")],
        )

        # Test with None
        serializer = GrandClientShowingDatesSerializer(data={"grand_id": None})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field cannot be null.", code="null")],
        )


class TestGrandClientShowingTimesSerializer(unittest.TestCase):
    def test_valid_data(self):
        serializer = GrandClientShowingTimesSerializer(
            data={"grand_id": "123", "date": "2023-01-01"}
        )
        self.assertTrue(serializer.is_valid())

    def test_missing_grand_id(self):
        serializer = GrandClientShowingTimesSerializer(data={"date": "2023-01-01"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

    def test_missing_date(self):
        serializer = GrandClientShowingTimesSerializer(data={"grand_id": "123"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("date", serializer.errors)
        self.assertEqual(
            serializer.errors["date"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

    def test_invalid_date(self):
        serializer = GrandClientShowingTimesSerializer(
            data={"grand_id": "123", "date": "invalid_date"}
        )
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("date", serializer.errors)
        self.assertEqual(
            serializer.errors["date"],
            [
                ErrorDetail(
                    string="This field must be in the format YYYY-MM-DD.",
                    code="invalid",
                )
            ],
        )


class TestTajClientTitleShowingsSerializer(unittest.TestCase):
    def test_valid_data(self):
        serializer = TajClientTitleShowingsSerializer(data={"taj_id": "123"})
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        # Test with missing required field
        serializer = TajClientTitleShowingsSerializer(data={"invalid_field": "123"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("taj_id", serializer.errors)
        self.assertEqual(
            serializer.errors["taj_id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

        # Test with empty string
        serializer = TajClientTitleShowingsSerializer(data={"taj_id": ""})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("taj_id", serializer.errors)
        self.assertEqual(
            serializer.errors["taj_id"],
            [ErrorDetail(string="This field cannot be empty.", code="blank")],
        )

        # Test with None
        serializer = TajClientTitleShowingsSerializer(data={"taj_id": None})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("taj_id", serializer.errors)
        self.assertEqual(
            serializer.errors["taj_id"],
            [ErrorDetail(string="This field cannot be null.", code="null")],
        )


class TestPrimeClientTitleShowingsSerializer(unittest.TestCase):
    def test_valid_data(self):
        serializer = PrimeClientTitleShowingsSerializer(data={"prime_id": "123"})
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        # Test with missing required field
        serializer = PrimeClientTitleShowingsSerializer(data={"invalid_field": "123"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("prime_id", serializer.errors)
        self.assertEqual(
            serializer.errors["prime_id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

        # Test with empty string
        serializer = PrimeClientTitleShowingsSerializer(data={"prime_id": ""})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("prime_id", serializer.errors)
        self.assertEqual(
            serializer.errors["prime_id"],
            [ErrorDetail(string="This field cannot be empty.", code="blank")],
        )

        # Test with None
        serializer = PrimeClientTitleShowingsSerializer(data={"prime_id": None})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("prime_id", serializer.errors)
        self.assertEqual(
            serializer.errors["prime_id"],
            [ErrorDetail(string="This field cannot be null.", code="null")],
        )
