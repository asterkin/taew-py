import unittest
from datetime import date, datetime
from pathlib import Path
from typing import NamedTuple

from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.ports.for_marshalling_objects import (
    FromMarshallable as FromMarshallableProtocol,
    ToMarshallable as ToMarshallableProtocol,
)


class SimpleRecord(NamedTuple):
    """Simple named tuple with basic types."""

    name: str
    age: int
    score: float


class DateTimeRecord(NamedTuple):
    """Named tuple with datetime and date fields."""

    event_time: datetime
    event_date: date
    description: str


class TestNamedTupleConfigureIntegration(unittest.TestCase):
    """Integration tests for named tuple marshalling adapter with dynamic binding."""

    def _get_configure_simple(self) -> ConfigureProtocol:
        from taew.adapters.python.named_tuple.for_marshalling_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_args=(SimpleRecord,))

    def _get_configure_datetime(
        self, variants: dict[type, str | dict[str, object]] | None = None
    ) -> ConfigureProtocol:
        from taew.adapters.python.named_tuple.for_marshalling_objects.for_configuring_adapters import (
            Configure,
        )

        if variants:
            return Configure(_args=(DateTimeRecord,), _variants=variants)
        return Configure(_args=(DateTimeRecord,))

    def test_simple_named_tuple_round_trip(self) -> None:
        """Test round-trip with simple types (str, int, float)."""
        configure: ConfigureProtocol = self._get_configure_simple()
        ports = configure()
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        from taew.adapters.launch_time.for_binding_interfaces.bind import bind

        # Configure for_browsing_code_tree

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)

        to_marshallable = bind(ToMarshallableProtocol, ports)
        from_marshallable = bind(FromMarshallableProtocol, ports)

        record = SimpleRecord(name="Alice", age=30, score=95.5)

        marshallable = to_marshallable(record)
        self.assertIsInstance(marshallable, dict)
        assert isinstance(marshallable, dict)
        self.assertEqual(marshallable["name"], "Alice")
        self.assertEqual(marshallable["age"], 30)
        self.assertEqual(marshallable["score"], 95.5)

        restored = from_marshallable(marshallable)
        self.assertIsInstance(restored, SimpleRecord)
        self.assertEqual(record, restored)

    def test_datetime_named_tuple_with_variants(self) -> None:
        """Test named tuple with datetime/date fields using explicit variants."""
        variants: dict[type, str | dict[str, object]] = {
            datetime: "timestamp",
            date: "isoformat",
        }
        configure: ConfigureProtocol = self._get_configure_datetime(variants)
        ports = configure()
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        from taew.adapters.launch_time.for_binding_interfaces.bind import bind

        to_marshallable = bind(ToMarshallableProtocol, ports)
        from_marshallable = bind(FromMarshallableProtocol, ports)

        record = DateTimeRecord(
            event_time=datetime(2025, 10, 15, 14, 30, 45),
            event_date=date(2025, 10, 15),
            description="Test event",
        )

        marshallable = to_marshallable(record)
        self.assertIsInstance(marshallable, dict)
        assert isinstance(marshallable, dict)

        # Verify datetime is timestamp (float)
        self.assertIsInstance(marshallable["event_time"], float)
        # Verify date is ISO format string
        self.assertIsInstance(marshallable["event_date"], str)
        self.assertEqual(marshallable["event_date"], "2025-10-15")
        # Verify description is plain string
        self.assertEqual(marshallable["description"], "Test event")

        restored = from_marshallable(marshallable)
        self.assertIsInstance(restored, DateTimeRecord)
        assert isinstance(restored, DateTimeRecord)

        # Verify fields
        self.assertEqual(restored.description, "Test event")
        self.assertEqual(restored.event_date, date(2025, 10, 15))
        # Datetime loses microseconds in float conversion
        self.assertAlmostEqual(
            restored.event_time.timestamp(), record.event_time.timestamp(), delta=0.001
        )

    def test_to_marshallable_error_on_non_namedtuple(self) -> None:
        """Test that ToMarshallable raises TypeError for non-namedtuple."""
        configure: ConfigureProtocol = self._get_configure_simple()
        ports = configure()
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        from taew.adapters.launch_time.for_binding_interfaces.bind import bind

        to_marshallable = bind(ToMarshallableProtocol, ports)

        with self.assertRaises(TypeError) as cm:
            to_marshallable("not a namedtuple")

        self.assertIn("Expected named tuple with _fields attribute", str(cm.exception))

    def test_from_marshallable_error_on_non_dict(self) -> None:
        """Test that FromMarshallable raises TypeError for non-dict."""
        configure: ConfigureProtocol = self._get_configure_simple()
        ports = configure()
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        from taew.adapters.launch_time.for_binding_interfaces.bind import bind

        from_marshallable = bind(FromMarshallableProtocol, ports)

        with self.assertRaises(TypeError) as cm:
            from_marshallable("not a dict")  # type: ignore[arg-type]

        self.assertIn("Expected dict for named tuple unmarshalling", str(cm.exception))

    def test_from_marshallable_error_on_field_mismatch(self) -> None:
        """Test that FromMarshallable raises ValueError for field mismatch."""
        configure: ConfigureProtocol = self._get_configure_simple()
        ports = configure()
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        from taew.adapters.launch_time.for_binding_interfaces.bind import bind

        from_marshallable = bind(FromMarshallableProtocol, ports)

        # Missing 'score' field
        invalid_dict: dict[str, object] = {"name": "Alice", "age": 30}

        with self.assertRaises(ValueError) as cm:
            from_marshallable(invalid_dict)  # type: ignore[arg-type]

        self.assertIn("Field mismatch", str(cm.exception))

    def test_configure_returns_ports_mapping(self) -> None:
        """Test that Configure returns a valid PortsMapping."""
        configure = self._get_configure_simple()
        ports = configure()
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        self.assertIsInstance(ports, dict)
        self.assertGreater(len(ports), 0)

    def test_field_order_preserved(self) -> None:
        """Test that field order is preserved in marshalling."""
        configure: ConfigureProtocol = self._get_configure_simple()
        ports = configure()
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        from taew.adapters.launch_time.for_binding_interfaces.bind import bind

        to_marshallable = bind(ToMarshallableProtocol, ports)

        record = SimpleRecord(name="Bob", age=25, score=88.0)
        marshallable = to_marshallable(record)

        assert isinstance(marshallable, dict)
        # Dict keys should match field names
        self.assertEqual(set(marshallable.keys()), {"name", "age", "score"})


if __name__ == "__main__":
    unittest.main()
