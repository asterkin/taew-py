"""Tests for RAM current datetime Configure adapter."""

import unittest
from pathlib import Path

from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.ports.for_obtaining_current_datetime import Now as NowProtocol


class TestRamCurrentDateTimeConfigureIntegration(unittest.TestCase):
    """Integration tests for RAM current datetime adapter configuration."""

    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.ram.for_obtaining_current_datetime.for_configuring_adapters import (
            Configure,
        )

        return Configure()

    def _bind(self, cfg: ConfigureProtocol) -> NowProtocol:
        from taew.adapters.python.inspect.for_browsing_code_tree.root import (
            Root as InspectRoot,
        )
        from taew.adapters.launch_time.for_binding_interfaces import Bind

        ports = cfg()
        root = InspectRoot(Path("."))
        bind = Bind(root)
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
