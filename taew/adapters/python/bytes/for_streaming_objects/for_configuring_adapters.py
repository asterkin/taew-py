from dataclasses import dataclass

from taew.domain.configuration import PortsMapping
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Bytes streamer configurator combining length streaming and optional serde.

    - _length: Configure for a for_streaming_objects adapter (e.g., int streamer).
               Optional; defaults to 2-byte unsigned big-endian int length.
    - _serde:  Optional Configure for a for_serializing_objects adapter (e.g., str serde)
    """

    _length: ConfigureProtocol | None = None
    _serde: ConfigureProtocol | None = None

    def __post_init__(self) -> None:
        # Auto-detect package and file for base configurator
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
        # Lazily default _length to 2-byte unsigned big-endian int streamer
        if self._length is None:
            from taew.adapters.python.int.for_streaming_objects.for_configuring_adapters import (  # noqa: E501
                Configure as IntConfigure,
            )

            object.__setattr__(self, "_length", IntConfigure(_width=2))

    def _collect_kwargs(self) -> dict[str, object]:
        # Top-level bytes streamer has no constructor kwargs; its dependencies
        # are injected via nested ports (_length/_serde)
        return {}

    def _nested_ports(self) -> PortsMapping:
        ports: PortsMapping = {}
        # Inject length streaming port configuration (length is ensured in __post_init__)
        ports.update(self._length())  # type: ignore[misc]
        # Inject optional serializer/deserializer port configuration
        if self._serde is not None:
            ports.update(self._serde())
        return ports
