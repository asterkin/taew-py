import unittest
from datetime import date
from pathlib import Path
from typing import NamedTuple

from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.ports.for_stringizing_objects import (
    Dumps as DumpsProtocol,
    Loads as LoadsProtocol,
)


class PaymentCard(NamedTuple):
    """Example named tuple with date field."""

    number: str
    cvv: str
    expiration: date


class TestJsonConfigureIntegration(unittest.TestCase):
    """Integration tests for JSON stringizing with marshalling adapters."""

    def _get_configure_namedtuple(
        self, variants: dict[type, str] | None = None, **kwargs: object
    ) -> ConfigureProtocol:
        from taew.adapters.python.json.for_stringizing_objects.for_configuring_adapters import (
            Configure,
        )

        if variants:
            return Configure(_type=PaymentCard, _variants=variants, **kwargs)  # type: ignore[arg-type]
        return Configure(_type=PaymentCard, **kwargs)  # type: ignore[arg-type]

    def test_namedtuple_with_date_roundtrip(self) -> None:
        """Test round-trip of named tuple with date field using isoformat."""
        variants: dict[type, str] = {date: "isoformat"}
        configure: ConfigureProtocol = self._get_configure_namedtuple(
            variants=variants, _sort_keys=True
        )
        ports = configure()

        from taew.adapters.launch_time.for_binding_interfaces.main import Bind
        from taew.adapters.python.inspect.for_browsing_code_tree.root import (
            Root as InspectRoot,
        )

        root = InspectRoot(Path("."))
        bind = Bind(root)

        dumps = bind(DumpsProtocol, ports)
        loads = bind(LoadsProtocol, ports)

        card = PaymentCard(
            number="1234567890123456", cvv="123", expiration=date(2025, 12, 31)
        )

        json_str = dumps(card)
        self.assertIsInstance(json_str, str)
        self.assertIn('"cvv": "123"', json_str)
        self.assertIn('"expiration": "2025-12-31"', json_str)
        self.assertIn('"number": "1234567890123456"', json_str)

        restored = loads(json_str)
        self.assertIsInstance(restored, PaymentCard)
        self.assertEqual(card, restored)

    def test_json_formatting_options(self) -> None:
        """Test that JSON formatting options (indent, sort_keys) work with marshalling."""
        variants: dict[type, str] = {date: "isoformat"}
        configure: ConfigureProtocol = self._get_configure_namedtuple(
            variants=variants, _indent=2, _sort_keys=True
        )
        ports = configure()

        from taew.adapters.launch_time.for_binding_interfaces.main import Bind
        from taew.adapters.python.inspect.for_browsing_code_tree.root import (
            Root as InspectRoot,
        )

        root = InspectRoot(Path("."))
        bind = Bind(root)

        dumps = bind(DumpsProtocol, ports)

        card = PaymentCard(
            number="1234567890123456", cvv="123", expiration=date(2025, 12, 31)
        )

        json_str = dumps(card)
        # Check indentation
        self.assertIn("\n", json_str)
        # Check sorting (cvv comes before expiration, which comes before number)
        cvv_pos = json_str.index('"cvv"')
        exp_pos = json_str.index('"expiration"')
        num_pos = json_str.index('"number"')
        self.assertLess(cvv_pos, exp_pos)
        self.assertLess(exp_pos, num_pos)

    def test_configure_returns_ports_mapping(self) -> None:
        """Test that Configure returns a valid PortsMapping."""
        variants: dict[type, str] = {date: "isoformat"}
        configure = self._get_configure_namedtuple(variants=variants)
        ports = configure()

        self.assertIsInstance(ports, dict)
        self.assertGreater(len(ports), 0)


if __name__ == "__main__":
    unittest.main()
