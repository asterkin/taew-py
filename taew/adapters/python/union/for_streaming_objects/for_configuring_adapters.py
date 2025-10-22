from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from taew.domain.configuration import (
    PortConfiguration,
    PortConfigurationDict,
    InterfaceMapping,
    PortsMapping,
)
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.ports import for_streaming_objects as for_streaming_objects_port


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for the union streaming adapter."""

    _args: tuple[Any, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
        if not self._args:
            raise ValueError("_args must contain at least one variant type")

    def _nested_ports(self) -> PortsMapping:
        streamers_cfg = self._configure_streamers()
        choices_cfg: InterfaceMapping = {"choices": self._configure_choices()}

        return {
            for_streaming_objects_port: PortConfigurationDict(
                adapter=streamers_cfg | choices_cfg
            ),
        }

    def _configure_choices(self) -> PortConfiguration:
        from taew.adapters.python.choices.for_streaming_objects.for_configuring_adapters import (
            Configure as ConfigureChoices,
        )

        cfg = ConfigureChoices(_choices=self._args)
        return cfg()[for_streaming_objects_port]

    def _configure_streamers(self) -> InterfaceMapping:
        return dict[str | type, PortConfiguration](
            self._configure_streamer(arg) for arg in self._args
        )

    def _configure_streamer(self, arg: Any) -> tuple[type[object], PortConfiguration]:
        return self._configure_item(arg, for_streaming_objects_port)
