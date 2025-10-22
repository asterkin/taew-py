from collections.abc import Callable, Collection
from dataclasses import dataclass
from typing import Any

from taew.domain.configuration import (
    InterfaceMapping,
    PortConfiguration,
    PortConfigurationDict,
    PortsMapping,
)
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.ports import for_streaming_objects as for_streaming_objects_port
from taew.ports.for_streaming_objects import SequenceContext


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Generic sequence configurator wiring length framing and item streamer."""

    _args: tuple[Any, ...] = ()
    _from: Callable[[object], Collection[object]] | None = None
    _target: Callable[[int], SequenceContext] | None = None
    _length_width: int = 2  # bytes for length prefix

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
        if len(self._args) != 1:
            raise ValueError("Sequence configurator expects exactly one item argument")

    def _collect_kwargs(self) -> dict[str, object]:
        return {"_from": self._from, "_target": self._target}

    def _nested_ports(self) -> PortsMapping:
        length_cfg = self._configure_length()
        item_cfg = self._configure_item_for_sequence()

        adapter_map: InterfaceMapping = {
            "length": length_cfg,
            "item": item_cfg,
        }

        return {for_streaming_objects_port: PortConfigurationDict(adapter=adapter_map)}

    def _configure_length(self) -> PortConfiguration:
        from taew.adapters.python.int.for_streaming_objects.for_configuring_adapters import (
            Configure as ConfigureIntStream,
        )

        cfg = ConfigureIntStream(_width=self._length_width)
        ports = cfg()
        return ports[for_streaming_objects_port]

    def _configure_item_for_sequence(self) -> PortConfiguration:
        _, config = self._configure_item(self._args[0], for_streaming_objects_port)
        return config
