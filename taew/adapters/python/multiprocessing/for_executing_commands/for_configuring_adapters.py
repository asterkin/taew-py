"""Configurator for multiprocessing-based command execution adapter.

Provides configuration support for in-process execution by importing and
calling CLI entry point modules directly.
"""

from dataclasses import dataclass

from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for multiprocessing-based command execution.

    Enables in-process execution of CLI commands by importing their entry point
    modules and calling their main() functions. This provides full coverage
    measurement of the entire application including configuration code.

    Example:
        >>> from taew.adapters.python.multiprocessing.for_executing_commands.for_configuring_adapters import Configure
        >>> config = Configure()
        >>> ports = config()
    """

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
