from io import BytesIO
from typing import Any, cast

from taew.ports.for_streaming_objects import Write as WriteProtocol


class Write:
    """Write fixed-arity heterogeneous tuples by delegating per position."""

    def __init__(self, *_writers: WriteProtocol) -> None:
        if not _writers:
            raise ValueError("Tuple writer requires at least one positional writer")
        self._writers = tuple(_writers)

    def __call__(self, obj: object, stream: BytesIO) -> None:
        if not isinstance(obj, tuple):
            raise TypeError(f"Tuple writer expected tuple, got {type(obj)}")
        items = cast(tuple[Any, ...], obj)  # type: ignore
        if len(items) != len(self._writers):
            raise ValueError(
                f"Tuple length mismatch: expected {len(self._writers)}, got {len(items)}"
            )
        for item, writer in zip(items, self._writers):
            writer(item, stream)
