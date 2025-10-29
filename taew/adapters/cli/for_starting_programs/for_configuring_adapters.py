from dataclasses import dataclass

from taew.domain.configuration import PortsMapping
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)


@dataclass(eq=False, frozen=True, kw_only=True)
class Configure(ConfigureBase):
    _ports_mapping: PortsMapping
    _cli_package: str = "adapters.cli"

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
