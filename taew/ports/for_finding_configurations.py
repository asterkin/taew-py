from types import ModuleType
from typing import Any, Protocol

from taew.domain.configuration import PortConfiguration


class Find(Protocol):
    """Locate a port configuration for a given annotated argument type.

    Implementations inspect ``arg`` (which may be a class, typing annotation,
    or other metadata object) and return both the base type used for mapping keys
    and the resolved ``PortConfiguration`` for the requested ``port``.
    """

    def __call__(
        self,
        arg: Any,
        port: ModuleType,
    ) -> tuple[type[object], PortConfiguration]: ...
