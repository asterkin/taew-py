"""Tests for unittest-based testing utilities."""

import unittest

from taew.domain.cli_test import SubTest, Test
from taew.domain.cli import CommandLine, Result
from taew.utils.unittest import TestCLI as TestCLIBase
from taew.ports.for_configuring_adapters import Configure


class TestCLI(TestCLIBase):
    """Test TestCLI framework using RAM adapter."""

    def _get_execute(self) -> Configure:
        """Override to use RAM adapter with predefined commands."""
        from taew.adapters.python.ram.for_executing_commands.for_configuring_adapters import (
            Configure as RAMExecute,
        )

        commands = {
            CommandLine(command="./bin/myapp", args=("--version",)): Result(
                stdout="1.0.0\n", stderr="", returncode=0
            ),
            CommandLine(command="./bin/myapp", args=("--help",)): Result(
                stdout="usage info\n", stderr="", returncode=0
            ),
            CommandLine(command="./bin/myapp", args=("--error",)): Result(
                stdout="", stderr="error occurred\n", returncode=1
            ),
        }

        return RAMExecute(_commands=commands)

    def test_multiple_subtests(self) -> None:
        """Test can run multiple subtests in single test."""
        self._run(
            Test(
                name="Multiple SubTests",
                command="./bin/myapp",
                subtests=(
                    SubTest(
                        name="version",
                        args=("--version",),
                        expected=Result(stdout="1.0.0\n", stderr="", returncode=0),
                    ),
                    SubTest(
                        name="help",
                        args=("--help",),
                        expected=Result(stdout="usage info\n", stderr="", returncode=0),
                    ),
                ),
            )
        )

    def test_stderr_and_exit_code(self) -> None:
        """Test stderr capture and non-zero exit code."""
        self._run(
            Test(
                name="Error Test",
                command="./bin/myapp",
                subtests=(
                    SubTest(
                        name="error",
                        args=("--error",),
                        expected=Result(
                            stdout="", stderr="error occurred\n", returncode=1
                        ),
                    ),
                ),
            )
        )


if __name__ == "__main__":
    unittest.main()
