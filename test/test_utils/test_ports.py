"""Tests for taew.utils.ports module."""

import unittest

from taew.domain.logging import INFO, DEBUG
from taew.utils.ports import build


class TestBuildFunction(unittest.TestCase):
    """Test the build function for merging Configure instances."""

    def test_build_with_single_configure(self) -> None:
        """Test build with a single Configure instance."""
        from taew.adapters.python.logging.for_logging.for_configuring_adapters import (
            Configure as ConfigureLogging,
        )

        result = build(ConfigureLogging(_name="TestApp", _level=INFO))

        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_build_with_multiple_configures(self) -> None:
        """Test build with multiple Configure instances."""
        from taew.adapters.python.logging.for_logging.for_configuring_adapters import (
            Configure as ConfigureLogging,
        )
        from taew.adapters.python.ram.for_obtaining_current_datetime.for_configuring_adapters import (
            Configure as ConfigureDateTime,
        )

        result = build(
            ConfigureLogging(_name="TestApp", _level=DEBUG),
            ConfigureDateTime(),
        )

        self.assertIsInstance(result, dict)
        # Should have configurations from both adapters
        self.assertGreater(len(result), 1)

    def test_build_with_no_arguments(self) -> None:
        """Test build with no arguments raises appropriate error."""
        with self.assertRaises((TypeError, ValueError)):
            build()

    def test_build_merges_configurations(self) -> None:
        """Test that build properly merges multiple configurations."""
        from taew.adapters.python.logging.for_logging.for_configuring_adapters import (
            Configure as ConfigureLogging,
        )
        from taew.adapters.python.ram.for_obtaining_current_datetime.for_configuring_adapters import (
            Configure as ConfigureDateTime,
        )

        config1 = ConfigureLogging(_name="App1", _level=INFO)
        config2 = ConfigureDateTime()

        # Build from configs
        result = build(config1, config2)

        # Each config should contribute to the result
        ports1 = config1()
        ports2 = config2()

        # Result should contain keys from both
        for key in ports1.keys():
            self.assertIn(key, result)
        for key in ports2.keys():
            self.assertIn(key, result)

    def test_build_returns_ports_mapping(self) -> None:
        """Test that build returns a valid PortsMapping type."""
        from taew.adapters.python.ram.for_obtaining_current_datetime.for_configuring_adapters import (
            Configure as ConfigureDateTime,
        )

        result = build(ConfigureDateTime())

        # Should be a dict-like PortsMapping
        self.assertIsInstance(result, dict)
        # Type annotation check - PortsMapping is dict[ModuleType, PortConfiguration]
        self.assertTrue(hasattr(result, "keys"))
        self.assertTrue(hasattr(result, "values"))


if __name__ == "__main__":
    unittest.main()
