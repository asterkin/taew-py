"""Port for executing CLI commands.

This port defines the interface for executing command-line applications
and capturing their output. Different adapters can provide different
execution strategies (subprocess, Docker, SSH, etc.) without changing
the code that uses this port.

The execution abstraction enables:
- Testing CLI applications with different execution environments
- Switching between local and remote execution via configuration
- Isolating test execution in containers or sandboxes
- Mocking command execution for testing the test framework itself
"""

from typing import Protocol

from taew.domain.cli import CommandLine, Result


class Execute(Protocol):
    """Execute a CLI command and return its result.

    This protocol defines the interface for running command-line applications
    and capturing their output, error streams, and exit codes.

    The command execution is synchronous - the call blocks until the command
    completes or times out.

    Example:
        >>> from taew.domain.cli import CommandLine, Result
        >>> execute: Execute = get_executor()  # From configuration
        >>> cmd = CommandLine(
        ...     command="./bin/myapp",
        ...     args=("--version",),
        ... )
        >>> result: Result = execute(cmd)
        >>> print(result.stdout)
        myapp version 2.13.5
    """

    def __call__(self, command_line: CommandLine) -> Result:
        """Execute a command line and return the result.

        Args:
            command_line: Command specification (command, args, env)

        Returns:
            Result containing stdout, stderr, and returncode

        Raises:
            TimeoutError: If command execution exceeds configured timeout
            OSError: If command cannot be executed (not found, permission denied, etc.)
        """
        ...
