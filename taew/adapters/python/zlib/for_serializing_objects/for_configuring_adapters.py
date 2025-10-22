from typing import Optional
from dataclasses import dataclass

from taew.domain.configuration import PortsMapping
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for zlib-based serialization adapter.

    Composes with nested serializers via _configure parameter, or uses
    identity serialization (bytes passthrough) when _configure is None.
    """

    _configure: Optional[ConfigureProtocol] = None
    _level: int = 6

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)

    def _collect_kwargs(self) -> dict[str, object]:
        """Return compression parameters for adapter initialization."""
        return {"_level": self._level}

    def _nested_ports(self) -> PortsMapping:
        """Return nested ports from the serializer configurator.

        If _configure is provided, resolves the nested serializer configuration.
        If _configure is None, uses identity serialization (no nested ports).
        """
        return {} if self._configure is None else self._configure()
