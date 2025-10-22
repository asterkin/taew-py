import unittest
import inspect
from taew.ports.for_browsing_code_tree import Argument as ArgumentProtocol
from taew.domain.argument import (
    POSITIONAL_OR_KEYWORD,
    VAR_POSITIONAL,
    KEYWORD_ONLY,
    VAR_KEYWORD,
)


class TestArgument(unittest.TestCase):
    """Test Argument adapter functionality."""

    def setUp(self) -> None:
        def test_func(
            required: int,
            optional: str = "default",
            *args: float,
            keyword_only: bool,
            **kwargs: str,
        ) -> None:
            pass

        self.signature = inspect.signature(test_func)
        self.params = self.signature.parameters

    @staticmethod
    def _make_argument(param: inspect.Parameter) -> ArgumentProtocol:
        from taew.adapters.python.inspect.for_browsing_code_tree.annotated_entity import (
            Argument,
        )

        return Argument(param)

    def test_argument_protocol_compliance(self) -> None:
        """Verify Argument implements ArgumentPort protocol."""
        param = self.params["required"]
        arg = self._make_argument(param)

        # Test protocol methods
        self.assertIsInstance(arg.annotation, type)
        self.assertIsInstance(arg.spec, tuple)
        self.assertIsInstance(arg.description, str)
        self.assertTrue(hasattr(arg.default, "is_empty"))
        self.assertTrue(hasattr(arg.default, "value"))
        self.assertIsInstance(arg.kind, int)

    def test_required_argument(self) -> None:
        """Test required argument properties."""
        param = self.params["required"]
        arg = self._make_argument(param)

        self.assertEqual(arg.annotation, int)
        self.assertTrue(arg.default.is_empty())
        self.assertEqual(arg.kind, POSITIONAL_OR_KEYWORD)

    def test_optional_argument(self) -> None:
        """Test optional argument with default."""
        param = self.params["optional"]
        arg = self._make_argument(param)

        self.assertEqual(arg.annotation, str)
        self.assertFalse(arg.default.is_empty())
        self.assertEqual(arg.default.value, "default")
        self.assertEqual(arg.kind, POSITIONAL_OR_KEYWORD)

    def test_varargs_argument(self) -> None:
        """Test *args parameter."""
        param = self.params["args"]
        arg = self._make_argument(param)

        self.assertEqual(arg.annotation, float)
        self.assertEqual(arg.kind, VAR_POSITIONAL)

    def test_keyword_only_argument(self) -> None:
        """Test keyword-only parameter."""
        param = self.params["keyword_only"]
        arg = self._make_argument(param)

        self.assertEqual(arg.annotation, bool)
        self.assertEqual(arg.kind, KEYWORD_ONLY)

    def test_varkwargs_argument(self) -> None:
        """Test **kwargs parameter."""
        param = self.params["kwargs"]
        arg = self._make_argument(param)

        self.assertEqual(arg.annotation, str)
        self.assertEqual(arg.kind, VAR_KEYWORD)


if __name__ == "__main__":
    unittest.main()
