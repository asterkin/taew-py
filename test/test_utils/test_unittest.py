"""Tests for unittest-based testing utilities."""

import sys
import unittest

from taew.utils.unittest import TestCLI
from taew.domain.cli import CommandLine, Result
from taew.domain.cli_test import SubTest, Test
from taew.ports.for_configuring_adapters import Configure


class TestTestCLIWithSubprocess(TestCLI):
    """Concrete test using default subprocess configuration."""

    def test_echo_simple(self) -> None:
        """Test simple echo command."""
        self._run(
            Test(
                name="Echo Simple",
                command="echo",
                subtests=(
                    SubTest(
                        name="simple",
                        args=("hello",),
                        expected=Result(stdout="hello\n", stderr="", returncode=0),
                    ),
                ),
            )
        )

    def test_echo_multiple_words(self) -> None:
        """Test echo with multiple arguments."""
        self._run(
            Test(
                name="Echo Multiple",
                command="echo",
                subtests=(
                    SubTest(
                        name="multiple_words",
                        args=("hello", "world"),
                        expected=Result(
                            stdout="hello world\n", stderr="", returncode=0
                        ),
                    ),
                ),
            )
        )


class TestTestCLIWithRAM(TestCLI):
    """Concrete test using RAM adapter override."""

    def _get_execute(self) -> Configure:
        """Override to use RAM adapter with predefined commands."""
        from taew.adapters.python.ram.for_executing_commands.for_configuring_adapters import (
            Configure as RAMExecute,
        )

        # Define expected commands
        commands = {
            CommandLine(command="./bin/myapp", args=("--version",)): Result(
                stdout="1.0.0\n", stderr="", returncode=0
            ),
            CommandLine(command="./bin/myapp", args=("--help",)): Result(
                stdout="usage info\n", stderr="", returncode=0
            ),
        }

        return RAMExecute(_commands=commands)

    def test_version(self) -> None:
        """Test version command with RAM adapter."""
        self._run(
            Test(
                name="Version",
                command="./bin/myapp",
                subtests=(
                    SubTest(
                        name="version",
                        args=("--version",),
                        expected=Result(stdout="1.0.0\n", stderr="", returncode=0),
                    ),
                ),
            )
        )

    def test_help(self) -> None:
        """Test help command with RAM adapter."""
        self._run(
            Test(
                name="Help",
                command="./bin/myapp",
                subtests=(
                    SubTest(
                        name="help",
                        args=("--help",),
                        expected=Result(stdout="usage info\n", stderr="", returncode=0),
                    ),
                ),
            )
        )


class TestTestCLIWithEnv(TestCLI):
    """Test environment variable handling."""

    def test_read_env(self) -> None:
        """Test command with environment variable."""
        self._run(
            Test(
                name="Env Test",
                command=sys.executable,
                subtests=(
                    SubTest(
                        name="read_env",
                        args=(
                            "-c",
                            "import os; print(os.environ.get('TEST_VAR', 'not_found'))",
                        ),
                        expected=Result(stdout="test_value\n", stderr="", returncode=0),
                    ),
                ),
                setup_env={"TEST_VAR": "test_value"},
            )
        )


class TestTestCLIWithNonZeroExit(TestCLI):
    """Test handling of non-zero exit codes."""

    def test_exit_42(self) -> None:
        """Test command with non-zero exit code."""
        self._run(
            Test(
                name="Exit Code Test",
                command=sys.executable,
                subtests=(
                    SubTest(
                        name="exit_42",
                        args=("-c", "exit(42)"),
                        expected=Result(stdout="", stderr="", returncode=42),
                    ),
                ),
            )
        )


class TestTestCLIWithStderr(TestCLI):
    """Test stderr capture."""

    def test_error_message(self) -> None:
        """Test command with stderr output."""
        self._run(
            Test(
                name="Stderr Test",
                command=sys.executable,
                subtests=(
                    SubTest(
                        name="error_message",
                        args=("-c", "import sys; sys.stderr.write('error\\n')"),
                        expected=Result(stdout="", stderr="error\n", returncode=0),
                    ),
                ),
            )
        )


class TestTestCLIConfiguration(unittest.TestCase):
    """Test TestCLI configuration behavior."""

    def test_override_get_configs(self) -> None:
        """Subclass should be able to override _get_configs()."""

        class CustomConfigTest(TestCLI):
            config_called = False

            def _get_configs(self) -> tuple[Configure, ...]:
                CustomConfigTest.config_called = True
                return super()._get_configs()

            def test_dummy(self) -> None:
                """Dummy test to satisfy unittest."""
                pass

        test = CustomConfigTest("test_dummy")
        test.setUp()

        self.assertTrue(CustomConfigTest.config_called)

        test.tearDown()

    def test_override_get_execute(self) -> None:
        """Subclass should be able to override _get_execute()."""

        class CustomExecuteTest(TestCLI):
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
