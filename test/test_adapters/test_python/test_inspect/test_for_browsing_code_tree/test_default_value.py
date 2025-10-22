import unittest
import inspect
from typing import Optional
from taew.adapters.python.inspect.for_browsing_code_tree.annotated_entity import (
    DefaultValue,
)


class TestDefaultValue(unittest.TestCase):
    """Test DefaultValue implementation in Inspect adapter."""

    def setUp(self) -> None:
        """Set up test functions with different default patterns."""

        def test_func_no_default(x: int) -> None:
            pass

        def test_func_with_default(x: int = 42) -> None:
            pass

        def test_func_none_default(x: Optional[int] = None) -> None:
            pass

        self.no_default_param = inspect.signature(test_func_no_default).parameters["x"]
        self.with_default_param = inspect.signature(test_func_with_default).parameters[
            "x"
        ]
        self.none_default_param = inspect.signature(test_func_none_default).parameters[
            "x"
        ]

    def test_empty_default_value(self) -> None:
        """Test parameter with no default value."""
        default_value = DefaultValue(self.no_default_param)

        self.assertTrue(default_value.is_empty())

    def test_non_empty_default_value(self) -> None:
        """Test parameter with actual default value."""
        default_value = DefaultValue(self.with_default_param)

        self.assertFalse(default_value.is_empty())
        self.assertEqual(default_value.value, 42)

    def test_none_default_value(self) -> None:
        """Test parameter with None as default value."""
        default_value = DefaultValue(self.none_default_param)

        self.assertFalse(default_value.is_empty())
        self.assertIsNone(default_value.value)

    def test_default_value_direct_access(self) -> None:
        """Test that value property returns inspect parameter default directly."""
        default_value = DefaultValue(self.with_default_param)

        # Should return the same as the underlying parameter
        self.assertEqual(default_value.value, self.with_default_param.default)


if __name__ == "__main__":
    unittest.main()
