"""Domain types for CLI command execution.

This module defines the fundamental domain of CLI interactions:
- CommandLine: specification of what to execute
- Result: outcome of execution

These types are framework-agnostic and represent the CLI execution domain itself,
independent of any testing or subprocess implementation concerns.
"""

from typing import NamedTuple


class CommandLine(NamedTuple):
    """Specification of a CLI command to execute.

    Attributes:
        command: Executable path or command name
        args: Command-line arguments (excluding the command itself)
        env: Optional environment variables as tuple of (key, value) pairs

    Example:
        >>> cmd = CommandLine(
        ...     command="./bin/myapp",
        ...     args=("--version",),
        ...     env=(("DEBUG", "1"), ("PATH", "/usr/bin"))
        ... )
    """

    command: str
    args: tuple[str, ...] = ()
    env: tuple[tuple[str, str], ...] = ()


class Result(NamedTuple):
    """Result of CLI command execution.

    Captures the complete outcome of running a CLI command.

    Attributes:
        stdout: Standard output captured as string
        stderr: Standard error captured as string
        returncode: Exit code (0 typically indicates success)

    Example:
        >>> result = Result(
        ...     stdout="myapp version 2.13.5\\n",
        ...     stderr="",
        ...     returncode=0
        ... )
    """

    stdout: str
    stderr: str
    returncode: int
