from io import BytesIO
from typing import Any, cast

from taew.ports.for_streaming_objects import Write as WriteProtocol


class Write:
    """Write mixed tuples with fixed head and variable tail."""

    def __init__(self, _length: int, _writers: dict[str, WriteProtocol]) -> None:
        if _length < 0:
            raise ValueError(f"Invalid head length: {_length}")
        if "head" not in _writers or "tail" not in _writers:
            raise ValueError("Mixed tuple writer requires 'head' and 'tail' writers")

        self._length = _length
        self._write_head = _writers["head"]
        self._write_tail = _writers["tail"]

    def __call__(self, obj: object, stream: BytesIO) -> None:
        if not isinstance(obj, tuple):
            raise TypeError(f"Mixed tuple writer expected tuple, got {type(obj)}")

        items = cast(tuple[Any, ...], obj)  # type: ignore
        if len(items) < self._length:
            raise ValueError(
                f"Tuple too short: expected at least {self._length} items, got {len(items)}"
            )

        # Write fixed head without length prefix
        head = items[: self._length]
        self._write_head(head, stream)

        # Write variable tail with length prefix
        tail = items[self._length :]
        self._write_tail(tail, stream)
