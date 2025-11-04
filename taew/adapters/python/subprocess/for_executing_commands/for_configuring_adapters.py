"""Configurator for subprocess-based command execution adapter.

Provides configuration support for subprocess execution with timeout
and working directory settings.
"""

from dataclasses import dataclass

from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.adapters.python.subprocess.for_executing_commands._common import ExecuteBase


@dataclass(eq=False, frozen=True)
class Configure(ExecuteBase, ConfigureBase):
    """Configurator for subprocess-based command execution.

    Inherits timeout and working directory configuration from ExecuteBase.
    Enables configuration of subprocess execution parameters for deterministic
    and controlled command execution.

    Attributes:
        _timeout: Maximum execution time in seconds (None for no timeout)
        _cwd: Working directory for command execution (None for current directory)

    Example:
        >>> from taew.adapters.python.subprocess.for_executing_commands.for_configuring_adapters import Configure
        >>> config = Configure(_timeout=30.0, _cwd="/tmp")
        >>> ports = config()
    """

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
