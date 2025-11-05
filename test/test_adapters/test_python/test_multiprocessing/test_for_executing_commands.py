"""Tests for multiprocessing-based command execution adapter.

Note: The multiprocessing adapter imports CLI entry point modules and calls
their main() functions directly for in-process execution with full coverage.
Since taew-py itself is a library, these tests verify the adapter can be
instantiated and configured correctly.

Full integration testing is done via test/test_utils/test_unittest.py which uses
the TestCLI framework with the multiprocessing adapter.
"""

import unittest
from pathlib import Path

from taew.adapters.launch_time.for_binding_interfaces.bind import bind
from taew.domain.configuration import PortsMapping
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.ports.for_executing_commands import Execute as ExecuteProtocol


class TestExecute(unittest.TestCase):
    """Unit tests for multiprocessing-based Execute adapter configuration."""

    def tearDown(self) -> None:
        """Clear Root cache after each test for isolation."""
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.multiprocessing.for_executing_commands.for_configuring_adapters import (
            Configure,
        )

        return Configure()

    def _get_ports(self) -> PortsMapping:
        """Get ports mapping with browsing configuration."""
        configure = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        return ports

    def test_configure_returns_ports_mapping(self) -> None:
        """Test that Configure returns a valid PortsMapping."""
        ports = self._get_ports()

        # PortsMapping is a dict, so we just verify it's a dict with entries
        self.assertIsInstance(ports, dict)
        self.assertGreater(len(ports), 0)

    def test_can_bind_execute_protocol(self) -> None:
        """Test that Execute protocol can be bound with multiprocessing adapter."""
        ports = self._get_ports()
        execute = bind(ExecuteProtocol, ports)

        # Verify we got an Execute instance
        self.assertIsNotNone(execute)
        # Verify it's callable
        self.assertTrue(callable(execute))


if __name__ == "__main__":
    unittest.main()
