"""RAM-based command executor for testing CLI applications.

Provides in-memory command execution by matching CommandLine specifications
to predefined Results. Enables deterministic testing without subprocess
overhead or external dependencies.
"""

from dataclasses import dataclass, field

from taew.adapters.python.ram.for_executing_commands._common import ExecuteBase
from taew.domain.cli import CommandLine, Result


@dataclass(frozen=True, eq=False)
class Execute(ExecuteBase):
    """RAM-based command executor that returns predefined results.

    Inherits from ExecuteBase for command-result mapping configuration.
    Implements dict-based lookup execution strategy with call tracking.

    The matching is based on the full CommandLine specification (command,
    args, env), enabling precise test scenarios. CommandLine is hashable
    because env is stored as tuple of tuples.

    Attributes:
        _commands: Mapping of CommandLine to predefined Result (from ExecuteBase)
        _calls: List recording all execute() invocations for verification

    Example:
        >>> from taew.domain.cli import CommandLine, Result
        >>> execute = Execute(
        ...     _commands={
        ...         CommandLine("./bin/app", ("--version",)): Result("1.0.0\\n", "", 0),
        ...         CommandLine("./bin/app", ("--help",)): Result("usage:\\n", "", 0),
        ...     },
        ...     _calls=[],
        ... )
        >>> result = execute(CommandLine("./bin/app", ("--version",)))
        >>> assert result.stdout == "1.0.0\\n"
        >>> assert len(execute._calls) == 1
    """

    _calls: list[CommandLine] = field(default_factory=list[CommandLine])

    def __call__(self, command_line: CommandLine) -> Result:
        """Execute a command by looking up its predefined result.

        Args:
            command_line: Command specification to execute

        Returns:
            Predefined Result for the given CommandLine

        Raises:
            KeyError: If no predefined result exists for this CommandLine
        """
        self._calls.append(command_line)
        return self._lookup(command_line)

    def _lookup(self, command_line: CommandLine) -> Result:
        """Look up a predefined result for a command.

        Args:
            command_line: Command specification to look up

        Returns:
            Predefined Result for the given CommandLine

        Raises:
            KeyError: If no predefined result exists for this CommandLine
        """
        return self._commands[command_line]
