import unittest
from typing import Callable
from unittest.mock import Mock, patch


class TestExtractShortDescription(unittest.TestCase):
    """Test extract_short_description function."""

    @staticmethod
    def _get_extract_function() -> Callable[[object], str]:
        """Factory method to get extract_short_description function."""
        from taew.adapters.python.inspect.for_browsing_code_tree.object_description import (
            extract_object_description,
        )

        return extract_object_description

    def test_function_with_single_line_docstring(self) -> None:
        """Test extraction from function with single line docstring."""

        def test_function() -> None:
            """This is a test function."""
            pass

        extract_short_description = self._get_extract_function()
        result = extract_short_description(test_function)

        self.assertEqual(result, "This is a test function.")

    def test_function_with_multiline_docstring(self) -> None:
        """Test extraction from function with multiline docstring."""

        def test_function() -> None:
            """This is a test function.

            This is additional detail that should not be included
            in the short description.
            """
            pass

        extract_short_description = self._get_extract_function()
        result = extract_short_description(test_function)

        self.assertEqual(result, "This is a test function.")

    def test_class_with_docstring(self) -> None:
        """Test extraction from class with docstring."""

        class TestClass:
            """This is a test class."""

            pass

        extract_short_description = self._get_extract_function()
        result = extract_short_description(TestClass)

        self.assertEqual(result, "This is a test class.")

    def test_module_with_docstring(self) -> None:
        """Test extraction from module with docstring."""

        # Create a mock module with docstring
        mock_module = Mock()
        mock_module.__doc__ = "This is a test module."

        extract_short_description = self._get_extract_function()
        result = extract_short_description(mock_module)

        self.assertEqual(result, "This is a test module.")

    def test_object_without_docstring(self) -> None:
        """Test extraction from object without docstring."""

        def no_doc_function() -> None:
            pass

        extract_short_description = self._get_extract_function()
        result = extract_short_description(no_doc_function)

        self.assertEqual(result, "")

    def test_object_with_empty_docstring(self) -> None:
        """Test extraction from object with empty docstring."""

        def empty_doc_function() -> None:
            """"""
            pass

        extract_short_description = self._get_extract_function()
        result = extract_short_description(empty_doc_function)

        self.assertEqual(result, "")

    def test_object_with_whitespace_only_docstring(self) -> None:
        """Test extraction from object with whitespace-only docstring."""

        def whitespace_doc_function() -> None:
            """ """
            pass

        extract_short_description = self._get_extract_function()
        result = extract_short_description(whitespace_doc_function)

        self.assertEqual(result, "")

    def test_object_with_none_docstring(self) -> None:
        """Test extraction from object with None docstring."""
        # Create object with None __doc__
        mock_obj = Mock()
        mock_obj.__doc__ = None

        extract_short_description = self._get_extract_function()
        result = extract_short_description(mock_obj)

        self.assertEqual(result, "")

    def test_inspect_getdoc_failure(self) -> None:
        """Test graceful handling when inspect.getdoc fails."""
        mock_obj = Mock()

        extract_short_description = self._get_extract_function()

        with patch(
            "taew.adapters.python.inspect.for_browsing_code_tree.object_description.inspect.getdoc",
            side_effect=Exception("getdoc failed"),
        ):
            # Should not raise, should return empty string
            result = extract_short_description(mock_obj)
            self.assertEqual(result, "")

    def test_docstring_parse_failure(self) -> None:
        """Test graceful handling when docstring parsing fails."""

        def test_function() -> None:
            """This is a test function."""
            pass

        extract_short_description = self._get_extract_function()

        with patch(
            "taew.adapters.python.inspect.for_browsing_code_tree.object_description.parse",
            side_effect=Exception("parse failed"),
        ):
            # Should not raise, should return empty string
            result = extract_short_description(test_function)
            self.assertEqual(result, "")

    def test_parsed_docstring_without_short_description(self) -> None:
        """Test handling when parsed docstring has no short_description."""

        def test_function() -> None:
            """This is a test function."""
            pass

        extract_short_description = self._get_extract_function()

        # Mock parse to return docstring without short_description
        mock_parsed = Mock()
        mock_parsed.short_description = None

        with patch(
            "taew.adapters.python.inspect.for_browsing_code_tree.object_description.parse",
            return_value=mock_parsed,
        ):
            result = extract_short_description(test_function)
            self.assertEqual(result, "")

    def test_parsed_docstring_with_empty_short_description(self) -> None:
        """Test handling when parsed docstring has empty short_description."""

        def test_function() -> None:
            """This is a test function."""
            pass

        extract_short_description = self._get_extract_function()

        # Mock parse to return docstring with empty short_description
        mock_parsed = Mock()
        mock_parsed.short_description = ""

        with patch(
            "taew.adapters.python.inspect.for_browsing_code_tree.object_description.parse",
            return_value=mock_parsed,
        ):
            result = extract_short_description(test_function)
            self.assertEqual(result, "")

    def test_various_object_types(self) -> None:
        """Test extraction from various object types."""
        extract_short_description = self._get_extract_function()

        # Test with different object types that can have docstrings
        objects_to_test = [
            # Function
            lambda: None,  # No docstring
            # Built-in function (may or may not have docstring)
            len,
            # Built-in class
            str,
        ]

        for obj in objects_to_test:
            # Should not raise exception for any object type
            result = extract_short_description(obj)
            self.assertIsInstance(result, str)

    def test_docstring_with_special_formatting(self) -> None:
        """Test extraction from docstring with special formatting."""

        def test_function() -> None:
            """Summary line with trailing whitespace.

            Args:
                param: Description

            Returns:
                Something
            """
            pass

        extract_short_description = self._get_extract_function()
        result = extract_short_description(test_function)

        # Should extract just the summary line, potentially cleaned up
        self.assertTrue(result.startswith("Summary line"))
        self.assertNotIn("Args:", result)
        self.assertNotIn("Returns:", result)


if __name__ == "__main__":
    unittest.main()
