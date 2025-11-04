"""Subprocess-based command executor for running CLI applications.

Provides real command execution using Python's subprocess module,
capturing stdout, stderr, and exit codes.
"""

import subprocess
from dataclasses import dataclass

from taew.adapters.python.subprocess.for_executing_commands._common import ExecuteBase
from taew.domain.cli import CommandLine, Result


@dataclass(frozen=True, eq=False)
class Execute(ExecuteBase):
    """Subprocess-based command executor for real CLI execution.

    Inherits timeout and working directory configuration from ExecuteBase.
    Executes commands using subprocess.run() with proper output capture
    and error handling.

    The executor runs commands synchronously, blocking until completion
    or timeout. Environment variables from CommandLine are merged with
    the current process environment.

    Attributes:
        _timeout: Maximum execution time in seconds (from ExecuteBase)
        _cwd: Working directory for execution (from ExecuteBase)

    Example:
        >>> from taew.domain.cli import CommandLine
        >>> execute = Execute(_timeout=30.0, _cwd="/tmp")
        >>> cmd = CommandLine(command="echo", args=("hello",))
        >>> result = execute(cmd)
        >>> print(result.stdout)
        hello
    """

    def __call__(self, command_line: CommandLine) -> Result:
        """Execute a command using subprocess.run().

        Builds the full command from CommandLine specification, merges
        environment variables, and captures all output. Non-zero exit
        codes are returned as-is (not raised as exceptions).

        Args:
            command_line: Command specification to execute

        Returns:
            Result containing captured stdout, stderr, and exit code

        Raises:
            TimeoutError: If command execution exceeds configured timeout
            OSError: If command cannot be executed (not found, permission denied, etc.)
        """
        # Build full command list: [command, arg1, arg2, ...]
        full_command = [command_line.command, *command_line.args]

        # Merge environment variables if provided
        env = None
        if command_line.env:
            import os

            env = os.environ.copy()
            env.update(dict(command_line.env))

        try:
            # Execute command with subprocess.run()
            process = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                cwd=self._cwd,
                env=env,
                check=False,  # Don't raise exception on non-zero exit
            )

            return Result(
                stdout=process.stdout,
                stderr=process.stderr,
                returncode=process.returncode,
            )

        except subprocess.TimeoutExpired as e:
            # Convert subprocess.TimeoutExpired to standard TimeoutError
            raise TimeoutError(
                f"Command '{command_line.command}' timed out after {self._timeout}s"
            ) from e

        except (FileNotFoundError, PermissionError) as e:
            # Re-raise as OSError with helpful message
            raise OSError(f"Failed to execute '{command_line.command}': {e}") from e
