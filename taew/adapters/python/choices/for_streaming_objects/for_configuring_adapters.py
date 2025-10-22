from dataclasses import dataclass
from taew.domain.configuration import PortsMapping
from taew.utils.int import unsigned_int_bytes_needed
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.adapters.python.int.for_streaming_objects.for_configuring_adapters import (
    Configure as ConfigureIntStream,
)

from ._common import ChoicesBase


@dataclass(eq=False, frozen=True)
class Configure(ChoicesBase, ConfigureBase):
    def __post_init__(self) -> None:
        ChoicesBase.__post_init__(self)
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)

    def _nested_ports(self) -> PortsMapping:
        int_port = ConfigureIntStream(
            _width=unsigned_int_bytes_needed(len(self._choices) - 1)
        )
        return int_port()
