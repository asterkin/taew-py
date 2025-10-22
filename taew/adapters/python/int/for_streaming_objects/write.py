from io import BytesIO
from dataclasses import dataclass

from ._common import IntStreamBase


@dataclass(eq=False, frozen=True)
class Write(IntStreamBase):
    """Write a fixed-width integer to a stream using int.to_bytes.

    Configuration:
    - _width: number of bytes to write (fixed width)
    - _byte_order: 'big' or 'little'
    - _signed: whether values may be negative
    """

    def __call__(self, obj: object, stream: BytesIO) -> None:
        if not isinstance(obj, int):  # type: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"Unsupported type for int streaming write: {type(obj)}")

        # Let OverflowError from to_bytes propagate for out-of-range values.
        data = obj.to_bytes(self._width, self._byte_order, signed=self._signed)
        stream.write(data)
