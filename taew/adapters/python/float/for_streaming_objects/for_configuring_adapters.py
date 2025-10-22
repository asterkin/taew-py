from typing import Literal
from dataclasses import dataclass

from ._common import FloatStreamBase, Width, FormatType, TypeCode
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)


@dataclass(eq=False, frozen=True, init=False)
class Configure(FloatStreamBase, ConfigureBase):
    """Configurator for float streaming.

    - _width: 4 (float32) or 8 (float64), default 8
    - _byte_order: 'big' or 'little' (InitVar), default 'big'

    Maps (_width, _byte_order) to struct format once and provides the
    fully-configured base for Write/Read. No nested ports or extra kwargs.
    """

    def __init__(
        self, _width: Width = 8, _byte_order: Literal["big", "little"] = "big"
    ) -> None:
        object.__setattr__(self, "_width", _width)
        # Set adapter identity for PortsMapping construction
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
        fmt: FormatType = ">" if _byte_order == "big" else "<"
        type_code: TypeCode = "f" if self._width == 4 else "d"
        FloatStreamBase.__init__(self, _width, fmt, type_code)
        ConfigureBase.__init__(self)
