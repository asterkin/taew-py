from dataclasses import dataclass

from ._common import IntStreamBase
from taew.domain.configuration import PortsMapping
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)


@dataclass(eq=False, frozen=True)
class ConfigureFixedLength(IntStreamBase, ConfigureBase):
    def __post_init__(self) -> None:
        # Validate IntStreamBase configuration
        IntStreamBase.__post_init__(self)
        # Auto-detect package and file for base configurator
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)


@dataclass(eq=False, frozen=True)
class Configure(IntStreamBase):
    def __post_init__(self) -> None:
        pass  # suppress base class validation

    def __call__(self) -> PortsMapping:
        cfg = (
            self._get_fixed_length_config(self._width, self._signed)
            if self._width
            else self._get_variable_length_config()
        )
        return cfg()

    def _get_fixed_length_config(self, width: int, signed: bool) -> ConfigureProtocol:
        return ConfigureFixedLength(
            _width=width,
            _byte_order=self._byte_order,
            _signed=signed,
        )

    def _get_variable_length_config(self) -> ConfigureProtocol:
        from taew.adapters.python.bytes.for_streaming_objects.for_configuring_adapters import (
            Configure as BytesConfigure,
        )
        from taew.adapters.python.int.for_serializing_objects.for_configuring_adapters import (
            Configure as IntSerializeConfigure,
        )

        return BytesConfigure(
            _length=self._get_fixed_length_config(1, False),
            _serde=IntSerializeConfigure(),
        )
