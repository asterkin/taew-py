import zlib
from dataclasses import dataclass

from taew.ports.for_serializing_objects import Serialize as SerializeProtocol


def _identity_serialize(value: object) -> bytes:
    """Default serializer that passes through bytes unchanged."""
    if isinstance(value, bytes):
        return value
    raise ValueError(f"Expected bytes, got {type(value).__name__}")


@dataclass(frozen=True, eq=False)
class Serialize:
    """Serialize objects to compressed bytes using zlib.

    First serializes object to bytes using _serialize, then applies zlib compression.
    """

    _level: int
    _serialize: SerializeProtocol = _identity_serialize

    def __call__(self, value: object) -> bytes:
        """Serialize and compress object to bytes.

        Args:
            value: The object to serialize and compress

        Returns:
            Compressed bytes
        """
        # First serialize object to bytes
        serialized = self._serialize(value)

        # Then compress the bytes
        return zlib.compress(serialized, self._level)
