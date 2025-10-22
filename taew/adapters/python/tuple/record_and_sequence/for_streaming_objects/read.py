from io import BytesIO
from typing import Any, cast

from taew.ports.for_streaming_objects import Read as ReadProtocol


class Read:
    """Read mixed tuples with fixed head and variable tail."""

    def __init__(self, _length: int, _readers: dict[str, ReadProtocol]) -> None:
        if _length < 0:
            raise ValueError(f"Invalid head length: {_length}")
        if "head" not in _readers or "tail" not in _readers:
            raise ValueError("Mixed tuple reader requires 'head' and 'tail' readers")

        self._length = _length
        self._read_head = _readers["head"]
        self._read_tail = _readers["tail"]

    def __call__(self, stream: BytesIO) -> object:
        # Read fixed head without length prefix
        head = self._read_head(stream)
        if not isinstance(head, tuple):
            raise TypeError(f"Head reader must return tuple, got {type(head)}")

        # Read variable tail with length prefix
        tail = self._read_tail(stream)
        if not isinstance(tail, tuple):
            raise TypeError(f"Tail reader must return tuple, got {type(tail)}")

        # Combine head and tail
        return cast(  # type: ignore
            tuple[Any, ...],
            head,
        ) + cast(  # type: ignore
            tuple[Any, ...],
            tail,
        )
