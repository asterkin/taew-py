import unittest
import inspect
from typing import Optional, Union, List, Callable, Any
from taew.adapters.python.inspect.for_browsing_code_tree.annotated_entity import (
    Argument,
)


class TestTypeValidation(unittest.TestCase):
    """Test type validation functionality in Inspect adapter."""

    def _make_argument_from_func(
        self, func: Callable[..., Any], param_name: str
    ) -> Argument:
        """Helper to create Argument from function parameter."""
        sig = inspect.signature(func)
        param = sig.parameters[param_name]
        return Argument(param)

    def test_basic_type_validation(self) -> None:
        """Test type validation for basic Python types."""

        def test_func(x: int, y: str, z: float, w: bool) -> None:
            pass

        int_arg = self._make_argument_from_func(test_func, "x")
        str_arg = self._make_argument_from_func(test_func, "y")
        float_arg = self._make_argument_from_func(test_func, "z")
        bool_arg = self._make_argument_from_func(test_func, "w")

        # Test valid types
        self.assertTrue(int_arg.has_valid_type(42))
        self.assertTrue(str_arg.has_valid_type("hello"))
        self.assertTrue(float_arg.has_valid_type(3.14))
        self.assertTrue(bool_arg.has_valid_type(True))

        # Test invalid types
        self.assertFalse(int_arg.has_valid_type("not_int"))
        self.assertFalse(str_arg.has_valid_type(123))
        self.assertFalse(float_arg.has_valid_type("not_float"))
        self.assertFalse(bool_arg.has_valid_type("not_bool"))

    def test_optional_type_validation(self) -> None:
        """Test type validation for Optional types."""

        def test_func(x: Optional[int], y: Optional[str]) -> None:
            pass

        opt_int_arg = self._make_argument_from_func(test_func, "x")
        opt_str_arg = self._make_argument_from_func(test_func, "y")

        # Test valid values (including None)
        self.assertTrue(opt_int_arg.has_valid_type(42))
        self.assertTrue(opt_int_arg.has_valid_type(None))
        self.assertTrue(opt_str_arg.has_valid_type("hello"))
        self.assertTrue(opt_str_arg.has_valid_type(None))

        # Test invalid types
        self.assertFalse(opt_int_arg.has_valid_type("not_int"))
        self.assertFalse(opt_str_arg.has_valid_type(123))

    def test_union_type_validation(self) -> None:
        """Test type validation for Union types."""

        def test_func(x: Union[int, str], y: Union[float, bool]) -> None:
            pass

        union_int_str_arg = self._make_argument_from_func(test_func, "x")
        union_float_bool_arg = self._make_argument_from_func(test_func, "y")

        # Test valid types (either type in union)
        self.assertTrue(union_int_str_arg.has_valid_type(42))
        self.assertTrue(union_int_str_arg.has_valid_type("hello"))
        self.assertTrue(union_float_bool_arg.has_valid_type(3.14))
        self.assertTrue(union_float_bool_arg.has_valid_type(True))

        # Test invalid types
        self.assertFalse(union_int_str_arg.has_valid_type(3.14))
        self.assertFalse(union_float_bool_arg.has_valid_type("invalid"))

    def test_no_annotation_permissive(self) -> None:
        """Test behavior when no type annotation is provided."""

        def test_func(x: object) -> None:
            pass

        no_annotation_arg = self._make_argument_from_func(test_func, "x")

        # Should accept any value when no annotation
        self.assertTrue(no_annotation_arg.has_valid_type("any_string"))
        self.assertTrue(no_annotation_arg.has_valid_type(123))
        self.assertTrue(no_annotation_arg.has_valid_type([1, 2, 3]))
        self.assertTrue(no_annotation_arg.has_valid_type({"key": "value"}))

    def test_complex_type_permissive(self) -> None:
        """Test behavior with complex types."""

        def test_func(x: List[int]) -> None:
            pass

        complex_arg = self._make_argument_from_func(test_func, "x")

        # Should be permissive for complex generic types
        self.assertTrue(complex_arg.has_valid_type([1, 2, 3]))
        self.assertTrue(complex_arg.has_valid_type("fallback_permissive"))

    def test_var_positional_validation(self) -> None:
        """Test type validation for *args (VAR_POSITIONAL) parameters."""

        def test_func(*args: int) -> None:
            pass

        args_param = self._make_argument_from_func(test_func, "args")

        # Test valid cases - tuple with correct element types
        self.assertTrue(args_param.has_valid_type((1, 2, 3)))
        self.assertTrue(args_param.has_valid_type(()))  # Empty tuple
        self.assertTrue(args_param.has_valid_type((42,)))  # Single element

        # Test invalid cases - wrong container type
        self.assertFalse(args_param.has_valid_type([1, 2, 3]))  # List instead of tuple
        self.assertFalse(args_param.has_valid_type({1, 2, 3}))  # Set instead of tuple
        self.assertFalse(
            args_param.has_valid_type(123)
        )  # Single value instead of tuple

        # Test invalid cases - wrong element types
        self.assertFalse(
            args_param.has_valid_type(("a", "b"))
        )  # Strings instead of ints
        self.assertFalse(args_param.has_valid_type((1, "mixed", 3)))  # Mixed types

    def test_var_keyword_validation(self) -> None:
        """Test type validation for **kwargs (VAR_KEYWORD) parameters."""

        def test_func(**kwargs: str) -> None:
            pass

        kwargs_param = self._make_argument_from_func(test_func, "kwargs")

        # Test valid cases - dict with correct value types
        self.assertTrue(kwargs_param.has_valid_type({"a": "hello", "b": "world"}))
        self.assertTrue(kwargs_param.has_valid_type({}))  # Empty dict
        self.assertTrue(kwargs_param.has_valid_type({"single": "value"}))

        # Test invalid cases - wrong container type
        self.assertFalse(
            kwargs_param.has_valid_type(("a", "b"))
        )  # Tuple instead of dict
        self.assertFalse(
            kwargs_param.has_valid_type(["a", "b"])
        )  # List instead of dict
        self.assertFalse(
            kwargs_param.has_valid_type("not_dict")
        )  # String instead of dict

        # Test invalid cases - wrong value types
        self.assertFalse(
            kwargs_param.has_valid_type({"a": 123, "b": 456})
        )  # Ints instead of strings
        self.assertFalse(
            kwargs_param.has_valid_type({"a": "hello", "b": 123})
        )  # Mixed types

    def test_var_positional_no_annotation(self) -> None:
        """Test *args without type annotation (should be permissive)."""

        # Create an argument with VAR_POSITIONAL kind and no annotation
        from unittest.mock import Mock

        mock_param = Mock()
        mock_param.annotation = inspect.Parameter.empty
        mock_param.kind = inspect.Parameter.VAR_POSITIONAL

        args_param = Argument(mock_param)

        # Should accept any tuple
        self.assertTrue(args_param.has_valid_type((1, "mixed", [1, 2, 3])))
        self.assertTrue(args_param.has_valid_type(()))

        # Still must be a tuple
        self.assertFalse(args_param.has_valid_type([1, 2, 3]))
        self.assertFalse(args_param.has_valid_type("not_tuple"))

    def test_var_keyword_no_annotation(self) -> None:
        """Test **kwargs without type annotation (should be permissive)."""

        # Create an argument with VAR_KEYWORD kind and no annotation
        from unittest.mock import Mock

        mock_param = Mock()
        mock_param.annotation = inspect.Parameter.empty
        mock_param.kind = inspect.Parameter.VAR_KEYWORD

        kwargs_param = Argument(mock_param)

        # Should accept any dict
        self.assertTrue(
            kwargs_param.has_valid_type({"a": 1, "b": "mixed", "c": [1, 2]})
        )
        self.assertTrue(kwargs_param.has_valid_type({}))

        # Still must be a dict
        self.assertFalse(kwargs_param.has_valid_type((1, 2, 3)))
        self.assertFalse(kwargs_param.has_valid_type("not_dict"))

    def test_var_positional_complex_annotation(self) -> None:
        """Test *args with complex type annotations (should be permissive)."""

        def test_func(*args: List[int]) -> None:
            pass

        args_param = self._make_argument_from_func(test_func, "args")

        # Should be permissive for complex annotations
        self.assertTrue(args_param.has_valid_type(([1, 2], [3, 4])))
        self.assertTrue(args_param.has_valid_type(("fallback",)))

        # Still must be a tuple
        self.assertFalse(args_param.has_valid_type([[1, 2], [3, 4]]))

    def test_var_keyword_complex_annotation(self) -> None:
        """Test **kwargs with complex type annotations (should be permissive)."""

        def test_func(**kwargs: Optional[int]) -> None:
            pass

        kwargs_param = self._make_argument_from_func(test_func, "kwargs")

        # Should be permissive for complex annotations
        self.assertTrue(kwargs_param.has_valid_type({"a": 1, "b": None}))
        self.assertTrue(kwargs_param.has_valid_type({"fallback": "permissive"}))

        # Still must be a dict
        self.assertFalse(kwargs_param.has_valid_type((1, None)))


if __name__ == "__main__":
    unittest.main()
