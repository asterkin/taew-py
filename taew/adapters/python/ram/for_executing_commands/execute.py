"""RAM-based command executor for testing CLI applications.

Provides in-memory command execution by matching CommandLine specifications
to predefined Results. Enables deterministic testing without subprocess
overhead or external dependencies.
"""

from taew.adapters.python.ram.for_executing_commands._common import ExecuteBase
from taew.domain.cli import CommandLine, Result


class Execute(ExecuteBase):
    """RAM-based command executor that returns predefined results.

    Inherits from ExecuteBase to provide standard command-result mapping
    and call recording infrastructure. Implements simple lookup-based
    execution strategy.

    The matching is based on the full CommandLine specification (command,
    args, env), enabling precise test scenarios. Uses list lookup instead of
    dict to handle unhashable env dictionaries.

    Attributes:
        _commands: List of (CommandLine, Result) pairs defining responses
        _calls: List recording all execute() invocations for verification

    Example:
        >>> from taew.domain.cli import CommandLine, Result
        >>> execute = Execute(
        ...     _commands=[
        ...         (CommandLine("./bin/app", ("--version",)), Result("1.0.0\\n", "", 0)),
        ...         (CommandLine("./bin/app", ("--help",)), Result("usage:\\n", "", 0)),
        ...     ],
        ...     _calls=[],
        ... )
        >>> result = execute(CommandLine("./bin/app", ("--version",)))
        >>> assert result.stdout == "1.0.0\\n"
        >>> assert len(execute._calls) == 1
    """

    def __call__(self, command_line: CommandLine) -> Result:
        """Execute a command by looking up its predefined result.

        Args:
            command_line: Command specification to execute

        Returns:
            Predefined Result for the given CommandLine

        Raises:
            LookupError: If no predefined result exists for this CommandLine
        """
        self._calls.append(command_line)
        return self._lookup(command_line)
