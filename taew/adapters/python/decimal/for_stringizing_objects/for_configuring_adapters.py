from dataclasses import dataclass

from ._common import DecimalBase
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)


@dataclass(eq=False, frozen=True)
class Configure(DecimalBase, ConfigureBase):
    """Dataclass-based configurator for decimal stringizing adapters.

    Inherits `_context` from DecimalBase so it is included in kwargs
    for the concrete Dumps/Loads adapters. No nested ports required.
    """

    def __post_init__(self) -> None:
        # Point to this package for adapter resolution and root detection
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
