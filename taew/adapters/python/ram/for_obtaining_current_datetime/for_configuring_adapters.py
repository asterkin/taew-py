"""Configurator for RAM-based current datetime adapter."""

from dataclasses import dataclass

from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for RAM-based current datetime adapter.

    Example:
        from taew.adapters.python.ram.for_obtaining_current_datetime.for_configuring_adapters import Configure

        ports = Configure()()
    """

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
