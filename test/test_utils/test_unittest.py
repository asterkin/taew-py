"""Tests for unittest-based testing utilities."""

import sys
import unittest

from taew.domain.cli import CommandLine, Result
from taew.domain.cli_test import SubTest, Test
from taew.domain.configuration import PortsMapping
from taew.utils.unittest import TestCLI


class TestTestCLIWithSubprocess(TestCLI):
    """Concrete test using default subprocess configuration."""

    def _get_test(self) -> Test:
        """Define test using real subprocess commands."""
        return Test(
            name="Echo Tests",
            command="echo",
            subtests=(
                SubTest(
                    name="simple",
                    args=("hello",),
                    expected=Result(stdout="hello\n", stderr="", returncode=0),
                ),
                SubTest(
                    name="multiple_words",
                    args=("hello", "world"),
                    expected=Result(stdout="hello world\n", stderr="", returncode=0),
                ),
            ),
        )


class TestTestCLIWithRAM(TestCLI):
    """Concrete test using RAM adapter override."""

    def _get_test(self) -> Test:
        """Define test specification."""
        return Test(
            name="RAM Tests",
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

    def _configure(self) -> PortsMapping:
        """Override to use RAM adapter with predefined commands."""
        from pathlib import Path

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )
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

        ports = RAMExecute(_commands=commands)()
        ports.update(BrowseCodeTree(_root_path=Path("./"))())
        return ports


class TestTestCLIWithEnv(TestCLI):
    """Test environment variable handling."""

    def _get_test(self) -> Test:
        """Define test with environment variables."""
        return Test(
            name="Env Tests",
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


class TestTestCLIWithNonZeroExit(TestCLI):
    """Test handling of non-zero exit codes."""

    def _get_test(self) -> Test:
        """Define test expecting non-zero exit."""
        return Test(
            name="Exit Code Tests",
            command=sys.executable,
            subtests=(
                SubTest(
                    name="exit_42",
                    args=("-c", "exit(42)"),
                    expected=Result(stdout="", stderr="", returncode=42),
                ),
            ),
        )


class TestTestCLIWithStderr(TestCLI):
    """Test stderr capture."""

    def _get_test(self) -> Test:
        """Define test expecting stderr output."""
        return Test(
            name="Stderr Tests",
            command=sys.executable,
            subtests=(
                SubTest(
                    name="error_message",
                    args=("-c", "import sys; sys.stderr.write('error\\n')"),
                    expected=Result(stdout="", stderr="error\n", returncode=0),
                ),
            ),
        )


class TestTestCLIAbstractMethod(unittest.TestCase):
    """Test that TestCLI enforces abstract method implementation."""

    def test_cannot_call_test_cli_without_get_test(self) -> None:
        """TestCLI.test_cli() should fail when _get_test is not implemented."""

        class IncompleteTest(TestCLI):  # type: ignore[misc]
            pass  # Intentionally not implementing _get_test

        # Can instantiate, but calling test_cli() should raise
        test = IncompleteTest("test_cli")

        # When setUp is called, it won't fail (no _get_test call yet)
        # But test_cli() should fail when it tries to call _get_test()
        with self.assertRaises((TypeError, AttributeError)) as cm:
            test.test_cli()

        # Should complain about abstract method or missing implementation
        # (Either TypeError for abstract or AttributeError for None.subtests)
        exception_str = str(cm.exception)
        self.assertTrue(
            "abstract" in exception_str.lower()
            or "subtests" in exception_str.lower()
            or "NoneType" in exception_str,
            f"Expected error about missing _get_test, got: {exception_str}",
        )


class TestTestCLIConfiguration(unittest.TestCase):
    """Test TestCLI configuration behavior."""

    def test_default_configuration_uses_subprocess(self) -> None:
        """Default _configure() should use subprocess adapter."""

        class MinimalTest(TestCLI):
            def _get_test(self) -> Test:
                return Test(
                    name="test",
                    command="echo",
                    subtests=(SubTest("x", ("y",), Result("y\n", "", 0)),),
                )

        test = MinimalTest()
        test.setUp()

        # Verify we got an Execute instance (we can't easily check the type)
        self.assertIsNotNone(test.execute)

        test.tearDown()

    def test_override_configuration(self) -> None:
        """Subclass should be able to override _configure()."""

        class CustomConfigTest(TestCLI):
            config_called = False

            def _get_test(self) -> Test:
                return Test(
                    name="test",
                    command="./bin/app",
                    subtests=(SubTest("x", (), Result("", "", 0)),),
                )

            def _configure(self) -> PortsMapping:
                CustomConfigTest.config_called = True
                return super()._configure()

        test = CustomConfigTest()
        test.setUp()

        self.assertTrue(CustomConfigTest.config_called)

        test.tearDown()


if __name__ == "__main__":
    unittest.main()
