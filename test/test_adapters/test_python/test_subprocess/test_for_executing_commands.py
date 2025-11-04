"""Tests for subprocess-based command execution adapter."""

import sys
import unittest
from pathlib import Path

from taew.adapters.launch_time.for_binding_interfaces.bind import bind
from taew.domain.cli import CommandLine
from taew.domain.configuration import PortsMapping
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.ports.for_executing_commands import Execute as ExecuteProtocol


class TestExecute(unittest.TestCase):
    """Integration tests for subprocess-based Execute adapter with dynamic binding."""

    def tearDown(self) -> None:
        """Clear Root cache after each test for isolation."""
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

    def _get_configure(
        self, timeout: float | None = None, cwd: str | None = None
    ) -> ConfigureProtocol:
        from taew.adapters.python.subprocess.for_executing_commands.for_configuring_adapters import (
            Configure,
        )

        return Configure(_timeout=timeout, _cwd=cwd)

    def _get_ports(
        self, timeout: float | None = None, cwd: str | None = None
    ) -> PortsMapping:
        """Get ports mapping with browsing configuration."""
        configure = self._get_configure(timeout=timeout, cwd=cwd)
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        return ports

    def test_execute_simple_command(self) -> None:
        """Execute should run a simple command and capture output."""
        ports = self._get_ports()
        execute = bind(ExecuteProtocol, ports)

        cmd = CommandLine(command="echo", args=("hello", "world"))
        result = execute(cmd)

        self.assertEqual(result.stdout.strip(), "hello world")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.returncode, 0)

    def test_execute_command_with_exit_code(self) -> None:
        """Execute should capture non-zero exit codes without raising."""
        ports = self._get_ports()
        execute = bind(ExecuteProtocol, ports)

        # Use Python to exit with specific code
        cmd = CommandLine(command=sys.executable, args=("-c", "exit(42)"))
        result = execute(cmd)

        self.assertEqual(result.returncode, 42)

    def test_execute_command_with_stderr(self) -> None:
        """Execute should capture stderr output."""
        ports = self._get_ports()
        execute = bind(ExecuteProtocol, ports)

        # Use Python to write to stderr
        cmd = CommandLine(
            command=sys.executable,
            args=("-c", "import sys; sys.stderr.write('error message')"),
        )
        result = execute(cmd)

        self.assertEqual(result.stderr, "error message")
        self.assertEqual(result.returncode, 0)

    def test_execute_command_with_env(self) -> None:
        """Execute should pass environment variables to subprocess."""
        ports = self._get_ports()
        execute = bind(ExecuteProtocol, ports)

        # Use Python to read environment variable
        cmd = CommandLine(
            command=sys.executable,
            args=("-c", "import os; print(os.environ.get('TEST_VAR', ''))"),
            env=(("TEST_VAR", "test_value"),),
        )
        result = execute(cmd)

        self.assertEqual(result.stdout.strip(), "test_value")
        self.assertEqual(result.returncode, 0)

    def test_execute_command_not_found(self) -> None:
        """Execute should raise OSError for non-existent commands."""
        ports = self._get_ports()
        execute = bind(ExecuteProtocol, ports)

        cmd = CommandLine(command="nonexistent_command_xyz", args=())

        with self.assertRaises(OSError) as cm:
            execute(cmd)

        self.assertIn("nonexistent_command_xyz", str(cm.exception))

    def test_execute_with_timeout(self) -> None:
        """Execute should timeout long-running commands."""
        ports = self._get_ports(timeout=0.1)
        execute = bind(ExecuteProtocol, ports)

        # Sleep for longer than timeout
        cmd = CommandLine(
            command=sys.executable,
            args=("-c", "import time; time.sleep(10)"),
        )

        with self.assertRaises(TimeoutError) as cm:
            execute(cmd)

        self.assertIn("timed out", str(cm.exception))

    def test_execute_with_cwd(self) -> None:
        """Execute should run command in specified working directory."""
        ports = self._get_ports(cwd="/tmp")
        execute = bind(ExecuteProtocol, ports)

        # Get current working directory from subprocess
        cmd = CommandLine(
            command=sys.executable,
            args=("-c", "import os; print(os.getcwd())"),
        )
        result = execute(cmd)

        self.assertEqual(result.stdout.strip(), "/tmp")
        self.assertEqual(result.returncode, 0)

    def test_execute_multiple_args(self) -> None:
        """Execute should handle commands with multiple arguments."""
        ports = self._get_ports()
        execute = bind(ExecuteProtocol, ports)

        # Echo with multiple arguments
        cmd = CommandLine(command="echo", args=("a", "b", "c", "d"))
        result = execute(cmd)

        self.assertEqual(result.stdout.strip(), "a b c d")

    def test_configure_returns_ports_mapping(self) -> None:
        """Test that Configure returns a valid PortsMapping."""
        ports = self._get_ports(timeout=30.0, cwd="/tmp")

        # PortsMapping is a dict, so we just verify it's a dict with entries
        self.assertIsInstance(ports, dict)
        self.assertGreater(len(ports), 0)


if __name__ == "__main__":
    unittest.main()
