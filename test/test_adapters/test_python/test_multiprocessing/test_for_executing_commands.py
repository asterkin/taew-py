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
from taew.domain.cli import CommandLine
from taew.domain.configuration import PortsMapping
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.ports.for_executing_commands import Execute as ExecuteProtocol


class TestExecute(unittest.TestCase):
    """Unit tests for multiprocessing-based Execute adapter configuration."""

    def setUp(self) -> None:
        """Set up fixtures directory path as relative path."""
        test_dir = Path(__file__).parent
        self.fixtures_rel = test_dir / "fixtures"
        # Make it relative to current working directory
        self.fixtures_rel = self.fixtures_rel.relative_to(Path.cwd())

    def tearDown(self) -> None:
        """Clear Root cache."""
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

    def test_execute_shim_file_without_extension(self) -> None:
        """Test executing a shim file without .py extension."""
        from taew.adapters.python.multiprocessing.for_executing_commands.execute import (
            Execute,
        )

        execute = Execute()
        cmd_line = CommandLine(
            command=str(self.fixtures_rel / "testcmd"),
            args=("arg1", "arg2"),
            env=(),
        )
        result = execute(cmd_line)

        self.assertEqual(result.returncode, 0)
        self.assertIn("Hello from shim", result.stdout)
        self.assertIn("Args:", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_execute_py_module(self) -> None:
        """Test executing a .py module file."""
        from taew.adapters.python.multiprocessing.for_executing_commands.execute import (
            Execute,
        )

        execute = Execute()
        cmd_line = CommandLine(
            command=str(self.fixtures_rel / "testmodule.py"),
            args=("arg1", "arg2"),
            env=(),
        )
        result = execute(cmd_line)

        self.assertEqual(result.returncode, 0)
        self.assertIn("Hello from module", result.stdout)
        self.assertIn("Args:", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_execute_shim_with_system_exit(self) -> None:
        """Test that SystemExit is captured correctly."""
        from taew.adapters.python.multiprocessing.for_executing_commands.execute import (
            Execute,
        )

        execute = Execute()
        cmd_line = CommandLine(
            command=str(self.fixtures_rel / "exitcmd"), args=(), env=()
        )
        result = execute(cmd_line)

        self.assertEqual(result.returncode, 42)
        self.assertIn("Before exit", result.stdout)

    def test_execute_shim_with_exception(self) -> None:
        """Test that exceptions are captured as stderr."""
        from taew.adapters.python.multiprocessing.for_executing_commands.execute import (
            Execute,
        )

        execute = Execute()
        cmd_line = CommandLine(
            command=str(self.fixtures_rel / "errorcmd"), args=(), env=()
        )
        result = execute(cmd_line)

        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: Test error", result.stderr)

    def test_execute_nonexistent_file(self) -> None:
        """Test that nonexistent file raises appropriate error."""
        from taew.adapters.python.multiprocessing.for_executing_commands.execute import (
            Execute,
        )

        execute = Execute()
        cmd_line = CommandLine(command="./nonexistent/command", args=(), env=())
        result = execute(cmd_line)

        self.assertEqual(result.returncode, 1)
        self.assertIn("does not exist", result.stderr)

    def test_execute_file_without_main(self) -> None:
        """Test that file without main() function is handled."""
        from taew.adapters.python.multiprocessing.for_executing_commands.execute import (
            Execute,
        )

        execute = Execute()
        cmd_line = CommandLine(
            command=str(self.fixtures_rel / "nomain"), args=(), env=()
        )
        result = execute(cmd_line)

        self.assertEqual(result.returncode, 1)
        self.assertIn("has no main() function", result.stderr)

    def test_execute_unsupported_extension(self) -> None:
        """Test that unsupported file extension is rejected."""
        from taew.adapters.python.multiprocessing.for_executing_commands.execute import (
            Execute,
        )

        execute = Execute()
        cmd_line = CommandLine(
            command=str(self.fixtures_rel / "badext.txt"), args=(), env=()
        )
        result = execute(cmd_line)

        self.assertEqual(result.returncode, 1)
        self.assertIn("Unsupported file extension", result.stderr)

    def test_execute_absolute_path_rejected(self) -> None:
        """Test that absolute paths are rejected."""
        from taew.adapters.python.multiprocessing.for_executing_commands.execute import (
            Execute,
        )

        execute = Execute()
        cmd_line = CommandLine(command="/absolute/path/cmd", args=(), env=())

        with self.assertRaises(ValueError) as ctx:
            execute(cmd_line)

        self.assertIn("Absolute command paths not supported", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
