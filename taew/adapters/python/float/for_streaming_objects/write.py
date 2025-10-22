import struct
from io import BytesIO
from dataclasses import dataclass

from ._common import FloatStreamBase


@dataclass(eq=False, frozen=True)
class Write(FloatStreamBase):
    def __call__(self, obj: object, stream: BytesIO) -> None:
        if not isinstance(obj, float):  # type: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"Unsupported type for float write: {type(obj)}")
        stream.write(struct.pack(self._fmt, obj))
