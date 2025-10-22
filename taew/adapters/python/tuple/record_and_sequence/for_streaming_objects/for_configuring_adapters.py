from dataclasses import dataclass
from typing import cast

from taew.domain.configuration import (
    PortConfigurationDict,
    PortsMapping,
)
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.ports import for_streaming_objects as for_streaming_objects_port


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for the mixed (hybrid) tuple streaming adapter."""

    _head: ConfigureProtocol = cast(ConfigureProtocol, None)
    _tail: ConfigureProtocol = cast(ConfigureProtocol, None)
    _head_length: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)

    def _collect_kwargs(self) -> dict[str, object]:
        return {"_length": self._head_length}

    def _nested_ports(self) -> PortsMapping:
        head_config = self._head()[for_streaming_objects_port]
        tail_config = self._tail()[for_streaming_objects_port]

        return {
            for_streaming_objects_port: PortConfigurationDict(
                adapter={
                    "head": head_config,
                    "tail": tail_config,
                }
            )
        }
