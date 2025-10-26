from typing import Any
from dataclasses import dataclass

from taew.adapters.python.json.for_stringizing_objects.for_configuring_adapters import (
    Configure as ConfigureJSON,
)


@dataclass(eq=False, frozen=True, kw_only=True)
class Configure(ConfigureJSON):
    """Dataclass-based configurator for named tuples."""

    _args: tuple[Any, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "_type", self._args[0] if self._args else None)
        return super().__post_init__()
