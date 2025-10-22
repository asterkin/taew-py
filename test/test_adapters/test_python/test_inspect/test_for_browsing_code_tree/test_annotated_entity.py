import inspect
import unittest
from unittest.mock import Mock
from typing import Any, Optional
from collections.abc import Iterable
from taew.domain.argument import POSITIONAL_ONLY
from inspect import _ParameterKind  # type: ignore[import-untyped]
from taew.ports.for_browsing_code_tree import AnnotatedEntity as AnnotatedEntityProtocol
from taew.adapters.python.inspect.for_browsing_code_tree.annotated_entity import (
    Argument,
    ReturnValue,
)


class TestAnnotatedEntity(unittest.TestCase):
    """Test AnnotatedEntity base functionality."""

    @staticmethod
    def _make_entity(
        annotation: Any, docstring: Optional[Any] = None
    ) -> AnnotatedEntityProtocol:
        from taew.adapters.python.inspect.for_browsing_code_tree.annotated_entity import (
            AnnotatedEntity,
        )

        return AnnotatedEntity(annotation, docstring)

    def test_simple_annotation(self) -> None:
        entity = self._make_entity(int)

        self.assertEqual(entity.annotation, int)
        self.assertEqual(entity.spec, (None, ()))
        self.assertEqual(entity.description, "")

    def test_generic_list_annotation(self) -> None:
        entity = self._make_entity(list[str])

        self.assertEqual(entity.annotation, list[str])
        self.assertEqual(entity.spec, (list, (str,)))

    def test_generic_iterable_annotation(self) -> None:
        entity = self._make_entity(Iterable[str])

        self.assertEqual(entity.annotation, Iterable[str])
        self.assertEqual(entity.spec, (Iterable, (str,)))

    def test_with_docstring_description(self) -> None:
        mock_docstring = Mock()
        mock_docstring.description = "Test description"

        entity = self._make_entity(int, mock_docstring)

        self.assertEqual(entity.description, "Test description")

    def test_empty_annotation(self) -> None:
        """Test handling of inspect.Parameter.empty annotation."""
        entity = self._make_entity(inspect.Parameter.empty)

        self.assertEqual(entity.annotation, inspect.Parameter.empty)
        self.assertEqual(entity.spec, (None, ()))
        self.assertEqual(entity.description, "")

    def test_none_annotation(self) -> None:
        """Test handling of None annotation (different from empty)."""
        entity = self._make_entity(None)

        self.assertEqual(entity.annotation, None)
        self.assertEqual(entity.spec, (None, ()))
        self.assertEqual(entity.description, "")

    def test_empty_annotation_with_docstring(self) -> None:
        """Test empty annotation with docstring description."""
        mock_docstring = Mock()
        mock_docstring.description = "Parameter without type annotation"

        entity = self._make_entity(inspect.Parameter.empty, mock_docstring)

        self.assertEqual(entity.annotation, inspect.Parameter.empty)
        self.assertEqual(entity.spec, (None, ()))
        self.assertEqual(entity.description, "Parameter without type annotation")

    def test_basic_protocol_methods_exist(self) -> None:
        entity = self._make_entity(str)

        # Test protocol methods exist and work
        self.assertIsInstance(entity.annotation, type)
        self.assertIsInstance(entity.spec, tuple)
        self.assertIsInstance(entity.description, str)

    def test_argument_kind_extraction(self) -> None:
        param = inspect.Parameter("x", _ParameterKind.POSITIONAL_ONLY, annotation=int)
        arg = Argument(param)
        self.assertEqual(arg.kind, POSITIONAL_ONLY)

    def test_return_value_inherits_annotated_entity(self) -> None:
        ret = ReturnValue(int)
        self.assertEqual(ret.annotation, int)
        self.assertEqual(ret.description, "")


if __name__ == "__main__":
    unittest.main()
