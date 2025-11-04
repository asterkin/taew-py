"""Configurator for RAM-based command execution adapter.

Provides configuration support for in-memory command execution with
predefined command-result mappings.
"""

from dataclasses import dataclass, field

from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.domain.cli import CommandLine, Result


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for RAM-based command execution.

    Enables configuration of predefined command-result mappings for
    deterministic testing without subprocess execution.

    Attributes:
        _ports: Port package name
        _root_marker: Marker path for adapter discovery
        _commands: Mapping of CommandLine to predefined Result
        _calls: Mutable list for recording execution calls

    Example:
        >>> from taew.domain.cli import CommandLine, Result
        >>> config = Configure(
        ...     _commands={
        ...         CommandLine("./bin/app", ("--version",)): Result("1.0.0\\n", "", 0),
        ...     }
        ... )
    """

    _ports: str = field(kw_only=True, default="ports")
    _root_marker: str = field(kw_only=True, default="/adapters")
    _commands: dict[CommandLine, Result] = field(kw_only=True, default_factory=dict)
    _calls: list[CommandLine] = field(kw_only=True, default_factory=list)

    def _collect_kwargs(self) -> dict[str, object]:
        """Collects keyword arguments for configuring the adapter.

        Returns:
            dict[str, object]: Dictionary with _commands and _calls parameters
        """
        return {"kwargs": {"_commands": self._commands, "_calls": self._calls}}
