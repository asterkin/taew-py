"""Common base class for subprocess command execution adapters.

Provides shared configuration for subprocess-based command execution.
"""

from dataclasses import dataclass


@dataclass(frozen=True, eq=False)
class ExecuteBase:
    """Base class for subprocess command execution adapters.

    Provides common configuration infrastructure for subprocess execution,
    including timeout settings and working directory configuration.

    Attributes:
        _timeout: Maximum execution time in seconds (None for no timeout)
        _cwd: Working directory for command execution (None for current directory)

    Example:
        >>> from taew.adapters.python.subprocess.for_executing_commands._common import ExecuteBase
        >>> class MyExecutor(ExecuteBase):
        ...     def __call__(self, command_line):
        ...         # Execute with self._timeout and self._cwd
        ...         pass
    """

    _timeout: float | None = None
    _cwd: str | None = None
