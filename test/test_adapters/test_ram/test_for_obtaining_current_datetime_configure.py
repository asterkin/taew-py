"""Tests for RAM current datetime Configure adapter."""

import unittest
from pathlib import Path

from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.ports.for_obtaining_current_datetime import Now as NowProtocol
from taew.adapters.launch_time.for_binding_interfaces.bind import bind


class TestRamCurrentDateTimeConfigureIntegration(unittest.TestCase):
    def tearDown(self) -> None:
        """Clear Root cache after each test for isolation."""
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

    """Integration tests for RAM current datetime adapter configuration."""

    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.ram.for_obtaining_current_datetime.for_configuring_adapters import (
            Configure,
        )

        return Configure()

    def _bind(self, cfg: ConfigureProtocol) -> NowProtocol:
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )
        from taew.utils.configure import configure as configure_adapters

        ports = cfg()
        # Add for_browsing_code_tree configuration
        ports_with_browsing = configure_adapters(BrowseCodeTree(_root_path=Path("./")))
        ports.update(ports_with_browsing)

        return bind(NowProtocol, ports)

    def test_configure_returns_ports_mapping(self) -> None:
        """Test that Configure returns a valid PortsMapping."""
        cfg = self._get_configure()
        ports = cfg()

        self.assertIsInstance(ports, dict)
        self.assertGreater(len(ports), 0)

    def test_configure_creates_working_adapter(self) -> None:
        """Test that Configure creates a working Now adapter."""
        cfg = self._get_configure()
        now = self._bind(cfg)

        # Should be callable and return a datetime
        result = now()
        from datetime import datetime

        self.assertIsInstance(result, datetime)


if __name__ == "__main__":
    unittest.main()
