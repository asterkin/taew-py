from dataclasses import dataclass
from ._common import SerdeBase


@dataclass(eq=False, frozen=True)
class Deserialize(SerdeBase):
    """Deserialize an integer from bytes (entire buffer).

    Rationale for empty-buffer handling:
    - Python's int.from_bytes(b"") yields 0, but in a framed protocol an empty
      buffer typically signals "no payload" or "insufficient data", not a value.
    - Treating empty as zero can mask truncation bugs and desynchronization in
      higher-level framing (e.g., when a length prefix is wrong).
    - Raising ValueError makes errors explicit and aligns with streaming Read
      behavior, which raises on insufficient data.
    """

    def __call__(self, buf: bytes) -> object:
        if not isinstance(buf, (bytes, bytearray, memoryview)):  # type: ignore[reportUnnecessaryIsInstance]
            raise TypeError(
                f"Unsupported buffer type for int deserialization: {type(buf)}"
            )
        if len(buf) == 0:
            raise ValueError("Empty buffer: cannot deserialize integer")
        return int.from_bytes(buf, self._byte_order, signed=self._signed)
