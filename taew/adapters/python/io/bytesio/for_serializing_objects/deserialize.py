from io import BytesIO
from dataclasses import dataclass

from taew.ports.for_streaming_objects import Read as ReadProtocol


@dataclass(frozen=True, eq=False)
class Deserialize:
    """Deserialize objects from bytes using streaming Read protocol with BytesIO."""

    _read: ReadProtocol

    def __call__(self, data: bytes) -> object:
        """Deserialize object from bytes by streaming from BytesIO.

        Args:
            data: The bytes to deserialize

        Returns:
            The deserialized object

        Raises:
            ValueError: If BytesIO stream was not fully consumed (trailing bytes)
        """
        stream = BytesIO(data)
        obj = self._read(stream)

        # Validate that stream was fully consumed
        remaining = stream.read()
        if remaining:
            raise ValueError(
                f"BytesIO stream was not fully consumed: {len(remaining)} trailing bytes"
            )

        return obj
