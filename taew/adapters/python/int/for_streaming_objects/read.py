from io import BytesIO
from ._common import IntStreamBase
from dataclasses import dataclass, field


@dataclass(eq=False, frozen=True)
class Read(IntStreamBase):
    """Read a fixed-width integer from a stream using int.from_bytes.

    Configuration mirrors Write: _width, _byte_order, _signed.
    """

    _buf: bytearray = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "_buf", bytearray(self._width))

    def __call__(self, stream: BytesIO) -> object:
        n = stream.readinto(self._buf)
        if n < self._width:
            raise ValueError(f"Not enough data: need {self._width} bytes, got {n}")
        return int.from_bytes(self._buf, self._byte_order, signed=self._signed)
