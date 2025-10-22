import unittest
from unittest.mock import Mock, patch
from typing import Optional, List, Literal, Callable, Any
from taew.ports.for_browsing_code_tree import (
    AnnotatedEntity,
    Argument,
    Function as FunctionProtocol,
)
from taew.domain.argument import (
    POSITIONAL_OR_KEYWORD,
    VAR_POSITIONAL,
    KEYWORD_ONLY,
    VAR_KEYWORD,
)
from taew.domain.function import (
    FunctionInvocationError,
)


class TestFunctionAdapter(unittest.TestCase):
    """Test Function adapter with various function signatures."""

    def setUp(self) -> None:
        """Set up test functions with different signatures."""

        def simple_function(x: int, y: str) -> bool:
            """A simple test function.

            Args:
                x: Integer parameter
                y: String parameter

            Returns:
                Boolean result
            """
            return len(y) > x

        def complex_function(
            a: int,
            b: str = "default",
            *args: float,
            c: Optional[List[str]] = None,
            **kwargs: bool,
        ) -> Literal["success", "failure"]:
            """Complex function with all parameter types."""
            return "success" if a > 0 else "failure"

        self.simple_function = simple_function
        self.complex_function = complex_function

    @staticmethod
    def _make_function(func: Callable[..., Any]) -> FunctionProtocol:
        from taew.adapters.python.inspect.for_browsing_code_tree.function import (
            Function,
        )

        return Function.from_callable(func)

    def _assertIsAnnotated(self, ent: AnnotatedEntity) -> None:
        self.assertTrue(hasattr(ent, "annotation"))
        self.assertTrue(hasattr(ent, "description"))
        self.assertTrue(hasattr(ent, "spec"))

    def _assertIsArgument(self, arg: Argument) -> None:
        self._assertIsAnnotated(arg)
        self.assertTrue(hasattr(arg, "kind"))

    def test_function_protocol_compliance(self) -> None:
        """Verify Function adapter implements FunctionPort protocol."""
        func_adapter = self._make_function(self.simple_function)

        # Test all protocol methods exist
        self.assertIsInstance(func_adapter.description, str)
        self._assertIsAnnotated(func_adapter.returns)

        # Test items() returns proper iterator
        items = list(func_adapter.items())
        self.assertIsInstance(items, list)
        for name, arg in items:
            self.assertIsInstance(name, str)
            self._assertIsArgument(arg)

    def test_simple_function_description(self) -> None:
        """Test description extraction from docstring."""
        func_adapter = self._make_function(self.simple_function)

        self.assertEqual(func_adapter.description, "A simple test function.")

    def test_return_value_extraction(self) -> None:
        """Test return type and description extraction."""
        func_adapter = self._make_function(self.simple_function)
        returns = func_adapter.returns

        self.assertEqual(returns.annotation, bool)
        self.assertEqual(returns.description, "Boolean result")

    def test_arguments_in_order(self) -> None:
        """Test that arguments are returned in signature order."""
        func_adapter = self._make_function(self.complex_function)
        items = list(func_adapter.items())

        expected_names = ["a", "b", "args", "c", "kwargs"]
        actual_names = [name for name, _ in items]

        self.assertEqual(actual_names, expected_names)

    def test_argument_kinds(self) -> None:
        """Test that argument kinds are correctly identified."""
        func_adapter = self._make_function(self.complex_function)
        items = dict(func_adapter.items())

        self.assertEqual(items["a"].kind, POSITIONAL_OR_KEYWORD)
        self.assertEqual(items["b"].kind, POSITIONAL_OR_KEYWORD)
        self.assertEqual(items["args"].kind, VAR_POSITIONAL)
        self.assertEqual(items["c"].kind, KEYWORD_ONLY)
        self.assertEqual(items["kwargs"].kind, VAR_KEYWORD)

    def test_argument_defaults(self) -> None:
        """Test default value extraction."""
        func_adapter = self._make_function(self.complex_function)
        items = dict(func_adapter.items())

        self.assertTrue(items["a"].default.is_empty())
        self.assertFalse(items["b"].default.is_empty())
        self.assertEqual(items["b"].default.value, "default")
        self.assertFalse(items["c"].default.is_empty())
        self.assertEqual(items["c"].default.value, None)

    def test_argument_annotations(self) -> None:
        """Test type annotation extraction."""
        func_adapter = self._make_function(self.complex_function)
        items = dict(func_adapter.items())

        self.assertEqual(items["a"].annotation, int)
        self.assertEqual(items["b"].annotation, str)
        self.assertEqual(items["args"].annotation, float)
        self.assertEqual(items["c"].annotation, Optional[List[str]])
        self.assertEqual(items["kwargs"].annotation, bool)

    def test_successful_function_call(self) -> None:
        """Test successful function invocation."""
        func_adapter = self._make_function(self.simple_function)

        result = func_adapter(5, "hello")
        self.assertFalse(result)  # len("hello") > 5 is False

        result = func_adapter(3, "hello")
        self.assertTrue(result)  # len("hello") > 3 is True

    def test_function_call_with_wrong_signature(self) -> None:
        """Test function call with incorrect arguments."""
        func_adapter = self._make_function(self.simple_function)

        # Missing required argument
        with self.assertRaises(FunctionInvocationError) as cm:
            func_adapter(5)  # Missing 'y' argument

        error = cm.exception
        self.assertEqual(error.function_name, self.simple_function.__qualname__)
        self.assertEqual(error.error_type, "signature_error")
        self.assertIn("missing", error.args[0].lower())

    def test_function_call_with_extra_arguments(self) -> None:
        """Test function call with too many arguments."""
        func_adapter = self._make_function(self.simple_function)

        with self.assertRaises(FunctionInvocationError) as cm:
            func_adapter(5, "hello", "extra")

        error = cm.exception
        self.assertEqual(error.error_type, "signature_error")

    def test_function_call_with_keyword_arguments(self) -> None:
        """Test function call with keyword arguments."""
        func_adapter = self._make_function(self.simple_function)

        result = func_adapter(x=2, y="test")
        self.assertTrue(result)  # len("test") > 2

    def test_function_call_with_defaults(self) -> None:
        """Test function call using default values."""
        func_adapter = self._make_function(self.complex_function)

        # Call with minimal required arguments
        result = func_adapter(1)  # Uses default for 'b' and 'c'
        self.assertEqual(result, "success")

    def test_from_callable_with_non_callable(self) -> None:
        """Test from_callable with non-callable object."""
        with self.assertRaises(TypeError) as cm:
            self._make_function("not a function")  # type: ignore

        error = cm.exception
        self.assertIn("Expected callable", str(error))
        self.assertIn("str", str(error))

    def test_from_callable_with_unsignable_builtin(self) -> None:
        """Test from_callable with builtin that might not have signature."""
        mock_func = Mock()

        with patch("inspect.signature", side_effect=ValueError("no signature")):
            with self.assertRaises(ValueError) as cm:
                self._make_function(mock_func)

            error = cm.exception
            self.assertIn("Cannot create signature", str(error))

    def test_from_callable_with_malformed_docstring(self) -> None:
        """Test from_callable gracefully handles docstring parsing errors."""

        def func_with_docstring() -> None:
            """This is a function."""
            pass

        # Force docstring_parser.parse to fail
        with patch(
            "taew.adapters.python.inspect.for_browsing_code_tree.function.parse",
            side_effect=Exception("Docstring parsing failed"),
        ):
            func_adapter = self._make_function(func_with_docstring)

            # Should have empty description due to fallback
            self.assertEqual(func_adapter.description, "")

    def test_from_callable_with_broken_param_docs(self) -> None:
        """Test from_callable handles broken parameter documentation."""

        def func_with_params(x: int, y: str) -> None:
            """Function with parameters.

            Args:
                x: Integer parameter
                y: String parameter
            """
            pass

        # Create a mock docstring that will cause param_docs creation to fail
        mock_docstring = Mock()
        mock_docstring.short_description = "Test function"
        mock_docstring.returns = None
        mock_docstring.params = Mock()
        # Make params iteration fail
        mock_docstring.params.__iter__ = Mock(
            side_effect=AttributeError("Broken params")
        )

        with patch(
            "taew.adapters.python.inspect.for_browsing_code_tree.function.parse",
            return_value=mock_docstring,
        ):
            # Should not raise, should fallback to empty param_docs
            func_adapter = self._make_function(func_with_params)

            # Should still work but with empty param docs
            self.assertEqual(func_adapter.description, "Test function")
            # Arguments should still be accessible (just without docstring info)
            arguments = list(func_adapter.items())
            self.assertEqual(len(arguments), 2)

    def test_function_without_docstring(self) -> None:
        """Test function with no docstring."""

        def no_doc_function(x: int) -> str:
            return str(x)

        func_adapter = self._make_function(no_doc_function)

        self.assertEqual(func_adapter.description, "")
        # Should still work normally
        result = func_adapter(42)
        self.assertEqual(result, "42")

    def test_function_with_empty_docstring(self) -> None:
        """Test function with empty docstring."""

        def empty_doc_function(x: int) -> str:
            """"""
            return str(x)

        func_adapter = self._make_function(empty_doc_function)

        self.assertEqual(func_adapter.description, "")
        # Should still work normally
        result = func_adapter(42)
        self.assertEqual(result, "42")


if __name__ == "__main__":
    unittest.main()
