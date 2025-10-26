"""Unit tests for BytesIO-based serialization adapter."""

import unittest
from pathlib import Path
from typing import NamedTuple

from taew.ports.for_serializing_objects import (
    Serialize as SerializeProtocol,
    Deserialize as DeserializeProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class Person(NamedTuple):
    """Simple test NamedTuple."""

    name: str
    age: int
    height: float


class TestBytesIOSerialization(unittest.TestCase):
    """Test cases for BytesIO-based serialization with NamedTuple."""

    def _get_configurator(
        self, named_tuple_type: type[NamedTuple]
    ) -> ConfigureProtocol:
        """Create configurator for named tuple type."""
        from taew.adapters.python.io.bytesio.for_serializing_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_type=named_tuple_type)

    def _bind_adapters(
        self, named_tuple_type: type[NamedTuple]
    ) -> tuple[SerializeProtocol, DeserializeProtocol]:
        """Bind serialize and deserialize adapters for named tuple type."""
        configurator = self._get_configurator(named_tuple_type)
        ports = configurator()

        from taew.adapters.python.inspect.for_browsing_code_tree.root import (
            Root as InspectRoot,
        )
        from taew.adapters.launch_time.for_binding_interfaces.bind import Bind

        root = InspectRoot(Path("."))
        bind = Bind(root)

        serialize = bind(SerializeProtocol, ports)
        deserialize = bind(DeserializeProtocol, ports)

        return serialize, deserialize

    def test_round_trip_named_tuple(self) -> None:
        """Test serialization and deserialization round trip with NamedTuple."""
        test_cases = (
            Person("Alice", 30, 5.5),
            Person("Bob", 25, 6.0),
            Person("", 0, 0.0),
        )

        serialize, deserialize = self._bind_adapters(Person)

        for person in test_cases:
            with self.subTest(person=person):
                # Serialize to bytes
                serialized = serialize(person)
                self.assertIsInstance(serialized, bytes)
                self.assertGreater(len(serialized), 0)

                # Deserialize back to object
                deserialized = deserialize(serialized)
                self.assertEqual(person, deserialized)

    def test_deserialize_with_trailing_bytes_raises_error(self) -> None:
        """Test that deserialization fails if stream not fully consumed."""
        serialize, deserialize = self._bind_adapters(Person)

        person = Person("Test", 42, 1.75)
        serialized = serialize(person)

        # Add trailing bytes
        corrupted = serialized + b"\x00\x01\x02"

        with self.assertRaises(ValueError) as context:
            deserialize(corrupted)

        self.assertIn("not fully consumed", str(context.exception))
        self.assertIn("3 trailing bytes", str(context.exception))


if __name__ == "__main__":
    unittest.main()
