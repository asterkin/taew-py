from dataclasses import dataclass

from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)

from ._common import BuildBase


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase, BuildBase):
    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
        if not self._root:
            object.__setattr__(self, "_root", self._detect_root())

    def _collect_kwargs(self) -> dict[str, object]:
        return super()._collect_kwargs() | {"_variants": self._variants}
