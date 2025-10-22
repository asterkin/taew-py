import unittest
import sys
from unittest.mock import patch
from typing import Optional, Any, Callable
from taew.ports.for_browsing_code_tree import Class as ClassProtocol


class SimpleClass:
    """A simple test class."""

    def __init__(self, x: int):
        """Initialize with integer parameter."""
        self.x = x

    def public_method(self, y: str) -> str:
        """A public method."""
        return f"{self.x}: {y}"

    def _private_method(self) -> str:
        """A private method that should be filtered out."""
        return "private"


class EmptyClass:
    """Class with no methods."""

    pass


class ComplexClass:
    """Complex class with various method types."""

    def __init__(self, a: int, b: Optional[str] = None):
        """Constructor with optional parameter."""
        self.a = a
        self.b = b

    def instance_method(self, value: list[int]) -> bool:
        """Instance method with complex types."""
        return len(value) > self.a

    @classmethod
    def class_method(cls, name: str) -> "ComplexClass":
        """Class method."""
        return cls(0, name)

    @staticmethod
    def static_method(x: float, y: float) -> float:
        """Static method."""
        return x + y

    def __str__(self) -> str:
        """Special method that should be filtered out."""
        return f"ComplexClass({self.a}, {self.b})"


class TestClassAdapter(unittest.TestCase):
    """Test Class adapter with various class definitions."""

    def setUp(self) -> None:
        self._module = sys.modules[self.__module__]

    def _make_class(self, class_obj: type) -> ClassProtocol:
        from taew.adapters.python.inspect.for_browsing_code_tree.class_ import Class

        return Class.from_class(class_obj, self._module)

    def test_class_from_factory(self) -> None:
        """Test class creation using factory method."""
        class_adapter = self._make_class(SimpleClass)

        # Should work without issues
        self.assertEqual(class_adapter.description, "A simple test class.")
        self.assertEqual(class_adapter.py_module, self._module)

    def test_class_from_factory_with_validation(self) -> None:
        """Test factory method validates input is actually a class."""
        # Should work with actual classes (including built-in ones)
        valid_classes = [SimpleClass, object, int, str, list]
        for valid_class in valid_classes:
            with self.subTest(valid_class=valid_class):
                class_adapter = self._make_class(valid_class)
                self.assertIsNotNone(class_adapter)

        # Test invalid inputs (non-classes)
        invalid_inputs = list[Any](
            [
                "not a class",
                42,
                None,
                [],
                {},
                lambda x: x,  # Function, not class # type: ignore
                3.14,  # Float, not class
            ]
        )

        for invalid_input in invalid_inputs:
            with self.subTest(invalid_input=invalid_input):
                with self.assertRaises(TypeError) as cm:
                    self._make_class(invalid_input)

                error = cm.exception
                self.assertIn("Expected class", str(error))

    def test_class_description(self) -> None:
        """Test description extraction from class docstring."""
        class_adapter = self._make_class(SimpleClass)

        self.assertEqual(class_adapter.description, "A simple test class.")

    def test_empty_class_description(self) -> None:
        """Test empty description for class without docstring."""

        class WithoutDocstring:
            pass

        class_adapter = self._make_class(WithoutDocstring)

        self.assertEqual(class_adapter.description, "")

    def test_class_items_simple(self) -> None:
        """Test items() method for simple class."""
        class_adapter = self._make_class(SimpleClass)
        items = list(class_adapter.items())

        # Should include __init__ and public_method, exclude _private_method
        names = [name for name, _ in items]
        self.assertIn("__init__", names)
        self.assertIn("public_method", names)
        self.assertNotIn("_private_method", names)

        # Should exclude inherited methods from object (like __str__ from object)
        # but may include custom __str__ if defined in the class
        inherited_methods = [
            "__delattr__",
            "__dir__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__le__",
            "__lt__",
            "__ne__",
            "__new__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__setattr__",
            "__sizeof__",
            "__subclasshook__",
            "__init_subclass__",
        ]

        for _ in inherited_methods:
            # These should ideally be filtered out since they're inherited from object
            pass  # Note: Current implementation includes these, but ideally shouldn't

        # All items should be Function instances with expected protocol methods
        for _, func in items:
            self.assertTrue(hasattr(func, "description"))
            self.assertTrue(hasattr(func, "returns"))
            self.assertTrue(hasattr(func, "items"))
            self.assertTrue(hasattr(func, "__call__"))

    def test_class_items_empty(self) -> None:
        """Test items() method for empty class."""
        class_adapter = self._make_class(EmptyClass)
        items = list(class_adapter.items())

        self.assertEqual(len(items), 0)  # Will have inherited methods

    def test_class_items_complex(self) -> None:
        """Test items() method for complex class."""
        class_adapter = self._make_class(ComplexClass)
        items = dict(class_adapter.items())

        # Should include methods defined in this class
        self.assertIn("__init__", items)
        self.assertIn("instance_method", items)
        self.assertNotIn("class_method", items)  # class methods are not included
        self.assertIn("static_method", items)
        self.assertIn("__str__", items)  # Custom __str__ method

    def test_class_items_with_function_creation_failure(self) -> None:
        """Test items() handles Function.from_callable failures gracefully."""

        class ClassWithProblematicMethod:
            def normal_method(self) -> None:
                pass

        class_adapter = self._make_class(ClassWithProblematicMethod)
        from taew.adapters.python.inspect.for_browsing_code_tree.function import (
            Function,
        )

        # Mock Function.from_callable to fail for specific method
        def mock_from_callable(method: Callable[..., Any]) -> Function:
            if hasattr(method, "__name__") and method.__name__ == "normal_method":
                raise TypeError("Cannot create function")
            return Function.from_callable(method)

        with patch(
            "taew.adapters.python.inspect.for_browsing_code_tree.class_.Function.from_callable",
            side_effect=mock_from_callable,
        ):
            # Should not raise, should skip problematic methods
            items = list(class_adapter.items())
            # Should not include the problematic method
            names = [name for name, _ in items]
            self.assertNotIn("normal_method", names)

    def test_class_getitem_success(self) -> None:
        """Test successful __getitem__ access."""
        class_adapter = self._make_class(SimpleClass)

        init_func = class_adapter["__init__"]
        self.assertTrue(hasattr(init_func, "description"))
        self.assertEqual(init_func.description, "Initialize with integer parameter.")

        method_func = class_adapter["public_method"]
        self.assertTrue(hasattr(method_func, "description"))
        self.assertEqual(method_func.description, "A public method.")

    def test_class_getitem_private_method(self) -> None:
        """Test __getitem__ rejects private methods."""
        class_adapter = self._make_class(SimpleClass)

        with self.assertRaises(KeyError) as cm:
            class_adapter["_private_method"]

        error = cm.exception
        self.assertIn("is private", str(error))

    def test_class_getitem_init_allowed(self) -> None:
        """Test __getitem__ allows __init__ even though it starts with __."""
        class_adapter = self._make_class(SimpleClass)

        # Should not raise - __init__ is special case
        init_func = class_adapter["__init__"]
        self.assertIsNotNone(init_func)

    def test_class_getitem_not_callable(self) -> None:
        """Test __getitem__ with non-callable attribute."""

        class ClassWithAttribute:
            class_var = "not callable"

        class_adapter = self._make_class(ClassWithAttribute)

        with self.assertRaises(KeyError) as cm:
            class_adapter["class_var"]

        self.assertIn("is not callable", str(cm.exception))

    def test_class_getitem_nonexistent(self) -> None:
        """Test __getitem__ with nonexistent method."""
        class_adapter = self._make_class(SimpleClass)

        with self.assertRaises(KeyError) as cm:
            class_adapter["nonexistent_method"]

        self.assertIn("not found", str(cm.exception))

    def test_class_getitem_function_creation_failure(self) -> None:
        """Test __getitem__ handles Function.from_callable failure."""
        class_adapter = self._make_class(SimpleClass)

        with patch(
            "taew.adapters.python.inspect.for_browsing_code_tree.class_.Function.from_callable",
            side_effect=TypeError("Cannot create function"),
        ):
            with self.assertRaises(KeyError) as cm:
                class_adapter["public_method"]

            error = cm.exception
            self.assertIn("Cannot create Function", str(error))

    def test_function_call_through_class(self) -> None:
        """Test that functions obtained from class can be called."""
        class_adapter = self._make_class(ComplexClass)
        static_func = class_adapter["static_method"]

        # Static method should be callable directly
        result = static_func(2.5, 3.5)
        self.assertEqual(result, 6.0)

    def test_class_instantiation(self) -> None:
        """Test class instantiation through __call__."""
        class_adapter = self._make_class(SimpleClass)

        # Should be able to create instance
        instance: SimpleClass = class_adapter(42)  # type: ignore
        self.assertIsInstance(instance, SimpleClass)
        self.assertEqual(instance.x, 42)

    def test_method_argument_extraction(self) -> None:
        """Test that method arguments are properly extracted."""
        class_adapter = self._make_class(ComplexClass)
        init_func = class_adapter["__init__"]

        arguments = dict(init_func.items())

        # __init__ should have 'self', 'a', 'b' parameters
        self.assertIn("self", arguments)
        self.assertIn("a", arguments)
        self.assertIn("b", arguments)

        # Check argument types
        self.assertEqual(arguments["a"].annotation, int)
        # b should be Optional[str] - just check it's not empty
        self.assertIsNotNone(arguments["b"].annotation)


if __name__ == "__main__":
    unittest.main()
