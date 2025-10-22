import unittest
from typing import Protocol, Any
from abc import ABC, abstractmethod
from collections.abc import Mapping

from taew.domain.argument import ArgumentKind, POSITIONAL_OR_KEYWORD
from taew.ports.for_browsing_code_tree import (
    is_protocol,
    is_abc,
    is_interface,
    is_interface_mapping,
)


class MockDefaultValue:
    def is_empty(self) -> bool:
        return False

    @property
    def value(self) -> Any:
        return None


class MockArgument:
    def __init__(self, annotation: Any) -> None:
        self.annotation = annotation

    @property
    def spec(self) -> tuple[Any, tuple[Any, ...]]:
        return self.annotation, ()

    @property
    def description(self) -> str:
        return "Mock argument for testing"

    @property
    def default(self) -> MockDefaultValue:
        return MockDefaultValue()

    @property
    def kind(self) -> ArgumentKind:
        return POSITIONAL_OR_KEYWORD

    def has_valid_type(self, value: Any) -> bool:
        return True


class MockMappingArgument:
    def __init__(self, origin: Any, args: tuple[Any, ...]) -> None:
        self.annotation = None  # Not used for mapping tests
        self._origin = origin
        self._args = args

    @property
    def spec(self) -> tuple[Any, tuple[Any, ...]]:
        return self._origin, self._args

    @property
    def description(self) -> str:
        return "Mock mapping argument for testing"

    @property
    def default(self) -> MockDefaultValue:
        return MockDefaultValue()

    @property
    def kind(self) -> ArgumentKind:
        return POSITIONAL_OR_KEYWORD

    def has_valid_type(self, value: Any) -> bool:
        return True


class TestProtocol(Protocol):
    def method(self) -> None: ...


class TestABC(ABC):
    @abstractmethod
    def method(self) -> None: ...


class RegularClass:
    def method(self) -> None:
        pass


class TestInterfaceFunctions(unittest.TestCase):
    def test_is_protocol_with_protocol(self) -> None:
        arg = MockArgument(TestProtocol)
        self.assertTrue(is_protocol(arg))

    def test_is_protocol_with_regular_class(self) -> None:
        arg = MockArgument(RegularClass)
        self.assertFalse(is_protocol(arg))

    def test_is_protocol_with_abc(self) -> None:
        arg = MockArgument(TestABC)
        self.assertFalse(is_protocol(arg))

    def test_is_abc_with_abc(self) -> None:
        arg = MockArgument(TestABC)
        self.assertTrue(is_abc(arg))

    def test_is_abc_with_regular_class(self) -> None:
        arg = MockArgument(RegularClass)
        self.assertFalse(is_abc(arg))

    def test_is_abc_with_protocol(self) -> None:
        arg = MockArgument(TestProtocol)
        self.assertFalse(is_abc(arg))

    def test_is_interface_with_protocol(self) -> None:
        arg = MockArgument(TestProtocol)
        self.assertTrue(is_interface(arg))

    def test_is_interface_with_abc(self) -> None:
        arg = MockArgument(TestABC)
        self.assertTrue(is_interface(arg))

    def test_is_interface_with_regular_class(self) -> None:
        arg = MockArgument(RegularClass)
        self.assertFalse(is_interface(arg))

    def test_is_interface_comprehensive(self) -> None:
        protocol_arg = MockArgument(TestProtocol)
        abc_arg = MockArgument(TestABC)
        regular_arg = MockArgument(RegularClass)

        self.assertTrue(is_interface(protocol_arg))
        self.assertTrue(is_interface(abc_arg))
        self.assertFalse(is_interface(regular_arg))


class TestIsInterfaceMapping(unittest.TestCase):
    def test_mapping_with_protocol_interface(self) -> None:
        """Test Mapping[type, Protocol] returns the Protocol type."""
        arg = MockMappingArgument(Mapping, (type, TestProtocol))
        result = is_interface_mapping(arg)
        self.assertEqual(result, TestProtocol)

    def test_mapping_with_abc_interface(self) -> None:
        """Test Mapping[str, ABC] returns the ABC type."""
        arg = MockMappingArgument(Mapping, (str, TestABC))
        result = is_interface_mapping(arg)
        self.assertEqual(result, TestABC)

    def test_dict_with_protocol_interface(self) -> None:
        """Test dict[type, Protocol] returns the Protocol type."""
        arg = MockMappingArgument(dict, (type, TestProtocol))
        result = is_interface_mapping(arg)
        self.assertEqual(result, TestProtocol)

    def test_dict_with_abc_interface(self) -> None:
        """Test dict[str, ABC] returns the ABC type."""
        arg = MockMappingArgument(dict, (str, TestABC))
        result = is_interface_mapping(arg)
        self.assertEqual(result, TestABC)

    def test_mapping_with_regular_class(self) -> None:
        """Test Mapping[type, RegularClass] returns None."""
        arg = MockMappingArgument(Mapping, (type, RegularClass))
        result = is_interface_mapping(arg)
        self.assertIsNone(result)

    def test_non_mapping_type(self) -> None:
        """Test non-mapping types return None."""
        arg = MockMappingArgument(list, (TestProtocol,))
        result = is_interface_mapping(arg)
        self.assertIsNone(result)

    def test_mapping_with_wrong_arg_count_single(self) -> None:
        """Test Mapping[OnlyOneType] returns None."""
        arg = MockMappingArgument(Mapping, (TestProtocol,))
        result = is_interface_mapping(arg)
        self.assertIsNone(result)

    def test_mapping_with_wrong_arg_count_three(self) -> None:
        """Test Mapping[A, B, C] returns None."""
        arg = MockMappingArgument(Mapping, (str, TestProtocol, int))
        result = is_interface_mapping(arg)
        self.assertIsNone(result)

    def test_mapping_with_no_args(self) -> None:
        """Test raw Mapping with no type args returns None."""
        arg = MockMappingArgument(Mapping, ())
        result = is_interface_mapping(arg)
        self.assertIsNone(result)

    def test_comprehensive_interface_mapping(self) -> None:
        """Comprehensive test covering all interface mapping scenarios."""
        # Positive cases
        mapping_protocol = MockMappingArgument(Mapping, (type, TestProtocol))
        mapping_abc = MockMappingArgument(Mapping, (str, TestABC))
        dict_protocol = MockMappingArgument(dict, (int, TestProtocol))
        dict_abc = MockMappingArgument(dict, (type, TestABC))

        self.assertEqual(is_interface_mapping(mapping_protocol), TestProtocol)
        self.assertEqual(is_interface_mapping(mapping_abc), TestABC)
        self.assertEqual(is_interface_mapping(dict_protocol), TestProtocol)
        self.assertEqual(is_interface_mapping(dict_abc), TestABC)

        # Negative cases
        non_mapping = MockMappingArgument(list, (TestProtocol,))
        wrong_value_type = MockMappingArgument(Mapping, (type, RegularClass))
        wrong_arg_count = MockMappingArgument(Mapping, (TestProtocol,))
        no_args = MockMappingArgument(Mapping, ())

        self.assertIsNone(is_interface_mapping(non_mapping))
        self.assertIsNone(is_interface_mapping(wrong_value_type))
        self.assertIsNone(is_interface_mapping(wrong_arg_count))
        self.assertIsNone(is_interface_mapping(no_args))


if __name__ == "__main__":
    unittest.main()
