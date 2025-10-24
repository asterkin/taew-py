from types import ModuleType
from typing import Any, Protocol

from taew.domain.configuration import PortsMapping


class Build(Protocol):
    """Construct the PortsMapping required to bind a configurator for a type."""

    def __call__(
        self,
        arg: Any,
        port: ModuleType,
    ) -> tuple[type[object], PortsMapping]: ...
