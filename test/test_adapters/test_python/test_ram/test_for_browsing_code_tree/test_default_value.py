import unittest
from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
    DefaultValue,
)


class TestDefaultValue(unittest.TestCase):
    """Test DefaultValue implementation in RAM adapter."""

    def test_empty_default_value(self) -> None:
        """Test default value with no value."""
        default_value = DefaultValue(_value=None, _is_empty=True)

        self.assertTrue(default_value.is_empty())
        # Should still be accessible but indicates no default
        self.assertIsNone(default_value.value)

    def test_non_empty_default_value(self) -> None:
        """Test default value with actual value."""
        test_value = "test_default"
        default_value = DefaultValue(_value=test_value, _is_empty=False)

        self.assertFalse(default_value.is_empty())
        self.assertEqual(default_value.value, test_value)

    def test_various_default_types(self) -> None:
        """Test default values with various types."""
        test_cases = [
            (42, int),
            ("hello", str),
            (3.14, float),
            (True, bool),
            ([1, 2, 3], list),
            ({"key": "value"}, dict),
            (None, type(None)),
        ]

        for test_value, expected_type in test_cases:
            with self.subTest(value=test_value, type=expected_type):
                default_value = DefaultValue(_value=test_value, _is_empty=False)

                self.assertFalse(default_value.is_empty())
                self.assertEqual(default_value.value, test_value)
                self.assertIsInstance(default_value.value, expected_type)


if __name__ == "__main__":
    unittest.main()
