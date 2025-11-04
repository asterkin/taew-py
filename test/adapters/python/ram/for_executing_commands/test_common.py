"""Tests for common base class for command execution adapters."""

import unittest

from taew.adapters.python.ram.for_executing_commands._common import ExecuteBase
from taew.domain.cli import CommandLine, Result


class TestExecuteBase(unittest.TestCase):
    """Test suite for ExecuteBase configuration infrastructure."""

    def test_stores_command_mapping(self):
        """ExecuteBase should store command-result mapping."""
        cmd1 = CommandLine(command="./bin/app", args=("--version",))
        cmd2 = CommandLine(command="./bin/app", args=("--help",))
        result1 = Result(stdout="1.0.0\n", stderr="", returncode=0)
        result2 = Result(stdout="help\n", stderr="", returncode=0)

        base = ExecuteBase(_commands={cmd1: result1, cmd2: result2})

        self.assertEqual(base._commands[cmd1], result1)
        self.assertEqual(base._commands[cmd2], result2)

    def test_empty_command_mapping(self):
        """ExecuteBase should support empty command mapping."""
        base = ExecuteBase(_commands={})

        self.assertEqual(len(base._commands), 0)

    def test_command_with_env_as_key(self):
        """ExecuteBase should support CommandLine with env as dict key."""
        cmd = CommandLine(
            command="./bin/app", args=("--debug",), env=(("DEBUG", "1"),)
        )
        result = Result(stdout="debug\n", stderr="", returncode=0)

        base = ExecuteBase(_commands={cmd: result})

        self.assertEqual(base._commands[cmd], result)


if __name__ == "__main__":
    unittest.main()
