from dataclasses import dataclass
from typing import Any

from taew.domain.configuration import (
    PortConfiguration,
    PortsMapping,
)
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.ports import for_streaming_objects as for_streaming_objects_port


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for the record (heterogeneous) tuple streaming adapter."""

    _args: tuple[Any, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
        if not self._args:
            raise ValueError("Record tuple requires at least one type")

    def _nested_ports(self) -> PortsMapping:
        return {
            for_streaming_objects_port: tuple(
                self._configure_field(arg) for arg in self._args
            )
        }

    def _configure_field(self, arg: Any) -> PortConfiguration:
        _, config = self._configure_item(arg, for_streaming_objects_port)
        return config
