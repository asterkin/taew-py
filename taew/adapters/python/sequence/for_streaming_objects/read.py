from io import BytesIO
from typing import Callable
from collections.abc import Mapping

from taew.ports.for_streaming_objects import (
    Read as ReadProtocol,
    SequenceContext,
)


class Read:
    """Generic sequence reader with length framing and element reader.

    Dataclasses are avoided for the same reason as the writer: ``InitVar`` would
    strip constructor arguments from ``__annotations__`` and break the dynamic
    port binder, so we manage initialisation manually.

    - _target: factory producing a build context for the given length
    - _readers: mapping with required keys: 'length' and 'item' to for_streaming_objects readers
    - _read_len: reader used to decode the item count
    - _read_item: reader used to decode each element
    """

    def __init__(
        self,
        _target: Callable[[int], SequenceContext],
        _readers: Mapping[str, ReadProtocol],
    ) -> None:
        self._target = _target
        try:
            self._read_len = _readers["length"]
            self._read_item = _readers["item"]
        except KeyError as e:
            missing = {k for k in ("length", "item") if k not in _readers}
            raise ValueError(
                f"Missing required reader(s) for sequence: {sorted(missing)}"
            ) from e

    def __call__(self, stream: BytesIO) -> object:
        count_obj = self._read_len(stream)
        if not isinstance(count_obj, int):  # type: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"Sequence length is not int: {type(count_obj)}")
        count = count_obj
        if count < 0:
            raise ValueError(f"Negative sequence length: {count}")

        with self._target(count) as target:
            for _ in range(count):
                item = self._read_item(stream)
                target.append(item)
            return target.value()
