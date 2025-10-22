from dataclasses import dataclass

from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as BaseConfigure,
)


@dataclass(eq=False, frozen=True)
class Configure(BaseConfigure):
    _alpha: int = 1
    _name: str = "x"
