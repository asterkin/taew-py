from io import BytesIO
from dataclasses import dataclass

from taew.ports.for_streaming_objects import Write as WriteProtocol
from taew.ports.for_serializing_objects import Serialize as SerializeProtocol


def _identity_serialize(value: object) -> bytes:
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    raise TypeError(f"Unsupported type for bytes streaming write: {type(value)}")


@dataclass(eq=False, frozen=True)
class Write:
    """Write bytes with a length prefix via injected length writer.

    Steps:
    - _serialize(obj) -> bytes
    - _write_length(len(bytes), stream)
    - stream.write(bytes)
    """

    _write_length: WriteProtocol
    _serialize: SerializeProtocol = _identity_serialize

    def __call__(self, obj: object, stream: BytesIO) -> None:
        data = self._serialize(obj)
        self._write_length(len(data), stream)
        stream.write(data)
