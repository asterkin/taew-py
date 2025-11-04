"""RAM-based command executor for testing CLI applications.

Provides in-memory command execution by matching CommandLine specifications
to predefined Results. Enables deterministic testing without subprocess
overhead or external dependencies.
"""

from dataclasses import dataclass, field

from taew.domain.cli import CommandLine, Result


@dataclass(frozen=True, eq=False)
class Execute:
    """RAM-based command executor that returns predefined results.

    Stores list of (CommandLine, Result) pairs and returns the first matching
    result. Records all execution calls for verification.

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

    _commands: list[tuple[CommandLine, Result]]
    _calls: list[CommandLine] = field(default_factory=list)

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
        for cmd, result in self._commands:
            if cmd == command_line:
                return result
        raise LookupError(
            f"No predefined result for command: {command_line.command} "
            f"with args: {command_line.args}"
        )
