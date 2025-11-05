"""Unittest-based testing utilities using Template Method pattern.

Provides base test classes for CLI testing that integrate with taew's
ports & adapters architecture while following the Template Method pattern.
"""

import textwrap
import unittest
from pathlib import Path

from taew.domain.cli_test import Test
from taew.domain.cli import CommandLine
from taew.utils.configure import configure
from taew.utils.test import normalize_timing_data
from taew.ports.for_executing_commands import Execute
from taew.ports.for_configuring_adapters import Configure
from taew.adapters.launch_time.for_binding_interfaces.bind import bind


class TestConfigure(unittest.TestCase):
    """Base class for configuration testing.

    Provides infrastructure configuration for testing. Subclasses can
    override _get_configs() to customize adapter configuration.

    Template Method:
        _get_configs(): Virtual - returns Configure instances (can override)
    """

    def _get_configs(self) -> tuple[Configure, ...]:
        """Return the Configure instances for infrastructure.

        Default implementation provides standard testing infrastructure:
        FindConfigurations, BuildConfigPortsMapping, and BrowseCodeTree.
        Subclasses can override to add or replace configurations.

        Returns:
            Tuple of Configure instances for infrastructure adapters

        Example:
            >>> def _get_configs(self) -> tuple[Configure, ...]:
            ...     return super()._get_configs() + (MyCustomConfig(),)
        """
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )
        from taew.adapters.python.dataclass.for_finding_configurations.for_configuring_adapters import (
            Configure as FindConfigurations,
        )
        from taew.adapters.python.typing.for_building_config_ports_mapping.for_configuring_adapters import (
            Configure as BuildConfigPortsMapping,
        )

        # TODO: overlap with cli.py - refactor to avoid duplication
        return (
            FindConfigurations(),
            BuildConfigPortsMapping(),
            BrowseCodeTree(_root_path=Path("./")),
        )


class TestCLI(TestConfigure):
    """Base class for CLI testing using Template Method pattern.

    Provides framework for testing CLI applications using the Test domain type.
    Subclasses define test methods that call _run(Test(...)) to execute CLI
    tests. Supports multiple test methods per class for granular test reporting.

    Template Methods:
        _get_configs(): Virtual - returns infrastructure Configure instances
        _get_execute(): Virtual - returns Execute Configure instance

    Example:
        >>> class TestMyApp(TestCLI):
        ...     def test_version(self) -> None:
        ...         self._run(Test(
        ...             name="version",
        ...             command="./bin/myapp",
        ...             subtests=(
        ...                 SubTest("v", ("--version",), Result("v1.0\\n", "", 0)),
        ...             )
        ...         ))
        ...
        ...     def test_help(self) -> None:
        ...         self._run(Test(
        ...             name="help",
        ...             command="./bin/myapp",
        ...             subtests=(
        ...                 SubTest("h", ("--help",), Result("usage\\n", "", 0)),
        ...             )
        ...         ))
    """

    def _get_configs(self) -> tuple[Configure, ...]:
        """Return Configure instances for test execution.

        Combines infrastructure configs from TestConfigure with Execute
        configuration from _get_execute(). Override to customize.

        Returns:
            Tuple of Configure instances including Execute adapter
        """
        return super()._get_configs() + (self._get_execute(),)

    def _get_execute(self) -> Configure:
        """Return Execute configuration for test execution.

        Default uses subprocess for real command execution. Override to use
        RAM adapter for mocked execution or to customize timeout/cwd.

        Returns:
            Configure instance for Execute adapter

        Example (RAM adapter override):
            >>> def _get_execute(self) -> Configure:
            ...     from taew.adapters.python.ram.for_executing_commands.for_configuring_adapters import (
            ...         Configure as RAMExecute,
            ...     )
            ...     return RAMExecute(_commands={
            ...         CommandLine("./bin/app", ("--version",)): Result("1.0\\n", "", 0)
            ...     })
        """
        from taew.adapters.python.subprocess.for_executing_commands.for_configuring_adapters import (
            Configure as SubprocessExecute,
        )

        return SubprocessExecute()

    def setUp(self) -> None:
        """Setup test execution infrastructure.

        Configures ports and binds Execute protocol. Called automatically
        before each test method.
        """
        ports = configure(*self._get_configs())
        self._execute = bind(Execute, ports)

    def tearDown(self) -> None:
        """Clean up after test execution.

        Clears Root cache for test isolation. Called automatically after
        each test method.
        """
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

    def _run(self, test: Test) -> None:
        """Execute CLI test specification.

        Runs each SubTest in the Test specification:
        1. Builds CommandLine from test.command + subtest.args + test.setup_env
        2. Executes command using bound Execute adapter
        3. Normalizes timing data in actual stdout/stderr with normalize_timing_data()
        4. Dedents and strips expected stdout/stderr for readability
        5. Strips actual stdout/stderr to match
        6. Asserts stdout, stderr, and returncode match expectations

        Args:
            test: Test specification with command, subtests, and optional setup_env

        Uses unittest.subTest() to report each SubTest individually.

        Note:
            Expected output is automatically dedented and stripped, allowing
            readable multiline strings. Actual output is normalized for timing
            data and stripped to match.

        Example:
            >>> def test_my_command(self) -> None:
            ...     self._run(Test(
            ...         name="my test",
            ...         command="echo",
            ...         subtests=(
            ...             SubTest("hello", ("hello",), Result("hello", "", 0)),
            ...         )
            ...     ))
        """
        for subtest in test.subtests:
            with self.subTest(name=subtest.name):
                # Build environment tuples if setup_env is provided
                env_tuples = tuple(test.setup_env.items()) if test.setup_env else ()

                # Build command line
                cmd = CommandLine(
                    command=test.command,
                    args=subtest.args,
                    env=env_tuples,
                )

                # Execute command
                result = self._execute(cmd)

                # Normalize timing data in actual output only
                actual_stdout = normalize_timing_data(result.stdout)
                actual_stderr = normalize_timing_data(result.stderr)

                # Prepare expected output: dedent and strip for readability
                expected_stdout = textwrap.dedent(subtest.expected.stdout).strip()
                expected_stderr = textwrap.dedent(subtest.expected.stderr).strip()

                # Strip actual output to match (since expected is stripped)
                actual_stdout = actual_stdout.strip()
                actual_stderr = actual_stderr.strip()

                # Assert results
                self.assertEqual(
                    actual_stdout,
                    expected_stdout,
                    f"stdout mismatch for subtest '{subtest.name}'",
                )
                self.assertEqual(
                    actual_stderr,
                    expected_stderr,
                    f"stderr mismatch for subtest '{subtest.name}'",
                )
                self.assertEqual(
                    result.returncode,
                    subtest.expected.returncode,
                    f"returncode mismatch for subtest '{subtest.name}'",
                )
