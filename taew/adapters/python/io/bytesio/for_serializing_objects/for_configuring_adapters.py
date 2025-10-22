from dataclasses import dataclass
from typing import Any

from taew.domain.configuration import PortsMapping
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.ports import for_streaming_objects as for_streaming_objects_port


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for BytesIO-based serialization adapter.

    Bridges for_serializing_objects to for_streaming_objects by using
    the base class _configure_item to resolve the appropriate streaming adapter.
    """

    _type: Any = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)

    def _nested_ports(self) -> PortsMapping:
        """Return nested ports from the for_streaming_objects configurator.

        Uses base class _configure_item to resolve the streaming adapter
        for the specified type.
        """
        _, config = self._configure_item(self._type, for_streaming_objects_port)
        return {for_streaming_objects_port: config}
