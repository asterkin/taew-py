import zlib
from dataclasses import dataclass

from taew.ports.for_serializing_objects import Deserialize as DeserializeProtocol


def _identity_deserialize(buf: bytes) -> object:
    """Default deserializer that passes through bytes unchanged."""
    return buf


@dataclass(frozen=True, eq=False)
class Deserialize:
    """Deserialize compressed bytes to objects using zlib.

    First decompresses bytes using zlib, then deserializes to object using _deserialize.
    """

    _deserialize: DeserializeProtocol = _identity_deserialize

    def __call__(self, buf: bytes) -> object:
        """Decompress and deserialize bytes to object.

        Args:
            buf: The compressed bytes to decompress and deserialize

        Returns:
            The deserialized object
        """
        # First decompress the bytes
        decompressed = zlib.decompress(buf)

        # Then deserialize to object
        return self._deserialize(decompressed)
