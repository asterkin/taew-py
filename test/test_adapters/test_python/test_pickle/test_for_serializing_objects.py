import unittest
from typing import Any, NamedTuple, cast

from taew.ports.for_serializing_objects import Deserialize as DeserializeProtocol
from taew.ports.for_serializing_objects import Serialize as SerializeProtocol


class Person(NamedTuple):
    name: str
    age: int
    active: bool


class TestPickleSerializationAdapters(unittest.TestCase):
    """Test suite for pickle-based serialization adapters."""

    def _get_serialize(self, **kwargs: Any) -> SerializeProtocol:
        """Factory method for creating Serialize adapter instances."""
        from taew.adapters.python.pickle.for_serializing_objects.serialize import (
            Serialize,
        )

        return Serialize(**kwargs)

    def _get_deserialize(self, **kwargs: Any) -> DeserializeProtocol:
        """Factory method for creating Deserialize adapter instances."""
        from taew.adapters.python.pickle.for_serializing_objects.deserialize import (
            Deserialize,
        )

        return Deserialize(**kwargs)

    def test_serialize_protocol_compliance(self) -> None:
        """Test that Serialize adapter implements the protocol correctly."""
        serialize = self._get_serialize()
        self.assertTrue(callable(serialize))

        person = Person("Alice", 30, True)
        result = serialize(person)
        self.assertIsInstance(result, bytes)

    def test_deserialize_protocol_compliance(self) -> None:
        """Test that Deserialize adapter implements the protocol correctly."""
        deserialize = self._get_deserialize()
        self.assertTrue(callable(deserialize))

        person = Person("Bob", 25, False)
        serialized = self._get_serialize()(person)
        result = deserialize(serialized)
        self.assertEqual(result, person)

    def test_roundtrip_serialization(self) -> None:
        """Test that serialize -> deserialize preserves data."""
        serialize = self._get_serialize()
        deserialize = self._get_deserialize()

        test_data = Person("Charlie", 35, True)
        serialized = serialize(test_data)
        deserialized = deserialize(serialized)

        self.assertEqual(deserialized, test_data)
        self.assertIsInstance(deserialized, Person)

    def test_complex_data_structures(self) -> None:
        """Test serialization of complex nested structures."""
        serialize = self._get_serialize()
        deserialize = self._get_deserialize()

        complex_data = {
            "people": [
                Person("Alice", 30, True),
                Person("Bob", 25, False),
                Person("Charlie", 35, True),
            ],
            "metadata": {"count": 3, "source": "test"},
            "numbers": [1, 2, 3, 4, 5],
        }

        serialized = serialize(complex_data)
        deserialized = deserialize(serialized)

        self.assertEqual(deserialized, complex_data)
        self.assertEqual(len(deserialized["people"]), 3)  # type: ignore
        self.assertIsInstance(deserialized["people"][0], Person)  # type: ignore

    def test_protocol_parameter(self) -> None:
        """Test different pickle protocol versions."""
        serialize_v4 = self._get_serialize(_protocol=4)
        serialize_v5 = self._get_serialize(_protocol=5)
        deserialize = self._get_deserialize()

        person = Person("Dave", 40, True)

        serialized_v4 = serialize_v4(person)
        serialized_v5 = serialize_v5(person)

        # Both should deserialize correctly
        self.assertEqual(deserialize(serialized_v4), person)
        self.assertEqual(deserialize(serialized_v5), person)

        # Results might differ in size/format
        self.assertIsInstance(serialized_v4, bytes)
        self.assertIsInstance(serialized_v5, bytes)

    def test_fix_imports_parameter(self) -> None:
        """Test fix_imports parameter functionality."""
        serialize = self._get_serialize(_fix_imports=False)
        deserialize = self._get_deserialize(_fix_imports=False)

        person = Person("Eve", 28, False)
        serialized = serialize(person)
        deserialized = deserialize(serialized)

        self.assertEqual(deserialized, person)

    def test_encoding_parameters(self) -> None:
        """Test encoding and errors parameters for deserialization."""
        serialize = self._get_serialize()
        deserialize_ascii = self._get_deserialize(_encoding="ASCII", _errors="strict")
        deserialize_utf8 = self._get_deserialize(_encoding="utf-8", _errors="replace")

        person = Person("François", 32, True)
        serialized = serialize(person)

        # Both should handle the data correctly
        result_ascii = deserialize_ascii(serialized)
        result_utf8 = deserialize_utf8(serialized)

        self.assertEqual(result_ascii, person)
        self.assertEqual(result_utf8, person)

    def test_dataclass_properties(self) -> None:
        """Test that dataclass is configured correctly."""
        serialize1 = self._get_serialize(_protocol=4)
        serialize2 = self._get_serialize(_protocol=4)
        serialize3 = self._get_serialize(_protocol=5)

        # eq=False means instances are not equal even with same params
        self.assertNotEqual(serialize1, serialize2)
        self.assertNotEqual(serialize1, serialize3)

        # frozen=True means immutable
        with self.assertRaises(AttributeError):
            serialize1._protocol = 3  # type: ignore

    def test_class_variables(self) -> None:
        """Test that class variables are set correctly."""
        serialize = self._get_serialize()
        deserialize = self._get_deserialize()

        self.assertEqual(serialize._media_type, "application/octet-stream")  # type: ignore
        self.assertEqual(serialize._roundtrippable, True)  # type: ignore
        self.assertEqual(deserialize._media_type, "application/octet-stream")  # type: ignore
        self.assertEqual(deserialize._roundtrippable, True)  # type: ignore

    def test_basic_data_types(self) -> None:
        """Test serialization of basic Python data types."""
        serialize = self._get_serialize()
        deserialize = self._get_deserialize()

        test_cases = [
            42,
            "hello",
            [1, 2, 3],
            {"a": 1, "b": 2},
            (1, 2, 3),
            {1, 2, 3},
            True,
            None,
            3.14,
        ]

        for value in test_cases:
            with self.subTest(value=value):
                serialized = serialize(value)
                deserialized = deserialize(serialized)
                self.assertEqual(deserialized, value)

    def test_namedtuple_fields_preservation(self) -> None:
        """Test that NamedTuple fields are preserved correctly."""
        serialize = self._get_serialize()
        deserialize = self._get_deserialize()

        person = Person("Grace", 45, True)
        serialized = serialize(person)
        deserialized = cast(Person, deserialize(serialized))

        # Check that it's still a Person NamedTuple
        self.assertIsInstance(deserialized, Person)
        self.assertEqual(deserialized.name, "Grace")
        self.assertEqual(deserialized.age, 45)
        self.assertEqual(deserialized.active, True)

    def test_multiple_instances_independence(self) -> None:
        """Test that multiple adapter instances work independently."""
        serialize1 = self._get_serialize(_protocol=4, _fix_imports=True)
        serialize2 = self._get_serialize(_protocol=5, _fix_imports=False)
        deserialize1 = self._get_deserialize(_encoding="ASCII")
        deserialize2 = self._get_deserialize(_encoding="utf-8")

        person = Person("Hugo", 29, False)

        serialized1 = serialize1(person)
        serialized2 = serialize2(person)

        # Both should deserialize correctly with their respective deserializers
        result1 = deserialize1(serialized1)
        result2 = deserialize2(serialized2)

        self.assertEqual(result1, person)
        self.assertEqual(result2, person)

    def test_return_type_consistency(self) -> None:
        """Test that methods always return correct types."""
        serialize = self._get_serialize()
        deserialize = self._get_deserialize()

        various_inputs: list[Any] = [
            None,
            0,
            "",
            [],
            {},
            set(),
            Person("Test", 0, False),
            complex(1, 2),
        ]

        for value in various_inputs:
            with self.subTest(value=type(value).__name__):
                serialized = serialize(value)
                self.assertIsInstance(
                    serialized,
                    bytes,
                    f"Expected bytes, got {type(serialized)} for {type(value)}",
                )

                deserialized = deserialize(serialized)
                self.assertEqual(deserialized, value)


if __name__ == "__main__":
    unittest.main()
