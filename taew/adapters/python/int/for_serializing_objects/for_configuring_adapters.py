from dataclasses import dataclass

from ._common import SerdeBase
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)


@dataclass(eq=False, frozen=True)
class Configure(SerdeBase, ConfigureBase):
    def __post_init__(self) -> None:
        # Validate serializer configuration
        SerdeBase.__post_init__(self)
        # Point to this adapter package for port binding and root detection
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
