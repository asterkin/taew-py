import unittest
from datetime import datetime, timezone
from pathlib import Path

from taew.ports.for_marshalling_objects import (
    ToMarshallable as ToMarshallableProtocol,
    FromMarshallable as FromMarshallableProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.adapters.launch_time.for_binding_interfaces.bind import bind


class TestDatetimeTimestampConfigureIntegration(unittest.TestCase):
    """Integration tests for datetime timestamp marshalling adapter with dynamic binding."""

    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.datetime.timestamp.for_marshalling_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure()

    def test_bind_and_round_trip_naive_datetimes(self) -> None:
        """Test full round-trip through dynamic adapter binding for naive datetimes."""
        configure: ConfigureProtocol = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import Configure as BrowseCodeTree

        from pathlib import Path

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)


        # Configure for_browsing_code_tree
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import Configure as BrowseCodeTree
        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        to_marshallable = bind(ToMarshallableProtocol, ports)
        from_marshallable = bind(FromMarshallableProtocol, ports)

        test_cases = [
            datetime(2025, 1, 1, 0, 0, 0),
            datetime(2025, 10, 15, 14, 30, 45),
            datetime(2025, 12, 31, 23, 59, 59, 999999),
            datetime(1970, 1, 1, 0, 0, 0),  # Unix epoch
            datetime(2038, 1, 19, 3, 14, 7),  # Near Y2038 limit
        ]

        for dt in test_cases:
            with self.subTest(datetime=dt):
                marshallable = to_marshallable(dt)
                self.assertIsInstance(marshallable, float)
                restored = from_marshallable(marshallable)
                self.assertIsInstance(restored, datetime)
                assert isinstance(restored, datetime)
                # Allow 1 microsecond tolerance for floating point precision
                self.assertAlmostEqual(
                    dt.timestamp(), restored.timestamp(), delta=0.000001
                )

    def test_bind_timezone_aware_datetime_loses_timezone(self) -> None:
        """Test that timezone-aware datetimes lose timezone info in round-trip."""
        configure: ConfigureProtocol = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import Configure as BrowseCodeTree

        from pathlib import Path

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)


        to_marshallable = bind(ToMarshallableProtocol, ports)
        from_marshallable = bind(FromMarshallableProtocol, ports)

        # Create timezone-aware datetime
        dt_aware = datetime(2025, 10, 15, 14, 30, 45, tzinfo=timezone.utc)

        marshallable = to_marshallable(dt_aware)
        self.assertIsInstance(marshallable, float)

        restored = from_marshallable(marshallable)
        self.assertIsInstance(restored, datetime)
        assert isinstance(restored, datetime)
        # Restored datetime should be naive (no timezone)
        self.assertIsNone(restored.tzinfo)
        # Timestamp values should match
        self.assertAlmostEqual(
            dt_aware.timestamp(), restored.timestamp(), delta=0.000001
        )

    def test_to_marshallable_error_on_invalid_type(self) -> None:
        """Test that ToMarshallable raises TypeError for non-datetime values."""
        configure: ConfigureProtocol = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import Configure as BrowseCodeTree

        from pathlib import Path

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)


        to_marshallable = bind(ToMarshallableProtocol, ports)

        with self.assertRaises(TypeError) as cm:
            to_marshallable("not a datetime")

        self.assertIn(
            "Unsupported type for datetime timestamp marshalling", str(cm.exception)
        )

    def test_from_marshallable_error_on_wrong_type(self) -> None:
        """Test that FromMarshallable raises TypeError for non-numeric input."""
        configure: ConfigureProtocol = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import Configure as BrowseCodeTree

        from pathlib import Path

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)


        from_marshallable = bind(FromMarshallableProtocol, ports)

        with self.assertRaises(TypeError) as cm:
            from_marshallable("not a number")  # type: ignore[arg-type]

        self.assertIn(
            "Expected int or float for datetime timestamp unmarshalling",
            str(cm.exception),
        )

    def test_from_marshallable_error_on_invalid_timestamp(self) -> None:
        """Test that FromMarshallable raises ValueError for invalid timestamps."""
        configure: ConfigureProtocol = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import Configure as BrowseCodeTree

        from pathlib import Path

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)


        from_marshallable = bind(FromMarshallableProtocol, ports)

        # Test with extremely large timestamp (beyond system limits)
        with self.assertRaises(ValueError) as cm:
            from_marshallable(1e20)  # Extremely large timestamp

        self.assertIn("Unable to parse datetime from timestamp", str(cm.exception))

    def test_configure_returns_ports_mapping(self) -> None:
        """Test that Configure returns a valid PortsMapping."""
        configure = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import Configure as BrowseCodeTree

        from pathlib import Path

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)

        # PortsMapping is a dict, so we just verify it's a dict with entries
        self.assertIsInstance(ports, dict)
        self.assertGreater(len(ports), 0)

    def test_microsecond_precision(self) -> None:
        """Test that microsecond precision is preserved in round-trip."""
        configure: ConfigureProtocol = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import Configure as BrowseCodeTree

        from pathlib import Path

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)


        to_marshallable = bind(ToMarshallableProtocol, ports)
        from_marshallable = bind(FromMarshallableProtocol, ports)

        dt_with_microseconds = datetime(2025, 10, 15, 14, 30, 45, 123456)

        marshallable = to_marshallable(dt_with_microseconds)
        restored = from_marshallable(marshallable)
        assert isinstance(restored, datetime)

        # Microseconds should be preserved (within floating point precision)
        self.assertEqual(dt_with_microseconds.microsecond, restored.microsecond)


if __name__ == "__main__":
    unittest.main()
