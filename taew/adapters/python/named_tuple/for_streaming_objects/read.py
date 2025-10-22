from io import BytesIO
from typing import Any
from dataclasses import dataclass, field

from taew.ports.for_streaming_objects import Read as ReadProtocol


@dataclass(frozen=True, eq=False)
class Read:
    """Read named tuples by field name using field-specific readers."""

    _type: type[Any]
    _readers: dict[str, ReadProtocol]
    _fields: tuple[str, ...] = field(init=False)

    def __post_init__(self) -> None:
        if not hasattr(self._type, "_fields"):
            raise TypeError(
                f"Expected named tuple type with _fields attribute, got {self._type.__name__}"
            )

        fields = getattr(self._type, "_fields")

        if set(fields) != set(self._readers.keys()):
            raise ValueError(
                f"Field mismatch: expected {set(self._readers.keys())}, "
                f"got {set(fields)}"
            )

        object.__setattr__(self, "_fields", fields)

    def __call__(self, stream: BytesIO) -> object:
        field_values = {
            field_name: self._readers[field_name](stream) for field_name in self._fields
        }
        return self._type(**field_values)
