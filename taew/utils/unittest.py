"""Unittest-based testing utilities using Template Method pattern.

Provides base test classes for CLI testing that integrate with taew's
ports & adapters architecture while following the Template Method pattern.
"""

import unittest
from abc import abstractmethod
from pathlib import Path

from taew.adapters.launch_time.for_binding_interfaces.bind import bind
from taew.domain.cli import CommandLine
from taew.domain.cli_test import Test
from taew.domain.configuration import PortsMapping
from taew.ports.for_executing_commands import Execute
from taew.utils.test import normalize_timing_data


class TestCLI(unittest.TestCase):
    """Base class for CLI testing using Template Method pattern.

    Provides a framework for testing CLI applications by defining test
    specifications using the Test domain type. Subclasses implement
    _get_test() to define their test scenarios, and can optionally
    override _configure() to customize execution infrastructure.

    The class executes each SubTest using unittest's subTest feature,
    automatically normalizing timing data in output for deterministic
    assertions.

    Template Methods:
        _get_test(): Abstract - returns Test specification (MUST implement)
        _configure(): Virtual - returns PortsMapping (can override)

    Example:
        >>> class TestMyApp(TestCLI):
        ...     def _get_test(self) -> Test:
        ...         return Test(
        ...             name="MyApp Tests",
        ...             command="./bin/myapp",
        ...             subtests=(
        ...                 SubTest("version", ("--version",), Result("v1.0\\n", "", 0)),
        ...             )
        ...         )
    """

    execute: Execute

    @abstractmethod
    def _get_test(self) -> Test:
        """Return the Test specification to execute.

        Subclasses must implement this method to define their CLI test
        scenarios using the Test domain type from taew.domain.cli_test.

        Returns:
            Test specification with command, subtests, and optional setup

        Example:
            >>> def _get_test(self) -> Test:
            ...     return Test(
            ...         name="Calculator CLI",
            ...         command="./bin/calc",
            ...         subtests=(
            ...             SubTest("add", ("2", "3"), Result("5\\n", "", 0)),
            ...             SubTest("multiply", ("4", "5"), Result("20\\n", "", 0)),
            ...         )
            ...     )
        """
        ...

    def _configure(self) -> PortsMapping:
        """Configure ports for test execution.

        Default implementation uses subprocess execution for running real
        CLI commands. Subclasses can override this to use RAM adapter for
        mocked execution or to customize timeout/working directory settings.

        Returns:
            PortsMapping with Execute and BrowseCodeTree configurations

        Example (override for RAM adapter):
            >>> def _configure(self) -> PortsMapping:
            ...     from taew.adapters.python.ram.for_executing_commands.for_configuring_adapters import Configure
            ...     commands = {
            ...         CommandLine("./bin/app", ("--version",)): Result("1.0\\n", "", 0)
            ...     }
            ...     ports = Configure(_commands=commands)()
            ...     # Add browsing config...
            ...     return ports
        """
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )
        from taew.adapters.python.subprocess.for_executing_commands.for_configuring_adapters import (
            Configure as SubprocessExecute,
        )

        # Default: subprocess execution with no timeout
        ports = SubprocessExecute()()
        ports.update(BrowseCodeTree(_root_path=Path("./"))())
        return ports

    def setUp(self) -> None:
        """Setup test execution infrastructure.

        Configures ports and binds the Execute protocol for use in test_cli().
        Called automatically before each test method.
        """
        ports = self._configure()
        self.execute = bind(Execute, ports)

    def tearDown(self) -> None:
        """Clean up after test execution.

        Clears the Root cache to ensure test isolation. Called automatically
        after each test method.
        """
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

    def test_cli(self) -> None:
        """Execute the CLI test specification.

        Runs each SubTest defined in the Test specification returned by
        _get_test(). For each SubTest:
        1. Builds CommandLine from test.command + subtest.args + test.setup_env
        2. Executes command using bound Execute adapter
        3. Normalizes stdout using normalize_timing_data()
        4. Asserts stdout, stderr, and returncode match expectations

        Uses unittest.subTest() to report results for each SubTest individually.
        """
        test = self._get_test()

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
                result = self.execute(cmd)

                # Normalize timing data in both actual and expected output
                actual_stdout = normalize_timing_data(result.stdout)
                expected_stdout = normalize_timing_data(subtest.expected.stdout)

                # Assert results
                self.assertEqual(
                    actual_stdout,
                    expected_stdout,
                    f"stdout mismatch for subtest '{subtest.name}'",
                )
                self.assertEqual(
                    result.stderr,
                    subtest.expected.stderr,
                    f"stderr mismatch for subtest '{subtest.name}'",
                )
                self.assertEqual(
                    result.returncode,
                    subtest.expected.returncode,
                    f"returncode mismatch for subtest '{subtest.name}'",
                )
