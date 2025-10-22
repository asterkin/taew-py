import unittest
from decimal import Decimal
from datetime import date, datetime
from uuid import UUID
from enum import Enum
from typing import NamedTuple

from taew.domain.json import is_jsonable


class TestIsJsonable(unittest.TestCase):
    """Test cases for is_jsonable function."""

    def test_basic_json_types_return_true(self) -> None:
        """Test that basic JSON types are recognized as JSONable."""
        self.assertTrue(is_jsonable(str))
        self.assertTrue(is_jsonable(int))
        self.assertTrue(is_jsonable(float))
        self.assertTrue(is_jsonable(bool))
        self.assertTrue(is_jsonable(list))
        self.assertTrue(is_jsonable(dict))

    def test_none_type_returns_true(self) -> None:
        """Test that NoneType is recognized as JSONable."""
        self.assertTrue(is_jsonable(type(None)))

    def test_extended_types_return_false(self) -> None:
        """Test that extended types are not recognized as JSONable."""
        self.assertFalse(is_jsonable(Decimal))
        self.assertFalse(is_jsonable(date))
        self.assertFalse(is_jsonable(datetime))
        self.assertFalse(is_jsonable(UUID))
        self.assertFalse(is_jsonable(bytes))

    def test_enum_returns_false(self) -> None:
        """Test that Enum types are not recognized as JSONable."""

        class TestEnum(Enum):
            VALUE = "test"

        self.assertFalse(is_jsonable(TestEnum))

    def test_named_tuple_returns_false(self) -> None:
        """Test that NamedTuple types are not recognized as JSONable."""

        class TestTuple(NamedTuple):
            field: str

        self.assertFalse(is_jsonable(TestTuple))

    def test_custom_classes_return_false(self) -> None:
        """Test that custom classes are not recognized as JSONable."""

        class CustomClass:
            pass

        self.assertFalse(is_jsonable(CustomClass))


if __name__ == "__main__":
    unittest.main()
