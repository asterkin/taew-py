import unittest
from taew.domain.argument import POSITIONAL_OR_KEYWORD
from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import Argument


class TestTypeValidation(unittest.TestCase):
    """Test type validation functionality in RAM adapter."""

    def _make_argument(
        self, annotation: type, default_value: object = None, has_default: bool = False
    ) -> Argument:
        """Helper to create test arguments."""
        return Argument(
            annotation=annotation,
            spec=(annotation, ()),
            description="test argument",
            _default_value=default_value,
            _has_default=has_default,
            kind=POSITIONAL_OR_KEYWORD,
        )

    def test_basic_type_validation(self) -> None:
        """Test type validation for basic Python types."""
        test_cases = [
            (int, 42, True),
            (int, "not_int", False),
            (str, "hello", True),
            (str, 123, False),
            (float, 3.14, True),
            (float, "not_float", False),
            (bool, True, True),
            (bool, "not_bool", False),
            (type(None), None, True),
            (type(None), "not_none", False),
        ]

        for annotation, test_value, expected_valid in test_cases:
            with self.subTest(annotation=annotation, value=test_value):
                arg = self._make_argument(annotation)
                self.assertEqual(arg.has_valid_type(test_value), expected_valid)

    def test_complex_type_permissive_behavior(self) -> None:
        """Test that complex types are handled permissively."""
        complex_annotations = [list, dict, tuple, set, object, type]

        for annotation in complex_annotations:
            with self.subTest(annotation=annotation):
                arg = self._make_argument(annotation)
                # RAM adapter should be permissive for complex types
                self.assertTrue(arg.has_valid_type("any_value"))
                self.assertTrue(arg.has_valid_type(42))
                self.assertTrue(arg.has_valid_type([1, 2, 3]))

    def test_no_annotation_permissive(self) -> None:
        """Test behavior when no type annotation is provided."""
        # Using object as a proxy for "no specific type"
        arg = self._make_argument(object)

        # Should accept any value for complex types
        self.assertTrue(arg.has_valid_type("any_string"))
        self.assertTrue(arg.has_valid_type(123))
        self.assertTrue(arg.has_valid_type([1, 2, 3]))
        self.assertTrue(arg.has_valid_type({"key": "value"}))


if __name__ == "__main__":
    unittest.main()
