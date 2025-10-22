from io import BytesIO
from dataclasses import dataclass

from taew.ports.for_streaming_objects import Write as WriteProtocol


@dataclass(frozen=True, eq=False)
class Serialize:
    """Serialize objects to bytes using streaming Write protocol with BytesIO."""

    _write: WriteProtocol

    def __call__(self, obj: object) -> bytes:
        """Serialize object to bytes by streaming to BytesIO.

        Args:
            obj: The object to serialize

        Returns:
            The serialized bytes
        """
        stream = BytesIO()
        self._write(obj, stream)
        return stream.getvalue()
