from dataclasses import dataclass

from taew.domain.configuration import PortsMapping
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.adapters.python.float.for_streaming_objects.for_configuring_adapters import (
    Configure as ConfigureFloatStream,
)


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configure datetime streaming via nested float streamer.

    Defaults to float64 (8 bytes), big-endian UNIX epoch seconds.
    """

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)

    def _nested_ports(self) -> PortsMapping:
        # Provide float streamer as nested port (8-byte, big-endian)
        return ConfigureFloatStream(_width=8, _byte_order="big")()
