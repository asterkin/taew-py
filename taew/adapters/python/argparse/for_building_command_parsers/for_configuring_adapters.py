from dataclasses import dataclass

from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from ._common import BuildBase


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase, BuildBase):
    """Configurator for argparse-based command parser builder adapter.

    Inherits _find and _bind from BuildBase.
    Inherits configuration infrastructure from ConfigureBase.
    """

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
