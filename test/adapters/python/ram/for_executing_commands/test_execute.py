"""Tests for RAM-based command execution adapter."""

import unittest

from taew.adapters.python.ram.for_executing_commands.execute import Execute
from taew.domain.cli import CommandLine, Result


class TestExecute(unittest.TestCase):
    """Test suite for RAM-based Execute adapter."""

    def test_execute_returns_predefined_result(self):
        """Execute should return the predefined result for a command."""
        cmd = CommandLine(command="./bin/app", args=("--version",))
        expected = Result(stdout="1.0.0\n", stderr="", returncode=0)
        execute = Execute(_commands=[(cmd, expected)], _calls=[])

        result = execute(cmd)

        self.assertEqual(result, expected)

    def test_execute_records_calls(self):
        """Execute should record all invocations for verification."""
        cmd1 = CommandLine(command="./bin/app", args=("--version",))
        cmd2 = CommandLine(command="./bin/app", args=("--help",))
        calls: list[CommandLine] = []
        execute = Execute(
            _commands=[
                (cmd1, Result("1.0.0\n", "", 0)),
                (cmd2, Result("usage\n", "", 0)),
            ],
            _calls=calls,
        )

        execute(cmd1)
        execute(cmd2)
        execute(cmd1)

        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0], cmd1)
        self.assertEqual(calls[1], cmd2)
        self.assertEqual(calls[2], cmd1)

    def test_execute_raises_lookup_error_for_unknown_command(self):
        """Execute should raise LookupError for unmapped commands."""
        execute = Execute(_commands=[], _calls=[])
        cmd = CommandLine(command="./bin/unknown", args=())

        with self.assertRaises(LookupError):
            execute(cmd)

    def test_execute_distinguishes_by_args(self):
        """Execute should distinguish commands with different arguments."""
        base_cmd = "./bin/app"
        cmd_version = CommandLine(command=base_cmd, args=("--version",))
        cmd_help = CommandLine(command=base_cmd, args=("--help",))
        execute = Execute(
            _commands=[
                (cmd_version, Result("1.0.0\n", "", 0)),
                (cmd_help, Result("usage\n", "", 0)),
            ],
            _calls=[],
        )

        result_version = execute(cmd_version)
        result_help = execute(cmd_help)

        self.assertEqual(result_version.stdout, "1.0.0\n")
        self.assertEqual(result_help.stdout, "usage\n")

    def test_execute_distinguishes_by_env(self):
        """Execute should distinguish commands with different environments."""
        cmd_no_env = CommandLine(command="./bin/app", args=("--debug",))
        cmd_with_env = CommandLine(
            command="./bin/app", args=("--debug",), env={"DEBUG": "1"}
        )
        execute = Execute(
            _commands=[
                (cmd_no_env, Result("debug: off\n", "", 0)),
                (cmd_with_env, Result("debug: on\n", "", 0)),
            ],
            _calls=[],
        )

        result_no_env = execute(cmd_no_env)
        result_with_env = execute(cmd_with_env)

        self.assertEqual(result_no_env.stdout, "debug: off\n")
        self.assertEqual(result_with_env.stdout, "debug: on\n")


if __name__ == "__main__":
    unittest.main()
