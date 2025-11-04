"""Tests for RAM-based command execution adapter."""

import unittest
from pathlib import Path

from taew.adapters.launch_time.for_binding_interfaces.bind import bind
from taew.domain.cli import CommandLine, Result
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.ports.for_executing_commands import Execute as ExecuteProtocol


class TestExecute(unittest.TestCase):
    """Integration tests for RAM-based Execute adapter with dynamic binding."""

    def tearDown(self) -> None:
        """Clear Root cache after each test for isolation."""
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

    def _get_configure(
        self, commands: dict[CommandLine, Result]
    ) -> ConfigureProtocol:
        from taew.adapters.python.ram.for_executing_commands.for_configuring_adapters import (
            Configure,
        )

        return Configure(_commands=commands)

    def _get_ports(self, commands: dict[CommandLine, Result]) -> dict:
        """Get ports mapping with browsing configuration."""
        configure = self._get_configure(commands)
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        return ports

    def test_execute_returns_predefined_result(self):
        """Execute should return the predefined result for a command."""
        cmd = CommandLine(command="./bin/app", args=("--version",))
        expected = Result(stdout="1.0.0\n", stderr="", returncode=0)
        ports = self._get_ports({cmd: expected})

        execute = bind(ExecuteProtocol, ports)
        result = execute(cmd)

        self.assertEqual(result, expected)

    def test_execute_raises_key_error_for_unknown_command(self):
        """Execute should raise KeyError for unmapped commands."""
        ports = self._get_ports({})
        execute = bind(ExecuteProtocol, ports)
        cmd = CommandLine(command="./bin/unknown", args=())

        with self.assertRaises(KeyError):
            execute(cmd)

    def test_execute_distinguishes_by_args(self):
        """Execute should distinguish commands with different arguments."""
        base_cmd = "./bin/app"
        cmd_version = CommandLine(command=base_cmd, args=("--version",))
        cmd_help = CommandLine(command=base_cmd, args=("--help",))
        ports = self._get_ports(
            {
                cmd_version: Result("1.0.0\n", "", 0),
                cmd_help: Result("usage\n", "", 0),
            }
        )

        execute = bind(ExecuteProtocol, ports)
        result_version = execute(cmd_version)
        result_help = execute(cmd_help)

        self.assertEqual(result_version.stdout, "1.0.0\n")
        self.assertEqual(result_help.stdout, "usage\n")

    def test_execute_distinguishes_by_env(self):
        """Execute should distinguish commands with different environments."""
        cmd_no_env = CommandLine(command="./bin/app", args=("--debug",))
        cmd_with_env = CommandLine(
            command="./bin/app", args=("--debug",), env=(("DEBUG", "1"),)
        )
        ports = self._get_ports(
            {
                cmd_no_env: Result("debug: off\n", "", 0),
                cmd_with_env: Result("debug: on\n", "", 0),
            }
        )

        execute = bind(ExecuteProtocol, ports)
        result_no_env = execute(cmd_no_env)
        result_with_env = execute(cmd_with_env)

        self.assertEqual(result_no_env.stdout, "debug: off\n")
        self.assertEqual(result_with_env.stdout, "debug: on\n")

    def test_execute_allows_multiple_calls(self):
        """Execute should allow calling the same command multiple times."""
        cmd = CommandLine(command="./bin/app", args=("--test",))
        ports = self._get_ports({cmd: Result("ok\n", "", 0)})

        execute = bind(ExecuteProtocol, ports)
        result1 = execute(cmd)
        result2 = execute(cmd)
        result3 = execute(cmd)

        self.assertEqual(result1.stdout, "ok\n")
        self.assertEqual(result2.stdout, "ok\n")
        self.assertEqual(result3.stdout, "ok\n")

    def test_configure_returns_ports_mapping(self):
        """Test that Configure returns a valid PortsMapping."""
        cmd = CommandLine(command="./bin/app", args=("--version",))
        ports = self._get_ports({cmd: Result("1.0.0\n", "", 0)})

        # PortsMapping is a dict, so we just verify it's a dict with entries
        self.assertIsInstance(ports, dict)
        self.assertGreater(len(ports), 0)


if __name__ == "__main__":
    unittest.main()
