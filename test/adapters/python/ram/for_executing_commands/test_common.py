"""Tests for common base class for command execution adapters."""

import unittest

from taew.adapters.python.ram.for_executing_commands._common import ExecuteBase
from taew.domain.cli import CommandLine, Result


class TestExecuteBase(unittest.TestCase):
    """Test suite for ExecuteBase common functionality."""

    def test_lookup_returns_matching_result(self):
        """_lookup should return the first matching result."""
        cmd = CommandLine(command="./bin/app", args=("--version",))
        expected = Result(stdout="1.0.0\n", stderr="", returncode=0)
        base = ExecuteBase(_commands=[(cmd, expected)], _calls=[])

        result = base._lookup(cmd)

        self.assertEqual(result, expected)

    def test_lookup_raises_for_unknown_command(self):
        """_lookup should raise LookupError for unmapped commands."""
        base = ExecuteBase(_commands=[], _calls=[])
        cmd = CommandLine(command="./bin/unknown", args=())

        with self.assertRaises(LookupError) as ctx:
            base._lookup(cmd)

        self.assertIn("No predefined result", str(ctx.exception))
        self.assertIn("./bin/unknown", str(ctx.exception))

    def test_lookup_distinguishes_by_full_specification(self):
        """_lookup should match on command, args, and env."""
        cmd1 = CommandLine(command="./bin/app", args=("--version",))
        cmd2 = CommandLine(command="./bin/app", args=("--help",))
        cmd3 = CommandLine(command="./bin/app", args=("--version",), env={"DEBUG": "1"})

        base = ExecuteBase(
            _commands=[
                (cmd1, Result("1.0.0\n", "", 0)),
                (cmd2, Result("help\n", "", 0)),
                (cmd3, Result("1.0.0-debug\n", "", 0)),
            ],
            _calls=[],
        )

        self.assertEqual(base._lookup(cmd1).stdout, "1.0.0\n")
        self.assertEqual(base._lookup(cmd2).stdout, "help\n")
        self.assertEqual(base._lookup(cmd3).stdout, "1.0.0-debug\n")

    def test_lookup_returns_first_match_for_duplicates(self):
        """_lookup should return the first matching result when duplicates exist."""
        cmd = CommandLine(command="./bin/app", args=("--test",))
        base = ExecuteBase(
            _commands=[
                (cmd, Result("first\n", "", 0)),
                (cmd, Result("second\n", "", 0)),
            ],
            _calls=[],
        )

        result = base._lookup(cmd)

        self.assertEqual(result.stdout, "first\n")

    def test_calls_list_is_mutable(self):
        """_calls list should be mutable for tracking executions."""
        calls: list[CommandLine] = []
        base = ExecuteBase(_commands=[], _calls=calls)
        cmd = CommandLine(command="./bin/test", args=())

        calls.append(cmd)

        self.assertEqual(len(base._calls), 1)
        self.assertEqual(base._calls[0], cmd)


if __name__ == "__main__":
    unittest.main()
