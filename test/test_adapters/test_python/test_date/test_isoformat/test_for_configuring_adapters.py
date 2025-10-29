import unittest
from datetime import date
from pathlib import Path

from taew.ports.for_marshalling_objects import (
    FromMarshallable as FromMarshallableProtocol,
    ToMarshallable as ToMarshallableProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestDateIsoformatConfigureIntegration(unittest.TestCase):
    def tearDown(self) -> None:
        """Clear Root cache after each test for isolation."""
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

    """Integration tests for date isoformat marshalling adapter with dynamic binding."""

    def _get_configure(self, format_str: str | None = None) -> ConfigureProtocol:
        from taew.adapters.python.date.isoformat.for_marshalling_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_format=format_str) if format_str else Configure()

    def test_bind_and_round_trip_iso_format(self) -> None:
        """Test full round-trip through dynamic adapter binding using ISO format."""
        configure: ConfigureProtocol = self._get_configure()
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

        test_cases = [
            date(2025, 1, 1),
            date(2025, 10, 15),
            date(2025, 12, 31),
            date(1970, 1, 1),  # Unix epoch
            date(2038, 1, 19),  # Near Y2038 limit
            date(1900, 1, 1),  # Historical date
            date(2099, 12, 31),  # Future date
        ]

        for dt in test_cases:
            with self.subTest(date=dt):
                marshallable = to_marshallable(dt)
                self.assertIsInstance(marshallable, str)
                assert isinstance(marshallable, str)
                # Verify ISO format
                self.assertRegex(marshallable, r"^\d{4}-\d{2}-\d{2}$")
                restored = from_marshallable(marshallable)
                self.assertIsInstance(restored, date)
                assert isinstance(restored, date)
                self.assertEqual(dt, restored)

    def test_bind_with_custom_format(self) -> None:
        """Test round-trip with custom date format."""
        configure: ConfigureProtocol = self._get_configure("%Y/%m/%d")
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)

        from taew.adapters.launch_time.for_binding_interfaces.bind import bind

        to_marshallable = bind(ToMarshallableProtocol, ports)
        from_marshallable = bind(FromMarshallableProtocol, ports)

        test_date = date(2025, 10, 15)

        marshallable = to_marshallable(test_date)
        self.assertIsInstance(marshallable, str)
        self.assertEqual(marshallable, "2025/10/15")

        restored = from_marshallable(marshallable)
        self.assertIsInstance(restored, date)
        assert isinstance(restored, date)
        self.assertEqual(test_date, restored)

    def test_to_marshallable_error_on_invalid_type(self) -> None:
        """Test that ToMarshallable raises TypeError for non-date values."""
        configure: ConfigureProtocol = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)

        from taew.adapters.launch_time.for_binding_interfaces.bind import bind

        to_marshallable = bind(ToMarshallableProtocol, ports)

        with self.assertRaises(TypeError) as cm:
            to_marshallable("not a date")

        self.assertIn(
            "Unsupported type for date isoformat marshalling", str(cm.exception)
        )

    def test_from_marshallable_error_on_wrong_type(self) -> None:
        """Test that FromMarshallable raises TypeError for non-string input."""
        configure: ConfigureProtocol = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)

        from taew.adapters.launch_time.for_binding_interfaces.bind import bind

        from_marshallable = bind(FromMarshallableProtocol, ports)

        with self.assertRaises(TypeError) as cm:
            from_marshallable(123)  # type: ignore[arg-type]

        self.assertIn(
            "Expected string for date isoformat unmarshalling", str(cm.exception)
        )

    def test_from_marshallable_error_on_invalid_iso_format(self) -> None:
        """Test that FromMarshallable raises ValueError for invalid ISO date strings."""
        configure: ConfigureProtocol = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)

        from taew.adapters.launch_time.for_binding_interfaces.bind import bind

        from_marshallable = bind(FromMarshallableProtocol, ports)

        invalid_strings = [
            "not-a-date",
            "2025-13-01",  # Invalid month
            "2025-02-30",  # Invalid day
            "2025/10/15",  # Wrong format (should be YYYY-MM-DD)
        ]

        for invalid_string in invalid_strings:
            with self.subTest(string=invalid_string):
                with self.assertRaises(ValueError) as cm:
                    from_marshallable(invalid_string)

                self.assertIn("Unable to parse date", str(cm.exception))

    def test_from_marshallable_error_on_invalid_custom_format(self) -> None:
        """Test that FromMarshallable raises ValueError for invalid custom format strings."""
        configure: ConfigureProtocol = self._get_configure("%Y/%m/%d")
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)

        from taew.adapters.launch_time.for_binding_interfaces.bind import bind

        from_marshallable = bind(FromMarshallableProtocol, ports)

        # Try ISO format when expecting slash format
        with self.assertRaises(ValueError) as cm:
            from_marshallable("2025-10-15")

        self.assertIn("Unable to parse date with format", str(cm.exception))

    def test_configure_returns_ports_mapping(self) -> None:
        """Test that Configure returns a valid PortsMapping."""
        configure = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)

        # PortsMapping is a dict, so we just verify it's a dict with entries
        self.assertIsInstance(ports, dict)
        self.assertGreater(len(ports), 0)

    def test_special_dates(self) -> None:
        """Test special edge-case dates."""
        configure: ConfigureProtocol = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)

        from taew.adapters.launch_time.for_binding_interfaces.bind import bind

        to_marshallable = bind(ToMarshallableProtocol, ports)
        from_marshallable = bind(FromMarshallableProtocol, ports)

        special_cases = [
            date(2000, 2, 29),  # Leap year
            date(2100, 1, 1),  # Not a leap year (divisible by 100 but not 400)
            date(2000, 1, 1),  # Y2K
            date(1999, 12, 31),  # Before Y2K
        ]

        for special_date in special_cases:
            with self.subTest(date=special_date):
                marshallable = to_marshallable(special_date)
                restored = from_marshallable(marshallable)
                assert isinstance(restored, date)
                self.assertEqual(special_date, restored)


if __name__ == "__main__":
    unittest.main()
