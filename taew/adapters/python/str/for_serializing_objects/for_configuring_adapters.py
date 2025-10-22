from typing import Optional
from dataclasses import dataclass

from ._common import SerdeBase
from taew.domain.configuration import PortsMapping
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


@dataclass(eq=False, frozen=True)
class Configure(SerdeBase, ConfigureBase):
    _configure: Optional[ConfigureProtocol] = None

    def __post_init__(self) -> None:
        # Validate SerdeBase configuration
        SerdeBase.__post_init__(self)
        # Auto-detect package and file for base configurator
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)

    def _collect_kwargs(self) -> dict[str, object]:
        """Return encoding parameters for adapter initialization."""
        return {
            key: value
            for key, value in super()._collect_kwargs().items()
            if key != "_configure"
        }

    def _nested_ports(self) -> PortsMapping:
        """Return nested ports from the serializer configurator.

        If _configure is provided, resolves the nested serializer configuration.
        If _configure is None, uses identity serialization (no nested ports).
        """
        return {} if self._configure is None else self._configure()
