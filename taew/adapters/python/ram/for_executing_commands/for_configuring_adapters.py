"""Configurator for RAM-based command execution adapter.

Provides configuration support for in-memory command execution with
predefined command-result mappings.
"""

from dataclasses import dataclass

from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.adapters.python.ram.for_executing_commands._common import ExecuteBase


@dataclass(eq=False, frozen=True)
class Configure(ExecuteBase, ConfigureBase):
    """Configurator for RAM-based command execution.

    Inherits command mapping configuration from ExecuteBase.
    Enables configuration of predefined command-result mappings for
    deterministic testing without subprocess execution.

    Example:
        >>> from taew.domain.cli import CommandLine, Result
        >>> config = Configure(
        ...     _commands={
        ...         CommandLine("./bin/app", ("--version",)): Result("1.0.0\\n", "", 0),
        ...     }
        ... )
    """

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
