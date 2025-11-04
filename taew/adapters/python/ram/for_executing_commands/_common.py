"""Common base class for command execution adapters.

Provides shared state management for tracking command executions
and predefined command-result mappings.
"""

from dataclasses import dataclass, field

from taew.domain.cli import CommandLine, Result


@dataclass(frozen=True, eq=False)
class ExecuteBase:
    """Base class for command execution adapters.

    Provides common infrastructure for storing predefined command-result
    mappings and recording execution calls. Subclasses implement the
    execution strategy.

    Attributes:
        _commands: List of (CommandLine, Result) pairs defining responses
        _calls: List recording all execute() invocations for verification

    Example:
        >>> from taew.domain.cli import CommandLine, Result
        >>> class MyExecutor(ExecuteBase):
        ...     def __call__(self, command_line: CommandLine) -> Result:
        ...         self._calls.append(command_line)
        ...         return self._lookup(command_line)
    """

    _commands: list[tuple[CommandLine, Result]]
    _calls: list[CommandLine] = field(default_factory=list)

    def _lookup(self, command_line: CommandLine) -> Result:
        """Look up a predefined result for a command.

        Args:
            command_line: Command specification to look up

        Returns:
            Predefined Result for the given CommandLine

        Raises:
            LookupError: If no predefined result exists for this CommandLine
        """
        for cmd, result in self._commands:
            if cmd == command_line:
                return result
        raise LookupError(
            f"No predefined result for command: {command_line.command} "
            f"with args: {command_line.args}"
        )
