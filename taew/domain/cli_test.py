"""Domain types for CLI testing specifications.

This module defines pure data structures for specifying CLI test cases.
These types are framework-agnostic and can be used with unittest, pytest,
or other testing frameworks.

Builds on the CLI execution domain (taew.domain.cli) to define test
specifications with expected outcomes.

The naming convention aligns with unittest terminology:
- SubTest: Individual CLI invocation (maps to unittest.TestCase.subTest())
- Test: Collection of related CLI invocations (maps to test_* method)
"""

from typing import NamedTuple

from taew.domain.cli import Result


class SubTest(NamedTuple):
    """Specification for a single CLI command invocation test.

    Maps to unittest.TestCase.subTest() - represents one parameterized
    test case within a larger test scenario.

    Attributes:
        name: Descriptive name for this subtest (appears in test output)
        args: Command-line arguments (excluding executable path)
        expected: Expected execution result (stdout, stderr, returncode)

    Example:
        >>> from taew.domain.cli import Result
        >>> subtest = SubTest(
        ...     name="show version",
        ...     args=("--version",),
        ...     expected=Result(
        ...         stdout="myapp version 2.13.5\\n",
        ...         stderr="",
        ...         returncode=0
        ...     )
        ... )
    """

    name: str
    args: tuple[str, ...]
    expected: Result


class Test(NamedTuple):
    """Collection of related CLI subtests for a single test case.

    Maps to unittest.TestCase.test_*() method - represents a logical
    grouping of related CLI invocations (e.g., all help commands,
    all error scenarios).

    Attributes:
        name: Test case name (used to generate test_* method name)
        command: CLI executable path or command to test
        subtests: Tuple of CLI subtests to run
        setup_env: Optional environment variables for all subtests

    Example:
        >>> from taew.domain.cli import Result
        >>> test = Test(
        ...     name="help_and_version",
        ...     command="./bin/myapp",
        ...     subtests=(
        ...         SubTest(
        ...             name="help",
        ...             args=("--help",),
        ...             expected=Result("usage: myapp\\n", "", 0)
        ...         ),
        ...         SubTest(
        ...             name="version",
        ...             args=("--version",),
        ...             expected=Result("1.0.0\\n", "", 0)
        ...         ),
        ...     )
        ... )
    """

    name: str
    command: str
    subtests: tuple[SubTest, ...]
    setup_env: dict[str, str] | None = None
