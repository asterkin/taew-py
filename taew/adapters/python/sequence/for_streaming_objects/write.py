from io import BytesIO
from typing import Callable
from collections.abc import Collection, Mapping

from taew.ports.for_streaming_objects import Write as WriteProtocol


class Write:
    """Generic sequence writer with length framing and element writer.

    Dataclasses were avoided here because using ``InitVar`` removes the constructor
    argument from ``__annotations__``. Our dynamic port binder relies on those
    annotations to discover dependencies, so we keep a hand-written ``__init__``
    instead.

    - _from:   extracts a collection of items from the input object
    - _writers: mapping with required keys: 'length' and 'item' to for_streaming_objects writers
    - _write_len: writer used to encode the item count
    - _write_item: writer used to encode each element
    """

    def __init__(
        self,
        _from: Callable[[object], Collection[object]],
        _writers: Mapping[str, WriteProtocol],
    ) -> None:
        self._from = _from
        try:
            self._write_len = _writers["length"]
            self._write_item = _writers["item"]
        except KeyError as e:
            missing = {k for k in ("length", "item") if k not in _writers}
            raise ValueError(
                f"Missing required writer(s) for sequence: {sorted(missing)}"
            ) from e

    def __call__(self, obj: object, stream: BytesIO) -> None:
        items = self._from(obj)
        self._write_len(len(items), stream)
        for item in items:
            self._write_item(item, stream)
