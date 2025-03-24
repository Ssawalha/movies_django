import unittest

from rest_framework.exceptions import ErrorDetail
from showings.serializers import (
    BaseIdSerializer,
    GrandClientShowingDatesSerializer,
    GrandClientShowingTimesSerializer,
    GrandServiceGetShowingDatesSerializer,
    GrandServiceGetShowingtimesSerializer,
    PrimeClientTitleShowingsSerializer,
    TajClientTitleShowingsSerializer,
)


class BaseIdSerializerTest(unittest.TestCase):
    """Test cases for the base ID serializer."""

    def setUp(self):
        self.serializer = BaseIdSerializer

    def test_default_id_field_name(self):
        """Test that the default id field name is 'id'."""
        self.assertEqual(self.serializer.id_field_name, "id")

    def test_valid_data(self):
        """Test validation with valid data."""
        serializer = self.serializer(data={"id": "123"})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["id"], "123")

    def test_missing_id(self):
        """Test validation when id field is missing."""
        serializer = self.serializer(data={})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("id", serializer.errors)
        self.assertEqual(
            serializer.errors["id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

    def test_empty_id(self):
        """Test validation when id field is empty."""
        serializer = self.serializer(data={"id": ""})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("id", serializer.errors)
        self.assertEqual(
            serializer.errors["id"],
            [ErrorDetail(string="This field cannot be empty.", code="blank")],
        )

    def test_none_id(self):
        """Test validation when id field is None."""
        serializer = self.serializer(data={"id": None})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("id", serializer.errors)
        self.assertEqual(
            serializer.errors["id"],
            [ErrorDetail(string="This field cannot be null.", code="null")],
        )

    def test_additional_fields(self):
        serializer = self.serializer(data={"id": "123", "other_field": "other value"})
        self.assertTrue(serializer.is_valid(raise_exception=False))


class TestGrandClientShowingDatesSerializer(unittest.TestCase):

    def setUp(self):
        self.serializer = GrandClientShowingDatesSerializer

    def test_valid_data(self):
        serializer = self.serializer(data={"grand_id": "123"})
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        # Test with missing required field
        serializer = self.serializer(data={"invalid_field": "123"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

        # Test with empty string
        serializer = self.serializer(data={"grand_id": ""})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field cannot be empty.", code="blank")],
        )

        # Test with None
        serializer = self.serializer(data={"grand_id": None})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field cannot be null.", code="null")],
        )


class TestGrandClientShowingTimesSerializer(unittest.TestCase):

    def setUp(self):
        self.serializer = GrandClientShowingTimesSerializer

    def test_valid_data(self):
        serializer = self.serializer(data={"grand_id": "123", "date": "2023-01-01"})
        self.assertTrue(serializer.is_valid())

    def test_missing_grand_id(self):
        serializer = self.serializer(data={"date": "2023-01-01"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

    def test_missing_date(self):
        serializer = self.serializer(data={"grand_id": "123"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("date", serializer.errors)
        self.assertEqual(
            serializer.errors["date"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

    def test_invalid_date(self):
        serializer = self.serializer(data={"grand_id": "123", "date": "invalid_date"})
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

    def setUp(self):
        self.serializer = TajClientTitleShowingsSerializer

    def test_valid_data(self):
        serializer = self.serializer(data={"taj_id": "123"})
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        # Test with missing required field
        serializer = self.serializer(data={"invalid_field": "123"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("taj_id", serializer.errors)
        self.assertEqual(
            serializer.errors["taj_id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

        # Test with empty string
        serializer = self.serializer(data={"taj_id": ""})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("taj_id", serializer.errors)
        self.assertEqual(
            serializer.errors["taj_id"],
            [ErrorDetail(string="This field cannot be empty.", code="blank")],
        )

        # Test with None
        serializer = self.serializer(data={"taj_id": None})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("taj_id", serializer.errors)
        self.assertEqual(
            serializer.errors["taj_id"],
            [ErrorDetail(string="This field cannot be null.", code="null")],
        )


class TestPrimeClientTitleShowingsSerializer(unittest.TestCase):

    def setUp(self):
        self.serializer = PrimeClientTitleShowingsSerializer

    def test_valid_data(self):
        serializer = self.serializer(data={"prime_id": "123"})
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        # Test with missing required field
        serializer = self.serializer(data={"invalid_field": "123"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("prime_id", serializer.errors)
        self.assertEqual(
            serializer.errors["prime_id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

        # Test with empty string
        serializer = self.serializer(data={"prime_id": ""})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("prime_id", serializer.errors)
        self.assertEqual(
            serializer.errors["prime_id"],
            [ErrorDetail(string="This field cannot be empty.", code="blank")],
        )

        # Test with None
        serializer = self.serializer(data={"prime_id": None})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("prime_id", serializer.errors)
        self.assertEqual(
            serializer.errors["prime_id"],
            [ErrorDetail(string="This field cannot be null.", code="null")],
        )


class TestGrandServiceGetShowingDatesSerializer(unittest.TestCase):

    def setUp(self):
        self.serializer = GrandServiceGetShowingDatesSerializer

    def test_valid_data(self):
        serializer = self.serializer(data={"grand_id": "123"})
        self.assertTrue(serializer.is_valid())

    def test_missing_id(self):
        serializer = self.serializer(data={})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

    def test_wrong_id(self):
        serializer = self.serializer(data={"other_id": "invalid id"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

    def test_empty_id(self):
        serializer = self.serializer(data={"grand_id": ""})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field cannot be empty.", code="blank")],
        )

    def test_none_id(self):
        serializer = self.serializer(data={"grand_id": None})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field cannot be null.", code="null")],
        )

    def test_additional_fields(self):
        serializer = self.serializer(
            data={"grand_id": "123", "other_field": "other value"}
        )
        self.assertTrue(serializer.is_valid(raise_exception=False))


class TestGrandServiceGetShowingtimesSerializer(unittest.TestCase):
    def setUp(self):
        self.serializer = GrandServiceGetShowingtimesSerializer

    def test_valid_data(self):
        serializer = self.serializer(data={"grand_id": "123", "date": "2023-01-01"})
        self.assertTrue(serializer.is_valid())

    def test_missing_fields(self):
        serializer = self.serializer(data={})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )
        self.assertIn("date", serializer.errors)
        self.assertEqual(
            serializer.errors["date"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

    def test_wrong_id(self):
        serializer = self.serializer(
            data={"other_id": "invalid id", "date": "2023-01-01"}
        )
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

    def test_invalid_date(self):
        serializer = self.serializer(data={"grand_id": "123", "date": "invalid_date"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("date", serializer.errors)

    def test_empty_id(self):
        serializer = self.serializer(data={"grand_id": "", "date": "2023-01-01"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field cannot be empty.", code="blank")],
        )

    def test_empty_date(self):
        serializer = self.serializer(data={"grand_id": "123", "date": ""})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("date", serializer.errors)

    def test_none_id(self):
        serializer = self.serializer(data={"grand_id": None, "date": "2023-01-01"})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("grand_id", serializer.errors)
        self.assertEqual(
            serializer.errors["grand_id"],
            [ErrorDetail(string="This field cannot be null.", code="null")],
        )

    def test_none_date(self):
        serializer = self.serializer(data={"grand_id": "123", "date": None})
        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertIn("date", serializer.errors)

    def test_additional_fields(self):
        serializer = self.serializer(
            data={"grand_id": "123", "date": "2023-01-01", "other_field": "other value"}
        )
        self.assertTrue(serializer.is_valid(raise_exception=False))
