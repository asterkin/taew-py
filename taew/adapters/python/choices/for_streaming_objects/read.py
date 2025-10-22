from io import BytesIO
from dataclasses import dataclass
from typing import cast

from ._common import ChoicesBase
from taew.ports.for_streaming_objects import Read as IntRead


@dataclass(eq=False, frozen=True)
class Read(ChoicesBase):
    _read_int: IntRead = cast(IntRead, None)

    def __call__(self, stream: BytesIO) -> object:
        idx_obj = self._read_int(stream)
        if not isinstance(idx_obj, int):
            raise TypeError(f"Choice index is not int: {type(idx_obj)}")
        idx = idx_obj
        if idx < 0 or idx >= len(self._choices):
            raise ValueError(
                f"Choice index {idx} out of range [0, {len(self._choices) - 1}]"
            )
        return self._choices[idx]
