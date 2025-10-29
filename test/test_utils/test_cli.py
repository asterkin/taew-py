"""Tests for taew.utils.cli module."""

import unittest

from taew.utils.cli import configure
from taew.adapters.python.ram.for_browsing_code_tree.root import Root
from taew.adapters.python.ram.for_browsing_code_tree.package import Package


class TestCLIConfigureFunction(unittest.TestCase):
    """Test the configure function for CLI application setup."""

    def tearDown(self) -> None:
        """Clear Root cache after each test for isolation."""
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create a mock CLI package for testing
        self.cli_package = Package(
            description="Mock CLI package",
            items={},
            version="1.0.0",
        )

        # Create a mock adapters package containing the CLI package
        self.adapters_package = Package(
            description="Mock adapters package",
            items={"cli": self.cli_package},
            version="1.0.0",
        )

        # Create a mock project root
        self.project_root = Root(
            items={"adapters": self.adapters_package},
        )

    def test_configure_with_no_adapters(self) -> None:
        """Test configure with no application adapters."""
        result = configure()

        self.assertIsInstance(result, dict)
        # Should have infrastructure ports configured
        self.assertGreater(len(result), 0)

    def test_configure_with_single_adapter(self) -> None:
        """Test configure with a single application adapter."""
        from taew.adapters.python.ram.for_obtaining_current_datetime.for_configuring_adapters import (
            Configure as ConfigureDateTime,
        )

        result = configure(ConfigureDateTime())

        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_configure_with_multiple_adapters(self) -> None:
        """Test configure with multiple application adapters."""
        from taew.adapters.python.logging.for_logging.for_configuring_adapters import (
            Configure as ConfigureLogging,
        )
        from taew.adapters.python.ram.for_obtaining_current_datetime.for_configuring_adapters import (
            Configure as ConfigureDateTime,
        )
        from taew.domain.logging import INFO

        result = configure(
            ConfigureLogging(_name="TestApp", _level=INFO),
            ConfigureDateTime(),
        )

        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 1)

    def test_configure_with_variants(self) -> None:
        """Test configure with type variants mapping."""
        from datetime import date

        result = configure(
            variants={date: {"_variant": "isoformat", "_format": "%m/%y"}},
        )

        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_configure_with_custom_cli_package(self) -> None:
        """Test configure with custom cli_package."""
        result = configure(cli_package="custom.cli")

        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_configure_with_all_parameters(self) -> None:
        """Test configure with all parameters specified."""
        from taew.adapters.python.ram.for_obtaining_current_datetime.for_configuring_adapters import (
            Configure as ConfigureDateTime,
        )
        from datetime import date
        from pathlib import Path

        result = configure(
            ConfigureDateTime(),
            root_path=Path("./"),
            cli_package="adapters.cli",
            variants={date: {"_variant": "isoformat"}},
        )

        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_configure_returns_ports_mapping(self) -> None:
        """Test that configure returns a valid PortsMapping type."""
        result = configure()

        # Should be a dict-like PortsMapping
        self.assertIsInstance(result, dict)
        self.assertTrue(hasattr(result, "keys"))
        self.assertTrue(hasattr(result, "values"))
        self.assertTrue(hasattr(result, "items"))

    def test_configure_includes_infrastructure_ports(self) -> None:
        """Test that configure includes expected infrastructure ports."""
        result = configure()

        # Should have multiple infrastructure ports configured
        # (BrowseCodeTree, CLI, PPrint, Argparse, FindConfigurations, BuildConfigPortsMapping)
        self.assertGreaterEqual(len(result), 6)

    def test_configure_with_empty_variants(self) -> None:
        """Test configure with explicitly empty variants dict."""
        result = configure(variants={})

        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()
