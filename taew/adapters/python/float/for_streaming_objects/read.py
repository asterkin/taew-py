import struct
from io import BytesIO
from dataclasses import dataclass, field

from ._common import FloatStreamBase, FormatType, TypeCode


@dataclass(eq=False, frozen=True)
class Read(FloatStreamBase):
    _buf: bytearray = field(init=False, repr=False, compare=False)

    def __post_init__(self, _format: FormatType, _type: TypeCode) -> None:  # type: ignore[override]
        super().__post_init__(_format, _type)  # compute _fmt
        object.__setattr__(self, "_buf", bytearray(self._width))

    def __call__(self, stream: BytesIO) -> object:
        n = stream.readinto(self._buf)
        if n < self._width:
            raise ValueError(f"Not enough data: need {self._width} bytes, got {n}")
        return struct.unpack(self._fmt, self._buf)[0]
