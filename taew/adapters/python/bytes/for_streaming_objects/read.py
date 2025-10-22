from io import BytesIO
from dataclasses import dataclass

from taew.ports.for_streaming_objects import Read as ReadProtocol
from taew.ports.for_serializing_objects import Deserialize as DeserializeProtocol


def _identity_deserialize(buf: bytes) -> object:
    return bytes(buf)


@dataclass(eq=False, frozen=True)
class Read:
    """Read bytes with a length prefix via injected length reader.

    Steps:
    - length = _read_length(stream)
    - allocate buffer of 'length' bytes
    - readinto buffer; ensure exact length was read
    - return _deserialize(buffer)
    """

    _read_length: ReadProtocol
    _deserialize: DeserializeProtocol = _identity_deserialize

    def __call__(self, stream: BytesIO) -> object:
        length_obj = self._read_length(stream)
        if not isinstance(length_obj, int):  # safeguard; length is expected to be int
            raise TypeError(f"Length reader returned non-int: {type(length_obj)}")
        if length_obj < 0:
            raise ValueError("Negative length prefix for bytes")

        length = length_obj
        buf = bytearray(length)
        n = stream.readinto(buf)
        if n < length:
            raise ValueError(f"Not enough data: need {length} bytes, got {n}")
        return self._deserialize(bytes(buf))
