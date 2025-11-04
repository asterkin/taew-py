"""Tests for unittest-based testing utilities."""

import unittest

from taew.domain.cli import CommandLine, Result
from taew.domain.cli_test import SubTest, Test
from taew.ports.for_configuring_adapters import Configure
from taew.utils.unittest import TestCLI as TestCLIBase


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


class TestConfiguration(unittest.TestCase):
    """Test TestCLI configuration override capability."""

    def test_override_get_execute(self) -> None:
        """Subclass should be able to override _get_execute()."""

        class CustomExecuteTest(TestCLIBase):
            execute_called = False

            def _get_execute(self) -> Configure:
                CustomExecuteTest.execute_called = True
                return super()._get_execute()

            def test_dummy(self) -> None:
                """Dummy test to satisfy unittest."""
                pass

        test = CustomExecuteTest("test_dummy")
        test.setUp()

        self.assertTrue(CustomExecuteTest.execute_called)

        test.tearDown()


if __name__ == "__main__":
    unittest.main()
