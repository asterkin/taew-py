from dataclasses import dataclass

from taew.domain.configuration import PortsMapping
from taew.adapters.python.decimal.for_stringizing_objects.for_configuring_adapters import (
    Configure as ConfigureDecimalString,
)
from taew.adapters.python.str.for_streaming_objects.for_configuring_adapters import (
    Configure as ConfigureStr,
)
from taew.adapters.python.int.for_streaming_objects.for_configuring_adapters import (  # noqa: E501
    Configure as IntConfigure,
)


@dataclass(eq=False, frozen=True)
class Configure(ConfigureStr):
    _length_width: int = 1  # bytes

    def __post_init__(self) -> None:
        ConfigureStr.__post_init__(self)
        object.__setattr__(self, "_length", IntConfigure(_width=self._length_width))

    def _nested_ports(self) -> PortsMapping:
        ports = super()._nested_ports()
        decimal_string_port = ConfigureDecimalString()()
        ports.update(decimal_string_port)

        return ports
