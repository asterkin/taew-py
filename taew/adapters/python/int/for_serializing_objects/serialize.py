from dataclasses import dataclass
from taew.utils.int import signed_int_bytes_needed
from taew.utils.int import unsigned_int_bytes_needed
from ._common import SerdeBase


@dataclass(eq=False, frozen=True)
class Serialize(SerdeBase):
    """Serialize an integer to minimal-width bytes (no length prefix)."""

    def __call__(self, value: object) -> bytes:
        if not isinstance(value, int):
            raise TypeError(f"Unsupported type for int serialization: {type(value)}")

        if value == 0:
            return b"\x00"

        width = (
            signed_int_bytes_needed(value)
            if self._signed
            else unsigned_int_bytes_needed(value)
        )
        return value.to_bytes(width, self._byte_order, signed=self._signed)
