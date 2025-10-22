from io import BytesIO
from typing import Any, cast
from dataclasses import dataclass

from taew.ports.for_streaming_objects import Write as WriteProtocol


@dataclass(frozen=True, eq=False)
class Write:
    """Write named tuples by field name using field-specific writers."""

    _writers: dict[str, WriteProtocol]

    def __call__(self, obj: object, stream: BytesIO) -> None:
        if not hasattr(obj, "_fields"):
            raise TypeError(
                f"Expected named tuple with _fields attribute, got {type(obj).__name__}"
            )

        named_tuple = cast(Any, obj)
        fields = getattr(named_tuple, "_fields")

        if set(fields) != set(self._writers.keys()):
            raise ValueError(
                f"Field mismatch: expected {set(self._writers.keys())}, "
                f"got {set(fields)}"
            )

        for field in fields:
            value = getattr(named_tuple, field)
            writer = self._writers[field]
            writer(value, stream)
