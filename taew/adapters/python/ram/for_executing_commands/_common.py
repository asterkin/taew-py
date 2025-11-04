"""Common base class for command execution adapters.

Provides shared configuration for command execution adapters.
"""

from dataclasses import dataclass

from taew.domain.cli import CommandLine, Result


@dataclass(frozen=True, eq=False)
class ExecuteBase:
    """Base class for command execution adapters.

    Provides common configuration infrastructure for storing predefined
    command-result mappings. Subclasses implement the execution strategy
    and call tracking.

    Attributes:
        _commands: Mapping of CommandLine to predefined Result

    Example:
        >>> from taew.domain.cli import CommandLine, Result
        >>> class MyExecutor(ExecuteBase):
        ...     def __call__(self, command_line: CommandLine) -> Result:
        ...         return self._commands[command_line]
    """

    _commands: dict[CommandLine, Result]
